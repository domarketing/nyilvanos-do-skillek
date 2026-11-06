#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Google Fonts betű-ellenőrző: megvan-e a magyar ő Ő ű Ű, és működik-e a css2 tengely-spec.

Egy családot akkor tekint "ok"-nak, ha:
  1. a css2?family=<F>[:<T>]&text=őŐűŰ kérés 200-at ad (400 = rossz családnév vagy tengely-spec),
  2. a CSS-ben kapott TTF-ek cmap-jében (fontTools) mind a négy kódpont benne van:
     U+0151 ő, U+0150 Ő, U+0171 ű, U+0170 Ű,
  3. a teljes tengely-spec (text nélkül) is 200-at ad; ebből kiolvassa a valóban kiszolgált súlyokat.
Nincs egyedi User-Agent: ismeretlen kliensnek a Google TTF-et ad, azt a fontTools közvetlenül olvassa.

Használat:
  python3 betu_ellenor.py "Playwrite HU" "Jost"                  # tengely: a betuk.json-ból, ha nincs benne:
                                                                  #   a Google Fonts metaadatból javasolt tengely
  python3 betu_ellenor.py "Fraunces:opsz,wght@9..144,400..900"   # kézzel megadott tengely (család:tengely)
  python3 betu_ellenor.py "Abril Fatface:"                       # üres tengely (egy súly), kézzel
  python3 betu_ellenor.py --katalogus                            # a teljes references/betuk.json újraellenőrzése
                                                                  #   (+ séma: osztaly, k5, ax, szerepek, temak megléte)
  python3 betu_ellenor.py --katalogus --jelol                    # ... és az "ellenorizve"/"hiba" mezők + dátum visszaírása
  python3 betu_ellenor.py ... --json eredmeny.json               # gépi kimenet (családonként egy rekord)
  python3 betu_ellenor.py ... --meta                             # a metaadat (kategória, subsetek, teljes súlykészlet) is

