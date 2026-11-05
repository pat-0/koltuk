# venue.json: ortak veri formatı (v0.2)

**Makinece doğrulanabilir şema:** `venue.schema.json` (JSON Schema draft 2020-12).
**Doğrulama aracı:** `3d/validate_venue.py`, hem şemayı hem de mantıksal kuralları denetler.

v0.2, v0.1 ile **geriye uyumludur**: bütün yeni alanlar opsiyoneldir. `schemaVersion` için `"0.1"` ve `"0.2"` değerlerinin ikisi de geçerlidir. v0.1 dosyaları bu şemayla doğrulanır. Tek davranış farkı `rotationY` biriminin artık tanımlı olmasıdır (§3.1).

Sorumluluklar aynı kalır: 3D ekibi dosyayı üretir, web görüntüleyici okur.

---

## 1. Koordinat sistemi ve orijin

Ölçü birimi metredir. Y ekseni yukarı bakar ve sağ el kuralı geçerlidir.

| `venue.origin` | Ne zaman (varsayılan) | Orijin | Eksenler | Y = 0 |
|---|---|---|---|---|
| `field-center` | `arena`, `stadium` | Saha merkezi | X = saha uzun ekseni, Z = kısa eksen | Saha zemini |
| `stage-front-center` | `theatre`, `concert-hall` | **Sahne ön kenarının (sahne ağzı / proscenium çizgisinin) orta noktası** | X = sahne ağzı boyunca (seyirciden bakınca sağa +X), **+Z seyirciye doğru**, −Z sahnenin içine | **Sahne döşemesi** |

`origin` alanı yoksa değer `type` alanından türetilir. Tiyatroda parter koltuklarının `eye.y` değeri negatif olabilir, çünkü parter zemini çoğunlukla sahne döşemesinin 0,6–1,1 m altındadır. Tiyatroda tipik `focus` değeri sahne içinde bir noktadır, örneğin `[0, 1.2, -3]`.

Arena veya stadyumda bir konser sahnesi kurulmuşsa orijin yine saha merkezidir. Sahneye bakış `focus` ve `section.focus` ile verilir.

## 2. Göz yüksekliği (netleştirildi)

`eye.y` = **koltuğun bulunduğu basamağın zemini + 1,15 m**. Bu, oturan yetişkinin göz yüksekliğidir ve yaklaşık olarak oturak yüzeyi + 0,70 m'ye denk gelir. Ayakta izlenen tribünlerde ve parterde basamak zemini + 1,60 m kullanılır.

v0.1'deki "oturma yüzeyi + 1,15 m" ifadesi yanlıştı. Kastedilen basamak zeminiydi. Görüntüleyici sandalye modelini `eye.y − 1,15` seviyesine (basamak zemini) oturtmalıdır.

Sabit 360 çekimlerde lens bu yüksekliğe ayarlanır. Sapma olursa `viewpoint.lensHeight` alanına yazılır.

## 3. Alanlar

