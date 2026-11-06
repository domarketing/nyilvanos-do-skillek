# -*- coding: utf-8 -*-
"""prezi-tema.json: a prezentációs arculat egyetlen forrása. A jóváhagyott webes tokenekből (tokenek.json) készül, és a
motor minden diát ebből rajzol. Örökölt (nem választható): paletta, betűk, ikonok, lekerekítés, árnyék, fotók és
fotókezelés, motívum, logó. Választható: a 10 prezi-kategória (katalogus.py) változatai.

    python3 prezi.py tema <munkamappa>            # -> <munkamappa>/prezi/prezi-tema.json (ajánlott változatokkal)
"""
import datetime
import json
import os
import re
from pathlib import Path

import alap
import betuk
import katalogus

VERZIO = 1


def _rel(p, alap_mappa):
    try:
        return str(Path(p).resolve().relative_to(Path(alap_mappa).resolve()))
    except Exception:
        return str(p)


def _abs(p, alap_mappa):
    if not p:
        return None
    return str(p) if os.path.isabs(str(p)) else str(Path(alap_mappa) / p)


def _pozicio(p):
    """'50% 62%' -> (0.5, 0.62)"""
    m = re.findall(r"(-?\d+(?:\.\d+)?)%", p or "")
    if len(m) >= 2:
        return float(m[0]) / 100.0, float(m[1]) / 100.0
    return 0.5, 0.5


def _van_alfa(ut):
    try:
        from PIL import Image
        im = Image.open(ut)
        if im.mode not in ("RGBA", "LA", "P"):
            return False
        a = im.convert("RGBA").getchannel("A")
        return a.getextrema()[0] < 200
    except Exception:
        return False


