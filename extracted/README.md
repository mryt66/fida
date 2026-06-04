# Extracted from `fida_sklepm.har`

Source: HTTP archive of fidamusic.pl (Hostinger e-commerce, 216 entries, 24 MB).
Extractor: `extract_har.py`  ·  Catalog builder: `build_catalog.py`

## Output tree

```
extracted/
├── images/        18 unique image files  (dedup of 54 requests)
│   └── svg/        1 SVG (card icons, 15 KB)
├── data/          5 unique JSON API responses (rest are dupes)
├── catalog.json   Merged product catalog (7 products, prices, images, variants)
├── manifests/
│   ├── all.json   Every HAR entry with url, mime, size, status, saved/note
│   ├── images.json, data.json, …
│   └── refetch_urls.txt   URLs whose response body was NOT captured in the HAR
└── README.md      This file
```

> Note: the 6 HTML pages in the HAR have no captured body content
> (DevTools was set to streaming). The real page content lives in
> `../www.fidamusic.pl/*.html` from the earlier download.

## What was useful (saved with content)

| Kind | Count | Why it matters |
|---|---|---|
| **7 product definitions** | `data/177_…_products.json`, `catalog.json` | Full schema: title, slug, price (PLN), variants, images, SEO, ribbon, updated_at |
| **18 unique images** | `images/` (5.8 MB) | Logo + 7 product images in PNG / AVIF / WebP variants. Largest originals (`214e3b12-…png` 1.9 MB) are the white t-shirt; `02410eab-…png` 1.6 MB is the red shopping bag |
| **5 unique JSON API responses** | `data/` | `collections`, `products` (×3, sorted by price ASC/DESC & created_at DESC), `variants` (inventory) |
| **1 SVG** | `images/svg/` | Card / payment icons |
| **7 POSTs** | `manifests/all.json` → `postData` field | Checkout creation, cart region/address/discount — reveals the cart-ID JWT shape and discount code handling |

## What was NOT captured by the HAR (147 entries, ~13 MB)

The DevTools export saved the request/response *metadata* but not the bodies for:

- 27 woff2 fonts (Alata, Rubik 300/400, Playfair Display 400/700, Space Grotesk)
- 20 CSS files (Zyro site builder stylesheets)
- 45 JavaScript files (Vue 3 + Sentry SDK + ecommerce runtime)
- 6 HTML pages
- 1 `favicon.svg` (404)
- 27 OPTIONS pre-flight + 20 `x-unknown` CORS responses

Re-fetch the missing bodies with:
```bash
# example using the saved URL list
xargs -n1 -P8 curl -sSLO --create-dirs < extracted/manifests/refetch_urls.txt
```

## The product catalog (7 items, all "in stock")

| Price (PLN) | Slug | Title |
|---:|---|---|
| 59.00 | `brelok-w-kacie-kurz` | Brelok W Kącie Kurz |
| 59.00 | `brelok-miodowe-lata` | Brelok Miodowe Lata |
| 59.00 | `brelok-upadek-w-tramwaju` | Brelok Upadek w Tramwaju |
| 69.00 | `torba-zakupowa-w-czerwonosci` | Torba Zakupowa W Czerwoności |
| 69.00 | `torba-zakupowa-korale` | Torba Zakupowa W Kremie |
| 99.00 | `biala-koszulka-idealny-samochod` | Biała Koszulka Idealny Samochód |
| 99.00 | `czarna-koszulka-idealny-samochod` | Czarna Koszulka Idealny Samochód |

Prices extracted from `variants[0].prices[0].amount` (cents → PLN).

## Re-running

```bash
python3 extract_har.py    # rebuild extracted/ and manifests/
python3 build_catalog.py  # rebuild catalog.json
```

The extractor skips duplicates by SHA-1, so the second run is a no-op.
