#!/usr/bin/env python3
"""Prosedürel Örnek Arena'dan SENTETİK bir 3D Gaussian Splatting sahnesi üretir (.splat, 32 bayt/gauss).

Gerçek çekim yokken görüntüleyicinin SplatScene yolunu uçtan uca test etmek içindir.
Girdi : demo venue.json (KoltukViewer.generateDemoVenue() çıktısı; scene.params + koltuklar)
Çıktı : .splat  [x,y,z f32][sx,sy,sz f32, doğrusal sigma][r,g,b,a u8][qw,qx,qy,qz u8 = q*128+128]
Koordinat: mekân koordinatı (metre, Y yukarı) -> transform kimlik.

Kullanım: python3 make_synthetic_splat.py demo-venue.json ../data/ornek.splat
"""
import json, math, sys
import numpy as np

rng = np.random.default_rng(7)
K = float(__import__('os').environ.get('SPLAT_K', '1.7'))  # yoğunluk katsayısı: aralıkları K ile çarpar (dosya boyutu ~1/K²)
P, SC, COL, Q = [], [], [], []

def add(pos, scale, col, theta=None, alpha=235, jitter=10):
    pos = np.asarray(pos, np.float32).reshape(-1, 3); n = len(pos)
    P.append(pos)
    SC.append(np.broadcast_to(np.asarray(scale, np.float32), (n, 3)).copy())
    c = np.broadcast_to(np.asarray(col, np.float32), (n, 3)) + rng.normal(0, jitter, (n, 3))
    a = np.full((n, 1), alpha, np.float32)
    COL.append(np.clip(np.hstack([c, a]), 0, 255).astype(np.uint8))
    th = np.zeros(n, np.float32) if theta is None else np.broadcast_to(np.asarray(theta, np.float32), (n,))
    q = np.stack([np.cos(th / 2), np.zeros(n), np.sin(th / 2), np.zeros(n)], 1)  # Y ekseni etrafında
    Q.append(q.astype(np.float32))

def curve(core, seg, f, d):
    cx, cz = core
    if seg % 2 == 0:
        if seg == 0: x, z, tx, tz = cx + d, -cz + 2 * cz * f, 0 * f, 1 + 0 * f
        elif seg == 2: x, z, tx, tz = cx - 2 * cx * f, cz + d + 0 * f, -1 + 0 * f, 0 * f
        elif seg == 4: x, z, tx, tz = -cx - d + 0 * f, cz - 2 * cz * f, 0 * f, -1 + 0 * f
        else: x, z, tx, tz = -cx + 2 * cx * f, -cz - d + 0 * f, 1 + 0 * f, 0 * f
    else:
        ox, oz, a0 = {1: (cx, cz, 0), 3: (-cx, cz, math.pi / 2), 5: (-cx, -cz, math.pi), 7: (cx, -cz, 1.5 * math.pi)}[seg]
        a = a0 + f * math.pi / 2
        x, z, tx, tz = ox + d * np.cos(a), oz + d * np.sin(a), -np.sin(a), np.cos(a)
    return x, z, tx, tz

def seglen(core, seg, d):
    return (2 * core[1] if seg % 4 == 0 else 2 * core[0]) if seg % 2 == 0 else math.pi / 2 * d

def ring(core, d, spacing):
    xs, zs, th = [], [], []
    for seg in range(8):
        n = max(1, int(math.ceil(seglen(core, seg, max(d, 0.01)) / spacing)))
        f = (np.arange(n) + 0.5) / n
        x, z, tx, tz = curve(core, seg, f, d)
        xs.append(np.broadcast_to(x, f.shape)); zs.append(np.broadcast_to(z, f.shape)); th.append(np.arctan2(-np.broadcast_to(tz, f.shape), np.broadcast_to(tx, f.shape)))
    return np.concatenate(xs), np.concatenate(zs), np.concatenate(th)

