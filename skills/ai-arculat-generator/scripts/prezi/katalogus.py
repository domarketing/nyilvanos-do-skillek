# -*- coding: utf-8 -*-
"""A prezi-választó 10 kategóriája és kategóriánként 5 változata (egy helyen: a motor, a választó és a leírás is
innen olvas).

Az 5 változat az ügyfél 5 KARAKTERE (a márka-diagnózisból, mint a webes fázisban: elegáns, modern, merész, barátságos,
klasszikus, de az ügyfél saját nevével és tartalmával, pl. Lilinél botanikus tábla, tervezőasztal, préri, kerti napló,
arborétum). Kategóriánként minden karakterhez a hozzá illő forma tartozik (KARAKTER_FORMA); a tartalom (szín, betű,
sarok, motívum, fotó, ikon) a jóváhagyott webes arculatból jön, és a karakter saját részlete (marka-dns: karakterek.*.
reszlet) is megjelenik a diákon, ahol a formához illik (elemek.karakter_reszlet)."""

KATEGORIAK = [
    ("cimdia", "Címdia", "A nyitódia elrendezése: hol áll a cím, hol a fotó, mennyi a levegő."),
    ("fejezet", "Fejezetdia", "A fejezetek közti átvezető dia nagy számmal; ez adja a prezi lélegzetvételeit."),
    ("hatter", "Háttér és ritmus", "Az alapháttér, és hogy a ritmustörő diák (a fejezetek és a kérdések, nagyjából minden "
                                   "5. dia) milyen színt kapnak."),
    ("kiemeles", "Címsor-kiemelés", "Hogyan emeljük ki a címsor kulcsszavát."),
    ("fotokeret", "Fotókeret", "A diákon álló (nem teljes képernyős) fotók kerete."),
    ("ikontarto", "Ikontartó", "Mi kerül az ikonok mögé a felsorolásban, a folyamatban és a kártyákon."),
    ("felsorolas", "Felsorolásjel", "A listák jele."),
    ("szamok", "Számos dia", "Hogyan mutatjuk a számokat (árak, határidők, eredmények)."),
    ("idezet", "Idézet, vélemény", "Idézet vagy ügyfélvélemény fotóval."),
    ("zaro", "Záródia", "Az utolsó dia: köszönet, elérhetőség, a következő lépés."),
]

