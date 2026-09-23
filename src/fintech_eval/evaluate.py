"""Run the eval set through the RAG pipeline and produce a report.

Metrics computed (deliberately cheap and provider-agnostic where possible,
so they still mean something in offline/no-LLM mode):

- retrieval hit rate: did the retrieved chunks include >=1 chunk from an
  expected source document?
- keyword coverage: crude proxy for answer correctness -- does the
  generated answer contain the expected keyword(s)? No LLM judge required.
- refusal correctness: for questions marked unanswerable, did the system
  correctly decline instead of inventing an answer? This is the
  hallucination check.
- latency per question.
- token usage & estimated cost (only meaningful with a real LLM provider).

This is intentionally simpler than a framework like ragas -- good enough to
generate real "what broke and why" talking points for an interview, not
meant as a production eval suite.
"""
from __future__ import annotations

import json
import unicodedata
from dataclasses import asdict, dataclass

from fintech_rag.config import INDEX_PATH, RESULTS_DIR
from fintech_rag.llm import get_provider
from fintech_rag.rag import ask
from fintech_rag.vector_store import VectorStore

from .dataset import EVAL_SET, EvalItem

# USD per 1M tokens. Illustrative placeholders -- edit to match whatever
# your actual contracted pricing is before you quote a cost number out loud
# in an interview.
PRICE_PER_1M_INPUT = {"gpt-4o-mini": 0.15, "gpt-4o": 2.50}
PRICE_PER_1M_OUTPUT = {"gpt-4o-mini": 0.60, "gpt-4o": 10.00}

REFUSAL_SIGNALS = [
    "nenasiel", "nenašiel", "nemam informaciu", "nemám informáciu",
    "nie je v podkladoch", "neviem",
]


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return s.lower()


@dataclass
class EvalResult:
    question: str
    note: str
    answerable: bool
    retrieval_hit: bool
    keyword_hit: bool
    refused: bool
    refusal_correct: bool
    latency_s: float
    prompt_tokens: int
    completion_tokens: int
    est_cost_usd: float
    answer_preview: str


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    p_in = PRICE_PER_1M_INPUT.get(model)
    p_out = PRICE_PER_1M_OUTPUT.get(model)
    if p_in is None or p_out is None:
        return 0.0
    return (prompt_tokens / 1_000_000) * p_in + (completion_tokens / 1_000_000) * p_out


def evaluate_item(item: EvalItem, store: VectorStore) -> EvalResult:
    result = ask(item.question, store=store)
    retrieved_sources = {c.source for c, _ in result.retrieved}

    retrieval_hit = bool(retrieved_sources & set(item.expected_sources)) if item.answerable else True

    normalized_answer = _norm(result.answer)
    keyword_hit = (
        all(_norm(k) in normalized_answer for k in item.expect_keywords) if item.answerable else True
    )

    looks_like_refusal = result.refused or any(sig in normalized_answer for sig in REFUSAL_SIGNALS)
    refusal_correct = looks_like_refusal == (not item.answerable)

    cost = estimate_cost(
        result.chat_result.model, result.chat_result.prompt_tokens, result.chat_result.completion_tokens
    )

    return EvalResult(
        question=item.question,
        note=item.note,
        answerable=item.answerable,
        retrieval_hit=retrieval_hit,
        keyword_hit=keyword_hit,
        refused=result.refused,
        refusal_correct=refusal_correct,
        latency_s=result.chat_result.latency_s,
        prompt_tokens=result.chat_result.prompt_tokens,
        completion_tokens=result.chat_result.completion_tokens,
        est_cost_usd=cost,
        answer_preview=result.answer[:160].replace("\n", " "),
    )


def run_evaluation() -> list[EvalResult]:
    store = VectorStore.load(INDEX_PATH)
    provider = get_provider()
    if not store.chunks:
        raise RuntimeError("Index is empty -- run `python -m fintech_rag.cli ingest` first.")

    results = [evaluate_item(item, store) for item in EVAL_SET]

    n = len(results)
    retrieval_acc = sum(r.retrieval_hit for r in results) / n
    keyword_acc = sum(r.keyword_hit for r in results) / n
    refusal_acc = sum(r.refusal_correct for r in results) / n
    avg_latency = sum(r.latency_s for r in results) / n
    total_cost = sum(r.est_cost_usd for r in results)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "eval_report.json").write_text(
        json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        f"# Eval report (provider={provider.name})",
        "",
        f"- Questions: {n}",
        f"- Retrieval hit rate: {retrieval_acc:.0%}",
        f"- Keyword coverage (proxy for correctness): {keyword_acc:.0%}",
        f"- Refusal correctness (hallucination guardrail): {refusal_acc:.0%}",
        f"- Avg latency: {avg_latency:.2f}s",
        f"- Est. total cost for this run: ${total_cost:.4f}",
        "",
        "| Question | answerable | retrieval_hit | keyword_hit | refusal_correct | latency_s | cost_usd |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        q = r.question[:60].replace("|", "/")
        lines.append(
            f"| {q}... | {r.answerable} | {r.retrieval_hit} | {r.keyword_hit} | "
            f"{r.refusal_correct} | {r.latency_s:.2f} | {r.est_cost_usd:.5f} |"
        )
    (RESULTS_DIR / "eval_report.md").write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines[:8]))
    print(f"\nFull report written to {RESULTS_DIR / 'eval_report.md'}")
    return results


if __name__ == "__main__":
    run_evaluation()
