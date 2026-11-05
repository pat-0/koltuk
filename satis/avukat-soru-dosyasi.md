# Avukat görüşmesi için soru dosyası

**Şirket:** Hyperbaric

**Hazırlanma tarihi:** 31 Ekim 2026

**Konu:** "Koltuktan görünüm" 3D ürünü için sözleşmeler, KVKK, fikri mülkiyet ve patent incelemesi

> Bu dosya, avukatımızın incelemesi için hazırlanmış bir soru listesidir. Belgelerdeki hukuki ifadeler yapay zekâ desteğiyle hazırlanmış taslaklardır; hiçbiri imzalanmamış ve hiçbir karşı tarafa gönderilmemiştir.

---

## 1. Kısaca ne yapıyoruz?

- Stadyum, arena, konser salonu ve tiyatrolar için **"koltuğundan sahayı/sahneyi gör"** özelliği geliştiriyoruz. Bilet alan kişi, koltuğunu seçmeden önce o koltuktan görünümü 3D olarak görüyor.
- Görüntüler, mekân **boşken** 360° kamera (ileride gerekirse lisanslı operatörün drone'u) ile çekiliyor ve "Gaussian splatting" denen yöntemle 3D sahneye dönüştürülüyor.
- Ürün, **bilet şirketlerinin** (Passo, Bubilet, iTicket vb.) ve mekânların bilet satış ekranına **beyaz etiketli** (onların markasıyla) bir eklenti olarak giriyor.
- İlk aşamada **pilot** yapacağız: 1 mekânda 90 gün, kurulum ücretsiz ya da maliyetine. Karşılığında mekândan/bilet şirketinden **toplu ve anonim satış verisini ölçme hakkı** ile **isim, logo ve vaka çalışması (referans) hakkı** istiyoruz.
- Görüntüleyici; blok görüntüleme, koltuk görüntüleme, görünümde kalma süresi ve "bu koltuğu seç" tıklaması gibi **kullanım olaylarını** ölçüyor. Ad, T.C. kimlik no, ödeme bilgisi toplamıyor; geçici bir oturum kimliği kullanıyor.

## 2. İncelenmesini istediğimiz belgeler

| # | Belge | Dosya | Ne için kullanılacak |
|---|---|---|---|
| 1 | Pilot sözleşmesi taslağı | `satis/pilot-sozlesme-taslagi.md` | Bilet şirketi veya mekânla 90 günlük pilot |
| 2 | Mekân çekim izin ve lisans formu | `satis/mekan-cekim-izin-formu.md` | Mekânın imzalayacağı çekim ve yayın izni |
| 3 | Çekim izni talep yazısı | `satis/cekim-izni-talep-yazisi.md` | Mekâna gönderilecek resmi talep |
| 4 | Ekip KVKK aydınlatma metni ve açık rıza formu | `satis/ekip-acik-riza-formu.md` | Çekimde görüntüye girebilecek ekip üyeleri |
| 5 | Drone operatörü şartnamesi | `satis/drone-operator-sartnamesi.md` | Gerekirse kiralanacak lisanslı operatör |
| 6 | İlk temas mesaj şablonları | `satis/satis-plani.md` §5 | Kurumlara e-posta / LinkedIn şirket sayfası mesajı |

## 3. Sorularımız

### A. Sözleşmeler

1. **Belge önceliği:** Pilot sözleşmesi ile mekân izin formu arasında çelişki olursa hangisi geçerli olmalı? Sözleşmelere nasıl bir öncelik maddesi koymalıyız?
2. **Bedelsiz lisans:** Mekâna, kendi görüntülerinden üretilen 3D modeli bedelsiz kullanma hakkı vermenin hukuki ve **vergisel** sonuçları nelerdir? Bedelsiz pilot kurulumunun vergi açısından bir sakıncası var mı?
3. **Lisansın süresi:** Mekânın bilet şirketiyle sözleşmesi biterse, bizim mekâna ve bilet şirketine verdiğimiz kullanım hakkı ne olmalı? Model başka bir bilet şirketine taşınabilir mi?
4. **Sorumluluk sınırı:** Ücretsiz pilotta sorumluluğumuzu belirli bir tutarla sınırlamak ve dolaylı zararları (kâr kaybı, itibar) hariç tutmak geçerli mi? "Kasıt ve ağır kusur hariç" ifadesi yeterli mi?
5. **Ham verinin silinmesi:** Mekân, çekim ham verisinin silinmesini isterse ne kabul etmeliyiz? Arşivleme ve yalnızca iç ar-ge kullanımı makul bir orta yol mu?
6. **Bildirilmeyen kısıtlar:** Mekânın sponsor sözleşmelerinden doğan ve bize bildirmediği kısıtlar nedeniyle üçüncü kişiler talepte bulunursa sorumluluk ve tazmin nasıl düzenlenmeli?
7. **Yetkili mahkeme ve tebligat:** İstanbul mahkemeleri + kurumsal e-posta / KEP / noter düzeni uygun mu?

### B. KVKK (kişisel veriler)

8. **Çalışandan açık rıza:** Ekip üyesi bizim çalışanımızsa, işçi-işveren ilişkisindeki güç dengesizliği nedeniyle açık rıza geçerli sayılır mı? Görüntüsünün işlenmesi ve yayımlanması için hangi hukuki sebebe dayanmalıyız (açık rıza, sözleşmenin ifası, meşru menfaat)? Serbest çalışan ekip üyeleri için ne değişir?
9. **Roller:** Pilotta biz, bilet şirketi ve mekân KVKK bakımından kim **veri sorumlusu**, kim **veri işleyen**? Drone operatörünün rolü ne olmalı? Sözleşmelere hangi veri işleme ekini koymalıyız?
10. **Görüntüleyici analitiği:** Geçici oturum kimliğiyle toplanan kullanım olayları kişisel veri sayılır mı? Bilet sitesinde çerez/onay bandı veya aydınlatma metni gerekir mi; bu yükümlülük bizde mi, bilet şirketinde mi?
11. **Yurt dışında bulut işleme:** Çekim görüntülerini Polycam gibi yurt dışında sunucusu olan bir servisle işlersek, 7499 sayılı Kanun'la değişen **KVKK m.9** kapsamında ne yapmamız gerekir? (Standart sözleşme ve 5 iş günü içinde Kurum'a bildirim yükümlülüğü bizde mi?) Görüntülerde hiç kişi yoksa bu hükümler yine uygulanır mı?
12. **Kişi görünmeyen görüntüler:** Boş mekân görüntüleri, içinde kimse yoksa kişisel veri sayılmaz diye düşünüyoruz. Doğru mu? Plaka, ekran, kâğıt gibi dolaylı bilgiler için ek önlem gerekir mi?
13. **VERBİS:** Bu faaliyet nedeniyle VERBİS kaydı yükümlülüğümüz doğar mı?

