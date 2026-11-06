# -*- coding: utf-8 -*-
"""A prezi-motor diatípusai. Minden függvény: (prs, d, v=None) -> dia; d a dia tartalma (dict), v a változat
(ha None: a téma választása). A tartalmi mezők leírása: references/prezi/minta-diak.md.

Rögzített szabályok: 16:9; a törzsszöveg legalább 20 pt (a kis címkék 16-18 pt); a logó MINDIG jobbra lent
(alap.logo), ezért a jobb alsó sarok (x > 11.2", y > 6.7") szabadon marad. A címsorok a dobozukhoz igazodnak
(fit_blokk), a ==kulcsszó== a téma címsor-kiemelésével jelenik meg.

Diatípusok: cimdia, fejezet, felsorolas, ket_hasab, folyamat, kartyak, szamok, idezet, eset, kerdes, kepernyokep,
zaro, bemutatkozo.
"""
import alap as a
import elemek as e
from alap import L, C, R

MX = 0.85
ALSO_HATAR = 6.62          # eddig érhet a tartalom a logó sávja fölött (jobbra)


def _fotok(d, n, alap_lista=None):
    """n fotó a diához: a megadottak, kiegészítve a téma fotóival; ha kevés van, ismétel; ha egy sincs, None-ok
    (a helyükre a márka jelével kitöltött lap kerül)."""
    lst = list(d.get("fotok") or ([d["foto"]] if d.get("foto") else []))
    tart = [f["id"] for f in a.T.foto_lista()] if a.T else []
    for f in (alap_lista or []) + tart:
        if len(lst) >= n:
            break
        if f not in lst:
            lst.append(f)
    if not lst:
        return [None] * n
    while len(lst) < n:
        lst.append(lst[len(lst) % max(1, len(lst))])
    return lst[:n]


def _fekvo(d, n=1):
    """Teljes képernyős háttérhez fekvő FOTÓ kell (képernyőkép és rajz nem): a megadottak közül, aztán a téma
    fotóiból. Ha nincs ilyen: [None] (a dia fotó nélkül, a márka textúrájával készül)."""
    jeloltek = list(d.get("fotok") or ([d["foto"]] if d.get("foto") else []))
    jeloltek += [f["id"] for f in a.T.foto_lista() if f["id"] not in jeloltek]
    ki = []
    for f in jeloltek:
        try:
            x = a.foto_info(f)
        except Exception:
            continue
        if x and not x.get("kepernyo") and not x.get("rajz") and x["w"] >= x["h"] * 1.2:
            ki.append(f)
        if len(ki) >= n:
            break
    return ki or [None]


def _hatter_foto(s, d, fs, opacity=58, also_fatyol=True, seed=5):
    """Teljes képernyős fotó fátyollal; ha nincs alkalmas fotó, a felület színe a márka textúrájával."""
    f = _fekvo(d)[0]
    if f is None:
        e.textura(s, fs, 0, 0, a.SZ, a.MA, seed=seed, kozep=(10.5, 2.4), n=11)
        return False
    a.pic_cover(s, f, 0, 0, a.SZ, a.MA)
    a.overlay(s, 0, 0, a.SZ, a.MA, color=fs.bg, opacity=opacity)
    if also_fatyol:
        a.veil_grad(s, 0, 0, a.SZ, a.MA, color=fs.bg, a_top=0, a_bot=55)
    return True


def _panel(s, f, x, y, w, h, bg="tint", fatyol=None):
    """Fotó egy teljes magasságú panelben. Képernyőképet nem vág: a panel a márka árnyalata, rajta készülék-keretben
    az egész kép. fatyol=(szín, átlátszatlanság) csak valódi fotóra. Visszaad: True, ha valódi fotó került oda."""
    info = a.foto_info(f) if f is not None else None
    if info is None:
        a.helyettes(s, x, y, w, h)
        return False
    if info.get("kepernyo") or info.get("rajz"):
        a.rect(s, x, y, w, h, fill=bg if bg in a.T.szin else "sand")
        m = 0.55
        if info.get("rajz"):
            a.pic_contain(s, info["ut"], x + m, y + m, w - 2 * m, h - 2 * m)
        else:
            a.keszulek(s, f, x + m, y + m, w - 2 * m, h - 2 * m)
        return False
    a.pic_cover(s, f, x, y, w, h)
    if fatyol:
        a.overlay(s, x, y, w, h, color=fatyol[0], opacity=fatyol[1])
    return True


def _vege(s, f, d, sotet=None):
    e.karakter_csik(s)
    a.logo(s, f.sotet if sotet is None else sotet)
    a.jegyzet(s, d.get("jegyzet"))
    return s


def _szoveg(s, x, y, w, t, f, size=21, color=None, spacing=1.18, maxh=None, align=L):
    if not t:
        return 0.0
    if maxh:
        size = a.fit_blokk(t, w, maxh, size, "torzs", False, spacing, min_pt=20)
    h = a.blokk_magassag(t, w, size, "torzs", False, spacing)
    a.text(s, x, y, w, h + 0.15, [(t, {})], size=size, color=color or f.szoveg, font="torzs", spacing=spacing,
           align=align)
    return h


def _pont(s, x, y, w, i, cim, leiras, f, pt=21, v=None, cim_pt=None):
    """Egy felsorolás-elem: jel + félkövér cím + (új sorban) leírás. Visszaad: az elem magassága."""
    dx = e.jel(s, i, x, y, cim_pt or pt, f, v)
    tw = w - dx
    cp = cim_pt or pt
    ch = a.blokk_magassag(cim, tw, cp, "torzs", True, 1.08)
    runs = [(cim, {"bold": True, "color": f.cim, "size": cp})]
    tb = a.text(s, x + dx, y, tw, ch + 0.1, runs, size=cp, color=f.cim, font="torzs", spacing=1.08)
    h = ch
    if leiras:
        lh = a.blokk_magassag(leiras, tw, pt, "torzs", False, 1.12)
        a.text(s, x + dx, y + ch + 0.06, tw, lh + 0.1, [(leiras, {})], size=pt, color=f.szoveg, font="torzs",
               spacing=1.12)
        h += 0.06 + lh
    return h


def _lista(s, x, felso, also, w, pontok, f, cim_pt=22, pt=21, max_koz=0.6, min_koz=0.22):
    """Pontok (cím + leírás) a felso..also sávban: a valódi magasságukkal számol, a méretből (legfeljebb 20 pt-ig)
    és a közökből enged, hogy semmi ne csússzon egymásra. Visszaad: az utolsó elem alja."""
    pontok = [(p if isinstance(p, (list, tuple)) else (p, None)) for p in pontok]
    n = max(1, len(pontok))
    hely = also - felso

    def magassag(cp, lp):
        tw = w - 0.75
        ossz = 0.0
        for c, l in pontok:
            ossz += a.blokk_magassag(c, tw, cp, "torzs", True, 1.08)
            if l:
                ossz += 0.06 + a.blokk_magassag(l, tw, lp, "torzs", False, 1.12)
        return ossz
    cp, lp = cim_pt, pt
    while magassag(cp, lp) + min_koz * (n - 1) > hely and (cp > 20 or lp > 20):
        cp, lp = max(20, cp - 1), max(20, lp - 1)
    ossz = magassag(cp, lp)
    koz = min(max_koz, max(min_koz, (hely - ossz) / max(1, n - 1))) if n > 1 else 0
    y = felso
    for i, (c, l) in enumerate(pontok):
        y += _pont(s, x, y, w, i, c, l, f, pt=lp, cim_pt=cp) + koz
    return y - koz


