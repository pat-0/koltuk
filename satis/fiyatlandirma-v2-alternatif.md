# [Ürün adı]: Fiyatlandırma v2 (Alternatif): Platform Ücreti Olmayan Bilet Şirketi Kanalı

*Hazırlanma: 31.10.2026 · `fiyatlandirma.md` (v1) üzerine yazılmamıştır; v1'in Seçenek C'sine alternatif olarak sunulur.*
*İşaretler: **[V]** = varsayım (doğrulanmadı) · Kur: 1 USD = 50 TL (v1 §1, 21.10.2026 serbest piyasa 49,61 TL esas alınarak yuvarlandı)*

---

## 0. Neden v2?
Kurucunun değerlendirmesi: bilet şirketinden mekân ücretlerine ek olarak ayrı bir **$20–40 bin/yıl platform lisansı** istemek, ürünü henüz kanıtlanmamışken yüksek ve mantıksız. Şu gerekçeler bu değerlendirmeyi destekliyor:
- **Değer mekânda ve bilet satışında oluşuyor**, SDK'nın kendisinde oluşmuyor. Bilet şirketi, kullanılmayan bir mekân için ödeme yapmak istemez.
- **Ölçüm verisi yok.** Rakipler de bağımsız dönüşüm verisi yayımlamıyor (v1 §6). Yüksek sabit ücret, ilk "evet"i zorlaştırır.
- **Pazar yoğun.** Futbolda fiilen Passo var; konserde Biletix, Bubilet, iTicket ve Passo var. İlk 1–2 bilet şirketi anlaşması, fiyattan daha değerli bir kanal kazanımıdır.

**v2'nin ilkesi:** Bilet şirketi **yalnızca canlı olan mekânlar için** ödeme yapar. Ödeme iki biçimde olabilir: indirimli kurulum ve sabit lisans, ya da bilet başı ücret (yıllık asgari ve tavanla). Hacim büyüdükçe birim fiyat düşer. Platform anlaşması ancak **5–10 mekân** eşiğinden sonra ve yalnızca belirli koşullarda konuşulur.

---

## 1. Kanal fiyat listesi (bilet şirketi üzerinden satılan mekânlar)

Kademeler v1 ile aynıdır: S ≤3.000 · M 3.001–15.000 · L 15.001–35.000 · XL 35.001+.

### 1.1 Kurulum (mekân başı, tek seferlik)
| Kademe | v1 liste (USD) | **v2 kanal (USD)** | **v2 kanal (TL)** | Kural |
|---|---|---|---|---|
| S | 2.500–4.000 | **2.200–3.200** | 110.000–160.000 | Taban $2.200. Doğrudan maliyet ~$1.800–2.100 **[V]**, altına inilmez. |
| M | 5.000–9.000 | **3.500–6.300** (−%30) | 175.000–315.000 | |
| L | 10.000–16.000 | **7.000–11.200** (−%30) | 350.000–560.000 | |
| XL | 16.000–28.000 | **11.200–19.600** (−%30) | 560.000–980.000 | |

### 1.2 Lisans: iki seçenek (mekân başı; bilet şirketi seçer)

**Seçenek L1: Sabit yıllık lisans (−%35)**
| Kademe | v1 liste (USD/yıl) | **v2 kanal (USD/yıl)** | **TL/yıl** |
|---|---|---|---|
| S | 2.000–3.500 | **1.300–2.300** | 65.000–115.000 |
| M | 4.000–8.000 | **2.600–5.200** | 130.000–260.000 |
| L | 8.000–14.000 | **5.200–9.100** | 260.000–455.000 |
| XL | 14.000–24.000 | **9.100–15.600** | 455.000–780.000 |

**Seçenek L2: Bilet başı ücret (yıllık asgari + tavan)**
- **Birim:** Koltuk görünümünün etkin olduğu etkinliklerde, bilet şirketinin o mekân için sattığı **her numaralı bilet** başına **$0,03 (1,5 TL)**. Önerilen aralık $0,02–0,05 **[V]**.
- **Neden "her bilet"?** v1'de ücret yalnızca "görünüm açılan oturumda satılan bilet" içindi. Bunu ölçmek, bilet şirketiyle oturum eşlemesi gerektirir ve faturalamada anlaşmazlık doğurur. "Etkin etkinlikteki her bilet" modeli bilet şirketinin kendi satış raporuyla doğrulanabilir. Birim fiyatın düşük tutulması bu kapsam genişliğini dengeler.
- **Yıllık asgari:** Kademenin L1 alt sınırının %60'ı.
  - S: $780
  - M: $1.560
  - L: $3.120
  - XL: $5.460
- **Yıllık tavan:** Kademenin L1 üst sınırının 1,5 katı.
  - S: $3.450
  - M: $7.800
  - L: $13.650
  - XL: $23.400
