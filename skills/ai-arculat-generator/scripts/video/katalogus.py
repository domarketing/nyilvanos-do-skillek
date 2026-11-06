# -*- coding: utf-8 -*-
"""A videó-választó kategóriái és változatai. Az élő előnézetet az assets/video/elonezet.js rajzolja (azonosító szerint),
a nevet, a leírást és az ajánlottat innen kapja. Ügyfelenként a video/tartalom.json "valtozatok" kulcsa felülírhatja
a neveket és a leírásokat (pl. a márka szavaival), az "ajanlott" kulcsa az ajánlottat."""

KATEGORIAK = [
    {"kat": "stilus", "nev": "Vágási stílus", "csoport": "fo",
     "leiras": "Hol van a grafika a beszélőhöz képest. Ez határozza meg a videóid összképét.",
     "valtozatok": [
         {"id": "klasszikus", "kar": "klasszikus", "nev": "Klasszikus", "leiras": "A felvétel végig teljes képen, a grafika egy lebegő kártyán a felirat alatt. Tiszta, gyors, a legsokoldalúbb."},
         {"id": "panel", "kar": "modern", "nev": "Felső panellel", "leiras": "Világos panel felülről a grafikával és a felirattal, alatta a teljes fej. Sok szöveges információhoz, hirdetéshez."},
         {"id": "tiszta", "kar": "elegans", "nev": "Tiszta", "leiras": "Kártya és keret nélkül: csak felirat, egy-egy nagy szám vagy fehér ikon a felvételen. Személyes, nyugodt."},
         {"id": "kivagasos", "kar": "meresz", "nev": "Kivágásos", "leiras": "A beszélő ki van vágva, a díszgrafika a feje mögött, az információ a feje mellett és fölött. Látványos, „prémium edit”."},
         {"id": "csakfej", "kar": "baratsagos", "nev": "Csak-fej", "leiras": "Hosszú felvételből (webinár, podcast) vágott shorthoz: csak a fej van kivágva, a felirat az áll alatt, az info a fej fölött."},
     ]},
    {"kat": "felirat", "nev": "Felirat", "csoport": "fo",
     "leiras": "Hogyan jelenik meg a kimondott szöveg. A felirat a néző szemének fix pontja.",
     "valtozatok": [
         {"id": "szavankent", "kar": "modern", "nev": "Szavanként", "leiras": "Mindig pontosan egy szó a képen, a kimondás pillanatában. A kulcsszó kiemelőszínű."},
         {"id": "karaoke", "kar": "baratsagos", "nev": "Karaoke 1-3 szó", "leiras": "Rövid szócsoport, az éppen elhangzó szó kiemelőszínnel. Nyugodtabban olvasható."},
         {"id": "slam", "kar": "meresz", "nev": "Nagybetűs ütés", "leiras": "Nagybetűs, nagy szavak, mindegyik ütéssel érkezik. Energikus, hirdetéshez is."},
         {"id": "doboz", "kar": "klasszikus", "nev": "Dobozos", "leiras": "A szó a márkaszínű dobozon (pill), fehér betűvel. Bármilyen háttéren olvasható."},
         {"id": "mondatsav", "kar": "elegans", "nev": "Mondatsáv", "leiras": "A teljes mondat egy alsó sávban, az éppen elhangzó szó kiemelve. Visszafogott, sok szöveghez."},
     ]},
    {"kat": "hook", "nev": "Címsor (hook)", "csoport": "fo",
     "leiras": "Az első 1-3 másodperc nagy mondata, ami megállítja a görgetést.",
     "valtozatok": [
         {"id": "sotetitett", "kar": "klasszikus", "nev": "Sötétített kép, nagy szöveg", "leiras": "A kép teteje lágyan elsötétül, rajta kicker és két sor nagy cím a címbetűddel."},
         {"id": "blokkok", "kar": "meresz", "nev": "Kiemelő blokkok", "leiras": "Megdöntött, kiemelőfilc-szerű blokkok a márkaszíneiddel. Hangos, gyorsan olvasható."},
         {"id": "uveg", "kar": "modern", "nev": "Üvegkártya", "leiras": "Elmosott hátterű, áttetsző kártya a márkajeleddel és a címmel, felül a fej fölött."},
         {"id": "fejmogott", "kar": "elegans", "nev": "Nagy szó a fej mögött", "leiras": "Egy óriási kulcsszó a feje mögött, a haj rálóg a betűk aljára. Kivágás kell hozzá."},
         {"id": "derenges", "kar": "baratsagos", "nev": "Sötét szöveg derengéssel", "leiras": "Sötétítés nélkül: sötét betűk fehér derengéssel a valódi háttéren, a kiemelés a fő színnel."},
     ]},
    {"kat": "kartya", "nev": "Kártyaforma", "csoport": "fo",
     "leiras": "Milyen felületen jelenik meg az információ (szám, lista, idézet).",
     "valtozatok": [
         {"id": "lebego", "kar": "klasszikus", "nev": "Lebegő fehér", "leiras": "Fehér kártya lágy árnyékkal, a lekerekítésed szerint. A legtisztább."},
         {"id": "texturas", "kar": "baratsagos", "nev": "Textúrás panel", "leiras": "Papírszínű panel a márkád textúrájával és vékony kerettel. Melegebb, kézzelfoghatóbb."},
         {"id": "uveg", "kar": "modern", "nev": "Üveg", "leiras": "Áttetsző, elmosott hátterű kártya fehér szöveggel. Modern, könnyed."},
         {"id": "telt", "kar": "meresz", "nev": "Telt márkaszín", "leiras": "A fő színed teljes felületen, fehér betűvel. Erős márkajel."},
         {"id": "keretes", "kar": "elegans", "nev": "Keretes tábla", "leiras": "Papír alapon kettős hajszálkeret és kis címke, mint egy tábla vagy tervlap."},
     ]},
    {"kat": "mozgas", "nev": "Mozgás és tempó", "csoport": "fo",
     "leiras": "Hogyan érkeznek és távoznak az elemek, és milyen sűrűn szól hangeffekt.",
     "valtozatok": [
         {"id": "nyugodt", "kar": "elegans", "nev": "Nyugodt", "leiras": "Lágy beúszás enyhe elmosásból, nincs ráközelítés. Kb. 1 hangeffekt 5 másodpercenként."},
         {"id": "maszkos", "kar": "klasszikus", "nev": "Maszkos felfedés", "leiras": "Az elemek egy függönyként húzódó maszk mögül tűnnek elő. Elegáns, kb. 1 effekt 3 mp-enként."},
         {"id": "rugos", "kar": "baratsagos", "nev": "Rugós pop", "leiras": "Kis túllendüléssel pattannak be. Barátságos, élénk, kb. 1 effekt 2,8 mp-enként."},
         {"id": "kinetikus", "kar": "meresz", "nev": "Kinetikus", "leiras": "Ütésszerű érkezés, villanás, 1,05-ös ráközelítés a kulcsszavakon. Gyors, kb. 1 effekt 1,2 mp-enként."},
         {"id": "szerkesztosegi", "kar": "modern", "nev": "Szerkesztőségi", "leiras": "Visszafogott beúszás, a kulcsszó alá kiemelés rajzolódik, szóról szóra halad."},
     ]},
    {"kat": "hangulat", "nev": "Hangulat (zene és effektek)", "csoport": "fo",
     "leiras": "A zenei alap és a hangeffektek karaktere. A hangminták itt helyben szólnak (a böngésző szintetizálja őket), egyforma hangerőn.",
     "valtozatok": [
         {"id": "akusztikus", "kar": "baratsagos", "nev": "Nyugodt, akusztikus", "leiras": "Lassú, 72 BPM, pengetős húrok; levegős suhogás és halk csengő. Személyes, nyugodt."},
         {"id": "meleg", "kar": "klasszikus", "nev": "Meleg, kézműves", "leiras": "88 BPM, marimba és fa koppanás, papírzörej a kártyákra. Barátságos, természetes."},
         {"id": "modern", "kar": "modern", "nev": "Tiszta, modern", "leiras": "100 BPM, puha szintipad, tiszta kattanás és pop. Szakmai, letisztult."},
         {"id": "lendulet", "kar": "meresz", "nev": "Lendületes", "leiras": "118 BPM, dob és basszus, whoosh és ütés. Energikus, hirdetéshez is."},
         {"id": "filmes", "kar": "elegans", "nev": "Prémium, filmes", "leiras": "84 BPM, mély pad, emelkedő (riser) és mély ütés. Komoly, nagyvonalú."},
     ]},
    {"kat": "tema", "nev": "Témaválasztó kártya", "csoport": "kis",
     "leiras": "Új elem: egy lista a videó témáival, az éppen tárgyalt téma kiemelve, a többi halványítva.",
     "valtozatok": [
         {"id": "lista", "nev": "Lista", "leiras": "Függőleges lista a fej fölött; a kész téma pipát kap, az aktuális kiemelt sávot."},
         {"id": "pillsor", "nev": "Pillsor", "leiras": "Vízszintes pillek egy sorban, az aktuális téma telt márkaszínű."},
         {"id": "lepcso", "nev": "Lépcső", "leiras": "Számozott pontok vonallal összekötve, alatta nagyban az aktuális téma."},
     ]},
    {"kat": "nev", "nev": "Névkártya", "csoport": "kis",
     "leiras": "Ki beszél: név és szerep az alsó harmadban, a Reels-sáv fölött.",
     "valtozatok": [
         {"id": "kartya", "nev": "Kártya színes sávval", "leiras": "Fehér kártya, a szélén a fő színed sávja; név és szerep."},
         {"id": "tabla", "nev": "Márkaszínű tábla", "leiras": "Telt fő szín, fehér név, alatta akcentszínű vonal."},
         {"id": "vonal", "nev": "Vonalas", "leiras": "Kártya nélkül: fehér név a felvételen, alatta kirajzolódó vonal és a szerep."},
     ]},
    {"kat": "fejezet", "nev": "Fejezetkártya", "csoport": "kis",
     "leiras": "Új rész kezdete hosszabb videóban vagy listás shortban.",
     "valtozatok": [
         {"id": "takeover", "nev": "Teljes képes", "leiras": "Egy pillanatra a teljes kép a papírszínen a textúráddal, nagy számmal és címmel (legfeljebb 1,2 mp)."},
         {"id": "pill", "nev": "Fejezet-pill", "leiras": "Felül egy pill a számmal és a címmel, a felvétel végig látszik."},
         {"id": "szam", "nev": "Nagy szám oldalt", "leiras": "Óriási körvonalas szám a kép szélén, mellette a cím az alsó harmadban."},
     ]},
    {"kat": "zaro", "nev": "CTA és záró", "csoport": "kis",
     "leiras": "A videó utolsó 2-3 másodperce. Közösségi videón lájk és követés, hirdetésnél ajánlat.",
     "valtozatok": [
         {"id": "social", "nev": "Lájk és követés", "leiras": "„Ha hasznos volt” címke és két pill a fej fölött, a kép lassan közelít."},
         {"id": "cta", "nev": "Ajánlatkártya", "leiras": "Hirdetéshez: az ajánlat, egy pulzáló gomb és a link."},
         {"id": "logo", "nev": "Logós zárókép", "leiras": "A logód és a szlogened a kép alján, a felvétel elsötétül."},
     ]},
    {"kat": "nyito", "nev": "Nyitókép", "csoport": "kis",
     "leiras": "A videó első fél másodperce, egyben a borítókép a hírfolyamban.",
     "valtozatok": [
         {"id": "blokk", "nev": "Kiemelő blokkok", "leiras": "A fotón felül két kiemelőfilc-blokk a címmel."},
         {"id": "nagyszo", "nev": "Nagy szó sávban", "leiras": "Egy nagy szó márkaszínű sávban a kép alsó harmadában."},
         {"id": "keretes", "nev": "Keretes fotó", "leiras": "A fotó fehér keretben, megdöntve, papíralapon, mellette a cím a címbetűddel."},
     ]},
]

