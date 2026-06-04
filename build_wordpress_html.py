#!/usr/bin/env python3
"""Build WordPress-compatible HTML snapshots from fida_sklepm.har data.

Outputs 6 standalone HTML files to wordpress_fida/ that visually match the
original fidamusic.pl pages, with all assets referenced from local files or CDN.
"""
import json
import re
import sys
from pathlib import Path
from html import escape

ROOT = Path(__file__).parent
SRC = ROOT / "www.fidamusic.pl"
EXTRACTED = ROOT / "extracted"
OUT = ROOT / "wordpress_fida"

OUT.mkdir(parents=True, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────
products_json = json.loads((EXTRACTED / "data" / "177_1bcf1e1163_products.json").read_bytes())
products = products_json["products"]

catalog = {p["slug"]: p for p in products}

# ── Template parts (extracted from sklep.html) ─────────────────────────
SKLEP_HTML = (SRC / "sklep.html").read_text()

def extract_head(src: str) -> str:
    """Extract <head> content (meta, css, fonts, title placeholder)."""
    m = re.search(r'<head>(.*?)</head>', src, re.DOTALL)
    if not m:
        return ""
    head = m.group(1)
    # Remove script tags from head
    head = re.sub(r'<script[^>]*>.*?</script>', '', head, flags=re.DOTALL)
    # Remove title (we'll add our own)
    head = re.sub(r'<title>.*?</title>', '', head)
    return head


def extract_header(src: str) -> str:
    """Extract <header> block."""
    m = re.search(r'(<header[^>]*>.*?</header>)', src, re.DOTALL)
    if m:
        return m.group(1)
    return ""


def extract_footer(src: str) -> str:
    """Extract footer section (id=z26dfS)."""
    m = re.search(r'(<section[^>]*id="z26dfS"[^>]*>.*?</section>)', src, re.DOTALL)
    if m:
        return m.group(1)
    return ""


def extract_content_section(src: str, exclude_ids=("stickyBar", "z26dfS")) -> str:
    """Extract the main content section (not stickyBar or footer)."""
    sections = re.findall(r'<section[^>]*id="([^"]+)"[^>]*>(.*?)</section>', src, re.DOTALL)
    for sid, sc in sections:
        if sid not in exclude_ids:
            # Strip Vue SSR markers only (not the content between them)
            sc = re.sub(r'<!--\[-->|<!--\]-->|<!---->', '', sc)
            return sc
    return ""


def clean_vue_markup(html: str) -> str:
    """Remove Vue-specific attributes and comments, leaving clean HTML."""
    html = re.sub(r' data-v-[a-f0-9]+=""', '', html)
    html = re.sub(r'\s+ssr="[^"]*"', '', html)
    html = re.sub(r'\s+v-[\w-]+="[^"]*"', '', html)
    # Remove empty Vue SSR markers only (NOT <!--[...]--> which wraps content)
    html = re.sub(r'<!--\[-->|<!--\]-->|<!---->', '', html)
    html = re.sub(r' products-per-page="[^"]*"', '', html)
    return html


def make_css_links() -> str:
    return '''
    <link rel="stylesheet" href="_astro-1779472190601/_..D9s3Ry08.css">
    <link rel="stylesheet" href="_astro-1779472190601/cookieconsent.CpXrOrr9.css">
    <link rel="stylesheet" href="_astro-1779472190601/Page.DWsMedUh.css">'''


HEAD_CONTENT = extract_head(SKLEP_HTML)
HEADER_HTML = clean_vue_markup(extract_header(SKLEP_HTML))
FOOTER_HTML = clean_vue_markup(extract_footer(SKLEP_HTML))
CSS_LINKS = make_css_links()

# Remove sticky bar from header if present
HEADER_HTML = re.sub(
    r'<section[^>]*id="stickyBar"[^>]*>.*?</section>',
    '', HEADER_HTML, flags=re.DOTALL
)


def assemble_page(title: str, body_content: str, og_image: str = "") -> str:
    """Wrap content in full HTML document with head/header/footer."""
    meta_og = ""
    if og_image:
        meta_og = f'''
    <meta property="og:image" content="{escape(og_image)}">
    <meta name="twitter:image" content="{escape(og_image)}">'''

    return f'''<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{HEAD_CONTENT}
{CSS_LINKS}
<title>{escape(title)}</title>
{meta_og}
<link rel="canonical" href="{escape(title.lower().replace(' ', '-'))}.html">
<style>
  /* Prevent skeleton loader display without JS */
  .skeleton-loader {{ display: none !important; }}
  /* Ensure text content is visible */
  .page__blocks section.block {{ opacity: 1 !important; }}
  /* Fix for product cards */
  .block-product-list .skeleton-loader {{ display: none !important; }}
  .block-product-list__content-container {{ min-height: auto !important; }}
  /* Ensure images display */
  img[src*="cdn.zyrosite.com"] {{ display: inline-block !important; }}
  /* Fix footer visibility */
  .block--footer .layout-element {{ opacity: 1 !important; }}
  /* Remove sticky bar */
  section#stickyBar {{ display: none !important; }}
</style>
</head>
<body>
<div id="app">
<div class="page">
{HEADER_HTML}
<div class="page__blocks">
{body_content}
{FOOTER_HTML}
</div>
</div>
</div>
</body>
</html>'''


# ── Page builders ──────────────────────────────────────────────────────

def build_static_page(source_file: str, title: str) -> str:
    """Build a static text page from an existing source HTML file."""
    src = (SRC / source_file).read_text()
    content = extract_content_section(src)
    content = clean_vue_markup(content)
    return assemble_page(title, content)


def build_sklep() -> str:
    """Build the shop page with product cards from JSON data."""
    cards_html = ""
    for p in products:
        slug = p.get("slug", "")
        name = escape(p.get("title", ""))
        subtitle = escape(p.get("subtitle", "") or "")
        thumb = escape(p.get("thumbnail", "") or "")
        ribbon = escape(p.get("ribbon_text", "") or "")
        price_amt = p["variants"][0]["prices"][0]["amount"] / 100 if p.get("variants") else 0
        price_str = f"{price_amt:.2f} zł"
        available = p.get("is_available", True)

        ribbon_badge = f'<span class="block-product-list__ribbon">{ribbon}</span>' if ribbon else ""

        cards_html += f'''
    <div class="block-product-list__item">
      <div class="block-product-list__card-wrapper">
        <a href="{slug}.html" class="block-product-list__card-link">
          <div class="block-product-list__card">
            <div class="block-product-list__image-wrapper">
              <img class="block-product-list__image" src="{thumb}" alt="{name}" loading="lazy">
              {ribbon_badge}
            </div>
            <div class="block-product-list__info">
              <h3 class="block-product-list__product-name">{name}</h3>
              <p class="block-product-list__product-subtitle">{subtitle}</p>
              <div class="block-product-list__price">
                <span class="block-product-list__price-current">{price_str}</span>
              </div>
            </div>
          </div>
        </a>
      </div>
    </div>'''

    content = f'''
    <section id="zXAQVu" class="block block-product-list block-product-list--with-categories"
      style="--textAlign:outlined;--block-padding-top:100px;--block-padding:100px 16px;--block-padding-right:16px;
      --block-padding-bottom:100px;--block-padding-left:16px;--content-width:1224px;--m-block-padding:56px 16px;">
      <div class="block-background" style="background-color:rgb(255, 255, 255);"></div>
      <div class="block-product-list__wrapper">
        <div class="block-product-list__content-container">
          <div class="block-product-list__grid product-grid--portrait product-grid--columns-4">
            {cards_html}
          </div>
        </div>
      </div>
    </section>'''

    return assemble_page("Sklep | Fida", content,
                         og_image="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=1440,h=756,fit=crop,f=jpeg/m5KL36pk2XCPBlMl/3-A3Q7qKBMrptZWlv7.jpg")


def build_product_page(slug: str) -> str:
    """Build a product detail page from JSON data."""
    p = catalog.get(slug)
    if not p:
        return assemble_page("Product Not Found", "<p>Product not found</p>")

    name = escape(p.get("title", ""))
    subtitle = escape(p.get("subtitle", "") or "")
    desc_html = p.get("description", "") or ""
    ribbon = escape(p.get("ribbon_text", "") or "")
    available = p.get("is_available", True)

    # Price
    v = p["variants"][0]
    price_amt = v["prices"][0]["amount"] / 100
    price_str = f"{price_amt:.2f} zł"

    # Images
    images = p.get("images", [])
    main_img = ""
    for img in images:
        if img.get("type") == "image":
            main_img = escape(img.get("url", ""))
            break
    if not main_img and p.get("thumbnail"):
        main_img = escape(p.get("thumbnail"))

    # Gallery thumbs (all images)
    thumbs_html = ""
    for img in images[:4]:
        url = escape(img.get("url", ""))
        if url:
            thumbs_html += f'<img src="{url}" alt="{name}" class="gallery-thumb" onclick="this.parentElement.querySelector(\'.gallery-main\').src=this.src">'

    # Description
    desc_clean = re.sub(r' data-v-[a-f0-9]+=""', '', desc_html)
    desc_clean = re.sub(r' class="[^"]*"', '', desc_clean)
    desc_clean = re.sub(r' dir="auto"', '', desc_clean)
    desc_clean = re.sub(r' style="[^"]*"', '', desc_clean)

    ribbon_badge = f'<span class="ribbon">{ribbon}</span>' if ribbon else ""
    avail_badge = '<span class="in-stock">Dostępny</span>' if available else '<span class="out-of-stock">Niedostępny</span>'

    content = f'''
    <section class="block product-detail-section"
      style="--block-padding-top:40px;--block-padding:40px 16px;--content-width:1224px;">
      <div class="block-background" style="background-color:rgb(255, 255, 255);"></div>
      <div class="product-detail-wrapper">
        <div class="product-detail-gallery">
          <div class="gallery-main-wrapper">
            <img src="{main_img}" alt="{name}" class="gallery-main">
            {ribbon_badge}
          </div>
          {f'<div class="gallery-thumbs">{thumbs_html}</div>' if thumbs_html else ''}
        </div>
        <div class="product-detail-info">
          <h1 class="product-detail-title">{name}</h1>
          <p class="product-detail-subtitle">{subtitle}</p>
          <div class="product-detail-price">{price_str}</div>
          {avail_badge}
          <div class="product-detail-description">
            {desc_clean}
          </div>
          <button class="product-detail-add-to-cart" onclick="alert('WordPress: dodaj do koszyka - wymaga integracji WooCommerce')">
            Dodaj do koszyka
          </button>
        </div>
      </div>
    </section>

    <style>
    .product-detail-wrapper {{
      display: flex; gap: 40px; max-width: 1224px; margin: 0 auto; padding: 0 16px;
    }}
    .product-detail-gallery {{ flex: 1; min-width: 0; }}
    .product-detail-info {{ flex: 1; }}
    .gallery-main-wrapper {{ position: relative; margin-bottom: 16px; }}
    .gallery-main {{ width: 100%; height: auto; border-radius: 0; }}
    .gallery-thumbs {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .gallery-thumb {{ width: 80px; height: 80px; object-fit: cover; cursor: pointer; border: 2px solid transparent; }}
    .gallery-thumb:hover {{ border-color: #e3342f; }}
    .product-detail-title {{ font-family: 'Playfair Display', serif; font-size: 32px; margin: 0 0 8px; color: #1a1a1a; }}
    .product-detail-subtitle {{ font-family: 'Rubik', sans-serif; font-size: 16px; color: #666; margin: 0 0 16px; }}
    .product-detail-price {{ font-family: 'Rubik', sans-serif; font-size: 28px; font-weight: 700; color: #1a1a1a; margin-bottom: 16px; }}
    .in-stock {{ display: inline-block; padding: 4px 12px; background: #e8f5e9; color: #2e7d32; border-radius: 4px; font-size: 14px; margin-bottom: 16px; }}
    .out-of-stock {{ display: inline-block; padding: 4px 12px; background: #fbe9e7; color: #c62828; border-radius: 4px; font-size: 14px; margin-bottom: 16px; }}
    .ribbon {{ position: absolute; top: 12px; left: 12px; background: #e3342f; color: #fff; padding: 4px 12px; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
    .product-detail-description {{ font-family: 'Rubik', sans-serif; font-size: 15px; line-height: 1.7; color: #333; margin-bottom: 24px; }}
    .product-detail-description ul {{ padding-left: 20px; }}
    .product-detail-add-to-cart {{ width: 100%; padding: 14px 24px; background: #1a1a1a; color: #fff; border: none; font-size: 16px; font-family: 'Rubik', sans-serif; cursor: pointer; transition: opacity .2s; }}
    .product-detail-add-to-cart:hover {{ opacity: .85; }}
    @media (max-width: 768px) {{
      .product-detail-wrapper {{ flex-direction: column; }}
    }}
    </style>'''

    return assemble_page(f"{name} | Fida", content, og_image=main_img)


def build_checkout() -> str:
    """Build a static checkout representation."""
    content = f'''
    <section class="block checkout-section"
      style="--block-padding-top:60px;--block-padding:60px 16px;--content-width:1224px;">
      <div class="block-background" style="background-color:rgb(255, 255, 255);"></div>
      <div class="checkout-wrapper">
        <div class="checkout-header">
          <h1>Kasa</h1>
          <p>Podsumowanie zamówienia</p>
        </div>
        <div class="checkout-layout">
          <div class="checkout-items">
            <div class="checkout-item">
              <div class="checkout-item-image">
                <img src="https://cdn.zyrosite.com/cdn-ecommerce/store_01KR747ZH98X57JZ69SP34V6G7/assets/1608d7cc-869b-48f8-ad03-29b0ce9406d4.png"
                     alt="Produkt" class="checkout-item-img">
              </div>
              <div class="checkout-item-info">
                <h3>Brelok W Kącie Kurz</h3>
                <p>Ilość: 1</p>
                <p class="checkout-item-price">59.00 zł</p>
              </div>
            </div>
          </div>
          <div class="checkout-summary">
            <h2>Podsumowanie</h2>
            <div class="checkout-summary-row">
              <span>Wartość koszyka</span>
              <span>59.00 zł</span>
            </div>
            <div class="checkout-summary-row">
              <span>Wysyłka</span>
              <span>Obliczana przy kasie</span>
            </div>
            <div class="checkout-summary-row checkout-summary-total">
              <span>Razem</span>
              <span>59.00 zł</span>
            </div>
            <p class="checkout-note">
              Płatność realizowana przez zewnętrznego dostawcę (Hostinger Checkout).
            </p>
          </div>
        </div>
      </div>
    </section>

    <style>
    .checkout-wrapper {{ max-width: 1224px; margin: 0 auto; padding: 0 16px; }}
    .checkout-header {{ margin-bottom: 32px; }}
    .checkout-header h1 {{ font-family: 'Playfair Display', serif; font-size: 32px; color: #1a1a1a; margin: 0 0 8px; }}
    .checkout-header p {{ font-family: 'Rubik', sans-serif; color: #666; }}
    .checkout-layout {{ display: flex; gap: 40px; }}
    .checkout-items {{ flex: 1.5; }}
    .checkout-item {{ display: flex; gap: 16px; padding: 16px 0; border-bottom: 1px solid #eee; }}
    .checkout-item-img {{ width: 100px; height: 100px; object-fit: cover; }}
    .checkout-item-info h3 {{ font-family: 'Rubik', sans-serif; font-size: 16px; margin: 0 0 4px; }}
    .checkout-item-price {{ font-weight: 700; color: #1a1a1a; }}
    .checkout-summary {{ flex: 1; background: #f9f9f9; padding: 24px; border-radius: 8px; }}
    .checkout-summary h2 {{ font-family: 'Playfair Display', serif; font-size: 24px; margin: 0 0 16px; }}
    .checkout-summary-row {{ display: flex; justify-content: space-between; padding: 8px 0; font-family: 'Rubik', sans-serif; font-size: 15px; }}
    .checkout-summary-total {{ font-weight: 700; font-size: 18px; border-top: 2px solid #1a1a1a; margin-top: 8px; padding-top: 12px; }}
    .checkout-note {{ font-family: 'Rubik', sans-serif; font-size: 13px; color: #999; margin-top: 24px; }}
    @media (max-width: 768px) {{ .checkout-layout {{ flex-direction: column; }} }}
    </style>'''

    return assemble_page("Kasa | Fida", content)


# ── Build all pages ────────────────────────────────────────────────────

PAGES = {
    "sklep": build_sklep(),
    "regulamin-sklepu": build_static_page("regulamin-sklepu.html", "Regulamin Sklepu | Fida"),
    "polityka-prywatnosci": build_static_page("polityka-prywatnosci.html", "Polityka Prywatności | Fida"),
    "polityka-zwrotow": build_static_page("polityka-zwrotow.html", "Polityka Zwrotów | Fida"),
    "torba-zakupowa-w-czerwonosci": build_product_page("torba-zakupowa-w-czerwonosci"),
    "checkout": build_checkout(),
}

# Note: extra product pages (brelok-*, etc.) are not generated by default.
# Add them here if you want all product detail pages:

for name, html in PAGES.items():
    path = OUT / f"{name}.html"
    path.write_text(html)
    size_kb = len(html) / 1024
    print(f"  {path.name:45s}  {size_kb:>8.1f} KB")

print(f"\nAll {len(PAGES)} pages written to {OUT}/")
print("\nNote: CSS files are in wordpress_fida/_astro-1779472190601/ (already copied)")
print("To use in WordPress:")
print("  1. Upload the entire wordpress_fida/ folder to your WP root or theme")
print("  2. Or use 'Custom HTML' blocks and update CSS/image paths as needed")
