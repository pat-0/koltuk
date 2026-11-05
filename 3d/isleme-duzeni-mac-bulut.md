# İşleme Düzeni: MacBook + Saatlik Bulut GPU

Sürüm 1.0 · 31.10.2026 · İlgili: `isleme-rehberi.md` (adımların ayrıntısı), `cloud/README.md` (pod içi), `ekipman-ve-yazilim.md` (v2)

**Öneri (kurucu onayı bekliyor):** Başlangıçta ayrı bir işleme bilgisayarı almadan başlanabilir. Çekim, ön işleme, önizleme ve temizlik **Apple Silicon MacBook**'ta; son kalite eğitim **saatlik kiralık NVIDIA GPU**'da yapılacak.

> İşaretler: **[TAHMİN]** = ölçülmemiş öngörü; ilk gerçek mekânda ölçülüp güncellenecek. *(doğrulanmadı)* = kaynaktan teyit edilmedi. Fiyatlar coordinatörün 31.10.2026'da doğruladığı listelerden.

---

## 1. Neresi ne yapar?

| # | Adım | Nerede | Araç | Not |
|---|---|---|---|---|
| 1 | .insv → equirect dışa aktarım | **Mac** | Insta360 Studio (macOS) | Uzun render; gece bırakılabilir |
| 2 | Kare çıkarma → seçim → 360→perspektif | **Mac** | `pipeline.py` | CPU; GPU gerekmez |
| 3 | Poz kestirimi (SfM) | **Mac** (varsayılan) veya bulut | COLMAP (CPU) | Mac'te ücretsiz ama yavaş; büyük mekânda buluta taşınabilir (§6) |
| 4 | **Hızlı önizleme eğitimi** | **Mac** | msplat (Metal) veya Brush (Metal/wgpu) | Kapsama/delik kontrolü; "buluta göndermeye değer mi?" kararı |
| 5 | **Son kalite eğitimi** | **Bulut** (NVIDIA) | nerfstudio splatfacto (gsplat) — `cloud/runpod_train.sh` | Saniye başı ücret; yalnız bu adım |
| 6 | Temizleme | **Mac** (tarayıcı) | SuperSplat | |
| 7 | Hizalama, .splat dönüşümü, base64 | **Mac** | `align_points.py`, `ply_to_splat.py`, `splat_to_b64.py` | |
| 8 | Koltuk eşleme, doğrulama | **Mac** | `seats_from_plan.py`, `validate_venue.py` | |

**İlke:** Bulutta yalnızca GPU'nun şart olduğu iş yapılır; pod'da beklenen her dakika paradır. Veri pod açılmadan önce paketlenir, pod iş biter bitmez kapatılır.

## 2. Mac kurulumu (bir kez, ~1–2 saat)

```bash
# Homebrew (yoksa): https://brew.sh
brew install ffmpeg colmap python@3.12 rustup-init git
# COLMAP Mac'te CUDA'sızdır: SIFT çıkarımı/eşleştirme CPU'da çalışır (Metal desteği yok — doğrulanmadı).
# GLOMAP (hızlı global SfM): Homebrew paketi var mı doğrulanmadı; yoksa kaynaktan derlenir
#   ya da yeni COLMAP sürümlerindeki global mapper kullanılır (sürüme bağlı — doğrulanmadı).

# Python ortamı (msplat tekerleri Python 3.12/3.13 için)
python3.12 -m venv ~/koltuk-venv && source ~/koltuk-venv/bin/activate
pip install numpy opencv-python-headless jsonschema "msplat[cli]"
msplat-train --help            # kurulum kontrolü (macOS 14+, Apple Silicon şart)

# Brush (Apache-2.0): GitHub sayfasında hazır macOS sürümü belirtilmiyor → kaynaktan derleme
rustup-init -y && source ~/.cargo/env          # Rust 1.88+
git clone https://github.com/ArthurBrussee/brush && cd brush && cargo build --release
./target/release/brush --help                   # CLI; --with-viewer ile arayüz de açılır
```
- Ayrıca: Insta360 Studio (macOS), bir tarayıcıda SuperSplat (kurulum yok), bu klasördeki betikler.
- **Postshot Mac'te çalışmaz** (Windows + NVIDIA şart). Opsiyonel olarak yalnızca Windows'lu bir bulut makinesinde kullanılabilir (§9).

