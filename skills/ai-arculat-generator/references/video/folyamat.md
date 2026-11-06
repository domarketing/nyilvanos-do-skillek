# A videó fázis (3. fázis, béta)

A webes (és a prezentációs) arculat jóváhagyása után jön. Örököl: a jóváhagyott színeket, betűket, ikonokat, lekerekítést,
árnyékot, díszítő motívumot, logót és hangnemet a `tokenek.json`-ból. Ezekre nem kérdez rá újra: a választóban csak
„Örökölt elemek” összefoglalóként látszanak.

Az ügyfél a vágó skillt a magyar tananyagból kapja (domarketing.hu/ai-video-vagas, „A vágórendszerünk, üresre
csupaszítva”, `video-vagas/SKILL.md`). **Ezt a skillt nem írjuk át**: a videó fázis kimenete úgy készül, hogy a tag
egy az egyben a saját vágó skilljébe tehesse (a 2.3-as arculati blokk kitöltve + egy „Videós arculatom” rész).

## Lépések

```bash
S=<SKILL>/scripts/video
python3 $S/video.py elokeszit <munkamappa> [--foto <portré>] [--bovites auto|ai|tukor]   # ~10-60 mp
python3 $S/video.py tema <munkamappa>                                                     # előzetes téma + CSS
# video/tartalom.json megírása (lásd lent), utána:
python3 $S/video.py valaszto <munkamappa>          # video/video-toredek.html + video-valaszto.html
python3 $S/video.py kepek <munkamappa>             # (nem kötelező) állóképek ellenőrzéshez
python3 <SKILL>/scripts/epit.py kozpont arculat.json --valasztas valasztas.json --jovahagyva --artifact
# publikálás ugyanarra az URL-re; az ügyfél a Videó fülön választ és jóváhagy
python3 $S/video.py vegleges <munkamappa> [--valasztas video/valasztas.json]
python3 $S/video.py skill <munkamappa> <az ügyfél vágó skilljének SKILL.md-je>             # ha kéri
```

### 1. Előkészítés: fotó és fejkivágás (`elokeszit`)
- A fotó: egy szemből készült portré a vállalkozóról (a `video/tartalom.json` `foto` kulcsa, vagy `--foto`). Ha nincs
  ilyen, a tokenek válogatott fotói közül az első, amelynek leírása portréra utal.
- A `maszk.py` beszélőfejes kivágásba teszi: a fejtető ~560 px-en, a fej ~430 px széles, hogy a fej fölött legyen hely a
  grafikának. A fejet RVM-mel vágja ki (onnxruntime; a kis modellt magától letölti a `~/.cache/ai-arculat/` alá); ha
  nincs onnxruntime, arcfelismerésből becsül (durvább, a `fej.json` `"modszer": "arc"` jelzi).
- **Szoros portrénál** (a fej a kép tetején) a felső sáv hiányzik, ezt ki kell egészíteni:
  - `--bovites auto` (alap): OpenAI képszerkesztés maszkkal, ha van kulcs; a fotó eredeti része pixelre változatlan
    marad, csak a hiányzó háttér készül (~6 Ft, 20-60 mp). `--tema "a spring garden with tall trees"`: mit fessen.
  - `--bovites tukor`: kulcs nélkül, a kép fej nélküli felső sávja tükrözve és felfelé egyre jobban elmosva.
  - Ha a szkriptnek nincs kulcsa, de neked van képszerkesztő eszközöd: `--bovites vaszon` kiírja a
    `video/kepek/vaszon-ai.png`-t (864×1536, a kitöltendő rész átlátszó, ez a maszk is), a kész képpel pedig
    `--bovites kep:<út>` fejezi be.
- Nézd meg a `video/kepek/hatter.jpg`-t: a háttér folytatása hihető-e, nincs-e varrat; a `fej.png` a fej körül tiszta-e.

### 2. A szövegek: `video/tartalom.json`
Az előnézet mondatai. **Minden tény az ügyfél oldaláról** (`bemenet/szoveg/*.md`), betűre: ár, szám, név, szerep.
Kitalált vélemény, díj, szám nincs. Magyarul, emberi hangon: nincs hosszú gondolatjel, nincs „nem X, hanem Y”, nincs
emoji; a nagy kiemelő szövegek végén nincs pont. Séma és példa: `tartalom.md`.

### 3. A választó (`valaszto`) és az arculat-központ
- `video/video-toredek.html` az arculat-központ Videó füle: az `epit.py kozpont` magától beilleszti (ha a fájl a
  munkamappa `video/` mappájában van). A töredék kb. 0,7 MB (a képek WebP-ként beágyazva); a GSAP a cdnjs-ről jön
  (3.12.5), a betűk a Google Fontsról.
- Mentés: `arculat/video-v<verzio>` (`allapot`, `gepi`, `szoveg`, `frissitve`, `verzio`, `jovahagyva`); a fázis
  jóváhagyásakor a töredék a `window.HUB.fazis('video', 'jovahagyva')` hívással jelez (`arculat/fazisok`).
