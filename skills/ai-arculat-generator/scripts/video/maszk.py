#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Álló (9:16) háttérkép és fejkivágás a videós előnézetekhez, egy fotóból.

  python3 maszk.py <foto> <kimeneti-mappa> [--fejteto 560] [--fejszel 430] [--szel 900] [--modell rvm.onnx]
                   [--bovites auto|ai|tukor|vaszon|kep:<út>]

A fotót beszélőfejes kivágásba teszi: a fejtető a színpadon kb. 560 px-en, a fej kb. 430 px széles, hogy a
fej fölött legyen hely a grafikának (Reels felső sáv: 230 px). Ha a fotó ehhez nem elég magas (szoros
portré), a felső sávot ki kell egészíteni: --bovites ai (az OpenAI képszerkesztője festi tovább a hátteret,
maszkkal, a fotó eredeti része pixelre változatlan marad; ~20-60 mp, pár forint), --bovites tukor (a kép felső,
fej nélküli sávja tükrözve, felfelé egyre jobban elmosva, kulcs nélkül), --bovites auto (alap: ai, ha van
OpenAI-kulcs és sikerül, különben tükör). Ha a szkriptnek nincs kulcsa, de a Claude-nak van képszerkesztő
eszköze: --bovites vaszon kiírja a vaszon-ai.png-t (864×1536, a kitöltendő rész átlátszó; ez a maszk is),
a kész képpel pedig --bovites kep:<út> fejezi be (a valódi fotó pixelre visszakerül).

Kimenet (a kimeneti mappában):
  hatter.jpg     a 9:16-os háttér (szel × szel·16/9)
  fej.png        csak a fej (átlátszó háttér), ugyanabban a méretben levágva a fej dobozára
  fej.json       {"meret": [w, h], "fej_doboz": [x, y, w, h], "fejteto": y, "fej_x": [x0, x1], "all": y,
                  "modszer": "rvm|arc", "megjegyzes"}  - a koordináták az 1080×1920-as színpadon

A kivágás sorrendje:
  1. RVM (Robust Video Matting, onnxruntime, CPU): a modellt a --modell, az RVM_MODELL környezeti változó,
     a ~/.cache/ai-arculat/ vagy a skill assets/video/ mappájából veszi; ha nincs, letölti a kis
     (mobilenetv3, ~15 MB) változatot a hivatalos GitHub-kiadásból.
  2. Ha nincs onnxruntime vagy hálózat: arcfelismerés (OpenCV Haar, a cv2 csomag része) és egy lágy szélű
     ellipszis a fej köré. Durvább, de a kis előnézetekben elég; a fej.json "modszer": "arc" jelzi.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

RVM_URL = "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx"
SKILL = Path(__file__).resolve().parents[2]


def arg(nev, alap=None):
    a = sys.argv
    return a[a.index(nev) + 1] if nev in a else alap


def pozicio(p):
    """CSS-szerű fókuszpont: '50% 26%' -> (0.5, 0.26)."""
    try:
        x, y = [float(v.strip().rstrip("%")) / 100 for v in (p or "50% 35%").split()[:2]]
        return min(max(x, 0), 1), min(max(y, 0), 1)
    except Exception:
        return 0.5, 0.35


def vag_9x16(im, fx, fy, szel):
    """object-fit: cover + object-position, ahogy a böngésző csinálja."""
    W, H = im.size
    cel = 9 / 16
    if W / H > cel:                       # túl széles: oldalt vágunk
        w, h = round(H * cel), H
    else:                                 # túl magas: fent/lent vágunk
        w, h = W, round(W / cel)
    x = round((W - w) * fx)
    y = round((H - h) * fy)
    return im.crop((x, y, x + w, y + h)).resize((szel, round(szel * 16 / 9)), Image.LANCZOS)


