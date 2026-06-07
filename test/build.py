#!/usr/bin/env python3
"""Generate Fida WordPress.com import files in test/.

Outputs:
  test/header.gutenberg.html  → Edytor → Szablony → Header
  test/footer.gutenberg.html  → Edytor → Szablony → Footer
  test/css-dodatkowy.css      → Wygląd → Dostosuj → Dodatkowy CSS
  test/INSTRUKCJA.md          → krok po kroku

Source data: wordpress_fida/{header,footer}.html, STYLE-GUIDE.md
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "wordpress_fida"
OUT = Path(__file__).resolve().parent


# ── 1. Header (kopia 1:1 z wordpress_fida/header.html, filtr usunięty) ─
# wordpress_fida/header.html miał `filter:brightness(0) invert(1)` na <img>
# — to odwracało czerwone logo na białe. Oryginał Zyro w single_file/ nie
# ma tego filtra: logo (logo_fidaczerwieni-...avif) jest czerwone i
# renderowane naturalnie na bordowym tle headera (#1f0a0a).
_header_html = (SRC / "header.html").read_text(encoding="utf-8")
_header_html = _header_html.replace(
    'filter:brightness(0) invert(1)',
    '',
)
# Wyczyść pusty `style="..."` po usunięciu filtra
import re as _re
_header_html = _re.sub(r' style=""', '', _header_html)
(OUT / "header.gutenberg.html").write_text(_header_html, encoding="utf-8")

# Skopiuj avif logo do test/ dla wygody (gdyby user chciał wrzucić do Media)
import shutil
_logo_src = SRC.parent / "single_file" / "logo_fidaczerwieni-Yleqr8eqWrTbbxZV.avif"
if _logo_src.exists():
    shutil.copy(_logo_src, OUT / "logo.avif")


# ── 2. Footer (1:1 z single_file, hardcoded) ────────────────────────────
# single_file/Sklep renderowany footer: H3 "© 2026." + "All Rights Reserved."
# + 3 linki w kolumnie (Regulamin Sklepu / Polityka Prywatności / Polityka Zwrotów)
FOOTER_HTML = '''<!-- Fida shop footer. Paste as Custom HTML block in: Wygląd → Edytor → Szablon: Footer -->
<footer class="fida-footer" style="background:#1f0a0a;color:#fff;padding:32px 40px;margin-top:0;font-family:Rubik,sans-serif;display:flex;flex-direction:column;gap:12px;align-items:flex-start">
  <h3 style="color:#fff;font-family:Rubik,sans-serif;font-weight:300;font-size:12px;line-height:1.3;margin:0">
    © 2026 Fida. Wszelkie prawa zastrzeżone.
  </h3>
  <nav style="display:flex;flex-direction:column;gap:8px">
    <a href="/regulamin-sklepu/" style="color:#fff;font-family:'Playfair Display',serif;font-weight:400;font-size:16px;line-height:1.3;text-decoration:underline">Regulamin Sklepu</a>
    <a href="/polityka-prywatnosci/" style="color:#fff;font-family:'Playfair Display',serif;font-weight:400;font-size:16px;line-height:1.3;text-decoration:underline">Polityka Prywatności</a>
    <a href="/polityka-zwrotow/" style="color:#fff;font-family:'Playfair Display',serif;font-weight:400;font-size:16px;line-height:1.3;text-decoration:underline">Polityka Zwrotów</a>
  </nav>
</footer>
'''

(OUT / "footer.gutenberg.html").write_text(FOOTER_HTML, encoding="utf-8")


# ── 3. CSS dodatkowy ────────────────────────────────────────────────────
CSS = r"""/* =========================================================================
   Fida — Dodatkowy CSS (Wygląd → Dostosuj → Dodatkowy CSS)
   Źródło: STYLE-GUIDE.md (sekcja WooCommerce overrides) + rozszerzenia
   ========================================================================= */

/* ── Fonty (Google Fonts) ───────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500&family=Rubik:wght@400;500;600&display=swap');

/* ── Bazowe typografie i kolory ────────────────────────────────────── */
body, .woocommerce {
  font-family: 'Rubik', sans-serif;
  color: #1a1a1a;
  background: #fff;
}
h1, h2, h3, h4,
.woocommerce div.product h1.product_title,
.woocommerce h1.page-title {
  font-family: 'Playfair Display', serif;
  font-weight: 400;
  color: #1a1a1a;
}

/* ── Breadcrumb ────────────────────────────────────────────────────── */
.woocommerce-breadcrumb,
.woocommerce nav.woocommerce-breadcrumb {
  font-family: 'Rubik', sans-serif;
  font-size: 13px;
  color: #666;
  margin: 24px 0;
  padding: 0 40px;
  max-width: 1280px;
  margin-left: auto;
  margin-right: auto;
}
.woocommerce-breadcrumb a,
.woocommerce nav.woocommerce-breadcrumb a {
  color: #666;
  text-decoration: none;
}
.woocommerce-breadcrumb a:hover {
  color: #1a1a1a;
}

/* ── Kontener główny produktu (max-width 1280, wycentrowany) ──────── */
.woocommerce div.product,
.woocommerce .single-product-wrapper,
.woocommerce .product {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 40px 80px;
}

/* ── Single product — układ 2-kolumnowy (galeria | info) ───────────── */
.woocommerce div.product {
  display: grid;
  grid-template-columns: minmax(0, 600px) 1fr;
  gap: 64px;
  align-items: flex-start;
}
.woocommerce div.product .woocommerce-product-gallery {
  position: sticky;
  top: 100px;
  max-width: 600px;
  width: 100%;
  background: #fff;
}
.woocommerce div.product .summary.entry-summary {
  padding-top: 8px;
}

/* Tytuł produktu */
.woocommerce div.product h1.product_title {
  font-family: 'Playfair Display', serif;
  font-size: 36px;
  font-weight: 400;
  margin: 0 0 16px;
  color: #1a1a1a;
  line-height: 1.2;
}

