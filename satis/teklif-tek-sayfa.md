# [Ürün adı]: Bilet alırken koltuğundan sahayı ve sahneyi gör

**[Kurum adı] için pilot teklifi** · Hyperbaric (Türkiye) · [Tarih]

---

### Problem
Bilet alan kişi kategori ve fiyatı görüyor ama **o koltuktan ne göreceğini** görmüyor. Sonuçları:
- Pahalı kategorilerde tereddüt yaşanıyor; kullanıcı sepeti terk ediyor ya da "garanti olsun" diyerek ucuz bloğa yöneliyor.
- "Kolon arkasıymış", "sahne yandan görünüyor" gibi şikâyetler ve iade talepleri çağrı merkezine yük oluyor.
- Taraftarlar ve izleyiciler forumlarda ve sosyal medyada tahmini görseller arıyor. Türkiye'de bu ihtiyaca gerçek çekimle cevap veren profesyonel bir çözüm bulamadık.

### Çözüm
[Ürün adı], **bilet ekranınıza beyaz etiketli olarak eklenen** bir 3D koltuk görünümüdür. Kullanıcı bloğu veya koltuğu seçer, sonra **o noktadan sahaya ya da sahneye 360° bakar**, hatta yakınlaşabilir.
- **Gerçek çekim:** Görüntüler AI çizimi değil; mekânın kendisinde 360° kamerayla çekilir ve Gaussian splatting ile 3D'ye dönüştürülür.
- **Sizin markanız:** Görünüm sizin renklerinizi ve logonuzu taşır; satış akışınızdan çıkmaz.
- **Hafif entegrasyon:** Embed veya SDK ile koltuk haritanıza bağlanır. Mobilde ve masaüstünde çalışır.
- **Ölçüm paneli:** Koltuk görünümünü açan oturumlar, satın alma oranı ve kategori dağılımı toplu ve anonim olarak raporlanır.

### Neden şimdi?
- **Passolig zorunluluğu 2025–26 sezonuyla kalktı.** Maçlara çipli kimlikle girilebiliyor; kulüpler satış ve giriş kurallarını anlaştıkları bilet şirketleriyle birlikte belirliyor ([Sporx](https://www.sporx.com/passolig-kalkti-mi-mac-biletleri-nasil-ve-nereden-alinacak-SXHBQ1123985SXQ)). Kulüpler artık bilet şirketlerini **teknolojiye ve taraftar deneyimine göre seçebiliyor.** Örneğin Fenerbahçe, 2025'te birkaç sağlayıcıyla görüştükten sonra sözleşme yeniledi ([Fanatik](https://www.fanatik.com.tr/fenerbahce/fenerbahceden-iddialara-yanit-soz-konusu-degil-2617989)).
- **Konser pazarı büyüyor ve bilet fiyatları yükseliyor.** Örnekler:
  - Biletix bilet gelirinin ~%30 arttığını bildiriyor ([IQ 2026](https://www.iqmagazine.com/publications/international-ticketing-report-2026/turkiye/)).
  - Bubilet 2025'in ilk 11 ayında 4,4 milyon bilet sattı ([Webrazzi](https://webrazzi.com/2025/12/11/bubilet-in-2025-performansi-ve-son-uc-yilda-one-cikan-verileri/)).
  - Arena konserlerinde biletler 7.000–32.000 TL aralığında ([TGRT Haber](https://www.tgrthaber.com/aktuel/tarkan-konseri-kac-bilet-satildi-3264846)).

  Pahalı biletlerde güven, dönüşümü belirliyor.
- **İlk olan siz olun.** Türkiye'de bilet ekranına entegre, gerçek çekime dayalı bir koltuk görünümü bulamadık.

### Dünyadan örnekler (şirketlerin kendi beyanları)
- **FC Barcelona:** Resmi bilet ekranındaki koltuk görünümü "Powered by 3D Digital Venue" ibaresi taşıyor. Barselona merkezli 3DDV, 2020'de 17 ülkede 400'den fazla müşterisi olduğunu açıklamıştı ([Sports Venue Business](https://sportsvenuebusiness.com/2020/07/18/3d-digital-venue-3ddv/)).
- **Tottenham Hotspur:** 2022'de Ticketmaster 3D Virtual Venue'yu bilet akışına ekleyen ilk İngiliz kulübü oldu. Ticketmaster teknolojinin **dönüşümü artırdığını söylüyor**; bağımsız bir rakam yayımlanmadı ([Tottenham](https://www.tottenhamhotspur.com/news/1009794/club-becomes-first-in-the-uk-to-launch-ticketmasters-3d-virtual-venue-technology)).
- **Pacifa3D:** PSG, Ajax, Paris Operası ve Roland-Garros gibi kurumlar için benzer görünümler üretiyor ([pacifa3d.com](https://pacifa3d.com/)).

*Bu örnekler sektör eğilimini gösterir; sonuçların sizde de aynı olacağı anlamına gelmez. Bu yüzden önce ölçülebilir bir pilot öneriyoruz.*

### Nasıl çalışır? (4 adım, ~2–3 hafta)
1. **Keşif (1 gün):** Oturma planınızı, satış ekranınızı ve başarı ölçütlerini birlikte belirleriz.
2. **Çekim (1–2 gün):** Etkinlik olmayan bir günde, güvenlik prosedürlerinize uyarak mekânda 360° çekim yaparız.
3. **İşleme (3–10 gün):** 3D model oluşturulur, bloklar ve koltuklar haritanızla eşleştirilir.
4. **Entegrasyon ve yayın (2–4 gün):** Embed veya SDK test ortamında denenir, onayınızla canlıya alınır.

### Pilot önerisi
| | |
|---|---|
| Kapsam | 1 mekân / 1 sahne düzeni, tüm numaralı bloklar |
| Süre | 90 gün canlı, en az 3 etkinlik |
| Ücret | Kurulum **ücretsiz** veya maliyetine; pilot boyunca lisans ücreti yok |
| Karşılığında | Toplu ve anonim satış ve etkileşim verisini ölçme hakkı (KVKK uyumlu); pilot başarılı olursa isminizi, logonuzu ve vaka çalışmasını (sizin onayınızla) referans olarak kullanma hakkı |
| Başarı ölçütü | Birlikte yazılır. Örnek: koltuk görünümü açılan oturumlarda satın alma oranı ve üst kategori payı |
| Sonrası | Önceden belirlenmiş lansman fiyatıyla devam ya da cezasız çıkış |

### Sonraki adım
**30 dakikalık bir görüşmede** size kendi mekânınıza benzer bir salonda canlı demo gösterelim. Pilot için uygun mekânı ve tarihi birlikte seçelim.

İletişim: [Ad Soyad, unvan] · [kurumsal e-posta] · [telefon] · [web sitesi]
