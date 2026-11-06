# 2 - Az arculati mag: honnan jön a változatosság és az egyediség

A jó arculati oldalak mélységét hat réteg adja: **felület-textúra, dekor-réteg,
különleges szekcióhatár, metafora-komponensek, mozgás, egyedi ikonok**. A te dolgod, hogy (1) a márka színei,
betűi, formái kerüljenek bele, (2) az opciók tényleg különbözzenek, (3) minden elemben legyen valami, ami csak
ennél az ügyfélnél értelmes.

> **Nincs fix készlet.** A régi változat minden ügyfélnek ugyanazt a 6 paletta-archetípust, ugyanazokat a
> „kedvenc” betűket és ugyanazt az 5 ikonstílust adta, ezért az ügyfelek oldalai összekeverhetők lettek. Most minden
> a márka-diagnózisból (`marka-dns.json`, `references/8-marka-dns.md`) indul, és három generátor ad javaslatot,
> amit te finomítasz. A `valtozatossag.py` nem enged építeni, ha az eredmény túl hasonló vagy sablonos.

## 1. Öt paletta: `paletta_gen.py`

```bash
python3 <SKILL>/scripts/paletta_gen.py javasol marka-dns.json --minta qa-paletta.png    # -> paletta-javaslat.json
```
A jelölt színek: a mostani oldal valódi márkaszínei (`ami_mar_megvan.szinek`) és a szakma tárgyi világának színei
(`targyi_vilag.szinek`, névvel). A szkript OKLCH színtérben dolgozik: karakterenként (elegáns, modern, merész,
barátságos, klasszikus) a karakter világosság- és telítettség-tartományába húzza a jelölteket, harmónia, kontraszt
(WCAG: szöveg/papír legalább 7, gombfelirat legalább 4,5) és a formanyelv szerint pontoz, majd globálisan választ
úgy, hogy az 5 paletta jól elkülönüljön (OKLab-távolság), és egy kiemelő szín legfeljebb két palettában szerepeljen.
Kötelező: **egy hű** (a mostani színek igényesebb változata) és **egy sötét alapon is működő**. Hogy melyik karakter
lesz sötét, azt a formanyelv dönti el (csendes márkánál inkább az elegáns, hangosnál a merész), nem mindig a merész.
A diagnózis `karakterek.<k>.szinek` mezőjével irányíthatod, melyik színek melyik karakterbe kerüljenek.

