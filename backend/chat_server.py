import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
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

class ChatMessagePart(BaseModel):
    text: str

class ChatMessage(BaseModel):
    role: str
    parts: List[ChatMessagePart]

class ChatRequest(BaseModel):
    history: List[ChatMessage] # Complete chat history
    message: str # The new user message
    system_instruction: Optional[str] = None # Optional system context

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Gemini Chatbot Proxy"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured on server.")

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
            model="gemini-3.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=request.system_instruction or None,
                # RAG 問答不需要深度推理，thinking level 調低以降低延遲
                thinking_config=types.ThinkingConfig(thinking_level="low"),
            ),
        )

        return {"text": response.text}

    except Exception as e:
        print(f"Error calling Gemini: {e}")
        raise HTTPException(status_code=500, detail=str(e))
