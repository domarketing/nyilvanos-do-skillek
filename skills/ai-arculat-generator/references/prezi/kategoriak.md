# A prezi-választó 10 kategóriája

Egy forrás: `scripts/prezi/katalogus.py` (a motor, a választó és a PREZI-ARCULAT.md is innen olvas).

## Az 5 változat = az ügyfél 5 karaktere

Mint a webes fázisban: elegáns, modern, merész, barátságos, klasszikus, de mindig az ügyfél saját nevével és tartalmával a `marka-dns.json` → `karakterek` mezőből (Lilinél: botanikus tábla, tervezőasztal, préri, kerti napló, arborétum). A választó minden kategóriában ebben a sorrendben mutatja őket, a karakter nevével. Kategóriánként minden karakterhez a hozzá illő forma tartozik (`KARAKTER_FORMA`):

| Kategória | elegáns | modern | merész | barátságos | klasszikus |
|---|---|---|---|---|---|
| Címdia | E · Tipográfiai, motívummal | B · Színes panel és fotó | C · Teljes kép, fátyollal | D · Döntött polaroidok | A · Rétegzett fotók |
| Fejezetdia | E · Óriás szám, motívummal | C · Szám, cím, filmszalag | A · Teljes kép, nagy szám | D · Döntött polaroidok | B · Fotó és színes panel |
| Háttér és ritmus | E · Papír, ritmustörő nélkül | B · Fehér, a fejezetek főszínben | D · Sötét alap, világos fejezetek | A · Papír, a fejezetek mély színben | C · Árnyalt alap, kiemelő szín |
| Címsor-kiemelés | E · Csak szín, dőlt | B · Filctoll-csík | A · Kiemelő doboz | D · Ceruzás bekarikázás | C · Vastag aláhúzás |
| Fotókeret | E · Kétszínű (duotone) | A · Tiszta, az arculat sarkaival | D · Eltolt színblokk | C · Döntött polaroid | B · Kör, gyűrűvel |
| Ikontartó | A · Csupaszon | D · Körvonal | B · Halvány kör | E · Számozott jelvény | C · Kártya-csempe |
| Felsorolásjel | E · Római szám | B · Számozott kör | C · Rövid sáv | D · A márka jele | A · Pipa körben |
| Számos dia | C · Sorok elválasztóval | D · Kártyák | B · Egy nagy, két kicsi | E · Számok fotóval | A · Három oszlop |
| Idézet, vélemény | B · Kerek portré, nagy idézet | E · Magas fotó, eltolt blokk | D · Fátyolos fotó, fehér panel | C · Kártya és polaroid | A · Fotó és idézet osztva |
| Záródia | E · Tipográfiai, motívummal | D · Fotó és kapcsolatkártya | C · Teljes kép, fátyollal | B · Elérhetőség és portré | A · Színes, középre zárt |

**A karakter saját részlete** (`karakterek.<k>.reszlet`) a címdián, a fejezetdián, a számos dián, az idézeten és a záródián jelenik meg (ott a választott változat karaktere adja az egész diát), kulcsszó szerint: „tábla” → növénycímke-tábla keret a kicker körül; „latin/címk” → hajszálvonal a kicker után; „ceruza/skicc” → ceruzás aláhúzás a kicker alatt; „csík/sáv” → színcsík (pl. évszak-csík) a dia tetején; „kör/lombkorona” → alaprajzi kör a textúra közepén. Ha a részlet egyikre sem illik, a karakter a formájával és a színeivel különül el.

**Ajánlott változat:** a `tema.py` `ajanlas()` vezeti le a webes döntésekből (pl. a webes fotókezelés polaroid → a címdia és a fotókeret a polaroidos, barátságos karakter; a webes címsor-kiemelés ceruzás karika → kiemelés D; a webes kártya tábla-stílus → ikontartó C, felsorolásjel E). Ha a márkához más illik jobban, írd át a `prezi-tema.json` `ajanlott` és `ajanlas_miert` mezőjét (a miért a márkáról szóljon), és építsd újra a választót.

## Címdia (`cimdia`)

A nyitódia elrendezése: hol áll a cím, hol a fotó, mennyi a levegő. Előnézet: címdia. Kód: `diak.cimdia`.

