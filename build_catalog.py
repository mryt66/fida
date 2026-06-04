#!/usr/bin/env python3
"""Build a useful catalog tying products -> images -> variants from the .har."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "extracted" / "data"
OUT = ROOT / "extracted" / "catalog.json"

products = json.load(open(DATA / "177_1bcf1e1163_products.json"))["products"]

catalog = []
for p in products:
    images = [{"order": i.get("order"), "url": i.get("url"), "type": i.get("type")}
              for i in p.get("images", [])]
    variants = []
    for v in p.get("variants", []):
        price_eur = None
        currency = None
        for pr in v.get("prices", []):
            amt = pr.get("amount")
            if amt is not None:
                price_eur = amt / 100  # store uses cents
                currency = pr.get("currency_code", "").upper()
        variants.append({
            "id": v.get("id"),
            "title": v.get("title"),
            "sku": v.get("sku"),
            "price": price_eur,
            "currency": currency,
            "available": v.get("is_available"),
            "manage_inventory": v.get("manage_inventory"),
        })
    catalog.append({
        "id": p.get("id"),
        "title": p.get("title"),
        "slug": p.get("slug"),
        "url": f"https://www.fidamusic.pl/{p.get('url_handle') or p.get('slug')}",
        "subtitle": p.get("subtitle"),
        "ribbon": p.get("ribbon_text"),
        "purchasable": p.get("purchasable"),
        "available": p.get("is_available"),
        "thumbnail": p.get("thumbnail"),
        "description_html": p.get("description"),
        "seo": p.get("seo_settings"),
        "variants": variants,
        "images": images,
        "updated_at": p.get("updated_at"),
    })

OUT.write_text(json.dumps(catalog, indent=2, ensure_ascii=False))
print(f"Wrote {OUT.relative_to(ROOT)} with {len(catalog)} products.")

print("\n--- Catalog summary ---")
for item in catalog:
    v = item["variants"][0] if item["variants"] else {}
    price = f"{v['price']:.2f} {v['currency']}" if v.get('price') is not None else "—"
    avail = "in stock" if item["available"] else "out"
    n_img = len(item["images"])
    print(f"  [{avail:>7}] {price:>10}  img={n_img}  {item['slug']:<35}  {item['title']}")
