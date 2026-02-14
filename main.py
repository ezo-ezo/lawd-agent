
from openai import RateLimitError 
from client.response import StreamEvent, TextDelta, TokenUsage, StreamEventType
import asyncio
import os
import click

class CLI:
    def __init__(self):
        pass

    def run_single(self):
        pass

    

@click.command()
@click.argument("prompt", required=False)
def main(
    prompt: str | None = None,
):
    print(prompt)
    messages = [{"role": "user", "content": prompt }]
    asyncio.run(run(messages))
    print('done')


    
main()