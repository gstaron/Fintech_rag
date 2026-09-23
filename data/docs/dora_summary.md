# DORA (Digital Operational Resilience Act) -- zhrnutie

DORA (nariadenie EÚ 2022/2554) je účinná od 17. januára 2025 a zjednocuje
požiadavky na digitálnu prevádzkovú odolnosť finančných subjektov v EÚ
(banky, poisťovne, investičné spoločnosti, platobné inštitúcie a i.).
Priamo sa vzťahuje aj na ich **kritických ICT dodávateľov tretích strán**
-- vrátane cloudových a AI/LLM poskytovateľov, ak sú kritickí.

## Piate piliere DORA

1. **ICT risk management** -- riadiaci orgán (predstavenstvo) nesie priamu
   zodpovednosť za ICT rizikovú stratégiu vrátane AI komponentov.
2. **Hlásenie ICT incidentov** -- povinné hlásenie závažných incidentov
   regulátorovi v stanovených lehotách (počiatočné hlásenie, priebežné,
   záverečné).
3. **Testovanie digitálnej prevádzkovej odolnosti** -- pravidelné testy
   vrátane pokročilého testovania (TLPT -- threat-led penetration testing)
   pre významné subjekty.
4. **Riadenie rizika tretích strán (ICT third-party risk)** -- toto je pre
   GenAI projekty najrelevantnejšie:
   - Register všetkých zmluvných dojednaní s ICT poskytovateľmi (vrátane
     API prístupu k LLM), s klasifikáciou kritickosti.
   - Povinné zmluvné náležitosti: SLA, right-to-audit, exit stratégia,
     lokalizácia dát, subdodávatelia (napr. ak OpenAI/Microsoft
     subdodáva infraštruktúru ďalej).
   - Pred-kontraktuálne posúdenie koncentračného rizika -- ak väčšina
     bánk v sektore používa toho istého poskytovateľa frontier modelu,
     regulátor to sleduje ako systémové riziko.
   - Kritickí ICT poskytovatelia tretích strán môžu byť priamo dohliadaní
     európskymi orgánmi dohľadu (ESAs).
5. **Zdieľanie informácií** -- dobrovoľná výmena informácií o hrozbách
   medzi finančnými subjektmi.

## Dôsledky pre nasadenie GenAI v banke

- Každý externý LLM API (OpenAI, Azure OpenAI, Anthropic...) musí prejsť
  ICT third-party risk assessmentom **pred** produkčným nasadením, nielen
  bežným vendor security review.
- Treba mať jasnú **exit stratégiu** -- ak dodávateľ modelu zlyhá alebo
  zmení podmienky, banka musí vedieť prejsť na alternatívu bez výpadku
  kritickej služby. Toto je jeden z dôvodov, prečo banky preferujú
  architektúry s abstraktnou vrstvou nad LLM providerom (nie hard-lock na
  jeden model).
- Incidenty spôsobené AI systémom (napr. halucinácia, ktorá viedla
  k nesprávnej informácii zákazníkovi vo veľkom rozsahu) môžu byť
  posudzované ako ICT incident s povinnosťou hlásenia, ak spĺňajú prahy
  závažnosti.
- Data residency: pre kritické dáta sa v praxi vyžaduje EU región nasadenia
  (napr. Azure OpenAI v EU regióne), nielen zmluvná garancia.
