
import sys
from openai import RateLimitError 
from agent.agent import Agent
from agent.events import AgentEventType
from client.response import StreamEvent, TextDelta, TokenUsage, StreamEventType
import asyncio
import os
import click

from ui.tui import TUI, get_console

console = get_console()

class CLI:
    def __init__(self):
        self.agent: Agent | None = None
        self.tui = TUI()

    async def run_single(self, message: str | None = None) -> str | None:
        async with Agent() as agent:
            self.agent = agent
            return await self._process_meessage(message)

    async def _process_meessage(self, message: str) -> str | None:
        if not self.agent:
            return None
        
        async for event in self.agent.run(message):
            if event.type == AgentEventType.TEXT_DELTA:
                content = event.data.get("content", "")
                self.tui.stream_asssitant_delta(content)


                


@click.command()
@click.argument("prompt", required=False)
def main(
    prompt: str | None = None,
):
    cli = CLI()
    # messages = [{"role": "user", "content": prompt }]
    if prompt:
        result = asyncio.run(cli.run_single(prompt))
        if result is None:
            sys.exit(1)
    
main()