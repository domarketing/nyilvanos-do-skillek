#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Öt betűpár-javaslat a márka-diagnózisból, a teljes ékezetbiztos katalógusból (references/betuk.json).

  python3 betu_valaszto.py marka-dns.json [--paletta paletta-javaslat.json] [--ki betu-javaslat.json] [--top 4]

Karakterenként (elegáns, modern, merész, barátságos, klasszikus) pontoz: a karakter-illeszkedés (k5), a formanyelvi
tengelyek (ax) és a szakma témái alapján. A túlhasznált kedvencek (Fraunces, Playfair Display, DM Serif Display,
Bricolage Grotesque, Outfit) pontlevonást kapnak: csak akkor kerülhetnek be, ha az arculat.json-ban
„kedvenc_indoklas” mondja meg, miért éppen ennek az ügyfélnek kellenek. Az ügyfél saját betűje a hű karakternél bónuszt
kap. Kimenet: kész "opciok.betu" vázlat + karakterenként 3 másik jelölt, hogy cserélni tudj.
"""
import argparse
import itertools
import json
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
KARAKTEREK = ("elegans", "modern", "meresz", "baratsagos", "klasszikus")
IDK = {"elegans": "bE", "modern": "bM", "meresz": "bB", "baratsagos": "bF", "klasszikus": "bK"}
NEVEK = {"elegans": "Elegáns", "modern": "Modern", "meresz": "Merész", "baratsagos": "Barátságos", "klasszikus": "Klasszikus"}
CIM_OSZTALY = {"serif", "sans", "slab", "display", "kerek", "keskeny"}
SZEREP_OSZTALY = {"cim-serif": "serif", "szoveg-serif": "serif", "cim-sans": "sans", "szoveg-sans": "sans", "cim-slab": "slab",
                  "cim-display": "display", "cim-kerek": "kerek", "szoveg-kerek": "kerek", "cim-keskeny": "keskeny",
                  "kez": "kez", "kez-script": "script", "cimke-mono": "mono", "egyeb": "egyeb", "tiltott-reflex": "sans"}
KEDVENC = {"Fraunces", "Playfair Display", "DM Serif Display", "Bricolage Grotesque", "Outfit"}
# a cím súlya karakterenként (a betű elérhető súlyaihoz igazítva)
SULY = {"elegans": 500, "modern": 650, "meresz": 850, "baratsagos": 650, "klasszikus": 600}


def katalogus():
    d = json.loads((SKILL / "references" / "betuk.json").read_text(encoding="utf-8"))
    out = []
    for b in d["betuk"]:
        if b.get("ellenorizve") is False:
            continue
        b = dict(b)
        b.setdefault("osztaly", SZEREP_OSZTALY.get(b.get("szerep"), "egyeb"))
        if "szerepek" not in b:
            sz = b.get("szerep", "")
            b["szerepek"] = (["display"] if sz.startswith("cim") or sz == "egyeb" else []) + \
                            (["body"] if sz.startswith("szoveg") else []) + (["hand"] if sz.startswith("kez") else []) + \
                            (["label"] if sz == "cimke-mono" else [])
        b.setdefault("kedvenc", b["csalad"] in KEDVENC)
        b.setdefault("tiltott", b.get("szerep") == "tiltott-reflex")
        out.append(b)
    return out


def illeszkedes(ax, dax):
    kozos = [k for k in (ax or {}) if k in dax]
    if not kozos:
        return 0.5
    return 1 - sum(abs(ax[k] - dax[k]) for k in kozos) / len(kozos)


def pont(b, kar, dns, blob, sajat, hu):
    s = 1.6 * (b.get("k5") or {}).get(kar, 1) / 3 + 1.4 * illeszkedes(b.get("ax"), dns.get("formanyelv") or {})
    s += 0.25 * sum(1 for t in b.get("temak") or [] if t.lower() in blob)
    s -= 1.2 if b.get("kedvenc") else 0
    if b["csalad"] in sajat:
        s += 1.0 if kar == hu else 0.2
    return s


def suly_tartomany(tengely):
    if not tengely or "@" not in tengely:
        return 400, 400, [400]
    ax, ert = tengely.split("@", 1)
    ax = ax.split(",")
    if "wght" not in ax:
        return 400, 400, [400]
    i = ax.index("wght")
    if ";" in ert:
        ws = [int(e.split(",")[i]) if "," in e else int(e) for e in ert.split(";")]
        return min(ws), max(ws), ws
    e = ert.split(",")[i]
    if ".." in e:
        a, b = e.split("..")
        return int(a), int(b), None
    return int(e), int(e), [int(e)]


def kozeli(w, tengely):
    lo, hi, lista = suly_tartomany(tengely)
    if lista:
        return min(lista, key=lambda x: abs(x - w))
    return int(max(lo, min(hi, round(w / 50) * 50)))


def javasol(dns, hu=None, top=6):
    kat = katalogus()
    blob = json.dumps(dns, ensure_ascii=False).lower()
    sajat = set((dns.get("ami_mar_megvan") or {}).get("betuk") or [])
    hu = hu or dns.get("hu_karakter") or "baratsagos"

    def jo(b, szerep):
        if szerep not in b["szerepek"]:
            return False
        if b.get("tiltott") and b["csalad"] not in sajat:
            return False
        return True

    disp = {k: sorted([b for b in kat if jo(b, "display") and b["osztaly"] in CIM_OSZTALY],
                      key=lambda b: -pont(b, k, dns, blob, sajat, hu))[:top] for k in KARAKTEREK}
    body = {k: sorted([b for b in kat if jo(b, "body")], key=lambda b: -pont(b, k, dns, blob, sajat, hu))[:5] for k in KARAKTEREK}
    hand = {k: sorted([b for b in kat if jo(b, "hand")], key=lambda b: -pont(b, k, dns, blob, sajat, hu))[:4] for k in KARAKTEREK}
    label = {k: sorted([b for b in kat if jo(b, "label")], key=lambda b: -pont(b, k, dns, blob, sajat, hu))[:4] for k in KARAKTEREK}

    # címbetűk: globálisan a legjobb ötös (különböző családok, legalább 3 osztály)
    legjobb, lp = None, -1e9
    for kombo in itertools.product(*(disp[k] for k in KARAKTEREK)):
        nevek = [b["csalad"] for b in kombo]
        if len(set(nevek)) < 5 or len({b["osztaly"] for b in kombo}) < 3:
            continue
        p = sum(pont(b, k, dns, blob, sajat, hu) for b, k in zip(kombo, KARAKTEREK))
        if p > lp:
            legjobb, lp = kombo, p
    if legjobb is None:
        legjobb = tuple(disp[k][0] for k in KARAKTEREK)

    out, hasznalt = [], {"body": [], "hand": [], "label": []}
    for k, d in zip(KARAKTEREK, legjobb):
        def valaszt(jeloltek, szerep, kerul_osztaly=None):
            jel = [b for b in jeloltek if b["csalad"] != d["csalad"]]
            if kerul_osztaly:   # szövegbetű: lehetőleg más osztály, mint a cím (kontraszt)
                jel = sorted(jel, key=lambda b: (b["osztaly"] == kerul_osztaly and d["osztaly"] in ("serif", "slab")))
            for b in jel:
                if b["csalad"] not in hasznalt[szerep]:
                    hasznalt[szerep].append(b["csalad"])
                    return b
            return jel[0] if jel else None
        bo = valaszt(body[k], "body", kerul_osztaly="serif")
        ha = valaszt(hand[k], "hand")
        la = valaszt(label[k], "label")
        w = kozeli(SULY[k], d.get("tengely", ""))
        keskeny = d["osztaly"] == "keskeny"
        x = {"id": IDK[k], "karakter": k, "nev": f"{NEVEK[k]} · {d['csalad']} és {bo['csalad'] if bo else ''}",
             "display": d["csalad"], "body": bo["csalad"] if bo else None, "hand": ha["csalad"] if ha else None,
             "label": la["csalad"] if la else None, "w_display": w,
             "ls_display": "0.01em" if keskeny else ("-0.01em" if k in ("elegans", "klasszikus") else "-0.02em"),
             "lh_display": 1.0 if keskeny else 1.06, "nagybetus": bool(keskeny),
             "hero_scale": 1.12 if (keskeny or w <= 450) else 1.0,
             "fs_hand": 1.4 if (ha and ha.get("osztaly") == "script") else 1.2,
             "miert": f"Cím: {d['csalad']} ({d.get('karakter', '').split(';')[0]}). "
                      f"Szöveg: {bo['csalad'] if bo else '-'}. Kézírás: {ha['csalad'] if ha else '-'}. "
                      f"Címke: {la['csalad'] if la else '-'}.",
             "_pont": round(pont(d, k, dns, blob, sajat, hu), 2),
             "_mas_cimbetu": [b["csalad"] for b in disp[k] if b["csalad"] != d["csalad"]][:3]}
        if d.get("kedvenc"):
            x["kedvenc_indoklas"] = ""
        out.append(x)
    return out


def main():
    ap = argparse.ArgumentParser(description="Betűpár-javaslat a katalógusból")
    ap.add_argument("dns")
    ap.add_argument("--paletta")
    ap.add_argument("--ki")
    ap.add_argument("--top", type=int, default=6)
    a = ap.parse_args()
    dns = json.loads(Path(a.dns).read_text(encoding="utf-8"))
    hu = None
    if a.paletta:
        pj = json.loads(Path(a.paletta).read_text(encoding="utf-8"))
        hu = next((p["karakter"] for p in pj.get("lista", []) if p["id"] == pj.get("_hu")), None)
    lista = javasol(dns, hu, a.top)
    ki = Path(a.ki) if a.ki else Path(a.dns).with_name("betu-javaslat.json")
    ki.write_text(json.dumps({"ajanlott": IDK.get(hu or "baratsagos"), "lista": lista}, ensure_ascii=False, indent=2),
                  encoding="utf-8")
    for x in lista:
        print(f'{x["id"]} {x["display"]:<22} + {str(x["body"]):<18} + {str(x["hand"]):<20} + {str(x["label"]):<16} '
              f'w{x["w_display"]}  pont {x["_pont"]}  (más cím: {", ".join(x["_mas_cimbetu"])})')
    if any("kedvenc_indoklas" in x for x in lista):
        print("Figyelem: kedvenc betű került be; írj kedvenc_indoklas-t, vagy cseréld a „más cím” listából.")
    print(f"kiírva: {ki}")


if __name__ == "__main__":
    main()
