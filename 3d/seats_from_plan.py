#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seats_from_plan.py — Blok geometrisi CSV'sinden koltuk göz konumlarını hesaplar ve
shared/venue-schema-v0.2.md (v0.2) formatında venue.json üretir
(doğrulama: validate_venue.py / shared/venue.schema.json).

Bağımlılıklar: Python 3.8+, yalnızca standart kütüphane.

KOORDİNAT SİSTEMİ (şema ile aynı)
  Metre, Y yukarı, sağ el kuralı.
  --origin field-center (arena/stadium varsayılanı): orijin saha merkezi, Y=0 saha zemini,
     X = saha uzun ekseni, Z = kısa eksen.
  --origin stage-front-center (theatre/concert-hall varsayılanı): orijin sahne ağzı çizgisinin
     orta noktası, Y=0 sahne döşemesi, X sahne ağzı boyunca, +Z seyirciye doğru (−Z sahne içi).
     Seyirci sahneye bakar → facingDeg 270 (−Z); parter frontHeight genelde negatiftir.
  "Azimut" (derece): XZ düzleminde +X ekseninden +Z eksenine doğru ölçülür;
  azimut θ yönü = (cos θ, 0, sin θ). 0 = +X, 90 = +Z, 180 = -X, 270 = -Z.

BLOK CSV SÜTUNLARI (başlık satırı zorunlu; boş hücre = varsayılan)
  section        Blok kodu. Bilet sistemindeki kodla BİREBİR aynı olmalı (ör. A1).   [zorunlu]
  name           Görünen ad (ör. "Alt Kat A1"). Boşsa section.
  tier           lower | middle | upper | vip | floor                                [zorunlu]
  priceCategory  Fiyat kategorisi (ör. CAT1).
  shape          line | arc                                                          [zorunlu]
  cx, cz         line: 1. sıranın ORTA noktası. arc: yayın merkezi.                   [zorunlu]
  facingDeg      line: izleyicinin baktığı yön (azimut). Sıralar bunun tersine doğru
                 geriye dizilir. arc için kullanılmaz (koltuklar yay merkezine bakar).
  startRadius    arc: 1. sıranın yay yarıçapı (m).
  angleStart,
  angleEnd       arc: yayın başlangıç/bitiş azimutu (derece, angleStart < angleEnd).
  rows           Sıra sayısı.                                                        [zorunlu]
  seatsPerRow    1. sıradaki koltuk sayısı; "auto" veya boş = uzunluk/seatWidth.
                 arc'ta "auto" her sıra için yay uzunluğundan ayrı hesaplanır.
  seatsPerRowIncrement  Her sırada eklenecek koltuk (line için; varsayılan 0).
  length         line: "auto" koltuk sayısı için sıra uzunluğu (m).
  seatWidth      Koltuk aralığı, merkezden merkeze (m). Varsayılan 0.50.
  rowDepth       Sıra derinliği / sıra arası yatay mesafe (m). Varsayılan 0.85.
  riserHeight    Sıralar arası basamak yüksekliği (m). Varsayılan 0.40. Düz zemin = 0.
  frontHeight    1. sıranın basamak ZEMİNİ yüksekliği (m, saha zemini = 0).
  eyeHeight      Basamak zemininden göz yüksekliği (m). Oturarak 1.15, ayakta 1.60.
  rowLabels      numeric (1,2,3..) | alpha (A,B,..,Z,AA..). Varsayılan numeric.
  rowStart       İlk sıra etiketi sayısal başlangıcı (varsayılan 1).
  seatOrder      ltr | rtl. ltr: oturan izleyicinin SOLUNDAKİ uç koltuk = 1. Varsayılan ltr.
  focusX,focusY,focusZ  Opsiyonel blok bakış hedefi (section.focus).

  Göz konumu = koltuk sırası çizgisi üzerindeki nokta, y = frontHeight + (sıraİndeksi × riserHeight) + eyeHeight.
  (Koltuğun yatay olarak ~10 cm arkadaki gerçek göz konumu ihmal edilir.)