Kilépési kód: 0 = minden ok, 1 = van hibás, 2 = használati hiba. Legfeljebb 4 párhuzamos kérés.
Csak Python 3 stdlib + fontTools (ha hiányzik: pip3 install --user fonttools).
"""
import argparse
import datetime
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
except ImportError:  # pragma: no cover
    print("Hiányzik a fontTools. Telepítés: pip3 install --user fonttools", file=sys.stderr)
    sys.exit(2)

KATALOGUS = Path(__file__).resolve().parents[1] / "references" / "betuk.json"
CSS2 = "https://fonts.googleapis.com/css2?"
META_URL = "https://fonts.google.com/metadata/fonts"
MAGYAR = {0x0151: "ő", 0x0150: "Ő", 0x0171: "ű", 0x0170: "Ű"}
TEXT_PARAM = "text=" + urllib.parse.quote("".join(MAGYAR.values()))
PARHUZAMOS = 4
IDOKORLAT = 30

_META = None


# ------------------------------------------------------------------ hálózat

class Http400(Exception):
    pass


def letolt(url, probak=3):
    """GET urllib alap User-Agenttel. 400-nál Http400 (végleges), átmeneti hibánál újrapróbál."""
    utolso = None
    for i in range(probak):
        try:
            with urllib.request.urlopen(url, timeout=IDOKORLAT) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 400 or e.code == 404:
                raise Http400(f"HTTP {e.code}")
            utolso = e
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            utolso = e
        time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"hálózati hiba: {utolso}")


def css2_url(csalad, tengely, text=False):
    q = "family=" + urllib.parse.quote_plus(csalad) + (":" + tengely if tengely else "")
    return CSS2 + q + ("&" + TEXT_PARAM if text else "")


def font_face_blokkok(css):
    """[(suly_tol, suly_ig, stilus, url), ...] a css2 válaszból."""
    out = []
    for blokk in re.findall(r"@font-face\s*\{([^}]*)\}", css):
        w = re.search(r"font-weight:\s*(\d+)(?:\s+(\d+))?", blokk)
        s = re.search(r"font-style:\s*(\w+)", blokk)
        u = re.search(r"url\((https://[^)]+)\)", blokk)
        if not (w and u):
            continue
        tol = int(w.group(1))
        ig = int(w.group(2)) if w.group(2) else tol
        out.append((tol, ig, s.group(1) if s else "normal", u.group(1)))
    return out


# ------------------------------------------------------------------ metaadat (javasolt tengelyhez)

def meta():
    """A Google Fonts nyilvános metaadat-listája (család -> rekord). Csak akkor tölti le, ha kell."""
    global _META
    if _META is None:
        raw = letolt(META_URL).decode("utf-8")
        if raw.startswith(")]}'"):
            raw = raw[4:]
        _META = {f["family"]: f for f in json.loads(raw).get("familyMetadataList", [])}
    return _META


def meta_info(m):
    if not m:
        return None
    sulyok = sorted({int(k) for k in m.get("fonts", {}) if k.isdigit()})
    return {"kategoria": m.get("category"), "subsetek": [s for s in m.get("subsets", []) if s != "menu"],
            "tengelyek": {a["tag"]: [a["min"], a["max"]] for a in m.get("axes", [])},
            "sulyok": sulyok, "dolt": any(k.endswith("i") for k in m.get("fonts", {}))}


def _szam(x):
    return str(int(x)) if float(x).is_integer() else str(x)


def javasolt_tengely(m, opsz=True):
    """A metaadatból: variable -> [opsz,]wght@min..max ; statikus -> wght@a;b;c ; egy súly (400) -> ''."""
    if not m:
        return ""
    tengelyek = {a["tag"]: a for a in m.get("axes", [])}
    if "wght" in tengelyek:
        w = tengelyek["wght"]
        if opsz and "opsz" in tengelyek:
            o = tengelyek["opsz"]
            return f"opsz,wght@{_szam(o['min'])}..{_szam(o['max'])},{_szam(w['min'])}..{_szam(w['max'])}"
        return f"wght@{_szam(w['min'])}..{_szam(w['max'])}"
    sulyok = sorted({int(k) for k in m.get("fonts", {}) if k.isdigit()})
    if not sulyok or sulyok == [400]:
        return ""
    return "wght@" + ";".join(str(s) for s in sulyok)


# ------------------------------------------------------------------ ellenőrzés

def ellenoriz(csalad, tengely, meta_is=False):
    """Egy család teljes ellenőrzése. Visszaad: dict (ok, hiba, hianyzo, sulyok, ...)."""
    e = {"csalad": csalad, "tengely": tengely, "ok": False, "hiba": "", "hianyzo": [], "sulyok": [],
         "fajlok": 0}
    # 1. text= kérés: csak a négy magyar betű, kicsi TTF-ek
    try:
        css = letolt(css2_url(csalad, tengely, text=True)).decode("utf-8")
    except Http400 as x:
        e["hiba"] = f"{x}: ismeretlen család vagy érvénytelen tengely-spec"
        return e
    except Exception as x:
        e["hiba"] = str(x)
        return e
    blokkok = [b for b in font_face_blokkok(css) if b[2] == "normal"] or font_face_blokkok(css)
    if not blokkok:
        e["hiba"] = "a CSS-ben nincs letölthető betűfájl"
        return e
    # 2. cmap: minden kiszolgált fájlban (változó betűnél ugyanaz a forrás, statikusnál súlyonként más fájl)
    hianyzo = set()
    for url in dict.fromkeys(b[3] for b in blokkok):
        try:
            adat = letolt(url)
        except Exception as x:
            e["hiba"] = f"hálózati hiba: {x}" if isinstance(x, Http400) else str(x)
            return e
        try:
            cmap = TTFont(io.BytesIO(adat), lazy=True).getBestCmap() or {}
        except Exception as x:
            e["hiba"] = f"a betűfájl nem olvasható ({x})"
            return e
        e["fajlok"] += 1
        hianyzo |= {MAGYAR[k] for k in MAGYAR if k not in cmap}
    e["hianyzo"] = sorted(hianyzo, key=lambda c: "őŐűŰ".index(c))
    if hianyzo:
        e["hiba"] = "hiányzó magyar betű a Google Fonts betűfájlban (fontTools cmap): " + " ".join(e["hianyzo"])
        return e
    # 3. a teljes tengely-spec (text nélkül) is működik-e, és milyen súlyokat szolgál ki
    try:
        css_teljes = letolt(css2_url(csalad, tengely)).decode("utf-8")
    except Http400 as x:
        e["hiba"] = f"{x}: a teljes tengely-spec elutasítva"
        return e
    except Exception as x:
        e["hiba"] = str(x)
        return e
    sulyok = set()
    for tol, ig, stilus, _ in font_face_blokkok(css_teljes):
        if stilus == "normal":
            sulyok |= {tol, ig}
    e["sulyok"] = sorted(sulyok)
    if not sulyok:
        e["hiba"] = "a teljes CSS-ben nincs normál stílusú betűfájl"
        return e
    if meta_is:
        try:
            e["meta"] = meta_info(meta().get(csalad))
        except Exception as x:
            e["meta"] = {"hiba": str(x)}
    e["ok"] = True
    return e


# ------------------------------------------------------------------ katalógus

KOTELEZO = ("csalad", "tengely", "szerep", "karakter", "osztaly", "k5", "ax", "szerepek", "temak")
OSZTALYOK = {"serif", "sans", "slab", "display", "kerek", "keskeny", "kez", "script", "mono"}
K5 = ("elegans", "modern", "meresz", "baratsagos", "klasszikus")
AX = ("organikus", "puha", "harsany", "kortars", "kezi")
SZEREPEK = {"display", "body", "hand", "label"}


def katalogus_betolt():
    return json.loads(KATALOGUS.read_text(encoding="utf-8"))


def json_kompakt(data):
    """A betuk.json formája: egy betű = egy blokk, a k5 / ax / szerepek / temak egy sorban."""
    d = lambda x: json.dumps(x, ensure_ascii=False)  # noqa: E731
    sorok = ["{"] + [f" {d(k)}: {d(v)}," for k, v in data.items() if k != "betuk"] + [' "betuk": [']
    betuk = data.get("betuk", [])
    for i, b in enumerate(betuk):
        sorok.append("  {")
        kulcsok = list(b)
        sorok += [f"   {d(k)}: {d(b[k])}" + ("," if j < len(kulcsok) - 1 else "") for j, k in enumerate(kulcsok)]
        sorok.append("  }" + ("," if i < len(betuk) - 1 else ""))
    return "\n".join(sorok + [" ]", "}"]) + "\n"


def katalogus_ir(data):
    KATALOGUS.write_text(json_kompakt(data), encoding="utf-8")


def sema_hibak(data):
    """A pontozó szkripthez szükséges kulcsok és értéktartományok ellenőrzése."""
    out, latott = [], set()
    for b in data.get("betuk", []):
        c = b.get("csalad", "?")
        if c in latott:
            out.append(f"{c}: kétszer szerepel")
        latott.add(c)
        hiany = [k for k in KOTELEZO if k not in b]
        if hiany:
            out.append(f"{c}: hiányzó kulcs: {', '.join(hiany)}")
            continue
        if b["osztaly"] not in OSZTALYOK:
            out.append(f"{c}: ismeretlen osztaly: {b['osztaly']}")
        if sorted(b["k5"]) != sorted(K5) or any(not isinstance(v, int) or not 0 <= v <= 3 for v in b["k5"].values()):
            out.append(f"{c}: hibás k5")
        if sorted(b["ax"]) != sorted(AX) or any(not isinstance(v, (int, float)) or not 0 <= v <= 1
                                                for v in b["ax"].values()):
            out.append(f"{c}: hibás ax")
        if not set(b["szerepek"]) <= SZEREPEK or (b.get("ellenorizve") is not False and not b["szerepek"]):
            out.append(f"{c}: hibás szerepek: {b['szerepek']}")
        if not 2 <= len(b["temak"]) <= 6:
            out.append(f"{c}: a temak 2-6 elemű legyen")
    return out


def feladatok_argbol(argok, kat_tengely):
    """'Család' vagy 'Család:tengely' -> [(csalad, tengely, forras)]."""
    out = []
    for a in argok:
        if ":" in a:
            c, t = a.split(":", 1)
            out.append((c.strip(), t.strip(), "megadott"))
        elif a in kat_tengely:
            out.append((a, kat_tengely[a], "katalógus"))
        else:
            try:
                t = javasolt_tengely(meta().get(a))
                forras = "javasolt (metaadat)" if a in meta() else "nincs a metaadatban"
            except Exception as x:
                t, forras = "", f"metaadat nem elérhető ({x})"
            out.append((a, t, forras))
    return out


def sor(e):
    sw = e.get("sulyok") or []
    sulyok = (f"{sw[0]}–{sw[-1]}" if len(sw) > 1 else (str(sw[0]) if sw else "-"))
    alap = f"{e['csalad']!r:34} [{e['tengely']}]"
    if e["ok"]:
        txt = f"OK    {alap}  súlyok: {sulyok}  (ő Ő ű Ű megvan, {e['fajlok']} fájl)"
    else:
        txt = f"HIBA  {alap}  {e['hiba']}"
    if e.get("forras") and e["forras"] != "katalógus":
        txt += f"  <{e['forras']}>"
    m = e.get("meta")
    if m and not m.get("hiba"):
        teng = ",".join(f"{k} {_szam(v[0])}..{_szam(v[1])}" for k, v in m["tengelyek"].items())
        txt += (f"\n      meta: {m['kategoria']}; subsetek: {', '.join(m['subsetek'])}; "
                f"elérhető súlyok: {', '.join(map(str, m['sulyok']))}" + (f"; tengelyek: {teng}" if teng else "")
                + ("; van dőlt" if m["dolt"] else ""))
    return txt


def main():
    ap = argparse.ArgumentParser(description="Google Fonts magyar ő/ű + tengely-ellenőrző (fontTools cmap).")
    ap.add_argument("csaladok", nargs="*", help="'Család' vagy 'Család:tengely'")
    ap.add_argument("--katalogus", action="store_true", help="a teljes references/betuk.json újraellenőrzése")
    ap.add_argument("--jelol", action="store_true",
                    help="--katalogus mellett: az 'ellenorizve' mezők és a dátum visszaírása a betuk.json-ba")
    ap.add_argument("--json", metavar="FAJL", help="az eredmények mentése JSON-ba")
    ap.add_argument("--meta", action="store_true", help="a Google Fonts metaadat (kategória, subsetek, súlyok) is")
    ap.add_argument("--csendes", action="store_true", help="csak a hibákat és az összesítést írja ki")
    a = ap.parse_args()

    if not a.katalogus and not a.csaladok:
        ap.print_usage()
        return 2
    if a.jelol and not a.katalogus:
        print("A --jelol csak a --katalogus mellett használható.", file=sys.stderr)
        return 2

    data = katalogus_betolt() if KATALOGUS.exists() else {"betuk": []}
    kat_tengely = {b["csalad"]: b.get("tengely", "") for b in data.get("betuk", [])}
    if a.katalogus:
        feladatok = [(b["csalad"], b.get("tengely", ""), "katalógus") for b in data.get("betuk", [])]
        feladatok += feladatok_argbol(a.csaladok, kat_tengely)
    else:
        feladatok = feladatok_argbol(a.csaladok, kat_tengely)

    def egy(f):
        e = ellenoriz(f[0], f[1], meta_is=a.meta)
        e["forras"] = f[2]
        return e

    if a.meta:
        try:
            meta()  # egyszer, a szálak indulása előtt
        except Exception as x:
            print(f"A metaadat nem érhető el ({x}); --meta nélkül folytatom.", file=sys.stderr)
            a.meta = False

    with ThreadPoolExecutor(max_workers=PARHUZAMOS) as ex:
        eredmenyek = list(ex.map(egy, feladatok))

    hibasak = [e for e in eredmenyek if not e["ok"]]
    for e in eredmenyek:
        if not a.csendes or not e["ok"]:
            print(sor(e))
    print(f"\nÖsszesen {len(eredmenyek)} család: {len(eredmenyek) - len(hibasak)} ok, {len(hibasak)} hibás.")
    if hibasak:
        print("Hibásak: " + "; ".join(f"{e['csalad']} ({e['hiba']})" for e in hibasak))

    sema = sema_hibak(data) if a.katalogus else []
    if sema:
        print(f"\nSÉMA ({len(sema)} gond a betuk.json kulcsaiban):\n  " + "\n  ".join(sema))

    if a.json:
        Path(a.json).write_text(json.dumps(eredmenyek, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"JSON: {a.json}")

    if a.jelol:
        allapot = {e["csalad"]: e for e in eredmenyek}
        for b in data.get("betuk", []):
            e = allapot.get(b["csalad"])
            if not e:
                continue
            if not e["ok"] and e["hiba"].startswith("hálózati hiba"):
                continue  # átmeneti hiba: a korábbi jelölés marad
            b["ellenorizve"] = e["ok"]
            if e["ok"]:
                b.pop("hiba", None)
            else:
                b["hiba"] = e["hiba"]
        data["ellenorizve"] = datetime.date.today().isoformat()
        katalogus_ir(data)
        print(f"Visszaírva: {KATALOGUS}")
    return 1 if hibasak or sema else 0


if __name__ == "__main__":
    sys.exit(main())
