# Koltuk Görünümü: web görüntüleyici, teknik not (demo v0.2)

> v0.2 değişiklikleri, yayın düzeni ve test sonuçları için önce **§9**'a bakın. §1–8 v0.1 notlarıdır; v0.2 ile geçersizleşen maddeler §9.6'da listelenir.

`demo.html`, satış demosu olarak hazırlanmış tek dosyalık bir görüntüleyici. Kurgusal "Örnek Arena"yı (11.270 koltuk, 28 blok, 2 kat) kodla üretir ve bu veriyi ortak `venue.json` şemasına (v0.1, bkz. `../shared/venue-schema.md`) uygun bir nesne olarak oluşturur. Görüntüleyici yalnızca bu nesne üzerinden çalışır.

## 1. Mimari

```
venue.json (nesne) ──► loadVenue(obj) ──► doğrulama + indeks (S.seats, S.sections, byCode)
                                           │
              ┌────────────────────────────┼─────────────────────────────┐
              ▼                            ▼                             ▼
     2D SVG blok haritası        3D çekirdek (GL)                 UI panelleri
     (koltuk eye'larından        - CameraRig: genel bakış         blok kartı, sıra/koltuk,
      poligon üretir)              (orbit) / koltuk (yaw-pitch)   koltuk çubuğu, CTA
                                 - flyTo geçişleri (reduced-motion)
                                 - SceneAdapter ◄── ProceduralScene (bugün)
                                                 ◄── SplatScene (stub)
                                        │
                               TicketAPI (mock): fiyat + müsaitlik
                               track(): analitik olay günlüğü → CustomEvent + postMessage
```

| Katman | Sorumluluk | Dosyadaki bölüm |
|---|---|---|
| `BRAND` | Beyaz etiket: ad, ana renk, vurgu rengi, logo metni, "altyapı" ibaresi | §1 |
| `I18N`, `CATS` | TR (varsayılan) / EN metinler, fiyat kategorisi adları | §2 |
| `generateDemoVenue()` | Şemaya uygun demo verisi (yalnız demo) | §3 |
| `SceneAdapter` | Sahne soyutlaması: `build`, `setTheme`, `setBrand`, `paintSeats`, `setSeatMarker`, `pick`, `dispose` | §4 |
| `ProceduralScene` | Kase basamakları, çatı, LED bant, saha dokusu, potalar, skorbord; koltuklar tek `InstancedMesh` | §4 |
| `SplatScene` | Stub; entegrasyon notları yorumda | §4 |
| `track()` | Olayları bellekte tutar, `koltuk:analytics` olayını yayar, iframe'de üst pencereye `postMessage` gönderir | §5 |
| `loadVenue()` | Doğrular, indeksler, sahneyi yeniden kurar | §6 |
| `GL` | Renderer, kamera, giriş (fare, dokunma, sıkıştırma, tekerlek, klavye), isteğe bağlı çizim | §7 |

Performans kararları:
- Koltuklar tek `InstancedMesh` (24 üçgenlik sandalye × 11.270 adet), yani tek çizim çağrısı. Renk değişimi `setColorAt` ile yapılır.
- Kase tek bir `BufferGeometry` (vertex color ile sıra sıra iki ton), `MeshLambertMaterial` kullanır. Gölge ve post-processing yok.
- Sahne yalnızca bir şey değiştiğinde çizilir (`dirty` bayrağı); boşta GPU yükü yok. Piksel oranı en fazla 1,75.
- Çatı ve dış duvar tek yüzlü. Genel bakışta kamera çatının üstünde kalınca bunlar görünmez ve kesit etkisi oluşur. Çatı makasları da kameranın yüksekliğine göre gizlenir.
- Dokunma ile seçim: ışın önce koltuğa, sonra basamağa çarpar; basamağa çarparsa en yakın koltuk seçilir. Böylece telefonda büyük bir dokunma hedefi elde edilir.

## 2. venue.json nasıl tüketiliyor

