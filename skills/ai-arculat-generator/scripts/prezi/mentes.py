# -*- coding: utf-8 -*-
"""Védett mentés: a megrendelő kézi javításait a következő kör nem írja felül.

  - Minden mentés előtt biztonsági másolat: <mappa>/backup-prezik/<név>--<időbélyeg>.pptx
  - Lenyomat arról, amit a gép legutóbb kiírt (<mappa>/backup-prezik/_lenyomat.json). Ha a fájl azóta változott
    (kézzel szerkesztették), vagy nem a motor írta, a mentés MEGÁLL, és kilistázza, mely diák változtak.
    Felülírni csak a megrendelő jóváhagyásával szabad: --felulir (a biztonsági másolat akkor is elkészül).
  - Védett fájlnevek (-kezi, -sajat, -vegleges, -final, -manual): ezekbe a motor soha nem ír.
  - Google Drive-on (és más felhős meghajtón) egy MEGLÉVŐ fájl megnyitása írásra, sőt olvasásra időtúllépéssel
    elszállhat (TimeoutError: [Errno 60] Operation timed out), miközben ugyanabba a mappába új fájlt írni lehet
    (2026.10.20.). Ezért a lenyomat, a gépi másolat és a biztonsági másolat új, egyedi nevű ideiglenes fájlba íródik,
    és os.replace teszi a helyére; félkész fájl nem marad. A fájlműveletek pár másodpercig újrapróbálkoznak. Végleges
    hibánál nyers traceback helyett érthető üzenet jön, és ha a meglévő prezit nem tudja beolvasni, a biztonsági
    másolat nem készül el, vagy a prezit nem tudja kiírni, nem ír tovább (kilépési kód: 4).
    Ha a prezi kint van, és csak a lenyomat vagy a gépi másolat maradt el, kiírja a pótló parancsot:
        python3 <motor>/mentes.py potol <prezi.pptx> <lenyomat eleje>
    Ez csak akkor ír, ha a fájl még bájtra az, amit a motor kiírt, így kézi munkát soha nem jelöl tisztának.
"""
import datetime
import hashlib
import io
import json
import os
import shlex
import sys
import time
from pathlib import Path

VEDETT = ("-kezi", "-sajat", "-vegleges", "-final", "-manual")

# Ennyi másodpercig próbálja újra a fájlműveletet, ha a lemez hibát ad (Google Drive: [Errno 60]).
UJRAPROBA_MASODPERC = 8


def _ujraprobal(muvelet):
    """`muvelet()` eredménye. OSError-nál egyre hosszabb szünetekkel újrapróbálja, összesen kb.
    UJRAPROBA_MASODPERC másodpercig, aztán az utolsó hibát dobja tovább. A hiányzó fájlt nem próbálja újra."""
    kezdet = time.monotonic()
    szunet = 0.5
    while True:
        try:
            return muvelet()
        except FileNotFoundError:
            raise
        except OSError:
            if time.monotonic() - kezdet + szunet > UJRAPROBA_MASODPERC:
                raise
            time.sleep(szunet)
            szunet *= 2


def _uj_fajlba(ut, adat):
    """Bájtok egy MÉG NEM LÉTEZŐ fájlba. Az "x" mód meglévő fájlt nem nyit meg."""
    with open(str(ut), "xb") as f:
        f.write(adat)


def _ir_helyben(ut, adat):
    """A prezi a saját helyén íródik felül, hogy a Drive-on ugyanaz a fájl maradjon (megosztás, verziók)."""
    with open(str(ut), "wb") as f:
        f.write(adat)


def _atomi_iras(cel, iro):
    """A `cel` fájl vagy a régi, vagy a teljes új tartalom lesz, félkész soha. A meglévő fájlt írásra meg sem
    nyitja: `iro(ut)` egy új, egyedi nevű ideiglenes fájlt ír a cél mellé, és azt az os.replace teszi a helyére.
    Hiba esetén újrapróbálja (mindig új ideiglenes névvel), a végén OSError-t dob, ideiglenes fájlt nem hagy."""
    cel = Path(cel)

    def egyszer():
        ideiglenes = cel.with_name("%s.%s.uj" % (cel.name, os.urandom(4).hex()))
        try:
            iro(ideiglenes)
            os.replace(str(ideiglenes), str(cel))
        except BaseException:
            try:
                os.remove(str(ideiglenes))
            except OSError:
                pass
            raise
    _ujraprobal(egyszer)


