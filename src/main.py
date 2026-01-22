from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.dependencies import init_clients, shutdown_clients
from src.api.routes import health, query, webhooks
from src.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    await init_clients(settings)
    yield
    # Shutdown
    await shutdown_clients()


def create_app() -> FastAPI:
    app = FastAPI(
        title="DocuBase Bot API",
        description="Multi-bot RAG platform for compliance and documentation",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Health check (no version prefix)
    app.include_router(health.router, tags=["Health"])

    # API v1 routes
    app.include_router(
        query.router,
        prefix="/api/v1/query",
        tags=["Query"],
    )
    app.include_router(
        webhooks.router,
        prefix="/api/v1/webhooks",
        tags=["Webhooks"],
    )

    return app


app = create_app()
