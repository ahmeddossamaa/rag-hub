from typing import Optional
from uuid import uuid4

import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.query import MetadataQuery

from src.clients.vector_db.base import BaseVectorDBClient, SearchResult


class WeaviateClient(BaseVectorDBClient):
    def __init__(self, url: str, collection_name: str, dimensions: int = 768):
        self._url = url
        self._collection_name = collection_name
        self._dimensions = dimensions
        self._client: Optional[weaviate.WeaviateClient] = None

    async def connect(self) -> None:
        self._client = weaviate.connect_to_local(
            host=self._url.replace("http://", "").split(":")[0],
            port=int(self._url.split(":")[-1]),
        )
        await self._ensure_collection()

    async def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        if not self._client.collections.exists(self._collection_name):
            self._client.collections.create(
                name=self._collection_name,
                vectorizer_config=Configure.Vectorizer.none(),
                properties=[
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                    Property(name="chunk_index", data_type=DataType.INT),
                ],
            )

    async def disconnect(self) -> None:
        if self._client:
            self._client.close()

    async def search(self, vector: list[float], limit: int = 3) -> list[SearchResult]:
        collection = self._client.collections.get(self._collection_name)
        results = collection.query.near_vector(
            near_vector=vector,
            limit=limit,
            return_metadata=MetadataQuery(distance=True),
        )
        return [
            SearchResult(
                content=obj.properties.get("content", ""),
                metadata={
                    "source": obj.properties.get("source", ""),
                    "chunk_index": obj.properties.get("chunk_index", 0),
                },
                score=1 - (obj.metadata.distance or 0),  # Convert distance to similarity
            )
            for obj in results.objects
        ]

    async def insert(self, content: str, vector: list[float], metadata: dict) -> str:
        collection = self._client.collections.get(self._collection_name)
        doc_id = str(uuid4())
        collection.data.insert(
            properties={"content": content, **metadata},
            vector=vector,
            uuid=doc_id,
        )
        return doc_id

    async def insert_batch(
        self, contents: list[str], vectors: list[list[float]], metadatas: list[dict]
    ) -> list[str]:
        collection = self._client.collections.get(self._collection_name)
        doc_ids = []
        with collection.batch.dynamic() as batch:
            for content, vector, metadata in zip(contents, vectors, metadatas):
                doc_id = str(uuid4())
                batch.add_object(
                    properties={"content": content, **metadata},
                    vector=vector,
                    uuid=doc_id,
                )
                doc_ids.append(doc_id)
        return doc_ids
