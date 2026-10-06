#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VTT/SRT felirat tömörítése olvasható munkaszöveggé.

Mit csinál:
  - kidobja a WEBVTT-fejlécet, a cue-sorszámokat és az időkódokat,
  - kiszedi az ASR-szemetet (pl. thai "เฮ" zenénél, magányos "H" / "He." sorok),
  - kiszűri a gördülő (rolling) feliratok ismétlődő sorait,
  - N másodpercenként egy [óó:pp:mm] jelölőt tesz a szöveg elé
    (a jelölő a blokk ELSŐ cue-jának KEZDŐ ideje: ezt használd a leirat időbélyegeihez).

A kimenet kb. harmada a nyers VTT-nek, így a teljes felvétel egyben átolvasható.

Használat:
  python vtt_tomorit.py felirat.vtt                 # 30 mp-es blokkok a képernyőre
  python vtt_tomorit.py felirat.vtt -o tomor.txt    # fájlba
  python vtt_tomorit.py felirat.vtt -i 60           # 60 mp-es blokkok
"""
import argparse, re, sys

for _s in (sys.stdout, sys.stderr):  # Windows-konzolon (cp1250) is jó ékezet és nyíl
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

TS = re.compile(r'(\d{1,2}):(\d{2}):(\d{2})[.,](\d{3})\s*-->')
LETTER = re.compile(r'[A-Za-zÁÉÍÓÖŐÚÜŰáéíóöőúüű0-9]')
JUNK_SCRIPTS = re.compile(r'[\u0E00-\u0E7F\u0600-\u06FF\u3040-\u30FF\u4E00-\u9FFF]+')  # thai, arab, japán, kínai
TAGS = re.compile(r'<[^>]+>')  # <c>, <00:00:01.000> stb.
JUNK_WORDS = {"h", "he", "he.", "hm", "hm.", "m", "ö", "ööö", "[zene]", "[music]", "[taps]", "[applause]"}


def sec_to_ts(s):
    s = int(s)
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def parse(path):
    raw = open(path, encoding="utf-8-sig", errors="replace").read()
    cues, start, buf = [], None, []
    for line in raw.splitlines():
        m = TS.search(line)
        if m:
            if start is not None and buf:
                cues.append((start, buf))
            h, mi, se, _ = map(int, m.groups())
            start, buf = h * 3600 + mi * 60 + se, []
            continue
        t = line.strip()
        if not t:
            continue
        if start is None:           # fejléc (WEBVTT, Kind:, Language:)
            continue
        if t.isdigit() and not buf:  # SRT sorszám
            continue
        buf.append(t)
    if start is not None and buf:
        cues.append((start, buf))
    return cues


def clean(line):
    line = TAGS.sub("", line)
    line = JUNK_SCRIPTS.sub("", line).strip()
    if not line or not LETTER.search(line):
        return ""
    if line.lower() in JUNK_WORDS:
        return ""
    return line


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("felirat")
    ap.add_argument("-o", "--out")
    ap.add_argument("-i", "--interval", type=int, default=30, help="blokkhossz másodpercben (alap: 30)")
    a = ap.parse_args()

    cues = parse(a.felirat)
    blocks, cur_start, cur, last = [], None, [], ""
    for start, lines in cues:
        for ln in lines:
            ln = clean(ln)
            if not ln or ln == last:
                continue
            if cur_start is None:
                cur_start = start
            if start - cur_start >= a.interval and cur:
                blocks.append((cur_start, cur))
                cur_start, cur = start, []
            cur.append(ln)
            last = ln
    if cur:
        blocks.append((cur_start, cur))

    out = "\n".join(f"[{sec_to_ts(s)}] " + " ".join(t) for s, t in blocks) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(out)
        end = sec_to_ts(cues[-1][0]) if cues else "00:00:00"
        print(f"{len(cues)} cue -> {len(blocks)} blokk, utolsó cue: {end}, {len(out)} karakter -> {a.out}", file=sys.stderr)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
