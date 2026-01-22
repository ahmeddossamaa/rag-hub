from src.clients.vector_db.base import BaseVectorDBClient, SearchResult
from src.services.embedder import Embedder


class Retriever:
    def __init__(self, vector_db: BaseVectorDBClient, embedder: Embedder, top_k: int = 3):
        self._vector_db = vector_db
        self._embedder = embedder
        self._top_k = top_k

    async def retrieve(self, query: str) -> list[SearchResult]:
        query_vector = await self._embedder.embed(query)
        return await self._vector_db.search(query_vector, limit=self._top_k)