## 3. Mac'te ön işleme ve poz

```bash
# 1) Equirect MP4'ler 01_adlandirilmis/V360/ altında, protokoldeki adlarla
python3 pipeline.py ~/Cekimler/2026-11-15_TYAT --fps 1 --window 3 --rel-threshold 0.4 \
        --pitches 0,30 --size 1600 --jobs 8
# → 10_isleme/images/, cameras.txt, rapor.md, komutlar.sh

# 2) COLMAP (CPU) — Mac'te
cd ~/Cekimler/2026-11-15_TYAT/10_isleme
F=$(awk '!/^#/{print $5","$6","$7","$8; exit}' cameras.txt)
colmap feature_extractor --database_path db.db --image_path images \
   --ImageReader.camera_model PINHOLE --ImageReader.single_camera 1 --ImageReader.camera_params "$F" \
   --SiftExtraction.use_gpu 0
colmap sequential_matcher --database_path db.db --SequentialMatching.overlap 20 --SiftMatching.use_gpu 0
mkdir -p sparse && colmap mapper --database_path db.db --image_path images --output_path sparse \
   --Mapper.ba_refine_focal_length 0 --Mapper.ba_refine_principal_point 0
```
**Görüntü bütçesi (önemli):** Eğitimde görüntüler belleğe alınır; 16 görünüm × binlerce kare kolayca 20.000+ görüntüye çıkar. Hedef: eğitim bölgesi başına **3.000–6.000 görüntü, 1600 px** [TAHMİN]. Ayar düğmeleri: `--fps` (0.5–1), `--window` (3–4), `--pitches 0,30` → `0` (8 görünüm/kare).

## 4. Mac'te hızlı önizleme (ücretsiz)

| Araç | Ne zaman | Komut |
|---|---|---|
| **msplat** (Apache-2.0, Metal) | Varsayılan önizleme; Python API ile otomatikleştirilebilir | `msplat-train 10_isleme -n 7000` *(veri klasörü olarak `images/` + `sparse/0` içeren COLMAP düzeni; tam yol düzeni doğrulanmadı)* — çıktı `.ply` (`export_ply`) |
| **Brush** (Apache-2.0, wgpu/Metal) | Eğitimi canlı izlemek, hızlı göz kontrolü | `brush 10_isleme --with-viewer` *(argümanlar `brush --help` ile doğrulanacak)* |

- Amaç **kalite değil karar**: Tribünlerde delik var mı, saha kenarı kopuk mu, poz kestirimi tüm rotaları birleştirdi mi? Sorun varsa ek çekim/ayar Mac'te, bulut parası harcamadan yapılır.
- Önizleme: düşük çözünürlük (msplat varsayılanı `num_downscales=2`), 5.000–7.000 adım. Süre: küçük salonda **20–60 dk** [TAHMİN, M-serisi Mac].
- msplat çıktısı da `.ply`: acil durumda (bulut erişimi yoksa) bu sonuç SuperSplat → web yoluna aynen girebilir; kalite daha düşük olur.

## 5. Veri yükleme / indirme

| Veri | Tipik boyut [TAHMİN] | Yön |
|---|---|---|
| `images/` (4.000 × 1600 px JPEG q95) | 2–4 GB | Mac → bulut |
| `sparse/0` (COLMAP) | 50–300 MB | Mac → bulut |
| Sonuç arşivi (`point_cloud.ply` + config + log) | 0,2–1 GB (1–4 M gauss × ~250 bayt) | bulut → Mac |
| Web için `.splat` (1,5 M gauss × 32 bayt) | ~48 MB; `.b64.txt` ~64 MB | Mac → web |

