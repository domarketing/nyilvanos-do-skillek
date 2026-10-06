---
name: leirat-javito
description: "Automatikus feliratból (WEBVTT .vtt, .srt, YouTube, Google Drive, Zoom vagy más platform auto-felirata, beillesztett feliratszöveg) rendezett, nyelvtanilag javított, SZÓ SZERINTI leiratot készít: webinár, élő oktatás, tréning, kérdezz-felelek, interjú, podcast, meeting. Tördel, beszélőket jelöl, időbélyegez, a saját szótár és a cegprofil.md alapján javítja a félrehallott neveket és márkákat, a maradék neveket és rövidítéseket munka előtt EGYSZERRE kérdezi meg. Hívd elő: 'alakítsd át leirattá', 'csinálj leiratot', 'javítsd a leiratot', 'tördeld', 'VTT-ből leirat', 'felirat', 'átirat', 'a felvétel szövege', 'leiratozd', vagy ha a felhasználó .vtt vagy .srt fájlt csatol. NEM összefoglaló-készítő: ha összefoglalót, posztot vagy e-mailt kérnek egy felvételből, a kész leirat lehet a bemenet, de a szöveget más skill írja. Hangfájlból felirat nélkül nem dolgozik."
---

# Leirat-javító

Nyers automatikus feliratból olvasható, **szó szerinti** leiratot készítesz. Ez nem összefoglaló:
az elhangzottból semmi nem maradhat ki, és a mondatokat sem írod át. Csak rendbe teszed: tördelés,
központozás, nyelvtan, félrehallott nevek, beszélők, időbélyegek.

A leirat gyakran tananyagba, tudásbázisba, kereshető archívumba vagy egy AI-asszisztens
forrásanyagába kerül, ezért a nevek pontossága a legfontosabb. Egy rossz név végigfut az egész anyagon.

## Előkészítés: szótár és cégprofil

- **Szótár:** [`references/szotar.md`](references/szotar.md). Ide kerülnek a felhasználó saját nevei,
  márkái, termékei és a rájuk jellemző félrehallások. **Munka előtt mindig olvasd el.** Alapból üres
  sablon. Ha a felhasználó saját szótárat tett a projekt fájljai közé vagy a munkamappába (például
  `leirat-szotar.md` néven), azt is olvasd el; ütközésnél az az erősebb.
- **Cégprofil:** Ha van `cegprofil.md` (a projekt fájljai között, a munkamappában vagy a
  beszélgetésben), abból dolgozz: a cég, a vezető és a csapat neve, a termékek, szolgáltatások és
  programok neve, a márkanév írásmódja onnan jön. Ha nincs, kérdezd meg a hiányzó minimumot (ki az
  előadó, mi a cég és a fő termékek neve), vagy ajánld fel a `cegprofil` skillt.

Ha a szótár még üres, és van cégprofil, a leirat végén ajánld fel, hogy kitöltöd belőle a szótárat
(ld. 8. lépés).

---

## Munkafolyamat

### 1. Beolvasás

- **Beillesztett szöveg:** dolgozz belőle közvetlenül.
- **Fájl (.vtt / .srt):** 40 KB fölött először tömörítsd. A szkript kidobja az időkódokat, a
  zajszemetet (zene alatti idegen írásjelek, magányos „H” sorok) és a gördülő feliratok
  ismétléseit, és 30 másodpercenként `[óó:pp:mm]` jelölőt tesz a szöveg elé:

  ```bash
  python scripts/vtt_tomorit.py felirat.vtt -o tomor.txt
  ```

  Így a szöveg lényegesen rövidebb lesz, és egy-két olvasással átfér. A nyers VTT-t a fájlolvasó
  eszköz méretkorlátja miatt csak darabokban tudnád végigolvasni.
- **Olvasd végig az egészet**, mielőtt bármit írsz: a nevek a végén (kérdezz-felelek) is előjönnek.
- Nézd meg a hosszát (utolsó időkód) és a szerkezetét: van-e bevezető videó az elején,
  felkonferálás, hány előadó vagy beszélgetőtárs, van-e kérdezz-felelek, felolvasott chatkérdés.

### 2. Nevek és rövidítések: egyetlen kérdéskör

1. Minden nevet, márkát, szoftvert, rövidítést, linket, ami a szótárban vagy a cégprofilban
   **benne van**, kérdés nélkül javíts.
