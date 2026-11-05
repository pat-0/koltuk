#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
filter_blurry.py — Laplacian varyansı ile bulanık kareleri eler.

Keskinlik ölçütü: gri tonlamalı görüntünün Laplacian'ının varyansı (yüksek = keskin).
Ölçüt çözünürlüğe bağlı olduğundan tüm kareler önce --analysis-width genişliğine
küçültülerek ölçülür (kareler arası karşılaştırılabilir olsun diye).

Üç seçim modu (birleştirilebilir):
  --threshold T   : skoru T'nin altındaki kareleri at (mutlak eşik).
  --percentile P  : en bulanık %P'yi at (göreli eşik; eşik bilmiyorsanız önerilen).
  --rel-threshold R : skoru R × medyan'ın altındaki kareleri at (sahneye uyarlanan eşik;
                    uzun bulanık bölümlerde yüzdelikten güvenilir. 0.4 önerilir).
  --window N      : ardışık N karelik pencerelerde yalnızca en keskini tut
                    (videodan yoğun çıkarılmış karelerde hem bulanığı eler hem seyreltir).
Hiçbiri verilmezse yalnızca rapor (scores.csv) üretilir.

360 kareler için --crop-poles 0.15: üst/alt %15 bant (tavan ve tripod/nadir) ölçüme
katılmaz; böylece bulanık zemin/yamalı nadir skoru bozmaz.

Bağımlılıklar:
  - Python 3.8+
  - numpy, opencv-python(-headless):  pip install numpy opencv-python-headless

Örnekler:
  python3 filter_blurry.py kareler/A1 --report-only
  python3 filter_blurry.py kareler/A1 -o secilen/A1 --percentile 20
  python3 filter_blurry.py kareler/A1 -o secilen/A1 --window 3 --threshold 40 --crop-poles 0.15
