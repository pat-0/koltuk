# venue.json — ortak veri formatı (v0.1)

3D ekibi (çekim/işleme) bu dosyayı üretir, web görüntüleyici bu dosyayı okur.
Koordinat sistemi: metre, Y yukarı, sağ el kuralı. Orijin = saha/sahne merkezi zemin seviyesi.
Saha uzun ekseni X, kısa ekseni Z.

```json
{
  "schemaVersion": "0.1",
  "venue": {
    "id": "ornek-arena",
    "name": "Örnek Arena",
    "type": "arena | stadium | theatre | concert-hall",
    "capacity": 12000,
    "focus": [0, 1.0, 0],              // varsayılan bakış hedefi (saha/sahne merkezi)
    "scene": {
      "kind": "procedural | splat | mesh",
      "url": "scene.splat",            // splat/mesh ise dosya yolu; procedural ise null
      "transform": { "position": [0,0,0], "rotationY": 0, "scale": 1 }
    }
  },
  "sections": [
    {
      "id": "A1",                      // bilet sistemindeki blok kodu ile birebir aynı olmalı
      "name": "Alt Kat A1",
      "tier": "lower | middle | upper | vip | floor",
      "priceCategory": "CAT1",
      "focus": [0, 1.0, 0],            // opsiyonel: blok için farklı bakış hedefi
      "rows": [
        {
          "id": "1",
          "seats": [
            {
              "id": "1",
              "ticketCode": "A1-1-1",    // bilet sistemindeki koltuk kodu
              "eye": [12.4, 3.1, -18.2], // oturan izleyicinin göz konumu (oturma yüksekliği ~1.15 m eklenmiş)
              "lookAt": [0, 1.0, 0]      // opsiyonel, yoksa section.focus / venue.focus
            }
          ]
        }
      ]
    }
  ],
  "viewpoints": [
    {
      "id": "vp-A1-front",
      "sectionId": "A1",
      "eye": [12.0, 2.4, -16.5],
      "lookAt": [0, 1.0, 0],
      "capture": { "file": "A1_front.jpg", "type": "equirect-360", "takenAt": "2026-11-15T10:30:00+03:00" }
    }
  ]
}
```

Kurallar
- Çekilen her nokta `viewpoints` içine girer. Arada kalan koltukların `eye` değeri satır/koltuk geometrisinden hesaplanır.
- `ticketCode` müşterinin bilet sisteminden gelir; eşleşme tablosu CSV olarak da tutulur: `section,row,seat,ticketCode`.
- Göz yüksekliği: oturma yüzeyi + 1.15 m (ayakta tribünlerde + 1.60 m).
