from client.llm_client import LLMClient
from openai import RateLimitError 
from client.response import StreamEvent, TextDelta, TokenUsage, StreamEventType
import asyncio
import os

async def main():
    client = LLMClient()
    messages = [{"role": "user", "content": "What's up"}]

    try:
        async for event in client.chat_completion(messages, False):
            print(event)
    except RateLimitError:
        print("Rate limited. Retrying in 5 seconds...")
        await asyncio.sleep(5)
        async for event in client.chat_completion(messages, False):
            print(event)
    print('done')


    

asyncio.run(main())