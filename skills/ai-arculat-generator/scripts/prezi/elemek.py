# -*- coding: utf-8 -*-
"""A választható prezi-elemek (a 10 kategória változatai) és a felületek.

Felület (Fel): a dia vagy egy panel háttere, és a rajta olvasható színek, kontraszt-ellenőrzéssel. Minden elem egy
felületre rajzol, így ugyanaz a kód világos papíron, fehéren, sötéten és a ritmustörő színen is olvasható marad.

Változatok (katalogus.py): kiemeles A-E (címsor), fotokeret A-E, ikontarto A-E, felsorolas A-E (jel). A háttér és a
ritmus (hatter A-E) a felulet_alap() és a felulet_ritmus() függvényekben.
"""
import math
import random

import alap as a
from alap import L, C, R


# ------------------------------------------------------------------ felületek

def _valaszt(bg, jeloltek, min_k):
    for c in jeloltek:
        try:
            if a.kontraszt(c, bg) >= min_k:
                return c
        except (ValueError, KeyError):
            continue
    return "#FFFFFF" if a.sotet(bg) else "#111111"


class Fel(object):
    """Egy felület színei: bg, cim, szoveg, halvany, kicker, szam, szam2, jel, kiemel (díszítő szín),
    kiemel_szo (kiemelt szó színe), kiemel_doboz, vonal, kartya, sotet."""

    def __init__(self, bg):
        self.bg = bg
        self.sotet = a.sotet(bg)
        if self.sotet:
            on = ["on_" + bg] if isinstance(bg, str) and ("on_" + bg) in a.T.szin else []
            self.cim = _valaszt(bg, on + ["on_deep", "card", "paper", "#FFFFFF"], 7)
            self.szoveg = _valaszt(bg, [a.kever(self.cim, bg, 0.1), self.cim], 4.5)
            self.halvany = _valaszt(bg, [a.kever(self.cim, bg, 0.28), self.szoveg], 3.0)
            self.kicker = _valaszt(bg, ["accent2", "sand", "tint", self.cim], 3.0)
            self.szam = _valaszt(bg, ["accent2", "sand", self.cim], 3.0)
            self.szam2 = _valaszt(bg, ["sand", "tint", self.cim], 3.0)
            self.jel = _valaszt(bg, ["accent2", "sand", self.cim], 2.5)
            self.kiemel = _valaszt(bg, ["accent2", "sand", "accent"], 2.2)
            self.kiemel_szo = _valaszt(bg, ["accent2", "sand", self.cim], 3.0)
            self.kiemel_doboz = a.kever(self.kiemel, bg, 0.55)
            self.vonal = a.kever(self.cim, bg, 0.72)
            self.textura = a.kever(self.cim, bg, 0.86)
        else:
            self.cim = _valaszt(bg, ["ink", "deep"], 7)
            self.szoveg = _valaszt(bg, ["ink_2", "ink"], 4.5)
            self.halvany = _valaszt(bg, ["ink_3", "ink_2"], 3.0)
            self.kicker = _valaszt(bg, ["primary_text", "accent_text", "primary", "ink_2"], 3.0)
            self.szam = _valaszt(bg, ["primary_text", "primary", "ink"], 3.0)
            self.szam2 = _valaszt(bg, ["accent_text", "accent", "primary_text"], 3.0)
            self.jel = _valaszt(bg, ["primary", "accent", "ink"], 2.5)
            self.kiemel = _valaszt(bg, ["accent", "primary", "ink_2"], 2.2)
            self.kiemel_szo = _valaszt(bg, ["accent_text", "primary_text", "ink"], 3.0)
            self.kiemel_doboz = a.kever("accent2" if "accent2" in a.T.szin else self.kiemel, bg, 0.55)
            self.vonal = "line" if "line" in a.T.szin else a.kever(self.cim, bg, 0.8)
            self.textura = a.kever("line" if "line" in a.T.szin else self.halvany, bg, 0.25)
        self.kartya = "card"
        self.ceruza = _valaszt(bg, ["ink_2", "primary"] if not self.sotet else ["accent2", "sand", self.cim], 3.0)


