# EU AI Act -- zhrnutie pre finančný sektor

Nariadenie EÚ o umelej inteligencii (EU AI Act, nariadenie 2024/1689) zavádza
rizikovo orientovaný rámec pre AI systémy uvádzané na trh alebo používané
v EÚ. Rozdeľuje systémy do štyroch kategórií podľa rizika: neprijateľné
riziko (zakázané), vysoké riziko, obmedzené riziko (transparentnosť) a
minimálne riziko.

## Vysoko rizikové AI systémy vo finančnom sektore

Príloha III nariadenia priamo označuje za vysoko rizikové:

- AI systémy používané na **hodnotenie úverovej bonity a kreditného skóre**
  fyzických osôb (okrem systémov na odhaľovanie podvodov, ktoré vysoko
  rizikové nie sú).
- AI systémy používané na **hodnotenie rizika a stanovovanie cien pri
  životnom a zdravotnom poistení**.

Pre banky teda takmer akýkoľvek model rozhodujúci alebo materiálne
ovplyvňujúci úverové rozhodnutie o fyzickej osobe spadá do vysoko rizikovej
kategórie -- to platí aj pre GenAI/LLM komponent, ak je súčasťou takého
rozhodovacieho procesu (napr. sumarizácia podkladov pre underwritera, ktorá
priamo vstupuje do rozhodnutia).

## Povinnosti pre vysoko rizikové systémy

- Systém riadenia rizika počas celého životného cyklu.
- Riadenie a kvalita trénovacích, validačných a testovacích dát.
- Technická dokumentácia a logovanie (traceability).
- Transparentnosť voči používateľom a inštrukcie na použitie.
- **Ľudský dohľad** (human oversight) -- človek musí byť schopný rozhodnutie
  systému pochopiť, spochybniť a v prípade potreby zvrátiť.
- Presnosť, robustnosť a kybernetická bezpečnosť.
- Posúdenie zhody (conformity assessment) pred uvedením na trh.

## Modely na všeobecné účely (GPAI)

Poskytovatelia veľkých jazykových modelov (napr. dodávatelia frontier
modelov) majú samostatné povinnosti (technická dokumentácia, politika
dodržiavania autorských práv, sumár trénovacích dát). Modely so
"systémovým rizikom" (nad určitým výpočtovým prahom) majú prísnejšie
požiadavky na evaluáciu a hlásenie incidentov. Banka ako nasadzovateľ
(deployer) si typicky tieto povinnosti nerieši sama, ale musí si od
dodávateľa modelu vedieť vyžiadať potrebnú dokumentáciu.

## Harmonogram

- Zákazy (neprijateľné riziko): účinné od februára 2025.
- Povinnosti pre GPAI modely: účinné od augusta 2025.
- Väčšina povinností pre vysoko rizikové systémy: účinné od augusta 2026.
- Vysoko rizikové systémy, ktoré sú súčasťou regulovaných produktov (napr.
  niektoré finančné produkty): predĺžený prechod do augusta 2027.

## Prečo je to relevantné pre GenAI use case v banke

Väčšina interných GenAI use casov (interný chatbot, sumarizácia dokumentov,
asistent pre zákaznícku podporu bez priameho rozhodovania o úvere) **nie je
vysoko riziková** podľa Prílohy III -- pokiaľ priamo nerozhoduje alebo
materiálne neovplyvňuje kreditné alebo poistné rozhodnutie o fyzickej osobe.
Napriek tomu platia horizontálne povinnosti okolo transparentnosti (napr.
informovanie používateľa, že komunikuje s AI) a odporúča sa AI Act
risk-tiering urobiť súčasťou intake procesu pre každý nový use case už od
prvého stretnutia s klientom.
