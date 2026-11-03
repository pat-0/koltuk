# İşleme Rehberi — Ham 360 Veriden Web'e Hazır Sahneye

Sürüm 0.2 · İlgili: `cekim-protokolu.md`, betikler bu klasörde, şema `shared/venue-schema-v0.2.md` + `shared/venue.schema.json` (v0.2)

> **İşleme düzeni (31.10.2026 kararı):** Ayrı GPU bilgisayarı yok — Mac + saatlik bulut GPU. Hangi adımın nerede yapıldığı, bulut oturumu, maliyet ve .ply → .splat → .b64.txt web yolu: `isleme-duzeni-mac-bulut.md`. Bu belgedeki Postshot/Polycam önerileri o belgeyle güncellenmiştir (varsayılan: ücretsiz zincir msplat/Brush + splatfacto).
>
> **Kısa yol:** 2–4. adımlar tek komutla: `python3 pipeline.py YYYY-MM-DD_MEKAN` → `10_isleme/images/`, `cameras.txt`, `rapor.md` ve COLMAP/Nerfstudio komutlarını içeren `komutlar.sh` (dry-run). Aşağıdaki adımlar boru hattının ne yaptığını ve elle ince ayarı anlatır.

> *(doğrulanmadı)* işaretli bilgiler ilk demo projesinde test edilip bu belgede güncellenecek. Süreler; tek blok/küçük salon (S) ve 12.000'lik arena (A) için **tahmindir**, RTX 4080/4090 sınıfı tek GPU varsayılmıştır.

## Akış özeti

```
.insv ──(1) Insta360 Studio──► equirect MP4/DNG
        ──(2) extract_frames.py──► equirect kareler
        ──(3) filter_blurry.py──► keskin kareler
        ──(4) equirect_to_persp.py──► perspektif görüntüler (+cameras.txt)
        ──(5) Polycam | Postshot | COLMAP+Nerfstudio──► ham splat (.ply)
        ──(6) SuperSplat──► temiz splat
        ──(7) align_points.py──► scene.transform (ölçek/dönüş/öteleme)
        ──(8) sıkıştırma/LOD──► web dosyası
        ──(9) seats_from_plan.py──► venue.json (koltuklar + viewpoints)
        ──(10) QC──► yayın
```

| # | Adım | Araç | Girdi | Çıktı | Süre S / A |
|---|---|---|---|---|---|
| 0 | Aktarım, yedek | rsync / sha256sum | SD kartlar | `00_ham/` + 2 kopya | 30 dk / 2 sa |
| 1 | Dikiş ve dışa aktarım | Insta360 Studio | .insv / .insp | equirect .mp4, .dng/.jpg | 30 dk / 3–5 sa (render) |
| 2 | Kare çıkarma | `extract_frames.py` | .mp4 | equirect .jpg | 5 dk / 45 dk |
| 3 | Bulanık eleme | `filter_blurry.py` | kareler | seçilmiş kareler + `scores.csv` | 5 dk / 30 dk |
| 4 | 360→perspektif | `equirect_to_persp.py` | seçilmiş kareler | perspektif .jpg + `views.json` | 10 dk / 1–2 sa |
| 5 | Poz + splat eğitimi | Polycam / Postshot / Nerfstudio | görüntüler | .ply | 1–3 sa / 8–24 sa |
| 6 | Temizleme | SuperSplat | .ply | temiz .ply | 1–2 sa / 4–8 sa |
| 7 | Hizalama, ölçek | SuperSplat + `align_points.py` | kontrol noktaları | transform | 30 dk / 1 sa |
| 8 | Web optimizasyonu | SuperSplat / web ekibi araçları | temiz .ply | sıkıştırılmış dosya | 30 dk / 2 sa |
| 9 | Koltuk eşleme | `seats_from_plan.py` | blok CSV, bilet CSV, günlük | `venue.json` | 1 sa / 1 gün (ölçü doğrulama dahil) |
| 10 | Kalite kontrol | görüntüleyici + referans fotoğraflar | hepsi | QC raporu | 1 sa / 1 gün |

---

