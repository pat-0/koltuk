# Ekipman ve Yazılım (v2: MacBook + saatlik bulut GPU)

Sürüm 2.0 · 31.10.2026 · Önceki sürüm: `ekipman-ve-yazilim-v1.md` (ayrı işleme bilgisayarı varsayımı)

Fiyatlar USD veya EUR, vergi hariç; Türkiye fiyatları farklıdır. **Bu belge satın alma kararı değildir ve hiçbir satın alma yapılmadı.**

Durum işaretleri:
- ✅ kaynakla doğrulandı
- ⚠️ ikincil kaynak
- ❓ doğrulanmadı veya tahmin

**v2'deki değişiklik:** Öneri (kurucu onayı bekliyor): başlangıçta ayrı bir işleme bilgisayarı **alınmadan** başlanabilir. Ön işleme, önizleme ve temizlik mevcut veya alınacak bir **Apple Silicon MacBook**'ta yapılacak. Son kalite eğitim için **saatlik kiralık NVIDIA GPU** kullanılacak. Zincirin tamamı ücretsiz ve ticari kullanıma açık araçlarla kurulabiliyor; Postshot opsiyonel. Ayrıntılı akış `isleme-duzeni-mac-bulut.md` dosyasında.

---

## 1. Minimum başlangıç seti

| Kalem | Öneri | Fiyat | Durum | Not |
|---|---|---|---|---|
| 360 kamera | Insta360 X5 | $549,99 (Essentials $659,99) | ✅ [1] | |
| Batarya, kart, çubuk, ayak, lazer metre, gri kart, şerit metre | v1 §1'deki gibi | ~$300–550 | ❓ | Bu kalemlerde v1'den değişiklik yok |
| Harici SSD | 2 TB × 2 (biri yedek) | ~$240–360 | ❓ | Mac'in dahili diski ham veriye yetmez |
| **İşleme makinesi** | **Apple Silicon MacBook** (mevcut veya son model). Önerilen yapılandırma: **≥ 32 GB birleşik bellek, ≥ 1 TB** | — | ❓ | COLMAP CPU'da, msplat/Brush Metal'de çalışır. Bellek önizleme eğitimini sınırlar: 16 GB'ta önizleme ancak düşük çözünürlükte mümkün [TAHMİN] |
| ~~GPU iş istasyonu~~ | **Alınmayacak** | ~~$2.500–4.500~~ | — | Yerine saatlik bulut GPU (§3) |
| **Toplam ilk yatırım (Mac hariç)** | | **~$1.100–1.500** | ❓ | v1'de iş istasyonu dahil ~$3.600–5.800 tutuyordu |

## 2. Yazılım ve lisanslar

