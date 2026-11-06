# -*- coding: utf-8 -*-
"""PREZI-ARCULAT.md: a prezentációs arculat emberi leírása (a választott layoutok, a szabályok, „így kérj új
prezentációt”). A prezi-tema.json-ból készül; a márka-skill és minden későbbi prezi-kérés ebből indul."""
import datetime
import json
from pathlib import Path

import alap as a_
import katalogus as K

SZIN_NEV = [("primary", "Fő szín", "kiemelések, felsorolásjelek, nagy számok"),
            ("accent", "Kiemelő", "a címsor-kiemelés, a második hangsúly"),
            ("accent2", "Díszítő", "díszítések, sötét felületen a kiemelések"),
            ("paper", "Papír", "a diák alapszíne"), ("card", "Kártya", "kártyák, csempék, polaroid-keret"),
            ("ink", "Szöveg", "címek és szöveg"), ("deep", "Mély felület", "a ritmustörő diák, sötét panelek")]
SZEREP_NEV = {"cim": "Címbetű", "torzs": "Szövegbetű", "kezi": "Kézírás", "cimke": "Címke-betű"}

TIPUSOK = [
    ("cimdia", "Címdia", "kicker, cim (==kulcsszó==), alcim, fotok [2-3]"),
    ("fejezet", "Fejezetdia", "szam, kicker, cim, alcim, fotok [1-3]"),
    ("felsorolas", "Felsorolás ikonnal", "kicker, cim, pontok [[cím, leírás] × 2-4], ikon"),
    ("ket_hasab", "Kéthasábos", "kicker, vezer (a vezérgondolat), szoveg, pontok [[cím, leírás] × 3-4]"),
    ("folyamat", "Folyamat", "kicker, cim, lepesek [[ikon, cím, leírás] × 3-4]"),
    ("kartyak", "Kártyák 2 × 2", "kicker, cim, alcim, kartyak [[ikon, cím, leírás] × 4]"),
    ("szamok", "Nagy számok", "kicker, cim, szamok [[szám, címke, leírás] × 3], foto (az E változathoz)"),
    ("idezet", "Idézet fotóval", "kicker, idezet, szerzo, szerep, foto, portre, felirat"),
    ("eset", "Esettanulmány", "pill, kicker, cim, szoveg, pontok [[cím, leírás] × 2] vagy szamok [[szám, címke]], fotok"),
    ("kerdes", "Kérdés (ritmusdia)", "kicker, kerdes, alcim"),
    ("kepernyokep", "Képernyőkép magyarázattal", "kicker, cim, kep, kivagas [x0, y0, x1, y1], url, "
                                                 "pontok [[x, y, cím, leírás] × 2-4] (x, y: 0..1 a képen)"),
    ("zaro", "Záródia", "kicker, cim, alcim, url, kontaktok [[címke, érték]], fotok"),
    ("bemutatkozo", "Bemutatkozó", "kicker, cim, szoveg, kezi (kézírásos sor), foto, felirat"),
]


