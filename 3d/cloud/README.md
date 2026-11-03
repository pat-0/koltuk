# cloud/: saatlik GPU pod'unda splat eğitimi

Uçtan uca akışın tamamı `../isleme-duzeni-mac-bulut.md` dosyasında anlatılıyor. Bu dosya yalnızca pod içinde yapılacakları kapsar.

## Dosyalar
| Dosya | Ne işe yarar |
|---|---|
| `runpod_train.sh` | Pod'da çalışır ve sırasıyla şunları yapar: GPU kontrolü → bağımlılık kurulumu → veri açma → poz (`ready` ya da `colmap`) → `ns-process-data` → `ns-train splatfacto` → `ns-export gaussian-splat` → tek arşiv (`*_sonuc.tar.gz`). |

## Girdi paketi (Mac'te hazırlanır)
```
TYAT.tar
  images/       pipeline.py çıktısı (perspektif JPEG)
  sparse/0/     COLMAP modeli (POSE_MODE=ready için)
  cameras.txt   PINHOLE iç parametreleri
```
Paketi oluşturmak için: `tar -cf TYAT.tar images sparse cameras.txt`. Bu komut `10_isleme/` klasöründe çalıştırılır.

## Parametreler (ortam değişkeni)
| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `DATA_ARCHIVE` | `/workspace/in/veri.tar` | Girdi dosyası (`.tar`, `.tar.gz`, `.zip`) ya da bir klasör |
| `WORK`, `OUT_DIR` | `/workspace/is`, `/workspace/out` | Çalışma ve çıktı klasörleri |
| `RUN_NAME` | tarih_saat_splat | Çıktı arşivinin adı |
| `POSE_MODE` | `ready` | `ready`: Mac'teki `sparse/0` kullanılır. `colmap`: pod'da COLMAP çalışır (apt sürümü CPU'da çalışır, yavaştır). |
| `COLMAP_MATCHER` | `sequential` | Seçenekler: `sequential` ya da `exhaustive` |
| `METHOD` | `splatfacto` | Büyük sahne için `splatfacto-big` (24 GB'tan fazla VRAM gerekebilir; doğrulanmadı) |
| `MAX_ITERS` | `30000` | Hızlı deneme için 7000 |
| `DOWNSCALE` | `1` | 2 verilirse görüntüler yarı çözünürlükte işlenir (hızlı deneme) |
| `KEEP_COORDS` | `1` | nerfstudio'nun otomatik yönlendirme, merkezleme ve ölçeklemesini kapatır, böylece .ply COLMAP koordinatlarında kalır. Bayrak adları doğrulanmadı. |
| `NS_VERSION` | boş | Sürüm sabitlemek için, ör. `==1.1.5` |
| `DRY_RUN` | `0` | `1` verilirse komutlar yalnızca yazdırılır, çalıştırılmaz |

## Pod'da çalıştırma
```bash
tmux new -s egitim
DRY_RUN=1 DATA_ARCHIVE=/workspace/in/TYAT.tar bash /workspace/in/runpod_train.sh    # önce komutları gözden geçir
DATA_ARCHIVE=/workspace/in/TYAT.tar RUN_NAME=TYAT_v1 bash /workspace/in/runpod_train.sh
# Çıktı: /workspace/out/TYAT_v1_sonuc.tar.gz → Mac'e rsync ile indir, ardından pod'u TERMINATE et
```

## Durum ve bilinen belirsizlikler
- **Test durumu:** Bu ortamda GPU yok. Betik `bash -n`, `shellcheck` ve `DRY_RUN` akışından geçti; gerçek bir pod'da henüz çalıştırılmadı. İlk gerçek koşuda doğrulanacak noktalar:
  1. **İmaj:** Hangi RunPod PyTorch/CUDA imajı `pip install nerfstudio` ve gsplat derlemesiyle sorunsuz çalışıyor?
  2. **`ns-process-data` bayrakları:** `--skip-image-processing` ve mutlak yol olarak `--colmap-model-path` beklendiği gibi çalışıyor mu?
  3. **Veri ayrıştırıcı bayrakları:** `--orientation-method none`, `--center-method none` ve `--auto-scale-poses False` bu sürümde geçerli mi?
  4. **Bellek:** Görüntüler belleğe alındığında RAM ve VRAM yetiyor mu? Yetmezse `DOWNSCALE=2` ile ya da daha az görüntüyle denenir.
- **Koordinatlar:** `KEEP_COORDS=1` ile dışa aktarılan `.ply` COLMAP koordinatlarında olmalıdır; bu varsayım doğrulanmadı. Hizalama her durumda Mac'te `align_points.py` ve `ply_to_splat.py --align-json` ile yapılır. `dataparser_transforms.json` dosyası da arşive eklenir, böylece gerekirse ters dönüşüm hesaplanabilir.
- **Alternatif:** gsplat'in kendi `examples/simple_trainer.py` betiği COLMAP klasörünü doğrudan okur. nerfstudio kurulumu sorun çıkarırsa bu yol denenecek; komut satırı doğrulanmadı.
