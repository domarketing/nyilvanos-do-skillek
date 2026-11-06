# A 12 minta-dia és a vázlat formátuma

A `prezi/tartalom.json` (a választó és a minta-deck tartalma) és minden új prezentáció `vazlat.json`-ja ugyanazt a
dia-leírást használja: `{"diak": [ {"tipus": ..., mezők...}, ... ]}`. A vázlatban ezen felül: `"tema"` (a
prezi-tema.json útja, a vázlathoz relatív is lehet) és `"ki"` (a pptx neve).

**Általános szabályok**
- A címsorok kulcsszava `==így==`; a motor a választott kiemeléssel rajzolja (doboz, filctoll, aláhúzás, karika, szín).
- `ikon`: a `prezi-tema.json` → `ikon.fajlok` egyik neve. `foto`, `fotok`, `portre`: a `fotok[].id` egyike (vagy a
  munkamappához relatív útvonal).
- Minden diához: `jegyzet` (előadói jegyzet, a dián nem látszik), `hatter`: `"szines"` (ritmustörő) vagy `"alap"`.
  Alapból a `fejezet` és a `kerdes` kapja a ritmustörő hátteret.
- Hosszok, hogy szép maradjon (a motor illeszt, de a túl hosszú szöveg kisebb lesz): cím 3-8 szó, pont-cím 2-5 szó,
  leírás legfeljebb 2 sor (kb. 70 karakter), szám legfeljebb 7 karakter (`200-350`, `2`, `0`, `12`).
- Tények csak az ügyfél anyagaiból. Ha nincs vélemény, nem írunk; az idézet-dia az ügyfél saját mondata.

## A 12 minta-dia (a választó alján, ebben a sorrendben)

| # | `tipus` | Mezők | Lili példája |
|---|---|---|---|
| 1 | `cimdia` | `kicker`, `cim`, `alcim`, `fotok` [2-3] | „A kerted, amit ==annyira szeretsz==” |
| 2 | `fejezet` | `szam`, `kicker`, `cim`, `alcim`, `fotok` [1-3] | „01 · A ==kerttervezés== menete” |
| 3 | `felsorolas` | `kicker`, `cim`, `pontok` [[cím, leírás] × 2-4], `ikon` | Miért válassz engem? (3 pont) |
| 4 | `ket_hasab` | `kicker`, `vezer`, `szoveg`, `pontok` [[cím, leírás] × 3-4] | „Fa nélkül ==nem kert== a kert.” |
| 5 | `folyamat` | `kicker`, `cim`, `lepesek` [[ikon, cím, leírás] × 3-4] | Előzetes egyeztetés → … → tervcsomag |
| 6 | `kartyak` | `kicker`, `cim`, `alcim`, `kartyak` [[ikon, cím, leírás] × 4] | Tanácsadás, növényágyak… |
| 7 | `szamok` | `kicker`, `cim`, `szamok` [[szám, címke, leírás] × 3], `foto` | 200-350 ezer Ft, 2 munkanap, 0 Ft |
| 8 | `idezet` | `kicker`, `idezet`, `szerzo`, `szerep`, `foto`, `portre`, `felirat` | „Mindenkinek kellene egy kert.” |
| 9 | `eset` | `pill`, `kicker`, `cim`, `szoveg`, `pontok` [[cím, leírás] × 2] vagy `szamok` [[szám, címke]], `fotok` [1-2] | Természetközeli évelőágyás |
| 10 | `kerdes` | `kicker`, `kerdes`, `alcim` | „Miért terveztessem meg a kertem…?” |
| 11 | `kepernyokep` | `kicker`, `cim`, `kep`, `kivagas` [x0, y0, x1, y1] (pixel), `url`, `pontok` [[x, y, cím, leírás] × 2-4] | Így kérhetsz ajánlatot |
| 12 | `zaro` | `kicker`, `cim`, `alcim`, `url`, `kontaktok` [[címke, érték]], `fotok` (az első a portré, a teljes képes változat fekvőt keres) | Találkozzunk a ==kertedben== |

A választó a fotókeret-változatokat egy 13. diatípuson mutatja: `bemutatkozo` (`kicker`, `cim`, `szoveg`, `kezi`,
`foto`, `felirat`); a `tartalom.json` → `"bemutatkozo"` kulcs alatt.

## Képernyőkép magyarázattal (új layout)
Balra a kép böngészőkeretben (a címsorában az `url`), rajta számozott pontok; jobbra ugyanazokkal a számokkal a
magyarázat. A `pontok` x, y értéke a (kivágott) képen 0..1: nézd meg a képet, és arra a gombra, címsorra, mezőre
tedd, amiről a sor szól. 2-4 pont az ideális. Jó forrás: a kész webes főoldal (`qa/kesz.png` teteje, 1440 × 900),
egy szoftver felülete, egy űrlap.

## Példa vázlat (6 dia)
```json
{
  "tema": "../prezi-tema.json",
  "ki": "tavaszi-kert.pptx",
  "diak": [
    {"tipus": "cimdia", "kicker": "Koppány Lili · kerttervezés", "cim": "Egész évben ==szép kert==, kevés munkával",
     "alcim": "Hogyan lesz minimális fenntartási igényű a kerted?", "fotok": ["vlinderhof", "lili_mezo"]},
    {"tipus": "kerdes", "kicker": "Kezdjük egy kérdéssel", "kerdes": "Mennyi időt töltenél szívesen a kertedben?"},
    {"tipus": "fejezet", "szam": "02", "kicker": "Második fejezet", "cim": "Mit nyersz, ha ==fákat ültetsz?==",
     "fotok": ["tolgy"]},
    {"tipus": "kartyak", "cim": "A fák ==ajándékai==", "kartyak": [["evszakok", "Árnyék", "…"], ["okologikus", "Jobb mikroklíma", "…"],
     ["fenntartas", "Tisztább levegő", "…"], ["novenyagy", "Élőhely", "…"]]},
    {"tipus": "idezet", "idezet": "…", "szerzo": "Richard Powers", "szerep": "Égig érő történet", "foto": "tolgy"},
    {"tipus": "zaro", "kicker": "Kérj ingyenes konzultációt", "cim": "Ültessünk ==fát== együtt", "url": "koppanylili.hu",
     "kontaktok": [["Telefon", "+36 30 756 8997"], ["E-mail", "hello@koppanylili.hu"]], "fotok": ["lili_portre", "evelo"]}
  ]
}
```
Működő példa: `koppanylili-arculat/prezi/pelda/vazlat.json` → `tavaszi-kert.pptx`.
