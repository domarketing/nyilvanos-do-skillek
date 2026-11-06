#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Változatosság-ellenőrzés önállóan (a választó építése ugyanezt futtatja, és hibánál nem épít).

  python3 <SKILL>/scripts/valtozatossag.py <munkamappa>/arculat.json
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from motor import epito, valtozatossag  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    spec = epito.betolt(sys.argv[1])
    opc = epito.opciok(spec)
    hiba, figy = valtozatossag.ellenoriz(spec, opc, epito.marka_dns(spec))
    for x in figy:
        print("figyelem:", x)
    for x in hiba:
        print("HIBA:", x)
    print("rendben: a változatok elég különbözők" if not hiba else f"{len(hiba)} hiba: így nem épül választó")
    sys.exit(1 if hiba else 0)


if __name__ == "__main__":
    main()
