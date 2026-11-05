# PİLOT UYGULAMA SÖZLEŞMESİ — ANA MADDELER TASLAĞI

> ## ⚠️ TASLAKTIR, HUKUKİ TAVSİYE DEĞİLDİR. İMZADAN ÖNCE AVUKAT İNCELEMESİ GEREKİR.
> Bu metin, müzakereye başlamak için hazırlanmış bir madde başlıkları ve öneri setidir. KVKK, Fikir ve Sanat Eserleri Kanunu, Türk Borçlar Kanunu, Türk Ticaret Kanunu ve sektöre özgü kurallar (ör. spor müsabakalarında güvenlik mevzuatı) açısından bir avukat ve gerektiğinde bir veri koruma uzmanı tarafından incelenmeden kullanılmamalıdır.

*Sürüm: v0.1 · 31.10.2026 · Köşeli parantezli alanlar doldurulacaktır.*

---

## 1. Taraflar
- **Sağlayıcı:** Hyperbaric [ticaret unvanı, MERSİS, adres]
- **Müşteri:** [Bilet şirketi / mekân işletmecisi / kulüp], [unvan, adres]
- **Mekân sahibi (gerekirse):** Müşteri mekânın sahibi değilse, çekim izni için mekân sahibi de tarafa eklenir veya izin yazısı ek olarak konur (bkz. Madde 9).

## 2. Tanımlar (özet)
- **Ürün:** [Ürün adı] 3D koltuk görünümü yazılımı, görüntüleyici, SDK/embed kodu ve analitik paneli.
- **Mekân Modeli:** Mekânda yapılan çekimlerden üretilen 3D veri. Bunlar 360° görüntüler, Gaussian splat dosyaları, nokta bulutları ve koltuk eşleme verisidir.
- **Pilot Dönemi:** Madde 4'te tanımlanan süre.
- **Toplu Veri:** Hiçbir gerçek kişiyle ilişkilendirilemeyen, anonimleştirilmiş, istatistiksel düzeyde metrikler.

## 3. Kapsam
3.1. Sağlayıcı şu işleri üstlenir:
- [Mekân adı] için [1] sahne düzeninde Mekân Modeli üretmek,
- Modeli Müşterinin bilet satış ekranına [embed/SDK] ile entegre etmek,
- Pilot Dönemi boyunca barındırmak ve destek vermek.

3.2. Kapsam dışı işler ayrıca fiyatlandırılır. Bunlar arasında ek sahne düzenleri, loca ve VIP alanlar, pazarlama videoları ve Müşteri sistemlerinde özel geliştirme sayılabilir.

3.3. **Müşterinin yükümlülükleri:**
- Güncel oturma planını ve blok/koltuk kodlarını vermek,
- Test ortamına erişim sağlamak,
- Bir teknik irtibat kişisi atamak,
- Çekim günü için erişim sağlamak.

3.4. **Hizmet seviyesi (pilot):**
- Erişilebilirlik hedefi %99; bu hedef bağlayıcı değildir.
- Destek talebine 1 iş günü içinde yanıt verilir.
- Görüntüleyici çalışmazsa satış akışı kesintisiz devam eder. Bu "zarif bozulma" kuralı Sağlayıcının taahhüdüdür.

## 4. Süre
- 4.1. Pilot Dönemi canlıya alma tarihinden itibaren **90 gündür.**
- 4.2. Taraflar yazılı olarak anlaşırsa süre bir kez, en fazla 60 gün uzatılabilir.
- 4.3. Pilot sonunda iki yol vardır:
  - Taraflar **Ek-A'daki önceden belirlenmiş ticari koşullarla** yıllık sözleşmeye geçebilir.
  - Ya da Madde 15'e göre sona erdirebilir.

