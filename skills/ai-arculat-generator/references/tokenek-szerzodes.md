# A közös tokenfájl: `tokenek.json` (1-es szerződés)

A web fázis írja a munkamappa gyökerébe, a prezi és a videó fázis ebből örököl. Jóváhagyás előtt az ajánlott
opciókból készül (`allapot.forras = "ajanlott"`), a webes jóváhagyás után a választottakból
(`"valasztott"`, `allapot.jovahagyva = true`). A prezi és a videó fázis csak jóváhagyott tokenekből ad végleges
kimenetet; ajánlottból csak előnézetet.

```bash
python3 <SKILL>/scripts/tokenek.py arculat.json                                   # ajánlott opciókból
python3 <SKILL>/scripts/tokenek.py arculat.json --valasztas valasztas.json --jovahagyva --ttf
```

`--ttf`: a négy betű TTF-jeit is letölti a `<munkamappa>/betuk/` mappába (a prezi szövegillesztéséhez és a
videó-rendereléshez). **Útvonalak**: minden fájlútvonal az `alap` mappához (a munkamappához) képest relatív.

## Mezők

| Mező | Tartalom |
|---|---|
| `verzio` | a szerződés verziója (1) |
| `marka` | `nev`, `slug`, `url`, `szlogen` |
| `szinek` | `primary`, `accent`, `accent2`, `paper`, `card`, `ink`, `deep` (hexa), `mod`: `vilagos` vagy `sotet` |
| `szinek_extra` | a web motor levezetett színei: `on_primary`, `on_accent`, `on_deep` (olvasható szöveg a színen), `primary_text`, `accent_text` (papíron olvasható változat), `ink_2`, `ink_3`, `line`, `tint`, `sand`, `hand` |
| `betuk.display/body/hand/label` | `csalad`, `suly` (a fő súly; a címnél a cím vastagsága), `sulyok`, `google_css`, `ttf` (lista, `--ttf` után). A `hand` lehet `null` |
| `betuk.beallitas` | a webes finomhangolás: `w_display`, `ls_display`, `nagybetus`, `lh_display`, `hero_scale`, `fs_hand` |
| `forma` | `r_kartya`, `r_gomb` (px; 999 = kapszula), `arnyek`: `nincs`, `lagy` vagy `eros` (kemény, eltolt), `keret_px` |
| `ikon` | `stilus_id`, `stilus_nev`, `elotag` (a kész angol prompt-előtag, színekkel kitöltve; új ikon = előtag + téma), `technika`, `mappa`, `fajlok` {név: útvonal}, `temak` {név: angol téma}, `spec` |
| `foto` | `kezeles` (a választott fotókezelés neve), `kezeles_id`, `leiras`, `mappa`, `valogatott` (útvonalak), `valogatott_info` (`id`, `fajl`, `alt`, `pozicio`) |
| `motivum` | `formak_svg` {név: teljes SVG, 100×100, fekete kitöltés}, `jel` (a fő jel neve), `textura`, `dekor`, `hatar` (`id`, `nev`, `leiras`; keverésnél lista), `szellemszavak`, `ticker`, `matricak` |
| `logo` | `szines`, `feher` (útvonal vagy `null`) |
| `hangnem` | 2-3 mondat a márka hangjáról (a `marka-dns.json`-ból) |
| `marka_dns` | `"marka-dns.json"` vagy `null` |
| `komponensek` | a választott webes elemek neve és leírása: `cim`, `alcim`, `gomb`, `kartya`, `foto`, `mozgas` (a prezi és a videó ehhez igazítja a saját változatait) |
| `allapot` | `web_verzio`, `forras` (`ajanlott` vagy `valasztott`), `jovahagyva`, `datum` |
| `alap` | a munkamappa abszolút útja |

## Szabályok az örökléshez

- A színeket és a betűket **pontosan** így kell használni: más betűt, más hexát a prezi és a videó nem vezet be.
  Árnyalatot képezhet (keverés a `paper`-rel vagy az `ink`-kel), új színt nem.
- Olvasható szöveg színes felületen: az `szinek_extra.on_*` értékei. Papíron a `primary_text` és az `accent_text`.
- Sötét mód (`mod = "sotet"`): a `paper` sötét, az `ink` világos. A logóból ilyenkor a `feher` változat kell.
- Új ikon kell? `ikon.elotag` + egy angol téma-mondat, ugyanazzal a generálóval (`scripts/ikon_generalo.py`).
