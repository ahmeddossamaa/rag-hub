from abc import ABC, abstractmethod

from src.clients.vector_db.base import SearchResult


class RAGProvider(ABC):
    """Abstract interface for RAG providers.

    Enables swapping between different LLM backends (Gemini, Claude, etc.)
    without changing business logic. Each provider handles:
    - Text embedding
    - Vector retrieval
    - Text generation
    """

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Convert text to embedding vector."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Convert multiple texts to embedding vectors."""
        pass

    @abstractmethod
    async def retrieve(
        self, query_vector: list[float], top_k: int = 3
    ) -> list[SearchResult]:
        """Retrieve similar documents from vector store."""
        pass

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        pass

    @property
    @abstractmethod
    def embedding_dimensions(self) -> int:
        """Return the dimensionality of embeddings."""
        pass

    async def retrieve_with_query(
        self, query: str, top_k: int = 3
    ) -> list[SearchResult]:
        """Convenience method: embed query and retrieve in one call."""
        query_vector = await self.embed(query)
        return await self.retrieve(query_vector, top_k)
