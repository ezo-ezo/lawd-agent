import os
from dotenv import load_dotenv # type: ignore
from openai import AsyncOpenAI

load_dotenv()


class LLMClient:
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None
    
    def get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
            )
        return self._client
    
    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None