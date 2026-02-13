import os
from typing import Any, AsyncGenerator
from dotenv import load_dotenv
from openai import AsyncOpenAI

from client.response import StreamEvent, TextDelta, TokenUsage, StreamEventType

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
    ) -> AsyncGenerator[StreamEvent, None]:
        client = self.get_client()

        kwargs = {
            "model":"google/gemma-3n-e4b-it:free",
            "messages": messages,
            "stream": stream,
        }

        if stream:
            self._stream_response()
        else:
            event = await self._non_stream_response(client, kwargs)
            yield event

    async def _stream_response(self):
        pass

    async def _non_stream_response(
        self,
        client: AsyncOpenAI,
        kwargs: dict[str, Any],            
    ) -> StreamEvent:
        response = await client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        messege = choice.message

        text_delta = None
        if messege.content:
            text_delta = TextDelta(content = messege.content)

        if response.usage:
            usage = TokenUsage(
                prompt_tokens = response.usage.prompt_tokens,
                completion_tokens = response.usage.completion_tokens,
                total_tokens = response.usage.total_tokens,
                cached_tokens = response.usage.prompt_tokens_details.cached_tokens,
            )
        
        return StreamEvent(
            type=StreamEventType.MESSAGE_COMPLETE,
            text_delta=text_delta,
            finish_reason=choice.finish_reason,
            usage=usage
        )