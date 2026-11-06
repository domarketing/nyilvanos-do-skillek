# 7 - Az opciók megírása: 5 karakter (alap-elemek) + az ügyfél témája (textúra, dekor, határ)

## A. Alap-elemek: 5 karakter, a tartalmuk az ügyfélből

Paletta, betűpár, ikonstílus, címsor, alcím, gomb, kártya, fotókezelés, mozgás: az 5 opció 5 KÜLÖNBÖZŐ KARAKTER
(elegáns · modern · merész · barátságos · klasszikus), de mind az ügyfélé. A karakterek tartalmát a márka-diagnózis
`karakterek` mezője adja (`references/8-marka-dns.md`): egy szó és egy mondat arról, mit jelent az adott karakter
ennél a vállalkozásnál, plusz egy szakmai részlet. Tisztességes, modern webdesign, nem kísérleti művészet.

> **Régi hiba, amit ne ismételj:** a korábbi recept-táblázat (elegáns = szögletes gomb belső éllel, modern = nyíl
> külön dobozban, merész = telt kapszula talppal, barátságos = puha fény, klasszikus = dupla keret; kártyáknál
> hajszálkeret, felső sáv, neo-brutál, puha színezett, füzetlap) minden ügyfélnél ugyanazt a 25 komponenst adta, csak
> más színben. Ezeket NE vedd elő kiindulásnak. A könyvtár (`epit.py lista`) a CSS technikájához jó minta, a
> formához nem.

Így írd meg kategóriánként az 5 opciót:
1. Vedd az 5 karakter ügyfélre írt nevét (pl. Lilinél: botanikus tábla · tervezőasztal · préri · kerti napló ·
   arborétum).
2. Minden karakterhez keress a szakmából **egy tárgyat vagy jelet**, ami az adott elemen megjelenhet:

| Elem | Mit kérdezz | Lili-példa (tájépítész) |
|---|---|---|
| Címsor-kiemelés | Hogyan jelöl ki valamit ez a szakma? | dőlt fajnév · méretvonal · szalmaszínű ecsetcsík · ceruzás bekarikázás · kiskapitális dupla vonallal |
| Alcím | Milyen címkét, számozást, feliratot használ? | Tab. 01 táblaszám · alaprajzi felirat-doboz · fűcsomó-jel · magtasak-címke · No. 01 arborétumi sorszám |
| Gomb | Milyen tárgyat nyom meg, tép le, szúr le? | levélvégű mutató · tervlap-sarokjelek · díszfű-szegély · perforált magtasak · névtábla két csavarral |
| Kártya | Milyen lapon, táblán, dobozban van az információ? | botanikus tábla Tab. I-gyel · pauszpapír illesztőkeresztekkel · préri-fejléc fűszegéllyel · naplólap washi-szalaggal · cím a névtáblán |
| Fotó | Hogyan keretezi a képeit, mivel jelöli? | ovális tábla-kép · léptékvonal · díszfű-él · préselt kasvirág · üvegház-boltív |

3. Írd meg a CSS-t `egyedi_opciok.<kategória>` alá (`%S` = a kategória data-attribútuma, `%K` = keyframe-előtag),
   és minden opcióhoz a `reszlet` mezőt (egy mondat: mi jön a szakmából). A `miert` mindig a márkáról szóljon.
4. Ellenőrizd: két opció ne legyen ugyanaz más színben (a `valtozatossag.py` a CSS vizuális jegyeit összeveti, és
   szól, ha két opció szinte egyforma).

A palettánál legyen egy hű (a mostani színek igényesebb változata) és egy sötét; a betűknél legyen egy, ami a
mostanihoz közel áll (ezt a generátorok magától intézik, lásd `2-arculati-mag.md`).

## B. Téma-elemek: textúra, dekor, határ az ügyfél FŐ TÉMÁJÁBÓL

Kérdés: *„Milyen képek, minták, tárgyak jutnak eszébe valakinek erről a szakmáról?”* Ezekből 5-5 ötlet. Nem kell
külön „koncepció”: a téma maga a forrás.

