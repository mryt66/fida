# Fida — Style Guide

Źródło: oryginalny design Zyro/Hostinger, przeniesiony 1:1 do WordPress.com + WooCommerce.

## Kolory

| Token         | HEX       | Użycie                                                |
|---------------|-----------|-------------------------------------------------------|
| `fida-red`    | `#1f0a0a` | Nagłówek, stopka, tło ciemnych sekcji                 |
| `fida-accent` | `#e3342f` | CTA, hover, aktywne linki, badge "Nowość", count cart |
| `fida-text`   | `#1a1a1a` | Tekst główny, nagłówki kart                            |
| `fida-muted`  | `#666`    | Opisy, meta, breadcrumbs                                |
| `fida-border` | `#e0e0e0` | Obramowania inputów, divider kart                      |
| `fida-bg`     | `#fff`    | Tło strony                                             |
| `fida-border-soft` | `#eee` | Linie w tabelach, delikatne separatory             |
| `fida-footer-text` | `#888` | Copyright w stopce                                |
| `fida-footer-link` | `#ccc` | Linki w stopce                                   |
| `fida-divider-dark` | `#3a1414` | Linia nad copyright w stopce                     |

## Typografia

- **Body:** Rubik, fallback `sans-serif`
- **Headings (H1–H4):** Playfair Display, fallback `serif`, waga 400
- **Rozmiary:**
  - H1: 42px (główny tytuł strony / nazwa produktu)
  - H2: 28px (sekcje typu "Może Cię zainteresuje")
  - H3: 20px (nazwa karty produktu)
  - H4: 18px (nagłówki w stopce)
  - Body: 16px
  - Small/meta: 13–14px

## Spacing

- Sekcje: `80px` górny margines
- Karty produktów: padding `20px`, gap `24px`
- Header: padding `18px 60px`
- Footer: padding `48px 60px 24px`

## Layout

- Max content width: `1280px`, centrowany
- Grid kart: 4 kolumny desktop, 2 tablet, 1 mobile
- Sidebar sklepu: `240px` stała szerokość
- Karta produktu: image 1:1, badge "Nowość" lewy górny, hover shadow `0 4px 12px rgba(0,0,0,.08)`

## Komponenty

### Header (`/wordpress_fida/header.html`)
- Sticky `top:0`, `z-index:100`
- Logo: wysokość 50px, `filter:brightness(0) invert(1)` (odwraca ciemne logo na białe)
- Nav: gap 32px, font-size 14px, aktywna strona ma `text-decoration:underline; text-underline-offset:6px`
- Social: SVG icons 18×18, gap 16px
- Cart: SVG, z czerwonym badge count (ukryty gdy 0)

### Footer (`/wordpress_fida/footer.html`)
- 4 kolumny grid (`auto-fit, minmax(180px, 1fr)`)
- Headings Playfair Display
- Linki `#ccc` na `#1f0a0a`
- Bottom: separator + copyright `#888`

### Karta produktu
```css
border: 1px solid #e0e0e0;
border-radius: 4px;
background: #fff;
padding: 0;
transition: box-shadow .2s;
```
Hover: `box-shadow: 0 4px 12px rgba(0,0,0,.08);`

### Przycisk "Dodaj do koszyka"
- Background `#1f0a0a`, color `#fff`
- Padding `12px 24px`, font-weight 500
- Hover: `#e3342f`
- Border-radius 4px

### Badge "Nowość"
- Position absolute, top 12px, left 12px
- Background `#e3342f`, color `#fff`
- Padding `4px 10px`, font-size 12px, font-weight 500
- Border-radius 3px

### Breadcrumb
- Font-size 13px, color `#666`
- Separator `/`
- Aktywna pozycja: `#1a1a1a`, font-weight 500

## WooCommerce overrides (Dodatkowy CSS w Customizer)

```css
/* Przycisk CTA */
.woocommerce a.button,
.woocommerce button.button,
.woocommerce input.button,
.wc-block-components-button {
  background-color: #1f0a0a !important;
  color: #fff !important;
  border-radius: 4px !important;
  font-family: 'Rubik', sans-serif !important;
  font-weight: 500 !important;
  padding: 12px 24px !important;
}
.woocommerce a.button:hover,
.woocommerce button.button:hover {
  background-color: #e3342f !important;
}

/* Cena */
.woocommerce div.product p.price,
.woocommerce ul.products li.product .price {
  color: #1a1a1a !important;
  font-weight: 500 !important;
  font-size: 18px !important;
}

/* Karty produktów */
.woocommerce ul.products li.product,
.wc-block-grid__product {
  border: 1px solid #e0e0e0 !important;
  border-radius: 4px !important;
  background: #fff !important;
  padding: 0 !important;
  transition: box-shadow .2s !important;
  overflow: hidden !important;
}
.woocommerce ul.products li.product:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,.08) !important;
}

/* Tytuły produktów */
.woocommerce ul.products li.product .woocommerce-loop-product__title,
.wc-block-grid__product-title {
  font-family: 'Playfair Display', serif !important;
  font-size: 20px !important;
  font-weight: 400 !important;
  color: #1a1a1a !important;
  padding: 12px 16px 4px !important;
}

/* Badge "Nowość" — wtyczka lub shortcode, lub dodatkowa klasa `fida-nowosc` */
```

## URL mapowanie

| Stary (Zyro)              | Nowy (WordPress)                           |
|---------------------------|--------------------------------------------|
| `sklep.html`              | `/sklep/`                                  |
| `produkt-{slug}.html`     | `/produkt/{slug}/`                         |
| `kategoria/{slug}.html`   | `/produkt-kategoria/{breloki\|torby\|koszulki}/` |
| `koszyk.html`             | `/koszyk/`                                 |
| `checkout.html`           | `/zamowienie/`                             |
| `polityka-prywatnosci.html` | `/polityka-prywatnosci/`                 |
| `polityka-zwrotow.html`   | `/polityka-zwrotow/`                       |
| `regulamin.html`          | `/regulamin-sklepu/`                       |
