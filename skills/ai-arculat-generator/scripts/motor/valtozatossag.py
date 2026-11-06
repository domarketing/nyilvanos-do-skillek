# -*- coding: utf-8 -*-
"""Változatosság-ellenőrzés: ne kapja meg minden ügyfél ugyanazt a palettát, betűpárt, ikonstílust és komponenst.

A valaszto.epit() a szabvány után ezt is lefuttatja; ha hibát talál, NEM épít (csak --engedd mellett, fejlesztéshez).
Önállóan: python3 <SKILL>/scripts/valtozatossag.py arculat.json
"""
import itertools
import json
import re
import sys
from pathlib import Path

from .alap import g
from . import epito

SKILL = Path(__file__).resolve().parents[2]
KEDVENC_ALAP = {"Fraunces", "Playfair Display", "DM Serif Display", "Bricolage Grotesque", "Outfit"}
KOMPONENS = ("cim", "alcim", "gomb", "kartya", "foto")
KAR_NEV = {"elegans": "Elegáns", "modern": "Modern", "meresz": "Merész", "baratsagos": "Barátságos", "klasszikus": "Klasszikus"}
OSZTALY_SZEREPBOL = {"cim-serif": "serif", "szoveg-serif": "serif", "cim-sans": "sans", "szoveg-sans": "sans",
                     "cim-slab": "slab", "cim-display": "display", "cim-kerek": "kerek", "szoveg-kerek": "kerek",
                     "cim-keskeny": "keskeny", "kez": "kez", "kez-script": "script", "cimke-mono": "mono"}


def _betu_kat():
    try:
        d = json.loads((SKILL / "references" / "betuk.json").read_text(encoding="utf-8"))
        return {b["csalad"]: b for b in d.get("betuk", [])}
    except Exception:
        return {}


def _technikak():
    try:
        d = json.loads((SKILL / "references" / "ikon-technikak.json").read_text(encoding="utf-8"))
        return {t["id"]: t for t in d.get("technikak", [])}
    except Exception:
        return {}


# ------------------------------------------------------------------ diagnózis

def dns_hibak(dns):
    if not dns:
        return ["Hiányzik a márka-diagnózis (marka-dns.json a munkamappában): ebből jön minden egyedi ötlet, "
                "lásd references/8-marka-dns.md."]
    h = []
    for k in ("szakma", "kinek", "igy_latunk"):
        if not dns.get(k):
            h.append(f"marka-dns.json: üres a „{k}” mező.")
    if len(g(dns, "targyi_vilag", "szinek") or []) < 6:
        h.append("marka-dns.json: a targyi_vilag.szinek listában legalább 6 szín kell (a szakma anyagaiból, névvel).")
    kar = dns.get("karakterek") or {}
    hiany = [KAR_NEV[k] for k in KAR_NEV if not (kar.get(k) or {}).get("nev")]
    if hiany:
        h.append("marka-dns.json: az ügyfélre írt karakter-név hiányzik: " + ", ".join(hiany) + ".")
    return h


# ------------------------------------------------------------------ paletta

def paletta_hibak(opc, spec, dns):
    sys.path.insert(0, str(SKILL / "scripts"))
    import paletta_gen
    lista = opc.get("paletta", {}).get("lista") or []
    talalt = [c["hex"] if isinstance(c, dict) else c for c in (g(dns or {}, "ami_mar_megvan", "szinek") or [])] \
        or (g(spec, "profil", "talalt_szinek") or [])
    return paletta_gen.ellenoriz_lista(lista, talalt)


# ------------------------------------------------------------------ betűk