- **A · Rétegzett fotók** (klasszikus): Balra a cím, jobbra három egymásra csúsztatott fotó.
- **B · Színes panel és fotó** (modern): Balra mély színű panel a címmel, jobbra teljes magasságú fotó.
- **C · Teljes kép, fátyollal** (merész): A fotó kitölti a diát, a cím középen, sötét fátyolon.
- **D · Döntött polaroidok** (barátságos): Balra a cím, jobbra két kicsit megdöntött, fehér keretes fotó.
- **E · Tipográfiai, motívummal** (elegáns): Nagy cím, a márka jeleivel és a háttér-textúrával, kis kerek fotóval.

## Fejezetdia (`fejezet`)

A fejezetek közti átvezető dia nagy számmal; ez adja a prezi lélegzetvételeit. Előnézet: fejezetdia. Kód: `diak.fejezet`.

- **A · Teljes kép, nagy szám** (merész): A fotó a háttér, rajta fátyol, nagy fejezetszám és cím.
- **B · Fotó és színes panel** (klasszikus): Balra fotó, jobbra színes panel a számmal és a címmel.
- **C · Szám, cím, filmszalag** (modern): Nagy szám és cím, alatta három fotó sorban.
- **D · Döntött polaroidok** (barátságos): Balra a szám és a cím, jobbra döntött fotók kollázsa.
- **E · Óriás szám, motívummal** (elegáns): Fotó nélkül: óriás, halvány szám a háttérben, cím és a márka jele.

## Háttér és ritmus (`hatter`)

Az alapháttér, és hogy a ritmustörő diák (a fejezetek és a kérdések, nagyjából minden 5. dia) milyen színt kapnak. Előnézet: 6 dia kicsiben (felsorolás, fejezet, kártyák, számok, kérdés, folyamat). Kód: `elemek.HATTER, felulet_alap/ritmus`.

- **A · Papír, a fejezetek mély színben** (barátságos): Meleg papír alap; a fejezet- és kérdésdiák a mély színt kapják.
- **B · Fehér, a fejezetek főszínben** (modern): Tiszta fehér alap; a ritmustörő diák a főszínben.
- **C · Árnyalt alap, kiemelő szín** (klasszikus): Halványan árnyalt alap; a ritmustörő diák a kiemelő színben.
- **D · Sötét alap, világos fejezetek** (merész): Sötét, esti hangulatú alap; a fejezetek papírszínűek.
- **E · Papír, ritmustörő nélkül** (elegáns): Végig papír alap; a fejezeteket csak a motívum és a nagy szám jelzi.

## Címsor-kiemelés (`kiemeles`)

Hogyan emeljük ki a címsor kulcsszavát. Előnézet: felsorolás ikonnal. Kód: `elemek.cimsor`.

- **A · Kiemelő doboz** (merész): A kulcsszó mögött telt, halvány színű doboz.
- **B · Filctoll-csík** (modern): Filctoll-csík a kulcsszó alsó részén, mintha kézzel húztad volna alá.
- **C · Vastag aláhúzás** (klasszikus): Határozott vonal a kulcsszó alatt.
- **D · Ceruzás bekarikázás** (barátságos): A kulcsszót egy kézzel húzott karika keríti be.
- **E · Csak szín, dőlt** (elegáns): A kulcsszó a kiemelő színben, minden más díszítés nélkül.

## Fotókeret (`fotokeret`)

A diákon álló (nem teljes képernyős) fotók kerete. Előnézet: bemutatkozó dia. Kód: `elemek.fotokeret`.

- **A · Tiszta, az arculat sarkaival** (modern): Keret nélküli fotó, a webes kártyák lekerekítésével és árnyékával.
- **B · Kör, gyűrűvel** (klasszikus): Kerek kivágás vékony színes gyűrűvel; portréhoz a legjobb.
- **C · Döntött polaroid** (barátságos): Fehér keret, enyhe döntés és árnyék, a sarkán a márka jele.
- **D · Eltolt színblokk** (merész): A fotó mögött kicsit eltolt, telt színes blokk.
- **E · Kétszínű (duotone)** (elegáns): A fotó a márka két színére hangolva; nyugodt, egységes hatás.

## Ikontartó (`ikontarto`)

Mi kerül az ikonok mögé a felsorolásban, a folyamatban és a kártyákon. Előnézet: folyamat 4 ikonnal. Kód: `elemek.ikontarto`.

