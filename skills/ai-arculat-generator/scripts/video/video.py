#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""video.py - az AI arculat-generátor VIDEÓ fázisa (béta). Csak Python 3 + Pillow (+ onnxruntime a kivágáshoz).

  python3 video.py elokeszit <munkamappa> [--foto <kép>] [--bovites auto|ai|tukor|vaszon|kep:<út>] [--modell rvm.onnx]
        -> video/kepek/hatter.jpg + fej.png + fej.json: az ügyfél fotója 9:16-os beszélőfejes kivágásban,
           a fej kivágva (a kivágásos és a csak-fej stílushoz). A fotó: --foto, a video/tartalom.json "foto"
           kulcsa, vagy a tokenek válogatott fotói közül az első portré.
  python3 video.py tema <munkamappa>
        -> video/video-tema.json + video/video-tokens.css az ajánlott változatokkal (előzetes)
  python3 video.py valaszto <munkamappa> [--verzio 1]
        -> video/video-toredek.html (az arculat-központ Videó füle; az `epit.py kozpont` beilleszti)
           + video/video-valaszto.html (önálló tesztoldal)
  python3 video.py vegleges <munkamappa> [--valasztas video/valasztas.json]
        -> a választásokból: video-tema.json, video-tokens.css, VIDEO-ARCULAT.md, MARKA-RESZ.md,
           arculat-video.json (a tag vágó skilljének 2.3-as blokkja és arculat.json-ja), kepek/*.png
  python3 video.py kepek <munkamappa> [--valasztas …]
        -> video/kepek/elem-*.png: a választott elemek állóképei (headless Chrome), a leíráshoz és tablóhoz
  python3 video.py minta <munkamappa> [--valasztas …] [--ki minta.mp4]
        -> 15-25 mp-es márkázott minta-videó a választott elemekből (az ügyfél fotóján, szintetizált zenével);
           Chrome + ffmpeg + websocket-client kell hozzá. Stílusbemutató, nem igazi vágás.
  python3 video.py elfogad <munkamappa>
        -> élő bemutatóhoz: minden ajánlott változat elfogadva és jóváhagyva; video/db-elfogadva.json (az arculat/video-v1
           dokumentum új tartalma, a töredék formátumában) + video/valasztas.json; utána: video.py vegleges
  python3 video.py skill <munkamappa> <a tag vágó skilljének SKILL.md-je> [--ki <mappa>]
        -> a vágó skill személyre szabott másolata: kitöltött 2.3-as arculati blokk + „Videós arculat” fejezet

A tokenek.json a webes fázis kimenete (references/tokenek-szerzodes.md); a szövegek a video/tartalom.json-ból
(references/video/tartalom.md), ha nincs, a tokenek tényeiből.
"""
import json
import subprocess
import sys
from pathlib import Path

ITT = Path(__file__).resolve().parent
sys.path.insert(0, str(ITT))


def arg(nev, alap=None):
    a = sys.argv
    return a[a.index(nev) + 1] if nev in a else alap


def portre(mappa, tok):
    tp = mappa / "video" / "tartalom.json"
    if tp.exists():
        f = json.loads(tp.read_text(encoding="utf-8")).get("foto")
        if f:
            return mappa / f
    info = (tok.get("foto") or {}).get("valogatott_info") or []
    for x in info:
        alt = (x.get("alt") or "").lower()
        if any(w in alt for w in ("portré", "mosolyog", "arc", "én ", "rólam")) or ((tok.get("marka") or {}).get("nev", "").split()[0].lower() in alt):
            return mappa / x["fajl"]
    v = (tok.get("foto") or {}).get("valogatott") or []
    return mappa / v[0] if v else None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    mod, mappa = sys.argv[1], Path(sys.argv[2]).resolve()
    tok = json.loads((mappa / "tokenek.json").read_text(encoding="utf-8"))
    (mappa / "video").mkdir(exist_ok=True)
    if mod == "elokeszit":
        foto = Path(arg("--foto")) if arg("--foto") else portre(mappa, tok)
        if not foto or not foto.exists():
            raise SystemExit("Nincs fotó: add meg a --foto kapcsolóval (egy portré, amin a vállalkozó szemből látszik).")
        cmd = [sys.executable, str(ITT / "maszk.py"), str(foto), str(mappa / "video" / "kepek")]
        for k in ("--bovites", "--modell", "--fejteto", "--fejszel", "--tema"):
            if arg(k):
                cmd += [k, arg(k)]
        subprocess.run(cmd, check=True)
    elif mod == "tema":
        import tema as TM
        import katalogus as K
        T = TM.tema(tok)
        tp = mappa / "video" / "tartalom.json"
        tart = json.loads(tp.read_text(encoding="utf-8")) if tp.exists() else {}
        T["valasztas"] = {"forras": "ajanlott", "valtozatok": K.ajanlott(tok, tart)}
        cel = mappa / "video" / "video-tema.json"
        if cel.exists() and "elemek" in json.loads(cel.read_text(encoding="utf-8")) and "--felulir" not in sys.argv:
            raise SystemExit("A video-tema.json már véglegesítve van (vegleges): nem írom felül. Újra: video.py vegleges, "
                             "vagy ha tényleg az előzetes kell: --felulir.")
        (mappa / "video" / "video-tema.json").write_text(json.dumps(T, ensure_ascii=False, indent=1), encoding="utf-8")
        (mappa / "video" / "video-tokens.css").write_text(TM.css(T), encoding="utf-8")
        print(f"KÉSZ: {mappa / 'video' / 'video-tema.json'} + video-tokens.css (ajánlott változatokkal, előzetes)")
        for m in T["betuk"]["megjegyzesek"] + T["szinek"]["megjegyzesek"]:
            print("  •", m)
    elif mod == "valaszto":
        import valaszto
        a, b, n = valaszto.epit(mappa, int(arg("--verzio", 1)))
        print(f"KÉSZ: {a}  ({n / 1024:.0f} KB)\n  + {b} (önálló teszt)")
    elif mod == "minta":
        import minta
        minta.minta(mappa, arg("--valasztas"), arg("--ki"))
    elif mod in ("vegleges", "kepek", "skill", "elfogad"):
        import leiras
        if mod == "elfogad":
            leiras.elfogad(mappa)
        elif mod == "vegleges":
            leiras.vegleges(mappa, arg("--valasztas"))
        elif mod == "kepek":
            leiras.kepek(mappa, arg("--valasztas"))
        else:
            leiras.skill(mappa, Path(sys.argv[3]), arg("--ki"))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
