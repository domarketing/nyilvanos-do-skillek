# -*- coding: utf-8 -*-
"""A prezi-motor betűi: letöltés a Google Fonts-ról, PowerPoint-név, telepítés, mérés.

A PowerPoint egy betűcsaládból megbízhatóan csak a normál és a félkövér vastagságot kezeli. A köztes súlyok (500, 600,
800) a TTF-ben külön családnévként szerepelnek („Brygada 1918 SemiBold”): ezt a PowerPoint Windowson megtalálja, a
LibreOffice Macen viszont normál vastagsággal rajzolja. Ezért a szerepek így képződnek le:
    a jóváhagyott súly <= 500 -> normál (400),  >= 550 -> félkövér (700, ha a családnak van ilyen).
A szövegmérés mindig azzal a TTF-fel történik, amelyik a dián tényleg megjelenik.

A betűknek telepítve kell lenniük, különben a PowerPoint és a LibreOffice másikat tesz a helyükre (a LibreOffice
Macen a saját profiljából nem tölt betűt). Telepítés a felhasználói betűmappába:
    Mac: ~/Library/Fonts · Windows: %LOCALAPPDATA%/Microsoft/Windows/Fonts + HKCU regisztráció · Linux: ~/.local/share/fonts
"""
import os
import re
import shutil
import struct
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SZEREPEK = ("cim", "torzs", "kezi", "cimke")
TOKEN_SZEREP = {"cim": "display", "torzs": "body", "kezi": "hand", "cimke": "label"}


# ------------------------------------------------------------------ TTF-fejléc (függőség nélkül)

_INFO = {}


def ttf_info(ut):
    """Nevek és függőleges metrikák egy TTF/OTF-ből: family (nameID 1), style (2), full (4), ps (6), typo_family (16),
    upm, ascent, descent, linegap (typo, ha a USE_TYPO_METRICS be van kapcsolva, különben hhea), cap, weight.
    Csak a szükséges táblákat olvassa be (sok telepített betűnél is gyors)."""
    ut = str(ut)
    kulcs = (ut, os.path.getmtime(ut))
    if kulcs in _INFO:
        return _INFO[kulcs]
    with open(ut, "rb") as f:
        fej = f.read(12)
        if fej[:4] == b"ttcf":
            raise ValueError("TTC gyűjteményt nem kezelünk: %s" % ut)
        n = struct.unpack(">H", fej[4:6])[0]
        kat = f.read(16 * n)
        t = {}
        for i in range(n):
            tag, _, off, hossz = struct.unpack(">4sIII", kat[16 * i: 16 * i + 16])
            t[tag.decode("latin-1")] = (off, hossz)

        def tabla(nev):
            if nev not in t:
                return None
            f.seek(t[nev][0])
            return f.read(t[nev][1])

        ki = {"ut": ut}
        nt = tabla("name") or b""
        nevek = {}
        if nt:
            _, db, tarolo = struct.unpack(">HHH", nt[:6])
            for i in range(db):
                p, e, l, nid, hossz, ofs = struct.unpack(">HHHHHH", nt[6 + 12 * i: 18 + 12 * i])
                nyers = nt[tarolo + ofs: tarolo + ofs + hossz]
                if p == 3 and l in (0x409, 0):
                    nevek[nid] = nyers.decode("utf-16-be", "replace")
                elif p == 1 and nid not in nevek:
                    nevek[nid] = nyers.decode("mac_roman", "replace")
        ki.update(family=nevek.get(1), style=nevek.get(2), full=nevek.get(4), ps=nevek.get(6), typo_family=nevek.get(16))
        head = tabla("head")
        ki["upm"] = struct.unpack(">H", head[18:20])[0] if head else 1000
        hh = tabla("hhea")
        asc, desc, gap = struct.unpack(">hhh", hh[4:10]) if hh else (800, -200, 0)
        os2 = tabla("OS/2")
        if os2 and len(os2) >= 78:
            ki["weight"] = struct.unpack(">H", os2[4:6])[0]
            fs = struct.unpack(">H", os2[62:64])[0]
            ta, td, tg = struct.unpack(">hhh", os2[68:74])
            if fs & (1 << 7):
                asc, desc, gap = ta, td, tg
            ki["cap"] = struct.unpack(">h", os2[88:90])[0] if len(os2) >= 90 else int(0.7 * ki["upm"])
        else:
            ki["weight"], ki["cap"] = 400, int(0.7 * ki["upm"])
    ki.update(ascent=asc, descent=desc, linegap=gap)
    _INFO[kulcs] = ki
    return ki