def fel(bg):
    return Fel(bg)


# háttér és ritmus: (alap, ritmus) szerepnevek; None = nincs ritmustörő szín
HATTER = {"A": ("paper", "deep"), "B": ("card", "primary"), "C": ("tint", "accent"), "D": ("deep", "paper"),
          "E": ("paper", None)}


def felulet_alap(valtozat=None):
    al, _ = HATTER.get(valtozat or a.T.v("hatter"), HATTER["A"])
    if al not in a.T.szin:
        al = "paper" if "paper" in a.T.szin else "card"
    return fel(al)


def felulet_ritmus(valtozat=None):
    al, rit = HATTER.get(valtozat or a.T.v("hatter"), HATTER["A"])
    if not rit or rit not in a.T.szin:
        return felulet_alap(valtozat)
    return fel(rit)


def dia(prs, f):
    return a.slide(prs, f.bg)


def karakter_csik(s):
    """A karakter részlete, ha színcsík (pl. Lili „préri” karakterénél az évszak-csík): a dia legtetején, minden
    fölött (a teljes képes diákon is látszik). A dia végén kell hívni."""
    r = a.T.reszlet() if a.T else ""
    if any(k in r for k in ("csík", "sáv")):
        szinek = [c for c in ("primary", "accent2", "accent", "deep") if c in a.T.szin]
        w = a.SZ / max(1, len(szinek))
        for i, c in enumerate(szinek):
            a.rect(s, i * w, 0, w + 0.01, 0.1, fill=c)


# ------------------------------------------------------------------ textúra (a webes háttér-textúra párja)

def textura(s, f, x=0.0, y=0.0, w=a.SZ, h=a.MA, seed=7, kozep=None, n=9):
    elemek_ = a.motivum_elemek("textura")
    t = elemek_[seed % len(elemek_)] if elemek_ else {}
    szo = ((t.get("nev") or "") + " " + (t.get("leiras") or "")).lower()
    r = a.T.reszlet()
    if any(k in r for k in ("lombkorona", "kör")):
        # a karakter részlete: alaprajzi lombkorona-kör a textúra közepén (pl. Lili „tervezőasztal” karaktere)
        cx, cy = kozep or (x + w * 0.7, y + h * 0.45)
        d = min(2.4, w * 0.45, h * 0.5)
        o = a.oval(s, cx - d / 2.0, cy - d / 2.0, d, d, fill=None, line=a.kever(f.kiemel, f.bg, 0.25), lw=1.25)
        a.oval(s, cx - 0.05, cy - 0.05, 0.1, 0.1, fill=a.kever(f.kiemel, f.bg, 0.25))
        for i in range(8):
            t_ = 2 * math.pi * i / 8.0
            a.sokszog(s, [(cx + d * 0.42 * math.cos(t_), cy + d * 0.42 * math.sin(t_)),
                          (cx + d * 0.5 * math.cos(t_), cy + d * 0.5 * math.sin(t_))], fill=None,
                      line=a.kever(f.kiemel, f.bg, 0.25), lw=1.0, zart=False)
    if not szo.strip():
        return []
    if any(k in szo for k in ("herbárium", "préselt", "levél", "levelek")):
        # szórt levélkörvonalak (a márka motívumából), nagyon halványan
        formak = a.T.motivum.get("formak_svg") or {}
        nev = "level" if "level" in formak else (a.T.motivum.get("jel") or next(iter(formak), None))
        if not nev:
            return []
        rnd = random.Random(seed)
        ki = []
        db = max(5, int(w * h / 6.5))
        for i in range(db):
            m_ = rnd.uniform(0.38, 0.85)
            px = x + rnd.uniform(0, max(0.01, w - m_))
            py = y + rnd.uniform(0, max(0.01, h - m_ * 1.3))
            ki += a.motivum(s, nev, px, py, m_, m_ * 1.3, fill=None, line=f.textura, lw=0.9, forgas=rnd.uniform(-70, 70))
        return ki
    if any(k in szo for k in ("rács", "kocka", "milliméter", "grid")):
        ki = []
        lep = 0.42
        xx = x
        while xx <= x + w:
            ki.append(a.rect(s, xx, y, 0.008, h, fill=f.textura))
            xx += lep
        yy = y
        while yy <= y + h:
            ki.append(a.rect(s, x, yy, w, 0.008, fill=f.textura))
            yy += lep
        return ki
    if any(k in szo for k in ("pötty", "pont", "szórt", "dot")):
        rnd = random.Random(seed)
        return [a.oval(s, x + rnd.uniform(0, w), y + rnd.uniform(0, h), 0.06, 0.06, fill=f.textura) for _ in range(90)]
    if any(k in szo for k in ("hullám", "csík", "vonal")) and "szint" not in szo:
        ki = []
        for k in range(10):
            yy = y + h * (k + 0.5) / 10.0
            pts = [(x + w * i / 80.0, yy + 0.12 * math.sin(i / 6.0 + k)) for i in range(81)]
            ki.append(a.sokszog(s, pts, fill=None, line=f.textura, lw=0.9, zart=False))
        return ki
    return a.szintvonalak(s, x, y, w, h, color=f.textura, lw=0.9, n=n, seed=seed, kozep=kozep)


