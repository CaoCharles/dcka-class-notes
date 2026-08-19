import hashlib
import logging
import os
import re
import threading
import time
from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from math import ceil
from typing import Literal

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google import genai
from google.cloud import firestore
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from google.genai import types
from pydantic import BaseModel, Field, field_validator

load_dotenv()

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("dcka.chat")


def env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    """Read a bounded integer setting without allowing a bad deploy to crash."""
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except ValueError:
        logger.warning("Invalid integer environment setting: %s", name)
        return default
    if not minimum <= value <= maximum:
        logger.warning("Out-of-range environment setting: %s", name)
        return default
    return value


DEFAULT_ALLOWED_ORIGINS = (
    "https://caocharles.github.io",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
)
ALLOWED_ORIGINS = tuple(
    origin.strip().rstrip("/")
    for origin in os.environ.get(
        "ALLOWED_ORIGINS", ",".join(DEFAULT_ALLOWED_ORIGINS)
    ).split(",")
    if origin.strip()
)

MAX_REQUEST_BODY_BYTES = env_int("MAX_REQUEST_BODY_BYTES", 1_048_576, 16_384, 5_242_880)
MAX_MESSAGE_CHARS = env_int("MAX_MESSAGE_CHARS", 4_000, 100, 20_000)
MAX_HISTORY_MESSAGES = env_int("MAX_HISTORY_MESSAGES", 20, 0, 100)
MAX_HISTORY_PART_CHARS = env_int("MAX_HISTORY_PART_CHARS", 8_000, 100, 50_000)
MAX_SYSTEM_INSTRUCTION_CHARS = env_int(
    "MAX_SYSTEM_INSTRUCTION_CHARS", 750_000, 10_000, 2_000_000
)
RATE_LIMIT_REQUESTS = env_int("RATE_LIMIT_REQUESTS", 20, 1, 1_000)
RATE_LIMIT_WINDOW_SECONDS = env_int("RATE_LIMIT_WINDOW_SECONDS", 60, 1, 3_600)
CHAT_LOG_RETENTION_DAYS = env_int("CHAT_LOG_RETENTION_DAYS", 90, 1, 365)

MODEL_NAME = "gemini-3.5-flash"
GENERIC_SERVICE_ERROR = "AI service is temporarily unavailable. Please try again later."


class RequestBodyLimitMiddleware:
    """Reject oversized chat payloads before JSON parsing and validation."""

    def __init__(self, app, max_body_size: int):
        self.app = app
        self.max_body_size = max_body_size

    async def __call__(self, scope, receive, send):
        if not (
            scope["type"] == "http"
            and scope.get("method") == "POST"
            and scope.get("path") == "/api/chat"
        ):
            await self.app(scope, receive, send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        content_length = headers.get(b"content-length")
        if content_length:
            try:
                if int(content_length) > self.max_body_size:
                    await JSONResponse(
                        status_code=413,
                        content={"detail": "Request body is too large."},
                    )(scope, receive, send)
                    return
            except ValueError:
                await JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid request."},
                )(scope, receive, send)
                return

        chunks = []
        total_size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return

            chunk = message.get("body", b"")
            total_size += len(chunk)
            if total_size > self.max_body_size:
                await JSONResponse(
                    status_code=413,
                    content={"detail": "Request body is too large."},
                )(scope, receive, send)
                return
            chunks.append(chunk)

            if not message.get("more_body", False):
                break

        body = b"".join(chunks)
        replayed = False

        async def replay_receive():
            nonlocal replayed
            if not replayed:
                replayed = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        await self.app(scope, replay_receive, send)


class InMemoryRateLimiter:
    """A bounded, per-instance sliding-window limiter for the public endpoint."""

    def __init__(self, request_limit: int, window_seconds: int):
        self.request_limit = request_limit
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key: str) -> tuple[bool, int]:
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self.lock:
            bucket = self.requests[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= self.request_limit:
                retry_after = max(1, ceil(self.window_seconds - (now - bucket[0])))
                return False, retry_after

            bucket.append(now)

            # Bound memory if an attacker rotates source addresses.
            if len(self.requests) > 10_000:
                expired_keys = [
                    item_key
                    for item_key, timestamps in self.requests.items()
                    if not timestamps or timestamps[-1] <= cutoff
                ]
                for item_key in expired_keys:
                    self.requests.pop(item_key, None)
                while len(self.requests) > 10_000:
                    self.requests.pop(next(iter(self.requests)))

            return True, 0


rate_limiter = InMemoryRateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)


def client_rate_limit_key_from_scope(scope) -> str:
    headers = {key.lower(): value for key, value in scope.get("headers", [])}
    forwarded_for = headers.get(b"x-forwarded-for", b"").decode("latin-1")
    forwarded_hops = [hop.strip() for hop in forwarded_for.split(",") if hop.strip()]
    # Google external load balancers append <client-ip>,<load-balancer-ip> to
    # any caller-supplied values, so the second-to-last hop resists spoofed
    # prefixes. Direct/local requests commonly contain zero or one hop.
    client_ip = (
        forwarded_hops[-2]
        if len(forwarded_hops) >= 2
        else (forwarded_hops[-1] if forwarded_hops else "")
    )
    if not client_ip and scope.get("client"):
        client_ip = scope["client"][0]
    return hashlib.sha256((client_ip or "unknown").encode("utf-8")).hexdigest()


