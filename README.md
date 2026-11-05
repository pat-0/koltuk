# Koltuktan Görünüm

Hyperbaric'in "koltuğundan sahayı/sahneyi gör" ürünü için çalışma deposu. Ürün, bilet şirketlerinin ve mekânların bilet ekranına beyaz etiketli eklenti olarak giriyor. Görüntüler mekânın gerçek çekiminden (360° kamera + Gaussian splatting) üretiliyor.

> Durum (3 Kasım 2026): Hazırlık aşaması. Gerçek çekim henüz yapılmadı; demodaki sahneler kodla üretilmiş örnek veri. Demo mekânı, fiyat modeli, işleme düzeni ve ekip kararları kurucuda.

## Canlı sayfalar (yalnızca sahibine açık, paylaşmak için Paylaş menüsü)

| Sayfa | Ne |
|---|---|
| [Koltuktan Saha Görünümü](https://claude.ai/artifact/NKDbx2pmtrDYtYBMpAVvSW) | Satış demosu: 5 örnek mekân, koltuk görünümü, beyaz etiket, analitik paneli, akıcılık testi, seviye karşılaştırma |
| [Biletra Etkinlik Sayfası](https://claude.ai/artifact/GRmSDJ9m5iSXsur66htB13) | Kurgusal bilet sitesine gömülü görüntüleyici; seçilen koltuk sepete düşüyor |
| [Koltuktan Görünüm Proje Paketi](https://claude.ai/artifact/KdtJNaB2BonUt7vQkifBk6) | 18 slaytlık özet sunum (kaynağı `docs/sunum/`) |

## Klasörler

```
shared/   Ortak veri formatı (venue.json şeması v0.1 ve v0.2) ve doğrulama notları
3d/       Çekim protokolü, işleme rehberleri, ekipman listesi, iş planları
          Betikler: extract_frames, equirect_to_persp, filter_blurry, seats_from_plan,
          align_points, validate_venue, pipeline, ply_to_splat, splat_to_b64
          cloud/    Bulutta (RunPod) eğitim betiği
          tests/    Test paketi (python3 3d/tests/run_tests.py)
web/      demo.html (Artifact olarak yayınlanan sayfa), viewer.html (iframe için tam sayfa),
          etkinlik.html + embed.js (örnek bilet sitesi), data/ (örnek mekânlar ve splat),
          README-teknik.md, iş planı
satis/    Hedef liste ve takip tablosu (xlsx), fiyatlandırma (v1 ve platform ücretsiz v2),
          teklifler, itiraz-yanıt, görüşme dosyaları (Bubilet, Passo, Biletinial),
          mekân dosyaları ve erişim planı, rakip araştırması, hukuki taslaklar,
          avukat soru dosyası (md + docx)
docs/     Sunum kaynağı, çatı kesme açıklama görseli, seçilmiş ekran görüntüleri
```

## Sık kullanılan komutlar

```bash
# 3D betik testleri
python3 3d/tests/run_tests.py

# venue.json doğrulama
python3 3d/validate_venue.py 3d/ornek-arena.venue.json

# demo.html değiştikten sonra iframe sayfasını yeniden üret
node web/build-viewer.js

# Yeni bir .ply çıktısını demoya hazırlama
python3 3d/ply_to_splat.py girdi.ply cikti.splat
python3 3d/splat_to_b64.py cikti.splat web/data/ornek.splat.b64.txt
```

## Önemli notlar

- Hukuki belgelerin hepsi **taslaktır**; avukat incelemesinden önce kullanılmaz.
- `web/screens/` (test ekran görüntüleri, ~46 MB) ve ikili `web/data/ornek.splat` depoya alınmadı.
- Hedef listede kişi adı veya kişisel iletişim bilgisi yok; yalnızca kurum düzeyinde bilgi.
- Fiyatlar, maliyet tahminleri ve bulut gideri doğrulanmamış varsayımlar içerir; ilgili belgelerde işaretli.
