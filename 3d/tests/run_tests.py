#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_tests.py — 3D araç betiklerinin sentetik verilerle uçtan uca testi.
Çalıştırma:  python3 tests/run_tests.py      (3d/ klasöründen)
Gereksinim: ffmpeg, numpy, opencv. Geçici dosyalar tests/_tmp altına yazılır ve sonda silinir
(--keep ile saklanır).
"""
import csv
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TMP = os.path.join(HERE, "_tmp")
PY = sys.executable
results = []


def run(args, expect_ok=True):
    p = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True)
    if expect_ok and p.returncode != 0:
        raise AssertionError(f"Komut başarısız: {' '.join(args)}\n{p.stdout}\n{p.stderr}")
    if not expect_ok and p.returncode == 0:
        raise AssertionError(f"Komutun başarısız olması bekleniyordu: {' '.join(args)}")
    return p


TESTS = []


def test(name):
    """Test fonksiyonunu kaydeder; çalıştırma __main__ içinde yapılır."""
    def deco(fn):
        TESTS.append((name, fn))
        return fn
    return deco


# ---------------------------------------------------------------- --help
@test("--help tüm betiklerde çalışıyor")
def t_help():
    for s in ("extract_frames.py", "equirect_to_persp.py", "filter_blurry.py", "seats_from_plan.py",
              "align_points.py", "validate_venue.py", "pipeline.py", "ply_to_splat.py", "splat_to_b64.py"):
        p = run([s, "--help"])
        assert "usage" in p.stdout.lower(), s
    return "9/9"


# ---------------------------------------------------------------- extract_frames
@test("extract_frames: 10 sn testsrc @30fps, --fps 2 → 20 kare")
def t_extract():
    vid = os.path.join(TMP, "test.mp4")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                    "testsrc=duration=10:size=1920x960:rate=30", "-pix_fmt", "yuv420p", vid], check=True)
    out = os.path.join(TMP, "frames")
    run(["extract_frames.py", vid, "-o", out, "--fps", "2"])
    frames = sorted(f for f in os.listdir(out) if f.endswith(".jpg"))
    assert len(frames) == 20, f"{len(frames)} kare"
    img = cv2.imread(os.path.join(out, frames[0]))
    assert img.shape[:2] == (960, 1920), img.shape
    # --start/--duration/--width
    out2 = os.path.join(TMP, "frames2")
    run(["extract_frames.py", vid, "-o", out2, "--fps", "1", "--start", "2", "--duration", "5", "--width", "960"])
    f2 = sorted(f for f in os.listdir(out2) if f.endswith(".jpg"))
    assert len(f2) == 5, f"{len(f2)} kare (beklenen 5)"
    assert cv2.imread(os.path.join(out2, f2[0])).shape[1] == 960
    # Üzerine yazma koruması
    run(["extract_frames.py", vid, "-o", out, "--fps", "2"], expect_ok=False)
    return "20 kare 1920x960; start/duration/width alt testi 5 kare 960px; üzerine yazma koruması OK"


# ---------------------------------------------------------------- equirect_to_persp
def synthetic_equirect(w=2048):
    """Her pikselin rengi kendi boylam/enlemini kodlar: B=boylam, G=enlem; ayrıca 30°'lik ızgara."""
    h = w // 2
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    lon = ((u + 0.5) / w - 0.5) * 360.0     # -180..180
    lat = (0.5 - (v + 0.5) / h) * 180.0     # 90..-90
    img = np.zeros((h, w, 3), np.uint8)
    img[..., 0] = np.round((lon + 180) / 360 * 255)
    img[..., 1] = np.round((lat + 90) / 180 * 255)
    grid = (np.abs(((lon + 15) % 30) - 15) < 0.4) | (np.abs(((lat + 15) % 30) - 15) < 0.4)
    img[..., 2] = np.where(grid, 255, 0)
    return img


@test("equirect_to_persp: görünüm merkezleri doğru boylam/enleme bakıyor")
def t_persp():
    src = os.path.join(TMP, "eq")
    os.makedirs(src, exist_ok=True)
    cv2.imwrite(os.path.join(src, "eq_00001.png"), synthetic_equirect())
    out = os.path.join(TMP, "persp")
    run(["equirect_to_persp.py", src, "-o", out, "--yaw-count", "8", "--pitches", "0,30,-30",
         "--stagger", "--zenith", "--fov", "90", "--size", "512", "--ext", "png", "--colmap-cameras"])
    files = sorted(f for f in os.listdir(out) if f.endswith(".png"))
    assert len(files) == 25, f"{len(files)} görüntü (beklenen 8*3+1=25)"
    meta = json.load(open(os.path.join(out, "views.json")))
    worst_lon = worst_lat = 0.0
    for vw in meta["views"]:
        if abs(vw["pitch"]) >= 89:
            continue
        img = cv2.imread(os.path.join(out, "eq_00001" + vw["suffix"] + ".png"))
        c = img[255:257, 255:257].reshape(-1, 3).astype(float).mean(0)
        lon = c[0] / 255 * 360 - 180
        lat = c[1] / 255 * 180 - 90
        exp_lon = ((vw["yaw"] + 180) % 360) - 180
        dlon = abs(((lon - exp_lon + 180) % 360) - 180)
        if abs(exp_lon) > 178:  # ±180 sarmalama dikişi: renk kodu süreksiz, atla
            dlon = 0
        worst_lon = max(worst_lon, dlon)
        worst_lat = max(worst_lat, abs(lat - vw["pitch"]))
    assert worst_lon < 1.5 and worst_lat < 1.5, f"sapma lon {worst_lon:.2f}°, lat {worst_lat:.2f}°"
    # Zenit görünümü merkezi enlem ~ +90
    z = cv2.imread(os.path.join(out, "eq_00001_y000_p+90.png"))
    zl = z[256, 256, 1] / 255 * 180 - 90
    assert zl > 85, f"zenit enlemi {zl:.1f}"
    # Yatay FOV kontrolü: yaw=0 görünümünde sol/sağ kenar boylamı ±45°
    img = cv2.imread(os.path.join(out, "eq_00001_y000_p+00.png")).astype(float)
    l_edge = img[256, 0, 0] / 255 * 360 - 180
    r_edge = img[256, 511, 0] / 255 * 360 - 180
    assert abs(l_edge + 45) < 1.5 and abs(r_edge - 45) < 1.5, f"kenarlar {l_edge:.1f} / {r_edge:.1f}"
    cams = open(os.path.join(out, "cameras.txt")).read()
    assert "PINHOLE 512 512 256.0" in cams, cams
    return (f"25 görüntü; merkez sapması maks lon {worst_lon:.2f}°, lat {worst_lat:.2f}°; "
            f"FOV kenarları {l_edge:.1f}°/{r_edge:.1f}°; zenit {zl:.1f}°; cameras.txt f=256 px")