def modell_ut(kert=None):
    jelolt = [kert, os.environ.get("RVM_MODELL"),
              Path.home() / ".cache/ai-arculat/rvm_mobilenetv3_fp32.onnx",
              Path.home() / ".cache/ai-arculat/rvm_resnet50_fp32.onnx",
              SKILL / "assets/video/rvm_mobilenetv3_fp32.onnx"]
    for j in jelolt:
        if j and Path(j).exists():
            return Path(j)
    cel = Path.home() / ".cache/ai-arculat/rvm_mobilenetv3_fp32.onnx"
    try:
        cel.parent.mkdir(parents=True, exist_ok=True)
        print("  RVM-modell letöltése (~15 MB)…")
        req = urllib.request.Request(RVM_URL, headers={"User-Agent": "ai-arculat-generator/1.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(cel, "wb") as f:
            f.write(r.read())
        return cel
    except Exception as e:
        print(f"  ! az RVM-modell nem tölthető le ({e}); arcfelismeréssel becsülök")
        return None


def rvm_alfa(rgb, modell):
    import onnxruntime as ort
    sess = ort.InferenceSession(str(modell), providers=["CPUExecutionProvider"])
    src = (np.asarray(rgb).astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
    rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
    dr = np.array([0.4], np.float32)
    pha = None
    for _ in range(3):                    # állóképen a visszacsatolt állapot pontosít
        out = sess.run(None, {"src": src, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3],
                              "downsample_ratio": dr})
        pha, rec = out[1], out[2:6]
    return np.clip(pha[0, 0], 0, 1)


def arc_alfa(rgb):
    import cv2
    g = cv2.cvtColor(np.asarray(rgb), cv2.COLOR_RGB2GRAY)
    cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    arcok = cas.detectMultiScale(g, 1.1, 6, minSize=(80, 80))
    H, W = g.shape
    a = np.zeros((H, W), np.float32)
    if len(arcok) == 0:
        return a
    x, y, w, h = max(arcok, key=lambda r: r[2] * r[3])
    cx, cy = x + w / 2, y + h * 0.42     # a haj miatt a fej közepe az arc közepe fölött van
    rx, ry = w * 0.62, h * 0.86
    yy, xx = np.mgrid[0:H, 0:W]
    d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    a[d <= 1] = 1
    return np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))) / 255.0


