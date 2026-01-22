from src.clients.vector_db.base import SearchResult


class PromptBuilder:
    """Builds prompts for RAG generation. Will be replaced by PromptManager in Phase 3."""

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

    def build_prompt(self, question: str, context: list[SearchResult]) -> str:
        """Build the full prompt from question and retrieved context."""
        context_text = "\n\n".join(
            f"[Source: {r.metadata.get('source', 'Unknown')}]\n{r.content}"
            for r in context
        )
        return self.SYSTEM_PROMPT.format(context=context_text, question=question)


# Backwards compatibility alias
Generator = PromptBuilder
