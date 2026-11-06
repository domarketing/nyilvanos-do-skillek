#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prezi.py - az AI arculat-generátor prezentációs fázisa (hordozható: Mac, Windows, Linux; DO!-függőség nélkül).

  python3 prezi.py tema <munkamappa> [--valasztas A,B,...]
        -> prezi/prezi-tema.json a jóváhagyott tokenek.json-ból (ajánlott változatokkal), a betűk letöltése és telepítése

  python3 prezi.py valaszto <munkamappa> [--verzio 2] [--elozo prezi-valasztas.json]
        -> a 10 kategória × 5 változat képei, a 12 diás minta-deck, prezi/prezi-toredek.html (az arculat-központ
           Prezentáció füle) és prezi/prezi-valaszto.html (önálló teszt). Tartalom: prezi/tartalom.json.

  python3 prezi.py valasztas <munkamappa> <prezi-valasztas.json> [--jovahagyva]
        -> a választó döntései (a gépi adat: ArtifactData arculat/prezi-v<n> 'gepi' mezője) a prezi-tema.json-ba

  python3 prezi.py minta <munkamappa>
        -> prezi/minta-deck.pptx + PDF + PNG a téma mostani választásaival (a jóváhagyás után ez a végleges)

  python3 prezi.py deck <vazlat.json> [--tema <munkamappa>/prezi/prezi-tema.json] [--ki deck.pptx] [--png] [--felulir]
        -> új prezentáció egy vázlatból (diák listája, a diatípusok: references/prezi/minta-diak.md), védett mentéssel

  python3 prezi.py ellenoriz <deck.pptx> [--tema ...]
        -> PDF + gépi ellenőrzés: idegen betű, kilógó és egymásra csúszott szöveg

  python3 prezi.py csomag <munkamappa> <célmappa>
        -> önálló prezi-csomag (a márka-skillbe): prezi-tema.json, a motor (motor/), betűk, ikonok, fotók, logó,
           PREZI-ARCULAT.md, minta-deck.pdf. Utána: python3 <célmappa>/motor/prezi.py deck vazlat.json --tema <célmappa>/prezi-tema.json

  python3 prezi.py leiras <munkamappa>
        -> prezi/PREZI-ARCULAT.md (a választott layoutok, a szabályok, „így kérj új prezentációt”)

  python3 prezi.py betuk <munkamappa>
        -> a téma betűinek letöltése és telepítése (a PowerPoint és a LibreOffice is csak a telepített betűt látja)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import alap as a  # noqa: E402
import betuk  # noqa: E402
import diak  # noqa: E402
import katalogus as K  # noqa: E402
import render  # noqa: E402
import leiras  # noqa: E402
import tema as tm  # noqa: E402


def arg(nev, alap=None):
    v = sys.argv
    return v[v.index(nev) + 1] if nev in v and v.index(nev) + 1 < len(v) else alap


def _tema_ut(munkamappa):
    return Path(munkamappa).resolve() / "prezi" / "prezi-tema.json"


def cmd_tema(mm):
    valasztas = None
    if arg("--valasztas"):
        ids = arg("--valasztas").split(",")
        valasztas = {k: v.strip().upper() for (k, _, _), v in zip(K.KATEGORIAK, ids) if v.strip()}
    t = tm.keszit(mm)
    if valasztas:
        t["valasztas"].update(valasztas)
    ut = tm.ment(t, _tema_ut(mm))
    print("KÉSZ:", ut)
    print("  betűk a dián: " + ", ".join("%s %s (%d)" % (k, b["typeface"], b.get("suly_dian", 400)) for k, b in t["betuk"].items()))
    for k, b in t["betuk"].items():
        if b.get("figyelem"):
            print("  ! " + b["figyelem"])
    print("  ajánlott: " + ", ".join("%s=%s" % (k, v) for k, v in t["ajanlott"].items()))
    if not t["forras"]["web_jovahagyva"]:
        print("  ! a webes arculat még nincs jóváhagyva: ez csak előnézet (8. alapszabály)")
    print("  + " + str(leiras.iras(mm)))


