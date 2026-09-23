# GDPR a GenAI -- zhrnutie pre bankový kontext

Nasadenie LLM/GenAI systémov v banke sa dotýka GDPR najmä v štyroch
oblastiach: právny základ spracovania, minimalizácia dát, automatizované
rozhodovanie a práva dotknutých osôb.

## Právny základ a účel

Ak GenAI systém spracúva osobné údaje klientov (napr. RAG nad
klientskou dokumentáciou, chatbot so zákazníckou históriou), musí mať
jasný právny základ (typicky oprávnený záujem alebo plnenie zmluvy) a
účel spracovania nesmie presiahnuť pôvodný účel, na ktorý boli dáta
zozbierané ("purpose limitation"). Trénovanie/fine-tuning modelu na
klientskych dátach je iný účel ako pôvodné spracovanie a spravidla
vyžaduje samostatné posúdenie.

## Minimalizácia dát a prompty

- Do promptu smerovaného k externému LLM API by nemali ísť priame
  identifikátory (rodné číslo, číslo účtu, celé meno), ak to nie je
  nevyhnutné -- v praxi sa rieši pseudonymizáciou/maskovaním pred
  odoslaním a re-identifikáciou po prijatí odpovede.
- Logy promptov a odpovedí (potrebné pre debugging a evaluáciu) sú tiež
  osobný údaj, ak obsahujú identifikovateľné dáta -- platia rovnaké
  retenčné a prístupové pravidlá ako pre iné produkčné logy.

## Automatizované rozhodovanie (čl. 22 GDPR)

Ak AI systém robí rozhodnutie s právnym alebo podobne významným účinkom na
osobu **výlučne automatizovane** (napr. automatické zamietnutie úveru bez
ľudského zásahu), dotknutá osoba má právo na ľudský zásah, vyjadrenie
svojho stanoviska a napadnutie rozhodnutia. V praxi to znamená, že čisto
autonómny AI agent rozhodujúci o úvere bez human-in-the-loop je z pohľadu
GDPR aj EU AI Act vysoko rizikový -- preto sa v bankovníctve takmer vždy
navrhuje architektúra AI-navrhuje / človek-schvaľuje.

## DPIA (Data Protection Impact Assessment)

Pre nové GenAI use casy spracúvajúce osobné údaje vo väčšom rozsahu (najmä
citlivé finančné dáta) je DPIA typicky povinná už vo fáze návrhu, nie až
pred nasadením -- odporúča sa robiť ju paralelne s AI Act risk-tieringom
v rovnakom intake procese.

## Práva dotknutých osôb

Právo na prístup, opravu a vymazanie sa vzťahuje aj na dáta použité v
RAG indexe alebo v histórii konverzácie s chatbotom. Pri vektorových
databázach to prakticky znamená potrebu vedieť dohľadať a vymazať chunky
patriace konkrétnej osobe -- architektonická požiadavka, ktorú treba
riešiť už pri návrhu chunking a indexovacej stratégie, nie dodatočne.
