# [Ürün adı] — Fiyatlandırma Modeli (Taslak v1)

*Hazırlanma: 31 Ekim 2026 · Hazırlayan: Satış ve iş geliştirme · Durum: iç kullanım, ilk müşteri görüşmeleriyle güncellenecek*

---

## 0. Özet

- **Önerilen ana model:** tek seferlik **kurulum ücreti** + **yıllık lisans**, mekânın **kapasite kademesine** göre.
- **Bilet şirketleri için:** yıllık **platform lisansı** (SDK/beyaz etiket) + mekân başına **indirimli** kurulum ve lisans.
- **Gelir paylaşımı:** yalnızca seçenek olarak sunulur; her zaman **yıllık asgari tutarla** birlikte.
- **Pilot:** 1 mekân, 90 gün. Kurulum ücretsiz ya da maliyetine; karşılığında **satış verisini ölçme hakkı** ve **referans hakkı** alınır.
- **Rakip fiyatları kamuya açık değil.** 3D Digital Venue, Pacifa3D ve Ticketmaster Virtual Venue sitelerinde fiyat yok; ikisi yalnızca "demo talep edin" diyor. Bulunan dolaylı fiyat sinyalleri §6'da.

---

## 1. Kur varsayımı

| Kaynak | Tarih | USD/TL |
|---|---|---|
| Serbest piyasa satış ([İşçi Haber](https://www.iscihaber.net/ekonomi/21-ekim-2026-dolar-ve-euro-fiyatlari-ne-kadar-oldu/273708)) | 21.10.2026, 14:40 | 49,61 |
| Aynı sayfanın canlı kur tablosu (sayfaya 31.10.2026'da bakıldı) | 31.10.2026 | 49,95 |

**Planlama kuru: 1 USD = 50 TL.** Aşağıdaki TL tutarları bu kurla yuvarlanmıştır.

**Faturalama kuralı:** Sözleşmede fiyat USD olarak yazılır. Faturaya fatura tarihindeki TCMB döviz satış kuruyla TL olarak yansıtılır. TL sabit fiyat istenirse yıllık lisans 6 ayda bir TÜFE ile güncellenir. KDV hariçtir.

---

## 2. Maliyet tabanı (fiyatın alt sınırı)

> Ekipman ve gün sayıları önceki araştırmadan gelir. **Günlük ekip maliyeti ve barındırma tutarları bizim varsayımımızdır, doğrulanmadı.**

| Kalem | Varsayım |
|---|---|
| Başlangıç ekipmanı (360° kamera + yazılım) | $750–2.000 (önceki araştırma) |
| İşleme bilgisayarı | $2.500–4.000 (önceki araştırma, doğrulanmadı) |
| Ekipman amortismanı | 24 ayda ~20 mekân varsayımıyla mekân başına ~$150–300 |
| Yüklü ekip günü (maaş + yol + yazılım) | **~$300/gün (varsayım)** |
| Barındırma/CDN (splat dosyaları) | **~$20–150/ay/mekân (varsayım; trafiğe bağlı)** |

**Mekân başına doğrudan iş maliyeti (tahmin):**

| Kademe | Çekim | İşleme/düzenleme | Entegrasyon/QA | Toplam gün | Maliyet (USD) |
|---|---|---|---|---|---|
| S (≤3.000 koltuk) | 1 | 3–4 | 2 | 6–7 | ~$1.800–2.100 |
| M (3.001–15.000) | 1–2 | 5–7 | 3 | 9–12 | ~$2.700–3.600 |
| L (15.001–35.000) | 2 | 7–9 | 3–4 | 12–15 | ~$3.600–4.500 |
| XL (35.001+ stadyum) | 2–3 | 8–10 | 4 | 14–17 | ~$4.200–5.100 |

**Kural:** Kurulum fiyatı doğrudan maliyetin en az **~1,8 katı** olmalı. Böylece satış, proje yönetimi ve yeniden çekim riski karşılanır. Yıllık lisans; barındırma, destek, sezonluk küçük güncellemeler (sahne düzeni değişikliği gibi) ve ürün geliştirmeyi taşır.

---

## 3. Fiyat modeli seçenekleri

### Seçenek A: Kurulum + yıllık lisans, kapasite kademeli (ÖNERİLEN, varsayılan)

| Kademe | Örnek mekân | Kurulum (USD) | Kurulum (TL) | Yıllık lisans (USD) | Yıllık lisans (TL) |
|---|---|---|---|---|---|
| **S** ≤3.000 | CRR (860), Bostancı GM (2.500), CSO Ada ana salon (2.023), AKM opera (~2.040) | 2.500–4.000 | 125.000–200.000 | 2.000–3.500 | 100.000–175.000 |
| **M** 3.001–15.000 | Harbiye (3.972), Volkswagen Arena (4.500–5.800), Ankara Arena (10.400), Ülker (13.800) | 5.000–9.000 | 250.000–450.000 | 4.000–8.000 | 200.000–400.000 |
| **L** 15.001–35.000 | Sinan Erdem (16.000), Göztepe (23.376), Samsun (34.346) | 10.000–16.000 | 500.000–800.000 | 8.000–14.000 | 400.000–700.000 |
| **XL** 35.001+ | Papara Park, Tüpraş, Chobani, RAMS Park | 16.000–28.000 | 800.000–1.400.000 | 14.000–24.000 | 700.000–1.200.000 |

**Kapsam:**
- Lisans; barındırma, yerleşik görüntüleyici (embed/SDK), temel analitik paneli, yılda 1 küçük güncelleme ve e-posta desteğini kapsar. Desteğe yanıt süresi 1 iş günüdür.
- Ek alanlar ayrı fiyatlanır: loca/VIP/hospitality alanları, soyunma odası turu gibi pazarlama amaçlı alanlar.
- Ek sahne düzenleri de ayrı fiyatlanır, örneğin arenada 360° sahne düzeni ile uç sahne düzeni.
- Ek düzen ücreti, kademenin kurulum ücretinin %25–40'ı kadardır.

### Seçenek B: Gelir paylaşımı (isteğe bağlı, yıllık asgari tutarla)

Bu seçenek, nakit bütçesi sınırlı ama satış hacmi yüksek mekânlar içindir.
- **Bilet başına mikro ücret:** satılan her bilet için $0,05–0,15 (2,5–7,5 TL). Bilet şirketi ile mekân aralarında paylaşabilir.
- Ücret yalnızca, koltuk görünümünün açıldığı oturumlarda satılan biletler için alınır. Bu, analitikte ölçülür.
- **Yıllık asgari tutar** = ilgili kademenin yıllık lisansının alt sınırı.
- **Tavan** = kademe lisansının üst sınırının 2 katı. Tavan, müşterinin "başarı cezası" itirazını önler.
- Kurulum ücreti gelir paylaşımında da alınır. Mekân isterse, kurulum %50'ye kadar ilk 12 aya yayılabilir.
- **Artış payı** (premium kategori artışından %3–5 pay) **ilk aşamada önerilmez.** Artışı ölçmek için A/B düzeni ve güven gerekir. Yalnızca pilotu başarıyla tamamlamış müşteriyle konuşulur.

### Seçenek C: Bilet şirketleri için platform / çoklu mekân lisansı

| Bileşen | Fiyat (USD) | Fiyat (TL) | Not |
|---|---|---|---|
| Yıllık platform lisansı (beyaz etiket SDK, marka özelleştirme, analitik API, SLA) | 20.000–40.000 | 1.000.000–2.000.000 | Bilet şirketinin hacmine göre |
| Mekân başı kurulum | Kademe fiyatından **%25–35 indirim** | | Bilet şirketi mekânı getirir ve faturalar |
| Mekân başı yıllık lisans | Kademe fiyatından **%30–40 indirim** | | |
| Paketler | **Başlangıç:** 5 mekân · **Büyüme:** 15 mekân · **Kurumsal:** sınırsız (özel teklif) | | Paket içindeki mekân kotası 12 ay içinde kullanılır |

- **Münhasırlık** varsayılan olarak yoktur. Kategori münhasırlığı istenirse platform lisansına **+%25–50** eklenir. Örneğin "Türkiye'de futbol biletlemesinde 12 ay yalnız sizinle".
- Münhasırlığın en fazla 12 ay sürmesi ve hacim taahhüdüne bağlanması önerilir.
- Bilet şirketi mekâna kendi fiyatıyla yeniden satabilir. Bizim mekâna doğrudan teklifimiz, aynı mekânda bilet şirketi kanalıyla çakışmamalıdır. Bu kural kanal çatışması yaşanmaması içindir.

### Seçenek D: Etkinlik bazlı (tek seferlik; istisna)

Festival veya tek konser için kurulumun %60'ı, 3 ay barındırma dahildir. Bu seçenek yalnızca **karar hızını artırmak** için sunulur ve kalıcı lisansa dönüşüm hedeflenir.

---

## 4. Gerekçe

### 4.1 Maliyet tabanı
S kademesinin alt sınırı $2.500, doğrudan maliyetin (~$2.000) biraz üzerindedir. Bu sınırın altına yalnızca pilot ve referans müşteride inilir. M ve üstü kademeler, maliyetin yaklaşık 1,8–4 katı arasındadır.

### 4.2 Değer argümanı (örnek hesap; iddia değil, senaryo)
- **Kaynak:** [TGRT Haber](https://www.tgrthaber.com/aktuel/tarkan-konseri-kac-bilet-satildi-3264846). Tarkan'ın Volkswagen Arena'daki 4 konserinde bilet fiyatları ~7.000–32.000 TL idi. Satılan bilet tahmini ~26.000–30.000. Kaynağın kendi kapasite rakamları tutarsız.
- **Senaryo:** Ortalama bilet fiyatını **12.000 TL** varsayalım (bizim varsayımımız). 20.000 bilet × 12.000 TL ≈ **240 milyon TL (~$4,8 M)** brüt satış eder, üstelik yalnızca 4 gecede.
- Koltuk görünümü dönüşümü veya üst kategoriye geçişi bu satışın yalnızca **%0,5'i** kadar artırsa, artış ≈ **1,2 milyon TL (~$24.000)** olur. Bu tutar M kademesinin yıllık lisansının (≤$8.000) yaklaşık 3 katıdır.
- Rakiplerin yayımlanmış bir dönüşüm oranı yok. Ticketmaster dönüşümü artırdığını yalnızca sözle söylüyor ([Tottenham duyurusu](https://www.tottenhamhotspur.com/news/1009794/club-becomes-first-in-the-uk-to-launch-ticketmasters-3d-virtual-venue-technology)). Bu yüzden **pilotta kendi verimizi üretmek** fiyatın meşruiyeti için kritik.

### 4.3 Pazar ödeme gücü sinyali
2026–27 Süper Lig kombine fiyatları 3.000 TL (Başakşehir) ile 275.000 TL (Galatasaray 1. kategori, Trabzonspor VIP Platinum) arasında değişiyor ([CNBC-e, 24.08.2026](https://www.cnbce.com/spor-ekonomisi/super-ligde-kombine-yarisi-en-pahali-275-bin-en-ucuz-3-bin-tl-h35682)). Pahalı koltuklarda "ne göreceğim?" sorusu satın alma kararının merkezinde.

---

## 5. Pilot teklifi (standart)

| Madde | Teklif |
|---|---|
| Kapsam | 1 mekân, 1 sahne düzeni, tüm numaralı oturma blokları. Mekân S veya M kademede olmalı; XL stadyumda yalnızca 1 tribün. |
| Süre | **90 gün** canlı yayın. En az 3 etkinlik veya 8 hafta açık satış dönemi. |
| Ücret | **Kurulum ücretsiz** (referans değeri yüksek mekân/bilet şirketi) **ya da maliyet karşılığı $1.000–1.500 (50.000–75.000 TL)**. Pilot boyunca lisans ücreti alınmaz. |
| Karşılığında (zorunlu) | (1) Toplu ve anonim satış ve etkileşim metriklerini ölçme hakkı, mümkünse A/B testi. (2) İsim, logo ve vaka çalışması hakkı. Bunlar onay sürecine tabidir; ayrıntılar pilot sözleşme taslağında. |
| Başarı ölçütü (önceden yazılı) | Örnek: koltuk görünümünü açan oturumlarda satın alma oranı, açmayanlara göre ≥ +%X; üst kategori payı ≥ +Y puan. X ve Y pilot başında birlikte belirlenir. |
| Pilot sonrası | Önceden yazılı fiyatla yıllık sözleşme. **Lansman müşterisi indirimi** ilk yıl kurulum ve lisansta %30'dur. Pilotta ödenen tutar ilk yıla **mahsup edilir.** |
| Çıkış | Başarı ölçütü tutmazsa müşteri cezasız çıkar. 3D model bizde kalır; ayrıntılar sözleşmenin fikri mülkiyet maddesinde. |

**Pilot sayısı sınırı:** İlk 12 haftada en fazla **3 ücretsiz pilot.** Sonrasında yalnızca maliyet karşılığı pilot yapılır.

---

## 6. Rakip fiyatları ve kamuya açık sinyaller

| Rakip | Kamuya açık fiyat | Bulunan sinyal | Kaynak |
|---|---|---|---|
| 3D Digital Venue (eski adı Ticketing 3D) | **Yok** ("Schedule a demo") | 2015 cirosu ~€500 bin, 2016 hedefi €1,3 M. O dönem müşterileri arasında Barça, Man City, Wembley, Twickenham vardı ve ekip 25 kişiydi. Twickenham'da 10 yıllık £9.000'lık koltukların satışına destek verdiler ve toplam £27 M satış oldu (o satışa etkileri belirtilmemiş). 2020'de "17 ülkede 400+ müşteri" iddiası. | [Via Empresa 2016](https://www.viaempresa.cat/via-empresa-in-english/ticketing-3d-conquers-sport_19631_102.html), [Sports Venue Business 2020](https://sportsvenuebusiness.com/2020/07/18/3d-digital-venue-3ddv/) |
| Pacifa3D | **Yok** | Müşteri testimonyalarında satış ve dönüşüm artışı deniyor, rakam yok. | [pacifa3d.com](https://pacifa3d.com/) |
| Ticketmaster 3D Virtual Venue / IOMEDIA | **Yok** | Ticketmaster'ın "premium products" paketinde, müşteriye özelleştirilen ücretli ek ürün izlenimi veriyor. IOMEDIA bazı takımlarda "aktif kullanıcı ~%40 arttı" diyor. | [SportBusiness 2022](https://gameday.sportbusiness.com/2022/09/ticketmasters-3d-virtual-venue-offers-a-view-of-the-future/) |
| seats.io (2D koltuk haritası; doğrudan rakip değil) | **Var:** Capterra'ya göre Basic plan **€35'ten** başlıyor ("özellik başına/aylık") | Koltuk haritası SaaS'ı için alt fiyat çıpası. Bizim ürün bunun üzerine 3D gerçek görüntü ekliyor. | [Capterra](https://www.capterra.com/p/166839/seats-io/) |
| Rukkus Seat360 (B2C, 2016) | — | Seat360 açık mekânlarda ~%40 daha uzun görüntüleme ve 3 kat ekran/oturum iddiası. | [Hypergrid Business](https://hypergridbusiness.com/2016/05/ticket-vendor-says-vr-brings-in-the-dough) |

**Sonuç:** Doğrudan rakip fiyatı bilinmiyor. Önerilen aralıklar **maliyet tabanı ve değer senaryosundan** türetildi. İlk 5 görüşmede fiyat tepkisi kaydedilip §3 güncellenecek.

---

## 7. İndirim kuralları

| Kural | İndirim | Not |
|---|---|---|
| Lansman müşterisi (ilk 3 imzalı sözleşme, referans hakkı şartıyla) | İlk yıl %30 | Pilot indirimiyle birleşmez, yerine geçer |
| Çok yıllı taahhüt | 2 yıl: lisansta %10 · 3 yıl: lisansta %15 | Yıllık peşin ödeme koşulu |
| Çoklu mekân (aynı işletmeci) | 3–5 mekân: %15 · 6+ mekân: %25 | Kurulum ve lisansta |
| Peşin ödeme (yıllık lisans tek seferde) | %5 | |
| Kamu kurumu / kâr amacı gütmeyen kültür kurumu | %10 | Referans hakkı şartıyla |

**Kesin sınırlar:**
1. Toplam indirim, liste fiyatının **%45'ini** geçemez. Ücretsiz pilot bunun dışındadır.
2. Kurulum fiyatı hiçbir koşulda **doğrudan maliyetin altına** inemez. S kademesinde taban $2.000.
3. %30'u aşan indirimler kurucu onayı gerektirir ve gerekçesi CRM'e yazılır.
4. İndirimin karşılığında mutlaka bir şey alınır: süre, hacim, peşin ödeme ya da referans. "Karşılıksız indirim" yapılmaz.
5. Sözleşmede indirim, liste fiyatının altında ayrı bir satır olarak gösterilir. Yenilemede liste fiyatı esas alınır.

---

## 8. Açık sorular / doğrulanacaklar
- Günlük ekip maliyeti ve barındırma maliyetleri. İlk pilotta gerçek değerler ölçülecek.
- Bilet şirketlerinin hizmet bedeli yapısı (gelir paylaşımı seçeneğinin tabanı). Kamuya açık bir kaynak bulunamadı.
- Ticketmaster Virtual Venue'nun Biletix'te kullanılıp kullanılmadığı doğrulanmadı.
- Stadyumlarda (XL) çekim süresi; 2–3 gün varsayımı doğrulanmadı.