def cmd_valasztas(mm, ut):
    """A választó gépi adatából a téma választásai (vegleges, ha van; különben az ajánlott)."""
    tu = _tema_ut(mm)
    t = json.loads(tu.read_text(encoding="utf-8"))
    raw = Path(ut).read_text(encoding="utf-8").strip()
    if "GÉPI ADAT" in raw:
        raw = raw.split("GÉPI ADAT", 1)[1]
        raw = raw[raw.index("{"):]
    g = json.loads(raw)
    if isinstance(g.get("gepi"), str):
        g = json.loads(g["gepi"])
    val = g.get("valasztas") or {}
    for k, v in val.items():
        if v.get("vegleges"):
            t["valasztas"][k] = v["vegleges"]
    if "--jovahagyva" in sys.argv or g.get("jovahagyva"):
        t["jovahagyva"] = True
    t["megjegyzesek"] = {k: v.get("megjegyzesek") for k, v in val.items() if v.get("megjegyzesek")}
    t["ujakat"] = [k for k, v in val.items() if v.get("ujakat")]
    t["altalanos_megjegyzes"] = g.get("altalanos", "")
    tm.ment(t, tu)
    print("KÉSZ: " + ", ".join("%s=%s" % (k, v) for k, v in t["valasztas"].items()))
    if t["ujakat"]:
        print("  új változatokat kér: " + ", ".join(t["ujakat"]))
    for k, m in t["megjegyzesek"].items():
        for i, x in m.items():
            print("  megjegyzés %s/%s: %s" % (k, i, x))
    if t.get("altalanos_megjegyzes"):
        print("  általános: " + t["altalanos_megjegyzes"])
    print("  + " + str(leiras.iras(mm)))


def cmd_minta(mm):
    import valaszto
    pm = Path(mm).resolve() / "prezi"
    T = tm.bekapcsol(tm.betolt(pm / "prezi-tema.json"))
    t = json.loads((pm / "tartalom.json").read_text(encoding="utf-8"))
    valaszto.minta_deck(T, t, pm / "minta-deck.pptx")
    pdf = render.pdf(pm / "minta-deck.pptx", pm / "minta-deck.pdf")
    kepek = render.kepek(pdf, pm / "minta-deck", szel=1600, fmt="png")
    hibak = valaszto._ellenor(pdf, T, "minta-deck")
    print("KÉSZ: %s (+ PDF, %d PNG a minta-deck/ mappában)" % (pm / "minta-deck.pptx", len(kepek)))
    for h in hibak:
        print("  ! " + h)
    print("  + " + str(leiras.iras(mm)))


def cmd_deck(vazlat_ut):
    import mentes
    v = json.loads(Path(vazlat_ut).read_text(encoding="utf-8"))
    tema_ut = arg("--tema") or v.get("tema")
    if not tema_ut:
        raise SystemExit("Add meg a témát: --tema <munkamappa>/prezi/prezi-tema.json (vagy a vázlatban: \"tema\").")
    tema_ut = Path(tema_ut) if Path(tema_ut).is_absolute() else (Path(vazlat_ut).parent / tema_ut)
    T = tm.bekapcsol(tm.betolt(tema_ut))
    if not T.d.get("jovahagyva"):
        print("  ! a prezentációs arculat még nincs jóváhagyva (a téma ajánlott választásaival készül)")
    prs = a.new_prs()
    for i, d in enumerate(v.get("diak") or [], 1):
        try:
            diak.dia(prs, d)
        except Exception as ex:
            raise SystemExit("A(z) %d. dia (%s) nem készült el: %s" % (i, d.get("tipus"), ex))
    ki = Path(arg("--ki") or v.get("ki") or Path(vazlat_ut).with_suffix(".pptx"))
    if not ki.is_absolute():
        ki = Path(vazlat_ut).parent / ki
    mentes.ment(prs, ki, felulir="--felulir" in sys.argv)
    if "--png" in sys.argv or "--ellenoriz" in sys.argv:
        cmd_ellenoriz(ki, T)


def cmd_ellenoriz(pptx, T=None):
    import valaszto
    pptx = Path(pptx)
    if T is None:
        tu = arg("--tema")
        if not tu:
            raise SystemExit("Add meg a témát: --tema <munkamappa>/prezi/prezi-tema.json")
        T = tm.bekapcsol(tm.betolt(tu))
    pdf = render.pdf(pptx, pptx.parent / "pdf" / (pptx.stem + ".pdf"))
    kepek = render.kepek(pdf, pptx.parent / "png" / pptx.stem, szel=1600, fmt="png")
    hibak = valaszto._ellenor(pdf, T, pptx.stem)
    print("PDF: %s · %d PNG: %s" % (pdf, len(kepek), kepek[0].parent if kepek else "-"))
    if hibak:
        for h in hibak:
            print("  ! " + h)
    else:
        print("  ellenőrzés: rendben (a téma betűi, nincs kilógó és egymásra csúszott szöveg)")


