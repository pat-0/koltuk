#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ply_to_splat.py — 3D Gaussian Splatting .ply dosyasını web görüntüleyicinin okuduğu
antimatter15 ".splat" biçimine (32 bayt/gauss) dönüştürür.

.splat kaydı (little-endian, web/demo.html SplatMesh ile aynı):
  [x, y, z  float32] [sx, sy, sz  float32, DOĞRUSAL ölçek = exp(scale_i)]
  [r, g, b, a  uint8]  renk = (0.5 + SH_C0·f_dc)·255, a = sigmoid(opacity)·255
  [qw, qx, qy, qz  uint8]  birim kuaterniyon · 128 + 128   (PLY'de rot_0 = w)
Kayıtlar "önem" sırasına göre dizilir: exp(sx+sy+sz)·sigmoid(opacity) büyükten küçüğe
(antimatter15 convert.py ile aynı; dosya kesilirse en önemli gauss'lar kalır).
Küresel harmonik (f_rest_*) atılır → görünüme bağlı renk kaybolur (SH derece 0).

Bağımlılıklar: Python 3.8+, numpy

Desteklenen girdi: binary_little_endian veya ascii PLY, "vertex" öğesinde
x,y,z, scale_0..2, rot_0..3, opacity ve f_dc_0..2 (yoksa red/green/blue uchar) alanları.
SuperSplat/PlayCanvas ".compressed.ply" desteklenmez → SuperSplat'ten normal PLY dışa aktarın.

Koordinat dönüşümü (opsiyonel, sıra: dönüşüm → kırpma → budama):
  --flip-yz            X ekseni etrafında 180° (COLMAP/OpenCV: Y aşağı, Z ileri → Y yukarı)
  --align-json F       align_points.py --json çıktısı: venue = scale·R·p + position
                       (pozisyon, ölçek ve kuaterniyonlar birlikte dönüştürülür)
  --crop=xmin,ymin,zmin,xmax,ymax,zmax  bu kutu dışını at (dönüşümden sonra, metre; eksi değerler için "=" şart)
  --min-alpha A        a < A (0-255) olanları at (varsayılan 0: hiçbirini atma)
  --max-splats N       önem sırasına göre ilk N'i tut (mobil bütçe için)

Örnekler:
  python3 ply_to_splat.py temiz.ply sahne.splat
  python3 ply_to_splat.py point_cloud.ply sahne.splat --align-json hizalama.json --min-alpha 8 --max-splats 1500000
  python3 ply_to_splat.py --inspect sahne.splat
"""
import argparse
import json
import math
import os
import sys

try:
    import numpy as np
except ImportError:
    sys.exit("HATA: numpy gerekli: pip install numpy")

SH_C0 = 0.28209479177387814
SPLAT_DTYPE = np.dtype([("p", "<f4", 3), ("s", "<f4", 3), ("c", "u1", 4), ("q", "u1", 4)])
assert SPLAT_DTYPE.itemsize == 32
PLY_TYPES = {"char": "i1", "int8": "i1", "uchar": "u1", "uint8": "u1", "short": "i2", "int16": "i2",
             "ushort": "u2", "uint16": "u2", "int": "i4", "int32": "i4", "uint": "u4", "uint32": "u4",
             "float": "f4", "float32": "f4", "double": "f8", "float64": "f8"}


def read_ply(path):
    """vertex öğesini numpy yapılandırılmış dizi olarak okur."""
    with open(path, "rb") as fh:
        if fh.readline().strip() != b"ply":
            raise ValueError("PLY başlığı yok")
        fmt, elements, cur = None, [], None
        while True:
            line = fh.readline()
            if not line:
                raise ValueError("end_header bulunamadı")
            tok = line.decode("ascii", "replace").strip().split()
            if not tok or tok[0] in ("comment", "obj_info"):
                continue
            if tok[0] == "format":
                fmt = tok[1]
            elif tok[0] == "element":
                cur = {"name": tok[1], "count": int(tok[2]), "props": []}
                elements.append(cur)
            elif tok[0] == "property":
                if tok[1] == "list":
                    raise ValueError(f"liste özelliği desteklenmiyor ({cur['name']}.{tok[-1]})")
                if tok[1] not in PLY_TYPES:
                    raise ValueError(f"bilinmeyen tip: {tok[1]}")
                cur["props"].append((tok[2], PLY_TYPES[tok[1]]))
            elif tok[0] == "end_header":
                break
        names = [e["name"] for e in elements]
        if "chunk" in names:
            raise ValueError("sıkıştırılmış PLY (.compressed.ply) — SuperSplat'ten normal PLY dışa aktarın")
        if "vertex" not in names:
            raise ValueError("vertex öğesi yok")
        if fmt not in ("binary_little_endian", "ascii"):
            raise ValueError(f"desteklenmeyen PLY biçimi: {fmt}")
        out = None
        for e in elements:
            endian = "<" if fmt == "binary_little_endian" else "="
            dt = np.dtype([(n, endian + t) for n, t in e["props"]])
            if fmt == "binary_little_endian":
                data = np.frombuffer(fh.read(dt.itemsize * e["count"]), dtype=dt, count=e["count"])
            else:
                rows = [fh.readline().split() for _ in range(e["count"])]
                data = np.array([tuple(r) for r in rows], dtype=dt) if rows else np.zeros(0, dt)
            if e["name"] == "vertex":
                out = data
                break
        return out


def quat_mul(a, b):
    """Hamilton çarpımı, [w,x,y,z]; a: (4,) veya (N,4), b: (N,4)."""
    aw, ax, ay, az = np.moveaxis(np.broadcast_to(a, b.shape), -1, 0)
    bw, bx, by, bz = np.moveaxis(b, -1, 0)
    return np.stack([aw * bw - ax * bx - ay * by - az * bz,
                     aw * bx + ax * bw + ay * bz - az * by,
                     aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw], -1)


def mat_to_quat(R):
    """3x3 rotasyon matrisi → [w,x,y,z]."""
    R = np.asarray(R, float)
    t = np.trace(R)
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        q = [0.25 * s, (R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s]
    else:
        i = int(np.argmax(np.diag(R)))
        j, k = (i + 1) % 3, (i + 2) % 3
        s = math.sqrt(1.0 + R[i, i] - R[j, j] - R[k, k]) * 2
        q = [0.0] * 4
        q[0] = (R[k, j] - R[j, k]) / s
        q[1 + i] = 0.25 * s
        q[1 + j] = (R[j, i] + R[i, j]) / s
        q[1 + k] = (R[k, i] + R[i, k]) / s
    q = np.array(q)
    return q / np.linalg.norm(q)


def convert(v, R=None, scale=1.0, t=None):
    """PLY vertex dizisi → (pozisyon, doğrusal ölçek, rgba float, kuaterniyon wxyz, önem)."""
    names = v.dtype.names
    need = ["x", "y", "z", "scale_0", "scale_1", "scale_2", "rot_0", "rot_1", "rot_2", "rot_3", "opacity"]
    miss = [n for n in need if n not in names]
    if miss:
        raise ValueError(f"PLY'de 3DGS alanları eksik: {miss}")
    P = np.stack([v["x"], v["y"], v["z"]], 1).astype(np.float64)
    logS = np.stack([v["scale_0"], v["scale_1"], v["scale_2"]], 1).astype(np.float64)
    Q = np.stack([v["rot_0"], v["rot_1"], v["rot_2"], v["rot_3"]], 1).astype(np.float64)
    op = v["opacity"].astype(np.float64)
    if "f_dc_0" in names:
        rgb = 0.5 + SH_C0 * np.stack([v["f_dc_0"], v["f_dc_1"], v["f_dc_2"]], 1).astype(np.float64)
    elif "red" in names:
        rgb = np.stack([v["red"], v["green"], v["blue"]], 1).astype(np.float64) / 255.0
    else:
        raise ValueError("renk alanı yok (f_dc_* veya red/green/blue)")
    alpha = 1.0 / (1.0 + np.exp(-op))
    S = np.exp(logS)
    importance = np.exp(logS.sum(1)) * alpha
    n = np.linalg.norm(Q, axis=1, keepdims=True)
    n[n == 0] = 1
    Q = Q / n
    if R is not None:
        P = scale * (P @ np.asarray(R).T) + (t if t is not None else 0)
        S = S * scale
        Q = quat_mul(mat_to_quat(R), Q)
        importance = importance * scale ** 3
    rgba = np.concatenate([rgb, alpha[:, None]], 1)
    return P, S, rgba, Q, importance


def pack(P, S, rgba, Q):
    rec = np.zeros(len(P), dtype=SPLAT_DTYPE)
    rec["p"] = P.astype(np.float32)
    rec["s"] = S.astype(np.float32)
    rec["c"] = np.clip(np.round(rgba * 255), 0, 255).astype(np.uint8)
    # w negatifse işaret çevir (aynı dönüş; sabit kodlama)
    Q = np.where(Q[:, :1] < 0, -Q, Q)
    rec["q"] = np.clip(np.round(Q * 128 + 128), 0, 255).astype(np.uint8)
    return rec


def inspect(path):
    raw = np.fromfile(path, dtype=np.uint8)
    if raw.size % 32:
        raise ValueError(f"boyut 32'nin katı değil ({raw.size} bayt)")
    r = raw.view(SPLAT_DTYPE)
    q = (r["q"].astype(np.float64) - 128) / 128
    qn = np.linalg.norm(q, axis=1)
    info = {"file": path, "count": int(len(r)), "bytes": int(raw.size),
            "bboxMin": r["p"].min(0).round(3).tolist() if len(r) else None,
            "bboxMax": r["p"].max(0).round(3).tolist() if len(r) else None,
            "scaleMedian": np.median(r["s"], 0).round(4).tolist() if len(r) else None,
            "alphaMean": round(float(r["c"][:, 3].mean()), 1) if len(r) else None,
            "quatNormMinMax": [round(float(qn.min()), 3), round(float(qn.max()), 3)] if len(r) else None,
            "finite": bool(np.isfinite(r["p"]).all() and np.isfinite(r["s"]).all())}
    return info


def main():
    ap = argparse.ArgumentParser(description="3DGS .ply → antimatter15 .splat (32 bayt/gauss) dönüştürücü.",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("input", help="Girdi .ply (veya --inspect ile .splat)")
    ap.add_argument("output", nargs="?", help="Çıktı .splat")
    ap.add_argument("--inspect", action="store_true", help="Girdi .splat dosyasının özetini yazdır (JSON).")
    ap.add_argument("--flip-yz", action="store_true", help="X ekseni etrafında 180° döndür (Y aşağı → Y yukarı).")
    ap.add_argument("--align-json", default=None, help="align_points.py --json çıktısı (scale, rotationMatrix, position).")
    ap.add_argument("--crop", default=None, help="xmin,ymin,zmin,xmax,ymax,zmax (dönüşümden sonra).")
    ap.add_argument("--min-alpha", type=int, default=0, help="Bu opaklığın (0-255) altını at.")
    ap.add_argument("--max-splats", type=int, default=0, help="Önem sırasına göre en fazla N gauss (0 = sınırsız).")
    args = ap.parse_args()

    if args.inspect:
        try:
            print(json.dumps(inspect(args.input), ensure_ascii=False, indent=2))
        except (OSError, ValueError) as e:
            sys.exit(f"HATA: {e}")
        return
    if not args.output:
        sys.exit("HATA: çıktı yolu gerekli.")
    try:
        v = read_ply(args.input)
        R, s, t = None, 1.0, None
        if args.flip_yz:
            R = np.diag([1.0, -1.0, -1.0])
        if args.align_json:
            A = json.load(open(args.align_json, encoding="utf-8"))
            Ra = np.asarray(A["rotationMatrix"], float)
            R = Ra if R is None else Ra @ R
            s, t = float(A["scale"]), np.asarray(A["position"], float)
        P, S, rgba, Q, imp = convert(v, R, s, t)
    except (OSError, ValueError, KeyError) as e:
        sys.exit(f"HATA: {e}")
    n0 = len(P)
    keep = np.isfinite(P).all(1) & np.isfinite(S).all(1)
    if args.crop:
        b = [float(x) for x in args.crop.split(",")]
        if len(b) != 6:
            sys.exit("HATA: --crop 6 değer almalı")
        keep &= (P >= b[:3]).all(1) & (P <= b[3:]).all(1)
    if args.min_alpha:
        keep &= rgba[:, 3] * 255 >= args.min_alpha
    idx = np.nonzero(keep)[0]
    idx = idx[np.argsort(-imp[idx], kind="stable")]
    if args.max_splats and len(idx) > args.max_splats:
        idx = idx[:args.max_splats]
    rec = pack(P[idx], S[idx], rgba[idx], Q[idx])
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    rec.tofile(args.output)
    print(f"{args.input}: {n0} gauss → {len(rec)} yazıldı ({n0 - len(rec)} atıldı), "
          f"{rec.nbytes / 1048576:.2f} MB → {args.output}")
    if len(rec):
        print(f"Sınır kutusu: {rec['p'].min(0).round(2).tolist()} .. {rec['p'].max(0).round(2).tolist()}")


if __name__ == "__main__":
    main()