## 5. Ücret
- 5.1. Kurulum ücreti: **[0 TL / ___ USD + KDV]**. Pilot boyunca lisans ücreti alınmaz.
- 5.2. Kurulum ücretinin yarısı imzada, yarısı canlıya almada ödenir. Fatura, fatura tarihindeki TCMB döviz satış kuru ile TL olarak düzenlenir.
- 5.3. Yıllık sözleşmeye geçilirse pilotta ödenen tutar ilk yıl bedelinden **mahsup edilir.**
- 5.4. Ek-A'da yazılı lansman fiyatı, pilot bitiminden itibaren [30] gün geçerlidir.

## 6. Başarı ölçütleri
- 6.1. Taraflar canlıya almadan önce **Ek-B**'de en çok 3 başarı ölçütü belirler. Örnekler:
  - koltuk görünümü açılan oturumlarda satın alma oranı ile açılmayanlar arasındaki fark,
  - üst kategori bilet payı,
  - koltuk konumuyla ilgili müşteri hizmetleri talep sayısı.
- 6.2. A/B testi Müşterinin onayıyla yapılır. Örnek: trafiğin %[50]'sine görünüm gösterilir.
- 6.3. Ölçütlerin tutmaması tek başına bir ihlal değildir. Yalnızca Madde 15.2'deki cezasız çıkış hakkını doğurur.

## 7. Veri ölçme hakkı ve kişisel verilerin korunması (KVKK)
**7.1. Ölçülecek metrikler (toplu ve anonim):**
- görünüm açılma sayısı ve oranı,
- blok ve kategori bazında görüntüleme süresi,
- koltuk görünümü açılan ve açılmayan oturumların satın alma oranı,
- kategori ve fiyat dağılımı,
- cihaz türü,
- terk noktası,
- iade ve şikâyet sayılarındaki değişim (Müşterinin toplu verisiyle).

**7.2. Kişisel verinin en aza indirilmesi:**
- Sağlayıcının görüntüleyicisi ad, T.C. kimlik numarası, e-posta, telefon, ödeme bilgisi ve bilet sahibi bilgisi **toplamaz.**
- Oturumlar rastgele ve geçici bir oturum kimliğiyle ölçülür.
- Satın alma sonucu, Müşteri tarafından yalnızca "oturum kimliği → satın aldı/almadı, kategori" düzeyinde paylaşılır.
- Çerez veya benzeri teknoloji kullanılacaksa Müşterinin çerez onay yönetimine tabi olur.

**7.3. Roller:**
- Bilet satış sürecinde **veri sorumlusu Müşteridir.**
- Sağlayıcı, görüntüleyici aracılığıyla işlenebilecek sınırlı teknik veriler için Müşteri adına **veri işleyen** sıfatıyla hareket eder. Örnek teknik veriler: IP adresi ve tarayıcı bilgisi.
- Toplu Veri anonimleştirildikten sonra kişisel veri niteliği taşımaz. Sağlayıcı bu veriyi Madde 7.6'daki amaçlarla kullanabilir.
- **Avukat notu:** Rol dağılımı fiili veri akışına göre teyit edilmelidir.

**7.4. Veri işleyen yükümlülükleri (Sağlayıcı):**
- Veriyi yalnızca Müşterinin talimatıyla işler.
- Uygun teknik ve idari tedbirleri alır.
- Alt işleyenleri (barındırma/CDN) listeler ve değişiklikleri önceden bildirir.
- Veri ihlalini öğrendiğinde Müşteriyi gecikmeksizin, en geç [24] saat içinde bilgilendirir.
- Sözleşme bittiğinde kişisel veriyi siler veya iade eder.

