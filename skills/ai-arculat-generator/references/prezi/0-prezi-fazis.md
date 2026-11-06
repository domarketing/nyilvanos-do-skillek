# 2. fázis: prezentációs arculat (béta)

A jóváhagyott webes arculatból (tokenek.json) natív, szerkeszthető PowerPoint-arculat: 10 kategória × 5 változat a
valódi .pptx-ből renderelt képekkel, alul a 12 diás minta-deck az ügyfél saját tartalmával. Hordozható motor
(`scripts/prezi/`): Mac, Windows, Linux, DO!-függőség nélkül.

**Az 5 változat = az ügyfél 5 karaktere** a `marka-dns.json`-ból (mint a webnél; Lilinél botanikus tábla, tervezőasztal,
préri, kerti napló, arborétum): minden kategóriában ugyanebben a sorrendben, a karakter nevével, a hozzá illő formával és a
karakter saját részletével (`kategoriak.md`). Ha a diagnózis karakter-részlete hiányzik, a forma és a szín különbözteti meg őket.

**Örökölt (nem kérdezünk rá újra):** paletta, pontosan a jóváhagyott betűk, ikonok, lekerekítés és árnyék, fotók és
fotókezelés, motívum (textúra, a márka jelei), logó. **Rögzített:** 16:9, a törzsszöveg legalább 20 pt, a logó jobbra lent.
**Választható:** `kategoriak.md`.

## Kell hozzá
- Python 3.9+, `python-pptx`, `Pillow`; az előnézethez **LibreOffice** (`soffice`; Mac: `brew install --cask libreoffice`,
  Windows: libreoffice.org) és **PyMuPDF** (`pip install pymupdf`) vagy a `pdftoppm`.
- Hálózat a Google Fonts-hoz (a betűk TTF-jei). A betűket a motor a felhasználói betűmappába telepíti (Mac:
  `~/Library/Fonts`, Windows: felhasználói Fonts + regisztráció, Linux: `~/.local/share/fonts`): a PowerPoint és a
  LibreOffice is csak a telepített betűt látja. Ezt mondd el a felhasználónak egy mondatban.
- Arcfelismerés (hogy a kivágás ne vágjon fejet): Macen a Vision (`swift`), máshol az OpenCV, ha telepítve van;
  ha egyik sincs, a webes fázis fókuszpontja (`pozicio`) dönt. Opcionális.

## A folyamat (kb. 3-6 perc gépidő)
```bash
P=<SKILL>/scripts/prezi/prezi.py
python3 $P tema <munkamappa>            # prezi/prezi-tema.json + betűk (letöltés, telepítés) + PREZI-ARCULAT.md
#   -> írd meg a prezi/tartalom.json-t (lent)
python3 $P valaszto <munkamappa>        # 50 változat-kép, 12 minta-dia, prezi-toredek.html, prezi-valaszto.html
```
1. **Előfeltétel:** a `tokenek.json` jóváhagyott (`allapot.jovahagyva`). Ha még nem az, csak előnézetet adsz (a töredék
   ezt jelzi is), végleges kimenetet nem (8. alapszabály).
2. **`prezi/tartalom.json`** (a te dolgod, kb. 5 perc): a 12 minta-dia + a bemutatkozó dia tartalma az ügyfél oldaláról
   (`bemenet/szoveg/*.md`, `arculat.json`), betűre a tényekkel. Séma és példa: `minta-diak.md`, a minta-dia példái
   Koppány Lili adataival készültek (`assets/pelda-lili/`).
   - Csak valódi tény: ha nincs ügyfélvélemény az oldalon, az idézet-dia az ügyfél saját mondata (vagy egy idézet,
     amit ő maga idéz az oldalán). Ha nincs szám, a számos dia az oldal tényeiből dolgozik (ár, határidő, évek).
   - A címsor kulcsszavát `==így==` jelöld; ebből lesz a kiemelés.
   - Ikon: a `prezi-tema.json` → `ikon.fajlok` nevei; fotó: a `fotok[].id`-k. A teljes képernyős változatok maguktól
     fekvő fotót választanak; a kerek portréhoz adj `portre`-t.
   - A „Képernyőkép magyarázattal” dia: a kész webes főoldal képe (pl. a `qa/kesz.png` teteje, 1440 × 900), másold a
     `prezi/forras/` mappába; a pontok helyét (0..1) a képet megnézve add meg.
3. **Ellenőrzés:** a `valaszto` parancs a végén gépi ellenőrzést futtat (a téma betűi vannak-e a PDF-ben, kilógó vagy
   egymásra csúszott szöveg, 20 pont alatti törzsszöveg). Ha jelez, javíts (rövidebb szöveg, más fotó), és futtasd
   újra. Utána **nézd meg a képeket** (Read): `prezi/kepek/v-*.jpg` (kategóriánként 5) és `m-*.jpg` (minta-deck).
   Figyelj: arc a szöveg mögött, olvashatatlan kontraszt, a kiemelés a jó szón van-e, üres hely.