def _beolvas(ut):
    return _ujraprobal(lambda: Path(ut).read_bytes())


def _hash_bajtok(adat):
    return hashlib.md5(adat).hexdigest()


def _hash(ut):
    return _hash_bajtok(_beolvas(ut))


def _hiba(e):
    """Rövid hibaszöveg, pl. "[Errno 60] Operation timed out"."""
    if isinstance(e, OSError) and e.errno and e.strerror:
        szoveg = "[Errno %d] %s" % (e.errno, e.strerror)
    else:
        szoveg = str(e) or type(e).__name__
    if isinstance(e, TimeoutError):
        szoveg += " (a meghajtó, pl. a Google Drive, nem válaszolt időben)"
    return szoveg


def _keret(*sorok):
    print("")
    print("=" * 72)
    for sor in sorok:
        print(sor)
    print("=" * 72)


def _lenyomatok(lny_ut):
    """A _lenyomat.json tartalma. Ha nincs (vagy sérült), {}. Ha van, de most nem olvasható (a Drive nem adja ki
    időben), OSError: az nem „nincs lenyomat”, hanem „nem tudom ellenőrizni”."""
    def olvas():
        return json.loads(Path(lny_ut).read_text(encoding="utf-8"))
    try:
        d = _ujraprobal(olvas)
    except (FileNotFoundError, ValueError):
        return {}
    return d if isinstance(d, dict) else {}


def _diaszovegek(ut):
    try:
        from pptx import Presentation
        prs = _ujraprobal(lambda: Presentation(str(ut)))
        return [" ".join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame).replace("\n", " ").replace("\v", " ")
                .strip() for s in prs.slides]
    except Exception:
        return []


def jelentes(ut, regi_ut):
    """Mely diák szövege változott a gép által utoljára kiírt változathoz képest."""
    uj, regi = _diaszovegek(ut), _diaszovegek(regi_ut)
    ki = []
    for i in range(max(len(uj), len(regi))):
        a = uj[i] if i < len(uj) else None
        b = regi[i] if i < len(regi) else None
        if a != b:
            ki.append((i + 1, (b or "")[:70], (a or "")[:70]))
    return ki


def _rogzit(ut, adat):
    """A mentés utolsó lépése: a gépi másolat (a kézi diff alapja) és a lenyomat, mindkettő atomian, a kiírt
    bájtokból. Nem dob hibát; visszaadja, ami elmaradt: [(mi, út, hiba), ...]."""
    ut = Path(ut)
    bk = ut.parent / "backup-prezik"
    try:
        _ujraprobal(lambda: bk.mkdir(parents=True, exist_ok=True))
    except OSError as e:
        return [("a backup-prezik mappa", bk, e)]
    hibak = []
    utolso = bk / ("_utolso-gepi--%s" % ut.name)
    try:
        _atomi_iras(utolso, lambda t: _uj_fajlba(t, adat))
    except OSError as e:
        hibak.append(("gépi másolat (a kézi diff alapja)", utolso, e))
    lny_ut = bk / "_lenyomat.json"
    try:
        lny = _lenyomatok(lny_ut)          # frissen olvasva, hogy a mappa többi prezijének lenyomata megmaradjon
        lny[ut.name] = _hash_bajtok(adat)
        szoveg = json.dumps(lny, ensure_ascii=False, indent=1).encode("utf-8")
        _atomi_iras(lny_ut, lambda t: _uj_fajlba(t, szoveg))
    except OSError as e:
        hibak.append(("lenyomat", lny_ut, e))
    return hibak


