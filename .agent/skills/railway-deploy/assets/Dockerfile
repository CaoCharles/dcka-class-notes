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
