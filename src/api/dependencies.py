from typing import Optional

from src.clients.embeddings.gemini import GeminiEmbeddingClient
from src.clients.llm.gemini import GeminiLLMClient
from src.clients.vector_db.weaviate import WeaviateClient
from src.config import Settings
from src.core.rag_engine import RAGEngine
from src.services.embedder import Embedder
from src.services.generator import Generator
from src.services.retriever import Retriever

# Global instances (initialized at startup)
_rag_engine: Optional[RAGEngine] = None
_weaviate_client: Optional[WeaviateClient] = None


async def init_clients(settings: Settings) -> None:
    global _rag_engine, _weaviate_client

    # Initialize clients
    llm_client = GeminiLLMClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )
    embedding_client = GeminiEmbeddingClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_embedding_model,
    )
    _weaviate_client = WeaviateClient(
        url=settings.weaviate_url,
        collection_name=settings.weaviate_collection,
        dimensions=settings.embedding_dimensions,
    )
    await _weaviate_client.connect()

    # Initialize services
    embedder = Embedder(embedding_client)
    retriever = Retriever(_weaviate_client, embedder, top_k=settings.retrieval_top_k)
    generator = Generator(llm_client)

    # Initialize RAG engine
    _rag_engine = RAGEngine(retriever, generator)


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
