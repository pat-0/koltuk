# [Ürün adı]: Bilet alırken koltuğundan sahayı ve sahneyi gör

**[Kurum adı] için pilot teklifi** · Hyperbaric (Türkiye) · [Tarih] · *Taslak v2 (v1: `teklif-tek-sayfa.md`)*

> **v2'de ne değişti?** İki ürün seviyesi (Standart / Gerçek görüntü) · "yıllık lisans, komisyon yok" dili · rakip referansları sadeleşti · pilot iki seviyeye göre yazıldı. Fiyat modeli (v1 platform lisanslı / v2 platform ücretsiz) henüz seçilmedi. Bu sayfa rakam vermez, yalnızca çerçeve çizer. Rakamlar için `fiyatlandirma.md` / `fiyatlandirma-v2-alternatif.md`.

---

### Problem
Bilet alan kişi kategoriyi ve fiyatı görüyor, ama **o koltuktan ne göreceğini** görmüyor.
- Pahalı kategoride kararsız kalan kullanıcı sepeti bırakıyor ya da ucuz bloğa geçiyor.
- "Kolon arkasıymış", "sahneyi yandan gördüm" türü şikâyetler ve iade talepleri çağrı merkezine yük getiriyor.
- Türkiye'de bilet ekranına entegre, gerçek çekime dayalı bir koltuk görünümü bulamadık.

### Çözüm: iki seviye, tek görüntüleyici
[Ürün adı], **bilet ekranınıza beyaz etiketli olarak eklenen** bir koltuk görünümü. Kullanıcı bloğu ya da koltuğu seçer ve o noktadan sahaya veya sahneye 360° bakar.

| | **Standart** | **Gerçek görüntü** |
|---|---|---|
| Nasıl üretilir? | Oturma planınızdan ve salon ölçülerinden **kodla** üretilen 3D görünüm | Mekânda **360° kamerayla çekim** + Gaussian splatting ile fotogerçekçi 3D sahne |
| Ne gösterir? | Blokların sahneye göre konumu, açı, uzaklık | Salonun kendisi: balkon çıkıntısı, kolon, korkuluk, ışık köprüsü, gerçek doku |
| Çekim gerekir mi? | Hayır | Evet, etkinliksiz 1 gün (küçük salonlarda yarım gün) |
| Uygun olduğu yer | Çok sayıda salonu hızla kapsamak, düşük bütçe | Görüş farkının satış kararını etkilediği salonlar: balkonlu, sahne çevresi oturmalı, pahalı kategorili |
| Yükseltme | Aynı entegrasyonla Gerçek görüntü seviyesine geçilir | — |

Her iki seviyede de:
- **Sizin markanız:** Görüntüleyici sizin renklerinizi ve logonuzu taşır; kullanıcı satış akışınızdan çıkmaz.
- **Hafif entegrasyon:** Embed (iframe) ya da SDK ile koltuk haritanıza bağlanır. Seçilen koltuk doğrudan sepetinize düşer. Mobil ve masaüstünde çalışır.
- **Kısıtlı görüş uyarısı:** Kısıtlı görüşlü olarak işaretlediğiniz koltuklarda ekranda açık bir uyarı çıkar.
- **Ölçüm paneli:** Görünümü açan oturumlar, satın alma oranı ve kategori dağılımı toplu ve anonim olarak raporlanır.

### Fiyat çerçevesi
- **Kapasiteye göre yıllık lisans + tek seferlik kurulum. Bilet başı komisyon yok.** Uluslararası sağlayıcılarda yaygın model de bu. Örneğin 3D Digital Venue, İngiltere'de tiyatro bilet sistemi Spektrix üzerinden "rekabetçi yıllık lisans, işlem ücreti veya komisyon yok" diye sunuluyor ([Spektrix ortak ilanı](https://partners.spektrix.com/listing/3d-digital-venue/)). Preevue de "kapasiteye göre yıllık lisans" diyor ([Preevue](https://www.preevue.com/theatre/seat-preevue-vfs)).
- **Standart seviye** düşük fiyatlı, giriş seviyesidir. **Gerçek görüntü** ise asıl üründür.
- **Tiyatrolar için isteğe bağlı kalem:** yeni prodüksiyonda ya da dekor değişikliğinde görüntü güncellemesi.
- Bilet şirketi kanalında koşullar ayrıca konuşulur: [platform lisansı / platform ücreti yok, yalnızca canlı mekân başı ödeme]. *Karar bekliyor.*

