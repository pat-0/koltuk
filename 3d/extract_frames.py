#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_frames.py — Videodan belirli fps'te kare çıkarır (ffmpeg sarmalayıcı).

Bağımlılıklar:
  - Python 3.8+
  - ffmpeg ve ffprobe (PATH içinde). Kurulum: apt install ffmpeg / brew install ffmpeg
  - Python paketi gerekmez (yalnızca standart kütüphane).

Notlar:
  - Insta360 .insv dosyaları çift balıkgözü (dual-fisheye) kayıttır. Önce Insta360 Studio
    ile "equirectangular MP4" olarak dışa aktarın (dikiş ve ufuk/yatay düzeltme açık;
    ayrıntı için bkz. isleme-rehberi.md), sonra bu betiği o MP4 üzerinde çalıştırın.
  - Çıktı adları: <önek>_<5 haneli sıra>.jpg  (ör. A1-yuruyus_00001.jpg)
  - Her çıktı klasörüne kaynak/parametreleri içeren bir <önek>_manifest.json yazılır.

Örnekler:
  python3 extract_frames.py A1_walk_01.mp4 -o kareler/A1 --fps 2
  python3 extract_frames.py *.mp4 -o kareler --fps 1.5 --start 5 --duration 60 --width 3840
"""
import argparse
import json
import os
import shutil
import subprocess
import sys


def ffprobe_info(path):
    """Videonun süre, çözünürlük ve fps bilgisini ffprobe ile okur."""
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_frames:format=duration",
        "-of", "json", path,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"ffprobe okuyamadı: {path}\n{out.stderr.strip()}")
    data = json.loads(out.stdout)
    st = (data.get("streams") or [{}])[0]
    num, den = (st.get("r_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den) if float(den) else 0.0
    return {
        "width": st.get("width"),
        "height": st.get("height"),
        "fps": round(fps, 3),
        "duration": float(data.get("format", {}).get("duration", 0.0)),
    }


def build_filter(fps, width):
    """ffmpeg -vf zincirini kurar: fps örnekleme + isteğe bağlı ölçekleme."""
    parts = [f"fps={fps}"]
    if width:
        # Yükseklik oranı korunur; -2 = çift sayıya yuvarla
        parts.append(f"scale={width}:-2:flags=lanczos")
    return ",".join(parts)


def extract(video, out_dir, prefix, fps, start, duration, width, fmt, quality, overwrite):
    os.makedirs(out_dir, exist_ok=True)
    info = ffprobe_info(video)
    pattern = os.path.join(out_dir, f"{prefix}_%05d.{fmt}")
    if not overwrite:
        existing = [f for f in os.listdir(out_dir) if f.startswith(prefix + "_") and f.endswith("." + fmt)]
        if existing:
            raise RuntimeError(
                f"{out_dir} içinde '{prefix}_*' kareleri zaten var ({len(existing)} adet). "
                f"--overwrite kullanın veya başka klasör seçin.")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    if start:
        cmd += ["-ss", str(start)]
    cmd += ["-i", video]
    if duration:
        cmd += ["-t", str(duration)]
    cmd += ["-vf", build_filter(fps, width), "-vsync", "vfr"]
    if fmt == "jpg":
        # -q:v 1 (en iyi) .. 31 (en kötü). Splat/fotogrametri için 1-3 önerilir.
        cmd += ["-q:v", str(quality)]
    elif fmt == "png":
        cmd += ["-compression_level", "3"]
    cmd += [pattern]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffmpeg hatası ({video}):\n{res.stderr.strip()}")
    frames = sorted(f for f in os.listdir(out_dir) if f.startswith(prefix + "_") and f.endswith("." + fmt))
    manifest = {
        "source": os.path.abspath(video),
        "sourceInfo": info,
        "fps": fps, "start": start, "duration": duration, "width": width,
        "format": fmt, "quality": quality, "prefix": prefix,
        "frameCount": len(frames),
        "ffmpegCommand": " ".join(cmd),
    }
    mpath = os.path.join(out_dir, f"{prefix}_manifest.json")
    with open(mpath, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return info, len(frames)


def main():
    ap = argparse.ArgumentParser(
        description="Videodan belirli fps'te kare çıkarır (ffmpeg). 360 equirect MP4 veya normal video.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("videos", nargs="+", help="Girdi video dosya(lar)ı (.mp4/.mov). .insv için önce Insta360 Studio'dan dışa aktarın.")
    ap.add_argument("-o", "--out", required=True, help="Çıktı klasörü. Birden çok video verilirse her biri için alt klasör açılır.")
    ap.add_argument("--fps", type=float, default=2.0,
                    help="Saniyede çıkarılacak kare. Yavaş yürüyüşte (~0.5 m/s) 360 video için 1–2 önerilir.")
    ap.add_argument("--start", type=float, default=0.0, help="Başlangıç saniyesi (baştaki kurulum anını atlamak için).")
    ap.add_argument("--duration", type=float, default=None, help="Yalnızca bu kadar saniye işle.")
    ap.add_argument("--width", type=int, default=None, help="Çıktı genişliği (piksel). Boşsa orijinal çözünürlük.")
    ap.add_argument("--format", choices=["jpg", "png"], default="jpg", help="Çıktı formatı.")
    ap.add_argument("--quality", type=int, default=2, help="JPEG kalitesi (ffmpeg -q:v, 1=en iyi, 31=en kötü).")
    ap.add_argument("--prefix", default=None, help="Dosya adı öneki. Boşsa video dosya adı kullanılır.")
    ap.add_argument("--overwrite", action="store_true", help="Var olan karelerin üzerine yaz.")
    args = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            sys.exit(f"HATA: '{tool}' bulunamadı. ffmpeg kurun (apt install ffmpeg).")
    if args.fps <= 0:
        sys.exit("HATA: --fps pozitif olmalı.")
    if not 1 <= args.quality <= 31:
        sys.exit("HATA: --quality 1..31 aralığında olmalı.")

    multi = len(args.videos) > 1
    total = 0
    for v in args.videos:
        if not os.path.isfile(v):
            sys.exit(f"HATA: dosya yok: {v}")
        if v.lower().endswith(".insv"):
            print(f"UYARI: {v} ham .insv (çift balıkgözü). Insta360 Studio'dan equirect MP4 dışa aktarmanız önerilir.",
                  file=sys.stderr)
        base = os.path.splitext(os.path.basename(v))[0]
        prefix = args.prefix or base
        out_dir = os.path.join(args.out, base) if multi else args.out
        try:
            info, n = extract(v, out_dir, prefix, args.fps, args.start, args.duration,
                              args.width, args.format, args.quality, args.overwrite)
        except RuntimeError as e:
            sys.exit(f"HATA: {e}")
        total += n
        print(f"{v}: {info['width']}x{info['height']} @ {info['fps']} fps, {info['duration']:.1f} sn "
              f"-> {n} kare ({out_dir})")
    print(f"Toplam {total} kare çıkarıldı.")


if __name__ == "__main__":
    main()
