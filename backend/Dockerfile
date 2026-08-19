FROM python:3.12-slim

WORKDIR /app

# Pin uv so dependency installation behaves the same in every build.
COPY --from=ghcr.io/astral-sh/uv:0.9.9 /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install the exact dependency graph recorded in uv.lock.
RUN uv sync --locked --no-dev --no-install-project

ENV PATH="/app/.venv/bin:${PATH}"

# Copy application code
COPY . .

# Cloud Run injects PORT; use 8000 for local containers.
CMD ["sh", "-c", "uvicorn chat_server:app --host 0.0.0.0 --port ${PORT:-8000}"]
