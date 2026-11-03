#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
equirect_to_persp.py — Equirectangular (2:1) 360 kareyi N adet perspektif (pinhole)
görüntüye böler. COLMAP / Nerfstudio / Postshot gibi perspektif kamera bekleyen
araçlara 360 veri vermek için kullanılır.

Bağımlılıklar:
  - Python 3.8+
  - numpy, opencv-python (veya opencv-python-headless)
    pip install numpy opencv-python-headless   (gerekirse --break-system-packages)

Koordinat kuralları (venue-schema ile uyumlu, Y yukarı, sağ el):
  - Equirect görüntünün yatay merkezi = boylam 0 = kameranın "ileri" (+Z) yönü.
  - yaw: Y ekseni etrafında dönüş, derece. yaw=+90 → görüntüde merkezin sağındaki çeyrek.
  - pitch: yukarı pozitif, derece. pitch=+90 → zenit (tepe), -90 → nadir (ayak altı).
  - Çıktı kamerası: x sağa, y aşağı (görüntü), odak f = (W/2) / tan(FOV/2), principal point merkez.

Çıktı:
  - <çıktı>/<kare_adı>_y<yaw>_p<pitch>.jpg
  - <çıktı>/views.json : her görünümün yaw/pitch/FOV/odak uzaklığı/rotasyon matrisi
    (COLMAP "rig" kurulumu veya kamera başlangıç değeri için).
  - --colmap-cameras verilirse COLMAP cameras.txt (PINHOLE, tek ortak kamera) yazılır.

Örnekler:
  # 8 yatay görünüm, FOV 90°, 1600 px kare görüntü
  python3 equirect_to_persp.py kareler/A1 -o persp/A1 --yaw-count 8 --fov 90 --size 1600
  # Üç kuşak: ufuk + 30° yukarı + 30° aşağı, yukarı/aşağı kuşaklar yarım adım kaydırılmış
  python3 equirect_to_persp.py kare.jpg -o out --yaw-count 8 --pitches 0,30,-30 --stagger
  # Elle görünüm listesi
  python3 equirect_to_persp.py kare.jpg -o out --views "0:0,90:0,180:0,270:0,0:90"