BİLET KODU EŞLEME
  --tickets eslesme.csv  (sütunlar: section,row,seat,ticketCode)
  Eşleşmeyen koltuklara --ticket-pattern ile kod üretilir (varsayılan "{section}-{row}-{seat}").
  --strict: eşleşmeyen koltuk veya geometride olmayan bilet kaydı varsa hata ver.

KISITLI GÖRÜŞ (v0.2 seat.obstructed)
  --obstructed kisitli.csv (sütunlar: section,row,seat,severity,reason)
     row/seat "*" = tümü; seat aralık olabilir ("1-4" veya "1-4;9;12"). severity: partial | severe
     (boş = partial). Geometride karşılığı olmayan satır HATA verir.

ÇEKİM NOKTALARI
  --viewpoints cekilen.csv (sütunlar: id,sectionId,row,seat,file,type,takenAt[,lensHeight,eyeX,eyeY,eyeZ])
     Göz konumu verilmezse ilgili koltuğun göz konumu kullanılır. lensHeight boşsa bloğun eyeHeight'ı yazılır.
     file boşsa capture null yazılır (planlanmış, çekilmemiş nokta).

SAHNE (v0.2)
  --scene-transform 'px,py,pz,rotationY,scale' — rotationY DERECE.
  --scene-rotation 'x,y,z,w' — opsiyonel kuaterniyon (varsa rotationY'yi ezer).
  --scene-format ply|compressed-ply|sog|spz|splat|ksplat|glb|gltf
  --scene-file 'url[,lod[,region]]' (tekrarlanabilir) — LOD/bölgeli çoklu dosya.
  --params-json dosya.json — procedural sahne için web görüntüleyici parametreleri (scene.params).
  --capture-plan plan.csv : her blok için ön/orta/arka sıra (geniş bloklarda sol/sağ da)
     önerilen çekim noktalarını ve dosya adlarını yazar (venue.json'a GİRMEZ; çekilmemiş noktalar).

Örnek:
  python3 seats_from_plan.py ornek-bloklar.csv -o ornek-arena.venue.json \\
      --venue-id ornek-arena --name "Örnek Arena" --type arena \\
      --capture-plan ornek-arena.cekim-plani.csv --seats-csv ornek-arena.koltuklar.csv
"""
import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict

TIERS = {"lower", "middle", "upper", "vip", "floor"}
DEFAULTS = {
    "seatWidth": 0.50, "rowDepth": 0.85, "riserHeight": 0.40, "frontHeight": 0.0,
    "eyeHeight": 1.15, "seatsPerRowIncrement": 0, "rowStart": 1,
}


def fnum(row, key, default=None, required=False, line=0):
    """CSV hücresini float'a çevirir; boşsa varsayılan."""
    v = (row.get(key) or "").strip()
    if v == "":
        if required:
            raise ValueError(f"satır {line}: '{key}' zorunlu")
        return default
    try:
        return float(v)
    except ValueError:
        raise ValueError(f"satır {line}: '{key}' sayı olmalı, '{v}' verildi")


def row_label(i, mode, start):
    """i: 0 tabanlı sıra indeksi → sıra etiketi."""
    n = i + start
    if mode == "alpha":
        s = ""
        while n > 0:
            n, r = divmod(n - 1, 26)
            s = chr(65 + r) + s
        return s
    return str(n)


def r2(v):
    return round(v + 0.0, 3)


def section_seats(spec):
    """Bir blok için [(sıraEtiketi, [(koltukNo, (x,y,z)), ...]), ...] üretir."""
    out = []
    w = spec["seatWidth"]
    for ri in range(spec["rows"]):
        label = row_label(ri, spec["rowLabels"], spec["rowStart"])
        y = spec["frontHeight"] + ri * spec["riserHeight"] + spec["eyeHeight"]
        pts = []
        if spec["shape"] == "line":
            f = math.radians(spec["facingDeg"])
            fx, fz = math.cos(f), math.sin(f)
            rx, rz = -fz, fx  # izleyicinin sağ vektörü (ileri × yukarı)
            ox = spec["cx"] - fx * ri * spec["rowDepth"]
            oz = spec["cz"] - fz * ri * spec["rowDepth"]
            if spec["seatsPerRow"] is None:
                n = int(math.floor(spec["length"] / w))
            else:
                n = int(spec["seatsPerRow"] + ri * spec["seatsPerRowIncrement"])
            for k in range(n):  # k=0 → en solda
                t = (k - (n - 1) / 2.0) * w
                pts.append((ox + rx * t, y, oz + rz * t))
        else:  # arc
            r = spec["startRadius"] + ri * spec["rowDepth"]
            a0, a1 = math.radians(spec["angleStart"]), math.radians(spec["angleEnd"])
            arc_len = r * (a1 - a0)
            if spec["seatsPerRow"] is None:
                n = int(math.floor(arc_len / w))
            else:
                n = int(spec["seatsPerRow"] + ri * spec["seatsPerRowIncrement"])
            if n > 0:
                # Koltuklar yayın ortasına ortalanır, aralık = seatWidth (yay boyunca)
                dth = w / r
                mid = (a0 + a1) / 2.0
                # İçe bakan izleyici için azimut ARTTIKÇA sola gidilir → soldaki = en büyük açı
                for k in range(n):
                    th = mid + ((n - 1) / 2.0 - k) * dth
                    pts.append((spec["cx"] + r * math.cos(th), y, spec["cz"] + r * math.sin(th)))
        if spec["seatOrder"] == "rtl":
            pts.reverse()
        seats = [(str(k + 1), p) for k, p in enumerate(pts)]
        out.append((label, seats))
    return out


def read_blocks(path):
    specs = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        for i, row in enumerate(rd, start=2):
            if not any((v or "").strip() for v in row.values()):
                continue
            sid = (row.get("section") or "").strip()
            if sid.startswith("#"):
                continue  # yorum satırı
            if not sid:
                raise ValueError(f"satır {i}: 'section' boş")
            shape = (row.get("shape") or "").strip().lower()
            if shape not in ("line", "arc"):
                raise ValueError(f"satır {i}: shape 'line' veya 'arc' olmalı")
            tier = (row.get("tier") or "").strip().lower()
            if tier not in TIERS:
                raise ValueError(f"satır {i}: tier {sorted(TIERS)} içinden olmalı, '{tier}' verildi")
            spr = (row.get("seatsPerRow") or "").strip().lower()
            spec = {
                "section": sid,
                "name": (row.get("name") or "").strip() or sid,
                "tier": tier,
                "priceCategory": (row.get("priceCategory") or "").strip() or None,
                "shape": shape,
                "cx": fnum(row, "cx", required=True, line=i),
                "cz": fnum(row, "cz", required=True, line=i),
                "rows": int(fnum(row, "rows", required=True, line=i)),
                "seatsPerRow": None if spr in ("", "auto") else int(float(spr)),
                "rowLabels": (row.get("rowLabels") or "numeric").strip().lower() or "numeric",
                "seatOrder": (row.get("seatOrder") or "ltr").strip().lower() or "ltr",
            }
            for k, d in DEFAULTS.items():
                spec[k] = fnum(row, k, d, line=i)
            spec["rowStart"] = int(spec["rowStart"])
            if shape == "line":
                spec["facingDeg"] = fnum(row, "facingDeg", required=True, line=i)
                spec["length"] = fnum(row, "length", None, line=i)
                if spec["seatsPerRow"] is None and spec["length"] is None:
                    raise ValueError(f"satır {i}: line blokta seatsPerRow veya length gerekli")
            else:
                spec["startRadius"] = fnum(row, "startRadius", required=True, line=i)
                spec["angleStart"] = fnum(row, "angleStart", required=True, line=i)
                spec["angleEnd"] = fnum(row, "angleEnd", required=True, line=i)
                if spec["angleEnd"] <= spec["angleStart"]:
                    raise ValueError(f"satır {i}: angleEnd > angleStart olmalı (gerekirse 360 ekleyin)")
            if spec["rows"] < 1:
                raise ValueError(f"satır {i}: rows >= 1 olmalı")
            if spec["rowLabels"] not in ("numeric", "alpha"):
                raise ValueError(f"satır {i}: rowLabels numeric|alpha olmalı")
            if spec["seatOrder"] not in ("ltr", "rtl"):
                raise ValueError(f"satır {i}: seatOrder ltr|rtl olmalı")
            fx, fy, fz = (fnum(row, k, None, line=i) for k in ("focusX", "focusY", "focusZ"))
            spec["focus"] = [fx, fy, fz] if None not in (fx, fy, fz) else None
            specs.append(spec)
    ids = [s["section"] for s in specs]
    dup = {x for x in ids if ids.count(x) > 1}
    if dup:
        raise ValueError(f"tekrarlanan blok kodu: {sorted(dup)}")
    return specs


def read_tickets(path):
    m = {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        need = {"section", "row", "seat", "ticketCode"}
        if not need.issubset(set(rd.fieldnames or [])):
            raise ValueError(f"{path}: sütunlar {sorted(need)} olmalı")
        for r in rd:
            key = (r["section"].strip(), r["row"].strip(), r["seat"].strip())
            if key in m:
                raise ValueError(f"{path}: tekrarlanan koltuk {key}")
            m[key] = r["ticketCode"].strip()
    return m


def parse_seat_spec(spec):
    """'*' → None (tümü); '1-4;9' → {'1','2','3','4','9'}"""
    spec = spec.strip()
    if spec in ("", "*"):
        return None
    out = set()
    for part in spec.replace(",", ";").split(";"):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(str(i) for i in range(int(a), int(b) + 1))
        elif part:
            out.add(part)
    return out


def read_obstructed(path):
    """Kısıtlı görüş listesi: section,row,seat,severity,reason"""
    items = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rd = csv.DictReader(fh)
        if not {"section", "row", "seat"}.issubset(set(rd.fieldnames or [])):
            raise ValueError(f"{path}: en az section,row,seat sütunları gerekli")
        for i, r in enumerate(rd, start=2):
            sev = (r.get("severity") or "partial").strip() or "partial"
            if sev not in ("partial", "severe"):
                raise ValueError(f"{path} satır {i}: severity partial|severe olmalı")
            row = (r.get("row") or "*").strip() or "*"
            items.append({"section": r["section"].strip(), "row": row, "seatSpec": r["seat"].strip() or "*",
                          "seats": parse_seat_spec(r["seat"]), "severity": sev,
                          "reason": (r.get("reason") or "").strip(), "hits": 0})
    return items


def match_obstructed(items, section, row, seat):
    """Koltuğa uyan İLK kaydı döndürür (severe öncelikli)."""
    best = None
    for o in items:
        if o["section"] != section or (o["row"] != "*" and o["row"] != row):
            continue
        if o["seats"] is not None and seat not in o["seats"]:
            continue
        o["hits"] += 1
        if best is None or (o["severity"] == "severe" and best["severity"] != "severe"):
            best = o
    if not best:
        return None
    ob = {"severity": best["severity"]}
    if best["reason"]:
        ob["reason"] = best["reason"]
    return ob


def check_overlap(all_pts, min_dist):
    """Farklı bloklardaki koltuklar min_dist'ten yakınsa çakışma say (ızgara kovaları ile)."""
    cell = max(min_dist, 0.01)
    grid = defaultdict(list)
    for sec, p in all_pts:
        grid[(int(math.floor(p[0] / cell)), int(math.floor(p[1] / cell)), int(math.floor(p[2] / cell)))].append((sec, p))
    hits = defaultdict(int)
    for (gx, gy, gz), items in grid.items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for sec2, q in grid.get((gx + dx, gy + dy, gz + dz), []):
                        for sec, p in items:
                            if sec < sec2 and math.dist(p, q) < min_dist:
                                hits[(sec, sec2)] += 1
    return hits


def main():
    ap = argparse.ArgumentParser(
        description="Blok geometrisi CSV'sinden koltuk göz konumlarını hesaplayıp venue.json (şema v0.2) üretir. "
                    "CSV sütunları için betiğin başındaki açıklamaya bakın.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("blocks", help="Blok geometrisi CSV dosyası.")
    ap.add_argument("-o", "--out", required=True, help="Çıktı venue.json yolu.")
    ap.add_argument("--venue-id", default="ornek-arena")
    ap.add_argument("--name", default="Örnek Arena")
    ap.add_argument("--type", default="arena", choices=["arena", "stadium", "theatre", "concert-hall"])
    ap.add_argument("--capacity", type=int, default=None, help="Boşsa üretilen koltuk sayısı yazılır.")
    ap.add_argument("--focus", default="0,1.0,0", help="Varsayılan bakış hedefi x,y,z (tiyatroda ör. '0,1.2,-3').")
    ap.add_argument("--origin", default=None, choices=["field-center", "stage-front-center"],
                    help="Orijin tanımı. Boşsa türden: arena/stadium → field-center, theatre/concert-hall → stage-front-center.")
    ap.add_argument("--scene-kind", default="procedural", choices=["procedural", "splat", "mesh"])
    ap.add_argument("--scene-url", default=None, help="splat/mesh dosya yolu (procedural ise boş).")
    ap.add_argument("--scene-transform", default="0,0,0,0,1",
                    help="Sahne dönüşümü 'px,py,pz,rotationY(DERECE),scale' (hizalama sonrası değerler).")
    ap.add_argument("--scene-rotation", default=None, help="Opsiyonel kuaterniyon 'x,y,z,w' (rotationY'yi ezer).")
    ap.add_argument("--scene-format", default=None,
                    choices=["ply", "compressed-ply", "sog", "spz", "splat", "ksplat", "glb", "gltf"])
    ap.add_argument("--scene-file", action="append", default=[], help="'url[,lod[,region]]' — tekrarlanabilir.")
    ap.add_argument("--params-json", default=None, help="procedural sahne için scene.params JSON dosyası.")
    ap.add_argument("--obstructed", default=None, help="Kısıtlı görüş listesi CSV (section,row,seat,severity,reason).")
    ap.add_argument("--tickets", default=None, help="section,row,seat,ticketCode CSV'si.")
    ap.add_argument("--ticket-pattern", default="{section}-{row}-{seat}",
                    help="Eşlemede olmayan koltuklar için kod deseni.")
    ap.add_argument("--strict", action="store_true", help="Eksik/fazla bilet eşlemesinde hata ver.")
    ap.add_argument("--viewpoints", default=None, help="Çekilmiş noktalar CSV'si (id,sectionId,row,seat,file,type,takenAt).")
    ap.add_argument("--capture-plan", default=None, help="Önerilen çekim noktaları CSV çıktısı.")
    ap.add_argument("--venue-code", default="ORNK", help="Çekim planı dosya adlarındaki mekân kısaltması.")
    ap.add_argument("--seats-csv", default=None,
                    help="Düz koltuk listesi CSV çıktısı (section,row,seat,ticketCode,x,y,z) — bilet eşleme şablonu.")
    ap.add_argument("--min-dist", type=float, default=0.30, help="Bloklar arası çakışma kontrol mesafesi (m).")
    ap.add_argument("--indent", type=int, default=None, help="JSON girintisi (boş = sıkıştırılmış, web için).")
    args = ap.parse_args()

    try:
        specs = read_blocks(args.blocks)
        tickets = read_tickets(args.tickets) if args.tickets else {}
        focus = [float(v) for v in args.focus.split(",")]
        tr = [float(v) for v in args.scene_transform.split(",")]
        if len(focus) != 3 or len(tr) != 5:
            raise ValueError("--focus 3, --scene-transform 5 değer almalı")
        quat = None
        if args.scene_rotation:
            quat = [float(v) for v in args.scene_rotation.split(",")]
            nq = math.sqrt(sum(v * v for v in quat))
            if len(quat) != 4 or nq == 0:
                raise ValueError("--scene-rotation 4 değer (x,y,z,w) almalı")
            quat = [round(v / nq, 9) for v in quat]
        files = []
        for spec_ in args.scene_file:
            parts = [p.strip() for p in spec_.split(",")]
            f = {"url": parts[0]}
            if args.scene_format:
                f["format"] = args.scene_format
            if len(parts) > 1 and parts[1]:
                f["lod"] = int(parts[1])
            if len(parts) > 2 and parts[2]:
                f["region"] = parts[2]
            files.append(f)
        params = None
        if args.params_json:
            with open(args.params_json, encoding="utf-8") as fh:
                params = json.load(fh)
            if not isinstance(params, dict):
                raise ValueError("--params-json bir JSON nesnesi olmalı")
        obstructed = read_obstructed(args.obstructed) if args.obstructed else []
    except (ValueError, OSError, json.JSONDecodeError) as e:
        sys.exit(f"HATA: {e}")
    if args.scene_kind != "procedural" and not (args.scene_url or files):
        sys.exit("HATA: splat/mesh sahne için --scene-url veya --scene-file gerekli.")
    if args.scene_kind != "procedural" and params is not None:
        sys.exit("HATA: --params-json yalnız procedural sahnede kullanılabilir.")
    if args.scene_kind == "procedural" and (args.scene_url or files):
        sys.exit("HATA: procedural sahnede --scene-url/--scene-file kullanılmaz.")
    origin = args.origin or ("stage-front-center" if args.type in ("theatre", "concert-hall") else "field-center")
    eye_h = {sp["section"]: sp["eyeHeight"] for sp in specs}

    sections, flat, all_pts, used_tickets = [], [], [], set()
    seat_index = {}
    missing = 0
    stats = []
    for spec in specs:
        rows_out, count = [], 0
        geo = section_seats(spec)
        for label, seats in geo:
            seats_out = []
            for sno, (x, y, z) in seats:
                key = (spec["section"], label, sno)
                if key in tickets:
                    code = tickets[key]
                    used_tickets.add(key)
                else:
                    missing += 1
                    code = args.ticket_pattern.format(section=spec["section"], row=label, seat=sno)
                eye = [r2(x), r2(y), r2(z)]
                seat = {"id": sno, "ticketCode": code, "eye": eye}
                ob = match_obstructed(obstructed, spec["section"], label, sno)
                if ob:
                    seat["obstructed"] = ob
                seats_out.append(seat)
                flat.append((spec["section"], label, sno, code, *eye))
                all_pts.append((spec["section"], (x, y, z)))
                seat_index[key] = eye
                count += 1
            rows_out.append({"id": label, "seats": seats_out})
        sec = {"id": spec["section"], "name": spec["name"], "tier": spec["tier"]}
        if spec["priceCategory"]:
            sec["priceCategory"] = spec["priceCategory"]
        if spec["focus"]:
            sec["focus"] = spec["focus"]
        sec["rows"] = rows_out
        sections.append(sec)
        stats.append((spec, geo, count))

    extra = set(tickets) - used_tickets
    if tickets:
        print(f"Bilet eşleme: {len(used_tickets)} eşleşti, {missing} koltuk desenle üretildi, "
              f"{len(extra)} kayıt geometride yok.")
        for k in sorted(extra)[:10]:
            print(f"  geometride olmayan: {k}", file=sys.stderr)
        if args.strict and (missing or extra):
            sys.exit("HATA (--strict): bilet eşlemesi eksiksiz değil.")

    viewpoints = []
    if args.viewpoints:
        with open(args.viewpoints, newline="", encoding="utf-8-sig") as fh:
            for i, r in enumerate(csv.DictReader(fh), start=2):
                key = (r["sectionId"].strip(), (r.get("row") or "").strip(), (r.get("seat") or "").strip())
                if all((r.get(k) or "").strip() for k in ("eyeX", "eyeY", "eyeZ")):
                    eye = [float(r["eyeX"]), float(r["eyeY"]), float(r["eyeZ"])]
                elif key in seat_index:
                    eye = seat_index[key]
                else:
                    sys.exit(f"HATA: {args.viewpoints} satır {i}: koltuk {key} bulunamadı ve eyeX/Y/Z yok.")
                vp = {"id": r["id"].strip(), "sectionId": key[0]}
                if key[1] and key[2]:
                    vp["row"], vp["seat"] = key[1], key[2]
                lh = (r.get("lensHeight") or "").strip()
                if lh:
                    vp["lensHeight"] = float(lh)
                elif key in seat_index:
                    vp["lensHeight"] = eye_h.get(key[0])
                vp["eye"], vp["lookAt"] = eye, focus
                if (r.get("file") or "").strip():
                    vp["capture"] = {"file": r["file"].strip(), "type": (r.get("type") or "equirect-360").strip()}
                    if (r.get("takenAt") or "").strip():
                        vp["capture"]["takenAt"] = r["takenAt"].strip()
                else:
                    vp["capture"] = None
                viewpoints.append(vp)

    unused = [o for o in obstructed if not o["hits"]]
    if unused:
        sys.exit("HATA: kısıtlı görüş listesinde geometride karşılığı olmayan satır(lar): "
                 + "; ".join(f"{o['section']}/{o['row']}/{o['seatSpec']}" for o in unused))

    total = len(flat)
    scene = {"kind": args.scene_kind, "url": args.scene_url if args.scene_kind != "procedural" else None}
    if args.scene_format and args.scene_kind != "procedural":
        scene["format"] = args.scene_format
    if files:
        scene["files"] = files
    scene["transform"] = {"position": tr[:3], "rotationY": tr[3], "scale": tr[4]}
    if quat:
        scene["transform"]["rotation"] = quat
    if params is not None:
        scene["params"] = params
    venue = {
        "schemaVersion": "0.2",
        "venue": {
            "id": args.venue_id, "name": args.name, "type": args.type,
            "capacity": args.capacity if args.capacity is not None else total,
            "origin": origin,
            "focus": focus,
            "scene": scene,
        },
        "sections": sections,
        "viewpoints": viewpoints,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        if args.indent:
            json.dump(venue, fh, ensure_ascii=False, indent=args.indent)
        else:
            json.dump(venue, fh, ensure_ascii=False, separators=(",", ":"))

    if args.seats_csv:
        with open(args.seats_csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["section", "row", "seat", "ticketCode", "x", "y", "z"])
            w.writerows(flat)

    if args.capture_plan:
        with open(args.capture_plan, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["id", "sectionId", "position", "row", "seat", "eyeX", "eyeY", "eyeZ",
                        "lensHeightAboveTread_m", "suggestedFile"])
            for spec, geo, _ in stats:
                nrows = len(geo)
                picks = [("on", 0), ("orta", nrows // 2), ("arka", nrows - 1)]
                seen = set()
                for pos, ri in picks:
                    if ri in seen:
                        continue
                    seen.add(ri)
                    label, seats = geo[ri]
                    if not seats:
                        continue
                    cols = [("", len(seats) // 2)]
                    # Geniş bloklarda (>24 koltuk) orta sırada sol ve sağ uçlara da nokta
                    if pos == "orta" and len(seats) > 24:
                        cols = [("-sol", 2), ("", len(seats) // 2), ("-sag", len(seats) - 3)]
                    for suf, si in cols:
                        sno, (x, y, z) = seats[si]
                        stem = f"{args.venue_code}_{spec['section']}_R{label}S{sno}_P360_01"
                        w.writerow([f"vp-{spec['section']}-{pos}{suf}", spec["section"], pos + suf, label, sno,
                                    r2(x), r2(y), r2(z), spec["eyeHeight"], stem + ".jpg"])

    # Özet
    n_obs = sum(1 for sec in sections for r in sec["rows"] for st in r["seats"] if "obstructed" in st)
    print(f"Şema v0.2 | orijin {origin} | {len(sections)} blok, {total} koltuk ({n_obs} kısıtlı görüş), "
          f"{len(viewpoints)} viewpoint -> {args.out} ({os.path.getsize(args.out) / 1024:.0f} KB)")
    by_tier = defaultdict(int)
    for spec, _, c in stats:
        by_tier[spec["tier"]] += c
    print("Kat bazında: " + ", ".join(f"{k}={v}" for k, v in sorted(by_tier.items())))
    for spec, geo, c in stats:
        ys = [p[1] for _, s in geo for _, p in s]
        print(f"  {spec['section']:>4} {spec['tier']:<6} {spec['shape']:<4} sıra={len(geo):>2} koltuk={c:>4} "
              f"göz y={min(ys):.2f}..{max(ys):.2f} m")
    hits = check_overlap(all_pts, args.min_dist)
    if hits:
        print(f"UYARI: bloklar arası {sum(hits.values())} koltuk çifti {args.min_dist} m'den yakın:", file=sys.stderr)
        for (a, b), n in sorted(hits.items()):
            print(f"  {a} ↔ {b}: {n}", file=sys.stderr)
    else:
        print(f"Çakışma kontrolü: bloklar arası {args.min_dist} m'den yakın koltuk yok.")


if __name__ == "__main__":
    main()
