"""Feasibility F6 (v4: SDF hero morph + river mist hand-off for the surroundings + rising river): Longhua Pagoda -> Zhujiajiao pavilion transformation (the signature shot), preview res.

Geometric morph, not a dissolve: matched points on both structures (eave tips, ridge, spire -> ridge)
drive a thin-plate-spline warp of BOTH images inside one camera move (descend + pull back). The blend is
luminance-keyed (bright sky changes first, dark rooflines last, so the roofs appear to persist and
reshape) and the water town's water rises from the bottom of frame. Target = real IMG_1039 frames at
5x slow motion (120 fps -> 24 fps).

    python f6_transform.py [--scale 0.5] [--frames 72]
Outputs (local): f6_strip.jpg, f6_transform.mp4
"""
import argparse
import subprocess
from pathlib import Path

import cv2
import numpy as np
from scipy.interpolate import RBFInterpolator

REPO = Path(__file__).resolve().parents[3]
F = Path(__file__).parent
ap = argparse.ArgumentParser()
ap.add_argument("--scale", type=float, default=0.5)
ap.add_argument("--frames", type=int, default=72)
ap.add_argument("--src-start", type=float, default=5.30, help="IMG_1039 time where the morph lands (s)")
a = ap.parse_args()
k = a.scale
OW, OH = int(1080 * k), int(1920 * k)

pag = cv2.imread(str(F / "longhua_clean.png")).astype(np.float32)          # 1512x2016 clean plate
cap = cv2.VideoCapture(str(REPO / "Shanghai_Film/02_Original_Videos/IMG_1039.mov"))
cap.set(cv2.CAP_PROP_POS_MSEC, a.src_start * 1000)
vid = []
for _ in range(a.frames):
    ok, fr = cap.read()
    if not ok:
        break
    vid.append(fr.astype(np.float32))
print("video frames", len(vid), vid[0].shape)

