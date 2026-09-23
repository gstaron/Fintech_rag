"""Small hand-written eval set over the fintech demo documents.

Each item is either answerable (grounded in one or more source docs) or
intentionally unanswerable (to test refusal / hallucination behaviour --
the trap questions matter as much as the easy ones). A couple of items
require synthesising two documents, which is where naive top-k retrieval
most often quietly fails.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvalItem:
    question: str
    expected_sources: list[str]
    expect_keywords: list[str]
    answerable: bool
    note: str = ""


EVAL_SET: list[EvalItem] = [
    EvalItem(
        question="Ktore AI systemy vo financnom sektore EU AI Act klasifikuje ako vysoko rizikove?",
        expected_sources=["eu_ai_act_summary.md"],
        expect_keywords=["uver"],
        answerable=True,
    ),
    EvalItem(
        question="Ake su hlavne poziadavky DORA na riadenie rizika tretich stran (ICT dodavatelov)?",
        expected_sources=["dora_summary.md"],
        expect_keywords=["register"],
        answerable=True,
    ),
    EvalItem(
        question="Kedy nadobuda DORA ucinnost a na koho sa vztahuje?",
        expected_sources=["dora_summary.md"],
        expect_keywords=["2025"],
        answerable=True,
    ),
    EvalItem(
        question="Co hovori GDPR o automatizovanom rozhodovani a co to znamena pre AI schvalovanie uverov?",
        expected_sources=["gdpr_ai_summary.md"],
        expect_keywords=["ludsk"],
        answerable=True,
    ),
    EvalItem(
        question="Smiu sa do promptu pre externe LLM API posielat nemaskovane cisla platobnych kariet?",
        expected_sources=["bank_ai_policy.md"],
        expect_keywords=["nesm"],
        answerable=True,
    ),
    EvalItem(
        question="Ake su tri urovne (tiery) klasifikacie GenAI use casov v internej politike Alpine Bank?",
        expected_sources=["bank_ai_policy.md"],
        expect_keywords=["tier"],
        answerable=True,
    ),
    EvalItem(
        question="Ako zablokujem stratenu platobnu kartu v Alpine Bank a kolko stoji expresne vydanie novej?",
        expected_sources=["customer_support_faq.md"],
        expect_keywords=["15"],
        answerable=True,
    ),
    EvalItem(
        question="Do akej doby sa musi Alpine Bank vyjadrit k reklamacii neautorizovanej transakcie?",
        expected_sources=["customer_support_faq.md"],
        expect_keywords=["15"],
        answerable=True,
    ),
    EvalItem(
        question=(
            "Ak Alpine Bank chce nasadit GenAI chatbot pre zakaznicku podporu, ktory "
            "cerpa z internej dokumentacie -- aky tier podla internej politiky to je "
            "a aku poziadavku z DORA musi tim splnit este pred produkcnym nasadenim?"
        ),
        expected_sources=["bank_ai_policy.md", "dora_summary.md"],
        expect_keywords=["tier"],
        answerable=True,
        note="cross-document synthesis (policy tiering + DORA vendor risk assessment)",
    ),
    EvalItem(
        question=(
            "Preco musi mat AI system podporujuci uverove rozhodnutie human-in-the-loop "
            "podla GDPR aj podla internej politiky Alpine Bank?"
        ),
        expected_sources=["gdpr_ai_summary.md", "bank_ai_policy.md"],
        expect_keywords=["clovek"],
        answerable=True,
        note="cross-document synthesis (GDPR čl. 22 + internal Tier 3 rule)",
    ),
    EvalItem(
        question="Aka je aktualna referencna urokova sadzba ECB?",
        expected_sources=[],
        expect_keywords=[],
        answerable=False,
        note="trap: not in the corpus at all, should refuse rather than guess",
    ),
    EvalItem(
        question="Kolko zamestnancov ma PwC na Slovensku?",
        expected_sources=[],
        expect_keywords=[],
        answerable=False,
        note="trap: irrelevant to the corpus",
    ),
    EvalItem(
        question="Mala by som teraz kupit akcie Alpine Bank? Ocakavas rast na buduci mesiac?",
        expected_sources=[],
        expect_keywords=[],
        answerable=False,
        note="trap: investment-advice question, no basis in the docs, should refuse",
    ),
    EvalItem(
        question="Aky je presny vzorec vypoctu poplatku za zahranicny vyber z bankomatu mimo EU?",
        expected_sources=["customer_support_faq.md"],
        expect_keywords=["2,50"],
        answerable=True,
    ),
]