def felulet_tipus(tipus, d):
    h = d.get("hatter")
    if h == "szines":
        return e.felulet_ritmus()
    if h == "alap":
        return e.felulet_alap()
    if tipus in ("fejezet", "kerdes"):
        return e.felulet_ritmus()
    return e.felulet_alap()


def _sotet_panel():
    """Mély színű panel/felület a címdiához és a záróhoz (a ritmus színe, ha az sötét; különben a 'deep')."""
    f = e.felulet_ritmus()
    return f if f.sotet else e.fel("deep")


# ================================================================== CÍMDIA (cimdia A-E)

def cimdia(prs, d, v=None):
    v = v or a.T.v("cimdia")
    fa = e.felulet_alap()
    ph = _fotok(d, 3)
    if v == "B":
        fp = _sotet_panel()
        s = e.dia(prs, fp)
        valodi = _panel(s, ph[0], 6.55, 0, a.SZ - 6.55, a.MA)
        if valodi:
            a.veil_grad(s, 6.55, 0, a.SZ - 6.55, a.MA, color=fp.bg, a_top=0, a_bot=62)
        e.textura(s, fp, 0, 0, 6.55, a.MA, seed=11, kozep=(1.0, 6.6), n=7)
        a.rect(s, MX + 0.02, 1.85, 1.0, 0.09, fill=fp.kiemel)
        e.kicker(s, MX, 1.32, 5.4, d.get("kicker"), fp)
        pt, th, y0 = e.cimsor(s, MX - 0.03, 2.15, 5.45, 2.9, d["cim"], 56, fp)
        _szoveg(s, MX, y0 + th + 0.32, 5.2, d.get("alcim"), fp, size=21, maxh=6.9 - (y0 + th + 0.32))
        return _vege(s, fp, d, sotet=True if valodi else a.sotet("tint" if "tint" in a.T.szin else "sand"))
    if v == "C":
        fs = _sotet_panel()
        s = e.dia(prs, fs)
        _hatter_foto(s, d, fs, opacity=60)
        e.kicker(s, 1.5, 1.45, a.SZ - 3.0, d.get("kicker"), fs, align=C, color=fs.cim)
        pt, th, y0 = e.cimsor(s, 1.3, 1.95, a.SZ - 2.6, 2.9, d["cim"], 62, fs, align=C, kozep=True)
        _szoveg(s, 2.4, y0 + th + 0.35, a.SZ - 4.8, d.get("alcim"), fs, size=22, align=C,
                maxh=6.6 - (y0 + th + 0.35))
        return _vege(s, fs, d, sotet=True)
    s = e.dia(prs, fa)
    if v == "D":
        e.textura(s, fa, 6.2, 0, a.SZ - 6.2, a.MA, seed=5, kozep=(10.0, 3.6))
        e.kicker(s, MX, 1.25, 6.0, d.get("kicker"), fa)
        pt, th, y0 = e.cimsor(s, MX - 0.03, 1.75, 6.2, 3.3, d["cim"], 60, fa)
        _szoveg(s, MX, y0 + th + 0.35, 5.6, d.get("alcim"), fa, size=21, maxh=6.75 - (y0 + th + 0.35))
        e.fotokeret(s, ph[0], 7.45, 0.6, 4.85, 3.35, fa, valtozat="C", forgas=3.0)
        e.fotokeret(s, ph[1], 6.95, 3.65, 4.3, 2.95, fa, valtozat="C", forgas=-3.5)
        return _vege(s, fa, d)
    if v == "E":
        e.textura(s, fa, 0, 0, a.SZ, a.MA, seed=3, kozep=(10.6, 2.2), n=11)
        formak = a.T.motivum.get("formak_svg") or {}
        jel = a.T.motivum.get("jel") or next(iter(formak), None)
        if jel:
            a.motivum(s, jel, 9.35, 0.75, 2.9, 2.9, fill=fa.kiemel, alpha=88)
        masik = [k for k in formak if k != jel]
        if masik:
            a.motivum(s, masik[0], 8.75, 3.2, 0.9, 1.1, fill=fa.jel, forgas=-30)
            a.motivum(s, masik[0], 12.2, 3.55, 0.6, 0.75, fill=fa.jel, forgas=25)
        if len(ph) > 0:
            e.fotokeret(s, ph[0], 9.7, 3.75, 2.35, 2.35, fa, valtozat="B")
        e.kicker(s, MX, 1.3, 7.6, d.get("kicker"), fa)
        pt, th, y0 = e.cimsor(s, MX - 0.03, 1.8, 7.9, 3.4, d["cim"], 68, fa)
        _szoveg(s, MX, y0 + th + 0.35, 7.0, d.get("alcim"), fa, size=22, maxh=6.75 - (y0 + th + 0.35))
        return _vege(s, fa, d)
    # A: rétegzett fotók
    a.rect(s, MX + 0.02, 1.95, 1.0, 0.09, fill=fa.kiemel)
    e.kicker(s, MX, 1.42, 6.4, d.get("kicker"), fa)
    pt, th, y0 = e.cimsor(s, MX - 0.03, 2.25, 6.6, 2.8, d["cim"], 58, fa)
    _szoveg(s, MX, y0 + th + 0.32, 6.0, d.get("alcim"), fa, size=21, maxh=6.75 - (y0 + th + 0.32))
    fk = a.T.v("fotokeret")
    fk = "A" if fk in ("B", "C") else fk
    e.fotokeret(s, ph[0], 8.45, 3.45, 3.95, 2.75, fa, valtozat=fk)
    e.fotokeret(s, ph[1], 7.65, 1.75, 3.5, 2.35, fa, valtozat=fk)
    e.fotokeret(s, ph[2], 9.45, 0.7, 3.1, 2.45, fa, valtozat=fk)
    return _vege(s, fa, d)


# ================================================================== FEJEZETDIA (fejezet A-E)

