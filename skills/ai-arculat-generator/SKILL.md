---
name: ai-arculat-generator
description: >
  AI ARCULAT-GENERÁTOR (béta): egy weboldal-URL-ből a vállalkozás teljes, egyedi arculata három fázisban, egy közös
  ARCULAT-KÖZPONTBAN: 1) WEBES arculat-választó (paletta, betűk, ikonok, gombok, kártyák, textúra, mozgás + az oldal
  szekciói, mind 5-5 változatban, élő oldallal), 2) PREZENTÁCIÓS arculat (szerkeszthető PowerPoint, minta-diák),
  3) VIDEÓS arculat (felirat, hook, kártyák, vágási stílus). Minden fázis a jóváhagyott előzőből örököl; a végén saját
  márka-skill (ZIP) és arculati kézikönyv készül. Használd, ha valaki ilyet kér: "csinálj arculatot a weboldalamhoz",
  "arculat a vállalkozásomnak", "milyen színek, betűk legyenek", "prezentációs arculat", "videós arculat",
  "arculat-választó", "arculat-központ", vagy beküld egy URL-t, hogy legyen szebb. Ha a munkamappában már van
  jóváhagyott arculat (tokenek.json, allapot.json), a következő fázissal folytasd.
metadata:
  version: 0.9.0-beta
---

# AI arculat-generátor (béta)

Egy URL-ből egyedi, márkára szabott arculat, amit az ügyfél **maga választ ki** egy élő, kommentelhető
arculat-központban, három fázisban: **web → prezentáció → videó**. Minden fázis a jóváhagyott előzőből örököl
(színek, betűk, ikonok, formák), a végén saját márka-skillt kap, amivel bárki a csapatából ugyanígy kérhet új anyagot.

A motor kész: a `scripts/` alatt minden lépésnek van szkriptje. **A te dolgod a márkára szabott tartalom**: a
márka-diagnózis, a generátorok javaslatainak finomítása, az opciók megírása, az indoklások, a szövegek.

## Az egyediség szabálya (ezért készült ez a változat)

A régi generátor minden ügyfélnek ugyanazt a 6 paletta-archetípust, ugyanazokat a kedvenc betűket, ugyanazt az 5
ikonstílust és ugyanazt a 25 gombot-kártyát adta, csak más színben. Itt ez tilos, és a motor ellenőrzi:

1. **Márka-diagnózis minden futás elején** (`marka-dns.json`, `references/8-marka-dns.md`): szakma, közönség, hangnem,
   tárgyi világ (tárgyak, anyagok, formák, legalább 6 névvel ellátott szín), formanyelvi tengelyek, és mit jelent
   nála az 5 karakter. A választó tetején „Így látunk téged” címmel olvassa az ügyfél.
2. **Az 5 karakter a váz** (elegáns · modern · merész · barátságos · klasszikus), de a tartalma ügyfelenként más.
   Külön „kreatív koncepció” réteg nem kell.
3. **Paletta: `paletta_gen.py`** (OKLCH, kontraszt, különbözőség; egy hű és egy sötét kötelező).
   **Betű: `betu_valaszto.py`** (204 betűs, gépileg ő/ű-ellenőrzött katalógus; a túlhasznált kedvencek csak
   indoklással). **Ikon: `ikon_technika.py`** (31 technikás szótár, öt különböző családból, ügyfélre írt csavarral).
4. **Komponensek**: minden címsor, alcím, gomb, kártya és fotó opciót az ügyfélre írsz, szakmai részlettel
   (`reszlet`). Recept: `references/7-alap-es-tema.md`.
5. **`valtozatossag.py`**: a választó építése ezt is lefuttatja, és ha a változatok túl hasonlók, sablonosak, vagy
   hiányzik a diagnózis, NEM épít. Nincs futások közötti emlékezet: az egyediség az ügyfélből jön.

## Fázisok és kapuk

| Fázis | Mit kap az ügyfél | Kapu | Kimenet a munkamappában |
|---|---|---|---|
| 1. Web | Arculat-választó a központ „Web” fülén (23 kategória, 5-5 változat, élő oldal) | „Jóváhagyom a webes arculatot” (kétkattintásos) | `arculat.json`, `marka-dns.json`, `tokenek.json`, `web/` (fooldal.html, DESIGN-RENDSZER.md, tokenek.css) |
| 2. Prezentáció | Prezi-választó a „Prezentáció” fülön, 12 minta-dia | a prezi fül jóváhagyása | `prezi/` (prezi-tema.json, minta-deck.pptx, PREZI-ARCULAT.md) |
| 3. Videó | Videó-választó a „Videó” fülön, élő előnézetek telefonkeretben | a videó fül jóváhagyása | `video/` (video-tema.json, video-tokens.css, VIDEO-ARCULAT.md, márka-rész a vágó skillhez) |
| Kézikönyv | „Arculati kézikönyv” fül + márka-skill ZIP | (előzetes, amíg nincs minden jóváhagyva) | `ARCULAT.md`, `<marka>-arculat.zip` |