## 0. Aktarım ve yedekleme
- Kartı **salt-okunur** kopyala: `rsync -a --checksum /media/SD/DCIM/ 00_ham/kamera-X5/`
- `sha256sum` listesi üret (`00_ham/SHA256SUMS`); ikinci diske kopyala ve listeyi doğrula. Kart, iki kopya doğrulanmadan biçimlendirilmez.
- `cekim-gunlugu.csv` ile dosyaları `01_adlandirilmis/` altına adlandırma kuralına göre **kopyala** (orijinal kalır).

## 1. Insta360 Studio dışa aktarım
- **Video:** Equirectangular, en yüksek çözünürlük (8K → 7680×3840), en yüksek bitrate, H.265 veya ProRes *(Studio'nun ProRes seçeneği ve bit hızı üst sınırı sürüme göre değişir — doğrulanmadı)*.
  - Dikiş: "optik akış (optical flow) dikiş" tercih *(menü adı doğrulanmadı)*.
  - **Ufuk düzeltme (horizon leveling) AÇIK**, **yön kilidi AÇIK**: equirect'in "yukarı"sı dünyanın yukarısı olur → hizalamada eğim azalır.
  - Renk iyileştirme/filtre, "Color Plus" vb. KAPALI; gürültü azaltma hafif.
- **Fotoğraf:** DNG → Studio veya Lightroom'da tüm noktalara **aynı** pozlama/WB düzeltmesi (preset); equirect JPEG (kalite 95) ve 16-bit TIFF arşiv. HDR basamaklama yapıldıysa birleştir.
- Çıktı: `02_equirect/video/*.mp4`, `02_equirect/foto/*.jpg`

## 2. Kare çıkarma — `extract_frames.py`
```bash
python3 extract_frames.py 02_equirect/video/*.mp4 -o 03_kareler --fps 2 --start 3
```
- Yürüyüş 0.3–0.5 m/s → **2 fps** ≈ 15–25 cm aralık. Çok yavaş/durağan bölümler varsa 1 fps yeter; sonraki adım fazla kareyi zaten seyreltir.
- Her video için alt klasör ve `<önek>_manifest.json` (kaynak, fps, ffmpeg komutu) yazılır.
- 8K kare ≈ 5–10 MB JPEG (q=2) → 10 dk video × 2 fps = 1.200 kare ≈ 8–12 GB. Disk planla.

## 3. Bulanık kare eleme — `filter_blurry.py`
```bash
# Önce yalnızca rapor: skor dağılımını gör
python3 filter_blurry.py 03_kareler/ROTA-alt-on --report-only --crop-poles 0.15
# Sonra: 3 ardışık kareden en keskinini tut, en bulanık %10'u da at
python3 filter_blurry.py 03_kareler/ROTA-alt-on -o 04_secilen/ROTA-alt-on --window 3 --percentile 10 --rel-threshold 0.4 --crop-poles 0.15
```
- `--crop-poles 0.15`: tavan ve operatörün bulunduğu alt bant ölçüme katılmaz.
- `--rel-threshold 0.4`: video medyanının %40'ının altındaki kareler atılır; uzun bulanık bölümlerde (pencerenin tamamı bulanık) yüzdelikten güvenilirdir. Pencere modu yalnız eşikleri geçen kareler arasından seçer.
- Laplacian varyansı sahneye bağlıdır (dokulu tribün > düz duvar); bu yüzden mutlak eşik yerine **yüzdelik + pencere** önerilir. Mutlak eşik yalnız aynı mekânda kalibre edildikten sonra.
- Hedef: rota başına kalan karelerin ardışık aralığı ≤ 50 cm (2 fps + pencere 3 → ~0.5 sn ≈ 20–30 cm × 3).

## 4. 360 → perspektif — `equirect_to_persp.py`
Çoğu SfM/splat aracı pinhole (perspektif) kamera bekler. Her equirect kare N görünüme bölünür:
```bash
python3 equirect_to_persp.py 04_secilen/ROTA-alt-on -o 05_persp/ROTA-alt-on \
    --yaw-count 8 --pitches 0,30 --stagger --fov 90 --size 1920 --colmap-cameras
```
- **Varsayılan öneri:** ufuk kuşağı 8 × FOV 90° (%50 yatay örtüşme) + 30° yukarı kuşak 8 görünüm (yarım adım kaydırılmış). **Aşağı kuşak ve nadir üretilmez** (operatör/tripod). Saha zemini, tribünden yürürken ufuk kuşağının alt yarısında zaten görünür.
- Sabit tripod noktalarında (operatör saklıyken) `--pitches 0,30,-30 --stagger` kullanılabilir.
- Çıktı çözünürlüğü: 8K equirect'te 90° FOV ≈ 1920 px'e karşılık gelir (7680 × 90/360). Daha büyüğü bilgi eklemez.
- `views.json` her görünümün rotasyonunu içerir: aynı karenin görünümleri **aynı optik merkezi paylaşır**; COLMAP'te "rig" kısıtı olarak verilebilir *(COLMAP sürümüne göre rig desteği — doğrulanmadı)*. Rig kısıtı yoksa SfM bunları bağımsız kameralar olarak çözer; genelde çalışır ama daha yavaştır.
- Görüntü sayısı uyarısı: 1.200 kare × 16 görünüm = 19.200 görüntü. Arena ölçeğinde **bölge bölge** işle (§5.4).

## 5. Poz kestirimi + Gaussian splat eğitimi

### 5.1 Seçenek tablosu

| | **Polycam (bulut)** | **Postshot (yerel, Windows+NVIDIA)** | **COLMAP/GLOMAP + Nerfstudio splatfacto (yerel, Linux)** | **RealityScan 2 (poz) + Postshot/Nerfstudio** |
|---|---|---|---|---|
| Ne zaman | İlk deneme, GPU yokken, küçük salon | **Önerilen üretim aracı**: hızlı, GUI, video/görüntü doğrudan | Tam kontrol, otomasyon, ölçek; sorun ayıklama | Büyük/zor sahnelerde poz kestirimi (hızlı, sağlam SfM) |
| Girdi | Görüntü/video yükleme | Görüntü, video; COLMAP ve RealityScan formatı içe aktarım (üretici sayfası) | Perspektif görüntüler (veya Nerfstudio'nun equirect işleme modu *(doğrulanmadı)*) | Perspektif görüntüler |
| Çıktı | Splat (PLY dışa aktarım plan seviyesine bağlı *(doğrulanmadı)*) | PLY/SPZ (**Indie ve üstü**; Free'de yalnız kamera/nokta) | PLY (`ns-export gaussian-splat`) | COLMAP formatı kameralar/noktalar |
| Görüntü sınırı | Plana bağlı *(doğrulanmadı)* | Sınırsız (üretici sayfası); VRAM sınırı | VRAM sınırı | Pratikte yüksek |
| Veri gizliliği | **Veri buluta gider** → mekân izni + KVKK kontrolü | Yerel | Yerel | Yerel |
| Ticari kullanım | Plan koşulları kontrol edilmeli | **Free = ticari değil**; Indie/Studio ticari | Apache-2.0 (Nerfstudio); COLMAP BSD *(lisans türü doğrulanmadı)* | Yıllık ciro < $1M ücretsiz |
| Süre (S) | 30–90 dk (kuyruk dahil) | 1–2 sa | 1–3 sa | +30 dk poz |

**Karar kuralı:** İlk demo → Postshot (ticari çıktı için Indie lisansı) ile başla; eş zamanlı olarak aynı veriyi Nerfstudio ile işle ve sonuçları karşılaştır (kalite/süre). Polycam yalnız hızlı ön izleme veya GPU arızası yedeği. Poz kestirimi başarısız olursa (kopuk modeller, eksik bloklar) RealityScan 2 ile poz → Postshot'a içe aktar.

### 5.2 Postshot
1. Yeni proje → perspektif görüntü klasörlerini (birden çok rota) sürükle.
2. Kamera takibi: varsayılan; "max image size" 1920.
3. Eğitim profili: splat; adım sayısı varsayılan ile başla, arena bölgeleri için artır *(parametre adları sürüme bağlı — doğrulanmadı)*.
4. Dışa aktarım: PLY (Indie+). Studio sürümü >4K ve AprilTag ile otomatik sahne hizalama sunuyor (üretici sayfası) — kontrol hedefleri AprilTag basılırsa §7 otomatikleşebilir *(test edilmedi)*.

### 5.3 COLMAP + Nerfstudio
```bash
# a) Poz kestirimi (video sıralı olduğu için sequential matcher)
colmap feature_extractor --database_path db.db --image_path 05_persp \
    --ImageReader.camera_model PINHOLE --ImageReader.single_camera 1
colmap sequential_matcher --database_path db.db      # + döngü kapatma için vocab tree (opsiyonel)
colmap mapper --database_path db.db --image_path 05_persp --output_path sparse   # veya: glomap mapper (daha hızlı)
# b) Nerfstudio formatına çevir ve eğit
ns-process-data images --data 05_persp --output-dir ns_data --skip-colmap --colmap-model-path sparse/0
ns-train splatfacto --data ns_data      # büyük sahne için: splatfacto-big
ns-export gaussian-splat --load-config outputs/.../config.yml --output-dir 06_splat
```
- `cameras.txt` (bizim betiğin ürettiği) bilinen PINHOLE iç parametrelerini verir; COLMAP'te `--ImageCamera` parametreleri sabitlenebilir *(bayrak adları sürüme bağlı)*.
- Alternatif: `ns-process-data images --camera-type equirectangular --images-per-equirect 8|14` equirect'i kendisi böler *(doğrulanmadı; bizim betik daha fazla kontrol verir: nadir atma, FOV, kuşaklar)*.

### 5.4 Büyük mekân (arena) stratejisi
- Sahne 4–8 bölgeye ayrılır (ör. her uzun kenar + kale arkası, alt/üst kat), her bölge **komşusuyla %20 örtüşen** rotalarla.
- Önce **tüm rotaların** seyreltilmiş (0.5 fps) görüntüleriyle tek bir global SfM → ortak koordinat sistemi; sonra bölge bazlı yoğun eğitim, bölgeler aynı koordinatlarda birleştirilir (SuperSplat'ta birden çok PLY birleştirme).
- VRAM: tek parça arena splat'ı 24 GB'ı aşabilir *(doğrulanmadı)* → bölgeleme zorunlu sayılmalı.

## 6. SuperSplat'ta temizleme
SuperSplat (tarayıcı tabanlı, MIT lisanslı):
1. PLY'yi aç. Önce **kırpma kutusu** (crop box): mekân dışı (dış cephe yansımaları, camdan görünen dış dünya) sil.
2. **Floater temizliği**: havada asılı yarı saydam bulutlar — fırça/kement seçimi ile sil. Özellikle **koltuktan sahaya bakış konisi** içinde hiç floater kalmamalı (kullanıcı hep oradan bakacak).
3. **Kişi/operatör izleri**: yürüyüş rotası boyunca "hayalet" insan şekilleri → sil (KVKK).
4. Düşük opaklık/çok büyük ölçekli splat'ları filtrele (opaklık eşiği; SuperSplat filtre araçları).
5. Tavan: düşük öncelikli; gürültülüyse tavanı tek renk/procedural ile değiştirmek web ekibiyle konuşulabilir.
6. Kaydet: `07_temiz/<mekan>_temiz.ply` (sıkıştırılmamış arşiv) + web için sıkıştırılmış çıktı (§8).

## 7. Venue koordinat sistemine hizalama ve ölçekleme
Şema: metre, Y yukarı, sağ el; orijin = saha/sahne merkezi zemin; **X = saha uzun ekseni**, Z = kısa eksen.

1. SuperSplat'ta (veya CloudCompare'de nokta bulutu olarak) **kontrol noktalarını** seç ve splat koordinatlarını oku: saha köşeleri (4), orta nokta, en az 2 yüksek nokta (alt kat arka korkuluk vb.).
2. Bu noktaların **venue koordinatlarını** sahadaki ölçümlerden yaz. Basketbol: köşeler (±14, 0, ±7.5) — ama sahada ölçtüğün gerçek değeri kullan. Futbol: (±52.5, 0, ±34). Tiyatro: sahne ağzı köşeleri (±genişlik/2, sahne yüksekliği, 0) ve orijin sahne ağzı merkezi (şema "sahne merkezi" diyor — tiyatroda hangisi olduğu web ekibiyle netleşmeli).
3. `kontrol-noktalari.csv` → `name,sx,sy,sz,vx,vy,vz`
4. Önce eğimi kontrol et:
   ```bash
   python3 align_points.py kontrol-noktalari.csv --mode full
   ```
   Eğim > 0.5° ise: SuperSplat'ta sahneyi bu kadar döndürüp yeniden dışa aktar (şema v0.1 yalnız `rotationY` taşıyor), noktaları yeniden oku.
5. Son değerler:
   ```bash
   python3 align_points.py kontrol-noktalari.csv --json hizalama.json
   ```
   Çıktı: `scale`, `rotationY` (derece ve radyan), `position`, nokta artıkları ve RMS. **Kabul: RMS ≤ 5 cm (salon), ≤ 10 cm (arena)**; büyükse yanlış seçilmiş nokta var demektir (artıklardan bul).
6. Ölçek bağımsız kontrolü: hizalanmış sahnede saha uzunluğunu ölç; bilinen ölçüyle fark **< %1** olmalı.
7. İki yol: (a) transform'u `venue.json → venue.scene.transform`'a yaz (`rotationY` **derece**, şema v0.2; eğim varsa `rotation` kuaterniyonu); ya da (b) transform'u SuperSplat'ta dosyaya pişir ve `transform` birim (0,0,0 / 0 / 1) bırak. **Önerilen: (b)** — görüntüleyici ve koltuk koordinatları tek sistemde olur, hata ihtimali azalır.

## 8. Web için boyut ve performans hedefleri *(öneri; web ekibinin ölçümleriyle güncellenecek)*

| Hedef | Masaüstü | Mobil (orta segment) |
|---|---|---|
| Splat sayısı (görünür sahne) | ≤ 2–3 milyon | ≤ 0.8–1 milyon |
| İndirme boyutu (ilk görüntü) | ≤ 40 MB | ≤ 15–20 MB |
| İlk görüntüye süre (4G) | — | ≤ 5 sn (önce düşük LOD) |
| Kare hızı | ≥ 60 fps | ≥ 30 fps |

Yöntemler: küresel harmonik (SH) derecesini düşür (renk kalitesi/boyut dengesi, SH 0–1 genelde yeterli — test edilecek), opaklığı çok düşük ve bakış konisi dışındaki splat'ları sil, **sıkıştırılmış formatlar** (SuperSplat'ın sıkıştırılmış PLY / SOG çıktısı, Niantic SPZ — hangisinin görüntüleyicide destekleneceği web ekibiyle kararlaştırılacak *(format desteği doğrulanmadı)*), LOD/parçalama (alt kat/üst kat ayrı dosya). Ham PLY: splat başına ~ 248 bayt (SH3) → 3 M splat ≈ 700 MB; sıkıştırma şarttır.

## 9. Koltuk eşleme — `seats_from_plan.py`
1. Blok CSV'sini (`ornek-bloklar.csv` biçimi; sütunlar betiğin `--help`/başlık açıklamasında) **sahada ölçülen** `rowDepth`, `riserHeight`, `frontHeight`, `seatWidth` ve plan geometrisiyle doldur.
2. Bilet sisteminden `section,row,seat,ticketCode` dışa aktarımı al (satış ekibi üzerinden).
3. Çekim günlüğünden `viewpoints.csv` (`id,sectionId,row,seat,file,type,takenAt`) üret.
4. Çalıştır:
   ```bash
   python3 seats_from_plan.py mekan-bloklar.csv -o mekan.venue.json \
       --venue-id tiyatro-x --name "..." --type theatre \
       --scene-kind splat --scene-url scene.splat \
       --tickets bilet-kodlari.csv --strict \
       --viewpoints viewpoints.csv --seats-csv koltuklar.csv
   ```
   - `--strict`: bilet sisteminde olup geometride olmayan veya tersi koltuk varsa durur → blok CSV'si düzeltilir.
   - Bloklar arası koltukları 0.30 m'den yakın ise uyarı verir (CSV hatası işareti).
   - Kısıtlı görüş: `--obstructed kisitli.csv` (`section,row,seat,severity,reason`; `*` ve `1-4` aralıkları) → `seat.obstructed`.
   - Tiyatro/konser salonu: `--type theatre` ile orijin otomatik `stage-front-center` (sahne ağzı ortası, Y=0 sahne döşemesi, +Z seyirciye). Hızlı başlangıç: `sablon-tiyatro-bloklar.csv`, `sablon-spor-salonu-bloklar.csv`.
   - Çıktıyı her zaman doğrula: `python3 validate_venue.py mekan.venue.json --warnings-as-errors`.
5. **Görsel doğrulama:** koltuk noktaları splat üzerinde görüntüleyicide gösterilir (web ekibinden "debug: koltukları göster" modu istenecek). Kabul: koltuk noktaları gerçek koltuk sırasından **≤ 30 cm** sapma; sabit fotoğraf noktalarında ölçülen lens konumu ile hesaplanan göz konumu farkı ≤ 30 cm.
6. Düzensiz salonlarda (eğri olmayan, değişken sıra) blok CSV'si yetmezse: blok başına birkaç koltuğun konumunu splat üzerinde ölçüp blok parametrelerini (cx, cz, startRadius, açılar) bunlara uydur; gerekirse bloğu daha küçük alt bloklara böl.

## 10. Kalite kontrol (yayın öncesi)

| Kontrol | Yöntem | Kabul |
|---|---|---|
| Gerçeğe benzerlik | Her sabit nokta için görüntüleyicide `viewpoint.eye`'den aynı yöne render al; 360 fotoğrafın aynı yönlü perspektif kesitiyle (`equirect_to_persp.py --views`) yan yana / %50 bindirme | Saha çizgileri, korkuluklar, kolonlar aynı yerde (≤ 1–2° açısal fark) |
| Ufuk ve dikeyler | Kolonlar/potalar dik mi | Eğim ≤ 0.5° |
| Ölçek | Saha uzunluğu görüntüleyicide ölçülür | Hata < %1 |
| Floater | Her blokta ön/orta/arka bakış | Bakış konisinde görünür floater yok |
| Delikler | Saha/sahne ve karşı tribün | Görünür delik yok; arka tribünlerde küçük kusur kabul |
| KVKK | Tüm sabit fotoğraflar + splat'ın yürüme rotaları | Tanınabilir kişi/yüz/plaka **sıfır** |
| Koltuk eşleme | Rastgele 20 koltuk: bilet kodu → görüntüleyici → telefon referans fotoğrafı | 20/20 doğru blok, sıra yönü, yaklaşık konum |
| Performans | Orta segment Android + iPhone | §8 hedefleri |
| Dosya | `venue.json` şema alanları, `ticketCode` benzersiz | Betik hatasız; web görüntüleyici yükleniyor |

QC raporu: `QC-<mekan>-<tarih>.md` — her maddenin sonucu, ekran görüntüleri, açık kusurlar.

## Ek: Betik özetleri
| Betik | Amaç | Bağımlılık |
|---|---|---|
| `extract_frames.py` | ffmpeg ile kare çıkarma | ffmpeg/ffprobe |
| `filter_blurry.py` | Laplacian varyansı, yüzdelik/eşik/pencere | numpy, opencv |
| `equirect_to_persp.py` | Equirect → perspektif ızgara, `views.json`, `cameras.txt` | numpy, opencv |
| `align_points.py` | Kontrol noktalarından ölçek/dönüş/öteleme (Umeyama) | numpy |
| `seats_from_plan.py` | Blok CSV → `venue.json` (v0.2), bilet eşleme, kısıtlı görüş, çekim planı | standart kütüphane |
| `validate_venue.py` | JSON Schema + mantıksal kontroller (id/ticketCode tekrarı, eye aralığı, kuaterniyon, viewpoint) | jsonschema |
| `pipeline.py` | Çekim klasörü → kareler → seçim → perspektif → yön bazlı eleme → `images/` + rapor + dry-run komutları | numpy, opencv, ffmpeg |
| `tests/run_tests.py` | Hepsinin sentetik uçtan uca testi | yukarıdakiler |
