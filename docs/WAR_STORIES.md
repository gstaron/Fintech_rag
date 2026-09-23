# War stories -- vyplň PO reálnom behu s API kľúčom

Toto nie je portfólio na ukázanie, je to zdroj konkrétnych detailov pre
STAR príbehy a pre úprimnú odpoveď na otázku o produkčnej skúsenosti (bod 2
z prípravy). Nechaj si tento súbor otvorený počas víkendu a priebežne si
zapisuj presné čísla a momenty, kde sa niečo rozbilo -- to sú presne tie
detaily, ktoré Novotný pozná odlíšiť od naučenej teórie.

## Ako na to

1. Nastav `.env` s reálnym `LLM_PROVIDER=openai` (alebo `azure_openai`) a
   API kľúčom -- pozri `.env.example`.
2. `python -m fintech_rag.cli ingest`
3. Polož si aspoň 15-20 vlastných otázok cez
   `python -m fintech_rag.cli ask "..."`, vrátane zámerne zákerných
   (nejednoznačných, mimo pokrytia dokumentov, kombinujúcich dva zdroje).
4. `python -m fintech_rag.cli eval` a pozri si `results/eval_report.md`.
5. Skús aspoň 5 agentových úloh cez `agent_client.py`, vrátane jednej, kde
   by mal agent správne eskalovať cez `request_human_review` namiesto toho,
   aby si niečo "vymyslel".
6. Po každom kroku si sem zapíš 2-3 vety -- čo prekvapilo, čo sa pokazilo,
   koľko to stálo, aká bola latencia.

## Šablóna: čo sa rozbilo

- **Kde model halucinoval:** _(napr. konkrétna otázka, kde si guardrail
  s prahom podobnosti nezachytil slabý kontext a model si niečo dopovedal)_
- **Kde retrieval vytiahol zlý chunk:** _(napr. otázka kombinujúca dva
  dokumenty, kde top-k vrátil len jeden a odpoveď bola neúplná -- presne
  scenár, na ktorý upozorňuje `dataset.py` v cross-document otázkach)_
- **Koľko to stálo:** _(vlož číslo z `results/eval_report.md`, over si
  reálne cenníkové sadzby a preprac `PRICE_PER_1M_INPUT/OUTPUT` v
  `fintech_eval/evaluate.py`, ak sa líšia od placeholderov)_
- **Aká bola latencia a kde bol bottleneck:** _(retrieval vs. generovanie
  vs. sieť)_
- **Kde agent správne eskaloval na človeka:** _(konkrétny príklad, že
  `request_human_review` zafungoval namiesto toho, aby si agent niečo
  "dovolil" -- toto je pozitívny príbeh, ktorý stojí za to povedať)_
- **Kde agent zvolil zlý nástroj alebo zbytočne veľa kôl:** _(pozri
  konzolový výstup agenta -- každé kolo je vypísané)_

## Úprimná odpoveď na otázku o produkčnom nasadení

Použi túto štruktúru namiesto vymýšľania si skúsenosti, ktorú nemáš --
klamať v tejto pozícii je podľa poznámok k pohovoru fatálne:

> "Produkčný GenAI systém som nenasadil. ML a backend v bankovom prostredí
> áno -- [tu doplň konkrétny projekt/rolu]. GenAI stack som si prakticky
> overil na víkendovom projekte: RAG nad fintech regulačnými dokumentmi s
> vlastnou eval sadou a malý MCP agent s human-in-the-loop guardrailom.
> Narazil som na [doplň konkrétnu vec z tohto súboru] a rozhodol som sa to
> riešiť [doplň, ako]."

## STAR príbehy -- pracovné poznámky (3-4)

Priprav si tieto štyri, s konkrétnymi číslami/detailmi, nie všeobecne:

1. **Vysvetlil si zložitú techniku netechnickému človeku.**
   Situácia / Úloha / Akcia / Výsledok: _____
2. **Odhalil si, že klient v skutočnosti chcel niečo iné, než zadal.**
   S/T/A/R: _____
3. **Zastavil si nerealistické zadanie.**
   S/T/A/R: _____
4. **Pomohol si tvoriť ponuku alebo scoping** (Mentateq sa ráta ako
   konzulting).
   S/T/A/R: _____

Štatistická fyzika: použiť len ako jednu vetu o spôsobe myslenia
("navyknutý modelovať zložité systémy cez agregátne správanie a
neistotu, nie hľadať jednu deterministickú príčinu") -- nie ako
samostatnú tému.