### Neden şimdi?
- **Passolig zorunluluğu 2025–26 sezonuyla kalktı.** Kulüpler satış ve giriş kurallarını anlaştıkları bilet şirketleriyle birlikte belirliyor ([Sporx](https://www.sporx.com/passolig-kalkti-mi-mac-biletleri-nasil-ve-nereden-alinacak-SXHBQ1123985SXQ)). Bilet şirketleri artık teknolojiyle ve taraftar deneyimiyle de yarışıyor.
- **Bilet fiyatları yükseliyor.** Arena konserlerinde biletler 7.000–32.000 TL aralığında ([TGRT Haber](https://www.tgrthaber.com/aktuel/tarkan-konseri-kac-bilet-satildi-3264846)). Biletix bilet gelirinin ~%30 arttığını bildiriyor ([IQ 2026](https://www.iqmagazine.com/publications/international-ticketing-report-2026/turkiye/)). Pahalı bilette satın alma kararını güven belirliyor.
- **Tiyatro ve salon tarafı büyüyor.** Bubilet'in tiyatro satışları 2023'te 204 bin iken 2025'te 655 bine çıktı ([Webrazzi](https://webrazzi.com/2025/12/11/bubilet-in-2025-performansi-ve-son-uc-yilda-one-cikan-verileri/)).

### Dünyadan örnekler (şirketlerin kendi beyanları)
- **3D Digital Venue:** Tickets.com üzerinden ABD beyzbol ligi MLB'de 25 kulübe hizmet verdiğini söylüyor ([3DDV](https://3ddigitalvenue.com/multiple-mlb-clubs-one-unified-fan-experience-how-3d-digital-venue-helped-standardize-ticketing-across-the-league/)). FC Barcelona'nın bilet ekranında "Powered by 3D Digital Venue" ibaresi var.
- **Pacifa3D:** İlk büyük müşterisi PSG (2013). Sonrasında bilet şirketlerinin kendi müşterileri için Pacifa3D'yi çağırdığını anlatıyor ([röportaj](https://www.post-logic.com/post/interview-pacifa-decision-la-visualisation-3d-au-service-de-la-billetterie)).
- **Ticketmaster 3D Virtual Venue:** Tottenham Hotspur 2022'de bilet akışına ekledi ([Tottenham](https://www.tottenhamhotspur.com/news/1009794/club-becomes-first-in-the-uk-to-launch-ticketmasters-3d-virtual-venue-technology)).
- **TickX:** "View From Seat" kullanan müşterilerinde dönüşümün %7,6 arttığını iddia ediyor; ölçüm yöntemini açıklamıyor ([TickX](https://www.tickx.com/solutions/view-from-seat)).

*Bu örnekler bağımsız ölçüm değildir ve aynı sonucun sizde de çıkacağını göstermez. Bu yüzden ölçülebilir bir pilotla başlamayı öneriyoruz.*

### Nasıl çalışır?
1. **Keşif (1 gün):** Oturma planı, satış ekranı, kısıtlı görüşlü koltuklar ve başarı ölçütü birlikte belirlenir.
2. **Çekim (yalnızca Gerçek görüntü; 0,5–1 gün):** Etkinlik olmayan bir günde, güvenlik prosedürünüze uyularak yapılır. Hassas alanlar maskelenir.
3. **İşleme ve eşleme (3–10 gün):** 3D sahne üretilir; blok ve koltuklar haritanızla eşleştirilir.
4. **Entegrasyon ve yayın (2–4 gün):** Test ortamında denenir, onayınızla canlıya alınır.

### Pilot önerisi
| | |
|---|---|
| Kapsam | 1 mekân / 1 sahne düzeni, numaralı bloklar. **Gerçek görüntü** seviyesi. İsterseniz aynı bilet şirketindeki 2–3 salon daha **Standart** seviyede eklenir; böylece iki seviye yan yana karşılaştırılır. |
| Süre | 90 gün canlı, en az 3 etkinlik |
| Ücret | Kurulum ücretsiz ya da maliyetine; pilot boyunca lisans ücreti yok |
| Karşılığında | Toplu ve anonim satış ve etkileşim verisini ölçme hakkı (KVKK uyumlu). Pilot başarılı olursa, onayınızla isim, logo ve vaka çalışmasını referans olarak kullanma hakkı. |
| Başarı ölçütü | Birlikte yazılır. Örnek: görünüm açılan oturumlarda satın alma oranı, üst kategori payı, görüşle ilgili destek talepleri (mümkünse A/B testiyle) |
| Sonrası | Önceden belirlenmiş lansman fiyatıyla devam ya da cezasız çıkış |

### Sonraki adım
**30 dakikalık bir görüşme:** Size kendi salonunuza benzer bir mekânda canlı demo gösterelim, örnek bilet sayfasında koltuğun sepete düştüğünü görün. Ardından pilot mekânını ve tarihini birlikte seçelim.

İletişim: [unvan] · [kurumsal e-posta] · [web sitesi]
