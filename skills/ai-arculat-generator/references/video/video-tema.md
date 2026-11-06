# `video-tema.json` és `video-tokens.css`: a videós arculat szerződése

A vágómotorok (a tag vágó skillje, a DO! saját vágó skilljei, a HyperFrames-kompozíció, a kivágásos rétegek) ebből a
két fájlból olvassák a márkát. A `tokenek.json`-ból készül (`references/tokenek-szerzodes.md`): új színt és új betűt
nem vezet be, csak a videós szerepekre fordítja és ahol kell, a márka saját színéből árnyalatot képez.

## `video-tema.json`
| mező | tartalom |
|---|---|
| `verzio`, `marka`, `forras` | a szerződés verziója (1), a márka, és melyik `tokenek.json`-ból (állapottal) készült |
| `allapot` | `forras`: `ajanlott` vagy `valasztott`, `jovahagyva`, `video_verzio`, `datum` |
| `szinek.alap` | a tokenek színei változatlanul |
| `szinek.szerepek` | `szoveg_felvetelen`, `kiemeles_felvetelen` (az aktív szó, legalább 6:1 a sötétítéshez), `szoveg_kartyan`, `masodlagos_kartyan`, `halvany_kartyan`, `kiemeles_kartyan`, `kartya`, `kartya_keret`, `papir`, `panel_a`/`panel_b`, `pill_hatter`/`pill_szoveg`, `akcent`/`akcent_szoveg` (csak fehér, ha olvasható; különben `null`), `akcent2`, `mely`/`mely_szoveg`, `fo`/`fo_szoveg`, `scrim` (a sötétítés alapszíne), `figyelmezteto`, `rendben`, `haladassav` |
| `szinek.kontraszt` | minden használt szövegpár WCAG-aránya és `ok` jelzője |
| `szinek.tiltasok`, `szinek.megjegyzesek` | pl. „sötét szöveg akcentszínen tilos”; miből lett a kiemelés |
| `betuk` | `felirat` (800-900, ő/ű), `cim` (a címbetű, ha legalább 700), `cimke`, `kez`: `csalad`, `suly`, `min`/`max`, `google_css`, `forras`, `hasznalat`; `megjegyzesek` (pl. pótbetű), `ellenorzes` |
| `forma` | `r_kartya_px` (a webes ×3, 4-48), `r_pill_px` (999 = kapszula), `keret_px`, `arnyek_kartya`, `arnyek_szoveg` |
| `motivum` | `jel`, `formak_svg`, `textura` (`szintvonalak`, `levelek`, `pottyok`, `racs`, `csikok`, `hullam`, `papir`, `motivum`), `textura_nev` (keverésnél a nevek +-szal), `textura_forma` (a mintához használt forma a `formak_svg`-ből), `dekor`, `hatar`, `kevert` |
| `ikon`, `ikon_szabaly` | a webes ikonstílus (előtag, fájlok); videón legalább 88 px, a felvételen csak a fehér sziluett |
| `foto`, `logo`, `hangnem` | a tokenekből |
| `formatumok` | `9x16`: 1080×1920, safe zone felül 230, alul 420, jobbra 120, a tartalomoszlop x 60-960, felirat 1140-1310, kártya 1340-1510, hírfolyam 4:5 (y 240-1680); `16x9`: 1920×1080, safe 54/80/96/96, alsó harmad 770-990 |
| `szabalyok` | a minden vágásra érvényes szabályok (85% felvétel, semmi az arcon, safe zone, helyesírás…) |
| `valasztas` | `valtozatok` {kategória: változat}, az ügyfél `megjegyzesek`-e, `altalanos` |
| `elemek` | a választott változatok pontos értékei kategóriánként (a `vegleges` után): pl. `felirat.meret_px`, `mozgas.be`, `hangulat.bpm`, `kartya.css` |

## `video-tokens.css`
- `@import` a Google Fonts betűkre (helyi .ttf-fel `@font-face`-szel felülírható, a HyperFrames-renderhez ez a biztos).
- `:root` változók: `--v-fo`, `--v-fo-szoveg`, `--v-akcent`, `--v-akcent2`, `--v-mely`, `--v-papir`, `--v-kartya`, `--v-keret`,
  `--v-szoveg-kartyan`, `--v-masodlagos`, `--v-halvany`, `--v-kiemeles-kartyan`, `--v-szoveg-felvetelen`,
  `--v-kiemeles-felvetelen`, `--v-pill`, `--v-pill-szoveg`, `--v-akcent-szoveg`, `--v-scrim`, `--v-scrim-eros`,
  `--v-figyelmezteto`, `--v-rendben`, `--v-panel`, `--v-haladassav`, `--v-betu-felirat`, `--v-suly-felirat`, `--v-betu-cim`,
  `--v-suly-cim`, `--v-betu-cimke`, `--v-betu-kez`, `--v-r-kartya`, `--v-r-pill`, `--v-keret-px`, `--v-arnyek-kartya`,
  `--v-arnyek-szoveg`, `--v-safe-felul`, `--v-safe-alul`, `--v-safe-jobbra`, `--v-oszlop-x`, `--v-oszlop-szel`, `--v-felirat-y`, `--v-kartya-y`.
- A `vegleges` után a választott elemek CSS-e is benne van, `.v-szinpad` alá szűkítve (`.v-szinpad .k.k-keretes`,
  `.v-szinpad .cap .g`, `.v-szinpad .nv.nv-kartya`…): ugyanaz, amit az ügyfél az előnézetben látott.

## Ha egy vágómotor ebből dolgozik
- A színt és a betűt **mindig** innen vedd, soha ne égesd be (a minta:
  minden szín CSS-változó a gyökéren, márkaváltás egy pillanatban).
- A felirat és a kártya helye a `formatumok` és az `elemek` szerint; a fej mért helyéhez igazítsd (a vágó skill 5.5).
- A hangulat (`elemek.hangulat`) a zene és az effektcsaládok karaktere; a hangot a vágó skill a saját készletéből vagy
  generálva teszi alá (a választó hangmintái csak a karaktert mutatják).
