FROM python:3.12.3-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .

# Install dependencies
RUN uv sync

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Default command (overridden in docker-compose)
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