**7.5. Yurt dışına aktarım:**
- Barındırma veya CDN sağlayıcısı yurt dışındaysa, KVKK m.9 kapsamında uygun aktarım mekanizması kullanılır. Örnek: standart sözleşme ve imzadan sonra 5 iş günü içinde Kurula bildirim.
- Bu yükümlülüğün hangi tarafa düştüğü avukatla netleştirilmelidir.
- Kaynak: 7499 sayılı Kanun ile yapılan değişiklik 01.06.2024'te yürürlüğe girdi; standart sözleşmede Kurula 5 iş günü içinde bildirim zorunluluğu var ([Hukuki Haber](https://www.hukukihaber.net/kvkk-yurt-disina-aktarim-kapsaminda-yapilan-kanun-degisikligi), [KVKK duyurusu](https://www.kvkk.gov.tr/Icerik/7938/Standart-Sozlesmeler-ve-Baglayici-Sirket-Kurallarina-Iliskin-Dokumanlar-Hakkinda-Kamuoyu-Duyurusu)).
- *Kanun numarası avukatça teyit edilmelidir.*
- Mümkünse veri Türkiye'deki veri merkezlerinde tutulur.

**7.6. Toplu Verinin kullanımı:**
- Sağlayıcı Toplu Veriyi ürün geliştirme ve **Müşteri adını içermeyen** sektör istatistikleri için kullanabilir.
- Müşteri adıyla yayımlanması Madde 8'deki onaya tabidir.
- Müşterinin ticari sırrı sayılan ham satış rakamları (ciro, bilet adedi) Müşterinin yazılı onayı olmadan hiçbir biçimde yayımlanmaz.

**7.7. Aydınlatma:** Gerekirse son kullanıcıya yönelik aydınlatma metni Müşteri tarafından güncellenir. Sağlayıcı bunun için önerilen bir metin sağlar.

## 8. Referans hakkı
- **8.1.** Müşteri, Sağlayıcıya Müşterinin **adını ve logosunu** "müşterilerimiz/referanslarımız" bağlamında kullanma hakkı verir. Bu hak web sitesi, sunum ve teklif dokümanlarında geçerlidir.
- **8.2. Vaka çalışması:** Sağlayıcı pilot sonuçlarını anlatan bir vaka çalışması hazırlayabilir. Yazılı veya video olabilir ve Müşteri yetkilisinin alıntısını içerebilir.
- **8.3. Onay süreci:**
  - Logo kullanımı dışındaki her yayın (vaka çalışması, basın bülteni, sosyal medya, rakam içeren her içerik) **yayından önce Müşterinin yazılı onayına** sunulur.
  - Müşteri [10] iş günü içinde onaylar, düzeltme ister ya da gerekçeli olarak reddeder.
  - Süre içinde yanıt gelmemesi **onay sayılmaz**; Sağlayıcı bir kez hatırlatma yapar.
- **8.4.** Rakamlar Müşterinin seçtiği biçimde yayımlanır. Örnek: mutlak rakam yerine yüzde ya da aralık.
- **8.5.** Müşteri, logo kullanımını ileriye dönük olarak [30] gün önceden bildirimle geri çekebilir. Önceden basılmış materyaller makul sürede tüketilir.
- **8.6.** Referans hakkı, Madde 15'e göre sona ermeden sonra [24] ay devam eder. Bu, pilot başarısız olsa bile Müşteri aksini bildirmedikçe geçerlidir; müzakere edilebilir.

## 9. Mekân çekim izni, güvenlik ve görüntü kullanımı
- **9.1.** Müşteri, mekânda çekim yapılabilmesi için gerekli izni verdiğini ya da mekân sahibinden aldığını beyan eder. Gerekirse izin yazısı **Ek-C** olarak eklenir.
- **9.2.** Çekim, **etkinlik olmayan** bir günde, Müşterinin belirlediği saatlerde ve Müşterinin güvenlik, iş sağlığı ve güvenliği ile erişim kurallarına uyularak yapılır. Sağlayıcı ekibi:
  - Müşteri yetkilisi refakatinde çalışır,
  - kimlik ve araç bilgilerini önceden bildirir,
  - yasak alanlara girmez.
