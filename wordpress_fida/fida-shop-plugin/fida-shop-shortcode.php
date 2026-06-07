<?php
/**
 * ============================================================
 *  FIDA SHOP – dynamiczny shortcode [fida_shop]
 *  ----------------------------------------------------------
 *  Plik:        fida-shop-shortcode.php
 *  Data:        2026-06-07
 *  Wersja:      1.0.0
 *  WordPress:   6.0+
 *  WooCommerce: 8.0+
 *  PHP:         7.4+
 *
 *  ----------------------------------------------------------
 *  CEL
 *  ----------------------------------------------------------
 *  Renderuje siatkę produktów WooCommerce w identycznej
 *  strukturze HTML i tych samych klasach CSS co widget
 *  HTML Elementora w wordpress_fida/elementor_sklep_full.html.
 *
 *  Dzięki temu:
 *    - edycja ceny / tytułu / obrazka w wp-admin → Produkty
 *      natychmiast odzwierciedla się na stronie Sklep
 *    - dodanie / usunięcie produktu automatycznie aktualizuje
 *      liczbę w toolbarze i samą siatkę
 *    - ribbon "Nowość" pokazuje się tylko na produktach
 *      oznaczonych tagiem o slugu "nowosc"
 *    - cały istniejący CSS (w widgecie HTML) działa 1:1
 *    - przycisk "Dodaj do koszyka" działa z AJAX WC
 *      (simple) lub przekierowuje na stronę produktu
 *      (variable – koszulki z rozmiarem)
 *
 *  ----------------------------------------------------------
 *  UŻYCIE (Code Snippets – wybrany wariant)
 *  ----------------------------------------------------------
 *  1. Skopiuj CAŁOŚĆ pliku (poniżej komentarza
 *     "--- POCZĄTEK KODU ---").
 *  2. W WordPress: Code Snippets → Add New
 *  3. Tytuł:        "FIDA Shop Shortcode"
 *  4. Typ:          "Functions (PHP)"
 *  5. "Run snippet" → "Run everywhere" (lub "Only on frontend"
 *                    – oba warianty działają)
 *  6. Wklej kod → Save and Activate.
 *  7. W widgetcie HTML Elementora w miejscu siatki
 *     produktów wpisz:  [fida_shop]
 *
 *  ALTERNATYWNIE (bez Code Snippets):
 *  - cały plik wrzuć do wp-content/plugins/fida-shop-plugin/
 *    i dodaj na samej górze nagłówek pluginu (patrz niżej
 *    wariant "WARIANT B: jako plugin").
 *
 *  ----------------------------------------------------------
 *  PARAMETRY SHORTCODE
 *  ----------------------------------------------------------
 *    [fida_shop]                                         ← domyślne
 *    [fida_shop orderby="date" order="DESC"]
 *    [fida_shop per_page="-1" nowosc_tag="nowosc"]
 *    [fida_shop category="breloki"]                      ← filtr kat.
 *
 *    orderby    : 'date' | 'title' | 'price' | 'menu_order'
 *    order      : 'DESC' | 'ASC'
 *    per_page   : liczba produktów, -1 = wszystkie
 *    nowosc_tag : slug tagu dla ribbonu (domyślnie 'nowosc')
 *    category   : opcjonalny slug kategorii (filtrowanie)
 *
 *  ----------------------------------------------------------
 *  STRUKTURA PLIKU
 *  ----------------------------------------------------------
 *    1. Zabezpieczenia (ABSPATH, WC check)
 *    2. Helper polskiej odmiany "X produktów"
 *    3. Helper – render toolbara (sam licznik)
 *    4. Helper – render pojedynczej karty produktu
 *    5. Główny shortcode [fida_shop]  (renderuje TYLKO
 *       wrapper kolekcji + <ul> z kartami – BEZ toolbara,
 *       bo toolbar jest w widgecie HTML Elementora)
 *    6. Rejestracja shortcode'ów
 *
 *  ----------------------------------------------------------
 *  KONTRAKT SHORTCODE'ÓW (dla widgetu HTML)
 *  ----------------------------------------------------------
 *  [fida_shop_count]  →  <p class="fida-shop-count">7 produktów</p>
 *  [fida_shop]         →  <div data-wp-interactive="…">
 *                            <ul class="wc-block-product-template">
 *                              <li>…</li> × N
 *                            </ul>
 *                         </div>
 *  Toolbar (.fida-shop-toolbar z h3) pozostaje statyczny
 *  w widgecie HTML. Shortcode NIE renderuje toolbara –
 *  wstawiaj go w HTML ręcznie obok [fida_shop_count].
 * ============================================================
 *
 *  WARIANT B: jako plugin (opcjonalny nagłówek, gdybyś
 *  w przyszłości wolał wtytynkę zamiast Code Snippets):
 *
 *    /*
 *     Plugin Name:       FIDA Shop Shortcode
 *     Description:       Shortcode [fida_shop] – dynamiczna
 *                        siatka produktów WC dla sklepu FIDA.
 *     Version:           1.0.0
 *     Requires at least: 6.0
 *     Requires PHP:      7.4
 *     WC requires at least: 8.0
 *     Author:            FIDA
 *     License:           GPL-2.0-or-later
 *     Text Domain:       fida-shop
 *     *\/
 *
 * ============================================================
 *  --- POCZĄTEK KODU ( kopiuj od tej linii w dół ) ---
 * ============================================================
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

if ( ! function_exists( 'wc_get_products' ) ) {
    add_action( 'admin_notices', function() {
        echo '<div class="notice notice-error"><p><strong>FIDA Shop Shortcode:</strong> wymaga aktywnego WooCommerce.</p></div>';
    });
    return;
}


/* ==========================================================
 * 2. POLSKA ODMIANA "X PRODUKTÓW"
 * ========================================================== */