A fázisok sorrendje kötött: a prezi a jóváhagyott webes tokenekből dolgozik, a videó a prezi után jön. Ha az ügyfél
a központban jóváhagy, az `arculat/fazisok` dokumentumba kerül (`ArtifactData get`), és a webes döntések az
`arculat/web-v<verzio>` dokumentumban vannak (`gepi` mező → `valasztas.json`). **Folytatás:** új beszélgetésben
először nézd meg a munkamappát: ha van `allapot.json` (lásd lent) és `tokenek.json`, ne kezdd újra, hanem olvasd ki az
ügyfél döntéseit az artifactból, és lépj a következő fázisra.

```jsonc
// allapot.json (a munkamappa gyökerében; minden fázisváltásnál frissítsd)
{"marka": "koppanylili", "kozpont_url": "https://claude.ai/artifact/…", "web": {"allapot": "dontesre-var|jovahagyva", "verzio": 1},
 "prezi": {"allapot": "zarva|keszul|dontesre-var|jovahagyva"}, "video": {"allapot": "…"}, "marka_skill": null}
```

## Alapszabályok

| # | Szabály | Miért |
|---|---|---|
| 1 | **Első futás = arculat-központ a webes választóval.** Soha ne építs rögtön végleges oldalt. | Az ügyfél akarja kiválasztani. |
| 2 | **Minden kategóriában 5 opció**, 5 tényleg más karakterrel, mind márkára hangolva, szakmai részlettel. | Ettől van értelme választani, és ettől nem sablon. |
| 3 | **A tények szentek.** Árak, nevek, címek, helyszín, számok csak az oldalról, betűre. Ha egy régebbi anyagban van, de az oldalon most nincs, hagyd ki és jelezd. | Hitelesség. |
| 4 | **Az ügyfél arculata a kiindulás.** A logó marad; egy paletta a mostani színek hű változata; ha a saját betűje a katalógusban van, a hű karakter örökölheti. | Frissítés, nem idegen márka. |
| 5 | **Ne kérdezz feleslegesen.** Ami hiányzik, levezeted; a végén 3-5 sorban jelzed, mit feltételeztél. Csak az OpenAI-kulcsot és a hálózatot kérdezd, ha nincs. Élő bemutatón a 3 kérdéses briefet se. | Egy URL, egy központ. |
| 6 | **Magyar szöveg, emberi hangon**: nincs hosszú gondolatjel, nincs „nem X, hanem Y”, nincs emoji, nincs töltelék. | Ne legyen AI-szaga. |
| 7 | **A kulcsot soha nem írod ki**, nem teszed fájlba a kimenet mellé, nem kerül a HTML-be. | Biztonság. |
| 8 | **A prezi és a videó csak jóváhagyott webes tokenekből ad végleges kimenetet.** Előtte csak előnézet. | Az öröklés így marad tiszta. |

## A folyamat

### 0. Előkészítés (1 perc)
- Munkamappa: Claude Code-ban a felhasználó mappájában `<marka>-arculat/`; Claude.ai-ban `/mnt/user-data/outputs/<marka>-arculat/`. A skill mappája: `<SKILL>`.
- **Van már munka?** `allapot.json` / `tokenek.json` / `valasztas.json` a mappában → folytatás (lásd fent).
- Kulcs: `python3 <SKILL>/scripts/ikon_generalo.py --check` → `OK` / `NO_KEY` (`references/1-folyamat.md`).
- Hálózat: ha a letöltés hibázik (Claude.ai-ban tiltott domain), `references/1-folyamat.md` → „Hálózat”.