KAT = {k["kat"]: k for k in KATEGORIAK}
KARSOR = ["elegans", "modern", "meresz", "baratsagos", "klasszikus"]
KARSZO = {"elegans": "elegáns", "modern": "modern", "meresz": "merész", "baratsagos": "barátságos", "klasszikus": "klasszikus"}


def ajanlott(tok, tartalom=None):
    """Ajánlott változat kategóriánként: a webes döntésekből és a márka jelleméből, felülírható a tartalom.json-ból."""
    K = tok.get("komponensek") or {}

    def szo(k):
        x = K.get(k) or {}
        return ((x.get("nev") or "") + " " + (x.get("leiras") or "")).lower()
    kartya = "lebego"
    s = szo("kartya")
    if any(w in s for w in ("tábla", "keret", "hajszál", "vonal")):
        kartya = "keretes"
    elif any(w in s for w in ("üveg", "áttetsz")):
        kartya = "uveg"
    elif any(w in s for w in ("papír", "textúr", "kraft")):
        kartya = "texturas"
    elif any(w in s for w in ("telt", "színes", "blokk")):
        kartya = "telt"
    m = szo("mozgas")
    mozgas = "rugos"
    if any(w in m for w in ("lágy", "bimbó", "nyugodt", "úsz", "elmos", "finom")):
        mozgas = "nyugodt"
    elif any(w in m for w in ("maszk", "függöny", "feltár", "kirajzol", "rajzol")):
        mozgas = "maszkos"
    elif any(w in m for w in ("üt", "kinetik", "villan", "gyors")):
        mozgas = "kinetikus"
    elif any(w in m for w in ("szerkeszt", "szóról", "aláhúz")):
        mozgas = "szerkesztosegi"
    hangulat = {"nyugodt": "akusztikus", "maszkos": "filmes", "rugos": "meleg", "kinetikus": "lendulet",
                "szerkesztosegi": "modern"}[mozgas]
    A = {"stilus": "klasszikus", "felirat": "szavankent", "hook": "sotetitett", "kartya": kartya, "mozgas": mozgas,
         "hangulat": hangulat, "tema": "lista", "nev": "kartya", "fejezet": "pill", "zaro": "social", "nyito": "blokk"}
    A.update(((tartalom or {}).get("ajanlott") or {}))
    return A


