import google.generativeai as genai

from src.clients.embeddings.base import BaseEmbeddingClient


class GeminiEmbeddingClient(BaseEmbeddingClient):
    def __init__(self, api_key: str, model: str = "text-embedding-004"):
        genai.configure(api_key=api_key)
        self._model = model
        self._dimensions = 768  # text-embedding-004 outputs 768 dimensions

    async def embed(self, text: str) -> list[float]:
        result = genai.embed_content(model=f"models/{self._model}", content=text)
        return result["embedding"]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # Gemini supports batch embedding
        result = genai.embed_content(model=f"models/{self._model}", content=texts)
        return result["embedding"]

    @property
    def dimensions(self) -> int:
        return self._dimensions