2. Ami **nincs benne**, vagy **ütközik** vele, azt gyűjtsd ki, és **egyszerre, egyetlen
   üzenetben** tedd fel, számozva, tippel:

   ```
   **Az elején bemutatkozó ügyfelek** (ezek a legfontosabbak, névvel mutatkoznak be):
   1. „Kovács Ana”: jól hallom, Kovács Anna? És a vállalkozása: „Napfény Jóga”?
   2. …
   **Felkonferálás / külföldi nevek / egyéb nevek / rövidítések, linkek:**
   …
   ```

   Csoportosíts: bemutatkozók → felkonferálás → külföldi nevek → kérdezők → cégek, helyszínek →
   rövidítések, linkek. Kérd, hogy **csak a javítandót** írja vissza.
3. Ugyanebben az üzenetben kérdezd meg a **formátumot**, ha nem adta meg (ld. 3. lépés). Ezt is
   csak egyszer.
4. **A válasz feldolgozása:** a felhasználó gyakran nem számozva vagy elcsúszva válaszol (kihagy
   egy kérdést, és onnan eltolódik minden). A párosítás alapja a tartalom, a sorszámra ne
   hagyatkozz. Ami így sem egyértelmű, vagy kimaradt, az `[?]` lesz a szövegben. Ne kérdezz újra,
   ne állj meg miatta.
5. Ha a válasz ellentmond a szótárnak, a friss válasz nyer, de a végén szólj az ütközésről.

Ha nincs ismeretlen név, névkérdés sem kell. A formátumot ilyenkor is egyszer kérdezd meg, ha nem adta meg.

### 3. Formátum

Két bevált sablon van. Ha a felhasználó nem mondja meg, melyik kell, kérdezd meg a névlistával
együtt. Ha azt feleli, hogy mindegy, az A legyen.

**A) Rendezett átirat** (fejezetcímek nélkül, a leggyorsabban olvasható):

```markdown
# <A felvétel címe, ahogy a felhasználó megadta>

*Könnyű szerkesztésű leirat: nyelvtan és központozás javítva, a beszélt stílus megtartva. Időbélyegek 5-10 percenként. A `[…]` a forrásfelvételben kisípolt káromkodást jelöli, a `[?]` a bizonytalan nevet.*

---

**[00:00:05]**

**<Előadó neve>:** …

**Résztvevő:** …
```

- Időbélyeg 5-10 percenként, **külön sorban**, `**[óó:pp:mm]**` alakban, mindig a felirat valós
  cue-kezdetéből (ahol új gondolat indul). Témaváltásnál sűríthetsz.
- Fejezetcím nincs.

**B) Tananyag-leirat** (fejezetekre bontva, tananyaghoz, tudásbázishoz):

```markdown
# <Cím> (<éééé.hh.nn.>)

**Dátum:** <éééé. hónap nap.>
**Előadó:** <név>
**Közreműködők:** <nevek>
**Formátum:** <pl. élő online képzés, kérdezz-felelek blokkokkal>
**Forrás:** <pl. Zoom-felvétel automatikus felirata (teljes, szó szerinti leirat)>

---

## Tartalomjegyzék        ← csak 2 óránál hosszabb anyagnál

## [00:00:00] Bevezető: ügyfélvisszajelzések

**Kovács Anna (Napfény Jóga):** …

## [00:10:43] Köszöntés és a mai program
```

- Témablokkonként `## [óó:pp:mm] Fejezetcím` (rövid és tartalmi, kattintásvadászat nélkül).
- Több napos vagy több részes anyagnál `# I. RÉSZ: Első nap (<előadó> előadása)` szintű tagolás;
  az időbélyeg mindig az adott felvétel elejétől számít.
- Word-változatnál a végére kerülhet a `[?]`-es tételek listája.

**Mindkét sablonban közös:**