Utána: nevezd el a palettákat az ügyfél szavaival (pl. „Klasszikus · tölgylevél és sedum-rozsda”), írd meg a
`miert`-et a márkáról, és tedd az `opciok.paletta` alá. Szabályok, amiket a generátor betart és te se rontsd el:
a papír soha nem tiszta fehér, a tinta soha nem tiszta fekete; a harmadik szín (`accent2`) csak apró díszekben
jelenik meg; **tilos a lila-kék AI-gradiens** (#7c3aed, #6366f1…), kivéve ha tényleg az ügyfél színe.

## 2. Öt betűpár: `betu_valaszto.py`

```bash
python3 <SKILL>/scripts/betu_valaszto.py marka-dns.json --paletta paletta-javaslat.json   # -> betu-javaslat.json
```
A katalógus (`references/betuk.json`, kb. 200 betű, mind gépileg ellenőrizve ő Ő ű Ű karakterre) minden betűjének
van osztálya, karakter-illeszkedése (k5), formanyelvi tengelyei (ax), szerepei (cím, szöveg, kézírás, címke) és
témái. A szkript karakterenként pontoz, globálisan választ (5 különböző címbetű, legalább 3 betűtípus-osztály),
a szövegbetűnél kontrasztot keres a címhez, és kiír karakterenként 3 másik címbetűt.

A túlhasznált kedvencek (Fraunces, Playfair Display, DM Serif Display, Bricolage Grotesque, Outfit) pontlevonást
kapnak; ha mégis kell, a betűpárba írj `kedvenc_indoklas`-t (miért éppen ennek az ügyfélnek), különben az ellenőrző
nem enged tovább. Az AI-reflex betűk (Inter, Poppins, Montserrat, Roboto, Open Sans, Lato) csak akkor jöhetnek, ha
az ügyfél saját betűje. Az ügyfél saját betűje (ha a katalógusban van) a hű karakternél bónuszt kap.
Hangolás betűpáronként: `w_display`, `ls_display`, `nagybetus`, `lh_display`, `hero_scale` (vékony/keskeny betűnél
1.1-1.15), `fs_hand` (kicsi x-magasságú kézírásnál 1.3-1.5).

## 3. Motívumok: a márka saját formái (3-4 db)

Kérdés, ami mindig működik: *„Milyen tárgyat, anyagot, formát fog kézbe ennek a szakmának a vevője?”* Nézd a logót
(formák), a nevet (jelentés), a fotókat (tárgyak), és a szakma eszközeit. A formákat maszk-SVG-ként adod meg
(100×100-as vászon, fekete kitöltés, egyszerű zárt formák; vonalnál `stroke='#000'` és vastag vonal). Ha az
ügyfélnek van saját rajza (pl. a weboldal ceruzarajzai), azt is használhatod maszkként (lásd `assets/pelda-lili/`).
Ezekből épül: a **Motívum-minta** textúra, a **lebegő motívumok**, az **óriás jel** (`jel` kulcs; legjobb a logó
egyszerűsített formája), a futószalag elválasztó-jele.

**Szellemszavak** (óriás kontúrszó a szekciók szélén): 1 szó szekciónként, nagybetűvel, a márka nyelvén.
**Futószalag-tények**: 5-7 rövid, VALÓDI tény. **Matricák**: 2-4 nagyon rövid, valódi állítás.

## 4. Egyedi opció (metafora-komponens): minden alap-elemben szakmai részlet

A választóban „Csak nektek” címkével jelenik meg. A címsor, alcím, gomb, kártya és fotó kategóriában **minden**
opciót az ügyfélre írsz (`egyedi_opciok.<kategória>`), és legalább 3-ban (inkább mind az 5-ben) van egy szakmai
részlet, amit a `reszlet` mezőben egy mondattal meg is nevezel. Recept:
1. Vedd az adott karakter ügyfélre írt nevét a diagnózisból (pl. „arborétum”), és kérdezd meg: milyen tárgy, jel,
   anyag tartozik hozzá? (névtábla két csavarral, sorszám-tábla, üvegház-boltív)
2. Ennek 1-2 felismerhető vonása legyen CSS-ben: forma (clip-path, border-radius), anyag (szín, áttetszőség,
   textúra), egy jellegzetes részlet (perforáció, pecsét, méretvonal, washi-szalag, léptékvonal).
3. Kártyánál a CSS `%S .krt{...}` formában (a `%S` a saját data-attribútumra szűkít), és kezeld a fotós kártyát is
   (`%S .krt>.krt-kep{...}`). A logóra `var(--logo-eredeti)` vagy `var(--logo-img)` (sötét palettán a fehér).
4. Hero/szekció egyedi opciónál `html` + `css` (a CSS a saját `.v-<id>` osztályára szűkítsen; reszponzívhoz
   `@container elo (max-width:...)`).

Iparági ötlettár (kiindulás, ne másold): fogorvos → perforált időpont-cédula, kezelési terv kártya, röntgen-panel ·
ács → tervlap-rács kártya, mérőszalag-idővonal, pecsételt árajánlat · pszichológus → jegyzetlap margóvonallal,
borítékos titoktartás · pénzügy → bankkártya chippel, guilloche-keret · ügyvéd → dosszié-fül, iktatószám · kozmetika
→ tükör-keret, kezelés-cédula · oktatás → füzetlap, bérlet-jegy, oklevél · autó → szervizkönyv, mérőóra-számláló ·
kertészet → növénycímke, magtasak, herbárium · ingatlan → alaprajz-kártya, kulcscímke · étterem → étlap-lap,
krétatábla, elviteles doboz.

## 5. Ajánlott kombináció

Az élő oldal az ajánlott opciókkal indul: ez az első benyomás, tehát ez legyen a legszebb, legkoherensebb összeállítás
(egy harsány elem mellé csendesebbek). Utána nézd meg képernyőképen, és ha valami üt, cseréld az ajánlottat.
