# 5 - Ikonok: lista, technikák, generálás

## Melyik ikonok? (8-14 db)
Minden ikon egy konkrét tárgy a márka világából, egy mondatban leírva angolul (a modell angolul pontosabb):
- a **kínálat** kategóriái (pl. tanácsadás, növényágy, kertterv; vagy: fogfehérítés, implantátum, gyerekfogászat),
- a **tények, garanciák, folyamat** lépései (felmérés, határidő, áttervezés, tervcsomag),
- 1-2 jellegzetes tárgy (a csomagolás, a szerszám, a hely).
Ugyanaz az ikon több helyen is szerepelhet. Ikonra SOHA nem kerül szöveg.

## Öt stílus: technika-szótár + ügyfélre írt csavar (nincs fix készlet)

A régi hat fix előtag (lapos, vonal+színfolt, kézzel rajzolt, matrica, agyag, riso) miatt minden ügyfél ugyanazt
kapta. Most a stílusok a `references/ikon-technikak.json` szótárból állnak össze (31 technika, 6 családban: vonal,
lapos, festett, nyomat, anyag, digitális), és mindegyikhez egy ügyfélre írt mondat jön.

```bash
python3 <SKILL>/scripts/ikon_technika.py marka-dns.json --paletta paletta-javaslat.json   # -> ikon-javaslat.json
```

A szkript karakterenként a formanyelvhez és a karakterhez leginkább illő technikát adja, globálisan optimalizálva:
mind az 5 más technika, legalább 3 családból, egy családból legfeljebb kettő, a régi készletből legfeljebb egy, és a
formanyelvhez nagyon nem illő technika (pl. neon egy csendes, kézműves márkánál) nem kerül be. Minden sorhoz kiír
3 másik jelöltet, ha cserélnél.

**A csavar a te dolgod.** Minden stílus `elotag`-ja = a szótár promptja + egy angol mondat az ügyfél tárgyi
világából: milyen anyagból, milyen nézőpontból, milyen rajzmóddal. Példák (Lili, tájépítész):
- tervrajz-nézet: *„Draw every subject the way a landscape architect draws on a garden plan: seen from above, tree
  canopies as soft circles with a centre dot, planting beds hatched in {primary}, paths as dashed double lines.”*
- ceruzaskicc: *„Match the hand of a landscape architect who sketches with soft grey graphite on tracing paper.”*

A csavart a `csavar` mezőbe is írd (a változatosság-ellenőrző ezt nézi). Ha az ügyfélnek van saját rajza vagy
ikonja, a hű karakter stílusa ahhoz igazodjon.

```jsonc
// ikon-spec.json
{"mappa": "ikonok", "quality": "medium", "parhuzamos": 6,
 "szinek": {"primary": "#466231", "accent": "#A85748", "accent2": "#BDA168", "ink": "#131B0D", "paper": "#F6F0E0"},
 "stilusok": [{"id": "iM", "nev": "Modern · tervrajz-nézet", "technika": "tervrajz", "csavar": "Draw every subject…",
               "elotag": "<a szótár promptja> <a csavar>"}],
 "ikonok": [{"nev": "kertterv", "tema": "a landscape architect's garden plan seen from above…"}]}
```
A `{primary}` `{accent}` `{accent2}` `{ink}` `{paper}` helyére az ajánlott paletta színei kerülnek. Ételnél adj hozzá
természetes kiegészítő színt (pl. „warm cream #F2DFA7”), különben zöld lesz a tészta.

## Futtatás, ellenőrzés, újragenerálás
```bash
cd <munkamappa>
python3 <SKILL>/scripts/ikon_generalo.py --spec ikon-spec.json          # csak a hiányzókat generálja
python3 <SKILL>/scripts/tablo.py ikonok --ki tablo-ikonok.jpg --oszlop 14 --meret 110 --sakk
```
- Nézd meg a tablót. Ha egy ikon kilóg (szöveg került rá, rossz tárgy, más stílus), töröld a PNG-t és futtasd újra.
- A végleges paletta ismeretében: írd át a `szinek`-et, és `--csak <választott stílus> --ujra`.
- Költség (gpt-image-2.5, medium, 1024²): kb. 4-5 Ft/ikon; 14 ikon × 5 stílus ≈ 300-350 Ft.
- Utómunka automatikus: átlátszó perem levágása, négyzetre igazítás, 256 px, kvantálás.

## Fotók
Az ügyfél saját fotóit használd (a kinyerő letölti, a stíluslapok háttérképeit is, `bg-` előtaggal). Valódi arcot
soha ne generálj. Ha kevés a fotó: inkább kevesebb fotós változatot válassz, és a záró üzenetben írd le, milyen
fotók hiányoznak.
