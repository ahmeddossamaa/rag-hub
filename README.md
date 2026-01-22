# HIPAA Slack Bot

A HIPAA compliance Slack bot using RAG (Retrieval-Augmented Generation) with FastAPI, Weaviate, and Google Gemini.

## Prerequisites

- Docker and Docker Compose
- Google Gemini API Key
- Slack Bot Token and Signing Secret (for Slack integration)

## Setup

1.  **Environment Variables**:
    Copy `.env.example` to `.env` and fill in your API keys.
    ```bash
    cp .env.example .env
    # Edit .env
    ```

2.  **Start Services**:
    Run the following command to start Weaviate, FastAPI, and Nginx:
    ```bash
    docker compose up --build -d
    ```

3.  **Ingest Documents**:
    Place your HIPAA text documents (`.txt`) in `data/hipaa_docs/` and run the ingestion script inside the container:
    ```bash
    docker compose exec fastapi uv run python scripts/ingest_docs.py
    ```

4.  **Test Query**:
    You can test the RAG endpoint locally:
    ```bash
    docker compose exec fastapi uv run python scripts/test_query.py "What is PHI?"
    ```

## API Endpoints

-   **Health Check**: `http://localhost:80/health`
-   **Query (RAG)**: `POST http://localhost:8000/query`
-   **Slack Events**: `POST http://localhost:8000/slack/events`

## Development

The `src` directory is mounted into the container, so changes will trigger a reload.
