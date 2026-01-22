from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.dependencies import init_clients, shutdown_clients
from src.api.routes import health, query, slack
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
    settings = get_settings()
    
    app = FastAPI(
        title="HIPAA Bot API",
        description="RAG-powered HIPAA compliance bot",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Include routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(query.router, prefix="/query", tags=["Query"])
    app.include_router(slack.router, prefix="/slack", tags=["Slack"])

    return app


app = create_app()
