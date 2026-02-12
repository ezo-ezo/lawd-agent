import os
from typing import Any
from dotenv import load_dotenv
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
    
    async def chat_completion(
            self,
            messages: list[dict[str, Any]],
            stream: bool = True,       
    ):
        client = self.get_client()

        kwargs = {
            "model":"google/gemma-3n-e4b-it:free",
            "messages": messages,
            "stream": stream,
        }

        if stream:
            self._stream_response()
        else:
            await self._non_stream_response(client, kwargs)

    async def _stream_response(self):
        pass

    async def _non_stream_response(
        self,
        client: AsyncOpenAI,
        kwargs: dict[str, Any],            
    ):
        response = await client.chat.completions.create(**kwargs)
        print(response)