def cmd_csomag(mm, cel):
    """A jóváhagyott prezi-téma önálló csomagként (a márka-skillbe): minden útvonal a csomag mappájához relatív."""
    import shutil
    mm = Path(mm).resolve()
    cel = Path(cel).resolve()
    t = json.loads(_tema_ut(mm).read_text(encoding="utf-8"))
    for al in ("betuk", "ikonok", "fotok", "logo", "motor"):
        (cel / al).mkdir(parents=True, exist_ok=True)

    def mas(rel, al):
        if not rel:
            return rel
        src = Path(rel) if Path(rel).is_absolute() else mm / rel
        if not src.exists():
            return None
        dst = cel / al / src.name
        shutil.copyfile(src, dst)
        return "%s/%s" % (al, src.name)
    for b in t["betuk"].values():
        b["ttf"] = mas(b["ttf"], "betuk")
        b["ttf_b"] = mas(b["ttf_b"], "betuk")
    t["ikon"]["fajlok"] = {n: mas(p, "ikonok") for n, p in (t["ikon"].get("fajlok") or {}).items()}
    t["ikon"]["fajlok"] = {n: p for n, p in t["ikon"]["fajlok"].items() if p}
    t["ikon"]["mappa"] = "ikonok"
    for f in t.get("fotok") or []:
        f["fajl"] = mas(f.get("fajl"), "fotok")
    t["fotok"] = [f for f in t.get("fotok") or [] if f.get("fajl")]
    t["logo"] = {k: mas(v, "logo") for k, v in (t.get("logo") or {}).items() if v}
    t["alap_rel"] = "."
    (cel / "prezi-tema.json").write_text(json.dumps(t, ensure_ascii=False, indent=2), encoding="utf-8")
    here = Path(__file__).resolve().parent
    for f in list(here.glob("*.py")) + [here / "arcok.swift"]:
        if f.exists():
            shutil.copyfile(f, cel / "motor" / f.name)
    for nev in ("PREZI-ARCULAT.md", "minta-deck.pdf", "tartalom.json"):
        if (mm / "prezi" / nev).exists():
            shutil.copyfile(mm / "prezi" / nev, cel / nev)
    print("KÉSZ: %s" % cel)
    print("  új prezi: python3 %s deck vazlat.json --tema %s --png" % (cel / "motor" / "prezi.py", cel / "prezi-tema.json"))


def cmd_betuk(mm):
    t = json.loads(_tema_ut(mm).read_text(encoding="utf-8"))
    alap_mappa = Path(mm).resolve()
    utak = [str(alap_mappa / b[k]) for b in t["betuk"].values() for k in ("ttf", "ttf_b")]
    uj = betuk.telepit(utak)
    print("betűk: %s" % ("telepítve: " + ", ".join(p.name for p in uj) if uj else "mind telepítve volt"))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    mod = sys.argv[1]
    if mod == "tema":
        cmd_tema(sys.argv[2])
    elif mod == "valaszto":
        import valaszto
        elozo = None
        if arg("--elozo"):
            elozo = json.loads(Path(arg("--elozo")).read_text(encoding="utf-8"))
            if isinstance(elozo.get("gepi"), str):
                elozo = json.loads(elozo["gepi"])
        valaszto.epit(sys.argv[2], verzio=int(arg("--verzio", 1)), elozo=elozo)
    elif mod == "valasztas":
        cmd_valasztas(sys.argv[2], sys.argv[3])
    elif mod == "minta":
        cmd_minta(sys.argv[2])
    elif mod == "deck":
        cmd_deck(sys.argv[2])
    elif mod == "ellenoriz":
        cmd_ellenoriz(sys.argv[2])
    elif mod == "betuk":
        cmd_betuk(sys.argv[2])
    elif mod == "leiras":
        print(leiras.iras(sys.argv[2]))
    elif mod == "csomag":
        cmd_csomag(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
