# AI arculat-generátor (béta): telepítés és használat

Ez a skill egyetlen weboldal-címből (URL) elkészíti a vállalkozásod saját arculatát, három lépésben: **webes arculat →
prezentációs arculat → videós arculat**. Mindegyiket egy közös **arculat-központban** választod ki: minden elemből
5 változatot kapsz, megjegyzést írhatsz, kijelölheted a véglegeset, és ha kész vagy, jóváhagyod. A végén egy saját
**márka-skillt** (ZIP) is kapsz: azt feltöltve a Claude bármikor a te arculatodban készít új aloldalt, prezit, videós
grafikát, akárki kéri a csapatodból.

> **Béta.** Első nyilvános kiadás. Mindhárom fázis működik, de még csiszoljuk; ha valami
> furcsát látsz, írd meg nekünk egy képernyőképpel.

## Amire szükséged lesz
1. **Claude-előfizetés** kódfuttatással (Pro, Max, Team vagy Enterprise). A legjobb élmény: **Claude Code** (asztali
   app, Code fül), mert ott a skill képernyőképekkel ellenőrzi a saját munkáját, és az arculat-központ artifactként
   jelenik meg.
2. **Saját OpenAI API-kulcs** az egyedi ikonokhoz. Egy teljes ikonkészlet (14 ikon × 5 stílus) kb. 300-350 Ft.
   - platform.openai.com → bejelentkezés → **API keys** → *Create new secret key* → másold ki (`sk-...`).
   - Tölts fel pár dollár egyenleget (Settings → Billing).
   - Ha a képgeneráláshoz „Verify organization” kell: Settings → Organization → General → *Verify* (egyszeri).
3. **Python 3.9 vagy újabb** a Pillow csomaggal. A telepítéskor a Claude ellenőrzi, és ha valami hiányzik, szól
   (és a te engedélyeddel feltelepíti):
   - **prezentációs fázis:** `python-pptx`, `pymupdf` (`pip3 install --user python-pptx pymupdf`) és a **LibreOffice**
     (Mac: `brew install --cask libreoffice`, vagy a libreoffice.org-ról). A motor a márkád betűit a felhasználói
     betűmappába telepíti, mert a PowerPoint és a LibreOffice is csak a telepített betűt látja.
   - **videós fázis:** **Google Chrome** (állóképek), és a fejkivágáshoz `pip3 install --user onnxruntime` (nélküle
     arcfelismeréses becsléssel dolgozik). A kis kivágó modellt (~15 MB) első használatkor letölti a
     `~/.cache/ai-arculat/` alá. A minta-videóhoz még `ffmpeg` és `pip3 install --user websocket-client` kell.
     Szoros portrénál a háttér felső sávját az OpenAI képszerkesztés egészíti ki (~6 Ft).

## Telepítés Claude Code-ban (ajánlott)
A legegyszerűbb, ha a Claude Code-od maga telepíti:
1. Nyiss egy új munkamenetet a Claude asztali appban (Code fül), és írd be:
   *„Telepítsd az AI arculat-generátor skillt: https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/ai-arculat-generator.zip”*
2. A Claude letölti az `ai-arculat-generator.zip`-et (ehhez engedélyt kér), kicsomagolja ide:
   `~/.claude/skills/ai-arculat-generator/`, és ellenőrzi a Python-csomagokat.
3. **Az OpenAI-kulcsot te teszed el**, a Claude nem látja: hozz létre egy fájlt `~/.config/openai-kulcs.txt` néven,
   egyetlen sorral (`sk-...`). A Claude ezután ellenőrzi: `python3 ~/.claude/skills/ai-arculat-generator/scripts/ikon_generalo.py --check`
   → `OK`.
4. Indíts egy **új munkamenetet** (a skillek induláskor töltődnek be).

Kézzel is mehet: csomagold ki a ZIP-et a `~/.claude/skills/` alá, és tedd el a kulcsot a fenti fájlba.

## Telepítés Claude.ai-ban (web vagy asztali app, Chat)
1. **Settings → Capabilities**: kapcsold be a *Code execution and file creation* opciót.
2. Ugyanitt a hálózati hozzáférésnél engedélyezd a kimenő forgalmat: *All domains*, vagy vedd fel: a saját
   weboldalad domainjét, `api.openai.com`, `fonts.googleapis.com`, `fonts.gstatic.com`, `api.frankfurter.app`.
3. **Customize → Skills → Upload skill**: töltsd fel az `ai-arculat-generator.zip` fájlt (https://github.com/domarketing/nyilvanos-do-skillek/releases/latest/download/ai-arculat-generator.zip).
4. Készíts egy `openai-kulcs.txt` fájlt egyetlen sorral (`sk-...`), és a beszélgetés elején töltsd fel.

## Használat
1. Írd be: *„Készíts arculatot ehhez a weboldalhoz: https://…”*. A Claude kinyeri az oldalad anyagát, felállítja a
   márka-diagnózist („Így látunk téged”), legenerálja a palettákat, betűpárokat, ikonokat, és megépíti az
   **arculat-központot** (artifact-link; Claude.ai Chatben letölthető HTML-fájl).
2. A központ **Web** fülén:
   - **kattints** bármelyik változatra: legalul, az élő oldalon azonnal úgy jelenik meg,
   - **★ Ez legyen a végleges**: így jelölöd a kedvencet (bármikor átjelölheted),
   - **megjegyzés**: minden változat alatt írhatsz, mi tetszik és mi nem; ha egyik sem jó, pipáld: „kérek újakat”,
   - az élő oldalt mobil nézetben is megnézheted,
   - a végén, legalul: **Jóváhagyom a webes arculatot**.
   Artifactként a döntéseid maguktól mentődnek, a Claude közvetlenül kiolvassa őket. Letöltött HTML-fájlnál a
   böngésződ menti őket, és a „Visszajelzés másolása” gombbal adod vissza.
3. Szólj a Claude-nak, hogy kész vagy. Elkészül a kész főoldal (`web/fooldal.html`) és a design-rendszer leírása.
4. *„Jöhet a prezentáció.”* A **Prezentáció** fülön ugyanígy választasz (10 kategória, 5-5 változat, 12 minta-dia a
   saját tartalmaddal), és jóváhagyod. Valódi, szerkeszthető PowerPoint lesz belőle.
5. *„Jöhet a videó.”* A **Videó** fülön a feliratok, címsorok, kártyák és a vágási stílus élő előnézetben.
6. A végén: **Arculati kézikönyv** fül és a **márka-skill** (`<márkád>-arculat.zip`). Ezt töltsd fel a Claude-ba
   (Customize → Skills), és onnantól: *„Készíts egy aloldalt az arculatom szerint erről: …”*, *„Készíts prezentációt
   az arculatom szerint ebből a vázlatból: …”*.

## Jó tudni
- Minden ügyfélnél más lesz: a skill a vállalkozásod szakmájából, tárgyaiból és a mostani oldaladból dolgozik, és
  nem enged tovább, ha a változatok túl hasonlók vagy sablonosak.
- A tényeket (árak, nevek, helyszín, nyitvatartás) a mostani oldaladról veszi, betűre. Véleményt, számot nem talál ki.
- A kulcsodat a skill nem írja ki és nem teszi bele a kész fájlokba.
- A betűk mind ellenőrzötten tudják az ő és ű betűt.
- A videós arculat a te vágó skilledhez igazodik (a tananyagból telepített vágórendszerhez): a márka-részt oda
  illesztheted.
