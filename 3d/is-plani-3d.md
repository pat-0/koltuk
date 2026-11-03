# 3D ve Çekim — İlk 12 Haftalık İş Planı

Sürüm 0.1 · Hafta 1 = karar verildiği hafta. Süreler kişi-gün (kg), tek sorumlu varsayımıyla.
Dış bağımlılıklar: **[SAT]** satış/iş geliştirme (mekân izni, pilot müşteri, bilet kodu verisi), **[WEB]** web görüntüleyici ekibi, **[YÖN]** yönetim (bütçe/satın alma), **[HUK]** hukuk.

| # | Hafta | Görev | Bağımlılık | Süre | Çıktı |
|---|---|---|---|---|---|
| 1 | 1 | Ekipman ve yazılım listesinin onayı, bütçe | [YÖN], `ekipman-ve-yazilim.md` | 1 kg | Onaylı satın alma listesi |
| 2 | 1 | Şema v0.1 açık noktalarının web ekibiyle netleştirilmesi (rotationY birimi, göz yüksekliği referansı, tiyatroda orijin, splat formatı) | [WEB] | 0.5 kg | Şema v0.2 önerisi |
| 3 | 1–2 | Ekipman teslimi, kamera firmware/Studio kurulumu, iş istasyonu kurulumu (CUDA, COLMAP, Nerfstudio, Postshot) | #1 | 2 kg | Çalışan işleme ortamı, kurulum notları |
| 4 | 2 | **Ofis/kampüs test çekimi** (izin gerektirmeyen bir oda/merdivenli amfi): X5 ayar testleri — 8K vs 5.7K, enstantane, WB, lens koruyucu etkisi, yürüyüş hızı | #3 | 1 kg | Test raporu; protokoldeki "doğrulanmadı" maddelerinin ilk turu |
| 5 | 2–3 | Test verisinin üç boru hattında işlenmesi (Postshot / Nerfstudio+COLMAP / Polycam) ve karşılaştırma (kalite, süre, maliyet) | #4 | 3 kg | Karşılaştırma tablosu; varsayılan araç kararı |
| 6 | 3 | `isleme-rehberi.md` ve `cekim-protokolu.md` v0.2 (test bulgularıyla) | #4, #5 | 1 kg | Güncellenmiş belgeler |
| 7 | 3 | Demo mekânı adayları için çekim gereksinim listesi (boş salon, ışık, süre, ekip) satışa iletilir | [SAT] | 0.5 kg | Tek sayfalık mekân talep listesi |
| 8 | 3–4 | Web ekibiyle uçtan uca entegrasyon: test splat + `venue.json` görüntüleyicide açılıyor; dosya formatı ve boyut hedefleri | #5, [WEB] | 2 kg | Çalışan prototip; format kararı (PLY sıkıştırılmış / SOG / SPZ) |
| 9 | 4 | Demo mekânı için ön blok CSV'si (oturma planından), çekim planı (`--capture-plan`), rota planı | Mekân seçimi [SAT], plan PDF | 1 kg | `mekan-bloklar.csv`, `cekim-plani.csv`, rota haritası |
| 10 | 5 | **Demo çekimi** (tiyatro/üniversite salonu/spor salonu) | #9, yazılı izin [SAT][HUK] | 1 kg saha + 0.5 kg hazırlık | Ham veri (2 kopya), çekim günlüğü, ölçümler |
| 11 | 5–6 | Demo işleme: kare çıkarma → splat → temizlik → hizalama | #10 | 4 kg | Temiz, hizalanmış splat |
| 12 | 6 | Koltuk eşleme + `venue.json` + viewpoints | #11, (varsa) bilet kodu listesi | 1.5 kg | `demo.venue.json`, koltuk CSV |
| 13 | 6–7 | Demo QC (referans fotoğraf karşılaştırması, KVKK taraması, mobil performans) ve düzeltmeler | #12, [WEB] | 2 kg | QC raporu, yayınlanabilir demo |
| 14 | 7 | Süre/maliyet kaydı: gerçek saha ve işleme süreleri → teklif hesaplayıcısı için birim süreler | #10–#13 | 0.5 kg | "Mekân başı efor" tablosu (satış fiyatlandırması girdisi) |
| 15 | 7–8 | Otomasyon: betikleri tek komutlu boru hattına bağlama (`pipeline.py`: klasör yapısı → persp → COLMAP/Nerfstudio), günlük → viewpoints.csv dönüştürücü | #11 | 3 kg | Yeniden üretilebilir boru hattı |
| 16 | 8 | Web görüntüleyicide "koltukları göster" hata ayıklama modu ve koltuk–splat sapma ölçümü | [WEB] | 1 kg (bizden) | Sapma ≤ 30 cm doğrulaması |
| 17 | 8–9 | Pilot müşteri mekânı ön keşif (plan, ölçü, ışık, izin koşulları); büyük mekân bölgeleme planı | Pilot müşteri [SAT] | 1.5 kg | Keşif raporu, çekim takvimi önerisi |
| 18 | 9 | Drone ihtiyacı değerlendirmesi (pilot açık hava ise): lisanslı operatör gereksinim listesi ve izin süreci araştırması | #17, [HUK] | 1 kg | Drone karar notu (operatör kiralama şartnamesi) |
| 19 | 9–10 | **Pilot çekim** (1–2 gün) | #17, izin | 2–3 kg | Ham veri, günlük, ölçümler |
| 20 | 10–11 | Pilot işleme (bölgeli), hizalama, koltuk eşleme (**gerçek bilet kodlarıyla, `--strict`**) | #19, bilet kodu dışa aktarımı [SAT] | 6 kg | `pilot.venue.json`, splat dosyaları |
| 21 | 11–12 | Pilot QC + müşteri geri bildirim turu, düzeltmeler | #20, [WEB] | 3 kg | QC raporu, kabul tutanağı taslağı |
| 22 | 12 | Retrospektif: protokol/rehber v1.0, ekipman ikinci aşama önerisi (2. kamera, LiDAR, drone?), sonraki mekânlar için kapasite planı | #21 | 1 kg | v1.0 belgeler, Q2 planı |