def betu_hibak(opc, dns):
    hiba, figy = [], []
    kat = _betu_kat()
    sajat = set(g(dns or {}, "ami_mar_megvan", "betuk") or [])
    lista = opc.get("betu", {}).get("lista") or []
    disp = [b.get("display") for b in lista]
    if len(set(disp)) < len(disp):
        hiba.append("Betűk: két betűpárban ugyanaz a címbetű; mind az 5 pár más címbetűvel készüljön.")
    osztalyok = set()
    for b in lista:
        for szerep in ("display", "body", "hand", "label"):
            c = b.get(szerep)
            if not c:
                continue
            info = kat.get(c)
            if info is None and c not in sajat:
                hiba.append(f'Betűk / {b["id"]}: a(z) „{c}” nincs a betuk.json-ban (ékezet-ellenőrzés nélküli betű).')
                continue
            info = info or {}
            if (info.get("tiltott") or info.get("szerep") == "tiltott-reflex") and c not in sajat:
                hiba.append(f'Betűk / {b["id"]}: a(z) „{c}” reflex-betű; csak akkor jöhet, ha az ügyfél saját betűje.')
            kedvenc = info.get("kedvenc") if "kedvenc" in info else (c in KEDVENC_ALAP)
            if kedvenc and szerep == "display" and not (b.get("kedvenc_indoklas") or "").strip() and c not in sajat:
                hiba.append(f'Betűk / {b["id"]}: a(z) „{c}” túlhasznált kedvenc. Csak indoklással (kedvenc_indoklas: '
                            f'miért éppen ennek az ügyfélnek), különben válassz mást a betu_valaszto.py listájából.')
        d = kat.get(b.get("display")) or {}
        osztalyok.add(d.get("osztaly") or OSZTALY_SZEREPBOL.get(d.get("szerep"), d.get("szerep")))
    if len(lista) >= 5 and len(osztalyok) < 3:
        hiba.append(f"Betűk: a címbetűk csak {len(osztalyok)} betűtípus-osztályból jönnek; legalább 3 kell "
                    "(pl. serif, grotesk, keskeny, kézírás, slab).")
    body = [b.get("body") for b in lista if b.get("body")]
    if len(lista) >= 5 and len(set(body)) < 3:
        hiba.append("Betűk: a szövegbetű 5 párból legalább 3 különböző legyen.")
    label = [b.get("label") for b in lista if b.get("label")]
    if len(label) >= 5 and len(set(label)) < 3:
        figy.append("Betűk: a címke-betűk (mono) nagyon ismétlődnek.")
    return hiba, figy


# ------------------------------------------------------------------ ikonok

def ikon_hibak(spec):
    hiba, figy = [], []
    isp = epito.ikon_spec(spec)
    st = isp.get("stilusok") or []
    if not st:
        return hiba, figy
    tech = _technikak()
    hasznalt = []
    for s in st:
        t = tech.get(s.get("technika"))
        if not t:
            hiba.append(f'Ikonok / {s.get("id")}: nincs „technika” (a references/ikon-technikak.json egyik id-je).')
            continue
        hasznalt.append(t)
        sablon = re.sub(r"\{[a-z0-9]+\}", "", t["prompt"])
        sajat = re.sub(r"\{[a-z0-9]+\}", "", s.get("elotag", ""))
        if not (s.get("csavar") or "").strip() and len(sajat) - len(sablon) < 40:
            hiba.append(f'Ikonok / {s["id"]}: a prompt a szótár sablonja, ügyfélre szabás nélkül. Írd bele a „csavart” '
                        f'(anyag, nézőpont, rajzmód a tárgyi világából).')
    ids = [t["id"] for t in hasznalt]
    if len(set(ids)) < len(ids):
        hiba.append("Ikonok: két stílus ugyanazzal a technikával készül.")
    cs = [t["csalad"] for t in hasznalt]
    if len(st) >= 5 and cs and (len(set(cs)) < 3 or max(cs.count(c) for c in cs) > 2):
        hiba.append("Ikonok: a stílusok legalább 3 technika-családból jöjjenek, egy családból legfeljebb kettő.")
    if sum(bool(t.get("regi")) for t in hasznalt) > 1:
        hiba.append("Ikonok: a régi fix készletből (lapos, vonal+színfolt, riso, agyag, matrica) legfeljebb egy stílus lehet.")
    return hiba, figy