def _potlas_uzenet(ut, adat, hibak):
    parancs = "python3 %s potol %s %s" % (shlex.quote(os.path.abspath(__file__)), shlex.quote(str(ut)),
                                          _hash_bajtok(adat)[:16])
    sorok = ["A PREZI KÉSZ, DE A MENTÉS UTOLSÓ LÉPÉSE ELMARADT.",
             "  fájl: %s" % ut,
             "A prezi rendben kiíródott, azzal nincs teendő. Ez maradt el:",
             ""]
    for mi, hol, e in hibak:
        sorok.append("  - %s: %s" % (mi, hol))
        sorok.append("      hiba: %s" % _hiba(e))
    sorok.append("")
    if any(mi != "gépi másolat (a kézi diff alapja)" for mi, _h, _e in hibak):
        sorok += ["Amíg nincs pótolva, a következő mentés úgy látja, mintha kézi változás lenne a fájlban,",
                  "és megáll (biztonságos, de félrevezető)."]
    else:
        sorok += ["A mentés ettől még rendben megy, de amíg nincs pótolva, a „mi változott” lista egy régebbi",
                  "gépi változathoz hasonlít."]
    sorok += ["",
              "PÓTLÁS, amíg a fájlt senki nem nyitotta meg és nem módosította (csak akkor ír, ha a fájl még",
              "bájtra az, amit most kiírtam):",
              "",
              "  " + parancs]
    _keret(*sorok)


def ment(prs, ut, felulir=False):
    ut = Path(ut)
    if any(j in ut.stem.lower() for j in VEDETT):
        raise SystemExit("VÉDETT FÁJL (%s): ebbe a motor nem ír. Adj más nevet a gépi változatnak." % ut.name)
    bk = ut.parent / "backup-prezik"
    utolso = bk / ("_utolso-gepi--%s" % ut.name)
    masolat = None
    try:
        _ujraprobal(lambda: ut.parent.mkdir(parents=True, exist_ok=True))
    except OSError as e:
        _keret("NEM ÍRTAM SEMMIT: nem tudom létrehozni a prezi mappáját.", "", "  mappa: %s" % ut.parent,
               "  hiba: %s" % _hiba(e))
        raise SystemExit(4)
    if ut.exists():
        try:
            regi_adat = _beolvas(ut)
        except OSError as e:
            _keret("NEM ÍRTAM SEMMIT: nem tudom beolvasni a meglévő prezit, így azt sem tudom, van-e benne kézi munka.",
                   "",
                   "  fájl: %s" % ut,
                   "  hiba: %s" % _hiba(e),
                   "",
                   "Várj pár percet (nézd meg, szinkronizál-e a Google Drive), aztán futtasd újra ugyanezt a parancsot.")
            raise SystemExit(4)
        try:
            ismert, olvashatatlan = _lenyomatok(bk / "_lenyomat.json").get(ut.name), None
        except OSError as e:
            ismert, olvashatatlan = None, e
        if ismert != _hash_bajtok(regi_adat) and not felulir:
            if olvashatatlan is not None:
                print("MEGÁLLTAM: a %s lenyomatát most nem tudom beolvasni (%s), így nem tudom ellenőrizni, van-e benne "
                      "kézi munka. Úgy kezelem, mintha lenne; ha a meghajtó helyreáll, futtasd újra."
                      % (ut.name, _hiba(olvashatatlan)))
            else:
                print("MEGÁLLTAM: a %s a legutóbbi gépi mentés óta változott (kézzel szerkesztették, vagy nem a motor írta)."
                      % ut.name)
                if utolso.exists():
                    for n, regi, uj in jelentes(ut, utolso):
                        print("  %d. dia: „%s” -> „%s”" % (n, regi, uj))
            print("Vezesd át a kézi változásokat a vázlatba, és csak a megrendelő jóváhagyásával: --felulir")
            raise SystemExit(2)
        # Biztonsági másolat a beolvasott bájtokból (nem olvassuk újra a Drive-ról). Nélküle nem írunk felül.
        # Ha ugyanabban a másodpercben már készült egy, sorszámot kap: a régi másolatot nem írjuk felül.
        ido = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        masolat = bk / ("%s--%s.pptx" % (ut.stem, ido))
        n = 2
        while masolat.exists():
            masolat = bk / ("%s--%s-%d.pptx" % (ut.stem, ido, n))
            n += 1
        try:
            _ujraprobal(lambda: bk.mkdir(parents=True, exist_ok=True))
            _atomi_iras(masolat, lambda t: _uj_fajlba(t, regi_adat))
        except OSError as e:
            _keret("NEM ÍRTAM FELÜL SEMMIT: nem tudtam biztonsági másolatot készíteni, és másolat nélkül nem írok",
                   "felül prezit.",
                   "",
                   "  fájl: %s" % ut,
                   "  ide:  %s/" % bk,
                   "  hiba: %s" % _hiba(e),
                   "",
                   "Várj pár percet (nézd meg, szinkronizál-e a Google Drive), aztán futtasd újra ugyanezt a parancsot.")
            raise SystemExit(4)
    # A prezi előbb a memóriában készül: ha a gyártás elhasal, a meglévő fájlhoz nem nyúltunk, és ugyanezek a bájtok
    # mennek a lenyomatba és a gépi másolatba, a kiírt fájlt nem kell visszaolvasni a Drive-ról.
    puffer = io.BytesIO()
    prs.save(puffer)
    adat = puffer.getvalue()
    try:
        _ujraprobal(lambda: _ir_helyben(ut, adat))
    except OSError as e:
        sorok = ["NEM SIKERÜLT KIÍRNI A PREZIT.", "", "  fájl: %s" % ut, "  hiba: %s" % _hiba(e), ""]
        if masolat is not None:
            sorok += ["Ha a fájl hiányos lett vagy nem nyílik meg, az előző változat itt van:", "  %s" % masolat, ""]
        sorok += ["A lenyomatot nem frissítettem: ha a következő futás kézi változást jelez, az ez a félbemaradt írás.",
                  "Zárd be a PowerPointot, várj pár percet (nézd meg, szinkronizál-e a Google Drive), és futtasd újra."]
        _keret(*sorok)
        raise SystemExit(4)
    # A prezi már kint van: ha a lenyomat vagy a gépi másolat elakad, nem lépünk ki hibával, hanem megmondjuk, mi
    # maradt el, és hogyan pótolható.
    hibak = _rogzit(ut, adat)
    print("mentve:", ut)
    if hibak:
        _potlas_uzenet(ut, adat, hibak)
    return ut