def ajanlas(tok):
    """Ajánlott változat kategóriánként, a jóváhagyott webes elemekből levezetve, indoklással."""
    komp = tok.get("komponensek") or {}

    def szo(k):
        v = komp.get(k) or {}
        return ((v.get("nev") or "") + " " + (v.get("leiras") or "")).lower()
    foto = ((tok.get("foto") or {}).get("kezeles") or "").lower() + " " + ((tok.get("foto") or {}).get("leiras") or "").lower()
    cim, kartya, alcim = szo("cim"), szo("kartya"), szo("alcim")
    sotet = (tok.get("szinek") or {}).get("mod") == "sotet"
    a, m = {}, {}
    polaroid = any(x in foto for x in ("polaroid", "megdönt", "döntött", "fehér keret"))
    if polaroid:
        a["cimdia"], m["cimdia"] = "D", "A weboldal nyitóképén is döntött, fehér keretes fotó áll; a címdia ezt viszi tovább."
    else:
        a["cimdia"], m["cimdia"] = "A", "Tiszta, sok levegős nyitás, a fotóid kerülnek előtérbe."
    a["fejezet"], m["fejezet"] = "B", "A színes panel jól elválasztja a fejezeteket, a fotóid pedig a márkád világát hozzák."
    a["hatter"] = "D" if sotet else "A"
    m["hatter"] = ("A webes arculatod sötét alapú, a diák is ezt követik." if sotet else
                   "A webes papírszín az alap; a fejezetek és a kérdések a mély színt kapják, ez adja a ritmust.")
    if "méretvonal" in cim or ("méret" in cim and "vonal" in cim):
        a["kiemeles"], m["kiemeles"] = "C", ("A weboldalon is méretvonal emeli ki a kulcsszót, két végén kis jelekkel, mint a "
                                             "kerttervek méretezése; a diákon ugyanez fut a kulcsszó alatt.")
    elif any(x in cim for x in ("karik", "kerít", "kör ")):
        a["kiemeles"], m["kiemeles"] = "D", "A weboldalon is kézzel húzott karika emeli ki a kulcsszót."
    elif any(x in cim for x in ("filc", "csík", "kiemelő")):
        a["kiemeles"], m["kiemeles"] = "B", "A weboldal címsoraiban is filctoll-csík emeli ki a kulcsszót."
    elif "aláhúz" in cim or "vonal" in cim:
        a["kiemeles"], m["kiemeles"] = "C", "A weboldal címsoraiban is vonal emeli ki a kulcsszót."
    elif "doboz" in cim or "blokk" in cim:
        a["kiemeles"], m["kiemeles"] = "A", "A weboldal címsoraiban is doboz emeli ki a kulcsszót."
    else:
        a["kiemeles"], m["kiemeles"] = "E", "A weboldalon a kulcsszót a szín emeli ki; a diákon is ez a legnyugodtabb."
    if polaroid:
        a["fotokeret"], m["fotokeret"] = "C", "Ez a webes fotókezelésed párja: fehér keret, enyhe döntés, a sarkán a jeled."
    elif "kör" in foto:
        a["fotokeret"], m["fotokeret"] = "B", "A weboldalon is kerek kivágású fotók szerepelnek."
    elif "eltolt" in foto or "blokk" in foto:
        a["fotokeret"], m["fotokeret"] = "D", "A weboldalon is eltolt színblokk áll a fotók mögött."
    else:
        a["fotokeret"], m["fotokeret"] = "A", "A weboldal kártyáinak sarkaival és árnyékával."
    tech = ((tok.get("ikon") or {}).get("technika") or "").lower()
    if any(x in kartya for x in ("tábla", "keret", "hajszál")):
        a["ikontarto"], m["ikontarto"] = "C", "A webes kártyáid keretes táblák; az ikonok is ilyen csempére kerülnek, így jobban látszanak."
    elif any(x in tech for x in ("ceruza", "vonal", "tus", "skicc")):
        a["ikontarto"], m["ikontarto"] = "B", "A finom vonalas ikonok egy halvány körön jobban kiemelkednek."
    else:
        a["ikontarto"], m["ikontarto"] = "A", "Az ikonjaid önmagukban is erősek, csempe nélkül nagyobbak lehetnek."
    if "tab." in kartya or "tab." in alcim or "tábla" in alcim:
        a["felsorolas"], m["felsorolas"] = "E", "A weboldalon „Tab. I, II” táblaszámok jelzik a sorrendet; a listák ezt folytatják."
    else:
        a["felsorolas"], m["felsorolas"] = "D", "A márkád saját jele lesz a felsorolásjel."
    a["szamok"], m["szamok"] = "A", "Három szám egymás mellett messziről is olvasható, és sok levegőt hagy."
    a["idezet"], m["idezet"] = ("C", "A kártya és a döntött fotó a webes fotókezelésedet folytatja.") if polaroid else \
        ("A", "Az idézet és a fotó egyenrangú, nyugodt elrendezés.")
    a["zaro"], m["zaro"] = "B", "A záródián ott vagy te is: a portréd, a neved és az elérhetőséged."
    return a, m


