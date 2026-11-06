#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Koppány Lili (koppanylili.hu) · ARCULAT-VÁLASZTÓ (ai-arculat-generator, első teszt, 2026.10.19).
Az alap-elemek az új egyediség-eszközökből: márka-diagnózis (marka-dns.json), paletta_gen.py, betu_valaszto.py,
ikon_technika.py; az 5 karakter Lilinél: botanikus tábla · tervezőasztal · préri · kerti napló · arborétum.
A tartalmi blokkok és a szekció-elrendezések az okt. 1-jei futásból (ugyanazok a tények az oldalról).
Régi leírás:
Alap-elemek 5 karakterben (elegáns · modern · merész · barátságos · klasszikus), Lili márkájára hangolva.
Téma-elemek a kerttervezés világából: szintvonalak, kertterv-jelek, díszfüvek, milliméterpapír, herbárium;
lepkék és méhek, óriás kasvirág, évszak-jelek, a mostani oldal ceruzarajzai, növénycímkék; fűszál-él, dombvonal,
cserjeszegély, léckerítés, ceruzás mezőrajz. A szekciók a mostani főoldal szekciói, ugyanabban a sorrendben."""
import base64
import io
import json
import math
import random
import sys
from pathlib import Path

from PIL import Image

ITT = Path(__file__).resolve().parent
SKILL = ITT.parent.parent / "scripts"   # a skill saját scripts/ mappája
sys.path.insert(0, str(SKILL))
from motor.alap import svg_uri, esc, md, ui  # noqa: E402
from motor.kozos import kick, shead, btn, gombsor, foto, ph, ik, logo, dk, hat  # noqa: E402
from motor.szekciok_a import KIN_KOZOS  # noqa: E402
from motor.szekciok_b import LAT_KOZOS, LBL_KOZOS, _lbl_linkek, _jogi  # noqa: E402
from motor.stilusok import NYIL  # noqa: E402

B = "bemenet/kepek/"


# ------------------------------------------------------------------ rajz-segédek

def url(s):
    return f'url("{svg_uri(s)}")'


def svg(vb, belso, extra=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{extra}>{belso}</svg>'


def png_maszk(fajl, max_w=420, alfa=1.0):
    """A mostani oldal egy ceruzarajzából maszk (csak az alfa számít): vágás, kicsinyítés, alfa-erősítés."""
    im = Image.open(ITT / fajl).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if bb:
        im = im.crop(bb)
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    if alfa != 1.0:
        a = im.getchannel("A").point(lambda v: min(255, int(v * alfa)))
        im = Image.new("RGBA", im.size, (0, 0, 0, 0))
        im.putalpha(a)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return f'url("data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}")', im.size


def cr(pts, zart=False):
    """Catmull-Rom görbe köbös Bézier-szakaszokkal (zárt vagy nyitott)."""
    n = len(pts)
    if zart:
        P = [pts[-1]] + pts + [pts[0], pts[1]]
        d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
        for i in range(1, n + 1):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
        return d + "Z"
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d


def felho(cx, cy, r, n=10, rot=0.0):
    """Cserje-/lombkorona-jel a kerttervekről: körre fűzött kifelé domborodó ívek."""
    pts = [(cx + r * math.cos(rot + 2 * math.pi * k / n), cy + r * math.sin(rot + 2 * math.pi * k / n)) for k in range(n)]
    ar = 2 * r * math.sin(math.pi / n) * .62
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for k in range(1, n + 1):
        x, y = pts[k % n]
        d += f"A{ar:.1f} {ar:.1f} 0 0 1 {x:.1f} {y:.1f}"
    return d + "Z"


# ------------------------------------------------------------------ téma-formák (maszk-SVG-k)

def _szint():
    rnd = random.Random(5)
    out = []
    for cx, cy, n, sx, sy in [(300, 270, 7, 1.25, .82), (1150, 650, 7, 1.2, .85), (1300, 140, 3, 1.1, .8), (150, 800, 3, 1.2, .7)]:
        fz = [rnd.uniform(0, 6.283) for _ in range(3)]
        for i in range(n):
            R = 30 + i * 38
            pts = []
            for k in range(56):
                t = k / 56 * 2 * math.pi
                f = 1 + .15 * math.sin(2 * t + fz[0] + i * .05) + .08 * math.sin(3 * t + fz[1] + i * .12) + .04 * math.sin(5 * t + fz[2] + i * .2)
                pts.append((cx + R * f * sx * math.cos(t), cy + R * f * sy * math.sin(t)))
            out.append(f'<path d="{cr(pts, True)}" fill="none" stroke="#000" stroke-width="{2.4 if i % 4 == 3 else 1.15}"/>')
    return url(svg("0 0 1440 900", "".join(out), ' preserveAspectRatio="xMidYMid slice"'))


def _kertterv_jelek():
    s = []
    # lombhullató fa: felhő-kontúr, középpont, kereszt
    s.append(f'<path d="{felho(84, 92, 46, 11, .2)}" fill="none" stroke="#000" stroke-width="1.7"/>'
             '<circle cx="84" cy="92" r="3.2"/><path d="M70 92H98M84 78V106" stroke="#000" stroke-width="1"/>')
    # tűlevelű: kör + küllők
    s.append('<circle cx="246" cy="64" r="25" fill="none" stroke="#000" stroke-width="1.5"/>'
             + "".join(f'<path d="M{246 + 8 * math.cos(a):.1f} {64 + 8 * math.sin(a):.1f}L{246 + 24 * math.cos(a):.1f} {64 + 24 * math.sin(a):.1f}" stroke="#000" stroke-width="1"/>'
                       for a in [k * math.pi / 8 for k in range(16)]))
    # cserjecsoport
    s.append("".join(f'<path d="{felho(x, y, r, 8, rt)}" fill="none" stroke="#000" stroke-width="1.4"/>'
                     for x, y, r, rt in [(222, 214, 20, .3), (252, 236, 16, 1.1), (226, 252, 13, .6)]))
    # lépőkövek
    s.append("".join(f'<ellipse cx="{x}" cy="{y}" rx="11" ry="7" transform="rotate({r} {x} {y})" fill="none" stroke="#000" stroke-width="1.4"/>'
                     for x, y, r in [(40, 236, 20), (66, 258, 30), (96, 274, 18), (128, 286, 8), (162, 294, 4)]))
    # évelő-pöttyök
    rnd = random.Random(4)
    s.append("".join(f'<circle cx="{150 + rnd.uniform(-22, 22):.1f}" cy="{168 + rnd.uniform(-18, 18):.1f}" r="{rnd.uniform(1.8, 3.2):.1f}"/>' for _ in range(11)))
    return url(svg("0 0 320 320", "".join(s)))


def _fuszalak():
    rnd = random.Random(8)
    w, h = 1440, 320
    d = []
    for _ in range(380):
        x = rnd.uniform(0, w)
        hh = rnd.uniform(.25, 1) ** 1.3 * h * .95
        lean = rnd.uniform(-.35, .35) * hh
        bw = rnd.uniform(1.6, 3.6)
        cx, cy = x + lean * .35, h - hh * .55
        d.append(f'<path d="M{x - bw:.1f} {h}Q{cx:.1f} {cy:.1f} {x + lean:.1f} {h - hh:.1f}Q{cx + bw * .6:.1f} {cy:.1f} {x + bw:.1f} {h}Z"/>')
    for i in range(28):
        x = rnd.uniform(0, w)
        hh = rnd.uniform(.45, .9) * h
        lean = rnd.uniform(-.1, .1) * hh
        tx, ty = x + lean, h - hh
        d.append(f'<path d="M{x:.1f} {h}Q{x + lean * .4:.1f} {h - hh * .5:.1f} {tx:.1f} {ty:.1f}" fill="none" stroke="#000" stroke-width="1.4"/>')
        if i % 2:
            d.append(f'<ellipse cx="{tx:.1f}" cy="{ty - 11:.1f}" rx="4.5" ry="13" transform="rotate({lean / hh * 70:.0f} {tx:.1f} {ty:.1f})"/>')
        else:
            d.append(f'<circle cx="{tx:.1f}" cy="{ty - 4:.1f}" r="6.5"/>')
    return url(svg(f"0 0 {w} {h}", "".join(d), ' preserveAspectRatio="none"'))


MM = url(svg("0 0 60 60", "".join(f'<path d="M{i * 6} 0V60M0 {i * 6}H60" stroke="#000" stroke-width=".45"/>' for i in range(1, 10))
             + '<path d="M0 0V60M0 0H60" stroke="#000" stroke-width="1.4"/>'))


def _levelek():
    rnd = random.Random(12)
    out = []

    def level(L, W):
        p = f'<path d="M0 0C{W} {-L * .25:.1f} {W * .8:.1f} {-L * .75:.1f} 0 {-L}C{-W * .8:.1f} {-L * .75:.1f} {-W} {-L * .25:.1f} 0 0Z" fill="none" stroke="#000" stroke-width="1.6"/>'
        p += f'<path d="M0 10L0 {-L * .92:.1f}" stroke="#000" stroke-width="1.2"/>'
        for j in range(1, 5):
            y = -L * j / 5.4
            p += f'<path d="M0 {y:.1f}L{W * .55:.1f} {y - L * .12:.1f}M0 {y:.1f}L{-W * .55:.1f} {y - L * .12:.1f}" stroke="#000" stroke-width=".9"/>'
        return p

    def ginkgo():
        p = '<path d="M0 0L0 -34" stroke="#000" stroke-width="1.4"/>'
        p += '<path d="M0 -34C-34 -40 -52 -74 -36 -104Q-18 -96 -3 -104L0 -92 3 -104Q18 -96 36 -104C52 -74 34 -40 0 -34Z" fill="none" stroke="#000" stroke-width="1.6"/>'
        p += "".join(f'<path d="M0 -36L{-30 + k * 7.5:.1f} -98" stroke="#000" stroke-width=".7"/>' for k in range(9))
        return p

    def tolgy():
        bal, jobb = [], []
        for k in range(15):
            t = k / 14
            wv = 26 * math.sin(math.pi * t) ** .8 * (.62 + .38 * abs(math.sin(4.5 * math.pi * t)))
            y = -t * 120
            bal.append((-wv, y))
            jobb.append((wv, y))
        pts = jobb + bal[::-1][1:-1]
        p = f'<path d="{cr(pts, True)}" fill="none" stroke="#000" stroke-width="1.6"/>'
        return p + '<path d="M0 12L0 -112" stroke="#000" stroke-width="1.2"/>'

    def pafrany():
        p = '<path d="M0 0C4 -40 2 -90 -6 -140" fill="none" stroke="#000" stroke-width="1.4"/>'
        for k in range(1, 11):
            t = k / 11
            x, y = -6 * t ** 2 + 4 * math.sin(t * 3), -140 * t
            L = 26 * (1 - t) + 6
            p += f'<ellipse cx="{x + L * .5:.1f}" cy="{y - 3:.1f}" rx="{L * .5:.1f}" ry="4" transform="rotate(-24 {x:.1f} {y:.1f})" fill="none" stroke="#000" stroke-width="1"/>'
            p += f'<ellipse cx="{x - L * .5:.1f}" cy="{y - 3:.1f}" rx="{L * .5:.1f}" ry="4" transform="rotate(24 {x:.1f} {y:.1f})" fill="none" stroke="#000" stroke-width="1"/>'
        return p

    alak = [lambda: level(110, 34), ginkgo, tolgy, pafrany, lambda: level(80, 30), tolgy, ginkgo, lambda: level(96, 22)]
    helyek = [(80, 170), (300, 120), (520, 210), (170, 420), (420, 380), (600, 520), (300, 610), (560, 40)]
    for f, (x, y) in zip(alak, helyek):
        out.append(f'<g transform="translate({x} {y}) rotate({rnd.uniform(-160, 160):.0f}) scale({rnd.uniform(.8, 1.15):.2f})">{f()}</g>')
    return url(svg("0 0 640 640", "".join(out)))


SZINT = _szint()
KTJ = _kertterv_jelek()
FUSZ = _fuszalak()
LEVELEK = _levelek()

# dekor-formák (100x100)
_SZARNY = ('<path d="M49 50C40 30 22 14 10 22 2 28 8 44 20 50 30 54 42 54 49 52Z"/>'
           '<path d="M49 54C40 58 26 64 24 76 22 88 36 90 44 78 48 70 49 62 49 56Z"/>')
LEPKE = url(svg("0 0 100 100", _SZARNY + f'<g transform="translate(100 0) scale(-1 1)">{_SZARNY}</g>'
                '<ellipse cx="50" cy="55" rx="2.8" ry="17"/>'
                '<path d="M49 39C46 30 42 24 37 21M51 39C54 30 58 24 63 21" fill="none" stroke="#000" stroke-width="2.2" stroke-linecap="round"/>'))
MEH = url(svg("0 0 100 100", '<defs><clipPath id="t"><ellipse cx="56" cy="62" rx="25" ry="16"/></clipPath></defs>'
              '<g clip-path="url(#t)"><rect x="30" y="40" width="9" height="44"/><rect x="45" y="40" width="9" height="44"/>'
              '<rect x="60" y="40" width="9" height="44"/><rect x="75" y="40" width="10" height="44"/></g>'
              '<ellipse cx="56" cy="62" rx="25" ry="16" fill="none" stroke="#000" stroke-width="3"/><circle cx="27" cy="59" r="9"/>'
              '<ellipse cx="50" cy="36" rx="11" ry="17" transform="rotate(-22 50 36)" fill="none" stroke="#000" stroke-width="3"/>'
              '<ellipse cx="66" cy="37" rx="9" ry="14" transform="rotate(22 66 37)" fill="none" stroke="#000" stroke-width="3"/>'
              '<path d="M80 60L92 62L80 65Z"/>'))
HOPE = url(svg("0 0 100 100", '<g stroke="#000" stroke-width="5" stroke-linecap="round" fill="none">'
               + "".join(f'<g transform="rotate({k * 60} 50 50)"><path d="M50 50V10M50 26L40 16M50 26L60 16"/></g>' for k in range(6)) + '</g>'))
VIRAG = url(svg("0 0 100 100", "".join(f'<ellipse cx="50" cy="27" rx="12" ry="21" transform="rotate({k * 72} 50 50)"/>' for k in range(5))
                + '<circle cx="50" cy="50" r="11"/>'))
NAP = url(svg("0 0 100 100", '<circle cx="50" cy="50" r="19"/>'
              + "".join(f'<rect x="47.5" y="6" width="5" height="17" rx="2.5" transform="rotate({k * 30} 50 50)"/>' for k in range(12))))
_jh = [(50, 6), (57, 24), (70, 16), (67, 36), (86, 30), (79, 46), (94, 56), (73, 60), (78, 74), (56, 66), (53, 80), (53, 96), (47, 96),
       (47, 80), (44, 66), (22, 74), (27, 60), (6, 56), (21, 46), (14, 30), (33, 36), (30, 16), (43, 24)]
JUHAR = url(svg("0 0 100 100", '<path d="M' + "L".join(f"{x} {y}" for x, y in _jh) + 'Z"/>'))

# határ-formák
def _fuszal_el(w=360, h=44, seed=3):
    rnd = random.Random(seed)
    d = [f'<rect x="0" y="{h - 5}" width="{w}" height="5"/>']
    x = -4.0
    while x < w + 4:
        hh = rnd.uniform(.22, 1) * (h - 3)
        lean = rnd.uniform(-.5, .5) * 10
        bw = rnd.uniform(1.8, 3.4)
        d.append(f'<path d="M{x - bw:.1f} {h}Q{x + lean * .3:.1f} {h - hh * .5:.1f} {x + lean:.1f} {h - hh:.1f}Q{x + lean * .3 + bw * .5:.1f} {h - hh * .5:.1f} {x + bw:.1f} {h}Z"/>')
        x += rnd.uniform(2.6, 5.4)
    return url(svg(f"0 0 {w} {h}", "".join(d), ' preserveAspectRatio="none"'))


def _domb():
    hatso = [(x, 30 - 20 * math.sin(x / 1440 * math.pi * 2.2 + .6) * .9 + 6 * math.sin(x / 140)) for x in range(0, 1441, 60)]
    elso = [(x, 42 - 12 * math.sin(x / 1440 * math.pi * 1.6 + 2.2) + 3 * math.sin(x / 90)) for x in range(0, 1441, 60)]
    return url(svg("0 0 1440 60", f'<path d="{cr(hatso)}L1440 60L0 60Z" fill-opacity=".45"/><path d="{cr(elso)}L1440 60L0 60Z"/>',
                   ' preserveAspectRatio="none"'))


def _cserje():
    rnd = random.Random(6)
    w, h = 300, 32
    d = [f'<rect x="0" y="{h - 8}" width="{w}" height="8"/>']
    x = 0
    while x < w + 20:
        r = rnd.uniform(9, 16)
        d.append(f'<circle cx="{x:.1f}" cy="{h - r * .55:.1f}" r="{r:.1f}"/>')
        x += r * rnd.uniform(1.15, 1.5)
    return url(svg(f"0 0 {w} {h}", "".join(d)))


KERITES = url(svg("0 0 34 46", '<path d="M7 46V12L17 2L27 12V46Z"/><rect x="0" y="17" width="34" height="5"/><rect x="0" y="32" width="34" height="5"/>'
                  '<rect x="0" y="43" width="34" height="3"/>'))
FUSZEL = _fuszal_el()
DOMB = _domb()
CSERJE = _cserje()
ROZETTA = url(svg("0 0 100 100", f'<path d="{felho(50, 50, 45, 22)}"/>'))

# címsor- és alcím-díszek
SWOOSH = url(svg("0 0 300 24", '<path d="M3 15C70 7 180 4 297 11" fill="none" stroke="#000" stroke-width="5" stroke-linecap="round"/>'
                 '<path d="M14 19C90 12 200 11 288 15" fill="none" stroke="#000" stroke-width="2" stroke-linecap="round" opacity=".55"/>',
                 ' preserveAspectRatio="none"'))
AG = url(svg("0 0 120 30", '<path d="M4 16C40 14 80 14 114 15" fill="none" stroke="#000" stroke-width="1.8" stroke-linecap="round"/>'
             + "".join(f'<ellipse cx="{14 + i * 18}" cy="10" rx="7.5" ry="3.2" transform="rotate(-28 {14 + i * 18} 10)"/>'
                       f'<ellipse cx="{23 + i * 18}" cy="21" rx="7.5" ry="3.2" transform="rotate(28 {23 + i * 18} 21)"/>' for i in range(5))
             + '<circle cx="114" cy="15" r="3"/>'))
LEVELKE = url(svg("0 0 26 12", '<path d="M2 6C8 0 16 0 22 6C16 12 8 12 2 6Z"/><path d="M22 6H26" stroke="#000" stroke-width="1.2"/>'))

# az új alap-elemek díszei (ecsetcsík, ceruzás karika, fűcsomó)
ECSET = url(svg("0 0 240 40", '<path d="M6 14C40 6 120 4 232 9C236 10 238 14 235 17C238 20 237 25 232 27C170 33 80 36 10 33C4 33 2 28 5 25C1 22 2 16 6 14Z"/>', ' preserveAspectRatio="none"'))
KARIKA = url(svg("0 0 200 60", '<path d="M22 44C6 34 10 16 52 9C98 2 170 4 190 22C204 36 170 54 108 56C58 58 16 52 12 38C9 28 30 16 64 12" fill="none" stroke="#000" stroke-width="3.2" stroke-linecap="round"/>', ' preserveAspectRatio="none"'))
FUCSOMO = url(svg("0 0 60 46", '<g fill="none" stroke="#000" stroke-width="3.4" stroke-linecap="round"><path d="M30 45C28 30 21 17 8 7"/><path d="M30 45C30 28 31 15 29 2"/><path d="M30 45C33 30 42 18 54 9"/><path d="M30 45C25 35 16 29 3 27"/><path d="M30 45C35 37 45 33 58 31"/></g>'))

# a mostani oldal ceruzarajzai maszkként
KASV, _ = png_maszk(B + "Favicon-2.png", 320)
TULIP, TULIP_M = png_maszk(B + "Untitled_Artwork-1-1-pn7av2kv5n6hy3o1cqli1rbnjg7ew82wm8z2wagu7c.png", 300, 2.2)
AGRAJZ, AGRAJZ_M = png_maszk(B + "Untitled_Artwork1-pmqkxdx2pm8ek0lsuit7303ltmc69mph27rf0t3zlg.png", 220, 2.4)
SEDUM, SEDUM_M = png_maszk(B + "sedum.png", 300, 1.9)
MEZO, MEZO_M = png_maszk(B + "lablec.png", 600, 1.8)
FEKVO, FEKVO_M = png_maszk(B + "Virag_fekvo-pmok8fh8emlc28fljrvtl2dbf8lakq07h50j37whug.png", 300, 2.4)

MINTAK = {"SZINT": SZINT, "KTJ": KTJ, "FUSZ": FUSZ, "MM": MM, "LEVELEK": LEVELEK, "LEPKE": LEPKE, "MEH": MEH, "HOPE": HOPE,
          "VIRAG": VIRAG, "NAP": NAP, "JUHAR": JUHAR, "FUSZEL": FUSZEL, "DOMB": DOMB, "CSERJE": CSERJE, "KERITES": KERITES,
          "ROZETTA": ROZETTA, "SWOOSH": SWOOSH, "AG": AG, "LEVELKE": LEVELKE, "KASV": KASV, "TULIP": TULIP, "AGRAJZ": AGRAJZ,
          "SEDUM": SEDUM, "MEZO": MEZO, "FEKVO": FEKVO, "NYIL": f'url("{NYIL}")',
          "TULIP_AR": f"{TULIP_M[0]}/{TULIP_M[1]}", "AGRAJZ_AR": f"{AGRAJZ_M[0]}/{AGRAJZ_M[1]}",
          "SEDUM_AR": f"{SEDUM_M[0]}/{SEDUM_M[1]}", "MEZO_AR": f"{MEZO_M[0]}/{MEZO_M[1]}", "FEKVO_AR": f"{FEKVO_M[0]}/{FEKVO_M[1]}"}
MINTAK.update({"ECSET": ECSET, "KARIKA": KARIKA, "FUCSOMO": FUCSOMO})


def T(css):
    """@NÉV@ helyére a minta (így a CSS-ben nem kell kapcsos zárójelet duplázni)."""
    for k, v in MINTAK.items():
        css = css.replace(f"@{k}@", v)
    return css


def mask(nev, hely="center/contain no-repeat"):
    return f"-webkit-mask:@{nev}@ {hely};mask:@{nev}@ {hely}"


# ------------------------------------------------------------------ PALETTÁK (paletta_gen.py, a diagnózis színeiből)

_PJ = json.loads((ITT / "paletta-javaslat.json").read_text(encoding="utf-8"))
_P_SZOVEG = {
    "pE": ("Elegáns · esti kert, szalmaarany sötét alapon",
           "Sötét, meleg földszín alap, rajta a díszfüvek szalmaaranya világít; a nyári ég kékje és a zsálya csak apró fényeknek jut. "
           "Esti, prémium hangulat: a kertfotók és a ceruzarajzok kiugranak rajta."),
    "pM": ("Modern · moha és nyári ég",
           "Mély mohazöld fő szín, mellette a nyári ég kékje és a cickafark sárgája. Friss és tiszta, mint egy jól megrajzolt terv; "
           "a gombok messziről látszanak."),
    "pB": ("Merész · kasvirág és szalma",
           "A faviconod kasvirágának erős rózsaszíne a fő szín, mellette az őszi díszfüvek aranya és egy csipet sedum-rozsda. "
           "A préri színei: a legélénkebb, legemlékezetesebb irány."),
    "pF": ("Barátságos · zsálya és púderrózsa, érettebben",
           "A mostani zsályazöldjeid és púderrózsád kicsit érettebb árnyalatban, a díszfű-szalmával kiegészítve. Ez áll a legközelebb "
           "a mostani oldaladhoz, csak rendezettebb."),
    "pK": ("Klasszikus · tölgylevél és sedum-rozsda",
           "A nagy tölgy levelének mélyzöldje és az őszi varjúháj rozsdavöröse, krémszínű papíron. Nyugodt és időtálló, mint egy "
           "régi botanikus kert."),
}
PALETTAK = []
for _p in _PJ["lista"]:
    _d = {k: _p[k] for k in ("id", "primary", "accent", "accent2", "paper", "ink", "deep", "card") if k in _p}
    if _p.get("mod"):
        _d["mod"] = _p["mod"]
    _d["nev"], _d["miert"] = _P_SZOVEG[_p["id"]]
    _d["karakter"] = _p["karakter"]
    PALETTAK.append(_d)

# ------------------------------------------------------------------ BETŰPÁROK (betu_valaszto.py, a teljes katalógusból)

_BJ = json.loads((ITT / "betu-javaslat.json").read_text(encoding="utf-8"))
_B_SZOVEG = json.loads((ITT / "betu-szoveg.json").read_text(encoding="utf-8")) if (ITT / "betu-szoveg.json").exists() else {}
BETUK = []
for _b in _BJ["lista"]:
    _d = {k: v for k, v in _b.items() if not k.startswith("_")}
    _d.update(_B_SZOVEG.get(_b["id"], {}))
    BETUK.append(_d)

IKON_MIERT = {
    "iE": "Cianotípia: a tárgyak fehér, áttetsző sziluettként a botanikus kéknyomat mélykékjén, mintha a kertedből napfénnyel "
          "nyomtattuk volna őket. Elegáns, tudományos, nagyon egyedi.",
    "iM": "Tervrajz-nézet: minden ikon úgy készül, ahogy a kertterveidet rajzolod: felülnézet, lombkorona-körök, sraffozott ágyások, "
          "szaggatott ösvény. Ez a tájépítész saját nyelve.",
    "iB": "Papírkivágás: rétegzett papírformák díszfüvekkel és kasvirággal, a préri színeiben. Játékos, mégis kézműves.",
    "iF": "Ceruzaskicc: puha grafit, könnyű sraffozás, egy kis zöld lazúr, ahogy most is rajzolsz. A legszemélyesebb: olyan, "
          "mintha te rajzoltad volna mindet.",
    "iK": "Herbárium-kollázs: préselt levelekből, szirmokból és fűszálakból kirakott tárgyak, egy csík papírragasztóval. "
          "Archív, gondos, botanikus.",
}

# ------------------------------------------------------------------ ALAP-ELEMEK: az 5 Lili-karakterből, szakmai részlettel
# elegáns = botanikus tábla · modern = tervezőasztal · merész = préri · barátságos = kerti napló · klasszikus = arborétum

CIM = [
    dict(id="cE", nev="Elegáns · dőlt fajnév hajszálvonallal", reszlet="a fajnevek dőlt szedése a botanikus táblákon",
         miert="A kiemelt szó dőlt, vékonyabb, alatta egy hajszálvonal, ahogy a botanikus táblákon a növény latin nevét szedik. Csendes, elegáns.", css="""