def potol(ut, lenyomat_eleje):
    """Pótolja a ment() elmaradt utolsó lépését (gépi másolat + lenyomat). CSAK akkor ír, ha a fájl még bájtra
    az, amit a motor akkor kiírt (a lenyomata `lenyomat_eleje`-vel kezdődik). A prezihez nem nyúl.
    Visszaad: True, ha minden pótolva."""
    ut = Path(os.path.abspath(str(ut)))
    eleje = (lenyomat_eleje or "").strip().lower()
    if len(eleje) < 12:
        print("A lenyomat elejéből legalább 12 jegy kell (a mentés 16-ot ír ki).")
        return False
    try:
        adat = _beolvas(ut)
    except OSError as e:
        print("Nem tudom beolvasni: %s" % ut)
        print("  hiba: %s" % _hiba(e))
        print("Próbáld újra pár perc múlva.")
        return False
    if not _hash_bajtok(adat).startswith(eleje):
        print("NEM PÓTOLOM: a fájl már nem az, amit a motor akkor kiírt.")
        print("  %s" % ut)
        print("Ha azóta a motor újra mentette, nincs teendő. Ha kézzel szerkesztették, azt nem jelölöm tisztának:")
        print("a következő mentés megáll, és kilistázza a változásokat.")
        return False
    hibak = _rogzit(ut, adat)
    if hibak:
        print("Most sem sikerült:")
        for mi, hol, e in hibak:
            print("  - %s: %s" % (mi, hol))
            print("      hiba: %s" % _hiba(e))
        print("Próbáld újra pár perc múlva ugyanezzel a paranccsal.")
        return False
    print("Pótolva: a lenyomat és a gépi másolat a mostani fájlhoz igazodik.")
    print("  %s" % ut)
    return True


if __name__ == "__main__":
    # python3 mentes.py potol <prezi.pptx> <lenyomat eleje>
    if sys.argv[1:2] == ["potol"] and len(sys.argv) == 4:
        sys.exit(0 if potol(sys.argv[2], sys.argv[3]) else 1)
    print("használat:")
    print("  python3 mentes.py potol <prezi.pptx> <lenyomat eleje>")
    sys.exit(2)
