# Architektonické rozhodnutia -- ťaháky na "2 minúty pred CTO aj pred risk"

Tento dokument mapuje na bod 1 z prípravy na AI Lead pohovor (PwC, Marek
Novotný): technika na úrovni rozhodnutí, nie na úrovni kódu. Každá sekcia je
zámerne krátka -- cieľ je vedieť to povedať naspamäť v 2 minútach, nie
prečítať esej. Kde je to relevantné, odkazujem na konkrétne rozhodnutie
urobené v tomto repe, aby si mal živý príklad, nie len teóriu.

## 1. RAG vs. fine-tuning vs. long context

**Default odpoveď: RAG.** Väčšina firemných use casov je "odpovedz na
základe našich dokumentov/dát", nie "nauč model nový spôsob uvažovania
alebo štýl". RAG to rieši bez trénovania, s okamžitou aktualizáciou (nový
dokument = re-index, nie re-training) a s auditovateľnosťou (vieš ukázať
presne, z ktorého zdroja odpoveď pochádza -- pozri `[zdroj: ...]` citácie
v `src/fintech_rag/rag.py`).

**Kedy fine-tuning dáva zmysel:**
- Potrebuješ konzistentný **formát/štýl** výstupu vo veľkom objeme (napr.
  štruktúrované extrakcie z dokumentov v presnom JSON tvare), nie nové
  fakty.
- Potrebuješ **nižšiu latenciu a menší model** pre úzku, opakovanú úlohu
  (distilácia veľkého modelu do malého pre jednu konkrétnu úlohu).
- Doménová terminológia je natoľko špecifická, že aj s dobrým RAG
  promptom model "nerozumie" kontextu (zriedkavé pri finančnej doméne --
  frontier modely majú slušné finančné znalosti už z predtrénovania).

**Prečo väčšina firiem fine-tuning nepotrebuje:** fine-tuning je drahší,
pomalší na iterovať (nový dataset -> nový tréning -> evaluácia -> nasadenie
vs. RAG kde stačí pridať dokument), viaže ťa na konkrétnu verziu modelu (pri
upgrade base modelu often treba fine-tuning zopakovať) a nerieši
aktuálnosť dát -- fakty sa menia, štýl odpovedí menej.

**Long context** (modely s 200k+ token oknom) je lákavá skratka -- "hoď tam
všetky dokumenty, netreba retrieval". V praxi: funguje pre desiatky
dokumentov, nie pre firemnú knowledge base s tisíckami strán; je drahšie na
každý request (platíš za celý kontext zakaždým); a "lost in the middle"
efekt znamená, že model reálne horšie využije informáciu uprostred veľmi
dlhého kontextu. Najlepšia prax: RAG na **výber** relevantného kontextu +
dostatočne veľké okno na to, aby si mohol poslať niekoľko celých
dokumentov namiesto útržkov, keď to úloha vyžaduje.

## 2. Agenti vs. deterministický workflow s LLM krokom

