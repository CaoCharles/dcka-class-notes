import importlib
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
os.environ.pop("GEMINI_API_KEY", None)

with patch("google.cloud.firestore.Client", return_value=None):
    chat_server = importlib.import_module("chat_server")


class FakeModels:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def generate_content(self, **kwargs):
        if self.error:
            raise self.error
        return SimpleNamespace(text=self.result)


class FakeFirestore:
    def __init__(self):
        self.records = []

    def collection(self, name):
        if name != "chat_logs":
            raise AssertionError(f"unexpected collection: {name}")
        return self

    def add(self, record):
        self.records.append(record)


class ChatServerTest(unittest.TestCase):
    def setUp(self):
        self.original_client = chat_server.client
        self.original_db = chat_server.db
        chat_server.rate_limiter = chat_server.InMemoryRateLimiter(20, 60)
        self.http = TestClient(chat_server.app)

    def tearDown(self):
        chat_server.client = self.original_client
        chat_server.db = self.original_db
        self.http.close()

    def test_cors_allows_only_configured_origin(self):
        allowed = self.http.options(
            "/api/chat",
            headers={
                "Origin": "https://caocharles.github.io",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(
            allowed.headers["access-control-allow-origin"],
            "https://caocharles.github.io",
        )

        denied = self.http.options(
            "/api/chat",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertEqual(denied.status_code, 400)
        self.assertNotIn("access-control-allow-origin", denied.headers)

    def test_request_body_and_message_limits(self):
        oversized = self.http.post(
            "/api/chat",
            content=b"x" * (chat_server.MAX_REQUEST_BODY_BYTES + 1),
            headers={
                "Content-Type": "application/json",
                "Origin": "https://caocharles.github.io",
            },
        )
        self.assertEqual(oversized.status_code, 413)
        self.assertEqual(
            oversized.headers["access-control-allow-origin"],
            "https://caocharles.github.io",
        )

        too_long = self.http.post(
            "/api/chat",
            json={"history": [], "message": "x" * (chat_server.MAX_MESSAGE_CHARS + 1)},
        )
        self.assertEqual(too_long.status_code, 422)
        self.assertEqual(too_long.json(), {"detail": "Invalid request."})

    def test_rate_limit_returns_retry_after(self):
        chat_server.client = SimpleNamespace(models=FakeModels(result="ok"))
        chat_server.rate_limiter = chat_server.InMemoryRateLimiter(1, 60)

        payload = {"history": [], "message": "Docker?", "session_id": "session_1"}
        first = self.http.post("/api/chat", json=payload)
        second = self.http.post("/api/chat", json=payload)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        self.assertIn("retry-after", second.headers)

    def test_rate_limit_ignores_spoofed_forwarded_prefix(self):
        chat_server.client = SimpleNamespace(models=FakeModels(result="ok"))
        chat_server.rate_limiter = chat_server.InMemoryRateLimiter(1, 60)
        payload = {"history": [], "message": "Docker?", "session_id": "session_1"}

        first = self.http.post(
            "/api/chat",
            json=payload,
            headers={"X-Forwarded-For": "198.51.100.10, 203.0.113.8, 192.0.2.1"},
        )
        second = self.http.post(
            "/api/chat",
            json=payload,
            headers={"X-Forwarded-For": "198.51.100.99, 203.0.113.8, 192.0.2.1"},
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)

    def test_invalid_requests_also_consume_rate_limit(self):
        chat_server.client = SimpleNamespace(models=FakeModels(result="ok"))
        chat_server.rate_limiter = chat_server.InMemoryRateLimiter(1, 60)

        invalid = self.http.post("/api/chat", content=b"not-json")
        valid = self.http.post(
            "/api/chat",
            json={"history": [], "message": "Docker?", "session_id": "session_1"},
        )

        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(valid.status_code, 429)

    def test_rate_limiter_bounds_source_tracking_memory(self):
        limiter = chat_server.InMemoryRateLimiter(1, 60)
        for index in range(10_002):
            limiter.allow(f"source-{index}")
        self.assertEqual(len(limiter.requests), 10_000)

    def test_internal_error_is_not_returned_to_client(self):
        chat_server.client = SimpleNamespace(
            models=FakeModels(error=RuntimeError("upstream secret detail"))
        )
        chat_server.db = FakeFirestore()

        response = self.http.post(
            "/api/chat",
            json={"history": [], "message": "Docker?", "session_id": "session_2"},
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], chat_server.GENERIC_SERVICE_ERROR)
        self.assertNotIn("secret", response.text)
        self.assertEqual(chat_server.db.records[0]["error"], "RuntimeError")

    def test_firestore_record_is_masked_and_has_expiry(self):
        chat_server.db = FakeFirestore()
        chat_server.log_chat(
            "session_3",
            "email me at test@example.com or 0912-345-678, id A123456789",
            "token: " + "AIza" + "A" * 28,
            123,
            "success",
        )

        record = chat_server.db.records[0]
        self.assertIn("[EMAIL]", record["question"])
        self.assertIn("[PHONE]", record["question"])
        self.assertIn("[TW_ID]", record["question"])
        self.assertIn("[SECRET]", record["answer"])
        self.assertIn("expires_at", record)


if __name__ == "__main__":
    unittest.main()