def fej_meres(alfa):
    """A fejtető, a fej szélessége és az áll becslése a maszkból (1080×1920-as színpad-koordinátákban)."""
    H, W = alfa.shape
    sorok = np.where((alfa > 0.5).sum(1) > W * 0.02)[0]
    if not len(sorok):
        return None
    top = int(sorok[0])
    mer = min(H - 1, top + int(W * 0.14))
    xs = np.where(alfa[mer] > 0.5)[0]
    x0, x1 = (int(xs.min()), int(xs.max())) if len(xs) else (W // 3, 2 * W // 3)
    fej_sz = x1 - x0
    all_y = min(H - 1, top + int(fej_sz * 1.32))
    return top, x0, x1, all_y



def tukor_toltes(kep, gap, fej_teto_kepen):
    """A felső rés kitöltése a kép fej nélküli felső sávjának tükrözésével, a távolsággal erősödő elmosással."""
    sw = kep.width
    R = max(24, min(int(fej_teto_kepen) - 16, kep.height // 3))
    sav = np.asarray(kep.crop((0, 0, sw, R))).astype(np.float32)
    d = np.arange(1, gap + 1)
    m = (d - 1) % (2 * R)
    r = np.where(m < R, m, 2 * R - 1 - m)
    sorok = sav[r][::-1]                       # a rés teteje a legtávolabbi sor
    nyers = Image.fromarray(np.clip(sorok, 0, 255).astype(np.uint8))
    szintek = [np.asarray(nyers.filter(ImageFilter.GaussianBlur(b))).astype(np.float32) for b in (2, 10, 26)]
    tav = (gap - np.arange(gap))[:, None, None].astype(np.float32)      # távolság a varrattól
    w1 = np.clip(tav / 120.0, 0, 1)
    w2 = np.clip((tav - 120) / 220.0, 0, 1)
    ki = szintek[0] * (1 - w1) + szintek[1] * w1
    ki = ki * (1 - w2) + szintek[2] * w2
    hom = np.linspace(0.85, 1.0, gap)[:, None, None]
    return Image.fromarray(np.clip(ki * hom, 0, 255).astype(np.uint8))


def ai_bovites(vaszon_rgba, prompt_tema=""):
    """OpenAI képszerkesztés maszkkal: a 1080×1920-as vászon átlátszó részét festi ki. None, ha nem sikerül."""
    import base64
    import io
    import uuid
    sys.path.insert(0, str(SKILL / "scripts"))
    try:
        from ikon_generalo import kulcs, MODELLEK
    except Exception:
        return None
    key = kulcs()
    if not key:
        print("  ! nincs OpenAI-kulcs: tükrözött kiterjesztés")
        return None
    # 9:16 -> 1024×1536-os vászon közepére (864×1536), a két oldalsáv is kitöltendő (utána levágjuk)
    kis = vaszon_rgba.resize((864, 1536), Image.LANCZOS)
    can = Image.new("RGBA", (1024, 1536), (0, 0, 0, 0))
    can.paste(kis, (80, 0))
    buf = io.BytesIO(); can.save(buf, "PNG"); png = buf.getvalue()
    prompt = ("Extend this vertical photo upward so it fills the whole frame naturally: continue the existing background "
              "above the person with the same scene, light, colors and soft depth of field" + (f" ({prompt_tema})" if prompt_tema else "")
              + ". Photorealistic, seamless. Do not change the person or anything already in the photo. No text, no people added.")
    for modell in MODELLEK:
        hatar = uuid.uuid4().hex
        def mezo(n, v):
            return (f"--{hatar}\r\nContent-Disposition: form-data; name=\"{n}\"\r\n\r\n{v}\r\n").encode()
        body = (mezo("model", modell) + mezo("prompt", prompt) + mezo("size", "1024x1536") + mezo("quality", "medium")
                + mezo("n", "1")
                + (f"--{hatar}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"kep.png\"\r\n"
                   f"Content-Type: image/png\r\n\r\n").encode() + png + b"\r\n"
                + (f"--{hatar}\r\nContent-Disposition: form-data; name=\"mask\"; filename=\"maszk.png\"\r\n"
                   f"Content-Type: image/png\r\n\r\n").encode() + png + b"\r\n" + f"--{hatar}--\r\n".encode())
        req = urllib.request.Request("https://api.openai.com/v1/images/edits", data=body, method="POST",
                                     headers={"Authorization": f"Bearer {key}",
                                              "Content-Type": f"multipart/form-data; boundary={hatar}"})
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                d = json.loads(r.read())
            b64 = d["data"][0]["b64_json"]
            ki = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
            print(f"  AI-kiterjesztés kész ({modell})")
            return ki.crop((80, 0, 944, 1536)).resize((1080, 1920), Image.LANCZOS)
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "ignore")[:300]
            if e.code in (400, 403, 404) and ("model" in msg.lower() or "verif" in msg.lower()):
                continue
            print(f"  ! AI-kiterjesztés hiba ({e.code}): tükrözött kiterjesztés")
            return None
        except Exception as e:
            print(f"  ! AI-kiterjesztés hiba ({type(e).__name__}): tükrözött kiterjesztés")
            return None
    return None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    foto, ki = Path(sys.argv[1]), Path(sys.argv[2])
    ki.mkdir(parents=True, exist_ok=True)
    szel = int(arg("--szel", 900))
    cel_top, cel_sz = int(arg("--fejteto", 560)), int(arg("--fejszel", 430))
    im = Image.open(foto).convert("RGB")
    if max(im.size) > 1800:
        im.thumbnail((1800, 1800), Image.LANCZOS)
    W, H = im.size

    modszer, alfa = "arc", None
    try:
        import onnxruntime  # noqa: F401
        m = modell_ut(arg("--modell"))
        if m:
            w16, h16 = max(16, (W // 16) * 16), max(16, (H // 16) * 16)
            a = rvm_alfa(im.resize((w16, h16)), m)
            alfa = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)) / 255.0
            modszer = "rvm"
    except ImportError:
        print("  ! nincs onnxruntime (pip3 install --user onnxruntime); arcfelismeréssel becsülök")
    if alfa is None:
        alfa = arc_alfa(im)
    meres = fej_meres(alfa)

    # elhelyezés a 1080×1920-as színpadon
    if meres:
        top, x0, x1, all_y = meres
        s = max(cel_sz / max(1, x1 - x0), 1080 / W)
        ox = min(0, max(1080 - W * s, 540 - (x0 + x1) / 2 * s))
        oy = cel_top - top * s
        if oy + H * s < 1920:             # lent ne maradjon üres sáv
            oy = 1920 - H * s
        if oy < 0 and top * s + oy < 235:  # a fej túl magasra kerülne: inkább nagyítunk
            s2 = 1920 / H
            s, oy = max(s, s2), 0
    else:
        s = max(1080 / W, 1920 / H)
        ox, oy = (1080 - W * s) / 2, (1920 - H * s) / 2
    sw, sh = round(W * s), round(H * s)
    ox, oy = round(ox), round(oy)
    kep = im.resize((sw, sh), Image.LANCZOS)
    vaszon = Image.new("RGB", (1080, 1920), (0, 0, 0))
    vaszon.paste(kep, (ox, oy))
    # alfa a színpadon (a teljes alak), a kivágáshoz és a varrathoz
    A = np.zeros((1920, 1080), np.float32)
    a_s = np.asarray(Image.fromarray((alfa * 255).astype(np.uint8)).resize((sw, sh), Image.LANCZOS)) / 255.0
    y0, x0s = max(0, oy), max(0, ox)
    y1, x1s = min(1920, oy + sh), min(1080, ox + sw)
    A[y0:y1, x0s:x1s] = a_s[y0 - oy:y1 - oy, x0s - ox:x1s - ox]
    bov_mod = "nincs"
    if oy > 0:
        mod = arg("--bovites", "auto")
        ai = None
        if mod in ("auto", "ai"):
            rgba = vaszon.convert("RGBA")
            al = np.zeros((1920, 1080), np.uint8); al[oy:, :] = 255
            rgba.putalpha(Image.fromarray(al))
            ai = ai_bovites(rgba, arg("--tema", ""))
        if mod == "vaszon":
            rgba = vaszon.convert("RGBA")
            al = np.zeros((1920, 1080), np.uint8); al[oy:, :] = 255
            rgba.putalpha(Image.fromarray(al))
            rgba.resize((864, 1536), Image.LANCZOS).save(ki / "vaszon-ai.png")
            print(f"  vászon a külső bővítéshez: {ki / 'vaszon-ai.png'} (864×1536, a felső {oy} px átlátszó; maszknak is jó)")
        elif mod.startswith("kep:"):
            ai = Image.open(mod[4:]).convert("RGB").resize((1080, 1920), Image.LANCZOS)
        if ai is not None:
            # a valódi fotó pixelre visszakerül, a varrat 40 px-en úszik
            m = np.zeros((1920, 1080), np.float32); m[oy:, :] = 1
            m[oy:oy + 40, :] = np.linspace(0, 1, 40)[:, None]
            v = np.asarray(vaszon).astype(np.float32); a = np.asarray(ai).astype(np.float32)
            vaszon = Image.fromarray(np.clip(v * m[:, :, None] + a * (1 - m[:, :, None]), 0, 255).astype(np.uint8))
            bov_mod = "ai"
        else:
            fej_kepen = (top * s) if meres else sh * 0.2
            tolt = tukor_toltes(kep, oy, fej_kepen)
            vaszon.paste(tolt, (ox, 0))
            bov_mod = "tukor"
    vaszon.resize((szel, round(szel * 16 / 9)), Image.LANCZOS).save(ki / "hatter.jpg", quality=82, optimize=True, progressive=True)

    if not meres:
        json.dump({"meret": [1080, 1920], "fej_doboz": None, "modszer": modszer,
                   "megjegyzes": "nem találtam embert a képen: kivágás nélkül megy"}, open(ki / "fej.json", "w"))
        print("  ! nincs ember a képen")
        return
    top_s, fx0, fx1, all_s = fej_meres(A)
    also = min(1920, all_s + int((fx1 - fx0) * 0.35))
    sav = np.clip((also - np.arange(1920)) / max(8, (fx1 - fx0) * 0.18), 0, 1)[:, None]
    fa = A * sav
    rgba = np.dstack([np.asarray(vaszon), (fa * 255).astype(np.uint8)])
    pad = int((fx1 - fx0) * 0.25)
    bx0, by0 = max(0, fx0 - pad), max(0, top_s - pad)
    bx1, by1 = min(1080, fx1 + pad), min(1920, also + 4)
    k = szel / 1080
    Image.fromarray(rgba).crop((bx0, by0, bx1, by1)).resize((round((bx1 - bx0) * k), round((by1 - by0) * k)),
                                                          Image.LANCZOS).save(ki / "fej.png", optimize=True)
    info = {"meret": [1080, 1920], "forras": str(foto.name), "modszer": modszer,
            "fej_doboz": [bx0, by0, bx1 - bx0, by1 - by0], "fejteto": int(top_s), "fej_x": [int(fx0), int(fx1)],
            "all": int(all_s), "kiterjesztes_px": max(0, oy), "kiterjesztes": bov_mod,
            "megjegyzes": ("RVM-kivágás" if modszer == "rvm" else "becsült fej (ellipszis az arc körül), durvább széllel")
            + (f"; a felső {oy} px a kép kiterjesztése" if oy > 0 else "")}
    json.dump(info, open(ki / "fej.json", "w"), ensure_ascii=False, indent=1)
    print(f"KÉSZ: {ki}/hatter.jpg + fej.png  ({modszer}; fejtető {info['fejteto']}, fej x {info['fej_x']}, "
          f"áll {info['all']}, kiterjesztés {info['kiterjesztes_px']} px)")


if __name__ == "__main__":
    main()