# ---------------------------------------------------------------- filter_blurry
@test("filter_blurry: bulanık kareler eleniyor, pencere modu en keskini tutuyor")
def t_blur():
    src = os.path.join(TMP, "blur_in")
    os.makedirs(src, exist_ok=True)
    rng = np.random.default_rng(0)
    base = (rng.random((480, 960)) * 255).astype(np.uint8)
    base = cv2.resize(cv2.resize(base, (240, 120)), (960, 480), interpolation=cv2.INTER_NEAREST)
    base = cv2.cvtColor(base, cv2.COLOR_GRAY2BGR)
    blurry = set()
    for i in range(12):
        k = [0, 0, 9, 0, 15, 0, 0, 21, 0, 5, 0, 31][i]  # 0 = keskin
        img = base if k == 0 else cv2.GaussianBlur(base, (k, k), 0)
        if k >= 9:
            blurry.add(i)
        cv2.imwrite(os.path.join(src, f"f_{i:05d}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    out = os.path.join(TMP, "blur_out")
    p = run(["filter_blurry.py", src, "-o", out, "--percentile", "34"])
    kept = {int(f[2:7]) for f in os.listdir(out) if f.endswith(".jpg")}
    assert not (kept & blurry), f"bulanık kareler tutuldu: {sorted(kept & blurry)}"
    assert len(kept) == 8, f"{len(kept)} tutuldu (beklenen 8)"
    rows = list(csv.DictReader(open(os.path.join(out, "scores.csv"))))
    s = {int(r["file"][2:7]): float(r["sharpness"]) for r in rows}
    # Pencere modu: 3'lük pencerelerde yalnız en keskin; bulanıklar asla seçilmemeli
    out2 = os.path.join(TMP, "blur_win")
    run(["filter_blurry.py", src, "-o", out2, "--window", "3"])
    kept2 = sorted(int(f[2:7]) for f in os.listdir(out2) if f.endswith(".jpg"))
    assert len(kept2) == 4 and not (set(kept2) & blurry), kept2
    # Mutlak eşik
    thr = (min(s[i] for i in s if i not in blurry) + max(s[i] for i in blurry)) / 2
    out3 = os.path.join(TMP, "blur_thr")
    run(["filter_blurry.py", src, "-o", out3, "--threshold", f"{thr:.1f}", "--crop-poles", "0.15"])
    kept3 = {int(f[2:7]) for f in os.listdir(out3) if f.endswith(".jpg")}
    assert kept3 & blurry == set() and len(kept3) >= 7, kept3
    sharp = [s[i] for i in s if i not in blurry and i != 9]
    return (f"yüzdelik: 8/12 tutuldu, 4 bulanığın hepsi elendi; pencere(3): {kept2}; "
            f"keskin skor ~{min(sharp):.0f}, sigma-31 skoru {s[11]:.1f}")


# ---------------------------------------------------------------- seats_from_plan
@test("seats_from_plan: örnek arena şemaya uygun, geometri ve numaralandırma doğru")
def t_seats():
    out = os.path.join(TMP, "arena.json")
    plan = os.path.join(TMP, "plan.csv")
    seats_csv = os.path.join(TMP, "seats.csv")
    run(["seats_from_plan.py", "ornek-bloklar.csv", "-o", out, "--capture-plan", plan, "--seats-csv", seats_csv])
    v = json.load(open(out, encoding="utf-8"))
    assert v["schemaVersion"] == "0.2", v["schemaVersion"]
    for k in ("id", "name", "type", "capacity", "focus", "scene"):
        assert k in v["venue"], k
    assert v["venue"]["scene"]["kind"] == "procedural" and v["venue"]["scene"]["url"] is None
    n = sum(len(r["seats"]) for s in v["sections"] for r in s["rows"])
    assert 11000 <= n <= 13000 and v["venue"]["capacity"] == n, n
    assert len(v["sections"]) >= 12
    tiers = {s["tier"] for s in v["sections"]}
    assert tiers == {"lower", "upper"}, tiers
    codes = [st["ticketCode"] for s in v["sections"] for r in s["rows"] for st in r["seats"]]
    assert len(codes) == len(set(codes)), "tekrarlanan ticketCode"
    sec = {s["id"]: s for s in v["sections"]}
    # 103: z=+11.5'te, -Z'ye bakan uzun kenar. 1. sıra göz y = 0.3 + 1.15
    r1 = sec["103"]["rows"][0]["seats"]
    assert all(abs(st["eye"][2] - 11.5) < 1e-6 and abs(st["eye"][1] - 1.45) < 1e-6 for st in r1)
    # -Z'ye bakan izleyicinin solu -X → koltuk 1 en küçük x
    assert r1[0]["eye"][0] < r1[-1]["eye"][0], "103 koltuk 1 solda değil"
    # 18. sıra 17*0.85 m geride (+Z) ve 17*0.42 m yukarıda
    r18 = sec["103"]["rows"][17]["seats"][0]["eye"]
    assert abs(r18[2] - (11.5 + 17 * 0.85)) < 1e-3 and abs(r18[1] - (1.45 + 17 * 0.42)) < 1e-3, r18
    # Arc 102: tüm 1. sıra koltukları merkezden 4 m uzakta; komşu koltuk aralığı ~0.5 m
    a = sec["102"]["rows"][0]["seats"]
    for st in a:
        assert abs(math.hypot(st["eye"][0] - 14, st["eye"][2] - 7.5) - 4.0) < 1e-3
    d = math.dist(a[0]["eye"], a[1]["eye"])
    assert abs(d - 0.5) < 0.01, d
    # Köşe 102'de (yay merkezi (14,7.5), içe bakış): koltuk 1 solda → en büyük açıda
    ang = lambda st: math.atan2(st["eye"][2] - 7.5, st["eye"][0] - 14)
    assert ang(a[0]) > ang(a[-1])
    # Plan dosyası
    prow = list(csv.DictReader(open(plan, encoding="utf-8")))
    assert len(prow) >= 3 * 24 and all(r["suggestedFile"].startswith("ORNK_") for r in prow)
    return (f"{len(v['sections'])} blok, {n} koltuk, ticketCode benzersiz; 103/102 geometri ve 'koltuk 1 solda' "
            f"kontrolleri OK; çekim planı {len(prow)} nokta")


@test("seats_from_plan: bilet eşleme, --strict, viewpoints, alpha sıra, hatalı girdi")
def t_tickets():
    blocks = os.path.join(TMP, "mini.csv")
    with open(blocks, "w", encoding="utf-8") as fh:
        fh.write("section,tier,priceCategory,shape,cx,cz,facingDeg,rows,seatsPerRow,seatsPerRowIncrement,"
                 "rowLabels,riserHeight,frontHeight,seatOrder\n")
        fh.write("SALON,lower,CAT1,line,0,6,270,3,4,2,alpha,0.15,0,rtl\n")
    tk = os.path.join(TMP, "tickets.csv")
    with open(tk, "w", encoding="utf-8") as fh:
        fh.write("section,row,seat,ticketCode\nSALON,A,1,TKT-0001\nSALON,C,8,TKT-0099\nSALON,Z,1,TKT-YOK\n")
    vp = os.path.join(TMP, "vp.csv")
    with open(vp, "w", encoding="utf-8") as fh:
        fh.write("id,sectionId,row,seat,file,type,takenAt\n")
        fh.write("vp-SALON-on,SALON,A,2,TST_SALON_RAS2_P360_01.jpg,equirect-360,2026-11-15T10:30:00+03:00\n")
    out = os.path.join(TMP, "mini.json")
    p = run(["seats_from_plan.py", blocks, "-o", out, "--tickets", tk, "--viewpoints", vp,
             "--type", "theatre", "--venue-id", "test-salon", "--name", "Test Salonu", "--indent", "2"])
    v = json.load(open(out, encoding="utf-8"))
    rows = v["sections"][0]["rows"]
    assert [r["id"] for r in rows] == ["A", "B", "C"]
    assert [len(r["seats"]) for r in rows] == [4, 6, 8]
    assert rows[0]["seats"][0]["ticketCode"] == "TKT-0001"
    assert rows[2]["seats"][7]["ticketCode"] == "TKT-0099"
    assert rows[1]["seats"][0]["ticketCode"] == "SALON-B-1"
    # rtl: koltuk 1 sağda; -Z'ye bakan izleyicinin sağı +X
    assert rows[0]["seats"][0]["eye"][0] > rows[0]["seats"][-1]["eye"][0]
    assert v["viewpoints"][0]["eye"] == rows[0]["seats"][1]["eye"]
    assert "geometride yok" in p.stdout
    run(["seats_from_plan.py", blocks, "-o", out, "--tickets", tk, "--strict"], expect_ok=False)
    bad = os.path.join(TMP, "bad.csv")
    with open(bad, "w", encoding="utf-8") as fh:
        fh.write("section,tier,shape,cx,cz,rows\nX,balkon,line,0,0,3\n")
    pb = run(["seats_from_plan.py", bad, "-o", out], expect_ok=False)
    assert "tier" in pb.stderr + pb.stdout
    # Çakışma uyarısı: aynı yere iki blok
    ov = os.path.join(TMP, "ov.csv")
    with open(ov, "w", encoding="utf-8") as fh:
        fh.write("section,tier,shape,cx,cz,facingDeg,rows,seatsPerRow\nA,lower,line,0,6,270,2,4\nB,lower,line,0,6,270,2,4\n")
    po = run(["seats_from_plan.py", ov, "-o", out])
    assert "UYARI" in po.stderr
    return "alpha sıralar A-C, artan koltuk 4/6/8, eşleme+desen, rtl, viewpoint göz=koltuk, --strict hata, geçersiz tier hata, çakışma uyarısı OK"


# ---------------------------------------------------------------- align_points
@test("align_points: bilinen dönüşüm (ölçek 0.37, 33°, öteleme, 1 cm gürültü) geri bulunuyor")
def t_align():
    rng = np.random.default_rng(1)
    V = np.array([[14, 0, 7.5], [-14, 0, 7.5], [-14, 0, -7.5], [14, 0, -7.5], [0, 0, 0],
                  [0, 8.6, 26.0], [32.5, 8.6, 0]], float)
    def make(tilt_deg):
        s, th = 0.37, math.radians(33)
        Ry = np.array([[math.cos(th), 0, math.sin(th)], [0, 1, 0], [-math.sin(th), 0, math.cos(th)]])
        a = math.radians(tilt_deg)
        Rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
        R = Ry @ Rx
        t = np.array([3.0, -1.2, 5.5])
        # splat = R^-1 (venue - t) / s  (+ gürültü venue ölçeğinde 1 cm)
        Sp = ((V + rng.normal(0, 0.01, V.shape) - t) @ R) / s
        path = os.path.join(TMP, f"ctrl_{tilt_deg}.csv")
        with open(path, "w") as fh:
            fh.write("name,sx,sy,sz,vx,vy,vz\n")
            for i, (a_, b_) in enumerate(zip(Sp, V)):
                fh.write(f"p{i}," + ",".join(f"{x:.6f}" for x in a_) + "," + ",".join(f"{x}" for x in b_) + "\n")
        return path
    out = os.path.join(TMP, "align.json")
    run(["align_points.py", make(0), "--json", out])
    r = json.load(open(out))
    assert abs(r["scale"] - 0.37) < 0.002 and abs(r["rotationYDeg"] - 33) < 0.1, r
    assert np.allclose(r["position"], [3.0, -1.2, 5.5], atol=0.03), r["position"]
    assert r["rms"] < 0.03, r["rms"]
    p = run(["align_points.py", make(2.0), "--mode", "full", "--json", out])
    r2 = json.load(open(out))
    assert abs(r2["tiltDeg"] - 2.0) < 0.1 and "UYARI" in p.stderr, r2["tiltDeg"]
    return (f"level: ölçek {r['scale']:.4f}, rotY {r['rotationYDeg']:.2f}°, RMS {r['rms']*100:.1f} cm; "
            f"full: 2° eğim {r2['tiltDeg']:.2f}° olarak bulundu ve uyarı verildi")


# ---------------------------------------------------------------- v0.2: şema, doğrulama, şablonlar
SCHEMA = os.path.normpath(os.path.join(ROOT, "..", "shared", "venue.schema.json"))


@test("venue.schema.json: geçerli draft 2020-12 şeması; v0.1 dosyası da geçiyor")
def t_schema():
    import jsonschema
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    v1 = {"schemaVersion": "0.1",
          "venue": {"id": "ornek-arena", "name": "Örnek Arena", "type": "arena", "capacity": 1, "focus": [0, 1.0, 0],
                    "scene": {"kind": "procedural", "url": None,
                              "transform": {"position": [0, 0, 0], "rotationY": 0, "scale": 1}}},
          "sections": [{"id": "A1", "name": "Alt Kat A1", "tier": "lower", "priceCategory": "CAT1", "focus": [0, 1.0, 0],
                        "rows": [{"id": "1", "seats": [{"id": "1", "ticketCode": "A1-1-1", "eye": [12.4, 3.1, -18.2],
                                                         "lookAt": [0, 1.0, 0]}]}]}],
          "viewpoints": [{"id": "vp-A1-front", "sectionId": "A1", "eye": [12.0, 2.4, -16.5], "lookAt": [0, 1.0, 0],
                          "capture": {"file": "A1_front.jpg", "type": "equirect-360",
                                      "takenAt": "2026-11-15T10:30:00+03:00"}}]}
    p = os.path.join(TMP, "v01.json")
    json.dump(v1, open(p, "w"))
    run(["validate_venue.py", p])
    # Web demosunun biçimi: params + capture:null (v0.1 etiketiyle → uyarı, hata değil)
    v1["venue"]["scene"]["params"] = {"core": {"w": 28}}
    v1["viewpoints"][0]["capture"] = None
    json.dump(v1, open(p, "w"))
    r = run(["validate_venue.py", p])
    assert "v0.2 alanları" in r.stdout, r.stdout
    return "check_schema OK; v0.1 örnek dosyası geçerli; web demo biçimi (params, capture:null) geçerli + sürüm uyarısı"


@test("validate_venue: bozuk dosyalarda hataları yakalıyor")
def t_validate_bad():
    base = json.load(open(os.path.join(ROOT, "sablon-spor-salonu.venue.json"), encoding="utf-8"))
    cases = {}
    import copy
    d = copy.deepcopy(base); d["sections"][1]["id"] = d["sections"][0]["id"]; cases["blok id tekrarı"] = (d, "tekrarlanan blok id")
    d = copy.deepcopy(base); d["sections"][0]["rows"][0]["seats"][1]["ticketCode"] = d["sections"][0]["rows"][0]["seats"][0]["ticketCode"]; cases["ticketCode tekrarı"] = (d, "tekrarlanan ticketCode")
    d = copy.deepcopy(base); d["sections"][0]["rows"][0]["seats"][0]["eye"] = [5000, 1, 0]; cases["eye aralık dışı"] = (d, "makul aralık")
    d = copy.deepcopy(base); d["venue"]["scene"] = {"kind": "splat", "url": None, "params": {}}; cases["splat+params, url yok"] = (d, "şema: venue/scene")
    d = copy.deepcopy(base); d["venue"]["scene"]["transform"]["rotation"] = [0, 0.5, 0, 0.5]; cases["birim olmayan kuaterniyon"] = (d, "birim kuaterniyon")
    d = copy.deepcopy(base); d["sections"][0]["rows"][0]["seats"][0]["obstructed"] = {"severity": "biraz"}; cases["geçersiz obstructed"] = (d, "obstructed")
    d = copy.deepcopy(base); d["sections"][0]["koltukSayisi"] = 3; cases["tanımsız alan"] = (d, "koltukSayisi")
    d = copy.deepcopy(base); d["viewpoints"] = [{"id": "v", "sectionId": "YOK", "eye": [0, 2, 9]}]; cases["viewpoint blok yok"] = (d, "sectionId")
    d = copy.deepcopy(base); d["schemaVersion"] = "0.3"; cases["bilinmeyen sürüm"] = (d, "schemaVersion")
    for name, (doc, needle) in cases.items():
        p = os.path.join(TMP, "bad.json")
        json.dump(doc, open(p, "w"))
        r = run(["validate_venue.py", p], expect_ok=False)
        assert needle in r.stdout, f"{name}: '{needle}' bulunamadı\n{r.stdout[:800]}"
    # Uyarı modu: aynı yere iki blok → yakınlık uyarısı → --warnings-as-errors çıkış 2
    d = copy.deepcopy(base); d["sections"][1]["rows"] = copy.deepcopy(d["sections"][0]["rows"])
    for r_ in d["sections"][1]["rows"]:
        for st in r_["seats"]:
            st["ticketCode"] += "-kopya"
    p = os.path.join(TMP, "warn.json"); json.dump(d, open(p, "w"))
    pr = subprocess.run([PY, "validate_venue.py", p, "--warnings-as-errors"], cwd=ROOT, capture_output=True, text=True)
    assert pr.returncode == 2 and "yakın" in pr.stdout, pr.stdout
    return f"{len(cases)} bozuk durumun hepsi HATA verdi; yakınlık uyarısı + --warnings-as-errors çıkış 2"


@test("seats_from_plan v0.2: obstructed, origin, LOD dosyaları, kuaterniyon, params, viewpoint row/seat/lensHeight")
def t_v02():
    out = os.path.join(TMP, "v02.json")
    vp = os.path.join(TMP, "vp2.csv")
    with open(vp, "w", encoding="utf-8") as fh:
        fh.write("id,sectionId,row,seat,file,type,takenAt,lensHeight\n")
        fh.write("vp-PO-on,PO,A,5,STYT_PO_RAS5_P360_01.jpg,equirect-360,2026-11-15T10:30:00+03:00,1.17\n")
        fh.write("vp-PO-arka,PO,O,10,,,,\n")
    run(["seats_from_plan.py", "sablon-tiyatro-bloklar.csv", "-o", out, "--type", "theatre", "--venue-id", "t",
         "--name", "T", "--focus", "0,1.2,-3", "--obstructed", "sablon-tiyatro.kisitli.csv", "--viewpoints", vp,
         "--scene-kind", "splat", "--scene-format", "sog", "--scene-file", "lod2.sog,2",
         "--scene-file", "parter.sog,0,parter", "--scene-file", "balkon.sog,0,balkon",
         "--scene-transform", "0.1,0,-0.2,90,1.02", "--scene-rotation", "0,0.7071068,0,0.7071068"])
    run(["validate_venue.py", out])
    v = json.load(open(out, encoding="utf-8"))
    sc = v["venue"]["scene"]
    assert v["schemaVersion"] == "0.2" and v["venue"]["origin"] == "stage-front-center"
    assert sc["url"] is None and len(sc["files"]) == 3 and sc["files"][1] == {"url": "parter.sog", "format": "sog", "lod": 0, "region": "parter"}
    assert sc["transform"]["rotationY"] == 90 and abs(sum(q * q for q in sc["transform"]["rotation"]) - 1) < 1e-6
    po = next(s for s in v["sections"] if s["id"] == "PO")
    rowO = next(r for r in po["rows"] if r["id"] == "O")
    assert all(st["obstructed"]["severity"] == "partial" for st in rowO["seats"])
    assert "obstructed" not in po["rows"][0]["seats"][0]
    assert po["rows"][0]["seats"][0]["eye"][1] < 0.5  # parter sahne döşemesinin altında: y = -0.9 + 1.15
    vps = {x["id"]: x for x in v["viewpoints"]}
    assert vps["vp-PO-on"]["row"] == "A" and vps["vp-PO-on"]["lensHeight"] == 1.17
    assert vps["vp-PO-arka"]["capture"] is None and vps["vp-PO-arka"]["lensHeight"] == 1.15
    # procedural + params
    pj = os.path.join(TMP, "params.json"); json.dump({"roofHeight": 22, "tiers": []}, open(pj, "w"))
    run(["seats_from_plan.py", "sablon-spor-salonu-bloklar.csv", "-o", out, "--params-json", pj])
    run(["validate_venue.py", out])
    assert json.load(open(out))["venue"]["scene"]["params"]["roofHeight"] == 22
    # params + splat → hata
    run(["seats_from_plan.py", "sablon-spor-salonu-bloklar.csv", "-o", out, "--params-json", pj,
         "--scene-kind", "splat", "--scene-url", "a.ply"], expect_ok=False)
    n_obs = sum(1 for s in v["sections"] for r in s["rows"] for st in r["seats"] if "obstructed" in st)
    return f"tiyatro splat+LOD(3 dosya)+kuaterniyon geçerli; {n_obs} kısıtlı koltuk; viewpoint row/seat/lensHeight/capture:null; params yalnız procedural"


@test("şablonlar ve örnek arena: v0.2, doğrulanıyor, kapasite aralıkları tutuyor")
def t_templates():
    summary = []
    for f, lo, hi, origin in (("ornek-arena.venue.json", 11000, 13000, "field-center"),
                              ("sablon-tiyatro.venue.json", 600, 900, "stage-front-center"),
                              ("sablon-spor-salonu.venue.json", 2000, 3000, "field-center")):
        run(["validate_venue.py", f, "--warnings-as-errors"])
        v = json.load(open(os.path.join(ROOT, f), encoding="utf-8"))
        n = sum(len(r["seats"]) for s in v["sections"] for r in s["rows"])
        assert v["schemaVersion"] == "0.2" and v["venue"]["origin"] == origin and lo <= n <= hi, (f, n)
        summary.append(f"{f.split('.')[0]}={n}")
    t = json.load(open(os.path.join(ROOT, "sablon-tiyatro.venue.json"), encoding="utf-8"))
    tiers = {s["tier"] for s in t["sections"]}
    assert tiers == {"lower", "upper"}
    # Tiyatroda tüm seyirci +Z tarafında (sahne −Z), sol bloklar −X'te
    assert all(st["eye"][2] > 0 for s in t["sections"] for r in s["rows"] for st in r["seats"])
    ps = next(s for s in t["sections"] if s["id"] == "PS")
    assert all(st["eye"][0] < 0 for r in ps["rows"] for st in r["seats"])
    for plan in ("sablon-tiyatro.cekim-plani.csv", "sablon-spor-salonu.cekim-plani.csv"):
        rows = list(csv.DictReader(open(os.path.join(ROOT, plan), encoding="utf-8")))
        assert len(rows) >= 12 and rows[0]["suggestedFile"][:4] in ("STYT", "SSPR")
        summary.append(f"{plan.split('.')[0]} {len(rows)} nokta")
    return ", ".join(summary)


# ---------------------------------------------------------------- pipeline
def make_shoot(root):
    """Sentetik çekim klasörü: dönen dokulu equirect video (bulanık bölümlü) + 2 sabit foto + 1 kurala uymayan dosya."""
    rng = np.random.default_rng(3)
    pano = (rng.random((64, 128)) * 255).astype(np.uint8)
    pano = cv2.resize(pano, (1024, 512), interpolation=cv2.INTER_NEAREST)
    pano = cv2.cvtColor(pano, cv2.COLOR_GRAY2BGR)
    pano[:, :, 1] = np.roll(pano[:, :, 1], 37, axis=1)
    vdir = os.path.join(root, "01_adlandirilmis", "V360")
    pdir = os.path.join(root, "01_adlandirilmis", "P360")
    os.makedirs(vdir); os.makedirs(pdir)
    fdir = os.path.join(TMP, "src_frames"); os.makedirs(fdir)
    blur_src = set(range(20, 26)) | set(range(40, 46))
    for i in range(60):  # 6 sn @ 10 fps; her karede 4 px yaw dönüşü
        img = np.roll(pano, i * 4, axis=1)
        if i in blur_src:
            img = cv2.GaussianBlur(img, (21, 21), 0)
        cv2.imwrite(os.path.join(fdir, f"s_{i:04d}.png"), img)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "10", "-i",
                    os.path.join(fdir, "s_%04d.png"), "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p",
                    os.path.join(vdir, "TEST_GENEL_ROTA-saha-cevre_V360_01.mp4")], check=True)
    shutil.copy(os.path.join(vdir, "TEST_GENEL_ROTA-saha-cevre_V360_01.mp4"), os.path.join(vdir, "VID_20261115_kamera.mp4"))
    cv2.imwrite(os.path.join(pdir, "TEST_PO_RAS5_P360_01.jpg"), pano)
    cv2.imwrite(os.path.join(pdir, "TEST_PO_ROS10_P360_01.jpg"), np.roll(pano, 200, axis=1))
    sharp = fb.sharpness(os.path.join(fdir, "s_0000.png"), 1024, 0.15)
    blurry = fb.sharpness(os.path.join(fdir, "s_0022.png"), 1024, 0.15)
    return sharp, blurry


