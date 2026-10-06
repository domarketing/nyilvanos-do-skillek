---
name: pdf-magyar
description: >
  Magyar ékezeteket hibátlanul kezelő PDF készítése Pythonnal és ReportLabbel, a skillbe
  csomagolt Montserrat betűtípussal. Csali PDF-hez (lead magnet), ellenőrzőlistához,
  munkafüzethez, útmutatóhoz, ajánlathoz vagy bármilyen letölthető magyar dokumentumhoz.
  A ReportLab beépített betűi (Helvetica, Times) az ő és ű betűt nem ismerik, ezért a skill
  megmutatja, hogyan kell TTF betűt regisztrálni, és hogyan jönnek a színek a cégprofilból.
  Használd, ha a kérés: "csinálj PDF-et", "csali PDF", "lead magnet PDF", "letölthető
  ellenőrzőlista", "PDF útmutató", "munkafüzet PDF-ben", "magyar szöveg PDF-ben",
  "reportlab", "ékezet", "az ő és ű nem jelenik meg", "fekete négyzet a PDF-ben",
  "font probléma PDF".
---

# Magyar ékezetes PDF (ReportLab + Montserrat)

Ez a skill akkor kell, amikor Pythonból, ReportLabbel készül PDF, és a szövegben magyar
ékezetek vannak. Tipikus felhasználás: csali PDF egy feliratkozó oldalhoz
(`feliratkozo-oldal`), letölthető ellenőrzőlista, rövid útmutató vagy munkafüzet.

A szöveget a felhasználó adja, vagy egy másik skill írja meg. Leadás előtt a szöveg menjen
át a `szovegellenorzo` skillen, ha az elérhető.

## A probléma

A ReportLab alapbetűi (Helvetica, Times-Roman, Courier) csak Latin-1 karaktereket tudnak.
Az **ő** és **ű** (és az **Ő**, **Ű**) ezekkel fekete négyzetként vagy kérdőjelként jelenik
meg. A megoldás: TTF betűtípus regisztrálása, és minden stílusban annak használata.

Ha a környezetben nincs ReportLab: `pip install reportlab`.

---

## 1. A betűtípus a skillben utazik

A Montserrat (normál és félkövér) itt van: `assets/fonts/`. Nem kell letölteni, nem kell
telepíteni. Fix útvonalat ne írj a kódba: a fontmappát mindig a skill mappájából számold
(abból a mappából, ahonnan ezt a SKILL.md-t beolvastad).

```python
from pathlib import Path

SKILL_DIR = Path("<a pdf-magyar skill mappája>")   # Python fájlból futtatva is megadhatod
FONT_DIR  = SKILL_DIR / "assets" / "fonts"
```

Ha a becsomagolt fájl valamiért nem érhető el, ez a függvény sorban végignézi a skill
mappáját, a rendszer betűtípusait, és végső esetben letölti a fájlt egy írható ideiglenes
mappába. Csak olvasható mappába soha ne próbálj írni.

```python
import glob, tempfile, urllib.request
from pathlib import Path

def find_font(filename):
    """Montserrat TTF keresése: skill mappa, rendszerbetűk, végül letöltés."""
    candidates = [
        FONT_DIR / filename,                              # 1. a skillben (alapeset)
        Path.home() / "Library/Fonts" / filename,         # 2a. macOS, felhasználói
        Path("/Library/Fonts") / filename,                # 2b. macOS, rendszer
        Path.home() / "AppData/Local/Microsoft/Windows/Fonts" / filename,  # 2c. Windows
        Path("C:/Windows/Fonts") / filename,              # 2d. Windows, rendszer
    ]
    candidates += [Path(p) for p in                       # 2e. Linux
                   glob.glob(f"/usr/share/fonts/**/{filename}", recursive=True)]
    for c in candidates:
        if c.exists():
            return str(c)

    # 3. Végső eset: letöltés a temp mappába (az mindig írható)
    cache = Path(tempfile.gettempdir()) / "pdf-magyar-fonts"
    cache.mkdir(parents=True, exist_ok=True)
    dst = cache / filename
    if not dst.exists():
        url = "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/" + filename
        urllib.request.urlretrieve(url, dst)
    return str(dst)
```

