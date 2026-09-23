# Fintech RAG + eval + MCP agent -- pohovorová príprava (PwC AI Lead)

Víkendový hands-on projekt na zúženie "hands-on medzery" pred pohovorom na
AI Lead pozíciu (pre-sales/advisory, PwC AI Service Offering). Cieľ nie je
portfólio -- cieľ sú vlastné "war stories": čo sa rozbilo, kde model
halucinoval, koľko to stálo, kedy agent správne eskaloval na človeka.

Obsahuje:

- **RAG s evaluáciou** nad fiktívnymi fintech/regulačnými dokumentmi
  (EU AI Act, DORA, GDPR, interná AI politika banky, FAQ zákazníckej
  podpory) -- `src/fintech_rag/`, eval harness v `src/fintech_eval/`.
- **Malý agent s MCP** -- MCP server s tromi nástrojmi (RAG search, ROI
  kalkulátor, eskalácia na človeka) a tool-calling agent loop --
  `src/fintech_agent/`.
- **Prípravné dokumenty** priamo naviazané na štruktúru pohovoru --
  `docs/ARCHITECTURE.md` (trade-off rozhodnutia), `docs/WAR_STORIES.md`
  (šablóna na STAR príbehy a čestnú odpoveď o produkčnej skúsenosti),
  `docs/CASE_INTERVIEW_PREP.md` (discovery framework + case script).

## Rýchly štart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # necháš LLM_PROVIDER=none pre offline režim bez API kľúča
```

**Offline režim** (`LLM_PROVIDER=none`, default) beží bez akéhokoľvek API
kľúča -- hashovací embedding a extraktívna "odpoveď" namiesto skutočného
LLM. Slúži len na overenie, že retrieval a celá inštalácia funguje; nedáva
zmysluplné eval čísla ani skutočné odpovede. Pre reálnu prípravu (a reálne
"war stories" na pohovor) nastav v `.env`:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

alebo `LLM_PROVIDER=azure_openai` s Azure OpenAI premennými -- PwC je
naviazané na Microsoft, takže Azure OpenAI je zmysluplnejšia voľba na
precvičenie, ak máš k nej prístup.

```bash
# 1. Naindexuj dokumenty
python -m fintech_rag.cli ingest

# 2. Polož otázku
python -m fintech_rag.cli ask "Ake su hlavne poziadavky DORA na riadenie rizika tretich stran?"

# 3. Spusti eval sadu (retrieval hit rate, keyword coverage, refusal correctness, latencia, cena)
python -m fintech_rag.cli eval

# 4. Vyskúšaj agenta s MCP nástrojmi (RAG search, ROI kalkulátor, eskalácia na človeka)
python -m fintech_agent.agent_client "Zakaznik sa pyta na politiku pouzivania AI v podpore, over to v podkladoch"

# testy (behia aj offline, bez API kluca)
pytest
```

## Štruktúra

```
data/docs/              fiktívne fintech/regulačné dokumenty (zdroj pre RAG)
src/fintech_rag/         ingest, vector store, RAG pipeline, CLI
src/fintech_eval/        eval sada a evaluačný harness
src/fintech_agent/       MCP server (nástroje) + tool-calling agent
docs/ARCHITECTURE.md     trade-off rozhodnutia (RAG vs fine-tuning, agenti vs workflow, výber modelu, evals/guardrails, regulácia, referenčné architektúry)
docs/WAR_STORIES.md      šablóna na zápis toho, čo sa pokazilo -- vypĺňaj priebežne
docs/CASE_INTERVIEW_PREP.md  discovery framework + case script "banka chce AI v zákazníckej podpore"
```

## Prečo je architektúra taká, aká je

Zámerne jednoduchá vektorová databáza (flat numpy store namiesto
Chroma/pgvector/Azure AI Search) a vlastný minimalistický eval harness
(namiesto napr. `ragas`) -- nie preto, že by som nevedel siahnuť po
ťažšom frameworku, ale preto, že pre pár desiatok dokumentov je jednoduché
riešenie rýchlejšie na pochopenie a debugovanie, a v pohovore vieš presne
vysvetliť, čo by si zmenil pri škálovaní na produkciu (pozri
`docs/ARCHITECTURE.md`). To je presne ten typ trade-off rozhodnutia, ktoré
sa v pre-sales/advisory role očakáva vedieť obhájiť.
