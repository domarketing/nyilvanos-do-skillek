# A videó-választó kategóriái

Hat fő kategória 5-5 változatban, öt kisebb elem 3-3 változatban. A nevek és a leírások a `scripts/video/katalogus.py`-ban
vannak (ügyfelenként a `tartalom.json` `valtozatok` kulcsa felülírja őket), az élő előnézetet az
`assets/video/elonezet.js` rajzolja azonosító szerint. A pontos értékek a vágómotornak: `leiras.specifikacio()`.

| # | kategória (`kat`) | változatok (`id`) | mire figyelj |
|---|---|---|---|
| 1 | Vágási stílus (`stilus`) | `klasszikus` lebegő kártya · `panel` felső panel · `tiszta` kártya nélkül · `kivagasos` grafika a fej mögött · `csakfej` hosszú videóból short | a kivágásos és a csak-fej kivágott fejet kér (`elokeszit`) |
| 2 | Felirat (`felirat`) | `szavankent` · `karaoke` 1-3 szó · `slam` nagybetűs ütés · `doboz` pill a szó alatt · `mondatsav` teljes mondat sávban | a DO!-alap a szavankénti; a kivágásos és a csak-fej mindig 1-3 szavas a mellkason |
| 3 | Címsor, hook (`hook`) | `sotetitett` · `blokkok` kiemelőfilc · `uveg` üvegkártya a márkajellel · `fejmogott` nagy szó a fej mögött · `derenges` sötét szöveg fehér derengéssel | zsúfolt háttéren a derengés gyenge: ott a sötétített vagy a blokkok |
| 4 | Kártyaforma (`kartya`) | `lebego` fehér · `texturas` papír + a márka textúrája · `uveg` · `telt` fő szín · `keretes` kettős hajszálkeret + kis címke | a textúra a webes textúrából jön (szintvonal, levél/herbárium a márka levélformájával, pötty, rács, csík, hullám, papír, vagy a márkajel mintaként); keverésnél az első a minta |
| 5 | Mozgás és tempó (`mozgas`) | `nyugodt` · `maszkos` · `rugos` · `kinetikus` · `szerkesztosegi` | a tempó a hangeffekt-sűrűséget és a ráközelítést (punch) is jelenti |
| 6 | Hangulat (`hangulat`) | `akusztikus` 72 · `meleg` 88 · `modern` 100 · `lendulet` 118 · `filmes` 84 BPM | a hangminták a böngészőben szintetizálódnak (WebAudio), egyforma hangerőre normálva: nincs licencgond |
| 7 | Témaválasztó kártya (`tema`) | `lista` · `pillsor` · `lepcso` | **új elem**: a videó témái, az aktuális kiemelve, a kész pipát kap |
| 8 | Névkártya (`nev`) | `kartya` · `tabla` · `vonal` | bal alsó harmad, 1300 px-től (a Reels alsó sávja fölött) |
| 9 | Fejezetkártya (`fejezet`) | `takeover` (≤1,2 mp) · `pill` · `szam` | a teljes képes legfeljebb kétszer egy videóban |
| 10 | CTA és záró (`zaro`) | `social` lájk + követés · `cta` ajánlatkártya · `logo` logós zárókép | közösségi videón nincs ajánlat; hirdetésnél a CTA |
| 11 | Nyitókép (`nyito`) | `blokk` · `nagyszo` · `keretes` | ez a borítókép is (az első 0,5 mp) |

## Új változat vagy finomítás („kérek újakat”)
- **Szöveg, név, indoklás:** a `tartalom.json` `valtozatok.<kat>.<id>` (`nev`, `leiras`, `miert`).
- **Szín, betű, forma:** a tokenekből jön; ha a videón más kell (pl. erősebb kiemelés), a `vegleges` után a
  `video-tema.json` `szinek.szerepek` értékét és a `video-tokens.css` változóját írd át, új színt ne vezess be.
- **Új elemtípus:** az `elonezet.js` `SC.<kat>` függvényében egy új ág (azonosító), a `katalogus.py`-ban a változat, a
  `leiras.specifikacio()`-ban a pontos értékek. A kártyák mindig a `.k` alaposztályra épülnek.
