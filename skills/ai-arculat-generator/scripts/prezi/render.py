# -*- coding: utf-8 -*-
"""Előnézet a valódi .pptx-ből: LibreOffice -> PDF -> PNG/JPG, plusz két gépi ellenőrzés.

- A soffice-t Macen, Windowson és Linuxon is megkeresi (SOFFICE környezeti változóval felülírható).
- Minden export saját, eldobható LibreOffice-profilt kap: egy futó soffice mellett a LibreOffice csendben a régi,
  gyorsítótárazott PDF-et adná vissza.
- betu_ellenor(): a PDF-be ágyazott betűk között csak a téma betűi lehetnek (más név = a LibreOffice helyettesített,
  tehát a betű nincs telepítve).
- kilogas(): a dia szélén kilógó szöveg.
A PDF -> kép lépéshez PyMuPDF kell (pip install pymupdf); ha nincs, a pdftoppm (poppler) is jó.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def soffice():
    jeloltek = [os.environ.get("SOFFICE"), os.environ.get("LIBREOFFICE")]
    if sys.platform == "darwin":
        jeloltek += ["/Applications/LibreOffice.app/Contents/MacOS/soffice",
                     str(Path.home() / "Applications/LibreOffice.app/Contents/MacOS/soffice")]
    elif os.name == "nt":
        for env in ("PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMW6432"):
            if os.environ.get(env):
                jeloltek.append(os.path.join(os.environ[env], "LibreOffice", "program", "soffice.exe"))
        jeloltek += [r"C:\Program Files\LibreOffice\program\soffice.exe",
                     r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"]
    jeloltek += [shutil.which("soffice"), shutil.which("libreoffice"), shutil.which("soffice.exe")]
    for ut in jeloltek:
        if ut and os.path.exists(ut):
            return ut
    raise RuntimeError("Nem találom a LibreOffice-t (soffice). Telepítsd: https://www.libreoffice.org/download/ "
                       "(Mac: brew install --cask libreoffice), vagy add meg az útját a SOFFICE környezeti változóban.")


def pdf(pptx_ut, cel=None, csendes=True):
    """PDF a pptx-ből. cel: a PDF útja (alapból a pptx mellé, azonos néven)."""
    pptx_ut = Path(pptx_ut).resolve()
    cel = Path(cel) if cel else pptx_ut.with_suffix(".pdf")
    cel.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="prezi-pdf-") as tmp:
        profil = Path(tmp, "profil").as_uri()
        ki = Path(tmp, "ki")
        ki.mkdir()
        subprocess.run([soffice(), "-env:UserInstallation=" + profil, "--headless", "--norestore",
                        "--convert-to", "pdf", "--outdir", str(ki), str(pptx_ut)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900, check=False)
        kesz = ki / (pptx_ut.stem + ".pdf")
        if not kesz.exists() or kesz.stat().st_size == 0:
            raise RuntimeError("A PDF-export nem sikerült: %s" % pptx_ut)
        shutil.copyfile(kesz, cel)
    if not csendes:
        print("pdf:", cel)
    return cel


def kepek(pdf_ut, mappa, nevek=None, szel=1600, fmt="png", minoseg=86):
    """A PDF oldalai képként. nevek: oldalankénti fájlnév (kiterjesztés nélkül), alapból dia-01, dia-02...
    Visszaad: az elkészült képek útjai."""
    mappa = Path(mappa)
    mappa.mkdir(parents=True, exist_ok=True)
    utak = []
    try:
        import fitz  # PyMuPDF
        d = fitz.open(str(pdf_ut))
        for i, oldal in enumerate(d):
            nev = (nevek[i] if nevek and i < len(nevek) else "dia-%02d" % (i + 1)) + "." + fmt
            zoom = szel / oldal.rect.width
            pix = oldal.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            ut = mappa / nev
            if fmt in ("jpg", "jpeg"):
                pix.save(str(ut), jpg_quality=minoseg)
            else:
                pix.save(str(ut))
            utak.append(ut)
        return utak
    except ImportError:
        pass
    if not shutil.which("pdftoppm"):
        raise RuntimeError("A PDF -> kép lépéshez kell a PyMuPDF (pip install pymupdf) vagy a pdftoppm (poppler).")
    with tempfile.TemporaryDirectory(prefix="prezi-png-") as tmp:
        kapcs = ["-jpeg", "-jpegopt", "quality=%d" % minoseg] if fmt in ("jpg", "jpeg") else ["-png"]
        subprocess.run(["pdftoppm", "-scale-to-x", str(szel), "-scale-to-y", "-1"] + kapcs + [str(pdf_ut), tmp + "/o"],
                       check=True)
        for i, f in enumerate(sorted(Path(tmp).glob("o-*"))):
            nev = (nevek[i] if nevek and i < len(nevek) else "dia-%02d" % (i + 1)) + "." + fmt
            shutil.move(str(f), str(mappa / nev))
            utak.append(mappa / nev)
    return utak


def _alapnev(ps):
    return ps.split("+", 1)[1] if "+" in ps else ps


def betu_ellenor(pdf_ut, vart_ps):
    """[(oldal, betűnév)] azokról a betűkről, amelyek nem a téma betűi (helyettesítés). A „Symbol”, „Arial” és
    hasonló tartalék-betűk is hibának számítanak, kivéve a pipa-jelhez használtakat (OpenSymbol, DejaVu)."""
    try:
        import fitz
    except ImportError:
        return []
    vart = {v.replace(" ", "").lower() for v in vart_ps}
    turt = ("opensymbol", "dejavusans", "symbol")
    hibak = []
    d = fitz.open(str(pdf_ut))
    for i, oldal in enumerate(d, 1):
        for f in oldal.get_fonts():
            nev = _alapnev(f[3]).replace(" ", "")
            if nev.lower() in vart or any(nev.lower().startswith(t) for t in turt):
                continue
            hibak.append((i, nev))
    return hibak


def kilogas(pdf_ut, tures=0.0, margo_in=0.12):
    """[(oldal, szöveg)] a diáról kilógó, vagy a széléhez margo_in hüvelyknél közelebb érő szövegekről."""
    try:
        import fitz
    except ImportError:
        return []
    hibak = []
    d = fitz.open(str(pdf_ut))
    for i, oldal in enumerate(d, 1):
        W, H = oldal.rect.width, oldal.rect.height
        m = margo_in * 72
        for b in oldal.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for sp in l["spans"]:
                    if not sp["text"].strip() or sp["size"] >= 150:     # az óriás díszítő szám szándékosan kifut
                        continue
                    x0, y0, x1, y1 = sp["bbox"]
                    # a betű tényleges teste (a bbox a sormagasság, ezért a descender-ráhagyást levonjuk)
                    test_also = y1 - 0.2 * sp["size"]
                    if x0 < m - 1 or y0 < -1 or x1 > W - m + 1 or test_also > H - m:
                        hibak.append((i, sp["text"][:40]))
    return hibak


def atfedes(pdf_ut, arany=0.18):
    """[(oldal, szöveg1, szöveg2)]: egymásra csúszott szövegsorok (két sor betűteste fedi egymást)."""
    try:
        import fitz
    except ImportError:
        return []
    hibak = []
    d = fitz.open(str(pdf_ut))
    for i, oldal in enumerate(d, 1):
        sorok = []
        for b in oldal.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for sp in l["spans"]:
                    t = sp["text"].strip()
                    if not t or sp["size"] >= 150:
                        continue
                    x0, y0, x1, y1 = sp["bbox"]
                    sz = sp["size"]
                    # a betűtest: a sor tetejéről a felső ráhagyás és alul a descender nélkül
                    sorok.append((x0, y1 - 0.95 * sz, x1, y1 - 0.22 * sz, t))
        for j in range(len(sorok)):
            for k in range(j + 1, len(sorok)):
                a_, b_ = sorok[j], sorok[k]
                w = min(a_[2], b_[2]) - max(a_[0], b_[0])
                h = min(a_[3], b_[3]) - max(a_[1], b_[1])
                if w <= 2 or h <= 0:
                    continue
                kisebb = min((a_[3] - a_[1]), (b_[3] - b_[1]))
                if h > arany * kisebb:
                    hibak.append((i, a_[4][:30], b_[4][:30]))
    return hibak


def kis_szoveg(pdf_ut, torzs_ps, min_pt=19.5, min_szo=4):
    """[(oldal, méret, szöveg)]: a törzsbetűvel szedett, legalább min_szo szavas sorok, amelyek min_pt alatt vannak
    (a „legalább 20 pontos törzsszöveg” szabály; a kis címkék, nevek, gombok nem számítanak)."""
    try:
        import fitz
    except ImportError:
        return []
    torzs = {p.replace(" ", "").lower() for p in torzs_ps}
    hibak = []
    d = fitz.open(str(pdf_ut))
    for i, oldal in enumerate(d, 1):
        for b in oldal.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for sp in l["spans"]:
                    nev = _alapnev(sp["font"]).replace(" ", "").lower()
                    if nev in torzs and sp["size"] < min_pt and len(sp["text"].split()) >= min_szo:
                        hibak.append((i, round(sp["size"], 1), sp["text"][:40]))
    return hibak
