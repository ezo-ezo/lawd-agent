from client.llm_client import LLMClient
from openai import RateLimitError 
import asyncio
import os

async def main():
    client = LLMClient()
    messages = [{"role": "user", "content": "What's up"}]

    try:
        await client.chat_completion(messages, False)
    except RateLimitError:
        print("Rate limited. Retrying in 5 seconds...")
        await asyncio.sleep(5)
        await client.chat_completion(messages, False)

    print('done')


    

asyncio.run(main())