- **9.3. Güvenlik açısından hassas alanlar:** Görüntülenmeyecek veya modelden çıkarılacak alanları Müşteri önceden bildirir. Örnekler: güvenlik odaları, kamera konumları, acil çıkış teknik detayları, VIP giriş güzergâhları. Sağlayıcı bunları **yayından önce maskeler**; Müşteri yayından önce son onayı verir.
- **9.4. Kişiler:** Çekimde kişi görüntülenmemesi esastır. Kazara görüntülenen kişiler ve araç plakaları **bulanıklaştırılır veya silinir.**
- **9.5. Marka ve sponsor görselleri:** Mekândaki üçüncü taraf marka, sponsor ve reklam panolarının modelde görünmesi doğal bir sonuçtur. Müşteri, sponsor sözleşmelerinden doğan bir kısıt varsa bunu önceden bildirir. Sağlayıcı talep halinde ilgili alanları nötrleştirir.
- **9.6. Müşterinin marka kullanım izni:** Müşteri, ürünün beyaz etiketli sunumu için kendi marka ve renklerinin kullanılmasına izin verir. Sağlayıcı, Müşteri markasını Madde 8 dışında kullanmaz.
- **9.7.** Çekim sırasında Sağlayıcının kusurundan doğan maddi zararlardan Sağlayıcı sorumludur. Sağlayıcı ekipman ve sorumluluk sigortası bilgisini çekimden önce paylaşır *(sigorta kapsamı doğrulanmalı)*.

## 10. Fikri mülkiyet
- **10.1.** Ürün, yazılım, görüntüleyici, SDK, işleme yöntemleri ve **Mekân Modeli** (ham çekimler ve 3D veri dahil) ile bunlar üzerindeki tüm haklar **Sağlayıcıya** aittir.
- **10.2.** Müşteriye Pilot Dönemi boyunca, Mekân Modelini yalnızca kendi bilet satış kanallarında göstermek için **münhasır olmayan, devredilemez, alt lisanslanamaz** bir kullanım lisansı verilir.
- **10.3. Mekân hakları ve modelin başka yerde kullanımı:**
  - Mekânın mimari tasarımı, adı ve markası üzerindeki haklar mekân sahibinde kalır.
  - Sağlayıcı, Mekân Modelini **mekânla doğrudan ilişkili ticari amaçlarla** başka bir bilet şirketi veya organizatör için kullanacaksa, mekân sahibinin onayını alır.
  - Bu kural, aynı mekânda birden fazla bilet şirketinin satış yaptığı durumlar için müzakere edilmelidir.
- **10.4.** Müşterinin verdiği oturma planı, logo ve içerikler Müşteriye aittir.
- **10.5.** Taraflar arasında yazılı olarak kararlaştırılmadıkça müşteriye özel geliştirmeler de Sağlayıcıya ait olur.
- **10.6. Model devri:** Müşteri, Mekân Modelinin mülkiyetini satın almak isterse, bu ayrı bir sözleşmeyle ve ayrı bir bedelle mümkündür.

## 11. Gizlilik
- 11.1. Taraflar birbirlerinin ticari, teknik ve finansal bilgilerini gizli tutar. Bu bilgilere satış verileri, fiyatlar, sistem mimarisi ve güvenlik bilgileri dahildir.
- 11.2. Gizlilik yükümlülüğü sözleşme sona erdikten sonra [3] yıl, ticari sırlar için süresiz devam eder.
- 11.3. Kamuya açık bilgiler, yasal zorunlulukla açıklanması gerekenler ve bağımsız olarak geliştirilenler bu yükümlülüğün istisnasıdır.

## 12. Müşteri sistemlerine erişim ve bilgi güvenliği
- 12.1. Sağlayıcının erişimi test ortamı ve gerekli API'larla sınırlıdır. Sağlayıcı ödeme ve kimlik sistemlerine erişmez.
- 12.2. Görüntüleyici Müşterinin sayfasında çalışan üçüncü taraf koddur. Bu nedenle sürüm kontrolü, içerik güvenlik politikası (CSP) uyumu ve değişikliklerin önceden bildirilmesi kuralları uygulanır.