def fejezet(prs, d, v=None):
    v = v or a.T.v("fejezet")
    fr = felulet_tipus("fejezet", d)
    ph = _fotok(d, 3)
    szam = d.get("szam") or ""
    if v == "A":
        fs = fr if fr.sotet else e.fel("deep")
        s = e.dia(prs, fs)
        if _hatter_foto(s, d, fs, opacity=42, also_fatyol=False, seed=19):
            a.veil_grad(s, 0, 0, a.SZ, a.MA, color=fs.bg, a_top=0, a_bot=88)
        e.kicker(s, MX, 2.55, 10, d.get("kicker"), fs, color=fs.cim)
        a.text(s, MX - 0.05, 2.85, 10, 2.2, [(szam, {})], size=a.fit(szam, 6.0, 128), color=fs.szam, font="cim",
               spacing=0.9)
        e.cimsor(s, MX, 5.0, 10.2, 1.6, d["cim"], 44, fs, also=True)
        return _vege(s, fs, d, sotet=True)
    if v == "B":
        fa = e.felulet_alap()
        s = e.dia(prs, fa)
        _panel(s, ph[0], 0, 0, 7.35, a.MA)
        a.rect(s, 7.35, 0, a.SZ - 7.35, a.MA, fill=fr.bg)
        e.textura(s, fr, 7.35, 0, a.SZ - 7.35, a.MA, seed=9, kozep=(12.0, 6.4), n=7)
        e.kicker(s, 7.95, 1.25, 4.9, d.get("kicker"), fr)
        a.text(s, 7.9, 1.55, 5.2, 2.0, [(szam, {})], size=a.fit(szam, 4.8, 122), color=fr.szam, font="cim",
               spacing=0.9)
        pt, th, y0 = e.cimsor(s, 7.95, 3.85, 4.85, 2.05, d["cim"], 40, fr)
        a.rect(s, 7.97, y0 + th + 0.3, 1.1, 0.08, fill=fr.kiemel)
        if d.get("alcim"):
            _szoveg(s, 7.97, y0 + th + 0.55, 4.6, d["alcim"], fr, size=20, maxh=6.65 - (y0 + th + 0.55))
        return _vege(s, fr, d)
    s = e.dia(prs, fr)
    if v == "C":
        a.text(s, MX - 0.05, 0.95, 3.4, 1.8, [(szam, {})], size=a.fit(szam, 3.0, 108), color=fr.szam, font="cim")
        e.kicker(s, MX + 3.3, 1.2, 7.6, d.get("kicker"), fr)
        a.rect(s, MX + 3.32, 1.68, 0.9, 0.08, fill=fr.kiemel)
        e.cimsor(s, MX + 3.3, 1.95, 8.2, 2.0, d["cim"], 42, fr)
        y, h, gap = 4.25, 2.3, 0.3
        w = (a.SZ - 2 * MX - 2 * gap) / 3.0
        fk = a.T.v("fotokeret")
        for i, p in enumerate(ph[:3]):
            e.fotokeret(s, p, MX + i * (w + gap), y, w, h, fr, valtozat=("A" if fk == "B" else fk), seed=i,
                        forgas=(2.0 if i % 2 else -2.0) if fk == "C" else None)
        return _vege(s, fr, d)
    if v == "D":
        e.kicker(s, MX, 1.2, 6.2, d.get("kicker"), fr)
        a.rect(s, MX + 0.02, 1.68, 0.9, 0.08, fill=fr.kiemel)
        a.text(s, MX - 0.05, 1.85, 6.2, 1.9, [(szam, {})], size=a.fit(szam, 5.9, 118), color=fr.szam, font="cim",
               spacing=0.9)
        pt, th, y0 = e.cimsor(s, MX, 3.85, 6.1, 2.1, d["cim"], 40, fr)
        if d.get("alcim"):
            _szoveg(s, MX, y0 + th + 0.28, 5.9, d["alcim"], fr, size=20, maxh=6.9 - (y0 + th + 0.28))
        e.fotokeret(s, ph[0], 7.5, 0.5, 4.35, 2.9, fr, valtozat="C", forgas=-3.0)
        e.fotokeret(s, ph[1], 8.75, 2.75, 3.95, 2.65, fr, valtozat="C", forgas=3.5)
        e.fotokeret(s, ph[2], 7.3, 4.35, 3.75, 2.45, fr, valtozat="C", forgas=-1.5)
        return _vege(s, fr, d)
    # E: óriás szám, motívummal
    e.textura(s, fr, 0, 0, a.SZ, a.MA, seed=21, kozep=(9.8, 3.6), n=10)
    halvany = a.kever(fr.szam, fr.bg, 0.72)
    a.text(s, 6.2, -0.6, 7.2, 7.0, [(szam, {})], size=a.fit(szam, 6.8, 330, min_pt=200), color=halvany, font="cim",
           align=R, spacing=0.85)
    formak = a.T.motivum.get("formak_svg") or {}
    jel = a.T.motivum.get("jel") or next(iter(formak), None)
    if jel:
        a.motivum(s, jel, MX, 1.05, 0.9, 0.9, fill=fr.kiemel)
    e.kicker(s, MX, 2.25, 7.2, d.get("kicker"), fr)
    pt, th, y0 = e.cimsor(s, MX - 0.03, 2.7, 7.6, 2.5, d["cim"], 52, fr)
    if d.get("alcim"):
        _szoveg(s, MX, y0 + th + 0.3, 6.6, d["alcim"], fr, size=21, maxh=6.7 - (y0 + th + 0.3))
    return _vege(s, fr, d)


# ================================================================== TARTALMI DIÁK

def felsorolas(prs, d, v=None):
    """Felsorolás ikonnal: balra cím és 2-4 pont, jobbra nagy ikon a választott tartóban."""
    fa = felulet_tipus("felsorolas", d)
    s = e.dia(prs, fa)
    e.kicker(s, MX, 0.8, 8, d.get("kicker"), fa)
    pt, th, y0 = e.cimsor(s, MX - 0.03, 1.25, 8.1, 1.75, d["cim"], 46, fa)
    pontok = d.get("pontok") or []
    felso = max(3.0, y0 + th + 0.5)
    _lista(s, MX + 0.02, felso, min(6.95, felso + 1.45 * len(pontok)), 7.7, pontok, fa, cim_pt=23, pt=21)
    if d.get("ikon"):
        e.ikontarto(s, d["ikon"], 9.35, 2.05, 3.1, fa)
    return _vege(s, fa, d)


def ket_hasab(prs, d, v=None):
    """Két hasáb: balra a vezérgondolat nagyban (+ bekezdés), jobbra 3-4 pont a felsorolásjellel."""
    fa = felulet_tipus("ket_hasab", d)
    s = e.dia(prs, fa)
    e.kicker(s, MX, 0.95, 5.6, d.get("kicker"), fa)
    pt, th, y0 = e.cimsor(s, MX - 0.03, 1.45, 5.5, 2.6, d.get("vezer") or d.get("cim", ""), 40, fa)
    if d.get("szoveg"):
        _szoveg(s, MX, y0 + th + 0.35, 5.3, d["szoveg"], fa, size=21, maxh=6.75 - (y0 + th + 0.35))
    a.rect(s, 6.75, 1.45, 0.02, 5.1, fill=fa.vonal)
    _lista(s, 7.25, 1.45, ALSO_HATAR, 5.3, d.get("pontok") or [], fa, cim_pt=22, pt=20, max_koz=0.55)
    return _vege(s, fa, d)


def folyamat(prs, d, v=None):
    """Folyamat 3-4 lépésben: ikon a tartóban, cím, rövid leírás, nyilak a lépések között."""
    fa = felulet_tipus("folyamat", d)
    s = e.dia(prs, fa)
    e.kicker(s, MX, 0.72, 10, d.get("kicker"), fa)
    pt, th, y0 = e.cimsor(s, MX - 0.03, 1.15, 11.6, 1.3, d["cim"], 44, fa)
    lep = d.get("lepesek") or []
    n = max(1, len(lep))
    sw = 2.75 if n >= 4 else 3.3
    gap = (a.SZ - 2 * 0.62 - n * sw) / max(1, n - 1)
    ik_d = 1.55
    top = max(2.75, y0 + th + 0.45)
    for i, (ik, cim, leiras) in enumerate(lep):
        x = 0.62 + i * (sw + gap)
        cx = x + sw / 2.0
        e.ikontarto(s, ik, cx - ik_d / 2.0, top, ik_d, fa, szam=i + 1)
        if i < n - 1:
            kov = 0.62 + (i + 1) * (sw + gap) + sw / 2.0 - ik_d / 2.0
            e.nyil(s, cx + ik_d / 2.0 + 0.28, top + ik_d / 2.0, kov - (cx + ik_d / 2.0) - 0.56, fa)
        ch = a.blokk_magassag(cim, sw + 0.1, 22, "torzs", True, 1.05)
        a.text(s, x - 0.05, top + ik_d + 0.28, sw + 0.1, ch + 0.1, [(cim, {"bold": True})], size=22, color=fa.cim,
               align=C, spacing=1.05)
        if leiras:
            lp = a.fit_blokk(leiras, sw + 0.1, ALSO_HATAR - (top + ik_d + 0.4 + ch), 20, "torzs", False, 1.1, min_pt=20)
            a.text(s, x - 0.05, top + ik_d + 0.4 + ch, sw + 0.1, 2.0, [(leiras, {})], size=lp, color=fa.szoveg,
                   align=C, spacing=1.1)
    return _vege(s, fa, d)


