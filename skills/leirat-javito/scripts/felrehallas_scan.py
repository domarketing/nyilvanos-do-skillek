#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kész leirat átfésülése félrehallásokra és nyers feliratmaradványokra.
Nem javít automatikusan, csak listáz: sor, talált alak, javaslat.

A keresett alakok két helyről jönnek:
  1. a szótárból (alapból a skill references/szotar.md fájlja): minden táblázatsor,
     ahol a második oszlopban „idézőjeles” félrehallott alak áll. Ha az alak után
     kérdőjel áll („mék”?), FIGYELJ szinten jelez, egyébként HIBA szinten;
  2. a beépített általános listából: gyakori magyar feliratozási hibák,
     gyakran félrehallott szoftvernevek, nyers maradványok.

Használat:
  python felrehallas_scan.py leirat.md
  python felrehallas_scan.py leirat.md --szotar leirat-szotar.md   # még egy szótár (ismételhető)
  python felrehallas_scan.py leirat.md --szotar-nelkul             # csak a beépített lista
  python felrehallas_scan.py leirat.md --csak-hiba                 # a FIGYELJ tételek nélkül

HIBA = biztosan rossz, FIGYELJ = lehet jó is, nézd meg.
"""
import argparse
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):  # Windows-konzolon (cp1250) is jó ékezet és nyíl
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

HIBA, FIGYELJ = "HIBA", "FIGYELJ"
ALAP_SZOTAR = Path(__file__).resolve().parent.parent / "references" / "szotar.md"

# (regex, javaslat, szint): a regex kis-nagybetű-érzéketlen, hacsak (?-i) nincs benne
ALTALANOS = [
    # --- gyakran félrehallott szoftverek, eszközök
    (r"\b(?:cl[óo]d|cló|cloud)\s*k[óo]d\w*|\bchrome\s*kód", "Claude Code", HIBA),
    (r"\b(?:cl[óo]d|cló)\w*(?!\w)(?!\s*k[óo]d)", "Claude (toldalékkal: Claude-dal, Claude-ot)", HIBA),
    (r"\bcloud(?:-?dal|-?ot|-?nak|-?ba|-?ban|-?os|-?ról)\b", "Claude (-dal/-ot/-nak…), ha a Claude-ról van szó", FIGYELJ),
    (r"\bentropic", "Anthropic", HIBA),
    (r"\bcs[ae]gyipiti\w*|\bcseh\s+gpt\w*", "ChatGPT", HIBA),
    (r"\bnotebook\s+elem", "NotebookLM", HIBA),
    (r"\bwhisper\s*flow|\bvisper\s*flow|\bviszperf[óo]\w*", "Wispr Flow (diktálóprogram; a Whisper más)", HIBA),
    (r"\bhen\s+vide|\bhagen\b", "HeyGen", HIBA),
    (r"\bhiggs[- ](?:f[eé]ld|field|füld)\w*|\bhiggsf(?:éld|eld|üld)\w*", "Higgsfield", HIBA),
    (r"\bsz[ée]sz\s*aut[óo]p\w*|\bszeas\s*autop\w*", "SalesAutopilot", HIBA),
    (r"\bm[ée]k(?:et|en|es|kel|ről|re)?\b", "Make (automatizáló szoftver)", FIGYELJ),
    (r"\bklik[áa][bp]\w*", "ClickUp", HIBA),
    (r"\bl[öo]nd[eé]s\w*|\bleendes\w*|\blearnes\w*", "LearnDash", HIBA),
    (r"\bmember\s+mous\b", "MemberMouse", HIBA),
    (r"\bmatricool\w*|\bmetricol\b", "Metricool", HIBA),
    (r"\bmen[iü]\s*c[sh]?[ae]t\w*|\bmenicet\w*", "ManyChat", HIBA),
    (r"\bobszidi[áa]n\w*", "Obsidian", HIBA),
    (r"\bkanv[áa]\w*", "Canva", HIBA),
    (r"\bedobi\b", "Adobe", HIBA),
    (r"\bmetaeds\b", "Meta Ads", HIBA),
    (r"\bpiton\w*", "Python", HIBA),
    (r"\bvp\s+plugin\w*", "WP plugin (WordPress)", HIBA),
    # --- marketing- és tartalomgyártási szakszavak
    (r"\bsz[ée]lsz\w*|\bszes\s+(oldal|kampány)", "sales", HIBA),
    (r"\bf[áa]n+el\w*|\bfánda\b", "funnel", HIBA),
    (r"\bapp?s+ell\w*|\bupszell\w*", "upsell", HIBA),
    (r"\blending\w*", "landing", HIBA),
    (r"\bwebd[aá]i?[gj]n\w*|\bwebdign\w*", "webdesign", HIBA),
    (r"\bhúk\w*", "hook", HIBA),
    (r"\brilsz\w*", "reels", HIBA),
    (r"\btárcsor\w*", "tárgysor", HIBA),
    (r"\btolkien[- ]?head\w*", "talking head", HIBA),
    (r"\bsort\s+vide[óo]\w*", "short videó", FIGYELJ),
    (r"\badvent\s+is\s+plusz", "Advantage+", HIBA),
    (r"\bfont\s+verzi[óo]\w*", "konverzió", HIBA),
    (r"\bkérdezfelel\w*|\bkérdezd\s+felelek", "kérdezz-felelek", HIBA),
    # --- általános magyar félrehallások
    (r"\bálf[áa]\w*", "áfa", HIBA),
    (r"\bnoró\s*vírus", "norovírus", HIBA),
    (r"\bspanyol\s+vastaszt", "spanyolviaszt", HIBA),
    (r"\bmintogyha\b", "mintha", HIBA),
    (r"\bleíat\w*", "leirat", HIBA),
    (r"\btéfit\w*", "tévhit", HIBA),
    (r"\begyessév\w*", "egyesével", HIBA),
    (r"\bfejav[áa]r\w*", "félvállról", HIBA),
    (r"\baelláta\w*", "apelláta", HIBA),
    (r"\bdíj(?:a|át|án|ára|ákat|ák)?\s+(?:van|láts|mutat|következ)", "dia (prezentációban a „díj” gyakran dia)", FIGYELJ),
    # --- nyers maradványok
    (r"\[\s*_+\s*\]", "[…] (kisípolt káromkodás jelölése)", HIBA),
    (r"[฀-๿؀-ۿ぀-ヿ一-鿿]", "ASR-szemét (idegen írásjel), törlendő", HIBA),
    (r"\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->", "VTT/SRT-időkód maradt a szövegben", HIBA),
]

IDEZETT = re.compile(r'[„"“]([^„"“”]+)[”"“](\?)?')


def alak_regex(alak):
    """Félrehallott alak → regex: rugalmas szóköz, 4 betűtől toldalékot is enged."""
    szavak = alak.split()
    minta = r"\s+".join(re.escape(sz) for sz in szavak)
    vege = r"[\w-]*" if len(alak) >= 4 else r"(?!\w)"
    return r"(?<!\w)" + minta + vege


def szotar_mintak(path):
    """A szótár táblázatsoraiból (Helyes | Félrehallott alakok | …) mintákat készít."""
    mintak, kodblokk = [], False
    for sor in path.read_text(encoding="utf-8-sig").splitlines():
        s = sor.strip()
        if s.startswith("```"):
            kodblokk = not kodblokk
            continue
        if kodblokk or not s.startswith("|"):
            continue
        cellak = [c.strip() for c in s.strip("|").split("|")]
        if len(cellak) < 2:
            continue
        helyes = re.sub(r"[*`]", "", cellak[0]).strip()
        if not helyes or set(helyes) <= set("-: ") or helyes.lower() == "helyes":
            continue
        for m in IDEZETT.finditer(cellak[1]):
            alak = m.group(1).strip()
            if alak:
                szint = FIGYELJ if m.group(2) else HIBA
                mintak.append((alak_regex(alak), helyes, szint))
    return mintak


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("leirat")
    ap.add_argument("--szotar", action="append", default=[], help="további szótárfájl (ismételhető)")
    ap.add_argument("--szotar-nelkul", action="store_true", help="csak a beépített általános lista")
    ap.add_argument("--csak-hiba", action="store_true", help="a FIGYELJ tételek nélkül")
    a = ap.parse_args()

    mintak = list(ALTALANOS)
    if not a.szotar_nelkul:
        fajlok = ([ALAP_SZOTAR] if ALAP_SZOTAR.exists() else []) + [Path(p) for p in a.szotar]
        szotarbol = 0
        for f in fajlok:
            if not f.exists():
                sys.exit(f"Nincs ilyen szótárfájl: {f}")
            sm = szotar_mintak(f)
            mintak += sm
            szotarbol += len(sm)
            nev = "references/szotar.md" if f == ALAP_SZOTAR else f
            print(f"Szótár: {nev} ({len(sm)} félrehallott alak)")
        if not szotarbol:
            print("A szótárban nincs félrehallott alak: csak a beépített általános listával ellenőrzök.")

    compiled = [(re.compile(p, re.IGNORECASE), j, s) for p, j, s in mintak]
    lines = Path(a.leirat).read_text(encoding="utf-8-sig").splitlines()
    talalat, osszesito = 0, {}
    for i, line in enumerate(lines, 1):
        for rx, javaslat, szint in compiled:
            if a.csak_hiba and szint != HIBA:
                continue
            helyes_eleje = re.split(r"[„\"(]", javaslat)[0].strip().lower()
            for m in rx.finditer(line):
                # ha a helyes alak áll ott (pl. a félrehallás a helyes név eleje), nem hiba
                if helyes_eleje and line[m.start():].lower().startswith(helyes_eleje):
                    continue
                talalat += 1
                osszesito[(javaslat, szint)] = osszesito.get((javaslat, szint), 0) + 1
                print(f"{i:>5}  [{szint}]  „{m.group(0)}”  →  {javaslat}")
    print(f"\n{talalat} találat.")
    for (j, s), n in sorted(osszesito.items(), key=lambda x: -x[1]):
        print(f"  {n:>4} × [{s}] {j}")


if __name__ == "__main__":
    main()
