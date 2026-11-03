#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_venue.py — venue.json dosyalarını JSON Schema (v0.2, draft 2020-12) ve
mantıksal kurallarla doğrular (shared/venue-schema-v0.2.md §4).

Bağımlılıklar:
  - Python 3.8+
  - jsonschema >= 4.18  (pip install jsonschema; gerekirse --break-system-packages)
    jsonschema yoksa yalnız mantıksal kontroller çalışır ve UYARI verilir.

Çıkış kodu: 0 = geçerli, 1 = hata var, 2 = (--warnings-as-errors ile) yalnız uyarı var.

Örnekler:
  python3 validate_venue.py ornek-arena.venue.json
  python3 validate_venue.py *.venue.json --schema ../shared/venue.schema.json --warnings-as-errors
"""
import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SCHEMA = os.path.normpath(os.path.join(HERE, "..", "shared", "venue.schema.json"))
V02_FIELDS = ("origin", "rotation", "files", "format", "obstructed", "lensHeight", "params")


def schema_errors(doc, schema):
    try:
        import jsonschema
    except ImportError:
        return None
    cls = jsonschema.validators.validator_for(schema)
    v = cls(schema, format_checker=cls.FORMAT_CHECKER)
    out = []
    for e in sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path)):
        path = "/".join(str(p) for p in e.absolute_path) or "(kök)"
        out.append(f"şema: {path}: {e.message[:300]}")
    return out


def logic_checks(doc, min_dist=0.30):
    """Mantıksal kontroller. (hatalar, uyarılar, istatistik) döner. Şema hatalı olsa da mümkün olduğunca çalışır."""
    err, warn = [], []
    venue = doc.get("venue") or {}
    vtype = venue.get("type")
    origin = venue.get("origin") or ("stage-front-center" if vtype in ("theatre", "concert-hall") else "field-center")
    vfocus = venue.get("focus") or [0, 1, 0]
    sections = doc.get("sections") or []

    sec_ids = [s.get("id") for s in sections]
    for k, n in Counter(sec_ids).items():
        if n > 1:
            err.append(f"tekrarlanan blok id: {k} ({n} kez)")

    seat_keys = set()
    codes = Counter()
    pts = []
    n_seats = 0
    n_obs = 0
    for s in sections:
        sid = s.get("id")
        sfocus = s.get("focus") or vfocus
        rows = s.get("rows") or []
        for k, n in Counter(r.get("id") for r in rows).items():
            if n > 1:
                err.append(f"blok {sid}: tekrarlanan sıra id {k}")
        for r in rows:
            rid = r.get("id")
            seats = r.get("seats") or []
            for k, n in Counter(st.get("id") for st in seats).items():
                if n > 1:
                    err.append(f"blok {sid} sıra {rid}: tekrarlanan koltuk id {k}")
            for st in seats:
                n_seats += 1
                seat_keys.add((sid, rid, st.get("id")))
                code = st.get("ticketCode") or f"{sid}-{rid}-{st.get('id')}"
                codes[code] += 1
                if st.get("obstructed"):
                    n_obs += 1
                e = st.get("eye")
                if not (isinstance(e, list) and len(e) == 3 and all(isinstance(v, (int, float)) for v in e)):
                    err.append(f"{sid}/{rid}/{st.get('id')}: eye geçersiz")
                    continue
                x, y, z = e
                if abs(x) > 400 or abs(z) > 400 or not (-30 <= y <= 120):
                    err.append(f"{sid}/{rid}/{st.get('id')}: eye makul aralık dışında {e}")
                if origin == "field-center" and y < 0.5:
                    warn.append(f"{sid}/{rid}/{st.get('id')}: eye.y={y} < 0.5 m (saha zemininin altında/çok alçak)")
                look = st.get("lookAt") or sfocus
                if math.dist(e, look) < 2.0:
                    warn.append(f"{sid}/{rid}/{st.get('id')}: bakış hedefine 2 m'den yakın")
                pts.append((sid, (x, y, z)))
    dups = [(c, n) for c, n in codes.items() if n > 1]
    for c, n in dups[:20]:
        err.append(f"tekrarlanan ticketCode: {c} ({n} kez)")
    if len(dups) > 20:
        err.append(f"... toplam {len(dups)} tekrarlanan ticketCode")

    cap = venue.get("capacity")
    if isinstance(cap, int) and n_seats and abs(cap - n_seats) / n_seats > 0.10:
        warn.append(f"capacity ({cap}) ile koltuk sayısı ({n_seats}) arasında %10'dan fazla fark")

    # Bloklar arası yakınlık (ızgara kovaları)
    cell = min_dist
    grid = defaultdict(list)
    for sid, p in pts:
        grid[tuple(int(math.floor(c / cell)) for c in p)].append((sid, p))
    close = Counter()
    for (gx, gy, gz), items in grid.items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for s2, q in grid.get((gx + dx, gy + dy, gz + dz), ()):
                        for s1, p in items:
                            if str(s1) < str(s2) and math.dist(p, q) < min_dist:
                                close[(s1, s2)] += 1
    for (a, b), n in close.items():
        warn.append(f"bloklar {a} ↔ {b}: {n} koltuk çifti {min_dist} m'den yakın")

    # Sahne
    scene = venue.get("scene") or {}
    tr = scene.get("transform") or {}
    q = tr.get("rotation")
    if isinstance(q, list) and len(q) == 4:
        nq = math.sqrt(sum(v * v for v in q))
        if abs(nq - 1) > 1e-3:
            err.append(f"transform.rotation birim kuaterniyon değil (|q|={nq:.4f})")
    if scene.get("kind") in ("splat", "mesh") and not (scene.get("url") or scene.get("files")):
        err.append("splat/mesh sahne için url veya files gerekli")

    # Viewpoint'ler
    vps = doc.get("viewpoints") or []
    for k, n in Counter(v.get("id") for v in vps).items():
        if n > 1:
            err.append(f"tekrarlanan viewpoint id: {k}")
    for v in vps:
        if v.get("sectionId") not in sec_ids:
            err.append(f"viewpoint {v.get('id')}: sectionId '{v.get('sectionId')}' yok")
        elif v.get("row") is not None and v.get("seat") is not None:
            if (v["sectionId"], v["row"], v["seat"]) not in seat_keys:
                err.append(f"viewpoint {v.get('id')}: koltuk {v['sectionId']}/{v['row']}/{v['seat']} yok")
        e = v.get("eye")
        if isinstance(e, list) and len(e) == 3 and (abs(e[0]) > 400 or abs(e[2]) > 400 or not (-30 <= e[1] <= 120)):
            err.append(f"viewpoint {v.get('id')}: eye makul aralık dışında")

    # Sürüm tutarlılığı
    if doc.get("schemaVersion") == "0.1":
        txt = json.dumps(doc)
        used = [f for f in V02_FIELDS if f'"{f}"' in txt]
        if used:
            warn.append(f"schemaVersion 0.1 ama v0.2 alanları var: {used}")

    stats = {"sections": len(sections), "seats": n_seats, "obstructed": n_obs, "viewpoints": len(vps),
             "origin": origin}
    return err, warn, stats


def main():
    ap = argparse.ArgumentParser(description="venue.json dosyalarını şema (v0.2) ve mantıksal kurallarla doğrular.",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("files", nargs="+", help="Doğrulanacak venue.json dosya(lar)ı.")
    ap.add_argument("--schema", default=DEFAULT_SCHEMA, help="JSON Schema dosyası.")
    ap.add_argument("--min-dist", type=float, default=0.30, help="Bloklar arası yakınlık uyarı eşiği (m).")
    ap.add_argument("--max-warnings", type=int, default=15, help="Dosya başına yazdırılacak en fazla uyarı.")
    ap.add_argument("--warnings-as-errors", action="store_true", help="Uyarı varsa çıkış kodu 2.")
    args = ap.parse_args()

    try:
        with open(args.schema, encoding="utf-8") as fh:
            schema = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"HATA: şema okunamadı: {args.schema}: {e}")

    worst = 0
    for f in args.files:
        try:
            with open(f, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[HATA] {f}: okunamadı / geçersiz JSON: {e}")
            worst = 1
            continue
        s_err = schema_errors(doc, schema)
        if s_err is None:
            print("UYARI: jsonschema kurulu değil; yalnız mantıksal kontroller yapıldı.", file=sys.stderr)
            s_err = []
        l_err, warn, st = logic_checks(doc, args.min_dist) if isinstance(doc, dict) else (["kök nesne değil"], [], {})
        errs = s_err + l_err
        status = "GEÇERSİZ" if errs else ("GEÇERLİ (uyarılı)" if warn else "GEÇERLİ")
        print(f"[{status}] {f}: sürüm {doc.get('schemaVersion')}, {st.get('sections')} blok, {st.get('seats')} koltuk, "
              f"{st.get('obstructed')} kısıtlı görüş, {st.get('viewpoints')} viewpoint, orijin {st.get('origin')}")
        for e in errs[:50]:
            print(f"  HATA: {e}")
        if len(errs) > 50:
            print(f"  ... {len(errs) - 50} hata daha")
        for w in warn[:args.max_warnings]:
            print(f"  uyarı: {w}")
        if len(warn) > args.max_warnings:
            print(f"  ... {len(warn) - args.max_warnings} uyarı daha")
        if errs:
            worst = 1
        elif warn and args.warnings_as_errors and worst == 0:
            worst = 2
    sys.exit(worst)


if __name__ == "__main__":
    main()