## 2. Regisztrálás

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

pdfmetrics.registerFont(TTFont("Montserrat",      find_font("Montserrat-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Montserrat-Bold", find_font("Montserrat-Bold.ttf")))

# Ettől működik a <b>...</b> a Paragraph szövegében (különben hibát dob vagy Helveticára vált)
addMapping("Montserrat", 0, 0, "Montserrat")        # normál
addMapping("Montserrat", 1, 0, "Montserrat-Bold")   # félkövér
addMapping("Montserrat", 0, 1, "Montserrat")        # dőlt: nincs külön fájl, normál marad
addMapping("Montserrat", 1, 1, "Montserrat-Bold")   # félkövér dőlt
```

Ezután minden `ParagraphStyle`-ban és `canvas.setFont()` hívásban a `"Montserrat"` és a
`"Montserrat-Bold"` nevet használd.

## 3. Színek és betű: a cégprofilból, ha van

1. Ha van `cegprofil.md` (a projekt fájljai között, a munkamappában vagy a beszélgetésben),
   abból vedd a márkaszíneket (HEX-kód) és a betűtípust. Ezt a `cegprofil` skill készíti.
2. Ha a cégprofil más betűtípust ír, és annak TTF-fájlja megvan (a felhasználó feltölti, vagy
   a gépen elérhető), regisztráld ugyanígy. Ha nincs meg, maradj a Montserratnál, és ezt
   mondd el a felhasználónak.
3. Ha nincs cégprofil, ezek a semleges alapszínek:

| Szerep | Szín |
|---|---|
| Elsődleges (címsáv, címek) | `#2F4B9A` |
| Kiemelés (vonalak, jelölők) | `#F2A93B` |
| Sötét szöveg | `#0F1B3D` |
| Halvány szöveg (lábjegyzet) | `#5A6275` |

## 4. Teljes minta: egyoldalas csali PDF ellenőrzőlistával

```python
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.fonts import addMapping
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Betű (ha a fájl nincs meg, használd az 1. pont find_font() függvényét)
SKILL_DIR = Path("<a pdf-magyar skill mappája>")
FONT_DIR  = SKILL_DIR / "assets" / "fonts"
pdfmetrics.registerFont(TTFont("Montserrat",      str(FONT_DIR / "Montserrat-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Montserrat-Bold", str(FONT_DIR / "Montserrat-Bold.ttf")))
addMapping("Montserrat", 0, 0, "Montserrat")
addMapping("Montserrat", 1, 0, "Montserrat-Bold")
addMapping("Montserrat", 0, 1, "Montserrat")
addMapping("Montserrat", 1, 1, "Montserrat-Bold")

# Színek (cegprofil.md-ből, vagy a semleges alapszínek)
PRIMER = colors.HexColor("#2F4B9A")
KIEMELO = colors.HexColor("#F2A93B")
SOTET = colors.HexColor("#0F1B3D")
HALVANY = colors.HexColor("#5A6275")

def S(name, **kw):
    alap = dict(fontName="Montserrat", fontSize=10.5, leading=16,
                textColor=SOTET, spaceAfter=6)
    alap.update(kw)
    return ParagraphStyle(name, **alap)

cim_s     = S("cim", fontName="Montserrat-Bold", fontSize=22, leading=28,
              textColor=colors.white, alignment=TA_CENTER, spaceAfter=0)
szakasz_s = S("szakasz", fontName="Montserrat-Bold", fontSize=13, leading=18,
              textColor=PRIMER, spaceBefore=12, spaceAfter=8)
torzs_s   = S("torzs")
jegyzet_s = S("jegyzet", fontSize=8, textColor=HALVANY, alignment=TA_CENTER)
doboz_s   = S("doboz", fontSize=12, textColor=PRIMER)

def cimsav(szoveg):
    t = Table([[Paragraph(szoveg, cim_s)]], colWidths=[16*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMER),
        ("TOPPADDING", (0, 0), (-1, -1), 18), ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LINEBELOW", (0, 0), (-1, -1), 4, KIEMELO),
    ]))
    return t

def lista(tetelek):
    sorok = [[Paragraph("\u25a1", doboz_s), Paragraph(t, torzs_s)] for t in tetelek]
    t = Table(sorok, colWidths=[0.8*cm, 15.2*cm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return t

doc = SimpleDocTemplate("csali.pdf", pagesize=A4,
                        leftMargin=2.5*cm, rightMargin=2.5*cm,
                        topMargin=2*cm, bottomMargin=2*cm,
                        title="Ellenőrzőlista", author="")
story = [
    cimsav("Öt lépés az első ügyfélig"),
    Spacer(1, 0.6*cm),
    Paragraph("Ez az ellenőrzőlista abban segít, hogy <b>egy hét alatt</b> "
              "végigmenj az első lépéseken.", torzs_s),
    Paragraph("Mit csinálj ezen a héten?", szakasz_s),
    lista([
        "Írd le egy mondatban, kinek segítesz és miben.",
        "Gyűjts össze három kérdést, amit a vevőid a leggyakrabban feltesznek.",
        "Válaszolj meg egyet egy rövid bejegyzésben.",
    ]),
    Spacer(1, 1*cm),
    Paragraph("Ár: 12\u00a0900 Ft", torzs_s),
    Paragraph("Ékezetpróba: árvíztűrő tükörfúrógép, ÁRVÍZTŰRŐ TÜKÖRFÚRÓGÉP", jegyzet_s),
]
doc.build(story)
```

A `title` és `author` mező a PDF tulajdonságaiban látszik: töltsd ki a cég nevével vagy a
dokumentum címével.

## 5. Szabályok

1. **Helvetica és Times nem kell** magyar szöveghez. A `getSampleStyleSheet()` stílusai
   Helveticát használnak: vagy ne használd őket, vagy írd át a `fontName`-et.
2. **Minden `ParagraphStyle`-ban** add meg a `fontName="Montserrat"` (vagy `-Bold`) értéket.
3. **A `<b>` címke** csak az `addMapping()` hívások után működik (2. pont).
4. **Ezek a jelek hiányoznak a Montserratból**, négyzetként jelennének meg: pipa (✓ ✔),
   telt kör (●), csillag (★), üres jelölőnégyzet (☐) és minden emoji. Helyettük jó:
   `•` felsorolásjel, `–` gondolatjel, `→` nyíl, `□` és `■` négyzet.
   Ha mégis pipa kell, rajzold ki a canvasra vonalakkal.
5. **Számok tagolása:** a magyar írásmód szóközzel tagol (12 900 Ft). Nem törő szóközt
   használj: `"\u00a0"`. A keskeny nem törő szóköz (`"\u202f"`) **nincs** a Montserratban.
6. **Alsó és felső index:** `<sub>` és `<super>` címkével a Paragraph szövegében.
7. **UTF-8:** a .py fájlt UTF-8 kódolással mentsd, és a szöveget ne kódold át.
8. **Ellenőrzés:** a kész PDF-ből olvasd vissza a szöveget (például `pypdf` vagy
   `pdftotext`), és nézd meg, hogy az ő és ű megvan-e. Ha van rá mód, nézz rá képként is.

## Ellenőrzőlista leadás előtt

- [ ] A TTF be van regisztrálva (`pdfmetrics.registerFont()`), és az `addMapping()` is lefutott
- [ ] Minden stílus Montserratot (vagy a cégprofil betűjét) használja
- [ ] Nem maradt `styles['Normal']` vagy más Helvetica-stílus a kódban
- [ ] A színek a cégprofilból jönnek, vagy a semleges alapszínek
- [ ] Nincs a betűből hiányzó jel (pipa, emoji, keskeny szóköz)
- [ ] A visszaolvasott szövegben megvannak az ékezetek (á, é, í, ó, ö, ő, ú, ü, ű)

## Licenc

A Montserrat betűtípus a SIL Open Font License 1.1 alatt használható; a licenc szövege:
`assets/fonts/OFL.txt`.
