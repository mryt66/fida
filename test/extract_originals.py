#!/usr/bin/env python3
"""Extract original header / footer HTML from every page in single_file/.

Output: test/originals/<slug>-header.html, <slug>-footer.html

Header: matches <header ...>...</header>.
Footer: <footer ...>...</footer> doesn't exist in single_file — the
"footer-like" content is the copyright H3 + 3 link <p>s at the bottom of
<body>. We extract that block.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "single_file"
OUT = ROOT / "test" / "originals"
OUT.mkdir(parents=True, exist_ok=True)

FOOTER_RE = re.compile(
    r"<h3\s+style=color:rgb\(255,255,255\).*?</section>",
    re.DOTALL,
)


def slugify(name: str) -> str:
    base = re.sub(r"\.html$", "", name)
    base = re.sub(r"\s*\([^)]*\)", "", base)
    base = re.sub(r"\s+", "-", base.strip())
    base = re.sub(r"[^a-zA-Z0-9-]+", "-", base).strip("-").lower()
    return base or "page"


files = sorted([f for f in SRC.iterdir() if f.suffix == ".html"])
print(f"Przetwarzam {len(files)} plików z {SRC}\n")

for f in files:
    slug = slugify(f.name)
    txt = f.read_text(encoding="utf-8", errors="replace")
    size_kb = len(txt) / 1024

    # Header
    h = re.search(r"<header[^>]*>.*?</header>", txt, re.DOTALL)
    h_count = 0
    if h:
        (OUT / f"{slug}-header.html").write_text(h.group(0), encoding="utf-8")
        h_count = 1

    # Footer (sklepowy wzorzec: H3 © + 3 linki)
    m = FOOTER_RE.search(txt)
    f_count = 0
    if m:
        (OUT / f"{slug}-footer.html").write_text(m.group(0), encoding="utf-8")
        f_count = 1

    print(f"  {f.name:<70}  {size_kb:>6.1f} KB  header:{h_count} footer:{f_count}")

print(f"\nWyekstrahowane pliki w: {OUT}")
print(f"Łącznie: {len(list(OUT.iterdir()))} plików")