@test("pipeline: sentetik çekim klasöründen images/ + rapor + dry-run komutları")
def t_pipeline():
    sys.path.insert(0, ROOT)
    global fb
    import filter_blurry as fb  # noqa
    shoot = os.path.join(TMP, "2026-11-15_TEST")
    sharp, blurry = make_shoot(shoot)
    p = run(["pipeline.py", shoot, "--fps", "5", "--skip-start", "0.5", "--skip-end", "0.5", "--window", "2",
             "--percentile", "10", "--jobs", "4"])
    out = os.path.join(shoot, "10_isleme")
    rep = json.load(open(os.path.join(out, "rapor.json"), encoding="utf-8"))
    c = rep["counts"]
    assert rep["nonconforming"] == ["VID_20261115_kamera.mp4"], rep["nonconforming"]
    assert 23 <= c["framesExtracted"] <= 26, c
    # Seçilen equirect karelerin hiçbiri bulanık olmamalı
    sc = list(csv.DictReader(open(os.path.join(out, "secilen", "TEST_GENEL_ROTA-saha-cevre_V360_01", "scores.csv"))))
    mid = (sharp + blurry) / 2
    kept_blurry = [r["file"] for r in sc if r["keep"] == "1" and float(r["sharpness"]) < mid]
    n_blurry = sum(1 for r in sc if float(r["sharpness"]) < mid)
    assert n_blurry >= 4 and not kept_blurry, (n_blurry, kept_blurry)
    imgs = [f for f in os.listdir(os.path.join(out, "images")) if f.endswith(".jpg")]
    assert c["perspectiveGenerated"] == c["framesSelected"] * 16 + 2 * 24, c
    assert len(imgs) == c["imagesFinal"] == c["perspectiveGenerated"] - c["perspectiveDropped"], (len(imgs), c)
    assert cv2.imread(os.path.join(out, "images", imgs[0])).shape[:2] == (256, 256)
    for f in ("cameras.txt", "views.json", "goruntu_dizini.csv", "rapor.md", "komutlar.sh"):
        assert os.path.isfile(os.path.join(out, f)), f
    cmds = open(os.path.join(out, "komutlar.sh")).read()
    assert "colmap mapper" in cmds and "ns-train splatfacto" in cmds and "[DRY-RUN]" in p.stdout
    # Dolu çıktı klasörü korunuyor; --force ile yeniden çalışıyor
    run(["pipeline.py", shoot], expect_ok=False)
    return (f"{c['framesExtracted']} kare → {c['framesSelected']} seçildi ({n_blurry} bulanık karenin hiçbiri seçilmedi); "
            f"{c['perspectiveGenerated']} perspektif → {c['imagesFinal']} images/; kural dışı dosya atlandı; "
            f"süre {rep['timingSec']['toplam']} sn")