/* Cena */
.woocommerce div.product p.price,
.woocommerce div.product span.price {
  font-family: 'Rubik', sans-serif;
  font-size: 20px;
  color: #1a1a1a;
  font-weight: 500;
  margin: 0 0 24px;
}
.woocommerce div.product p.price del {
  color: #999;
  font-weight: 400;
}

/* Excerpt (krótki opis) */
.woocommerce div.product .woocommerce-product-details__short-description {
  font-family: 'Rubik', sans-serif;
  font-size: 15px;
  color: #1a1a1a;
  line-height: 1.6;
  margin: 0 0 24px;
}

/* ── Przycisk "Dodaj do koszyka" ────────────────────────────────────── */
.woocommerce a.button,
.woocommerce button.button,
.woocommerce input.button,
.woocommerce #respond input#submit,
.wc-block-components-button,
.woocommerce button.single_add_to_cart_button {
  background-color: #1f0a0a !important;
  color: #fff !important;
  border-radius: 4px !important;
  font-family: 'Rubik', sans-serif !important;
  font-weight: 500 !important;
  padding: 12px 24px !important;
  border: 0 !important;
  transition: background-color .2s;
  cursor: pointer;
}
.woocommerce a.button:hover,
.woocommerce button.button:hover,
.woocommerce input.button:hover,
.woocommerce button.single_add_to_cart_button:hover,
.wc-block-components-button:hover {
  background-color: #e3342f !important;
  color: #fff !important;
}
.woocommerce button.single_add_to_cart_button {
  width: 100%;
  padding: 18px 24px !important;
  font-size: 15px !important;
  letter-spacing: .5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

/* Ilość (+/-) */
.woocommerce .quantity {
  display: inline-flex;
  align-items: center;
  border: 1px solid #d4d4d4;
  background: #fff;
  width: fit-content;
  margin-bottom: 16px;
}
.woocommerce .quantity .qty {
  width: 56px;
  height: 48px;
  border: 0;
  border-left: 1px solid #d4d4d4;
  border-right: 1px solid #d4d4d4;
  text-align: center;
  font-family: 'Rubik', sans-serif;
  font-size: 16px;
  color: #1a1a1a;
  background: transparent;
  -moz-appearance: textfield;
}

/* ── Meta (kategoria, SKU) ─────────────────────────────────────────── */
.woocommerce div.product .product_meta {
  font-family: 'Rubik', sans-serif;
  font-size: 13px;
  color: #666;
  border-top: 1px solid #eee;
  padding-top: 16px;
  margin-top: 16px;
}
.woocommerce div.product .product_meta a {
  color: #1a1a1a;
  text-decoration: underline;
}

/* ── Zakładki (Opis, Dodatkowe informacje) ─────────────────────────── */
.woocommerce div.product .woocommerce-tabs {
  grid-column: 1 / -1;
  margin-top: 64px;
  border-top: 1px solid #eee;
  padding-top: 40px;
}
.woocommerce div.product .woocommerce-tabs .panel h2 {
  font-family: 'Playfair Display', serif;
  font-size: 24px;
  font-weight: 400;
  margin: 0 0 16px;
  color: #1a1a1a;
}
.woocommerce div.product .woocommerce-tabs .panel,
.woocommerce div.product .woocommerce-Tabs-panel {
  font-family: 'Rubik', sans-serif;
  font-size: 15px;
  color: #1a1a1a;
  line-height: 1.7;
}
.woocommerce div.product .shop_attributes {
  width: 100%;
  max-width: 520px;
  border-collapse: collapse;
  font-family: 'Rubik', sans-serif;
  font-size: 14px;
}
.woocommerce div.product .shop_attributes th,
.woocommerce div.product .shop_attributes td {
  text-align: left;
  padding: 10px 16px 10px 0;
  font-weight: 400;
  border-bottom: 1px solid #eee;
}
.woocommerce div.product .shop_attributes th {
  color: #666;
  width: 60%;
}

/* ── Ribbon "Nowość" (pseudo-element na galerii) ─────────────────────
   Wymaga: produkt w Kokpit → Produkty → Szybka edycja → w polu
   "Klasy CSS produktu" dodaj: fida-nowosc
   Albo ustaw atrybut w PRODUCT DATA → zaawansowane → CSS class.
*/
.woocommerce div.product.product.fida-nowosc .woocommerce-product-gallery::before,
.woocommerce div.product.fida-nowosc .woocommerce-product-gallery::before {
  content: "Nowość";
  position: absolute;
  top: 0;
  left: 0;
  background: #1d1e20;
  color: #fff;
  padding: 6px 12px;
  font-family: 'Rubik', sans-serif;
  font-size: 11px;
  line-height: 1;
  z-index: 2;
}

/* Warianty rozmiaru (koszulki) — select stylowany */
.woocommerce div.product form.cart .variations {
  margin-bottom: 16px;
  width: 100%;
}
.woocommerce div.product form.cart .variations td,
.woocommerce div.product form.cart .variations th {
  padding: 4px 8px 4px 0;
  font-family: 'Rubik', sans-serif;
  font-size: 14px;
  color: #1a1a1a;
  vertical-align: middle;
}
.woocommerce div.product form.cart .variations select {
  font-family: 'Rubik', sans-serif;
  font-size: 14px;
  padding: 8px 12px;
  border: 1px solid #d4d4d4;
  border-radius: 4px;
  background: #fff;
  color: #1a1a1a;
  min-width: 200px;
}
.woocommerce div.product form.cart .reset_variations {
  font-size: 12px;
  color: #e3342f;
}

/* ── Karty produktów (archive / shop page) ─────────────────────────── */
.woocommerce ul.products,
.wc-block-grid {
  display: grid !important;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 40px;
}
@media (max-width: 1024px) {
  .woocommerce ul.products,
  .wc-block-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .woocommerce ul.products,
  .wc-block-grid { grid-template-columns: 1fr; }
}

.woocommerce ul.products li.product,
.wc-block-grid__product {
  border: 1px solid #e0e0e0 !important;
  border-radius: 4px !important;
  background: #fff !important;
  padding: 0 !important;
  transition: box-shadow .2s !important;
  overflow: hidden !important;
  margin: 0 !important;
  float: none !important;
  width: 100% !important;
}
.woocommerce ul.products li.product:hover,
.wc-block-grid__product:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,.08) !important;
}
.woocommerce ul.products li.product a img,
.wc-block-grid__product-image img {
  width: 100%;
  height: auto;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  display: block;
  margin: 0 !important;
}
.woocommerce ul.products li.product .woocommerce-loop-product__title,
.wc-block-grid__product-title {
  font-family: 'Playfair Display', serif !important;
  font-size: 20px !important;
  font-weight: 400 !important;
  color: #1a1a1a !important;
  padding: 12px 16px 4px !important;
  margin: 0 !important;
}
.woocommerce ul.products li.product .price,
.wc-block-grid__product-price {
  font-family: 'Rubik', sans-serif !important;
  color: #1a1a1a !important;
  font-weight: 500 !important;
  font-size: 18px !important;
  padding: 0 16px 16px !important;
}
.woocommerce ul.products li.product .button,
.wc-block-grid__product .wp-block-button__link {
  margin: 0 16px 16px !important;
  display: block !important;
  text-align: center !important;
}