%S mark{font-style:italic;font-weight:400;color:var(--hl);letter-spacing:0;padding:0 .05em .04em;background:linear-gradient(currentColor,currentColor) 0 100%/100% max(1px,.03em) no-repeat;-webkit-box-decoration-break:clone;box-decoration-break:clone}
"""),
    dict(id="cM", nev="Modern · méretvonal", reszlet="méretvonal, ahogy a kertterveken a távolságokat jelölöd",
         miert="A kulcsszó alatt egy méretvonal fut, két végén kis jelekkel, mint a kerttervek méretezése. Görgetésre kirajzolódik. Pontos, mai.", css="""
%S mark{position:relative;display:inline-block;color:inherit;padding:0 .02em}
%S mark::after{content:"";position:absolute;left:0;right:0;bottom:-.17em;height:.26em;border-left:max(2px,.035em) solid var(--hl);border-right:max(2px,.035em) solid var(--hl);background:linear-gradient(var(--hl),var(--hl)) center/100% max(2px,.035em) no-repeat;transform-origin:left;transition:transform .9s var(--ease-out) .2s}
%S.js-rv [data-rv]:not(.in) mark::after{transform:scaleX(0)}
"""),
    dict(id="cB", nev="Merész · szalmaszínű ecsetcsík", reszlet="az őszi díszfüvek szalmaszíne, ecsettel",
         miert="Széles, ecsettel húzott szalmaszínű csík a kulcsszó mögött, görgetésre végighúzódik. A préri ősszel: erős, meleg, emlékezetes.", css=T("""
%S mark{position:relative;display:inline-block;z-index:0;color:inherit;padding:0 .1em}
%S mark::before{content:"";position:absolute;left:-.1em;right:-.12em;top:.56em;bottom:-.07em;background:color-mix(in srgb,var(--c-accent2) 78%,transparent);""" + mask("ECSET", "center/100% 100% no-repeat") + """;z-index:-1;transform-origin:left;transition:transform .8s var(--ease-out) .2s}
%S.js-rv [data-rv]:not(.in) mark::before{transform:scaleX(.04)}
%S .s-primary mark::before{background:var(--c-primary-mk)}
%S .s-deep mark::before{background:var(--c-deep-hl);opacity:.6}
""")),
    dict(id="cF", nev="Barátságos · ceruzás bekarikázás", reszlet="ceruzás karika, ahogy a kertnaplóban megjelölöd a lényeget",
         miert="A kulcsszót egy ceruzával húzott karika keríti be, mintha a kertnaplódban jelölnéd meg. Görgetésre rajzolódik ki. Személyes, kedves.", css=T("""
%S mark{position:relative;display:inline-block;color:inherit;padding:0 .14em}
%S mark::after{content:"";position:absolute;left:-.24em;right:-.24em;top:-.14em;bottom:-.18em;background:var(--c-ink-2);""" + mask("KARIKA", "center/100% 100% no-repeat") + """;opacity:.85;pointer-events:none;clip-path:inset(0 0 0 0);transition:clip-path 1.1s var(--ease-out) .3s}
%S.js-rv [data-rv]:not(.in) mark::after{clip-path:inset(0 100% 0 0)}
%S .s-deep mark::after,%S .s-primary mark::after{background:var(--hl)}
""")),
    dict(id="cK", nev="Klasszikus · kiskapitális, dupla vonallal", reszlet="a régi arborétumi névtáblák kiskapitális, kettős vonalas felirata",
         miert="A kiemelt szó kiskapitálissal, márkaszínnel, alatta két vékony vonallal, mint a régi botanikus kertek névtábláin. Rendezett, időtálló.", css="""
%S mark{font-variant-caps:all-small-caps;letter-spacing:.05em;color:var(--hl);font-weight:inherit;padding-bottom:.2em;background:linear-gradient(currentColor,currentColor) 0 calc(100% - .02em)/100% max(1px,.025em) no-repeat,linear-gradient(currentColor,currentColor) 0 calc(100% - .13em)/100% max(1px,.025em) no-repeat;-webkit-box-decoration-break:clone;box-decoration-break:clone}
"""),
]

ALCIM = [
    dict(id="kE", nev="Elegáns · táblaszám és dőlt felirat", reszlet="a botanikus atlaszok tábla-számozása (Tab. 01)",
         miert="Minden szekció felett „Tab. 01”, „Tab. 02”, mellette dőlt felirat, mint egy botanikus atlasz tábláin. Finom, tudományos.", css="""
%S .kick{display:flex;align-items:center;justify-content:center;gap:12px;font-family:var(--f-display);font-style:italic;font-weight:400;font-size:1.05rem;letter-spacing:.01em;text-transform:none;color:var(--c-ink-2)}
%S .shead .kick::before{content:"Tab. " attr(data-n);font-family:var(--f-label);font-style:normal;font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--hl);padding-bottom:2px;border-bottom:1px solid currentColor}
%S .kick::after{content:"";width:38px;height:1px;background:currentColor;opacity:.5}
%S .bal .kick{justify-content:flex-start}
"""),
    dict(id="kM", nev="Modern · alaprajzi felirat-doboz", reszlet="felirat-doboz vezetővonallal, mint az alaprajzok jelölései",
         miert="A felvezető egy vékony keretes dobozban ül, egy vezetővonal és egy pötty mutat rá, mint a kerttervek feliratai. Rendezett, pontos.", css="""
%S .kick{display:inline-flex;align-items:center;position:relative;margin-left:38px;padding:5px 11px;border:1px solid currentColor;font-family:var(--f-label);font-weight:600;font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--c-head)}
%S .kick::before{content:"";position:absolute;right:100%;top:50%;width:30px;height:1px;background:currentColor}
%S .kick::after{content:"";position:absolute;right:calc(100% + 27px);top:calc(50% - 4px);width:8px;height:8px;border-radius:50%;background:var(--c-accent)}
%S .s-deep .kick,%S .s-primary .kick{color:var(--hl)}
"""),
    dict(id="kB", nev="Merész · fűcsomó-jel", reszlet="a díszfüves ágyások fűcsomója jelként",
         miert="Nagybetűs, erős felvezető, előtte egy fűcsomó-jel a préri aranyában. Határozott, és rögtön a kertjeidre utal.", css=T("""
%S .kick{display:inline-flex;align-items:flex-end;gap:10px;font-family:var(--f-display);font-weight:var(--w-display);font-size:.95rem;letter-spacing:.03em;text-transform:uppercase;color:var(--c-head)}
%S .kick::before{content:"";width:34px;height:26px;flex:none;background:var(--c-accent);""" + mask("FUCSOMO") + """}
%S .s-deep .kick::before,%S .s-primary .kick::before{background:var(--hl)}
%S .s-deep .kick,%S .s-primary .kick{color:var(--c-on-deep)}
""")),
    dict(id="kF", nev="Barátságos · magtasak-címke", reszlet="kézzel írt magtasak-címke lyukkal, ahogy a kertnaplóba ragasztod",
         miert="Kézzel írt felvezető egy kis, lyukas papírcímkén, kicsit megdöntve, mintha a kertnaplódba ragasztottad volna. Mesélős, közvetlen.", css="""
%S .kick{display:inline-flex;align-items:center;position:relative;padding:5px 15px 6px 24px;border-radius:3px;background:color-mix(in srgb,var(--c-accent) 26%,var(--c-card));color:var(--c-ink);font-family:var(--f-hand);font-size:calc(var(--fs-hand)*1.05rem);font-weight:400;letter-spacing:0;text-transform:none;clip-path:polygon(11px 0,100% 0,100% 100%,11px 100%,0 50%);transform:rotate(-2deg)}
%S .kick::before{content:"";position:absolute;left:10px;top:50%;width:6px;height:6px;margin-top:-3px;border-radius:50%;background:var(--c-paper);box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--c-ink) 35%,transparent)}
"""),
    dict(id="kK", nev="Klasszikus · arborétumi sorszám", reszlet="az arborétumok fáinak sorszám-táblái (No. 01)",
         miert="Minden szekció egy kis sötét táblát kap sorszámmal („No. 01”), mellette ritkított kiskapitális. Mint a botanikus kertek fái előtti címkék.", css="""
%S .kick{display:flex;align-items:center;justify-content:center;gap:12px;font-family:var(--f-body);font-weight:600;font-size:.74rem;letter-spacing:.2em;text-transform:uppercase;color:var(--c-ink-2)}
%S .shead .kick::before{content:"No. " attr(data-n);font-family:var(--f-label);letter-spacing:.06em;font-size:.72rem;color:var(--c-on-deep);background:var(--c-deep);padding:4px 11px;border-radius:999px;box-shadow:inset 0 0 0 1.5px color-mix(in srgb,var(--c-accent) 65%,transparent)}
%S .bal .kick{justify-content:flex-start}
%S .s-deep .shead .kick::before{background:var(--c-paper);color:var(--c-ink)}
"""),
]

GOMB = [
    dict(id="gE", nev="Elegáns · dőlt felirat levélvégű mutatóval", reszlet="levélvégű mutatóvonal, mint a botanikus rajzok jelölései",
         miert="Szögletes, csendes gomb dőlt antikva felirattal; a nyíl helyén egy kis levél, ami rámutatva előrébb lép. Finom és elegáns.", css=T("""