"""
import argparse
import glob
import json
import math
import os
import sys

try:
    import numpy as np
    import cv2
except ImportError:
    sys.exit("HATA: numpy ve opencv gerekli: pip install numpy opencv-python-headless")

IMG_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp")


def rotation(yaw_deg, pitch_deg):
    """Kamera→dünya rotasyon matrisi (kamera: x sağ, y yukarı, z ileri). Önce pitch (X), sonra yaw (Y)."""
    y, p = math.radians(yaw_deg), math.radians(pitch_deg)
    # Pitch: X ekseni etrafında; +p ileri vektörü yukarı (+Y) kaldırır.
    rx = np.array([[1, 0, 0],
                   [0, math.cos(p), math.sin(p)],
                   [0, -math.sin(p), math.cos(p)]], dtype=np.float64)
    # Kontrol: rx @ (0,0,1) = (0, sin p, cos p) → ileri vektör yukarı kalkar.
    # Yaw: Y ekseni etrafında; +y ileri vektörü sağa (+X) çevirir.
    ry = np.array([[math.cos(y), 0, math.sin(y)],
                   [0, 1, 0],
                   [-math.sin(y), 0, math.cos(y)]], dtype=np.float64)
    return ry @ rx


def build_maps(eq_w, eq_h, out_w, out_h, fov_deg, yaw_deg, pitch_deg):
    """cv2.remap için kaynak piksel haritalarını (map_x, map_y) hesaplar."""
    f = (out_w / 2.0) / math.tan(math.radians(fov_deg) / 2.0)
    cx, cy = (out_w - 1) / 2.0, (out_h - 1) / 2.0
    u, v = np.meshgrid(np.arange(out_w, dtype=np.float64), np.arange(out_h, dtype=np.float64))
    # Kamera uzayında ışın yönleri (y yukarı olduğu için görüntü v'si ters çevrilir)
    d = np.stack([(u - cx) / f, -(v - cy) / f, np.ones_like(u)], axis=-1)
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    R = rotation(yaw_deg, pitch_deg)
    w = d @ R.T  # dünya yönleri
    lon = np.arctan2(w[..., 0], w[..., 2])          # -pi..pi, 0 = ileri
    lat = np.arcsin(np.clip(w[..., 1], -1.0, 1.0))  # -pi/2..pi/2, + = yukarı
    map_x = (lon / (2 * math.pi) + 0.5) * eq_w - 0.5
    map_y = (0.5 - lat / math.pi) * eq_h - 0.5
    return map_x.astype(np.float32), map_y.astype(np.float32), f


def parse_views(args):
    """Komut satırı seçeneklerinden (yaw, pitch) listesi üretir."""
    if args.views:
        views = []
        for tok in args.views.split(","):
            tok = tok.strip()
            if not tok:
                continue
            ya, pi = tok.split(":")
            views.append((float(ya), float(pi)))
        return views
    pitches = [float(p) for p in args.pitches.split(",") if p.strip() != ""]
    step = 360.0 / args.yaw_count
    views = []
    for i, p in enumerate(pitches):
        if abs(p) >= 89.9:  # zenit/nadir için tek görünüm yeterli
            views.append((0.0, p))
            continue
        offset = (step / 2.0) if (args.stagger and p != 0) else 0.0
        for k in range(args.yaw_count):
            views.append(((args.yaw_offset + offset + k * step) % 360.0, p))
    if args.zenith:
        views.append((0.0, 90.0))
    if args.nadir:
        views.append((0.0, -90.0))
    return views


def list_inputs(inp):
    if os.path.isdir(inp):
        files = sorted(f for f in glob.glob(os.path.join(inp, "*")) if f.lower().endswith(IMG_EXT))
    else:
        files = sorted(glob.glob(inp)) if any(c in inp for c in "*?[") else [inp]
    return [f for f in files if os.path.isfile(f)]


def main():
    ap = argparse.ArgumentParser(
        description="Equirectangular 360 kareleri perspektif görüntülere böler (numpy + OpenCV).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("input", help="Equirect görüntü dosyası, klasör veya glob deseni ('kareler/*.jpg').")
    ap.add_argument("-o", "--out", required=True, help="Çıktı klasörü.")
    ap.add_argument("--fov", type=float, default=90.0, help="Yatay görüş açısı (derece). 80–100 önerilir.")
    ap.add_argument("--size", type=int, default=1600, help="Çıktı genişliği (piksel).")
    ap.add_argument("--aspect", type=float, default=1.0, help="Genişlik/yükseklik oranı (1.0 = kare).")
    ap.add_argument("--yaw-count", type=int, default=8, help="Her pitch kuşağında yatay görünüm sayısı.")
    ap.add_argument("--yaw-offset", type=float, default=0.0, help="İlk yaw açısı (derece).")
    ap.add_argument("--pitches", default="0", help="Virgülle ayrılmış pitch açıları (ör. '0,30,-30').")
    ap.add_argument("--stagger", action="store_true", help="Sıfır olmayan pitch kuşaklarını yarım yaw adımı kaydır.")
    ap.add_argument("--zenith", action="store_true", help="Tepe (pitch=+90) görünümü ekle (tavan/çatı için).")
    ap.add_argument("--nadir", action="store_true",
                    help="Nadir (pitch=-90) görünümü ekle. Genelde tripod/operatör içerdiği için ÖNERİLMEZ.")
    ap.add_argument("--views", default=None, help="Elle görünüm listesi 'yaw:pitch,...' (diğer ızgara seçeneklerini ezer).")
    ap.add_argument("--interp", choices=["linear", "cubic", "lanczos"], default="cubic", help="Örnekleme yöntemi.")
    ap.add_argument("--quality", type=int, default=95, help="JPEG kalitesi (1-100).")
    ap.add_argument("--ext", choices=["jpg", "png"], default="jpg", help="Çıktı formatı.")
    ap.add_argument("--colmap-cameras", action="store_true", help="COLMAP cameras.txt (PINHOLE) dosyası da yaz.")
    args = ap.parse_args()

    files = list_inputs(args.input)
    if not files:
        sys.exit(f"HATA: girdi bulunamadı: {args.input}")
    if not (1 <= args.fov < 179):
        sys.exit("HATA: --fov 1..179 arasında olmalı.")
    views = parse_views(args)
    if not views:
        sys.exit("HATA: hiç görünüm tanımlanmadı.")
    os.makedirs(args.out, exist_ok=True)

    out_w = args.size
    out_h = int(round(args.size / args.aspect))
    interp = {"linear": cv2.INTER_LINEAR, "cubic": cv2.INTER_CUBIC, "lanczos": cv2.INTER_LANCZOS4}[args.interp]
    cache = {}  # (eq_w, eq_h, yaw, pitch) -> haritalar; aynı çözünürlükte tekrar hesaplanmaz
    focal = None
    written = 0
    for path in files:
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            print(f"UYARI: okunamadı, atlandı: {path}", file=sys.stderr)
            continue
        eh, ew = img.shape[:2]
        if abs(ew / eh - 2.0) > 0.02:
            print(f"UYARI: {path} oranı 2:1 değil ({ew}x{eh}); equirect olmayabilir.", file=sys.stderr)
        stem = os.path.splitext(os.path.basename(path))[0]
        for (yaw, pitch) in views:
            key = (ew, eh, yaw, pitch)
            if key not in cache:
                mx, my, focal = build_maps(ew, eh, out_w, out_h, args.fov, yaw, pitch)
                cache[key] = (mx, my)
            mx, my = cache[key]
            # Yatayda 360° sarmalama: BORDER_WRAP; kutuplarda küçük taşma için de güvenli.
            out = cv2.remap(img, mx, my, interpolation=interp, borderMode=cv2.BORDER_WRAP)
            name = f"{stem}_y{int(round(yaw)):03d}_p{int(round(pitch)):+03d}.{args.ext}"
            params = [cv2.IMWRITE_JPEG_QUALITY, args.quality] if args.ext == "jpg" else []
            cv2.imwrite(os.path.join(args.out, name), out, params)
            written += 1
    if focal is None:
        focal = (out_w / 2.0) / math.tan(math.radians(args.fov) / 2.0)
    meta = {
        "fovDeg": args.fov, "width": out_w, "height": out_h,
        "focalPx": focal, "cx": (out_w - 1) / 2.0, "cy": (out_h - 1) / 2.0,
        "convention": "kamera x sağ, y yukarı, z ileri; R kamera→dünya (equirect merkezi = +Z)",
        "views": [{"yaw": y, "pitch": p, "suffix": f"_y{int(round(y)):03d}_p{int(round(p)):+03d}",
                   "R": rotation(y, p).round(9).tolist()} for (y, p) in views],
        "sourceCount": len(files),
    }
    with open(os.path.join(args.out, "views.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
    if args.colmap_cameras:
        with open(os.path.join(args.out, "cameras.txt"), "w") as fh:
            fh.write("# CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[fx,fy,cx,cy]\n")
            fh.write(f"1 PINHOLE {out_w} {out_h} {focal:.6f} {focal:.6f} {out_w / 2.0:.6f} {out_h / 2.0:.6f}\n")
    print(f"{len(files)} equirect kare x {len(views)} görünüm = {written} perspektif görüntü -> {args.out}")
    print(f"Odak uzaklığı: {focal:.2f} px (FOV {args.fov}°, {out_w}x{out_h})")


if __name__ == "__main__":
    main()