| Szabály | Hogyan |
|---|---|
| Beszélő | `**Név:**` a bekezdés elején. Beszélőváltásnál új bekezdés. |
| Ismeretlen beszélő | `**Résztvevő:**` (élő közönség), `**Kérdező:**` |
| Névtelen ügyfél, ajánló | `**Ügyfél (nem nevezi meg magát):**` |
| Felkonferáló hang | `**Felkonferálás:**` |
| Ajánló márkával | `**Kovács Anna (Napfény Jóga):**` (B-sablonban) |
| Chatből felolvasott kérdés | Az előadó szövegében: `Péter: „Akkor ezt most hogyan…?”`, utána az előadó válasza. |
| Írásos kérdezz-felelek (csak chat) | `**Szabó Éva (chat):**` külön beszélőként |
| Ha a kérdező élőben visszaszól | külön beszélő (`**Nagy Péter:**`) |
| Interjú, podcast | a műsorvezető és a vendég is névvel |
| Meeting, ha nem mutatkoznak be | `**1. résztvevő:**`, `**2. résztvevő:**`; a kérdéskörben kérdezd meg, ki kicsoda |
| Idézett prompt, felolvasott szöveg | „…” között, a beszélő szövegén belül |
| Kisípolt káromkodás (`[ __ ]`) | `[…]`, **nem pótoljuk**, akkor sem, ha kitalálható |
| Hallható káromkodás | marad, ahogy elhangzott |
| Bizonytalan név vagy szó | `[?]` közvetlenül utána (`Kiss Judit [?]`) |
| Zárás | `*[A felvétel vége]*` |

Az automatikus felirat nem jelzi, ki beszél. A beszélőváltást a tartalomból következtesd ki
(kérdés és válasz, megszólítás, bemutatkozás). Ahol nem egyértelmű, `**Résztvevő:**`.

### 4. Szerkesztési szint

| Szint | Mit jelent | Mikor |
|---|---|---|
| **1. könnyű** (alapértelmezés) | Nyelvtan, központozás, félrehallás javítva. Töltelékszavak, ismétlések, önjavítások, félbehagyott mondatok **maradnak**. Mondat nem íródik át. | leirat, tananyag, tudásbázis |
| 2. közepes | Töltelékszavak és dadogó ismétlések kigyomlálva, a mondatszerkezet és a hangvétel marad. | ha kifejezetten kérik |
| 3. erős | Szerkesztett, írott próza („javított leirat”). | csak kérésre, ez már közel van az összefoglalóhoz |

Könnyű szintnél a szótár 7. szakaszában felsorolt szófordulatok és az általános töltelékszavak
(„ugye”, „na”, „hát”, „szóval”, „nagyon-nagyon-nagyon”) mind maradnak. Az ismétlést se húzd össze.

Mindig javítsd: a nyilvánvaló ASR-szóhibát a szövegkörnyezetből („noró vírus” → norovírus, „díj” a
prezentációban → dia), a szótár házi írásmódját, a számok formáját (`542 000 Ft`, `34%`). Ne
javítsd a tartalmi tévedést, és azt a nevet se, amit az előadó maga mondott rosszul (például egy
könyvet rossz szerzőnek tulajdonít): úgy írd, ahogy elhangzott, és a végén szólj.

### 5. Írás részletekben

- Egy részfájl kb. **15-25 perc** anyag: `<slug>-01.md`, `<slug>-02.md` … a munkamappába. Az első
  rész tartalmazza a fejlécet.
- Minden rész a következő időbélyeggel zárul, a következő rész onnan folytatja. Így látszik, ha
  kimaradt valami.
- **Semmit ne hagyj ki, ne foglalj össze.** Ha elfogy a hely egy részben, inkább vágd ott, és
  kezdj új részt.
- Összefűzés (Mac és Windows alatt is UTF-8-helyesen):

  ```bash
  python scripts/osszefuz.py <slug> --torol     # <slug>-01.md, -02.md … → <slug>.md, a részek törölve
  ```

### 6. Ellenőrzés

```bash
python scripts/felrehallas_scan.py <slug>.md
python scripts/felrehallas_scan.py <slug>.md --szotar leirat-szotar.md   # ha a projektben külön szótár is van
```

A szkript beolvassa a skill szótárát (és a `--szotar` kapcsolóval megadott továbbiakat), és
kilistázza a szótárban rögzített félrehallásokat, néhány általános magyar feliratozási hibát
(„lending oldal”, „fánel”, „szélsz”) és a nyers maradványokat (`[ __ ]`, idegen írásjel,
VTT-időkód). `HIBA` = biztosan rossz, `FIGYELJ` = nézd meg. Javítsd, futtasd újra, amíg a `HIBA`
nulla. Ezen kívül nézd meg kézzel: az eleje és a vége rendben van-e (cím, első mondat, záró sor),
és az utolsó időbélyeg egyezik-e a felvétel végével.