/* ── Sklep (page title, wyniki) ────────────────────────────────────── */
.woocommerce .page-title,
.woocommerce-products-header__title {
  font-family: 'Playfair Display', serif !important;
  font-size: 42px !important;
  font-weight: 400 !important;
  color: #1a1a1a !important;
  max-width: 1280px;
  margin: 24px auto !important;
  padding: 0 40px;
}
.woocommerce .woocommerce-result-count,
.woocommerce .woocommerce-ordering {
  max-width: 1280px;
  margin: 0 auto 24px !important;
  padding: 0 40px;
  font-family: 'Rubik', sans-serif;
  font-size: 14px;
  color: #666;
}

/* ── "Może Cię zainteresuje" (Related Products) ────────────────────── */
.woocommerce .related.products,
.woocommerce .up-sells {
  max-width: 1280px;
  margin: 80px auto 0;
  padding: 0 40px;
  clear: both;
}
.woocommerce .related.products h2,
.woocommerce .up-sells h2 {
  font-family: 'Playfair Display', serif !important;
  font-size: 28px !important;
  font-weight: 400 !important;
  color: #1a1a1a !important;
  margin: 0 0 24px !important;
  padding: 0;
}

/* ── Strona kategorii ──────────────────────────────────────────────── */
.tax-product_cat .woocommerce-products-header {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 40px 0;
}
.tax-product_cat .woocommerce-products-header h1 {
  font-family: 'Playfair Display', serif;
  font-size: 42px;
  font-weight: 400;
  color: #1a1a1a;
  margin: 0 0 8px;
}
.tax-product_cat .woocommerce-products-header .term-description {
  font-family: 'Rubik', sans-serif;
  font-size: 15px;
  color: #666;
  line-height: 1.6;
  margin: 0 0 24px;
}

/* ── Koszyk (Cart) ─────────────────────────────────────────────────── */
.woocommerce-cart .woocommerce {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 40px 80px;
}
.woocommerce-cart h1, .woocommerce-cart h2 {
  font-family: 'Playfair Display', serif;
  font-weight: 400;
  color: #1a1a1a;
}
.woocommerce table.shop_table {
  border: 1px solid #eee;
  border-radius: 4px;
}
.woocommerce table.shop_table th {
  font-family: 'Rubik', sans-serif;
  font-size: 13px;
  color: #666;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .5px;
  border-bottom: 1px solid #eee;
}
.woocommerce table.shop_table td {
  font-family: 'Rubik', sans-serif;
  color: #1a1a1a;
  border-bottom: 1px solid #f5f5f5;
}
.woocommerce table.shop_table .product-name a {
  color: #1a1a1a;
  text-decoration: none;
  font-weight: 500;
}
.woocommerce table.shop_table .product-subtotal {
  font-weight: 500;
}
.woocommerce .cart_totals {
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 24px;
}
.woocommerce .cart_totals .order-total {
  font-size: 18px;
  font-weight: 500;
}
.woocommerce .wc-proceed-to-checkout a.checkout-button {
  background-color: #1f0a0a !important;
  color: #fff !important;
  border-radius: 4px !important;
  font-family: 'Rubik', sans-serif !important;
  font-weight: 500 !important;
  padding: 16px 24px !important;
  font-size: 15px !important;
  text-transform: none;
  letter-spacing: .5px;
}
.woocommerce .wc-proceed-to-checkout a.checkout-button:hover {
  background-color: #e3342f !important;
}

/* ── Checkout ──────────────────────────────────────────────────────── */
.woocommerce-checkout .woocommerce {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 40px 80px;
}
.woocommerce-checkout h1, .woocommerce-checkout h3 {
  font-family: 'Playfair Display', serif;
  font-weight: 400;
  color: #1a1a1a;
}
.woocommerce form.checkout_coupon,
.woocommerce form.login,
.woocommerce form.register,
.woocommerce-checkout #payment {
  border: 1px solid #eee;
  border-radius: 4px;
  background: #fafafa;
}
.woocommerce-checkout #payment #place_order {
  background-color: #1f0a0a !important;
  color: #fff !important;
  border-radius: 4px !important;
  font-family: 'Rubik', sans-serif !important;
  font-weight: 500 !important;
  padding: 16px 24px !important;
  font-size: 15px !important;
  width: 100%;
}
.woocommerce-checkout #payment #place_order:hover {
  background-color: #e3342f !important;
}

