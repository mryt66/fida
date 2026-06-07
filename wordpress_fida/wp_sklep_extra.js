/* ============================================================
   FIDA SHOP – skrypt dodający toolbar nad siatką produktów
   Wklej przez: wtyczka "Insert Headers and Footers" → Footer
   Albo w Elementor: widget "HTML" → tryb "Zamknij <body>"
   ============================================================ */
(function(){
  function addFidaHeading(){
    var collection = document.querySelector('.wp-block-woocommerce-product-collection');
    if (!collection || document.querySelector('.fida-shop-heading')) return;
    var toolbar = document.createElement('div');
    toolbar.className = 'fida-shop-toolbar';
    toolbar.innerHTML = '<h3 class="fida-shop-heading">Wszystkie produkty</h3><p class="fida-shop-toolbar__count">7 produkty</p>';
    collection.insertBefore(toolbar, collection.firstChild);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addFidaHeading);
  } else {
    addFidaHeading();
  }
  window.addEventListener('load', addFidaHeading);
})();