# ---------------------------------------------------------------- 3. tur: ply → splat → b64, bulut betiği
WEB_SPLAT = os.path.normpath(os.path.join(ROOT, "..", "web", "data", "ornek.splat"))
# web/tools/make_synthetic_splat.py içindeki kayıt yapısının birebir kopyası
WEB_DTYPE = np.dtype([("p", "<f4", 3), ("s", "<f4", 3), ("c", "u1", 4), ("q", "u1", 4)])


def write_3dgs_ply(path, P, logS, Q, op, fdc, binary=True):
    """Gerçek 3DGS eğitim çıktısıyla aynı alan düzeninde (.ply) sentetik dosya yazar."""
    names = ["x", "y", "z", "nx", "ny", "nz", "f_dc_0", "f_dc_1", "f_dc_2"] + [f"f_rest_{i}" for i in range(45)] + \
            ["opacity", "scale_0", "scale_1", "scale_2", "rot_0", "rot_1", "rot_2", "rot_3"]
    n = len(P)
    arr = np.zeros(n, dtype=[(k, "<f4") for k in names])
    for i, k in enumerate("xyz"):
        arr[k] = P[:, i]
    for i in range(3):
        arr[f"f_dc_{i}"] = fdc[:, i]
        arr[f"scale_{i}"] = logS[:, i]
    for i in range(4):
        arr[f"rot_{i}"] = Q[:, i]
    arr["opacity"] = op
    arr["f_rest_0"] = 0.3  # atılması gereken SH verisi
    hdr = "ply\nformat {} 1.0\nelement vertex {}\n".format("binary_little_endian" if binary else "ascii", n)
    hdr += "".join(f"property float {k}\n" for k in names) + "end_header\n"
    with open(path, "wb") as fh:
        fh.write(hdr.encode())
        if binary:
            fh.write(arr.tobytes())
        else:
            for r in arr:
                fh.write((" ".join(f"{float(v):.7g}" for v in r) + "\n").encode())