```bash
# Paketle (JPEG zaten sıkıştırılmış → tar yeterli, gzip zaman kaybı)
cd ~/Cekimler/2026-11-15_TYAT/10_isleme && tar -cf ~/yukle/TYAT.tar images sparse cameras.txt
shasum -a 256 ~/yukle/TYAT.tar > ~/yukle/TYAT.tar.sha256
# Pod'a gönder (RunPod "SSH over exposed TCP" açıkken; IP/port pod sayfasından)
rsync -avP -e "ssh -p <PORT> -i ~/.ssh/runpod_ed25519" ~/yukle/TYAT.tar* root@<IP>:/workspace/in/
# Sonucu al
rsync -avP -e "ssh -p <PORT> -i ~/.ssh/runpod_ed25519" root@<IP>:/workspace/out/ ~/Cekimler/2026-11-15_TYAT/20_bulut/
```
- Ev/ofis yükleme hızı 20–50 Mbit/s ise 3 GB ≈ 8–20 dk [TAHMİN]. **Pod bu sürede ücretlenir.** Seçenekler: (a) önce ucuz bir CPU pod'u/ağ diski ile yükleyip sonra GPU pod'unu aynı diske bağlamak *(RunPod ağ diski fiyatı ve iş akışı doğrulanmadı)*, (b) küçük işlerde doğrudan GPU pod'una yüklemek (4090'da 20 dk ≈ $0,30 — ayrı altyapı kurmaya değmeyebilir).
- RunPod `runpodctl send/receive` aracı da kullanılabilir *(ayrıntılar doğrulanmadı)*; `rsync` yarıda kesilirse kaldığı yerden devam ettiği için tercih edilir.

## 6. Bulutta bir oturum (adım adım)

1. **Hazırlık (Mac, pod KAPALI):** `TYAT.tar` + `.sha256` hazır; `cloud/runpod_train.sh` güncel; SSH anahtarı hesapta tanımlı.
2. **Pod aç:** RunPod → *Secure Cloud* → GPU: küçük salon **RTX 4090** (24 GB), büyük bölge/`splatfacto-big` **RTX 5090** veya **L40S** (48 GB). İmaj: CUDA *devel* içeren PyTorch şablonu. Disk: ≥ 50 GB. Bölge: §8.
3. **Bağlan, yükle:** `rsync` ile `TYAT.tar` ve `runpod_train.sh` → `/workspace/in/`; pod'da `sha256sum -c`.
4. **Çalıştır (tmux içinde, bağlantı koparsa iş sürsün):**
   ```bash
   tmux new -s egitim
   DATA_ARCHIVE=/workspace/in/TYAT.tar POSE_MODE=ready METHOD=splatfacto MAX_ITERS=30000 \
     RUN_NAME=TYAT_v1 bash /workspace/in/runpod_train.sh
   ```
   Önce `DRY_RUN=1` ile komutları gör. Büyük mekânda Mac'te COLMAP günler sürerse `POSE_MODE=colmap` (pod'da; ancak Ubuntu deposundaki COLMAP da CUDA'sız → CPU'lu güçlü pod gerekir).
5. **İzle:** `nvidia-smi`, `tail -f /workspace/is/log/egitim.log`. Takılırsa erken kes (pod parası sürüyor).
6. **İndir:** `/workspace/out/TYAT_v1_sonuc.tar.gz` → Mac; aç, `point_cloud.ply`'nin boyutu mantıklı mı kontrol et.
7. **Kapat:** Pod'u **Terminate** et (Stop değil; durdurulmuş pod'un diski de ücretlenebilir — doğrulanmadı). Ağ diski kullanıldıysa veri gerekmiyorsa sil (§8).
8. **Kaydet:** Pod türü, saat, ücret, adım süreleri (`ozet.txt`) → `maliyet-gunlugu.csv`.

## 7. Çıktı → web

