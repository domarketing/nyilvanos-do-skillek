# prezi-tema.json (a prezentációs arculat egyetlen forrása)

A `python3 <SKILL>/scripts/prezi/prezi.py tema <munkamappa>` írja a `tokenek.json`-ból (és az `arculat.json`
kapcsolat-adataiból) a `<munkamappa>/prezi/prezi-tema.json`-ba. A motor minden diát ebből rajzol (`tema.betolt()` →
`alap.T`). Az útvonalak a munkamappához relatívak, így a mappa másik gépre is vihető.

| Mező | Tartalom |
|---|---|
| `verzio` | 1 |
| `marka` | a tokenek `marka` blokkja (`nev`, `slug`, `url`, `szlogen`) |
| `forras` | `tokenek`, `web_verzio`, `web_jovahagyva` (ha hamis: csak előnézet) |
| `szinek` | a tokenek színei + a `szinek_extra` (`on_*`, `primary_text`, `ink_2`, `ink_3`, `line`, `tint`, `sand`, `hand`) |
| `betuk.cim/torzs/kezi/cimke` | `csalad`, `suly_web` (a jóváhagyott), `suly_dian` (400 vagy 700), `typeface` és `bold` (ahogy a PowerPoint hivatkozik rá), `ttf` (a mért TTF), `ttf_b` (a félkövér), `b_typeface`, `metrika` (`upm`, `ascent`, `descent`, `linegap`, `cap`), `ps` (PostScript-nevek a PDF-ellenőrzéshez), esetleg `figyelem` |
| `forma` | `r_kartya_px`, `r_gomb_px` (999 = kapszula), `arnyek` (`nincs`, `lagy`, `eros`), `keret_px` |
| `ikon` | `stilus_nev`, `technika`, `elotag` (új ikonhoz), `mappa`, `fajlok` {név: útvonal}, `temak` |
| `fotok` | `[{id, fajl, alt, fx, fy, rajz}]` a webes válogatásból; `fx/fy` a fókuszpont (a `pozicio`-ból), `rajz` = átlátszó illusztráció |
| `fotokezeles` | a webes fotókezelés neve és leírása (az ajánláshoz) |
| `motivum` | `formak_svg` {név: SVG} (natív alakzatként rajzolódik), `jel` (a fő jel), `textura`, `dekor`, `hatar` |
| `logo` | `szines`, `feher` |
| `hangnem`, `komponensek_web` | a webes hangnem és a választott webes elemek (az ajánláshoz) |
| `kontakt` | `nev`, `szerep`, `telefon`, `email`, `web` (a záródiához; az `arculat.json`-ból) |
| `valasztas` | kategóriánként a változat (`cimdia: "D"`...); induláskor az ajánlott |
| `ajanlott`, `ajanlas_miert` | az ajánlott változat és az indoklása (a választó mutatja) |
| `szabalyok` | `arany: 16:9`, `min_torzs_pt: 20`, `min_cimke_pt: 16`, `logo: jobbra lent` |
| `jovahagyva` | a prezi fázis jóváhagyása (a `valasztas` parancs írja) |
| `megjegyzesek`, `ujakat`, `altalanos_megjegyzes` | az ügyfél visszajelzése a választóból |

## Szerepek a motorban
- **Színek**: a layoutok szerepnevet használnak (`primary`, `ink`, `deep`...), és minden felületen (`elemek.Fel`) a
  kontrasztból választanak szövegszínt. Árnyalat csak a téma színeinek keveréke lehet (`alap.kever`).
- **Betűk**: `cim` (címsorok, nagy számok, idézetek), `torzs` (minden szöveg), `kezi` (kézírásos sor, képaláírás),
  `cimke` (kicker, kis címkék). A súlyok leképezése: a jóváhagyott súly <= 500 → normál, >= 550 → félkövér (700).
  A köztes súly (pl. 600) a PowerPointban külön családnév volna, amit a LibreOffice Macen normálként rajzol; a 700-as
  mindenhol egyformán jelenik meg.
- **Lekerekítés**: `r_kartya_px / 96 × 1,35` hüvelyk (a weben 2 px → a diákon kb. 0,03"), a kapszula 0,5.
- **Logó**: mindig jobbra lent (`alap.logo`), sötét felületen a fehér változat.