def band_h(core, d0, d1, y, spacing, col, alpha=235):  # yatay şerit (basamak)
    spacing *= K
    k = max(1, int(round((d1 - d0) / spacing)))
    for j in range(k):
        d = d0 + (j + 0.5) * (d1 - d0) / k
        x, z, th = ring(core, d, spacing)
        add(np.stack([x, np.full_like(x, y), z], 1), (spacing * 0.62, 0.012, (d1 - d0) / k * 0.62), col, th, alpha)

def band_v(core, d, y0, y1, spacing, col, alpha=235):  # dikey şerit (dikme/duvar)
    spacing *= K
    k = max(1, int(round((y1 - y0) / spacing)))
    x, z, th = ring(core, d, spacing)
    for j in range(k):
        y = y0 + (j + 0.5) * (y1 - y0) / k
        add(np.stack([x, np.full_like(x, y), z], 1), (spacing * 0.62, (y1 - y0) / k * 0.62, 0.012), col, th, alpha)

def main(src, dst):
    v = json.load(open(src)); p = v['venue']['scene']['params']; core = p['core']
    CONC, CONC2, RISER = (112, 117, 121), (100, 105, 109), (78, 82, 86)
    prev_top, prev_outer = 0.0, None
    for ti, t in enumerate(p['tiers']):
        if ti > 0: band_h(core, prev_outer, t['d0'], prev_top, 0.35, (66, 70, 74))           # ara koridor
        for r in range(t['rows']):
            d, h = t['d0'] + r * t['depth'], t['h0'] + r * t['riser']
            hp = prev_top if r == 0 else h - t['riser']
            band_v(core, d, hp, h, 0.3, RISER)
            band_h(core, d, d + t['depth'], h, 0.3, CONC if r % 2 == 0 else CONC2)
        prev_top, prev_outer = t['h0'] + (t['rows'] - 1) * t['riser'], t['d0'] + t['rows'] * t['depth']
    roof = p['roofHeight']
    band_v(core, prev_outer, prev_top, roof, 0.55, (54, 58, 62))                                 # arka duvar
    up, lo = p['tiers'][1], p['tiers'][0]; low_top = lo['h0'] + (lo['rows'] - 1) * lo['riser']
    band_v(core, up['d0'] - 0.05, low_top + (up['h0'] - low_top) * .45, low_top + (up['h0'] - low_top) * .8, 0.14, (235, 178, 52), 250)  # LED bant
    # çatı: ızgara, kase dış sınırı içinde
    g = np.arange(-(core[0] + prev_outer), core[0] + prev_outer, 0.8 * K)
    X, Z = np.meshgrid(g, np.arange(-(core[1] + prev_outer), core[1] + prev_outer, 0.8 * K))
    dx, dz = np.maximum(np.abs(X) - core[0], 0), np.maximum(np.abs(Z) - core[1], 0)
    m = np.hypot(dx, dz) < prev_outer
    add(np.stack([X[m], np.full(m.sum(), roof), Z[m]], 1), (0.5 * K, 0.02, 0.5 * K), (34, 37, 40), None, 240, 6)
    for x in np.arange(-(core[0] + prev_outer), core[0] + prev_outer, 6):                          # makaslar
        zz = np.arange(-(core[1] + prev_outer), core[1] + prev_outer, 0.25); keep = np.hypot(np.maximum(abs(x) - core[0], 0), np.maximum(np.abs(zz) - core[1], 0)) < prev_outer
        add(np.stack([np.full(keep.sum(), x), np.full(keep.sum(), roof - .6), zz[keep]], 1), (0.06, 0.06, 0.16), (70, 74, 78), None, 220, 4)
    # zemin (kase içi)
    gx = np.arange(-(core[0] + lo['d0']), core[0] + lo['d0'], 0.35 * K); gz = np.arange(-(core[1] + lo['d0']), core[1] + lo['d0'], 0.35 * K)
    X, Z = np.meshgrid(gx, gz); m = (np.abs(X) > 16.5) | (np.abs(Z) > 9.5)
    add(np.stack([X[m], np.full(m.sum(), -0.01), Z[m]], 1), (0.22 * K, 0.01, 0.22 * K), (44, 47, 50), None, 240, 5)
    # saha kenarı + saha (ahşap, çizgiler, boyalı alanlar)
    X, Z = np.meshgrid(np.arange(-16.5, 16.5, 0.25 * K), np.arange(-9.5, 9.5, 0.25 * K)); m = (np.abs(X) > 14) | (np.abs(Z) > 7.5)
    add(np.stack([X[m], np.full(m.sum(), 0.0), Z[m]], 1), (0.16 * K, 0.01, 0.16 * K), (14, 72, 54), None, 245, 5)
    X, Z = np.meshgrid(np.arange(-14 + .1, 14, 0.2), np.arange(-7.5 + .1, 7.5, 0.2)); X, Z = X.ravel(), Z.ravel()
    col = np.tile(np.array([201, 154, 98], np.float32), (len(X), 1)); col[(np.floor(Z / 0.2).astype(int) % 2) == 0] *= 0.95
    key = (np.abs(X) > 14 - 5.8) & (np.abs(Z) < 2.45); cc = np.hypot(X, Z) < 1.8
    col[key | cc] = (16, 96, 72)
    P.append(np.stack([X, np.full_like(X, 0.01), Z], 1).astype(np.float32)); SC.append(np.tile(np.array([0.13, 0.01, 0.13], np.float32), (len(X), 1)))
    COL.append(np.clip(np.hstack([col + rng.normal(0, 6, col.shape), np.full((len(X), 1), 250)]), 0, 255).astype(np.uint8)); Q.append(np.tile(np.array([1, 0, 0, 0], np.float32), (len(X), 1)))
    def line(pts):
        pts = np.asarray(pts, np.float32)
        for a, b in zip(pts[:-1], pts[1:]):
            L = float(np.hypot(*(b - a))); n = max(1, int(L / 0.05)); f = (np.arange(n) + .5) / n
            xy = a + (b - a) * f[:, None]; th = math.atan2(-(b - a)[1], (b - a)[0])
            add(np.stack([xy[:, 0], np.full(n, 0.02), xy[:, 1]], 1), (0.035, 0.005, 0.022), (245, 245, 240), th, 250, 3)
    def arc(cx, cz, r, a0, a1, n=80):
        a = np.linspace(a0, a1, n); line(np.stack([cx + r * np.cos(a), cz + r * np.sin(a)], 1))
    line([(-14, -7.5), (14, -7.5), (14, 7.5), (-14, 7.5), (-14, -7.5)]); line([(0, -7.5), (0, 7.5)]); arc(0, 0, 1.8, 0, 2 * math.pi)
    ang = math.acos(6.6 / 6.75)
    for s in (-1, 1):
        bx = s * (14 - 1.575)
        line([(s * 14, -2.45), (s * 8.2, -2.45), (s * 8.2, 2.45), (s * 14, 2.45)]); arc(s * 8.2, 0, 1.8, 0, 2 * math.pi)
        line([(s * 14, -6.6), (s * (14 - 2.99), -6.6)]); line([(s * 14, 6.6), (s * (14 - 2.99), 6.6)])
        c0 = math.pi if s > 0 else 0
        arc(bx, 0, 6.75, c0 - (math.pi / 2 - ang), c0 + (math.pi / 2 - ang))
        # pota: panya + direk
        Y, Zb = np.meshgrid(np.arange(2.95, 3.95, 0.08), np.arange(-0.9, 0.9, 0.08))
        add(np.stack([np.full(Y.size, s * 12.8), Y.ravel(), Zb.ravel()], 1), (0.01, 0.05, 0.05), (235, 238, 240), None, 200, 4)
        add(np.stack([np.full(30, s * 15.4), np.linspace(0, 3.3, 30), np.zeros(30)], 1), (0.17, 0.08, 0.17), (40, 44, 48), None, 250, 3)
        add(np.stack([np.linspace(s * 15.4, s * 12.85, 20), np.full(20, 3.2), np.zeros(20)], 1), (0.09, 0.09, 0.09), (40, 44, 48), None, 250, 3)
        a = np.linspace(0, 2 * math.pi, 24); add(np.stack([s * (14 - 1.575) + 0.23 * np.cos(a), np.full(24, 3.05), 0.23 * np.sin(a)], 1), (0.025, 0.012, 0.025), (224, 80, 42), None, 250, 2)
    # skorbord
    yb = 14.6
    for i in range(4):
        th = i * math.pi / 2; nx, nz = math.sin(th), math.cos(th)
        U, Vv = np.meshgrid(np.arange(-2.9, 2.9, 0.12), np.arange(-1.6, 1.6, 0.12)); U, Vv = U.ravel(), Vv.ravel()
        x = nx * 3.12 + U * nz; z = nz * 3.12 - U * nx
        col = np.tile(np.array([12, 14, 16], np.float32), (len(U), 1))
        col[Vv > 1.05] = (11, 110, 79)
        col[(np.abs(np.abs(U) - 1.8) < 0.55) & (np.abs(Vv + 0.1) < 0.6)] = (240, 240, 235)
        col[(np.abs(U) < 0.5) & (np.abs(Vv) < 0.2)] = (198, 244, 50)
        P.append(np.stack([x, yb + Vv, z], 1).astype(np.float32)); SC.append(np.tile(np.array([0.075, 0.075, 0.075], np.float32), (len(U), 1)))
        COL.append(np.hstack([col, np.full((len(U), 1), 252)]).astype(np.uint8)); Q.append(np.tile(np.array([1, 0, 0, 0], np.float32), (len(U), 1)))
    X, Z = np.meshgrid(np.arange(-3.1, 3.1, 0.2), np.arange(-3.1, 3.1, 0.2))
    for y in (yb - 1.8, yb + 1.8): add(np.stack([X.ravel(), np.full(X.size, y), Z.ravel()], 1), (0.13, 0.02, 0.13), (26, 29, 32), None, 250, 3)
    # koltuklar (kategori rengi): oturak + sırtlık, 4 gauss
    cat = {'CAT1': (224, 80, 42), 'CAT2': (227, 155, 18), 'CAT3': (34, 150, 138), 'CAT4': (74, 119, 212), 'CAT5': (122, 132, 150)}
    pos, cols, ths = [], [], []
    for s in v['sections']:
        c = cat.get(s['priceCategory'], (120, 120, 120))
        for r in s['rows']:
            for k in r['seats']:
                ex, ey, ez = k['eye']; th = math.atan2(-(0 - ex), -(0 - ez))
                pos.append((ex, ey - 1.15, ez)); cols.append(c); ths.append(th)
    pos = np.array(pos, np.float32); cols = np.array(cols, np.float32); ths = np.array(ths, np.float32)
    fwd = np.stack([-np.sin(ths), np.zeros_like(ths), -np.cos(ths)], 1); right = np.stack([np.cos(ths), np.zeros_like(ths), -np.sin(ths)], 1)
    # 2 gauss/koltuk (oturak + sırtlık); boyut bütçesi için yan yana ikiye bölünmez
    add(pos + np.array([0, 0.43, 0]) - fwd * 0.02, (0.17, 0.03, 0.12), cols, ths, 250, 8)
    add(pos + np.array([0, 0.68, 0]) - fwd * 0.22, (0.17, 0.13, 0.03), cols * 0.85, ths, 250, 8)

    P_, S_, C_, Q_ = np.concatenate(P), np.concatenate(SC), np.concatenate(COL), np.concatenate(Q)
    q = np.clip(np.round(Q_ / np.linalg.norm(Q_, axis=1, keepdims=True) * 128 + 128), 0, 255).astype(np.uint8)
    rec = np.zeros(len(P_), dtype=[('p', '<f4', 3), ('s', '<f4', 3), ('c', 'u1', 4), ('q', 'u1', 4)])
    rec['p'], rec['s'], rec['c'], rec['q'] = P_, S_, C_, q
    rec.tofile(dst)
    print(f'{dst}: {len(P_)} gauss, {rec.nbytes/1048576:.2f} MB')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
