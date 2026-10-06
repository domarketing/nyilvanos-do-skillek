#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kész leirat (.md) → weboldalba (pl. WordPressbe) illeszthető HTML-blokk.

Önálló <style> + <div class="lr-leirat">, így nem ütközik a weboldal témájával. A # cím
kimarad (a bejegyzésnek már van címe). Kezeli a két leiratsablont:
  - **[óó:pp:mm]** időbélyeg-sorok   → halvány elválasztó
  - ## [óó:pp:mm] Fejezetcím          → h2 időbélyeggel
  - **Név:** szöveg                   → beszélőnév a fő színnel
  - *dőlt sor*                        → bevezető megjegyzés-doboz

A színek és a betűtípus semleges alapértékek; a saját arculatodat (például a cegprofil.md-ből)
kapcsolókkal adhatod meg. A betűtípust a szkript nem tölti be, csak megnevezi: ha a weboldaladon
be van töltve, azt használja, ha nincs, a rendszer betűtípusát.

Használat:
  python md2html.py leirat.md leirat-web.html
  python md2html.py leirat.md leirat-web.html --fo-szin "#2F4B9A" --kiemelo-szin "#F2A93B" \\
      --sotet-szin "#0F1B3D" --betu "Inter"

Beillesztés WordPressbe: szerkesztő → ⋮ → Kódszerkesztő (a blokkszerkesztő nagy anyagnál
beragadhat), vagy egy „Egyéni HTML” blokkba.
"""
import argparse
import html
import re
import sys

for _s in (sys.stdout, sys.stderr):  # Windows-konzolon (cp1250) is jó ékezet és nyíl
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    return t


def biztonsagos(ertek, mi):
    """CSS-be kerülő érték: ne lehessen vele kitörni a stílusblokkból."""
    if re.search(r"[;{}<>\\]", ertek):
        sys.exit(f"Érvénytelen {mi}: {ertek!r}")
    return ertek.strip()


CSS = """<style>
.lr-leirat{{max-width:760px;margin:0 auto;font-family:{betu}-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
 font-size:17px;line-height:1.75;color:#1c2430}}
.lr-leirat .lr-l{{margin:0 0 1.1em}}
.lr-leirat .lr-sp{{color:{fo}}}
.lr-leirat .lr-ts{{margin:2.2em 0 1.1em;padding-top:1.1em;border-top:1px solid #e4e7ee;
 font-size:13px;letter-spacing:.08em;font-weight:600;color:#8b93a3}}
.lr-leirat h2.lr-h{{margin:2.4em 0 .8em;font-size:21px;line-height:1.35;color:{sotet}}}
.lr-leirat h2.lr-h span{{display:block;font-size:13px;letter-spacing:.08em;font-weight:600;color:#8b93a3}}
.lr-leirat .lr-note{{margin:0 0 2em;padding:14px 18px;background:#f5f6f9;border-left:3px solid {kiemelo};
 border-radius:6px;font-size:15px;color:#555e6c}}
.lr-leirat code{{background:#eef0f4;padding:1px 5px;border-radius:4px;font-size:.9em}}
@media(max-width:640px){{.lr-leirat{{font-size:16px}}}}
</style>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("forras", help="a kész leirat (.md)")
    ap.add_argument("cel", help="a kimeneti HTML-fájl")
    ap.add_argument("--fo-szin", default="#2F4B9A", help="beszélőnevek színe (alap: #2F4B9A)")
    ap.add_argument("--kiemelo-szin", default="#F2A93B", help="a megjegyzés-doboz csíkja (alap: #F2A93B)")
    ap.add_argument("--sotet-szin", default="#0F1B3D", help="fejezetcímek színe (alap: #0F1B3D)")
    ap.add_argument("--betu", default="", help="betűtípus neve, ha a weboldalon be van töltve (pl. Inter)")
    a = ap.parse_args()

    betu = biztonsagos(a.betu, "betűtípus").replace("'", "").replace('"', "")
    css = CSS.format(
        fo=biztonsagos(a.fo_szin, "fő szín"),
        kiemelo=biztonsagos(a.kiemelo_szin, "kiemelő szín"),
        sotet=biztonsagos(a.sotet_szin, "sötét szín"),
        betu=f"'{betu}'," if betu else "",
    )

    out, n = [], {"ts": 0, "h": 0, "sp": 0, "p": 0}
    for raw in open(a.forras, encoding="utf-8-sig").read().split("\n"):
        s = raw.strip()
        if not s or s == "---" or re.match(r"^# ", s):
            continue
        m = re.fullmatch(r"\*\*\[(\d{2}:\d{2}:\d{2})\]\*\*", s)
        if m:
            n["ts"] += 1
            out.append(f'<p class="lr-ts" id="t{m.group(1).replace(":", "")}">{m.group(1)}</p>')
            continue
        m = re.match(r"^#{2,3}\s+\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(.*)$", s)
        if m:
            n["h"] += 1
            out.append(f'<h2 class="lr-h"><span>{m.group(1)}</span>{inline(m.group(2))}</h2>')
            continue
        m = re.match(r"^#{2,3}\s+(.*)$", s)
        if m:
            n["h"] += 1
            out.append(f'<h2 class="lr-h">{inline(m.group(1))}</h2>')
            continue
        m = re.match(r"^\*\*([^:*]{1,45}):\*\*\s*(.*)$", s)
        if m:
            n["sp"] += 1
            out.append(f'<p class="lr-l"><strong class="lr-sp">{html.escape(m.group(1))}:</strong> {inline(m.group(2))}</p>')
            continue
        if s.startswith("*") and s.endswith("*") and not s.startswith("**"):
            out.append(f'<p class="lr-note">{inline(s)}</p>')
            continue
        n["p"] += 1
        out.append(f'<p class="lr-l">{inline(s)}</p>')

    doc = css + '\n<div class="lr-leirat">\n' + "\n".join(out) + "\n</div>\n"
    open(a.cel, "w", encoding="utf-8").write(doc)
    kb = len(doc.encode("utf-8")) // 1024
    print(f"{a.cel}: {n['ts']} időbélyeg, {n['h']} fejezetcím, {n['sp']} beszélő-bekezdés, {n['p']} egyéb, {kb} KB")
    if kb > 300:
        print("Figyelem: 300 KB fölött a WordPress blokkszerkesztője beragadhat, a Kódszerkesztőbe illeszd.")


if __name__ == "__main__":
    main()
