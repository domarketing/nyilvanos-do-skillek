# DO! skillek ügyfeleknek

Claude-hoz készült skillek a webináros futószalag megépítéséhez: feliratkozó oldal, köszönőoldal,
értékesítési levelek és értékesítési oldal, plusz néhány hasznos kiegészítő. A DO! marketing belső
skilljeinek csupaszított változatai: a módszertan benne van, a mi saját adataink nincsenek. A saját
cégedre a `cegprofil` skill-lel szabod őket.

## Letöltés

Skillenként egy zip. Ezt a fájlt töltöd fel a claude.ai-ra, kicsomagolás nélkül.

| Skill | Mire jó | Letöltés |
|---|---|---|
| `cegprofil` | Kikérdez a cégedről, az ideális vásárlódról és az ajánlatodról, és összeírja egy `cegprofil.md`-be. A többi skill ebből dolgozik, ezért ezzel kezdd. | [zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/cegprofil.zip) |
| `feliratkozo-oldal` | Feliratkozó oldal webinárhoz vagy több napos kihíváshoz, bevált minták szerkezetével. | [zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/feliratkozo-oldal.zip) |
| `webinar-koszonooldal` | Köszönőoldal a feliratkozás utánra: visszaszámláló, teendők, naptárlink. | [zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/webinar-koszonooldal.zip) |
| `ertekesitesi-level-iro` | Értékesítési és kampánylevelek, levélsorozatok a webinár előtt és után. | [zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/ertekesitesi-level-iro.zip) |
| `ertekesitesi-oldal-keszito` | Vázlatból vagy dokumentumból kész értékesítési oldal (egy HTML-fájl) a 16 legókockás keretrendszer szerint. | [zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/ertekesitesi-oldal-keszito.zip) |
| `szovegellenorzo` | Kiszedi a kész magyar szövegből, amiről ráismerni, hogy AI írta. A többi skill a végén magától futtatja. | [zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/szovegellenorzo.zip) |
| `claude-oldalak-feltolto` | A kész oldalakat a Claude Oldalak bővítménnyel közvetlenül a saját WordPress-oldaladra teszi. | [zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/claude-oldalak-feltolto.zip) |
| `webdesign-arculat-generator` | A weboldalad címéből arculat-választót készít, a kiválasztott elemekből pedig kész főoldalt és designrendszer-leírást. | [zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/webdesign-arculat-generator.zip) |
| `facebook-poszt-iro` | Személyes hangú Facebook- és LinkedIn-posztok erős nyitómondattal. | [zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/facebook-poszt-iro.zip) |
| `leirat-javito` | Automatikus feliratból (VTT, SRT) rendezett, javított, szó szerinti leirat, például a webinárfelvételedből. | [zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/leirat-javito.zip) |
| `pdf-magyar` | Ékezethelyes magyar PDF, például csali-anyaghoz, ellenőrzőlistához, útmutatóhoz. | [zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/pdf-magyar.zip) |

