# -*- coding: utf-8 -*-
"""A prezi-választó: 10 kategória × 5 változat a valódi .pptx-ből renderelt képekkel, alul a 12 diás minta-deck.

Kimenet a munkamappa prezi/ mappájában:
  valtozatok.pptx, ritmus.pptx   a változatok forrása (ezekből renderelt képek: kepek/v-<kat>-<id>.jpg)
  minta-deck.pptx + .pdf         a 12 minta-dia a téma választásaival (képek: kepek/m-01.jpg..., minta-deck/dia-01.png...)
  prezi-toredek.html             az arculat-központ Prezentáció füle (<section id="fazis-prezi">, mentés:
                                 arculat/prezi-v<verzio>; a képek útja a munkamappához relatív: prezi/kepek/...)
  prezi-valaszto.html            önálló teszt-oldal ugyanezzel (a képek útja: kepek/...)
"""
import datetime
import html
import json
import shutil
import sys
import time
from pathlib import Path

import alap as a
import diak
import elemek as e
import katalogus as K
import render
import tema as tm

# melyik diatípuson mutatjuk az adott kategória változatait
ELONEZET = {"cimdia": "cimdia", "fejezet": "fejezet", "kiemeles": "felsorolas", "fotokeret": "bemutatkozo",
            "ikontarto": "folyamat", "felsorolas": "ket_hasab", "szamok": "szamok", "idezet": "idezet", "zaro": "zaro"}
RITMUS_DIAK = ["felsorolas", "fejezet", "kartyak", "szamok", "kerdes", "folyamat"]
MINTA_SORREND = ["cimdia", "fejezet", "felsorolas", "ket_hasab", "folyamat", "kartyak", "szamok", "idezet", "eset",
                 "kerdes", "kepernyokep", "zaro"]
MINTA_NEV = {"cimdia": "Címdia", "fejezet": "Fejezetdia", "felsorolas": "Felsorolás ikonnal", "ket_hasab": "Kéthasábos",
             "folyamat": "Folyamat 4 ikonnal", "kartyak": "Kártyák 2 × 2", "szamok": "Nagy számok",
             "idezet": "Idézet fotóval", "eset": "Esettanulmány", "kerdes": "Kérdés (ritmusdia)",
             "kepernyokep": "Képernyőkép magyarázattal", "zaro": "Záródia", "bemutatkozo": "Bemutatkozó"}


def _tartalom(t, tipus):
    for d in t.get("diak") or []:
        if d.get("tipus") == tipus:
            return d
    if (t.get(tipus) or {}).get("tipus") == tipus:
        return t[tipus]
    raise KeyError("A tartalom.json-ból hiányzik a(z) %s dia." % tipus)


def _ellenor(pdf, T, nev):
    vart = sorted({p for b in T.betu.values() for p in b.get("ps", [])})
    hibak = []
    for o, b in render.betu_ellenor(pdf, vart):
        hibak.append("%s %d. dia: idegen betű (%s), nincs telepítve a téma betűje?" % (nev, o, b))
    for o, t in render.kilogas(pdf):
        hibak.append("%s %d. dia: a szél közelében vagy kilóg: %s" % (nev, o, t))
    for o, t1, t2 in render.atfedes(pdf):
        hibak.append("%s %d. dia: egymásra csúszott szöveg: „%s” / „%s”" % (nev, o, t1, t2))
    for o, m, t in render.kis_szoveg(pdf, T.betu["torzs"].get("ps", [])):
        hibak.append("%s %d. dia: %.1f pontos törzsszöveg (legalább 20 kell): %s" % (nev, o, m, t))
    return hibak


def valtozat_deck(T, t, ki):
    """A 9 egydiás kategória × 5 változat egy pptx-ben (45 dia), a sorrend: KATEGORIAK, A-E."""
    prs = a.new_prs()
    nevek = []
    eredeti = dict(T.valasztas)
    try:
        for kat, _, _ in K.KATEGORIAK:
            if kat == "hatter":
                continue
            for vid, _, _ in K.VALTOZATOK[kat]:
                T.valasztas = dict(eredeti)
                T.valasztas[kat] = vid
                tipus = ELONEZET[kat]
                d = _tartalom(t, tipus)
                if kat in ("cimdia", "fejezet", "szamok", "idezet", "zaro"):
                    diak.dia(prs, d, vid)
                else:
                    diak.dia(prs, d)
                nevek.append("v-%s-%s" % (kat, vid))
    finally:
        T.valasztas = eredeti
    prs.save(str(ki))
    return nevek


def ritmus_deck(T, t, ki):
    prs = a.new_prs()
    eredeti = dict(T.valasztas)
    nevek = []
    try:
        for vid, _, _ in K.VALTOZATOK["hatter"]:
            T.valasztas = dict(eredeti)
            T.valasztas["hatter"] = vid
            for tipus in RITMUS_DIAK:
                diak.dia(prs, _tartalom(t, tipus))
                nevek.append("r-%s-%s" % (vid, tipus))
    finally:
        T.valasztas = eredeti
    prs.save(str(ki))
    return nevek


def minta_deck(T, t, ki):
    prs = a.new_prs()
    for tipus in MINTA_SORREND:
        diak.dia(prs, _tartalom(t, tipus))
    prs.save(str(ki))
    return ["m-%02d" % (i + 1) for i in range(len(MINTA_SORREND))]


