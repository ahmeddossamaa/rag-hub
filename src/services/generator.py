from src.clients.llm.base import BaseLLMClient
from src.clients.vector_db.base import SearchResult


class Generator:
    SYSTEM_PROMPT = """You are a HIPAA compliance assistant. Answer questions ONLY based on the provided context.

Rules:
- If the context doesn't contain enough information, say "I don't have enough information to answer that question."
- Always cite the source (HIPAA section numbers) when possible.
- Be concise and specific.
- Do not make up information not present in the context.

Context:
{context}

Question: {question}

Answer:"""

    def __init__(self, llm_client: BaseLLMClient):
        self._llm = llm_client

    async def generate(self, question: str, context: list[SearchResult]) -> str:
        context_text = "\n\n".join(
            f"[Source: {r.metadata.get('source', 'Unknown')}]\n{r.content}" for r in context
        )
        prompt = self.SYSTEM_PROMPT.format(context=context_text, question=question)
        return await self._llm.generate(prompt)
