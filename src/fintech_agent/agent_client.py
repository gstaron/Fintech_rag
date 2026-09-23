"""Minimal tool-calling agent that talks to the fintech MCP server.

Connects to mcp_server.py over stdio, asks the LLM (via fintech_rag.llm) to
decide which tool(s) to call for a given user question, executes them
through the MCP server, and feeds results back until the model produces a
final answer. Every step is printed to stdout -- the trace is the point:
"what did the agent try, and did it correctly escalate instead of guessing"
is the actual story to bring to an interview.
"""
from __future__ import annotations

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from fintech_rag.llm import get_provider

MAX_TOOL_ROUNDS = 4

SYSTEM_PROMPT = (
    "Si AI agent pre podporu Alpine Bank. Mas k dispozicii nastroje: "
    "rag_search (fakty z internej dokumentacie a regulacii), roi_calculator "
    "(odhad uspor z automatizacie podpory), request_human_review (eskalacia "
    "na cloveka -- POUZI VZDY, ked by akcia menila cokolvek na konkretnom "
    "ucte alebo uverovom rozhodnuti zakaznika; takuto akciu sam nikdy "
    "nevykonavaj ani nepredstieraj, ze bola vykonana). Nastroje pouzivaj "
    "namiesto hadania faktov alebo cisiel."
)


def mcp_tool_to_openai_schema(tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        },
    }


async def run_agent(question: str) -> str:
    server_params = StdioServerParameters(command=sys.executable, args=["-m", "fintech_agent.mcp_server"])
    provider = get_provider()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_resp = await session.list_tools()
            tool_schemas = [mcp_tool_to_openai_schema(t) for t in tools_resp.tools]
            print(f"[agent] dostupne MCP nastroje: {[t.name for t in tools_resp.tools]}")

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ]

            for round_i in range(MAX_TOOL_ROUNDS):
                result = provider.chat_with_tools(messages, tool_schemas)
                if not result.tool_calls:
                    print(f"[agent] finalna odpoved po {round_i} kolach volania nastrojov")
                    return result.content

                messages.append(
                    {
                        "role": "assistant",
                        "content": result.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": tc.name, "arguments": json.dumps(tc.arguments, ensure_ascii=False)},
                            }
                            for tc in result.tool_calls
                        ],
                    }
                )

                for tc in result.tool_calls:
                    print(f"[agent] volam nastroj: {tc.name}({tc.arguments})")
                    tool_result = await session.call_tool(tc.name, tc.arguments)
                    text = "\n".join(block.text for block in tool_result.content if hasattr(block, "text"))
                    print(f"[agent] vysledok nastroja: {text[:200]}")
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": text})

            return "[agent] Dosiahnuty limit kol volania nastrojov bez finalnej odpovede."


def main() -> None:
    if len(sys.argv) < 2:
        print('Pouzitie: python -m fintech_agent.agent_client "otazka"')
        sys.exit(1)
    question = " ".join(sys.argv[1:])
    answer = asyncio.run(run_agent(question))
    print("\n=== FINALNA ODPOVED ===")
    print(answer)


if __name__ == "__main__":
    main()
