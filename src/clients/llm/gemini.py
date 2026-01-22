import google.generativeai as genai

from src.clients.llm.base import BaseLLMClient


class GeminiLLMClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)

    async def generate(self, prompt: str) -> str:
        response = await self._model.generate_content_async(prompt)
        return response.text
