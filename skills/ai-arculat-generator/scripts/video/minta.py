# -*- coding: utf-8 -*-
"""Márkázott minta-videó (15-25 mp) a választott elemekből: az összeállítás jelenetei az ügyfél fotóján, zenével.

Egyetlen headless Chrome-ból, a DevTools-protokollal kockánként (gyors), a hang ugyanazzal a szintetizátorral,
amelyik a választóban szól (WebAudio, OfflineAudioContext), a végén ffmpeg (H.264, AAC, -14 LUFS).
Kell hozzá: Chrome, ffmpeg, a websocket-client Python-csomag (pip3 install --user websocket-client).
Ez stílusbemutató: igazi vágáshoz (leirat, szóra időzítés, arckövetés) a tag vágó skillje kell.
"""
import base64
import json
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

from leiras import chrome_ut, dontesek, valasztas_betolt
import katalogus as K


class CDP:
    def __init__(self, ws_url):
        import websocket
        self.ws = websocket.create_connection(ws_url, max_size=None, timeout=60, suppress_origin=True)
        self.i = 0

    def cmd(self, method, **params):
        self.i += 1
        mid = self.i
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == mid:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})

    def ertek(self, expr, var=False):
        r = self.cmd("Runtime.evaluate", expression=expr, awaitPromise=var, returnByValue=True)
        if r.get("exceptionDetails"):
            raise RuntimeError(r["exceptionDetails"].get("text", "JS-hiba"))
        return (r.get("result") or {}).get("value")


def master(be, ki, I=-14, TP=-1, LRA=11):
    """Kétmenetes loudnorm, mint a vágó skill masterje: az első menet mér, a második lineárisan normalizál."""
    import re
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(be), "-af", f"loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"\{[^{}]*\}", r.stderr)
    if not m:
        shutil.copy(be, ki)
        return ki
    d = json.loads(m[-1])
    af = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={d['input_i']}:measured_TP={d['input_tp']}:"
          f"measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true,alimiter=limit=0.70:attack=3:release=60:level=disabled")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(be), "-af", af, "-ar", "48000", str(ki)], check=True)
    return ki


def _port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def minta(mappa, valasztas=None, ki=None, fps=30):
    mappa = Path(mappa)
    html = mappa / "video" / "video-valaszto.html"
    if not html.exists():
        raise SystemExit("Előbb: video.py valaszto <munkamappa>")
    if not shutil.which("ffmpeg"):
        raise SystemExit("Nincs ffmpeg (Mac: brew install ffmpeg, Windows: winget install ffmpeg).")
    ch = chrome_ut()
    if not ch:
        raise SystemExit("Nincs Chrome a gépen.")
    tok = json.loads((mappa / "tokenek.json").read_text(encoding="utf-8"))
    tp = mappa / "video" / "tartalom.json"
    tart = json.loads(tp.read_text(encoding="utf-8")) if tp.exists() else {}
    D = dontesek(tok, tart, valasztas_betolt(mappa, valasztas))
    q = urllib.parse.urlencode({"kep": "osszeallitas:x@0.05", "val": ",".join(f"{k}:{v}" for k, v in D.items())})
    url = html.resolve().as_uri() + "?" + q
    port, tmp = _port(), Path(tempfile.mkdtemp(prefix="vv-minta-"))
    pr = subprocess.Popen([ch, "--headless=new", f"--remote-debugging-port={port}", "--window-size=1080,1920", "--hide-scrollbars",
                           "--force-device-scale-factor=1", "--allow-file-access-from-files", f"--user-data-dir={tmp / 'profil'}",
                           "--no-first-run", "--no-default-browser-check", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws = None
        for _ in range(100):
            try:
                L = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2).read())
                ws = next((x["webSocketDebuggerUrl"] for x in L if x.get("type") == "page"), None)
                if ws:
                    break
            except Exception:
                pass
            time.sleep(0.2)
        if not ws:
            raise SystemExit("A Chrome nem indult el távvezérléssel.")
        c = CDP(ws)
        c.cmd("Emulation.setDeviceMetricsOverride", width=1080, height=1920, deviceScaleFactor=1, mobile=False)
        for _ in range(150):
            if c.ertek("document.documentElement.getAttribute('data-kesz') === '1' && document.fonts.status === 'loaded'"):
                break
            time.sleep(0.2)
        else:
            raise SystemExit("Az oldal nem állt össze (GSAP vagy betűk nem töltődtek be?).")
        time.sleep(0.8)
        dur = float(c.ertek("window.__vv.hossz"))
        n = int(dur * fps)
        # a kockák egyenesen az ffmpeg-be mennek (nincs ideiglenes képsorozat a lemezen)
        kepvid = tmp / "kep.mp4"
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
                               "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", str(kepvid)], stdin=subprocess.PIPE)
        for i in range(n):
            c.ertek(f"window.__vv.seek({i / fps:.4f})")
            img = c.cmd("Page.captureScreenshot", format="jpeg", quality=92,
                        clip={"x": 0, "y": 0, "width": 1080, "height": 1920, "scale": 1})["data"]
            ff.stdin.write(base64.b64decode(img))
        ff.stdin.close()
        if ff.wait() != 0:
            raise SystemExit("Az ffmpeg nem tudta összefűzni a kockákat.")
        wav = tmp / "hang.wav"
        wav.write_bytes(base64.b64decode(c.ertek(f"window.__vv.hang({dur:.3f})", var=True)))
        hangulat = c.ertek("window.__vv.hangulat")
    finally:
        pr.terminate()
    slug = (tok.get("marka") or {}).get("slug", "marka")
    ki = Path(ki) if ki else mappa / "video" / f"minta-{slug}-9x16.mp4"
    norm = master(wav, tmp / "hang-14.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(kepvid), "-i", str(norm), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(ki)], check=True)
    # kontaktlap: másodpercenként egy kocka
    lap = ki.with_name(ki.stem + "-kontaktlap.jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ki), "-vf", "fps=1,scale=216:384,tile=10x2", "-frames:v", "1", str(lap)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    hn = next((v["nev"] for v in K.KAT["hangulat"]["valtozatok"] if v["id"] == hangulat), hangulat)
    print(f"KÉSZ: {ki}  ({dur:.1f} mp, {n} kocka, hangulat: {hn})\n  + {lap}")
    return ki
