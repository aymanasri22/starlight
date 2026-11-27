#!/usr/bin/env python3
"""Still photo -> monocular depth -> 2.5D virtual camera move (CPU).

    depth_parallax.py depth  PHOTO --out depth.png                      16-bit depth map (white = near)
    depth_parallax.py move   PHOTO --out shot.mov [--depth depth.png]
                             [--move push|truck|crane|orbit] [--strength 0.04] [--seconds 5] [--fps 24]
                             [--size 1920x1080] [--codec prores|h264]

Depth: Depth Anything V2 Small (Apache-2.0, ONNX). Relative depth only: the move is a *plate* effect,
so keep strengths modest (0.02-0.06) or edges stretch. Large moves need a proper layered matte +
background fill (08_VFX_Compositing) or an AI image-to-video pass.

The warp is a backward map with fixed-point iteration on a dilated, edge-aware-smoothed depth, so
near objects keep their silhouette and the background stretches behind them rather than tearing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

sys.path.insert(0, str(Path(__file__).parent))
from common import BT709_TAGS, FFMPEG, MODELS, TAG709, guided_filter  # noqa: E402

MODEL = MODELS / "depth_anything_v2_small.onnx"


def estimate_depth(img_bgr: np.ndarray, size: int = 518) -> np.ndarray:
    """Relative inverse depth in [0,1], 1 = nearest, at the input resolution."""
    h, w = img_bgr.shape[:2]
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    s = size / max(h, w)
    nh, nw = max(14, int(round(h * s / 14)) * 14), max(14, int(round(w * s / 14)) * 14)
    x = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_CUBIC)
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
    d = sess.run(None, {sess.get_inputs()[0].name: x})[0].squeeze()
    d = cv2.resize(d.astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    lo, hi = np.percentile(d, 1), np.percentile(d, 99.5)
    return np.clip((d - lo) / (hi - lo + 1e-6), 0, 1)


def prep_depth(depth: np.ndarray, guide: np.ndarray) -> np.ndarray:
    """Edge-aware smooth, then dilate near regions so silhouettes stay intact."""
    g = cv2.cvtColor(guide, cv2.COLOR_BGR2GRAY)
    d = guided_filter(g, depth.astype(np.float32), radius=8, eps=1e-3)
    k = max(3, int(min(depth.shape) * 0.006) | 1)
    return cv2.dilate(d, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))


def camera(move: str, t: float, strength: float):
    """Return (tx, ty, zoom) at normalised time t in [0,1] with an S-curve ease."""
    e = t * t * (3 - 2 * t)
    a = (e - 0.5) * 2  # -1 .. 1
    if move == "push":
        return 0.0, 0.0, strength * e * 2.5
    if move == "truck":
        return strength * a, 0.0, strength * 0.6
    if move == "crane":
        return 0.0, -strength * a * 0.8, strength * 0.6 + strength * 0.5 * e
    if move == "orbit":
        return strength * np.sin(np.pi * a / 2), -0.25 * strength * np.cos(np.pi * a / 2), strength * 0.8
    raise ValueError(move)


def warp(img: np.ndarray, depth: np.ndarray, tx: float, ty: float, zoom: float, focus: float = 0.0):
    h, w = depth.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w / 2, h / 2
    rel = depth - focus  # parallax relative to the focus plane (0 = far plane stays put)
    sx, sy = xx.copy(), yy.copy()
    for _ in range(3):  # fixed-point: sample depth where the source pixel is
        d = cv2.remap(rel, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        z = 1.0 + zoom * (0.35 + d)
        sx = (xx - cx) / z + cx - tx * w * d
        sy = (yy - cy) / z + cy - ty * h * d
    return cv2.remap(img, sx, sy, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT_101)


def cover(img: np.ndarray, size: tuple[int, int], margin: float) -> np.ndarray:
    """Scale to cover the output frame with an overscan margin for the move."""
    W, H = size
    s = max(W / img.shape[1], H / img.shape[0]) * (1 + margin)
    r = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_LANCZOS4 if s > 1 else cv2.INTER_AREA)
    y0, x0 = (r.shape[0] - int(H * (1 + margin))) // 2, (r.shape[1] - int(W * (1 + margin))) // 2
    return r[y0:y0 + int(H * (1 + margin)), x0:x0 + int(W * (1 + margin))]


def render_move(photo: str, out: str, depth_path: str | None, move: str, strength: float, seconds: float,
                fps: int, size: tuple[int, int], codec: str) -> None:
    import subprocess
    img = cv2.imread(photo, cv2.IMREAD_COLOR)
    if img is None:
        sys.exit(f"cannot read {photo}")
    depth = (cv2.imread(depth_path, cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535.0
             if depth_path else estimate_depth(img))
    margin = 0.12
    W, H = size
    plate = cover(img, size, margin)
    dmap = prep_depth(cover(depth, size, margin), plate)
    ph, pw = plate.shape[:2]
    y0, x0 = (ph - H) // 2, (pw - W) // 2
    enc = (["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"] if codec == "prores"
           else ["-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p"])
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
           "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-vf", TAG709, *enc, *BT709_TAGS, out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round(seconds * fps))
    for i in range(n):
        tx, ty, z = camera(move, i / max(1, n - 1), strength)
        f = warp(plate, dmap, tx, ty, z)
        p.stdin.write(np.ascontiguousarray(f[y0:y0 + H, x0:x0 + W]).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        sys.exit("ffmpeg encode failed")
    print(f"wrote {out}: {n} frames, move={move}, strength={strength}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["depth", "move"])
    ap.add_argument("photo")
    ap.add_argument("--out", required=True)
    ap.add_argument("--depth")
    ap.add_argument("--move", default="push", choices=["push", "truck", "crane", "orbit"])
    ap.add_argument("--strength", type=float, default=0.04)
    ap.add_argument("--seconds", type=float, default=5.0)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--codec", default="prores", choices=["prores", "h264"])
    a = ap.parse_args()
    if a.cmd == "depth":
        d = estimate_depth(cv2.imread(a.photo))
        cv2.imwrite(a.out, (d * 65535).astype(np.uint16))
        print(f"wrote {a.out}")
    else:
        W, H = map(int, a.size.lower().split("x"))
        render_move(a.photo, a.out, a.depth, a.move, a.strength, a.seconds, a.fps, (W, H), a.codec)