**Az összes egyszerre:** [osszes-skill-csomag.zip](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/osszes-skill-csomag.zip).
Ezt ne töltsd fel közvetlenül: csomagold ki, és a benne lévő zipeket jelöld ki egyszerre a feltöltőben.
Minden fájl egy helyen: [legfrissebb kiadás](https://github.com/domarketing/nyilvanos-do-skillek/releases/latest).

## A futószalag sorrendje

1. `cegprofil`: egyszer elkészíted, utána minden skill ebből dolgozik.
2. `feliratkozo-oldal`: ide érkeznek a hirdetésekből és a posztokból.
3. `webinar-koszonooldal`: feliratkozás után ezt látják.
4. `ertekesitesi-level-iro`: emlékeztetők a webinár előtt, visszanézős és értékesítő levelek utána.
5. `ertekesitesi-oldal-keszito`: ide visznek a levelek és a webinár végi ajánlat.
6. `claude-oldalak-feltolto`: ha WordPress-oldalad van, ezzel kerülnek ki az oldalak.

A `szovegellenorzo` közben a háttérben dolgozik: a szöveges skillek a végén lefuttatják.

## Telepítés

### claude.ai (böngésző, asztali app)

1. Töltsd le a kívánt skill zipjét a fenti táblázatból.
2. A claude.ai beállításaiban nyisd meg a Skills részt, és válaszd az **Upload skill** lehetőséget.
3. Válaszd ki a letöltött zipet. Egyszerre többet is kijelölhetsz.

A skillekhez be kell kapcsolni a kódfuttatást és a fájlkészítést (Code execution and file creation)
a beállításokban.

**Fontos:** ne a zöld „Code → Download ZIP” gombbal letöltött teljes repót töltsd fel, és ne egy
mappát, amiben több skill van. A feltöltő skillenként egy zipet vár, benne egyetlen mappával, és abban
a `SKILL.md`-vel. A fenti linkeken pontosan ilyen zipek vannak.

### Claude Code

Pluginként, egyben az összes skill, frissítésekkel:

```
/plugin marketplace add domarketing/nyilvanos-do-skillek
/plugin install do-skillek@nyilvanos-do-skillek
```

Frissítés: `/plugin marketplace update nyilvanos-do-skillek`. Ha azt szeretnéd, hogy magától
frissüljön, a `/plugin` menü Marketplaces fülén bekapcsolhatod az automatikus frissítést.

Vagy kézzel: másold a kívánt skill mappáját (`skills/<skill>`) a `~/.claude/skills/` alá, és indíts
új sessiont.

## Ha a feltöltés hibát ír

| Hibaüzenet | Mi a gond | Mit csinálj |
|---|---|---|
| `Zip must contain exactly one top-level folder` | A zipben több mappa van, vagy a teljes repót tömörítetted. | Töltsd le a skill saját zipjét a fenti táblázatból. |
| `A skill cannot contain a plugin manifest` | Plugin-csomagot próbálsz skillként feltölteni. | Ugyanaz: a skill saját zipje kell. |
| `SKILL.md file must be in the top-level folder` | A `SKILL.md` egy szinttel mélyebben van. | Csak a skill mappáját tömörítsd, ne a fölötte lévőt. |
| `description … must be at most 1024 characters` | Átírtad a leírást, és túl hosszú lett. | Rövidítsd 1024 karakter alá. |
| `description cannot contain XML tags` | A leírásban `<` vagy `>` jel van. | Vedd ki, például `<URL>` helyett írd azt, hogy „URL”. |

## Mire figyelj

- A skillek kiindulópontok. A saját márkádra, ajánlatodra és hangodra a `cegprofil` szabja őket, de a
  végeredményt mindig nézd át.
- A `webdesign-arculat-generator` ikonjaihoz saját OpenAI API-kulcs kell. A kulcsot soha ne írd a
  skillbe, és ne tedd fel sehova nyilvánosan.
- A `claude-oldalak-feltolto` a [Claude Oldalak WordPress-bővítménnyel](https://domarketing.hu/plugin/)
  működik. A bővítmény API-kulcsára ugyanez vonatkozik.
- A `feliratkozo-oldal` mintái a DO! marketing saját oldalai. Csak a szerkezetet és a stílust veszi át
  belőlük, a szövegek, nevek és képek a te cégedé lesznek.

---

## Karbantartóknak

- A skillek a `skills/<név>/` mappákban vannak. Módosítás után futtasd: `python scripts/ellenor.py`
  (feltöltési szabályok, belső adatok, mérőkódok, kulcsok).
- A `main` ágra pusholt változás után a GitHub Action újraépíti a zipeket, és kicseréli őket a
  „legfrissebb” kiadásban. A letöltési linkek nem változnak.
- Új skillnél: mappa a `skills/` alá, sor a fenti táblázatba, és bejegyzés a
  `.claude-plugin/marketplace.json` `skills` listájába.
