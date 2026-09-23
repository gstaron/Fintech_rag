# Case interview príprava -- "Banka chce AI v zákazníckej podpore"

Bod 3 z prípravy: case interview takmer isto príde. Kľúčové posolstvo,
ktoré sa v inzeráte opakuje: **najprv sa pýtaj, potom navrhuj riešenie.**
Recruiter to formuloval ako "prepojenie obchodnej a technologickej stránky
projektov" a "identifikácia use casov s vysokým obchodným prínosom" --
presne to je schopnosť, ktorú bude case interview testovať.

## Discovery framework (nauč sa poradie, nie skript naspamäť)

1. **Skutočný problém a metrika úspechu.**
   - Prečo teraz? Čo konkrétne bolí (náklady na podporu, čas odozvy,
     spokojnosť zákazníkov, škálovanie počas špičiek)?
   - Aká metrika rozhodne o úspechu pilota? (napr. zníženie AHT, % ticketov
     vyriešených bez eskalácie, CSAT, náklady na ticket)
2. **Dáta a ich kvalita.**
   - Existuje znalostná báza / historické tickety? V akom stave (aktuálna,
     konzistentná, v jednom jazyku)?
   - Kto dáta vlastní a kto ich bude udržiavať po nasadení?
3. **Obmedzenia.**
   - Regulácia (DORA vendor risk, GDPR pri osobných dátach, AI Act ak sa
     systém dotýka úverového rozhodnutia -- pozri `docs/ARCHITECTURE.md`).
   - Security/architektúra (kde smú dáta byť spracované, aké systémy treba
     integrovať -- CRM, core banking).
   - Legacy (aké API/rozhrania už existujú, aké nie).
4. **Build vs. buy.**
   - Existuje hotové riešenie (napr. od dodávateľa core bankingu), ktoré
     pokryje 80 % za zlomok nákladov? Kedy sa oplatí vlastný vývoj (unikátny
     use case, konkurenčná výhoda, integrácia na mieru)?
5. **Pilot, potom škálovanie.**
   - Malý, jasne ohraničený pilot (jedna kategória ticketov, jeden jazyk,
     jeden kanál) s definovanými exit/go kritériami pred plošným rollout.
6. **ROI a riziká.**
   - Kvantifikuj prínos (pozri nástroj nižšie) aj náklady vrátane tých,
     ktoré klienti zabúdajú -- monitoring, human review, údržba promptov,
     re-training/re-evaluácia pri zmene modelu.
   - Pomenuj top 2-3 riziká a ako ich zmierniť (halucinácia -> guardrails +
     human-in-the-loop pre citlivé prípady; vendor lock-in -> abstraktná
     vrstva nad LLM providerom; regulačné riziko -> DORA/GDPR posúdenie pred
     kontraktom).

## Použi postavený ROI kalkulátor ako oporný bod

`fintech_agent/mcp_server.py` obsahuje jednoduchý `roi_calculator` nástroj
presne pre tento scenár. V pohovore ho nemusíš spomínať technicky, ale
štruktúra výpočtu (počet ticketov, cena za ticket dnes, cena za ticket s AI,
miera automatizácie) je presne to, čo od teba klient/interviewer čaká, že
vieš na mieste postaviť aj na papieri:

```
automatizované tickety = tickety/mesiac × miera automatizácie
mesačná úspora = automatizované tickety × (cena/ticket dnes − cena/ticket s AI)
```

Pripomeň si nahlas, že toto je **hrubý horný odhad** -- chýbajú náklady na
implementáciu, monitoring, human review frontu a pokles CSAT pri zlých
odpovediach, ktorý sa dá len ťažko vopred vyčísliť.

## Skúsená ukážka otvorenia (over si nahlas, ideálne po česky)

> "Než navrhnu riešenie, potreboval by som pochopiť pár vecí. Po prvé --
> čo presne dnes bolí najviac: objem ticketov, čas odozvy, alebo náklady?
> Po druhé -- akú znalostnú bázu dnes podpora používa a je aktuálna? Po
> tretie -- je v tomto use case niekde bod, kde by AI systém rozhodoval o
> niečom s finančným dopadom na klienta, alebo len odpovedá na otázky?
> Od toho sa totiž odvíja, či ideme rovno do pilota, alebo najprv riešime
> AI Act/DORA posúdenie."

Posledná veta je zámerne tam -- ukazuje, že vieš prepojiť obchodnú aj
regulačnú stránku hneď na prvom stretnutí, čo je presne to, čo poznámky k
pohovoru označujú ako tvoju silnú stránku (KB, Creditinfo, Cyrrus skúsenosť).

## Mock case interview

Ak chceš, môžeme si case interview rovno teraz zahrať naspamäť -- ja budem
klient z banky (alebo Novotný) a budem odpovedať len na otázky, ktoré mi
naozaj položíš, bez toho, aby som ti dopredu prezradil, čo je "správne
poradie" otázok. Stačí povedať, že chceš začať.
