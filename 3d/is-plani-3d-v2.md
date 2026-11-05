# 3D ve Çekim — İlk 12 Haftalık İş Planı (v2: Mac + bulut GPU)

Sürüm 2.0 · 31.10.2026 · Önceki: `is-plani-3d.md` (v0.1). Değişen görevler **(v2)** ile işaretli.
Kısaltmalar: kg = kişi-gün · [SAT] satış · [WEB] web ekibi · [YÖN] yönetim · [HUK] hukuk.

**v2 önerisi (kurucu onayı bekliyor):** Başlangıçta ayrı işleme bilgisayarı alınmadan başlanabilir. Mac'te ön işleme/önizleme/temizlik, bulutta (RunPod, saatlik) son eğitim. Ayrıntı: `isleme-duzeni-mac-bulut.md`.

| # | Hafta | Görev | Bağımlılık | Süre | Çıktı |
|---|---|---|---|---|---|
| 1 | 1 | **(v2)** Ekipman listesi onayı — iş istasyonu YOK; Mac yapılandırması (≥32 GB önerisi) ve bulut harcama limiti | [YÖN], `ekipman-ve-yazilim.md` v2 | 0.5 kg | Onaylı liste, aylık bulut bütçesi |
| 2 | 1 | Şema v0.2'nin web ekibince uygulanması takibi (rotationY derece, göz yüksekliği) | [WEB] | 0.5 kg | Uyum teyidi |
| 3 | 1–2 | **(v2)** Mac kurulumu: Homebrew, ffmpeg, COLMAP, Python ortamı, msplat, Brush (Rust derleme), Insta360 Studio; betik testleri Mac'te (`tests/run_tests.py`) | Mac, #1 | 1 kg | Çalışan Mac ortamı, kurulum notu |
| 4 | 2 | **(v2)** Bulut hesabı açılışı için gereksinim listesi (SSH anahtarı, 2FA, harcama uyarısı, Secure Cloud + Avrupa bölgesi) — hesabı yönetim açar | [YÖN] | 0.25 kg | Hesap kurulum kontrol listesi |
| 5 | 2 | Ofis/kampüs test çekimi (izin gerektirmeyen alan) — X5 ayar testleri | #3 | 1 kg | Test raporu |
| 6 | 2–3 | **(v2)** Test verisi: `pipeline.py` → Mac'te COLMAP → **msplat ve Brush önizleme karşılaştırması** (süre, bellek, kalite) | #5 | 1.5 kg | Önizleme aracı kararı; Mac'te SfM süre ölçümü |
| 7 | 3 | **(v2)** **İlk bulut koşusu**: `cloud/runpod_train.sh` ile RTX 4090'da splatfacto; imaj seçimi, bayrak doğrulaması (cloud/README "doğrulanacak" listesi), gerçek süre/ücret ölçümü | #4, #6 | 1 kg | Çalıştığı doğrulanmış betik, `maliyet-gunlugu.csv` ilk satırı |
| 8 | 3 | **(v2)** Önizleme (msplat) vs. bulut (splatfacto) kalite karşılaştırması aynı veride; gerekiyorsa 1 aylık Postshot Indie ile Windows bulut makinesinde 3. karşılaştırma | #7 | 1 kg | Araç zinciri kararı (varsayılan: ücretsiz zincir) |
| 9 | 3 | `isleme-rehberi.md`, `isleme-duzeni-mac-bulut.md` ve protokolde "doğrulanmadı/TAHMİN" maddelerinin güncellenmesi | #5–#8 | 1 kg | Belgeler v1.1 |
| 10 | 3–4 | **(v2)** Web entegrasyonu: test splat → SuperSplat → `align_points` → `ply_to_splat.py` → `splat_to_b64.py` → demo görüntüleyicide açılıyor; mobil boyut hedefi (`--max-splats`) | #7, [WEB] | 1.5 kg | Gerçek veriyle çalışan SplatScene |
| 11 | 3 | Demo mekânı adayları için çekim gereksinim listesi | [SAT] | 0.5 kg | Tek sayfa |
| 12 | 4 | Demo mekânı ön blok CSV'si (`sablon-tiyatro` / `sablon-spor-salonu` şablonundan), çekim planı, rota | Mekân seçimi [SAT] | 1 kg | `mekan-bloklar.csv`, `cekim-plani.csv` |
| 13 | 5 | **Demo çekimi** | #12, yazılı izin [SAT][HUK] | 1.5 kg | Ham veri, günlük, ölçümler, kısıtlı görüş listesi |
| 14 | 5–6 | **(v2)** Demo işleme: Mac'te pipeline + COLMAP (gece) + önizleme → bulutta 2–3 koşu → SuperSplat temizlik → hizalama | #13 | 3.5 kg | Temiz, hizalanmış splat; bulut gideri kaydı |
| 15 | 6 | Koltuk eşleme + `venue.json` (v0.2) + doğrulama | #14 | 1.5 kg | `demo.venue.json` |
| 16 | 6–7 | Demo QC (referans foto karşılaştırma, KVKK taraması, mobil performans) | #15, [WEB] | 2 kg | QC raporu, yayınlanabilir demo |
| 17 | 7 | **(v2)** Efor ve maliyet tablosu: Mac saatleri + bulut saatleri/$ (gerçek) → fiyatlandırma girdisi | #13–#16 | 0.5 kg | Mekân başı efor/maliyet |
| 18 | 7–8 | **(v2)** Otomasyon: Mac'te tek komut "paketle → yükle → pod'da çalıştır → indir" sarmalayıcısı (pod açma/kapama elle kalabilir); oturum sonu kontrol listesi (açık pod kalmasın) | #7 | 2 kg | `cloud/` betikleri v2 |
| 19 | 8 | Koltuk–splat sapma ölçümü (web hata ayıklama modu) | [WEB] | 1 kg | Sapma ≤ 30 cm |
| 20 | 8–9 | Pilot mekân ön keşif; büyük mekânsa **bölgeleme planı + bulut bütçesi** (arena ~$25–50 [TAHMİN]) | Pilot [SAT] | 1.5 kg | Keşif raporu |
| 21 | 9 | Drone ihtiyacı değerlendirmesi | #20, [HUK] | 1 kg | Karar notu |
| 22 | 9–10 | **Pilot çekim** | #20, izin | 2–3 kg | Ham veri |
| 23 | 10–11 | **(v2)** Pilot işleme: Mac'te SfM (büyükse pod'da `POSE_MODE=colmap` değerlendirmesi), bölgeli bulut eğitimi, gerçek bilet kodlarıyla eşleme (`--strict`) | #22, [SAT] | 6 kg | `pilot.venue.json`, splat dosyaları |
| 24 | 11–12 | Pilot QC + müşteri geri bildirimi | #23, [WEB] | 3 kg | QC raporu |
| 25 | 12 | **(v2)** Retrospektif: bulut gideri vs. yerel GPU eşiği ($250–300/ay) değerlendirmesi; protokol/rehber v1.0 | #24 | 1 kg | v1.0 belgeler, Q2 planı |