function fida_polish_count( $count, $word = 'produkt' ) {
    if ( 1 === $count ) {
        return '1 ' . $word;
    }
    $mod10 = $count % 10;
    $mod100 = $count % 100;
    if ( $mod10 >= 2 && $mod10 <= 4 && ( $mod100 < 12 || $mod100 > 14 ) ) {
        return $count . ' ' . $word . 'y';
    }
    return $count . ' ' . $word . 'ów';
}


/* ==========================================================
 * 3. HELPER – TOOLBAR (sam <p> z licznikiem)
 * ========================================================== */

function fida_render_toolbar_count( $count ) {
    return '<p class="fida-shop-count">' . esc_html( fida_polish_count( $count ) ) . '</p>';
}


/* ==========================================================
 * 4. HELPER – RENDER POJEDYNCZEJ KARTY PRODUKTU
 * ========================================================== */

function fida_render_product_card( $product, $index, $nowosc_tag_slug ) {

    $pid        = $product->get_id();
    $permalink  = get_permalink( $pid );
    $title      = $product->get_name();
    $sku        = $product->get_sku();
    $is_variable = $product->is_type( 'variable' );
    $is_simple  = $product->is_type( 'simple' );

    $img_id     = $product->get_image_id();
    $img_html   = $img_id
        ? wp_get_attachment_image( $img_id, 'woocommerce_thumbnail', false, array(
            'loading'  => 'lazy',
            'decoding' => 'async',
            'class'    => 'attachment-woocommerce_thumbnail size-woocommerce_thumbnail',
            'alt'      => esc_attr( $title ),
        ) )
        : wc_placeholder_img( 'woocommerce_thumbnail' );

    if ( $img_html ) {
        $img_html = str_replace( '<img ', '<img data-testid="product-image" data-image-id="' . esc_attr( $img_id ) . '" style="object-fit:cover;" ', $img_html );
    }

    $price_html = $product->get_price_html();

    $has_nowosc = has_term( $nowosc_tag_slug, 'product_tag', $pid );

    $position_class = '';
    if ( 0 === $index % 4 ) {
        $position_class = ' first';
    }
    if ( 3 === $index % 4 || ( $index === ($GLOBALS['fida_shop_total'] - 1) ) ) {
        $position_class .= ' last';
    }

    $tag_slugs = wp_list_pluck( wp_get_post_terms( $pid, 'product_tag' ), 'slug' );
    $cat_slugs = wp_list_pluck( wp_get_post_terms( $pid, 'product_cat'  ), 'slug' );

    $tax_classes = '';
    foreach ( $cat_slugs as $slug ) {
        $tax_classes .= ' product_cat-' . sanitize_html_class( $slug );
    }
    foreach ( $tag_slugs as $slug ) {
        $tax_classes .= ' product_tag-' . sanitize_html_class( $slug );
    }

    $stock_status = $product->get_stock_status();
    $stock_class  = ' outofstock' === $stock_status ? ' outofstock' : ' instock';
    $purchasable  = $product->is_purchasable() ? ' purchasable' : ' not-purchasable';
    $ship         = $product->needs_shipping() ? ' shipping-taxable' : '';
    $has_thumb    = $img_id ? ' has-post-thumbnail' : '';

    $li_classes = sprintf(
        'wc-block-product post-%1$d product type-product status-publish%2$s%3$s%4$s%5$s%6$s%7$s%8$s%9$s product-type-%10$s',
        $pid,
        $has_thumb,
        $tax_classes,
        $position_class,
        $stock_class,
        $purchasable,
        $ship,
        $has_nowosc ? ' fida-has-nowosc' : '',
        $is_variable ? ' variable' : '',
        $is_variable ? 'variable' : 'simple'
    );

    $li_classes = trim( preg_replace( '/\s+/', ' ', $li_classes ) );

    $data_context_json = wp_json_encode( array(
        'quantityToAdd'   => 1,
        'addToCartText'   => 'Dodaj do koszyka',
        'tempQuantity'    => 0,
        'animationStatus' => 'IDLE',
        'inTheCartText'   => '### w koszyku',
        'noticeId'        => '',
        'hasPressedButton' => false,
    ) );

    if ( $is_variable ) {
        $button_html = sprintf(
            '<div data-block-name="woocommerce/product-button" data-font-size="small" data-text-align="center" class="wp-block-button wc-block-components-product-button align-center wp-block-woocommerce-product-button has-small-font-size"%s>' .
                '<a class="wp-block-button__link wp-element-button wc-block-components-product-button__button add_to_cart_button product_type_variable has-font-size has-small-font-size has-text-align-center wc-interactive" href="%s" rel="nofollow" data-product_id="%d" data-product_sku="%s" aria-label="%s"><span>Dodaj do koszyka</span></a>' .
            '</div>',
            ' data-wp-context="' . esc_attr( $data_context_json ) . '"',
            esc_url( $permalink ),
            $pid,
            esc_attr( $sku ),
            esc_attr( 'Dodaj do koszyka: „' . $title . '”' )
        );
    } else {
        $button_html = sprintf(
            '<div data-block-name="woocommerce/product-button" data-font-size="small" data-text-align="center" class="wp-block-button wc-block-components-product-button align-center wp-block-woocommerce-product-button has-small-font-size" data-wp-interactive="woocommerce/product-button"%s>' .
                '<button class="wp-block-button__link wp-element-button wc-block-components-product-button__button add_to_cart_button ajax_add_to_cart product_type_simple has-font-size has-small-font-size has-text-align-center wc-interactive" type="button" data-product_id="%d" data-product_sku="%s" aria-label="%s" data-wp-on--click="actions.addCartItem"><span data-wp-text="state.addToCartText">Dodaj do koszyka</span></button>' .
                '<span hidden data-wp-bind--hidden="!state.displayViewCart"><a href="%s" class="added_to_cart wc_forward" title="Zobacz koszyk">Zobacz koszyk</a></span>' .
            '</div>',
            ' data-wp-context="' . esc_attr( $data_context_json ) . '"',
            $pid,
            esc_attr( $sku ),
            esc_attr( 'Dodaj do koszyka: „' . $title . '”' ),
            esc_url( wc_get_cart_url() )
        );
    }

    return sprintf(
        '<li class="%1$s" data-wp-interactive="woocommerce/product-collection" data-wp-key="product-item-%2$d">' .
            '<div data-block-name="woocommerce/product-image" data-show-sale-badge="false" class="wc-block-components-product-image wc-block-grid__product-image wc-block-components-product-image--aspect-ratio-auto wp-block-woocommerce-product-image">' .
                '<a href="%3$s">%4$s</a>' .
            '</div>' .
            '<h2 style="line-height:1.4;margin-bottom:0.75rem;margin-top:0" class="wp-block-post-title has-medium-font-size">' .
                '<a href="%3$s" target="_self">%5$s</a>' .
            '</h2>' .
            '<div data-block-name="woocommerce/product-price" data-font-size="small" data-text-align="center" class="has-font-size has-small-font-size has-text-align-center wp-block-woocommerce-product-price">' .
                '<div class="wc-block-components-product-price wc-block-grid__product-price">%6$s</div>' .
            '</div>' .
            '%7$s' .
        '</li>',
        esc_attr( $li_classes ),
        $pid,
        esc_url( $permalink ),
        $img_html,
        esc_html( $title ),
        $price_html,
        $button_html
    );
}