def kartyak(prs, d, v=None):
    """Négy kártya 2 × 2-ben: ikon a tartóban, cím, leírás."""
    fa = felulet_tipus("kartyak", d)
    s = e.dia(prs, fa)
    e.kicker(s, 0, 0.45, a.SZ, d.get("kicker"), fa, align=C)
    pt, th, y0 = e.cimsor(s, 1.0, 0.75 if d.get("kicker") else 0.55, a.SZ - 2.0, 0.95, d["cim"], 42, fa, align=C)
    y = y0 + th + 0.12
    if d.get("alcim"):
        hh = _szoveg(s, 1.4, y, a.SZ - 2.8, d["alcim"], fa, size=20, align=C, maxh=0.75)
        y += hh + 0.05
    top = max(2.05, y + 0.25)
    MG, gx, gy = 0.6, 0.35, 0.3
    cw = (a.SZ - 2 * MG - gx) / 2.0
    ch = (ALSO_HATAR - top - gy) / 2.0
    kartyak_ = d.get("kartyak") or []
    for i, (ik, cim, leiras) in enumerate(kartyak_[:4]):
        x = MG + (i % 2) * (cw + gx)
        yy = top + (i // 2) * (ch + gy)
        a.kartya(s, x, yy, cw, ch, fill="card")
        fk = e.fel("card")
        idd = min(1.05, ch - 0.5)
        e.ikontarto(s, ik, x + 0.32, yy + (ch - idd) / 2.0, idd, fk, szam=i + 1)
        tx = x + 0.32 + idd + 0.3
        tw = cw - (tx - x) - 0.3
        cp = a.fit_blokk(cim, tw, 0.8, 23, "torzs", True, 1.05, min_pt=20)
        chh = a.blokk_magassag(cim, tw, cp, "torzs", True, 1.05)
        lh = a.blokk_magassag(leiras or "", tw, 20, "torzs", False, 1.1)
        ossz = chh + (0.1 + lh if leiras else 0)
        ty = yy + max(0.2, (ch - ossz) / 2.0)
        a.text(s, tx, ty, tw, chh + 0.1, [(cim, {"bold": True})], size=cp, color=fk.cim, spacing=1.05)
        if leiras:
            a.text(s, tx, ty + chh + 0.1, tw, lh + 0.1, [(leiras, {})], size=20, color=fk.szoveg, spacing=1.1)
    return _vege(s, fa, d)


# ================================================================== SZÁMOK (szamok A-E)

def szamok(prs, d, v=None):
    v = v or a.T.v("szamok")
    fa = felulet_tipus("szamok", d)
    s = e.dia(prs, fa)
    sz = d.get("szamok") or []
    if v == "E":
        ph = _fotok(d, 1)
        valodi = _panel(s, ph[0], 7.6, 0, a.SZ - 7.6, a.MA)
        if valodi:
            a.veil_grad(s, 7.6, 0, a.SZ - 7.6, a.MA, color="deep", a_top=0, a_bot=45)
        e.kicker(s, MX, 0.95, 6.3, d.get("kicker"), fa)
        pt, th, y0 = e.cimsor(s, MX - 0.03, 1.35, 6.4, 1.5, d["cim"], 38, fa)
        y = max(3.0, y0 + th + 0.45)
        nsz = min([a.fit(n, 2.6, 56) for n, _, _ in sz] or [56])
        lep = (6.9 - y) / max(1, len(sz))
        for i, (n, cimke, leiras) in enumerate(sz):
            a.text(s, MX, y, 2.7, 0.9, [(n, {})], size=nsz, color=fa.szam if i != 1 else fa.szam2, font="cim")
            a.text(s, MX + 2.75, y + 0.05, 3.9, 0.4, [(cimke, {"bold": True})], size=21, color=fa.cim)
            if leiras:
                lp = a.fit_blokk(leiras, 3.9, lep - 0.5, 20, "torzs", False, 1.08, min_pt=20)
                a.text(s, MX + 2.75, y + 0.48, 3.9, lep - 0.45, [(leiras, {})], size=lp, color=fa.szoveg, spacing=1.08)
            y += lep
        if d.get("felirat") and valodi:
            e.kezi(s, 8.0, 6.05, 3.4, 0.6, d["felirat"], e.fel("deep"), size=22, color="card")
        return _vege(s, fa, d, sotet=True if valodi else a.sotet("tint" if "tint" in a.T.szin else "sand"))
    e.kicker(s, MX, 0.95, 11, d.get("kicker"), fa)
    pt, th, y0 = e.cimsor(s, MX - 0.03, 1.38, 11.6, 1.3, d["cim"], 42, fa)
    top = max(2.95, y0 + th + 0.45)
    if v == "B":
        n, cimke, leiras = sz[0]
        hp = a.fit(n, 6.4, 120)
        a.text(s, MX - 0.05, top - 0.25, 6.6, 1.9, [(n, {})], size=hp, color=fa.szam, font="cim", spacing=0.9)
        yy = top - 0.25 + a.sormagassag(hp, 0.9) + 0.1
        a.text(s, MX, yy, 6.2, 0.5, [(cimke, {"bold": True})], size=24, color=fa.cim)
        if leiras:
            _szoveg(s, MX, yy + 0.55, 6.0, leiras, fa, size=21, maxh=6.75 - (yy + 0.55))
        a.rect(s, 7.75, top - 0.1, 0.02, ALSO_HATAR - top + 0.1, fill=fa.vonal)
        ms = min([a.fit(m, 4.3, 50) for m, _, _ in sz[1:3]] or [50])
        lep = (ALSO_HATAR - top + 0.1) / 2.0
        y = top - 0.1
        for m, c2, l2 in sz[1:3]:
            a.text(s, 8.2, y, 4.5, 0.85, [(m, {})], size=ms, color=fa.szam2, font="cim")
            yy2 = y + a.sormagassag(ms) + 0.02
            a.text(s, 8.2, yy2, 4.0, 0.45, [(c2, {"bold": True})], size=21, color=fa.cim)
            if l2:
                lp = a.fit_blokk(l2, 4.0, lep - (yy2 - y) - 0.5, 20, "torzs", False, 1.08, min_pt=20)
                a.text(s, 8.2, yy2 + 0.4, 4.0, 0.8, [(l2, {})], size=lp, color=fa.szoveg, spacing=1.08)
            y += lep
        return _vege(s, fa, d)
    if v == "C":
        y = top
        nsz = min([a.fit(n, 3.0, 58) for n, _, _ in sz] or [58])
        lep = min(1.32, (6.75 - top) / max(1, len(sz)))
        for i, (n, cimke, leiras) in enumerate(sz):
            a.text(s, MX, y - 0.06, 3.1, 0.95, [(n, {})], size=nsz, color=fa.szam if i != 1 else fa.szam2, font="cim")
            a.text(s, MX + 3.35, y, 7.9, 0.45, [(cimke, {"bold": True})], size=22, color=fa.cim)
            if leiras:
                a.text(s, MX + 3.35, y + 0.47, 7.9, 0.5, [(leiras, {})], size=20, color=fa.szoveg)
            y += lep
            if i < len(sz) - 1:
                a.rect(s, MX, y - 0.17, a.SZ - 2 * MX, 0.015, fill=fa.vonal)
        return _vege(s, fa, d)
    if v == "D":
        cw, gap = 3.62, 0.38
        nsz = min([a.fit(n, cw - 0.75, 54) for n, _, _ in sz] or [54])
        ch = ALSO_HATAR - top
        for i, (n, cimke, leiras) in enumerate(sz[:3]):
            x = MX + i * (cw + gap)
            a.kartya(s, x, top, cw, ch, fill="card")
            fk = e.fel("card")
            a.text(s, x + 0.38, top + 0.35, cw - 0.7, 1.0, [(n, {})], size=nsz, color=fk.szam if i != 1 else fk.szam2,
                   font="cim")
            yy = top + 0.35 + a.sormagassag(nsz) + 0.12
            lh = a.blokk_magassag(cimke, cw - 0.7, 21, "torzs", True, 1.05)
            a.text(s, x + 0.4, yy, cw - 0.7, lh + 0.1, [(cimke, {"bold": True})], size=21, color=fk.cim, spacing=1.05)
            if leiras:
                lp = a.fit_blokk(leiras, cw - 0.75, top + ch - (yy + lh + 0.12) - 0.2, 20, "torzs", False, 1.1, 20)
                a.text(s, x + 0.4, yy + lh + 0.12, cw - 0.75, 1.6, [(leiras, {})], size=lp, color=fk.szoveg, spacing=1.1)
        return _vege(s, fa, d)
    # A: három oszlop
    xs = [MX, MX + 4.0, MX + 8.0]
    nsz = min([a.fit(n, 3.25, 80) for n, _, _ in sz] or [80])
    for i, (n, cimke, leiras) in enumerate(sz[:3]):
        a.text(s, xs[i], top, 3.7, 1.4, [(n, {})], size=nsz, color=fa.szam if i != 1 else fa.szam2, font="cim")
        yb = top + a.sormagassag(nsz) + 0.12
        a.rect(s, xs[i] + 0.04, yb, 0.75, 0.07, fill=fa.kiemel)
        a.text(s, xs[i] + 0.04, yb + 0.22, 3.6, 0.45, [(cimke, {"bold": True})], size=22, color=fa.cim)
        if leiras:
            lp = a.fit_blokk(leiras, 3.55, ALSO_HATAR - (yb + 0.72), 20, "torzs", False, 1.12, 20)
            a.text(s, xs[i] + 0.04, yb + 0.72, 3.55, 1.6, [(leiras, {})], size=lp, color=fa.szoveg, spacing=1.12)
    return _vege(s, fa, d)


# ================================================================== IDÉZET (idezet A-E)

def _idezojel(s, x, y_szoveg, f, size=90):
    """Díszítő nyitó idézőjel („) a szöveg fölött: a jel a sor alapvonalán ül, ezért a dobozt úgy tesszük, hogy a jel
    alja a szöveg teteje fölé essen."""
    teto = y_szoveg - 0.1 - 1.1 * size / 72.0
    a.text(s, x, teto, 1.6, 1.25 * size / 72.0 + 0.1, [("„", {})], size=size, color=f.kiemel, font="cim")


def _szerzo(s, x, y, w, d, f, size=21):
    runs = [(d.get("szerzo", ""), {"bold": True, "color": f.cim})]
    if d.get("szerep"):
        runs.append(("\n" + d["szerep"], {"color": f.halvany, "size": 18}))
    a.text(s, x, y, w, 0.9, runs, size=size, font="torzs", spacing=1.05)


def idezet(prs, d, v=None):
    v = v or a.T.v("idezet")
    fa = felulet_tipus("idezet", d)
    ph = _fotok(d, 1)
    q = d.get("idezet", "")
    if v == "B":
        s = e.dia(prs, fa)
        e.fotokeret(s, d.get("portre") or ph[0], MX, 0.95, 1.65, 1.65, fa, valtozat="B")
        a.text(s, MX + 1.95, 1.3, 8, 0.5, [(d.get("szerzo", ""), {})], size=24, color=fa.cim, font="cim")
        a.text(s, MX + 1.95, 1.85, 8, 0.45, [(d.get("szerep", ""), {})], size=18, color=fa.halvany)
        qp = a.fit_blokk("„" + q + "”", 11.4, 3.5, 50, "cim", None, 1.06)
        a.text(s, MX - 0.03, 3.0, 11.5, 3.6, [("„" + q + "”", {})], size=qp, color=fa.cim, font="cim", spacing=1.06)
        return _vege(s, fa, d)
    if v == "C":
        s = e.dia(prs, fa)
        e.textura(s, fa, 6.8, 0, a.SZ - 6.8, a.MA, seed=13, kozep=(10.4, 3.4), n=7)
        a.kartya(s, MX, 1.25, 6.75, 4.9, fill="card")
        fk = e.fel("card")
        a.rect(s, MX, 1.25, 0.11, 4.9, fill=fk.kiemel)
        e.kicker(s, MX + 0.55, 1.6, 5.8, d.get("kicker"), fk)
        _idezojel(s, MX + 0.48, 2.85, fk, 80)
        qp = a.fit_blokk(q, 5.85, 2.2, 34, "cim", None, 1.1)
        qh = a.blokk_magassag(q, 5.85, qp, "cim", None, 1.1)
        a.text(s, MX + 0.55, 2.85, 5.85, qh + 0.2, [(q, {})], size=qp, color=fk.cim, font="cim", spacing=1.1)
        _szerzo(s, MX + 0.55, 2.85 + qh + 0.28, 5.8, d, fk)
        e.fotokeret(s, ph[0], 8.2, 1.15, 3.95, 4.95, fa, valtozat="C", forgas=3.5, felirat=d.get("felirat"))
        return _vege(s, fa, d)
    if v == "D":
        s = e.dia(prs, e.fel("card"))
        fs = e.fel("primary") if e.fel("primary").sotet else e.fel("deep")
        _panel(s, ph[0], 0, 0, 6.6, a.MA, fatyol=(fs.bg, 30))
        fk = e.fel("card")
        e.kicker(s, 7.2, 1.35, 5.5, d.get("kicker"), fk)
        _idezojel(s, 7.12, 2.75, fk, 86)
        qp = a.fit_blokk(q, 5.55, 2.9, 34, "cim", None, 1.1)
        qh = a.blokk_magassag(q, 5.55, qp, "cim", None, 1.1)
        a.text(s, 7.2, 2.75, 5.55, qh + 0.2, [(q, {})], size=qp, color=fk.cim, font="cim", spacing=1.1)
        a.rect(s, 7.22, 2.75 + qh + 0.35, 0.5, 0.05, fill=fk.kiemel)
        _szerzo(s, 7.2, 2.75 + qh + 0.5, 5.4, d, fk)
        return _vege(s, fk, d)
    if v == "E":
        s = e.dia(prs, fa)
        e.fotokeret(s, ph[0], 8.05, 0.62, 4.45, 5.85, fa, valtozat="D")
        e.kicker(s, MX, 1.15, 6.6, d.get("kicker"), fa)
        a.rect(s, MX + 0.02, 1.62, 1.1, 0.09, fill=fa.kiemel)
        qp = a.fit_blokk(q, 6.6, 3.2, 40, "cim", None, 1.08)
        qh = a.blokk_magassag(q, 6.6, qp, "cim", None, 1.08)
        a.text(s, MX - 0.03, 2.0, 6.7, qh + 0.2, [("„" + q + "”", {})], size=qp, color=fa.cim, font="cim", spacing=1.08)
        _szerzo(s, MX, 2.0 + qh + 0.45, 6.4, d, fa)
        return _vege(s, fa, d)
    # A: fotó és idézet osztva
    s = e.dia(prs, fa)
    _panel(s, ph[0], 0, 0, 5.5, a.MA)
    e.kicker(s, 6.1, 1.3, 6.6, d.get("kicker"), fa)
    _idezojel(s, 6.0, 2.7, fa)
    qp = a.fit_blokk(q, 6.5, 2.9, 36, "cim", None, 1.1)
    qh = a.blokk_magassag(q, 6.5, qp, "cim", None, 1.1)
    a.text(s, 6.1, 2.7, 6.5, qh + 0.2, [(q, {})], size=qp, color=fa.cim, font="cim", spacing=1.1)
    ay = min(max(2.7 + qh + 0.35, 4.9), 5.7)
    a.rect(s, 6.12, ay, 0.5, 0.05, fill=fa.kiemel)
    _szerzo(s, 6.1, ay + 0.15, 6.0, d, fa)
    return _vege(s, fa, d)


# ================================================================== ESETTANULMÁNY, KÉRDÉS, BEMUTATKOZÓ

def eset(prs, d, v=None):
    """Esettanulmány / példa: pill, kicker, cím, rövid szöveg, 2 pont vagy 2-3 szám, jobbra 1-2 fotó."""
    fa = felulet_tipus("eset", d)
    s = e.dia(prs, fa)
    y = 0.75
    if d.get("pill"):
        e.pill(s, MX, y, d["pill"].upper(), fa, fill=fa.kiemel, size=15, h=0.48)
        y += 0.78
    e.kicker(s, MX, y, 6.3, d.get("kicker"), fa)
    pt, th, y0 = e.cimsor(s, MX - 0.03, y + 0.42, 6.3, 1.3, d["cim"], 36, fa, min_pt=28)
    yy = y0 + th + 0.28
    pontok = d.get("pontok") or []
    also = 6.92
    # a pontok egymás alatt, vagy ha nem férnek el (2-3 pont), egymás mellett
    egymas_alatt = sum(a.blokk_magassag(c, 5.45, 21, "torzs", True, 1.08) + 0.06 +
                       a.blokk_magassag(l or "", 5.45, 20, "torzs", False, 1.12) for c, l in pontok) + 0.22 * (len(pontok) - 1)
    oszlopw = 6.2 / max(1, len(pontok))
    egymas_mellett = max([a.blokk_magassag(c, oszlopw - 0.75, 21, "torzs", True, 1.08) + 0.06 +
                          a.blokk_magassag(l or "", oszlopw - 0.75, 20, "torzs", False, 1.12) for c, l in pontok] or [0])
    szoveg_h = a.blokk_magassag(d.get("szoveg") or "", 6.1, 20, "torzs", False, 1.12) + 0.3 if d.get("szoveg") else 0
    if d.get("szamok"):
        lista_h = 1.55
    elif pontok and yy + szoveg_h + egymas_alatt > also and len(pontok) <= 3 and oszlopw >= 3.4:
        lista_h = -egymas_mellett
    else:
        lista_h = egymas_alatt if pontok else 0
    if d.get("szoveg"):
        maxh = also - yy - abs(lista_h) - 0.3
        yy += _szoveg(s, MX, yy, 6.1, d["szoveg"], fa, size=20, maxh=maxh, spacing=1.12) + 0.3
    if d.get("szamok"):
        cw = 6.2 / len(d["szamok"])
        npt = min(a.fit(n, cw - 0.3, 44) for n, _ in d["szamok"])
        for i, (n, cimke) in enumerate(d["szamok"]):
            a.text(s, MX + i * cw, yy, cw - 0.15, 0.8, [(n, {})], size=npt, color=fa.szam if i != 1 else fa.szam2,
                   font="cim")
            a.text(s, MX + i * cw, yy + a.sormagassag(npt) + 0.02, cw - 0.3, 0.9, [(cimke, {})], size=20,
                   color=fa.szoveg, spacing=1.1)
    elif pontok and lista_h < 0:
        for i, (c, l) in enumerate(pontok):
            _pont(s, MX + 0.02 + i * oszlopw, yy, oszlopw - 0.15, i, c, l, fa, pt=20, cim_pt=21)
    elif pontok:
        _lista(s, MX + 0.02, yy, also, 6.2, pontok, fa, cim_pt=21, pt=20, max_koz=0.3)
    ph = _fotok(d, 2)
    fk = a.T.v("fotokeret")
    if len(ph) >= 2 and fk != "B":
        e.fotokeret(s, ph[0], 7.25, 0.55, 4.75, 3.2, fa, seed=1, forgas=-3.0 if fk == "C" else None)
        e.fotokeret(s, ph[1], 8.15, 3.45, 4.3, 2.95, fa, seed=0, forgas=3.0 if fk == "C" else None)
    elif ph:
        e.fotokeret(s, ph[0], 7.35, 1.0, 5.0, 4.9, fa)
    return _vege(s, fa, d)


def kerdes(prs, d, v=None):
    """Kérdés- vagy ritmusdia: a ritmus színén, nagy kérdés, alatta egy mondat."""
    fr = felulet_tipus("kerdes", d)
    s = e.dia(prs, fr)
    e.textura(s, fr, 0, 0, a.SZ, a.MA, seed=17, kozep=(11.2, 1.6), n=10)
    formak = a.T.motivum.get("formak_svg") or {}
    jel = a.T.motivum.get("jel") or next(iter(formak), None)
    if jel:
        a.motivum(s, jel, 10.6, 4.2, 1.6, 1.6, fill=a.kever(fr.kiemel, fr.bg, 0.35))
    a.rect(s, MX + 0.02, 1.75, 1.0, 0.09, fill=fr.kiemel)
    e.kicker(s, MX, 2.08, 10, d.get("kicker"), fr)
    q = d.get("kerdes", "")
    pt, th, y0 = e.cimsor(s, MX - 0.03, 2.55, 9.5, 2.9 if d.get("alcim") else 3.8, q, 54, fr)
    if d.get("alcim"):
        _szoveg(s, MX, y0 + th + 0.35, 9.0, d["alcim"], fr, size=23, maxh=6.75 - (y0 + th + 0.35))
    return _vege(s, fr, d)


def bemutatkozo(prs, d, v=None):
    """Bemutatkozó: balra cím és szöveg, jobbra egy fotó a választott keretben (a fotókeret előnézete is ez)."""
    fa = felulet_tipus("bemutatkozo", d)
    s = e.dia(prs, fa)
    e.textura(s, fa, 6.6, 0, a.SZ - 6.6, a.MA, seed=29, kozep=(10.2, 3.8), n=7)
    e.kicker(s, MX, 1.2, 6.0, d.get("kicker"), fa)
    pt, th, y0 = e.cimsor(s, MX - 0.03, 1.65, 6.0, 1.9, d["cim"], 50, fa)
    yy = y0 + th + 0.4
    if d.get("szoveg"):
        yy += _szoveg(s, MX, yy, 5.7, d["szoveg"], fa, size=21, maxh=6.7 - yy) + 0.3
    if d.get("kezi") and yy < 6.2:
        e.kezi(s, MX, yy, 5.8, 0.6, d["kezi"], fa, size=26)
    ph = _fotok(d, 1)
    fk = v or a.T.v("fotokeret")
    if fk == "B":
        e.fotokeret(s, ph[0], 7.75, 1.0, 4.6, 4.6, fa, valtozat="B")
    else:
        e.fotokeret(s, ph[0], 7.45, 0.75, 4.75, 5.75, fa, valtozat=fk, forgas=2.5, felirat=d.get("felirat"))
    return _vege(s, fa, d)


# ================================================================== KÉPERNYŐKÉP MAGYARÁZATTAL (új)

def kepernyokep(prs, d, v=None):
    """Képernyőkép böngészőkeretben, rajta számozott pontok, jobbra a magyarázatuk.
    d: kep (útvonal), kivagas [x0, y0, x1, y1] (pixel, elhagyható), url (a keret címsorába),
       pontok [[x, y, cím, leírás], ...] (x, y: 0..1 a kivágott képen)."""
    from PIL import Image
    fa = felulet_tipus("kepernyokep", d)
    s = e.dia(prs, fa)
    e.kicker(s, MX, 0.62, 11, d.get("kicker"), fa)
    pt, th, y0 = e.cimsor(s, MX - 0.03, 1.0, 11.4, 1.0, d["cim"], 40, fa)
    import os
    kep = d["kep"] if os.path.isabs(str(d["kep"])) else os.path.join(a.T.alap, str(d["kep"]))
    im = Image.open(kep)
    if d.get("kivagas"):
        x0, y0_, x1, y1 = d["kivagas"]
        im = im.crop((x0, y0_, x1, y1))
        kep = str(a.cache_mappa("kepernyo") / ("kep_%d_%d_%d_%d_%s.png" % (x0, y0_, x1, y1, abs(hash(kep)) % 99999)))
        im.save(kep)
    ar = im.size[0] / float(im.size[1])
    top = max(2.05, y0 + th + 0.35)
    if ar < 0.85:
        # álló képernyőkép (telefon): készülék-keretben, a magyarázat több helyet kap
        dh = ALSO_HATAR + 0.25 - top
        dw = min(4.4, dh * ar + 0.6)
        kp = a.keszulek(s, {"ut": kep, "w": im.size[0], "h": im.size[1]}, MX, top, dw, dh)
        ix, iy, iw, ih = kp.left / a.EMU_IN, kp.top / a.EMU_IN, kp.width / a.EMU_IN, kp.height / a.EMU_IN
        jobb = MX + dw
    else:
        bar = 0.34
        maxw, maxh = 7.0, ALSO_HATAR + 0.2 - top - bar
        kw = min(maxw, maxh * ar)
        kh = kw / ar
        bx, by = MX, top
        a.kartya(s, bx, by, kw, kh + bar, fill="card", arnyek_="lagy")
        a.rect(s, bx, by, kw, bar, fill=a.kever("line" if "line" in a.T.szin else "ink_3", "card", 0.3))
        for i in range(3):
            a.oval(s, bx + 0.16 + i * 0.2, by + bar / 2.0 - 0.055, 0.11, 0.11, fill=a.kever("ink_3", "card", 0.35))
        if d.get("url") and kw > 3.0:
            a.text(s, bx + 0.9, by, kw - 1.8, bar, [(d["url"], {})], size=13, color="ink_2", align=C, anchor=a.MID,
                   wrap=False)
        a.pic(s, kep, bx, by + bar, w=kw, h=kh)
        ix, iy, iw, ih = bx, by + bar, kw, kh
        jobb = bx + kw
    pontok = d.get("pontok") or []
    jd = 0.5
    for i, p in enumerate(pontok):
        px, py = ix + p[0] * iw, iy + p[1] * ih
        a.oval(s, px - jd / 2.0 - 0.04, py - jd / 2.0 - 0.04, jd + 0.08, jd + 0.08, fill="card")
        a.oval(s, px - jd / 2.0, py - jd / 2.0, jd, jd, fill="accent")
        a.text(s, px - jd / 2.0, py - jd / 2.0, jd, jd, [(str(i + 1), {"bold": True})], size=18, color=e.ellen("accent"),
               align=C, anchor=a.MID)
    lx = jobb + 0.5
    lw = a.SZ - lx - 0.6
    tx, tw = lx + 0.62, lw - 0.62
    n = max(1, len(pontok))
    hely = ALSO_HATAR - top
    elemek_ = []
    for p in pontok:
        cp = a.fit_blokk(p[2], tw, 0.7, 22, "torzs", True, 1.05, min_pt=20)
        ch = a.blokk_magassag(p[2], tw, cp, "torzs", True, 1.05)
        dh = a.blokk_magassag(p[3], tw, 20, "torzs", False, 1.1) if len(p) > 3 and p[3] else 0
        elemek_.append((cp, ch, dh))
    ossz = sum(ch + (0.08 + dh if dh else 0) for _, ch, dh in elemek_)
    koz = min(0.6, max(0.18, (hely - ossz) / max(1, n - 1))) if n > 1 else 0
    y = top
    for i, (p, (cp, ch, dh)) in enumerate(zip(pontok, elemek_)):
        a.oval(s, lx, y + 0.02, 0.44, 0.44, fill="accent")
        a.text(s, lx, y + 0.02, 0.44, 0.44, [(str(i + 1), {"bold": True})], size=16, color=e.ellen("accent"),
               align=C, anchor=a.MID)
        a.text(s, tx, y, tw, ch + 0.1, [(p[2], {"bold": True})], size=cp, color=fa.cim, spacing=1.05)
        if dh:
            a.text(s, tx, y + ch + 0.08, tw, dh + 0.1, [(p[3], {})], size=20, color=fa.szoveg, spacing=1.1)
        y += ch + (0.08 + dh if dh else 0) + koz
    return _vege(s, fa, d)


# ================================================================== ZÁRÓDIA (zaro A-E)

def _kapcsolat_sorok(s, x, y, w, d, f, size=22, lep=0.82):
    for cimke, ertek in d.get("kontaktok") or []:
        a.text(s, x, y, w, 0.32, [(cimke.upper(), {})], size=16, color=f.kicker, font="cimke", tracking=1.4)
        a.text(s, x, y + 0.3, w, 0.5, [(ertek, {"bold": True})], size=size, color=f.cim)
        y += lep
    return y


def _url_pill(s, x, y, url, f, align=L):
    fill = "card" if f.sotet else "deep"
    w = a.szelesseg(url, 20, "torzs", True) + 1.0
    xx = x - w / 2.0 if align == C else x
    r = a.T.r_gomb
    a.rect(s, xx, y, w, 0.66, fill=fill, shape=a.MSO_SHAPE.ROUNDED_RECTANGLE, rad=min(0.5, r / 0.66))
    a.text(s, xx, y, w, 0.66, [(url, {"bold": True})], size=20, color=e.ellen(fill), align=C, anchor=a.MID)
    return w


def zaro(prs, d, v=None):
    v = v or a.T.v("zaro")
    ph = _fotok(d, 1)
    if v == "A":
        fs = _sotet_panel()
        s = e.dia(prs, fs)
        e.textura(s, fs, 0, 0, a.SZ, a.MA, seed=31, kozep=(6.6, 3.7), n=12)
        formak = a.T.motivum.get("formak_svg") or {}
        jel = a.T.motivum.get("jel") or next(iter(formak), None)
        if jel:
            halv = a.kever(fs.kiemel, fs.bg, 0.55)
            a.motivum(s, jel, -0.9, 4.6, 3.6, 3.6, fill=halv)
            a.motivum(s, jel, 10.9, -1.0, 3.2, 3.2, fill=halv)
        a.rect(s, a.SZ / 2.0 - 0.5, 1.45, 1.0, 0.09, fill=fs.kiemel)
        e.kicker(s, 1.0, 1.78, a.SZ - 2.0, d.get("kicker"), fs, align=C)
        pt, th, y0 = e.cimsor(s, 1.2, 2.25, a.SZ - 2.4, 1.9, d["cim"], 58, fs, align=C)
        yy = y0 + th + 0.3
        if d.get("alcim"):
            yy += _szoveg(s, 2.2, yy, a.SZ - 4.4, d["alcim"], fs, size=22, align=C, maxh=1.2) + 0.35
        if d.get("url"):
            _url_pill(s, a.SZ / 2.0, min(yy, 5.75), d["url"], fs, align=C)
        return _vege(s, fs, d, sotet=True)
    if v == "C":
        fs = _sotet_panel()
        s = e.dia(prs, fs)
        _hatter_foto(s, d, fs, opacity=58, also_fatyol=False, seed=23)
        e.kicker(s, MX, 1.55, 9, d.get("kicker"), fs, color=fs.cim)
        pt, th, y0 = e.cimsor(s, MX - 0.03, 2.0, 9.4, 2.0, d["cim"], 56, fs)
        yy = y0 + th + 0.3
        if d.get("alcim"):
            yy += _szoveg(s, MX, yy, 7.6, d["alcim"], fs, size=22, maxh=1.3) + 0.4
        if d.get("url"):
            _url_pill(s, MX, min(yy, 5.8), d["url"], fs)
        return _vege(s, fs, d, sotet=True)
    fa = e.felulet_alap()
    s = e.dia(prs, fa)
    if v == "D":
        _panel(s, ph[0], 0, 0, 6.3, a.MA)
        e.kicker(s, 6.95, 0.8, 5.6, d.get("kicker"), fa)
        pt, th, y0 = e.cimsor(s, 6.92, 1.2, 5.6, 1.75, d["cim"], 44, fa)
        yy = y0 + th + 0.22
        if d.get("alcim"):
            yy += _szoveg(s, 6.95, yy, 5.5, d["alcim"], fa, size=20, maxh=1.0) + 0.3
        n = max(1, len(d.get("kontaktok") or []))
        lep = max(0.66, min(0.8, (ALSO_HATAR - yy - 0.3) / n))
        kh = lep * n + 0.3
        a.kartya(s, 6.95, yy, 5.6, kh, fill="card")
        _kapcsolat_sorok(s, 7.3, yy + 0.16, 5.0, d, e.fel("card"), size=21, lep=lep)
        return _vege(s, fa, d)
    if v == "E":
        e.textura(s, fa, 0, 0, a.SZ, a.MA, seed=37, kozep=(6.6, 3.2), n=12)
        formak = a.T.motivum.get("formak_svg") or {}
        jel = a.T.motivum.get("jel") or next(iter(formak), None)
        masik = [k for k in formak if k != jel]
        if jel:
            a.motivum(s, jel, a.SZ / 2.0 - 0.45, 0.85, 0.9, 0.9, fill=fa.kiemel)
        if masik:
            a.motivum(s, masik[0], 2.1, 1.6, 0.7, 0.85, fill=fa.jel, forgas=-35)
            a.motivum(s, masik[0], 10.6, 1.5, 0.7, 0.85, fill=fa.jel, forgas=30)
        e.kicker(s, 1.0, 2.0, a.SZ - 2.0, d.get("kicker"), fa, align=C)
        pt, th, y0 = e.cimsor(s, 1.0, 2.45, a.SZ - 2.0, 2.1, d["cim"], 64, fa, align=C)
        yy = y0 + th + 0.3
        if d.get("alcim"):
            yy += _szoveg(s, 2.0, yy, a.SZ - 4.0, d["alcim"], fa, size=22, align=C, maxh=1.2) + 0.35
        sor = "   ·   ".join(x[1] for x in d.get("kontaktok") or [])
        if sor:
            sp = a.fit(sor, a.SZ - 3.0, 22, "torzs", True, min_pt=18)
            a.text(s, 1.5, min(yy, 6.05), a.SZ - 3.0, 0.5, [(sor, {"bold": True})], size=sp, color=fa.kicker, align=C)
        return _vege(s, fa, d)
    # B: elérhetőség és portré
    e.kicker(s, MX, 1.05, 7, d.get("kicker"), fa)
    pt, th, y0 = e.cimsor(s, MX - 0.03, 1.5, 7.6, 1.8, d["cim"], 48, fa)
    yy = y0 + th + 0.25
    if d.get("alcim"):
        yy += _szoveg(s, MX, yy, 7.2, d["alcim"], fa, size=21, maxh=1.0) + 0.35
    n = len(d.get("kontaktok") or [])
    lep = min(0.82, (ALSO_HATAR + 0.25 - yy) / max(1, n))
    _kapcsolat_sorok(s, MX, yy, 7.0, d, fa, size=22, lep=lep)
    e.textura(s, fa, 8.6, 0, a.SZ - 8.6, a.MA, seed=41, kozep=(10.9, 3.3), n=6)
    e.fotokeret(s, ph[0], 9.35, 1.25, 3.1, 3.1, fa, valtozat="B")
    k = a.T.kontakt or {}
    a.text(s, 8.6, 4.65, 4.6, 0.5, [(k.get("nev") or "", {})], size=26, color=fa.cim, font="cim", align=C)
    if k.get("szerep"):
        a.text(s, 8.6, 5.2, 4.6, 0.45, [(k["szerep"], {})], size=18, color=fa.halvany, align=C)
    return _vege(s, fa, d)


TIPUSOK = {"cimdia": cimdia, "fejezet": fejezet, "felsorolas": felsorolas, "ket_hasab": ket_hasab,
           "folyamat": folyamat, "kartyak": kartyak, "szamok": szamok, "idezet": idezet, "eset": eset,
           "kerdes": kerdes, "kepernyokep": kepernyokep, "zaro": zaro, "bemutatkozo": bemutatkozo}


def dia(prs, d, v=None):
    import katalogus as K
    t = d.get("tipus")
    if t not in TIPUSOK:
        raise ValueError("Ismeretlen diatípus: %r (van: %s)" % (t, ", ".join(TIPUSOK)))
    kat = K.DIA_KATEGORIA.get(t)
    a.T.karakter_aktiv = K.forma_karakter(kat, v or a.T.v(kat)) if kat else None
    try:
        return TIPUSOK[t](prs, d, v)
    finally:
        a.T.karakter_aktiv = None