# ------------------------------------------------------------------ komponensek

def _maszk_ujjlenyomat(c):
    """A használt maszk/háttér-SVG-k azonosítója: két opció más formával (ecsetcsík vs. ceruzás karika) nem egyforma."""
    import hashlib
    urls = sorted(set(re.findall(r'url\("?data:[^)]{20,200}', c)))
    return hashlib.md5("|".join(urls).encode()).hexdigest()[:8] if urls else ""


def _jegyek(css):
    """Néhány durva vizuális jegy a CSS-ből (két opció túl hasonló, ha szinte mind egyezik)."""
    c = (css or "").lower()
    r = re.findall(r"border-radius:\s*([\d.]+)(px|em|%)", c)
    rv = max([float(x) * (16 if u == "em" else 1) for x, u in r] or [0])
    rb = 0 if rv <= 4 else 1 if rv <= 12 else 2 if rv <= 30 else 3
    arny = "nincs" if "box-shadow" not in c else ("kemeny" if re.search(r"box-shadow:[^;]*\b\d+px \d+px 0", c) else "lagy")
    return (rb, arny, "border:" in c or "outline:" in c, "uppercase" in c, "letter-spacing" in c, "gradient" in c,
            "rotate" in c or "skew" in c, c.count("::before") + c.count("::after") > 0, "background-image" in c,
            "clip-path" in c or "mask" in c, "--f-hand" in c, "--f-label" in c, "--f-display" in c, "dashed" in c or "dotted" in c,
            "inset" in c, bool(re.search(r"0 0 0 [\d.]+px", c)), "padding" in c, min(c.count("{"), 6) // 2,
            bool(re.search(r"#[0-9a-f]{3,6}\b", c)), "filter" in c, "transition" in c,
            "italic" in c, "small-caps" in c, "clip-path" in c, "::before" in c, "::after" in c, "inline-block" in c,
            "counter" in c, "attr(" in c, _maszk_ujjlenyomat(c))


def komponens_hibak(opc):
    hiba, figy = [], []
    for kat in KOMPONENS:
        lista = opc.get(kat, {}).get("lista") or []
        konyvtari = [x["id"] for x in lista if not x.get("egyedi")]
        if konyvtari:
            hiba.append(f'{epito.KAT_NEV[kat][0]}: könyvtári opció ({", ".join(konyvtari)}); az alap-elemeket az ügyfélre '
                        f'kell írni (egyedi_opciok.{kat}), a könyvtár csak kiindulás.')
        reszlet = [x for x in lista if (x.get("reszlet") or "").strip()]
        if len(lista) >= 5 and len(reszlet) < 3:
            hiba.append(f'{epito.KAT_NEV[kat][0]}: legalább 3 opcióban legyen szakmai részlet („reszlet”: mi jön a '
                        f'szakma tárgyi világából, pl. latin növénynév, perforáció, pecsét).')
        for a, b in itertools.combinations(lista, 2):
            ja, jb = _jegyek(a.get("css")), _jegyek(b.get("css"))
            egyezo = sum(x == y for x, y in zip(ja, jb)) / len(ja)
            if egyezo >= 0.95:
                hiba.append(f'{epito.KAT_NEV[kat][0]}: a(z) {a["id"]} és {b["id"]} szinte ugyanaz (forma, keret, árnyék, '
                            f'betű); legyen tényleg más karakter.')
    return hiba, figy


def ellenoriz(spec, opc, dns):
    hiba, figy = [], []
    hiba += dns_hibak(dns)
    for fv in (lambda: paletta_hibak(opc, spec, dns), lambda: betu_hibak(opc, dns), lambda: ikon_hibak(spec),
               lambda: komponens_hibak(opc)):
        h, f = fv()
        hiba += h
        figy += f
    return hiba, figy
