#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
splat_to_b64.py — .splat dosyasını web demo görüntüleyicisinin okuduğu tek satırlık base64
metnine (.splat.b64.txt) çevirir. Artifact barındırması ikili dosya sunmadığı için demo,
URL'si ".b64.txt" ile biten sahneyi metin olarak indirip atob() ile çözer (web/demo.html fetchBuffer).

Kurallar: satır sonu YOK, standart base64 alfabesi (+/), '=' dolgulu. Boyut ≈ ikili × 4/3.
Bağımlılıklar: Python 3.8+, yalnız standart kütüphane.

Örnekler:
  python3 splat_to_b64.py sahne.splat                    # → sahne.splat.b64.txt
  python3 splat_to_b64.py sahne.splat -o yayin/sahne.splat.b64.txt --max-mb 20
  python3 splat_to_b64.py --decode sahne.splat.b64.txt -o geri.splat
"""
import argparse
import base64
import os
import sys


def main():
    ap = argparse.ArgumentParser(description=".splat ↔ tek satır base64 (.splat.b64.txt) dönüştürücü.",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("input", help="Girdi .splat (veya --decode ile .b64.txt)")
    ap.add_argument("-o", "--out", default=None, help="Çıktı yolu (varsayılan: <girdi>.b64.txt).")
    ap.add_argument("--decode", action="store_true", help="Ters yön: base64 metni → ikili .splat.")
    ap.add_argument("--max-mb", type=float, default=0, help="Çıktı bu MB'ı aşarsa uyarı ve çıkış kodu 2 (0 = kapalı).")
    args = ap.parse_args()

    try:
        data = open(args.input, "rb").read()
    except OSError as e:
        sys.exit(f"HATA: {e}")
    if args.decode:
        out = args.out or (args.input[:-8] if args.input.endswith(".b64.txt") else args.input + ".bin")
        try:
            raw = base64.b64decode(data.strip(), validate=True)
        except ValueError as e:
            sys.exit(f"HATA: geçersiz base64: {e}")
        open(out, "wb").write(raw)
        print(f"{args.input} → {out} ({len(raw)} bayt, {len(raw) // 32} gauss)")
        return
    if len(data) % 32:
        sys.exit(f"HATA: {args.input} 32 baytın katı değil ({len(data)} bayt) — .splat değil mi?")
    out = args.out or args.input + ".b64.txt"
    enc = base64.b64encode(data)
    if base64.b64decode(enc) != data:  # gidiş-dönüş denetimi
        sys.exit("HATA: base64 gidiş-dönüş denetimi başarısız")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, "wb").write(enc)
    mb = len(enc) / 1048576
    print(f"{args.input}: {len(data) // 32} gauss, {len(data) / 1048576:.2f} MB → {out} ({mb:.2f} MB, tek satır)")
    if args.max_mb and mb > args.max_mb:
        print(f"UYARI: çıktı {mb:.1f} MB > {args.max_mb} MB. ply_to_splat.py --max-splats / --min-alpha ile küçültün.",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