4. **Az arculat-központba:** az `epit.py kozpont` magától beilleszti a `prezi/prezi-toredek.html`-t a Prezentáció fülre.
   **Publikáláskor a képeket is fel kell tölteni** (`files`): minden `prezi/kepek/*` ugyanazon az útvonalon
   (`{"prezi/kepek/v-cimdia-A.jpg": "<munkamappa>/prezi/kepek/v-cimdia-A.jpg", ...}`), mert a töredék így hivatkozik
   rájuk. Ugyanarra az URL-re publikálj, mint a webes fázist.
   Önálló teszt: `prezi/prezi-valaszto.html` (a képek: `prezi/kepek/`); artifactként is publikálható
   (`capabilities: {"db": {}}`, a `kepek/*` fájlokkal).
5. **Visszajelzés:** `ArtifactData get`, collection `arculat`, doc `prezi-v<verzio>`. A `gepi` mező (JSON-szöveg) a
   döntések; mentsd fájlba, és:
   ```bash
   python3 $P valasztas <munkamappa> prezi-valasztas.json      # a véglegesek a témába, a megjegyzések kiírva
   ```
   Foglald össze 3-6 pontban, mit értettél. „Kérek újakat” vagy sok kritika: módosítsd a tartalmat vagy a
   változatot (`references/prezi/kategoriak.md`), `--verzio 2 --elozo prezi-valasztas.json`, ugyanarra az URL-re.
   Helyi fájlnál a felhasználó a „Visszajelzés másolása” gombbal adja vissza ugyanezt (a `valasztas` parancs ezt is
   beolvassa).
6. **Jóváhagyás után** (`jovahagyva: true` a dokumentumban, vagy az `arculat/fazisok` → `prezi`):
   ```bash
   python3 $P valasztas <munkamappa> prezi-valasztas.json --jovahagyva
   python3 $P minta <munkamappa>        # a végleges minta-deck (.pptx, PDF, PNG) + PREZI-ARCULAT.md
   ```
   Frissítsd az `allapot.json`-t (`prezi.allapot = "jovahagyva"`), és mondd el: hol a minta-deck, a leírás, és hogy
   ezután „Készíts prezentációt az arculatom szerint ebből a vázlatból” kéréssel jöhet bármelyik új prezi.

## Új prezentáció a jóváhagyott arculattal
```bash
python3 $P deck vazlat.json --tema <munkamappa>/prezi/prezi-tema.json --png
```
A `vazlat.json` a diák listája (`minta-diak.md`); a motor védetten ment (a kézi javításokat nem írja felül:
megáll, és kiírja, mely diák változtak; felülírni csak `--felulir`-ral, a felhasználó jóváhagyásával). A `--png` a
`png/<név>/` mappába renderel és ellenőriz. Nézd meg a képeket, mielőtt átadod.
Google Drive-on (felhős meghajtón) a mentés időtúllépésnél pár másodpercig újrapróbál, a lenyomatot és a gépi
másolatot pedig atomian írja. Ha a 4-es kóddal áll le, nem írt felül semmit: várj pár percet, és futtasd újra. Ha a
prezi kiíródott, de a lenyomat elmaradt, a motor kiírja a pótló parancsot (`python3 <motor>/mentes.py potol <prezi.pptx>
<lenyomat eleje>`); ezt akkor futtasd, ha a fájlt azóta senki nem nyitotta meg.

## A márka-skillbe (önálló prezi-csomag)
```bash
python3 $P csomag <munkamappa> <célmappa>      # prezi-tema.json + motor/ + betűk, ikonok, fotók, logó, leírás
python3 <célmappa>/motor/prezi.py deck vazlat.json --tema <célmappa>/prezi-tema.json --png
```
A csomag minden útvonala a saját mappájához relatív (kb. 8 MB), így a márka-skill ZIP-jében is működik: az ügyfél
Claude-ja az AI arculat-generátor nélkül is tud decket építeni a jóváhagyott prezentációs arculattal.

## Ha valami hiányzik (a motor nem áll le)
- **Nincs ikon** (pl. az OpenAI nem generált): a tartóban a márka jele áll; a kimenet figyelmeztet.
- **Nincs fotó**, vagy rossz azonosító: a márka jelével kitöltött lap; a teljes képes változatok fotó nélkül, a
  márka textúrájával készülnek.
- **Képernyőképek** (alkalmazás, weboldal; álló PNG vagy `screen` a nevében): nem vágjuk teljes képernyős háttérré,
  hanem készülék-keretben, egészben mutatjuk.
- **Hiányzó levezetett színek** (régebbi tokenfájl): a téma a márkaszínek keveréséből pótolja őket.
- **Túl hosszú kicker**: 12 pontig kisebbedik, utána figyelmeztet (rövidítsd).

## Ismert buktatók
| Buktató | Megoldás |
|---|---|
| A PDF-ben idegen betű (pl. Arial) | A téma betűje nincs telepítve: `python3 $P betuk <munkamappa>`, aztán újra. |
| A címbetű a weben 600-as, a dián 700-as | Szándékos: a PowerPoint csak a normál és a félkövér súlyt kezeli egységesen. |
| Arc a szöveg mögött a teljes képes dián | Adj másik (fekvő, tájkép) fotót a `fotok` elejére. |
| Túl hosszú cím, a kiemelés két sorba törne | A motor elé tör vagy kisebbít; ha így sem szép, rövidíts. |
| `soffice` nem található | Telepítsd a LibreOffice-t, vagy add meg az útját: `SOFFICE=/út/soffice`. |
| A LibreOffice nem lát betűt a saját profiljából | Macen ez így van: ezért kell a telepítés. |