- `video/video-valaszto.html` ugyanez önálló oldalként: helyi teszthez (localStorage, „Visszajelzés másolása”).
- Az ügyfélnek 4 lépésben: kattints egy telefonra (kipróbálás, jobb oldalt az összeállításban látszik), ★ Ez legyen,
  megjegyzés bármelyikhez, a végén „Jóváhagyom a videós arculatot” (kétszer kell kattintani). A fejlécben a
  „✓ Ajánlottak elfogadása” gomb minden olyan kategóriában, ahol nincs végleges, az ajánlottat teszi véglegessé (és ment).
- Élő bemutatón, ha a döntést a chatben mondják ki („mindegyik ajánlott jó, jóváhagyom”): `video.py elfogad <munkamappa>`
  megírja a `video/db-elfogadva.json`-t (az `arculat/video-v1` dokumentum új tartalma, a töredék formátumában: minden
  végleges az ajánlott, jóváhagyva; a db-mentésben már meglévő végleges marad) és a `video/valasztas.json`-t. A dokumentumot
  az `ArtifactData` írja be (a `fazisok`-ba `video: jovahagyva`), utána `video.py vegleges`.

### 4. Visszajelzés feldolgozása
`ArtifactData get`, collection `arculat`, doc `video-v<verzio>`: a `gepi` mező a gépi adat (mentsd
`video/valasztas.json`-ba), a `szoveg` az olvasható összefoglaló. Olvasd végig a megjegyzéseket:
- „kérek újakat” egy kategóriában: írj új változatnevet és leírást a `tartalom.json` `valtozatok` kulcsába, vagy kérj
  a változathoz új paramétert (lásd `kategoriak.md`), `verzio` +1, újra `valaszto`, ugyanarra az URL-re.
- finomítás („a felirat legyen nagyobb”, „a kártya ne legyen ennyire kerek”): a `video-tema.json`-ban a megfelelő
  `elemek.<kategória>` értéket írd át a `vegleges` után, és a `video-tokens.css`-ben a változót.
- Mindig foglald össze 3-6 pontban, mit értettél a megjegyzésekből.

### 5. Lezárás (`vegleges`)
A választásokból (végleges, ha nincs: kipróbált, ha az sincs: ajánlott):
- `video/video-tema.json`: a teljes videós arculat gépi formában (színszerepek kontraszttal, betűk, formák, a választott
  elemek pontos értékei a vágómotornak, szabályok, formátumok) → `video-tema.md`.
- `video/video-tokens.css`: `--v-*` változók és a választott elemek CSS-e (a vágó skill kompozíciója ebből olvas).
- `video/VIDEO-ARCULAT.md`: emberi leírás képekkel (`kepek/elem-*.jpg`, `kepek/tablo-valasztott.jpg`).
- `video/MARKA-RESZ.md` + `video/vago-arculat.json`: a vágó skill 2.3-as blokkja kitöltve és a „Videós arculatom” rész.
- Frissítsd az `allapot.json`-t (`"video": {"allapot": "jovahagyva"}`); a márka-skill (`marka_skill.py`) a `video/`
  mappát is beleteszi.

### 6. A tag vágó skillje (`skill`)
Ha a tag kéri („tedd be a videós arculatomat a vágó skillembe”): `video.py skill <munkamappa> <SKILL.md>`. A kimenet a
`video/vago-skill/video-vagas/` mappa (SKILL.md kitöltött 2.3-as blokkal, a 2.3b „Videós arculatom” résszel, a
hivatkozott helyőrzők kitöltve, verziószám +1, változásnapló-sor) és `video-vagas.zip`. A tag a Customize → Skills alatt
lecseréli a régit, és új beszélgetést nyit. A szkriptek a vágó munkamappába kerülnek: a `video-tokens.css` és a logók az
`a/` mappába, a betűk .ttf-fájljai az `a/fonts/` mappába (a `tokenek.py --ttf` már letöltötte őket a `betuk/` alá).

### 7. Minta-videó (ha kérik)
15-25 másodperces márkázott minta a választott elemekkel: `video.py minta <munkamappa> <felvétel.mp4>` (lásd
`elonezet.md`, „Minta-videó”). Ha nincs ügyfélfelvétel, egy semleges mintafelvétellel.

## Kész-e? (videó fázis)
- [ ] Minden előnézet fut és ismétlődik; a Reels-felület és a safe zone kapcsoló működik; a konzolban nincs hiba.
- [ ] A fejkivágás tiszta, a háttér folytatása hihető; a fej sehol nem takar információt.
- [ ] A feliratban helyes az ő és az ű; a felvételen is jó a kontraszt (a `video-tema.json` `kontraszt` táblája).
- [ ] Minden szöveg az ügyfél oldaláról jön, betűre.
- [ ] A `vegleges` lefutott: a négy fájl és a képek a `video/` mappában; a `MARKA-RESZ.md` blokkja kitöltött.