# ------------------------------------------------------------------ kicker, kis címke

def kicker(s, x, y, w, t, f, align=L, size=17, min_size=12, color=None):
    """Kis felső címke a címke-betűvel, nagybetűvel, egy sorban: előbb a betűközből, aztán a méretből enged
    (legfeljebb min_size-ig). Ha így sem fér ki, figyelmeztet (a címkét rövidíteni kell). Az aktív karakter részlete
    itt jelenik meg: „tábla” -> növénycímke-tábla keret, „latin/címk” -> hajszálvonal utána, „ceruza/skicc” ->
    ceruzás aláhúzás."""
    if not t:
        return None
    T_ = t.upper()
    tr = 1.6

    def szel(sz, tr_):
        return a.szelesseg(T_, sz, "cimke") + len(T_) * tr_ / 72.0
    while szel(size, tr) > w and (tr > 0 or size > min_size):
        if tr > 0:
            tr = max(0.0, tr - 0.4)
        else:
            size = max(min_size, size - 0.5)
    elfer = szel(size, tr) <= w
    if not elfer:
        print("  ! túl hosszú kicker (%d karakter), rövidítsd: %s" % (len(t), t))
    szin = color or f.kicker
    tw = min(szel(size, tr), w)
    bx = x if align == L else (x + (w - tw) / 2.0 if align == C else x + w - tw)
    r = a.T.reszlet()
    th = size * 1.2 / 72.0
    if elfer and "tábla" in r:
        p = 0.13
        a.rect(s, bx - p, y - 0.07, tw + 2 * p, th + 0.12, fill=None, line=szin, lw=0.9,
               shape=a.MSO_SHAPE.ROUNDED_RECTANGLE, rad=0.12)
    tb = a.text(s, x, y, (w + 0.3) if (elfer and align == L) else w, 0.42, [(T_, {})], size=size, color=szin,
                font="cimke", tracking=tr, align=align, wrap=not elfer)
    if elfer and "tábla" not in r and any(k in r for k in ("latin", "címk")) and align == L and tw + 0.95 < w:
        ly = y + th * 0.55
        a.rect(s, bx + tw + 0.18, ly, 0.75, 0.012, fill=szin)
    if elfer and any(k in r for k in ("ceruza", "skicc")):
        rnd = random.Random(len(T_))
        ly = y + th + 0.05
        pts = [(bx + tw * i / 24.0, ly + rnd.uniform(-0.012, 0.012) + 0.02 * math.sin(i / 3.0)) for i in range(25)]
        sp = a.sokszog(s, pts, fill=None, line=szin, lw=1.3, zart=False)
        a.vonal_kerek(sp)
    return tb