### 1. Kinyerés (10-20 mp)
```bash
python3 <SKILL>/scripts/oldal_kinyero.py <url> <munkamappa>          # főoldal + aloldalak + a stíluslapok háttérképei (bg-*)
python3 <SKILL>/scripts/tablo.py <munkamappa>/bemenet/kepek --ki <munkamappa>/tablo-fotok.jpg --sakk
```
Olvasd el: `bemenet/arculat.md`, `bemenet/szoveg/*.md` (minden tény innen), nézd meg a fotótablót és az
`eredeti-fooldal-1440.png`-t. A CSS-ből kiolvasott színek között ott vannak a WordPress alapszínei is (#0693e3,
#cf2e2e…): a valódi márkaszínt a gyakoriságból és a képernyőképből döntsd el.

### 2. Márka-diagnózis → `marka-dns.json` (5-10 perc, a legfontosabb gondolkodás)
Séma és példák: `references/8-marka-dns.md`. Utána a három generátor:
```bash
cd <munkamappa>
python3 <SKILL>/scripts/paletta_gen.py javasol marka-dns.json --minta qa-paletta.png
python3 <SKILL>/scripts/betu_valaszto.py marka-dns.json --paletta paletta-javaslat.json
python3 <SKILL>/scripts/ikon_technika.py marka-dns.json --paletta paletta-javaslat.json
```
Nézd át a javaslatokat (a palettaképet Read-del). Cserélj, ha valami nem illik (a betűválasztó és az ikontechnika
karakterenként 3 másik jelöltet is kiír), nevezd el a palettákat és a betűpárokat az ügyfél szavaival, és írd meg
a `miert`-eket a márkáról. Az ikonstílusok `elotag`-ját egészítsd ki az ügyfélre írt csavarral (`references/5-ikonok.md`).

### 3. `arculat.json` (a választó tartalma)
Séma: `references/4-arculat-json.md`. Működő példa a teljes új folyamattal: `assets/pelda-lili/` (tájépítész:
`marka-dns.json`, `gen_arculat.py`, javaslat-fájlok). Ebben a sorrendben töltsd:
1. **opciok.paletta / opciok.betu**: a finomított javaslatokból (5-5, karakterenként egy).
2. **motivum**: a márka saját formái (maszk-SVG, vagy az ügyfél saját rajzai maszkként), szellemszavak, valódi tények.
3. **Tartalom**: a beadott oldal szekcióinak szövege a kinyert anyagból; `szekcio_sorrend` = a beadott oldal szekciói.
4. **fotok**: azonosító → fájl + alt + `pozicio`.
5. **egyedi_opciok**: `cim alcim gomb kartya foto` → 5-5 opció az 5 ügyfél-karakterből, mindegyikben `reszlet`;
   `felulet dekor hatar` → 5-5 ötlet az ügyfél témájából, mindegyik szekciónként is működjön, mert az ügyfél
   többet is kipipálhat, és az oldal váltogatja őket (`references/7-alap-es-tema.md`); `mozgas`; minden szekcióhoz
   5 elrendezés (könyvtárból: `python3 <SKILL>/scripts/epit.py lista`, vagy egyedi `html`+`css`).
6. **opciok.<kategória>**: `lista`, `ajanlott` (a legszebb, legkoherensebb összeállítás), `miert`.

### 4. Ikonok (2-3 perc, kb. 4-5 Ft/ikon)
`ikon-spec.json` (8-14 ikon, 5 stílus a technika-javaslatból, az ajánlott paletta színeivel), aztán:
```bash
python3 <SKILL>/scripts/ikon_generalo.py --spec ikon-spec.json
python3 <SKILL>/scripts/tablo.py ikonok --ki tablo-ikonok.jpg --oszlop 14 --meret 110 --sakk
```
Nézd meg a tablót; ami kilóg (szöveg van rajta, más stílus, rossz tárgy), azt töröld és futtasd újra.

### 5. Ellenőrzés és az arculat-központ
```bash
python3 <SKILL>/scripts/valtozatossag.py arculat.json             # a központ építése is lefuttatja
python3 <SKILL>/scripts/epit.py kozpont arculat.json --artifact   # + tokenek.json (az ajánlott opciókból, előzetes)
python3 <SKILL>/scripts/kepernyokep.py <marka>-arculat-kozpont.html --konzol
python3 <SKILL>/scripts/kepernyokep.py <marka>-arculat-kozpont.html qa/komp --csak kat-cim,kat-gomb,kat-kartya,kat-foto
```
Nézd meg a szeleteket (Read). Javítsd: olvashatatlan kontraszt (a másodlagos gomb színes szekcióban!), túlcsorduló
szöveg, áthúzásnak látszó kiemelés, kilógó dísz, hiányzó fotó. Ha nincs Chrome, `scripts/ellenorzo.py` kötelező.

**Publikálás (ha van `Artifact` eszköz, MINDIG így):** a `<marka>-arculat-kozpont-artifact.html`-t,
`capabilities: {"db": {}}`, `icon: "palette"`. Írd az URL-t az `allapot.json`-ba (`kozpont_url`). A második körtől és
minden fázisnál ugyanarra az URL-re publikálj újra. Utána egy ellenőrzés: `ArtifactData list`, collection `arculat`.
Az ügyfélnek írd le 4 lépésben: kattintás = előnézet lent, ★ = végleges, megjegyzés bármelyik opcióhoz, a végén
„Jóváhagyom a webes arculatot”; a döntései maguktól mentődnek, másolni nem kell.

### 6. Visszajelzés feldolgozása (web)
`ArtifactData get`, collection `arculat`, doc `web-v<verzio>`: a `gepi` mező a GÉPI ADAT JSON (mentsd
`valasztas.json`-ba), a `szoveg` az olvasható összefoglaló, a `jovahagyva` a kapu. A textúra, a dekor és a határ
`vegleges` mezője lista is lehet (keverés: az oldal szekcióról szekcióra váltogatja őket; az `epit.py oldal` és a
`tokenek.py` ezt magától kezeli). Olvasd végig a megjegyzéseket:
- **„kérek újakat”** vagy sok negatív megjegyzés egy kategóriában → új opciók abban a kategóriában (a generátorokat
  újrafuttathatod más tippekkel), `verzio` +1, `epit.py kozpont arculat.json --elozo valasztas.json`, ugyanarra az URL-re.
- **Finomítás** („a zöld legyen élénkebb”) → hexa vagy `egyedi_css`. Szövegkérés → a tartalmat írd át.
- **Jóváhagyva** → 7. lépés. Mindig foglald össze 3-6 pontban, mit értettél a megjegyzésekből.

### 7. A webes fázis lezárása
```bash
python3 <SKILL>/scripts/epit.py oldal arculat.json valasztas.json --ki web/fooldal.html --md web/DESIGN-RENDSZER.md
python3 <SKILL>/scripts/tokenek.py arculat.json --valasztas valasztas.json --jovahagyva --ttf
python3 <SKILL>/scripts/epit.py kozpont arculat.json --valasztas valasztas.json --jovahagyva --artifact
```
Ha a végleges paletta más, mint amivel az ikonok készültek: írd át az `ikon-spec.json` színeit, és
`ikon_generalo.py --csak <stílus> --ujra`. A `tokenek.json` (`references/tokenek-szerzodes.md`) a prezi és a videó
fázis bemenete. Ellenőrizd a főoldalt 1440 és 500 px széles képernyőképen, frissítsd az `allapot.json`-t.

### 8. Prezentáció, majd videó
Mindkét fázis a jóváhagyott `tokenek.json`-ból dolgozik, az 5 változat itt is az ügyfél 5 karaktere (`marka-dns.json`),
és egy töredéket ad (`prezi/prezi-toredek.html`, `video/video-toredek.html`), amit az `epit.py kozpont` magától
beilleszt a saját fülére. A fázis jóváhagyását a töredék a központban jelzi (`arculat/fazisok`); a döntések az
`arculat/prezi-v<n>` és `arculat/video-v<n>` dokumentumban vannak (`ArtifactData get`, `gepi` mező).

**Prezentáció** (leírás: `references/prezi/0-prezi-fazis.md`):
```bash
python3 <SKILL>/scripts/prezi/prezi.py tema <munkamappa>          # prezi-tema.json + a betűk letöltése, telepítése
# írd meg a prezi/tartalom.json-t az ügyfél oldaláról (references/prezi/minta-diak.md)
python3 <SKILL>/scripts/prezi/prezi.py valaszto <munkamappa>      # 10 kategória × 5 változat, 12 minta-dia, töredék
python3 <SKILL>/scripts/epit.py kozpont arculat.json --valasztas valasztas.json --jovahagyva --artifact
```
Publikáláskor a prezi képei külön fájlok: a `files`-ba kell a `prezi/kepek/*` ugyanazon az úton (a forrásuk a
munkamappán belül, vagy egy ideiglenes mappába másolva), különben a Prezentáció fül képek nélkül jelenik meg.
Jóváhagyás után: `prezi.py valasztas <munkamappa> prezi-valasztas.json --jovahagyva`, majd `prezi.py minta <munkamappa>`.

**Videó** (leírás: `references/video/folyamat.md`):
```bash
python3 <SKILL>/scripts/video/video.py elokeszit <munkamappa>     # fotó + fejkivágás
# írd meg a video/tartalom.json-t az ügyfél oldaláról (references/video/tartalom.md)
python3 <SKILL>/scripts/video/video.py valaszto <munkamappa>      # élő előnézetek telefonkeretben, töredék
python3 <SKILL>/scripts/epit.py kozpont arculat.json --valasztas valasztas.json --jovahagyva --artifact
```
Jóváhagyás után: `video.py vegleges <munkamappa>` (video-tema.json, video-tokens.css, VIDEO-ARCULAT.md, és a
tananyagos vágó skillbe illeszthető `MARKA-RESZ.md`); ha kéri: `video.py skill` (a vágó skill személyre szabott
másolata ZIP-ben) és `video.py minta` (rövid márkázott minta-MP4). A DO! saját vágó skilljeihez nem nyúlunk.

### 9. Márka-skill és kézikönyv
```bash
python3 <SKILL>/scripts/marka_skill.py <munkamappa>        # -> ARCULAT.md + <marka>-arculat/ + <marka>-arculat.zip
```
A ZIP a Claude-ba feltölthető skill (Customize → Skills → Upload, vagy Claude Code-ban a `~/.claude/skills/` alá).
Benne: SKILL.md (mikor és hogyan használja a márkát), ARCULAT.md, tokenek, ikonok és ikon-spec, logó, a kész főoldal
mint minta, és ha elkészült, a prezi- és videótéma. Záró üzenet 5-8 sorban: mi készült, mit feltételeztél, mit
érdemes még (pl. valódi vélemények, jobb fotók).

## Referenciák (akkor olvasd, amikor ott tartasz)
`references/1-folyamat.md` Claude.ai vs Claude Code, hálózat, kulcs · `2-arculati-mag.md` a generátorok, motívumok,
szakmai részletek · `3-opcio-katalogus.md` a könyvtári opciók · `4-arculat-json.md` a séma · `5-ikonok.md` ikonlista,
technikák, csavar · `6-minoseg.md` ellenőrzőlista, magyar szövegszabályok · `7-alap-es-tema.md` az 5 karakter és a
téma-elemek receptje · `8-marka-dns.md` a márka-diagnózis · `tokenek-szerzodes.md` a közös tokenfájl ·
`betuk.json` a betűkatalógus · `ikon-technikak.json` a technika-szótár.

## Kész-e? (webes fázis)
- [ ] Van `marka-dns.json`, és az „Így látunk téged” blokk konkrét, igaz, kedves.
- [ ] A `valtozatossag.py` rendben (a központ hiba nélkül megépült): 5 különböző paletta egy hűvel és egy sötéttel,
      5 különböző címbetű legalább 3 osztályból, 5 ikontechnika legalább 3 családból, minden komponensben szakmai részlet.
- [ ] A textúra, a dekor és a határ 5-5 ötlete az ügyfél fő témájából jön, és a demóban is jól látszik.
- [ ] Az `ajanlott` mindenhol a szerinted legjobb, a `miert` a márkáról szól.
- [ ] Artifactként publikálva (`capabilities: {"db": {}}`), az URL az `allapot.json`-ban, az `ArtifactData list` lefutott.
- [ ] Az ikonok egységesek stílusonként, átlátszó hátterűek, nincs rajtuk szöveg.
- [ ] Az élő oldal az ajánlottakkal is szép, mobilon sincs túlcsordulás; a konzolban nincs JS-hiba.
- [ ] Minden tény az ügyfél oldaláról jön.

## Ismert buktatók
| Buktató | Megoldás |
|---|---|
| A választó nem épül: „túl hasonló” | A jelzett két opció tényleg ugyanaz más színben: írj másik szakmai részletet, formát, anyagot. |
| Kedvenc betű került be (Fraunces, Playfair…) | Cseréld a betűválasztó „más cím” listájából, vagy írj `kedvenc_indoklas`-t. |
| Régi betű, amiből hiányzik az ő/ű | A katalógusban `ellenorizve: false` (pl. Lato, Lilita One, Fredoka): ne használd; az ügyfél saját Lato-ja sem jó magyar szöveghez. |
| A másodlagos gomb eltűnik a színes szekcióban | `.btn.alt` színe `var(--c0-card)` / `var(--c0-ink)` (az érintetlen alapszínek). |
| A kiemelő csík áthúzásnak hat | Lejjebb (a betűk alsó harmadába) és halványabban. |
| A kézírásos képaláírás felcsúszik a fotóra | Egy sor, `white-space:nowrap; text-overflow:ellipsis`. |
| Hiányzik a hero háttérképe (Elementor, Divi) | A kinyerő a stíluslapok háttérképeit `bg-` előtaggal tölti le; ha mégsem, nézd meg a `post-XX.css`-t. |
| Túl nagy HTML (>12 MB) | Kevesebb fotó, `fotok.<id>.max` 1000-re; az artifact határa 16 MB. |
| Claude.ai: a letöltés 403/tiltott | Hálózati engedély kell (`references/1-folyamat.md`). |
| Az OpenAI 403 „verify organization” | A felhasználó ellenőrizteti a szervezetét a platform.openai.com-on; addig ikon nélkül megy. |