def kategoriak(tok, tartalom=None, dns=None):
    """A választóba kerülő kategóriák: nevek, leírások, ajánlott; az ügyfélre írt felülírásokkal. Ha van márka-diagnózis,
    az 5-ös kategóriák változatai az ügyfél 5 karakterének sorrendjében jönnek, a karakter nevével (mint a web és a prezi)."""
    import copy
    T = (tartalom or {}).get("valtozatok") or {}
    A = ajanlott(tok, tartalom)
    KR = (dns or {}).get("karakterek") or {}
    ki = []
    for k in copy.deepcopy(KATEGORIAK):
        for v in k["valtozatok"]:
            f = (T.get(k["kat"]) or {}).get(v["id"]) or {}
            v.update({kk: vv for kk, vv in f.items() if kk in ("nev", "leiras", "miert")})
            if v.get("kar"):
                v["karakter"] = {"id": v["kar"], "szo": KARSZO[v["kar"]], "nev": (KR.get(v["kar"]) or {}).get("nev", "")}
        if KR and all(v.get("kar") for v in k["valtozatok"]):
            k["valtozatok"].sort(key=lambda v: KARSOR.index(v["kar"]))
        k["ajanlott"] = A.get(k["kat"]) or k["valtozatok"][0]["id"]
        ki.append(k)
    return ki