Agent (LLM si sám vyberá poradie a počet krokov/nástrojov) dáva zmysel keď:
- Postupnosť krokov sa **nedá vopred predpovedať** (líši sa podľa
  konkrétneho vstupu -- napr. "over to v troch rôznych zdrojoch, podľa
  toho čo tam nájdeš, over aj štvrtý").
- Úloha vyžaduje **iteratívne dolaďovanie** (skús, over výsledok, skús
  inak).

Deterministický workflow s jedným alebo viacerými LLM krokmi (pevný pipeline,
kde LLM robí jeden konkrétny krok -- napr. klasifikácia, extrakcia,
sumarizácia -- ale orchestráciu riadi normálny kód) je **defaultná voľba**
keď:
- Postupnosť krokov je vopred známa a stabilná (90 % firemných use casov).
- Potrebuješ predvídateľné náklady, latenciu a ľahké testovanie.
- Chyba v kroku 2 nesmie spôsobiť, že agent "skúsi niečo úplne iné" --
  radšej zlyhá čisto a eskaluje.

V tomto repe je to ukázané priamo: `fintech_agent/agent_client.py` je
skutočný agent (LLM rozhoduje, ktorý nástroj a kedy zavolať, max. 4 kolá),
zatiaľ čo `fintech_rag/rag.py` je deterministický pipeline (retrieve ->
threshold guardrail -> generate -> cituj zdroje) -- LLM robí presne jeden
krok, zvyšok je obyčajný kód. Toto rozlíšenie je presne to, čo v pohovore
očakávajú, že vieš pomenovať pri návrhu riešenia pre klienta.

**MCP (Model Context Protocol)** je spôsob, ako nástroje pre agenta
štandardizovať a oddeliť od konkrétneho LLM providera -- agent sa "spýta"
MCP servera na zoznam dostupných nástrojov (`list_tools`) namiesto toho,
aby mal schémy zahardcodované, a server beží ako samostatný proces
(`fintech_agent/mcp_server.py`), ktorý môže zdieľať viacero rôznych
agentov/aplikácií. Pre klienta je argument jednoduchý: nová integrácia
(nový zdroj dát, nový interný systém) sa pridá ako MCP server raz a môže ju
použiť ľubovoľný agent v organizácii, namiesto point-to-point integrácie
pre každý pár (agent, systém).

**Human-in-the-loop** nie je "nice to have", je to regulatórna nutnosť pre
čokoľvek s finančným dopadom na klienta (pozri GDPR čl. 22 a EU AI Act
vysoko rizikové systémy v `data/docs/`). V tomto repe to demonštruje nástroj
`request_human_review` -- agent nikdy sám "nevykoná" akciu s dopadom na
konkrétny účet, len ju zaradí do frontu a vráti potvrdenie, že čaká na
človeka.

## 3. Výber modelu

Tri osi rozhodovania, v poradí, v akom sa na ne v banke reálne pýtajú:

1. **Data residency / dôvernosť dát.** Ak dáta nesmú opustiť perimeter
   alebo EU región, frontier API (aj cez Azure) môže byť problém --
   riešenie je buď Azure OpenAI v EU regióne so zmluvnou garanciou, alebo
   open-weight model nasadený on-prem/v privátnom cloude banky. V tomto
   repe `data/docs/bank_ai_policy.md` modeluje presne tento rozhodovací
   strom (Tier podľa citlivosti -> povolený provider).
2. **Cena na request pri objeme.** Frontier model za každý request je
   drahší, ale pri nízkom objeme (interný nástroj pre desiatky ľudí) je to
   zanedbateľné oproti nákladom na vlastnú infraštruktúru. Pri vysokom
   objeme (miliony zákazníckych ticketov) sa oplatí zvážiť menší/distilovaný
   model pre bežný prípad a frontier model len pre eskalácie -- klasický
   "router" pattern.
3. **Kvalita/schopnosti** -- posledná os, nie prvá. V pohovore je bežná
   chyba začať práve tu ("použime najlepší model"), zatiaľ čo klient sa
   opýta na cenu a data residency skôr.

**Small LLMs a distilácia:** typický pattern je natrénovať/vybrať malý
model na úzku úlohu (klasifikácia intentu, extrakcia polí) pomocou dát
vygenerovaných frontier modelom (distilácia) -- lacnejšie a rýchlejšie v
produkcii, frontier model sa použije len na "ťažké"/neisté prípady.

## 4. Evals, guardrails, LLMOps, monitoring

Toto je presne to, kde recruiter/partner pozná rozdiel medzi "vie o tom" a
"robil to" -- preto je `src/fintech_eval/` v tomto repe skutočný, funkčný
kód, nie len opis:

- **Evals** = testovacia sada s očakávaným výsledkom, spustená
  automatizovane (`fintech_eval/dataset.py` + `evaluate.py`). Meria sa
  retrieval hit rate, správnosť odpovede a -- kriticky -- či systém
  správne **odmietne** odpovedať na otázku, ktorú podklady nepokrývajú.
- **Guardrails** = lacné, deterministické poistky pred/popri LLM volaní --
  napr. similarity threshold pred generovaním (`REFUSAL_SIMILARITY_THRESHOLD`
  v `rag.py`), maskovanie PII v prompte pred odoslaním do externého API
  (pozri `gdpr_ai_summary.md`), kontrola, či agent nevolá akciu s reálnym
  dopadom bez eskalácie.
- **LLMOps** = verziovanie promptov, sledovanie zmien modelu/verzie API,
  reprodukovateľné eval behy pri každej zmene promptu alebo modelu (nie len
  raz pred go-live).
- **Monitoring v produkcii** = miera halucinácií na vzorke, miera eskalácie
  na človeka, náklady a latencia na request, CSAT pri zákazníckych use
  casoch -- presne metriky opísané v `bank_ai_policy.md`.

## 5. Regulácia (EU AI Act, DORA, GDPR)

Pozri priamo `data/docs/eu_ai_act_summary.md`, `dora_summary.md`,
`gdpr_ai_summary.md` -- napísané tak, aby si ich vedel prerozprávať vlastnými
slovami, nie citovať naspamäť. Kľúčová vec, ktorú treba vedieť povedať
plynule: **väčšina interných GenAI use casov nie je vysoko riziková podľa
AI Act**, ale DORA (ICT third-party risk pre LLM providera) a GDPR
(automatizované rozhodovanie, minimalizácia dát) platia takmer vždy, keď sa
spracúvajú osobné/klientske dáta -- a tieto tri sa dajú posudzovať v jednom
intake procese namiesto troch oddelených (pozri `bank_ai_policy.md`).

## 6. Referenčné architektúry (Azure OpenAI, Bedrock, Vertex)

PwC je silno naviazané na Microsoft, takže **Azure OpenAI** je defaultná
referenčná architektúra, na ktorú by si mal vedieť namapovať práve
postavené demo:

- Embeddings + chat cez Azure OpenAI deployment (endpoint + API key +
  deployment name namiesto modelu -- presne ako v `AzureOpenAI` klientovi v
  `fintech_rag/llm.py`, ktorý je v tomto repe reálne implementovaný, nielen
  spomenutý).
- Vektorová databáza: Azure AI Search (namiesto flat np store použitého
  tu pre jednoduchosť demo projektu -- pozri poznámku v
  `vector_store.py` o tom, kedy prejsť na skutočnú vektorovú DB).
- Orchestrácia: Azure AI Foundry / Semantic Kernel / vlastný kód (ako v
  tomto repe) -- voľba závisí od toho, či klient chce "managed" platformu
  alebo plnú kontrolu nad promptmi a nákladmi.
- AWS Bedrock a GCP Vertex AI sú analogické (modely rôznych providerov za
  jedným API, IAM integrácia, natívna prepojenosť na zvyšok cloudu klienta)
  -- relevantné hlavne ak klient už je na AWS/GCP a nechce multi-cloud.
