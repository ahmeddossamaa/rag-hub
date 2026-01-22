from dataclasses import dataclass

from src.clients.vector_db.base import SearchResult
from src.services.generator import Generator
from src.services.retriever import Retriever


@dataclass
class RAGResponse:
    answer: str
    sources: list[SearchResult]


class RAGEngine:
    def __init__(self, retriever: Retriever, generator: Generator):
        self._retriever = retriever
        self._generator = generator

    async def query(self, question: str) -> RAGResponse:
        # Retrieve relevant context
        sources = await self._retriever.retrieve(question)
        
        # Generate answer
        answer = await self._generator.generate(question, sources)
        
        return RAGResponse(answer=answer, sources=sources)