def alap_tartalom(tok):
    """Ha nincs video/tartalom.json, ezekkel a szövegekkel megy az előnézet (a tokenek tényeiből).
    A futás során a Claude az ügyfél oldaláról írja meg a valódi mondatokat (references/video/tartalom.md)."""
    M = tok.get("motivum") or {}
    marka = tok.get("marka") or {}
    tick = [t for t in (M.get("ticker") or []) if t][:3] or ["Első téma", "Második téma", "Harmadik téma"]
    while len(tick) < 3:
        tick.append("Következő téma")
    szel = (M.get("szellemszavak") or {})
    kulcs = (szel.get("hero") or (marka.get("nev") or "MÁRKA").split()[0]).upper()
    return {
        "felirat": ["ezt", "mindenkinek", "érdemes", "tudnia"], "felirat_kiemelt": 1,
        "hook": {"kicker": marka.get("nev", ""), "sorok": [tick[0], tick[1]], "kiemelt": 1},
        "info": {"kicker": marka.get("nev", ""), "szam": "3", "egyseg": "", "cimke": "téma ebben a videóban"},
        "temak": tick, "aktiv": 1,
        "nev": {"nev": marka.get("nev", ""), "szerep": marka.get("szlogen", "")[:40]},
        "fejezet": {"szam": "02", "cim": tick[1]},
        "zaro": {"social": "Ha hasznos volt", "cta": {"cim": "Kérj ajánlatot", "gomb": "Érdekel", "link": (marka.get("url") or "").replace("https://", "").rstrip("/")},
                 "szlogen": marka.get("szlogen", "")},
        "nyito": {"sorok": [tick[0], ""], "kiemelt": 0},
        "kulcsszo": kulcs,
        "oldalcsempek": [],
    }
