"""RAG query pipeline: retrieve -> guardrail -> generate with citations."""
from __future__ import annotations

from dataclasses import dataclass

from .config import INDEX_PATH, settings
from .llm import ChatResult, get_provider
from .vector_store import Chunk, VectorStore

SYSTEM_PROMPT = (
    "Si asistent pre interne otazky fintech/bankoveho timu. Odpovedaj "
    "VYHRADNE na zaklade poskytnuteho kontextu. Ak kontext otazku "
    "nepokryva, jasne napis, ze informaciu v podkladoch nemas -- nikdy si "
    "nevymyslaj fakty ani cisla. Za kazdym tvrdenim uved zdroj v tvare "
    "[zdroj: <subor>]."
)

# Below this cosine-similarity score the top retrieved chunk is treated as
# "not actually relevant" and the system refuses instead of forcing the LLM
# to answer from weak context -- the cheapest anti-hallucination guardrail
# there is, and worth having even before any LLM-based check.
REFUSAL_SIMILARITY_THRESHOLD = 0.15


@dataclass
class RAGAnswer:
    answer: str
    sources: list[str]
    retrieved: list[tuple[Chunk, float]]
    chat_result: ChatResult
    refused: bool


def build_prompt(question: str, retrieved: list[tuple[Chunk, float]]) -> str:
    context = "\n\n".join(f"[zdroj: {c.source}]\n{c.text}" for c, _ in retrieved)
    return f"Kontext:\n{context}\n\nOtazka: {question}\n\nOdpoved:"


def ask(question: str, store: VectorStore | None = None, top_k: int | None = None) -> RAGAnswer:
    provider = get_provider()
    store = store or VectorStore.load(INDEX_PATH)
    top_k = top_k or settings.top_k

    query_vec = provider.embed([question])[0]
    retrieved = store.search(query_vec, top_k=top_k)

    if not retrieved or retrieved[0][1] < REFUSAL_SIMILARITY_THRESHOLD:
        return RAGAnswer(
            answer="V podkladoch som nenasiel relevantnu informaciu k tejto otazke.",
            sources=[],
            retrieved=retrieved,
            chat_result=ChatResult(text="", model=provider.name),
            refused=True,
        )

    prompt = build_prompt(question, retrieved)
    chat_result = provider.chat(SYSTEM_PROMPT, prompt)
    sources = sorted({c.source for c, _ in retrieved})
    return RAGAnswer(
        answer=chat_result.text,
        sources=sources,
        retrieved=retrieved,
        chat_result=chat_result,
        refused=False,
    )