def kezi(s, x, y, w, h, t, f, size=24, align=L, color=None):
    """Kézírásos sor (a webes kézírás-betűvel), ha van ilyen szerep."""
    if not t:
        return None
    return a.text(s, x, y, w, h, [(t, {})], size=size, color=color or f.kiemel_szo, font="kezi", align=align)


# ------------------------------------------------------------------ címsor kiemeléssel (kiemeles A-E)

def _darabok(sima, tart):
    ki, poz = [], 0
    for x0, x1 in tart:
        if x0 > poz:
            ki.append((sima[poz:x0], False))
        ki.append((sima[x0:x1], True))
        poz = x1
    if poz < len(sima):
        ki.append((sima[poz:], False))
    return ki


def cimsor(s, x, y, w, h, szoveg, pt, f, align=L, spacing=1.02, min_pt=None, valtozat=None, also=False,
           kozep=False, color=None):
    """Címsor a ==kulcsszó== kiemelésével. A méret a dobozhoz igazodik (fit_blokk). A tördelést a motor dönti el, és
    kifejezett sortörésekkel írja a dobozba (a LibreOffice és a PowerPoint alávágással kicsit szűkebben szed, ezért
    határesetben máshol törne, és a díszítés elcsúszna). also=True: a doboz aljához igazít, kozep=True: középre.
    Visszaad: (pontméret, a szöveg magassága, a szöveg teteje)."""
    sima, tart = a.kiemeles_bont(szoveg)
    v = valtozat or a.T.v("kiemeles")
    extra = 0.04 if v == "D" else 0.0          # a karika a szó körül kicsit több helyet kér
    bw = w * (1 - extra)                        # a szövegdoboz szélessége
    dw = bw * 0.975                             # ebben a szélességben tördelünk (biztonsági ráhagyás)
    pt = a.fit_blokk(sima, dw, h, pt, "cim", None, spacing, min_pt)
    def egyben(szov, p):
        hs_ = a.szo_helyek(szov, dw, p, "cim", None, L)
        return all(len({sor for _, ps, sor, _, _ in hs_ if t0 <= ps < t1}) <= 1 for t0, t1 in tart)
    if tart and not egyben(sima, pt):
        # a kiemelt szakasz lehetőleg ne törjön két sorba (a díszítés így egyben marad):
        # 1) sortörés a kiemelt szakasz elé, ha így is elfér; 2) kisebb méret (legfeljebb 18%-kal)
        t0 = tart[0][0]
        also_hatar = max(min_pt or 0, pt * 0.8)
        # A) sortörés a kiemelt szakasz elé, a lehető legnagyobb méretben
        jelolt_a = None
        if t0 > 0 and sima[t0 - 1] == " ":
            proba = sima[:t0 - 1] + "\v" + sima[t0:]
            p2 = a.fit_blokk(proba, dw, h, pt, "cim", None, spacing, min_pt)
            while p2 >= also_hatar and not egyben(proba, p2):
                p2 -= 1
            if p2 >= also_hatar:
                jelolt_a = (proba, p2)
        # B) sortörés nélkül, kisebb mérettel
        jelolt_b = None
        p = pt
        while p >= also_hatar:
            if egyben(sima, p):
                jelolt_b = (sima, p)
                break
            p -= 1
        jo = [j for j in (jelolt_a, jelolt_b) if j]
        if jo:
            sima, pt = max(jo, key=lambda j: j[1])
    # kifejezett sortörések (Shift+Enter) a motor tördelése szerint; a karakterpozíciók nem változnak (szóköz -> \v)
    hs = a.szo_helyek(sima, dw, pt, "cim", None, L)
    betuk_ = list(sima)
    elozo_sor = None
    for _, ps, sor, _, _ in hs:
        if elozo_sor is not None and sor != elozo_sor and ps > 0 and betuk_[ps - 1] == " ":
            betuk_[ps - 1] = "\v"
        elozo_sor = sor
    sima = "".join(betuk_)
    nsor = (max(x[2] for x in hs) + 1) if hs else 1
    th = nsor * a.sormagassag(pt, spacing)
    y0 = y + (h - th) if also else (y + (h - th) / 2.0 if kozep else y)
    cim_szin = color or f.cim
    met = a.T.betu["cim"]["metrika"]
    cap = met["cap"] / float(met["upm"]) * pt / 72.0
    helyek = a.szo_helyek(sima, bw, pt, "cim", None, align)
    eltol = (w * extra / 2.0) if align == C else 0.0
    sorok = {}
    for szo, p, sor, x0, x1 in helyek:
        if any(t0 <= p < t1 for t0, t1 in tart):
            v0 = sorok.get(sor)
            sorok[sor] = (min(v0[0], x0), max(v0[1], x1)) if v0 else (x0, x1)
    utana = []
    for sor, (x0, x1) in sorok.items():
        base = a.alapvonal(y0, pt, spacing, sor)
        X0, X1 = x + eltol + x0, x + eltol + x1
        if v == "A":
            pad = 0.16 * pt / 72.0
            a.rect(s, X0 - pad, base - cap - 0.22 * pt / 72.0, X1 - X0 + 2 * pad, cap + 0.42 * pt / 72.0,
                   fill=f.kiemel_doboz, shape=a.MSO_SHAPE.ROUNDED_RECTANGLE, rad=0.18)
        elif v == "B":
            a.filctoll(s, X0 - 0.05, base - cap * 0.42, X1 - X0 + 0.1, cap * 0.5, color=f.kiemel, alpha=45, seed=sor + 3)
        elif v == "C":
            utana.append(("C", X0, X1, base))
        elif v == "D":
            utana.append(("D", X0, X1, base))
    darabok = _darabok(sima, tart)
    runs = []
    for d, hl in darabok:
        ov = {"font": "cim"}
        if hl and v == "E":
            ov["color"] = f.kiemel_szo
        runs.append((d, ov))
    tb = a.text(s, x + eltol, y0, bw, th + 0.3, runs, size=pt, color=cim_szin, font="cim", align=align,
                spacing=spacing)
    meretvonal = ((a.T.d.get("stilus") or {}).get("kiemeles_C") == "meretvonal") if a.T else False
    for tip, X0, X1, base in utana:
        if tip == "C" and meretvonal:
            # méretvonal: vékony vonal a kulcsszó alatt, két végén kis függőleges jellel és ferde vágással,
            # mint a kerttervek méretezésénél (a webes „Modern · méretvonal” párja)
            yv = base + 0.28 * pt / 72.0
            lw = max(1.3, pt / 30.0)
            jel = 0.13 * pt / 72.0 + 0.05
            c_ = f.jel          # a weben is a fő színnel fut (sötét felületen a díszítő szín)
            sp = a.sokszog(s, [(X0 - 0.04, yv), (X1 + 0.04, yv)], fill=None, line=c_, lw=lw, zart=False)
            for xx in (X0, X1):
                a.sokszog(s, [(xx, yv - jel), (xx, yv + jel)], fill=None, line=c_, lw=lw, zart=False)
                a.sokszog(s, [(xx - jel * 0.55, yv + jel * 0.55), (xx + jel * 0.55, yv - jel * 0.55)], fill=None,
                          line=c_, lw=lw, zart=False)
        elif tip == "C":
            vast = max(0.045, 0.085 * pt / 72.0)
            a.rect(s, X0, base + 0.09 * pt / 72.0, X1 - X0, vast, fill=f.kiemel)
        else:
            mx, my = 0.15 * pt / 72.0, 0.28 * pt / 72.0
            a.ceruza_karika(s, X0 - mx, base - cap - my, X1 - X0 + 2 * mx, cap + 2 * my + 0.12 * pt / 72.0,
                            color=f.ceruza, lw=max(1.6, pt / 26.0), seed=int(X0 * 10) % 7 + 2)
    return pt, th, y0


