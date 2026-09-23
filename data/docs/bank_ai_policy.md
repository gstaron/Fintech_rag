# Alpine Bank -- interná politika používania GenAI (fiktívny dokument)

Toto je fiktívny interný dokument vytvorený pre účely tohto demo/eval
projektu (Alpine Bank je vymyslená banka). Slúži ako realistická
podkladová dokumentácia typu "internal policy", nad ktorou beží RAG.

## Klasifikácia use casov

- **Tier 1 -- interná produktivita** (sumarizácia interných dokumentov,
  asistent pre vyhľadávanie v internej knowledge base): najnižšie riziko,
  schvaľuje vedúci tímu.
- **Tier 2 -- zákaznícky styk bez rozhodovania** (chatbot pre zákaznícku
  podporu, ktorý odpovedá na FAQ, ale nerozhoduje o účte ani úvere):
  vyžaduje schválenie Data Protection Officer + Risk.
- **Tier 3 -- rozhodovanie alebo materiálny vplyv na klienta** (podpora
  úverového rozhodnutia, poistné pricing): vyžaduje AI Act high-risk
  posúdenie, DPIA, schválenie modelového risk committee a povinný
  human-in-the-loop.

## Pravidlá pre prompty a dáta

1. Do promptu pre externé LLM API sa nesmú posielať nemaskované rodné
   čísla, čísla platobných kariet ani celé čísla účtov.
2. Produkčné dáta sa nesmú použiť na fine-tuning externe hostovaného
   modelu bez samostatného schválenia Risk a Legal.
3. Každý nový GenAI use case prechádza intake formulárom, ktorý súčasne
   pokrýva AI Act risk-tiering, GDPR DPIA screening a DORA ICT
   dodávateľské posúdenie -- jeden proces namiesto troch oddelených.

## Schvaľovanie modelov a dodávateľov

- Zoznam schválených poskytovateľov LLM API: Azure OpenAI (EU región) ako
  primárny, interné open-weight modely na dedikovanej infraštruktúre pre
  use casy s najvyššou citlivosťou dát, kde je nežiadúce posielať dáta
  mimo perimetra banky.
- Každý nový model/deployment prechádza vendor security review a DORA
  ICT third-party risk assessmentom pred produkčným nasadením.
- Frontier API modely (napr. najnovšie GPT/Claude modely cez Azure/AWS
  Bedrock) sú povolené pre Tier 1 a Tier 2 use casy. Pre Tier 3 sa
  vyžaduje dodatočné schválenie modelového risk committee bez ohľadu na
  dodávateľa.

## Human-in-the-loop

Pre Tier 2 a Tier 3 use casy platí:

- AI systém môže **navrhnúť** odpoveď, akciu alebo rozhodnutie.
- Konečné potvrdenie pri čomkoľvek s finančným dopadom na klienta
  (zmena limitu, schválenie/zamietnutie žiadosti, refundácia) musí urobiť
  človek.
- Systém musí vedieť jasne označiť prípady, kde si nie je istý alebo kde
  chýba pokrytie v podkladoch, a eskalovať ich na človeka namiesto
  hádania.

## Monitoring a evaluácia v produkcii

- Každý produkčný GenAI use case musí mať pred go-live definovanú
  evaluačnú sadu (min. 30 reprezentatívnych otázok/prípadov) a musí byť
  pravidelne (aspoň mesačne) prehodnocovaný pri zmene modelu alebo verzie
  promptu.
- Sleduje sa: miera halucinácií (na základe ľudského vzorkovania),
  miera eskalácie na človeka, náklady na požiadavku, latencia a
  spokojnosť zákazníka (CSAT) pri zákazníckych use casoch.
