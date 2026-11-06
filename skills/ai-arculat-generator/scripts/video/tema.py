# -*- coding: utf-8 -*-
"""A videós téma: a közös tokenek.json-ból a videó nyelvére fordítva (video-tema.json + video-tokens.css).

Mit csinál:
  - színszerepek: szöveg és kiemelés a felvételen és a kártyán/panelen, pill, akcentus, sötétítő réteg (scrim),
    figyelmeztető és „rendben” szín, haladássáv; minden párra kontrasztot számol (WCAG), és ahol kell, a márka
    saját színéből képez világosabb/sötétebb árnyalatot (új színt nem vezet be). Sötét szöveg akcentszínen: tiltott.
  - betűk: a felirathoz 800-900-as vastagság és ő/ű kell (a skill betűkatalógusából ellenőrizve); ha a márka
    betűi ezt nem tudják, a címbetűhöz illő pótbetűt választ a katalógusból, és ezt jelzi.
  - formák: a webes lekerekítés és árnyék videós léptékre (a 1080 px-es színpadot telefonon ~3x kisebben látjuk).
  - formátumok: 9:16 (Reels safe zone: felül 230, alul 420, jobbra 120 px) és 16:9.
"""
import colorsys
import json
import math
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
KATALOGUS = SKILL / "references" / "betuk.json"


# ---------------------------------------------------------------- színek
def rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexa(c):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in c)