def keszit(munkamappa, tokenek_ut=None, valasztas=None, ajanlott=None, telepit=True):
    """A prezi-tema.json tartalma. munkamappa: az ügyfél arculat-mappája (benne tokenek.json)."""
    alap_mappa = Path(munkamappa).resolve()
    tok_ut = Path(tokenek_ut) if tokenek_ut else alap_mappa / "tokenek.json"
    tok = json.loads(tok_ut.read_text(encoding="utf-8"))
    aj, miert = ajanlas(tok)
    if ajanlott:
        aj.update(ajanlott)
    # betűk: a szerepek PowerPoint-neve, a mért TTF-ek (a hiányzókat letölti a munkamappa betuk/ mappájába)
    bt = {}
    for sz, tk in betuk.TOKEN_SZEREP.items():
        blokk = (tok.get("betuk") or {}).get(tk) or (tok.get("betuk") or {}).get("body")
        b = betuk.szerep_betu(blokk, sz, alap_mappa, alap_mappa / "betuk")
        b["ttf"] = _rel(b["ttf"], alap_mappa)
        b["ttf_b"] = _rel(b["ttf_b"], alap_mappa)
        bt[sz] = b
    if telepit:
        betuk.telepit([_abs(b[k], alap_mappa) for b in bt.values() for k in ("ttf", "ttf_b")])
    f = tok.get("forma") or {}
    szinek = dict(tok.get("szinek") or {})
    szinek.update({k: v for k, v in (tok.get("szinek_extra") or {}).items() if isinstance(v, str)})
    fotok = []
    for x in (tok.get("foto") or {}).get("valogatott_info") or []:
        ut = _abs(x.get("fajl"), alap_mappa)
        if not ut or not os.path.exists(ut):
            continue
        fx, fy = _pozicio(x.get("pozicio"))
        try:
            from PIL import Image, ImageOps
            w, h = ImageOps.exif_transpose(Image.open(ut)).size
        except Exception:
            w, h = 1600, 1000
        rajz = _van_alfa(ut)
        fotok.append({"id": x.get("id") or Path(ut).stem, "fajl": x.get("fajl"), "alt": x.get("alt", ""),
                      "fx": fx, "fy": fy, "w": w, "h": h, "rajz": rajz,
                      "kepernyo": (not rajz) and alap.kepernyo_e(ut, w, h)})
    arc = {}
    if (alap_mappa / "arculat.json").exists():
        try:
            arc = json.loads((alap_mappa / "arculat.json").read_text(encoding="utf-8"))
        except Exception:
            arc = {}
    kap = arc.get("kapcsolat") or {}
    alair = (arc.get("tortenet") or {}).get("alairas") or {}
    marka = tok.get("marka") or {}
    web = re.sub(r"^https?://(www\.)?", "", marka.get("url") or "").rstrip("/")
    kontakt = {"nev": alair.get("nev") or marka.get("nev"), "szerep": alair.get("szerep", ""),
               "telefon": kap.get("telefon", ""), "email": kap.get("email", ""), "web": web}
    ik = tok.get("ikon") or {}
    # az ügyfél 5 karaktere a márka-diagnózisból (a változatok neve és részlete ebből jön)
    dns = {}
    dns_ut = alap_mappa / (tok.get("marka_dns") or "marka-dns.json")
    if dns_ut.exists():
        try:
            dns = json.loads(dns_ut.read_text(encoding="utf-8"))
        except Exception:
            dns = {}
    karakterek = {}
    for k in katalogus.KARAKTEREK:
        x = (dns.get("karakterek") or {}).get(k) or {}
        karakterek[k] = {"nev": x.get("nev") or katalogus.KARAKTER_ALAPNEV[k], "alapnev": katalogus.KARAKTER_ALAPNEV[k],
                         "otlet": x.get("otlet", ""), "reszlet": x.get("reszlet", "")}
    # a webes címsor-kiemelés karaktere (cM -> modern): a prezi kiemelés-változata ugyanahhoz a karakterhez kerüljön
    betu2kar = {"E": "elegans", "M": "modern", "B": "meresz", "F": "baratsagos", "K": "klasszikus"}
    felulir, nevek, stilus = {}, {}, {}
    cim_k = ((tok.get("komponensek") or {}).get("cim") or {})
    cim_szo = ((cim_k.get("nev") or "") + " " + (cim_k.get("leiras") or "")).lower()
    if "méretvonal" in cim_szo or ("méret" in cim_szo and "vonal" in cim_szo):
        stilus["kiemeles_C"] = "meretvonal"
        nevek["kiemeles"] = {"C": ["Méretvonal", "Vékony méretvonal a kulcsszó alatt, két végén kis jelekkel, mint a "
                                                 "kerttervek méretezésénél."]}
    web_kar = betu2kar.get((cim_k.get("id") or "")[-1:]) if cim_k.get("id") else None
    if web_kar:
        t_ = dict(katalogus.KARAKTER_FORMA["kiemeles"])
        cel = aj.get("kiemeles")
        regi = t_.get(web_kar)
        if cel and regi and regi != cel:
            masik = next(k for k, f in t_.items() if f == cel)
            t_[web_kar], t_[masik] = cel, regi
            felulir["kiemeles"] = t_
    tema = {
        "verzio": VERZIO,
        "marka": marka,
        "forras": {"tokenek": _rel(tok_ut, alap_mappa), "web_verzio": (tok.get("allapot") or {}).get("web_verzio"),
                   "web_jovahagyva": bool((tok.get("allapot") or {}).get("jovahagyva"))},
        "szinek": szinek,
        "betuk": bt,
        "forma": {"r_kartya_px": f.get("r_kartya", 12), "r_gomb_px": f.get("r_gomb", 12),
                  "arnyek": f.get("arnyek", "lagy"), "keret_px": f.get("keret_px", 1)},
        "ikon": {"stilus_nev": ik.get("stilus_nev"), "technika": ik.get("technika"), "elotag": ik.get("elotag"),
                 "mappa": ik.get("mappa"), "fajlok": ik.get("fajlok") or {}, "temak": ik.get("temak") or {}},
        "fotok": fotok,
        "fotokezeles": {k: (tok.get("foto") or {}).get(k) for k in ("kezeles", "kezeles_id", "leiras")},
        "motivum": {k: (tok.get("motivum") or {}).get(k) for k in ("formak_svg", "jel", "textura", "dekor", "hatar")},
        "logo": tok.get("logo") or {},
        "hangnem": tok.get("hangnem", ""),
        "komponensek_web": tok.get("komponensek") or {},
        "kontakt": kontakt,
        "karakterek": karakterek,
        "karakter_forma": felulir,
        "valtozat_nevek": nevek,
        "stilus": stilus,
        "valasztas": dict(valasztas or aj),
        "ajanlott": aj,
        "ajanlas_miert": miert,
        "szabalyok": {"arany": "16:9", "min_torzs_pt": 20, "min_cimke_pt": 16, "logo": "jobbra lent"},
        "jovahagyva": False,
        "datum": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    return tema


def _potol(sz):
    """A hiányzó levezetett színek pótlása a márkaszínek keveréséből (régebbi tokenfájlokhoz). Új színt nem vezet be."""
    def h2t(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def t2h(t):
        return "#%02X%02X%02X" % t

    def mix(a, b, t):
        a, b = h2t(a), h2t(b)
        return t2h(tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)))

    def lum(h):
        def f(v):
            v = v / 255.0
            return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        r, g, b = h2t(h)
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

    def kontr(a, b):
        la, lb = lum(a), lum(b)
        return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
    sz.setdefault("paper", "#FFFFFF")
    sz.setdefault("ink", "#1A1A1A")
    sz.setdefault("primary", sz["ink"])
    sz.setdefault("accent", sz["primary"])
    sz.setdefault("accent2", sz["accent"])
    sz.setdefault("deep", mix(sz["primary"], "#000000", 0.55))
    p, i = sz["paper"], sz["ink"]
    sz.setdefault("ink_2", mix(i, p, 0.25))
    sz.setdefault("ink_3", mix(i, p, 0.45))
    sz.setdefault("line", mix(i, p, 0.82))
    sz.setdefault("tint", mix(sz["primary"], p, 0.84))
    sz.setdefault("sand", mix(sz["accent2"], p, 0.8))
    for k in ("primary", "accent", "deep"):
        sz.setdefault("on_" + k, "#FFFFFF" if kontr(sz[k], "#FFFFFF") >= kontr(sz[k], i) else i)
    for k in ("primary", "accent"):
        if ("%s_text" % k) not in sz:
            c = sz[k]
            t = 0.0
            while kontr(c, p) < 4.5 and t < 0.9:
                t += 0.1
                c = mix(sz[k], i, t)
            sz["%s_text" % k] = c
    sz.setdefault("hand", sz.get("accent_text", sz["accent"]))