"""
import argparse
import csv
import glob
import os
import shutil
import sys

try:
    import numpy as np
    import cv2
except ImportError:
    sys.exit("HATA: numpy ve opencv gerekli: pip install numpy opencv-python-headless")

IMG_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp")


def sharpness(path, analysis_width, crop_poles):
    """Laplacian varyansı. Okunamazsa None döner."""
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    h, w = img.shape
    if crop_poles > 0:
        c = int(h * crop_poles)
        img = img[c:h - c, :]
        h = img.shape[0]
    if analysis_width and w > analysis_width:
        img = cv2.resize(img, (analysis_width, max(1, int(h * analysis_width / w))), interpolation=cv2.INTER_AREA)
    return float(cv2.Laplacian(img, cv2.CV_64F, ksize=3).var())


def select(scores, threshold, percentile, window, rel_threshold=None):
    """Her kare için (tut/at, neden) kararı üretir. scores: [(ad, skor)] sıralı.
    Önce mutlak/göreli/yüzdelik eşikler uygulanır; pencere modu yalnız eşiği geçen kareler arasından seçer
    (tamamı bulanık bir pencereden kare tutulmaz)."""
    keep = [True] * len(scores)
    reason = [""] * len(scores)
    vals = np.array([s for _, s in scores], dtype=np.float64)
    cut = None
    if percentile is not None and len(vals):
        cut = float(np.percentile(vals, percentile))
    rel_cut = float(np.median(vals)) * rel_threshold if (rel_threshold and len(vals)) else None
    for i, (_, s) in enumerate(scores):
        if rel_cut is not None and s < rel_cut:
            keep[i], reason[i] = False, f"medyan*{rel_threshold}<{rel_cut:.1f}"
        elif threshold is not None and s < threshold:
            keep[i], reason[i] = False, f"esik<{threshold}"
        elif cut is not None and s < cut:
            keep[i], reason[i] = False, f"yuzdelik<{cut:.1f}"
    if window and window > 1:
        for start in range(0, len(scores), window):
            idx = [i for i in range(start, min(start + window, len(scores))) if keep[i]]
            if not idx:
                continue
            best = max(idx, key=lambda i: scores[i][1])
            for i in idx:
                if i != best:
                    keep[i], reason[i] = False, f"pencere({window})"
    return keep, reason


def main():
    ap = argparse.ArgumentParser(
        description="Laplacian varyansı ile bulanık kareleri eler; kayan pencerede en keskini tutabilir.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("input", help="Kare klasörü veya glob deseni ('kareler/*.jpg'). Dosya adı sırası = zaman sırası.")
    ap.add_argument("-o", "--out", default=None, help="Seçilen karelerin kopyalanacağı klasör.")
    ap.add_argument("--threshold", type=float, default=None, help="Mutlak eşik; altındaki skorlar atılır.")
    ap.add_argument("--percentile", type=float, default=None, help="En bulanık yüzde P atılır (0-100).")
    ap.add_argument("--rel-threshold", type=float, default=None, help="Medyanın bu katının altını at (ör. 0.4).")
    ap.add_argument("--window", type=int, default=0, help="Ardışık N karede yalnızca en keskini tut (0/1 = kapalı).")
    ap.add_argument("--analysis-width", type=int, default=1024, help="Ölçüm öncesi küçültme genişliği (piksel).")
    ap.add_argument("--crop-poles", type=float, default=0.0, help="Üst ve alttan kırpılacak oran (360 için 0.15).")
    ap.add_argument("--mode", choices=["copy", "move", "link"], default="copy",
                    help="Seçilenleri kopyala / taşı / sembolik bağla.")
    ap.add_argument("--report", default=None, help="Skor raporu CSV yolu (varsayılan: <çıktı veya girdi>/scores.csv).")
    ap.add_argument("--report-only", action="store_true", help="Yalnızca skorla, dosya kopyalama.")
    args = ap.parse_args()

    if os.path.isdir(args.input):
        files = sorted(f for f in glob.glob(os.path.join(args.input, "*")) if f.lower().endswith(IMG_EXT))
    else:
        files = sorted(f for f in glob.glob(args.input) if f.lower().endswith(IMG_EXT))
    if not files:
        sys.exit(f"HATA: görüntü bulunamadı: {args.input}")
    if args.percentile is not None and not (0 <= args.percentile < 100):
        sys.exit("HATA: --percentile 0..100 aralığında olmalı.")
    if not (0 <= args.crop_poles < 0.5):
        sys.exit("HATA: --crop-poles 0..0.5 aralığında olmalı.")
    if not args.report_only and not args.out:
        sys.exit("HATA: -o/--out verin veya --report-only kullanın.")

    scores = []
    for f in files:
        s = sharpness(f, args.analysis_width, args.crop_poles)
        if s is None:
            print(f"UYARI: okunamadı: {f}", file=sys.stderr)
            continue
        scores.append((f, s))

    keep, reason = select(scores, args.threshold, args.percentile, args.window, args.rel_threshold)

    report_dir = args.out if (args.out and not args.report_only) else (args.input if os.path.isdir(args.input) else ".")
    os.makedirs(report_dir, exist_ok=True)
    report = args.report or os.path.join(report_dir, "scores.csv")
    with open(report, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "sharpness", "keep", "reason"])
        for (f, s), k, r in zip(scores, keep, reason):
            w.writerow([os.path.basename(f), f"{s:.2f}", int(k), r])

    if not args.report_only:
        os.makedirs(args.out, exist_ok=True)
        for (f, _), k in zip(scores, keep):
            if not k:
                continue
            dst = os.path.join(args.out, os.path.basename(f))
            if args.mode == "copy":
                shutil.copy2(f, dst)
            elif args.mode == "move":
                shutil.move(f, dst)
            else:
                if os.path.lexists(dst):
                    os.remove(dst)
                os.symlink(os.path.abspath(f), dst)

    vals = np.array([s for _, s in scores])
    print(f"{len(scores)} kare ölçüldü | skor min {vals.min():.1f} / medyan {np.median(vals):.1f} / maks {vals.max():.1f}")
    print(f"Tutulan: {sum(keep)}  Atılan: {len(keep) - sum(keep)}  Rapor: {report}")


if __name__ == "__main__":
    main()