| Yazılım | Nerede | Kullanım | Fiyat | Lisans / ticari kullanım | Durum |
|---|---|---|---|---|---|
| Insta360 Studio | Mac | Dikiş, equirect | Ücretsiz | Üretici yazılımı; EULA okunmadı | ❓ |
| ffmpeg, numpy, OpenCV, jsonschema | Mac | Betiklerimiz | Ücretsiz | LGPL/GPL, BSD, Apache, MIT; dağıtmıyoruz | ⚠️ |
| COLMAP | Mac (CPU), gerekirse bulut | Poz kestirimi | Ücretsiz | BSD tipi *(doğrulanmadı)* | ❓ |
| **msplat** | Mac (Apple Silicon, macOS 14+, Metal) | Hızlı önizleme eğitimi; COLMAP, Nerfstudio ve Polycam veri setlerini okur; `.ply` çıktısı verir | Ücretsiz | **Apache-2.0**, ticari kullanıma açık | ✅ [2] |
| **Brush** | Mac, Windows, Linux | Önizleme ve görsel kontrol; COLMAP ve Nerfstudio verisini okur | Ücretsiz | **Apache-2.0**, ticari kullanıma açık. macOS için hazır sürüm belirtilmiyor, Rust ile derleniyor | ✅ [3] |
| **nerfstudio splatfacto / gsplat** | Bulut (NVIDIA) | Son kalite eğitim (`cloud/runpod_train.sh`) | Ücretsiz | **Apache-2.0**, ticari kullanıma açık | ✅ (coordinatör doğrulaması) |
| SuperSplat | Mac (tarayıcı) | Temizleme | Ücretsiz | MIT | ⚠️ |
| Kendi betiklerimiz (`ply_to_splat.py`, `splat_to_b64.py` vb.) | Mac | Web dönüşümü | — | Şirket içi | — |
| RealityScan 2 | Windows *(macOS desteği doğrulanmadı)* | Opsiyonel poz kestirimi | Ciro $1M altıysa ücretsiz, üstündeyse $1.250/koltuk/yıl | | ✅ [v1-5] |
| **Postshot (opsiyonel)** | **Yalnız Windows + NVIDIA** (Mac'te çalışmaz) | Alternatif eğitim (GUI) | Free: ticari değil. **Indie €17/ay (€204/yıl)**: ticari. **Studio €468/yıl**: CLI ve AprilTag | | ✅ [4][5] |
| Kullanılmayacak | | | | Inria orijinal 3DGS kodu **ticari değil**. LichtFeld Studio GPLv3 ve NVIDIA gerektiriyor; dahili araç olarak ancak hukuk görüşüyle | ✅ (coordinatör) |
| Polycam | Bulut | | Pro ~$150/yıl ⚠️ | Veri yurt dışı buluta gidiyor; ücretsiz zincir varken **gerekli değil** | ⚠️ |

## 3. Bulut GPU (saatlik, kullandıkça öde)

| Sağlayıcı | GPU | $/saat | Not | Durum |
|---|---|---|---|---|
| RunPod | RTX 4090 (24 GB) | 0,89 | **Varsayılan**: küçük ve orta mekân | ✅ [6] |
| RunPod | RTX 5090 | 1,19 | Büyük bölgeler | ✅ [6] |
| RunPod | L40S (48 GB) | 1,09 | `splatfacto-big` ve VRAM gerektiren işler | ✅ [6] |
| RunPod | A100 / H100 | 1,79 / 2,89–3,99 | Gerekmesi beklenmiyor | ✅ [6] |
| Lambda | A100 40GB / H100 | 1,99 / 3,99 | Yedek sağlayıcı | ✅ [7] |
| Vast.ai | Piyasa fiyatı | Kesintiye açık örnekler %50'den fazla ucuz | Yalnız kendi test verimiz için (üçüncü kişilere ait sunucular) | ✅ (coordinatör) |

RunPod saniye başı ücretlendiriyor. Müşteri verisi yalnızca **Secure Cloud** ve Avrupa veri merkezinde işlenecek (ör. `EU-RO-1`; ülkesi doğrulanmadı). Türkiye bölgesi bulunamadı. KVKK açısından bkz. `isleme-duzeni-mac-bulut.md` §8 ve avukat soru dosyasındaki 11. soru.

## 4. Maliyet tablosu

Tahmin işareti olan değerler ilk gerçek mekânda ölçülecek.

| Kalem | Tutar | Not |
|---|---|---|
| İlk ekipman (kamera seti, SSD, ölçüm) | ~$1.100–1.500 | Mac hariç |
| Yazılım (zorunlu) | **$0** | msplat, Brush, nerfstudio, COLMAP, SuperSplat |
| Yazılım (opsiyonel) | Postshot Indie €204/yıl; bir aylık deneme €17 | Yalnız ücretsiz zincir yetmezse; Windows'lu bulut makinesi gerekir |
| Bulut: küçük salon | ~$3–6 / mekân [TAHMİN] | Her koşu 1–2 saat RTX 4090, 2–3 koşu |
| Bulut: spor salonu | ~$4–9 / mekân [TAHMİN] | |
| Bulut: arena (~12 bin) | ~$25–50 / mekân [TAHMİN] | Her koşu 8–14 saat L40S/5090, 2–3 koşu |
| Bulut: aylık (2–3 mekân) | ~$10–100 [TAHMİN] | Ayrıca ağ diski depolaması (fiyatı doğrulanmadı) |
| **Yeniden değerlendirme eşiği** | Bulut gideri ayda sürekli $250–300'ü aşarsa | Ya da KVKK cevabı yurt dışı işlemeyi engellerse yerel GPU (v1 §1) yeniden düşünülür |

## 5. Sonraki aşama ekipmanı

v1 §3'teki liste geçerli: ikinci X5, DJI Mini 5 Pro veya operatör kiralama, aynasız fotoğraf makinesi, LiDAR, NAS. Bunlara iki ek seçenek eklendi:

- **Yerel NVIDIA iş istasyonu:** yalnız yukarıdaki eşik aşılırsa.
- **Windows'lu bulut masaüstü (Postshot için):** yalnız karşılaştırma testinde, saatlik.

## 6. Açık sorular
1. Avukat soru dosyası, 11. soru: kişi içermeyen görüntüleri yurt dışı buluta yüklemek KVKK m.9 kapsamına giriyor mu?
2. RunPod'un Avrupa veri merkezi hangi ülkede, AB içinde mi? Ağ diski fiyatı ne? (doğrulanmadı)
3. COLMAP'in Mac'teki hızı ve GLOMAP'in Homebrew ile kurulup kurulamadığı (doğrulanmadı). Arena ölçeğinde Mac'te SfM kaç saat sürer?
4. Mac belleği: msplat/Brush önizlemesi 16 GB ile 32 GB arasında ne kadar fark ediyor?

## Kaynaklar
1. Insta360 X5 ABD fiyatı: https://www.techradar.com/cameras/360-cameras/insta360-x5-review
2. msplat: https://pypi.org/project/msplat/
3. Brush: https://github.com/ArthurBrussee/brush
4. Postshot fiyat ve planları: https://activation.jawset.com/shop/pricing/
5. Postshot v1.0: https://radiancefields.com/postshot-launches-v1-0-out-of-beta
6. RunPod fiyatları: https://www.runpod.io/pricing · veri merkezleri: https://docs.runpod.io/runpodctl/reference/runpodctl-datacenter
7. Lambda fiyatları: https://lambda.ai/pricing
- v1 kaynakları (B&H, RealityScan, DJI, SHGM notları): `ekipman-ve-yazilim-v1.md`
