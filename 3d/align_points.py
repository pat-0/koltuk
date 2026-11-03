#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
align_points.py — Splat/mesh koordinatlarındaki bilinen noktaları (ör. basketbol sahası
köşeleri) mekân (venue) koordinatlarına eşleyen benzerlik dönüşümünü (ölçek + dönüş +
öteleme) en küçük kareler ile hesaplar (Umeyama yöntemi). Sonuç venue.json içindeki
venue.scene.transform alanına yazılacak değerleri verir.

Bağımlılıklar: Python 3.8+, numpy  (pip install numpy)

GİRDİ CSV (başlık zorunlu):  name,sx,sy,sz,vx,vy,vz
  s* = noktanın splat dosyasındaki koordinatı (SuperSplat'ta noktayı seçip okuyun)
  v* = aynı noktanın venue koordinatı (metre, Y yukarı, orijin saha merkezi, X uzun eksen)
  Örnek (basketbol 28 x 15 m saha köşeleri, zemin y=0):
     kose_KD, ...,  14, 0,  7.5
     kose_KB, ..., -14, 0,  7.5  ...
  En az 3 nokta (tercihen 4-8, sahaya yayılmış; en az biri farklı yükseklikte olursa eğim daha iyi çözülür).

MODLAR
  --mode level (varsayılan): splat'ın zaten yatay (Y yukarı) olduğu varsayılır; yalnızca
        ölçek + Y ekseni etrafında dönüş + öteleme çözülür. Şema v0.1'deki transform
        (position, rotationY, scale) ile birebir uyumludur.
  --mode full: tam 3B dönüş çözülür. Eğim (tilt) 0.5°'den büyükse UYARI verilir:
        bu eğim şemada ifade edilemez; SuperSplat'ta sahneye uygulanıp dosyaya "pişirilmeli".

DÖNÜŞÜM KURALI (three.js ile aynı varsayıldı — web ekibiyle teyit edin):
  venue = R_y(rotationY) · (scale · splat) + position
  R_y(θ) = [[cos θ, 0, sin θ], [0, 1, 0], [-sin θ, 0, cos θ]]  (θ radyan; çıktıda derece de verilir)

Örnek:
  python3 align_points.py kontrol-noktalari.csv
  python3 align_points.py kontrol-noktalari.csv --mode full --json hizalama.json
"""
import argparse
import csv
import json
import math
import sys

try:
    import numpy as np
except ImportError:
    sys.exit("HATA: numpy gerekli: pip install numpy")


def umeyama(src, dst):
    """src → dst benzerlik dönüşümü: dst ≈ s R src + t. Yansıma engellenir."""
    n, dim = src.shape
    mu_s, mu_d = src.mean(0), dst.mean(0)
    xs, xd = src - mu_s, dst - mu_d
    var_s = (xs ** 2).sum() / n
    cov = xd.T @ xs / n
    U, D, Vt = np.linalg.svd(cov)
    S = np.eye(dim)
    if np.linalg.det(U) * np.linalg.det(Vt) < 0:
        S[-1, -1] = -1
    R = U @ S @ Vt
    s = np.trace(np.diag(D) @ S) / var_s
    t = mu_d - s * R @ mu_s
    return s, R, t


def main():
    ap = argparse.ArgumentParser(
        description="Splat koordinatlarındaki kontrol noktalarından venue.json scene.transform değerlerini hesaplar.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("points", help="CSV: name,sx,sy,sz,vx,vy,vz")
    ap.add_argument("--mode", choices=["level", "full"], default="level", help="Çözüm modu (açıklamaya bakın).")
    ap.add_argument("--json", default=None, help="Sonucu JSON olarak da yaz.")
    ap.add_argument("--max-rms", type=float, default=0.10, help="Bu RMS hatasını (m) aşarsa çıkış kodu 2.")
    args = ap.parse_args()

    names, S, V = [], [], []
    with open(args.points, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            names.append(r["name"])
            S.append([float(r[k]) for k in ("sx", "sy", "sz")])
            V.append([float(r[k]) for k in ("vx", "vy", "vz")])
    S, V = np.array(S), np.array(V)
    if len(S) < 3:
        sys.exit("HATA: en az 3 kontrol noktası gerekli.")

    tilt_deg = 0.0
    if args.mode == "level":
        # XZ düzleminde 2B benzerlik; R_y(θ) (x,z) üzerinde [[c, s], [-s, c]] olarak etkir.
        s, R2, t2 = umeyama(S[:, [0, 2]], V[:, [0, 2]])
        theta = math.atan2(R2[0, 1], R2[0, 0])
        ty = float(np.mean(V[:, 1] - s * S[:, 1]))
        R = np.array([[math.cos(theta), 0, math.sin(theta)], [0, 1, 0], [-math.sin(theta), 0, math.cos(theta)]])
        t = np.array([t2[0], ty, t2[1]])
    else:
        s, R, t = umeyama(S, V)
        theta = math.atan2(R[0, 2], R[0, 0])
        # Eğim: dönüşmüş Y ekseninin dünya Y ekseninden sapması
        tilt_deg = math.degrees(math.acos(max(-1.0, min(1.0, R[1, 1]))))

    pred = (s * (R @ S.T)).T + t
    err = np.linalg.norm(pred - V, axis=1)
    rms = float(math.sqrt((err ** 2).mean()))

    print(f"Mod: {args.mode}   Nokta sayısı: {len(S)}")
    print(f"scale      = {s:.6f}")
    print(f"rotationY  = {math.degrees(theta):.4f}°  ({theta:.6f} rad)")
    print(f"position   = [{t[0]:.4f}, {t[1]:.4f}, {t[2]:.4f}]")
    if args.mode == "full":
        print(f"eğim (tilt) = {tilt_deg:.3f}°")
        if tilt_deg > 0.5:
            print("UYARI: eğim 0.5°'den büyük. Şema v0.1 yalnız rotationY taşır; eğimi SuperSplat'ta sahneye "
                  "uygulayıp dosyayı yeniden dışa aktarın, sonra --mode level ile tekrar hesaplayın.", file=sys.stderr)
    print("Nokta artıkları (m):")
    for n, e in zip(names, err):
        print(f"  {n:<16} {e:.3f}")
    print(f"RMS = {rms:.3f} m")
    print("--scene-transform için: "
          f"\"{t[0]:.4f},{t[1]:.4f},{t[2]:.4f},<rotationY birimi web ekibiyle teyit edilmeli>,{s:.6f}\"")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"mode": args.mode, "scale": s, "rotationYDeg": math.degrees(theta), "rotationYRad": theta,
                       "position": t.tolist(), "tiltDeg": tilt_deg, "rms": rms,
                       "residuals": dict(zip(names, err.round(4).tolist())),
                       "rotationMatrix": R.round(9).tolist()}, fh, ensure_ascii=False, indent=2)
    sys.exit(2 if rms > args.max_rms else 0)


if __name__ == "__main__":
    main()