# ------------------------------------------------------------------ fotókeret (fotokeret A-E)

def _forgat(cx, cy, dx, dy, fok):
    t = math.radians(fok)
    return cx + dx * math.cos(t) - dy * math.sin(t), cy + dx * math.sin(t) + dy * math.cos(t)


def fotokeret(s, foto, x, y, w, h, f, valtozat=None, forgas=None, felirat=None, seed=0, kor_ok=True):
    """Egy fotó a választott keretben, az (x, y, w, h) dobozban. A polaroid és a gyűrű a dobozon belül marad."""
    v = valtozat or a.T.v("fotokeret")
    info = a.foto_info(foto) if foto is not None else None
    if info is None:
        if v == "B" and kor_ok:
            d = min(w, h)
            return a.helyettes(s, x + (w - d) / 2.0, y + (h - d) / 2.0, d, d, kor=True)
        return a.helyettes(s, x, y, w, h)
    if info.get("kepernyo") and not (v == "B" and kor_ok):
        # képernyőképet nem vágunk: készülék-keretben, egészben látszik
        return a.keszulek(s, foto, x, y, w, h)
    if v == "B" and kor_ok:
        d = min(w, h)
        cx, cy = x + w / 2.0, y + h / 2.0
        a.oval(s, cx - d / 2.0, cy - d / 2.0, d, d, fill=None, line=f.kiemel, lw=2.5)
        g = d * 0.06
        return a.pic_circle(s, foto, cx - d / 2.0 + g, cy - d / 2.0 + g, d - 2 * g)
    if v == "C":
        fok = forgas if forgas is not None else (2.5 if seed % 2 == 0 else -2.5)
        m = 0.07 * min(w, h) + 0.06
        also_m = m * (2.4 if felirat else 1.6)
        kw, kh = w, h
        pw, ph = kw - 2 * m, kh - m - also_m
        cx, cy = x + kw / 2.0, y + kh / 2.0
        keret = a.rect(s, x, y, kw, kh, fill="card", line="line" if "line" in a.T.szin else None, lw=0.5)
        keret.rotation = fok
        a.arnyek(keret, "lagy")
        pcx, pcy = _forgat(cx, cy, 0, (m - also_m) / 2.0, fok)
        p = a.pic_cover(s, foto, pcx - pw / 2.0, pcy - ph / 2.0, pw, ph)
        p.rotation = fok
        if felirat:
            fcx, fcy = _forgat(cx, cy, 0, kh / 2.0 - also_m / 2.0, fok)
            fp = a.fit(felirat, pw * 0.94, min(24, max(16, also_m * 72 * 0.45)), "kezi", min_pt=14)
            tb = a.text(s, fcx - pw / 2.0, fcy - also_m * 0.42, pw, also_m * 0.8, [(felirat, {})], size=fp,
                        color=a.T.szin.get("hand", f.kiemel_szo), font="kezi", align=C, anchor=a.MID, wrap=False)
            tb.rotation = fok
        jel = a.T.motivum.get("jel")
        if jel:
            js = max(0.42, 0.13 * min(w, h))
            jx, jy = _forgat(cx, cy, -kw / 2.0 + js * 0.15, -kh / 2.0 + js * 0.15, fok)
            a.motivum(s, jel, jx - js / 2.0, jy - js / 2.0, js, js, fill=f.kiemel if not f.sotet else "accent",
                      forgas=fok - 18)
        return p
    if v == "D":
        o = 0.22
        a.rect(s, x + o, y + o, w - o, h - o, fill=f.kiemel if f.sotet else "accent",
               shape=a.MSO_SHAPE.ROUNDED_RECTANGLE if a.T.r_kartya > 0.01 else a.MSO_SHAPE.RECTANGLE,
               rad=min(0.5, a.T.r_kartya / max(min(w, h), 0.1)))
        return a.pic_round(s, foto, x, y, w - o, h - o)
    if v == "E":
        p = a.pic_round(s, foto, x, y, w, h, duotone=("deep", "paper" if "paper" in a.T.szin else "card"))
        return p
    p = a.pic_round(s, foto, x, y, w, h)
    if a.T.arnyek in ("lagy", "eros"):
        a.arnyek(p, a.T.arnyek)
    return p


