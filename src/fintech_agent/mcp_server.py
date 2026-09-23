"""MCP server exposing tools for the fintech support agent demo.

Run standalone for manual/debug testing:
    python -m fintech_agent.mcp_server
Normally it's spawned as a subprocess by agent_client.py over stdio, which
is the whole point of MCP here: the tool implementations (RAG search, a
calculator, a human-review queue) are decoupled from whichever agent/LLM
loop calls them.
"""
from __future__ import annotations

import json

from mcp.server.mcpserver import MCPServer

from fintech_rag.config import RESULTS_DIR
from fintech_rag.rag import ask

server = MCPServer("fintech-agent-tools")

REVIEW_QUEUE_PATH = RESULTS_DIR / "human_review_queue.jsonl"


@server.tool()
def rag_search(query: str) -> str:
    """Search the fintech/bank knowledge base and return a grounded answer with sources.

    Use for any factual question about regulation (EU AI Act, DORA, GDPR),
    internal Alpine Bank AI policy, or the customer support FAQ.
    """
    result = ask(query)
    if result.refused:
        return result.answer
    sources = ", ".join(result.sources)
    return f"{result.answer}\n\n[zdroje: {sources}]"


@server.tool()
def roi_calculator(
    tickets_per_month: int,
    current_cost_per_ticket_eur: float,
    ai_cost_per_ticket_eur: float,
    automation_rate: float,
) -> str:
    """Estimate monthly/annual savings from automating a share of support tickets with AI.

    automation_rate is a fraction between 0 and 1 (e.g. 0.3 for 30%).
    """
    automated = tickets_per_month * automation_rate
    savings_per_ticket = current_cost_per_ticket_eur - ai_cost_per_ticket_eur
    monthly_savings = automated * savings_per_ticket
    annual_savings = monthly_savings * 12
    return (
        f"Automatizovanych ticketov/mesiac: {automated:.0f}\n"
        f"Uspora na ticket: {savings_per_ticket:.2f} EUR\n"
        f"Odhadovana mesacna uspora: {monthly_savings:.2f} EUR\n"
        f"Odhadovana rocna uspora: {annual_savings:.2f} EUR\n"
        "(Hruby odhad bez nakladov na implementaciu, monitoring a queue pre "
        "human review -- pouzit len ako vychodiskovy bod pre business case, "
        "nie ako finalne cislo.)"
    )


@server.tool()
def request_human_review(reason: str, payload: str) -> str:
    """Escalate to a human instead of taking or recommending an action directly.

    Use whenever a request would change something about a specific
    customer's account, money, or credit decision -- the agent must never
    execute or claim to have executed such an action itself. This is the
    human-in-the-loop guardrail described in docs/bank_ai_policy.md.
    """
    REVIEW_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {"reason": reason, "payload": payload}
    with REVIEW_QUEUE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return (
        "Poziadavka bola zaradena do fronty na ludske schvalenie a NEBOLA "
        f"vykonana automaticky. Dovod eskalacie: {reason}"
    )


if __name__ == "__main__":
    server.run()
