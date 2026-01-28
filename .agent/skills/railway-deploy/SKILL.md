---
name: Railway 後端部署
description: 將 AI Chatbot 後端部署到 Railway 的完整指南
---

# Railway 後端部署 Skill

## 概述

本 Skill 定義如何將 AI Chatbot 後端部署到 Railway，使用 UV + pyproject.toml 管理依賴。

## 觸發條件

當使用者提到以下關鍵字時啟用：
- Railway、後端部署
- API 部署、Gemini 後端
- chat_server

---

## 範本檔案

本 Skill 包含以下範本（位於 `assets/` 目錄）：

| 檔案 | 說明 |
|------|------|
| `chat_server.py` | FastAPI 主程式 |
| `pyproject.toml` | UV 專案設定 |
| `Dockerfile` | Docker 設定（使用 UV） |
| `.python-version` | Python 版本設定 |

---

## 後端檔案結構

```
backend/
├── .python-version     # 3.12
├── pyproject.toml      # UV 專案設定
├── uv.lock             # 依賴鎖定
├── chat_server.py      # FastAPI 主程式
└── Dockerfile          # Docker 設定
```

---

## pyproject.toml

```toml
[project]
name = "chatbot-backend"
version = "0.1.0"
description = "AI Chatbot Backend with Gemini API"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "google-generativeai>=0.8.0",
    "pydantic>=2.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## Dockerfile (使用 UV)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安裝 UV
RUN pip install uv

# 複製專案設定
COPY pyproject.toml .
COPY .python-version .

# 安裝依賴
RUN uv sync --no-dev

# 複製程式碼
COPY . .

# 啟動服務
CMD ["uv", "run", "python", "chat_server.py"]
```

---

## chat_server.py

```python
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI(title="AI Chatbot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not set")

genai.configure(api_key=api_key)
MODEL_ID = "gemini-2.5-flash"

class ChatRequest(BaseModel):
    history: list = []
    message: str
    system_instruction: str = ""

@app.get("/")
def root():
    return {"status": "ok", "model": MODEL_ID}

@app.post("/api/chat")
async def chat(request: ChatRequest):
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
```

---

## 本地開發

```bash
cd backend

# 初始化 UV 專案
uv python pin 3.12
uv init
uv add fastapi uvicorn google-generativeai pydantic

# 設定環境變數
$env:GEMINI_API_KEY = "your-api-key"

# 啟動開發伺服器
uv run python chat_server.py
```

---

## Railway 部署步驟

### 1. 取得 Gemini API Key

1. 前往 [Google AI Studio](https://aistudio.google.com/)
2. 建立 API Key
3. 複製 Key 備用

### 2. 建立 Railway 專案

1. 前往 [Railway](https://railway.app/)
2. 登入（可用 GitHub）
3. 點擊 **New Project**
4. 選擇 **Deploy from GitHub repo**
5. 選擇你的 repo
6. 設定 **Root Directory** 為 `backend`

### 3. 設定環境變數

在 Railway Dashboard → Variables：

| 變數名 | 值 |
|--------|-----|
| `GEMINI_API_KEY` | 你的 Gemini API Key |

### 4. 確認部署

1. 等待 Railway 建置完成
2. 點擊產生的 URL
3. 應該看到 `{"status": "ok", "model": "..."}`

---

## 前端連接設定

在 `chatbot.js` 中設定 API URL：

```javascript
window.BACKEND_API_URL = "https://your-app-name.up.railway.app";
```

---

## 故障排除

| 錯誤 | 原因 | 解決 |
|------|------|------|
| `GEMINI_API_KEY not set` | 環境變數未設定 | 在 Railway Variables 設定 |
| `Build failed` | Dockerfile 或依賴問題 | 檢查 pyproject.toml |
| `uv: command not found` | UV 未安裝 | 確認 Dockerfile 有 `pip install uv` |

---

## 相關連結

- [Railway Dashboard](https://railway.app/dashboard)
- [Google AI Studio](https://aistudio.google.com/)
- [UV 官方文件](https://docs.astral.sh/uv/)
