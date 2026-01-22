from src.clients.embeddings.base import BaseEmbeddingClient


class Embedder:
    def __init__(self, embedding_client: BaseEmbeddingClient):
        self._client = embedding_client

    async def embed(self, text: str) -> list[float]:
        return await self._client.embed(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return await self._client.embed_batch(texts)

    @property
    def dimensions(self) -> int:
        return self._client.dimensions
