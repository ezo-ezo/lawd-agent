import asyncio
import os
from typing import Any, AsyncGenerator
from dotenv import load_dotenv
from openai import APIConnectionError, APIError, AsyncOpenAI, RateLimitError

from client.response import StreamEvent, TextDelta, TokenUsage, StreamEventType

load_dotenv()


class LLMClient:
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None
        self._max_retires: int = 3
    
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

        #ERROR HANDLING WITH EXPONENTIAL BACKOFF
        for attempt in range(self._max_retires + 1):    
            try:
                if stream:
                    async for event in self._stream_response(client, kwargs):
                        yield event
                else:
                    event = await self._non_stream_response(client, kwargs)
                    yield event
                return
            except RateLimitError as e:
                if attempt < self._max_retires:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    yield StreamEvent(
                        type = StreamEventType.ERROR,
                        error = f"Rate limit exceeded: {e}",
                    )
                    return
            except APIConnectionError as e:
                if attempt < self._max_retires:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    yield StreamEvent(
                        type = StreamEventType.ERROR,
                        error = f"Connection error: {e}",
                    )
                    return
            except APIError as e:    
                yield StreamEvent(
                    type = StreamEventType.ERROR,
                    error = f"API error: {e}",
                )
                return
            
    async def _stream_response(
        self,
        client: AsyncOpenAI,
        kwargs: dict[str, Any],
    ) -> AsyncGenerator[StreamEvent, None]:
        response = await client.chat.completions.create(**kwargs)
        
        usage: TokenUsage |None = None
        delta: TextDelta | None = None
        finish_reason: str | None = None

        async for chunk in response:
            if hasattr(chunk, "usage") and chunk.usage:
                usage = TokenUsage(
                    prompt_tokens = chunk.usage.prompt_tokens,
                    completion_tokens = chunk.usage.completion_tokens,
                    total_tokens = chunk.usage.total_tokens,
                    cached_tokens = chunk.usage.prompt_tokens_details.cached_tokens,
                )

            if not chunk.choices:
                continue

            choice = chunk.choices[0]
            delta = choice.delta

            if choice.finish_reason:
                finish_reason = choice.finish_reason
                
            if delta.content:
                yield StreamEvent(
                    type = StreamEventType.TEXT_DELTA,
                    text_delta = TextDelta(content = delta.content),
                )

        yield StreamEvent(
            type = StreamEventType.MESSAGE_COMPLETE,
            finish_reason = finish_reason,
            usage = usage,
        )

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