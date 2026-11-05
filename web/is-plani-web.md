# Web geliştirici: ilk 12 hafta iş planı

Varsayım: tek web geliştirici, haftada ~40 saat. 3D ekibi 6. haftada ilk splat ve 360 çekimini teslim ediyor. Satış ekibi 3. haftadan itibaren pilot müşteri görüşmesi yapıyor. Süreler adam-gün (ag) cinsinden.

| # | Hafta | Görev | Süre | Bağımlılık | Çıktı |
|---|---|---|---|---|---|
| 1 | 1 | Satış demosunu (demo.html) satış ekibinden gelen geri bildirimle cilalamak; gerçek telefonlarda (iOS Safari, orta segment Android) FPS ve dokunma testi yapmak | 3 ag | — | Demo v0.2, cihaz test raporu |
| 2 | 1 | `venue.json` şemasını 3D ekibiyle netleştirmek: `scene.params` / kabuk mesh, `viewpoints.capture`, sürüm kuralları; JSON Schema dosyası yazmak | 2 ag | 3D ekibi | `venue.schema.json` v0.2, örnek dosyalar |
| 3 | 2 | Kod tabanını ayırmak: Vite + TypeScript monorepo (`viewer-core`, `scene-procedural`, `scene-splat`, `embed`); demo davranışını birim ve görsel regresyon testleriyle (Playwright) sabitlemek | 5 ag | 1 | Repo, CI, görsel test referansları |
| 4 | 3 | `venue.json` doğrulayıcı ve içe aktarma aracı: CSV (`section,row,seat,ticketCode`) eşleşme raporu, eksik `eye` için satır/koltuk geometrisinden ara değerleme | 4 ag | 2 | CLI `koltuk-validate`, hata raporu formatı |
| 5 | 3–4 | Gömme katmanı: iframe sayfası, `postMessage` protokolü (origin izin listesi), `KoltukViewer.mount()` script paketi, Shadow DOM ile stil izolasyonu | 6 ag | 3 | `embed.js` v0.1, entegrasyon dokümanı, örnek host sayfası |
| 6 | 4–5 | Beyaz etiket yapılandırması: marka teması JSON'u, logo SVG, font seçimi, "altyapı" ibaresi kontrolü; marka başına önizleme sayfası | 3 ag | 5 | Tema şeması, 2 pilot marka teması |
| 7 | 5 | Bilet sağlayıcı adaptör arayüzü (`TicketProvider`) ve mock sunucu; müsaitlik önbelleği (TTL) ve tazeleme | 4 ag | 4 | Adaptör paketi, sözleşme testleri |
| 8 | 6–7 | `SplatScene`: splat renderer entegrasyonu, aşamalı yükleme, `transform` hizalama aracı (eye noktalarını bindirme), görünmez çarpışma koltukları | 8 ag | 3D ekibinin ilk çekimi, 3 | SplatScene v0.1, hizalama ekran görüntüleri |
| 9 | 8 | 360 viewpoint katmanı: en yakın çekim noktasına cross-fade, equirect kürede sınırlı bakış; mobil bellek ve doku sıkıştırma | 4 ag | 8 | 360 modu, performans ölçümleri |
| 10 | 8–9 | Analitik hattı: `sendBeacon` ile toplu gönderim, olay toplayıcı uç noktası (backend ile), müşteri için `onEvent` / GA4 / dataLayer köprüsü; KVKK metni girdisi | 5 ag | 5, backend | Olay şeması v1, örnek dashboard sorguları |
| 11 | 10 | Performans ve erişilebilirlik turu: LOD, piksel oranı uyarlama, ilk görüntü ≤ 3 sn hedefi; klavye ve ekran okuyucu (koltuk listesi alternatifi), kontrast denetimi | 5 ag | 8, 9 | Lighthouse ve cihaz raporu, düzeltmeler |
| 12 | 11 | Pilot müşteri entegrasyonu: gerçek etkinlik, bilet API'si (staging), uçtan uca test, hata izleme (Sentry vb.) | 5 ag | 5, 7, 10, pilot sözleşmesi | Pilot canlıya hazır sürüm |
| 13 | 12 | Pilot canlıya alma, ilk hafta izleme; satış için "önce/sonra" dönüşüm raporu şablonu; v1 yol haritası | 4 ag | 12 | Canlı pilot, rapor şablonu, v1 backlog |

Toplam: ~58 ag (12 haftada ~60 ag kapasite; tampon dar). Risk durumunda ilk ertelenecek iş 9 (360 katmanı), sonra 6'nın önizleme sayfası.

## Kritik bağımlılıklar ve riskler
- **3D ekibi çekim takvimi (6. hafta):** gecikirse 8–9. işler kayar. Bu durumda pilot ProceduralScene + 360 görsel ile yapılır.
- **Bilet sağlayıcı API erişimi:** staging erişimi 7. haftaya kadar gelmezse adaptör mock ile tamamlanır, pilotta yalnızca görüntüleme açılır.
- **Mobil splat performansı:** hedef karşılanmazsa mobilde 360 görüntüye düşen hibrit mod kullanılır.
- **Hukuk/KVKK:** analitik verisinin müşteri tarafında mı yoksa bizde mi tutulacağı 8. haftadan önce karara bağlanmalı.

## Haftalık ritim
- Pazartesi: 3D ve satış ekipleriyle 30 dk senkron (şema, demo talepleri).
- Cuma: demo ortamına sürüm ve kısa değişiklik notu; satışa "bu hafta gösterilebilecekler" listesi.