def ttf_cmap_ellenor(ut, karakterek="őűŐŰáéíóöüú"):
    """Igaz, ha a betűben megvan az összes megadott karakter (a PIL-lel ellenőrizve, ha elérhető)."""
    try:
        from PIL import ImageFont
        f = ImageFont.truetype(str(ut), 40)
        ures = f.getmask("\uffff").getbbox()
        for k in karakterek:
            if f.getmask(k).getbbox() is None or f.getmask(k).getbbox() == ures:
                return False
        return True
    except Exception:
        return True


# ------------------------------------------------------------------ letöltés

def ttf_letolt(csalad, suly, cel):
    """Egy súly TTF-je a Google Fonts-ról (ismeretlen kliensnek TTF-et ad). Visszaad: Path, vagy None, ha a
    családnak nincs ilyen súlya, vagy nincs hálózat."""
    cel = Path(cel)
    p = cel / ("%s-%d.ttf" % (csalad.replace(" ", ""), int(suly)))
    if p.exists() and p.stat().st_size > 1000:
        return p
    css = None
    for q in ("family=%s:wght@%d" % (urllib.parse.quote_plus(csalad), int(suly)),
              "family=%s" % urllib.parse.quote_plus(csalad)):
        try:
            css = urllib.request.urlopen("https://fonts.googleapis.com/css2?" + q, timeout=25).read().decode("utf-8")
            break
        except Exception:
            css = None
    if not css:
        return None
    for blokk in re.findall(r"@font-face\s*\{([^}]*)\}", css):
        w = re.search(r"font-weight:\s*(\d+)", blokk)
        u = re.search(r"url\((https://[^)]+\.ttf)\)", blokk)
        if not (w and u) or "italic" in blokk or int(w.group(1)) != int(suly):
            continue
        try:
            cel.mkdir(parents=True, exist_ok=True)
            p.write_bytes(urllib.request.urlopen(u.group(1), timeout=40).read())
            return p
        except Exception as e:
            print("  ! %s: letöltési hiba (%s)" % (p.name, e))
            return None
    return None


# ------------------------------------------------------------------ szerepek -> PowerPoint

def _helyi_ttf(blokk, suly, alap):
    for rel in blokk.get("ttf") or []:
        p = Path(rel) if os.path.isabs(rel) else Path(alap) / rel
        m = re.search(r"-(\d{3})\.ttf$", p.name)
        if p.exists() and m and int(m.group(1)) == int(suly):
            return p
    return None


