# -*- coding: utf-8 -*-
"""Rajzoló alapkönyvtár a prezi-motorhoz: natív, szerkeszthető PowerPoint-elemek, témavezérelten.

Hordozható, natív PowerPoint-motor. Nincs benne beégetett szín, betű, logó vagy
útvonal: minden az aktív témából (T, lásd tema.py) jön, HÍVÁSKOR olvasva (nem def-időben kötött alapértékből).

Színek: bárhol megadható szerepnév ("primary", "ink", "on_deep"...), "#RRGGBB" vagy (r, g, b).
Betűk: szerepnév ("cim", "torzs", "kezi", "cimke"). A mérés (szelesseg, sorok, fit_blokk) a dián megjelenő TTF-fel
számol. A LibreOffice és a PowerPoint sormagassága 1,2 × pontméret × sorköz; az első alapvonal a doboz tetejétől
(1,2 × sorköz − 0,2) × pontméretnyire van. Erre épül a címsor-kiemelések helye.
"""
import hashlib
import json
import math
import os
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

SZ, MA = 13.333, 7.5
EMU_IN = 914400
L, C, R = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MID, BOT = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE, MSO_ANCHOR.BOTTOM
HERE = Path(__file__).resolve().parent

T = None          # az aktív téma (tema.Tema); a tema.bekapcsol() állítja be


# ------------------------------------------------------------------ gyorsítótár (a felhasználói mappában)

def cache_mappa(*al):
    if sys.platform == "darwin":
        m = Path.home() / "Library" / "Caches" / "ai-arculat-generator" / "prezi"
    elif os.name == "nt":
        m = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "ai-arculat-generator" / "cache" / "prezi"
    else:
        m = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "ai-arculat-generator" / "prezi"
    m = m.joinpath(*al)
    m.mkdir(parents=True, exist_ok=True)
    return m


# ------------------------------------------------------------------ színek

def hex2rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgbt(c):
    """Szín tuple-ként: szerepnév, '#hex', tuple vagy RGBColor."""
    if isinstance(c, RGBColor):
        s = str(c)
        return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
    if isinstance(c, (tuple, list)):
        return tuple(int(x) for x in c[:3])
    if isinstance(c, str):
        if c.startswith("#"):
            return hex2rgb(c)
        if T is not None and c in T.szin:
            return hex2rgb(T.szin[c])
        if len(c) == 6:
            try:
                return hex2rgb(c)
            except ValueError:
                pass
    raise ValueError("Ismeretlen szín: %r" % (c,))


def rgb(c):
    t = rgbt(c)
    return RGBColor(t[0], t[1], t[2])


def hexs(c):
    return "%02X%02X%02X" % rgbt(c)


