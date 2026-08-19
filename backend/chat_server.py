import os
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from google.cloud import firestore
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS
# In production, specific origins should be allowed instead of "*"
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://caocharles.github.io", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_origins=["*"], # For easier testing on Cloud Run/localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    # Instead of crashing, print a warning. The endpoint will fail if called.
    print("WARNING: GEMINI_API_KEY is not set.")
client = genai.Client(api_key=api_key) if api_key else None

MODEL_NAME = "gemini-3.5-flash"

# Firestore：問答紀錄用，寫入失敗不應該影響聊天功能本身
try:
    db = firestore.Client()
except Exception as e:
    print(f"WARNING: Firestore client init failed, chat logging disabled: {e}")
    db = None


def log_chat(session_id, question, answer, latency_ms, status, error=None):
    if not db:
        return
    try:
        db.collection("chat_logs").add({
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "model": MODEL_NAME,
            "latency_ms": latency_ms,
            "status": status,
            "error": error,
            "created_at": SERVER_TIMESTAMP,
        })
    except Exception as e:
        print(f"WARNING: Failed to write chat log to Firestore: {e}")


class ChatMessagePart(BaseModel):
    text: str

class ChatMessage(BaseModel):
    role: str
    parts: List[ChatMessagePart]

class ChatRequest(BaseModel):
    history: List[ChatMessage] # Complete chat history
    message: str # The new user message
    system_instruction: Optional[str] = None # Optional system context
    session_id: Optional[str] = None # 前端 sessionStorage 產生的識別碼，用來把同一次對話串起來

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Gemini Chatbot Proxy"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured on server.")

    start = time.monotonic()
    try:
        # Gemini expects 'user' or 'model' roles.
        # Our frontend sends 'user' and 'bot' (or 'model'). We need to map them.
        contents = []
        for msg in request.history:
            role = "user" if msg.role == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=part.text) for part in msg.parts],
                )
            )
        contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=request.message)])
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=request.system_instruction or None,
                # RAG 問答不需要深度推理，thinking level 調低以降低延遲
                thinking_config=types.ThinkingConfig(thinking_level="low"),
            ),
        )

        latency_ms = round((time.monotonic() - start) * 1000)
        log_chat(request.session_id, request.message, response.text, latency_ms, "success")

        return {"text": response.text}

    except Exception as e:
        latency_ms = round((time.monotonic() - start) * 1000)
        log_chat(request.session_id, request.message, None, latency_ms, "error", error=str(e))
        print(f"Error calling Gemini: {e}")
        raise HTTPException(status_code=500, detail=str(e))