class RateLimitMiddleware:
    """Rate-limit every POST attempt, including invalid JSON and schemas."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if (
            scope["type"] == "http"
            and scope.get("method") == "POST"
            and scope.get("path") == "/api/chat"
        ):
            allowed, retry_after = rate_limiter.allow(
                client_rate_limit_key_from_scope(scope)
            )
            if not allowed:
                logger.warning("Rate limit exceeded")
                await JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."},
                    headers={"Retry-After": str(retry_after)},
                )(scope, receive, send)
                return

        await self.app(scope, receive, send)


app = FastAPI()
app.add_middleware(RequestBodyLimitMiddleware, max_body_size=MAX_REQUEST_BODY_BYTES)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(ALLOWED_ORIGINS),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    expose_headers=["Retry-After"],
)


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
):
    logger.warning(
        "Request validation failed path=%s error_count=%d",
        request.url.path,
        len(exc.errors()),
    )
    return JSONResponse(status_code=422, content={"detail": "Invalid request."})


# Configure Gemini. A missing key does not prevent the health endpoint from starting.
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    logger.warning("GEMINI_API_KEY is not set")
client = genai.Client(api_key=api_key) if api_key else None


# Firestore logging is best effort and must never become a chat dependency.
try:
    db = firestore.Client()
except Exception:
    logger.exception("Firestore client initialization failed; chat logging disabled")
    db = None


SENSITIVE_PATTERNS = (
    (re.compile(r"\b[A-Z][12]\d{8}\b", re.IGNORECASE), "[TW_ID]"),
    (
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
        "[EMAIL]",
    ),
    (re.compile(r"(?<!\d)(?:\+886[- ]?|0)9\d{2}[- ]?\d{3}[- ]?\d{3}(?!\d)"), "[PHONE]"),
    (re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"), "[CARD]"),
    (re.compile(r"\bAIza[A-Za-z0-9_-]{20,}\b"), "[SECRET]"),
    (
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|secret)\s*[:=]\s*[A-Za-z0-9._~+/=-]{8,}"
        ),
        "[SECRET]",
    ),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{10,}"), "Bearer [SECRET]"),
)


def mask_sensitive_data(value: str | None, max_length: int) -> str | None:
    if value is None:
        return None
    masked = value
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked[:max_length]


def log_chat(session_id, question, answer, latency_ms, status, error=None):
    if not db:
        return
    try:
        db.collection("chat_logs").add(
            {
                "session_id": session_id,
                "question": mask_sensitive_data(question, 8_000),
                "answer": mask_sensitive_data(answer, 12_000),
                "model": MODEL_NAME,
                "latency_ms": latency_ms,
                "status": status,
                "error": mask_sensitive_data(error, 500),
                "created_at": SERVER_TIMESTAMP,
                "expires_at": datetime.now(UTC)
                + timedelta(days=CHAT_LOG_RETENTION_DAYS),
            }
        )
    except Exception:
        logger.exception("Failed to write chat log to Firestore")


class ChatMessagePart(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_HISTORY_PART_CHARS)


class ChatMessage(BaseModel):
    role: Literal["user", "model", "bot"]
    parts: list[ChatMessagePart] = Field(min_length=1, max_length=8)


class ChatRequest(BaseModel):
    history: list[ChatMessage] = Field(
        default_factory=list, max_length=MAX_HISTORY_MESSAGES
    )
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    system_instruction: str | None = Field(
        default=None, max_length=MAX_SYSTEM_INSTRUCTION_CHARS
    )
    session_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9_-]+$",
    )

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be blank")
        return value


@app.get("/")
def read_root():
    return {"status": "ok", "service": "Gemini Chatbot Proxy"}


@app.post("/api/chat")
def chat_endpoint(
    payload: ChatRequest,
    background_tasks: BackgroundTasks,
):
    if not client:
        logger.error("Chat request rejected because Gemini client is unavailable")
        return JSONResponse(
            status_code=503,
            content={"detail": GENERIC_SERVICE_ERROR},
        )

    start = time.monotonic()
    try:
        contents = []
        for message in payload.history:
            role = "user" if message.role == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[
                        types.Part.from_text(text=part.text) for part in message.parts
                    ],
                )
            )
        contents.append(
            types.Content(
                role="user", parts=[types.Part.from_text(text=payload.message)]
            )
        )

        # A synchronous endpoint makes FastAPI run this blocking SDK call in its
        # worker threadpool instead of blocking the event loop.
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=payload.system_instruction or None,
                thinking_config=types.ThinkingConfig(thinking_level="low"),
            ),
        )
        answer = response.text
        if not answer:
            raise RuntimeError("Gemini returned an empty response")

        latency_ms = round((time.monotonic() - start) * 1000)
        background_tasks.add_task(
            log_chat,
            payload.session_id,
            payload.message,
            answer,
            latency_ms,
            "success",
        )
        return {"text": answer}

    except Exception as exc:
        latency_ms = round((time.monotonic() - start) * 1000)
        logger.exception(
            "Gemini request failed model=%s latency_ms=%d",
            MODEL_NAME,
            latency_ms,
        )
        background_tasks.add_task(
            log_chat,
            payload.session_id,
            payload.message,
            None,
            latency_ms,
            "error",
            type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": GENERIC_SERVICE_ERROR},
            background=background_tasks,
        )
