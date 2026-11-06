#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A közös tokenfájl (tokenek.json): a web fázis írja, a prezi és a videó fázis ebből örököl.

Használat (a munkamappában):
  python3 <SKILL>/scripts/tokenek.py arculat.json                          # jóváhagyás előtt: az ajánlott opciók
  python3 <SKILL>/scripts/tokenek.py arculat.json --valasztas valasztas.json --jovahagyva
  python3 <SKILL>/scripts/tokenek.py arculat.json --ttf                    # a betűk TTF-jei is (<munkamappa>/betuk/)
  python3 <SKILL>/scripts/tokenek.py arculat.json --ki /mashova/tokenek.json

A séma: references/tokenek-szerzodes.md. Minden útvonal az "alap" mappához (a munkamappához) képest relatív.
"""
import argparse
import datetime
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from motor import alap, epito  # noqa: E402

SZERZODES_VERZIO = 1
KOMPONENSEK = ("cim", "alcim", "gomb", "kartya", "foto", "mozgas")
TEMA_ELEMEK = {"textura": "felulet", "dekor": "dekor", "hatar": "hatar"}


def valasztott(v, kat, ajanlott):
    """A választott opció(k) id-je: ★ végleges, ha van; különben az ajánlott. Keverésnél lista."""
    x = ((v or {}).get("valasztas") or {}).get(kat) or {}
    veg = x.get("vegleges")
    if isinstance(veg, list) and veg:
        return veg
    return [veg] if veg else [ajanlott]


def keres(opc, kat, oid):
    return next((x for x in opc.get(kat, {}).get("lista", []) if x.get("id") == oid), None)


# ------------------------------------------------------------------ betűk

def suly_tartomany(tengely):
    """'wght@400..900' -> (400, 900, None); 'wght@400;700' -> (400, 700, [400, 700]); '' -> (400, 400, [400])."""
    if not tengely or "@" not in tengely:
        return 400, 400, [400]
    tengelyek, ertekek = tengely.split("@", 1)
    tengelyek = tengelyek.split(",")
    if "wght" not in tengelyek:
        return 400, 400, [400]
    i = tengelyek.index("wght")
    if ";" in ertekek:
        ws = [int(e.split(",")[i]) if "," in e else int(e) for e in ertekek.split(";")]
        return min(ws), max(ws), ws
    e = ertekek.split(",")[i]
    if ".." in e:
        a, b = e.split("..")
        return int(a), int(b), None
    return int(e), int(e), [int(e)]


def kozeli(w, tart):
    lo, hi, lista = tart
    if lista:
        return min(lista, key=lambda x: abs(x - w))
    return max(lo, min(hi, int(w)))


def ttf_letolt(csalad, sulyok, tengely, cel):
    """TTF-ek a Google Fonts-ról (ismeretlen kliensnek TTF-et ad, súlyonként egy fájl, teljes karakterkészlettel)."""
    q = "family=" + urllib.parse.quote_plus(csalad)
    if suly_tartomany(tengely) != (400, 400, [400]):
        q += ":wght@" + ";".join(str(w) for w in sorted(set(sulyok)))
    try:
        css = urllib.request.urlopen("https://fonts.googleapis.com/css2?" + q, timeout=25).read().decode("utf-8")
    except Exception as e:
        print(f"  ! {csalad}: a betű-CSS nem jött le ({e})")
        return []
    cel.mkdir(parents=True, exist_ok=True)
    utak = []
    for blokk in re.findall(r"@font-face\s*\{([^}]*)\}", css):
        w = re.search(r"font-weight:\s*(\d+)", blokk)
        u = re.search(r"url\((https://[^)]+\.ttf)\)", blokk)
        it = "italic" in blokk
        if not (w and u) or it:
            continue
        nev = f"{csalad.replace(' ', '')}-{w.group(1)}.ttf"
        p = cel / nev
        if not p.exists():
            try:
                p.write_bytes(urllib.request.urlopen(u.group(1), timeout=40).read())
            except Exception as e:
                print(f"  ! {nev}: letöltési hiba ({e})")
                continue
        utak.append(p)
    return utak


def betu_blokk(csalad, sulyok, kat, ttf_cel, alap_mappa):
    """sulyok[0] a fő súly (a címnél a cím vastagsága, a többinél 400), a többi a kiegészítő."""
    if not csalad:
        return None
    tengely = kat.get(csalad, "")
    tart = suly_tartomany(tengely)
    fo = kozeli(sulyok[0], tart)
    sulyok = sorted(set(kozeli(w, tart) for w in sulyok))
    b = {"csalad": csalad, "suly": fo, "sulyok": sulyok,
         "google_css": alap.google_fonts_url([csalad]), "ttf": []}
    if ttf_cel is not None:
        b["ttf"] = [str(p.relative_to(alap_mappa)) if alap_mappa in p.parents else str(p)
                    for p in ttf_letolt(csalad, sulyok, tengely, ttf_cel)]
    return b


# ------------------------------------------------------------------ formák (a választott CSS-ből)

def css_ertek(css, szelektor_re, prop):
    for m in re.finditer(r"([^{}]+)\{([^}]*)\}", css or ""):
        if re.search(szelektor_re, m.group(1).strip()):
            mm = re.search(r"(?:^|;)\s*" + re.escape(prop) + r"\s*:\s*([^;]+)", m.group(2))
            if mm:
                return mm.group(1).strip()
    return None


def px(v, alap_ertek):
    if not v:
        return alap_ertek
    m = re.match(r"([\d.]+)px", v)
    return float(m.group(1)) if m else alap_ertek


def forma(kartya, gomb):
    kc, gc = (kartya or {}).get("css", ""), (gomb or {}).get("css", "")
    tok_k, tok_g = (kartya or {}).get("tokenek") or {}, (gomb or {}).get("tokenek") or {}
    r_k = tok_k.get("r_kartya", px(css_ertek(kc, r"\.krt$", "border-radius"), 16))
    r_g = tok_g.get("r_gomb", px(css_ertek(gc, r"\.btn$", "border-radius"), 12))
    arny = css_ertek(kc, r"\.krt$", "box-shadow") or ""
    if "arnyek" in tok_k:
        arnyek = tok_k["arnyek"]
    elif not arny or arny == "none":
        arnyek = "nincs"
    elif "--sh-3" in arny or re.search(r"(^|,)\s*-?\d+px\s+-?\d+px\s+0(px)?\s", arny + " "):
        arnyek = "eros"
    else:
        arnyek = "lagy"
    keret = tok_k.get("keret_px")
    if keret is None:
        b = css_ertek(kc, r"\.krt$", "border") or ""
        m = re.match(r"([\d.]+)px", b) or re.search(r"inset 0 0 0 ([\d.]+)px", arny)
        keret = float(m.group(1)) if m else 0
    return {"r_kartya": r_k, "r_gomb": r_g, "arnyek": arnyek, "keret_px": keret}


# ------------------------------------------------------------------ fő

def svg_teljes(belso):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{belso}</svg>'


def rel(p, alap_mappa):
    p = Path(p)
    try:
        return str(p.relative_to(alap_mappa))
    except ValueError:
        return str(p)


def keszit(arculat_ut, valasztas_ut=None, jovahagyva=False, ttf=False):
    spec = epito.betolt(arculat_ut)
    alap_mappa = Path(spec["_alap"]).resolve()
    v = json.loads(Path(valasztas_ut).read_text(encoding="utf-8")) if valasztas_ut else None
    opc = epito.opciok(spec)
    kat = alap.betu_katalogus()
    vid = {k: valasztott(v, k, opc.get(k, {}).get("ajanlott")) for k in opc}

    # színek
    p = keres(opc, "paletta", vid["paletta"][0]) or {}
    t = alap.paletta_tokenek(p) if p.get("primary") else {}
    szinek = {"primary": p.get("primary"), "accent": t.get("--c-accent"), "accent2": t.get("--c-accent2"),
              "paper": t.get("--c-paper"), "card": t.get("--c-card"), "ink": t.get("--c-ink"),
              "deep": t.get("--c-deep"), "mod": "sotet" if p.get("mod") == "sotet" else "vilagos"}
    szinek_extra = {k.replace("--c-", "").replace("-", "_"): t[k] for k in (
        "--c-on-primary", "--c-on-accent", "--c-on-deep", "--c-primary-text", "--c-accent-text",
        "--c-ink-2", "--c-ink-3", "--c-line", "--c-tint", "--c-sand", "--c-hand") if k in t}

    # betűk
    b = keres(opc, "betu", vid["betu"][0]) or {}
    ttf_cel = (alap_mappa / "betuk") if ttf else None
    betuk = {
        "display": betu_blokk(b.get("display"), [b.get("w_display", 700), 400], kat, ttf_cel, alap_mappa),
        "body": betu_blokk(b.get("body"), [400, b.get("w_body_b", 700)], kat, ttf_cel, alap_mappa),
        "hand": betu_blokk(b.get("hand"), [400, 700], kat, ttf_cel, alap_mappa),
        "label": betu_blokk(b.get("label"), [400, 600], kat, ttf_cel, alap_mappa),
        "beallitas": {k: b[k] for k in ("w_display", "ls_display", "nagybetus", "lh_display", "hero_scale", "fs_hand")
                      if k in b},
        "nev": b.get("nev", ""),
    }

    # ikonok
    isp = epito.ikon_spec(spec)
    ikon = None
    if isp.get("stilusok"):
        sid = vid["ikon"][0]
        st = next((s for s in isp["stilusok"] if s["id"] == sid), isp["stilusok"][0])
        elotag = st.get("elotag", "")
        for k, c in (isp.get("szinek") or {}).items():
            elotag = elotag.replace("{" + k + "}", c)
        mappa = Path(isp["_mappa"]) / st["id"]
        fajlok = {ik["nev"]: rel(mappa / f'{ik["nev"]}.png', alap_mappa)
                  for ik in isp.get("ikonok", []) if (mappa / f'{ik["nev"]}.png').exists()}
        ikon = {"stilus_id": st["id"], "stilus_nev": st.get("nev", ""), "elotag": elotag,
                "technika": st.get("technika", ""), "mappa": rel(mappa, alap_mappa), "fajlok": fajlok,
                "temak": {ik["nev"]: ik.get("tema", "") for ik in isp.get("ikonok", [])},
                "spec": rel(Path(spec["_alap"]) / epito.g(spec, "ikonok", "spec"), alap_mappa)}

    # fotók
    fo = keres(opc, "foto", vid["foto"][0]) or {}
    valog, info = [], []
    for fid, f in (spec.get("fotok") or {}).items():
        if f.get("fajl") and f["fajl"] not in valog:
            valog.append(f["fajl"])
            info.append({"id": fid, "fajl": f["fajl"], "alt": f.get("alt", ""), "pozicio": f.get("pozicio", "50% 50%")})
    foto = {"kezeles": fo.get("nev", ""), "kezeles_id": fo.get("id"), "leiras": fo.get("miert") or fo.get("leiras", ""),
            "mappa": "bemenet/kepek", "valogatott": valog, "valogatott_info": info}

    # motívum + téma-elemek
    mot = spec.get("motivum") or {}
    motivum = {"formak_svg": {k: svg_teljes(s) for k, s in (mot.get("formak") or {}).items()}, "jel": mot.get("jel")}
    for kulcs, k in TEMA_ELEMEK.items():
        elemek = [keres(opc, k, i) for i in vid.get(k, [])]
        elemek = [{"id": e["id"], "nev": e.get("nev", ""), "leiras": e.get("miert") or e.get("leiras", "")}
                  for e in elemek if e]
        motivum[kulcs] = elemek[0] if len(elemek) == 1 else (elemek or None)
    for k in ("szellemszavak", "ticker", "matricak"):
        if mot.get(k):
            motivum[k] = mot[k]

    # logó
    lg = spec.get("logo") or {}
    szines = alap_mappa / "_logo_vagott.png"
    feher = alap_mappa / "_logo_feher.png"
    logo = {"szines": rel(szines, alap_mappa) if szines.exists() else lg.get("fajl"),
            "feher": rel(feher, alap_mappa) if feher.exists() else lg.get("feher_fajl")}

    # márka-diagnózis
    dns_ut = alap_mappa / "marka-dns.json"
    dns = json.loads(dns_ut.read_text(encoding="utf-8")) if dns_ut.exists() else {}
    hangnem = dns.get("hangnem") or ""
    if isinstance(hangnem, dict):
        hangnem = hangnem.get("leiras") or " ".join(str(x) for x in hangnem.values())

    m = spec.get("marka") or {}
    out = {
        "verzio": SZERZODES_VERZIO,
        "marka": {"nev": m.get("nev", ""), "slug": m.get("slug", ""), "url": m.get("url", ""), "szlogen": m.get("szlogen", "")},
        "szinek": szinek,
        "szinek_extra": szinek_extra,
        "betuk": betuk,
        "forma": forma(keres(opc, "kartya", vid["kartya"][0]), keres(opc, "gomb", vid["gomb"][0])),
        "ikon": ikon,
        "foto": foto,
        "motivum": motivum,
        "logo": logo,
        "hangnem": hangnem,
        "marka_dns": "marka-dns.json" if dns_ut.exists() else None,
        "komponensek": {k: {"id": x["id"], "nev": x.get("nev", ""), "leiras": x.get("miert") or x.get("leiras", "")}
                        for k in KOMPONENSEK for x in [keres(opc, k, vid.get(k, [None])[0])] if x},
        "allapot": {"web_verzio": spec.get("verzio", 1), "forras": "valasztott" if v else "ajanlott",
                    "jovahagyva": bool(jovahagyva or (v or {}).get("jovahagyva")),
                    "datum": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")},
        "alap": str(alap_mappa),
    }
    return out


def main():
    ap = argparse.ArgumentParser(description="tokenek.json a web fázis eredményéből")
    ap.add_argument("arculat")
    ap.add_argument("--valasztas", help="valasztas.json (a választó gépi adata); nélküle az ajánlott opciók")
    ap.add_argument("--jovahagyva", action="store_true", help="a web fázis jóvá van hagyva")
    ap.add_argument("--ttf", action="store_true", help="a betűk TTF-jeit is letölti a <munkamappa>/betuk/ mappába")
    ap.add_argument("--ki", help="kimenet (alap: <munkamappa>/tokenek.json)")
    a = ap.parse_args()
    out = keszit(a.arculat, a.valasztas, a.jovahagyva, a.ttf)
    ki = Path(a.ki) if a.ki else Path(out["alap"]) / "tokenek.json"
    ki.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    s, b = out["szinek"], out["betuk"]
    print(f"tokenek.json kész: {ki}")
    print(f"  színek: {s['primary']} / {s['accent']} / {s['accent2']} · papír {s['paper']} · tinta {s['ink']} · {s['mod']}")
    print("  betűk: " + " + ".join(x["csalad"] for x in (b["display"], b["body"], b["hand"], b["label"]) if x))
    if out["ikon"]:
        print(f"  ikon: {out['ikon']['stilus_nev']} ({len(out['ikon']['fajlok'])} fájl)")
    print(f"  forma: {out['forma']} · forrás: {out['allapot']['forras']}, jóváhagyva: {out['allapot']['jovahagyva']}")


if __name__ == "__main__":
    main()
