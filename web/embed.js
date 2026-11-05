/*! Koltuk görünümü — gömme betiği v0.2 (Hyperbaric)
 * Bilet sitesine iframe ile "koltuğundan sahayı gör" görüntüleyicisini ekler.
 *
 *   <div id="koltuk"></div>
 *   <script src="embed.js"></script>
 *   <script>
 *     const v = KoltukViewer.mount(document.getElementById('koltuk'), {
 *       venue: 'arena3d',                 // örnek mekân kimliği (viewer.html VENUE_OPTIONS)
 *       brand: 'biletra',                 // hazır marka kimliği ya da {primary, accent, logoText, ...}
 *       onSeatSelect: seat => sepeteEkle(seat)   // "Bu koltuğu seç" tıklandığında
 *     });
 *     v.selectVenue('tiyatro'); v.selectSeat('PS-A-1'); v.destroy();
 *   </script>
 *
 * Güvenlik:
 *  - Görüntüleyiciden gelen mesajlar yalnızca (a) bu iframe'in penceresinden, (b) izinli origin'den
 *    ve (c) mount sırasında üretilen kanal kimliğiyle gelirse işlenir.
 *  - Görüntüleyiciye giden mesajlar yalnız görüntüleyicinin origin'ine gönderilir.
 *  - İki sayfa da sandbox'lı (opak, "null" origin) bir çerçevede çalışıyorsa origin karşılaştırılamaz;
 *    bu durumda pencere + kanal kimliği eşleşmesi zorunludur ve hedef '*' olur. Mesajlarda kişisel veri yoktur.
 */
(function (global) {
  'use strict';
  var VERSION = '0.2.0';
  var PROTOCOL = 'koltuk:';

  function scriptBase() {
    var s = document.currentScript;
    try { return s && s.src ? new URL('.', s.src).href : document.baseURI; } catch (e) { return document.baseURI; }
  }
  var BASE = scriptBase();

  function randomId() {
    var a = new Uint8Array(12);
    (global.crypto || global.msCrypto).getRandomValues(a);
    return Array.prototype.map.call(a, function (b) { return ('0' + b.toString(36)).slice(-2); }).join('').slice(0, 20);
  }

  function mount(el, opts) {
    if (!el || el.nodeType !== 1) throw new Error('KoltukViewer.mount: geçerli bir öğe verin');
    opts = opts || {};
    var channel = randomId();
    var src = new URL(opts.src || 'viewer.html', BASE);
    var q = src.searchParams;
    q.set('embed', '1');
    if (typeof opts.venue === 'string') q.set('venue', opts.venue);
    if (typeof opts.brand === 'string') q.set('brand', opts.brand);
    if (opts.lang) q.set('lang', opts.lang);
    if (opts.theme) q.set('theme', opts.theme);
    src.hash = 'ch=' + channel;

    var opaque = global.location.origin === 'null';
    var viewerOrigin = src.origin;
    var allowed = (opts.allowedOrigins || [viewerOrigin]).filter(function (o) { return o && o !== 'null'; });
    var targetOrigin = opaque ? '*' : viewerOrigin;

    var iframe = document.createElement('iframe');
    iframe.src = src.href;
    iframe.title = opts.title || 'Koltuktan görünüm';
    iframe.setAttribute('allow', 'fullscreen');
    iframe.setAttribute('loading', 'eager');
    iframe.style.cssText = 'display:block;width:100%;height:100%;border:0;background:transparent;color-scheme:normal';
    el.appendChild(iframe);

    var ready = false, queue = [], destroyed = false;

    function send(msg) {
      msg.channel = channel;
      if (!ready) { queue.push(msg); return; }
      try { iframe.contentWindow.postMessage(msg, targetOrigin); } catch (e) { /* çerçeve kapandı */ }
    }

    function onMessage(e) {
      if (destroyed || e.source !== iframe.contentWindow) return;
      var m = e.data;
      if (!m || typeof m !== 'object' || typeof m.type !== 'string' || m.type.indexOf(PROTOCOL) !== 0) return;
      if (m.channel !== channel) return;
      if (!(allowed.indexOf(e.origin) >= 0 || (opaque && e.origin === 'null'))) return;
      if (typeof opts.onMessage === 'function') opts.onMessage(m);
      switch (m.type) {
        case 'koltuk:ready':
          ready = true;
          if (opts.brand && typeof opts.brand === 'object') queue.unshift({ type: 'koltuk:setBrand', brand: opts.brand, channel: channel });
          if (opts.venue && typeof opts.venue === 'object') queue.unshift({ type: 'koltuk:loadVenue', venue: opts.venue, channel: channel });
          var q2 = queue; queue = [];
          q2.forEach(send);
          if (typeof opts.onReady === 'function') opts.onReady(m);
          break;
        case 'koltuk:seatSelected':
          if (typeof opts.onSeatSelect === 'function') opts.onSeatSelect(m.seat);
          break;
        case 'koltuk:venueLoaded':
          if (typeof opts.onVenueLoaded === 'function') opts.onVenueLoaded(m);
          break;
        case 'koltuk:event':
          if (typeof opts.onEvent === 'function') opts.onEvent(m.event);
          break;
        case 'koltuk:resize':
          // Dar ekranda (varsayılan < 860 px) kapsayıcıyı içerik yüksekliğine getir; geniş ekranda sabit yükseklik korunur.
          var h = +m.height;
          if (opts.autoHeight !== false && h > 0 && h < 20000) {
            el.style.height = global.innerWidth < (opts.autoHeightBelow || 860) ? h + 'px' : '';
          }
          break;
      }
    }
    global.addEventListener('message', onMessage);

    return {
      iframe: iframe,
      channel: channel,
      selectVenue: function (id) { send({ type: 'koltuk:selectVenue', venueId: String(id) }); },
      loadVenue: function (obj) { send({ type: 'koltuk:loadVenue', venue: obj }); },
      selectSection: function (id) { send({ type: 'koltuk:selectSection', sectionId: String(id) }); },
      selectSeat: function (code) { send({ type: 'koltuk:selectSeat', ticketCode: String(code) }); },
      overview: function () { send({ type: 'koltuk:overview' }); },
      setBrand: function (b) { send({ type: 'koltuk:setBrand', brand: b }); },
      setLang: function (l) { send({ type: 'koltuk:setLang', lang: l }); },
      setTheme: function (t) { send({ type: 'koltuk:setTheme', theme: t }); },
      destroy: function () { destroyed = true; global.removeEventListener('message', onMessage); if (iframe.parentNode) iframe.parentNode.removeChild(iframe); }
    };
  }

  global.KoltukViewer = { mount: mount, version: VERSION };
})(window);