def js_cov(rec):
    """web/demo.html SplatMesh'in kovaryans hesabının Python eşleniği: Σ = (R·S)(R·S)ᵀ."""
    q = (rec["q"].astype(np.float64) - 128) / 128
    q /= np.linalg.norm(q, axis=1, keepdims=True)
    w, x, y, z = q.T
    R = np.stack([np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], -1),
                  np.stack([2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)], -1),
                  np.stack([2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], -1)], 1)
    M = R * rec["s"].astype(np.float64)[:, None, :]
    return M @ np.transpose(M, (0, 2, 1))


def qmat(q):
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


@test("ply_to_splat: sentetik 3DGS .ply → .splat; web formatıyla aynı yapı; renk/opaklık/kovaryans doğru")
def t_ply_to_splat():
    rng = np.random.default_rng(5)
    n = 500
    P = rng.uniform(-20, 20, (n, 3))
    logS = rng.uniform(-4, -0.5, (n, 3))
    Q = rng.normal(size=(n, 4)) * rng.uniform(0.5, 3, (n, 1))  # normalize edilmemiş (gerçek çıktı gibi)
    op = rng.normal(0, 3, n)
    fdc = rng.normal(0, 1.2, (n, 3))
    ply = os.path.join(TMP, "s.ply"); out = os.path.join(TMP, "s.splat")
    write_3dgs_ply(ply, P, logS, Q, op, fdc)
    run(["ply_to_splat.py", ply, out])
    raw = open(out, "rb").read()
    assert len(raw) == n * 32, len(raw)
    rec = np.frombuffer(raw, dtype=WEB_DTYPE)
    # Önem sırası: exp(Σ log s)·sigmoid(op) azalan
    imp = np.exp(logS.sum(1)) / (1 + np.exp(-op))
    order = np.argsort(-imp, kind="stable")
    assert np.allclose(rec["p"], P[order], atol=1e-4)
    assert np.allclose(rec["s"], np.exp(logS[order]), rtol=1e-5)
    exp_c = np.clip(np.round((0.5 + 0.28209479177387814 * fdc[order]) * 255), 0, 255)
    exp_a = np.clip(np.round(255 / (1 + np.exp(-op[order]))), 0, 255)
    assert np.abs(rec["c"][:, :3].astype(int) - exp_c).max() <= 1 and np.abs(rec["c"][:, 3].astype(int) - exp_a).max() <= 1
    # Kovaryans: SplatMesh hesabı vs. gerçek (uint8 kuaterniyon nicemlemesi toleransı)
    Rq = np.stack([qmat(q) for q in Q[order]])
    Strue = np.exp(logS[order])
    Mt = Rq * Strue[:, None, :]
    cov_true = Mt @ np.transpose(Mt, (0, 2, 1))
    rel = np.linalg.norm(js_cov(rec) - cov_true, axis=(1, 2)) / np.linalg.norm(cov_true, axis=(1, 2))
    assert np.median(rel) < 0.02 and rel.max() < 0.15, (np.median(rel), rel.max())
    # ASCII PLY aynı sonucu vermeli
    ply2 = os.path.join(TMP, "s_ascii.ply"); out2 = os.path.join(TMP, "s2.splat")
    write_3dgs_ply(ply2, P, logS, Q, op, fdc, binary=False)
    run(["ply_to_splat.py", ply2, out2])
    r2 = np.fromfile(out2, dtype=WEB_DTYPE)
    assert np.allclose(r2["p"], rec["p"], atol=1e-3) and np.abs(r2["c"].astype(int) - rec["c"].astype(int)).max() <= 1
    # --inspect hem bizim çıktıda hem web'in sentetik dosyasında aynı yapıyı görüyor
    a = json.loads(run(["ply_to_splat.py", "--inspect", out]).stdout)
    msg = f"{n} gauss, kovaryans medyan göreli hata {np.median(rel)*100:.2f}%"
    if os.path.isfile(WEB_SPLAT):
        b = json.loads(run(["ply_to_splat.py", "--inspect", WEB_SPLAT]).stdout)
        web = np.fromfile(WEB_SPLAT, dtype=WEB_DTYPE)
        assert set(a) == set(b) and a["finite"] and b["finite"]
        assert 0.95 < a["quatNormMinMax"][0] and a["quatNormMinMax"][1] < 1.05
        assert 0.95 < b["quatNormMinMax"][0] and b["quatNormMinMax"][1] < 1.05
        assert WEB_DTYPE.itemsize == 32 and os.path.getsize(WEB_SPLAT) % 32 == 0 and len(web) == b["count"]
        msg += f"; web ornek.splat ({b['count']} gauss) aynı 32 bayt yapı, kuaterniyon normları {b['quatNormMinMax']}"
    return msg


