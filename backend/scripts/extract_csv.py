"""One-time helper: extract embedded sample CSV from legacy index.html into data/."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "index.html"
OUT = ROOT / "data" / "CoffeeBeanAndTeaLeafCoffeeShopData1.csv"


def main() -> None:
    if not HTML.exists():
        raise SystemExit(f"Not found: {HTML}")
    text = HTML.read_text(encoding="utf-8")
    match = re.search(r"const SAMPLE_CSV = `(.*?)`;", text, re.DOTALL)
    if not match:
        raise SystemExit("SAMPLE_CSV block not found in index.html")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(match.group(1), encoding="utf-8")
    print(f"Wrote {OUT} ({len(match.group(1).splitlines())} lines)")


if __name__ == "__main__":
    main()