# ------------------------------------------------------------------ ikontartó (ikontarto A-E)

def ikontarto(s, nev, x, y, d, f, valtozat=None, szam=None):
    """Ikon a választott tartóban, a d × d dobozban (x, y a bal felső sarok)."""
    v = valtozat or a.T.v("ikontarto")
    ut = a.ikon_ut(nev) if nev else None
    cx, cy = x + d / 2.0, y + d / 2.0
    vil = a.kever("card", f.bg, 0.0)

    def ikon(arany):
        iw = d * arany
        if ut:
            return a.pic_contain(s, ut, cx - iw / 2.0, cy - iw / 2.0, iw, iw)
        # nincs ikon: a márka jele (vagy a sorszám) kerül a helyére
        jel_ = (a.T.motivum or {}).get("jel") or next(iter((a.T.motivum or {}).get("formak_svg") or {}), None)
        alap_bg = "card" if (v in ("A", "C") and f.sotet) or v == "C" else f.bg
        if jel_:
            j = iw * 0.62
            return a.motivum(s, jel_, cx - j / 2.0, cy - j / 2.0, j, j, fill=f.jel if not a.sotet(alap_bg) else "accent2")
        return a.text(s, cx - iw / 2.0, cy - iw / 2.0, iw, iw, [(str(szam or "•"), {})], size=iw * 72 * 0.45,
                      color=f.jel, font="cim", align=C, anchor=a.MID)
    if v == "A":
        if f.sotet:
            a.kartya(s, x, y, d, d, fill="card", line=None, arnyek_="nincs")
            return ikon(0.84)
        return ikon(1.0)
    if v == "B":
        a.oval(s, x, y, d, d, fill=a.kever("tint" if "tint" in a.T.szin else "primary", f.bg, 0.0 if not f.sotet else 0.0)
               if not f.sotet else vil)
        return ikon(0.7)
    if v == "C":
        a.kartya(s, x, y, d, d, fill="card")
        return ikon(0.8)
    if v == "D":
        a.oval(s, x, y, d, d, fill=None if not f.sotet else vil, line=f.jel if not f.sotet else f.kiemel, lw=1.75)
        return ikon(0.66)
    # E: számozott jelvény
    a.oval(s, x, y, d, d, fill=a.kever("tint" if "tint" in a.T.szin else "primary", f.bg, 0.0) if not f.sotet else vil)
    p = ikon(0.66)
    if szam is not None:
        bd = max(0.36, d * 0.3)
        bx, by = x + d - bd * 0.85, y - bd * 0.1
        a.oval(s, bx, by, bd, bd, fill="accent")
        a.text(s, bx, by, bd, bd, [(str(szam), {})], size=max(12, bd * 72 * 0.5), color="on_accent", font="torzs",
               bold=True, align=C, anchor=a.MID)
    return p


