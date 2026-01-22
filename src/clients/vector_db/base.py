from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SearchResult:
    content: str
    metadata: dict
    score: float


class BaseVectorDBClient(ABC):
    """Abstract interface for vector database clients."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the database."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the database."""
        pass

    @abstractmethod
    async def search(self, vector: list[float], limit: int = 3) -> list[SearchResult]:
        """Search for similar vectors."""
        pass

    @abstractmethod
    async def insert(self, content: str, vector: list[float], metadata: dict) -> str:
        """Insert a document with its vector. Returns document ID."""
        pass

    @abstractmethod
    async def insert_batch(
        self, contents: list[str], vectors: list[list[float]], metadatas: list[dict]
    ) -> list[str]:
        """Insert multiple documents. Returns list of document IDs."""
        pass
