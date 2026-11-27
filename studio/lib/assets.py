#!/usr/bin/env python3
"""CC0 / open asset fetching + equirect plate extraction.

    assets.py hdri-list [--category urban] [--limit 20]          browse Poly Haven HDRIs (CC0)
    assets.py hdri ID --res 4k --out-dir 06_CGI_3D/hdri            download .hdr (+ md5 check)
    assets.py plate HDR --out plate.png --yaw 0 --pitch 0 --fov 70 --size 1280x720 [--ev 0]
                                                                   perspective backplate from an HDRI,
                                                                   aligned with Blender's world mapping
    assets.py osm-buildings --bbox S,W,N,E --out buildings.json    OpenStreetMap footprints (ODbL:
                                                                   credit "(c) OpenStreetMap contributors")

Poly Haven assets are CC0 (no attribution required, credit appreciated). Every download is logged
to 13_Project_Documentation/asset_licences.json so the end credits and licence record stay complete.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import cv2
import numpy as np
import requests

sys.path.insert(0, str(Path(__file__).parent))
from common import FILM, write_json  # noqa: E402

UA = {"User-Agent": "studio-pipeline/1.0 (asset fetch)"}  # generic client name, no personal data
PH = "https://api.polyhaven.com"


def log_licence(entry: dict) -> None:
    p = FILM / "13_Project_Documentation" / "asset_licences.json"
    data = json.loads(p.read_text()) if p.exists() else []
    try:  # store paths relative to the film root so the record is portable
        entry["file"] = str(Path(entry["file"]).resolve().relative_to(FILM.resolve()))
    except ValueError:
        pass
    if not any(d.get("file") == entry["file"] for d in data):
        data.append({**entry, "fetched": str(date.today())})
        write_json(p, data)


def hdri_list(category: str | None, limit: int) -> None:
    r = requests.get(f"{PH}/assets", params={"t": "hdris", **({"c": category} if category else {})}, headers=UA, timeout=30)
    r.raise_for_status()
    items = sorted(r.json().items(), key=lambda kv: -kv[1].get("download_count", 0))[:limit]
    for k, v in items:
        print(f"{k:32s} {','.join(v.get('categories', []))[:60]}")


def hdri(asset: str, res: str, out_dir: Path) -> Path:
    r = requests.get(f"{PH}/files/{asset}", headers=UA, timeout=30)
    r.raise_for_status()
    f = r.json()["hdri"][res]["hdr"]
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / f"{asset}_{res}.hdr"
    if not dst.exists():
        data = requests.get(f["url"], headers=UA, timeout=300).content
        if hashlib.md5(data).hexdigest() != f["md5"]:
            raise SystemExit("md5 mismatch on download")
        dst.write_bytes(data)
    log_licence({"file": str(dst), "source": f"https://polyhaven.com/a/{asset}", "licence": "CC0-1.0",
                 "author": "Poly Haven", "kind": "hdri"})
    print(f"wrote {dst}")
    return dst


def tonemap(hdr: np.ndarray, ev: float) -> np.ndarray:
    x = hdr * (2.0 ** ev)
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14  # ACES-fitted filmic curve (Narkowicz)
    y = np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)
    return (np.power(y, 1 / 2.2) * 255).astype(np.uint8)


def plate(hdr_path: str, out: str, yaw: float, pitch: float, fov: float, size: str, ev: float) -> None:
    """Rectilinear view. yaw: degrees CCW from +X (Blender world), pitch: degrees up."""
    eq = cv2.imread(hdr_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH)
    if eq is None:
        raise SystemExit(f"cannot read {hdr_path}")
    H, W = eq.shape[:2]
    w, h = map(int, size.lower().split("x"))
    az, el = np.radians(yaw), np.radians(pitch)
    fwd = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    right = np.array([np.sin(az), -np.cos(az), 0.0])
    up = np.cross(right, fwd)
    f = (w / 2) / np.tan(np.radians(fov) / 2)
    xs, ys = np.meshgrid(np.arange(w) + 0.5 - w / 2, h / 2 - (np.arange(h) + 0.5))
    d = f * fwd[None, None] + xs[..., None] * right + ys[..., None] * up
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    azp = np.arctan2(d[..., 1], d[..., 0])
    elp = np.arcsin(np.clip(d[..., 2], -1, 1))
    # Cycles: +X at image centre, azimuth decreasing to the right. -0.5: remap samples pixel centres.
    mx = ((0.5 - azp / (2 * np.pi)) % 1.0) * W - 0.5
    my = (0.5 - elp / np.pi) * H - 0.5
    view = cv2.remap(eq.astype(np.float32), mx.astype(np.float32), my.astype(np.float32),
                     cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)
    cv2.imwrite(out, tonemap(np.maximum(view, 0), ev))
    print(f"wrote {out} ({w}x{h}, yaw {yaw}, pitch {pitch}, hfov {fov})")


def osm_buildings(bbox: str, out: str) -> None:
    q = f"[out:json][timeout:60];(way[building]({bbox}););out geom tags;"
    # Public Overpass instances (wiki.openstreetmap.org/wiki/Overpass_API#Public_Overpass_API_instances).
    # overpass-api.de drops connections through this environment's egress proxy, so fall back in order.
    endpoints = ["https://overpass-api.de/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
                 "https://overpass.private.coffee/api/interpreter"]
    last = None
    for ep in endpoints:
        try:
            r = requests.post(ep, data={"data": q}, headers=UA, timeout=120)
            r.raise_for_status()
            els = r.json().get("elements", [])
            print(f"overpass: {ep}")
            break
        except Exception as e:  # try the next public instance
            last = e
    else:
        raise SystemExit(f"all Overpass endpoints failed: {last}")
    feats = []
    for e in els:
        tags = e.get("tags", {})
        h = tags.get("height") or tags.get("building:height")
        lv = tags.get("building:levels")
        try:
            height = float(str(h).split()[0]) if h else (float(lv) * 3.2 if lv else None)
        except ValueError:
            height = None
        feats.append({"id": e["id"], "name": tags.get("name"), "height": height,
                      "coords": [[p["lat"], p["lon"]] for p in e.get("geometry", [])]})
    write_json(out, {"bbox": bbox, "licence": "ODbL-1.0", "credit": "(c) OpenStreetMap contributors", "buildings": feats})
    log_licence({"file": out, "source": "https://www.openstreetmap.org", "licence": "ODbL-1.0",
                 "author": "OpenStreetMap contributors", "kind": "map data", "credit_required": True})
    print(f"wrote {out}: {len(feats)} buildings, {sum(1 for f in feats if f['height'])} with heights")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("hdri-list"); l.add_argument("--category"); l.add_argument("--limit", type=int, default=20)
    h = sub.add_parser("hdri"); h.add_argument("id"); h.add_argument("--res", default="4k")
    h.add_argument("--out-dir", default=str(FILM / "06_CGI_3D" / "hdri"))
    p = sub.add_parser("plate"); p.add_argument("hdr"); p.add_argument("--out", required=True)
    for k, v in dict(yaw=0.0, pitch=0.0, fov=70.0, ev=0.0).items():
        p.add_argument(f"--{k}", type=float, default=v)
    p.add_argument("--size", default="1280x720")
    o = sub.add_parser("osm-buildings"); o.add_argument("--bbox", required=True); o.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "hdri-list":
        hdri_list(a.category, a.limit)
    elif a.cmd == "hdri":
        hdri(a.id, a.res, Path(a.out_dir))
    elif a.cmd == "plate":
        plate(a.hdr, a.out, a.yaw, a.pitch, a.fov, a.size, a.ev)
    else:
        osm_buildings(a.bbox, a.out)
