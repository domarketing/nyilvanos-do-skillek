# -*- coding: utf-8 -*-
"""A videó fázis lezárása: állóképek, végleges téma, VIDEO-ARCULAT.md, márka-rész a tag vágó skilljéhez."""
import json
import os
import platform
import shutil
import subprocess
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import katalogus as K
import tema as TM

# a változatok kulcspillanata (mp), amikor minden elem a képen van
KULCSIDO = {"stilus": 2.6, "felirat": 2.6, "kartya": 2.6, "mozgas": 2.6, "hangulat": 2.6, "hook": 1.7, "tema": 2.0,
            "nev": 1.7, "fejezet": {"takeover": 0.95, "pill": 1.2, "szam": 1.3}, "zaro": 1.9, "nyito": 0.6}


def chrome_ut():
    jel = [os.environ.get("CHROME", "")]
    if platform.system() == "Darwin":
        jel += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium"]
    elif platform.system() == "Windows":
        for b in (os.environ.get("PROGRAMFILES", ""), os.environ.get("PROGRAMFILES(X86)", ""), os.environ.get("LOCALAPPDATA", "")):
            jel.append(os.path.join(b, "Google", "Chrome", "Application", "chrome.exe"))
    jel += [shutil.which(x) or "" for x in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")]
    hf = Path.home() / ".cache" / "hyperframes" / "chrome"
    if hf.exists():
        jel += [str(p) for p in hf.rglob("chrome-headless-shell") if p.is_file()]
    for j in jel:
        if j and Path(j).exists():
            return j
    return None


def kep(html, ki, kat, vid, t, val=None, reels=False):
    ch = chrome_ut()
    if not ch:
        raise SystemExit("Nincs Chrome a gépen: telepítsd (chrome.com), vagy add meg a CHROME környezeti változóban.")
    q = {"kep": f"{kat}:{vid}@{t}"}
    if val:
        q["val"] = ",".join(f"{k}:{v}" for k, v in val.items())
    if reels:
        q["reels"] = "1"
    url = Path(html).resolve().as_uri() + "?" + urllib.parse.urlencode(q)
    subprocess.run([ch, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--allow-file-access-from-files", "--window-size=1080,1920", "--virtual-time-budget=7000",
                    f"--screenshot={ki}", url], check=True, capture_output=True, timeout=120)
    return ki


def valasztas_betolt(mappa, ut=None):
    """valasztas.json (a gépi adat) vagy a „Visszajelzés másolása” szövege: a GÉPI ADAT sorból."""
    p = Path(ut) if ut else Path(mappa) / "video" / "valasztas.json"
    if not p.exists():
        return None
    t = p.read_text(encoding="utf-8").strip()
    if "--- GÉPI ADAT" in t:
        t = t.split("--- GÉPI ADAT", 1)[1].split("\n", 1)[1].strip()
    return json.loads(t)


def dontesek(tok, tart, V):
    """kategória -> a végleges változat (végleges, ha nincs: kipróbált, ha az sincs: ajánlott)."""
    A = K.ajanlott(tok, tart)
    D = {}
    for k in K.KATEGORIAK:
        v = ((V or {}).get("valasztas") or {}).get(k["kat"]) or {}
        D[k["kat"]] = v.get("vegleges") or v.get("elonezet") or A.get(k["kat"]) or k["valtozatok"][0]["id"]
    return D


def kepek(mappa, valasztas=None, mind=False, kimappa=None):
    mappa = Path(mappa)
    html = mappa / "video" / "video-valaszto.html"
    if not html.exists():
        raise SystemExit("Előbb: video.py valaszto <munkamappa>")
    tok = json.loads((mappa / "tokenek.json").read_text(encoding="utf-8"))
    tp = mappa / "video" / "tartalom.json"
    tart = json.loads(tp.read_text(encoding="utf-8")) if tp.exists() else {}
    D = dontesek(tok, tart, valasztas_betolt(mappa, valasztas))
    ki = Path(kimappa) if kimappa else mappa / "video" / "kepek"
    ki.mkdir(parents=True, exist_ok=True)
    feladat = []
    for k in K.KATEGORIAK:
        ids = [v["id"] for v in k["valtozatok"]] if mind else [D[k["kat"]]]
        for vid in ids:
            t = KULCSIDO[k["kat"]]
            if isinstance(t, dict):
                t = t.get(vid, 1.2)
            feladat.append((k["kat"], vid, t, ki / f"elem-{k['kat']}-{vid}.png"))
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(lambda f: kep(html, f[3], f[0], f[1], f[2], val=D), feladat))
    from PIL import Image
    jpg = []
    for f in feladat:
        j = f[3].with_suffix(".jpg")
        Image.open(f[3]).convert("RGB").save(j, quality=84, optimize=True, progressive=True)
        f[3].unlink()
        jpg.append(j)
    return D, jpg