@test("ply_to_splat: hizalama (align_points JSON), --flip-yz, kırpma, budama, hatalı girdiler")
def t_ply_transform():
    rng = np.random.default_rng(9)
    n = 300
    P = rng.uniform(-5, 5, (n, 3)); logS = rng.uniform(-3, -1, (n, 3))
    Q = rng.normal(size=(n, 4)); op = rng.normal(1, 2, n); fdc = rng.normal(0, 1, (n, 3))
    ply = os.path.join(TMP, "t.ply"); write_3dgs_ply(ply, P, logS, Q, op, fdc)
    th = math.radians(33); s = 2.5; t = np.array([3.0, -1.0, 4.0])
    Ry = np.array([[math.cos(th), 0, math.sin(th)], [0, 1, 0], [-math.sin(th), 0, math.cos(th)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(0.3), -math.sin(0.3)], [0, math.sin(0.3), math.cos(0.3)]])
    R = Ry @ Rx
    aj = os.path.join(TMP, "al.json")
    json.dump({"scale": s, "rotationMatrix": R.tolist(), "position": t.tolist()}, open(aj, "w"))
    out = os.path.join(TMP, "t.splat")
    run(["ply_to_splat.py", ply, out, "--align-json", aj])
    rec = np.fromfile(out, dtype=WEB_DTYPE)
    imp = np.exp(logS.sum(1)) / (1 + np.exp(-op)); order = np.argsort(-imp, kind="stable")
    assert np.allclose(rec["p"], (s * (P @ R.T) + t)[order], atol=1e-3)
    Rq = np.stack([qmat(q) for q in Q[order]]); St = np.exp(logS[order])
    M0 = Rq * St[:, None, :]; cov0 = M0 @ np.transpose(M0, (0, 2, 1))
    cov_exp = s * s * (R @ cov0 @ R.T)
    rel = np.linalg.norm(js_cov(rec) - cov_exp, axis=(1, 2)) / np.linalg.norm(cov_exp, axis=(1, 2))
    assert np.median(rel) < 0.02, np.median(rel)
    # --flip-yz: y,z işaret değiştirir
    run(["ply_to_splat.py", ply, out, "--flip-yz"])
    f = np.fromfile(out, dtype=WEB_DTYPE)
    assert np.allclose(f["p"], (P * [1, -1, -1])[order], atol=1e-4)
    # kırpma + opaklık + sayı sınırı
    run(["ply_to_splat.py", ply, out, "--crop=-5,-5,-5,0,5,5", "--min-alpha", "128", "--max-splats", "50"])
    c = np.fromfile(out, dtype=WEB_DTYPE)
    assert 0 < len(c) <= 50 and (c["p"][:, 0] <= 0).all() and (c["c"][:, 3] >= 127).all()
    # hatalı girdiler
    bad = os.path.join(TMP, "bad.ply")
    open(bad, "wb").write(b"ply\nformat binary_little_endian 1.0\nelement chunk 1\nproperty float min_x\nend_header\n")
    assert "compressed" in run(["ply_to_splat.py", bad, out], expect_ok=False).stderr
    open(bad, "wb").write(b"ply\nformat binary_little_endian 1.0\nelement vertex 1\nproperty float x\nend_header\n" + bytes(4))
    assert "eksik" in run(["ply_to_splat.py", bad, out], expect_ok=False).stderr
    return f"hizalama konum ±1 mm, kovaryans medyan hata {np.median(rel)*100:.2f}%; flip/kırpma/budama OK; sıkıştırılmış PLY ve eksik alan reddedildi"


