#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Részfájlokban írt leirat összefűzése egy fájlba (UTF-8, BOM nélkül).

  <slug>-01.md, <slug>-02.md, … → <slug>.md

Használat:
  python osszefuz.py webinar-2026-03-leirat
  python osszefuz.py webinar-2026-03-leirat --torol     # a részfájlokat utána törli
  python osszefuz.py mappa/valami-leirat                # útvonallal is megy
"""
import argparse, glob, os, re, sys

for _s in (sys.stdout, sys.stderr):  # Windows-konzolon (cp1250) is jó ékezet és nyíl
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", help="a részfájlok közös előtagja, a -01.md nélkül")
    ap.add_argument("--torol", action="store_true", help="sikeres összefűzés után törli a részeket")
    a = ap.parse_args()

    parts = sorted(glob.glob(glob.escape(a.slug) + "-[0-9][0-9].md"),
                   key=lambda p: int(re.search(r"-(\d{2})\.md$", p).group(1)))
    if not parts:
        sys.exit(f"Nincs ilyen részfájl: {a.slug}-01.md …")

    nums = [int(re.search(r"-(\d{2})\.md$", p).group(1)) for p in parts]
    missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
    if missing:
        sys.exit(f"Hiányzó rész(ek): {', '.join(f'{n:02d}' for n in missing)}, nem fűzöm össze.")

    chunks = [open(p, encoding="utf-8-sig").read().strip("\n") for p in parts]
    out = a.slug + ".md"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n\n".join(chunks) + "\n")

    if a.torol:
        for p in parts:
            os.remove(p)
    print(f"{len(parts)} rész → {out} ({os.path.getsize(out) // 1024} KB)"
          + (", részek törölve" if a.torol else ""))


if __name__ == "__main__":
    main()