### 7. Kiadás

- A `.md` a fő kimenet. Mondd meg a fájlnevet és a méretet, a `[?]`-ek számát és helyét, és azt,
  amit a szótárhoz képest másképp írtál.
- **Weboldalba illeszthető HTML** (semleges színekkel, mobilra méretezve, a beszélőnév színnel
  kiemelve). Ha a cégprofilban vannak márkaszínek és betűtípus, add meg őket:

  ```bash
  python scripts/md2html.py <slug>.md <slug>-web.html
  python scripts/md2html.py <slug>.md <slug>-web.html --fo-szin "#2F4B9A" --kiemelo-szin "#F2A93B" --sotet-szin "#0F1B3D" --betu "Inter"
  ```

- **Érzékeny tartalom:** ha a felvételen elhangzik, hogy valami „maradjon köztünk” vagy „ne
  kerüljön ki”, vagy konkrét munkatársi, ügyfél-ügyről, fizetésről, elbocsátásról beszélnek,
  **publikálás előtt jelezd** időbélyeggel. A leiratból ne vágd ki magadtól, az a felhasználó döntése.

### 8. A szótár bővítése

Ha a felhasználó új nevet, márkát vagy félrehallást erősített meg:

1. Írd be a szótár megfelelő szakaszába (csapat → 1., ügyfél → 2., saját termék → 3. stb.), a
   félrehallott alakkal együtt, a szótár elején leírt formátumban. Ütközést a 8. szakaszba.
2. A `felrehallas_scan.py` a táblázatokból magától felveszi a félrehallott alakokat, külön listát
   nem kell karbantartani.
3. Hova mentsd:
   - **Claude Code-ban** (vagy ha van írható munkamappa) írd közvetlenül a szótárfájlba.
   - **claude.ai-on** a feltöltött skill fájljai nem módosíthatók tartósan. Add oda a frissített
     szótárat letölthető fájlként, és javasold, hogy tegye a projekt fájljai közé
     `leirat-szotar.md` néven, vagy cserélje le vele a skill `references/szotar.md` fájlját, és
     töltse fel újra a skillt.

---

## Feltöltés weboldalra

- **WordPress:** a HTML-t a bejegyzés vagy oldal **Kódszerkesztőjébe** illessze (szerkesztő → ⋮ →
  Kódszerkesztő), vagy egy „Egyéni HTML” blokkba. A blokkszerkesztő 300 KB körüli anyagnál beragadhat.
- Ha a weboldalon a Claude Oldalak bővítmény fut, a `claude-oldalak-feltolto` skill fel tudja tenni.
- Jelszóval vagy tagsággal védett oldal tartalmát kijelentkezve nem lehet elérni. Ilyenkor a
  felhasználó illeszti be a szöveget.
- WordPress-jelszót vagy alkalmazásjelszót **ne kérj el** a chatben.

## Gyakori buktatók

- **Elcsúszott válaszok** a névkérdésekre: tartalom szerint párosíts (ld. 2. lépés, 4. pont).
- **Egy felvételen belül többféle félrehallás** ugyanarra a névre („Kis Balás” / „Kis Balázs”):
  egységesíts.
- **Átfedő VTT-cue-k:** az időtartamok átfedik egymást, de a szöveg nem ismétlődik; időbélyegnek a
  cue kezdetét vedd.
- **Zene alatti ASR-szemét** (idegen írásjelek, „He.”, „H”): törlendő, a tömörítő kiszedi.
- **Hasonló hangzású rövidítések:** ha a felirat a saját rövidítéseteket egy hasonló hangzású
  másikként hallja, és a szövegkörnyezetből nem dönthető el, melyik hangzott el, tedd be a
  kérdéskörbe.
- **Windows-útvonal ékezettel** (`D:\Letöltések…`): Git Bashből a Python nem mindig találja;
  PowerShellből futtasd.

## Kapcsolódó skillek

- `cegprofil`: nevek, márkák, termékek a szótárhoz.
- `facebook-poszt-iro`, `ertekesitesi-level-iro`: ha a kész leiratból poszt vagy levél készül.
- `claude-oldalak-feltolto`: a HTML-változat feltöltése a Claude Oldalak bővítménnyel.