@test("splat_to_b64: web demosunun .b64.txt biçimiyle birebir (tek satır), gidiş-dönüş")
def t_b64():
    src = os.path.join(TMP, "s.splat")
    if not os.path.isfile(src):
        raise AssertionError("önce ply_to_splat testi çalışmalı")
    run(["splat_to_b64.py", src])
    b = open(src + ".b64.txt", "rb").read()
    import base64
    assert b"\n" not in b and base64.b64decode(b) == open(src, "rb").read()
    back = os.path.join(TMP, "geri.splat")
    run(["splat_to_b64.py", "--decode", src + ".b64.txt", "-o", back])
    assert open(back, "rb").read() == open(src, "rb").read()
    msg = "tek satır, gidiş-dönüş birebir"
    web_b64 = WEB_SPLAT + ".b64.txt"
    if os.path.isfile(web_b64):
        out = os.path.join(TMP, "web.b64.txt")
        run(["splat_to_b64.py", WEB_SPLAT, "-o", out])
        assert open(out, "rb").read() == open(web_b64, "rb").read()
        msg += "; web/data/ornek.splat → üretilen .b64.txt, web'deki dosyayla BAYT BAYT aynı"
    # 32'nin katı olmayan dosya reddedilir; --max-mb uyarısı çıkış 2
    odd = os.path.join(TMP, "odd.splat"); open(odd, "wb").write(bytes(33))
    run(["splat_to_b64.py", odd], expect_ok=False)
    pr = subprocess.run([PY, "splat_to_b64.py", src, "-o", os.path.join(TMP, "x.txt"), "--max-mb", "0.001"],
                        cwd=ROOT, capture_output=True, text=True)
    assert pr.returncode == 2
    return msg