def szerep_betu(blokk, szerep, alap, cel_mappa):
    """Egy token-betűblokkból (display/body/hand/label) a dián használt betű:
    {csalad, suly_web, typeface, bold, ttf, ttf_b, ttf_b_typeface, ttf_b_bold}. A hiányzó TTF-eket letölti."""
    csalad = blokk["csalad"]
    suly_web = int(blokk.get("suly") or 400)
    if szerep == "cim":
        akar_felkover = suly_web >= 550
    else:
        akar_felkover = False

    def beszerez(w):
        return _helyi_ttf(blokk, w, alap) or ttf_letolt(csalad, w, cel_mappa)

    normal = beszerez(400)
    if normal is None:                   # pl. csak 300-as vagy csak egy súlyú család
        for w in sorted(blokk.get("sulyok") or [suly_web], key=lambda x: abs(x - 400)):
            normal = beszerez(w)
            if normal:
                break
    felkover = beszerez(700)
    ki = {"csalad": csalad, "suly_web": suly_web, "szerep": szerep}
    if akar_felkover and felkover:
        fi = ttf_info(felkover)
        ki.update(typeface=fi["family"], bold=(fi["style"] or "").lower().startswith("bold"), ttf=str(felkover), suly_dian=700)
    elif akar_felkover:
        # nincs 700-as: a legnehezebb meglévő súly, a saját (régi) családnevén
        for w in (600, 800, 500, 900):
            p = beszerez(w)
            if p:
                fi = ttf_info(p)
                ki.update(typeface=fi["family"], bold=False, ttf=str(p), suly_dian=w,
                          figyelem="A %s családnak nincs 700-as súlya: a dián a %d-as szerepel, saját családnéven." % (csalad, w))
                break
    if "ttf" not in ki:
        if normal is None:
            raise RuntimeError("Nem sikerült letölteni a(z) %s betű TTF-jét (hálózat?)." % csalad)
        fi = ttf_info(normal)
        ki.update(typeface=fi["family"], bold=False, ttf=str(normal), suly_dian=fi.get("weight", 400))
    # félkövér futam (pl. kiemelt szó a törzsszövegben): a család 700-asa, ha van
    if felkover:
        fb = ttf_info(felkover)
        ki["ttf_b"] = str(felkover)
        ki["b_typeface"] = fb["family"]
    else:
        ki["ttf_b"] = ki["ttf"]
        ki["b_typeface"] = ki["typeface"]
    fi = ttf_info(ki["ttf"])
    ki["metrika"] = {k: fi[k] for k in ("upm", "ascent", "descent", "linegap", "cap")}
    ki["ps"] = sorted({ttf_info(p)["ps"] for p in {ki["ttf"], ki["ttf_b"]} if p})
    return ki


# ------------------------------------------------------------------ telepítés

def betumappa():
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Fonts"
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "Microsoft" / "Windows" / "Fonts"
    return Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))) / "fonts"


def telepitve(ps_nev, mappa=None):
    """Van-e már ilyen PostScript-nevű betű a felhasználói (vagy rendszer-) betűmappákban."""
    mappak = [mappa or betumappa()]
    if sys.platform == "darwin":
        mappak += [Path("/Library/Fonts")]
    elif os.name == "nt":
        mappak += [Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"]
    else:
        mappak += [Path("/usr/share/fonts"), Path("/usr/local/share/fonts")]
    for m in mappak:
        if not m.exists():
            continue
        for p in list(m.glob("*.ttf")) + list(m.glob("*.otf")) + list(m.glob("*/*.ttf")):
            try:
                if p.stem.replace(" ", "").lower() == ps_nev.lower() or ttf_info(p).get("ps") == ps_nev:
                    return p
            except Exception:
                continue
    return None


def telepit(ttf_utak, csendes=False):
    """A TTF-eket a felhasználói betűmappába másolja (ha még nincsenek ott). Visszaad: [újonnan telepített]."""
    mappa = betumappa()
    mappa.mkdir(parents=True, exist_ok=True)
    uj = []
    for ut in dict.fromkeys(str(u) for u in ttf_utak if u):
        info = ttf_info(ut)
        if telepitve(info["ps"], mappa):
            continue
        cel = mappa / Path(ut).name
        if cel.exists():
            cel = mappa / (info["ps"] + ".ttf")
        shutil.copyfile(ut, cel)
        uj.append(cel)
        if os.name == "nt":
            try:
                import winreg
                k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts", 0,
                                   winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, "%s (TrueType)" % (info["full"] or info["ps"]), 0, winreg.REG_SZ, str(cel))
                winreg.CloseKey(k)
            except Exception as e:
                print("  ! a betű regisztrációja nem sikerült (%s): %s" % (cel.name, e))
    if uj and sys.platform.startswith("linux") and shutil.which("fc-cache"):
        subprocess.run(["fc-cache", "-f", str(mappa)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if uj and not csendes:
        print("  betűk telepítve (%s): %s" % (mappa, ", ".join(p.name for p in uj)))
    return uj
