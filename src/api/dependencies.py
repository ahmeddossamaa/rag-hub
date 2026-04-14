from typing import Optional

from src.clients.slack_client import SlackClient
from src.clients.vector_db.weaviate import WeaviateClient
from src.config import Settings
from src.core.rag_engine import RAGEngine
from src.providers import GeminiRAGProvider, RAGProvider

# Global instances (initialized at startup)
_rag_engine: Optional[RAGEngine] = None
_rag_provider: Optional[RAGProvider] = None
_weaviate_client: Optional[WeaviateClient] = None
_slack_client: Optional[SlackClient] = None


async def init_clients(settings: Settings) -> None:
    global _rag_engine, _rag_provider, _weaviate_client, _slack_client

    # Initialize vector DB client
    _weaviate_client = WeaviateClient(
        url=settings.weaviate_url,
        collection_name=settings.weaviate_collection,
        dimensions=settings.embedding_dimensions,
    )
    await _weaviate_client.connect()

    # Initialize RAG provider (swappable - currently Gemini)
    _rag_provider = GeminiRAGProvider(
        api_key=settings.gemini_api_key,
        vector_db=_weaviate_client,
        llm_model=settings.gemini_model,
        embedding_model=settings.gemini_embedding_model,
    )

    # Initialize RAG engine with provider
    _rag_engine = RAGEngine(
        provider=_rag_provider,
        top_k=settings.retrieval_top_k,
    )

    # Initialize Slack client
    _slack_client = SlackClient(
        bot_token=settings.slack_bot_token,
        signing_secret=settings.slack_signing_secret,
    )


async def shutdown_clients() -> None:
    global _weaviate_client
    if _weaviate_client:
        await _weaviate_client.disconnect()


def get_rag_engine() -> RAGEngine:
    if _rag_engine is None:
        raise RuntimeError("RAG engine not initialized")
    return _rag_engine


def get_weaviate_client() -> WeaviateClient:
    if _weaviate_client is None:
        raise RuntimeError("Weaviate client not initialized")
    return _weaviate_client


def get_rag_provider() -> RAGProvider:
    if _rag_provider is None:
        raise RuntimeError("RAG provider not initialized")
    return _rag_provider


def get_slack_client() -> SlackClient:
    if _slack_client is None:
        raise RuntimeError("Slack client not initialized")
    return _slack_client