def betu_ut(mappa=None):
    jel = []
    if mappa:
        jel += sorted(Path(mappa).glob("betuk/*-700.ttf")) + sorted(Path(mappa).glob("betuk/*-400.ttf"))
    jel += [Path("/System/Library/Fonts/Supplemental/Arial.ttf"), Path("/Library/Fonts/Arial.ttf"),
            Path("C:/Windows/Fonts/arial.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
    for j in jel:
        if Path(j).exists():
            return str(j)
    return None


def tablo(kepek_, ki, oszlop=6, szel=270, cimkek=None, mappa=None):
    from PIL import Image, ImageDraw, ImageFont
    bu = betu_ut(mappa)
    fnt = ImageFont.truetype(bu, 15) if bu else ImageFont.load_default()
    n = len(kepek_)
    sor = (n + oszlop - 1) // oszlop
    mag = int(szel * 16 / 9)
    T = Image.new("RGB", (oszlop * (szel + 12) + 12, sor * (mag + 40) + 12), (241, 239, 232))
    d = ImageDraw.Draw(T)
    for i, p in enumerate(kepek_):
        im = Image.open(p).convert("RGB").resize((szel, mag))
        x, y = 12 + (i % oszlop) * (szel + 12), 12 + (i // oszlop) * (mag + 40)
        T.paste(im, (x, y))
        d.text((x + 4, y + mag + 8), (cimkek[i] if cimkek else Path(p).stem.replace("elem-", "")), fill=(31, 30, 27), font=fnt)
    T.save(ki, quality=88)
    return ki


# ---------------------------------------------------------------- a változatok gépi leírása (a vágómotoroknak)
def specifikacio(T, D, tart):
    R, B, F = T["szinek"]["szerepek"], T["betuk"], T["forma"]
    fel, cim = B["felirat"], B["cim"]
    S = {
        "stilus": {
            "klasszikus": {"vago_skill_fejezet": "5. KLASSZIKUS (lebegő elrendezés)", "mod": "lebego",
                           "savok_px": {"felvetel": [235, 1110], "felirat": [1140, 1310], "kartya": [1340, 1510]},
                           "kartya": "mindig középen, a tartalmához igazodik, csak amíg mond valamit", "also_scrim": 0.78},
            "panel": {"vago_skill_fejezet": "5.4 panel(edge)", "mod": "panel", "panel": "felülről a tartalom alja + 210 px-ig (700-880)",
                      "fejteto": "a panel alja alatt 50 px", "felirat": "a panelen, sötét szöveggel", "panel_hatter": f"{R['panel_a']} → {R['panel_b']} + a márka textúrája"},
            "tiszta": {"vago_skill_fejezet": "5.3 „Tiszta” változat", "mod": "lebego", "kartya": "nincs: fehér szöveg a felvételen, a kis címkék kiesnek",
                       "ikon": "csak fehér sziluett", "also_scrim": 0.9},
            "kivagasos": {"vago_skill_fejezet": "6. KIVÁGÁSOS", "kivagas": "teljes alak (RVM)",
                          "fej_mogott": ["nagy kulcsszó (az alja 60-75 px-szel a fejtető alatt)", "két csempe a fej két oldalán, köztük fénycsík",
                                         "óragyűrű, 3D kártyák (a vágó skill motion-szótárából)"],
                          "info": "a fej fölött vagy mellett, soha mögötte", "felirat": "a mellkason, 1-3 szó, az aktív szó kiemelőszínű"},
            "csakfej": {"vago_skill_fejezet": "12. Hosszú videóból short", "kivagas": "csak a fej (fejtetőtől ~470 px-ig)",
                        "felirat": "az áll alatt: az áll 90. percentilise + 62 px, 1440-1620 px közé szorítva",
                        "info": "a fej fölött, az alja a fejtetőhöz horgonyozva (felfelé nő)", "disz": "kiemelő blokkok a fej mögött, a haj rálóghat"},
        },
        "felirat": {
            "szavankent": {"szavak_egyszerre": 1, "betu": fel["csalad"], "suly": fel["suly"],
                           "meret_px": {"<=9 betű": 92, "<=12": 82, "<=15": 70, "<=18": 60, "hosszabb": 52},
                           "szin_felvetelen": R["szoveg_felvetelen"], "arnyek": F["arnyek_szoveg"], "kiemeles": R["kiemeles_felvetelen"],
                           "szin_panelen": R["szoveg_kartyan"], "kiemeles_panelen": R["kiemeles_kartyan"], "be_s": 0.09, "ki_s": 0.05},
            "karaoke": {"szavak_egyszerre": "1-3 (írásjelnél új csoport)", "betu": fel["csalad"], "suly": 800, "meret_px": 68,
                        "szin": R["szoveg_felvetelen"], "aktiv_szo": R["kiemeles_felvetelen"], "arnyek": F["arnyek_szoveg"]},
            "slam": {"szavak_egyszerre": 1, "nagybetus": True, "betu": fel["csalad"], "suly": fel["suly"], "meret_px": 118,
                     "be": "scale 1.45→1, rotation -4°→0, 0,16 s expo.out", "kiemeles": R["kiemeles_felvetelen"]},
            "doboz": {"szavak_egyszerre": 1, "betu": fel["csalad"], "suly": 800, "meret_px": 66, "hatter": R["pill_hatter"],
                      "szoveg": R["pill_szoveg"], "kulcsszo_hatter": R["akcent"], "kulcsszo_szoveg": R["akcent_szoveg"], "lekerekites_px": F["r_pill_px"]},
            "mondatsav": {"szavak_egyszerre": "a teljes mondat", "betu": fel["csalad"], "suly": 700, "meret_px": 50,
                          "sav": T["szinek"]["szerepek"]["scrim"] + " 78%", "kimondott": "#FFFFFF", "hatralevo": "fehér 62%", "kulcsszo": R["kiemeles_felvetelen"]},
        },
        "hook": {
            "sotetitett": {"scrim": "felső 960 px, a mély szín sötétített változata", "kicker": {"meret_px": 28, "szin": R["kiemeles_felvetelen"]},
                           "cim": {"betu": cim["csalad"], "suly": cim["suly"], "meret_px": "72-96", "kiemelt_sor": R["kiemeles_felvetelen"]}, "zona_px": [235, 470]},
            "blokkok": {"blokkok": [{"hatter": R["kartya"], "szoveg": R["szoveg_kartyan"]}, {"hatter": R["fo"], "szoveg": R["fo_szoveg"]}],
                        "elforgatas_fok": -2, "betu": fel["csalad"], "suly": 900, "meret_px": "88-96 (hosszú sor kisebb)"},
            "uveg": {"hatter": "rgba(255,255,255,.80) + 16 px elmosás", "jel": T["motivum"].get("jel"), "zona_px": [235, 500],
                     "cim": {"betu": cim["csalad"], "suly": cim["suly"], "meret_px": 60}},
            "fejmogott": {"betu": cim["csalad"], "suly": cim["suly"], "meret_px": 260, "also_el": "fejtető + 60-75 px",
                          "szin": R["szoveg_kartyan"], "derenges": "fehér", "kell": "kivágás (RVM)"},
            "derenges": {"szin": R["szoveg_kartyan"], "kiemeles": R["kiemeles_kartyan"],
                         "derenges": "0 0 3px #fff, 0 0 20px rgba(255,255,255,.95), 0 0 46px rgba(255,255,255,.85)", "megjegyzes": "zsúfolt háttéren kerüld"},
        },
        "kartya": {
            "lebego": {"hatter": R["kartya"], "lekerekites_px": F["r_kartya_px"], "arnyek": F["arnyek_kartya"], "css": ".k.k-lebego"},
            "texturas": {"hatter": R["papir"], "textura": T["motivum"]["textura_nev"] or T["motivum"]["textura"], "keret": f"{F['keret_px']}px {R['kartya_keret']}",
                         "lekerekites_px": F["r_kartya_px"], "css": ".k.k-texturas"},
            "uveg": {"hatter": "rgba(255,255,255,.16) + 18 px elmosás", "keret": "2px rgba(255,255,255,.55)", "szoveg": "#FFFFFF", "css": ".k.k-uveg"},
            "telt": {"hatter": R["fo"], "szoveg": R["fo_szoveg"], "lekerekites_px": F["r_kartya_px"], "css": ".k.k-telt"},
            "keretes": {"hatter": R["papir"], "keret": f"kettős hajszálkeret ({R['szoveg_kartyan']})", "cimke": tart.get("tabla_cimke") or "",
                        "cimke_betu": B["cimke"]["csalad"], "css": ".k.k-keretes"},
        },
        "mozgas": {
            "nyugodt": {"be": "átlátszóság 0→1, y +34→0 px, elmosás 8→0 px, 0,6 s power2.out", "ki": "0,38 s", "punch": None,
                        "effekt": "~1 / 5 s", "effektsav_szorzo": 0.7},
            "maszkos": {"be": "maszk (clip-path) balról jobbra nyílik, 0,55 s power3.inOut", "ki": "jobbra záródik, 0,4 s", "punch": None,
                        "effekt": "~1 / 3 s", "effektsav_szorzo": 0.8},
            "rugos": {"be": "scale 0,55→1, back.out(1.9), 0,45 s", "ki": "scale 0,88, 0,2 s", "punch": 1.03, "effekt": "~1 / 2,8 s", "effektsav_szorzo": 0.8},
            "kinetikus": {"be": "scale 1,5→1, rotation -3°→0, 0,22 s expo.out + fehér villanás", "ki": "balra kicsúszik, 0,18 s", "punch": 1.05,
                          "effekt": "~1 / 1,2 s", "effektsav_szorzo": 1.0},
            "szerkesztosegi": {"be": "y +14→0 px, 0,45 s power2.out, a kulcsszó alá akcentszínű aláhúzás rajzolódik (0,5 s)", "ki": "0,3 s",
                               "punch": None, "effekt": "~1 / 3,5 s", "effektsav_szorzo": 0.75},
        },
        "hangulat": {
            "akusztikus": {"bpm": 72, "zene": "pengetős húrok, lassú arpeggio, sok levegő", "atmenet": "levegős whoosh", "kartya": "papírzörej",
                           "kiemeles": "halk üveghangú csengő", "zene_szorzo": 0.11},
            "meleg": {"bpm": 88, "zene": "marimba, halk shaker", "atmenet": "suhogás (swish)", "kartya": "fa koppanás", "kiemeles": "kis harang", "zene_szorzo": 0.12},
            "modern": {"bpm": 100, "zene": "puha szintipad, halk klikk a negyedekre", "atmenet": "tiszta whoosh", "kartya": "pop", "kiemeles": "tiszta klikk", "zene_szorzo": 0.11},
            "lendulet": {"bpm": 118, "zene": "dob (lábdob, taps) és basszus", "atmenet": "magas whoosh", "kartya": "pop", "kiemeles": "mély ütés", "zene_szorzo": 0.13},
            "filmes": {"bpm": 84, "zene": "mély pad, lassú pulzus", "atmenet": "emelkedő (riser)", "kartya": "tompa koppanás", "kiemeles": "mély boom", "zene_szorzo": 0.12},
        },
        "tema": {
            "lista": {"hely": "a fej fölött, az alja a fejtető fölött ~15 px", "sorok": "legfeljebb 4; kész: pipa, halvány; aktuális: kiemelt sáv + MOST", "hatter": R["kartya"],
                      "kiemelt_sav": f"{R['papir']} + bal szélén {R['fo']}"},
            "pillsor": {"hely": "felül, 270 px-től", "pill": "fehér 92%, az aktuális telt fő színű"},
            "lepcso": {"hely": "felül, 280 px-től", "pontok": "számozott körök vonallal; kész: rendben-szín, aktuális: fő szín", "cim": "alatta nagyban, a címbetűvel"},
        },
        "nev": {
            "kartya": {"hely": "bal alsó harmad, 1300 px-től (a Reels-sáv fölött)", "hatter": R["kartya"], "sav": "fő → akcent színátmenet a bal szélen", "nev_betu": cim["csalad"]},
            "tabla": {"hely": "bal alsó harmad", "hatter": R["fo"], "szoveg": R["fo_szoveg"], "vonal": R["akcent2"]},
            "vonal": {"hely": "bal alsó harmad, lágy alsó sötétítéssel", "szoveg": "#FFFFFF", "vonal": R["kiemeles_felvetelen"]},
        },
        "fejezet": {
            "takeover": {"hossz_s": "legfeljebb 1,2", "hatter": f"{R['papir']} + textúra", "szam": {"betu": cim["csalad"], "meret_px": 300, "szin": R["fo"]}},
            "pill": {"hely": "bal felső, 250 px-től", "hatter": R["kartya"], "szam_kor": R["fo"]},
            "szam": {"hely": "bal alsó harmad", "szam": "460 px körvonalas fehér", "cim": {"betu": cim["csalad"], "meret_px": 76}},
        },
        "zaro": {
            "social": {"szoveg": (tart.get("zaro") or {}).get("social") or "Ha hasznos volt", "pillek": ["♥ Lájk (kártyán, figyelmeztető színnel)", "+ Követés (fő szín)"],
                       "hely": "a fej fölött", "kep": "lassú közelítés 1,07-ig"},
            "cta": {"ajanlat": ((tart.get("zaro") or {}).get("cta") or {}), "gomb": f"{R['pill_hatter']} / {R['pill_szoveg']}, lassan pulzál", "hely": "alsó harmad"},
            "logo": {"logo": "fehér változat", "szlogen": (tart.get("zaro") or {}).get("szlogen"), "hely": "alul, sötétítéssel"},
        },
        "nyito": {
            "blokk": {"blokkok": "két kiemelő blokk a fotón felül", "hossz_s": 0.5},
            "nagyszo": {"sav": R["fo"], "szoveg": R["fo_szoveg"], "hely": "alsó harmad, 1190 px-től"},
            "keretes": {"hatter": f"{R['papir']} + textúra", "foto": "fehér keret, -3°", "cim": cim["csalad"], "jel": T["motivum"].get("jel")},
        },
    }
    return {kat: dict(S.get(kat, {}).get(vid, {}), valtozat=vid) for kat, vid in D.items()}


def komponens_css(D):
    """A választott változatok CSS-e az előnézet stíluslapjából, a választó hatóköre nélkül (a vágómotor ebből olvas)."""
    css = (Path(__file__).resolve().parents[2] / "assets" / "video" / "elonezet.css").read_text(encoding="utf-8")
    kell = {"cap", "w", "g", "bx", "msav", "ink", "k", "kk", "kr", "kn", "kl", "ki2", "alahuz", "s-alul", "s-felul", "bar", "kozep", "abs",
            "h-kick", "h-cim", "mk", "mkst", "kpill", "nagyszo", "capc", "tile", "streak"}
    kell |= {f"k-{D['kartya']}", "k-tiszta"}
    kell |= {"pn", "pn-tag", "pn-row", "pn-num", "pn-lab", "pn-tile"} if D["stilus"] == "panel" else set()
    kell |= {"uveg", "jelk", "gk", "gt"} if D["hook"] == "uveg" else set()
    kell |= {"derenges"} if D["hook"] == "derenges" else set()
    kell |= {"tm", "k1", "t", "n", "d", "hl", "most"} if D["tema"] == "lista" else ({"tpills", "p"} if D["tema"] == "pillsor" else {"lepcso", "sor", "vo", "pt", "ct"})
    kell |= {"nv", "nm", "rl", f"nv-{D['nev']}", "sav", "tx", "vl"}
    kell |= {f"fj-{D['fejezet']}", "fj-szc"} if D["fejezet"] == "szam" else {f"fj-{D['fejezet']}"}
    kell |= {"zlk", "l", "l1", "l2"} if D["zaro"] == "social" else ({"zcta"} if D["zaro"] == "cta" else {"zlogo"})
    kell |= {"ny-sav"} if D["nyito"] == "nagyszo" else ({"ny-papir", "ny-foto", "ny-cim", "ny-jel"} if D["nyito"] == "keretes" else set())
    ki = ["/* A választott elemek (az előnézet CSS-éből, a színpad-hatókör nélkül). Az osztályok: .k (kártya), .cap (felirat), ... */",
          ".v-szinpad{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:var(--v-betu-felirat);color:#fff}"]
    import re
    for sor in css.splitlines():
        if not sor.startswith("#fazis-video .vst ."):
            continue
        sel = sor.split("{", 1)[0]
        osztalyok = set(re.findall(r"\.([a-z0-9-]+)", sel.replace("#fazis-video .vst", "")))
        if osztalyok and osztalyok <= (kell | {"on", "ak", "ki", "kesz", "alatta", "slam", "f", "p", "a", "c", "u", "s", "tab", "el", "zn", "zl"}):
            ki.append(sor.replace("#fazis-video .vst ", ".v-szinpad "))
    return "\n".join(ki)


def vegleges(mappa, valasztas=None):
    mappa = Path(mappa)
    tok = json.loads((mappa / "tokenek.json").read_text(encoding="utf-8"))
    tp = mappa / "video" / "tartalom.json"
    tart = K.alap_tartalom(tok)
    if tp.exists():
        tart.update(json.loads(tp.read_text(encoding="utf-8")))
    V = valasztas_betolt(mappa, valasztas)
    D = dontesek(tok, tart, V)
    T = TM.tema(tok)
    T["allapot"] = {"forras": "valasztott" if V else "ajanlott", "jovahagyva": bool((V or {}).get("jovahagyva")),
                    "video_verzio": (V or {}).get("verzio", 1), "datum": (V or {}).get("datum")}
    T["valasztas"] = {"valtozatok": D,
                      "megjegyzesek": {k: v.get("megjegyzesek") for k, v in ((V or {}).get("valasztas") or {}).items() if v.get("megjegyzesek")},
                      "altalanos": (V or {}).get("altalanos", "")}
    T["elemek"] = specifikacio(T, D, tart)
    T["tartalom_minta"] = {k: tart.get(k) for k in ("nev", "zaro", "kulcsszo")}
    vm = mappa / "video"
    (vm / "video-tema.json").write_text(json.dumps(T, ensure_ascii=False, indent=1), encoding="utf-8")
    (vm / "video-tokens.css").write_text(TM.css(T, komponens_css(D)), encoding="utf-8")
    try:
        D2, kepek_ = kepek(mappa, valasztas)
        tablo(kepek_, vm / "kepek" / "tablo-valasztott.jpg", oszlop=6, szel=260, mappa=mappa,
              cimkek=[f"{K.KAT[k]['nev'].split(' (')[0]}: {nevv(k, D[k], tart)}"[:36] for k in [p.stem.split('-')[1] for p in kepek_]])
    except SystemExit as e:
        print("  ! képek nélkül:", e)
    md = arculat_md(T, D, tart, tok, mappa)
    (vm / "VIDEO-ARCULAT.md").write_text(md, encoding="utf-8")
    blokk, szakasz, aj = marka_resz(T, D, tart, tok, mappa)
    (vm / "MARKA-RESZ.md").write_text(marka_resz_md(blokk, szakasz, tok, aj), encoding="utf-8")
    (vm / "vago-arculat.json").write_text(json.dumps(aj, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"KÉSZ: {vm}/video-tema.json, video-tokens.css, VIDEO-ARCULAT.md, MARKA-RESZ.md, vago-arculat.json, kepek/")
    return T


def nevv(kat, vid, tart):
    k = K.KAT[kat]
    o = next((v for v in k["valtozatok"] if v["id"] == vid), {"nev": vid})
    f = ((tart.get("valtozatok") or {}).get(kat) or {}).get(vid) or {}
    return f.get("nev") or o["nev"]


def leirasv(kat, vid, tart):
    k = K.KAT[kat]
    o = next((v for v in k["valtozatok"] if v["id"] == vid), {"leiras": ""})
    f = ((tart.get("valtozatok") or {}).get(kat) or {}).get(vid) or {}
    return f.get("leiras") or o["leiras"]


# ---------------------------------------------------------------- emberi leírás
ARNYEK = {"lagy": "lágy", "eros": "erős, eltolt", "nincs": "nincs (videón egy halvány árnyék akkor is kell)"}


def tized(x):
    return str(x).replace(".", ",") if isinstance(x, float) else x


SZEREP_SOR = [("szoveg_felvetelen", "Szöveg a felvételen", "felirat, nagy szöveg, mindig árnyékkal vagy sötétítésen"),
              ("kiemeles_felvetelen", "Kiemelés a felvételen", "az éppen elhangzó szó, kulcsszó, kicker"),
              ("szoveg_kartyan", "Szöveg kártyán, panelen", "minden szöveg a világos felületeken"),
              ("kiemeles_kartyan", "Kiemelés kártyán", "szám, kulcsszó, kicker a világos felületen"),
              ("pill_hatter", "Pill, gomb", "címkék, gombok háttere (a betű: pill-szöveg)"),
              ("akcent", "Akcentus", "csak fehér betűvel, vagy maga a szöveg sötét alapon"),
              ("papir", "Papír", "textúrás és keretes kártya, fejezetkártya alapja"),
              ("mely", "Mély szín", "sötét felületek, a sötétítés alapja"),
              ("figyelmezteto", "Figyelmeztető", "áthúzás, hibás érték, „rossz” oldal"),
              ("rendben", "Rendben", "pipa, kész téma")]


def osszefoglalo(D, tart):
    n = lambda k: nevv(k, D[k], tart)
    return (f"A videóid **{n('stilus')}** stílusban készülnek: {leirasv('stilus', D['stilus'], tart).split('.')[0].lower()}. "
            f"Felirat: **{n('felirat')}**. Címsor: **{n('hook')}**. Az információ kártyája: **{n('kartya')}**. "
            f"Mozgás: **{n('mozgas')}**. Hangulat: **{n('hangulat')}**. "
            f"A kisebb elemek: a témaválasztó „{n('tema')}”, a névkártya „{n('nev')}”, a fejezetkártya „{n('fejezet')}”, "
            f"a záró „{n('zaro')}”, a nyitókép „{n('nyito')}”.")


def arculat_md(T, D, tart, tok, mappa):
    R, B, F = T["szinek"]["szerepek"], T["betuk"], T["forma"]
    nev = (tok.get("marka") or {}).get("nev", "")
    A = T["allapot"]
    all_ = f"jóváhagyva ({A.get('datum') or ''})" if A.get("jovahagyva") else "ajánlott összeállítás, még nincs jóváhagyva"
    s = [f"# Videós arculat: {nev}", "",
         f"> AI arculat-generátor, videó fázis (béta) · állapot: {all_}.",
         "> A színek és a betűk a jóváhagyott webes arculatból öröklődnek (tokenek.json); ez a fájl a videós döntéseket írja le.", "",
         "## Röviden", "", osszefoglalo(D, tart), "", "![A választott elemek](kepek/tablo-valasztott.jpg)", "",
         "## Színek a videón", "", "| szerep | szín | mire |", "|---|---|---|"]
    for k, n, m in SZEREP_SOR:
        if R.get(k):
            s.append(f"| {n} | `{R[k]}` | {m} |")
    s.append(f"| Sötétítés (scrim) | `{R['scrim']}` 78-92% | a felirat és a nagy szöveg alatt a felvételen |")
    rossz = [k for k, v in T["szinek"]["kontraszt"].items() if not v["ok"]]
    s += ["", "Kontraszt: " + ("minden szövegpár legalább 4,5:1." if not rossz else "figyelj ezekre: " + ", ".join(rossz) + "."),
          *[f"- {x}" for x in T["szinek"]["tiltasok"]], *[f"- {x}" for x in T["szinek"]["megjegyzesek"]], "",
          "## Betűk", ""]
    for k, n in (("felirat", "Felirat és címkék"), ("cim", "Nagy címek, hook, névkártya"), ("cimke", "Kis címke kártyán"), ("kez", "Kézírásos dísz")):
        b = B.get(k)
        if b:
            s.append(f"- **{n}:** {b['csalad']} {b.get('suly', '')}" + (f" ({b['hasznalat']})" if b.get("hasznalat") else ""))
    s += [*[f"- {x}" for x in B["megjegyzesek"]], "- Minden betű ő/ű-biztos (a skill betűkatalógusában gépileg ellenőrizve).", "",
          "## Formák", "",
          f"- Kártya lekerekítése: {F['r_kartya_px']} px, pill: {'kapszula' if F['r_pill_px'] >= 999 else str(F['r_pill_px']) + ' px'}, keret: {F['keret_px']} px.",
          f"- Árnyék: {ARNYEK.get(F['arnyek_tipus'], F['arnyek_tipus'])} (`{F['arnyek_kartya']}`). A webes értékek videós léptékben (a telefonon kb. harmad akkorának látszik).", "",
          "## A választott elemek", ""]
    megj = (T.get("valasztas") or {}).get("megjegyzesek") or {}
    for i, k in enumerate(K.KATEGORIAK):
        vid = D[k["kat"]]
        s += [f"### {i + 1}. {k['nev']}: {nevv(k['kat'], vid, tart)}", "", leirasv(k["kat"], vid, tart), "",
              f"![{k['nev']}](kepek/elem-{k['kat']}-{vid}.jpg)", ""]
        sp = (T.get("elemek") or {}).get(k["kat"]) or {}
        reszl = [f"{a}: {json.dumps(b, ensure_ascii=False) if isinstance(b, (dict, list)) else b}" for a, b in sp.items() if a != "valtozat" and b not in (None, "")]
        if reszl:
            s += ["<details><summary>Pontos értékek a vágómotornak</summary>", "", *[f"- {x}" for x in reszl], "", "</details>", ""]
        for vid2, t in ((megj.get(k["kat"]) or {}).items()):
            s.append(f"> Megjegyzés ({nevv(k['kat'], vid2, tart)}): {t}")
        if megj.get(k["kat"]):
            s.append("")
    if (T.get("valasztas") or {}).get("altalanos"):
        s += ["**Általános megjegyzés:** " + T["valasztas"]["altalanos"], ""]
    f9 = T["formatumok"]["9x16"]
    s += ["## Szabályok", "", *[f"- {x}" for x in T["szabalyok"]], "",
          "## Formátumok", "",
          f"- **9:16** (Reels, TikTok, Shorts): 1080×1920; üresen marad felül {f9['safe']['felul']}, alul {f9['safe']['alul']}, "
          f"jobbra {f9['safe']['jobbra']} px; a tartalomoszlop x {f9['oszlop']['x']}-{f9['oszlop']['x'] + f9['oszlop']['szel']}; a hírfolyam 4:5-re vág (y 240-1680).",
          "- **16:9** (YouTube): 1920×1080; csak ha ott is gyártasz (névkártya, fejezetkártya, szám, idézet, CTA ugyanezekkel a színekkel és betűkkel).", "",
          "## Így használd", "",
          "1. A vágó skilled a tananyagból jön (domarketing.hu/ai-video-vagas, „A vágórendszerünk, üresre csupaszítva”). A `MARKA-RESZ.md` "
          "kitöltött 2.3-as blokkját és a „Videós arculatom” részét tedd bele, vagy kérd a Claude-ot: "
          "„Tedd be a videós arculatomat a vágó skillembe: <ennek a mappának az útja>/MARKA-RESZ.md”.",
          "2. A `video-tokens.css` kerüljön a vágó munkamappád `a/` mappájába: a kompozíció ebből veszi a színeket, a betűket és az elemek CSS-ét.",
          "3. Utána egyszerűen: „Vágd meg ezt a videót a saját videós arculatommal.”", "",
          "## Fájlok", "",
          "- `video-tema.json`: a teljes videós arculat gépi formában (színszerepek, betűk, formák, elemek pontos értékei, szabályok, formátumok).",
          "- `video-tokens.css`: CSS-változók (`--v-*`) és a választott elemek CSS-e; minden vágómotor ebből olvas.",
          "- `MARKA-RESZ.md` és `vago-arculat.json`: a vágó skill 2.3-as arculati blokkja kitöltve, és ugyanez a szkripteknek.",
          "- `kepek/`: a választott elemek állóképei és a tabló; `video-valaszto.html`: az élő előnézet.", ""]
    return "\n".join(s)


# ---------------------------------------------------------------- márka-rész a tag vágó skilljéhez
def marka_resz(T, D, tart, tok, mappa):
    R, B = T["szinek"]["szerepek"], T["betuk"]
    mappa = Path(mappa)
    nev = (tok.get("marka") or {}).get("nev", "")
    vil = R["papir"] if D["kartya"] in ("keretes", "texturas") else R["kartya"]
    lg = tok.get("logo") or {}
    logo = ", ".join(f"a/logo-{k}.png ({n})" for k, n in (("szines", "színes"), ("feher", "fehér")) if lg.get(k)) or "[ÚTVONAL]"
    logo_forras = "; ".join(f"{(mappa / lg[k]).as_posix()} → a/logo-{k}.png" for k in ("szines", "feher") if lg.get(k))
    hn = tok.get("hangnem") or ""
    teg = "tegező" if "tegez" in hn.lower() else ("magázó" if "magáz" in hn.lower() else "[TEGEZŐ/MAGÁZÓ]")
    pelda = tart.get("hangnem_pelda") or " ".join(tart.get("felirat") or [])
    C = (tart.get("zaro") or {}).get("cta") or {}
    zar = (tart.get("zaro") or {}).get("social") or "Ha hasznos volt"
    zaras = f"„{zar.rstrip('.!')}, nyomj egy lájkot, és kövess be!”"
    ik = tok.get("ikon") or {}
    H = T["elemek"]["hangulat"]
    fotok = (mappa / ((tok.get("foto") or {}).get("mappa") or "bemenet/kepek")).as_posix()
    ak_alap = (T["szinek"].get("megjegyzesek") or [""])[0]
    sorok = [("vállalkozás neve", nev, ""),
             ("fő szín (kiemelés)", R["fo"], "pl. gombok, kiemelt szó a kártyán, pillek"),
             ("második szín (akcentus)", R["kiemeles_felvetelen"], f"pl. aktív szó a felvételen, aláhúzás, gyűrű (az alap akcentus: {R['akcent']}, fehér betűvel)"),
             ("sötét szövegszín", R["szoveg_kartyan"], "a világos kártyákon"),
             ("világos kártyaszín", vil, "a kártyák és panelek alapja"),
             ("figyelmeztető szín", R["figyelmezteto"], "áthúzás, „rossz” oldal"),
             ("betűtípus", f"{B['felirat']['csalad']}", "kell hozzá: 600, 700, 800, 900 vastagság .ttf-ben (a/fonts/)"),
             ("címbetű", f"{B['cim']['csalad']} {B['cim']['suly']}", "nagy címek, hook, névkártya (a/fonts/)"),
             ("logó", logo, "átlátszó PNG"),
             ("hangnem", f"{teg}, „{pelda}”", ""),
             ("CTA hirdetéshez", f"{C.get('cim', '[AJÁNLAT]')}, {C.get('gomb', '[GOMB SZÖVEGE]')}, {C.get('link', '[LINK]')}", ""),
             ("zárás tartalomvideóhoz", zaras, ""),
             ("ikonstílus", f"{ik.get('stilus_nev', '')}: {ik.get('elotag', '')}", ""),
             ("fotókönyvtár", fotok, ""),
             ("b-roll mappa", "nincs", ""),
             ("zene", f"generált, „{nevv('hangulat', D['hangulat'], tart)}”: {H.get('bpm')} BPM, {H.get('zene')}", ""),
             ("hangeffektek", f"generált: {H.get('atmenet')}, {H.get('kartya')}, {H.get('kiemeles')}", ""),
             ("kimeneti mappa", "[ÚTVONAL]", "")]
    blokk = "[A TE ARCULATOD]\n" + "\n".join(f"  {(a + ':').ljust(25)} {b}" + (f"      {c}" if c else "") for a, b, c in sorok)
    E = T["elemek"]
    n = lambda k: nevv(k, D[k], tart)
    st = {"klasszikus": "5. fejezet, lebegő elrendezés", "panel": "5.4, panel(edge) mód", "tiszta": "5.3, „tiszta” változat",
          "kivagasos": "6. fejezet", "csakfej": "12. fejezet (hosszú videóból short), a „fej” stílus"}[D["stilus"]]
    fel_sz = E["felirat"]
    m = E["mozgas"]
    szakasz = "\n".join([
        f"### 2.3b A videós arculatom ({nev}, AI arculat-generátor)", "",
        "Ezek a döntések a videós arculat-választóból jönnek. Ahol a lenti fejezetek mást mondanak, ez az erősebb. "
        "A pontos értékek a `video-tema.json`-ban, a CSS a `video-tokens.css`-ben (a munkamappa `a/` mappájában).", "",
        f"- **Alapstílus: {n('stilus')}** ({st}). {leirasv('stilus', D['stilus'], tart)}",
        f"- **Felirat: {n('felirat')}.** {leirasv('felirat', D['felirat'], tart)} Betű: {fel_sz.get('betu', B['felirat']['csalad'])} "
        f"{fel_sz.get('suly', '')}, méret: {json.dumps(fel_sz.get('meret_px'), ensure_ascii=False)} px. "
        + ("A 4.5 „egyszerre egy szó” szabálya helyett ez érvényes." if D["felirat"] != "szavankent" else ""),
        f"- **Címsor (hook): {n('hook')}.** {leirasv('hook', D['hook'], tart)}",
        f"- **Kártya: {n('kartya')}.** {leirasv('kartya', D['kartya'], tart)} CSS: `{E['kartya'].get('css', '')}`.",
        f"- **Mozgás és tempó: {n('mozgas')}.** Belépés: {m.get('be')}; kilépés: {m.get('ki')}; ráközelítés (punch): "
        f"{tized(m.get('punch')) or 'nincs'}; hangeffekt: {m.get('effekt')}, az effektsáv szorzója {tized(m.get('effektsav_szorzo'))}.",
        f"- **Hangulat: {n('hangulat')}.** {H.get('bpm')} BPM, {H.get('zene')}; átmenet: {H.get('atmenet')}, kártya: {H.get('kartya')}, "
        f"kiemelés: {H.get('kiemeles')}; a zene a beszéd alatt {tized(H.get('zene_szorzo'))} szorzóval.",
        f"- **Témaválasztó kártya (új elem): {n('tema')}.** Akkor kell, ha a videó 3-4 témát vesz sorra: minden új témánál 2-3 másodpercre "
        f"megjelenik. {leirasv('tema', D['tema'], tart)}",
        f"- **Névkártya: {n('nev')}.** {leirasv('nev', D['nev'], tart)} Az első megszólaláskor, 2-3 mp.",
        f"- **Fejezetkártya: {n('fejezet')}.** {leirasv('fejezet', D['fejezet'], tart)}",
        f"- **Záró: {n('zaro')}.** {leirasv('zaro', D['zaro'], tart)}",
        f"- **Nyitókép: {n('nyito')}.** {leirasv('nyito', D['nyito'], tart)} A 7. fejezet tíz opciója közül legalább kettő ilyen legyen.",
        "- **Színszabály:** sötét szöveg akcentszínen tilos; a felvételen a kiemelés az akcentus világosított árnyalata "
        f"({R['kiemeles_felvetelen']}), kártyán a fő szín ({R['kiemeles_kartyan']}).", ""])
    aj = {"vallalkozas_neve": nev, "fo_szin": R["fo"], "akcentus": R["kiemeles_felvetelen"], "akcentus_alap": R["akcent"],
          "sotet_szoveg": R["szoveg_kartyan"], "vilagos_kartya": vil, "figyelmezteto": R["figyelmezteto"],
          "betu": {"felirat": B["felirat"]["csalad"], "felirat_suly": B["felirat"]["suly"], "cim": B["cim"]["csalad"], "cim_suly": B["cim"]["suly"],
                   "google_css": [B[k]["google_css"] for k in ("felirat", "cim") if B.get(k)]},
          "logo": {k: (mappa / v).as_posix() for k, v in lg.items() if v}, "hangnem": {"forma": teg, "leiras": hn, "pelda": pelda},
          "cta": C, "zaras": zaras, "ikonstilus": {"nev": ik.get("stilus_nev"), "elotag": ik.get("elotag")},
          "fotokonyvtar": fotok, "broll": None, "zene": {"tipus": "generált", **{k: H.get(k) for k in ("bpm", "zene", "zene_szorzo")}},
          "hangeffektek": {"tipus": "generált", **{k: H.get(k) for k in ("atmenet", "kartya", "kiemeles")}},
          "video_tokens_css": "video-tokens.css", "video_tema": "video-tema.json", "valasztas": D}
    aj["logo_forras"] = logo_forras
    return blokk, szakasz, aj


def marka_resz_md(blokk, szakasz, tok, aj=None):
    nev = (tok.get("marka") or {}).get("nev", "")
    return "\n".join([
        f"# Márka-rész a vágó skillhez: {nev}", "",
        "A tananyagból telepített vágó skill (domarketing.hu/ai-video-vagas, `video-vagas/SKILL.md`) két helyen kapja meg a videós arculatodat.",
        "Két út közül választhatsz:", "",
        "**A) A Claude beírja.** Írd neki: „Tedd be a videós arculatomat a vágó skillembe: <ennek a fájlnak az útja>.” A Claude ekkor lefuttatja:",
        "`python3 <AI arculat-generátor skill>/scripts/video/video.py skill <munkamappa> <a vágó skilled SKILL.md-je>`, ami elkészíti a skill",
        "személyre szabott másolatát és új ZIP-et; ezt a Customize → Skills alatt cseréld le, és nyiss új beszélgetést.", "",
        "**B) Kézzel.** 1. A SKILL.md 2.3-as fejezetében a `[A TE ARCULATOD]` blokkot cseréld erre:", "",
        "```", blokk, "```", "",
        "2. Közvetlenül a 2.3 után (a 2.4 elé) illeszd be ezt a részt:", "", szakasz,
        "3. A `video-tokens.css`-t és a betűk .ttf-fájljait tedd a vágó munkamappád `a/` (illetve `a/fonts/`) mappájába, a `vago-arculat.json`-t pedig `arculat.json` néven a munkamappába.",
        "   A logók: " + ((aj or {}).get("logo_forras") or "a logód színes és fehér PNG-je az a/ mappába") + ".", ""])


# ---------------------------------------------------------------- a vágó skill személyre szabott másolata
def skill(mappa, skill_md, ki=None):
    import re
    import zipfile
    mappa = Path(mappa)
    tok = json.loads((mappa / "tokenek.json").read_text(encoding="utf-8"))
    tp = mappa / "video" / "tartalom.json"
    tart = K.alap_tartalom(tok)
    if tp.exists():
        tart.update(json.loads(tp.read_text(encoding="utf-8")))
    tj = mappa / "video" / "video-tema.json"
    T = json.loads(tj.read_text(encoding="utf-8")) if tj.exists() else vegleges(mappa)
    D = (T.get("valasztas") or {}).get("valtozatok") or dontesek(tok, tart, None)
    if "elemek" not in T:
        T["elemek"] = specifikacio(T, D, tart)
    blokk, szakasz, aj = marka_resz(T, D, tart, tok, mappa)
    s = Path(skill_md).read_text(encoding="utf-8")
    m = re.search(r"```[^\n]*\n\[A TE ARCULATOD\].*?\n```", s, re.S)
    if m:
        s = s[:m.start()] + "```\n" + blokk + "\n```" + s[m.end():]
        k = s.find("\n### 2.4", m.start())
        s = (s[:k] + "\n\n" + szakasz + s[k:]) if k > 0 else (s + "\n\n" + szakasz)
    else:
        s += "\n\n## Videós arculat\n\n```\n" + blokk + "\n```\n\n" + szakasz
    R, B = T["szinek"]["szerepek"], T["betuk"]
    C = (tart.get("zaro") or {}).get("cta") or {}
    csere = {"[FŐ SZÍN]": f"fő szín ({R['fo']})", "[AKCENTUS]": f"akcentus ({R['kiemeles_felvetelen']})",
             "[SÖTÉT SZÖVEGSZÍN]": R["szoveg_kartyan"], "[FIGYELMEZTETŐ SZÍN]": R["figyelmezteto"],
             "[A TE BETŰTÍPUSOD]": B["felirat"]["csalad"], "[A TE IKONSTÍLUSOD]": (tok.get("ikon") or {}).get("stilus_nev", ""),
             "[A TE ZÁRÓMONDATOD]": aj["zaras"], "[A TE AJÁNLATOD]": C.get("cim", "[A TE AJÁNLATOD]"),
             "[GOMB SZÖVEGE]": C.get("gomb", "[GOMB SZÖVEGE]"), "[A TE CÉGED]": (tok.get("marka") or {}).get("slug", ""),
             "[A TE NYITÓKÉP-STÍLUSOD]": nevv("nyito", D["nyito"], tart), "[A TE ZÁRÓKÁRTYÁD]": nevv("zaro", D["zaro"], tart)}
    for a, b in csere.items():
        s = s.replace(a, b)
    mv = re.search(r"^version:\s*(\d+)\.(\d+)\.(\d+)", s, re.M)
    if mv:
        uj = f"{mv.group(1)}.{mv.group(2)}.{int(mv.group(3)) + 1}"
        s = s[:mv.start()] + f"version: {uj}" + s[mv.end():]
        s = s.rstrip() + f"\n| {uj} | a videós arculat beírva az AI arculat-generátorból ({(tok.get('marka') or {}).get('nev', '')}) |\n"
    ki = Path(ki) if ki else mappa / "video" / "vago-skill"
    sk = ki / "video-vagas"
    (sk / "arculat").mkdir(parents=True, exist_ok=True)
    (sk / "SKILL.md").write_text(s, encoding="utf-8")
    for f in ("video-tokens.css", "video-tema.json"):
        if (mappa / "video" / f).exists():
            shutil.copy(mappa / "video" / f, sk / "arculat" / f)
    for k, v in (tok.get("logo") or {}).items():
        if v and (mappa / v).exists():
            shutil.copy(mappa / v, sk / "arculat" / f"logo-{k}.png")
    (sk / "arculat" / "arculat.json").write_text(json.dumps(aj, ensure_ascii=False, indent=1), encoding="utf-8")
    z = ki / "video-vagas.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sk.rglob("*"):
            if p.is_file():
                zf.write(p, p.relative_to(ki).as_posix())
    print(f"KÉSZ: {sk}/SKILL.md (személyre szabott vágó skill) + {z}")
    return z


# ---------------------------------------------------------------- „minden ajánlott elfogadva” mentés (élő bemutatóhoz)
def elfogad(mappa, jovahagy=True):
    """Az arculat/video-v1 dokumentum teljes tartalma úgy, ahogy a töredék mentené az „Ajánlottak elfogadása” és a
    „Jóváhagyom” után (ahol volt végleges a db-mentésben, az marad). Kiírja: video/db-elfogadva.json (az adatbázisba
    szánt dokumentum) és video/valasztas.json (a gépi adat, ebből dolgozik a vegleges)."""
    import datetime
    mappa = Path(mappa)
    tok = json.loads((mappa / "tokenek.json").read_text(encoding="utf-8"))
    tart = K.alap_tartalom(tok)
    tp = mappa / "video" / "tartalom.json"
    if tp.exists():
        tart.update(json.loads(tp.read_text(encoding="utf-8")))
    dns = {}
    dp = mappa / (tok.get("marka_dns") or "marka-dns.json")
    if dp.exists():
        dns = json.loads(dp.read_text(encoding="utf-8"))
    KT = K.kategoriak(tok, tart, dns)
    regi = {}
    for rp in (mappa / "db-mentes" / "video-v1.json", mappa / "video" / "db-mentes.json"):
        if rp.exists():
            try:
                regi = json.loads(json.loads(rp.read_text(encoding="utf-8")).get("allapot") or "{}").get("val") or {}
            except Exception:
                regi = {}
            break
    most = datetime.datetime.now()
    iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + f"{most.microsecond // 1000:03d}Z"
    ST = {"val": {}, "alt": "", "jovahagyva": iso if jovahagy else False}
    for k in KT:
        r = regi.get(k["kat"]) or {}
        ST["val"][k["kat"]] = {"veg": r.get("veg") or k["ajanlott"], "elo": r.get("elo"), "megj": r.get("megj") or {}, "ujakat": bool(r.get("ujakat"))}
    slug = (tok.get("marka") or {}).get("slug", "marka")
    nev = (tok.get("marka") or {}).get("nev", "")
    js = {"marka": slug, "fazis": "video", "verzio": 1, "datum": most.strftime("%Y-%m-%d %H:%M"), "valasztas": {},
          "altalanos": "", "jovahagyva": ST["jovahagyva"]}
    sor = [f"=== VIDEÓS ARCULAT: {nev} (v1) · {js['datum']} ==="]
    kesz = sum(1 for k in KT if ST["val"][k["kat"]]["veg"])
    sor += [f"Végleges döntés: {kesz} / {len(KT)} elemnél." + (" JÓVÁHAGYVA." if ST["jovahagyva"] else ""), ""]
    for i, k in enumerate(KT):
        v = ST["val"][k["kat"]]
        def nv(vid):
            o = next((x for x in k["valtozatok"] if x["id"] == vid), None)
            return f"„{o['nev']}” ({vid})" if o else vid
        sor.append(f"[{i + 1}] {k['nev']} → VÉGLEGES: {nv(v['veg'])}" + ("   ⚠ ÚJ VÁLTOZATOKAT KÉR" if v["ujakat"] else ""))
        mj = {}
        for vid, t in (v["megj"] or {}).items():
            if (t or "").strip():
                mj[vid] = t.strip()
                sor.append(f"    • {nv(vid)}: " + " / ".join(x for x in t.strip().splitlines() if x))
        vk = next((x for x in k["valtozatok"] if x["id"] == v["veg"]), {})
        js["valasztas"][k["kat"]] = {"vegleges": v["veg"], "vegleges_karakter": vk.get("kar"), "elonezet": v["elo"],
                                     "ajanlott": k["ajanlott"], "megjegyzesek": mj, "ujakat": v["ujakat"],
                                     "opciok": [x["id"] for x in k["valtozatok"]]}
    sor += ["", "--- GÉPI ADAT (ezt ne töröld, ebből dolgozik tovább a Claude) ---", json.dumps(js, ensure_ascii=False, separators=(",", ":"))]
    doc = {"allapot": json.dumps(ST, ensure_ascii=False, separators=(",", ":")), "gepi": json.dumps(js, ensure_ascii=False, separators=(",", ":")),
           "szoveg": "\n".join(sor), "frissitve": iso, "verzio": 1, "jovahagyva": True if jovahagy else False}
    vm = mappa / "video"
    (vm / "db-elfogadva.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    (vm / "valasztas.json").write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"KÉSZ: {vm / 'db-elfogadva.json'} (az arculat/video-v1 új tartalma) + {vm / 'valasztas.json'}")
    for k in KT:
        print(f"  {k['nev']}: {ST['val'][k['kat']]['veg']}")
    return doc
