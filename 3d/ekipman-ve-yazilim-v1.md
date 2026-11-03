# Ekipman ve Yazılım

Sürüm 0.1 · Tarih: 2026-10-31 · Fiyatlar USD, ABD perakende, vergi hariç; Türkiye fiyatları (gümrük/KDV) **farklıdır** ve ayrıca alınmalıdır.
**Bu belge satın alma kararı değildir; hiçbir satın alma yapılmadı.**

Durum işaretleri: ✅ kaynakla doğrulandı (URL aşağıda) · ⚠️ ikincil kaynak · ❓ doğrulanmadı / tahmin

---

## 1. Minimum başlangıç seti (demo + ilk pilot)

| Kalem | Model / öneri | Fiyat (USD) | Durum | Not |
|---|---|---|---|---|
| 360 kamera | Insta360 X5 (standart paket) | 549.99 | ✅ [1] | Essentials paketi 659.99 [1]. 8K30 360 video, 72 MP fotoğraf, değiştirilebilir lens [1][2] |
| Ek batarya | Insta360 X5 orijinal batarya × 2 | ~? | ❓ | Essentials paketi ek batarya içeriyorsa paket daha ekonomik olabilir (içerik doğrulanmadı) |
| Hafıza kartı | microSD V30/UHS-I, 256 GB × 2 | ~25–40/adet | ❓ | Insta360 uyumlu kart listesinden seçilmeli |
| Görünmez selfie çubuğu | Insta360 114 cm veya uzun versiyon | ~25–60 | ❓ | Yürüyüş çekimi |
| Işık ayağı/tripod | Lens 0.9–2.2 m ayarlanabilir, dar tabanlı | ~40–100 | ❓ | Tribün sıraları arasına sığmalı; kabarcık terazili |
| Lazer metre | Bosch GLM 50-27 C sınıfı veya muadili | ~100–150 | ❓ | Saha ve sıra ölçüleri |
| Şerit metre | 5 m + 30 m | ~30 | ❓ | |
| Gri kart | 18% gri / WB kartı | ~15 | ❓ | Sabit beyaz dengesi |
| Harici SSD | 2 TB × 2 (yedek için iki ayrı) | ~120–180/adet | ❓ | 8K video ~81 GB/saat (180 Mb/s'den hesap) |
| İşleme iş istasyonu | NVIDIA GPU **≥ 16 GB VRAM** (RTX 4080/5080 sınıfı), arena için **24–32 GB** (RTX 4090/5090 sınıfı), 64 GB RAM, 4 TB NVMe | ~2.500–4.500 | ❓ | En büyük kalem. Alternatif: saatlik bulut GPU kiralama (ör. 24 GB+ GPU), başlangıçta daha ucuz |
| Dizüstü (saha QC) | Herhangi bir dizüstü; GPU'lu ise sahada hızlı splat testi | mevcut | — | |
| **Toplam (iş istasyonu hariç)** | | **~1.000–1.300** | ❓ | |

## 2. Yazılım ve lisanslar

| Yazılım | Kullanım | Fiyat | Ticari kullanım / lisans notu | Durum |
|---|---|---|---|---|
| **Insta360 Studio** | .insv dikiş, equirect dışa aktarım | Ücretsiz | Üretici yazılımı; çıktı görüntüler bize ait (EULA okunmadı) | ❓ |
| **ffmpeg** | Kare çıkarma | Ücretsiz | LGPL/GPL; yalnız dahili araç olarak kullanıyoruz, dağıtmıyoruz → sorun beklenmez | ⚠️ |
| **Python + numpy + OpenCV** | Betiklerimiz | Ücretsiz | BSD / Apache-2.0 | ⚠️ |
| **Postshot (Jawset)** | Yerel splat eğitimi (Windows + NVIDIA) | Planlar: Free / Indie / Studio. Üretici sayfasında fiyatlar dinamik yükleniyor, **USD fiyat okunamadı**. İkincil kaynak "Pro $199/yıl" diyor; mevcut plan adları ile eşleşmiyor | **Free = ticari değil** ve PLY/SPZ dışa aktarım yok; **Indie ve Studio ticari kullanıma izinli**, Indie PLY/SPZ dışa aktarım ve filigransız; Studio: >4K, HDR, CLI, AprilTag ile otomatik hizalama [3] | ✅ plan içeriği [3] · ❓ fiyat |
| **Polycam** | Bulut splat/fotogrametri | Pro ~$150/yıl, Business ~$400/yıl (ikincil kaynak [4]) | Ticari kullanım ve veri işleme koşulları **okunmadı**; veri bulut sunucusuna gider → mekân izni/KVKK | ⚠️ fiyat · ❓ lisans |
| **Nerfstudio** (splatfacto) | Yerel açık kaynak splat | Ücretsiz | Apache-2.0 [4] | ⚠️ |
| **gsplat** | Nerfstudio'nun splat motoru | Ücretsiz | Apache-2.0 olduğu düşünülüyor | ❓ |
| **COLMAP / GLOMAP** | Poz kestirimi (SfM) | Ücretsiz | BSD tipi lisans olduğu düşünülüyor | ❓ |
| **RealityScan 2 (Epic)** | Hızlı/sağlam poz kestirimi, fotogrametri | Son 12 ay brüt geliri **< $1M** olan birey/şirket ve eğitim kurumları için **ücretsiz**; üzeri **$1.250/koltuk/yıl** [5] | Gelir eşiğinin şirket mi ürün bazında mı olduğu ve TL gelirin nasıl çevrildiği SSS'te — okunamadı; EULA okunmadı | ✅ eşik/fiyat · ❓ ayrıntı |
| **SuperSplat (PlayCanvas)** | Splat temizleme, sıkıştırma | Ücretsiz | MIT [4] | ⚠️ |
| **CloudCompare** | Nokta bulutu ölçüm/hizalama (opsiyonel) | Ücretsiz | GPL (dahili araç) | ❓ |

## 3. Sonraki aşama ekipmanı (pilot müşteri sonrası)

| Kalem | Ne zaman | Fiyat (USD) | Durum | Not |
|---|---|---|---|---|
| İkinci Insta360 X5 | Arena/stadyum ölçeğinde 2 ekip paralel çekim | 549.99 | ✅ [1] | |
| **DJI Mini 5 Pro** | Açık stadyum çatı/üst görünüm, dış cephe | Amazon'da gözlenen $759; Fly More Combo $1.099 (gözlenen) [6] | ⚠️ (lansman fiyatı değil) | ~249 g; "Battery Plus" ile 250 g sınırını aşabilir (inceleme [7]) — Türkiye kayıt/izin eşikleri **doğrulanmadı**. İlk projelerde **lisanslı operatör kiralama** önerilir |
| Drone operatörü hizmeti | İlk 1–3 açık hava projesi | proje başına teklif | ❓ | İzinleri operatör alır, sigortalı |
| Aynasız fotoğraf makinesi + balıkgözü lens | 360 kameranın çözünürlüğü yetmezse (büyük stadyum, uzak sahne detayı) | ~1.500–3.000 | ❓ | Daha keskin splat; çekim süresi uzar |
| El tipi LiDAR tarayıcı (ör. XGRIDS Lixel sınıfı) veya iPhone Pro LiDAR | Doğru ölçek ve geometri, büyük mekânda hız | iPhone mevcutsa 0; profesyonel tarayıcılar $10.000+ | ❓ | Fiyatlar doğrulanmadı; önce kiralama |
| Ek GPU / bulut GPU bütçesi | Aynı anda birden çok mekân | aylık | ❓ | |
| NAS (≥ 20 TB) | Ham veri arşivi (müşteri başına 0.5–2 TB) | ~1.000–1.500 | ❓ | 3-2-1 yedek kuralı |

## 4. Açık lisans soruları (hukuk/satın alma ile netleşecek)
1. Postshot Indie ile Studio arasındaki **USD yıllık fiyat** ve koltuk sayısı; AprilTag hizalama için Studio gerekli mi? (İş akışında zaman kazandırır.)
2. Polycam ile işlenen müşteri mekân verisinin **saklama/eğitim amaçlı kullanım** koşulları — müşteri sözleşmesine aykırı olabilir.
3. RealityScan ücretsiz eşiği: Hyperbaric'in grup/toplam geliri < $1M mi? Eşik aşılırsa $1.250/koltuk/yıl.
4. Insta360 Studio EULA'sında ticari kullanım kısıtı var mı (beklenmez ama okunmalı).
5. Web'de kullanılacak splat görüntüleyici kütüphanesinin lisansı (web ekibinin sorumluluğu; uyumlu olmalı).

## Kaynaklar
1. TechRadar, Insta360 X5 incelemesi (ABD fiyatı $549.99 / Essentials $659.99; 1/1.28" sensörler, 8K30, değiştirilebilir lens): https://www.techradar.com/cameras/360-cameras/insta360-x5-review
2. B&H Photo, Insta360 X5 teknik özellikleri (8K 24/25/30, 5.7K 60'a kadar, 72 MP DNG, 180 Mb/s, manuel pozlama, WB 2000–10000K, 8K30'da ~88 dk): https://www.bhphotovideo.com/c/product/803199665-USE/insta360_cinsaaha_x501_x5_360_deg_8k_camera.html/specs
3. Jawset Postshot fiyat/plan sayfası (Free ticari değil; Indie/Studio ticari; dışa aktarım ve Studio özellikleri): https://activation.jawset.com/shop/pricing
4. The Future 3D, "Gaussian splatting software tools compared 2026" (Polycam Pro $150/yıl, Business ~$400/yıl; PostShot Pro $199/yıl; Nerfstudio Apache 2.0; SuperSplat MIT): https://www.thefuture3d.com/blog/gaussian-splatting-software-tools-compared-2026
5. RealityScan lisans sayfası (< $1M ücretsiz; üzeri $1.250/koltuk/yıl): https://www.realityscan.com/license?lang=en-us
6. DroneXL, DJI Mini 5 Pro teknik/fiyat (Amazon $759, Fly More Combo $1.099 gözlenen): https://dronexl.co/specs/dji-mini-5-pro/
7. T3, DJI Mini 5 Pro incelemesi ("no longer truly sub-250 g"): https://www.t3.com/tech/drones/dji-mini-5-pro-review
8. FFK Partner Hukuk, "Drone kullanmanın hukuki şartları 2026" (500 g ve üzeri kayıt, ticari kullanımda lisans/izin — ikincil kaynak, SHGM'den teyit edilmeli): https://www.ffkpartnerhukuk.com.tr/drone-kullanmanin-hukuki-sartlari-2026-guncel-rehber-iha-ve-drone-hukuku/
