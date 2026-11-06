#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Öt paletta az ügyfél saját színeiből és a szakmája tárgyi világának színeiből (OKLCH, kontraszt, különbözőség).

A fix paletta-archetípusok helyett: a jelölt színek a márka-diagnózisból jönnek (marka-dns.json):
  "ami_mar_megvan.szinek"  a mostani oldal színei (hexa lista)
  "targyi_vilag.szinek"    a szakma anyagainak, tárgyainak színei [{"nev": "zsálya", "hex": "#9CAF88"}, ...]
  "formanyelv"             tengelyek 0..1 (harsany, kortars, homerseklet...), "sotet_karakter", "hu_karakter" (opcionális)

  python3 paletta_gen.py javasol marka-dns.json [--ki paletta-javaslat.json] [--minta minta.png]
  python3 paletta_gen.py ellenoriz arculat.json          # az arculat.json 5 palettájának ellenőrzése

A kimenet egy kész "opciok.paletta" blokk (5 karakter: pE pM pB pF pK, mindegyik más színekből), amit a nevek és
az indoklások finomítása után az arculat.json-ba teszel. Az ellenőrzést a valtozatossag.py is futtatja.
"""
import argparse
import itertools
import json
import math
import sys
from pathlib import Path

# ------------------------------------------------------------------ színtér

def h2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2h(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in rgb)


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(x):
    v = 12.92 * x if x <= 0.0031308 else 1.055 * (abs(x) ** (1 / 2.4)) * (1 if x >= 0 else -1) - 0.055
    return v * 255


def _cbrt(x):
    return math.copysign(abs(x) ** (1 / 3), x)


def oklab(hexa):
    r, g, b = (_lin(c) for c in h2rgb(hexa))
    l = _cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = _cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = _cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def _oklab_rgb(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (_gam(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
            _gam(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
            _gam(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s))


def oklch(hexa):
    L, a, b = oklab(hexa)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def lch2hex(L, C, h):
    """OKLCH -> hexa, a színtérből kilógó színnél a telítettséget csökkenti (a világosság és az árnyalat marad)."""
    L = max(0.0, min(1.0, L))
    lo, hi = 0.0, max(0.0, C)
    def rgb(c):
        return _oklab_rgb(L, c * math.cos(math.radians(h)), c * math.sin(math.radians(h)))
    def bent(v):
        return all(-0.5 <= x <= 255.5 for x in v)
    if bent(rgb(hi)):
        return rgb2h(rgb(hi))
    for _ in range(24):
        mid = (lo + hi) / 2
        if bent(rgb(mid)):
            lo = mid
        else:
            hi = mid
    return rgb2h(rgb(lo))


def de(a, b):
    """Színkülönbség (OKLab euklideszi; ~0.02 alig észrevehető, 0.1 felett jól látható)."""
    A, B = oklab(a), oklab(b)
    return math.dist(A, B)


def hue_tav(h1, h2):
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)


def lum(hexa):
    r, g, b = (_lin(c) for c in h2rgb(hexa))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def kontraszt(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def on(bg):
    """Olvasható szöveg a színen: fehér vagy sötét (mint a web motorban)."""
    return "#FFFFFF" if kontraszt(bg, "#FFFFFF") >= kontraszt(bg, "#161616") * 0.8 else "#161616"


# ------------------------------------------------------------------ magyar színnevek (ha a diagnózis nem nevezte el)

def szinnev(hexa):
    L, C, h = oklch(hexa)
    if C < 0.03:
        if L > 0.93:
            return "tört fehér"
        if L > 0.75:
            return "kőszürke"
        if L > 0.45:
            return "grafit"
        return "tinta"
    sav = [(20, "bordó" if L < 0.5 else "rózsa"), (45, "korall" if L > 0.55 else "téglavörös"),
           (70, "barack" if L > 0.7 else "rozsda"), (95, "mustár" if L < 0.78 else "napsárga"),
           (115, "olajzöld" if C < 0.12 else "citrom"), (150, "zsálya" if C < 0.1 else "levélzöld"),
           (185, "mélyzöld" if L < 0.5 else "menta"), (215, "türkiz"), (245, "acélkék" if C < 0.1 else "égkék"),
           (275, "tintakék" if L < 0.5 else "búzavirág"), (310, "levendula" if L > 0.6 else "szilva"),
           (345, "mályva" if C < 0.12 else "pink"), (361, "bordó" if L < 0.5 else "rózsa")]
    for hatar, nev in sav:
        if h < hatar:
            return nev
    return "színes"


# ------------------------------------------------------------------ karakterek (paraméter-tartományok, nem kész paletták)

KARAKTEREK = {
    #             fő szín L / C         kiemelő L / C         harmad C     papír L, C     tinta L
    "elegans":    dict(pL=(.36, .52), pC=(.04, .11), aL=(.62, .80), aC=(.04, .11), a2C=(.05, .13), paL=.972, paC=.008, iL=.24,
                       harm={"rokon": 1.0, "kieg": .7, "tobb": .45}),
    "modern":     dict(pL=(.48, .64), pC=(.12, .20), aL=(.62, .82), aC=(.10, .18), a2C=(.10, .18), paL=.985, paC=.004, iL=.22,
                       harm={"rokon": .6, "kieg": 1.0, "tobb": .85}),
    "meresz":     dict(pL=(.50, .70), pC=(.17, .26), aL=(.70, .88), aC=(.14, .22), a2C=(.12, .22), paL=.965, paC=.02, iL=.20,
                       harm={"rokon": .4, "kieg": 1.0, "tobb": .9}),
    "baratsagos": dict(pL=(.58, .76), pC=(.10, .17), aL=(.70, .86), aC=(.08, .15), a2C=(.08, .16), paL=.975, paC=.018, iL=.27,
                       harm={"rokon": .8, "kieg": .75, "tobb": 1.0}),
    "klasszikus": dict(pL=(.30, .46), pC=(.05, .12), aL=(.55, .72), aC=(.06, .13), a2C=(.05, .12), paL=.955, paC=.022, iL=.21,
                       harm={"rokon": .9, "kieg": .85, "tobb": .5}),
}
SOTET = dict(pL=(.70, .84), aL=(.74, .88), paL=.20, paC=.022, iL=.94)
NEVEK = {"elegans": "Elegáns", "modern": "Modern", "meresz": "Merész", "baratsagos": "Barátságos", "klasszikus": "Klasszikus"}
IDK = {"elegans": "pE", "modern": "pM", "meresz": "pB", "baratsagos": "pF", "klasszikus": "pK"}


def illeszt(hexa, Ls, Cs, h_tol=None):
    """A szín a karakter tartományába: világosság és telítettség a tartomány közelébe, az árnyalat marad."""
    L, C, h = oklch(hexa)
    L2 = min(max(L, Ls[0]), Ls[1])
    C2 = min(max(C, Cs[0]), Cs[1]) if C > 0.025 else min(C, Cs[1])   # szürkét nem színezünk be
    return lch2hex(L2, C2, h), math.hypot(L2 - L, C2 - C)


def harmonia(h1, h2):
    d = hue_tav(h1, h2)
    if d < 40:
        return "rokon"
    if d > 140:
        return "kieg"
    return "tobb"


def jeloltek(dns):
    """A színforrások: a mostani oldal színei és a tárgyi világ színei, névvel és eredettel."""
    out = []
    for h in (dns.get("ami_mar_megvan") or {}).get("szinek") or []:
        hx = h["hex"] if isinstance(h, dict) else h
        nev = h.get("nev") if isinstance(h, dict) else None
        out.append({"hex": hx.upper(), "nev": nev or szinnev(hx), "forras": "a mostani oldal"})
    for h in (dns.get("targyi_vilag") or {}).get("szinek") or []:
        out.append({"hex": h["hex"].upper(), "nev": h.get("nev") or szinnev(h["hex"]), "forras": h.get("forras") or "a szakma világa"})
    # ismétlődő (szinte azonos) színek ki
    egyedi = []
    for j in out:
        if all(de(j["hex"], e["hex"]) > 0.03 for e in egyedi):
            egyedi.append(j)
    return egyedi


def semleges(jel, pri_h):
    """Papír-árnyalat: a világ legkevésbé telített színéből, különben a fő szín árnyalatából."""
    s = sorted(jel, key=lambda j: oklch(j["hex"])[1])
    if s and oklch(s[0]["hex"])[1] < 0.06:
        return oklch(s[0]["hex"])[2], s[0]
    return pri_h, None


def paletta_jelolt(kar, pri, acc, acc2, jel, sotet=False):
    k = KARAKTEREK[kar]
    pL = SOTET["pL"] if sotet else k["pL"]
    aL = SOTET["aL"] if sotet else k["aL"]
    p, dp = illeszt(pri["hex"], pL, k["pC"])
    a, da = illeszt(acc["hex"], aL, k["aC"])
    a2, da2 = illeszt(acc2["hex"], (min(pL[0], aL[0]), max(pL[1], aL[1])), k["a2C"])
    ph, papir_forras = semleges(jel, oklch(p)[2])
    if sotet:
        paper = lch2hex(SOTET["paL"], SOTET["paC"], oklch(p)[2])
        ink = lch2hex(SOTET["iL"], 0.012, ph)
        deep = lch2hex(SOTET["paL"] - 0.06, SOTET["paC"], oklch(p)[2])
        card = lch2hex(SOTET["paL"] + 0.05, SOTET["paC"], oklch(p)[2])
    else:
        paper = lch2hex(k["paL"], k["paC"], ph)
        ink = lch2hex(k["iL"], 0.03, oklch(p)[2])
        deep = lch2hex(0.27, min(0.07, oklch(p)[1]), oklch(p)[2])
        card = "#FFFFFF" if k["paL"] < 0.98 else lch2hex(0.995, 0.003, ph)
    return {"primary": p, "accent": a, "accent2": a2, "paper": paper, "ink": ink, "deep": deep, "card": card,
            "mod": "sotet" if sotet else "vilagos", "_igazitas": dp + da + 0.5 * da2,
            "_forras": {"primary": pri, "accent": acc, "accent2": acc2, "papir": papir_forras}}


def ellenorzes(p):
    """Kontraszt-mérések egy palettán (WCAG)."""
    paper, ink = p["paper"], p["ink"]
    m = {"ink_paper": kontraszt(ink, paper), "primary_paper": kontraszt(p["primary"], paper),
         "on_primary": kontraszt(on(p["primary"]), p["primary"]), "accent_paper": kontraszt(p["accent"], paper)}
    return {k: round(v, 2) for k, v in m.items()}


def pontoz(kar, P, dns, hu=False):
    k = KARAKTEREK[kar]
    m = ellenorzes(P)
    s = 0.0
    tipp = [t.lower() for t in (((dns.get("karakterek") or {}).get(kar) or {}).get("szinek") or [])]
    if tipp:
        f = P["_forras"]
        s += 1.4 * (f["primary"]["nev"].lower() in tipp) + 0.8 * (f["accent"]["nev"].lower() in tipp) \
            + 0.3 * (f["accent2"]["nev"].lower() in tipp)
    s += 2.0 if m["ink_paper"] >= 7 else (1.0 if m["ink_paper"] >= 4.5 else -3)
    s += 1.0 if m["on_primary"] >= 4.5 else (0.3 if m["on_primary"] >= 3.6 else -1.5)
    s += 0.6 if m["primary_paper"] >= 3 else 0
    s += 1.6 * k["harm"][harmonia(oklch(P["primary"])[2], oklch(P["accent"])[2])]
    s -= 3.0 * P["_igazitas"]                       # minél kevésbé kell erőszakolni a forrásszínt, annál jobb
    s += 0.4 * (P["_forras"]["primary"]["forras"] != "a mostani oldal") * (0 if hu else 1)
    # lila-kék AI-gradiens tilalom, ha nem az ügyfél színe
    for x in ("primary", "accent"):
        L, C, h = oklch(P[x])
        if 265 <= h <= 300 and C > 0.12 and P["_forras"][x]["forras"] != "a mostani oldal":
            s -= 2.5
    # hőmérséklet: a diagnózis szerinti meleg/hideg
    hom = (dns.get("formanyelv") or {}).get("homerseklet")
    if hom is not None:
        h = oklch(P["primary"])[2]
        meleg = 1.0 if (h < 100 or h > 330) else (0.0 if 160 < h < 290 else 0.5)
        s += 0.8 * (1 - abs(meleg - hom))
    return s


def paletta_tav(p, q):
    return min(de(p["primary"], q["primary"]), 0.6) + 0.5 * de(p["accent"], q["accent"]) + 0.3 * de(p["paper"], q["paper"])


def sotet_karakter(dns, hu_kar):
    if dns.get("sotet_karakter") in KARAKTEREK:
        return dns["sotet_karakter"]
    f = dns.get("formanyelv") or {}
    harsany, kortars, kezi = f.get("harsany", .5), f.get("kortars", .5), f.get("kezi", .5)
    jel = {"elegans": (1 - harsany) * (1 - .4 * kortars), "klasszikus": (1 - kortars) * .9,
           "meresz": harsany, "modern": kortars * (1 - kezi), "baratsagos": .1}
    jel.pop(hu_kar, None)
    return max(jel, key=jel.get)


def hu_karakter(dns, jel):
    if dns.get("hu_karakter") in KARAKTEREK:
        return dns["hu_karakter"]
    sajat = [j for j in jel if j["forras"] == "a mostani oldal" and oklch(j["hex"])[1] > 0.02]
    if not sajat:
        return "modern"
    fo = max(sajat, key=lambda j: oklch(j["hex"])[1])
    return min(KARAKTEREK, key=lambda kr: illeszt(fo["hex"], KARAKTEREK[kr]["pL"], KARAKTEREK[kr]["pC"])[1])


def javasol(dns):
    jel = jeloltek(dns)
    szines = [j for j in jel if oklch(j["hex"])[1] > 0.02]
    if len(szines) < 3:
        raise SystemExit("Kevés a színes jelölt: a marka-dns.json targyi_vilag.szinek listájába írj legalább 6 színt.")
    hu = hu_karakter(dns, jel)
    st = sotet_karakter(dns, hu)
    sajat = [j for j in szines if j["forras"] == "a mostani oldal"] or szines
    eredmeny = {}
    for kar in KARAKTEREK:
        lista = []
        prik = sajat if kar == hu else szines
        for pri in prik:
            for acc in szines:
                if acc is pri:
                    continue
                if de(pri["hex"], acc["hex"]) < 0.1:
                    continue
                for acc2 in szines:
                    if acc2 is pri or acc2 is acc:
                        continue
                    if min(de(acc2["hex"], pri["hex"]), de(acc2["hex"], acc["hex"])) < 0.07:
                        continue
                    if hue_tav(oklch(acc2["hex"])[2], oklch(pri["hex"])[2]) < 25 and hue_tav(oklch(acc2["hex"])[2], oklch(acc["hex"])[2]) < 25:
                        continue
                    P = paletta_jelolt(kar, pri, acc, acc2, jel, sotet=(kar == st))
                    lista.append((pontoz(kar, P, dns, hu=(kar == hu)), P))
        lista.sort(key=lambda x: -x[0])
        eredmeny[kar] = lista[:60]
    # összeállítás: karakterenként a legjobb, ami a többitől elég távol van (kis kereséssel)
    sorrend = [hu] + [k for k in KARAKTEREK if k != hu]
    legjobb, legjobb_pont = None, -1e9
    for kuszob in (0.22, 0.16, 0.11, 0.0):
        def keres(i, valasztott, pont):
            nonlocal legjobb, legjobb_pont
            if i == len(sorrend):
                if pont > legjobb_pont:
                    legjobb, legjobb_pont = dict(valasztott), pont
                return
            kar = sorrend[i]
            n = 0
            for s, P in eredmeny[kar]:
                acc_hasznalat = sum(Q["_forras"]["accent"]["hex"] == P["_forras"]["accent"]["hex"] for Q in valasztott.values())
                if all(paletta_tav(P, Q) >= kuszob for Q in valasztott.values()) and acc_hasznalat < 2 and \
                   all(P["_forras"]["primary"]["hex"] != Q["_forras"]["primary"]["hex"] for Q in valasztott.values()):
                    valasztott[kar] = P
                    keres(i + 1, valasztott, pont + s)
                    del valasztott[kar]
                    n += 1
                    if n >= 6:
                        break
        keres(0, {}, 0.0)
        if legjobb:
            break
    out = []
    for kar in KARAKTEREK:
        P = legjobb[kar]
        f = P["_forras"]
        nev = f'{NEVEK[kar]} · {f["primary"]["nev"]} és {f["accent"]["nev"]}' + (" (sötét)" if P["mod"] == "sotet" else "")
        miert = (f'Fő szín: {f["primary"]["nev"]} ({f["primary"]["forras"]}), kiemelő: {f["accent"]["nev"]} '
                 f'({f["accent"]["forras"]}), apró díszekhez {f["accent2"]["nev"]}.')
        if kar == hu:
            miert += " Ez a mostani színek igényesebb változata."
        if P["mod"] == "sotet":
            miert += " Sötét alapon is működik (esti, prémium hangulat)."
        d = {"id": IDK[kar], "karakter": kar, "nev": nev, "miert": miert}
        d.update({k: P[k] for k in ("primary", "accent", "accent2", "paper", "ink", "deep", "card")})
        if P["mod"] == "sotet":
            d["mod"] = "sotet"
        d["_meres"] = ellenorzes(P)
        d["_forras"] = {k: (v["nev"] if v else None) for k, v in f.items()}
        out.append(d)
    return {"ajanlott": IDK[hu], "lista": out, "_hu": IDK[hu], "_sotet": IDK[st]}


# ------------------------------------------------------------------ ellenőrzés (a valtozatossag.py is ezt hívja)

def ellenoriz_lista(lista, talalt=()):
    """Hibák és figyelmeztetések az 5 palettára. talalt: a mostani oldal színei (a hű paletta ellenőrzéséhez)."""
    hiba, figy = [], []
    for p in lista:
        if not p.get("primary"):
            hiba.append(f'{p.get("id")}: nincs primary szín.')
            continue
        paper = p.get("paper") or ("#141816" if p.get("mod") == "sotet" else "#FBF8F2")
        ink = p.get("ink") or ("#F3EFE6" if p.get("mod") == "sotet" else "#222222")
        k1 = kontraszt(ink, paper)
        if k1 < 7:
            (hiba if k1 < 4.5 else figy).append(f'{p["id"]}: a szöveg és a papír kontrasztja {k1:.1f} (legalább 7 kell).')
        k2 = kontraszt(on(p["primary"]), p["primary"])
        if k2 < 3.6:
            hiba.append(f'{p["id"]}: a gombfelirat a fő színen nem olvasható ({k2:.1f}); sötétíts vagy világosíts a fő színen.')
    for p, q in itertools.combinations([x for x in lista if x.get("primary")], 2):
        d1 = de(p["primary"], q["primary"])
        if d1 < 0.06 and de(p.get("accent", p["primary"]), q.get("accent", q["primary"])) < 0.08:
            hiba.append(f'{p["id"]} és {q["id"]} szinte ugyanaz (fő szín ΔE {d1:.3f}): legyen más a fő vagy a kiemelő szín.')
    if not any(p.get("mod") == "sotet" or (p.get("paper") and lum(p["paper"]) < 0.08) for p in lista):
        hiba.append("Nincs sötét alapon működő paletta (egy legyen mod: sotet).")
    if talalt:
        if not any(min(de(p["primary"], t) for t in talalt) < 0.09 for p in lista if p.get("primary")):
            hiba.append("Nincs hű paletta: egyik fő szín sincs közel a mostani oldal színeihez.")
    szinesek = [oklch(p["primary"]) for p in lista if p.get("primary")]
    arnyalat_csoport = {round(h / 45) % 8 for L, C, h in szinesek if C > 0.04}
    if len(lista) >= 5 and len(arnyalat_csoport) < 3:
        figy.append("A fő színek árnyalata nagyon hasonló (3-nál kevesebb színcsalád).")
    return hiba, figy


def minta_kep(lista, ut):
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return
    W, H = 900, 110 * len(lista)
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    for i, p in enumerate(lista):
        y = i * 110
        d.rectangle([0, y, W, y + 110], fill=p["paper"])
        for j, k in enumerate(("primary", "accent", "accent2", "ink", "deep")):
            d.rectangle([20 + j * 120, y + 15, 120 + j * 120, y + 95], fill=p[k])
        d.text((640, y + 30), p["id"] + " " + p["nev"][:40], fill=p["ink"])
        d.text((640, y + 55), " ".join(f"{k}:{v}" for k, v in p["_meres"].items())[:46], fill=p["ink"])
    im.save(ut)


def main():
    ap = argparse.ArgumentParser(description="Paletta-generátor (OKLCH)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("javasol")
    j.add_argument("dns")
    j.add_argument("--ki")
    j.add_argument("--minta", help="PNG a palettákról (gyors átnézéshez)")
    e = sub.add_parser("ellenoriz")
    e.add_argument("arculat")
    a = ap.parse_args()
    if a.cmd == "javasol":
        dns = json.loads(Path(a.dns).read_text(encoding="utf-8"))
        res = javasol(dns)
        hiba, figy = ellenoriz_lista(res["lista"], [x["hex"] if isinstance(x, dict) else x
                                                     for x in (dns.get("ami_mar_megvan") or {}).get("szinek") or []])
        ki = Path(a.ki) if a.ki else Path(a.dns).with_name("paletta-javaslat.json")
        ki.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        for p in res["lista"]:
            print(f'{p["id"]} {p["nev"]:<52} {p["primary"]} {p["accent"]} {p["accent2"]} papír {p["paper"]} {p.get("mod", "")}  {p["_meres"]}')
        print(f'hű: {res["_hu"]} · sötét: {res["_sotet"]} · kiírva: {ki}')
        for x in hiba:
            print("  HIBA:", x)
        for x in figy:
            print("  figyelem:", x)
        if a.minta:
            minta_kep(res["lista"], a.minta)
    else:
        spec = json.loads(Path(a.arculat).read_text(encoding="utf-8"))
        lista = ((spec.get("opciok") or {}).get("paletta") or {}).get("lista") or []
        talalt = (spec.get("profil") or {}).get("talalt_szinek") or []
        hiba, figy = ellenoriz_lista(lista, talalt)
        for x in hiba:
            print("HIBA:", x)
        for x in figy:
            print("figyelem:", x)
        print("rendben" if not hiba else f"{len(hiba)} hiba")
        sys.exit(1 if hiba else 0)


if __name__ == "__main__":
    main()
