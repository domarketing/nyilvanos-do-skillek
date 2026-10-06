#!/usr/bin/env python3
"""A skillek ellenőrzése feltöltés előtt.

Megnézi, hogy minden skill átmegy-e a claude.ai skill-feltöltő szabályain
(név, leírás hossza, XML-tag tilalom), és hogy nem maradt-e benne belső adat:
mérőkód, API-kulcs, belső név vagy cím.

Használat:
    python scripts/ellenor.py            # az összes skill a skills/ mappában
    python scripts/ellenor.py skills/x   # csak egy skill
Hiba esetén 1-es kilépési kóddal áll meg.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

MAX_DESC = 1024          # karakter ÉS bájt (UTF-8), hogy mindkét számolás szerint beférjen
MAX_NAME = 64
ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}

# Belső adatok, amiknek egyik skillben sem szabad maradniuk.
TILTOTT = [
    (r"AW-\d{6,}", "Google Ads mérőkód"),
    (r"\bGTM-[A-Z0-9]{4,}", "Google Tag Manager azonosító"),
    (r"\bG-[A-Z0-9]{8,}\b", "Google Analytics azonosító"),
    (r"\bUA-\d{4,}-\d+", "Google Analytics azonosító"),
    (r"fbq\(\s*['\"]init['\"]", "Facebook pixel"),
    (r"pysOptions|PixelYourSite", "PixelYourSite mérőkód"),
    (r"(?i)(api[_-]?key|token|secret)\s*[=:]\s*['\"][A-Za-z0-9_\-]{20,}['\"]", "beégetett kulcs"),
    (r"\bsk-[A-Za-z0-9_\-]{20,}", "OpenAI-kulcs"),
    (r"(?i)hostingersite\.com|domarketing\.hu/wp-admin", "belső WordPress-cím"),
    (r"(?i)@domarketing\.hu", "belső e-mail-cím"),
    (r"(?i)#0046c7|#1ae4be|#081e47", "DO!-márkaszín (semleges alapszín kell)"),
    (r"(?i)\bdomarketing[:\-](?=[a-z])", "belső plugin- vagy skillhivatkozás"),
]

# Belső nevek: a skillek szövegében nem maradhatnak. Kivétel a feliratkozo-oldal
# mintái, mert azok a DO! saját, nyilvános oldalai (ez döntés volt).
# A domarketing.hu/plugin a Claude Oldalak bővítmény nyilvános letöltőoldala, arra hivatkozhatnak.
BELSO_NEVEK = r"(?i)\b(do!\s?marketing|domarketing(?!\.hu/plugin)|zsolt|domi\b|orsi\b|uvf\+?|belső kör|mastermind)"
MINTA_KIVETEL = {"feliratkozo-oldal/samples", "ertekesitesi-level-iro/references/email-mintak.md"}

SZOVEG = {".md", ".py", ".html", ".css", ".js", ".json", ".txt", ".yml", ".yaml"}


def frontmatter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None
    fm, kulcsok, aktualis = {}, [], None
    for sor in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", sor)
        if km:
            aktualis = km.group(1)
            kulcsok.append(aktualis)
            fm[aktualis] = km.group(2)
        elif aktualis and sor.startswith((" ", "\t")):
            fm[aktualis] += "\n" + sor
    return fm, kulcsok


def leiras_szoveg(nyers):
    nyers = nyers.strip()
    if nyers[:1] in (">", "|"):
        sorok = [s.strip() for s in nyers.splitlines()[1:]]
        return " ".join(s for s in sorok if s)
    if nyers[:1] in ("'", '"') and nyers[-1:] == nyers[:1]:
        return nyers[1:-1]
    return " ".join(s.strip() for s in nyers.splitlines())


def ellenoriz(mappa):
    hibak = []
    skill_md = mappa / "SKILL.md"
    if not skill_md.exists():
        return [f"{mappa.name}: nincs SKILL.md"]
    t = skill_md.read_text(encoding="utf-8")
    eredmeny = frontmatter(t)
    if not eredmeny:
        return [f"{mappa.name}: a SKILL.md nem YAML-fejléccel (---) kezdődik"]
    fm, kulcsok = eredmeny
    for k in kulcsok:
        if k not in ALLOWED_KEYS:
            hibak.append(f"{mappa.name}: nem engedett fejléc-kulcs: {k}")
    nev = fm.get("name", "").strip()
    if nev != mappa.name:
        hibak.append(f"{mappa.name}: a name ({nev!r}) nem egyezik a mappa nevével")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", nev) or len(nev) > MAX_NAME:
        hibak.append(f"{mappa.name}: a name csak kisbetű, szám és kötőjel lehet, max. {MAX_NAME} karakter")
    d = leiras_szoveg(fm.get("description", ""))
    if not d:
        hibak.append(f"{mappa.name}: hiányzik a description")
    if len(d) > MAX_DESC or len(d.encode("utf-8")) > MAX_DESC:
        hibak.append(f"{mappa.name}: a description {len(d)} karakter / {len(d.encode())} bájt (max. {MAX_DESC})")
    if "<" in d or ">" in d:
        hibak.append(f"{mappa.name}: a description nem tartalmazhat < vagy > jelet (XML-tagnek veszi a feltöltő)")
    if (mappa / ".claude-plugin").exists():
        hibak.append(f"{mappa.name}: a skill mappájában nem lehet .claude-plugin")

    for f in mappa.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in SZOVEG:
            continue
        rel = f.relative_to(SKILLS).as_posix()
        szoveg = f.read_text(encoding="utf-8", errors="replace")
        for minta, mi in TILTOTT:
            for m in re.finditer(minta, szoveg):
                sor = szoveg.count("\n", 0, m.start()) + 1
                hibak.append(f"{rel}:{sor}: {mi}: {m.group(0)[:60]!r}")
        if not any(rel.startswith(k) for k in MINTA_KIVETEL):
            for m in re.finditer(BELSO_NEVEK, szoveg):
                sor = szoveg.count("\n", 0, m.start()) + 1
                hibak.append(f"{rel}:{sor}: belső név: {m.group(0)!r}")
    return hibak


def main():
    if len(sys.argv) > 1:
        mappak = [Path(a).resolve() for a in sys.argv[1:]]
    else:
        mappak = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    osszes = []
    for m in mappak:
        h = ellenoriz(m)
        osszes += h
        print(f"{'OK ' if not h else 'HIBA'} {m.name}" + (f" ({len(h)})" if h else ""))
    if osszes:
        print()
        for h in osszes:
            print("  " + h)
        sys.exit(1)


if __name__ == "__main__":
    main()