def _tablo(kepek, ki, oszlop=3, szel=1280):
    """Ritmus-csík: a diák kicsiben, rácsban, egyetlen képen (a háttér-ritmus előnézete)."""
    from PIL import Image
    ims = [Image.open(k) for k in kepek]
    sorok = (len(ims) + oszlop - 1) // oszlop
    gap = 14
    w = (szel - gap * (oszlop + 1)) // oszlop
    h = int(w * 7.5 / 13.333)
    lap = Image.new("RGB", (szel, sorok * h + gap * (sorok + 1)), (214, 210, 200))
    for i, im in enumerate(ims):
        lap.paste(im.resize((w, h), Image.LANCZOS), (gap + (i % oszlop) * (w + gap), gap + (i // oszlop) * (h + gap)))
    lap.save(ki, "JPEG", quality=86)
    return ki


def epit(munkamappa, tartalom_ut=None, verzio=1, elozo=None, gyors=False):
    alap_mappa = Path(munkamappa).resolve()
    pm = alap_mappa / "prezi"
    tema_ut = pm / "prezi-tema.json"
    if not tema_ut.exists():
        raise SystemExit("Nincs prezi/prezi-tema.json. Előbb: python3 prezi.py tema <munkamappa>")
    T = tm.bekapcsol(tm.betolt(tema_ut))
    t = json.loads(Path(tartalom_ut or pm / "tartalom.json").read_text(encoding="utf-8"))
    kepek = pm / "kepek"
    if kepek.exists():
        for f in kepek.glob("*.jpg"):
            f.unlink()
    kepek.mkdir(parents=True, exist_ok=True)
    tmp = pm / "_render"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()
    hibak = []
    t0 = time.time()
    # 1) változatok
    nv = valtozat_deck(T, t, pm / "valtozatok.pptx")
    pdf = render.pdf(pm / "valtozatok.pptx", tmp / "valtozatok.pdf")
    hibak += _ellenor(pdf, T, "valtozatok")
    render.kepek(pdf, kepek, nevek=nv, szel=1280, fmt="jpg", minoseg=84)
    # 2) ritmus (háttér)
    nr = ritmus_deck(T, t, pm / "ritmus.pptx")
    pdf = render.pdf(pm / "ritmus.pptx", tmp / "ritmus.pdf")
    hibak += _ellenor(pdf, T, "ritmus")
    rk = render.kepek(pdf, tmp, nevek=nr, szel=640, fmt="jpg", minoseg=88)
    for vid, _, _ in K.VALTOZATOK["hatter"]:
        _tablo([p for p in rk if p.stem.startswith("r-%s-" % vid)], kepek / ("v-hatter-%s.jpg" % vid))
    # 3) minta-deck
    nm = minta_deck(T, t, pm / "minta-deck.pptx")
    mpdf = render.pdf(pm / "minta-deck.pptx", pm / "minta-deck.pdf")
    hibak += _ellenor(mpdf, T, "minta-deck")
    render.kepek(mpdf, kepek, nevek=nm, szel=1280, fmt="jpg", minoseg=86)
    render.kepek(mpdf, pm / "minta-deck", szel=1600, fmt="png")
    # 4) örökölt elemek képei (ikonok kicsiben, logó)
    from PIL import Image
    for nev, ut in list(T.ikonok.items())[:8]:
        im = Image.open(ut).convert("RGBA")
        im.thumbnail((160, 160))
        im.save(kepek / ("ikon-%s.png" % nev))
    if T.logo.get("szines"):
        shutil.copyfile(T.logo["szines"], kepek / "logo.png")
    shutil.rmtree(tmp, ignore_errors=True)
    # 5) töredék + önálló oldal
    adat = adatok(T, t, verzio, elozo)
    (pm / "prezi-toredek.html").write_text(toredek(adat, "prezi/"), encoding="utf-8")
    (pm / "prezi-valaszto.html").write_text(onallo(adat), encoding="utf-8")
    import leiras
    leiras.iras(alap_mappa)
    print("KÉSZ (%.0f mp): %s" % (time.time() - t0, pm))
    print("  változatok: %d kép · minta-deck: %d dia · töredék: prezi/prezi-toredek.html · teszt: prezi/prezi-valaszto.html"
          % (len(nv) + 5, len(nm)))
    if hibak:
        print("  ELLENŐRIZD (%d):" % len(hibak))
        for h in hibak:
            print("   -", h)
    else:
        print("  ellenőrzés: a betűk a téma betűi, nincs kilógó és egymásra csúszott szöveg")
    return hibak


# ------------------------------------------------------------------ adatok a felülethez

def adatok(T, t, verzio=1, elozo=None):
    d = T.d
    kat = []
    kar = getattr(T, "karakterek", None) or d.get("karakterek") or {}

    def kar_nev(kk):
        n = (kar.get(kk) or {}).get("nev") or K.KARAKTER_ALAPNEV[kk]
        return n[:1].upper() + n[1:]
    for k, nev, leiras in K.KATEGORIAK:
        opciok = []
        for forma, kk in K.karakter_sorrend(k):
            fn, fl = next((n, l) for i, n, l in K.valtozatok(k) if i == forma)
            opciok.append({"id": forma, "kar": kk, "karnev": kar_nev(kk), "nev": fn, "leiras": fl,
                           "kep": "kepek/v-%s-%s.jpg" % (k, forma)})
        kat.append({"kat": k, "nev": nev, "leiras": leiras, "ajanlott": (d.get("ajanlott") or {}).get(k, "A"),
                    "miert": (d.get("ajanlas_miert") or {}).get(k, ""), "opciok": opciok})
    bt = d.get("betuk") or {}
    orok = {
        "szinek": [(k, (d.get("szinek") or {}).get(k)) for k in ("primary", "accent", "accent2", "paper", "card", "ink", "deep")
                   if (d.get("szinek") or {}).get(k)],
        "betuk": [(n, bt[k]["csalad"], bt[k].get("suly_dian") or 400, bt[k].get("suly_web")) for k, n in
                  (("cim", "Cím"), ("torzs", "Szöveg"), ("kezi", "Kézírás"), ("cimke", "Címke")) if k in bt],
        "google": sorted({"https://fonts.googleapis.com/css2?family=%s:wght@400;700&display=swap" %
                          bt[k]["csalad"].replace(" ", "+") for k in bt}),
        "ikon": (d.get("ikon") or {}).get("stilus_nev") or "",
        "ikonok": ["kepek/ikon-%s.png" % n for n in list(T.ikonok)[:8]],
        "forma": "kártyasarok %.0f px · gombsarok %.0f px · árnyék: %s" % (
            (d.get("forma") or {}).get("r_kartya_px", 0), (d.get("forma") or {}).get("r_gomb_px", 0),
            {"nincs": "nincs", "lagy": "lágy", "eros": "erős"}.get((d.get("forma") or {}).get("arnyek"), "")),
        "foto": (d.get("fotokezeles") or {}).get("kezeles") or "",
        "motivum": ", ".join(x for x in [a.motivum_nevek(k, d.get("motivum") or {}) for k in ("textura", "dekor", "hatar")]
                             if x),
        "logo": "kepek/logo.png" if T.logo.get("szines") else None,
    }
    minta = [{"kep": "kepek/m-%02d.jpg" % (i + 1), "nev": MINTA_NEV[tp]} for i, tp in enumerate(MINTA_SORREND)]
    karakterek = [{"kar": kk, "nev": kar_nev(kk), "alapnev": K.KARAKTER_ALAPNEV[kk], "otlet": (kar.get(kk) or {}).get("otlet", ""),
                   "reszlet": (kar.get(kk) or {}).get("reszlet", "")} for kk in K.KARAKTEREK]
    return {"marka": {"nev": (d.get("marka") or {}).get("nev"), "slug": (d.get("marka") or {}).get("slug") or "marka"},
            "verzio": verzio, "dbnev": "prezi", "kategoriak": kat, "minta": minta, "orokolt": orok, "karakterek": karakterek,
            "web_jovahagyva": bool((d.get("forras") or {}).get("web_jovahagyva")),
            "elozo": elozo or None, "datum": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}


# ------------------------------------------------------------------ HTML

CSS = r"""
#fazis-prezi{--pz-bg:#f1efe8;--pz-ink:#1f1e1b;--pz-ink2:#4d4a43;--pz-ink3:#7a766b;--pz-line:#dcd8cc;--pz-card:#fff;--pz-acc:#191b18;--pz-ok:#2f7d4f;--pz-star:#c58a12;
 background:var(--pz-bg);color:var(--pz-ink);font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;min-height:80vh}
#fazis-prezi *{box-sizing:border-box}
#fazis-prezi .pz-in{max-width:1320px;margin:0 auto;padding:34px 22px 90px}
#fazis-prezi .pz-kick{display:inline-block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--pz-ink3);margin-bottom:6px}
#fazis-prezi h2{font-size:34px;line-height:1.1;margin:0 0 10px;letter-spacing:-.015em}
#fazis-prezi h3{font-size:22px;margin:0 0 4px;letter-spacing:-.01em}
#fazis-prezi p{line-height:1.55;color:var(--pz-ink2);margin:0 0 10px;max-width:78ch}
#fazis-prezi .pz-fej{display:grid;grid-template-columns:1.3fr 1fr;gap:28px;align-items:start;margin-bottom:22px}
#fazis-prezi .pz-lepesek{background:var(--pz-card);border:1px solid var(--pz-line);border-radius:16px;padding:16px 18px;font-size:14.5px;color:var(--pz-ink2)}
#fazis-prezi .pz-lepesek ol{margin:6px 0 0;padding-left:20px;line-height:1.6}
#fazis-prezi .pz-figy{background:#fbf3d9;border:1px solid #e9d7a0;border-radius:12px;padding:10px 14px;font-size:14px;margin:0 0 16px;color:#5a4a1a}
#fazis-prezi .pz-mentes{display:inline-block;font-size:12.5px;padding:4px 10px;border-radius:999px;background:#e8e4d8;color:var(--pz-ink2);margin-top:8px}
#fazis-prezi .pz-mentes.ok{background:#e1efe5;color:var(--pz-ok)}#fazis-prezi .pz-mentes.hiba{background:#f6dcd6;color:#9b2c1a}
#fazis-prezi .pz-orok{background:var(--pz-card);border:1px solid var(--pz-line);border-radius:18px;padding:18px 20px;margin:8px 0 28px}
#fazis-prezi .pz-orok-racs{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px 22px;margin-top:10px}
#fazis-prezi .pz-orok b{display:block;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--pz-ink3);margin-bottom:6px}
#fazis-prezi .pz-szinek{display:flex;gap:6px;flex-wrap:wrap}
#fazis-prezi .pz-szinek i{width:34px;height:34px;border-radius:8px;border:1px solid rgba(0,0,0,.12);display:inline-block}
#fazis-prezi .pz-betu{font-size:15px;line-height:1.5}
#fazis-prezi .pz-betu span{font-size:21px;margin-right:8px}
#fazis-prezi .pz-ikonok{display:flex;gap:6px;flex-wrap:wrap}
#fazis-prezi .pz-ikonok img{width:44px;height:44px;object-fit:contain;background:#faf8f2;border-radius:8px}
#fazis-prezi .pz-kat{background:var(--pz-card);border:1px solid var(--pz-line);border-radius:22px;padding:22px;margin:0 0 22px}
#fazis-prezi .pz-kat-fej{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:flex-start;margin-bottom:14px}
#fazis-prezi .pz-kat-fej .sz{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;background:var(--pz-acc);color:#fff;font-size:13px;font-weight:700;margin-right:8px;vertical-align:2px}
#fazis-prezi .pz-ajanl{font-size:13.5px;color:var(--pz-ink2);background:#f4f1e8;border-radius:10px;padding:8px 11px;max-width:520px}
#fazis-prezi .pz-ajanl b{color:var(--pz-ink)}
#fazis-prezi .pz-allapot{font-size:13px;font-weight:700;padding:5px 10px;border-radius:999px;background:#efece3;color:var(--pz-ink3);white-space:nowrap}
#fazis-prezi .pz-allapot.kesz{background:#fff3d6;color:#8a5d00}
#fazis-prezi .pz-nagy{position:relative;border-radius:14px;overflow:hidden;background:#e6e2d7;cursor:zoom-in;aspect-ratio:16/9}
#fazis-prezi .pz-nagy img{width:100%;height:100%;object-fit:contain;display:block}
#fazis-prezi .pz-nagy .cimke{position:absolute;left:12px;top:12px;background:rgba(25,27,24,.82);color:#fff;font-size:13px;padding:5px 10px;border-radius:8px}
#fazis-prezi .pz-opts{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-top:12px}
#fazis-prezi .pz-opt{border:2px solid var(--pz-line);border-radius:14px;padding:6px;background:#fff;display:flex;flex-direction:column;gap:6px}
#fazis-prezi .pz-opt.elo{border-color:var(--pz-acc)}
#fazis-prezi .pz-opt.veg{border-color:var(--pz-star);box-shadow:0 0 0 3px rgba(197,138,18,.18)}
#fazis-prezi .pz-opt button.kep{all:unset;cursor:pointer;display:block;border-radius:9px;overflow:hidden;aspect-ratio:16/9;background:#eee}
#fazis-prezi .pz-opt button.kep img{width:100%;height:100%;object-fit:cover;display:block}
#fazis-prezi .pz-opt .nev{font-size:13.5px;font-weight:700;line-height:1.25;padding:0 2px}
#fazis-prezi .pz-opt .nev em{font-style:normal;font-size:11px;font-weight:700;background:#e1efe5;color:var(--pz-ok);border-radius:6px;padding:1px 6px;margin-left:4px}
#fazis-prezi .pz-opt .forma{font-size:12.5px;color:var(--pz-ink2);padding:0 2px;margin-top:-4px}
#fazis-prezi .pz-karakterek{background:#fff;border:1px solid var(--pz-line);border-radius:18px;padding:16px 20px;margin:0 0 18px;font-size:14px;color:var(--pz-ink2)}
#fazis-prezi .pz-karakterek>b{color:var(--pz-ink)}
#fazis-prezi .pz-kar-racs{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-top:10px}
#fazis-prezi .pz-kar{background:#faf8f2;border-radius:12px;padding:10px 12px;line-height:1.35}
#fazis-prezi .pz-kar b{display:block;color:var(--pz-ink);font-size:14.5px}
#fazis-prezi .pz-kar small{display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--pz-ink3);margin:1px 0 4px}
#fazis-prezi .pz-kar span{font-size:12.5px}
@media (max-width:980px){#fazis-prezi .pz-kar-racs{grid-template-columns:repeat(2,minmax(0,1fr))}}
#fazis-prezi .pz-opt .leir{font-size:12.5px;color:var(--pz-ink3);line-height:1.35;padding:0 2px;flex:1}
#fazis-prezi .pz-opt .sor{display:flex;gap:6px}
#fazis-prezi .pz-gomb{font:600 12.5px/1 system-ui,-apple-system,'Segoe UI',sans-serif;border:1px solid var(--pz-line);background:#faf8f2;color:var(--pz-ink);border-radius:9px;padding:8px 9px;cursor:pointer;flex:1}
#fazis-prezi .pz-gomb:hover{background:#f1ede2}
#fazis-prezi .pz-gomb.csillag.on{background:var(--pz-star);border-color:var(--pz-star);color:#fff}
#fazis-prezi .pz-gomb.megj.van{background:#eef4ff;border-color:#b9cdf2}
#fazis-prezi textarea{width:100%;min-height:62px;border:1px solid var(--pz-line);border-radius:9px;padding:7px 9px;font:13.5px/1.4 system-ui,-apple-system,'Segoe UI',sans-serif;resize:vertical;background:#fffdf8;color:var(--pz-ink)}
#fazis-prezi .pz-opt textarea{display:none}#fazis-prezi .pz-opt.nyitott textarea{display:block}
#fazis-prezi .pz-elozo{font-size:12px;color:#5b5446;background:#f6f1e3;border-radius:8px;padding:5px 7px}
#fazis-prezi .pz-uj{display:flex;align-items:center;gap:8px;font-size:14px;margin-top:12px;color:var(--pz-ink2)}
#fazis-prezi .pz-uj input{width:18px;height:18px}
#fazis-prezi .pz-minta-racs{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:12px}
#fazis-prezi .pz-minta-racs figure{margin:0;background:#fff;border:1px solid var(--pz-line);border-radius:12px;padding:6px;cursor:zoom-in}
#fazis-prezi .pz-minta-racs img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:7px;display:block}
#fazis-prezi .pz-minta-racs figcaption{font-size:12.5px;color:var(--pz-ink2);padding:6px 2px 2px}
#fazis-prezi .pz-zaro{background:#fff;border:2px solid var(--pz-acc);border-radius:20px;padding:22px 24px;margin-top:26px}
#fazis-prezi .pz-fo{font:700 15px/1 system-ui,-apple-system,'Segoe UI',sans-serif;padding:14px 22px;border-radius:12px;border:0;background:var(--pz-acc);color:#fff;cursor:pointer}
#fazis-prezi .pz-fo.meg{background:#b5431c}
#fazis-prezi .pz-fo.kis{padding:11px 16px;font-size:14px}
#fazis-prezi .pz-uzenet{font-size:13.5px;color:var(--pz-ok);font-weight:600;margin:8px 0 0;min-height:1em}
#fazis-prezi .pz-fo.masod{background:#fff;color:var(--pz-acc);border:1px solid var(--pz-acc)}
#fazis-prezi .pz-gombsor{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:12px}
#fazis-prezi .pz-ok{display:none;color:var(--pz-ok);font-weight:700;margin-top:10px}
#fazis-prezi.pz-jovahagyva .pz-ok{display:block}#fazis-prezi.pz-jovahagyva #pz-jovahagy{display:none}
#fazis-prezi .pz-doboz{position:fixed;inset:0;background:rgba(15,16,14,.86);display:none;align-items:center;justify-content:center;z-index:200;padding:24px}
#fazis-prezi .pz-doboz.nyitva{display:flex}
#fazis-prezi .pz-doboz img{max-width:min(1500px,100%);max-height:86vh;border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.4);background:#fff}
#fazis-prezi .pz-doboz .zar,#fazis-prezi .pz-doboz .lap{position:absolute;background:rgba(255,255,255,.12);color:#fff;border:0;border-radius:999px;width:46px;height:46px;font-size:22px;cursor:pointer}
#fazis-prezi .pz-doboz .zar{top:18px;right:18px}#fazis-prezi .pz-doboz .lap.bal{left:18px}#fazis-prezi .pz-doboz .lap.jobb{right:18px}
#fazis-prezi .pz-doboz .felirat{position:absolute;bottom:16px;left:0;right:0;text-align:center;color:#eee;font-size:14px}
@media (max-width:1150px){#fazis-prezi .pz-opts{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:980px){#fazis-prezi .pz-fej{grid-template-columns:1fr}#fazis-prezi .pz-minta-racs{grid-template-columns:repeat(2,1fr)}}
@media (max-width:700px){#fazis-prezi .pz-opts{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:520px){#fazis-prezi .pz-in{padding:22px 14px 70px}#fazis-prezi h2{font-size:27px}#fazis-prezi .pz-opts{gap:8px}#fazis-prezi .pz-opt .leir{display:none}#fazis-prezi .pz-kat{padding:14px}}
"""

JS = r"""
(function(){
var R = document.getElementById('fazis-prezi'); if (!R) return;
var D = JSON.parse(R.querySelector('script.pz-adat').textContent);
var KEP = R.getAttribute('data-kepek') || '';
var KEY = 'prezi:' + D.marka.slug + ':v' + D.verzio;
var S = null;
try { S = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch(e) {}
function alapS(){ var s = {val:{}, alt:'', jovahagyva:false}; D.kategoriak.forEach(function(k){ s.val[k.kat] = {veg:null, elo:k.ajanlott, megj:{}, ujakat:false}; }); return s; }
if (!S || !S.val) S = alapS();
D.kategoriak.forEach(function(k){ if (!S.val[k.kat]) S.val[k.kat] = {veg:null, elo:k.ajanlott, megj:{}, ujakat:false}; });
var EL = (D.elozo && D.elozo.valasztas) || {};
function $$(s, r){ return Array.prototype.slice.call((r || R).querySelectorAll(s)); }
function esc(t){ return String(t == null ? '' : t).replace(/[<>&"]/g, function(c){ return {'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c]; }); }
function opc(k, id){ var kk = D.kategoriak.filter(function(x){ return x.kat === k; })[0]; return kk && kk.opciok.filter(function(o){ return o.id === id; })[0]; }
function rajzol(){
  D.kategoriak.forEach(function(k){
    var box = R.querySelector('.pz-kat[data-kat="' + k.kat + '"]'); if (!box) return;
    var v = S.val[k.kat], o = opc(k.kat, v.elo) || k.opciok[0];
    var img = box.querySelector('.pz-nagy img'); if (img.getAttribute('src') !== KEP + o.kep) img.setAttribute('src', KEP + o.kep);
    box.querySelector('.pz-nagy .cimke').textContent = (o.karnev || o.id) + ' · ' + o.nev + (v.veg === o.id ? '  ★ végleges' : '');
    $$('.pz-opt', box).forEach(function(el){
      var id = el.getAttribute('data-id');
      el.classList.toggle('elo', id === v.elo); el.classList.toggle('veg', id === v.veg);
      var cs = el.querySelector('.csillag'); cs.classList.toggle('on', id === v.veg); cs.textContent = id === v.veg ? '★ Végleges' : '☆ Ez legyen';
      var t = el.querySelector('textarea'); if (document.activeElement !== t) t.value = (v.megj || {})[id] || '';
      el.querySelector('.megj').classList.toggle('van', !!((v.megj || {})[id] || '').trim());
    });
    box.querySelector('.pz-uj input').checked = !!v.ujakat;
    var all = box.querySelector('.pz-allapot');
    var ov = opc(k.kat, v.veg), oa = opc(k.kat, k.ajanlott);
    all.textContent = v.veg ? ('Végleges: ' + (ov ? ov.karnev : v.veg)) : ('Ajánlott: ' + (oa ? oa.karnev : k.ajanlott));
    all.classList.toggle('kesz', !!v.veg);
  });
  var alt = R.querySelector('#pz-alt'); if (document.activeElement !== alt) alt.value = S.alt || '';
  R.classList.toggle('pz-jovahagyva', !!S.jovahagyva);
}
function exportAdat(){
  var val = {};
  D.kategoriak.forEach(function(k){ var v = S.val[k.kat];
    var m = {}; Object.keys(v.megj || {}).forEach(function(id){ if ((v.megj[id] || '').trim()) m[id] = v.megj[id].trim(); });
    var vo = opc(k.kat, v.veg);
    val[k.kat] = {vegleges: v.veg, vegleges_karakter: vo ? vo.kar : null, elonezet: v.elo, ajanlott: k.ajanlott, megjegyzesek: m, ujakat: !!v.ujakat, opciok: k.opciok.map(function(o){ return o.id; })}; });
  var json = {marka: D.marka.slug, fazis: 'prezi', verzio: D.verzio, datum: new Date().toISOString(), valasztas: val, altalanos: (S.alt || '').trim(), jovahagyva: S.jovahagyva || false};
  var sor = ['PREZENTÁCIÓS ARCULAT · ' + (D.marka.nev || '') + ' · ' + D.verzio + '. kör', ''];
  D.kategoriak.forEach(function(k){ var v = val[k.kat], o = opc(k.kat, v.vegleges || v.ajanlott);
    sor.push(k.nev + ': ' + (v.vegleges ? '★ ' : 'ajánlott ') + (o ? o.karnev + ' (' + o.id + ' · ' + o.nev + ')' : '-') + (v.ujakat ? ' · KÉR ÚJAKAT' : ''));
    Object.keys(v.megjegyzesek).forEach(function(id){ var oo = opc(k.kat, id); sor.push('   megjegyzés ' + (oo ? oo.karnev + ' (' + id + ' · ' + oo.nev + ')' : id) + ': ' + v.megjegyzesek[id]); }); });
  if (json.altalanos) { sor.push(''); sor.push('Általános megjegyzés: ' + json.altalanos); }
  sor.push(''); sor.push(json.jovahagyva ? 'JÓVÁHAGYVA: ' + json.jovahagyva : 'Még nincs jóváhagyva.');
  return {json: json, szoveg: sor.join('\n')};
}
var DBDOC = null, dbT = null, dbFut = false, dbUjra = false, dbKesz = false, indult = false;
function jel(c, t){ var m = R.querySelector('.pz-mentes'); if (m) { m.className = 'pz-mentes ' + (c || ''); m.textContent = t; } }
function ment(){ try { localStorage.setItem(KEY, JSON.stringify(S)); } catch(e) {} if (!DBDOC) jel('', 'mentve ebben a böngészőben'); dbMent(); }
function dbMent(){
  if (!DBDOC || !dbKesz) return; clearTimeout(dbT);
  dbT = setTimeout(function(){
    if (dbFut) { dbUjra = true; return; }
    dbFut = true; jel('', 'mentés…');
    var e = exportAdat();
    DBDOC.set({allapot: JSON.stringify(S), gepi: JSON.stringify(e.json), szoveg: e.szoveg, frissitve: new Date().toISOString(), verzio: D.verzio, jovahagyva: S.jovahagyva || false})
      .then(function(){ dbFut = false; jel('ok', '✓ mentve a Claude-nál'); if (dbUjra) { dbUjra = false; dbMent(); } },
            function(err){ dbFut = false; jel('hiba', 'a mentés nem sikerült (' + ((err && err.code) || '?') + ')'); });
  }, 600);
}
function init(db){
  if (indult) return; indult = true;
  if (!db) { jel('', 'helyi mentés (ebben a böngészőben); a végén: Visszajelzés másolása'); return; }
  try { DBDOC = db.doc('arculat/' + (D.dbnev || 'prezi') + '-v' + D.verzio); } catch(e) { DBDOC = null; return; }
  jel('', 'kapcsolódás…');
  DBDOC.get().then(function(snap){
    var d = snap.exists ? snap.data() : null;
    if (d && d.allapot) { try { var r = JSON.parse(d.allapot); if (r && r.val) { S = r; D.kategoriak.forEach(function(k){ if (!S.val[k.kat]) S.val[k.kat] = {veg:null, elo:k.ajanlott, megj:{}, ujakat:false}; }); rajzol(); } } catch(e) {} }
    dbKesz = true; jel('ok', '✓ a döntéseid a Claude-nál mentődnek');
    if (!d) dbMent();
  }, function(){ jel('hiba', 'az adatbázis nem elérhető (marad a böngésző)'); });
}
window.FAZISOK = window.FAZISOK || {};
window.FAZISOK.prezi = {init: init, allapot: function(){ return S; }, export: exportAdat};
/* előző kör megjegyzései */
D.kategoriak.forEach(function(k){
  var e = EL[k.kat]; if (!e) return;
  var box = R.querySelector('.pz-kat[data-kat="' + k.kat + '"]'); if (!box) return;
  Object.keys(e.megjegyzesek || {}).forEach(function(id){
    var o = box.querySelector('.pz-opt[data-id="' + id + '"] textarea'); if (!o) return;
    var p = document.createElement('p'); p.className = 'pz-elozo'; p.innerHTML = '<b>Előző kör:</b> ' + esc(e.megjegyzesek[id]);
    o.parentNode.insertBefore(p, o);
  });
});
/* események */
$$('.pz-kat[data-kat]').forEach(function(box){
  var k = box.getAttribute('data-kat');
  $$('.pz-opt', box).forEach(function(el){
    var id = el.getAttribute('data-id');
    el.querySelector('button.kep').addEventListener('click', function(){ S.val[k].elo = id; ment(); rajzol(); });
    el.querySelector('.csillag').addEventListener('click', function(){ S.val[k].veg = (S.val[k].veg === id ? null : id); S.val[k].elo = id; ment(); rajzol(); });
    el.querySelector('.megj').addEventListener('click', function(){ el.classList.toggle('nyitott'); if (el.classList.contains('nyitott')) el.querySelector('textarea').focus(); });
    var t = el.querySelector('textarea'), tt;
    t.addEventListener('input', function(){ S.val[k].megj = S.val[k].megj || {}; S.val[k].megj[id] = t.value; clearTimeout(tt); tt = setTimeout(function(){ ment(); rajzol(); }, 400); });
  });
  box.querySelector('.pz-uj input').addEventListener('change', function(ev){ S.val[k].ujakat = ev.target.checked; ment(); });
  box.querySelector('.pz-nagy').addEventListener('click', function(){ var o = opc(k, S.val[k].elo); nyit([{kep: o.kep, nev: (o.karnev || o.id) + ' · ' + o.nev}], 0); });
});
/* ajánlottak elfogadása: ahol még nincs végleges, ott az ajánlott lesz az (és az előnézet is arra áll) */
R.querySelector('#pz-ajanlott').addEventListener('click', function(){
  var n = 0;
  D.kategoriak.forEach(function(k){ var v = S.val[k.kat]; if (!v.veg) { v.veg = k.ajanlott; v.elo = k.ajanlott; n++; } });
  ment(); rajzol();
  var u = R.querySelector('#pz-ajanlott-uzenet');
  if (u) u.textContent = n ? ('✓ ' + n + ' kategóriában az ajánlott lett a végleges. Ha kész vagy, legalul hagyd jóvá.') : 'Már mindenhol van végleges.';
});
var alt = R.querySelector('#pz-alt'), at;
alt.addEventListener('input', function(){ S.alt = alt.value; clearTimeout(at); at = setTimeout(ment, 400); });
/* nagyító */
var DB_ = R.querySelector('.pz-doboz'), LISTA = [], IDX = 0;
function mutat(){ DB_.querySelector('img').src = KEP + LISTA[IDX].kep; DB_.querySelector('.felirat').textContent = LISTA[IDX].nev + (LISTA.length > 1 ? '  (' + (IDX + 1) + '/' + LISTA.length + ')' : '');
  $$('.lap', DB_).forEach(function(b){ b.style.display = LISTA.length > 1 ? '' : 'none'; }); }
function nyit(l, i){ LISTA = l; IDX = i; mutat(); DB_.classList.add('nyitva'); }
DB_.addEventListener('click', function(ev){ if (ev.target === DB_ || ev.target.classList.contains('zar')) DB_.classList.remove('nyitva'); });
DB_.querySelector('.bal').addEventListener('click', function(ev){ ev.stopPropagation(); IDX = (IDX + LISTA.length - 1) % LISTA.length; mutat(); });
DB_.querySelector('.jobb').addEventListener('click', function(ev){ ev.stopPropagation(); IDX = (IDX + 1) % LISTA.length; mutat(); });
document.addEventListener('keydown', function(ev){ if (!DB_.classList.contains('nyitva')) return;
  if (ev.key === 'Escape') DB_.classList.remove('nyitva'); if (ev.key === 'ArrowLeft') DB_.querySelector('.bal').click(); if (ev.key === 'ArrowRight') DB_.querySelector('.jobb').click(); });
$$('.pz-minta-racs figure').forEach(function(f, i){ f.addEventListener('click', function(){ nyit(D.minta, i); }); });
/* jóváhagyás: két kattintás (a confirm() artifactban nem működik) */
var gomb = R.querySelector('#pz-jovahagy'), elso = false, gt;
gomb.addEventListener('click', function(){
  if (!elso) { elso = true; gomb.textContent = 'Biztosan? Kattints még egyszer a jóváhagyáshoz'; gomb.classList.add('meg');
    gt = setTimeout(function(){ elso = false; gomb.textContent = 'Jóváhagyom a prezentációs arculatot'; gomb.classList.remove('meg'); }, 4500); return; }
  clearTimeout(gt); elso = false; gomb.classList.remove('meg'); gomb.textContent = 'Jóváhagyom a prezentációs arculatot';
  S.jovahagyva = new Date().toISOString(); ment(); rajzol();
  if (window.HUB && window.HUB.fazis) window.HUB.fazis('prezi', 'jovahagyva');
});
R.querySelector('#pz-visszavon').addEventListener('click', function(){ S.jovahagyva = false; ment(); rajzol(); if (window.HUB && window.HUB.fazis) window.HUB.fazis('prezi', 'dontes'); });
R.querySelector('#pz-masol').addEventListener('click', function(){
  var e = exportAdat(), t = e.szoveg + '\n\nGÉPI ADAT (ne módosítsd):\n' + JSON.stringify(e.json);
  function kesz(){ jel('ok', '✓ kimásolva: illeszd be a Claude-nak'); }
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(kesz, fallback); else fallback();
  function fallback(){ var ta = document.createElement('textarea'); ta.value = t; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); kesz(); } catch(x) {} document.body.removeChild(ta); }
});
rajzol();
if (!(window.claude && typeof window.claude.use === 'function') && !window.HUB) init(null);
})();
"""


def _section(adat, kepek_elotag):
    esc = html.escape
    o = adat["orokolt"]
    szinek = "".join('<i title="%s %s" style="background:%s"></i>' % (esc(k), esc(v), esc(v)) for k, v in o["szinek"])
    betuk = "".join('<div style="margin-bottom:6px"><span style="font-family:\'%s\';font-weight:%s">Árvíztűrő</span><br>'
                    '<small style="color:#7a766b">%s: %s, %s-as</small></div>' % (esc(cs), sd, esc(n), esc(cs), sd)
                    for n, cs, sd, sw in o["betuk"])
    ikonok = "".join('<img src="%s%s" alt="">' % (kepek_elotag, esc(p)) for p in o["ikonok"])
    logo = ('<img src="%s%s" alt="logó" style="max-width:150px;max-height:44px;object-fit:contain">' % (kepek_elotag, o["logo"])
            if o.get("logo") else "")
    figy = ("" if adat.get("web_jovahagyva") else
            '<div class="pz-figy">Előnézet: a webes arculat még nincs jóváhagyva, ezért ezek a diák az ajánlott webes '
            'elemekből készültek. A webes jóváhagyás után a Claude a végleges színekkel és betűkkel újraépíti őket.</div>')
    katok = []
    for i, k in enumerate(adat["kategoriak"], 1):
        aj = k["ajanlott"]
        ajo = next((x for x in k["opciok"] if x["id"] == aj), k["opciok"][0])
        aj_nev = "%s · %s" % (ajo.get("karnev", aj), ajo["nev"])
        opts = []
        for x in k["opciok"]:
            opts.append(
                '<div class="pz-opt" data-id="%s"><button class="kep" type="button" title="Megnézem">'
                '<img loading="lazy" src="%s%s" alt="%s"></button><div class="nev">%s%s</div><div class="forma">%s</div>'
                '<div class="leir">%s</div><div class="sor"><button class="pz-gomb csillag" type="button">☆ Ez legyen</button>'
                '<button class="pz-gomb megj" type="button">Megjegyzés</button></div>'
                '<textarea placeholder="Mi tetszik, mi nem? Írd le úgy, ahogy egy kollégának mondanád."></textarea></div>'
                % (esc(x["id"]), kepek_elotag, esc(x["kep"]), esc(x.get("karnev", x["nev"])), esc(x.get("karnev", x["id"])),
                   '<em>ajánlott</em>' if x["id"] == aj else "", esc(x["nev"]), esc(x["leiras"])))
        katok.append(
            '<div class="pz-kat" data-kat="%s" id="pz-kat-%s"><div class="pz-kat-fej"><div><h3><span class="sz">%d</span>%s</h3>'
            '<p>%s</p></div><div><span class="pz-allapot">Ajánlott: %s</span></div></div>'
            '<div class="pz-ajanl"><b>Ajánlott: %s.</b> %s</div>'
            '<div class="pz-nagy" style="margin-top:12px" title="Nagyítás"><img alt="" src="%s%s"><span class="cimke"></span></div>'
            '<div class="pz-opts">%s</div>'
            '<label class="pz-uj"><input type="checkbox"> Egyik sem az igazi, kérek újakat ebben a kategóriában</label></div>'
            % (esc(k["kat"]), esc(k["kat"]), i, esc(k["nev"]), esc(k["leiras"]), esc(ajo.get("karnev", aj)), esc(aj_nev),
               esc(k["miert"]), kepek_elotag, esc(ajo["kep"]), "".join(opts)))
    minta = "".join('<figure><img loading="lazy" src="%s%s" alt="%s"><figcaption>%d. %s</figcaption></figure>' % (
        kepek_elotag, esc(m["kep"]), esc(m["nev"]), i, esc(m["nev"])) for i, m in enumerate(adat["minta"], 1))
    fontok = "".join('<link rel="stylesheet" href="%s">' % esc(u) for u in o["google"])
    karakterek = "".join('<div class="pz-kar"><b>%s</b><small>%s</small><span>%s</span></div>' % (
        esc(x["nev"]), esc(x["alapnev"]), esc(x["otlet"])) for x in adat.get("karakterek") or [])
    adat_js = json.dumps(adat, ensure_ascii=False).replace("</", "<\\/")
    return """<section id="fazis-prezi" data-kepek="%(elo)s">%(fontok)s<div class="pz-in">
<div class="pz-fej"><div><span class="pz-kick">2. fázis</span><h2>%(nev)s · prezentációs arculat</h2>
<p>A webes arculatod színei, betűi, ikonjai és formái már benne vannak minden dián. Itt azt választod ki, milyen legyen a
prezentációid szerkezete: 10 kérdés, mindegyikre 5 válasz, mind a saját tartalmaddal, valódi PowerPoint-diákon.</p>
<div class="pz-gombsor" style="margin-top:12px"><button class="pz-fo kis" id="pz-ajanlott" type="button" title="Ahol még nincs végleges, ott az ajánlott változat lesz a végleges">✓ Ajánlottak elfogadása</button>
<span class="pz-mentes">betöltés…</span></div><p class="pz-uzenet" id="pz-ajanlott-uzenet"></p></div>
<div class="pz-lepesek"><b>Így válassz</b><ol><li>Kattints egy kis képre: fent nagyban megjelenik (a nagy képre kattintva nagyítható).</li>
<li><b>☆ Ez legyen</b>: így jelölöd a véglegeset (bármikor átjelölheted).</li><li><b>Megjegyzés</b>: írd meg, mit változtatnál; ha egyik sem jó, pipáld be a „kérek újakat” sort.</li>
<li>Legalul a 12 diás minta-deck, a végén pedig <b>Jóváhagyom</b>. Ahol nincs végleges, ott az ajánlott számít.</li></ol></div></div>
%(figy)s
<div class="pz-karakterek"><b>Az 5 változat a márkád 5 karaktere</b> (ugyanazok, mint a webes arculatnál): minden
kategóriában ugyanebben a sorrendben, mindegyik a hozzá illő formával és a saját részletével.<div class="pz-kar-racs">%(karakterek)s</div></div>
<div class="pz-orok"><b style="font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:#7a766b">Örökölt elemek (a jóváhagyott webes arculatból, itt nem kell választani)</b>
<div class="pz-orok-racs"><div><b>Színek</b><div class="pz-szinek">%(szinek)s</div></div><div><b>Betűk</b><div class="pz-betu">%(betuk)s</div></div>
<div><b>Ikonok · %(ikon)s</b><div class="pz-ikonok">%(ikonok)s</div></div><div><b>Formák</b><div class="pz-betu">%(forma)s</div></div>
<div><b>Fotókezelés</b><div class="pz-betu">%(foto)s</div></div><div><b>Motívum</b><div class="pz-betu">%(motivum)s</div></div>
<div><b>Logó · mindig jobbra lent</b>%(logo)s</div><div><b>Rögzített szabályok</b><div class="pz-betu">16:9 · a szöveg legalább 20 pontos · natív, szerkeszthető PowerPoint</div></div></div></div>
%(katok)s
<div class="pz-kat"><div class="pz-kat-fej"><div><h3>A 12 diás minta-deck</h3><p>A saját tartalmaddal, az ajánlott (és az általad jelölt) elemekkel. Ha
befejezted a választást, a Claude másodpercek alatt újraépíti a véglegesekkel. Kattints egy diára a nagyításhoz.</p></div></div>
<div class="pz-minta-racs">%(minta)s</div></div>
<div class="pz-kat"><h3>Általános megjegyzés</h3><p>Bármi, ami az egész prezentációra vonatkozik (pl. „több fotó legyen”, „a fejezetdiák legyenek nyugodtabbak”).</p>
<textarea id="pz-alt" placeholder="Ide írhatsz bármit a prezentációs arculatról."></textarea></div>
<div class="pz-zaro"><h3>Kész a prezentációs arculat?</h3><p>Ha mindenhol megvan a végleges (★), vagy elfogadod az ajánlottakat, hagyd jóvá. Ebből készül a
végleges minta-deck (.pptx és PDF) és a prezentációs arculat leírása, amiből a Claude minden következő prezidet építi.</p>
<div class="pz-gombsor"><button class="pz-fo" id="pz-jovahagy" type="button">Jóváhagyom a prezentációs arculatot</button>
<button class="pz-fo masod" id="pz-masol" type="button">Visszajelzés másolása</button></div>
<p class="pz-ok">✓ A prezentációs arculat jóvá van hagyva. Szólj a Claude-nak: „jöhet a videó”. <button class="pz-gomb" id="pz-visszavon" type="button" style="flex:none">Visszavonom</button></p></div>
</div>
<div class="pz-doboz" role="dialog" aria-label="Nagyítás"><img alt=""><button class="zar" type="button" aria-label="Bezárás">×</button>
<button class="lap bal" type="button" aria-label="Előző">‹</button><button class="lap jobb" type="button" aria-label="Következő">›</button><div class="felirat"></div></div>
<script type="application/json" class="pz-adat">%(adat)s</script>
</section>""" % {"elo": kepek_elotag, "fontok": fontok, "nev": esc(adat["marka"]["nev"] or ""), "figy": figy,
                 "szinek": szinek, "betuk": betuk, "ikon": esc(o["ikon"]), "ikonok": ikonok, "forma": esc(o["forma"]),
                 "foto": esc(o["foto"]), "motivum": esc(o["motivum"]), "logo": logo, "katok": "".join(katok),
                 "minta": minta, "adat": adat_js, "karakterek": karakterek}


def toredek(adat, kepek_elotag="prezi/"):
    """Az arculat-központba illeszthető töredék (a képek útja a munkamappához relatív)."""
    return "<style>%s</style>\n%s\n<script>%s</script>\n" % (CSS, _section(adat, kepek_elotag), JS)


def onallo(adat):
    """Önálló teszt-oldal (a prezi/ mappában; a képek útja: kepek/...). Artifactként is publikálható
    (capabilities: {"db": {}}); akkor ugyanúgy az arculat/prezi-v<verzio> dokumentumba ment."""
    return ("<!doctype html><html lang=\"hu\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,"
            "initial-scale=1\"><title>%s · prezi-választó</title><style>body{margin:0;background:#f1efe8}</style></head><body>"
            % html.escape(adat["marka"]["nev"] or "") + toredek(adat, "") +
            "<script>(function(){var f=window.FAZISOK&&window.FAZISOK.prezi;if(!f)return;"
            "if(window.claude&&typeof window.claude.use==='function'){window.claude.use('db').then(function(db){f.init(db||null);},"
            "function(){f.init(null);});}else{f.init(null);}})();</script></body></html>")