```jsonc
{
  "schemaVersion": "0.2",
  "venue": {
    "id": "ornek-arena",                 // ^[a-z0-9][a-z0-9-]*$
    "name": "Örnek Arena",
    "type": "arena | stadium | theatre | concert-hall",
    "capacity": 12000,
    "origin": "field-center",            // v0.2, opsiyonel (bkz. §1)
    "focus": [0, 1.0, 0],
    "scene": {
      "kind": "procedural | splat | mesh",
      "url": "scene.sog",                // procedural ise null; files varsa opsiyonel
      "format": "sog",                   // v0.2, opsiyonel: ply | compressed-ply | sog | spz | splat | ksplat | glb | gltf
      "files": [                         // v0.2, opsiyonel: LOD / bölgeli çoklu dosya
        { "url": "scene_lod2.sog", "format": "sog", "lod": 2, "bytes": 4200000, "count": 300000 },
        { "url": "scene_alt_lod0.sog", "format": "sog", "lod": 0, "region": "alt-kat" },
        { "url": "scene_ust_lod0.sog", "format": "sog", "lod": 0, "region": "ust-kat" }
      ],
      "transform": {
        "position": [0, 0, 0],
        "rotationY": 0,                  // DERECE (bkz. §3.1)
        "rotation": [0, 0, 0, 1],        // v0.2, opsiyonel kuaterniyon [x,y,z,w]; varsa rotationY yok sayılır
        "scale": 1
      },
      "params": { }                      // v0.2, YALNIZ kind=procedural iken; serbest nesne (görüntüleyiciye özgü)
    }
  },
  "sections": [
    {
      "id": "A1", "name": "Alt Kat A1", "tier": "lower | middle | upper | vip | floor",
      "priceCategory": "CAT1", "focus": [0, 1.0, 0],
      "rows": [
        { "id": "1", "seats": [
          { "id": "1", "ticketCode": "A1-1-1", "eye": [12.4, 3.1, -18.2], "lookAt": [0, 1.0, 0],
            "obstructed": { "severity": "partial", "reason": "kolon" } }   // v0.2, opsiyonel
        ] }
      ]
    }
  ],
  "viewpoints": [
    {
      "id": "vp-A1-front", "sectionId": "A1",
      "row": "1", "seat": "14",           // v0.2, opsiyonel
      "lensHeight": 1.15,                 // v0.2, opsiyonel: lens merkezi − basamak zemini (m)
      "eye": [12.0, 2.4, -16.5], "lookAt": [0, 1.0, 0],
      "capture": { "file": "ORNK_A1_R1S14_P360_01.jpg", "type": "equirect-360", "takenAt": "2026-11-15T10:30:00+03:00" }
                                          // capture opsiyonel ve null olabilir (planlanmış ama henüz çekilmemiş nokta)
    }
  ]
}
```

### 3.1 Sahne dönüşümü

```
venue_noktası = R · (scale · sahne_noktası) + position
R = rotation (kuaterniyon) varsa o; yoksa R_y(rotationY)
R_y(θ) = [[cos θ, 0, sin θ], [0, 1, 0], [−sin θ, 0, cos θ]]
```

`rotationY` derece cinsindendir. Dönüş +Y ekseni etrafında sağ el kuralıyla yapılır: yukarıdan bakınca saat yönünün tersidir ve +90° değeri +X eksenini −Z'ye çevirir. three.js'te karşılığı `object.rotation.y = rotationY * Math.PI / 180` olur.

Eğimli bir splat hizalanacaksa iki seçenek vardır: tam dönüşü `rotation` kuaterniyonu olarak yazmak ya da eğimi dosyaya pişirmek. Kuaterniyon three.js sırasıyla `[x, y, z, w]` olarak yazılır, birim uzunlukta olmalıdır (tolerans ±0,001).

### 3.2 Sahne dosyaları ve LOD

- Yalnızca `url` verilirse tek dosya demektir (v0.1 davranışı).
- `files` verilirse görüntüleyici önce en büyük `lod` numaralı (en kaba) dosyaları yükler, sonra daha küçük numaralı (daha ayrıntılı) dosyalara geçer.
- Aynı `lod` değerine sahip ve farklı `region` etiketi taşıyan dosyalar birlikte yüklenir. Örnek: alt kat ve üst kat ayrı dosyalar.
- `kind` `splat` veya `mesh` ise `url` ya da `files` alanlarından en az biri zorunludur.
- Dosya yolları `venue.json` dosyasının bulunduğu yere göre görelidir ya da mutlak URL'dir.

### 3.3 `scene.params`

Yalnızca `kind = "procedural"` iken kullanılır. Biçimi serbesttir; web görüntüleyicinin prosedürel kabuğu için çekirdek dikdörtgen, katlar ve çatı gibi değerleri taşır. 3D ekibi bu alanı doldurmaz, yalnızca dosyaya geçirir (`seats_from_plan.py --params-json`). `splat` veya `mesh` sahnede bu alanın bulunması şema hatasıdır.

### 3.4 `obstructed` (kısıtlı görüş)

