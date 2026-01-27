FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway sets PORT env var, we capture it or default to 8000
CMD sh -c "uvicorn chat_server:app --host 0.0.0.0 --port ${PORT:-8000}"