VALTOZATOK = {
    "cimdia": [
        ("A", "Rétegzett fotók", "Balra a cím, jobbra három egymásra csúsztatott fotó."),
        ("B", "Színes panel és fotó", "Balra mély színű panel a címmel, jobbra teljes magasságú fotó."),
        ("C", "Teljes kép, fátyollal", "A fotó kitölti a diát, a cím középen, sötét fátyolon."),
        ("D", "Döntött polaroidok", "Balra a cím, jobbra két kicsit megdöntött, fehér keretes fotó."),
        ("E", "Tipográfiai, motívummal", "Nagy cím, a márka jeleivel és a háttér-textúrával, kis kerek fotóval."),
    ],
    "fejezet": [
        ("A", "Teljes kép, nagy szám", "A fotó a háttér, rajta fátyol, nagy fejezetszám és cím."),
        ("B", "Fotó és színes panel", "Balra fotó, jobbra színes panel a számmal és a címmel."),
        ("C", "Szám, cím, filmszalag", "Nagy szám és cím, alatta három fotó sorban."),
        ("D", "Döntött polaroidok", "Balra a szám és a cím, jobbra döntött fotók kollázsa."),
        ("E", "Óriás szám, motívummal", "Fotó nélkül: óriás, halvány szám a háttérben, cím és a márka jele."),
    ],
    "hatter": [
        ("A", "Papír, a fejezetek mély színben", "Meleg papír alap; a fejezet- és kérdésdiák a mély színt kapják."),
        ("B", "Fehér, a fejezetek főszínben", "Tiszta fehér alap; a ritmustörő diák a főszínben."),
        ("C", "Árnyalt alap, kiemelő szín", "Halványan árnyalt alap; a ritmustörő diák a kiemelő színben."),
        ("D", "Sötét alap, világos fejezetek", "Sötét, esti hangulatú alap; a fejezetek papírszínűek."),
        ("E", "Papír, ritmustörő nélkül", "Végig papír alap; a fejezeteket csak a motívum és a nagy szám jelzi."),
    ],
    "kiemeles": [
        ("A", "Kiemelő doboz", "A kulcsszó mögött telt, halvány színű doboz."),
        ("B", "Filctoll-csík", "Filctoll-csík a kulcsszó alsó részén, mintha kézzel húztad volna alá."),
        ("C", "Vastag aláhúzás", "Határozott vonal a kulcsszó alatt."),
        ("D", "Ceruzás bekarikázás", "A kulcsszót egy kézzel húzott karika keríti be."),
        ("E", "Csak szín, dőlt", "A kulcsszó a kiemelő színben, minden más díszítés nélkül."),
    ],
    "fotokeret": [
        ("A", "Tiszta, az arculat sarkaival", "Keret nélküli fotó, a webes kártyák lekerekítésével és árnyékával."),
        ("B", "Kör, gyűrűvel", "Kerek kivágás vékony színes gyűrűvel; portréhoz a legjobb."),
        ("C", "Döntött polaroid", "Fehér keret, enyhe döntés és árnyék, a sarkán a márka jele."),
        ("D", "Eltolt színblokk", "A fotó mögött kicsit eltolt, telt színes blokk."),
        ("E", "Kétszínű (duotone)", "A fotó a márka két színére hangolva; nyugodt, egységes hatás."),
    ],
    "ikontarto": [
        ("A", "Csupaszon", "Az ikon önmagában, nagyobb méretben."),
        ("B", "Halvány kör", "Halvány, telt kör az ikon mögött."),
        ("C", "Kártya-csempe", "Fehér csempe vékony kerettel, a webes kártyák sarkával."),
        ("D", "Körvonal", "Vékony színes körvonal, belül üres."),
        ("E", "Számozott jelvény", "Halvány kör kis számjelvénnyel; lépésekhez."),
    ],
    "felsorolas": [
        ("A", "Pipa körben", "Kis telt kör pipával."),
        ("B", "Számozott kör", "Sorszám telt körben."),
        ("C", "Rövid sáv", "Rövid, vastag színes vonal a sor elején."),
        ("D", "A márka jele", "A márka motívuma (pl. levél) kicsiben, felsorolásjelként."),
        ("E", "Római szám", "Római szám a címbetűvel, mint egy botanikai atlasz tábláin."),
    ],
    "szamok": [
        ("A", "Három oszlop", "Három nagy szám egymás mellett, alattuk vonal és magyarázat."),
        ("B", "Egy nagy, két kicsi", "Egy kiemelt nagy szám, mellette két kisebb."),
        ("C", "Sorok elválasztóval", "Számok soronként, finom elválasztó vonalakkal."),
        ("D", "Kártyák", "Minden szám saját kártyán."),
        ("E", "Számok fotóval", "Balra a számok, jobbra teljes magasságú fotó."),
    ],
    "idezet": [
        ("A", "Fotó és idézet osztva", "Balra fotó, jobbra az idézet nagy idézőjellel."),
        ("B", "Kerek portré, nagy idézet", "Fent kis kerek portré a névvel, alatta nagy idézet."),
        ("C", "Kártya és polaroid", "Az idézet kártyán, mellette döntött fotó."),
        ("D", "Fátyolos fotó, fehér panel", "Balra színes fátyolos fotó, jobbra fehér panel az idézettel."),
        ("E", "Magas fotó, eltolt blokk", "Balra az idézet, jobbra magas fotó, mögötte eltolt színes blokk."),
    ],
    "zaro": [
        ("A", "Színes, középre zárt", "Színes háttér, középen a cím és az elérhetőség."),
        ("B", "Elérhetőség és portré", "Balra a teendő és az elérhetőség, jobbra kerek portré a névvel."),
        ("C", "Teljes kép, fátyollal", "A fotó a háttér, rajta a cím és a webcím."),
        ("D", "Fotó és kapcsolatkártya", "Balra fotó, jobbra kártya az elérhetőséggel."),
        ("E", "Tipográfiai, motívummal", "Nagy köszönő cím a márka jeleivel, alatta az elérhetőség egy sorban."),
    ],
}