**Toplam:** ~38 kişi-gün (v0.1: ~40). İş istasyonu kurulumu (2 kg) yerine Mac kurulumu + bulut ilk koşusu (2 kg); araç karşılaştırması bulut parasıyla değil Mac önizlemesiyle yapılıyor.

## Kritik yol
Mac kurulumu (#3) → test çekimi (#5) → Mac önizleme (#6) → **ilk bulut koşusu (#7)** → web entegrasyonu (#10) → demo çekimi (#13, izin) → demo yayını (#16) → pilot (#22–24).

## Yeni riskler (v2)
| Risk | Etki | Önlem |
|---|---|---|
| Açık unutulan pod | Beklenmedik fatura | Harcama uyarısı/limit; oturum sonu kontrol listesi; betik sonu uyarısı |
| KVKK: yurt dışı bulut (avukat 11. soru cevapsız) | Müşteri verisini işleyememe | Cevaba kadar yalnız kişi içermeyen, iki kez kontrol edilmiş veri; Avrupa veri merkezi; gerekirse yerel GPU |
| Mac'te SfM çok yavaş (büyük mekân) | Takvim | Gece çalıştırma; görüntü bütçesi; bölgeleme; pod'da COLMAP |
| Bulut imajı/bağımlılık kırılması | Koşu başarısız, para kaybı | Sürüm sabitleme (`NS_VERSION`), `DRY_RUN`, ilk koşuda küçük `MAX_ITERS` |
| Yükleme hızı | Pod beklerken ücret | Pod açmadan paketleme; ağ diski seçeneği |