# ---- v2: separate structure from sky in both sources (solid silhouettes morph; skies cross separately)
import sys
sys.path.insert(0, str(REPO / "studio" / "lib"))
from common import guided_filter
d = cv2.imread(str(F / "d_0909.png"), cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
gA = cv2.cvtColor(pag.astype(np.uint8), cv2.COLOR_BGR2GRAY)
matA = np.clip(guided_filter(gA, np.clip((d - 0.30) / 0.10, 0, 1), radius=4, eps=2e-4), 0, 1)
hsvA = cv2.cvtColor(pag.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
cables = (hsvA[..., 2] < 150) & (np.mgrid[0:2016, 0:1512][0] < 720)
matA = np.maximum(matA, cables.astype(np.float32))

def sky_plate(img, skymask):
    """Sky-only plate: in-paint the structure at low res (only ever seen under the morphing silhouette)."""
    small = cv2.resize(img.astype(np.uint8), (img.shape[1] // 6, img.shape[0] // 6), interpolation=cv2.INTER_AREA)
    hole = cv2.resize((skymask < 0.5).astype(np.uint8), (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    filled = cv2.inpaint(small, cv2.dilate(hole, np.ones((5, 5), np.uint8)), 9, cv2.INPAINT_TELEA)
    big = cv2.resize(cv2.GaussianBlur(filled, (0, 0), 2), (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    sm = skymask[..., None]
    return img * sm + big * (1 - sm)

skyA = sky_plate(pag, 1 - matA)
rowsA = np.arange(2016, dtype=np.float32)[:, None]
structA = matA * (rowsA < 1440)
mats_B, skies_B = [], []
for fr in vid:
    hsv = cv2.cvtColor(fr.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    rows = np.arange(fr.shape[0], dtype=np.float32)[:, None]
    sky = ((hsv[..., 2] > 150) & (hsv[..., 1] < 70) & (rows < 870)).astype(np.float32)
    sky = cv2.morphologyEx(sky, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    sky = np.clip(guided_filter(cv2.cvtColor(fr.astype(np.uint8), cv2.COLOR_BGR2GRAY), sky, radius=4, eps=2e-4), 0, 1)
    mats_B.append((1 - sky) * (rows < 905))   # pavilion + banks above the waterline
    skies_B.append(sky_plate(fr, sky))

# correspondences: pagoda photo coords  <->  pavilion video coords (1080x1920 portrait)
PA = np.array([[585, 705], [1085, 690], [830, 600],      # tier 1: L tip, R tip, roof top
               [580, 905], [1095, 900],                  # tier 2 tips
               [570, 1115], [1115, 1105],                # tier 3 tips
               [550, 1360], [1150, 1340],                # tier 4 tips -> base corners
               [830, 190]], np.float32)                  # spire top -> sinks into the ridge
PB = np.array([[555, 590], [800, 585], [690, 550],
               [540, 675], [840, 700],
               [485, 780], [850, 820],
               [470, 905], [880, 905],
               [700, 515]], np.float32)

def ease(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)

def cam(s, c):
    """photo/video coords -> output coords (full-res units) for scale s centred on point c."""
    return lambda p: (p - c) * s + np.array([540, 960], np.float32)

def warp_layer(img, src_pts, out_pts, s, c, border=cv2.BORDER_REPLICATE):
    """Warp img so src_pts land on out_pts; elsewhere follow the camera (s, c). Output at preview res."""
    inv = lambda q: (q - np.array([540, 960], np.float32)) / s + c
    ring = np.array([[x, y] for x in (-900, 540, 1980) for y in (-1500, 960, 3400) if not (x == 540 and y == 960)], np.float32)
    P = np.vstack([out_pts, ring])
    Q = np.vstack([src_pts, inv(ring)])
    rbf = RBFInterpolator(P, Q, kernel="thin_plate_spline", smoothing=1.0)
    gs = 12
    gy, gx = np.mgrid[0:OH:gs, 0:OW:gs].astype(np.float32)
    grid = np.stack([gx.ravel() / k, gy.ravel() / k], -1)
    m = rbf(grid).reshape(gy.shape + (2,)).astype(np.float32)
    mx = cv2.resize(m[..., 0], (OW, OH), interpolation=cv2.INTER_CUBIC)
    my = cv2.resize(m[..., 1], (OW, OH), interpolation=cv2.INTER_CUBIC)
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=border, borderValue=0)

n = len(vid)
out = []
for i in range(n):
    t = i / (n - 1)
    # camera: pagoda layer descends + pulls back; pavilion layer pulls back to near-native scale
    sA, cA = 0.95 - 0.25 * ease(t), np.array([830, 880 + 120 * ease(t)], np.float32)
    sB, cB = 1.42 - 0.27 * ease(t), np.array([690, 690 + 160 * ease(t)], np.float32)
    m = ease((t - 0.12) / 0.70)                                   # geometric morph progress
    pa_out = cam(sA, cA)(PA)
    pb_out = cam(sB, cB)(PB)
    p_out = (1 - m) * pa_out + m * pb_out
    A = warp_layer(pag, PA, p_out, sA, cA, cv2.BORDER_CONSTANT)
    mA = warp_layer(structA, PA, p_out, sA, cA, cv2.BORDER_CONSTANT)
    gA_ = warp_layer(matA, PA, p_out, sA, cA, cv2.BORDER_CONSTANT)        # pagoda + trees/people
    sAk = warp_layer(skyA, PA, p_out, sA, cA)
    B = warp_layer(vid[i], PB, p_out, sB, cB)
    mB = warp_layer(mats_B[i], PB, p_out, sB, cB)
    sBk = warp_layer(skies_B[i], PB, p_out, sB, cB)
    ws = ease((t - 0.05) / 0.55)
    sky = sAk * (1 - ws) + sBk * ws
    # ONE crisp silhouette: interpolate signed distance fields, never opacities
    def sdf(mask):
        mk = (mask > 0.5).astype(np.uint8)
        return cv2.distanceTransform(mk, cv2.DIST_L2, 5) - cv2.distanceTransform(1 - mk, cv2.DIST_L2, 5)
    sd = sdf(mA) * (1 - m) + sdf(mB) * m
    sil = np.clip((sd + 1.2) / 2.4, 0, 1)
    lum = cv2.GaussianBlur(cv2.cvtColor(A.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255, (0, 0), 2)
    w = ease(np.clip(m * 1.7 - (1 - lum) * 0.7, 0, 1))
    hasA, hasB = (mA > 0.3), (mB > 0.3)
    w = np.where(hasA & ~hasB, np.minimum(w, 1 - m * 0.0), w)
    w = np.where(~hasA & hasB, 1.0, w)
    w = np.where(~hasA & ~hasB, m, w)[..., None]
    struct = A * (1 - w) + B * w
    # surroundings: Longhua's sky/trees exchange with Zhujiajiao's banks behind a brief river mist
    envA = np.where((gA_ > 0.02)[..., None], A, sAk)
    e = ease((t - 0.30) / 0.40)
    env = envA * (1 - e) + B * e
    haze = 0.62 * np.exp(-((t - 0.50) / 0.17) ** 2)
    haze_col = np.array([222, 230, 236], np.float32)            # warm river-mist white (BGR)
    env = env * (1 - haze) + haze_col * haze
    hero = struct * (1 - haze * 0.30) + haze_col * haze * 0.30  # roofline stays readable through the mist
    frame = env * (1 - sil[..., None]) + hero * sil[..., None]
    bank_y = cam(sB, cB)(np.array([[540, 905]], np.float32))[0, 1] * k
    level = OH + 40 - (OH + 40 - bank_y) * ease((t - 0.10) / 0.62)
    yy = np.arange(OH, dtype=np.float32)[:, None]
    under = np.clip((yy - level) / 3.0, 0, 1)
    edge = np.exp(-((yy - level) / 2.5) ** 2) * 0.10            # thin bright meniscus at the rising surface
    frame = frame * (1 - under[..., None]) + B * under[..., None]
    frame = frame + edge[..., None] * 255 * (under[..., None] < 1)
    out.append(np.clip(frame, 0, 255).astype(np.uint8))

keys = [0, n // 4, n // 2, 3 * n // 4, n - 1]
strip = np.hstack([out[j] for j in keys])
for idx, j in enumerate(keys):
    cv2.putText(strip, f"{j / 24:.2f}s", (8 + idx * OW, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
cv2.imwrite(str(F / "f6_strip_v4.jpg"), strip, [cv2.IMWRITE_JPEG_QUALITY, 85])
p = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                      "-s", f"{OW}x{OH}", "-r", "24", "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                      str(F / "f6_transform_v4.mp4")], stdin=subprocess.PIPE)
for fr in out:
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
print("wrote f6_strip.jpg, f6_transform.mp4")
