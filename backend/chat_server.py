import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS
# In production, specific origins should be allowed instead of "*"
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://caocharles.github.io", "http://localhost:8000", "http://127.0.0.1:8000"], 
    allow_origins=["*"], # For easier testing on Railway/localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    # Instead of crashing, print a warning. The endpoint will fail if called.
    print("WARNING: GEMINI_API_KEY is not set.")
else:
    genai.configure(api_key=api_key)

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
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured on server.")

    try:
        # Construct the model
        model = genai.GenerativeModel('gemini-2.5-flash')  # Stable Gemini 2.5 Flash model

        # Prepare chat history for Gemini
        # Gemini expects 'user' or 'model' roles. 
        # Our frontend sends 'user' and 'bot' (or 'model'). We need to map them.
        gemini_history = []
        for msg in request.history:
            role = "user" if msg.role == "user" else "model"
            gemini_history.append({
                "role": role,
                "parts": [{"text": part.text} for part in msg.parts]
            })

        # Start chat session or use generate_content depending on if we want to use the ChatSession object
        # Since we receive full history stateless-ly, we can rebuild the chat object
        chat = model.start_chat(history=gemini_history)
        
        # Add system instruction to the prompt context if provided, or rely on what's in history.
        # Note: 'gemini-1.5-flash' supports system_instruction in the constructor, but we are using start_chat.
        # A simple way to handle system instruction in stateless HTTP is to prepend it to the history or strictly use it as context.
        # However, for RAG, we might append the context to the latest message.
        
        final_message = request.message
        if request.system_instruction:
             # If system instruction is essentially the RAG context:
             final_message = f"{request.system_instruction}\n\nUser Question: {request.message}"

        response = chat.send_message(final_message)
        
        return {"text": response.text}

    except Exception as e:
        print(f"Error calling Gemini: {e}")
        raise HTTPException(status_code=500, detail=str(e))