def kever(a, b, t):
    """a és b keveréke (t=0: a, t=1: b). Árnyalatot csak a téma színeiből képzünk, új színt nem."""
    a, b = rgbt(a), rgbt(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def lum(c):
    def f(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgbt(c)
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def kontraszt(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def sotet(c):
    return lum(c) < 0.25


# ------------------------------------------------------------------ betűk és mérés

def betu(font="torzs", bold=None):
    """(typeface, bold, ttf) a szerephez. A 'cim' vastagsága a témából jön (a jóváhagyott súly), a többinél bold=True
    a család félkövér változata."""
    if T is None or font not in T.betu:
        return font, bool(bold), None
    b = T.betu[font]
    if font == "cim":
        if bold is False:
            return b["typeface"], False, b["ttf"]
        return b["typeface"], b["bold"], b["ttf"]
    if bold:
        return b["b_typeface"], True, b["ttf_b"]
    return b["typeface"], False, b["ttf"]


_FONT_CACHE = {}


def _pil_font(ttf):
    if ttf not in _FONT_CACHE:
        _FONT_CACHE[ttf] = ImageFont.truetype(ttf, 200) if ttf and os.path.exists(ttf) else None
    return _FONT_CACHE[ttf]


def szelesseg(szoveg, pt, font="cim", bold=None):
    """A szöveg szélessége HÜVELYKBEN, a dián megjelenő betűvel mérve."""
    f = _pil_font(betu(font, bold)[2])
    if f is None:
        return len(szoveg) * pt / 72.0 * 0.6
    return f.getlength(szoveg) / 200.0 * pt / 72.0


def sorok(szoveg, box_w, pt, font="torzs", bold=None):
    """A szöveg sorai `box_w` hüvelyk szélességben, valódi szóhatárokkal (mint a LibreOffice és a PowerPoint).
    A kézi sortörést (\\n) is tiszteli."""
    import re
    ki = []
    for bek in re.split(r"[\n\v]", szoveg or ""):
        sor = ""
        for szo in bek.split():
            proba = (sor + " " + szo).strip()
            if not sor or szelesseg(proba, pt, font, bold) <= box_w:
                sor = proba
            else:
                ki.append(sor)
                sor = szo
        ki.append(sor)
    return ki


def sorszam(szoveg, box_w, pt, font="torzs", bold=None):
    return len(sorok(szoveg, box_w, pt, font, bold)) if szoveg else 0


def sormagassag(pt, spacing=1.0):
    return pt * 1.2 * spacing / 72.0


def blokk_magassag(szoveg, box_w, pt, font="torzs", bold=None, spacing=1.0):
    return sorszam(szoveg, box_w, pt, font, bold) * sormagassag(pt, spacing)


def fit(szoveg, box_w, pt, font="cim", bold=None, min_pt=None):
    """Akkora pontméret, amivel a szöveg EGY sorba kifér (sosem kisebb, mint min_pt, alapból az eredeti 55%-a)."""
    if not szoveg:
        return pt
    min_pt = min_pt or pt * 0.55
    w = max(szelesseg(x, pt, font, bold) for x in szoveg.replace("\v", "\n").split("\n"))
    if w <= box_w * 0.985 or w <= 0:
        return pt
    return round(max(min_pt, pt * box_w * 0.985 / w), 1)


def fit_blokk(szoveg, box_w, box_h, pt, font="cim", bold=None, spacing=1.0, min_pt=None):
    """A legnagyobb pontméret (legfeljebb pt), amivel a szöveg több sorban elfér a box_w × box_h dobozban, és egyetlen
    szó sem lóg ki a szélességből."""
    if not szoveg:
        return pt
    min_pt = min_pt or pt * 0.6
    m = float(pt)
    leghosszabb = max(szoveg.split(), key=lambda s: szelesseg(s, 10, font, bold))
    while m > min_pt:
        if (szelesseg(leghosszabb, m, font, bold) <= box_w and
                blokk_magassag(szoveg, box_w, m, font, bold, spacing) <= box_h):
            return round(m, 1)
        m -= 1
    return round(min_pt, 1)


def alapvonal(y, pt, spacing=1.0, sor=0):
    """A sor-adik sor alapvonala (hüvelyk), ha a szövegdoboz teteje y."""
    lh = sormagassag(pt, spacing)
    return y + sor * lh + lh - 0.2 * pt / 72.0


def kiemeles_bont(szoveg):
    """'A ==kerttervezés== menete' -> ('A kerttervezés menete', [(2, 14)]) (karakterpozíciók)."""
    sima, tart, i, kezd = "", [], 0, None
    darabok = (szoveg or "").split("==")
    for j, d in enumerate(darabok):
        if j % 2 == 1:
            tart.append((len(sima), len(sima) + len(d)))
        sima += d
    return sima, tart


def szo_helyek(szoveg, box_w, pt, font="cim", bold=None, align=L):
    """Minden szó helye a tördelt szövegben: [(szó, kezdő_karakter, sor, x0, x1)] (x a doboz bal szélétől, hüvelyk)."""
    import re
    ki = []
    poz = 0
    sor_i = 0
    for bek in re.split(r"[\n\v]", szoveg or ""):
        szavak = []
        for szo in bek.split(" "):
            szavak.append((szo, poz))
            poz += len(szo) + 1
        sor_szavak = []
        sorok_ = []
        for szo, p in szavak:
            if not szo:
                continue
            proba = " ".join(x[0] for x in sor_szavak + [(szo, p)])
            if sor_szavak and szelesseg(proba, pt, font, bold) > box_w:
                sorok_.append(sor_szavak)
                sor_szavak = [(szo, p)]
            else:
                sor_szavak.append((szo, p))
        sorok_.append(sor_szavak)
        for sz in sorok_:
            teljes = szelesseg(" ".join(x[0] for x in sz), pt, font, bold)
            eltol = 0 if align == L else ((box_w - teljes) / 2.0 if align == C else box_w - teljes)
            elotte = ""
            for szo, p in sz:
                x0 = eltol + (szelesseg(elotte + " ", pt, font, bold) if elotte else 0)
                x1 = x0 + szelesseg(szo, pt, font, bold)
                ki.append((szo, p, sor_i, x0, x1))
                elotte = (elotte + " " + szo).strip()
            sor_i += 1
    return ki


# ------------------------------------------------------------------ prezentáció, dia, jegyzet

def new_prs():
    prs = Presentation()
    prs.slide_width = Inches(SZ)
    prs.slide_height = Inches(MA)
    return prs


def slide(prs, bg="paper"):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    if bg is not None:
        rect(s, 0, 0, SZ, MA, fill=bg)
    return s


def jegyzet(s, szoveg):
    if szoveg:
        s.notes_slide.notes_text_frame.text = szoveg


# ------------------------------------------------------------------ alakzatok

def _noline(sp):
    sp.line.fill.background()


def rect(s, x, y, w, h, fill=None, line=None, lw=1.0, shape=MSO_SHAPE.RECTANGLE, rad=None):
    sp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = rgb(fill)
    if line is None:
        _noline(sp)
    else:
        sp.line.color.rgb = rgb(line)
        sp.line.width = Pt(lw)
    sp.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE and rad is not None:
        try:
            sp.adjustments[0] = max(0.0, min(0.5, rad))
        except Exception:
            pass
    return sp


def kartya(s, x, y, w, h, fill="card", line=None, lw=None, r=None, arnyek_=None):
    """Kártya a téma lekerekítésével (r: hüvelyk; alapból T.r_kartya), keretével és árnyékával."""
    r = T.r_kartya if r is None else r
    rad = min(0.5, r / max(min(w, h), 0.01))
    if line is None and T.keret_pt > 0:
        line = "line"
    lw = T.keret_pt if lw is None else lw
    sp = rect(s, x, y, w, h, fill=fill, line=line, lw=lw or 1.0,
              shape=MSO_SHAPE.ROUNDED_RECTANGLE if rad > 0.004 else MSO_SHAPE.RECTANGLE, rad=rad)
    if (arnyek_ if arnyek_ is not None else T.arnyek) in ("lagy", "eros"):
        arnyek(sp, arnyek_ or T.arnyek)
    return sp


def oval(s, x, y, w, h, fill="accent", line=None, lw=1.0):
    sp = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = rgb(fill)
    if line is None:
        _noline(sp)
    else:
        sp.line.color.rgb = rgb(line)
        sp.line.width = Pt(lw)
    sp.shadow.inherit = False
    return sp


def _fill_csere(spPr, uj):
    for tag in ("a:noFill", "a:solidFill", "a:gradFill", "a:blipFill", "a:pattFill", "a:grpFill"):
        e = spPr.find(qn(tag))
        if e is not None:
            spPr.remove(e)
    ln = spPr.find(qn("a:ln"))
    if ln is not None:
        spPr.insert(list(spPr).index(ln), uj)
    else:
        prst = spPr.find(qn("a:prstGeom"))
        if prst is None:
            prst = spPr.find(qn("a:custGeom"))
        if prst is not None:
            prst.addnext(uj)
        else:
            spPr.append(uj)


def gradient(sp, c1, c2, angle=45):
    """Lineáris színátmenet (c1 -> c2) a téma színeiből."""
    spPr = sp.fill._xPr
    g = spPr.makeelement(qn("a:gradFill"), {"rotWithShape": "1"})
    lst = g.makeelement(qn("a:gsLst"), {})
    for pos, col in ((0, c1), (100000, c2)):
        gs = g.makeelement(qn("a:gs"), {"pos": str(pos)})
        gs.append(g.makeelement(qn("a:srgbClr"), {"val": hexs(col)}))
        lst.append(gs)
    g.append(lst)
    g.append(g.makeelement(qn("a:lin"), {"ang": str(int(angle * 60000)), "scaled": "1"}))
    _fill_csere(spPr, g)


def set_fill_alpha(shape, opacity_pct):
    srgb = shape.fill._xPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
    srgb.append(srgb.makeelement(qn("a:alpha"), {"val": str(int(opacity_pct * 1000))}))


def set_line_alpha(shape, opacity_pct):
    ln = shape._element.spPr.find(qn("a:ln"))
    if ln is None:
        return
    sf = ln.find(qn("a:solidFill"))
    if sf is not None:
        c = sf.find(qn("a:srgbClr"))
        c.append(c.makeelement(qn("a:alpha"), {"val": str(int(opacity_pct * 1000))}))


def vonal_kerek(shape):
    """Kerek vonalvég és -illesztés (ceruzás, kézi hatású vonalakhoz)."""
    ln = shape._element.spPr.find(qn("a:ln"))
    if ln is None:
        return
    ln.set("cap", "rnd")
    if ln.find(qn("a:round")) is None:
        ln.append(ln.makeelement(qn("a:round"), {}))


def overlay(s, x, y, w, h, color="deep", opacity=55):
    r = rect(s, x, y, w, h, fill=color)
    set_fill_alpha(r, opacity)
    return r


def veil_grad(s, x, y, w, h, color="deep", a_top=0, a_bot=82, angle=90):
    """Átlátszóból színbe menő fátyol (fotó fölé, hogy a szöveg olvasható legyen)."""
    sp = rect(s, x, y, w, h, fill=color)
    spPr = sp.fill._xPr
    g = spPr.makeelement(qn("a:gradFill"), {"rotWithShape": "1"})
    lst = g.makeelement(qn("a:gsLst"), {})
    for pos, al in ((0, a_top), (100000, a_bot)):
        gs = g.makeelement(qn("a:gs"), {"pos": str(pos)})
        sc = g.makeelement(qn("a:srgbClr"), {"val": hexs(color)})
        sc.append(sc.makeelement(qn("a:alpha"), {"val": str(int(al * 1000))}))
        gs.append(sc)
        lst.append(gs)
    g.append(lst)
    g.append(g.makeelement(qn("a:lin"), {"ang": str(int(angle * 60000)), "scaled": "1"}))
    _fill_csere(spPr, g)
    return sp


def arnyek(sp, erosseg="lagy"):
    """Külső árnyék: 'lagy' = puha, lefelé; 'eros' = kemény, eltolt (a webes 'eros' árnyék párja)."""
    spPr = sp._element.spPr
    for e in spPr.findall(qn("a:effectLst")):
        spPr.remove(e)
    eff = spPr.makeelement(qn("a:effectLst"), {})
    if erosseg == "eros":
        attr = {"blurRad": "0", "dist": str(int(0.07 * EMU_IN)), "dir": "2700000", "algn": "tl", "rotWithShape": "0"}
        alfa = 100
        szin = hexs("ink")
    else:
        attr = {"blurRad": str(int(0.16 * EMU_IN)), "dist": str(int(0.05 * EMU_IN)), "dir": "5400000", "algn": "t",
                "rotWithShape": "0"}
        alfa = 22
        szin = hexs("ink")
    sh = eff.makeelement(qn("a:outerShdw"), attr)
    c = sh.makeelement(qn("a:srgbClr"), {"val": szin})
    c.append(c.makeelement(qn("a:alpha"), {"val": str(alfa * 1000)}))
    sh.append(c)
    eff.append(sh)
    ln = spPr.find(qn("a:ln"))
    if ln is not None:
        ln.addnext(eff)
    else:
        spPr.append(eff)
    return sp


def sokszog(s, pontok, fill=None, line=None, lw=1.0, zart=True, alpha=None, line_alpha=None):
    """Szabad alakzat hüvelykben megadott pontokból (natív, szerkeszthető)."""
    x0 = min(p[0] for p in pontok)
    y0 = min(p[1] for p in pontok)
    fb = s.shapes.build_freeform(int(pontok[0][0] * EMU_IN), int(pontok[0][1] * EMU_IN), scale=1.0)
    fb.add_line_segments([(int(x * EMU_IN), int(y * EMU_IN)) for x, y in pontok[1:]], close=zart)
    sp = fb.convert_to_shape()
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = rgb(fill)
        if alpha is not None:
            set_fill_alpha(sp, alpha)
    if line is None:
        _noline(sp)
    else:
        sp.line.color.rgb = rgb(line)
        sp.line.width = Pt(lw)
        if line_alpha is not None:
            set_line_alpha(sp, line_alpha)
    sp.shadow.inherit = False
    return sp


# ------------------------------------------------------------------ SVG-motívum -> natív alakzat

def _bezier(p0, p1, p2, p3, n=14):
    return [((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0],
             (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1])
            for t in [i / float(n) for i in range(1, n + 1)]]


def _ivpontok(p0, rx, ry, phi, nagy, irany, p1, n=16):
    # SVG ív -> pontok (a W3C implementációs jegyzet szerint)
    if rx == 0 or ry == 0:
        return [p1]
    cp, sp_ = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (p0[0] - p1[0]) / 2.0, (p0[1] - p1[1]) / 2.0
    x1 = cp * dx + sp_ * dy
    y1 = -sp_ * dx + cp * dy
    lam = (x1 ** 2) / (rx ** 2) + (y1 ** 2) / (ry ** 2)
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1 ** 2 - ry ** 2 * x1 ** 2
    den = rx ** 2 * y1 ** 2 + ry ** 2 * x1 ** 2
    k = math.sqrt(max(0.0, num / den)) if den else 0.0
    if nagy == irany:
        k = -k
    cx1, cy1 = k * rx * y1 / ry, -k * ry * x1 / rx
    cx = cp * cx1 - sp_ * cy1 + (p0[0] + p1[0]) / 2.0
    cy = sp_ * cx1 + cp * cy1 + (p0[1] + p1[1]) / 2.0

    def szog(u, v):
        a = math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])
        return a
    t1 = szog((1, 0), ((x1 - cx1) / rx, (y1 - cy1) / ry))
    dt = szog(((x1 - cx1) / rx, (y1 - cy1) / ry), ((-x1 - cx1) / rx, (-y1 - cy1) / ry))
    if not irany and dt > 0:
        dt -= 2 * math.pi
    elif irany and dt < 0:
        dt += 2 * math.pi
    ki = []
    for i in range(1, n + 1):
        t = t1 + dt * i / float(n)
        ki.append((cx + rx * math.cos(t) * cp - ry * math.sin(t) * sp_, cy + rx * math.cos(t) * sp_ + ry * math.sin(t) * cp))
    return ki


def _path_pontok(d):
    """SVG path -> alútvonalak pontlistái (M, L, H, V, C, S, Q, T, A, Z; abszolút és relatív)."""
    import re
    tok = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    utak, ut = [], []
    i, cmd = 0, None
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    utolso_c = None

    def num():
        nonlocal i
        v = float(tok[i])
        i += 1
        return v
    while i < len(tok):
        if tok[i].isalpha():
            cmd = tok[i]
            i += 1
            if cmd in "Zz":
                if ut:
                    utak.append(ut)
                ut = []
                cur = start
                continue
        rel = cmd.islower()
        c = cmd.upper()
        ox, oy = (cur if rel else (0.0, 0.0))
        if c == "M":
            cur = (num() + ox, num() + oy)
            if ut:
                utak.append(ut)
            ut = [cur]
            start = cur
            cmd = "l" if rel else "L"
        elif c == "L":
            cur = (num() + ox, num() + oy)
            ut.append(cur)
        elif c == "H":
            cur = (num() + (cur[0] if rel else 0), cur[1])
            ut.append(cur)
        elif c == "V":
            cur = (cur[0], num() + (cur[1] if rel else 0))
            ut.append(cur)
        elif c == "C":
            p1 = (num() + ox, num() + oy)
            p2 = (num() + ox, num() + oy)
            p3 = (num() + ox, num() + oy)
            ut += _bezier(cur, p1, p2, p3)
            utolso_c = p2
            cur = p3
        elif c == "S":
            p1 = (2 * cur[0] - utolso_c[0], 2 * cur[1] - utolso_c[1]) if utolso_c else cur
            p2 = (num() + ox, num() + oy)
            p3 = (num() + ox, num() + oy)
            ut += _bezier(cur, p1, p2, p3)
            utolso_c = p2
            cur = p3
        elif c == "Q":
            q = (num() + ox, num() + oy)
            p3 = (num() + ox, num() + oy)
            p1 = (cur[0] + 2 / 3.0 * (q[0] - cur[0]), cur[1] + 2 / 3.0 * (q[1] - cur[1]))
            p2 = (p3[0] + 2 / 3.0 * (q[0] - p3[0]), p3[1] + 2 / 3.0 * (q[1] - p3[1]))
            ut += _bezier(cur, p1, p2, p3)
            cur = p3
        elif c == "T":
            p3 = (num() + ox, num() + oy)
            ut.append(p3)
            cur = p3
        elif c == "A":
            rx, ry, phi, nagy, irany = num(), num(), num(), num(), num()
            p3 = (num() + ox, num() + oy)
            ut += _ivpontok(cur, rx, ry, phi, int(nagy), int(irany), p3)
            cur = p3
        else:
            i += 1
    if ut:
        utak.append(ut)
    return [u for u in utak if len(u) >= 3]


def svg_utak(svg):
    """Egy egyszerű (fekete kitöltésű) SVG elemei pontlistákként, a viewBox 0..1 tartományára vetítve.
    Kezeli: path, circle, ellipse, rect, polygon; transform: rotate(a cx cy), translate, scale."""
    import re
    vb = re.search(r'viewBox="([\d.\-\s]+)"', svg)
    vx, vy, vw, vh = [float(v) for v in vb.group(1).split()] if vb else (0, 0, 100, 100)
    ki = []
    for m in re.finditer(r"<(path|circle|ellipse|rect|polygon)\b([^>]*)/?>", svg):
        tag, attr = m.group(1), m.group(2)

        def a(n, d=0.0):
            mm = re.search(r'\b%s="([^"]+)"' % n, attr)
            return mm.group(1) if mm else d
        if tag == "path":
            utak = _path_pontok(a("d", ""))
        elif tag in ("circle", "ellipse"):
            cx, cy = float(a("cx")), float(a("cy"))
            rx = float(a("r") if tag == "circle" else a("rx"))
            ry = float(a("r") if tag == "circle" else a("ry"))
            utak = [[(cx + rx * math.cos(2 * math.pi * k / 48), cy + ry * math.sin(2 * math.pi * k / 48)) for k in range(48)]]
        elif tag == "rect":
            x, y, w, h = float(a("x")), float(a("y")), float(a("width")), float(a("height"))
            utak = [[(x, y), (x + w, y), (x + w, y + h), (x, y + h)]]
        else:
            nums = [float(v) for v in re.findall(r"-?\d*\.?\d+", a("points", ""))]
            utak = [list(zip(nums[0::2], nums[1::2]))]
        tr = a("transform", "")
        for t in re.finditer(r"(rotate|translate|scale)\(([^)]*)\)", tr or ""):
            v = [float(x) for x in re.findall(r"-?\d*\.?\d+", t.group(2))]
            if t.group(1) == "rotate":
                ang = math.radians(v[0])
                cx, cy = (v[1], v[2]) if len(v) >= 3 else (0, 0)
                utak = [[(cx + (px - cx) * math.cos(ang) - (py - cy) * math.sin(ang),
                          cy + (px - cx) * math.sin(ang) + (py - cy) * math.cos(ang)) for px, py in u] for u in utak]
            elif t.group(1) == "translate":
                tx, ty = v[0], (v[1] if len(v) > 1 else 0)
                utak = [[(px + tx, py + ty) for px, py in u] for u in utak]
            else:
                sx, sy = v[0], (v[1] if len(v) > 1 else v[0])
                utak = [[(px * sx, py * sy) for px, py in u] for u in utak]
        for u in utak:
            ki.append([((px - vx) / vw, (py - vy) / vh) for px, py in u])
    return ki


def motivum(s, nev, x, y, w, h=None, fill="accent", alpha=None, forgas=0.0, line=None, lw=1.0):
    """A márka motívuma (tokenek: motivum.formak_svg[nev]) natív alakzatként. Több elemű motívumnál (pl. virág) az
    elemek csoportba kerülnek. Visszaad: alakzatok listája."""
    svg = (T.motivum.get("formak_svg") or {}).get(nev) if T else None
    if not svg:
        return []
    h = h or w
    ki = []
    cx, cy = x + w / 2.0, y + h / 2.0
    ang = math.radians(forgas)
    for u in svg_utak(svg):
        pts = []
        for px, py in u:
            X, Y = x + px * w, y + py * h
            if forgas:
                X, Y = (cx + (X - cx) * math.cos(ang) - (Y - cy) * math.sin(ang),
                        cy + (X - cx) * math.sin(ang) + (Y - cy) * math.cos(ang))
            pts.append((X, Y))
        ki.append(sokszog(s, pts, fill=fill, line=line, lw=lw, alpha=alpha))
    if len(ki) > 1:
        try:
            grp = s.shapes.add_group_shape(ki)
            return [grp]
        except Exception:
            pass
    return ki


def motivum_elemek(kulcs, mot=None):
    """A motivum.textura/dekor/hatar mező elemei listaként: a tokenekben objektum (egy választás) vagy lista
    (keverés, több kipipált opció) is lehet."""
    mot = mot if mot is not None else ((T.motivum if T else None) or {})
    v = mot.get(kulcs)
    if not v:
        return []
    if isinstance(v, dict):
        return [v]
    if isinstance(v, (list, tuple)):
        return [x for x in v if isinstance(x, dict)]
    return []


def motivum_nevek(kulcs, mot=None):
    return ", ".join(x.get("nev", "") for x in motivum_elemek(kulcs, mot) if x.get("nev"))


# ------------------------------------------------------------------ kézi hatású vonalak, textúra

def ceruza_karika(s, x, y, w, h, color="accent", lw=2.2, seed=3, korok=1.35):
    """Ceruzával húzott, kicsit szabálytalan karika egy szó körül (a webes „ceruzás bekarikázás” párja)."""
    rnd = random.Random(seed)
    cx, cy = x + w / 2.0, y + h / 2.0
    n = int(90 * korok)
    a0 = rnd.uniform(-0.6, -0.2)
    pts = []
    for i in range(n + 1):
        t = a0 + 2 * math.pi * korok * i / n
        rr = 1 + 0.03 * math.sin(3 * t + seed) + 0.015 * math.sin(7 * t) + (0.035 * i / n)
        pts.append((cx + w / 2.0 * rr * math.cos(t), cy + h / 2.0 * rr * math.sin(t) * (1 - 0.06 * i / n)))
    sp = sokszog(s, pts, fill=None, line=color, lw=lw, zart=False)
    vonal_kerek(sp)
    return sp


def filctoll(s, x, y, w, h, color="accent2", alpha=70, seed=5):
    """Filctoll-csík a szó alsó részén, kicsit szabálytalan széllel."""
    rnd = random.Random(seed)
    n = 18
    felso = [(x + w * i / n, y + rnd.uniform(-0.012, 0.012) * 2) for i in range(n + 1)]
    also = [(x + w * i / n + 0.02, y + h + rnd.uniform(-0.02, 0.02)) for i in range(n, -1, -1)]
    return sokszog(s, felso + also, fill=color, alpha=alpha)


def szintvonalak(s, x, y, w, h, color="line", lw=0.9, n=9, seed=7, kozep=None, alpha=None):
    """Halvány, egymásba simuló szintvonalak (topográfiai textúra) natív görbékből."""
    rnd = random.Random(seed)
    cx, cy = kozep or (x + w * rnd.uniform(0.55, 0.8), y + h * rnd.uniform(0.25, 0.6))
    fazis = [rnd.uniform(0, 6.28) for _ in range(4)]
    ki = []
    for k in range(1, n + 1):
        r0 = 0.32 * k
        pts = []
        for i in range(120):
            t = 2 * math.pi * i / 120
            rr = r0 * (1 + 0.16 * math.sin(2 * t + fazis[0]) + 0.08 * math.sin(3 * t + fazis[1] + k * 0.15)
                       + 0.05 * math.sin(5 * t + fazis[2]))
            px = cx + rr * 1.35 * math.cos(t)
            py = cy + rr * 0.9 * math.sin(t)
            pts.append((min(max(px, x), x + w), min(max(py, y), y + h)))
        sp = sokszog(s, pts, fill=None, line=color, lw=lw, zart=True, line_alpha=alpha)
        ki.append(sp)
    return ki


# ------------------------------------------------------------------ szöveg

def _rpr_sorrend(rPr, elem):
    """Az a:rPr gyerekeinek sémasorrendje: ln, fill, effect, highlight, uLn, uFill, latin, ea, cs, sym, ..."""
    sorrend = ["ln", "noFill", "solidFill", "gradFill", "blipFill", "pattFill", "grpFill", "effectLst", "effectDag",
               "highlight", "uLnTx", "uLn", "uFillTx", "uFill", "latin", "ea", "cs", "sym", "hlinkClick"]
    nev = elem.tag.split("}")[1]
    i = sorrend.index(nev)
    for gy in list(rPr):
        gnev = gy.tag.split("}")[1]
        if gnev in sorrend and sorrend.index(gnev) > i:
            gy.addprevious(elem)
            return
    rPr.append(elem)


def _run(p, txt, ov, size, color, font, bold, italic, tracking):
    r = p.add_run()
    r.text = txt
    f = r.font
    fnev = ov.get("font", font)
    tf, tb, _ = betu(fnev, ov.get("bold", bold))
    f.name = tf
    f.size = Pt(ov.get("size", size))
    f.bold = tb
    f.italic = bool(ov.get("italic", italic))
    f.color.rgb = rgb(ov.get("color", color))
    rPr = f._rPr
    for tag in ("a:ea", "a:cs"):
        e = rPr.makeelement(qn(tag), {"typeface": tf})
        _rpr_sorrend(rPr, e)
    tr = ov.get("tracking", tracking)
    if tr is not None:
        rPr.set("spc", str(int(tr * 100)))
    hl = ov.get("hl")
    if hl is not None:
        h = rPr.makeelement(qn("a:highlight"), {})
        h.append(h.makeelement(qn("a:srgbClr"), {"val": hexs(hl)}))
        _rpr_sorrend(rPr, h)
    if ov.get("u"):
        rPr.set("u", ov.get("u"))
    return r


def text(s, x, y, w, h, runs, size=20, color="ink", bold=None, font="torzs", align=L, anchor=TOP, spacing=1.0,
         space_after=0, tracking=None, italic=False, wrap=True):
    """Szövegdoboz margó nélkül. runs: str vagy [(szöveg, {color,size,bold,font,italic,tracking,hl})].
    A '\\n' új bekezdést kezd ugyanazokkal a beállításokkal."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    for m in ("left", "right", "top", "bottom"):
        setattr(tf, "margin_" + m, 0)
    if isinstance(runs, str):
        runs = [(runs, {})]
    p = tf.paragraphs[0]

    def uj_bek(p):
        p.alignment = align
        p.line_spacing = spacing
        if space_after:
            p.space_after = Pt(space_after)
        return p
    uj_bek(p)
    for txt, ov in runs:
        darabok = txt.split("\n")
        for j, d in enumerate(darabok):
            if j > 0:
                p = uj_bek(tf.add_paragraph())
            for k, dd in enumerate(d.split("\v")):
                if k > 0:
                    br = p._p.add_br()
                    rpr = br.get_or_add_rPr()
                    rpr.set("sz", str(int(ov.get("size", size) * 100)))
                if dd:
                    _run(p, dd, ov, size, color, font, bold, italic, tracking)
    return tb


def para(tb, runs, size=20, color="ink", bold=None, font="torzs", align=L, spacing=1.0, space_before=0):
    tf = tb.text_frame
    p = tf.add_paragraph()
    p.alignment = align
    p.line_spacing = spacing
    if space_before:
        p.space_before = Pt(space_before)
    if isinstance(runs, str):
        runs = [(runs, {})]
    for txt, ov in runs:
        _run(p, txt, ov, size, color, font, bold, False, None)
    return p


# ------------------------------------------------------------------ képek

def _arc_doboz(ut, W, H, tar):
    """Arcvédő kivágás (opcionális): macOS-en a Vision keretrendszer (swift), máshol az OpenCV, ha telepítve van.
    Ha egyik sincs, None (marad a fókuszpont szerinti vágás)."""
    arcok = _arcok(ut)
    if not arcok:
        return None
    if W / float(H) > tar:
        nw = int(H * tar)
        xs = [v for a in arcok for v in (a[0], a[2])]
        kozep = (min(xs) + max(xs)) / 2.0 * W
        x0 = int(min(max(kozep - nw / 2.0, 0), W - nw))
        return (x0, 0, x0 + nw, H)
    nh = int(W / tar)
    teto = max(0.0, min(a[1] - 0.6 * (a[3] - a[1]) for a in arcok)) * H
    y0 = int(min(max(teto - 0.06 * nh, 0), H - nh))
    return (0, y0, W, y0 + nh)


def _arcok(ut):
    cache = cache_mappa() / "arcok.json"
    try:
        c = json.loads(cache.read_text())
    except Exception:
        c = {}
    kulcs = "%s|%d" % (ut, int(os.path.getmtime(ut)))
    if kulcs in c:
        return c[kulcs]
    arcok = []
    swift = HERE / "arcok.swift"
    try:
        if sys.platform == "darwin" and swift.exists() and _van("swift"):
            r = subprocess.run(["swift", str(swift), ut], capture_output=True, text=True, timeout=120)
            arcok = json.loads(r.stdout).get(ut, [])
        else:
            import cv2  # noqa: F401  (opcionális)
            kep = cv2.imread(ut)
            sz = cv2.cvtColor(kep, cv2.COLOR_BGR2GRAY)
            cc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            H, W = sz.shape[:2]
            arcok = [[x / W, y / H, (x + w) / W, (y + h) / H] for (x, y, w, h) in cc.detectMultiScale(sz, 1.1, 6)]
    except Exception:
        arcok = []
    c[kulcs] = arcok
    try:
        cache.write_text(json.dumps(c))
    except Exception:
        pass
    return arcok


_VAN = {}


def _van(prg):
    if prg not in _VAN:
        import shutil
        _VAN[prg] = bool(shutil.which(prg))
    return _VAN[prg]


ARCVEDELEM = True


def crop(path, w_in, h_in, fx=0.5, fy=0.5, duotone=None):
    """A fotót a cél arányára vágja (cover), a gyorsítótárba, és visszaadja az útját. fx/fy: fókuszpont (0..1),
    a webes 'pozicio' mezőből. Ha elérhető arcfelismerés, a fejet nem vágja le. duotone=(sötét, világos)."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    W, H = im.size
    tar = w_in / float(h_in)
    box = _arc_doboz(str(path), W, H, tar) if ARCVEDELEM else None
    if box:
        im = im.crop(box)
    elif W / float(H) > tar:
        nw = int(H * tar)
        x0 = int((W - nw) * fx)
        im = im.crop((x0, 0, x0 + nw, H))
    else:
        nh = int(W / tar)
        y0 = int((H - nh) * fy)
        im = im.crop((0, y0, W, y0 + nh))
    if max(im.size) > 2200:
        im.thumbnail((2200, 2200))
    if duotone:
        g = ImageOps.grayscale(im)
        g = ImageOps.autocontrast(g, cutoff=1)
        im = ImageOps.colorize(g, black=rgbt(duotone[0]), white=rgbt(duotone[1]))
    h = hashlib.md5(("%s|%s|%.3f|%.3f|%.3f|%.3f|%s|%s" % (path, os.path.getmtime(path), w_in, h_in, fx, fy, box, duotone))
                    .encode("utf-8")).hexdigest()[:16]
    out = cache_mappa("vagas") / ("%s_%s.jpg" % (Path(path).stem[:40], h))
    if not out.exists():
        im.save(out, "JPEG", quality=88)
    return str(out)


def _set_geom(pic, prst, adj=None):
    spPr = pic._element.spPr
    for tag in ("a:prstGeom", "a:custGeom"):
        e = spPr.find(qn(tag))
        if e is not None:
            spPr.remove(e)
    g = spPr.makeelement(qn("a:prstGeom"), {"prst": prst})
    av = g.makeelement(qn("a:avLst"), {})
    if adj is not None:
        av.append(g.makeelement(qn("a:gd"), {"name": "adj", "fmla": "val %d" % adj}))
    g.append(av)
    xfrm = spPr.find(qn("a:xfrm"))
    if xfrm is not None:
        xfrm.addnext(g)
    else:
        spPr.append(g)


_FOTO_FIGY = set()


def foto_info(f):
    """Fotó azonosító / útvonal / dict -> {ut, fx, fy, rajz, kepernyo, w, h}; None, ha nincs fotó."""
    if f is None:
        return None
    if isinstance(f, dict) and "ut" in f:
        x = dict(f)
    else:
        x = None
        if T is not None:
            for y in T.fotok:
                if y["id"] == f:
                    x = dict(y)
                    break
            if x is None:
                p = Path(f) if os.path.isabs(str(f)) else Path(T.alap) / str(f)
                if p.exists():
                    x = next((dict(y) for y in T.fotok if Path(y["ut"]) == p), None) or {"ut": str(p)}
        if x is None:
            if f not in _FOTO_FIGY:
                _FOTO_FIGY.add(f)
                print("  ! nincs ilyen fotó: %s (a helyére a márka jelével kitöltött lap kerül)" % f)
            return None
    if "w" not in x:
        try:
            x["w"], x["h"] = ImageOps.exif_transpose(Image.open(x["ut"])).size
        except Exception:
            x["w"], x["h"] = 1600, 1000
    x.setdefault("fx", 0.5)
    x.setdefault("fy", 0.5)
    x.setdefault("rajz", False)
    x.setdefault("kepernyo", kepernyo_e(x["ut"], x["w"], x["h"]))
    return x


def kepernyo_e(ut, w, h):
    """Képernyőkép-e (alkalmazás, weboldal): ezt nem vágjuk teljes képernyős háttérré, hanem egészben mutatjuk."""
    nev = Path(ut).name.lower()
    if any(k in nev for k in ("screen", "kepernyo", "képernyő", "screenshot")):
        return True
    return nev.endswith(".png") and max(w, h) / float(max(1, min(w, h))) >= 1.6


def foto(f):
    """Foto azonosító vagy útvonal -> (abszolút út, fx, fy); None, ha nincs ilyen fotó."""
    x = foto_info(f)
    return (x["ut"], x["fx"], x["fy"]) if x else None


def helyettes(s, x, y, w, h, kor=False, fill=None):
    """Ha nincs fotó: márkaszínű lap a márka jelével (nem omlik össze a dia, és nem hat üresnek)."""
    sp = (oval(s, x, y, w, h, fill=fill or "tint") if kor else
          rect(s, x, y, w, h, fill=fill or ("tint" if "tint" in T.szin else "sand")))
    jel = (T.motivum or {}).get("jel") or next(iter((T.motivum or {}).get("formak_svg") or {}), None)
    if jel:
        d = min(w, h) * 0.38
        motivum(s, jel, x + (w - d) / 2.0, y + (h - d) / 2.0, d, d, fill=kever("primary", fill or "tint", 0.45))
    return sp


def pic_cover(s, f, x, y, w, h, fx=None, fy=None, duotone=None):
    adat = foto(f) if f is not None else None
    if adat is None:
        return helyettes(s, x, y, w, h)
    ut, ffx, ffy = adat
    c = crop(ut, w, h, ffx if fx is None else fx, ffy if fy is None else fy, duotone=duotone)
    return s.shapes.add_picture(c, Inches(x), Inches(y), Inches(w), Inches(h))


def pic_round(s, f, x, y, w, h, r=None, fx=None, fy=None, duotone=None):
    """Lekerekített fotó a téma sarkaival (r hüvelyk; alapból T.r_kartya)."""
    p = pic_cover(s, f, x, y, w, h, fx, fy, duotone)
    r = T.r_kartya if r is None else r
    if r > 0.004 and p is not None and p.shape_type == 13:
        _set_geom(p, "roundRect", int(min(0.5, r / min(w, h)) * 100000))
    return p


def pic_circle(s, f, x, y, d, fx=None, fy=None):
    if f is None or foto_info(f) is None:
        return helyettes(s, x, y, d, d, kor=True)
    p = pic_cover(s, f, x, y, d, d, fx, fy)
    _set_geom(p, "ellipse")
    return p


def keszulek(s, f, x, y, w, h, keret="deep", arnyek_=True):
    """Képernyőkép készülék-keretben (telefon vagy monitor), arányosan, a dobozban középre. Visszaad: a kép alakzata."""
    x_ = foto_info(f)
    if x_ is None:
        return helyettes(s, x, y, w, h)
    ar = x_["w"] / float(x_["h"])
    m = 0.07 * min(w, h)
    if w / h > ar:
        kh = h
        kw = (h - 2 * m) * ar + 2 * m
    else:
        kw = w
        kh = (w - 2 * m) / ar + 2 * m
    kx, ky = x + (w - kw) / 2.0, y + (h - kh) / 2.0
    r = min(0.5, (0.22 * min(kw, kh)) / min(kw, kh)) if ar < 1 else 0.06
    test = rect(s, kx, ky, kw, kh, fill=keret, shape=MSO_SHAPE.ROUNDED_RECTANGLE, rad=0.12 if ar < 1 else 0.04)
    if arnyek_:
        arnyek(test, "lagy")
    p = s.shapes.add_picture(x_["ut"], Inches(kx + m), Inches(ky + m), Inches(kw - 2 * m), Inches(kh - 2 * m))
    _set_geom(p, "roundRect", int((0.09 if ar < 1 else 0.02) * 100000))
    return p


def pic(s, path, x, y, w=None, h=None):
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    return s.shapes.add_picture(str(path), Inches(x), Inches(y), **kw)


def pic_contain(s, path, x, y, w, h):
    """A kép arányosan, a dobozban középre."""
    im = Image.open(path)
    ar = im.size[0] / float(im.size[1])
    if w / h > ar:
        ww, hh = h * ar, h
    else:
        ww, hh = w, w / ar
    return s.shapes.add_picture(str(path), Inches(x + (w - ww) / 2.0), Inches(y + (h - hh) / 2.0), Inches(ww), Inches(hh))


# ------------------------------------------------------------------ ikon, logó

_IKON_FIGY = set()


def ikon_ut(nev):
    """Az ikon útja, vagy None, ha nincs ilyen (pl. az OpenAI-generálás elmaradt): ilyenkor a tartó a márka jelét
    rajzolja a helyére."""
    if T is None:
        raise RuntimeError("Nincs aktív téma.")
    if nev in T.ikonok:
        return T.ikonok[nev]
    p = Path(nev) if os.path.isabs(str(nev)) else Path(T.alap) / str(nev)
    if p.exists() and p.is_file():
        return str(p)
    if nev not in _IKON_FIGY:
        _IKON_FIGY.add(nev)
        print("  ! nincs ilyen ikon: %s (van: %s); a helyére a márka jele kerül" % (nev, ", ".join(sorted(T.ikonok)) or "-"))
    return None


LOGO_JOBB, LOGO_ALSO = 12.93, 7.2
LOGO_MAX_W, LOGO_MAX_H = 1.55, 0.42


def logo(s, sotet_=False):
    """A márka logója MINDIG jobbra lent (rögzített szabály). sotet_: a jobb alsó sarok sötét felület."""
    ut = T.logo.get("feher" if sotet_ else "szines") or T.logo.get("szines")
    if not ut or not os.path.exists(ut):
        return None
    im = Image.open(ut)
    ar = im.size[0] / float(im.size[1])
    w = min(LOGO_MAX_W, LOGO_MAX_H * ar)
    h = w / ar
    return s.shapes.add_picture(ut, Inches(LOGO_JOBB - w), Inches(LOGO_ALSO - h), Inches(w), Inches(h))