# ------------------------------------------------------------------ felsorolásjel (felsorolas A-E)

ROMAI = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def jel(s, i, x, y, pt, f, valtozat=None):
    """Felsorolásjel az i. elemhez (0-tól). x, y: a sor bal felső sarka; pt: a sor szövegének mérete.
    Visszaad: a jel utáni szöveg x-eltolása (hüvelyk)."""
    v = valtozat or a.T.v("felsorolas")
    sor = a.sormagassag(pt)
    m = 0.62 * pt / 20.0 * 0.5          # 20 pt-nél kb. 0.31"
    kozep_y = y + sor / 2.0
    if v == "A":
        a.oval(s, x, kozep_y - m / 2.0, m, m, fill=f.jel)
        pip = [(x + m * 0.27, kozep_y + m * 0.02), (x + m * 0.43, kozep_y + m * 0.19), (x + m * 0.74, kozep_y - m * 0.17)]
        sp = a.sokszog(s, pip, fill=None, line=ellen(f.jel), lw=max(1.5, pt / 10.0), zart=False)
        a.vonal_kerek(sp)
        return m + 0.22
    if v == "B":
        m2 = m * 1.15
        a.oval(s, x, kozep_y - m2 / 2.0, m2, m2, fill=f.jel)
        a.text(s, x, kozep_y - m2 / 2.0, m2, m2, [(str(i + 1), {})], size=pt * 0.62, color=ellen(f.jel), font="torzs",
               bold=True, align=C, anchor=a.MID)
        return m2 + 0.22
    if v == "C":
        a.rect(s, x, kozep_y - 0.035, 0.36, 0.07, fill=f.kiemel)
        return 0.58
    if v == "D":
        jn = a.T.motivum.get("jel") or next(iter((a.T.motivum.get("formak_svg") or {"": ""}).keys()), None)
        formak = a.T.motivum.get("formak_svg") or {}
        nev = "level" if "level" in formak else jn
        if nev and nev in formak:
            a.motivum(s, nev, x, kozep_y - m * 0.65, m * 1.1, m * 1.3, fill=f.jel, forgas=24)
            return m * 1.1 + 0.22
        a.oval(s, x, kozep_y - m / 3.0, m / 1.5, m / 1.5, fill=f.jel)
        return m + 0.2
    # E: római szám a címbetűvel
    a.text(s, x, y - 0.02, 0.8, sor + 0.1, [(ROMAI[i % 10] + ".", {})], size=pt * 1.08, color=f.szam, font="cim")
    return max(0.72, a.szelesseg("VIII.", pt * 1.08, "cim") * 0.75 + 0.18) if i >= 3 else 0.72


