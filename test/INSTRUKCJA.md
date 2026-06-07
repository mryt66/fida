# Fida — Instrukcja wgrania (WordPress.com)

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