```bash
# 1) SuperSplat (tarayıcı): point_cloud.ply aç → kırp, floater/insan izi sil → "PLY" olarak dışa aktar
#    (sıkıştırılmış .compressed.ply DEĞİL; ply_to_splat.py onu okumaz)
# 2) Kontrol noktalarıyla hizalama (isleme-rehberi §7)
python3 align_points.py kontrol-noktalari.csv --mode full --json hizalama.json
# 3) .ply → .splat (32 bayt/gauss; demo SplatMesh biçimi), venue koordinatlarına pişirilmiş
python3 ply_to_splat.py temiz.ply TYAT.splat --align-json hizalama.json --min-alpha 8 --max-splats 1500000
python3 ply_to_splat.py --inspect TYAT.splat          # sayı, sınır kutusu, kuaterniyon normu
# 4) Demo/artifact yayını için tek satır base64 (demo ".b64.txt" uzantısını atob ile çözer)
python3 splat_to_b64.py TYAT.splat --max-mb 40         # → TYAT.splat.b64.txt
# 5) venue.json: scene.kind "splat", format "splat", url "TYAT.splat.b64.txt", transform kimlik
python3 seats_from_plan.py tyat-bloklar.csv -o tyat.venue.json --type theatre --focus 0,1.2,-3 \
   --scene-kind splat --scene-format splat --scene-url TYAT.splat.b64.txt
python3 validate_venue.py tyat.venue.json --warnings-as-errors
```
- Hizalama `.splat` içine pişirildiği için `transform` kimlik kalır (önerilen yol). `--flip-yz`: hizalama yapmadan yalnız COLMAP'in Y-aşağı eksenini çevirip hızlı bakmak için.
- **Boyut:** `.splat` SH (görünüme bağlı renk) taşımaz; 1,5 M gauss ≈ 48 MB ikili, base64 ile ≈ 64 MB. Mobil hedefe (≤ 15–20 MB) inmek için `--max-splats 500000` (≈ 16 MB) ve bölgeleme; üretimde base64 yerine ikili `.splat` veya sıkıştırılmış format (SOG/SPZ) web ekibiyle kararlaştırılacak.
- `.splat` önem sırasına göre yazılır (büyük ve opak gauss'lar önce) → kesme (`--max-splats`) en az görsel kaybı verir.

## 8. Güvenlik ve KVKK

- **Kişisel veri:** Buluta yalnızca **kişi içermeyen** görüntüler yüklenir. Yükleme öncesi `images/` örneklenerek kontrol edilir (protokol §1.3; boş mekân şartı). Operatör yansıması, ekranlar, plakalar dâhil.
- **Yurt dışı aktarım:** Görüntüleri yurt dışındaki bir sunucuda işlemek, kişisel veri içerirse **KVKK m.9 (7499 sayılı Kanun ile değişik, 1 Haziran 2024)** kapsamına girer: yeterlilik kararı yoksa standart sözleşme ve imzadan sonra **5 iş günü içinde Kurum'a bildirim** gibi yükümlülükler gündeme gelir (bkz. `shared/dogrulama-notlari.md`). Kişi içermeyen görüntülerde durumun ne olduğu **avukat soru dosyasındaki 11. soru** (`satis/avukat-soru-dosyasi.md`) ile soruldu — **cevap gelene kadar buluta yalnızca kendi test çekimlerimiz ve kişi içermediği iki kez kontrol edilmiş mekân verisi yüklenir.** Müşteri sözleşmesine "işleme için yurt dışı bulut altyapısı kullanılabilir" maddesi eklenmesi değerlendirilmeli.
- **Bölge:** RunPod'un Avrupa veri merkezi var (ör. `EU-RO-1`, bölge `EUROPE`; ülke dokümanda belirtilmiyor — doğrulanmadı). **Türkiye bölgesi bulunamadı (doğrulanmadı).** Lambda'nın AB bölgesi var mı doğrulanmadı. Varsayılan: RunPod Secure Cloud, Avrupa veri merkezi.
- **Sağlayıcı türü:** RunPod *Community Cloud* ve Vast.ai makineleri üçüncü kişilere ait sunuculardır → müşteri verisi için **kullanılmaz**; yalnızca kendi test verimiz için (Vast.ai kesintiye açık örnekleri %50+ ucuz).
- **Teknik önlemler:** Yalnız SSH anahtarı (parola yok); veri yalnız şifreli kanaldan (rsync/ssh); pod işi bitince **Terminate**; ağ diski ve sonuç arşivi pod'da bırakılmaz; ham `.insv` ve 360 fotoğraflar asla yüklenmez (yalnız seçilmiş perspektif kareler); hesapta 2FA; harcama limiti/uyarısı tanımlı.

## 9. Maliyet

**Fiyatlar (31.10.2026, saatlik, saniye başı faturalama — RunPod):** RTX 4090 $0,89 · RTX 5090 $1,19 · L40S $1,09 · A100 $1,79 · H100 $2,89–3,99. Lambda: A100 40GB $1,99, H100 $3,99. Vast.ai piyasa fiyatlı.

**Oturum süresi [TAHMİN — ilk gerçek koşuda ölçülecek]:**

| Kalem | Küçük salon (tiyatro/üniversite, 3–6 bin görüntü) | Spor salonu (2–3 bin koltuk) | Arena (~12 bin, 4–6 bölge) |
|---|---|---|---|
| Pod açılış + kurulum (pip, gsplat derleme) | 15–25 dk | 15–25 dk | 15–25 dk × bölge (aynı pod'da sırayla: 1 kez) |
| Yükleme (pod açıkken) | 10–20 dk | 15–30 dk | 1–2 sa |
| Eğitim splatfacto 30k adım | 30–60 dk | 45–90 dk | bölge başı 1–2 sa → 5–10 sa |
| Dışa aktarım + indirme | 5–10 dk | 10 dk | 30–60 dk |
| **Toplam / koşu** | **~1–2 sa** | **~1,5–2,5 sa** | **~8–14 sa** |
| GPU | RTX 4090 | RTX 4090 / 5090 | L40S / RTX 5090 |
| **Koşu başı ücret** | **~$1–2** | **~$1,5–3** | **~$9–17** |
| Deneme sayısı (parametre/temizlik turu) | 2–3 | 2–3 | 2–3 |
| **Mekân başı bulut gideri** | **~$3–6** | **~$4–9** | **~$25–50** |

- Mac'te COLMAP ve önizleme ücretsizdir ama zaman alır: küçük salon birkaç saat, arena 1–2 gün (gece çalıştırma) [TAHMİN].
- Karşılaştırma: ~$3.000–4.500'lük bir işleme bilgisayarının parası, yukarıdaki tahminlerle **yüzlerce küçük salon / ~100 arena koşusuna** eşdeğer → ayda 1–3 mekân için bulut açıkça daha ucuz. **Yeniden değerlendirme eşiği:** aylık bulut gideri sürekli $250–300'ü aşarsa veya veri yurt dışına çıkarılamazsa (KVKK cevabı) yerel GPU satın alınması tekrar düşünülür.
- Gizli maliyetler: ağ diski depolaması (doğrulanmadı), başarısız koşular, unutulan açık pod (en büyük risk → hesapta harcama uyarısı + oturum sonu kontrol listesi).

## 10. Postshot (opsiyonel)

Postshot yalnızca **Windows + NVIDIA** çalışır. Ticari kullanım için **Indie €17/ay (€204/yıl)**; komut satırı/otomasyon ve AprilTag hizalama için **Studio €468/yıl**. Mac düzeninde ancak Windows'lu bir bulut makinesinde (uzak masaüstü) kullanılabilir; bu kurulum doğrulanmadı. Öneri: ücretsiz zincir (msplat/Brush + splatfacto) ilk demoda yetersiz kalırsa 1 aylık Indie ile karşılaştırma testi.

## 11. Lisans özeti (ticari kullanım)

| Araç | Lisans | Ticari kullanım |
|---|---|---|
| nerfstudio / gsplat (splatfacto) | Apache-2.0 | Evet |
| Brush | Apache-2.0 | Evet |
| msplat | Apache-2.0 | Evet |
| SuperSplat | MIT | Evet |
| COLMAP | BSD tipi *(doğrulanmadı)* | Evet *(doğrulanmadı)* |
| Inria orijinal 3DGS kodu | Ticari olmayan lisans | **Hayır** — kullanılmaz |
| LichtFeld Studio | GPLv3 (+ NVIDIA) | Dahili araç olarak mümkün; dağıtımda GPL yükümlülükleri — gerekirse hukuk |
| Postshot Free | — | **Hayır**; Indie/Studio evet |

## Kaynaklar
- Postshot fiyat/plan: https://activation.jawset.com/shop/pricing/ · https://radiancefields.com/postshot-launches-v1-0-out-of-beta
- Brush: https://github.com/ArthurBrussee/brush · msplat: https://pypi.org/project/msplat/
- RunPod fiyatları: https://www.runpod.io/pricing · veri merkezi listesi (`runpodctl datacenter`): https://docs.runpod.io/runpodctl/reference/runpodctl-datacenter
- Lambda fiyatları: https://lambda.ai/pricing
- KVKK m.9 değişikliği: `shared/dogrulama-notlari.md` (kaynak: https://www.erdem-erdem.av.tr/bilgi-bankasi/kisisel-verilerin-korunmasi-kanununda-neler-degisti)