# ------------------------------------------------------------------ apróságok

def ellen(bg):
    """Olvasható szövegszín egy telt színen (a téma színeiből)."""
    if a.sotet(bg) or a.kontraszt(bg, "ink") < 4.5:
        return _valaszt(bg, ["card", "paper", "#FFFFFF"], 4.5)
    return _valaszt(bg, ["ink", "deep", "#111111"], 4.5)


def nyil(s, x, y, w, f, color=None):
    """Vízszintes nyíl (vonal + hegy) natív alakzatból, a folyamat lépései közé."""
    c = color or f.kiemel
    sp = a.sokszog(s, [(x, y), (x + w, y)], fill=None, line=c, lw=2.0, zart=False)
    a.vonal_kerek(sp)
    h = 0.11
    sp2 = a.sokszog(s, [(x + w - h, y - h), (x + w, y), (x + w - h, y + h)], fill=None, line=c, lw=2.0, zart=False)
    a.vonal_kerek(sp2)
    return sp


def pill(s, x, y, szoveg, f, fill=None, color=None, size=15, h=0.5, align_jobb=False):
    """Lekerekített címke (a webes gomb sarkaival)."""
    w = a.szelesseg(szoveg, size, "torzs", True) + 0.6
    xx = x - w if align_jobb else x
    r = a.T.r_gomb
    a.rect(s, xx, y, w, h, fill=fill or f.kiemel, shape=a.MSO_SHAPE.ROUNDED_RECTANGLE,
           rad=min(0.5, r / h) if r < 0.5 else 0.5)
    a.text(s, xx, y, w, h, [(szoveg, {})], size=size, color=color or ellen(fill or f.kiemel), font="torzs", bold=True,
           align=C, anchor=a.MID)
    return w
