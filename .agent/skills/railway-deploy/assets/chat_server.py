"""
AI Chatbot 後端 - FastAPI + Gemini API
複製此檔案到專案的 backend/ 目錄
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(title="AI Chatbot Backend")

# CORS 設定 - 允許所有來源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== Gemini 設定 ======
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=api_key)

# TODO: 可更換為其他 Gemini 模型
MODEL_ID = "gemini-2.0-flash-lite-preview-02-05"


class ChatRequest(BaseModel):
    history: list = []
    message: str
    system_instruction: str = ""


@app.get("/")
def root():
    """健康檢查端點"""
    return {
        "status": "ok",
        "model": MODEL_ID,
        "message": "AI Chatbot Backend is running"
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    處理聊天請求
    
    Args:
        request: 包含 history, message, system_instruction
    
    Returns:
        AI 的回覆
    """
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_ID,
            system_instruction=request.system_instruction
        )
        
        chat_session = model.start_chat(history=request.history)
        response = chat_session.send_message(request.message)
        
        return {"response": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