- **Faturalama:** Çeyreklik, bilet şirketinin satış raporuna göre yapılır. Asgari tutarın dörtte biri her çeyrek peşin alınır.
- **Kombine ve sezonluk biletler:** 1 kombine = [10] bilet sayılır **[V]**, ya da kombineler kapsam dışı bırakılır. Müzakere konusu.

**L2 örnek hesaplar** (tümü **[V]**: etkinlik sayısı ve doluluk varsayımdır):
| Mekân tipi | Varsayım | Yıllık bilet | $0,03 ile | Asgari/tavan sonrası |
|---|---|---|---|---|
| Tiyatro (S, ~2.000 koltuk) | 150 gösteri × %60 doluluk | 180.000 | $5.400 | **$3.450** (tavan) |
| Arena (M, ~5.000) | 60 etkinlik × %70 | 210.000 | $6.300 | **$6.300** |
| Büyük stadyum (XL, ~50.000) | 17 lig iç saha maçı × ~42.000 ort. seyirci (Galatasaray 2025–26 ort. 41.661, [Fanatik](https://www.fanatik.com.tr/goztepe/tribunde-lider-goztepe-2624431)) | ~708.000 (kombine dahil sayım **[V]**) | $21.240 | **$21.240** |
| Küçük salon (S, ~800) | 80 konser × %50 | 32.000 | $960 | **$960** |

### 1.3 Hacim kademeleri (bilet şirketinin canlı mekân sayısına göre)
| Bilet şirketindeki canlı mekân | Kurulum | Lisans (L1) / bilet başı ücret (L2) |
|---|---|---|
| 1–4 | Kanal fiyatı (§1.1) | Kanal fiyatı |
| 5–9 | Ek −%5 | Ek −%10 (L2 birim: $0,027) |
| 10–19 | Ek −%10 | Ek −%20 (L2 birim: $0,024) |
| 20+ | Platform anlaşması müzakeresi (§2) | |

- Kademe, takvim yılı başında veya yeni mekân canlıya alındığında güncellenir. Geriye dönük iade yapılmaz.
- **Kesin sınırlar (v1 §7 geçerli):**
  - Toplam indirim liste fiyatının %45'ini aşamaz.
  - Kurulum doğrudan maliyetin altına inemez.

### 1.4 Ek koşullar
- **Münhasırlık:** v2'de varsayılan olarak yoktur. Talep edilirse §2'deki platform anlaşmasında ve yalnızca hacim taahhüdüyle konuşulur.
- **Kanal çatışması:** Mekân bilet şirketi üzerinden geldiyse, o mekâna doğrudan v1 fiyatıyla teklif verilmez. Mekân birden çok bilet şirketiyle satış yapıyorsa, **model bir kez üretilir**. Her ek bilet şirketi yalnızca kendi lisansını öder; kurulum ücreti ikinci kez alınmaz.
- **Bilet şirketinin yeniden satışı:** Bilet şirketi mekâna kendi fiyatıyla yeniden satabilir ya da ücreti bilet hizmet bedeline yansıtabilir. Bu bilet şirketinin kararıdır.

---

## 2. Platform anlaşması: ne zaman ve hangi koşulda konuşulur?

**Tetikleyiciler.** Aşağıdaki koşulların **ilki ve en az biri daha** sağlanmalıdır:
1. Bilet şirketinde **en az 5 canlı mekân** ya da **10 imzalı mekân** var. *(Zorunlu)*
2. En az **2 mekânda** pilotta tanımlanan başarı ölçütü tuttu ve ölçüldü.
3. Bilet şirketi şunlardan birini istiyor:
   - (a) SDK'yı kendi koltuk haritasına yerel entegre etmek,
   - (b) ileri beyaz etiket özelleştirmesi,
   - (c) %99,9 SLA ve 7/24 destek,
   - (d) segment münhasırlığı,
   - (e) kendi ekibinin model güncellemelerini yapabilmesi.

**Platform anlaşmasının biçimi (öneri; ayrı platform ücreti zorunlu değildir):**
- **Kurumsal toplu lisans:** O ana kadarki mekân lisanslarının yıllık toplamından **−%10–15**. Tek fatura, yıllık peşin ödeme.
- **Yeni mekânlar:** Sabit kurulum fiyatı (kademe başına sabit tutar) ve toplu lisansa otomatik ekleme.
- **Ek hizmetler ayrıca fiyatlanır.** Ayrı ücret yalnızca bilet şirketinin talep ettiği ek değerler için alınır. Bunlar özel geliştirme (adam-gün), yüksek SLA ve münhasırlıktır.
  - **Münhasırlık primi:** Toplu lisansın +%25–50'si. En fazla 12 ay, yıllık asgari mekân sayısı taahhüdüyle.
- **Yıllık asgari taahhüt:** Platform indirimi karşılığında bilet şirketi yıllık asgari tutar veya mekân sayısı taahhüt eder.

---

## 3. v1 ile v2 karşılaştırması

| Boyut | v1 (Seçenek C) | **v2 (alternatif)** |
|---|---|---|
| Bilet şirketinden ayrı platform ücreti | $20–40 bin/yıl | **Yok** (5–10 mekân eşiğinden sonra isteğe bağlı) |
| Mekân başı kurulum | Liste −%25–35 | Liste −%30 (S için taban $2.200) |
| Mekân başı lisans | Liste −%30–40 | Liste −%35 (L1) **veya** bilet başı ücret (L2) |
| Hacim teşviki | Paketler (5/15/sınırsız) | Canlı mekân sayısına göre kademeli ek indirim |
| Bilet şirketinin ilk yıl riski | Yüksek (mekân canlı olmasa da platform ücreti) | **Düşük** (yalnızca canlı mekân için ödeme) |
| Bizim gelir öngörülebilirliği | Yüksek (sabit ücret) | Orta (L2'de asgari ve tavanla sınırlı dalgalanma) |
| Satış döngüsü | Uzun (bütçe onayı gerekir) | **Kısa** (mekân bazında küçük kararlar) |
| Kanal çatışması | Paket kotası nedeniyle düşük | Kurallarla yönetilir (§1.4) |

**Örnek: 5 mekânlı bilet şirketi** (2×S, 2×M, 1×L; aralık ortaları; **[V]**)
| | v1 Seçenek C | v2 (L1 sabit lisans) |
|---|---|---|
| Platform ücreti | $30.000 | $0 |
| Kurulum toplamı | $23.450 | $23.085 (5–9 mekân kademesi: ek −%5) |
| Yıllık lisans toplamı | $18.525 | $16.695 (5–9 mekân kademesi: ek −%10) |
| **1. yıl toplam** | **$71.975 (~3,6 M TL)** | **$39.780 (~1,99 M TL)** |
| **2. yıl toplam** | **$48.525** | **$16.695** |

**Yorum:** v2'de 1. yıl geliri ~%45 daha düşük, 2. yıl geliri belirgin şekilde daha düşük. Ancak v1'in sabit ücreti, büyük olasılıkla ilk anlaşmayı hiç gerçekleştirmeyecek bir engel. v2'de gelir **mekân sayısıyla** büyür. 10. mekândan sonra §2'deki kurumsal toplu lisans ve ek hizmetlerle öngörülebilirlik geri kazanılır.

---

## 4. Öneri
1. **Bilet şirketleri için varsayılan model v2 olsun.** İlk görüşmelerde platform ücreti hiç gündeme getirilmesin.
2. **İlk anlaşmada L1 (sabit lisans) önerilsin;** L2 (bilet başı ücret) ikinci seçenek olarak dursun. Erken dönemde sabit gelir ve basit faturalama daha değerli. L2, nakit akışını gelire bağlamak isteyen bilet şirketleri (ör. Bubilet tipi hızlı büyüyenler) için kullanılsın.
3. **Pilot koşulları v1 §5 ile aynı kalsın.** Pilot sonrası fiyat v2 kanal listesinden yazılsın. Lansman indirimi (−%30) kanal fiyatının üzerine **eklenmesin**; kanal fiyatı zaten indirimli.
4. **Platform anlaşması** yalnızca §2'deki tetikleyicilerle ve "ek değer karşılığı ek ücret" ilkesiyle konuşulsun.
5. **Doğrudan mekân satışında** v1 Seçenek A (liste fiyatı) geçerli kalsın.
6. **Geri bildirimle güncelleme:** İlk 3 bilet şirketi görüşmesinden sonra L2 birim fiyatı ($0,03) ve asgari/tavan oranları gözden geçirilsin.

## 5. Varsayımlar ve açık sorular
- **[V]** Doğrudan maliyet, ekip günü (~$300) ve barındırma maliyetleri v1 §2'den alındı; sahada doğrulanmadı.
- **[V]** Etkinlik sayıları ve doluluk oranları (L2 örnekleri) varsayımdır. Stadyum örneğindeki seyirci ortalaması kaynaklıdır, ancak bilet adedi ile seyirci sayısı aynı değildir: kombine ve davetiyeler var.
- **Bilinmiyor:** Bilet şirketlerinin hizmet bedeli marjı. L2 birim fiyatının bilet şirketi marjının ne kadarına denk geldiği bu yüzden hesaplanamadı. Görüşmelerde sorulmalı.
- **Bilinmiyor:** Kombine biletlerin bilet şirketi raporlarında nasıl sayıldığı.
- Kur riski: USD fiyat ve TL fatura kuralı v1 §1'deki gibidir.
