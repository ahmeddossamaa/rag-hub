from src.clients.embeddings.base import BaseEmbeddingClient
from src.clients.embeddings.gemini import GeminiEmbeddingClient
from src.clients.llm.base import BaseLLMClient
from src.clients.llm.gemini import GeminiLLMClient
from src.clients.vector_db.base import BaseVectorDBClient, SearchResult
from src.providers.rag_provider import RAGProvider


class GeminiRAGProvider(RAGProvider):
    """RAG provider using Gemini for embeddings and generation."""

    def __init__(
        self,
        api_key: str,
        vector_db: BaseVectorDBClient,
        llm_model: str = "gemini-1.5-flash",
        embedding_model: str = "text-embedding-004",
    ):
        self._embedding_client: BaseEmbeddingClient = GeminiEmbeddingClient(
            api_key=api_key, model=embedding_model
        )
        self._llm_client: BaseLLMClient = GeminiLLMClient(
            api_key=api_key, model=llm_model
        )
        self._vector_db = vector_db

    async def embed(self, text: str) -> list[float]:
        """Convert text to embedding vector using Gemini."""
        return await self._embedding_client.embed(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Convert multiple texts to embedding vectors using Gemini."""
        return await self._embedding_client.embed_batch(texts)

    async def retrieve(
        self, query_vector: list[float], top_k: int = 3
    ) -> list[SearchResult]:
        """Retrieve similar documents from vector store."""
        return await self._vector_db.search(query_vector, limit=top_k)

    async def generate(self, prompt: str) -> str:
        """Generate text from a prompt using Gemini."""
        return await self._llm_client.generate(prompt)

    @property
    def embedding_dimensions(self) -> int:
        """Return the dimensionality of Gemini embeddings."""
        return self._embedding_client.dimensions