/* ── WC Blocks (nowe bloki koszyka i checkout) ─────────────────────── */
.wc-block-cart__submit-button,
.wc-block-components-button {
  background-color: #1f0a0a !important;
  color: #fff !important;
  border-radius: 4px !important;
  font-family: 'Rubik', sans-serif !important;
  font-weight: 500 !important;
}
.wc-block-cart__submit-button:hover,
.wc-block-components-button:hover {
  background-color: #e3342f !important;
}

/* ── Powiadomienia / komunikaty ────────────────────────────────────── */
.woocommerce-message,
.woocommerce-info,
.woocommerce-error,
.woocommerce-notice {
  font-family: 'Rubik', sans-serif;
  border-radius: 4px;
  border-top-color: #e3342f;
}
.woocommerce-message::before,
.woocommerce-info::before {
  color: #e3342f;
}

/* ── Responsywność ─────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .woocommerce div.product,
  .woocommerce .single-product-wrapper,
  .woocommerce .product {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 0 20px 60px;
  }
  .woocommerce div.product .woocommerce-product-gallery {
    position: static;
    max-width: 100%;
  }
  .woocommerce-breadcrumb,
  .woocommerce ul.products,
  .wc-block-grid,
  .woocommerce-cart .woocommerce,
  .woocommerce-checkout .woocommerce,
  .woocommerce .page-title,
  .woocommerce-products-header,
  .woocommerce .related.products {
    padding-left: 20px;
    padding-right: 20px;
  }
  .woocommerce div.product h1.product_title {
    font-size: 28px;
  }
}
"""

(OUT / "css-dodatkowy.css").write_text(CSS, encoding="utf-8")


# ── 4. INSTRUKCJA.md ────────────────────────────────────────────────────
INSTRUKCJA = r"""# Fida — Instrukcja wgrania (WordPress.com)

3 kroki, ~15 minut. Produkty WooCommerce zostają, nie tworzysz żadnych nowych stron produktów.

## Krok 1 — Header

1. Kokpit → **Wygląd** → **Edytor** (Edytor witryny / Site Editor)
2. Po lewej: **Szablony** → **Header**
3. Kliknij w obszar headera, aby go edytować
4. ⋮ (trzy kropki w prawym górnym rogu) → **Edytor kodu** (włącza tryb code editor)
5. Zaznacz wszystko, usuń, wklej całą zawartość pliku `test/header.gutenberg.html`
6. **Zapisz**

## Krok 2 — Footer

1. j.w. → **Szablony** → **Footer**
2. j.w. → Edytor kodu → wklej `test/footer.gutenberg.html`
3. **Zapisz**

## Krok 3 — Dodatkowy CSS

1. Kokpit → **Wygląd** → **Dostosuj** (Customizer)
2. Na dole: **Dodatkowy CSS**
3. Otwórz plik `test/css-dodatkowy.css`, skopiuj całość, wklej w pole Dodatkowy CSS
4. **Opublikuj**

## Krok 4 — Test

Otwórz w nowej karcie (wymuś `Ctrl/Cmd + Shift + R`, pomiń cache):

- `/sklep/` — karty produktów z borderem, hover, 4 kolumny
- `/produkt/{slug}/` — produkt w układzie 2-kolumnowym, cena, "Dodaj do koszyka" ciemnoczerwone
- `/koszyk/` — tabela koszyka, przycisk "Do kasy" ciemnoczerwony
- `/zamowienie/` — formularz checkout, przycisk "Złóż zamówienie" ciemnoczerwony
- `/regulamin-sklepu/`, `/polityka-prywatnosci/`, `/polityka-zwrotow/` — strony informacyjne, header/footer w nowym stylu

## Ribbon "Nowość" na obrazku produktu (opcjonalnie)

Domyślnie ribbon nie pojawia się (brak custom fields na WP.com Free). Aby go włączyć dla wybranych produktów:

1. Kokpit → **Produkty** → wybierz produkt
2. Po prawej: **Atrybuty produktu** → **Klasa CSS produktu** → wpisz `fida-nowosc`
3. **Aktualizuj**

Ribbon pojawi się w lewym górnym rogu galerii.

## Co działa, a czego nie

| Element | Status |
|---|---|
| Header / footer (1:1 z oryginału) | ✅ |
| Sklep — karty produktów, grid 4 kol, hover, badge | ✅ |
| Kategoria produktu (Breloki/Torby/Koszulki) — strona WC | ✅ |
| Produkt — układ 2-kol, galeria, cena, "Dodaj do koszyka" | ✅ ~85% 1:1 |
| Warianty rozmiaru (koszulki XS–2XL) | ✅ przez WC natywnie |
| Powiązane produkty ("Może Cię zainteresuje") | ✅ WC related + CSS |
| Koszyk, Checkout | ✅ |
| Regulamin, Polityki, Refund | ✅ |
| Dodatkowa tabela wymiarów w opisie | ✅ użyj atrybutów produktu w Kokpicie |
| Ribbon "Nowość" | ⚠️ wymaga ręcznego dodania klasy CSS (powyżej) |
| Własne dodatkowe sekcje na stronie produktu | ❌ wymaga Pro/Business+ |

## Gdyby coś nie działało

- **Elementor nadpisuje CSS** — niektóre motywy mają agresywne style Elementora. W takim wypadku sprawdź czy header/footer w Edytorze Szablonu nie został nadpisany przez Elementor Theme Builder (jeśli był używany).
- **Custom HTML pusty po wklejeniu** — upewnij się, że jesteś w trybie "Edytor kodu", nie wizualnym. Custom HTML w trybie wizualnym stripuje niektóre atrybuty.
- **Czcionki nie ładują się** — sprawdź czy domena ma HTTPS (Google Fonts wymaga secure context).
"""

(OUT / "INSTRUKCJA.md").write_text(INSTRUKCJA, encoding="utf-8")


# ── 5. Preview (lokalne mocki stron do testów w przeglądarce) ───────────
PREVIEW = OUT / "preview"
PREVIEW.mkdir(exist_ok=True)

# Wspólny head: Google Fonts + bazowe style + CSS z css-dodatkowy.css
HEAD = '''<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{title} — Fida preview</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500&family=Rubik:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
{CSS}
  </style>
</head>
<body class="{body_class}">'''


def strip_comment(s: str) -> str:
    """Usuwa pierwszy komentarz HTML (instrukcja w plikach gutenberg)."""
    import re
    return re.sub(r"^<!--.*?-->\s*", "", s, flags=re.DOTALL)


def fix_links(html: str) -> str:
    """Zamienia wewnętrzne linki relative na # żeby działały w file://."""
    import re
    html = re.sub(r'href="/[^"]*"', 'href="#"', html)
    html = re.sub(r'href="sklep\.html"', 'href="shop.html"', html)
    return html


HEADER_INNER = fix_links(strip_comment((OUT / "header.gutenberg.html").read_text(encoding="utf-8")))
FOOTER_INNER = fix_links(strip_comment((OUT / "footer.gutenberg.html").read_text(encoding="utf-8")))
CSS_INNER = strip_comment((OUT / "css-dodatkowy.css").read_text(encoding="utf-8"))


def page(title: str, body_class: str, content: str) -> str:
    return (
        HEAD.format(title=title, body_class=body_class, CSS=CSS_INNER)
        + HEADER_INNER
        + content
        + FOOTER_INNER
        + "</body></html>"
    )


# ── index.html (landing) ───────────────────────────────────────────────
INDEX_BODY = '''
<main style="max-width:1280px;margin:0 auto;padding:80px 40px;font-family:Rubik,sans-serif">
  <h1 style="font-family:'Playfair Display',serif;font-size:42px;font-weight:400;margin:0 0 8px;color:#1a1a1a">Fida — lokalny podgląd</h1>
  <p style="font-size:15px;color:#666;margin:0 0 48px">Self-contained mocki stron z headerem, footerem i CSS-em identycznym jak ten, który wgrasz do WordPress.</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px">
    <a href="header.html" style="display:block;border:1px solid #e0e0e0;border-radius:4px;padding:32px;text-decoration:none;color:#1a1a1a;background:#fff;transition:box-shadow .2s">
      <h2 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:400;margin:0 0 8px">Header (sticky)</h2>
      <p style="margin:0;color:#666;font-size:14px">Sam header + placeholder content</p>
    </a>
    <a href="footer.html" style="display:block;border:1px solid #e0e0e0;border-radius:4px;padding:32px;text-decoration:none;color:#1a1a1a;background:#fff;transition:box-shadow .2s">
      <h2 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:400;margin:0 0 8px">Footer</h2>
      <p style="margin:0;color:#666;font-size:14px">Placeholder + sam footer</p>
    </a>
    <a href="shop.html" style="display:block;border:1px solid #e0e0e0;border-radius:4px;padding:32px;text-decoration:none;color:#1a1a1a;background:#fff;transition:box-shadow .2s">
      <h2 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:400;margin:0 0 8px">Sklep</h2>
      <p style="margin:0;color:#666;font-size:14px">Grid 4 kol, karty z hover</p>
    </a>
    <a href="product.html" style="display:block;border:1px solid #e0e0e0;border-radius:4px;padding:32px;text-decoration:none;color:#1a1a1a;background:#fff;transition:box-shadow .2s">
      <h2 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:400;margin:0 0 8px">Produkt</h2>
      <p style="margin:0;color:#666;font-size:14px">Layout 2-kol, galeria + info</p>
    </a>
    <a href="cart.html" style="display:block;border:1px solid #e0e0e0;border-radius:4px;padding:32px;text-decoration:none;color:#1a1a1a;background:#fff;transition:box-shadow .2s">
      <h2 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:400;margin:0 0 8px">Koszyk</h2>
      <p style="margin:0;color:#666;font-size:14px">Tabela + podsumowanie</p>
    </a>
    <a href="checkout.html" style="display:block;border:1px solid #e0e0e0;border-radius:4px;padding:32px;text-decoration:none;color:#1a1a1a;background:#fff;transition:box-shadow .2s">
      <h2 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:400;margin:0 0 8px">Checkout</h2>
      <p style="margin:0;color:#666;font-size:14px">Formularz + płatność</p>
    </a>
  </div>
</main>
'''
(PREVIEW / "index.html").write_text(page("Index", "", INDEX_BODY), encoding="utf-8")


# ── header.html ─────────────────────────────────────────────────────────
HEADER_BODY = '''
<main style="max-width:1280px;margin:0 auto;padding:80px 40px;font-family:Rubik,sans-serif">
  <h1 style="font-family:'Playfair Display',serif;font-size:42px;font-weight:400;margin:0 0 24px">Header w izolacji</h1>
  <p style="font-size:15px;color:#1a1a1a;line-height:1.7;max-width:720px">
    Header jest <em>sticky</em> (przykleja się do góry przy scrollu). Sprawdź:
  </p>
  <ul style="font-size:15px;color:#1a1a1a;line-height:1.7;max-width:720px">
    <li>czy logo wyświetla się poprawnie (wymaga HTTPS do assets.zyrosite.com)</li>
    <li>czy fonty się ładują (Rubik, Playfair Display)</li>
    <li>kliknij w linki — w mocku prowadzą do # (placeholder)</li>
    <li>scroll w dół — header zostaje na górze</li>
  </ul>
  <div style="height:1500px;background:linear-gradient(180deg,#fafafa 0%,#fff 100%);margin-top:32px;border-radius:4px"></div>
</main>
'''
(PREVIEW / "header.html").write_text(page("Header", "", HEADER_BODY), encoding="utf-8")


# ── footer.html ─────────────────────────────────────────────────────────
FOOTER_BODY = '''
<main style="max-width:1280px;margin:0 auto;padding:80px 40px;font-family:Rubik,sans-serif;min-height:60vh">
  <h1 style="font-family:'Playfair Display',serif;font-size:42px;font-weight:400;margin:0 0 24px">Footer w izolacji</h1>
  <p style="font-size:15px;color:#1a1a1a;line-height:1.7;max-width:720px">
    Stopka 1:1 z single_file. Linki prowadzą do <code>#</code> (placeholder).
  </p>
</main>
'''
(PREVIEW / "footer.html").write_text(page("Footer", "", FOOTER_BODY), encoding="utf-8")


# ── shop.html (mock strony sklepu z 4 kartami) ──────────────────────────
SHOP_BODY = '''
<nav class="woocommerce-breadcrumb" aria-label="Ścieżka">
  <a href="index.html">Strona główna</a>
  <span style="margin:0 8px">/</span>
  <span style="color:#1a1a1a">Sklep</span>
</nav>
<div class="woocommerce" style="max-width:1280px;margin:0 auto;padding:0 40px 80px">
  <h1 class="page-title" style="font-family:'Playfair Display',serif;font-size:42px;font-weight:400;color:#1a1a1a;margin:0 0 24px">Sklep</h1>
  <p class="woocommerce-result-count" style="font-family:Rubik,sans-serif;font-size:14px;color:#666;margin:0 0 24px">Wyświetlanie 1–6 z 6 produktów</p>

  <ul class="products" style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;list-style:none;padding:0;margin:0">
'''
for i, (title, price, color) in enumerate([
    ("Brelok W Kącie Kurz",         "59,00 zł", "#1a1a1a"),
    ("Brelok Miodowe Lata",         "59,00 zł", "#8b4513"),
    ("Brelok Upadek W Tramwaju",    "59,00 zł", "#e3342f"),
    ("Torba Zakupowa W Czerwoności","69,00 zł", "#e3342f"),
    ("Torba Zakupowa W Kremie",     "69,00 zł", "#f5f5dc"),
    ("Biała Koszulka — Ideał",      "89,00 zł", "#1a1a1a"),
]):
    SHOP_BODY += f'''
    <li class="product" style="border:1px solid #e0e0e0;border-radius:4px;background:#fff;overflow:hidden;transition:box-shadow .2s">
      <a href="product.html" style="text-decoration:none;color:inherit">
        <div style="aspect-ratio:1/1;background:{color};display:flex;align-items:center;justify-content:center;font-family:'Playfair Display',serif;font-size:24px;color:#fff">img</div>
        <h2 class="woocommerce-loop-product__title" style="font-family:'Playfair Display',serif;font-size:20px;font-weight:400;color:#1a1a1a;padding:12px 16px 4px;margin:0">{title}</h2>
        <span class="price" style="font-family:Rubik,sans-serif;color:#1a1a1a;font-weight:500;font-size:18px;padding:0 16px 16px;display:block">{price}</span>
      </a>
    </li>'''
SHOP_BODY += '''
  </ul>
</div>
'''
(PREVIEW / "shop.html").write_text(page("Sklep", "", SHOP_BODY), encoding="utf-8")


# ── product.html (mock strony produktu 2-kol) ───────────────────────────
PRODUCT_BODY = '''
<nav class="woocommerce-breadcrumb" aria-label="Ścieżka">
  <a href="index.html">Strona główna</a>
  <span style="margin:0 8px">/</span>
  <a href="shop.html">Sklep</a>
  <span style="margin:0 8px">/</span>
  <a href="#">Torby</a>
  <span style="margin:0 8px">/</span>
  <span style="color:#1a1a1a">Torba Zakupowa W Czerwoności</span>
</nav>
<div class="woocommerce">
  <div class="product type-product" itemscope itemtype="https://schema.org/Product" style="display:grid;grid-template-columns:minmax(0,600px) 1fr;gap:64px;align-items:flex-start;max-width:1280px;margin:0 auto;padding:0 40px 80px">
    <div class="woocommerce-product-gallery" style="position:sticky;top:100px;max-width:600px;background:#fff">
      <span class="fida-ribbon" style="position:absolute;top:0;left:0;background:#1d1e20;color:#fff;padding:6px 12px;font-family:Rubik,sans-serif;font-size:11px;z-index:2">Nowość</span>
      <div style="aspect-ratio:1/1;background:#e3342f;display:flex;align-items:center;justify-content:center;font-family:'Playfair Display',serif;font-size:24px;color:#fff">img</div>
    </div>
    <div class="summary entry-summary">
      <p style="font-family:Rubik,sans-serif;font-size:13px;color:#666;margin:0 0 8px"><a href="#" style="color:#666;text-decoration:none">Torby</a></p>
      <h1 class="product_title entry-title" itemprop="name" style="font-family:'Playfair Display',serif;font-size:36px;font-weight:400;margin:0 0 16px;color:#1a1a1a;line-height:1.2">Torba Zakupowa W Czerwoności</h1>
      <p class="price" style="font-family:Rubik,sans-serif;font-size:20px;color:#1a1a1a;font-weight:500;margin:0 0 24px"><span style="font-weight:500">69,00 zł</span></p>
      <div class="woocommerce-product-details__short-description" style="font-family:Rubik,sans-serif;font-size:15px;color:#1a1a1a;line-height:1.6;margin:0 0 24px">
        <p style="margin:0 0 12px">Duża, solidna torba zakupowa w kolorze czerwieni z minimalistycznym, klasycznym designem. Idealnie sprawdzi się na zakupy, na co dzień i na koncert.</p>
      </div>
      <form class="cart" method="get" style="margin:0 0 24px">
        <div class="quantity" style="display:inline-flex;align-items:center;border:1px solid #d4d4d4;background:#fff;width:fit-content;margin-bottom:16px">
          <button type="button" style="width:48px;height:48px;background:transparent;border:0;cursor:pointer;font-size:18px;color:#1a1a1a;font-family:Rubik,sans-serif">−</button>
          <input type="number" class="qty" name="quantity" value="1" min="1" max="99" style="width:56px;height:48px;border:0;border-left:1px solid #d4d4d4;border-right:1px solid #d4d4d4;text-align:center;font-family:Rubik,sans-serif;font-size:16px;color:#1a1a1a;background:transparent">
          <button type="button" style="width:48px;height:48px;background:transparent;border:0;cursor:pointer;font-size:18px;color:#1a1a1a;font-family:Rubik,sans-serif">+</button>
        </div>
        <button type="submit" class="single_add_to_cart_button button alt" style="display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:18px 24px;background:#1f0a0a;color:#fff;border:0;font-family:Rubik,sans-serif;font-size:15px;font-weight:500;letter-spacing:.5px;cursor:pointer">Dodaj do koszyka</button>
      </form>
      <div class="product_meta" style="font-family:Rubik,sans-serif;font-size:13px;color:#666;border-top:1px solid #eee;padding-top:16px;margin-top:16px">
        <p style="margin:0 0 4px"><span style="color:#1a1a1a">Kategoria:</span> <a href="#" style="color:#1a1a1a;text-decoration:underline">Torby</a></p>
        <p style="margin:0">SKU: <span style="color:#1a1a1a">FIDA-TORBA-CZ</span></p>
      </div>
    </div>
  </div>

  <div class="woocommerce-tabs" style="max-width:1280px;margin:0 auto;padding:0 40px 80px;border-top:1px solid #eee;padding-top:40px">
    <h2 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:400;margin:0 0 16px;color:#1a1a1a">Opis</h2>
    <ul style="font-family:Rubik,sans-serif;font-size:15px;color:#1a1a1a;line-height:1.7;padding-left:20px;margin:0 0 24px">
      <li>Wykonana z włókien bawełny (bawełna 100%)</li>
      <li>Starannie wykonane szycie, mocny splot drelichowy typu panama</li>
      <li>Nadaje się do prania</li>
      <li>Produkt polski</li>
    </ul>
    <h3 style="font-family:Rubik,sans-serif;font-size:16px;font-weight:500;margin:24px 0 12px;color:#1a1a1a">Wymiary</h3>
    <table class="shop_attributes" style="width:100%;max-width:520px;border-collapse:collapse;font-family:Rubik,sans-serif;font-size:14px">
      <tbody>
        <tr style="border-bottom:1px solid #eee"><th style="text-align:left;padding:10px 16px 10px 0;font-weight:400;color:#666;width:60%">długość</th><td style="padding:10px 0">56 cm</td></tr>
        <tr style="border-bottom:1px solid #eee"><th style="text-align:left;padding:10px 16px 10px 0;font-weight:400;color:#666">wysokość</th><td style="padding:10px 0">37 cm</td></tr>
        <tr style="border-bottom:1px solid #eee"><th style="text-align:left;padding:10px 16px 10px 0;font-weight:400;color:#666">szerokość przy podstawie</th><td style="padding:10px 0">14 cm</td></tr>
      </tbody>
    </table>
  </div>
</div>
'''
(PREVIEW / "product.html").write_text(page("Produkt", "", PRODUCT_BODY), encoding="utf-8")


# ── cart.html (mock koszyka) ────────────────────────────────────────────
CART_BODY = '''
<div class="woocommerce-cart">
  <div class="woocommerce">
    <h1 style="font-family:'Playfair Display',serif;font-size:42px;font-weight:400;margin:24px 0 8px;color:#1a1a1a">Koszyk</h1>
    <table class="shop_table" style="width:100%;border:1px solid #eee;border-radius:4px;border-collapse:collapse;margin:24px 0">
      <thead>
        <tr style="border-bottom:1px solid #eee">
          <th style="font-family:Rubik,sans-serif;font-size:13px;color:#666;font-weight:500;text-transform:uppercase;letter-spacing:.5px;padding:16px;text-align:left">Produkt</th>
          <th style="font-family:Rubik,sans-serif;font-size:13px;color:#666;font-weight:500;text-transform:uppercase;letter-spacing:.5px;padding:16px;text-align:left">Cena</th>
          <th style="font-family:Rubik,sans-serif;font-size:13px;color:#666;font-weight:500;text-transform:uppercase;letter-spacing:.5px;padding:16px;text-align:left">Ilość</th>
          <th style="font-family:Rubik,sans-serif;font-size:13px;color:#666;font-weight:500;text-transform:uppercase;letter-spacing:.5px;padding:16px;text-align:left">Suma</th>
        </tr>
      </thead>
      <tbody>
        <tr style="border-bottom:1px solid #f5f5f5">
          <td style="font-family:Rubik,sans-serif;padding:16px">
            <div style="display:flex;gap:16px;align-items:center">
              <div style="width:64px;height:64px;background:#e3342f;flex-shrink:0"></div>
              <a href="product.html" style="color:#1a1a1a;text-decoration:none;font-weight:500">Torba Zakupowa W Czerwoności</a>
            </div>
          </td>
          <td style="font-family:Rubik,sans-serif;padding:16px">69,00 zł</td>
          <td style="font-family:Rubik,sans-serif;padding:16px">1</td>
          <td style="font-family:Rubik,sans-serif;padding:16px;font-weight:500">69,00 zł</td>
        </tr>
      </tbody>
    </table>
    <div class="cart_totals" style="background:#fafafa;border:1px solid #eee;border-radius:4px;padding:24px;max-width:400px;margin-left:auto">
      <h2 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:400;margin:0 0 16px;color:#1a1a1a">Podsumowanie</h2>
      <table style="width:100%;border-collapse:collapse;font-family:Rubik,sans-serif;font-size:14px">
        <tr><td style="padding:8px 0;color:#666">Suma częściowa</td><td style="padding:8px 0;text-align:right">69,00 zł</td></tr>
        <tr><td style="padding:8px 0;color:#666">Dostawa</td><td style="padding:8px 0;text-align:right">—</td></tr>
        <tr class="order-total" style="font-size:18px;font-weight:500"><td style="padding:16px 0 8px;border-top:1px solid #eee">Razem</td><td style="padding:16px 0 8px;text-align:right;border-top:1px solid #eee">69,00 zł</td></tr>
      </table>
      <div class="wc-proceed-to-checkout" style="margin-top:16px">
        <a href="checkout.html" class="checkout-button button alt wc-forward" style="display:block;text-align:center;background:#1f0a0a;color:#fff;border-radius:4px;font-family:Rubik,sans-serif;font-weight:500;padding:16px 24px;font-size:15px;text-decoration:none">Przejdź do kasy</a>
      </div>
    </div>
  </div>
</div>
'''
(PREVIEW / "cart.html").write_text(page("Koszyk", "", CART_BODY), encoding="utf-8")


# ── checkout.html (mock checkout) ───────────────────────────────────────
CHECKOUT_BODY = '''
<div class="woocommerce-checkout">
  <div class="woocommerce">
    <h1 style="font-family:'Playfair Display',serif;font-size:42px;font-weight:400;margin:24px 0 24px;color:#1a1a1a">Zamówienie</h1>
    <div style="display:grid;grid-template-columns:1fr 380px;gap:48px;align-items:flex-start">
      <div>
        <h3 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:400;margin:0 0 16px;color:#1a1a1a">Dane do wysyłki</h3>
        <form style="font-family:Rubik,sans-serif">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
            <input type="text" placeholder="Imię" style="font-family:Rubik,sans-serif;padding:12px 16px;border:1px solid #d4d4d4;border-radius:4px;font-size:14px">
            <input type="text" placeholder="Nazwisko" style="font-family:Rubik,sans-serif;padding:12px 16px;border:1px solid #d4d4d4;border-radius:4px;font-size:14px">
          </div>
          <input type="email" placeholder="E-mail" style="font-family:Rubik,sans-serif;padding:12px 16px;border:1px solid #d4d4d4;border-radius:4px;font-size:14px;width:100%;margin-bottom:16px">
          <input type="text" placeholder="Adres" style="font-family:Rubik,sans-serif;padding:12px 16px;border:1px solid #d4d4d4;border-radius:4px;font-size:14px;width:100%;margin-bottom:16px">
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px">
            <input type="text" placeholder="Kod pocztowy" style="font-family:Rubik,sans-serif;padding:12px 16px;border:1px solid #d4d4d4;border-radius:4px;font-size:14px">
            <input type="text" placeholder="Miasto" style="font-family:Rubik,sans-serif;padding:12px 16px;border:1px solid #d4d4d4;border-radius:4px;font-size:14px">
            <input type="text" placeholder="Telefon" style="font-family:Rubik,sans-serif;padding:12px 16px;border:1px solid #d4d4d4;border-radius:4px;font-size:14px">
          </div>
        </form>

        <h3 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:400;margin:32px 0 16px;color:#1a1a1a">Płatność</h3>
        <div style="background:#fafafa;border:1px solid #eee;border-radius:4px;padding:16px;font-family:Rubik,sans-serif;font-size:14px">
          <label style="display:flex;gap:8px;align-items:center;margin-bottom:8px"><input type="radio" name="payment" checked> Przelew tradycyjny</label>
          <label style="display:flex;gap:8px;align-items:center;margin-bottom:8px"><input type="radio" name="payment"> Przelewy24</label>
          <label style="display:flex;gap:8px;align-items:center"><input type="radio" name="payment"> Płatność przy odbiorze</label>
        </div>
        <button id="place_order" style="background:#1f0a0a;color:#fff;border:0;border-radius:4px;font-family:Rubik,sans-serif;font-weight:500;padding:16px 24px;font-size:15px;width:100%;margin-top:16px;cursor:pointer">Złóż zamówienie</button>
      </div>
      <aside style="background:#fafafa;border:1px solid #eee;border-radius:4px;padding:24px">
        <h3 style="font-family:'Playfair Display',serif;font-size:20px;font-weight:400;margin:0 0 16px;color:#1a1a1a">Twoje zamówienie</h3>
        <div style="display:flex;gap:12px;align-items:center;padding:12px 0;border-bottom:1px solid #eee">
          <div style="width:48px;height:48px;background:#e3342f;flex-shrink:0"></div>
          <div style="flex:1;font-family:Rubik,sans-serif;font-size:14px">
            <div style="color:#1a1a1a">Torba Zakupowa W Czerwoności</div>
            <div style="color:#666">× 1</div>
          </div>
          <div style="font-family:Rubik,sans-serif;font-weight:500">69,00 zł</div>
        </div>
        <table style="width:100%;border-collapse:collapse;font-family:Rubik,sans-serif;font-size:14px;margin-top:16px">
          <tr><td style="padding:8px 0;color:#666">Suma</td><td style="padding:8px 0;text-align:right">69,00 zł</td></tr>
          <tr class="order-total" style="font-size:18px;font-weight:500"><td style="padding:16px 0 0;border-top:1px solid #eee">Razem</td><td style="padding:16px 0 0;text-align:right;border-top:1px solid #eee">69,00 zł</td></tr>
        </table>
      </aside>
    </div>
  </div>
</div>
'''
(PREVIEW / "checkout.html").write_text(page("Checkout", "", CHECKOUT_BODY), encoding="utf-8")


print("✓ header.gutenberg.html")
print("✓ footer.gutenberg.html")
print("✓ css-dodatkowy.css")
print("✓ INSTRUKCJA.md")
print("✓ preview/ (index, header, footer, shop, product, cart, checkout)")
print(f"\nWszystko w: {OUT}")
print(f"\nAby zobaczyć preview, uruchom w terminalu:")
print(f"  python3 -m http.server 8765 --directory {OUT}/preview")
print(f"Otwórz: http://localhost:8765/")