def iras(munkamappa, skill_ut=None):
    mm = Path(munkamappa).resolve()
    t = json.loads((mm / "prezi" / "prezi-tema.json").read_text(encoding="utf-8"))
    K.FELULIRAS.clear()
    K.FELULIRAS.update(t.get("karakter_forma") or {})
    K.NEV_FELULIRAS.clear()
    K.NEV_FELULIRAS.update(t.get("valtozat_nevek") or {})
    nev = (t.get("marka") or {}).get("nev") or ""
    jov = bool(t.get("jovahagyva"))
    v = t.get("valasztas") or {}
    aj = t.get("ajanlott") or {}
    sor = []
    sor.append("# %s · prezentációs arculat" % nev)
    sor.append("")
    sor.append("> %s · %s · a motor: `scripts/prezi/` (AI arculat-generátor), a téma: `prezi/prezi-tema.json`" % (
        "Jóváhagyva" if jov else "Ajánlott (még nincs jóváhagyva)", datetime.date.today().isoformat()))
    sor.append("")
    sor.append("Ez a leírás a márka prezentációs szabálykönyve. Minden új prezentáció ebből készül: a színek, a betűk, az ikonok "
               "és a formák a jóváhagyott webes arculatból jönnek, a diák szerkezete az alábbi választásokból.")
    sor.append("")
    sor.append("## A választott layoutok")
    sor.append("")
    kar = t.get("karakterek") or {}
    sor.append("Az 5 változat minden kategóriában a márka 5 karaktere (a márka-diagnózisból): " + ", ".join(
        "**%s** (%s)" % ((kar.get(kk) or {}).get("nev", K.KARAKTER_ALAPNEV[kk]), K.KARAKTER_ALAPNEV[kk]) for kk in K.KARAKTEREK) + ".")
    sor.append("")
    sor.append("| Kategória | Karakter | Forma | Mit jelent |")
    sor.append("|---|---|---|---|")
    for k, kn, _ in K.KATEGORIAK:
        vid = v.get(k, aj.get(k, "A"))
        kk = K.forma_karakter(k, vid)
        knev = (kar.get(kk) or {}).get("nev", K.KARAKTER_ALAPNEV.get(kk, "")) if kk else ""
        leir = next((l for i, n, l in K.valtozatok(k) if i == vid), "")
        sor.append("| %s | **%s**%s | %s · %s | %s |" % (kn, knev, " (ajánlott)" if vid == aj.get(k) else "", vid, K.nev(k, vid), leir))
    sor.append("")
    if t.get("megjegyzesek") or t.get("altalanos_megjegyzes"):
        sor.append("**Az ügyfél megjegyzései:**")
        for k, m in (t.get("megjegyzesek") or {}).items():
            for i, x in m.items():
                sor.append("- %s / %s: %s" % (K.kat_nev(k), i, x))
        if t.get("altalanos_megjegyzes"):
            sor.append("- Általános: %s" % t["altalanos_megjegyzes"])
        sor.append("")
    sor.append("## Örökölt elemek (a webes arculatból)")
    sor.append("")
    sor.append("**Színek**")
    sor.append("")
    sor.append("| Szerep | Kód | Hol |")
    sor.append("|---|---|---|")
    for k, n, h in SZIN_NEV:
        if (t.get("szinek") or {}).get(k):
            sor.append("| %s | `%s` | %s |" % (n, t["szinek"][k], h))
    sor.append("")
    sor.append("Árnyalatot a motor csak ezek keverésével képez; új színt nem vezet be. A szövegszínt minden felületen "
               "kontraszt-ellenőrzéssel választja (WCAG szerint olvasható).")
    sor.append("")
    sor.append("**Betűk** (a dián így jelennek meg; a TTF-ek a munkamappa `betuk/` mappájában)")
    sor.append("")
    for k, b in (t.get("betuk") or {}).items():
        megj = ""
        if b.get("suly_web") and b.get("suly_dian") and int(b["suly_web"]) != int(b["suly_dian"]):
            megj = " (a weben %s-as; a PowerPoint csak a normál és a félkövér vastagságot kezeli egységesen)" % b["suly_web"]
        sor.append("- %s: **%s**, %s-as%s" % (SZEREP_NEV.get(k, k), b["csalad"], b.get("suly_dian", 400), megj))
    sor.append("")
    sor.append("A betűket telepíteni kell azon a gépen, ahol a prezentációt megnyitják (Mac: dupla kattintás a TTF-en → "
               "Betű telepítése; Windows: jobb klikk → Telepítés). A motor a saját gépén ezt magától elvégzi.")
    sor.append("")
    f = t.get("forma") or {}
    sor.append("**Formák:** kártyasarok %s px, gombsarok %s px, árnyék: %s, keret: %s px." % (
        f.get("r_kartya_px"), f.get("r_gomb_px"), {"nincs": "nincs", "lagy": "lágy", "eros": "erős"}.get(f.get("arnyek"), ""),
        f.get("keret_px")))
    sor.append("")
    ik = t.get("ikon") or {}
    sor.append("**Ikonok:** %s. A vázlatban a nevükkel hivatkozz rájuk: %s. Új ikon: az ikon-előtag (`prezi-tema.json` → "
               "`ikon.elotag`) + egy angol téma-mondat, a skill ikongenerálójával." % (
                   ik.get("stilus_nev") or "", ", ".join("`%s`" % n for n in (ik.get("fajlok") or {}))))
    sor.append("")
    sor.append("**Fotók** (azonosító · leírás):")
    sor.append("")
    for x in t.get("fotok") or []:
        sor.append("- `%s` · %s%s" % (x["id"], x.get("alt", ""), " (rajz, átlátszó)" if x.get("rajz") else ""))
    sor.append("")
    fk = t.get("fotokezeles") or {}
    mot = t.get("motivum") or {}
    sor.append("**Fotókezelés a weben:** %s. **Motívum:** %s." % (
        fk.get("kezeles") or "-", ", ".join(x for x in [a_.motivum_nevek("textura", mot), a_.motivum_nevek("dekor", mot),
                                                       a_.motivum_nevek("hatar", mot)] if x) or "-"))
    sor.append("")
    sor.append("## Rögzített szabályok")
    sor.append("")
    sor.append("- 16:9 (13,333 × 7,5 hüvelyk), natív, szerkeszthető PowerPoint.")
    sor.append("- A törzsszöveg legalább 20 pontos; a kis címkék (kicker, név alatti szerep) 16-18 pontosak.")
    sor.append("- A logó mindig jobbra lent; a jobb alsó sarokba más nem kerül.")
    sor.append("- A címsor a dobozához igazodik; a kulcsszót `==így==` jelöld, a választott kiemelés (%s) rajzolódik köré." %
               K.nev("kiemeles", v.get("kiemeles", aj.get("kiemeles", "A"))))
    sor.append("- A tények (árak, nevek, számok) csak az ügyfél oldaláról, betűre. Kitalált vélemény, szám nincs.")
    sor.append("- Magyar szöveg emberi hangon: nincs hosszú gondolatjel, nincs „nem X, hanem Y”, nincs emoji.")
    sor.append("- Ritmus: a fejezet- és a kérdésdiák kapják a ritmustörő hátteret (%s)." % K.nev("hatter", v.get("hatter", "A")))
    sor.append("")
    sor.append("## Diatípusok (a vázlat mezői)")
    sor.append("")
    sor.append("| Típus | Mire | Mezők |")
    sor.append("|---|---|---|")
    for k, n, m in TIPUSOK:
        sor.append("| `%s` | %s | %s |" % (k, n, m))
    sor.append("")
    sor.append("Minden diához írható `jegyzet` (előadói jegyzet) és `hatter` (`szines` = ritmustörő, `alap`).")
    sor.append("")
    sor.append("## Így kérj új prezentációt")
    sor.append("")
    sor.append("Mondd a Claude-nak: *„Készíts prezentációt az arculatom szerint ebből a vázlatból: …”*. A Claude ilyenkor:")
    sor.append("")
    sor.append("1. a vázlatot diákra bontja, minden diához a fenti típusok közül választ (számok → `szamok`, lépések → `folyamat`, "
               "blokkváltás → `fejezet`, gondolkodtató kérdés → `kerdes`);")
    sor.append("2. megírja a `vazlat.json`-t (a minta: `prezi/tartalom.json`), a tényeket a te anyagaidból;")
    sor.append("3. legyártja: `python3 <SKILL>/scripts/prezi/prezi.py deck vazlat.json --tema %s --png`;" %
               (mm / "prezi" / "prezi-tema.json"))
    sor.append("4. megnézi a PNG-ket, javít, és csak akkor adja át, ha a gépi ellenőrzés is tiszta (a téma betűi, "
               "nincs kilógó és egymásra csúszott szöveg, a törzsszöveg legalább 20 pontos).")
    sor.append("")
    sor.append("A kézi javításaidat a következő kör nem írja felül: ha a fájlt kézzel szerkesztetted, a motor megáll, és "
               "megmutatja, mely diák változtak (a régi változat a `backup-prezik/` mappában marad).")
    sor.append("")
    sor.append("## Fájlok")
    sor.append("")
    sor.append("- `prezi/prezi-tema.json` · a téma (ebből dolgozik a motor)")
    sor.append("- `prezi/minta-deck.pptx` és `prezi/minta-deck.pdf` · a 12 minta-dia; képek: `prezi/minta-deck/`")
    sor.append("- `prezi/tartalom.json` · a minta-diák tartalma (vázlat-mintának is jó)")
    sor.append("- `prezi/prezi-toredek.html` · a Prezentáció fül az arculat-központban; `prezi/prezi-valaszto.html` · önálló változat")
    ki = mm / "prezi" / "PREZI-ARCULAT.md"
    ki.write_text("\n".join(sor) + "\n", encoding="utf-8")
    return ki