@test("cloud/runpod_train.sh: bash -n, shellcheck (varsa), DRY_RUN akışı")
def t_cloud_script():
    sh = os.path.join(ROOT, "cloud", "runpod_train.sh")
    subprocess.run(["bash", "-n", sh], check=True)
    msg = "bash -n OK"
    if shutil.which("shellcheck"):
        p = subprocess.run(["shellcheck", "-S", "warning", sh], capture_output=True, text=True)
        assert p.returncode == 0, p.stdout
        msg += "; shellcheck (warning+) temiz"
    env = dict(os.environ, DRY_RUN="1", WORK=os.path.join(TMP, "pod"), OUT_DIR=os.path.join(TMP, "pod_out"),
               DATA_ARCHIVE="/yok/veri.tar", POSE_MODE="colmap", METHOD="splatfacto-big", MAX_ITERS="7000")
    p = subprocess.run(["bash", sh], env=env, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    for needle in ("colmap mapper", "ns-train splatfacto-big", "--max-num-iterations 7000", "ns-export gaussian-splat",
                   "_sonuc.tar.gz"):
        assert needle in p.stdout, needle
    env["POSE_MODE"] = "yanlis"
    assert subprocess.run(["bash", sh], env=env, capture_output=True, text=True).returncode != 0
    return msg + "; DRY_RUN tüm adımları sırayla yazdırdı; geçersiz POSE_MODE reddedildi"


if __name__ == "__main__":
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP)
    for name, fn in TESTS:
        try:
            msg = fn()
            results.append((name, True, msg or ""))
        except Exception as e:  # noqa
            results.append((name, False, str(e)))
    ok = all(r[1] for r in results)
    for name, good, msg in results:
        print(f"[{'GEÇTİ' if good else 'KALDI'}] {name}: {msg}")
    if "--keep" not in sys.argv:
        shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(0 if ok else 1)