| Alan | Kullanım |
|---|---|
| `schemaVersion` | Zorunlu. İleride sürüm kontrolüne bağlanacak. |
| `venue.focus` | Varsayılan bakış hedefi (`seat.lookAt` ve `section.focus` yoksa). |
| `venue.type` | `arena` ise haritaya saha dikdörtgeni çizilir. |
| `venue.scene.kind` | Adaptörü seçer: `procedural` → ProceduralScene, `splat` → SplatScene (şimdilik ProceduralScene'e düşer ve konsola uyarı yazar). |
| `venue.scene.transform` | Sahne kökünün konumu, Y dönüşü ve ölçeği. |
| `venue.scene.params` | **Demo uzantısı (şemada yok):** prosedürel kabuk parametreleri (çekirdek dikdörtgen, katlar, çatı). Yoksa yalnızca koltuklar çizilir. Şemaya `scene.params` olarak eklenmesini öneriyoruz. |
| `sections[].id / tier / priceCategory` | Harita etiketi, kat adı, renk ve fiyat eşlemesi. |
| `sections[].rows[].seats[].eye` | Kameranın koltuk görünümündeki konumu, birebir. 3D sandalye `eye.y − 1,15 − 0,45` tabanına oturtulur ve bakış hedefine döndürülür. Harita poligonu, bloğun ilk ve son sırasındaki `eye`'lardan çıkarılır. |
| `seats[].lookAt` → `section.focus` → `venue.focus` | Koltuk görünümünün başlangıç yönü. |
| `seats[].ticketCode` | Tüm API, analitik ve `postMessage` çağrılarında kimlik olarak kullanılır. Yoksa `blok-sıra-koltuk` biçiminde üretilir. |
| `viewpoints[]` | Demo bu alanı üretiyor ama henüz kullanmıyor. Splat ve 360 aşamasında koltuk görünümünü en yakın çekim noktasıyla zenginleştirmek için kullanılacak (bkz. §4). |

Doğrulama hatalı veriyi (eksik `focus`, boş `sections`, `eye` uzunluğu ≠ 3) reddeder. Bu durumda bildirim gösterilir, `false` döner ve mevcut sahne korunur.

## 3. Müşteri sitesine gömme

### a) iframe (önerilen ilk yol: izolasyon, CSP dostu)
```html
<iframe src="https://view.hyperbaric.app/e/{eventId}?brand={brandId}&lang=tr"
        title="Koltuktan görünüm" allow="fullscreen"
        style="width:100%;height:640px;border:0;border-radius:12px"></iframe>
<script>
  const f = document.querySelector('iframe');
  // Bilet ekranındaki seçimi görüntüleyiciye ilet
  function showSeat(ticketCode){ f.contentWindow.postMessage({type:'koltuk:selectSeat', ticketCode}, 'https://view.hyperbaric.app'); }
  // Görüntüleyiciden olay al (CTA → kendi sepetinize ekleyin)
  window.addEventListener('message', e => {
    if (e.origin !== 'https://view.hyperbaric.app') return;
    if (e.data?.type === 'koltuk:event' && e.data.event.name === 'cta_click') addToBasket(e.data.event.ticket_code);
  });
</script>
```
Gelen komutlar: `koltuk:selectSeat {ticketCode}`, `koltuk:selectSection {sectionId}`, `koltuk:overview`, `koltuk:setBrand {brand}`, `koltuk:loadVenue {venue}`. Giden mesaj: `koltuk:event {event}`. Üretimde `postMessage` hedefi `'*'` yerine müşteri origin'ine (izin listesi) sabitlenmeli.

**v0.2:** bu elle yazılmış örneğin yerini `embed.js` aldı (kanal kimliği, origin izin listesi, `koltuk:seatSelected`). Protokol §9.3'te.

### b) Script snippet (aynı DOM, daha sıkı entegrasyon)
```html
<div id="koltuk-view" style="height:600px"></div>
<script src="https://cdn.hyperbaric.app/koltuk/1.0.0/viewer.min.js" defer></script>
<script>
  window.addEventListener('DOMContentLoaded', async () => {
    const viewer = await KoltukViewer.mount('#koltuk-view', {
      venueUrl: '/venues/ornek-arena/venue.json',
      brand: { name:'Biletra', primary:'#0B6E4F', accent:'#C6F432', logoText:'BİLETRA' },
      lang: 'tr',
      api: { availability: (sectionId) => fetch(`/api/events/123/availability?section=${sectionId}`).then(r=>r.json()) },
      onEvent: (ev) => window.dataLayer?.push({ event: 'koltuk_' + ev.name, ...ev })
    });
    viewer.selectSeat('A1-1-1');
  });
</script>
```
Demo bugün `window.KoltukViewer` üzerinden `loadVenue`, `selectSection`, `selectSeat`, `overview`, `setBrand`, `setLang`, `setTheme`, `getEvents` ve `getState` sunuyor. `mount()` biçimli kütüphane paketi iş planında yer alıyor. CSS bugün `:root`'ta. Script modunda Shadow DOM ve kapsamlı token'lara (`.koltuk-root`) taşınacak.

## 4. Splat sahnesi entegrasyonu: yol haritası

1. **Biçim:** 3D ekibiyle `.spz` veya sıkıştırılmış `.ply` üzerinde anlaşmak. Hedef boyut mekân başına ≤ 30 MB (mobil), LOD'lu sürüm masaüstü için.
2. **Hizalama:** `venue.scene.transform` splat'i mekân koordinatına (metre, Y yukarı, orijin saha merkezi) oturtur. Doğrulama için koltuk `eye`'ları ve viewpoint'ler splat üzerine nokta olarak bindirilip ekran görüntüsüyle karşılaştırılır.
3. **SplatScene.build:** three.js uyumlu bir Gaussian splat renderer'ı aynı `THREE.Scene`'e eklemek. Koltuklar görünmez çarpışma `InstancedMesh`'i olarak kalır, böylece `pick()`, işaretçi ve kamera değişmez. `paintSeats()` yalnızca haritayı ve isteğe bağlı yarı saydam koltuk vurgularını boyar.
4. **Akış:** önce düşük çözünürlüklü önizleme, sonra tam splat (aşamalı yükleme). Bu sırada ProceduralScene "yer tutucu" olarak görünür.
5. **360 çekimler:** `viewpoints[].capture` (equirect-360) varsa koltuk görünümü en yakın çekime karışım (cross-fade) ile geçer. Arada kalan koltuklarda splat kullanılır.
6. **Kalite kapısı:** mobilde (orta segment Android) ≥ 30 fps ve ilk görüntü ≤ 3 sn. Altında kalınırsa ProceduralScene + 360 görsele düşülür.

## 5. Bilet API entegrasyonu (müsaitlik ve fiyat)

Demo `TicketAPI` mock'unu kullanıyor: sabit kategori fiyatları ve `ticketCode` hash'iyle belirlenen "satıldı" durumu. Üretim için adaptör arayüzü:

```ts
interface TicketProvider {
  getPrices(eventId): Promise<Record<PriceCategory, {amount:number, currency:'TRY'}>>;
  getAvailability(eventId, sectionId?): Promise<{ ticketCode:string, status:'available'|'sold'|'held' }[]>;
  hold?(eventId, ticketCode): Promise<{ holdId, expiresAt }>;   // opsiyonel: CTA'da koltuğu tut
}
```
- Eşleşme anahtarı `ticketCode`. CSV (`section,row,seat,ticketCode`) içeri alınırken eşleşmeyen kayıtlar raporlanır.
- Müsaitlik blok açıldığında çekilir, 30–60 sn TTL ile önbelleğe alınır. Seçili blok için SSE veya polling ile tazelenir.
- Fiyat görüntüleyicide yalnızca gösterim içindir. Satış fiyatı her zaman müşterinin sepet akışında hesaplanır.
- CTA, satın almayı görüntüleyicide yapmaz: `cta_click` olayı ve `postMessage` ile host'un sepete ekleme fonksiyonu tetiklenir.

## 6. Analitik olayları

Ortak alanlar: `name, ts (ISO), session_id, venue_id, brand_id`.

| Olay | Ne zaman | Ek alanlar |
|---|---|---|
| `section_view` | Blok haritadan, 3D'den, API'den veya host'tan açıldığında (ilk yükleme sayılmaz) | `section_id, price_category, source` |
| `seat_view` | Koltuk görünümü açıldığında | `ticket_code, section_id, row, seat, price_category, available, source` |
| `view_duration` | Koltuk görünümünden çıkıldığında (başka koltuk, genel bakış, sekme gizlendi); 250 ms altı atılır | `ticket_code, section_id, ms` |
| `cta_click` | "Bu koltuğu seç" tıklandığında | `ticket_code, section_id, row, seat, price_category, price, currency` |

`source` değerleri: `map | 3d | section_card | seatbar | picker | nav | api | host`.
Üretimde olaylar toplu halde (`navigator.sendBeacon`) bir olay toplayıcıya gönderilecek. Müşteriye `onEvent` ve `postMessage` ile kendi analitiğine (GA4, Segment) aktarma imkânı sunulacak. Kişisel veri toplanmaz; `session_id` rastgele ve oturumluktur. KVKK metni müşterinin çerez politikasına eklenecek.

"Ne ölçüyoruz?" paneli bu olaylardan şu KPI'ları türetir: blok görüntüleme, koltuk görüntüleme, ortalama bakış süresi, görünümden seçime dönüşüm, en çok bakılan bloklar. Satış görüşmesinde asıl değer, olayların satın alma verisiyle birleştirilmesidir: "görünüme bakanların dönüşümü bakmayanlara göre +x puan".

## 7. Artifact ve demo notları
- Tek dosya, `<html>`, `<head>` ve `<body>` etiketi olmadan. three.js r128, cdnjs'ten UMD global olarak yükleniyor. Fontlar Google Fonts'tan: Bricolage Grotesque, IBM Plex Sans ve IBM Plex Mono.
- Tema: `:root` token'ları, `prefers-color-scheme` ve `data-theme` geçersiz kılması. 3D sahne renkleri de token'lardan okunur ve tema değişince yenilenir.
- Tercihler (marka, dil, tema) `localStorage`'da tutulur. Erişim try/catch içinde ve yalnızca kolaylık içindir.
- `prefers-reduced-motion` açıksa kamera geçişleri ve CSS animasyonları anında gerçekleşir.

## 8. Bilinen sınırlamalar
- Sahne prosedürel. Gerçek mekân görüntüsü yok; görüş kalitesi (direk, korkuluk, kafa engeli) modellenmiyor.
- `scene.params` şemaya ait değil, demo uzantısı. Şemaya eklenmesi ya da kabuğun ayrı bir mesh olarak gelmesi kararlaştırılmalı.
- `viewpoints[]` ve `capture` henüz kullanılmıyor. SplatScene yalnızca stub.
- Müsaitlik ve fiyat sahte (deterministik hash). Satıldı/tutuldu ayrımı yok.
- Erişilebilirlik: harita blokları ve koltuk düğmeleri klavye ile kullanılabilir, 3D görünüm ok tuşlarıyla döner. Ekran okuyucu için 3D sahnenin metin karşılığı yalnızca koltuk çubuğundaki bilgilerden ibaret.
- Uzun sıralarda (45 koltuğa kadar) koltuk şeridi yatay kaydırma gerektiriyor. Büyük stadyumlarda koltuk seçimi için mini ızgara gerekecek.
- Prosedürel arenada üst kat köşe bloklarının ilk sıraları dar. Blok poligonları ilk ve son sıradan türetildiği için düzensiz bloklarda harita sadeleşir.
- Görüntüleyici test ortamında, ağ kısıtı nedeniyle three.js yerel bir kopyadan yüklendi; fontlar yüklenmedi ve yedek font kullanıldı. Artifact'ta cdnjs ve Google Fonts doğrudan yüklenir.
- Headless Chromium'da (SwiftShader) çalıştırıldı; gerçek telefonda FPS ölçümü yapılmadı.

## 9. v0.2: 3D verisi, splat, gömme (bu sürüm)

### 9.1 Dosyalar ve yayın yolları
İki ayrı Artifact yayınlanır. Yollar göreli; sayfa `fetch('data/…')` ile yanında yayınlanan dosyaları okur.

| Artifact | Ana sayfa (`file_path`) | Yanında yayınlanan dosyalar (`files`: yayın yolu → kaynak) |
|---|---|---|
| **A. Satış demosu** (demo-v1'in yerine, aynı URL'ye) | `demo.html` | `data/ornek-arena.venue.json`, `data/sablon-spor-salonu.venue.json`, `data/sablon-tiyatro.venue.json`, `data/ornek.splat` |
| **B. Örnek bilet sitesi** (yeni) | `etkinlik.html` | `viewer.html`, `embed.js`, `data/ornek-arena.venue.json`, `data/sablon-spor-salonu.venue.json`, `data/sablon-tiyatro.venue.json`, `data/ornek.splat` |

- `demo.html` ve `etkinlik.html` Artifact sözleşmesine uyar (doctype/html/head/body yok; `<title>`, `claude:viewport-fit-sides`, `<style>`).
- `viewer.html` **tam iskeletli** ayrı sayfadır (iframe içinde açılır). Elle düzenlenmez: `node build-viewer.js` ile `demo.html`'den üretilir. `demo.html` değişince yeniden üretin.
- `data/*.venue.json` dosyaları `../3d/` altındaki 3D ekibi çıktılarının küçültülmüş kopyasıdır (içerik aynı; `validate_venue.py` GEÇERLİ).
- `data/ornek.splat` sentetiktir: `tools/make_synthetic_splat.py` prosedürel demo mekânından üretir (`SPLAT_K=1.8`, 100.860 gauss, 3,08 MB).
- `demo-v1.html` referanstır, yayınlanmaz. `screens/v2/` test ekran görüntüleridir, yayınlanmaz.

### 9.2 Şema v0.2 uyumu
- `transform.rotationY` derece (`×π/180`); `transform.rotation` kuaterniyonu varsa o kullanılır. Dönüşüm yalnız sahne kabuğuna/splat'e uygulanır, koltuklar mekân koordinatındadır.
- Sandalye tabanı = basamak zemini = `eye.y − 1,15` (v0.1 demo −1,60 kullanıyordu).
- `venue.origin` (yoksa `type`'tan türetilir). `stage-front-center`: saha dikdörtgeni çizilmez; sahne kutusu (Y=0 döşeme, −Z içeri), sahne ağzı çerçevesi ve marka bandı çizilir; kamera genel bakışta seyirci tarafından sahneye bakar. `field-center` + `arena`: basketbol sahası, potalar, skorbord; `stadium`: 105×68 düz zemin.
- `scene.params` yalnız `kind=procedural` iken okunur. Yoksa (3D ekibi dosyaları) kabuk koltuklardan türetilir: her koltuğun altına basamak bloğu. **Çıkma tespiti:** bir bloğun koltuklarının altında (XZ'de 1,2 m içinde, ≥1,5 m aşağıda) başka bloktan koltuk varsa o blok balkon sayılır ve bloklar zemine inmez (yalnız önceki sıranın basamağına; ilk sıra 0,7 m korkuluk). Aksi halde tiyatro balkonu parteri örtüyordu.
- `seat.obstructed` (`true` veya `{severity, reason}`): koltuk çubuğunda "Kısıtlı görüş" / "Ciddi kısıtlı görüş" uyarısı ve gerekçe, blok kartında sayaç, koltuk şeridinde köşe işareti. Önerilen koltuk seçimi kısıtlı koltukları atlar. `seat_view` olayına `obstructed` alanı eklendi.
- `scene.format` / `scene.files`: splat yükleyici `files` varsa en büyük `lod`'u seçer (bu sürüm tek `.splat` dosyası yükler). `viewpoints[].row/seat/lensHeight` okunur ama henüz kullanılmaz.
- Demo uzantıları `x-` önekli (`x-categories`). Demonun ürettiği venue nesnesi JSON'a dökülüp doğrulandı: prosedürel ve splat varyantı ikisi de **GEÇERLİ** (28 blok, 11.270 koltuk, 28 viewpoint).
- Blok haritası (SVG) her yüklemede bloklardan üretilir. Tiyatroda katlar üst üste bindiği için her kat (Parter, Balkon…) ayrı panelde, sahne üstte çizilir; seçili koltuk noktası da aynı kaydırmayla yerleşir. Bilinmeyen fiyat kategorileri için `VIP` rengi eklendi (spor salonu şablonu).

### 9.3 Gömme protokolü (`embed.js`)
```html
<div id="koltuk" style="height:680px"></div>
<script src="embed.js"></script>
<script>
  const v = KoltukViewer.mount(document.getElementById('koltuk'), {
    venue: 'arena3d', brand: 'biletra', lang: 'tr',
    onSeatSelect: seat => sepeteEkle(seat),   // {ticketCode, sectionId, sectionName, row, seat, priceCategory, categoryName, price, currency, obstructed, venueId, venueName}
    onEvent: ev => dataLayer.push(ev), onReady: () => {}, onVenueLoaded: m => {}
  });
  v.selectVenue('tiyatro'); v.selectSeat('PS-A-1'); v.setTheme('dark'); v.destroy();
</script>
```
- `mount` iframe'i `viewer.html?embed=1&venue=…&brand=…#ch=<rastgele kanal>` ile açar. Hazır olmadan gönderilen komutlar kuyruğa alınır.
- Host → görüntüleyici: `koltuk:selectVenue`, `loadVenue`, `selectSection`, `selectSeat`, `overview`, `setBrand`, `setLang`, `setTheme`. Görüntüleyici → host: `koltuk:ready`, `venueLoaded`, `seatSelected`, `event`.
- Kabul kuralları (iki yönde): kaynak pencere doğru (`e.source`), kanal kimliği eşleşiyor, origin izin listesinde. Görüntüleyicide izin listesi demo için `[location.origin]`; üretimde müşteri kaydından sunucu tarafında doldurulur (URL parametresine güvenilmez).
- Opak origin (`"null"`, sandbox'lı çerçeve): origin karşılaştırılamadığı için pencere + kanal eşleşmesi zorunlu, hedef `'*'`. Mesajlar kişisel veri taşımaz. Artifact barındırıcısı sayfayı sandbox'lı çerçevede açıyorsa bu yol devreye girer.
- Host sayfa kök öğesinde `data-theme` değişirse (`MutationObserver`) görüntüleyiciye `setTheme` gider.

### 9.4 Örnek bilet sitesi (`etkinlik.html`)
Kurgusal "Biletra" etkinlik sayfası: üç etkinlik sekmesi (Örnek Arena basketbol, Şablon Spor Salonu, Şablon Tiyatro), "Etkinlik → Koltuk seç → Ödeme" adımları, iframe'de görüntüleyici, sağda (telefonda altta + yapışkan alt çubuk) sepet. "Bu koltuğu seç" → `koltuk:seatSelected` → sepete satır, toplam, sayaç. Aynı koltuk iki kez eklenmez, en fazla 6 bilet. "Entegrasyon günlüğü" açılır kutusu gelen/giden mesajları gösterir (satış görüşmesinde entegrasyonu anlatmak için). Ödeme adımı yok.

### 9.5 Splat (SplatScene)
- Harici kütüphane yok: three r128 üzerinde ~150 satırlık minimal çizici. `.splat` (32 bayt/gauss) → 3 adet RGBA32F doku; vertex shader'da EWA projeksiyonu; kamera değişince CPU'da 16 bit sayma sıralaması (100k gauss için 1,5–2,3 ms), yalnız sıra dizisi GPU'ya yüklenir. Koltuklar görünmez çarpışma geometrisi olarak kalır (seçim, işaretçi, kamera aynı).
- Yükleme: fetch akışıyla ilerleme çubuğu; başarısızsa koltuklardan türetilen kabuğa düşer ve uyarı verir.
- Sonuç: 3,08 MB, headless Chromium'da yerel sunucudan ~0,8 sn indirme + 20 ms ayrıştırma. FPS yalnız SwiftShader (yazılım GPU) ile ölçülebildi: splat 0,3–0,7 fps, aynı ortamda prosedürel sahne 2,3 fps; yani ölçüm gerçek cihazı temsil etmez. Gerçek telefon/masaüstü GPU'sunda ölçüm yapılmalı.
- Öneri: gerçek çekimler için (≥1M gauss, SH, LOD) bakımı süren bir kütüphaneye geçmek (ör. three.js üzerinde Spark veya GaussianSplats3D; `.spz`/`.sog` desteği), bu minimal çiziciyi yedek/test yolu olarak tutmak. Sıralamayı Web Worker'a taşımak gerekecek.

### 9.6 v0.1 notlarından geçersizleşenler
- §8 "SplatScene yalnızca stub" ve "`scene.params` şemaya ait değil": artık geçersiz (bkz. 9.2, 9.5).
- §3b'deki `mount()` taslağı: demo sürümü `embed.js` ile iframe tabanlı olarak hazır; script/Shadow DOM modu hâlâ yol haritasında.

### 9.7 Test (v2)
Statik sunucu (`python3 -m http.server`) + Playwright Chromium; three.js ve fontlar proxy 403 verdiği için testte yerel kopyadan/boş CSS ile sunuldu (yayın dosyalarında CDN URL'leri duruyor). Masaüstü 1280×800 ve telefon 390×844, açık/koyu tema:
- Konsol/sayfa hatası: 0. Yatay kaydırma: yok.
- Üç 3D ekibi mekânı yüklendi (11.868 / 2.112 / 770 koltuk). Haritadan blok → "Görünümü aç" sonrası kamera konumu ile koltuğun `eye` değeri arasındaki fark ≤ 3 mm.
- Kısıtlı görüş: `101-1-12` → "Ciddi kısıtlı görüş", `PS-M-1` → "Kısıtlı görüş" (gerekçeyle).
- Host sayfa: arena ve tiyatroda "Bu koltuğu seç" → sepet 1 → 2, toplam doğru; yanlış kanaldan gelen komut ve sahte kaynaklı `seatSelected` yok sayıldı.
- Ekran görüntüleri: `screens/v2/`.

### 9.8 Bilinen sorunlar (v0.2)
- Türetilmiş kabuk (3D ekibi dosyaları) kaba: basamak blokları koltuk başına; arena dış cephesinde dikey çizgili görünüm. Tiyatroda yan duvar/tavan yok, sahne çerçevesi şematik.
- Spor salonu şablonunda skorbord yüksekliği tahmini (9 m); çatı yok.
- Sentetik splat yakın plandaki koltuklarda bulanık (koltuk başına 2 gauss).
- Görüntüleyici embed modunda telefonda kendi içinde kaydırılır (iframe 760 px); host sayfa ile iç içe kaydırma var.
- Opak origin yolunda (sandbox) güvenlik kanal kimliğine dayanır; üretimde görüntüleyici ayrı bir origin'den sunulmalı.


## 10. v0.3: "Seviye karşılaştır" modu

İki ürün seviyesi aynı koltuktan yan yana gösterilir:
- **Standart · plan verisinden** (sol/üst): ProceduralScene, yani oturma planından kodla üretilen 3D.
- **Gerçek görüntü · mekân çekiminden** (sağ/alt): SplatScene. Panelde "örnek veri" ibaresi var, çünkü splat sentetik.

**Nasıl açılır**
- Demo ayarları → "Seviye karşılaştır".
- `?mod=karsilastir` adresi.
- Gömülüyken host'tan `koltuk:setCompare {on}`, ya da API'de `KoltukViewer.setCompare(true)`.
- Yalnız splat sahnesi olan mekânda anlamlı. Başka mekândayken açılırsa "Örnek Arena · splat sahnesi"ne geçilir ve kullanıcıya bildirilir. Splatsiz bir mekâna dönülünce karşılaştırma kendiliğinden kapanır.

**Teknik**
- Tek WebGL bağlamı, iki viewport (`setScissor`/`setViewport`) ve iki `THREE.Scene`; kamera tek. Bu sayede eye/lookAt, sürükleme, yakınlaştırma ve koltuk geçişleri iki panelde her zaman aynıdır.
- Kameranın en-boy oranı panel boyutuna göre ayarlanır.
- Masaüstünde paneller yan yana. Dikey sahnede (en/boy < 0,95, yani telefonda) üst/alt yerleşir ve sahne yüksekliği %72'ye çıkar.
- Dokunma/tıklama, tıklanan panelin kendi NDC'sine çevrilir.
- `SplatMesh.update` viewport boyutunu `renderer.getCurrentViewport()`'tan okur; yarım panelde EWA ölçeği bu yüzden doğru kalır. Çatı kesme (`clipY`) iki modda da çalışır.
- Standart panelin prosedürel kabuğu, splat mekân nesnesinin kökündeki `x-standardScene` uzantısından gelir (şemaya uygun `x-` alanı). Bu alan yoksa kabuk koltuklardan türetilir.

**Analitik**
- `compare_view` olayı (`ticket_code, section_id, price_category, source`) iki durumda gönderilir: mod açıldığında ve karşılaştırma açıkken koltuk değiştiğinde.
- `source` değerleri: `url | settings | button | api | host | nav | picker | 3d`.

**Test**
- Ortam: Playwright, 1280×800 ve 390×844, açık/koyu tema.
- Konsol hatası çıkmadı.
- Kamera, seçilen koltuğun `eye` noktasıyla aynı konumda: fark 0,000 m. İki panel aynı kamerayı kullanıyor.
- Koltuk değişimi, sürükleme, mekân değişince modun kapanması, ayarlardan yeniden açılması ve kapatma düğmesi doğrulandı.
- Ekran görüntüleri: `screens/v3/`.

**Bilinen sorunlar**
- Telefonda koltuk çubuğu alt panelin bir kısmını örtüyor.
- Karşılaştırmada iki sahne çizildiği için kare maliyeti kabaca toplanır.
- Sentetik splat yakın planda bulanık; bu, "gerçek görüntü" seviyesini olduğundan zayıf gösterir.