# a téma felülírásai (tema.bekapcsol állítja): {kat: {karakter: forma}} és {kat: {forma: [név, leírás]}}
FELULIRAS = {}
NEV_FELULIRAS = {}


def valtozatok(kat):
    """[(forma, név, leírás)] a téma névfelülírásaival (pl. Lilinél a C kiemelés „Méretvonal”)."""
    nf = NEV_FELULIRAS.get(kat) or {}
    return [(i, (nf.get(i) or [n, l])[0], (nf.get(i) or [n, l])[1]) for i, n, l in VALTOZATOK[kat]]


def nev(kat, vid):
    for i, n, _ in valtozatok(kat):
        if i == vid:
            return n
    return vid


def kat_nev(kat):
    for k, n, _ in KATEGORIAK:
        if k == kat:
            return n
    return kat


KARAKTEREK = ["elegans", "modern", "meresz", "baratsagos", "klasszikus"]
KARAKTER_ALAPNEV = {"elegans": "elegáns", "modern": "modern", "meresz": "merész", "baratsagos": "barátságos",
                    "klasszikus": "klasszikus"}

# kategóriánként: karakter -> forma (A-E), mindegyik forma pontosan egyszer
KARAKTER_FORMA = {
    "cimdia": {"elegans": "E", "modern": "B", "meresz": "C", "baratsagos": "D", "klasszikus": "A"},
    "fejezet": {"elegans": "E", "modern": "C", "meresz": "A", "baratsagos": "D", "klasszikus": "B"},
    "hatter": {"elegans": "E", "modern": "B", "meresz": "D", "baratsagos": "A", "klasszikus": "C"},
    "kiemeles": {"elegans": "E", "modern": "B", "meresz": "A", "baratsagos": "D", "klasszikus": "C"},
    "fotokeret": {"elegans": "E", "modern": "A", "meresz": "D", "baratsagos": "C", "klasszikus": "B"},
    "ikontarto": {"elegans": "A", "modern": "D", "meresz": "B", "baratsagos": "E", "klasszikus": "C"},
    "felsorolas": {"elegans": "E", "modern": "B", "meresz": "C", "baratsagos": "D", "klasszikus": "A"},
    "szamok": {"elegans": "C", "modern": "D", "meresz": "B", "baratsagos": "E", "klasszikus": "A"},
    "idezet": {"elegans": "B", "modern": "E", "meresz": "D", "baratsagos": "C", "klasszikus": "A"},
    "zaro": {"elegans": "E", "modern": "D", "meresz": "C", "baratsagos": "B", "klasszikus": "A"},
}

# ezeken a diatípusokon a választott változat karaktere a dia egészét adja (a részletével együtt)
DIA_KATEGORIA = {"cimdia": "cimdia", "fejezet": "fejezet", "szamok": "szamok", "idezet": "idezet", "zaro": "zaro"}


def _terkep(kat):
    return FELULIRAS.get(kat) or KARAKTER_FORMA.get(kat) or {}


def forma_karakter(kat, forma):
    for k, f in _terkep(kat).items():
        if f == forma:
            return k
    return None


def karakter_sorrend(kat):
    """[(forma, karakter)] a karakterek sorrendjében (elegáns, modern, merész, barátságos, klasszikus)."""
    return [(_terkep(kat)[k], k) for k in KARAKTEREK]
