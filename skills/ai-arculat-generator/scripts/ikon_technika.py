#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Öt ikonstílus-javaslat a márka-diagnózisból, a technika-szótárból (references/ikon-technikak.json).

  python3 ikon_technika.py marka-dns.json [--paletta paletta-javaslat.json] [--ki ikon-javaslat.json]

Karakterenként (elegáns, modern, merész, barátságos, klasszikus) a legjobban illő technikát adja, öt KÜLÖNBÖZŐ
családból, a régi fix készletből legfeljebb egyet. A kimenet az ikon-spec.json "stilusok" vázlata: a promptot
(elotag) neked kell az ügyfélre csavarni (anyag, nézőpont, rajzmód a tárgyi világából), mielőtt generálsz.
"""
import argparse
import json
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
KARAKTEREK = ("elegans", "modern", "meresz", "baratsagos", "klasszikus")
IDK = {"elegans": "iE", "modern": "iM", "meresz": "iB", "baratsagos": "iF", "klasszikus": "iK"}
NEVEK = {"elegans": "Elegáns", "modern": "Modern", "meresz": "Merész", "baratsagos": "Barátságos", "klasszikus": "Klasszikus"}
# magyar kulcsszavak: ha a diagnózis szövegében szerepelnek, az a technika közelebb áll az ügyfél mostani képi világához
KULCS = {
    "ceruzaskicc": ["ceruza", "skicc", "grafit", "rajz"], "tervrajz": ["alaprajz", "tervrajz", "kertterv", "műszaki", "építész"],
    "akvarell": ["akvarell", "festmény", "festett"], "herbarium": ["herbárium", "préselt", "botanik", "növény"],
    "linometszet": ["linó", "metszet", "nyomda"], "himzes": ["hímzés", "textil", "varr", "kötött"],
    "keramia": ["kerámia", "agyag", "fazekas", "bögre"], "intarzia": ["asztalos", "faipar", "bútor"],
    "olommuveg": ["üveg", "templom", "vitrázs"], "cianotipia": ["cianotípia", "kéknyomat", "botanik"],
    "pecset": ["pecsét", "bélyegző", "hivatal", "jog"], "zomanc": ["jelvény", "kitűző", "egyesület"],
    "pixel": ["játék", "gamer", "retró gép"], "neon": ["bár", "klub", "éjszak"], "zsirkreta": ["óvoda", "gyerek", "iskola"],
    "metszet": ["tudomány", "antik", "régiség", "atlasz"], "papirkivagas": ["papír", "kézműves"],
    "mozaik": ["csempe", "fürdő", "mozaik"], "tus_ecset": ["kalligráf", "tus", "japán"], "origami": ["papír", "hajtogat"],
}


def szoveg(dns):
    return json.dumps(dns, ensure_ascii=False).lower()


def illeszkedes(ax, dax):
    kozos = [k for k in ax if k in dax]
    if not kozos:
        return 0.5
    return 1 - sum(abs(ax[k] - dax[k]) for k in kozos) / len(kozos)


def pontoz(t, kar, dns, blob):
    s = 1.6 * t["k5"].get(kar, 0) / 3 + 1.4 * illeszkedes(t["ax"], dns.get("formanyelv") or {})
    s += 0.6 * any(k in blob for k in KULCS.get(t["id"], []))
    s -= 0.5 * t.get("regi", False)
    return s


def javasol(dns, hu=None):
    """Globális keresés: karakterenként a 8 legjobb technika közül az az ötös, aminek az összpontszáma a legnagyobb,
    úgy, hogy egy családból legfeljebb kettő, legalább 3 különböző család, a régi készletből legfeljebb egy legyen,
    és a formanyelvhez nagyon nem illő technika (illeszkedés < 0.55) ne kerüljön be."""
    import itertools
    tech = json.loads((SKILL / "references" / "ikon-technikak.json").read_text(encoding="utf-8"))["technikak"]
    blob = szoveg(dns)
    dax = dns.get("formanyelv") or {}
    jel = {}
    for kar in KARAKTEREK:
        ok = [t for t in tech if illeszkedes(t["ax"], dax) >= 0.55] or tech
        jel[kar] = sorted(ok, key=lambda t: -pontoz(t, kar, dns, blob))[:8]
    legjobb, lp = None, -1e9
    for kombo in itertools.product(*(jel[k] for k in KARAKTEREK)):
        ids = [t["id"] for t in kombo]
        if len(set(ids)) < 5:
            continue
        cs = [t["csalad"] for t in kombo]
        if max(cs.count(c) for c in cs) > 2 or len(set(cs)) < 3 or sum(t.get("regi", False) for t in kombo) > 1:
            continue
        pont = sum(pontoz(t, k, dns, blob) for t, k in zip(kombo, KARAKTEREK))
        if pont > lp:
            legjobb, lp = kombo, pont
    out = []
    for kar, t in zip(KARAKTEREK, legjobb):
        out.append({"id": IDK[kar], "karakter": kar, "nev": f'{NEVEK[kar]} · {t["nev"].lower()}', "technika": t["id"],
                    "csalad": t["csalad"], "elotag": t["prompt"], "csavar": "",
                    "_pont": round(pontoz(t, kar, dns, blob), 2),
                    "_tobbi": [x["id"] for x in jel[kar] if x["id"] != t["id"]][:3]})
    return out


def main():
    ap = argparse.ArgumentParser(description="Ikonstílus-javaslat a technika-szótárból")
    ap.add_argument("dns")
    ap.add_argument("--paletta", help="paletta-javaslat.json (a hű karakterhez)")
    ap.add_argument("--ki")
    a = ap.parse_args()
    dns = json.loads(Path(a.dns).read_text(encoding="utf-8"))
    hu = None
    if a.paletta:
        pj = json.loads(Path(a.paletta).read_text(encoding="utf-8"))
        hu = next((p["karakter"] for p in pj.get("lista", []) if p["id"] == pj.get("_hu")), None)
    lista = javasol(dns, hu)
    ki = Path(a.ki) if a.ki else Path(a.dns).with_name("ikon-javaslat.json")
    ki.write_text(json.dumps({"stilusok": lista}, ensure_ascii=False, indent=2), encoding="utf-8")
    for s in lista:
        print(f'{s["id"]} {s["nev"]:<34} család: {s["csalad"]:<9} pont {s["_pont"]}  (még jó lenne: {", ".join(s["_tobbi"])})')
    print(f"kiírva: {ki}\nKövetkező lépés: minden stílus 'elotag'-ját egészítsd ki egy ügyfélre írt mondattal "
          "(anyag, nézőpont, rajzmód a tárgyi világából), és ezt írd a 'csavar' mezőbe is.")


if __name__ == "__main__":
    main()