class Tema(object):
    """A betöltött prezi-téma: a motor ebből rajzol (alap.T)."""

    def __init__(self, d, alap_mappa):
        self.d = d
        self.alap = str(Path(alap_mappa).resolve())
        self.szin = {k: v for k, v in (d.get("szinek") or {}).items() if isinstance(v, str) and v.startswith("#")}
        self.szin.setdefault("card", "#FFFFFF")
        self.szin.setdefault("white", "#FFFFFF")
        _potol(self.szin)
        self.mod = (d.get("szinek") or {}).get("mod", "vilagos")
        self.betu = {}
        for sz, b in (d.get("betuk") or {}).items():
            b = dict(b)
            b["ttf"] = _abs(b.get("ttf"), self.alap)
            b["ttf_b"] = _abs(b.get("ttf_b"), self.alap) or b["ttf"]
            self.betu[sz] = b
        fo = d.get("forma") or {}
        rk = float(fo.get("r_kartya_px", 12))
        self.r_kartya = 0.5 if rk >= 99 else rk / 96.0 * 1.35
        rg = float(fo.get("r_gomb_px", 12))
        self.r_gomb = 0.5 if rg >= 99 else rg / 96.0 * 1.35
        self.arnyek = fo.get("arnyek", "lagy")
        kp = float(fo.get("keret_px", 1) or 0)
        self.keret_pt = 0 if kp <= 0 else max(0.75, kp * 0.75)
        ik = d.get("ikon") or {}
        self.ikonok = {n: _abs(p, self.alap) for n, p in (ik.get("fajlok") or {}).items() if os.path.exists(_abs(p, self.alap))}
        self.fotok = []
        for x in d.get("fotok") or []:
            ut = _abs(x.get("fajl"), self.alap)
            if ut and os.path.exists(ut):
                y = dict(x)
                y["ut"] = ut
                self.fotok.append(y)
        self.motivum = d.get("motivum") or {}
        self.logo = {k: _abs(v, self.alap) for k, v in (d.get("logo") or {}).items() if v}
        self.kontakt = d.get("kontakt") or {}
        self.marka = d.get("marka") or {}
        self.valasztas = dict(d.get("ajanlott") or {})
        self.valasztas.update(d.get("valasztas") or {})
        self.karakterek = d.get("karakterek") or {}
        self.karakter_aktiv = None       # a rajzolás alatt álló dia karaktere (diak.dia állítja)

    def reszlet(self):
        """Az aktív karakter részlete (kisbetűvel), vagy üres szöveg."""
        k = self.karakterek.get(self.karakter_aktiv or "") or {}
        return (k.get("reszlet") or "").lower()

    def v(self, kat):
        return self.valasztas.get(kat) or "A"

    def foto_lista(self, rajz=False):
        return [f for f in self.fotok if bool(f.get("rajz")) == rajz]


def betolt(ut):
    ut = Path(ut).resolve()
    d = json.loads(ut.read_text(encoding="utf-8"))
    # a téma a munkamappa prezi/ almappájában van; az útvonalak a munkamappához relatívak
    # (exportált csomagban: "alap_rel": "." -> a téma mappájához relatívak)
    if d.get("alap_rel"):
        alap_mappa = (ut.parent / d["alap_rel"]).resolve()
    else:
        alap_mappa = ut.parent.parent if ut.parent.name == "prezi" else ut.parent
    return Tema(d, alap_mappa)


def bekapcsol(t):
    alap.T = t
    alap._FONT_CACHE.clear()
    katalogus.FELULIRAS.clear()
    katalogus.FELULIRAS.update(t.d.get("karakter_forma") or {})
    katalogus.NEV_FELULIRAS.clear()
    katalogus.NEV_FELULIRAS.update(t.d.get("valtozat_nevek") or {})
    return t


def ment(tema, ut):
    ut = Path(ut)
    ut.parent.mkdir(parents=True, exist_ok=True)
    ut.write_text(json.dumps(tema, ensure_ascii=False, indent=2), encoding="utf-8")
    return ut
