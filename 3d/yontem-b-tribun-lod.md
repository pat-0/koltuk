# Yöntem B: Tribün parçalı model + akışlı detay (Spark 2.0)

*05.11.2026 · Durum: **Öneri — karar Sencer'de.** Yöntem A (mevcut plan: `cekim-protokolu.md`, `isleme-rehberi.md`, `isleme-duzeni-mac-bulut.md`) geçerliliğini koruyor; bu belge onu silmez, yanına alternatif koyar.*

## 1. Tek cümlede fark

| | Yöntem A (mevcut) | Yöntem B (bu belge) |
|---|---|---|
| Model | Mekânın tamamı tek splat dosyası | Oturma planındaki **her tribün ayrı splat**, tarayıcıda tek mekânda birleşir |
| Web gösterimi | Kendi yazdığımız splat çizici (three.js r128), dosyanın tamamı indirilir | **Spark 2.0** (World Labs, MIT lisansı): yakın yer yüksek detay, uzak yer düşük detay; detay parça parça indirilir |
| Telefon sınırı | Toplam dosya boyutu (büyük mekânda aşılır) | Her karede çizilen splat sayısı (cihaza göre 500 bin – 2,5 milyon); toplam mekân büyüklüğü sınır değil |
| Kullanıcı deneyimi | Genel bakış ↔ koltuk | Genel bakış ↔ koltuk + **seçilen koltuklar ve tribünler arasında akıcı geçiş** |
| Uygun mekân | Küçük–orta salon (BGM, Yalova) | Her boy; stadyumda (Erzincan) neredeyse zorunlu |

## 2. Kullanıcı deneyimi (kurucunun tarifi)

Serbest "rota üzerinde gezinti" değil, **seçimler arası geçiş**:

1. Kullanıcı bir koltuk seçer → kamera o koltuğa uçar, oturan göz hizasından bakar.
2. Sepetteki / karşılaştırılan diğer koltuğa geçer → kamera iki koltuk arasında akıcı biçimde uçar.
3. Başka bir tribünü seçer → o tribün yüksek detayla yüklenir, önceki düşük detaya iner.
4. Geçiş sırasında görüntü bozulmasın diye kamera, çekimde gerçekten geçilen hatlara yakın bir yay izler (saha kenarı, koridorlar).

Mevcut demo 1–2'yi zaten yapıyor (`GL.flyTo`). Yöntem B ile bu, gerçek çekimden gelen ve tribün tribün akan bir sahnede çalışır.

## 3. Çekim (Yöntem A'dan farkları)

- **Tribün = çekim parçası.** Her tribün kendi rotalarıyla çekilir (ön koridor, merdivenler, arka koridor, oturma yüksekliğinde sıra geçişleri) ve günlükte tribün koduyla işaretlenir.
- **Bağlantı rotaları:** Tribünleri birbirine bağlayan saha çevresi turu ve koridor geçişleri zorunlu. Parçaların aynı koordinat sisteminde hizalanması ve geçiş animasyonlarının temiz görünmesi bunlara bağlı.
- **Kontrol noktaları her tribünde:** Her tribünde en az 2 ölçülmüş hedef işaret (A4) görünmeli; birleştirmede kayma olmasın.
- Süre: Yöntem A ile hemen hemen aynı; bağlantı rotaları için +30–60 dk tahmin.

## 4. İşleme

1. Tüm çekimden kamera konumları **tek seferde** hesaplanır (ortak koordinat sistemi).
2. Her tribün için ayrı splat eğitilir (kendi kareleri + komşu bağlantı rotaları). Paralel eğitilebilir; bulut GPU süresi toplamda A'ya yakın.
3. Saha/sahne ve çatı ayrı bir parça olabilir.
4. Her parça Spark'ın `build-lod` aracıyla akışlı `.RAD` dosyasına çevrilir.
5. Parçaların sınırlarındaki taşmalar kırpılır (SuperSplat vb.).

Not: Inria'nın 2024 SIGGRAPH yöntemi (büyük sahneyi parçalarda eğitip birleştirme) bu fikrin akademik karşılığı; lisansı ticari kullanım için **kontrol edilmedi**. Aynı mantık açık lisanslı araçlarla (gsplat/nerfstudio + Spark build-lod) kurulabilir.

## 5. Web

- Görüntüleyiciyi Spark 2.0'a taşımak: three.js **r128 → r179+** yükseltmesi gerekir (Spark 2.x şartı). Tahmini iş: birkaç gün.
- Mevcut özellikler (koltuk seçimi, kalabalık modu, seviye karşılaştırma, gömme/postMessage) korunur; Spark normal three.js nesneleriyle aynı sahnede çalışıyor.
- Yakın koltuk/korkuluk için "temiz 3D model + uzak splat" karma çözümü Spark'ta da uygulanabilir.
- `venue.json` şemasına tribün → dosya eşlemesi eklenir (öneri: `scene.parts[] = {id, sectionIds[], url}`); şema sürümü v0.3 olur.

## 6. Bilinmeyenler (deneme çekiminde ölçülecek)

- [ ] Parça sınırlarında dikiş/renk farkı görünüyor mu?
- [ ] Orta segment Android ve iPhone 13'te geçiş akıcı mı (hedef ≥ 30 fps)?
- [ ] İlk görüntü kaç saniyede geliyor (mobil veri, soğuk tarayıcı)?
- [ ] Tribünler arası uçuşta bozulma var mı?
- [ ] `.RAD` dosyalarını nereden sunacağız (CDN), maliyeti?

## 7. Hazırlık işleri (Sencer onaylarsa)

1. Demoyu Spark 2.0'a taşıyan bir dal (`yontem-b`), Yöntem A demosu bozulmadan.
2. Örnek arenanın sentetik splat'ını tribün tribün bölüp `.RAD`'a çeviren script.
3. Telefon test sayfası: tribün değiştirme + iki koltuk arası geçiş + akıcılık ölçümü.
4. Çekim protokolüne "Yöntem B eki" (bağlantı rotaları, tribün kodlu günlük).

## 8. Sencer için karar soruları

1. Görüntüleyiciyi Spark 2.0'a taşıyalım mı, yoksa kendi çizicimize parçalı yükleme mi ekleyelim?
2. Yalova/BGM gibi küçük salonlarda da B mi, yoksa yalnız stadyumlarda mı?
3. Parça sınırı oturma planındaki tribün mü, yoksa daha büyük gruplar (ör. "kuzey kale arkası") mı?
4. Deneme çekimini her iki yönteme de uygun çekelim mi (öneri: evet; ek süre ~30 dk)?

## Kaynaklar

- World Labs, Spark 2.0 teknik yazısı: https://www.worldlabs.ai/blog/spark-2.0
- Spark (GitHub, MIT): https://github.com/sparkjsdev/spark
- Spark 2.0 tanıtım videosu (World Labs, 40 sn): https://www.youtube.com/watch?v=BpzKZnV0MQc
- Akışlı LOD anlatımı (Olli Huttunen, 17 dk): https://www.youtube.com/watch?v=N4VfC9qsWuc
- Inria, A Hierarchical 3D Gaussian Representation for Very Large Datasets (2024): https://arxiv.org/abs/2406.12080
- Swyvl, cihaz bazında splat sınırları: https://swyvl.io/blog/best-gaussian-splat-viewers/