| Téma | Textúra (háttér) | Dekor (lebegő/óriás díszek) | Határ (szekciók között) |
|---|---|---|---|
| Pénzügy, befektetés | árfolyamgörbe, bankjegy-guilloche, gyertyadiagram, kamatos kamat-görbék, mikroírás | érmék, növekedési nyíl, mini-grafikonok, rozetta, garancia-pecsét | hozamgörbe-él, árfolyam-cikcakk, tőzsdei ticker, bankjegy-hullám, oszlopdiagram |
| Étterem, étel | kockás terítő, receptkártya-vonalak, liszt-szemcse | gőz, fűszerlevelek, tányérperem, matrica | napellenző-ív, tépett étlap, kenyérhéj-él |
| Fogászat, egészség | finom fogkontúr-minta, tiszta pöttyrács | csepp, fogkefe-fej, tükör-kör | hullámos „mosoly” ív, steril varrásvonal |
| Ács, építőipar | tervlap-rács, faerezet | szögfej, fecskefark-kötés, mérőszalag | fűrészfog, mérőszalag-vonalzó |
| Kert, táj | szintvonalak, kertterv-jelek, milliméterpapír | lepkék, méhek, óriás virág, évszak-jelek | fűszál-él, dombvonal, cserjeszegély |
| Oktatás, gyerek | füzetrács, krétatábla-szemcse | ceruza, betűkockák, matrica | vonalas füzetlap-él, cikcakk |

Technika:
- **Textúra**: `%S .tx::before{background-color:var(--c-primary);-webkit-mask:url(<svg>) …;mask:…;opacity:.07-.15}`.
  Az SVG-t Pythonból generáld (lásd `assets/pelda-lili/gen_arculat.py`).
  Sötét felületre `%S .s-deep.tx::before{background-color:var(--c-deep-hl)}`.
- **Dekor**: a `.dk` elemei (`dk-a dk-b dk-c dk-jel dk-r dk-f1 dk-f2 dk-szo dk-m`) alapból rejtettek; az opció
  megjeleníti és formázza őket (maszk-SVG, animáció `%K`-val). A `dk-m` a matrica szövegét kapja (motivum.matricak).
  Mobilra csak 340 px alatt rejts el, különben a választó keskeny demóiban sem látszik.
- **Határ**: a `.hat` a szekció tetején ül (alapból 0 magas); maszkkal formázd (`background:var(--sec-bg)`), vagy a
  `.hat .tick` futószalagot jelenítsd meg (motivum.ticker). **Váltakozó határ**: a motor minden `.hat`-ot sorszámoz
  (`data-hn` = 0/1/2 az oldal sorrendjében), így `%S .hat[data-hn="0"]{…} %S .hat[data-hn="1"]{…}` háromféle határt
  ad egymás után.
- **Keverés (pipálva)**: a választóban ebben a három kategóriában az ügyfél több opciót is kipipálhat („Ezt is kérem
  (váltakozva)”), és az élő oldal meg a kész főoldal szekcióról szekcióra váltogatja őket (a motor a szekciót burkoló
  elemre teszi a `data-felulet` / `data-dekor` / `data-hatar` attribútumot). Ezért minden téma-opció **szekciónként is
  működjön**: a CSS a `%S` alatt csak a szekción belüli elemekre hivatkozzon (`.tx`, `.dk`, `.hat`), a gyökérre
  (`%S.valami`) és szekciók közti testvér-szelektorra (`+`, `~`) ne. A választás ilyenkor lista:
  `valasztas.felulet.vegleges = ["tL1", "tL3"]`.
- Mind az 5 legyen jól látható a demóban, és ne nyomja el a szöveget.

## C. Szekciók: a beadott oldal szekciói, 5-5 elrendezés

A `szekcio_sorrend` a beadott oldal szekcióit sorolja (amit ott találsz, abban a sorrendben). Szekciónként 5
elrendezés: a motor típusaiból (`nav hero tenyek kinalat ajanlat folyamat tortenet galeria latogatas lablec`,
`epit.py lista`) válassz 5 illőt, vagy írj egyedit (`egyedi_opciok.<szekció>`: `html` + `css`, a CSS a `.v-<id>`
osztályra szűkítsen). Ha egy szekció egyik típushoz sem illik (pl. „Árak”, „GYIK”, „Csapat”), vedd fel:
`"egyedi_szekciok": {"gyik": {"nev": "GYIK", "leiras": "Gyakori kérdések"}}`, és írj hozzá 5 változatot.
