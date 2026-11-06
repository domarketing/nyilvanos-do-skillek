#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A márka saját skillje: ARCULAT.md + <slug>-arculat/ mappa + <slug>-arculat.zip (Customize → Skills-be feltölthető).

  python3 marka_skill.py <munkamappa>            # a tokenek.json-ból (jóváhagyás előtt előzetes, utána végleges)

Bemenet a munkamappában: tokenek.json (kötelező), marka-dns.json, ikon-spec.json + ikonok/, logó, és ha van:
web/fooldal.html + web/DESIGN-RENDSZER.md, prezi/, video/, betuk/ (TTF). A márka-skill önálló: nem kell hozzá ez a
generátor, sem a DO! skilljei. Új ikonhoz a saját OpenAI-kulcs kell (az ikon-spec.json elotag-ja + egy téma-mondat).
"""
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from motor import alap  # noqa: E402

SZIN_SZEREP = [("primary", "Fő szín", "gombok, kiemelések, a márka jele"), ("accent", "Kiemelő", "második hangsúly, ikonok, díszek"),
               ("accent2", "Díszítő", "csak apró díszekben"), ("paper", "Papír", "a lap alapszíne"),
               ("card", "Kártya", "kártyák, dobozok"), ("ink", "Szöveg", "címek és szöveg"), ("deep", "Mély felület", "sötét szekciók, lábléc")]
BETU_SZEREP = [("display", "Címbetű"), ("body", "Szövegbetű"), ("hand", "Kézírás (apró akcentus)"), ("label", "Címke-betű")]
KOMP_NEV = {"cim": "Címsor-kiemelés", "alcim": "Alcím (felső címke)", "gomb": "Gomb", "kartya": "Kártya", "foto": "Fotókezelés", "mozgas": "Mozgás"}
MAX_FAJL = 8 * 1024 * 1024


def olvas(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return None


def css_tokenek(tok):
    """A web motor teljes token-készlete (ugyanaz, amiből a minta főoldal épül)."""
    sz = dict(tok.get("szinek") or {})
    p = {k: sz.get(k) for k in ("primary", "accent", "accent2", "paper", "ink", "card", "deep") if sz.get(k)}
    if sz.get("mod") == "sotet":
        p["mod"] = "sotet"
    t = alap.paletta_tokenek(p)
    b = tok.get("betuk") or {}
    beall = dict(b.get("beallitas") or {})
    bt = alap.betu_tokenek({"display": (b.get("display") or {}).get("csalad"), "body": (b.get("body") or {}).get("csalad"),
                            "hand": (b.get("hand") or {}).get("csalad"), "label": (b.get("label") or {}).get("csalad"), **beall})
    f = tok.get("forma") or {}
    sorok = [f"  {k}: {v};" for k, v in list(t.items()) + list(bt.items()) if not k.startswith("--logo")]
    sorok += [f"  --r-kartya: {f.get('r_kartya', 16)}px;", f"  --r-gomb: {f.get('r_gomb', 12)}px;"]
    css = []
    for k in ("display", "body", "hand", "label"):
        if isinstance(b.get(k), dict) and b[k].get("google_css"):
            css.append(f"@import url('{b[k]['google_css']}');")
    return "\n".join(css) + "\n:root{\n" + "\n".join(sorok) + "\n}\n"


def arculat_md(tok, dns, alap_mappa):
    m = tok.get("marka") or {}
    all_ = tok.get("allapot") or {}
    vegleges = all_.get("jovahagyva")
    sz, b, f = tok.get("szinek") or {}, tok.get("betuk") or {}, tok.get("forma") or {}
    ik, mot, komp = tok.get("ikon") or {}, tok.get("motivum") or {}, tok.get("komponensek") or {}
    dns = dns or {}
    hn = dns.get("hangnem") or {}
    if isinstance(hn, str):
        hn = {"leiras": hn}
    L = [f"# {m.get('nev', '')} · arculati kézikönyv", ""]
    L.append(("Végleges: a jóváhagyott választásokból (" + str(all_.get("datum", "")) + ").") if vegleges else
             "Előzetes: az ajánlott opciókból. A jóváhagyás után újragenerálandó.")
    L += ["", f"Weboldal: {m.get('url', '')}" + (f" · Szlogen: {m.get('szlogen')}" if m.get("szlogen") else ""), ""]
    if dns.get("igy_latunk"):
        L += ["## Így látjuk a márkát", "", dns["igy_latunk"], ""]
    L += ["## Színek", "", "| Szerep | Hexa | Mire |", "|---|---|---|"]
    L += [f"| {n} | `{sz.get(k)}` | {mi} |" for k, n, mi in SZIN_SZEREP if sz.get(k)]
    L += ["", f"Mód: {'sötét alap' if sz.get('mod') == 'sotet' else 'világos alap'}. Szöveg színes felületen: "
          f"`on_primary` = `{(tok.get('szinek_extra') or {}).get('on_primary', '')}`. Más színt ne vezess be; árnyalatot csak "
          "a papírral vagy a szöveg színével keverve képezz.", ""]
    L += ["## Betűk", "", "| Szerep | Betű | Súly | Google Fonts |", "|---|---|---|---|"]
    for k, n in BETU_SZEREP:
        x = b.get(k)
        if isinstance(x, dict):
            L.append(f"| {n} | {x['csalad']} | {x['suly']} | {x.get('google_css', '')} |")
    if b.get("beallitas"):
        L += ["", "Finomhangolás: " + ", ".join(f"{k} = {v}" for k, v in b["beallitas"].items()) + "."]
    L += ["", "Mind a négy betű ellenőrzötten tud ő, Ő, ű, Ű betűt. Más betűt ne használj.", ""]
    L += ["## Formák", "", f"- Kártya lekerekítése: {f.get('r_kartya')} px; gomb: {f.get('r_gomb')} px (999 = kapszula)",
          f"- Árnyék: {f.get('arnyek')}; keret: {f.get('keret_px')} px", ""]
    if komp:
        L += ["## Elemek", ""] + [f"- **{KOMP_NEV.get(k, k)}**: {v.get('nev', '')}. {v.get('leiras', '')}" for k, v in komp.items()] + [""]
    if ik:
        L += ["## Ikonok", "", f"Stílus: **{ik.get('stilus_nev', '')}** (technika: {ik.get('technika') or '-'}).", "",
              "Új ikon (OpenAI képmodell, átlátszó háttér, szöveg nélkül): a prompt eleje mindig ez, utána egy angol mondat a tárgyról:", "",
              "```", ik.get("elotag", ""), "```", "", "Meglévő ikonok: " + ", ".join(sorted((ik.get("fajlok") or {}).keys())), ""]
    fo = tok.get("foto") or {}
    if fo.get("kezeles"):
        L += ["## Fotók", "", f"Kezelés: **{fo['kezeles']}**. {fo.get('leiras', '')}", "",
              "Valódi arcot soha ne generálj; a saját fotók az `assets/fotok/` mappában vannak (ha átadtad).", ""]
    tema = []
    for k, n in (("textura", "Háttér-textúra"), ("dekor", "Dekor"), ("hatar", "Szekcióhatár")):
        v = mot.get(k)
        if isinstance(v, dict):
            tema.append(f"- **{n}**: {v.get('nev', '')}. {v.get('leiras', '')}")
        elif isinstance(v, list):
            tema.append(f"- **{n}**: " + "; ".join(x.get("nev", "") for x in v))
    if tema:
        L += ["## A márka saját díszítése", ""] + tema + ["", f"Saját formák (maszk-SVG): {', '.join((mot.get('formak_svg') or {}).keys())}.", ""]
    if hn or dns.get("kerulendo"):
        L += ["## Hangnem", "", hn.get("leiras", ""), ""]
        if hn.get("szavak"):
            L += ["Kulcsszavak: " + ", ".join(hn["szavak"]) + ".", ""]
        if dns.get("kerulendo"):
            L += ["Kerülendő:"] + [f"- {x}" for x in dns["kerulendo"]] + [""]
    L += ["## Szövegszabályok", "", "- Magyarul, emberi hangon, a márka hangnemében.",
          "- Nincs hosszú gondolatjel, nincs „nem X, hanem Y” szerkezet, nincs emoji, nincs üres marketing-töltelék.",
          "- A tények (árak, nevek, számok, helyszín) csak a márka saját forrásaiból.", ""]
    return "\n".join(L)


def skill_md(tok, dns, slug, van):
    m = tok.get("marka") or {}
    nev = m.get("nev", slug)
    leiras = (f"{nev} ({m.get('url', '')}) arculata: színek, betűk, ikonstílus, gombok, kártyák, fotókezelés, hangnem, kész minták. "
              f"Használd MINDIG, ha {nev} számára bármilyen vizuális anyag készül: weboldal, aloldal, landing oldal, prezentáció, "
              "közösségi poszt grafika, hírlevél, videós felirat vagy kártya, ikon. Ilyenkor ezek a színek, betűk és elemek "
              "kötelezők, és a szöveg is a márka hangnemében készül.")
    resz = [f"---\nname: {slug}-arculat\ndescription: >\n  " + leiras + "\n---\n",
            f"# {nev} arculata\n",
            "Ez a márka saját szabálykönyve. Minden új anyag ebből készül, hogy egységes legyen, akárki kéri a Claude-tól.\n",
            "## Először ezt olvasd\n",
            "1. `ARCULAT.md`: színek, betűk, formák, elemek, ikonstílus, hangnem, kerülendők.",
            "2. `tokenek.json` (gépi) és `tokenek.css` (CSS-változók, a Google Fonts betöltéssel együtt).\n",
            "## Új weboldal vagy aloldal\n"]
    if van.get("minta"):
        resz.append("Indulj a `minta/fooldal.html`-ből: abban már benne vannak a márka tokenjei és a jóváhagyott elemek "
                    "(gomb, kártya, címsor, alcím, fotó, textúra, dekor, határ) CSS-e. Az új oldal ugyanezeket az osztályokat és "
                    "változókat használja, csak a tartalom és a szekciók változnak. A `minta/DESIGN-RENDSZER.md` leírja az elemeket.\n")
    else:
        resz.append("Használd a `tokenek.css` változóit (`--c-primary`, `--f-display`…), és az `ARCULAT.md` elemleírásait.\n")
    resz.append("Ikonok: az `assets/ikonok/` meglévő ikonjai. Új ikonhoz az `ikon-spec.json` stílusa (elotag) + egy angol "
                "téma-mondat, átlátszó háttérrel, szöveg nélkül (OpenAI képmodell, saját kulccsal).\n")
    resz.append("## Új prezentáció\n")
    if van.get("prezi"):
        resz.append("A `prezi/` mappában a jóváhagyott prezentációs téma (`prezi-tema.json`), a leírása (`PREZI-ARCULAT.md`) "
                    "és egy önálló motor. Új prezentáció egy vázlatból (a diatípusok a `PREZI-ARCULAT.md`-ben):\n\n"
                    "```bash\npython3 <ennek a skillnek a mappája>/prezi/motor/prezi.py deck vazlat.json "
                    "--tema <ennek a skillnek a mappája>/prezi/prezi-tema.json --png\n```\n\n"
                    "A motor a márka betűit magától telepíti; a PDF-hez és a PNG-előnézethez LibreOffice kell.\n")
    else:
        resz.append("A színeket, betűket és az ikonstílust az `ARCULAT.md` szerint használd; 16:9, legalább 20 pt szöveg, "
                    "logó jobbra lent. (A prezentációs arculat még nem készült el.)\n")
    resz.append("## Videó\n")
    if van.get("video"):
        resz.append("A `video/` mappában a videós arculat (`VIDEO-ARCULAT.md`, `video-tema.json`, `video-tokens.css`). "
                    "Videóvágáshoz a vágó skilled kell (a tananyagból telepített vágórendszer): a `video/MARKA-RESZ.md` "
                    "tartalmát a vágó skill „A TE ARCULATOD” blokkjába illeszd, és onnantól minden videó ebben a stílusban készül.\n")
    else:
        resz.append("A videós arculat még nem készült el; addig a színek és a betűk az `ARCULAT.md` szerint.\n")
    resz += ["## Ellenőrzés leadás előtt\n",
             "- Csak a márka színei és betűi szerepelnek (új szín, új betű nincs).",
             "- Minden ő, ű jól jelenik meg; a szöveg és a háttér kontrasztja olvasható.",
             "- Az ikonok egy stílusban vannak, átlátszó háttérrel, szöveg nélkül.",
             "- A szöveg a márka hangnemében van, a tények a márka saját forrásaiból.\n"]
    return "\n".join(resz)


def masol(forras, cel):
    if forras.is_dir():
        for p in forras.rglob("*"):
            if p.is_file() and p.stat().st_size <= MAX_FAJL and "__pycache__" not in p.parts and not p.name.startswith("."):
                q = cel / p.relative_to(forras)
                q.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, q)
    elif forras.is_file():
        cel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(forras, cel)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    mappa = Path(sys.argv[1]).resolve()
    tok = olvas(mappa / "tokenek.json")
    if not tok:
        raise SystemExit("Nincs tokenek.json: előbb `epit.py kozpont` vagy `tokenek.py`.")
    dns = olvas(mappa / "marka-dns.json")
    slug = (tok.get("marka") or {}).get("slug") or "marka"
    (mappa / "ARCULAT.md").write_text(arculat_md(tok, dns, mappa), encoding="utf-8")

    cel = mappa / f"{slug}-arculat"
    if cel.exists():
        shutil.rmtree(cel)
    cel.mkdir()
    van = {"minta": (mappa / "web" / "fooldal.html").exists() or (mappa / "fooldal.html").exists(),
           "prezi": (mappa / "prezi" / "prezi-tema.json").exists(), "video": (mappa / "video" / "MARKA-RESZ.md").exists()}
    (cel / "SKILL.md").write_text(skill_md(tok, dns, slug, van), encoding="utf-8")
    shutil.copy2(mappa / "ARCULAT.md", cel / "ARCULAT.md")
    t2 = dict(tok)
    t2.pop("alap", None)
    (cel / "tokenek.json").write_text(json.dumps(t2, ensure_ascii=False, indent=2), encoding="utf-8")
    (cel / "tokenek.css").write_text(css_tokenek(tok), encoding="utf-8")
    if dns:
        (cel / "marka-dns.json").write_text(json.dumps(dns, ensure_ascii=False, indent=2), encoding="utf-8")
    lg = tok.get("logo") or {}
    for k in ("szines", "feher"):
        if lg.get(k) and (mappa / lg[k]).exists():
            masol(mappa / lg[k], cel / "assets" / "logo" / f"logo-{k}{Path(lg[k]).suffix}")
    ik = tok.get("ikon") or {}
    for nev, rel in (ik.get("fajlok") or {}).items():
        masol(mappa / rel, cel / "assets" / "ikonok" / f"{nev}.png")
    isp = olvas(mappa / "ikon-spec.json")
    if isp and ik:
        isp["stilusok"] = [s for s in isp.get("stilusok", []) if s.get("id") == ik.get("stilus_id")]
        isp["mappa"] = "assets/ikonok"
        (cel / "ikon-spec.json").write_text(json.dumps(isp, ensure_ascii=False, indent=2), encoding="utf-8")
    for rel in ((tok.get("betuk") or {}).get(k, {}) or {} for k in ("display", "body", "hand", "label")):
        for t in (rel.get("ttf") or []) if isinstance(rel, dict) else []:
            masol(mappa / t, cel / "assets" / "betuk" / Path(t).name)
    for f in ("web/fooldal.html", "fooldal.html"):
        if (mappa / f).exists():
            masol(mappa / f, cel / "minta" / "fooldal.html")
            break
    for f in ("web/DESIGN-RENDSZER.md", "DESIGN-RENDSZER.md"):
        if (mappa / f).exists():
            masol(mappa / f, cel / "minta" / "DESIGN-RENDSZER.md")
            break
    # prezentáció: önálló csomag a prezi-motorral (téma + motor + betűk + ikonok + fotók + logó + leírás)
    if (mappa / "prezi" / "prezi-tema.json").exists():
        import subprocess
        prezi_py = Path(__file__).resolve().parent / "prezi" / "prezi.py"
        r = subprocess.run([sys.executable, str(prezi_py), "csomag", str(mappa), str(cel / "prezi")],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("  ! a prezi-csomag nem készült el, csak a téma és a leírás megy át:", (r.stderr or r.stdout)[-300:])
            for f in ("prezi-tema.json", "PREZI-ARCULAT.md"):
                masol(mappa / "prezi" / f, cel / "prezi" / f)
    # videó: a márka-rész és a téma (a vágó skill a tananyagból jön, ahhoz illeszthető)
    for f in ("video-tema.json", "video-tokens.css", "VIDEO-ARCULAT.md", "MARKA-RESZ.md", "kepek/tablo-valasztott.jpg"):
        if (mappa / "video" / f).exists():
            masol(mappa / "video" / f, cel / "video" / f)

    zip_ut = mappa / f"{slug}-arculat.zip"
    with zipfile.ZipFile(zip_ut, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(cel.rglob("*")):
            if p.is_file():
                z.write(p, Path(cel.name) / p.relative_to(cel))
    n = sum(1 for p in cel.rglob("*") if p.is_file())
    print(f"KÉSZ: {mappa / 'ARCULAT.md'}\n  + {cel}/ ({n} fájl)\n  + {zip_ut} ({zip_ut.stat().st_size / 1024 / 1024:.1f} MB)")
    print("  " + ("végleges (jóváhagyott tokenekből)" if (tok.get("allapot") or {}).get("jovahagyva") else
                  "ELŐZETES: a tokenek még az ajánlott opciókból vannak; jóváhagyás után futtasd újra"))


if __name__ == "__main__":
    main()
