from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Abstract interface for LLM clients. Swap implementations without changing business logic."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        pass