### C. Fikri mülkiyet

14. **3D modelin sahipliği:** Mekânın görüntülerinden ürettiğimiz 3D modelin mülkiyeti bizde kalabilir mi? Mekâna yalnızca kullanım hakkı vermek yeterli mi?
15. **Mimari eser:** Binanın içini çekip ticari olarak yayımlamak için mekânın izni yeterli mi, yoksa mimarın (eser sahibinin) ayrıca izni gerekir mi? FSEK'teki kamuya açık yerlerdeki eserlere ilişkin istisna bizim durumumuzda uygulanır mı?
16. **Marka ve sponsor logoları:** Görüntüde kalan sponsor logoları, reklam panoları ve sanat eserleri için ayrı izin gerekir mi, yoksa bulanıklaştırma yeterli mi?
17. **Drone görüntülerinin hak devri:** Operatörden mali hakların devrini nasıl almalıyız? Yazılı olma ve hakların tek tek sayılması şartları için şartnamedeki madde yeterli mi? Manevi haklar (isim belirtme) nasıl düzenlenmeli?
18. **Açık kaynak yazılımlar:** Ürünümüzde Apache-2.0 lisanslı yazılımlar (ör. Brush, nerfstudio/gsplat, three.js-MIT) kullanmayı düşünüyoruz. GPL/AGPL lisanslı araçları (ör. OpenSplat, LichtFeld Studio) yalnızca kendi bilgisayarımızda işleme için kullanırsak ticari üründe bir yükümlülük doğar mı?

### D. Patent

19. **Mevcut patentler:** ABD'de "3D koltuk haritası" ile ilgili patent başvuruları gördük (ör. yayın no **US 2013/0268899** "Method and system for generating 3D seating maps" ve **US 2014/0095223** "Three-dimensional interactive seat map"). Bunların durumu, Türkiye/Avrupa'da karşılıkları ve ürünümüz için risk oluşturup oluşturmadığına dair bir **serbest kullanım (FTO) değerlendirmesi** yaptırmalı mıyız? Yaklaşık maliyeti nedir?
20. **Kendi korumamız:** Kendi yöntemimizi (ör. koltuk planından otomatik göz konumu üretimi, bilet ekranına gömme yöntemi) patent veya başka bir yolla korumak mantıklı mı?

### E. Ticari ileti ve satış

21. **İlk temas mesajları:** Kurumların genel iletişim adreslerine ve LinkedIn şirket sayfalarına göndereceğimiz tanıtım mesajları için İYS kaydı veya önceden onay gerekir mi? B2B e-postada sınırlar neler?
22. **Rakip referansları:** Teklifimizde "FC Barcelona 3D Digital Venue kullanıyor", "Tottenham Ticketmaster'ın ürününü kullanıyor" gibi kamuya açık bilgileri anmamızda sakınca var mı?

### F. Drone (ileride gerekirse)

23. 30 Temmuz 2026'da yürürlüğe giren yeni SHT-İHA talimatına göre, ticari çekim yapacak operatörde en az **P1** lisansı aramamız yeterli mi? Stadyum gibi alanların üzerinde uçuş ve **sigorta zorunluluğu** konusunda ne şart koşmalıyız?

## 4. Sizden beklediğimiz

1. Yukarıdaki sorulara kısa yazılı görüş.
2. Belge 1, 2 ve 4'ün imzaya hazır revize hali.
3. Patent (soru 19) için ayrı bir FTO çalışması gerekiyorsa kapsam ve ücret teklifi.
4. Tüm iş için ücret teklifi ve tahmini süre.

**Öncelik sırası:** Önce belge 2 ve 4 (ilk demo çekimi için gerekli), sonra belge 1 (pilot için), sonra patent.

## 5. Ek bilgi (kaynaklar)

- KVKK m.9 değişikliği: 7499 sayılı Kanun, Resmî Gazete 12.03.2024; m.9 hükümleri 01.06.2024'te yürürlükte. https://www.erdem-erdem.av.tr/bilgi-bankasi/kisisel-verilerin-korunmasi-kanununda-neler-degisti
- SHT-İHA talimatı (30.07.2026): https://www.alomaliye.com/2026/07/30/iha-pilotlari-icin-yeni-lisans-donemi/
- Patent başvuruları: https://patents.justia.com/patent/20130268899 · https://patents.justia.com/patent/20140095223
