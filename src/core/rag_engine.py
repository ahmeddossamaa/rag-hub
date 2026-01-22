from dataclasses import dataclass

from src.clients.vector_db.base import SearchResult
from src.providers.rag_provider import RAGProvider
from src.services.generator import PromptBuilder


@dataclass
class RAGResponse:
    answer: str
    sources: list[SearchResult]


class RAGEngine:
    def __init__(
        self,
        provider: RAGProvider,
        prompt_builder: PromptBuilder | None = None,
        top_k: int = 3,
    ):
        self._provider = provider
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._top_k = top_k

    async def query(self, question: str) -> RAGResponse:
        # Retrieve relevant context using provider
        sources = await self._provider.retrieve_with_query(question, top_k=self._top_k)

        # Build prompt with context
        prompt = self._prompt_builder.build_prompt(question, sources)

        # Generate answer using provider
        answer = await self._provider.generate(prompt)

        return RAGResponse(answer=answer, sources=sources)