def lum(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def kontraszt(a, b):
    la, lb = lum(a), lum(b)
    return round((max(la, lb) + 0.05) / (min(la, lb) + 0.05), 2)


def kever(a, b, t):
    """a és b keveréke: t=0 -> a, t=1 -> b"""
    A, B = rgb(a), rgb(b)
    return hexa([A[i] + (B[i] - A[i]) * t for i in range(3)])


def hsl(h):
    r, g, b = [v / 255 for v in rgb(h)]
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, s, l


def rgba(h, a):
    r, g, b = rgb(h)
    return f"rgba({r},{g},{b},{a})"


def kontrasztig(szin, hatter, cel, fele, lepes=0.04, max_t=0.85):
    """A szín árnyalata `fele` irányába, amíg a kontraszt a háttérrel eléri a célt. (szín, t, kontraszt)"""
    t = 0.0
    while t <= max_t + 1e-9:
        c = kever(szin, fele, t)
        if kontraszt(c, hatter) >= cel:
            return c, round(t, 2), kontraszt(c, hatter)
        t += lepes
    c = kever(szin, fele, max_t)
    return c, max_t, kontraszt(c, hatter)


# ---------------------------------------------------------------- betűk
def katalogus():
    try:
        d = json.loads(KATALOGUS.read_text(encoding="utf-8"))
        return {b["csalad"]: b for b in d.get("betuk", [])}
    except Exception:
        return {}


def sulyok(tengely):
    """'wght@400..900' -> (400, 900); 'wght@400;700' -> (400, 700); '' -> (400, 400)"""
    if not tengely:
        return 400, 400
    m = re.search(r"wght@([0-9.;,]+)", tengely)
    if not m:
        return 400, 400
    szamok = [int(float(x)) for x in re.findall(r"\d+(?:\.\d+)?", m.group(1)) if 100 <= float(x) <= 1000]
    return (min(szamok), max(szamok)) if szamok else (400, 400)


def google_css(csalad, tengely):
    fam = csalad.replace(" ", "+")
    return f"https://fonts.googleapis.com/css2?family={fam}{':' + tengely if tengely else ''}&display=swap"


def betu_adat(csalad, kat, tok_betu=None):
    b = kat.get(csalad) or {}
    mn, mx = sulyok(b.get("tengely", ""))
    if not b and tok_betu:
        sl = tok_betu.get("sulyok") or [tok_betu.get("suly", 400)]
        mn, mx = min(sl), max(sl)
        m = re.search(r"wght@(\d+)\.\.(\d+)", tok_betu.get("google_css", ""))
        if m:
            mn, mx = int(m.group(1)), int(m.group(2))
    return {"csalad": csalad, "min": mn, "max": mx, "ellenorizve": bool(b.get("ellenorizve", bool(tok_betu))),
            "osztaly": b.get("osztaly", ""), "ax": b.get("ax", {}),
            "google_css": (tok_betu or {}).get("google_css") or google_css(csalad, b.get("tengely", "")),
            "tengely": b.get("tengely", ""), "tiltott": b.get("tiltott", False), "katalogusban": bool(b)}


def nevelo(szo):
    """a vagy az a szó előtt (magánhangzóval kezdődő szó előtt az)."""
    return "az" if str(szo)[:1].lower() in "aáeéiíoóöőuúüű" else "a"


def potbetu(minta, kat, kerulendo=()):
    """Katalógusból: ő/ű-biztos, 800+ vastagság, nem tiltott, a minta formatengelyeihez legközelebbi."""
    jo = []
    for c, b in kat.items():
        if c in kerulendo or not b.get("ellenorizve") or b.get("tiltott") or b.get("kedvenc"):
            continue
        if sulyok(b.get("tengely", ""))[1] < 800 or b.get("osztaly") in ("kez", "script", "mono"):
            continue
        ax, max_ = b.get("ax", {}), minta.get("ax", {})
        tav = math.sqrt(sum((ax.get(k, .5) - max_.get(k, .5)) ** 2 for k in ("organikus", "puha", "harsany", "kortars", "kezi")))
        if b.get("osztaly") == minta.get("osztaly"):
            tav -= 0.25
        if "body" in (b.get("szerepek") or []):
            tav -= 0.1                       # a felirat sok szó: legyen jól olvasható
        jo.append((tav, c))
    jo.sort()
    return [c for _, c in jo[:4]]


def video_betuk(tok):
    kat = katalogus()
    B = tok.get("betuk") or {}
    disp = betu_adat((B.get("display") or {}).get("csalad", "Montserrat"), kat, B.get("display"))
    body = betu_adat((B.get("body") or {}).get("csalad", disp["csalad"]), kat, B.get("body"))
    megj = []
    # felirat: 800-900 kell
    felirat = None
    for jelolt, nev in ((body, "a szövegbetűd"), (disp, "a címbetűd")):
        if jelolt["max"] >= 800 and jelolt["ellenorizve"]:
            felirat = dict(jelolt, suly=900 if jelolt["max"] >= 900 else 800, forras=nev)
            break
    if not felirat:
        jel = potbetu(disp, kat, kerulendo=(disp["csalad"], body["csalad"]))
        cs = jel[0] if jel else "Archivo"
        felirat = dict(betu_adat(cs, kat), suly=900, forras="pótbetű", jeloltek=jel)
        megj.append(f"A betűid közül egyiknek sincs 800-900-as vastagsága, ezért a felirat pótbetűje: {cs} "
                    f"(a címbetűdhöz legközelebbi ő/ű-biztos betű a katalógusból; más jelöltek: {', '.join(jel[1:]) or 'nincs'}).")
    elif felirat["forras"] != "a szövegbetűd":
        megj.append(f"A felirat a címbetűdből megy ({felirat['csalad']} {felirat['suly']}).")
    # cím (hook, nagy kiemelés): a címbetű, ha legalább 700 és ő/ű-biztos
    if disp["max"] >= 700 and disp["ellenorizve"]:
        cim = dict(disp, suly=min(900, disp["max"]) if disp["max"] >= 800 else disp["max"], forras="a címbetűd")
        if disp["max"] < 800:
            megj.append(f"A címbetűd ({disp['csalad']}) legfeljebb {disp['max']}-as vastagságú: a nagy címek ezzel mennek, "
                        f"a felirat és a sűrű címkék {nevelo(felirat['csalad'])} {felirat['csalad']} {felirat['suly']}-as vágásával.")
    else:
        cim = dict(felirat, forras="a feliratbetű")
        megj.append(f"A címbetűd ({disp['csalad']}) videón nem elég erős (legfeljebb {disp['max']}), a címek is a "
                    f"{felirat['csalad']} betűvel mennek.")
    lab = B.get("label") or {}
    cimke = betu_adat(lab["csalad"], kat, lab) if lab.get("csalad") else dict(felirat)
    cimke["suly"] = min(cimke["max"], 800)
    if cimke.get("osztaly") == "mono" and cimke["max"] < 600:
        cimke["hasznalat"] = "csak kártyán, kis címkének; vékony, a felvételen nem olvasható"
    hand = B.get("hand") or None
    kez = betu_adat(hand["csalad"], kat, hand) if hand and hand.get("csalad") else None
    if kez:
        kez["suly"] = kez["max"]
        kez["hasznalat"] = "ritka dísz: aláírás, kézírásos megjegyzés; feliratnak soha"
    return {"felirat": felirat, "cim": cim, "cimke": cimke, "kez": kez, "megjegyzesek": megj,
            "ellenorzes": {"display": {"csalad": disp["csalad"], "max_suly": disp["max"], "o_u_biztos": disp["ellenorizve"]},
                           "body": {"csalad": body["csalad"], "max_suly": body["max"], "o_u_biztos": body["ellenorizve"]}}}


# ---------------------------------------------------------------- színszerepek
def szinszerepek(tok):
    S = tok.get("szinek") or {}
    X = tok.get("szinek_extra") or {}
    primary, accent = S.get("primary", "#1F3A5F"), S.get("accent", "#2BB39A")
    accent2 = S.get("accent2") or accent
    paper, card = S.get("paper", "#FFFFFF"), S.get("card", "#FFFFFF")
    ink, deep = S.get("ink", "#111111"), S.get("deep") or S.get("ink", "#111111")
    feher = "#FFFFFF"
    # sötétítés a felvételen: a mély márkaszín feketébe húzva
    scrim_alap = kever(deep, "#000000", 0.45)
    # kiemelés a felvételen (aktív szó, kiemelt szám): akcentus -> díszítő -> fő szín, világosítva a papír felé
    kiem_f, kiem_info = None, None
    for nev, c in (("accent", accent), ("accent2", accent2), ("primary", primary)):
        h, s, l = hsl(c)
        if s < 0.18:
            continue                          # szürkés szín nem kiemelés
        v, t, k = kontrasztig(c, scrim_alap, 6.0, paper, max_t=0.6)
        if k >= 4.5 and kontraszt(v, feher) >= 1.15:
            kiem_f, kiem_info = v, {"alap": nev, "vilagositas": t, "kontraszt_scrim": k}
            break
    if not kiem_f:
        kiem_f, kiem_info = kever(accent, paper, 0.5), {"alap": "accent", "vilagositas": 0.5, "kontraszt_scrim": None}
    # kiemelés kártyán: a fő szín, ha kell, sötétítve
    kiem_k, t_k, k_k = kontrasztig(primary, card, 4.5, ink)
    # pill: fő szín alapon fehér, ha olvasható, különben mély szín
    pill_bg = primary if kontraszt(feher, primary) >= 4.5 else (deep if kontraszt(feher, deep) >= 4.5 else primary)
    pill_fg = feher if kontraszt(feher, pill_bg) >= 4.5 else ink
    # akcent-pill: csak fehér betűvel (sötét szöveg akcentszínen tilos)
    ak_ok = kontraszt(feher, accent) >= 3.0
    # figyelmeztető (áthúzás, hibás érték) és „rendben” (pipa)
    def keres(tart, alap):
        for c in (accent, accent2, primary, deep):
            h, s, l = hsl(c)
            if tart(h) and s >= 0.3 and 0.2 <= l <= 0.65:
                return c, "a palettádból"
        return alap, "funkcionális szín (a palettádban nincs ilyen)"
    figy, figy_f = keres(lambda h: h >= 340 or h <= 28, "#C8372D")
    ok, ok_f = keres(lambda h: 85 <= h <= 170, "#1E8E5A")
    figy_k = kontrasztig(figy, card, 4.5, ink)[0]
    ok_k = kontrasztig(ok, card, 4.5, ink)[0]
    vonal = X.get("line") or kever(ink, card, 0.86)
    panel_b = X.get("tint") or kever(paper, primary, 0.08)
    R = {
        "szoveg_felvetelen": feher,
        "kiemeles_felvetelen": kiem_f,
        "szoveg_kartyan": ink,
        "masodlagos_kartyan": X.get("ink_2") or kever(ink, card, 0.35),
        "halvany_kartyan": X.get("ink_3") or kever(ink, card, 0.55),
        "kiemeles_kartyan": kiem_k,
        "kartya": card,
        "kartya_keret": vonal,
        "papir": paper,
        "panel_a": paper,
        "panel_b": panel_b,
        "pill_hatter": pill_bg,
        "pill_szoveg": pill_fg,
        "akcent": accent,
        "akcent_szoveg": feher if ak_ok else None,
        "akcent2": accent2,
        "mely": deep,
        "mely_szoveg": X.get("on_deep") or (feher if kontraszt(feher, deep) >= 4.5 else ink),
        "fo": primary,
        "fo_szoveg": X.get("on_primary") or pill_fg,
        "scrim": scrim_alap,
        "figyelmezteto": figy_k,
        "rendben": ok_k,
        "haladassav": [primary, accent],
    }
    T = [("szoveg_kartyan", "kartya"), ("masodlagos_kartyan", "kartya"), ("kiemeles_kartyan", "kartya"),
         ("pill_szoveg", "pill_hatter"), ("mely_szoveg", "mely"), ("figyelmezteto", "kartya"), ("rendben", "kartya"),
         ("kiemeles_felvetelen", "scrim"), ("szoveg_felvetelen", "scrim")]
    K = {}
    for a, b in T:
        if R.get(a) and R.get(b):
            k = kontraszt(R[a], R[b])
            K[f"{a} / {b}"] = {"arany": k, "ok": k >= 4.5}
    if R["akcent_szoveg"]:
        k = kontraszt(feher, accent)
        K["fehér / akcent"] = {"arany": k, "ok": k >= 3.0, "megjegyzes": "csak nagy, vastag szöveg (pill, címke)"}
    tilt = ["Sötét szöveg akcentszínen tilos: az akcentuson fehér betű, vagy az akcentus maga a szöveg sötét alapon."]
    if not ak_ok:
        tilt.append("Az akcentszín túl világos fehér szöveghez is: csak szövegszínként (sötét alapon), aláhúzásként vagy "
                    "díszként használd, pill háttérnek nem.")
    SZNEV = {"accent": "a kiemelő színed (akcentus)", "accent2": "a díszítő színed", "primary": "a fő színed"}
    jegyz = [f"A kiemelés a felvételen {SZNEV.get(kiem_info['alap'], kiem_info['alap'])} árnyalata ({kiem_f})"
             + (f", {round(kiem_info['vilagositas'] * 100)}%-kal világosítva, hogy a sötétített felvételen is olvasható legyen."
                if kiem_info["vilagositas"] else ".")]
    if figy_f.startswith("funkcionális"):
        jegyz.append(f"Figyelmeztető szín: {figy} ({figy_f}).")
    return R, K, tilt, jegyz, {"kiemeles": kiem_info}


# ---------------------------------------------------------------- formák, textúra
def formak(tok):
    F = tok.get("forma") or {}
    rk = float(F.get("r_kartya", 16) or 0)
    rg = float(F.get("r_gomb", 12) or 0)
    ink = (tok.get("szinek") or {}).get("ink", "#111111")
    arny = F.get("arnyek", "lagy")
    return {
        "r_kartya_px": int(max(4, min(48, round(rk * 3)))),
        "r_pill_px": 999 if rg >= 20 else int(max(8, min(40, round(rg * 3)))),
        "keret_px": int(max(0, round(float(F.get("keret_px", 0) or 0) * 2))),
        "arnyek_tipus": arny,
        "arnyek_kartya": {"lagy": "0 24px 60px rgba(0,0,0,.38)", "eros": f"12px 12px 0 {ink}",
                          "nincs": "0 10px 30px rgba(0,0,0,.28)"}.get(arny, "0 24px 60px rgba(0,0,0,.38)"),
        "arnyek_szoveg": "0 4px 12px rgba(0,0,0,.9), 0 8px 34px rgba(0,0,0,.7)",
        "forras": {"r_kartya": rk, "r_gomb": rg, "arnyek": arny, "keret_px": F.get("keret_px")},
    }


def elemlista(x):
    """A motivum.textura/dekor/hatar objektum vagy (keverésnél) lista: mindig listát ad."""
    if isinstance(x, list):
        return [e for e in x if isinstance(e, dict)]
    return [x] if isinstance(x, dict) and x else []


def nevek(x):
    return " + ".join(e.get("nev", "") for e in elemlista(x) if e.get("nev"))


def textura_tipus(tok):
    M = tok.get("motivum") or {}
    L = elemlista(M.get("textura"))
    t = L[0] if L else {}
    n = ((t.get("nev") or "") + " " + (t.get("leiras") or "")).lower()
    for kulcs, tip in (("szintvonal", "szintvonalak"), ("levél", "levelek"), ("levelek", "levelek"), ("herbár", "levelek"),
                       ("pötty", "pottyok"), ("pont", "pottyok"), ("rács", "racs"),
                       ("csík", "csikok"), ("vonal", "csikok"), ("papír", "papir"), ("vászon", "papir"), ("hullám", "hullam")):
        if kulcs in n:
            return tip, nevek(M.get("textura"))
    return "motivum", nevek(M.get("textura"))


# ---------------------------------------------------------------- a téma
FORMATUMOK = {
    "9x16": {"meret": [1080, 1920], "safe": {"felul": 230, "alul": 420, "jobbra": 120, "balra": 60},
             "oszlop": {"x": 60, "szel": 900}, "felirat_sav": [1140, 1310], "kartya_sav": [1340, 1510],
             "hirfolyam_4x5": [240, 1680],
             "megjegyzes": "Reels/TikTok/Shorts: fent a formátum felirata, lent a név és a leírás, jobbra a lájk-oszlop takar."},
    "16x9": {"meret": [1920, 1080], "safe": {"felul": 54, "alul": 80, "balra": 96, "jobbra": 96},
             "also_harmad": [770, 990],
             "megjegyzes": "YouTube: csak ha az ügyfél ott is gyárt (névkártya, fejezetkártya, szám, idézet, CTA)."},
}

SZABALYOK = [
    "A felvétel az idő legalább 85%-ában látszik; teljes takarás legfeljebb 2-szer, egyenként legfeljebb 3 mp.",
    "Amit a videóra teszel, az soha nem takarhatja az arcot, a szájat vagy a fejet; az információ a fej fölött vagy mellett van.",
    "Egy grafika minden kimondott mondatra, a kimondás pillanatára időzítve.",
    "A felső grafika soha nem ismétli szó szerint, ami épp elhangzik: kulcsszó, szám, ellentét vagy rövid saját megfogalmazás.",
    "Reels safe zone 9:16-on: felül 230, alul 420, jobbra 120 px üres.",
    "A felirat tökéletes magyar helyesírással és központozással jelenik meg; a nagy kiemelő szövegek végén nincs pont.",
    "Szoftver vagy platform a mondatban: a hivatalos logója jelenik meg.",
    "Sötét szöveg akcentszínen tilos.",
]


def tema(tok, valasztas=None, katalog=None):
    R, K, tilt, jegyz, info = szinszerepek(tok)
    B = video_betuk(tok)
    F = formak(tok)
    tex, tex_nev = textura_tipus(tok)
    M = tok.get("motivum") or {}
    fsvg = M.get("formak_svg") or {}
    tforma = M.get("jel")
    if tex == "levelek":
        tforma = next((k for k in fsvg if "lev" in k.lower() or "leaf" in k.lower()), tforma)
    T = {
        "verzio": 1,
        "marka": tok.get("marka"),
        "forras": {"tokenek": "tokenek.json", "tokenek_allapot": tok.get("allapot"), "marka_dns": tok.get("marka_dns")},
        "allapot": {"forras": "ajanlott", "jovahagyva": False, "video_verzio": 1},
        "szinek": {"alap": tok.get("szinek"), "szerepek": R, "kontraszt": K, "tiltasok": tilt, "megjegyzesek": jegyz},
        "betuk": B,
        "forma": F,
        "motivum": {"jel": M.get("jel"), "formak_svg": M.get("formak_svg") or {}, "textura": tex, "textura_nev": tex_nev, "textura_forma": tforma,
                    "dekor": nevek(M.get("dekor")) or None, "hatar": nevek(M.get("hatar")) or None,
                    "kevert": any(isinstance(M.get(k), list) and len(M.get(k)) > 1 for k in ("textura", "dekor", "hatar"))},
        "ikon": {k: (tok.get("ikon") or {}).get(k) for k in ("stilus_nev", "elotag", "technika", "mappa", "fajlok")},
        "ikon_szabaly": "Videón legalább 88 px (soron belüli 64 px-es ikon tilos); a felvételen csak a fehér sziluett-változat.",
        "foto": {k: (tok.get("foto") or {}).get(k) for k in ("kezeles", "leiras", "mappa", "valogatott")},
        "logo": tok.get("logo"),
        "hangnem": tok.get("hangnem"),
        "formatumok": FORMATUMOK,
        "szabalyok": SZABALYOK,
    }
    if valasztas:
        T["valasztas"] = valasztas
    return T


def css(T, komponens_css=""):
    """video-tokens.css: minden vágómotor ebből olvas (HyperFrames-kompozíció, kivágásos rétegek)."""
    R, B, F = T["szinek"]["szerepek"], T["betuk"], T["forma"]
    imp = []
    for k in ("felirat", "cim", "cimke", "kez"):
        b = B.get(k)
        if b and b.get("google_css") and b["google_css"] not in imp:
            imp.append(b["google_css"])
    sorok = [f"/* {T['marka']['nev']} · videós arculat (AI arculat-generátor). A fontok helyben: a/fonts/*.ttf, "
             f"@font-face-szel felülírható. */"]
    sorok += [f"@import url('{u}');" for u in imp]
    v = {
        "--v-fo": R["fo"], "--v-fo-szoveg": R["fo_szoveg"], "--v-akcent": R["akcent"], "--v-akcent2": R["akcent2"],
        "--v-mely": R["mely"], "--v-mely-szoveg": R["mely_szoveg"], "--v-papir": R["papir"], "--v-kartya": R["kartya"],
        "--v-keret": R["kartya_keret"], "--v-szoveg-kartyan": R["szoveg_kartyan"], "--v-masodlagos": R["masodlagos_kartyan"],
        "--v-halvany": R["halvany_kartyan"], "--v-kiemeles-kartyan": R["kiemeles_kartyan"],
        "--v-szoveg-felvetelen": R["szoveg_felvetelen"], "--v-kiemeles-felvetelen": R["kiemeles_felvetelen"],
        "--v-pill": R["pill_hatter"], "--v-pill-szoveg": R["pill_szoveg"],
        "--v-akcent-szoveg": R["akcent_szoveg"] or R["szoveg_kartyan"],
        "--v-scrim": rgba(R["scrim"], 0.78), "--v-scrim-eros": rgba(R["scrim"], 0.92),
        "--v-figyelmezteto": R["figyelmezteto"], "--v-rendben": R["rendben"],
        "--v-panel": f"linear-gradient(168deg,{R['panel_a']} 0%,{R['panel_b']} 100%)",
        "--v-haladassav": f"linear-gradient(90deg,{R['haladassav'][0]},{R['haladassav'][1]})",
        "--v-betu-felirat": f"'{B['felirat']['csalad']}', Arial, sans-serif", "--v-suly-felirat": str(B["felirat"]["suly"]),
        "--v-betu-cim": f"'{B['cim']['csalad']}', Georgia, serif" if B["cim"].get("osztaly") in ("serif", "slab") else f"'{B['cim']['csalad']}', Arial, sans-serif",
        "--v-suly-cim": str(B["cim"]["suly"]),
        "--v-betu-cimke": f"'{B['cimke']['csalad']}', monospace" if B["cimke"].get("osztaly") == "mono" else f"'{B['cimke']['csalad']}', Arial, sans-serif",
        "--v-betu-kez": f"'{B['kez']['csalad']}', cursive" if B.get("kez") else "inherit",
        "--v-r-kartya": f"{F['r_kartya_px']}px", "--v-r-pill": f"{F['r_pill_px']}px", "--v-keret-px": f"{F['keret_px']}px",
        "--v-arnyek-kartya": F["arnyek_kartya"], "--v-arnyek-szoveg": F["arnyek_szoveg"],
        "--v-safe-felul": "230px", "--v-safe-alul": "420px", "--v-safe-jobbra": "120px", "--v-oszlop-x": "60px", "--v-oszlop-szel": "900px",
        "--v-felirat-y": "1140px", "--v-kartya-y": "1340px",
    }
    sorok.append(":root{\n" + "\n".join(f"  {k}: {val};" for k, val in v.items()) + "\n}")
    if komponens_css:
        sorok.append(komponens_css)
    return "\n".join(sorok) + "\n"
