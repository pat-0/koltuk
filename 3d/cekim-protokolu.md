# Çekim Protokolü — "Koltuğundan Gör" 3D/360 Çekimi

Sürüm 0.1 · Sahibi: 3D ve çekim sorumlusu · Kamera: Insta360 X5
İlgili belgeler: `isleme-rehberi.md`, `ekipman-ve-yazilim.md`, `shared/venue-schema.md`

> İşaretler: **[Z]** zorunlu · **[Ö]** önerilen · *(doğrulanmadı)* = üretici belgesinden veya sahada teyit edilmedi; ilk test çekiminde doğrulanacak.

---

## 0. Özet: bir çekim günü neden oluşur?

| Çıktı | Amaç | Yöntem |
|---|---|---|
| **A. Sabit 360 fotoğraf noktaları** | Web'de "bu koltuktan gerçek görüntü" ve kalite kontrol referansı; `venue.json → viewpoints` | Tripod/ışık ayağı, oturan göz yüksekliği, 72 MP fotoğraf |
| **B. Yürüyüş videoları** | Gaussian splat sahnesinin ham verisi (tüm salonun 3D'si) | Elde/çubukta 8K 360 video, yavaş ve sistematik rotalar |
| **C. Ölçümler ve kontrol noktaları** | Sahneyi metre ölçeğine ve venue koordinatlarına hizalamak; blok CSV'sini doğrulamak | Lazer metre, şerit metre, saha çizgileri, fotoğraf |
| **D. Referans fotoğraflar** | Kalite kontrol (splat render ile karşılaştırma), blok/sıra/koltuk numaralarının kanıtı | Telefon, normal fotoğraf |

---

## 1. Çekimden önce (T-14 gün → T-1 gün)

### 1.1 İzinler ve yazışmalar **[Z]**
- [ ] Mekân yönetiminden **yazılı çekim izni** (tarih, saat aralığı, erişilecek alanlar, çekim amacı: ticari bilet ekranı görselleştirmesi). Kimseyle doğrudan iletişime satış/iş geliştirme ekibi geçer; bu protokol yalnız neyin istenmesi gerektiğini listeler.
- [ ] İzin metninde **ticari kullanım ve yayın hakkı** açıkça yer alıyor (görüntülerin bilet şirketinin/mekânın web sitesinde yayınlanması). Hukuk teyidi: *(açık soru — hukuk danışmanı)*.
- [ ] Mekân içi **marka/sponsor logoları, reklam panoları, sanat eserleri** için kısıt var mı? (Bazı mekânlarda sponsor görünürlüğü sözleşmeyle düzenlenir.) Gerekirse panolar sonradan bulanıklaştırılır veya boş/nötr içerikle çekilir.
- [ ] **Güvenlik/teknik sorumlu** adı, telefonu; çekim boyunca bir mekân görevlisi eşlik edecek mi?
- [ ] Giriş için kimlik listesi, araç plakası, ekipman giriş izni (tripod, batarya, drone varsa ayrıca).
- [ ] **Drone** kullanılacaksa: bkz. §9 — ayrı izin ve lisanslı operatör. Varsayılan: drone YOK.

### 1.2 Mekân koşulları **[Z]**
- [ ] Mekân çekim süresince **boş** (seyirci, etkinlik, prova, temizlik ekibi yok). Temizlik/bakım ekibinin çekim saatinde başka bölgede çalışması rica edilecek.
- [ ] **Işık**: Etkinlik/maç aydınlatması (tüm salon ışıkları açık, sahne/saha ışığı tam) çekim boyunca **sabit** kalacak. Işık kademeli açılıyor/ısınıyorsa (metal halide) en az 15–20 dk önce açılsın. Dinamik LED efektleri, ekranlar, skorbord animasyonları **kapalı** veya sabit görüntüde.
- [ ] Gün ışığı alan cam/çatı varsa: güneş açısı değişimi parlaklığı bozar → bulutlu gün veya akşam (yapay ışık) tercih edilir.
- [ ] Sahne/saha **etkinlik düzeninde** mi? (Konser sahnesi kurulu mu, basketbol potaları yerinde mi, zemin örtüsü?) Müşteriyle hangi düzenin çekileceği yazılı olarak netleşsin. Farklı düzenler = ayrı çekim.
- [ ] Koltuklar açık mı (katlanır koltuklar oturma konumunda mı)? Göz yüksekliği ölçümü için birkaç koltuk açık olmalı.
- [ ] Vomitoryum/koridor kapıları, merdiven korkulukları üzerinde örtü, malzeme, branda yok.

### 1.3 KVKK ve mahremiyet **[Z]**
- [ ] Hedef: **görüntülerde tanınabilir kişi, yüz, plaka, kişisel veri içeren ekran/kâğıt olmaması**.
- [ ] Ekip dışındaki herkes çekim alanından çıkarılır; ekip üyeleri de 360 fotoğraf anında kadraj dışına (koltuk sıraları arkasına, kapı arkasına) saklanır.
- [ ] Ekip üyelerinden **açık rıza** (görüntüde kalırlarsa), ama hedef yine de silmek/maskelemektir.
- [ ] Çekim sonrası her 360 fotoğraf ve splat sahnesi **kişi taraması** yapılır (bkz. isleme-rehberi §QC). Bulunan kişi → maske/bulanıklaştırma/kare silme.
- [ ] Ham veri yalnız şirket depolamasında; bulut işleme (Polycam vb.) kullanılacaksa mekân izninde **üçüncü taraf bulut işleme** maddesi var mı kontrol edilir. *(hukuk teyidi gerekli)*
- [ ] Bilet panolarında/ekranlarda kişisel bilgi (isim listesi, kamera ekranları) varsa kapatılır.

### 1.4 Güvenlik (İSG) **[Z]**
- [ ] Mekânın acil çıkışları ve toplanma noktası öğrenildi.
- [ ] Dik tribünlerde (üst kat) **tek elle yürüme yok**: video çekerken bir el korkuluğa yakın; merdivenlerde operatörün yanında **gözcü** (2. kişi) yürür.
- [ ] Ön sıra korkuluğu/balkon kenarından kamera çubuğu dışarı uzatılmaz (düşen ekipman alttakileri yaralar). Çubuğa **bilek kayışı** takılı.
- [ ] Kablolar/tripod ayakları yürüme yolunda bırakılmaz.
- [ ] Yüksek erişim (podyum, platform, sepetli vinç) yalnız mekânın yetkili personeliyle.
- [ ] Ekip: en az **2 kişi** (operatör + gözcü/kayıtçı). Tek kişi çekim yapılmaz.

### 1.5 Hazırlık (ofiste, T-1)
- [ ] Mekânın oturma planı (PDF/görsel) alındı; bloklar, sıra sayıları, koltuk numaralandırma yönü (soldan sağa mı?) not edildi.
- [ ] `ornek-bloklar.csv` biçiminde **ön blok CSV'si** hazırlandı (ölçüler tahmini olabilir) ve `seats_from_plan.py --capture-plan` ile **çekim planı** üretildi:
  ```bash
  python3 seats_from_plan.py mekan-bloklar.csv -o taslak.venue.json \
      --venue-code TYAT --capture-plan cekim-plani.csv
  ```
  `cekim-plani.csv` her blok için ön/orta/arka (geniş bloklarda sol/sağ) noktaları ve **önerilen dosya adlarını** verir. Yazdırılıp sahaya götürülür.
- [ ] Yürüyüş rotaları plan üzerine çizildi (bkz. §3.3).
- [ ] Ekipman kontrol listesi (§10) tamam; tüm bataryalar dolu; kartlar **biçimlendirildi** (önceki veri yedeklendikten sonra).
- [ ] Kamera **saat/tarih** doğru (Türkiye saati, UTC+3) — `takenAt` buradan gelir.
- [ ] Kamera ürün yazılımı (firmware) güncel; Insta360 Studio sürümü kayıt altında.
- [ ] Lens koruyucu kullanılmayacak (splat kalitesini düşürür, yansıma yapar) *(Insta360'ın kendi standart koruyucuları için etkisi doğrulanmadı — testte karşılaştır)*; lensler mikrofiber bezle temiz.

---

## 2. Kamera ayarları — Insta360 X5

> Teknik dayanak (B&H spec sayfası): 360 video 8K (7680×3840) 24/25/30 fps; 5.7K (5760×2880) 60 fps'e kadar; fotoğraf 72 MP (11904×5952) DNG/INSP; enstantane 1/8000–120 s; ISO 100–6400; beyaz dengesi 2000–10000 K; manuel pozlama modu var. Bitrate 180 Mb/s. Log profil desteği **doğrulanmadı**.

### 2.1 Yürüyüş videosu (splat ham verisi)
| Ayar | Değer | Neden |
|---|---|---|
| Mod | 360 Video | |
| Çözünürlük / fps | **8K 30 fps** (varsayılan) · loşsa veya ısınma olursa **5.7K 30** | Splat detayı çözünürlükle artar; 60 fps'e gerek yok (zaten 1–2 fps kare çıkarılacak) |
| Pozlama | **Manuel**. Enstantane **1/250 s veya daha hızlı** (yürüyüşte hareket bulanıklığı), ISO en düşük kabul edilebilir (≤800 hedef), gerekirse 1/125 s'ye inilir | Otomatik pozlama kareler arası parlaklık değiştirir → splat'ta "titreyen" yüzeyler |
| Beyaz dengesi | **Sabit K değeri** (ör. 4000–5600 K; sahada gri karta/beyaz duvara göre seçilir). Otomatik KAPALI | Kareler arası renk tutarlılığı |
| Renk profili | Standart; keskinlik "düşük/orta", yoğun gürültü azaltma kapalı/az *(menü adları firmware'e göre değişir — doğrulanmadı)* | Aşırı keskinleştirme hale/artefakt üretir |
| Sabitleme | Kamerada açık (FlowState); yön kilidi ve ufuk düzeltme Studio dışa aktarımında açılır | Equirect zaten tüm küreyi kapsar; stabilizasyon kare eşleşmesini kolaylaştırır |
| Ses | Kapalı veya düşük (önemli değil) | |
| Lens yönü | Kameranın **lenslerinden biri sahaya/sahneye bakar**, dikiş çizgisi yanlara gelir | Önemli içerik dikiş çizgisine düşmesin |

### 2.2 Sabit 360 fotoğraf noktaları
| Ayar | Değer |
|---|---|
| Mod | 360 Fotoğraf, **72 MP**, **DNG + INSP** (RAW) |
| Pozlama | Manuel; tripod olduğu için düşük ISO (100–200), enstantane serbest (1/30–1/4 s olabilir) |
| HDR / pozlama basamaklama | Varsa **3 veya 5 kare basamaklama** *(X5'te AEB/HDR fotoğraf seçeneği ve RAW ile birleşimi doğrulanmadı)*; yoksa tek kare RAW, vurgular kırpılmayacak şekilde |
| Beyaz dengesi | Video ile **aynı K değeri** |
| Zamanlayıcı | 5–10 sn (operatör saklanacak) veya telefondan uzaktan tetik |
| Yükseklik | Bkz. §3.2 |

### 2.3 Bataryalar, ısı, depolama
- 8K30'da batarya ~88 dk (B&H). Yanında **en az 3 batarya**. Kart başına yaklaşık **180 Mb/s ≈ 81 GB/saat** (hesap) → 256 GB kart ≈ 3 saat 8K.
- 8K'da ısınma bildirilmiştir (TechRadar incelemesi). Uzun rotaları ≤10 dk parçalara böl, aralarda kamerayı soğut.

---

## 3. Örnekleme stratejisi

### 3.1 Koordinat sözleşmesi (çekimden ÖNCE belirle)
- Orijin = saha/sahne merkezi, zemin. **+X = saha uzun ekseni** (hangi yönün +X olduğunu plan üzerinde ok ile işaretle: ör. "skorbord tarafı +X"). +Z sağ el kuralıyla belirlenir. Bu bilgi `isleme-rehberi.md §7` hizalamasında kullanılır.
- **Tiyatro / konser salonu (şema v0.2):** orijin = sahne ağzı (sahne ön kenarı) çizgisinin orta noktası, **Y=0 = sahne döşemesi**, X sahne ağzı boyunca (seyirciden bakınca sağa +X), +Z seyirciye doğru. Sahada ölç: sahne döşemesinin parter 1. sıra zeminine göre yüksekliği (→ parter `frontHeight`, negatif), sahne ağzı genişliği, balkon ön korkuluğunun sahne ağzına uzaklığı ve yüksekliği.
- **Kısıtlı görüş:** kolon, balkon çıkması, pota, ışık/ses kulesi arkasındaki koltukları sahada tespit edip fotoğrafla (REF) ve `kisitli.csv` listesine yaz (`section,row,seat,severity,reason`).

### 3.2 Sabit 360 fotoğraf noktaları (A)
**Göz yüksekliği (şema ile uyumlu yorum):** lens merkezi, koltuğun bulunduğu **basamak zemininden 1.15 m** yukarıda (oturan yetişkin göz yüksekliği). Ayakta tribünlerde **1.60 m**. Ölçüm: şerit metre basamak zemininden lens merkezine. *(Şemadaki "oturma yüzeyi + 1.15 m" ifadesi bu şekilde yorumlandı; bkz. rapor/öneri.)*

**Konum:** koltuğun tam üzerinde (koltuk açık, ayak koltuk önünde) veya koltuk katlıysa koltuk merkezinin dikey izdüşümünde. Tripod ayakları sıra aralığına sığmazsa **monopod + mini ayak** ya da koltuğa kelepçe kullanılır.

**Blok başına nokta sayısı (varsayılan):**

| Blok tipi | Nokta | Konumlar |
|---|---|---|
| Küçük blok (≤ 24 koltuk/sıra, ≤ 15 sıra) | **3** | Ön sıra orta, orta sıra orta, arka sıra orta |
| Geniş blok (> 24 koltuk/sıra) | **5** | + orta sıra sol uç (2. koltuk) ve sağ uç (sondan 2.) |
| Çok derin blok (> 25 sıra) | **+1** | 1/4 ve 3/4 sıralara birer nokta (toplam 4–6) |
| Özel koltuklar (VIP loca, engelli alanı, kolon arkası/kısıtlı görüş) | **+1 her biri** | Satışta "kısıtlı görüş" uyarısının kanıtı |
| Saha/zemin (konser parteri) | Izgara | 10–15 m aralıklı, ayakta 1.60 m |

`seats_from_plan.py --capture-plan` bu kuralları otomatik uygular (ön/orta/arka + geniş bloklarda sol/sağ). Örnek Arena (24 blok) için 120 nokta üretti.

**Nokta başına işlem (~2–3 dk):**
- [ ] Ayağı koltuğa yerleştir, lens yüksekliğini ölç (± 2 cm), kabarcık terazi ile dik.
- [ ] Lens yönü: bir lens sahaya.
- [ ] Ekip saklanır, uzaktan tetik/zamanlayıcı.
- [ ] Telefonda önizleme: kişi yok, pozlama kırpılmamış, dikiş saha üzerinde değil.
- [ ] **Çekim günlüğüne** satır ekle (bkz. §5).
- [ ] Telefonla **referans fotoğraf (REF)**: koltuktan sahaya, normal 1x lens, göz hizasında; ve **koltuk/sıra numarasının** yakın fotoğrafı.

### 3.3 Yürüyüş videoları (B) — splat için
Genel kurallar:
- **Hız:** 0.3–0.5 m/s (yavaş, sabit adım). Merdivenlerde her basamakta kısa duraklama.
- **Yükseklik:** kamera, operatörün başının ~30–50 cm üzerinde çubukta (görünmez selfie çubuğu, ~1.8–2.2 m) **veya** göz hizasında; her rotada **sabit** tutulur. Oturma göz yüksekliği (1.15 m) çeşitliliği sabit noktalardan gelir.
- **Örtüşme:** 2 fps kare çıkarımında ardışık kareler arası 15–25 cm → %80+ örtüşme. Dönüşlerde (köşe/merdiven) yavaşla.
- **Döngü kapatma:** her rota başladığı yere (veya önceki bir rotanın üzerine) dönerek biter; SfM'in birleştirmesi kolaylaşır.
- Operatör kamerayı **gövdesinin önünde/üstünde** tutar; görüntünün altında kendisi görünecektir — bu, işleme aşamasında alt (nadir) bölgenin atılmasıyla çözülür (`equirect_to_persp.py` varsayılan olarak nadir üretmez).
- Video başında ve sonunda **3 sn sabit** dur (kare çıkarmada başlangıç atlanır).

Rota seti (küçük salon / spor salonu için hepsi; arena için her kat ve her blok grubu için tekrarlanır):

| # | Rota kodu | Açıklama |
|---|---|---|
| 1 | `ROTA-saha-cevre` | Saha/sahne çevresinde tam tur (kenar çizgisinin 1–2 m dışından) |
| 2 | `ROTA-saha-izgara` | Saha içinde uzun eksene paralel 2–3 geçiş (izin varsa; parke/zemin örtüsü korunur) |
| 3 | `ROTA-<kat>-on` | Her katın ön sıra önündeki koridor boyunca tam tur |
| 4 | `ROTA-<blok>-merdiven` | Her blok aralığındaki merdivenden **yukarı çık, aşağı in** (blok sınırları) |
| 5 | `ROTA-<kat>-arka` | Her katın en arka sırasının arkasındaki koridor/konkurs boyunca tam tur |
| 6 | `ROTA-<blok>-sira` | (Ö) Geniş bloklarda orta sıra boyunca yatay geçiş — sıra arası dar ise atla |
| 7 | `ROTA-tavan` | (Ö) Tavan/çatı ayrıntısı önemliyse kamera yukarı çubukla, yavaş tur |

### 3.4 Ölçümler ve kontrol noktaları (C)
- [ ] Saha çizgileri (basketbol 28 × 15 m / futbol 105 × 68 m / sahne ağzı genişliği) lazer metre ile **gerçek ölçüldü** (standart ölçüye güvenme, birkaç cm–m fark olabilir).
- [ ] En az **4 kontrol noktası**: saha köşeleri veya sahne ağzı köşeleri (zemin seviyesi) + en az **2 yüksek nokta** (ör. alt kat arka sıra korkuluğu, balkon kenarı) — venue koordinatlarında ölçülmüş.
- [ ] (Ö) Kontrol noktalarına A4 basılı **hedef işareti** (dama tahtası/AprilTag) konur, videoda ve fotoğraflarda görünür. *(Postshot Studio'nun AprilTag ile otomatik hizalama özelliği üretici sayfasında listeleniyor; iş akışı doğrulanmadı.)*
- [ ] Her blok tipinden 1 örnekte: **sıra derinliği** (rowDepth), **basamak yüksekliği** (riserHeight), **1. sıra basamak yüksekliği** (frontHeight), **koltuk aralığı** (seatWidth). Bunlar blok CSV'sine girer.
- [ ] Koltuk numaralandırma yönü (blokta koltuk 1 izleyicinin solunda mı?) fotoğrafla kanıtlandı.

---

## 4. Dosya adlandırma kuralı **[Z]**

```
{MEKAN}_{BLOK}_{KONUM}_{TUR}_{NN}.{uzantı}
```
| Alan | Biçim | Örnek |
|---|---|---|
| MEKAN | 4 harf büyük, proje başında sabitlenir | `ORNK`, `TYAT` |
| BLOK | Bilet sistemindeki blok kodu (birebir) veya `GENEL` | `103`, `A1`, `PARTER` |
| KONUM | Sabit nokta: `R{sıra}S{koltuk}` · Video: rota kodu · Ölçüm: nokta adı | `R1S14`, `RAS2` (harfli sıra A), `ROTA-alt-on`, `KOSE-KD` (sıfır doldurma yok; bilet sistemindeki etiket aynen) |
| TUR | `P360` sabit 360 foto · `V360` 360 video · `REF` telefon referans · `OLC` ölçüm fotoğrafı · `DRN` drone | |
| NN | Aynı nokta/rota için tekrar sayacı | `01`, `02` |

Örnekler: `ORNK_103_R1S13_P360_01.dng`, `ORNK_GENEL_ROTA-saha-cevre_V360_01.insv`, `ORNK_103_R1S13_REF_01.jpg`.

Kamera dosyaları kendi adıyla kaydedilir (`VID_2026...insv`); **yeniden adlandırma akşam aktarımda** `cekim-gunlugu.csv`'deki eşleşmeyle yapılır (sahada yeniden adlandırma yok). Ham orijinaller ayrı klasörde değişmeden saklanır.

Klasör yapısı:
```
YYYY-MM-DD_MEKAN/
  00_ham/kamera-X5/          # kameradan birebir kopya (salt-okunur)
  00_ham/telefon/
  01_adlandirilmis/P360 V360 REF OLC/
  cekim-gunlugu.csv
  olcumler.csv               # kontrol noktaları, rowDepth vb.
  izinler/                   # izin yazısının PDF'i
```

---

## 5. Çekim günlüğü (`cekim-gunlugu.csv`)

```
saat,kamera_dosyasi,hedef_ad,blok,sira,koltuk,tur,lens_yuksekligi_m,iso,enstantane,wb_k,not
10:31,IMG_20261115_103101_00_012.insv,ORNK_103_R1S13_P360_01,103,1,13,P360,1.15,200,1/15,4300,
10:52,VID_20261115_105210_00_013.insv,ORNK_GENEL_ROTA-alt-on_V360_01,GENEL,,,V360,2.0,800,1/250,4300,köşede yavaşladım
```
Bu günlük daha sonra `seats_from_plan.py --viewpoints` girdisine dönüştürülür (`id,sectionId,row,seat,file,type,takenAt`).

---

## 6. Sahada kalite kontrol **[Z]**

Her blok bitince (5 dk):
- [ ] Planlanan tüm noktalar çekildi mi? (`cekim-plani.csv` üzerinde işaretle)
- [ ] Rastgele 2 fotoğrafı telefonda %100 yakınlaştır: netlik, kişi yok, dikiş hatası yok.

Her rota bitince:
- [ ] Video süresi mantıklı mı (rota uzunluğu / 0.4 m/s)?
- [ ] İlk/son 3 sn sabit duruş var mı?

Öğle arası ve gün sonu (dizüstü bilgisayarda, 20–40 dk):
- [ ] Kartlar **iki ayrı diske** kopyalandı (dizüstü + harici SSD); kopya boyutları kontrol edildi.
- [ ] 1 rota videosu Insta360 Studio ile hızlı equirect dışa aktarım → `extract_frames.py --fps 1` → `filter_blurry.py --report-only --crop-poles 0.15`: bulanık kare oranı %20'yi aşıyorsa o rota **daha yavaş tekrar** çekilir.
- [ ] (Ö) GPU'lu dizüstü varsa bir bloğun hızlı düşük çözünürlüklü splat denemesi (Postshot) — delik/kopukluk varsa ek rota.
- [ ] Ölçümler `olcumler.csv`'ye girildi, fotoğrafları var.
- [ ] Mekândan ayrılmadan önce: eksik nokta listesi **sıfır** veya bilinçli olarak kabul edildi.

---

## 7. Çekim sırası (önerilen akış)

1. Kurulum, ışık stabilizasyonu, beyaz dengesi ölçümü (gri kart) — 20 dk
2. Ölçümler ve kontrol noktası işaretleri (§3.4) — 30–60 dk
3. Yürüyüş videoları: saha → alt kat → üst kat (ışık değişmeden en kritik veri önce) 
4. Sabit 360 noktaları: blok blok, plan sırasıyla
5. Telefon referans fotoğrafları (sabit noktalarla eşzamanlı yapılabilir)
6. Kontrol noktası işaretlerini topla, alanı teslim et

## 8. Tipik süre (tahmini — ilk demoda ölçülüp güncellenecek)

| Mekân | Sabit nokta | Video | Ölçüm | Toplam sahada |
|---|---|---|---|---|
| Tiyatro / üniversite salonu (300–800 koltuk, 4–8 blok, 1 balkon) | 15–30 nokta ≈ 1–1.5 sa | 6–10 rota ≈ 1 sa | 45 dk | **3–4 saat** (2 kişi) |
| Spor salonu (2.000–5.000) | 30–60 nokta ≈ 2–3 sa | 1.5–2 sa | 1 sa | **5–7 saat** |
| Arena (~12.000, 24 blok) | ~120 nokta ≈ 5–6 sa | 3–4 sa | 1.5 sa | **2 gün** (veya 3 kişiyle 1 uzun gün) |

## 9. Drone notu

- Varsayılan: **ilk projelerde drone yok**. Kapalı salonlarda zaten gerekmez; açık stadyumlarda çatı/üst görünüm ve dış cephe için gerekir.
- Türkiye'de İHA kullanımı SHGM düzenlemesine tabidir; ticari kullanım için pilot lisansı/kayıt ve uçuş izni gerekir. Ağırlık eşikleri ve 2025–2026 değişiklikleri **doğrulanmadı** (bir hukuk bürosu özeti 500 g üzeri için kayıt zorunluluğu belirtiyor; güncel SHGM İHA Talimatı'ndan teyit edilmeli). Kalabalık etkinlik üzerinde uçuş yapılmaz.
- Öneri: ihtiyaç olduğunda **lisanslı, sigortalı İHA operatörü** kiralanır; izinleri operatör alır; sözleşmede görüntü hakları bize devredilir.
- Kapalı mekânda (indoor) uçuş: GPS yok, çarpışma riski yüksek; yalnız mekânın yazılı izniyle ve deneyimli pilotla.
- Drone görüntüleri de aynı KVKK kurallarına tabidir.

## 10. Ekipman kontrol listesi (çanta)

- [ ] Insta360 X5 + **3 batarya** + şarj ünitesi + powerbank
- [ ] 2 × microSD (V30+, 256 GB) + yedek kart
- [ ] Hafif ışık ayağı / tripod (lens 0.9–2.2 m arası ayarlanabilir) + kabarcık terazi
- [ ] Görünmez selfie çubuğu (yürüyüş için)
- [ ] Lazer metre + 5 m ve 30 m şerit metre
- [ ] Gri kart / beyaz denge kartı
- [ ] Basılı kontrol hedefleri (A4) + kâğıt bant (iz bırakmayan)
- [ ] Mikrofiber bez, lens temizleme
- [ ] Dizüstü + harici SSD (≥ 2 TB) + kart okuyucu
- [ ] Basılı oturma planı + `cekim-plani.csv` çıktısı + kalem
- [ ] Telefon (uzaktan tetik, referans foto)
- [ ] Kimlik, izin yazısı çıktısı, ekip yeleği/yaka kartı