## 13. Garanti ve sorumluluğun sınırlandırılması
- 13.1. Görünüm, gerçek çekime dayalı **temsili** bir görüntüdür. Hava, ışık, sahne düzeni, etkinliğe özel dekor ve seyirci yoğunluğu nedeniyle gerçek görüşten farklı olabilir.
- 13.2. Müşteri satış ekranında şu uyarıyı gösterir: "Görüntü temsilidir; etkinliğe göre farklılık gösterebilir."
- 13.3. Sağlayıcının toplam sorumluluğu, Pilot Dönemi içinde ödenen bedelle sınırlıdır. Ücretsiz pilotta bu sınır [___ TL]'dir. Kasıt ve ağır kusur bu sınırlamanın istisnasıdır *(avukat teyidi gerekir)*.
- 13.4. Taraflar dolaylı zararlardan sorumlu değildir. Dolaylı zarara kâr kaybı ve itibar kaybı dahildir.

## 14. Rekabet / münhasırlık
- Pilot münhasırlık içermez.
- Müşteri münhasırlık talep ederse, Ek-A'da ücret ve süreyle tanımlanır.

## 15. Fesih ve sona erme
- **15.1.** Pilot Dönemi bitince sözleşme kendiliğinden sona erer; yıllık sözleşmeye geçiş Madde 4.3'e göre olur.
- **15.2. Cezasız çıkış:** Ek-B'deki başarı ölçütleri tutmazsa Müşteri, Pilot Dönemi sonunda hiçbir ek ücret ödemeden çıkabilir.
- **15.3. Haklı nedenle fesih:**
  - Taraflardan biri esaslı bir yükümlülüğü ihlal eder ve yazılı ihtardan sonra [15] gün içinde gidermezse, diğer taraf sözleşmeyi feshedebilir.
  - KVKK veya güvenlik ihlallerinde bu süre aranmaz.
- **15.4. Sona ermenin sonuçları:**
  - Sağlayıcı [10] iş günü içinde görünümü Müşteri kanallarından kaldırır.
  - Kişisel veriyi siler veya iade eder.
  - Mekân Modeli Sağlayıcıda kalır (Madde 10).
  - Madde 7, 8, 10, 11 ve 13 sona ermeden sonra da geçerlidir.
- **15.5. Mücbir sebep:** Mekânın kapanması, etkinlik iptalleri veya seyircisiz oynama kararları Pilot Dönemini askıya alır. Bu durumda süre, eksik kalan kısım kadar uzar.

## 16. Diğer
- Uygulanacak hukuk: Türk hukuku. Yetkili mahkeme: [İstanbul (Çağlayan)] mahkemeleri ve icra daireleri.
- Bildirimler kurumsal e-posta adreslerine yapılır; ihtarlar KEP veya noter aracılığıyla gönderilir.
- Sözleşmeyi devretmek için diğer tarafın yazılı onayı gerekir.
- Değişiklikler yalnızca yazılı yapılır.

## Ekler
- **Ek-A:** Pilot sonrası ticari koşullar (kademe, kurulum, yıllık lisans, lansman indirimi, münhasırlık varsa ücreti)
- **Ek-B:** Başarı ölçütleri ve ölçüm yöntemi (A/B oranı, ölçüm dönemi, veri paylaşım formatı)
- **Ek-C:** Mekân çekim izni, çekim günü planı, maskelenecek alanlar listesi
- **Ek-D:** Veri işleme eki (işlenen veri kategorileri, amaç, süre, alt işleyenler, güvenlik tedbirleri, yurt dışı aktarım)

---
*Hatırlatma: Bu taslak hukuki tavsiye değildir; imzadan önce avukat incelemesi gerekir.*