/* ==========================================================
 * 5. GŁÓWNY SHORTCODE [fida_shop]
 * ========================================================== */

function fida_shop_shortcode( $atts ) {

    $atts = shortcode_atts( array(
        'orderby'    => 'date',
        'order'      => 'DESC',
        'per_page'   => -1,
        'nowosc_tag' => 'nowosc',
        'category'   => '',
    ), $atts, 'fida_shop' );

    $orderby = sanitize_key( $atts['orderby'] );
    $order   = ( 'ASC' === strtoupper( $atts['order'] ) ) ? 'ASC' : 'DESC';
    $per_page = (int) $atts['per_page'];
    $nowosc  = sanitize_title( $atts['nowosc_tag'] );
    $cat     = sanitize_title( $atts['category'] );

    $allowed_orderby = array( 'date', 'title', 'price', 'menu_order', 'popularity', 'rating', 'id', 'rand' );
    if ( ! in_array( $orderby, $allowed_orderby, true ) ) {
        $orderby = 'date';
    }

    $query_args = array(
        'status'   => 'publish',
        'limit'    => $per_page,
        'orderby'  => $orderby,
        'order'    => $order,
        'return'   => 'objects',
    );

    if ( '' !== $cat ) {
        $query_args['category'] = array( $cat );
    }

    $products = wc_get_products( $query_args );

    if ( empty( $products ) ) {
        return '<p class="fida-shop-count">Brak produktów.</p>';
    }

    $GLOBALS['fida_shop_total'] = count( $products );

    $items_html = '';
    $i = 0;
    foreach ( $products as $product ) {
        $items_html .= fida_render_product_card( $product, $i, $nowosc );
        $i++;
    }

    unset( $GLOBALS['fida_shop_total'] );

    return sprintf(
        '<div data-wp-interactive="woocommerce/product-collection" data-wp-router-region="wc-product-collection-40" data-block-name="woocommerce/product-collection" data-display-layout="{&quot;type&quot;:&quot;flex&quot;,&quot;columns&quot;:4,&quot;shrinkColumns&quot;:true}" data-query-id="40" data-tag-name="div" class="wp-block-woocommerce-product-collection is-layout-flow wp-block-woocommerce-product-collection-is-layout-flow">' .
            '<ul data-block-name="woocommerce/product-template" class="wc-block-product-template__responsive columns-4 wc-block-product-template wp-block-woocommerce-product-template is-layout-flow wp-block-woocommerce-product-template-is-layout-flow" data-wp-on--scroll="actions.watchScroll">%1$s</ul>' .
        '</div>',
        $items_html
    );
}


/* ==========================================================
 * 6. REJESTRACJA SHORTCODÓW
 * ========================================================== */

add_shortcode( 'fida_shop',      'fida_shop_shortcode' );
add_shortcode( 'fida_shop_count', function() {
    $count = count( wc_get_products( array( 'status' => 'publish', 'return' => 'ids', 'limit' => -1 ) ) );
    return fida_render_toolbar_count( $count );
});