- **A · Csupaszon** (elegáns): Az ikon önmagában, nagyobb méretben.
- **B · Halvány kör** (merész): Halvány, telt kör az ikon mögött.
- **C · Kártya-csempe** (klasszikus): Fehér csempe vékony kerettel, a webes kártyák sarkával.
- **D · Körvonal** (modern): Vékony színes körvonal, belül üres.
- **E · Számozott jelvény** (barátságos): Halvány kör kis számjelvénnyel; lépésekhez.

## Felsorolásjel (`felsorolas`)

A listák jele. Előnézet: kéthasábos dia. Kód: `elemek.jel`.

- **A · Pipa körben** (klasszikus): Kis telt kör pipával.
- **B · Számozott kör** (modern): Sorszám telt körben.
- **C · Rövid sáv** (merész): Rövid, vastag színes vonal a sor elején.
- **D · A márka jele** (barátságos): A márka motívuma (pl. levél) kicsiben, felsorolásjelként.
- **E · Római szám** (elegáns): Római szám a címbetűvel, mint egy botanikai atlasz tábláin.

## Számos dia (`szamok`)

Hogyan mutatjuk a számokat (árak, határidők, eredmények). Előnézet: számos dia. Kód: `diak.szamok`.

- **A · Három oszlop** (klasszikus): Három nagy szám egymás mellett, alattuk vonal és magyarázat.
- **B · Egy nagy, két kicsi** (merész): Egy kiemelt nagy szám, mellette két kisebb.
- **C · Sorok elválasztóval** (elegáns): Számok soronként, finom elválasztó vonalakkal.
- **D · Kártyák** (modern): Minden szám saját kártyán.
- **E · Számok fotóval** (barátságos): Balra a számok, jobbra teljes magasságú fotó.

## Idézet, vélemény (`idezet`)

Idézet vagy ügyfélvélemény fotóval. Előnézet: idézet fotóval. Kód: `diak.idezet`.

- **A · Fotó és idézet osztva** (klasszikus): Balra fotó, jobbra az idézet nagy idézőjellel.
- **B · Kerek portré, nagy idézet** (elegáns): Fent kis kerek portré a névvel, alatta nagy idézet.
- **C · Kártya és polaroid** (barátságos): Az idézet kártyán, mellette döntött fotó.
- **D · Fátyolos fotó, fehér panel** (merész): Balra színes fátyolos fotó, jobbra fehér panel az idézettel.
- **E · Magas fotó, eltolt blokk** (modern): Balra az idézet, jobbra magas fotó, mögötte eltolt színes blokk.

## Záródia (`zaro`)

Az utolsó dia: köszönet, elérhetőség, a következő lépés. Előnézet: záródia. Kód: `diak.zaro`.

- **A · Színes, középre zárt** (klasszikus): Színes háttér, középen a cím és az elérhetőség.
- **B · Elérhetőség és portré** (barátságos): Balra a teendő és az elérhetőség, jobbra kerek portré a névvel.
- **C · Teljes kép, fátyollal** (merész): A fotó a háttér, rajta a cím és a webcím.
- **D · Fotó és kapcsolatkártya** (modern): Balra fotó, jobbra kártya az elérhetőséggel.
- **E · Tipográfiai, motívummal** (elegáns): Nagy köszönő cím a márka jeleivel, alatta az elérhetőség egy sorban.

## Új változat vagy „kérek újakat”

- Előbb a tartalmon javíts (más fotó, rövidebb cím, más ikon): a legtöbb kritika ezzel megoldható.
- Új forma: a kategória függvényében (lásd fent) adj hozzá egy ágat, vedd fel a `katalogus.py`-ba, és rendeld egy karakterhez a `KARAKTER_FORMA`-ban. A változatok száma maradjon 5 (karakterenként egy).
- Minden változat a felületekből (`elemek.Fel`) veszi a színeket, így sötét és világos háttéren is olvasható marad; a logó helyét (jobbra lent, x > 11,2", y > 6,7") szabadon kell hagyni.

## A motívum (textúra, dekor, határ)

A tokenekben objektum (egy választás) vagy lista (keverés) is lehet; a motor mindkettőt kezeli (`alap.motivum_elemek`). Keverésnél a textúrák diánként váltakoznak.
