#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline.py — Tek komutlu ön işleme boru hattı:
  çekim klasörü (cekim-protokolu.md adlandırması) → kare çıkarma → bulanık kare eleme (equirect)
  → 360→perspektif → yön bazlı bulanık görünüm eleme → COLMAP/Nerfstudio'ya hazır images/
  + özet rapor (rapor.md, rapor.json) + eğitim komutları (DRY-RUN, komutlar.sh).

Splat eğitimi bu betikte ÇALIŞTIRILMAZ (GPU gerekir); komut satırları yazdırılır/dosyaya yazılır.

Bağımlılıklar:
  - Python 3.8+, numpy, opencv-python(-headless), ffmpeg/ffprobe (PATH'te)
  - Aynı klasördeki extract_frames.py, filter_blurry.py, equirect_to_persp.py (modül olarak içe aktarılır)

BEKLENEN GİRDİ YAPISI (cekim-protokolu.md §4)
  YYYY-MM-DD_MEKAN/
    01_adlandirilmis/V360/  MEKAN_BLOK_KONUM_V360_NN.mp4   (Insta360 Studio'dan equirect dışa aktarım)
    01_adlandirilmis/P360/  MEKAN_BLOK_KONUM_P360_NN.jpg   (equirect sabit fotoğraflar; opsiyonel)
  Adlandırmaya uymayan dosyalar raporlanır ve atlanır (--allow-nonconforming ile dahil edilir).

ÇIKTI (varsayılan: <çekim>/10_isleme/)
  kareler/<video>/        equirect kareler
  secilen/<video>/        pencere+yüzdelik ile seçilmiş equirect kareler (+ scores.csv)
  images/                 düz klasör, perspektif görüntüler (COLMAP image_path)
  cameras.txt, views.json  ortak PINHOLE kamera ve görünüm rotasyonları
  goruntu_dizini.csv      her perspektif görüntünün kaynağı, yönü, keskinliği, tutuldu mu
  rapor.json, rapor.md    sayımlar ve adım süreleri
  komutlar.sh             COLMAP/GLOMAP + Nerfstudio komutları (dry-run)

Örnek:
  python3 pipeline.py 2026-11-15_TYAT --fps 2 --window 3 --percentile 10 --rel-threshold 0.4
  python3 pipeline.py 2026-11-15_TYAT -o /veri/isleme/TYAT --pitches 0,30 --size 1600 --jobs 8
"""
import argparse
import csv
import json
import math
import os
import re
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import numpy as np
    import cv2
    import extract_frames as xf
    import filter_blurry as fb
    import equirect_to_persp as ep
except ImportError as e:
    sys.exit(f"HATA: bağımlılık eksik ({e}). numpy, opencv ve aynı klasördeki betikler gerekli.")

NAME_RE = re.compile(r"^(?P<mekan>[A-Z0-9]{2,8})_(?P<blok>[^_]+)_(?P<konum>[^_]+)_(?P<tur>P360|V360|REF|OLC|DRN)_(?P<nn>\d{2})$")
VID_EXT = (".mp4", ".mov", ".m4v")
IMG_EXT = (".jpg", ".jpeg", ".png", ".tif", ".tiff")


def scan(folder, exts, tur, allow_nc):
    """Klasördeki dosyaları adlandırma kuralına göre ayırır."""
    ok, bad = [], []
    if not os.path.isdir(folder):
        return ok, bad
    for f in sorted(os.listdir(folder)):
        p = os.path.join(folder, f)
        if not (os.path.isfile(p) and f.lower().endswith(exts)):
            continue
        stem = os.path.splitext(f)[0]
        m = NAME_RE.match(stem)
        if m and m.group("tur") == tur:
            ok.append((p, stem, m.groupdict()))
        else:
            bad.append(f)
            if allow_nc:
                ok.append((p, re.sub(r"[^A-Za-z0-9_.-]", "-", stem), {}))
    return ok, bad


def persp_jobs(eq_path, stem, views, size, fov, out_dir, cache, quality):
    """Bir equirect kareden tüm görünümleri üretir; [(görüntü_adı, yaw, pitch, keskinlik)] döner."""
    img = cv2.imread(eq_path, cv2.IMREAD_COLOR)
    if img is None:
        return []
    h, w = img.shape[:2]
    res = []
    for yaw, pitch in views:
        key = (w, h, yaw, pitch)
        if key not in cache:
            mx, my, _ = ep.build_maps(w, h, size, size, fov, yaw, pitch)
            cache[key] = (mx, my)
        mx, my = cache[key]
        out = cv2.remap(img, mx, my, interpolation=cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)
        name = f"{stem}_y{int(round(yaw)):03d}_p{int(round(pitch)):+03d}.jpg"
        cv2.imwrite(os.path.join(out_dir, name), out, [cv2.IMWRITE_JPEG_QUALITY, quality])
        g = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        if g.shape[1] > 1024:
            g = cv2.resize(g, (1024, int(g.shape[0] * 1024 / g.shape[1])), interpolation=cv2.INTER_AREA)
        res.append((name, yaw, pitch, float(cv2.Laplacian(g, cv2.CV_64F, ksize=3).var())))
    return res


def grid_views(yaw_count, pitches, stagger):
    step = 360.0 / yaw_count
    views = []
    for p in pitches:
        off = step / 2 if (stagger and p != 0) else 0.0
        views += [((off + k * step) % 360.0, p) for k in range(yaw_count)]
    return views


def main():
    ap = argparse.ArgumentParser(
        description="Çekim klasöründen COLMAP/Nerfstudio'ya hazır images/ klasörü üretir (eğitim adımı dry-run).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("shoot", help="Çekim klasörü (YYYY-MM-DD_MEKAN).")
    ap.add_argument("-o", "--out", default=None, help="Çıktı klasörü (varsayılan <çekim>/10_isleme).")
    ap.add_argument("--fps", type=float, default=2.0, help="Videodan kare çıkarma hızı.")
    ap.add_argument("--skip-start", type=float, default=3.0, help="Video başında atlanacak saniye (sabit duruş).")
    ap.add_argument("--skip-end", type=float, default=3.0, help="Video sonunda atlanacak saniye.")
    ap.add_argument("--window", type=int, default=3, help="Equirect seçim: N ardışık karede en keskini tut.")
    ap.add_argument("--percentile", type=float, default=10.0, help="Equirect seçim: en bulanık %%P'yi at.")
    ap.add_argument("--rel-threshold", type=float, default=0.4,
                    help="Equirect seçim: skoru video medyanının bu katının altındaki kareleri at (0 = kapalı).")
    ap.add_argument("--crop-poles", type=float, default=0.15, help="Keskinlik ölçümünde üst/alt bant oranı.")
    ap.add_argument("--yaw-count", type=int, default=8)
    ap.add_argument("--pitches", default="0,30", help="Video kareleri için pitch kuşakları (nadir/operatör yok).")
    ap.add_argument("--still-pitches", default="0,30,-30", help="Sabit P360 fotoğraflar için pitch kuşakları.")
    ap.add_argument("--no-stagger", action="store_true", help="Pitch kuşaklarını yarım adım kaydırma.")
    ap.add_argument("--fov", type=float, default=90.0)
    ap.add_argument("--size", type=int, default=0,
                    help="Perspektif genişlik (px). 0 = otomatik: equirect_genişlik × FOV/360 (en fazla 1920).")
    ap.add_argument("--view-percentile", type=float, default=10.0,
                    help="Perspektif adımı sonrası: aynı yöndeki (yaw,pitch) görünümler içinde en bulanık %%P atılır. 0 = kapalı.")
    ap.add_argument("--quality", type=int, default=95, help="Perspektif JPEG kalitesi.")
    ap.add_argument("--jobs", type=int, default=max(1, min(8, os.cpu_count() or 1)), help="Paralel iş parçacığı.")
    ap.add_argument("--allow-nonconforming", action="store_true", help="Adlandırmaya uymayan dosyaları da işle.")
    ap.add_argument("--force", action="store_true", help="Var olan çıktı klasörünü silip baştan başla.")
    args = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            sys.exit(f"HATA: {tool} bulunamadı.")
    shoot = os.path.abspath(args.shoot)
    if not os.path.isdir(shoot):
        sys.exit(f"HATA: çekim klasörü yok: {shoot}")
    out = os.path.abspath(args.out or os.path.join(shoot, "10_isleme"))
    if os.path.exists(out):
        if not args.force and os.listdir(out):
            sys.exit(f"HATA: çıktı klasörü dolu: {out} (--force ile silinir)")
        shutil.rmtree(out, ignore_errors=True)
    for d in ("kareler", "secilen", "images"):
        os.makedirs(os.path.join(out, d), exist_ok=True)

    T = {}
    t0 = time.time()
    videos, bad_v = scan(os.path.join(shoot, "01_adlandirilmis", "V360"), VID_EXT, "V360", args.allow_nonconforming)
    stills, bad_s = scan(os.path.join(shoot, "01_adlandirilmis", "P360"), IMG_EXT, "P360", args.allow_nonconforming)
    if not videos and not stills:
        sys.exit("HATA: işlenecek V360 video veya P360 fotoğraf bulunamadı (adlandırma kuralını kontrol edin).")
    for f in bad_v + bad_s:
        print(f"UYARI: adlandırma kuralına uymuyor{' (yine de işlenecek)' if args.allow_nonconforming else ', atlandı'}: {f}",
              file=sys.stderr)

    # 1) Kare çıkarma
    t = time.time()
    per_video = []
    for path, stem, meta in videos:
        info = xf.ffprobe_info(path)
        dur = max(0.0, info["duration"] - args.skip_start - args.skip_end)
        if dur <= 0:
            print(f"UYARI: {stem} çok kısa ({info['duration']:.1f} sn), atlandı.", file=sys.stderr)
            continue
        fdir = os.path.join(out, "kareler", stem)
        _, n = xf.extract(path, fdir, stem, args.fps, args.skip_start, dur, None, "jpg", 2, True)
        per_video.append({"video": os.path.basename(path), "stem": stem, "meta": meta,
                          "durationSec": round(info["duration"], 2), "resolution": f"{info['width']}x{info['height']}",
                          "framesExtracted": n})
    T["1_kare_cikarma"] = time.time() - t

    # 2) Equirect düzeyinde bulanık kare eleme (pencere + yüzdelik)
    t = time.time()
    selected = []  # (equirect_yolu, isim_kökü, tür)
    for pv in per_video:
        fdir = os.path.join(out, "kareler", pv["stem"])
        files = sorted(os.path.join(fdir, f) for f in os.listdir(fdir) if f.endswith(".jpg"))
        scores = [(f, fb.sharpness(f, 1024, args.crop_poles)) for f in files]
        scores = [(f, s) for f, s in scores if s is not None]
        keep, reason = fb.select(scores, None, args.percentile if args.percentile > 0 else None, args.window,
                                 args.rel_threshold if args.rel_threshold > 0 else None)
        sdir = os.path.join(out, "secilen", pv["stem"])
        os.makedirs(sdir, exist_ok=True)
        with open(os.path.join(sdir, "scores.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["file", "sharpness", "keep", "reason"])
            for (f, s), k, r in zip(scores, keep, reason):
                w.writerow([os.path.basename(f), f"{s:.2f}", int(k), r])
                if k:
                    dst = os.path.join(sdir, os.path.basename(f))
                    shutil.copy2(f, dst)
                    selected.append((dst, os.path.splitext(os.path.basename(f))[0], "video"))
        pv["framesSelected"] = int(sum(keep))
        pv["framesDropped"] = len(keep) - int(sum(keep))
    for path, stem, meta in stills:
        selected.append((path, stem, "still"))
    T["2_bulanik_eleme_equirect"] = time.time() - t

    # 3) 360 → perspektif
    t = time.time()
    stagger = not args.no_stagger
    v_views = grid_views(args.yaw_count, [float(p) for p in args.pitches.split(",") if p.strip()], stagger)
    s_views = grid_views(args.yaw_count, [float(p) for p in args.still_pitches.split(",") if p.strip()], stagger)
    size = args.size
    if size <= 0:
        first = cv2.imread(selected[0][0]) if selected else None
        eq_w = first.shape[1] if first is not None else 7680
        size = int(min(1920, round(eq_w * args.fov / 360.0 / 16) * 16)) or 512
    img_dir = os.path.join(out, "images")
    cache = {}
    rows = []

    def work(item):
        path, stem, kind = item
        views = v_views if kind == "video" else s_views
        return [(stem, kind) + r for r in persp_jobs(path, stem, views, size, args.fov, img_dir, cache, args.quality)]

    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for res in ex.map(work, selected):
            rows.extend(res)
    T["3_perspektif"] = time.time() - t

    # 4) Yön bazlı bulanık görünüm eleme: aynı (tür, yaw, pitch) grubunda en bulanık %P silinir.
    t = time.time()
    groups = {}
    for i, r in enumerate(rows):
        groups.setdefault((r[1], r[3], r[4]), []).append(i)
    keep_view = [True] * len(rows)
    if args.view_percentile > 0:
        for idx in groups.values():
            if len(idx) < 5:  # küçük gruplarda istatistik anlamsız
                continue
            cut = float(np.percentile([rows[i][5] for i in idx], args.view_percentile))
            for i in idx:
                if rows[i][5] < cut:
                    keep_view[i] = False
                    os.remove(os.path.join(img_dir, rows[i][2]))
    T["4_bulanik_eleme_perspektif"] = time.time() - t

    # Kamera ve görünüm meta verisi
    f_px = (size / 2.0) / math.tan(math.radians(args.fov) / 2.0)
    with open(os.path.join(out, "cameras.txt"), "w") as fh:
        fh.write("# CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[fx,fy,cx,cy]\n")
        fh.write(f"1 PINHOLE {size} {size} {f_px:.6f} {f_px:.6f} {size / 2.0:.6f} {size / 2.0:.6f}\n")
    with open(os.path.join(out, "views.json"), "w", encoding="utf-8") as fh:
        json.dump({"fovDeg": args.fov, "width": size, "height": size, "focalPx": f_px,
                   "videoViews": [{"yaw": y, "pitch": p, "R": ep.rotation(y, p).round(9).tolist()} for y, p in v_views],
                   "stillViews": [{"yaw": y, "pitch": p, "R": ep.rotation(y, p).round(9).tolist()} for y, p in s_views]},
                  fh, ensure_ascii=False, indent=2)
    with open(os.path.join(out, "goruntu_dizini.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["image", "source_frame", "kind", "yaw", "pitch", "sharpness", "keep"])
        for r, k in zip(rows, keep_view):
            w.writerow([r[2], r[0], r[1], r[3], r[4], f"{r[5]:.2f}", int(k)])

    # 5) Eğitim komutları (DRY-RUN)
    n_img = sum(keep_view)
    cmds = f"""#!/usr/bin/env bash
# DRY-RUN: pipeline.py tarafından üretildi. GPU'lu makinede gözden geçirip çalıştırın.
# Görüntü: {n_img} adet, {size}x{size}, PINHOLE f={f_px:.2f}px (cameras.txt)
set -euo pipefail
cd "{out}"
# --- A) COLMAP poz kestirimi (kamera iç parametreleri sabit) ---
colmap feature_extractor --database_path db.db --image_path images \\
  --ImageReader.camera_model PINHOLE --ImageReader.single_camera 1 \\
  --ImageReader.camera_params "{f_px:.4f},{f_px:.4f},{size / 2.0:.4f},{size / 2.0:.4f}"
colmap sequential_matcher --database_path db.db --SequentialMatching.overlap 20
mkdir -p sparse
colmap mapper --database_path db.db --image_path images --output_path sparse \\
  --Mapper.ba_refine_focal_length 0 --Mapper.ba_refine_principal_point 0
# Alternatif (daha hızlı global SfM): glomap mapper --database_path db.db --image_path images --output_path sparse
# --- B) Nerfstudio splatfacto ---
ns-process-data images --data images --output-dir ns_data --skip-colmap --colmap-model-path ../sparse/0
ns-train splatfacto --data ns_data          # büyük sahne: splatfacto-big
# ns-export gaussian-splat --load-config outputs/<deney>/splatfacto/<zaman>/config.yml --output-dir splat
# --- C) Postshot: images/ klasörünü (veya sparse/ COLMAP modelini) içe aktarın (GUI; Studio CLI sözdizimi doğrulanmadı) ---
"""
    with open(os.path.join(out, "komutlar.sh"), "w") as fh:
        fh.write(cmds)
    os.chmod(os.path.join(out, "komutlar.sh"), 0o755)
    T["5_egitim_dry_run"] = 0.0
    T["toplam"] = time.time() - t0

    rep = {
        "shoot": shoot, "output": out,
        "parameters": dict({k: v for k, v in vars(args).items() if k not in ("shoot", "out")}, sizeResolved=size),
        "videos": per_video,
        "stills": [os.path.basename(p) for p, _, _ in stills],
        "nonconforming": bad_v + bad_s,
        "counts": {
            "framesExtracted": sum(p["framesExtracted"] for p in per_video),
            "framesSelected": sum(p.get("framesSelected", 0) for p in per_video),
            "framesDropped": sum(p.get("framesDropped", 0) for p in per_video),
            "stills": len(stills),
            "viewsPerVideoFrame": len(v_views), "viewsPerStill": len(s_views),
            "perspectiveGenerated": len(rows),
            "perspectiveDropped": len(rows) - n_img,
            "imagesFinal": n_img,
        },
        "timingSec": {k: round(v, 2) for k, v in T.items()},
    }
    with open(os.path.join(out, "rapor.json"), "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=2)
    c = rep["counts"]
    md = [f"# Ön işleme raporu — {os.path.basename(shoot)}", "",
          f"- Çıktı: `{out}`",
          f"- Videolar: {len(per_video)} · Sabit fotoğraflar: {c['stills']} · Adlandırmaya uymayan: {len(rep['nonconforming'])}",
          f"- Kare: {c['framesExtracted']} çıkarıldı → {c['framesSelected']} seçildi ({c['framesDropped']} elendi)",
          f"- Perspektif: {c['perspectiveGenerated']} üretildi ({c['viewsPerVideoFrame']}/kare, {c['viewsPerStill']}/foto, "
          f"{size}px, FOV {args.fov}°) → {c['perspectiveDropped']} bulanık elendi → **{c['imagesFinal']} görüntü** (`images/`)",
          "", "| Video | Süre (sn) | Çözünürlük | Çıkarılan | Seçilen | Elenen |", "|---|---|---|---|---|---|"]
    md += [f"| {p['video']} | {p['durationSec']} | {p['resolution']} | {p['framesExtracted']} | {p.get('framesSelected', 0)} | "
           f"{p.get('framesDropped', 0)} |" for p in per_video]
    md += ["", "| Adım | Süre (sn) |", "|---|---|"] + [f"| {k} | {v:.1f} |" for k, v in rep["timingSec"].items()]
    md += ["", "Eğitim adımı çalıştırılmadı (dry-run). Komutlar: `komutlar.sh`."]
    with open(os.path.join(out, "rapor.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")

    print("\n".join(md[2:6]))
    print(f"Toplam süre {T['toplam']:.1f} sn. Rapor: {os.path.join(out, 'rapor.md')}")
    print("\n[DRY-RUN] Splat eğitimi için (GPU'lu makinede):")
    for line in cmds.splitlines():
        if line.startswith(("colmap", "ns-", "glomap", "  --")):
            print("  " + line)


if __name__ == "__main__":
    main()