Alan yoksa veya `false` ise koltukta görüş kısıtı yoktur. Değer `true` ise kısıt vardır ama türü belirtilmemiştir. Ayrıntı vermek için `{ "severity": "partial" | "severe", "reason": "..." }` nesnesi kullanılır. Bilet ekranında "kısıtlı görüş" uyarısı bu alandan türetilir.

### 3.5 Genişletme

Kökte ve `venue`, `section`, `seat` nesnelerinde `x-` önekli alanlar serbesttir (ör. `x-notes`). Bunların dışında tanımsız alan kullanmak şema hatası sayılır; bu kural yazım hatalarını yakalamak için konmuştur.

## 4. Mantıksal kurallar (`validate_venue.py` denetler)

**Hata** olarak işaretlenen kurallar:

- `sections[].id` değerleri benzersizdir.
- Her blokta `rows[].id`, her sırada `seats[].id` benzersizdir.
- `ticketCode` değerleri dosyanın tamamında benzersizdir.
- `viewpoints[].id` değerleri benzersizdir. Her `sectionId` mevcut bir bloğu gösterir. `row`/`seat` verilmişse o koltuk da mevcuttur.
- `eye` makul aralıktadır: |x|, |z| ≤ 400 m ve −30 ≤ y ≤ 120 m.
- Kuaterniyon birim uzunluktadır.

**Uyarı** olarak işaretlenen kurallar:

- `capacity` ile koltuk sayısı arasındaki fark %10'u aşıyor.
- Bir `eye` noktası bakış hedefine 2 m'den yakın.
- Farklı bloklardaki iki koltuk birbirine 0,30 m'den yakın.
- `field-center` orijinli bir mekânda bir koltuğun `eye.y` değeri < 0,5 m.
- `schemaVersion` "0.1" olduğu halde v0.2 alanları kullanılmış.

`ticketCode` eşleşme tablosu değişmedi: `section,row,seat,ticketCode` sütunlu CSV.

## 5. v0.1 → v0.2 değişiklikleri

| # | Değişiklik | Tür | Web etkisi |
|---|---|---|---|
| 1 | `transform.rotationY` birimi **derece** olarak tanımlandı, yönü de belirtildi | Netleştirme | **Gerekli:** `root.rotation.y = rotationY * π/180`. Şu ana kadarki dosyalarda değer 0 olduğu için pratik bir etkisi yok |
| 2 | `transform.rotation` kuaterniyonu eklendi (opsiyonel, rotationY'yi ezer) | Yeni alan | Varsa `quaternion.fromArray()` |
| 3 | Göz yüksekliği: **basamak zemini + 1,15 m** | Netleştirme | **Gerekli:** sandalye tabanı `eye.y − 1,15` (demo şu an `− 1,15 − 0,45` kullanıyor) |
| 4 | `venue.origin`; tiyatro ve konser salonunda orijin = sahne ağzı orta noktası, Y=0 = sahne döşemesi, +Z seyirciye doğru | Yeni alan + tanım | Tiyatroda saha dikdörtgeni çizilmemeli; negatif `eye.y` desteklenmeli |
| 5 | `scene.format`, `scene.files[]` (LOD/bölge/boyut) | Yeni alan | Splat yükleyici |
| 6 | `viewpoints[].row`, `.seat`, `.lensHeight`; `capture` opsiyonel ve null olabilir | Yeni alan | En yakın çekim eşleşmesi kolaylaşır |
| 7 | `seat.obstructed` | Yeni alan | "Kısıtlı görüş" rozeti |
| 8 | `scene.params` (yalnızca procedural, serbest nesne) | Demo uzantısının resmîleşmesi | Değişiklik yok |
| 9 | `x-` öneki dışında tanımsız alanlar şema hatası | Sıkılaştırma | Demo uzantıları `x-` önekiyle yazılmalı |
| 10 | `schemaVersion`: "0.1" veya "0.2"; `ticketCode` opsiyonel (yoksa `blok-sıra-koltuk`) | Netleştirme | Mevcut davranış |