**Toplam:** ~40 kişi-gün / 12 hafta (≈ %65 kullanım; kalan zaman beklemeler, yeniden çekim ve beklenmedik işler için tampon).

## Kritik yol
Ekipman (#1, #3) → test çekimi (#4) → araç seçimi (#5) → **demo mekânı izni** [SAT] → demo çekim (#10) → demo yayını (#13) → pilot (#19–21).
En büyük risk: **mekân izninin gecikmesi**. Önlem: #4 test çekimi izin gerektirmeyen bir alanda yapılır; demo için en az 2 yedek mekân adayı tutulur.

## Kilometre taşları
- **H3 sonu:** Boru hattı seçildi, test sahnesi web'de açılıyor.
- **H7 sonu:** Demo mekânı yayınlanabilir kalitede; efor/maliyet ölçümleri satışa teslim.
- **H12 sonu:** Pilot müşteri sahnesi kabul aşamasında; protokol v1.0.

## Riskler
| Risk | Etki | Önlem |
|---|---|---|
| Mekân izni / boş salon zamanı bulunamaması | Takvim kayar | Yedek mekânlar; gece/sabah erken çekim |
| Büyük mekânda SfM kopukluğu | Yeniden çekim | Döngü kapatan rotalar, RealityScan ile poz, bölgeleme |
| Splat dosya boyutu mobilde ağır | Kötü UX | Erken (H3–4) web entegrasyonu, LOD, SH düşürme |
| Lisans (Postshot Free ticari değil, Polycam bulut verisi) | Hukuki | Indie/Studio lisans, yerel işleme |
| KVKK — görüntüde kişi | Hukuki/itibar | Boş mekân şartı, iki aşamalı tarama |
| Işık/etkinlik düzeni farkı (müşteri farklı düzen ister) | Ek çekim | Düzen sözleşmede yazılı; ek düzen = ek iş kalemi |