%S .btn{padding:1.05em 1.6em;border-radius:1px;background:var(--b-bg);color:var(--b-ink);font-family:var(--f-display);font-style:italic;font-weight:400;font-size:1.04rem;letter-spacing:.01em;position:relative;transition:background .25s,transform .25s var(--ease)}
%S .btn:not(:has(.ui)){padding-right:2.7em}
%S .btn:not(:has(.ui))::after{content:"";position:absolute;right:1.05em;top:50%;width:1.15em;height:.56em;margin-top:-.28em;background:currentColor;""" + mask("LEVELKE") + """;transition:transform .3s var(--ease)}
%S .btn .ui{transition:transform .25s var(--ease)}
%S .btn:hover{background:color-mix(in srgb,var(--b-bg),#000 12%)}%S .btn:hover::after,%S .btn:hover .ui{transform:translateX(5px)}
%S .btn.alt{background:transparent;color:var(--c-head);box-shadow:inset 0 -1px 0 currentColor;padding-left:.3em}
""")),
    dict(id="gM", nev="Modern · tervlap-sarokjelek", reszlet="a tervlapok vágó- és illesztőjelei a gomb sarkain",
         miert="Egyenes, lapos gomb címke-betűvel, a sarkain vékony jelekkel, mint egy nyomtatott tervlapon. Rámutatva a jelek ráfeszülnek a gombra.", css="""
%S .btn{--sarok:var(--c-head);padding:1em 1.6em;border-radius:0;background:var(--b-bg);color:var(--b-ink);font-family:var(--f-label);font-weight:600;font-size:.8rem;letter-spacing:.1em;text-transform:uppercase;position:relative;transition:background .2s}
%S .btn::before{content:"";position:absolute;inset:-7px;pointer-events:none;background:linear-gradient(var(--sarok),var(--sarok)) 0 0/9px 1.5px,linear-gradient(var(--sarok),var(--sarok)) 0 0/1.5px 9px,linear-gradient(var(--sarok),var(--sarok)) 100% 0/9px 1.5px,linear-gradient(var(--sarok),var(--sarok)) 100% 0/1.5px 9px,linear-gradient(var(--sarok),var(--sarok)) 0 100%/9px 1.5px,linear-gradient(var(--sarok),var(--sarok)) 0 100%/1.5px 9px,linear-gradient(var(--sarok),var(--sarok)) 100% 100%/9px 1.5px,linear-gradient(var(--sarok),var(--sarok)) 100% 100%/1.5px 9px;background-repeat:no-repeat;opacity:.75;transition:inset .25s var(--ease)}
%S .btn:hover::before{inset:-2px}
%S .s-deep .btn,%S .s-primary .btn{--sarok:var(--hl)}
%S .btn.alt{background:var(--c0-card);color:var(--c0-ink);box-shadow:inset 0 0 0 1px var(--c0-line2)}
%S .s-deep .btn.alt,%S .s-primary .btn.alt{--sarok:var(--hl)}
"""),
    dict(id="gB", nev="Merész · kapszula díszfű-szegéllyel", reszlet="díszfű-szegély a gomb alján, mint a préri a pad körül",
         miert="Nagy, telt kapszula vastag felirattal; alul díszfüvek nőnek ki mögüle, rámutatva megnőnek. Erős, játékos, a préri hangulatával.", css=T("""
%S .btn{padding:1.05em 1.9em;border-radius:999px;background:var(--b-bg);color:var(--b-ink);font-weight:800;position:relative;isolation:isolate;transition:transform .2s var(--ease)}
%S .btn::after{content:"";position:absolute;left:12%;right:12%;bottom:-12px;height:18px;background:var(--c-accent);""" + mask("FUSZEL", "center bottom/auto 100% repeat-x") + """;z-index:-1;transform-origin:50% 100%;transition:transform .35s var(--ease)}
%S .btn:hover{transform:translateY(-2px)}%S .btn:hover::after{transform:scaleY(1.4)}
%S .btn.alt{background:var(--balt-bg);color:var(--balt-ink)}%S .btn.alt::after{background:var(--c-line2)}
""")),
    dict(id="gF", nev="Barátságos · perforált magtasak", reszlet="a magtasakok perforált, letéphető pereme",
         miert="Puha, papírszerű gomb, a teteje perforált, mint egy letéphető magtasak. Rámutatva kicsit megbillen. Kedves, kézzelfogható.", css="""
%S .btn{padding:1.15em 1.75em 1em;border-radius:2px 2px 9px 9px;background:var(--b-bg);color:var(--b-ink);font-weight:700;-webkit-mask:radial-gradient(circle 3.2px at 5px 0,#0000 96%,#000) 0 0/10px 100% repeat-x;mask:radial-gradient(circle 3.2px at 5px 0,#0000 96%,#000) 0 0/10px 100% repeat-x;transition:transform .25s var(--ease)}
%S .btn:hover{transform:rotate(-1.5deg) translateY(-2px)}
%S .btn.alt{background:color-mix(in srgb,var(--c-accent) 28%,var(--c0-card));color:var(--c0-ink)}
"""),
    dict(id="gK", nev="Klasszikus · névtábla két csavarral", reszlet="az arborétumok sötét névtáblái két réz csavarral",
         miert="Sötét tábla vékony réz kerettel és két csavarral, antikva felirattal, mint a botanikus kertek fái előtt. Rámutatva kivilágosodik.", css="""
%S .btn{padding:1em 2.15em;border-radius:6px;background-color:var(--c-deep);color:var(--c-on-deep);font-family:var(--f-display);font-weight:var(--w-display);letter-spacing:.03em;box-shadow:inset 0 0 0 2px color-mix(in srgb,var(--c-accent) 55%,transparent),0 8px 16px -10px rgba(0,0,0,.5);background-image:radial-gradient(circle at 12px 50%,color-mix(in srgb,var(--c-accent) 80%,#fff) 2.4px,transparent 3px),radial-gradient(circle at calc(100% - 12px) 50%,color-mix(in srgb,var(--c-accent) 80%,#fff) 2.4px,transparent 3px);transition:filter .2s}
%S .btn:hover{filter:brightness(1.18)}
%S .s-deep .btn{background-color:var(--c-primary);color:var(--c-on-primary)}
%S .btn.alt{background-color:var(--c0-card);color:var(--c0-ink);box-shadow:inset 0 0 0 1.5px var(--c0-line2)}
"""),
]

KARTYA = [
    dict(id="rE", nev="Elegáns · botanikus tábla", reszlet="tábla-számozás (Tab. I, II…) és kettős hajszálkeret, mint egy botanikus atlaszban",
         miert="Tiszta lap kettős hajszálkerettel, alul dőlt táblaszámmal (Tab. I, II, III), mint egy botanikus atlasz lapjai. Elegáns, sok levegővel.", css="""
%S .sec{counter-reset:tabla}
%S .krt{--kp:30px;padding:var(--kp) var(--kp) calc(var(--kp) + 16px);background:var(--c-card);border-radius:2px;box-shadow:inset 0 0 0 1px var(--c-line2),inset 0 0 0 6px var(--c-card),inset 0 0 0 7px var(--c-line2),0 18px 34px -26px rgba(0,0,0,.4);counter-increment:tabla}
%S .krt::after{content:"Tab. " counter(tabla,upper-roman);position:absolute;left:0;right:0;bottom:12px;text-align:center;font-family:var(--f-display);font-style:italic;font-size:.82rem;color:var(--c-ink-3)}
%S .krt h3{font-style:italic;font-weight:400}
%S .krt>.krt-kep{margin:calc(-1*var(--kp) + 10px) calc(-1*var(--kp) + 10px) 12px}
"""),
    dict(id="rM", nev="Modern · pauszpapír illesztőkeresztekkel", reszlet="egymásra fektetett pauszpapír-tervek illesztőkeresztjei",
         miert="Áttetsző, pauszpapírszerű lap, ami alól átdereng a háttér; két sarkán illesztőkereszt. Mint amikor a terveket egymásra fekteted. Könnyed, mai.", css="""
%S .krt{--kp:26px;padding:var(--kp);background:color-mix(in srgb,var(--c-card) 74%,transparent);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);border:1px solid color-mix(in srgb,var(--c-ink) 16%,transparent);border-radius:0}
%S .krt::before,%S .krt::after{content:"";position:absolute;width:16px;height:16px;background:linear-gradient(var(--c-accent),var(--c-accent)) center/100% 1.5px no-repeat,linear-gradient(var(--c-accent),var(--c-accent)) center/1.5px 100% no-repeat;z-index:2}
%S .krt::before{top:-8px;left:-8px}%S .krt::after{bottom:-8px;right:-8px}
%S .krt>.krt-kep{margin:calc(-1*var(--kp)) calc(-1*var(--kp)) 12px}
"""),
    dict(id="rB", nev="Merész · préri-kártya fűszegéllyel", reszlet="fűcsomó-sziluett a kártya fejében, a préri színeivel",
         miert="Erős színes fejléc, amibe alulról díszfüvek nőnek bele, alatta tiszta szövegrész. Karakteres, vidám, a díszfüves ágyásaidat idézi.", css=T("""
%S .krt{--kp:24px;padding:calc(var(--kp) + 40px) var(--kp) var(--kp);background:var(--c-card);border-radius:22px;overflow:hidden;box-shadow:var(--sh-2)}
%S .krt::before{content:"";position:absolute;left:0;right:0;top:0;height:46px;background:var(--c-primary);z-index:0}
%S .krt::after{content:"";position:absolute;left:0;right:0;top:24px;height:24px;background:var(--c-card);""" + mask("FUSZEL", "left bottom/auto 100% repeat-x") + """;z-index:0}
%S .krt>*{position:relative;z-index:1}
%S .krt .krt-fej .ik{background-color:var(--c-card);border-radius:50%;padding:8px;background-origin:content-box;box-shadow:var(--sh-1)}
""")),
    dict(id="rF", nev="Barátságos · naplólap washi-szalaggal", reszlet="washi-szalaggal beragasztott, enyhén ferde kertnapló-lap",
         miert="Fehér lap, a tetején átlátszó, színes ragasztószalag, kicsit ferdén, mintha a kertnaplódba ragasztottad volna. Rámutatva kiegyenesedik.", css="""
%S .krt{--kp:26px;padding:calc(var(--kp) + 6px) var(--kp) var(--kp);background:var(--c-card);border-radius:3px;box-shadow:0 1px 1px rgba(0,0,0,.05),0 14px 26px -18px rgba(0,0,0,.4);transform:rotate(var(--fordit,-.8deg));transition:transform .3s var(--ease)}
%S .krt:nth-child(2n){--fordit:.9deg}%S .krt:nth-child(3n){--fordit:-.4deg}
%S .krt::before{content:"";position:absolute;left:50%;top:-10px;width:86px;height:22px;margin-left:-43px;transform:rotate(-3deg);background:color-mix(in srgb,var(--c-accent) 55%,transparent);box-shadow:0 1px 2px rgba(0,0,0,.06);z-index:2}
%S .krt:hover{transform:rotate(0) translateY(-3px)}
"""),
    dict(id="rK", nev="Klasszikus · cím a névtáblán", reszlet="a kártya címe arborétumi névtáblán, két csavarral",
         miert="Tiszta krémszínű kártya sötét felső éllel; a címe egy kis sötét névtáblára kerül két csavarral, mint a fák előtt egy botanikus kertben. Rendezett, időtálló.", css="""
%S .krt{--kp:26px;padding:var(--kp);background:var(--c-card);border-radius:4px;box-shadow:inset 0 0 0 1px var(--c-line2),var(--sh-1);border-top:6px solid var(--c-deep)}
%S .krt h3{display:inline-block;padding:.3em 1.15em .34em;border-radius:5px;background-color:var(--c-deep);color:var(--c-on-deep);font-size:1.02rem;box-shadow:inset 0 0 0 1.5px color-mix(in srgb,var(--c-accent) 60%,transparent);background-image:radial-gradient(circle at 7px 50%,color-mix(in srgb,var(--c-accent) 80%,#fff) 2px,transparent 2.6px),radial-gradient(circle at calc(100% - 7px) 50%,color-mix(in srgb,var(--c-accent) 80%,#fff) 2px,transparent 2.6px)}
%S .krt>.krt-kep{margin:calc(-1*var(--kp)) calc(-1*var(--kp)) 14px}
"""),
]

FOTO = [
    dict(id="fE", nev="Elegáns · ovális tábla-kép", reszlet="ovális, kamea-szerű kivágás, mint a régi botanikus kiadványok képei",
         miert="A fotók ovális kivágásban, vékony keretes lapon, dőlt képaláírással, mint egy régi botanikus kiadványban. Finom, nyugodt.", css="""
%S .ft{padding:12px;background:var(--c-card);box-shadow:inset 0 0 0 1px var(--c-line2)}
%S .ft .ph{border-radius:50%/44%}
%S .ft figcaption{font-family:var(--f-display);font-style:italic;text-align:center;color:var(--c-ink-2);margin-top:8px}
%S .ft.krt-kep{padding:0;background:none;box-shadow:none}%S .ft.krt-kep .ph{border-radius:0}
"""),
    dict(id="fM", nev="Modern · léptékvonallal", reszlet="léptékvonal (0, 5, 10 m) a kép sarkában, mint a kerttervek lapjain",
         miert="Egyenes szélű fotók, a sarkukban kis fekete-fehér léptékvonallal, mint a kertterveken. Rendezett, szakmai, kicsit játékos.", css="""
%S .ft .ph{border-radius:0;position:relative}
%S .ft .ph::after{content:"0          5         10 m";position:absolute;left:10px;bottom:10px;width:min(128px,44%);padding-top:9px;white-space:pre;font-family:var(--f-label);font-size:.62rem;line-height:1;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.55);background:linear-gradient(90deg,#fff 0 25%,#1d1d1d 25% 50%,#fff 50% 75%,#1d1d1d 75%) 0 0/100% 5px no-repeat;pointer-events:none}
%S .ft.krt-kep .ph::after{display:none}
"""),
    dict(id="fB", nev="Merész · díszfű-él és szalmablokk", reszlet="a fotó alja díszfű-sziluettben ér véget",
         miert="A fotók alja díszfüvek sziluettjében ér véget, mögöttük egy eltolt szalmaszínű blokk. Erős, grafikus, mégis a kertből jön.", css=T("""
%S .ft .ph{border-radius:18px 18px 0 0;-webkit-mask:linear-gradient(#000,#000) top/100% calc(100% - 20px) no-repeat,""" + "@FUSZEL@" + """ bottom/auto 26px repeat-x;mask:linear-gradient(#000,#000) top/100% calc(100% - 20px) no-repeat,""" + "@FUSZEL@" + """ bottom/auto 26px repeat-x}
%S .ft::before{content:"";position:absolute;left:22px;right:-10px;top:18px;aspect-ratio:var(--ar,4/3);background:var(--c-accent2);border-radius:18px;z-index:-1}
%S .ft.krt-kep::before{display:none}%S .ft.krt-kep .ph{-webkit-mask:none;mask:none;border-radius:0}
""")),
    dict(id="fF", nev="Barátságos · kasvirággal a sarkán", reszlet="a faviconod kasvirága préselve a fotó sarkán",
         miert="Fehér keretes, kicsit megdöntött fotók kézírásos felirattal, a sarkukon egy préselt kasvirággal (a faviconod virága). Személyes, mint egy kertnapló.", css=T("""
%S .ft{background:#fff;padding:10px 10px 36px;box-shadow:var(--sh-3);border-radius:3px;transform:rotate(-1.2deg)}
%S .ft:nth-child(even){transform:rotate(1.3deg)}
%S .ft::after{content:"";position:absolute;right:-14px;top:-18px;width:60px;height:60px;background:var(--c-primary);""" + mask("KASV") + """;transform:rotate(18deg);opacity:.9;z-index:2}
%S .ft figcaption{position:absolute;left:10px;right:10px;bottom:7px;font-family:var(--f-hand);font-size:calc(var(--fs-hand)*.92rem);line-height:1.6;color:#3b3b3b;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
%S .ft.krt-kep{background:none;padding:0;box-shadow:none;transform:none;border-radius:0}%S .ft.krt-kep::after{display:none}
""")),
    dict(id="fK", nev="Klasszikus · üvegház-boltív", reszlet="üvegház-boltív osztókkal, mint egy botanikus kert pálmaházán",
         miert="A fotók boltíves ablakként, fent vékony osztókkal, mint egy régi botanikus kert üvegházán. Méltóságteljes, nyugodt.", css="""
%S .ft .ph{border-radius:999px 999px 6px 6px}
%S .ft::after{content:"";position:absolute;inset:0 0 auto 0;aspect-ratio:var(--ar,4/3);border-radius:999px 999px 6px 6px;box-shadow:inset 0 0 0 6px var(--c-card),inset 0 0 0 7px var(--c-line2);background:linear-gradient(var(--c-card),var(--c-card)) 50% 0/4px 30% no-repeat,linear-gradient(var(--c-card),var(--c-card)) 0 30%/100% 4px no-repeat;opacity:.92;pointer-events:none}
%S .ft.krt-kep::after{display:none}%S .ft.krt-kep .ph{border-radius:0}
"""),
]

MOZGAS_SAJAT = [
    dict(id="mW", nev="Merész · szélben hajló fű", miert="Az elemek alulról, kicsit megdőlve érkeznek, és rugalmasan kiegyenesednek, mint a díszfű a szélben. Élénk, a préri ritmusa.", css="""
%S.js-rv [data-rv]{opacity:0;transform:translateY(34px) skewX(7deg);transform-origin:50% 100%;transition:opacity .6s ease,transform 1.1s cubic-bezier(.2,1.5,.35,1);transition-delay:calc(var(--i)*80ms)}
%S.js-rv [data-rv].in{opacity:1;transform:none}
"""),
    dict(id="mB", nev="Barátságos · kibomló bimbó", miert="Az elemek enyhén elmosódva, kicsit megdöntve „kinyílnak”, mint egy bimbó, aztán élesre állnak. Élő, kedves, nem kapkodó.", css="""
%S.js-rv [data-rv]{opacity:0;transform:scale(.94) rotate(-1.2deg);filter:blur(5px);transform-origin:50% 100%;transition:opacity .8s ease,transform 1.1s cubic-bezier(.2,1.25,.35,1),filter .9s ease;transition-delay:calc(var(--i)*90ms)}
%S.js-rv [data-rv].in{opacity:1;transform:none;filter:none}
"""),
]
MOZGAS_MIERT = {
    "m1": "Elegáns · az elemek lassan, finoman úsznak be, a díszek ráérősen lebegnek. Pihentető, mint egy botanikus album lapozása.",
    "m2": "Modern · egymás után, pontosan a helyükre emelkednek be az elemek, mint a rétegek egy terven. Friss, rendezett.",
    "mW": MOZGAS_SAJAT[0]["miert"],
    "mB": MOZGAS_SAJAT[1]["miert"],
    "m5": "Klasszikus · nincs beúszás és lebegés, csak apró visszajelzések rámutatáskor. Gyors, akadálymentes, nyugodt, mint egy séta az arborétumban.",
}

# ------------------------------------------------------------------ TÉMA-ELEMEK (kerttervezés): textúra, dekor, határ

FELULET = [
    dict(id="tL1", nev="Szintvonalak", miert="Halvány, egymásba simuló szintvonalak, mint egy tájépítészeti felmérési terven a domborzat. Nyugodt, szakmai, rögtön a terepet idézi.", css=T("""
%S .tx::before{background-color:var(--c-primary);""" + mask("SZINT", "center/cover no-repeat") + """;opacity:.14}
%S .s-deep.tx::before{background-color:var(--c-deep-hl);opacity:.12}
%S .s-primary.tx::before{background-color:var(--c-on-primary);opacity:.1}
""")),
    dict(id="tL2", nev="Kertterv-jelek", miert="A kerttervek felülnézeti jelei szórva: lombkorona-körök, tűlevelű, cserjecsoport, lépőkövek, évelő-pöttyök. Csak egy tájépítésznél van értelme.", css=T("""
%S .tx::before{background-color:var(--c-primary);""" + mask("KTJ", "0 0/320px 320px repeat") + """;opacity:.14}
%S .tx::after{content:"";position:absolute;inset:0;pointer-events:none;z-index:0;background:radial-gradient(ellipse 58% 52% at 50% 46%,var(--sec-bg,var(--c-paper)) 22%,transparent 78%)}
%S .s-deep.tx::before{background-color:var(--c-deep-hl);opacity:.13}
""")),
    dict(id="tL3", nev="Díszfüvek alulról", miert="A szekciók alján halvány fűszálak és virágfejek nőnek fel, mint egy természetközeli évelőágyás széle.", css=T("""
%S .tx::before{background-color:var(--c-primary);""" + mask("FUSZ", "center bottom/100% min(46%,250px) no-repeat") + """;opacity:.17}
%S .s-deep.tx::before{background-color:var(--c-deep-hl);opacity:.15}
""")),
    dict(id="tL4", nev="Milliméterpapír", miert="Finom tervezőpapír-rács, a szélek felé erősödve, középen elhalványulva, mint egy kerttervlap alapja.", css=T("""
%S .tx::before{background-color:var(--c-primary);""" + mask("MM", "0 0/60px 60px repeat") + """;opacity:.14}
%S .tx::after{content:"";position:absolute;inset:0;pointer-events:none;z-index:0;background:radial-gradient(ellipse 62% 56% at 50% 48%,var(--sec-bg,var(--c-paper)) 30%,transparent 80%)}
%S .s-deep.tx::before{background-color:var(--c-deep-hl);opacity:.11}
""")),
    dict(id="tL5", nev="Herbárium-levelek", miert="Préselt levelek vékony körvonalai (tölgy, ginkgó, páfrány) szórva, nagyon halványan. Botanikus, kézzel rajzolt hangulat.", css=T("""
%S .tx::before{background-color:var(--c-ink);""" + mask("LEVELEK", "0 0/640px 640px repeat") + """;opacity:.1}
%S .s-deep.tx::before{background-color:var(--c-on-deep);opacity:.09}
""")),
]

DEKOR = [
    dict(id="dL1", nev="Lepkék és méhek", miert="Két lepke és egy méh lassan száll a szekciók sarkaiban, ahogy írod: a madaraktól a méheken, lepkéken át sok élőlény talál otthonra a kertben. Élő, mégsem tolakodó.", css=T("""
%S .dk-a,%S .dk-b{display:block;width:var(--s,44px);aspect-ratio:1;background:var(--c-accent);""" + mask("LEPKE") + """;opacity:.75;animation:%Kszall 11s ease-in-out infinite}
%S .dk-a{--s:48px;left:4%;top:14%}
%S .dk-b{--s:32px;right:6%;top:24%;background:var(--c-primary);opacity:.55;animation-duration:14s;animation-delay:-5s}
%S .dk-c{display:block;width:36px;aspect-ratio:1;right:11%;bottom:14%;background:var(--c-ink-2);""" + mask("MEH") + """;opacity:.5;animation:%Kmeh 7s ease-in-out infinite alternate}
@keyframes %Kszall{0%{transform:translate(0,0) rotate(-8deg) scaleX(1)}22%{transform:translate(18px,-14px) rotate(4deg) scaleX(1)}25%{transform:translate(20px,-15px) rotate(4deg) scaleX(.45)}28%{transform:translate(22px,-16px) rotate(4deg) scaleX(1)}55%{transform:translate(42px,-4px) rotate(10deg) scaleX(1)}58%{transform:translate(44px,-3px) rotate(10deg) scaleX(.5)}61%{transform:translate(46px,-2px) rotate(10deg) scaleX(1)}100%{transform:translate(0,0) rotate(-8deg) scaleX(1)}}
@keyframes %Kmeh{from{transform:translate(0,0) rotate(-6deg)}to{transform:translate(-26px,-12px) rotate(6deg)}}
%S .s-deep .dk-c{background:var(--c-on-deep-2)}
@container elo (max-width:340px){%S .dk-a,%S .dk-b,%S .dk-c{display:none}}
""")),
    dict(id="dL2", nev="Óriás kasvirág", miert="A faviconod kasvirága hatalmas méretben, alig láthatóan, nagyon lassan forog a szekciók sarkában. Nyugodt, elegáns márkaépítés.", css=T("""
%S .dk-jel{display:block;width:clamp(240px,34cqi,460px);aspect-ratio:1;right:-5%;top:-8%;background:var(--c-primary);""" + mask("KASV") + """;opacity:.1;animation:%Kfor 160s linear infinite}
%S .s-deep .dk-jel{background:var(--c-deep-hl);opacity:.13}
%S .s-primary .dk-jel{background:var(--c-on-primary);opacity:.12}
@keyframes %Kfor{to{transform:rotate(360deg)}}
""")),
    dict(id="dL3", nev="Évszak-jelek", miert="Hópehely, virág, nap és juharlevél lebeg a sarkokban, a „Változatosság télen-nyáron” rajzod négy jele. Játékos, de rendezett.", css=T("""
%S .dk-a,%S .dk-b,%S .dk-c,%S .dk-r{display:block;aspect-ratio:1;opacity:.45;animation:%Klebeg 10s ease-in-out infinite alternate}
%S .dk-a{width:40px;left:4%;top:13%;background:var(--c-ink-3);""" + mask("HOPE") + """}
%S .dk-b{width:38px;right:5%;top:17%;background:var(--c-accent);""" + mask("VIRAG") + """;animation-delay:-3s}
%S .dk-c{width:46px;right:9%;bottom:12%;background:color-mix(in srgb,#E2B04A 75%,var(--c-accent));""" + mask("NAP") + """;animation-duration:13s}
%S .dk-r{width:40px;left:7%;bottom:14%;background:var(--c-primary);""" + mask("JUHAR") + """;animation-delay:-6s}
%S .s-deep .dk-a{background:var(--c-on-deep-2)}%S .s-deep .dk-r{background:var(--c-deep-hl)}
@keyframes %Klebeg{from{transform:translateY(0) rotate(-10deg)}to{transform:translateY(-12px) rotate(10deg)}}
@container elo (max-width:340px){%S .dk-a,%S .dk-b,%S .dk-c,%S .dk-r{display:none}}
""")),
    dict(id="dL4", nev="Ceruzarajzok a sarkokban", miert="A mostani oldalad ceruzarajzai (tulipán, ág, varjúháj) bukkannak elő a szekciók sarkaiban, mintha a lap szélére rajzoltad volna. A legszemélyesebb díszítés.", css=T("""
%S .dk-a,%S .dk-b,%S .dk-c{display:block;background:var(--c-ink);opacity:.36}
%S .dk-a{width:clamp(130px,16cqi,210px);aspect-ratio:@TULIP_AR@;left:2.5%;bottom:9%;""" + mask("TULIP") + """;transform:rotate(-12deg)}
%S .dk-b{width:clamp(120px,14cqi,180px);aspect-ratio:@AGRAJZ_AR@;right:3%;top:10%;""" + mask("AGRAJZ") + """;transform:rotate(7deg)}
%S .dk-c{width:clamp(80px,9cqi,124px);aspect-ratio:@SEDUM_AR@;right:5%;bottom:7%;""" + mask("SEDUM") + """;opacity:.3}
%S .s-deep .dk-a,%S .s-deep .dk-b,%S .s-deep .dk-c{background:var(--c-on-deep);opacity:.3}
@container elo (max-width:340px){%S .dk-a,%S .dk-b,%S .dk-c{display:none}}
""")),
    dict(id="dL5", nev="Növénycímkék", miert="A kertészetben a növények mellé szúrt fa címkék a sarkokban, rajtuk kézírással két valódi ígéreted: ingyenes konzultáció, korlátlan áttervezés.", css="""
%S .dk-a,%S .dk-b{display:block;width:112px;height:150px;filter:drop-shadow(0 8px 10px rgba(0,0,0,.16));transform-origin:50% 100%;animation:%Kbillen 9s ease-in-out infinite alternate}
%S .dk-a::before,%S .dk-b::before{content:"";position:absolute;inset:0;background:color-mix(in srgb,#EFE3CB 86%,var(--c-accent));clip-path:polygon(0 6%,6% 0,94% 0,100% 6%,100% 54%,64% 60%,64% 90%,50% 100%,36% 90%,36% 60%,0 54%)}
%S .dk-a::after,%S .dk-b::after{position:absolute;left:8%;right:8%;top:7%;height:44%;display:grid;place-items:center;text-align:center;font-family:var(--f-hand);font-size:calc(var(--fs-hand)*.86rem);line-height:1.02;color:#3b3326}
%S .dk-a::after{content:"Ingyenes konzultáció"}%S .dk-b::after{content:"Korlátlan áttervezés"}
%S .dk-a{right:4.5%;top:8%;--r:7deg}%S .dk-b{left:3.5%;bottom:6%;--r:-6deg;animation-delay:-4s}
@keyframes %Kbillen{from{transform:rotate(var(--r))}to{transform:rotate(calc(var(--r)*-.4))}}
@container elo (max-width:700px){%S .dk-a,%S .dk-b{width:84px;height:112px}%S .dk-a::after,%S .dk-b::after{font-size:calc(var(--fs-hand)*.66rem)}}
@container elo (max-width:340px){%S .dk-a,%S .dk-b{display:none}}
"""),
]

HATAR = [
    dict(id="sL1", nev="Fűszál-él", miert="A szekciók egy sűrű fűszál-sorral érnek össze, mintha a következő blokk a gyepből nőne ki. Természetes, élő.", css=T("""
%S .hat{top:-43px;height:44px;background:var(--sec-bg);""" + mask("FUSZEL", "0 100%/360px 44px repeat-x") + """}
%S .hat.masod{-webkit-mask-position:180px 100%;mask-position:180px 100%}
""")),
    dict(id="sL2", nev="Dombvonal", miert="Kétrétegű, lágy dombvonal a szekciók között: egy halványabb hátsó és egy teltebb első domb, mint egy tájkép látóhatára.", css=T("""
%S .hat{top:-59px;height:60px;background:var(--sec-bg);""" + mask("DOMB", "center bottom/100% 100% no-repeat") + """}
%S .hat.masod{transform:scaleX(-1)}
""")),
    dict(id="sL3", nev="Cserjeszegély", miert="Hullámos, felhős él, ahogy a tájépítészek a cserjék és a lombkoronák szélét rajzolják a terveken. Puha, rendezett.", css=T("""
%S .hat{top:-31px;height:32px;background:var(--sec-bg);""" + mask("CSERJE", "0 100%/300px 32px repeat-x") + """}
%S .hat.masod{-webkit-mask-position:150px 100%;mask-position:150px 100%}
""")),
    dict(id="sL4", nev="Léckerítés", miert="Alacsony léckerítés sziluettje a szekciók határán, a következő blokk színében, mint az előkertek kerítése a rajzodon. Bájos, otthonos.", css=T("""
%S .hat{top:-45px;height:46px;background:var(--sec-bg);""" + mask("KERITES", "0 100%/34px 46px repeat-x") + """}
""")),
    dict(id="sL5", nev="Ceruzás mezőrajz", miert="A mostani láblécedben lévő ceruzás virágmező fut végig a szekciók határán, mintha a lap szélére rajzoltad volna.", css=T("""
%S .hat{top:-54px;height:64px;background:var(--c-ink-3);""" + mask("MEZO", "0 100%/auto 64px repeat-x") + """;opacity:.8}
%S .hat.masod{-webkit-mask-position:220px 100%;mask-position:220px 100%}
""")),
]

STILUS = {"cim": CIM, "alcim": ALCIM, "gomb": GOMB, "kartya": KARTYA, "foto": FOTO, "felulet": FELULET, "dekor": DEKOR, "hatar": HATAR}
AJANLOTT = {"paletta": "pK", "betu": "bK", "ikon": "iF", "cim": "cF", "alcim": "kE", "gomb": "gK", "kartya": "rE", "foto": "fF",
            "felulet": "tL1", "dekor": "dL1", "hatar": "sL3", "mozgas": "mB"}

# ------------------------------------------------------------------ TARTALOM (minden tény a koppanylili.hu-ról)

KAPCSOLAT = {"telefon": "+36 30 756 8997", "email": "hello@koppanylili.hu", "cim": "",
             "nyitvatartas": [["Visszahívás", "2 munkanapon belül"], ["E-mailre válasz", "2 napon belül"], ["Helyszíni konzultáció", "ingyenes"]],
             "nyitva_cim": "Mire számíthatsz", "nyitva_rovid": "Visszahívás 2 munkanapon belül"}

GARANCIAK = [
    {"cim": "Határidők betartása", "szoveg": "Az előre megbeszélt időpontban meg fogod kapni a terveket.", "ikon": "hatarido"},
    {"cim": "Gyors válasz", "szoveg": "Ha nem érsz el telefonon, két munkanapon belül visszahívlak. Az emailjeidre szintén két napon belül válaszolok.", "ikon": "valasz"},
    {"cim": "Korlátlan áttervezés", "szoveg": "Ha nem tetszik a terv, amit kapsz, addig módosítjuk majd, amíg elégedett nem leszel az eredménnyel.", "ikon": "atterv"},
]

GYIK = [
    ("Mennyibe kerül egy kert megtervezése?", [
        "A teljes kert megtervezése általában 200-350 ezer forint között mozog, függ a telek méretétől, a tervek részletezettségétől, a megrendelői igényektől. Természetesen egy kisebb kertrészlet vagy növényágy tervezése, kertfelújítás terve ennél lényegesen olcsóbb."]),
    ("Miért terveztessem meg a kertem, ha én is ki tudom találni, mit szeretnék?", [
        "2 ok miatt javaslom, hogy szakembert bízz meg a kerted tervezésével:",
        "**1) Nem fog kihalni 1-2 év alatt, azaz végül pénzt spórolsz a szakemberrel.** Nem mindegy, hogyan válogatod össze a növényeket. Szempont, hogy a növényeid igényei megfeleljenek a kerted adottságainak (talaj típusa, fényellátottság, csapadék/öntözés mennyisége, telek lejtése, stb.). Fontos az is, hogy mit mivel kombinálhatsz, hogy ne szorítsák ki egymást.",
        "Ha ezt nem veszed figyelembe, 1-2 év alatt kihalhatnak a növények és az összes rászánt időt és pénzt elpazaroltad.",
        "**2) 4 évszakos szépséghez komoly szakmai tudás szükséges.** Mindenki el tudja dönteni, mit talál szépnek, amikor épp virágzik. De egy kertnek nem csak pár hétig kell jól mutatnia, hanem egész évben. Itt jön képbe a tájépítészeti szaktudás, melynek birtokában olyan kertek is tervezhetőek, amelyekben nincsenek „unalmas” időszakok és a kerted mindig jól mutat.",
        "Jó kertet tervezni összetett feladat, ezért érdemes tervezőt bevonni a folyamatba, hogy ne próba-szerencse alapon működjön a folyamat, hanem átgondolt szempontrendszer mentén."]),
    ("Miért ne bízzam a kerttervezést is egy kertépítő cégre?", [
        "Praktikusnak tűnhet a tervezést és a kertépítést is egy kivitelező cégre bízni, két legyet ütve egy csapásra. A kertépítéssel foglalkozó cégek azonban – tisztelet a kivételnek – általában abban érdekeltek, hogy minél egyszerűbben megépíthető kertet tervezzenek Neked, a saját jól bevált, mindenhol alkalmazott gyakorlataikat bevetve.",
        "Ha a burkolat, gyepszőnyeg és bele néhány, mulcshalomban vagy murvasivatagban szomorkodó tuja kombinációjánál valami egyedibbet szeretnél, akkor érdemes egy tájépítész segítségét igénybe venned. Így a tervezést nem a kivitelezés szokványos gyakorlata fogja meghatározni, hanem jól átgondolt szakmai szempontrendszer, a kerted adottságaihoz és a Te személyes preferenciáidhoz igazítva."]),
    ("Érdemes-e saját kezűleg kivitelezni a kertemet?", [
        "Ha csak kisebb átalakításokat végzel, vagy néhány ágyást tervezel, és egyébként szívesen barkácsolsz, kertészkedsz, akkor valószínűleg örömöd telik majd az alkotás folyamatában és az eredményben is. Az ültetésben szívesen vállalom, hogy segédkezem, keress bátran ezzel kapcsolatban.",
        "Ha nem sürget semmi, és nem szempont, hogy belátható időn belül kész legyen a kerted, hanem apránként, több évre ütemezve alakítanád ki a vágyott kertet, akkor nyugodtan vágj bele az építgetésbe.",
        "Ha egy teljes, új kertről van szó, és szeretnéd egyben letudni a munkálatokat, akkor mindenképp bízd egy szakképzett csapatra a kivitelezést. A ráfordított összeg meg fog térülni, mert keservesen összebarkácsolt, tákolt hatású kert helyett profi eredményt kapsz."]),
]

AJANLATKERES = {
    "kicker": "Ajánlatkérés", "cim": "Kérj árajánlatot vagy ==ingyenes helyszíni konzultációt==",
    "menete": "Az árajánlatkérés / helyszíni konzultáció menete",
    "lepesek": [
        "Töltsd ki az űrlapot.",
        "Megnézem az űrlapon megadott adatokat és ezek alapján visszajelzek, hogy tudok-e segíteni neked. Nem minden munkát tudok elvállalni, de minden esetben visszajelzek.",
        "Ha szükséges, ingyenes helyszíni konzultáció keretében megismerkedem Veled és a kerteddel, megbeszéljük az igényeidet és a lehetőségeket.",
        "Ezután egy héten belül emailben kapni fogsz tőlem egy árajánlatot a közös munkához."],
    "doboz_cim": "Kötelezettségmentes helyszíni konzultáció – nincs mit veszítened",
    "doboz": "Ha úgy döntesz, hogy nem szeretnél velem dolgozni, a helyszíni konzultációért akkor sem fogok utólagosan díjat felszámolni.",
}


def tartalom():
    return {
        "verzio": 1,
        "marka": {"nev": "Koppány Lili", "szlogen": "…amit annyira szeretsz, hogy be sem akarsz többé menni a házba…",
                  "slug": "koppanylili", "url": "https://koppanylili.hu/"},
        "seo": {"title": "Koppány Lili · tájépítészmérnök · minimális fenntartású, természethű kertek",
                "description": "Minimális fenntartási igényű, természethű kertek tervezése. Ingyenes helyszíni konzultáció."},
        "logo": {"fajl": B + "Logo.png"},
        "profil": {"osszefoglalo": (
            "Koppány Lili okleveles tájépítészmérnök: minimális fenntartási igényű, természethű kerteket tervez. "
            "A mostani oldal zsályazöld (#ADCE8A) és púderrózsa színekkel, nagybetűs Montserrat címekkel és egy kézírásos sorral dolgozik; a legszebb benne a sok kézzel rajzolt "
            "ceruzarajz (kertterv, évelőágyás, házikó, évszakok) és a KL-monogram. Az alap-elemekből 5 eltérő karakterű, de mind Lilire hangolt változat készült; a háttér, a díszítés "
            "és a szekcióhatárok a kerttervezés világából jönnek: szintvonalak, kertterv-jelek, díszfüvek, lepkék, cserjeszegély. A szekciók a mostani főoldal sorrendjét követik."),
            "talalt_szinek": ["#ADCE8A", "#D1BEB9", "#E8DFDD", "#707070"], "talalt_betuk": ["Montserrat", "Karla", "La Belle Aurore"],
            "motivumok": "Kerttervezés: szintvonal, lombkorona- és cserjejel, díszfű, kasvirág, lepke, méh, évszakok, a mostani oldal ceruzarajzai."},
        "motivum": {
            "formak": {"level": '<path d="M50 6C78 24 84 62 50 94 16 62 22 24 50 6z"/>',
                       "virag": "".join(f'<ellipse cx="50" cy="27" rx="12" ry="21" transform="rotate({k * 72} 50 50)"/>' for k in range(5)) + '<circle cx="50" cy="50" r="11"/>',
                       "fa": f'<path d="{felho(50, 50, 40, 9)}"/>'},
            "jel": "virag",
            "szellemszavak": {"hero": "KERT", "tenyek": "TERMÉSZET", "kinalat": "TERVEZÉS", "folyamat": "LÉPÉSEK", "tortenet": "LILI",
                              "latogatas": "KAPCSOLAT", "garancia": "GARANCIA", "gyik": "KÉRDÉSEK", "ajanlatkeres": "AJÁNLAT"},
            "ticker": ["Minimális fenntartás", "Változatosság télen-nyáron", "Ökologikus szemlélet", "Ingyenes helyszíni konzultáció",
                       "Korlátlan áttervezés"],
            "matricak": ["Ingyenes konzultáció", "Korlátlan áttervezés", "Évszakról évszakra"],
        },
        "fotok": {
            "vlinderhof": {"fajl": B + "bg-vlinderhof.jpg", "alt": "Természetközeli évelőágyás ösvénnyel (forrás: vlinderhof.com)", "pozicio": "50% 62%", "max": 1400},
            "gyep": {"fajl": B + "bg-viragos-gyep.jpg", "alt": "Virágos gyep", "pozicio": "50% 60%", "max": 1100},
            "evelo": {"fajl": B + "bg-IMG_4013-2-1.jpg", "alt": "Dúsan virágzó évelőágyás", "pozicio": "50% 50%", "max": 1400},
            "tolgy": {"fajl": B + "IMG_1587-1.jpg", "alt": "A bátaszéki 3-400 éves molyhos tölgy", "pozicio": "50% 45%"},
            "lili_fa": {"fajl": B + "IMG_1586-1-1-1.jpg", "alt": "Koppány Lili egy idős tölgyfát ölel", "pozicio": "50% 58%"},
            "lili_mezo": {"fajl": B + "IMG_1582-1-700x525.jpg", "alt": "Koppány Lili a szabadban", "pozicio": "55% 40%"},
            "lili_portre": {"fajl": B + "magamrol-2-1.jpg", "alt": "Koppány Lili szobanövényekkel", "pozicio": "50% 28%", "max": 900},
            "lili_tulipan": {"fajl": B + "bg-igazolvanykep.jpg", "alt": "Koppány Lili mosolyog egy tulipános kertben", "pozicio": "50% 26%", "max": 900},
            "rajz_fa": {"fajl": B + "Untitled_Artwork4-pmqkyl5r3k96ge0c8tfrvhmwgaa1px3viaa6k8119c.png", "alt": "Ceruzarajz: fa és évelőágyás", "max": 520},
            "rajz_sedum": {"fajl": B + "sedum.png", "alt": "Ceruzarajz: virágzó szár", "max": 420},
        },
        "kapcsolat": KAPCSOLAT,
        "nav": {"linkek": [["Szolgáltatások", "#kinalat"], ["Tervezés menete", "#folyamat"], ["Rólam", "#rolunk"], ["Ajánlatkérés", "#ajanlatkeres"], ["Kapcsolat", "#kapcsolat"]],
                "cta": {"szoveg": "Ajánlatkérés", "href": "#ajanlatkeres", "ikon": "nyil"}, "nev_mutat": False},
        "hero": {"kicker": "Koppány Lili · okleveles tájépítészmérnök",
                 "meta": "Minimális fenntartás · **Változatosság télen-nyáron** · Ökologikus szemlélet",
                 "badgek": [{"ikon": "pipa", "szoveg": "Minimális fenntartás"}, {"ikon": "pipa", "szoveg": "Változatosság télen-nyáron"}, {"ikon": "pipa", "szoveg": "Ökologikus szemlélet"}],
                 "cim": "A kerted, amit ==annyira szeretsz,== hogy be sem akarsz többé menni a házba",
                 "lead": "Minimális fenntartási igényű, természethű kertek tervezése, ahol otthon érzed magad, és minden évszakra rácsodálkozol.",
                 "cta1": {"szoveg": "Mit tud egy ilyen kert?", "href": "https://koppanylili.hu/rolam/"},
                 "cta2": {"szoveg": "Ingyenes konzultáció", "href": "#ajanlatkeres", "ikon": "le"},
                 "jegyzet": "fa nélkül nem kert a kert",
                 "statok": [["Ingyenes", "helyszíni konzultáció"], ["2 munkanap", "alatt visszahívlak"], ["Korlátlan", "áttervezés"]],
                 "fotok": ["vlinderhof", "lili_fa", "gyep", "evelo"],
                 "fotok_h1": ["vlinderhof", "lili_portre", "gyep"], "fotok_h5": ["vlinderhof"], "fotok_h6": ["gyep", "lili_mezo", "evelo", "tolgy"],
                 "kiemelt": {"ikon": "okologikus", "cim": "Kötelezettségmentes konzultáció", "szoveg": "nincs mit veszítened"}},
        "folyamat": {"kicker": "Lépésről lépésre", "cim": "A ==kerttervezés== menete",
                     "lead": "Minden kert teljesen más történet. Megrendelőként mégis joggal szeretnéd tudni, milyen folyamat vezet odáig, hogy a kezedbe vehesd a kerted kész terveit.",
                     "lepesek": [
                         {"ikon": "valasz", "cim": "Előzetes egyeztetés", "szoveg": "Telefonon vagy emailben röviden vázolod a kerted adottságait és azt, hogy mit szeretnél. Ha tudsz, küldj fotókat és alaprajzot."},
                         {"ikon": "felmeres", "cim": "Helyszíni konzultáció és felmérés", "szoveg": "Felkeresem a kertedet, megbeszéljük az igényeidet és a telek adottságait. A konzultációért nem számolok fel díjat."},
                         {"ikon": "hatarido", "cim": "Árajánlat és szerződés", "szoveg": "A konzultáció után elküldöm az árajánlatot és a vállalt határidőket. Ha elfogadod, szerződést kötünk."},
                         {"ikon": "atterv", "cim": "Funkcióvázlat és vázlattervek", "szoveg": "Előbb a téralakítás rajza, aztán kétféle vázlatterv. Addig módosítom, amíg elégedett nem leszel."},
                         {"ikon": "tervcsomag", "cim": "Végleges tervcsomag", "szoveg": "Kertterv, részlettervek, növénykiültetési terv, növénylista, anyagkiírás és fenntartási kézikönyv."}]},
        "kinalat": {"kicker": "Szolgáltatások", "cim": "Miben tudok ==segíteni?==",
                    "cta": {"szoveg": "Kérj ajánlatot", "href": "#ajanlatkeres"},
                    "elemek": [
                        {"nev": "Tanácsadás", "ikon": "tanacsadas", "csoport": "Miben segítek?", "leiras": "Ha kérdésed merült fel a kerteddel kapcsolatban, nyugodtan keress; az ültetésben is szívesen segédkezem."},
                        {"nev": "Növényágyak, kertrészletek tervezése", "ikon": "novenyagy", "foto": "evelo", "csoport": "Miben segítek?", "leiras": "Egy kisebb kertrészlet vagy növényágy terve, akár egy kertfelújításhoz."},
                        {"nev": "Kerttervezés", "ikon": "kertterv", "csoport": "Miben segítek?", "leiras": "A teljes kert terve, a funkcióvázlattól a növénykiültetési tervig.", "ar": "ált. 200-350 ezer Ft"},
                        {"nev": "Családi házak kertje", "ikon": "csaladi_haz", "csoport": "Milyen kertekben?"},
                        {"nev": "Társasházak kertje", "ikon": "tarsashaz", "csoport": "Milyen kertekben?"},
                        {"nev": "Előkertek", "ikon": "elokert", "csoport": "Milyen kertekben?"}]},
        "tenyek": {"kicker": "Ilyen lesz a kerted", "cim": "Miért ==válassz engem?==",
                   "elemek": [
                       {"ikon": "fenntartas", "cim": "Minimális fenntartás", "szoveg": "Nem sok munkád lesz a kerteddel, mégis gyönyörű marad – felejtsd el az állandó gyomlálást és a folyamatos öntözést!"},
                       {"ikon": "evszakok", "cim": "Változatosság télen-nyáron", "szoveg": "Minden évszakban látványos, más-más arcát mutató kerted lesz, tele meglepetésekkel – mindig lesz miben gyönyörködnöd."},
                       {"ikon": "okologikus", "cim": "Ökologikus szemlélet", "szoveg": "A kerteddel támogatod a biodiverzitást, a madaraktól a méheken, lepkéken át sok-sok élőlény talál majd otthonra Nálad, egy kis darab újragondolt természetben."}]},
        "garancia": {"kicker": "Garancia", "cim": "Amire ==garanciát vállalok=="},
        "tortenet": {"kicker": "Rólam", "cim": "Szia, ==Lili vagyok==",
                     "bekezdesek": [
                         "Koppány Lili vagyok, okleveles tájépítészmérnök, és a növények eltökélt híve. Hiszek abban, hogy mindenkinek lehet gyönyörű kertje, még akkor is, ha nincs sok ideje foglalkozni vele, és kertészt sem fizetne.",
                         "Tudatos, a kertünk adottságainak megfelelő növények kiválasztásával, a növények számára megfelelő fenntartás biztosításával a hagyományos kerti munka nagy részét megspórolhatjuk magunknak. Ebben szeretnék a segítségedre lenni."],
                     "idezet": "Mindenkinek kellene egy kert. Akkor is, ha elfoglalt.",
                     "alairas": {"nev": "Koppány Lili", "szerep": "okleveles tájépítészmérnök"},
                     "fotok": ["lili_portre", "lili_fa", "tolgy"],
                     "fotok_felirat": ["Koppány Lili", "Ennyire szeretem a fákat", "A bátaszéki 3-400 éves molyhos tölgy"],
                     "merfoldkovek": [["3 évesen", "virágkötő akartam lenni, hála a sarki virágboltos Áginak"],
                                      ["Diploma", "okleveles tájépítészmérnök lettem"],
                                      ["2,5 év", "egy tájépítész irodában, közparkok tervezésében"],
                                      ["Váltás", "belevágtam a kerttervezésbe, hogy a növényekkel foglalkozhassak"],
                                      ["Most", "favizsgáló és faápoló szakmérnöknek tanulok, posztgraduális képzésen"]]},
        "gyik": {"kicker": "GYIK", "cim": "Gyakori ==kérdések=="},
        "ajanlatkeres": AJANLATKERES,
        "latogatas": {"kicker": "Kapcsolat", "cim": "Kapcsolat és ==elérhetőség==",
                      "lead": "Ha kérdésed merült fel, nyugodtan keress – akár írásban, akár telefonon örömmel veszem fel Veled a kapcsolatot.",
                      "cta1": {"szoveg": "Hívj most", "href": "tel:+36307568997", "ikon": "tel"},
                      "cta2": {"szoveg": "Írj e-mailt", "href": "mailto:hello@koppanylili.hu", "ikon": "mail"},
                      "foto": "lili_tulipan"},
        "lablec": {"szoveg": "Minimális fenntartási igényű, természethű kertek tervezése.",
                   "cegnev": "Koppány Lili", "felhivas": "Kérj ingyenes ==helyszíni konzultációt==",
                   "linkek": [["Szolgáltatások", "#kinalat"], ["Tervezés menete", "#folyamat"], ["Rólam", "#rolunk"], ["GYIK", "#gyik"], ["Ajánlatkérés", "#ajanlatkeres"]],
                   "jogi": [["Adatkezelési tájékoztató", "https://koppanylili.hu/adatkezelesi-tajekoztato/"], ["ÁSZF", "https://koppanylili.hu/aszf/"]]},
        "ikonok": {"spec": "ikon-spec.json"},
        "szekcio_sorrend": ["nav", "hero", "folyamat", "kinalat", "tenyek", "garancia", "tortenet", "gyik", "ajanlatkeres", "latogatas", "lablec"],
        "egyedi_szekciok": {"garancia": {"nev": "Garanciák", "leiras": "Amire garanciát vállalok: határidő, gyors válasz, korlátlan áttervezés."},
                            "gyik": {"nev": "GYIK", "leiras": "Gyakori kérdések: ár, miért tervező, kertépítő cég, saját kivitelezés."},
                            "ajanlatkeres": {"nev": "Ajánlatkérés", "leiras": "Az ajánlatkérés menete, a kötelezettségmentes konzultáció és az űrlap."}},
    }


def ctx_epit(spec):
    """Ugyanaz a környezet, amivel a motor a szekciókat rendereli (fotók, logó-arány)."""
    c = {k: v for k, v in spec.items()}
    im = Image.open(ITT / spec["logo"]["fajl"]).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox()
    c["_logo"] = {"ar": f"{bb[2] - bb[0]}/{bb[3] - bb[1]}", "feher": True}
    return c


def _p(lst):
    return "".join(f"<p>{md(x)}</p>" for x in lst)


def _kin_lab(c):
    b = btn(c["kinalat"].get("cta"))
    return f'<div class="lab">{b}</div>' if b else ""


RAJZ_PH = ".rz .ph{background-color:transparent!important;background-size:contain!important;background-repeat:no-repeat;box-shadow:none!important;border-radius:0!important}"

# ------------------------------------------------------------------ HERO: tervlap (csak nektek)


def _hx1(c):
    h = c["hero"]
    return (f'<section class="sec v-hx1 s-paper tx" id="top">{dk(c, "hero")}<div class="wrap grid">'
            f'<div class="txt bal" data-rv>{kick(h.get("kicker"))}<h1 class="hcim">{md(h["cim"])}</h1>'
            f'<p class="lead">{md(h["lead"])}</p>{gombsor(h)}<p class="kezi jegyzet">{md(h["jegyzet"])}</p></div>'
            f'<div class="lap" data-rv><div class="papir"><div class="kep">{ph(c, "vlinderhof")}</div>'
            f'<div class="rajz rz">{ph(c, "rajz_fa")}</div>'
            f'<span class="eszak" aria-hidden="true"><i></i><b>É</b></span>'
            f'<div class="szm"><div><span class="mono">Tervező</span><b>Koppány Lili</b><small>okleveles tájépítészmérnök</small></div>'
            f'<div><span class="mono">Konzultáció</span><b>Ingyenes</b><small>a helyszínen, kötelezettség nélkül</small></div>'
            f'<div class="lgo">{logo(c, 24, "ko")}</div></div></div></div></div></section>')


HX1_CSS = RAJZ_PH.replace(".rz", ".v-hx1 .rz") + r"""
.v-hx1{padding:clamp(110px,11cqi,150px) 0 clamp(70px,8cqi,110px)}
.v-hx1 .grid{display:grid;grid-template-columns:1fr 1.02fr;gap:clamp(30px,5cqi,80px);align-items:center}
.v-hx1 .hcim{font-size:calc(var(--t-hero)*.8)}
.v-hx1 .lead{margin:20px 0 28px}
.v-hx1 .jegyzet{margin:26px 0 0;display:inline-block;transform:rotate(-2deg);font-size:calc(var(--fs-hand)*1.35rem)}
.v-hx1 .lap{position:relative;padding:0 0 30px 40px}
.v-hx1 .papir{position:relative;background-color:#FBFAF5;background-image:linear-gradient(color-mix(in srgb,var(--c-primary) 12%,transparent) 1px,transparent 1px),linear-gradient(90deg,color-mix(in srgb,var(--c-primary) 12%,transparent) 1px,transparent 1px);background-size:16px 16px;padding:16px 16px 82px;box-shadow:0 30px 60px -30px rgba(0,0,0,.5),0 2px 6px rgba(0,0,0,.06);transform:rotate(1.4deg);border-radius:3px}
.v-hx1 .kep .ph{aspect-ratio:5/4;border-radius:2px}
.v-hx1 .rajz{position:absolute;left:-44px;bottom:28px;width:44%;background:#fff;padding:10px 12px 8px;box-shadow:0 18px 30px -18px rgba(0,0,0,.45);transform:rotate(-4deg);z-index:2}
.v-hx1 .rajz .ph{aspect-ratio:5/4}
.v-hx1 .eszak{position:absolute;right:30px;top:30px;z-index:3;width:46px;height:46px;border-radius:50%;background:rgba(255,255,255,.93);display:grid;place-items:center;box-shadow:0 6px 14px -6px rgba(0,0,0,.4)}
.v-hx1 .eszak i{position:absolute;top:7px;left:50%;width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-bottom:13px solid #2d302c;translate:-50% 0}
.v-hx1 .eszak b{font-family:var(--f-label);font-size:.7rem;color:#2d302c;margin-top:15px;font-weight:700}
.v-hx1 .szm{position:absolute;right:16px;bottom:14px;display:grid;grid-template-columns:auto auto auto;border:1.5px solid #2d302c;background:#fff;color:#2d302c;z-index:3}
.v-hx1 .szm>div{padding:6px 12px;border-left:1px solid #2d302c;display:grid;gap:1px;line-height:1.2;align-content:center}
.v-hx1 .szm>div:first-child{border-left:0}
.v-hx1 .szm .mono{font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;color:#6f6f6f}
.v-hx1 .szm b{font-family:var(--f-display);font-weight:var(--w-display);font-size:.9rem;color:#2d302c}
.v-hx1 .szm small{font-size:.66rem;color:#555}
.v-hx1 .szm .lgo{place-items:center;padding:6px 12px}
.v-hx1 .szm .logo{background-image:var(--logo-eredeti)!important}
@container elo (max-width:900px){.v-hx1 .grid{grid-template-columns:1fr}.v-hx1 .lap{padding:0 0 20px 26px;max-width:640px}.v-hx1 .rajz{left:-22px;width:38%}}
@container elo (max-width:560px){.v-hx1 .lap{padding:0}.v-hx1 .szm{grid-template-columns:1fr 1fr;left:12px;right:12px}.v-hx1 .szm .lgo{display:none}.v-hx1 .rajz{display:none}.v-hx1 .papir{padding-bottom:96px}}
"""

# ------------------------------------------------------------------ FOLYAMAT: kerti ösvény (csak nektek)


def _fx1(c):
    f = c["folyamat"]
    l = f["lepesek"][:5]
    li = "".join(f'<li data-rv><span class="ko"><b>{i + 1}</b></span><div class="fej">{ik(e.get("ikon"))}</div><h3>{md(e["cim"])}</h3><p>{md(e["szoveg"])}</p></li>'
                 for i, e in enumerate(l))
    return (f'<section class="sec v-fx1 s-tint tx" id="folyamat">{hat(c, masod=True)}{dk(c, "folyamat")}<div class="wrap">{shead(f)}'
            f'<div class="osv"><svg class="ut" viewBox="0 0 1000 140" preserveAspectRatio="none" aria-hidden="true">'
            f'<path d="M30 30H100C200 30 200 90 300 90S400 30 500 30 600 90 700 90 800 30 900 30H970"/></svg>'
            f'<ol style="--n:{len(l)}">{li}</ol></div></div></section>')


FX1_CSS = r"""
.v-fx1 .osv{position:relative}
.v-fx1 .ut{position:absolute;left:0;top:0;width:100%;height:150px;overflow:visible;z-index:0}
.v-fx1 .ut path{fill:none;stroke:color-mix(in srgb,var(--c-primary) 50%,transparent);stroke-width:3;stroke-dasharray:2 12;stroke-linecap:round;vector-effect:non-scaling-stroke}
.v-fx1 ol{position:relative;z-index:1;display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:var(--gap);margin:0;padding:0;list-style:none}
.v-fx1 li{display:flex;flex-direction:column;align-items:center;text-align:center}
.v-fx1 li:nth-child(even){margin-top:64px}
.v-fx1 .ko{width:86px;height:64px;border-radius:52% 48% 46% 54%/58% 52% 48% 42%;background:radial-gradient(ellipse at 34% 28%,#fff 0,color-mix(in srgb,var(--c-sand),#fff 35%) 42%,color-mix(in srgb,var(--c-sand),#000 9%) 100%);box-shadow:0 10px 16px -10px rgba(0,0,0,.45),inset 0 -4px 0 rgba(0,0,0,.06);display:grid;place-items:center;margin-bottom:12px;flex:none}
.v-fx1 li:nth-child(odd) .ko{border-radius:46% 54% 52% 48%/48% 44% 56% 52%}
.v-fx1 .ko b{font-family:var(--f-display);font-weight:var(--w-display);font-size:1.5rem;color:var(--c0-primary-text)}
.v-fx1 .fej .ik{--ik:72px}
.v-fx1 h3{font-size:1.08rem;margin:8px 0 6px}
.v-fx1 li p{margin:0;font-size:.92rem;color:var(--c-ink-2);max-width:28ch}
@container elo (max-width:900px){.v-fx1 .ut{display:none}.v-fx1 ol{grid-template-columns:1fr 1fr;row-gap:34px}.v-fx1 li:nth-child(even){margin-top:0}}
@container elo (max-width:560px){.v-fx1 ol{grid-template-columns:1fr;row-gap:22px}.v-fx1 li{display:grid;grid-template-columns:86px 1fr;text-align:left;column-gap:16px;align-items:start}.v-fx1 .ko{grid-row:span 3;margin:0}.v-fx1 .fej{display:none}.v-fx1 h3{margin-top:2px}}
"""

# ------------------------------------------------------------------ KÍNÁLAT: 4 egyedi elrendezés (rajzközpontú)


def _kx1(c):
    k = c["kinalat"]
    kk = "".join(f'<article class="krt" data-rv><div class="kp">{ik(e.get("ikon"))}</div><h3 class="krt-h">{md(e["nev"])}</h3></article>' for e in k["elemek"])
    return (f'<section class="sec v-kx1 s-paper tx" id="kinalat">{hat(c)}{dk(c, "kinalat")}<div class="wrap">{shead(k)}'
            f'<div class="racs" style="--oszlop:3">{kk}</div>{_kin_lab(c)}</div></section>')


KX1_CSS = KIN_KOZOS + r"""
.v-kx1 .krt{align-items:center;text-align:center;justify-content:flex-start;padding-top:30px!important}
.v-kx1 .kp .ik{--ik:clamp(112px,12cqi,150px)}
.v-kx1 .krt-h{font-size:1.1rem;max-width:22ch}
"""


def _kx2(c):
    k = c["kinalat"]
    cs = {}
    for e in k["elemek"]:
        cs.setdefault(e.get("csoport", ""), []).append(e)
    cols = "".join(f'<div class="cs" data-rv><h3 class="csn">{esc(n)}</h3><ul>'
                   + "".join(f'<li>{ik(e.get("ikon"))}<span>{md(e["nev"])}</span></li>' for e in lst) + '</ul></div>' for n, lst in cs.items())
    return (f'<section class="sec v-kx2 s-white tx" id="kinalat">{hat(c)}{dk(c, "kinalat")}<div class="wrap">{shead(k)}'
            f'<div class="ket">{cols}</div>{_kin_lab(c)}</div></section>')


KX2_CSS = KIN_KOZOS + r"""
.v-kx2 .ket{display:grid;grid-template-columns:1fr 1fr;gap:clamp(24px,5cqi,80px);max-width:1040px;margin:0 auto}
.v-kx2 .csn{font-family:var(--f-hand);font-weight:400;font-size:calc(var(--fs-hand)*1.35rem);color:var(--c-hand);margin:0 0 6px;transform:rotate(-1.5deg);display:inline-block}
.v-kx2 li{display:flex;align-items:center;gap:20px;padding:14px 0;border-bottom:1px dashed var(--c-line2);font-family:var(--f-display);font-weight:var(--w-display);font-size:clamp(1.05rem,1.6cqi,1.32rem);line-height:1.2;color:var(--c-head)}
.v-kx2 li:last-child{border-bottom:0}
.v-kx2 li .ik{--ik:84px}
@container elo (max-width:760px){.v-kx2 .ket{grid-template-columns:1fr}}
"""


def _kx3(c):
    k = c["kinalat"]
    el = k["elemek"]
    pont = [(30, 28), (66, 22), (48, 50), (24, 70), (72, 62), (52, 82)]
    jel = "".join(f'<i style="left:{x}%;top:{y}%">{i + 1}</i>' for i, (x, y) in enumerate(pont[:len(el)]))
    lis = "".join(f'<li data-rv><b>{i + 1}</b>{ik(e.get("ikon"))}<span>{md(e["nev"])}</span></li>' for i, e in enumerate(el))
    return (f'<section class="sec v-kx3 s-paper tx" id="kinalat">{hat(c)}{dk(c, "kinalat")}<div class="wrap grid">'
            f'<div class="lap" data-rv><div class="rajzlap">{ik("kertterv", "nagy")}{jel}</div><p class="mono felirat">Jelmagyarázat</p></div>'
            f'<div class="jobb">{shead(k, bal=True)}<ol class="jm">{lis}</ol>{_kin_lab(c)}</div></div></section>')


KX3_CSS = KIN_KOZOS + r"""
.v-kx3 .grid{display:grid;grid-template-columns:1fr 1.05fr;gap:clamp(30px,5cqi,80px);align-items:center}
.v-kx3 .rajzlap{position:relative;aspect-ratio:1;background-color:#FBFAF5;background-image:linear-gradient(color-mix(in srgb,var(--c-primary) 12%,transparent) 1px,transparent 1px),linear-gradient(90deg,color-mix(in srgb,var(--c-primary) 12%,transparent) 1px,transparent 1px);background-size:16px 16px;box-shadow:0 26px 50px -30px rgba(0,0,0,.5),0 0 0 1px rgba(0,0,0,.05);padding:9%;transform:rotate(-1.4deg);display:grid;place-items:center;border-radius:3px}
.v-kx3 .rajzlap .ik{--ik:100%;width:100%;height:100%}
.v-kx3 .rajzlap i{position:absolute;width:32px;height:32px;border-radius:50%;background:var(--c-primary);color:var(--c-on-primary);display:grid;place-items:center;font-style:normal;font-family:var(--f-label);font-weight:700;font-size:.82rem;box-shadow:0 0 0 4px #FBFAF5,0 6px 12px -4px rgba(0,0,0,.35);translate:-50% -50%}
.v-kx3 .felirat{text-align:center;margin:16px 0 0;font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:var(--c-ink-3)}
.v-kx3 .shead{margin-bottom:22px}
.v-kx3 .jm{margin:0;padding:0;list-style:none}
.v-kx3 .jm li{display:grid;grid-template-columns:32px 58px 1fr;align-items:center;gap:14px;padding:10px 0;border-bottom:1px solid var(--c-line)}
.v-kx3 .jm b{width:32px;height:32px;border-radius:50%;border:1.5px solid var(--hl);display:grid;place-items:center;font-family:var(--f-label);font-size:.8rem;color:var(--hl)}
.v-kx3 .jm .ik{--ik:56px}
.v-kx3 .jm span{font-family:var(--f-display);font-weight:var(--w-display);font-size:1.08rem;line-height:1.2;color:var(--c-head)}
.v-kx3 .lab{justify-content:flex-start}
@container elo (max-width:860px){.v-kx3 .grid{grid-template-columns:1fr}.v-kx3 .lap{max-width:440px;margin:0 auto}}
"""


def _kx4(c):
    k = c["kinalat"]
    rot = [-3, 2, -1.5, 2.5, -2, 1.5]
    kk = "".join(f'<div class="cw" data-rv style="--r:{r}deg"><div class="ncimke">{ik(e.get("ikon"))}<h3>{md(e["nev"])}</h3></div><i class="karo"></i></div>'
                 for e, r in zip(k["elemek"], rot))
    return (f'<section class="sec v-kx4 s-tint tx" id="kinalat">{hat(c)}{dk(c, "kinalat")}<div class="wrap">{shead(k)}'
            f'<div class="agyas">{kk}</div>{_kin_lab(c)}</div></section>')


KX4_CSS = KIN_KOZOS + r"""
.v-kx4 .agyas{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:30px clamp(18px,3cqi,44px)}
.v-kx4 .cw{display:flex;flex-direction:column;align-items:center;transform:rotate(var(--r));transform-origin:50% 100%}
.v-kx4 .ncimke{position:relative;width:100%;max-width:280px;background:color-mix(in srgb,#F2E6CF 84%,var(--c-accent));border-radius:16px 16px 10px 10px;padding:30px 18px 20px;text-align:center;box-shadow:0 16px 26px -18px rgba(0,0,0,.5),inset 0 0 0 1px rgba(0,0,0,.06)}
.v-kx4 .ncimke::before{content:"";position:absolute;top:11px;left:50%;width:10px;height:10px;border-radius:50%;background:var(--sec-bg,var(--c-paper));box-shadow:inset 0 1px 2px rgba(0,0,0,.35);translate:-50% 0}
.v-kx4 .ncimke .ik{--ik:104px;display:block;margin:0 auto 8px}
.v-kx4 .ncimke h3{font-family:var(--f-hand);font-weight:400;font-size:calc(var(--fs-hand)*1.12rem);line-height:1.1;color:#3b3326;text-transform:none;letter-spacing:0}
.v-kx4 .karo{display:block;width:22px;height:58px;margin-top:-1px;background:linear-gradient(90deg,color-mix(in srgb,#E3D1AE 84%,var(--c-accent)),color-mix(in srgb,#CDB68C 84%,var(--c-accent)));clip-path:polygon(0 0,100% 0,100% 72%,50% 100%,0 72%)}
.v-kx4 .cw::after{content:"";width:150px;height:14px;margin-top:-8px;border-radius:50%;background:radial-gradient(ellipse,color-mix(in srgb,#5b4630 40%,transparent),transparent 70%)}
@container elo (max-width:860px){.v-kx4 .agyas{grid-template-columns:1fr 1fr}}
@container elo (max-width:520px){.v-kx4 .agyas{grid-template-columns:1fr}}
"""

# ------------------------------------------------------------------ TÉNYEK: kártyák virágos fotón (a mostani, frissítve)


def _tx1(c):
    t = c["tenyek"]
    kk = "".join(f'<article class="krt s-vilagos" data-rv><div class="kp">{ik(e.get("ikon"))}</div><h3 class="krt-h">{md(e["cim"])}</h3><p class="krt-p">{md(e["szoveg"])}</p></article>'
                 for e in t["elemek"])
    return (f'<section class="sec v-tx1 s-deep">{ph(c, "evelo", "bg")}<i class="arny"></i>{hat(c)}<div class="wrap">{shead(t)}'
            f'<div class="racs" style="--oszlop:3">{kk}</div></div></section>')


TX1_CSS = r"""
.v-tx1{overflow:hidden;padding-bottom:calc(var(--sec-y) + 10px)}
.v-tx1 .bg{position:absolute;inset:0;aspect-ratio:auto;height:100%;z-index:-2}
.v-tx1 .arny{position:absolute;inset:0;z-index:-1;background:linear-gradient(180deg,color-mix(in srgb,var(--c-deep) 78%,transparent),color-mix(in srgb,var(--c-deep) 52%,transparent) 70%,color-mix(in srgb,var(--c-deep) 66%,transparent))}
.v-tx1 .krt{align-items:center;text-align:center}
.v-tx1 .kp .ik{--ik:100px}
.v-tx1 .krt-h{font-size:1.2rem}
.v-tx1 .racs .krt:nth-child(2){transform:translateY(-22px)}
@container elo (max-width:900px){.v-tx1 .racs .krt:nth-child(2){transform:none}}
"""

# ------------------------------------------------------------------ GARANCIA: 5 egyedi változat


def _gar(c, vid, belso, felulet="s-white"):
    return (f'<section class="sec v-{vid} {felulet} tx" id="garancia">{hat(c)}{dk(c, "garancia")}<div class="wrap">{shead(c["garancia"])}'
            f'{belso}</div></section>')


def _gx1(c):
    kk = "".join(f'<article class="krt" data-rv><div class="krt-fej">{ik(g["ikon"])}<h3 class="krt-h">{esc(g["cim"])}</h3></div><p class="krt-p">{esc(g["szoveg"])}</p></article>' for g in GARANCIAK)
    return _gar(c, "gx1", f'<div class="racs" style="--oszlop:3">{kk}</div>')


def _gx2(c):
    sorok = "".join(f'<div class="sor" data-rv><b class="n">{i + 1}</b><div class="i">{ik(g["ikon"])}</div><h3>{esc(g["cim"])}</h3><p>{esc(g["szoveg"])}</p></div>'
                    for i, g in enumerate(GARANCIAK))
    fej = (f'<div class="fej"><span class="mono">Garanciák · 3 pont</span><span class="mono rejt">Koppány Lili · okleveles tájépítészmérnök</span>'
           f'{logo(c, 22, "ko")}</div>')
    return _gar(c, "gx2", f'<div class="szm">{fej}{sorok}</div>', "s-paper")


def _gx3(c):
    pk = "".join(f'<div class="p" data-rv><div class="roz"><span class="kor">{ik(g["ikon"])}</span></div><h3>{esc(g["cim"])}</h3><p>{esc(g["szoveg"])}</p></div>' for g in GARANCIAK)
    return _gar(c, "gx3", f'<div class="pk">{pk}</div>')


def _gx4(c):
    li = "".join(f'<li data-rv><span class="pipa">{ui("pipa")}</span><div><h3>{esc(g["cim"])}</h3><p>{esc(g["szoveg"])}</p></div><div class="i">{ik(g["ikon"])}</div></li>' for g in GARANCIAK)
    return _gar(c, "gx4", f'<div class="lap" data-rv><ul>{li}</ul><div class="alair"><span class="kezi">Koppány Lili</span>'
                           f'<span class="mono">okleveles tájépítészmérnök</span></div></div>', "s-tint")


def _gx5(c):
    sz = "".join(f'<div class="g" data-rv><b class="n">{i + 1:02d}</b><div class="fej">{ik(g["ikon"])}<h3>{esc(g["cim"])}</h3></div><p>{esc(g["szoveg"])}</p></div>'
                 for i, g in enumerate(GARANCIAK))
    return _gar(c, "gx5", f'<div class="sz3">{sz}</div>', "s-deep")


GAR_CSS = {
    "gx1": ("Három kártya ikonnal", "Három egyforma kártya: ikon, cím, a vállalás. Egyszerű, gyorsan átlátható.", r"""
.v-gx1 .krt-fej .ik{--ik:64px}
.v-gx1 .krt-h{font-size:1.15rem}
"""),
    "gx2": ("Tervlap-szövegmező", "A három vállalás egy tervlap szövegmezőjében, vastag kerettel, sorszámmal, mint a terveid jobb alsó sarkában. Szakmai, csak egy tájépítésznél van értelme.", r"""
.v-gx2 .szm{max-width:1000px;margin:0 auto;border:2px solid var(--c-head);background:var(--c-card);box-shadow:var(--sh-2)}
.v-gx2 .fej{display:flex;justify-content:space-between;align-items:center;gap:14px;padding:10px 16px;border-bottom:2px solid var(--c-head);font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;color:var(--c-ink-2)}
.v-gx2 .fej .logo{flex:none}
.v-gx2 .sor{display:grid;grid-template-columns:70px 86px minmax(150px,.75fr) 1.6fr;border-bottom:1px solid var(--c-line2)}
.v-gx2 .sor:last-child{border-bottom:0}
.v-gx2 .sor>*{margin:0;padding:16px 18px;border-left:1px solid var(--c-line2);display:flex;align-items:center}
.v-gx2 .sor>*:first-child{border-left:0}
.v-gx2 .n{justify-content:center;font-family:var(--f-display);font-weight:var(--w-display);font-size:2.1rem;color:var(--hl)}
.v-gx2 .i{justify-content:center}.v-gx2 .i .ik{--ik:54px}
.v-gx2 h3{font-size:1.1rem}
.v-gx2 .sor p{color:var(--c-ink-2);font-size:.96rem;line-height:1.55}
@container elo (max-width:760px){.v-gx2 .sor{grid-template-columns:56px 1fr}.v-gx2 .i{display:none!important}.v-gx2 .sor p{grid-column:1/-1;border-left:0;border-top:1px dashed var(--c-line2);padding-top:12px}.v-gx2 .rejt{display:none}}
"""),
    "gx3": ("Pecsétek", "Három fogazott szélű, zöld rozetta-pecsét az ikonokkal, alattuk a vállalás. Kézzelfogható „garancia” hatás.", T(r"""
.v-gx3 .pk{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--gap);text-align:center}
.v-gx3 .roz{width:156px;height:156px;margin:0 auto 18px;background:repeating-conic-gradient(var(--c-primary) 0 7.5deg,color-mix(in srgb,var(--c-primary),#fff 22%) 7.5deg 15deg);""" + mask("ROZETTA") + r""";display:grid;place-items:center;filter:drop-shadow(0 10px 14px rgba(0,0,0,.18))}
.v-gx3 .kor{width:104px;height:104px;border-radius:50%;background:var(--c-card);display:grid;place-items:center;box-shadow:inset 0 0 0 3px color-mix(in srgb,var(--c-primary) 30%,transparent)}
.v-gx3 .kor .ik{--ik:70px}
.v-gx3 h3{font-size:1.15rem;margin-bottom:8px}
.v-gx3 .p p{max-width:30ch;margin:0 auto;color:var(--c-ink-2);font-size:.95rem}
@container elo (max-width:820px){.v-gx3 .pk{grid-template-columns:1fr;row-gap:36px}}
""")),
    "gx4": ("Ígéretlista aláírással", "Egy fehér lapon a három vállalás pipával, a végén kézírásos aláírás. Személyes, mint egy levél.", r"""
.v-gx4 .lap{max-width:880px;margin:0 auto;background:var(--c-card);border-radius:24px;padding:clamp(22px,3.6cqi,46px);box-shadow:var(--sh-2)}
.v-gx4 ul{margin:0;padding:0;list-style:none}
.v-gx4 li{display:grid;grid-template-columns:46px 1fr 76px;gap:18px;align-items:center;padding:18px 0;border-bottom:1px dashed var(--c-line2)}
.v-gx4 .pipa{width:46px;height:46px;border-radius:50%;background:var(--c-primary);color:var(--c-on-primary);display:grid;place-items:center}
.v-gx4 .pipa .ui{width:24px;height:24px}
.v-gx4 h3{font-size:1.12rem;margin-bottom:4px}
.v-gx4 li p{margin:0;color:var(--c-ink-2);font-size:.96rem}
.v-gx4 .i .ik{--ik:70px}
.v-gx4 .alair{display:flex;flex-direction:column;align-items:flex-end;margin-top:20px}
.v-gx4 .alair .kezi{font-size:calc(var(--fs-hand)*1.9rem);line-height:1}
.v-gx4 .alair .mono{font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;color:var(--c-ink-3)}
@container elo (max-width:600px){.v-gx4 li{grid-template-columns:40px 1fr}.v-gx4 .i{display:none}}
"""),
    "gx5": ("Sötét sáv, nagy számokkal", "Sötét blokk, három hasáb óriás, kontúros sorszámmal. Határozott, magabiztos lezárás a vállalásoknak.", r"""
.v-gx5 .sz3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(18px,3cqi,44px)}
.v-gx5 .g{border-top:1px solid var(--c-line2);padding-top:18px}
.v-gx5 .n{display:block;font-family:var(--f-display);font-weight:var(--w-display);font-size:clamp(3.2rem,7cqi,6rem);line-height:.9;color:transparent;-webkit-text-stroke:2px var(--hl)}
.v-gx5 .fej{display:flex;gap:12px;align-items:center;margin:16px 0 8px}
.v-gx5 .fej .ik{--ik:46px}
.v-gx5 h3{font-size:1.15rem}
.v-gx5 .g p{margin:0;color:var(--c-ink-2)}
@container elo (max-width:820px){.v-gx5 .sz3{grid-template-columns:1fr}}
"""),
}
GAR_REND = {"gx1": _gx1, "gx2": _gx2, "gx3": _gx3, "gx4": _gx4, "gx5": _gx5}

# ------------------------------------------------------------------ GYIK: 5 egyedi változat


def _gyik_sec(c, vid, belso, felulet="s-paper"):
    return (f'<section class="sec v-{vid} {felulet} tx" id="gyik">{hat(c)}{dk(c, "gyik")}<div class="wrap">{shead(c["gyik"])}'
            f'{belso}</div></section>')


def _yx1(c):
    el = "".join(f'<details class="gy" data-rv{" open" if i == 0 else ""}><summary>{esc(k)}</summary><div class="v">{_p(v)}</div></details>' for i, (k, v) in enumerate(GYIK))
    return _gyik_sec(c, "yx1", f'<div class="gyl">{el}</div>')


def _yx2(c):
    el = "".join(f'<details class="gy" data-rv{" open" if i == 0 else ""}><summary><span class="gn">{i + 1}</span><span>{esc(k)}</span></summary><div class="v">{_p(v)}</div></details>'
                 for i, (k, v) in enumerate(GYIK))
    return _gyik_sec(c, "yx2", f'<div class="gyl">{el}</div>', "s-tint")


def _yx3(c):
    tb = "".join(f'<button class="tb{" on" if i == 0 else ""}" type="button" data-tab="{i}"><span class="n">{i + 1}</span><span>{esc(k)}</span></button>' for i, (k, _) in enumerate(GYIK))
    pn = "".join(f'<div class="pane{" on" if i == 0 else ""}" data-tab="{i}"><h3>{esc(k)}</h3>{_p(v)}</div>' for i, (k, v) in enumerate(GYIK))
    return _gyik_sec(c, "yx3", f'<div class="lap" data-tabs data-rv><div class="tbs" role="tablist">{tb}</div><div class="panes">{pn}</div></div>', "s-sand")


def _yx4(c):
    el = "".join(f'<div class="gy" data-rv><h3>{esc(k)}</h3>{_p(v)}</div>' for k, v in GYIK)
    return _gyik_sec(c, "yx4", f'<div class="ket">{el}</div>', "s-white")


def _yx5(c):
    el = "".join(f'<div class="cs" data-rv><p class="kb">{esc(k)}</p><div class="vb">{ph(c, "lili_portre", "av")}<div class="bub"><b class="ki">Lili</b>{_p(v)}</div></div></div>'
                 for k, v in GYIK)
    return _gyik_sec(c, "yx5", f'<div class="chat">{el}</div>', "s-tint")


GYIK_ALAP = r"""
.v-%(v)s .gyl{max-width:880px;margin:0 auto;display:grid;gap:12px}
.v-%(v)s summary{cursor:pointer;list-style:none;display:flex;gap:14px;align-items:center;font-family:var(--f-display);font-weight:var(--w-display);font-size:clamp(1.02rem,1.5cqi,1.2rem);line-height:1.3;color:var(--c-head)}
.v-%(v)s summary::-webkit-details-marker{display:none}
.v-%(v)s .v{padding-top:12px}
.v-%(v)s .v p{margin:0 0 .8em;line-height:1.65;color:var(--c-ink-2)}
.v-%(v)s .v p:last-child{margin-bottom:0}
"""
GYIK_CSS = {
    "yx1": ("Lenyíló sorok vonallal", "Egyszerű, vékony vonallal elválasztott lenyíló kérdések, jobbra plusz jellel. A legtisztább.", r"""
.v-yx1 .gy{border-bottom:1px solid var(--c-line2);padding:18px 0}
.v-yx1 summary::after{content:"+";margin-left:auto;flex:none;width:34px;height:34px;border-radius:50%;display:grid;place-items:center;font-family:var(--f-body);font-size:1.3rem;color:var(--hl);border:1px solid var(--c-line2);transition:transform .3s}
.v-yx1 .gy[open] summary::after{transform:rotate(45deg)}
"""),
    "yx2": ("Kártyák sorszámmal", "Minden kérdés egy fehér kártya, előtte kerek sorszámmal. Rendezett, barátságos.", r"""
.v-yx2 .gy{background:var(--c-card);border-radius:18px;padding:18px 22px;box-shadow:var(--sh-1)}
.v-yx2 .gn{flex:none;width:34px;height:34px;border-radius:50%;display:grid;place-items:center;background:var(--c-primary-ll);color:var(--c-primary-d);font-family:var(--f-body);font-size:.9rem;font-weight:800}
.v-yx2 .gy[open] .gn{background:var(--c-primary);color:var(--c-on-primary)}
.v-yx2 .v{padding-left:48px}
@container elo (max-width:560px){.v-yx2 .v{padding-left:0}}
"""),
    "yx3": ("Lapozós: kérdések balra, válasz jobbra", "Balra a négy kérdés, jobbra egy nagy lapon a kiválasztott válasza. Hosszú válaszoknál is áttekinthető.", r"""
.v-yx3 .lap{display:grid;grid-template-columns:.9fr 1.35fr;gap:clamp(18px,3cqi,40px);align-items:start;max-width:1100px;margin:0 auto}
.v-yx3 .tbs{display:grid;gap:8px}
.v-yx3 .tb{display:flex;gap:12px;align-items:flex-start;text-align:left;width:100%;padding:16px 18px;border:0;border-radius:16px;background:transparent;cursor:pointer;font-weight:700;font-size:.98rem;line-height:1.35;color:var(--c-ink-2);transition:background .2s,color .2s}
.v-yx3 .tb:hover{background:color-mix(in srgb,var(--c-card) 60%,transparent)}
.v-yx3 .tb.on{background:var(--c-card);color:var(--c-head);box-shadow:var(--sh-2)}
.v-yx3 .tb .n{flex:none;width:28px;height:28px;border-radius:50%;display:grid;place-items:center;background:var(--c-primary-ll);color:var(--c-primary-d);font-size:.8rem;font-weight:800}
.v-yx3 .tb.on .n{background:var(--c-primary);color:var(--c-on-primary)}
.v-yx3 .panes{background:var(--c-card);border-radius:24px;padding:clamp(22px,3.2cqi,40px);box-shadow:var(--sh-2)}
.v-yx3 .pane{display:none}.v-yx3 .pane.on{display:block}
.v-yx3 .pane h3{font-size:clamp(1.2rem,2cqi,1.5rem);margin-bottom:14px}
.v-yx3 .pane p{line-height:1.65;color:var(--c-ink-2)}
@container elo (max-width:820px){.v-yx3 .lap{grid-template-columns:1fr}}
"""),
    "yx4": ("Két hasáb, mind nyitva", "Nincs kattintgatás: két hasábban minden kérdés és válasz látszik, mint egy jól szerkesztett kiadványban.", r"""
.v-yx4 .ket{columns:2 360px;column-gap:clamp(28px,4cqi,60px)}
.v-yx4 .gy{break-inside:avoid;margin:0 0 30px;padding-top:16px;border-top:2px solid var(--c-head)}
.v-yx4 .gy h3{font-size:1.15rem;margin-bottom:10px}
.v-yx4 .gy p{font-size:.95rem;line-height:1.62;color:var(--c-ink-2)}
"""),
    "yx5": ("Beszélgetés Lilivel", "A kérdés a te buborékod, a válasz Liliéé, mellette a kis portréja. Közvetlen, mintha üzenetben kérdeznél.", r"""
.v-yx5 .chat{max-width:900px;margin:0 auto;display:grid;gap:30px}
.v-yx5 .cs{display:grid;gap:12px}
.v-yx5 .kb{justify-self:end;max-width:78%;margin:0;background:var(--c-primary);color:var(--c-on-primary);padding:14px 20px;border-radius:22px 22px 6px 22px;font-weight:700;line-height:1.4;box-shadow:var(--sh-2)}
.v-yx5 .vb{display:grid;grid-template-columns:48px 1fr;gap:12px;align-items:end;max-width:88%}
.v-yx5 .av{width:48px;height:48px;aspect-ratio:1;border-radius:50%;box-shadow:0 0 0 3px var(--c-card)}
.v-yx5 .bub{background:var(--c-card);padding:16px 20px;border-radius:22px 22px 22px 6px;box-shadow:var(--sh-1)}
.v-yx5 .ki{display:block;font-family:var(--f-hand);font-weight:400;font-size:calc(var(--fs-hand)*1.05rem);color:var(--c-hand);margin-bottom:4px}
.v-yx5 .bub p{margin:0 0 .7em;line-height:1.6;color:var(--c-ink-2);font-size:.96rem}.v-yx5 .bub p:last-child{margin:0}
@container elo (max-width:600px){.v-yx5 .kb,.v-yx5 .vb{max-width:100%}}
"""),
}
GYIK_REND = {"yx1": _yx1, "yx2": _yx2, "yx3": _yx3, "yx4": _yx4, "yx5": _yx5}

# ------------------------------------------------------------------ AJÁNLATKÉRÉS: 5 egyedi változat

MEZOK = [("Név", "text", "name", False), ("Email", "email", "email", False), ("Telefonszám", "tel", "tel", False), ("Település", "text", "address-level2", False),
         ("A kerted mérete (m2-ben)", "text", "off", False), ("Mikorra tervezed a kivitelezést?", "text", "off", False)]


def _urlap(c):
    m = "".join(f'<label class="m"><span>{esc(n)}</span><input type="{t}" autocomplete="{a}"></label>' for n, t, a, _ in MEZOK)
    m += ('<label class="m szeles"><span>Az elképzelésed néhány mondatban</span><textarea rows="3"></textarea></label>'
          '<label class="m szeles"><span>Körülbelül mekkora összeget tervezel a kert teljes megépítésére szánni? <small>(Tervezés + anyagköltség + kivitelezés)</small></span><input type="text"></label>'
          '<label class="m szeles"><span>Mire szeretnéd használni a kertet, mit fogsz csinálni benne?</span><textarea rows="2"></textarea></label>'
          '<label class="m fajl"><span>Fotók a kertedről <small>(nem kötelező)</small></span><input type="file" multiple accept="image/*"></label>'
          '<label class="m fajl"><span>Alaprajz <small>(nem kötelező)</small></span><input type="file" accept="image/*,.pdf"></label>')
    return (f'<form class="urlap" action="#" novalidate aria-label="Ajánlatkérő űrlap"><div class="mezok">{m}</div>'
            f'<button class="btn" type="button">Küldés{ui("nyil")}</button></form>')


def _lep_ol(cls="lep"):
    return f'<ol class="{cls}">' + "".join(f'<li data-rv><b>{i + 1}</b><p>{esc(t)}</p></li>' for i, t in enumerate(AJANLATKERES["lepesek"])) + "</ol>"


def _doboz(c, cls="doboz"):
    a = AJANLATKERES
    return (f'<div class="{cls}" data-rv><div class="rz">{ph(c, "rajz_sedum")}</div><div><h3>{esc(a["doboz_cim"])}</h3><p>{esc(a["doboz"])}</p></div></div>')


def _aj_sec(c, vid, belso, felulet="s-white"):
    return f'<section class="sec v-{vid} {felulet} tx" id="ajanlatkeres">{hat(c)}{dk(c, "ajanlatkeres")}<div class="wrap">{belso}</div></section>'


def _ax1(c):
    a = AJANLATKERES
    bal = f'<div class="bal">{shead(a, bal=True)}<p class="mono menete">{esc(a["menete"])}</p>{_lep_ol()}{_doboz(c)}</div>'
    return _aj_sec(c, "ax1", f'<div class="grid">{bal}<div class="uk s-vilagos" data-rv>{_urlap(c)}</div></div>')


def _ax2(c):
    a = AJANLATKERES
    fej = shead(a)
    lep = f'<p class="mono menete">{esc(a["menete"])}</p>{_lep_ol("lep sor4")}'
    lap = (f'<div class="papir" data-rv>{_urlap(c)}<div class="szm"><div><span class="mono">Ajánlatkérés</span><b>Koppány Lili</b></div>'
           f'<div><span class="mono">Visszahívás</span><b>2 munkanapon belül</b></div><div class="lgo">{logo(c, 22, "ko")}</div></div>'
           f'{_doboz(c, "doboz cetli")}</div>')
    return _aj_sec(c, "ax2", f'{fej}{lep}{lap}', "s-paper")


def _ax3(c):
    a = AJANLATKERES
    return _aj_sec(c, "ax3", f'{shead(a)}<p class="mono menete">{esc(a["menete"])}</p>{_lep_ol("lep sor4")}'
                             f'<div class="uk s-vilagos" data-rv>{_urlap(c)}</div>{_doboz(c, "doboz sav")}', "s-tint")


def _ax4(c):
    a = AJANLATKERES
    bal = f'<div class="bal">{shead(a, bal=True)}<p class="mono menete">{esc(a["menete"])}</p>{_lep_ol()}{_doboz(c, "doboz kontur")}</div>'
    return _aj_sec(c, "ax4", f'<div class="grid">{bal}<div class="uk s-vilagos" data-rv>{_urlap(c)}</div></div>', "s-deep")


def _ax5(c):
    a = AJANLATKERES
    banner = (f'<div class="banner" data-rv><div class="rz">{ph(c, "rajz_sedum")}</div><div class="bt"><span class="pecset">0 Ft</span>'
              f'<h3>{esc(a["doboz_cim"])}</h3><p>{esc(a["doboz"])}</p></div></div>')
    return _aj_sec(c, "ax5", f'{shead(a)}{banner}<div class="grid"><div><p class="mono menete">{esc(a["menete"])}</p>{_lep_ol("lep idov")}</div>'
                             f'<div class="uk s-vilagos" data-rv>{_urlap(c)}</div></div>', "s-paper")


def urlap_css(v):
    return (RAJZ_PH.replace(".rz", f".v-{v} .rz") + r"""
.v-%(v)s .menete{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--c-ink-3);margin:0 0 14px}
.v-%(v)s .lep{margin:0 0 24px;padding:0;list-style:none;display:grid;gap:14px}
.v-%(v)s .lep li{display:grid;grid-template-columns:38px 1fr;gap:14px;align-items:start}
.v-%(v)s .lep b{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;background:var(--c-primary);color:var(--c-on-primary);font-family:var(--f-display);font-weight:var(--w-display);font-size:1.05rem}
.v-%(v)s .lep p{margin:6px 0 0;color:var(--c-ink-2);font-size:.96rem;line-height:1.55}
.v-%(v)s .lep.sor4{grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--gap);margin-bottom:34px}
.v-%(v)s .lep.sor4 li{grid-template-columns:1fr;gap:10px;align-content:start}
.v-%(v)s .doboz{display:grid;grid-template-columns:88px 1fr;gap:16px;align-items:center;background:var(--c-tint);border-radius:20px;padding:16px 20px}
.v-%(v)s .doboz .rz .ph{aspect-ratio:1}
.v-%(v)s .doboz h3{font-size:1.05rem;margin-bottom:4px}
.v-%(v)s .doboz p{margin:0;color:var(--c-ink-2);font-size:.92rem}
.v-%(v)s .uk{background:var(--c-card);border-radius:24px;padding:clamp(20px,3cqi,36px);box-shadow:var(--sh-3)}
.v-%(v)s .urlap{display:grid;gap:18px}
.v-%(v)s .mezok{display:grid;grid-template-columns:1fr 1fr;gap:14px 16px}
.v-%(v)s .m{display:grid;gap:6px;font-size:.86rem;font-weight:700;color:var(--c-head);align-content:start}
.v-%(v)s .m.szeles{grid-column:1/-1}
.v-%(v)s .m small{font-weight:400;color:var(--c-ink-3)}
.v-%(v)s .m input,.v-%(v)s .m textarea{font:inherit;font-weight:400;font-size:.95rem;color:var(--c-ink);background:var(--c-paper);border:1px solid var(--c-line2);border-radius:10px;padding:11px 13px;width:100%;transition:border-color .2s,box-shadow .2s}
.v-%(v)s .m textarea{resize:vertical;min-height:80px}
.v-%(v)s .m input:focus,.v-%(v)s .m textarea:focus{outline:none;border-color:var(--c-primary);box-shadow:0 0 0 3px color-mix(in srgb,var(--c-primary) 22%,transparent)}
.v-%(v)s .m input[type=file]{padding:8px;background:var(--c-card);border-style:dashed;font-size:.8rem}
.v-%(v)s .m input[type=file]::file-selector-button{font:inherit;font-weight:700;border:0;border-radius:8px;padding:7px 12px;margin-right:10px;background:var(--c-primary-ll);color:var(--c-primary-d);cursor:pointer}
.v-%(v)s .urlap .btn{justify-self:start}
@container elo (max-width:620px){.v-%(v)s .mezok{grid-template-columns:1fr}.v-%(v)s .lep.sor4{grid-template-columns:1fr 1fr}}
""").replace("%(v)s", v)


AJ_CSS = {
    "ax1": ("Lépések balra, űrlap jobbra", "Balra a négy lépés és a kötelezettségmentes konzultáció dobozával a varjúháj-rajz, jobbra egy tiszta, fehér űrlap-kártya. A mostani szerkezet, rendezettebben.", r"""
.v-ax1 .grid{display:grid;grid-template-columns:.95fr 1.05fr;gap:clamp(28px,5cqi,70px);align-items:start}
.v-ax1 .shead{margin-bottom:22px}
@container elo (max-width:900px){.v-ax1 .grid{grid-template-columns:1fr}}
"""),
    "ax2": ("Űrlap egy tervlapon", "A négy lépés egy sorban, alatta az űrlap egy milliméterpapír tervlapon, szövegmezővel és egy rátűzött cetlivel a díjmentes konzultációról.", r"""
.v-ax2 .papir{position:relative;max-width:980px;margin:0 auto;background-color:#FBFAF5;background-image:linear-gradient(color-mix(in srgb,var(--c-primary) 10%,transparent) 1px,transparent 1px),linear-gradient(90deg,color-mix(in srgb,var(--c-primary) 10%,transparent) 1px,transparent 1px);background-size:16px 16px;padding:clamp(22px,3.4cqi,44px) clamp(22px,3.4cqi,44px) 92px;box-shadow:0 30px 60px -32px rgba(0,0,0,.5),0 0 0 1px rgba(0,0,0,.05);border-radius:3px;--c-ink:#2f332e;--c-head:#2f332e;--c-ink-2:#4b504a;--c-ink-3:#6f6f6f;--c-line2:#cfd2c8;--c-paper:#ffffff;--c-card:#ffffff}
.v-ax2 .szm{position:absolute;left:clamp(22px,3.4cqi,44px);bottom:22px;display:grid;grid-template-columns:auto auto auto;border:1.5px solid #2d302c;background:#fff;color:#2d302c}
.v-ax2 .szm>div{padding:6px 12px;border-left:1px solid #2d302c;display:grid;gap:1px;line-height:1.2;align-content:center}
.v-ax2 .szm>div:first-child{border-left:0}
.v-ax2 .szm .mono{font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;color:#6f6f6f}
.v-ax2 .szm b{font-family:var(--f-display);font-weight:var(--w-display);font-size:.88rem}
.v-ax2 .szm .lgo{place-items:center}.v-ax2 .szm .logo{background-image:var(--logo-eredeti)!important}
.v-ax2 .cetli{position:absolute;right:-18px;bottom:-26px;width:min(330px,46%);background:color-mix(in srgb,#FFF6C9 80%,var(--c-accent2));border-radius:4px;transform:rotate(2.5deg);box-shadow:0 18px 26px -16px rgba(0,0,0,.4);grid-template-columns:62px 1fr;padding:14px 16px}
.v-ax2 .cetli h3,.v-ax2 .cetli p{color:#3b3326}
.v-ax2 .menete,.v-ax2 .lep{max-width:980px;margin-left:auto;margin-right:auto}
@container elo (max-width:760px){.v-ax2 .szm{grid-template-columns:1fr 1fr}.v-ax2 .szm .lgo{display:none}.v-ax2 .cetli{position:relative;right:auto;bottom:auto;width:auto;margin-top:16px;transform:none}.v-ax2 .papir{padding-bottom:30px}.v-ax2 .szm{position:relative;left:auto;bottom:auto;margin-top:20px;width:max-content}}
"""),
    "ax3": ("Négy lépés felül, űrlap középen", "Középre zárt fej, a négy lépés egy sorban, alatta egy nagy, középre zárt űrlap-kártya, a végén széles sáv a díjmentes konzultációról.", r"""
.v-ax3 .menete{text-align:center}
.v-ax3 .lep.sor4 li{text-align:center;justify-items:center}
.v-ax3 .uk{max-width:820px;margin:0 auto}
.v-ax3 .sav{max-width:820px;margin:22px auto 0;background:var(--c-card);box-shadow:var(--sh-1)}
"""),
    "ax4": ("Sötét blokk, világos űrlap", "Sötét záró blokk: balra a lépések világos betűkkel, jobbra kiemelt, világos űrlap-kártya. Erős kontraszt, a figyelem az űrlapon.", r"""
.v-ax4 .grid{display:grid;grid-template-columns:.95fr 1.05fr;gap:clamp(28px,5cqi,70px);align-items:start}
.v-ax4 .shead{margin-bottom:22px}
.v-ax4 .lep b{background:var(--c-deep-hl);color:var(--c-on-deep-hl)}
.v-ax4 .kontur{background:transparent;border:1px solid var(--c-line2)}
.v-ax4 .kontur .rz{filter:invert(1);opacity:.85}
@container elo (max-width:900px){.v-ax4 .grid{grid-template-columns:1fr}}
"""),
    "ax5": ("Konzultáció kiemelve", "Felül nagy, rajzos sáv a kötelezettségmentes konzultációról „0 Ft” pecséttel, alatta idővonalon a lépések és mellette az űrlap.", r"""
.v-ax5 .banner{display:grid;grid-template-columns:150px 1fr;gap:clamp(16px,3cqi,34px);align-items:center;background:var(--c-tint);border-radius:28px;padding:clamp(18px,3cqi,30px) clamp(20px,3.4cqi,40px);margin:0 auto 38px;max-width:1000px;position:relative}
.v-ax5 .banner .rz .ph{aspect-ratio:1}
.v-ax5 .bt h3{font-size:clamp(1.2rem,2.1cqi,1.6rem);margin-bottom:8px;max-width:30ch}
.v-ax5 .bt p{margin:0;color:var(--c-ink-2)}
.v-ax5 .pecset{position:absolute;right:26px;top:-22px;width:86px;height:86px;border-radius:50%;display:grid;place-items:center;font-family:var(--f-display);font-weight:var(--w-display);font-size:1.4rem;color:var(--c-on-accent);background:radial-gradient(circle,var(--c-accent) 0 60%,transparent 61%),repeating-conic-gradient(var(--c-accent) 0 8deg,var(--c-accent-d) 8deg 16deg);transform:rotate(12deg);box-shadow:0 10px 18px -10px rgba(0,0,0,.45)}
.v-ax5 .grid{display:grid;grid-template-columns:.9fr 1.1fr;gap:clamp(28px,5cqi,70px);align-items:start;max-width:1100px;margin:0 auto}
.v-ax5 .idov{position:relative}
.v-ax5 .idov::before{content:"";position:absolute;left:18px;top:20px;bottom:20px;border-left:2px dashed color-mix(in srgb,var(--c-primary) 45%,transparent)}
.v-ax5 .idov li{position:relative}
@container elo (max-width:900px){.v-ax5 .grid{grid-template-columns:1fr}}
@container elo (max-width:560px){.v-ax5 .banner{grid-template-columns:1fr}.v-ax5 .banner .rz{max-width:120px}.v-ax5 .pecset{width:70px;height:70px;font-size:1.1rem;right:14px}}
"""),
}
AJ_REND = {"ax1": _ax1, "ax2": _ax2, "ax3": _ax3, "ax4": _ax4, "ax5": _ax5}

# ------------------------------------------------------------------ KAPCSOLAT: névjegykártya (csak nektek)


def _elerhet(c):
    k = c["kapcsolat"]
    return (f'<div class="adat"><a href="tel:{esc(k["telefon"].replace(" ", ""))}">{ui("tel")}<span>{esc(k["telefon"])}</span></a>'
            f'<a href="mailto:{esc(k["email"])}">{ui("mail")}<span>{esc(k["email"])}</span></a></div>')


def _lx1(c):
    l = c["latogatas"]
    return (f'<section class="sec v-lx1 s-sand tx" id="kapcsolat">{hat(c)}{dk(c, "latogatas")}<div class="wrap grid">'
            f'<div class="bal" data-rv>{kick(l.get("kicker"))}<h2 class="cim">{md(l["cim"])}</h2><p class="lead">{md(l["lead"])}</p>{gombsor(l)}</div>'
            f'<div class="nj-w" data-rv><div class="nj s-vilagos"><div class="nj-f">{logo(c, 38)}<i class="ag" aria-hidden="true"></i></div>'
            f'<p class="nev">Koppány Lili</p><p class="mono szerep">okleveles tájépítészmérnök</p>{_elerhet(c)}'
            f'</div></div></div></section>')


LX1_CSS = LAT_KOZOS + T(r"""
.v-lx1 .grid{display:grid;grid-template-columns:1fr 1fr;gap:clamp(30px,5cqi,80px);align-items:center}
.v-lx1 .lead{margin:16px 0 26px}
.v-lx1 .nj-w{position:relative;justify-self:center;width:min(100%,470px);padding:18px 18px 18px 0}
.v-lx1 .nj-w::before{content:"";position:absolute;inset:24px 0 0 24px;background:var(--c-primary);border-radius:12px;transform:rotate(3deg);opacity:.9}
.v-lx1 .nj{position:relative;background:var(--c0-card);border-radius:12px;padding:clamp(20px,3cqi,32px);box-shadow:0 30px 50px -30px rgba(0,0,0,.55),0 1px 3px rgba(0,0,0,.06);transform:rotate(-2.5deg);overflow:hidden}
.v-lx1 .nj-f{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-bottom:14px;border-bottom:1px solid var(--c-line)}
.v-lx1 .nj .logo{background-image:var(--logo-eredeti)!important}
.v-lx1 .ag{width:110px;aspect-ratio:@FEKVO_AR@;background:var(--c-accent);""" + mask("FEKVO") + r""";opacity:.9}
.v-lx1 .nev{font-family:var(--f-display);font-weight:var(--w-display);font-size:1.55rem;line-height:1.1;margin:16px 0 2px;color:var(--c-head)}
.v-lx1 .szerep{font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:var(--c-ink-3);margin:0 0 14px}
.v-lx1 .adat{margin-top:0}
.v-lx1 .ter{display:flex;gap:10px;align-items:flex-start;margin:12px 0 0;font-size:.9rem;color:var(--c-ink-2)}
.v-lx1 .ter .ui{color:var(--hl);flex:none;margin-top:2px}
@container elo (max-width:860px){.v-lx1 .grid{grid-template-columns:1fr}}
""")

# ------------------------------------------------------------------ LÁBLÉC: ceruzás mező (a mostani, frissítve)


def _lbx1(c):
    return (f'<footer class="v-lbx1 s-white"><div class="mezo" aria-hidden="true"></div><div class="wrap"><div class="cols">'
            f'<div class="c0">{logo(c, 52)}<p>{md(c["lablec"]["szoveg"])}</p></div>'
            f'<div><h4>Oldalak</h4><nav>{_lbl_linkek(c)}</nav></div>'
            f'<div><h4>Elérhetőség</h4>{_elerhet(c)}</div></div>'
            f'<div class="also">{_jogi(c)}</div></div></footer>')


LBX1_CSS = LBL_KOZOS + LAT_KOZOS + T(r"""
.v-lbx1{background:var(--c-card);padding:0 0 24px;position:relative}
.v-lbx1 .mezo{height:clamp(70px,9cqi,112px);background:var(--c-ink-3);""" + mask("MEZO", "0 100%/auto 100% repeat-x") + r""";opacity:.75}
.v-lbx1 .cols{display:grid;grid-template-columns:1.3fr 1fr 1.2fr;gap:clamp(24px,4cqi,60px);padding-top:clamp(30px,4cqi,46px);border-top:1px solid var(--c-line2)}
.v-lbx1 .c0 p{margin:16px 0 0;color:var(--c-ink-2);max-width:36ch}
.v-lbx1 .adat{margin-top:0}
.v-lbx1 .ter{margin:12px 0 0;font-size:.9rem;color:var(--c-ink-2)}
.v-lbx1 .also{margin-top:34px;padding-top:16px;border-top:1px solid var(--c-line)}
.elo-root .v-lbx1 h4{font-family:var(--f-body);font-size:.76rem;letter-spacing:.16em;text-transform:uppercase;font-weight:800;margin-bottom:14px;color:var(--c-head)}
@container elo (max-width:820px){.v-lbx1 .cols{grid-template-columns:1fr 1fr}}
@container elo (max-width:520px){.v-lbx1 .cols{grid-template-columns:1fr}}
""")

# ------------------------------------------------------------------ szekció-listák (a beadott oldal szekciói, 5-5 elrendezés)

SZEKCIO_OPCIOK = {"nav": ["n2", "n1", "n3", "n6", "n5"], "hero": ["hx1", "h3", "h5", "h6", "h1"], "folyamat": ["fx1", "f1", "f2", "f3", "f4"],
                  "kinalat": ["kx1", "kx2", "kx3", "kx4", "k1"], "tenyek": ["tx1", "p1", "p3", "p4", "p5"],
                  "tortenet": ["t1", "t2", "t3", "t4", "t5"], "latogatas": ["lx1", "l5", "l2", "l4", "l1"], "lablec": ["lbx1", "lb1", "lb2", "lb3", "lb4"],
                  "garancia": list(GAR_CSS), "gyik": list(GYIK_CSS), "ajanlatkeres": list(AJ_CSS)}
SZEKCIO_AJANLOTT = {"nav": "n2", "hero": "hx1", "folyamat": "fx1", "kinalat": "kx1", "tenyek": "tx1", "garancia": "gx2", "tortenet": "t1",
                    "gyik": "yx1", "ajanlatkeres": "ax1", "latogatas": "lx1", "lablec": "lbx1"}
SZEKCIO_MIERT = {
    "nav": {"n2": "A mostani oldalad zöld felső sávja a telefonnal és az e-maillel, rendezettebben: felül a gyakorlati infó (telefon, visszahívási idő, terület), alatta a menü.",
            "n1": "Lebegő, lekerekített menüsáv, ami a kertfotó fölött úszik és görgetéskor végig kéznél van. Könnyed, mai.",
            "n3": "Középen a KL-monogram egy lelógó fülön, két oldalt a menü. Klasszikus, butikos hangulat.",
            "n6": "Nagy, középre zárt monogram vékony vonalak között, alatta a menü, mint egy szép kiadvány fejléce.",
            "n5": "Csak a monogram, egy nagy, kattintható telefonszám és egy Menü gomb. Mobilon a legtisztább."},
    "hero": {"hx1": "Csak nektek: a kertfotó egy milliméterpapír tervlapon, rajta a vázlatod egy rátűzött lapon, északjel és szövegmező a neveddel. „A rajzból kert lesz”: a cím a mostani mondatod.",
             "h3": "A mostani nyitóképed: a vlinderhofi évelőágyás kitölti a képernyőt, rajta egy tiszta, világos kártya a címmel és a gombokkal.",
             "h5": "Kettéosztott kép: balra a szöveg a három ígérettel (ingyenes konzultáció, 2 munkanap, korlátlan áttervezés), jobbra a nagy kertfotó lebegő kártyával.",
             "h6": "Középen a cím, körülötte négy fotó (gyep, évelőágyás, tölgy, te a szabadban) lassan lebeg. Nyitott, barátságos.",
             "h1": "Telt zsályazöld háttér, balra a nagy cím, jobbra egymásra csúsztatott fotók és a monogram matricaként. Harsányabb, emlékezetes."},
    "folyamat": {"fx1": "Csak nektek: a lépések lépőkövek egy kanyargó kerti ösvényen. Öt fő lépés a tervezés menetéből, a teljes lista a menet-oldalon marad.",
                 "f1": "Lépés-kártyák egy szaggatott útvonalon, számozott pecséttel. Egyértelmű, „ilyen egyszerű”.",
                 "f2": "Függőleges, szaggatott idővonal, a lépések felváltva balra és jobbra. Mesélős, mint a kert útja a tervtől a kiültetésig.",
                 "f3": "Óriás, kontúros sorszámok vastag vonal alatt, mellettük ikon és rövid szöveg. Szerkesztőségi, sok levegővel.",
                 "f4": "A lépés-kártyák lépcsőzetesen emelkednek, mintha egyre közelebb vinnének a kész tervhez."},
    "kinalat": {"kx1": "A mostani elrendezésed, rendezettebben: hat kártya, mindegyiken nagyban a rajz (az ikonstílusban választottal) és a szolgáltatás neve.",
                "kx2": "A hat elem két csoportban: „Miben segítek?” (tanácsadás, növényágyak, kerttervezés) és „Milyen kertekben?” (családi ház, társasház, előkert). Gyorsabban érthető.",
                "kx3": "Csak nektek: egy nagy kertterv-rajz számozott jelekkel, mellette jelmagyarázatként a hat szolgáltatás, mint egy igazi tervlapon.",
                "kx4": "Hat fa növénycímke, ahogy a kertészetben a növények mellé szúrják; rajtuk a rajz és kézírással a szolgáltatás neve. Barátságos, kézzelfogható.",
                "k1": "Tiszta ikonos kártyarács: ikon és név egy sorban. A legegyszerűbb, a választott kártyastílus viszi."},
    "tenyek": {"tx1": "A mostani megoldásod frissítve: három kártya a virágzó évelőágyás fotóján, a középső kicsit kiemelve.",
               "p1": "Három kártya: ikon, cím, rövid magyarázat. A választott kártyastílust kapja, nagyon rendezett.",
               "p3": "Egyetlen tiszta sor ikonnal és szöveggel, szaggatott elválasztókkal, kártyák nélkül. Levegős.",
               "p4": "Kerek pecsétek körbefutó felirattal, középen az ikon. Kézműves, „minőségi” hatás.",
               "p5": "Balra a cím, jobbra nagy betűs kulcsszavak vékony vonalak között. Magazinos, magabiztos."},
    "tortenet": {"t1": "A portréd, mellette a bemutatkozásod, kiemelve a mondatod („Mindenkinek kellene egy kert. Akkor is, ha elfoglalt.”) és kézírásos aláírás.",
                 "t2": "Balra a bemutatkozás, jobbra három egymásra dobott, feliratos fotó: a portréd, a tölgy-ölelés és a bátaszéki molyhos tölgy.",
                 "t3": "Rövid bemutatkozás fotóval, alatta idővonal: virágkötő-álom 3 évesen, diploma, 2,5 év tájépítész iroda, kerttervezés, favizsgáló képzés.",
                 "t4": "Óriás idézőjel a mondatoddal és kerek portré, alatta két hasábban a bemutatkozás. Erős, emberi.",
                 "t5": "A bemutatkozás egy vonalas levélpapíron, felragasztott fotóval és aláírással. Nagyon személyes."},
    "latogatas": {"lx1": "Csak nektek: a kapcsolat egy névjegykártyán a monogrammal és egy ceruzás ággal, mellette a meghívó szöveged és a két gomb (hívás, e-mail).",
                  "l5": "Balra a tulipános portréd, jobbra a meghívó szöveg és két hasáb: mire számíthatsz (visszahívás, válaszidő, ingyenes konzultáció) és elérhetőség.",
                  "l2": "Sötét záró blokk, benne a telefonszámod óriási, kattintható betűkkel. Egyértelmű: „hívj, és kész”.",
                  "l4": "Rajzolt, zöld „térkép” lüktető tűvel, előtte kártya a meghívással és a válaszidőkkel. Helyi, „itt vagyok a környéken”.",
                  "l1": "Telt zöld blokk nagy meghívással és gombokkal, mellette tiszta kártya a válaszidőkkel és az elérhetőséggel."},
    "lablec": {"lbx1": "A mostani láblécedben lévő ceruzás virágmező a lábléc tetején, alatta monogram, oldalak, elérhetőség, jogi sor. Ismerős, csak rendezettebb.",
               "lb1": "Klasszikus sötét lábléc négy hasábbal: monogram és rövid szöveg, oldalak, elérhetőség, válaszidők.",
               "lb2": "Világos lábléc, az alján a neved a teljes szélességben, óriási betűkkel. Magabiztos lezárás.",
               "lb3": "Minden középen: monogram, egy sor menü, apró betűs adatok. Csendes, elegáns.",
               "lb4": "Zöld, lekerekített lábléc, a tetején nagy felhívás az ingyenes konzultációra és a telefonszám."},
}

# ------------------------------------------------------------------ globális finomítások

EGYEDI_CSS = r"""
/* a ceruzarajz-ikonok (iL) sötét felületen világos vonallal */
[data-ikon="iL"] .s-deep .ik:not(.s-vilagos .ik){filter:invert(1) brightness(1.25)}
[data-paletta="pB"][data-ikon="iL"] .ik{filter:invert(1) brightness(1.25)}
[data-paletta="pB"][data-ikon="iL"] .s-vilagos .ik,[data-paletta="pB"][data-ikon="iL"] .v-kx3 .rajzlap .ik,[data-paletta="pB"][data-ikon="iL"] .v-kx4 .ncimke .ik{filter:none}
/* hosszú hero-cím: kicsit kisebb a könyvtári hero-változatokban is */
.v-h1 .hcim,.v-h3 .hcim,.v-h5 .hcim,.v-h6 .hcim{font-size:calc(var(--t-hero)*.84)}
/* Felfelé lépcső: 5 keskeny kártyán a hosszú lépésnév ne lógjon ki */
.v-f4 .krt-fej{flex-direction:column;align-items:flex-start;gap:8px}.v-f4 .krt-h{font-size:1rem;hyphens:auto;overflow-wrap:break-word}
/* nincs közösségi oldal: a színes lábléc üres „Kövess” oszlopa ne látsszon */
.v-lb4 .cols>div:last-child:not(:has(a)){display:none}
"""


def osszeallit():
    spec = tartalom()
    c = ctx_epit(spec)
    egyedi = {k: [dict(x, leiras=x["miert"]) for x in v] for k, v in STILUS.items()}
    egyedi["mozgas"] = [dict(x, leiras=x["miert"]) for x in MOZGAS_SAJAT]
    egyedi["hero"] = [dict(id="hx1", nev="Tervlap: a rajzból kert lesz", leiras=SZEKCIO_MIERT["hero"]["hx1"], html=_hx1(c), css=HX1_CSS)]
    egyedi["folyamat"] = [dict(id="fx1", nev="Kerti ösvény lépőkövekkel", leiras=SZEKCIO_MIERT["folyamat"]["fx1"], html=_fx1(c), css=FX1_CSS)]
    egyedi["kinalat"] = [dict(id="kx1", nev="Nagy rajzok rácsban", leiras=SZEKCIO_MIERT["kinalat"]["kx1"], html=_kx1(c), css=KX1_CSS),
                         dict(id="kx2", nev="Két csoport: mit és milyen kertet", leiras=SZEKCIO_MIERT["kinalat"]["kx2"], html=_kx2(c), css=KX2_CSS),
                         dict(id="kx3", nev="Kertterv jelmagyarázattal", leiras=SZEKCIO_MIERT["kinalat"]["kx3"], html=_kx3(c), css=KX3_CSS),
                         dict(id="kx4", nev="Növénycímkék", leiras=SZEKCIO_MIERT["kinalat"]["kx4"], html=_kx4(c), css=KX4_CSS)]
    egyedi["tenyek"] = [dict(id="tx1", nev="Kártyák virágos fotón", leiras=SZEKCIO_MIERT["tenyek"]["tx1"], html=_tx1(c), css=TX1_CSS)]
    egyedi["garancia"] = [dict(id=k, nev=n, leiras=l, html=GAR_REND[k](c), css=css) for k, (n, l, css) in GAR_CSS.items()]
    egyedi["gyik"] = [dict(id=k, nev=n, leiras=l, html=GYIK_REND[k](c), css=GYIK_ALAP.replace("%(v)s", k) + css) for k, (n, l, css) in GYIK_CSS.items()]
    egyedi["ajanlatkeres"] = [dict(id=k, nev=n, leiras=l, html=AJ_REND[k](c), css=urlap_css(k) + css) for k, (n, l, css) in AJ_CSS.items()]
    egyedi["latogatas"] = [dict(id="lx1", nev="Névjegykártya", leiras=SZEKCIO_MIERT["latogatas"]["lx1"], html=_lx1(c), css=LX1_CSS)]
    egyedi["lablec"] = [dict(id="lbx1", nev="Ceruzás virágmező", leiras=SZEKCIO_MIERT["lablec"]["lbx1"], html=_lbx1(c), css=LBX1_CSS)]
    opciok = {
        "paletta": {"ajanlott": AJANLOTT["paletta"], "lista": PALETTAK},
        "betu": {"ajanlott": AJANLOTT["betu"], "lista": BETUK},
        "ikon": {"ajanlott": AJANLOTT["ikon"], "miert": IKON_MIERT},
        "mozgas": {"ajanlott": AJANLOTT["mozgas"], "lista": ["m1", "m2", "mW", "mB", "m5"], "miert": MOZGAS_MIERT},
    }
    for kat, lst in STILUS.items():
        opciok[kat] = {"ajanlott": AJANLOTT[kat], "lista": [x["id"] for x in lst], "miert": {x["id"]: x["miert"] for x in lst}}
    for slot in spec["szekcio_sorrend"]:
        miert = dict(SZEKCIO_MIERT.get(slot, {}))
        for x in egyedi.get(slot, []):
            miert.setdefault(x["id"], x["leiras"])
        opciok[slot] = {"ajanlott": SZEKCIO_AJANLOTT[slot], "lista": SZEKCIO_OPCIOK[slot], "miert": miert}
    spec["opciok"] = opciok
    spec["egyedi_opciok"] = egyedi
    spec["egyedi_css"] = EGYEDI_CSS
    (ITT / "arculat.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(len(v) for v in egyedi.values())
    print(f"arculat.json kész ({(ITT / 'arculat.json').stat().st_size / 1024:.0f} KB), {n} egyedi opció")


if __name__ == "__main__":
    osszeallit()
