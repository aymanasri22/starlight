"""Feasibility F6 v5: Longhua Pagoda -> Zhujiajiao pavilion, "water is the medium of time" (director's note D1).

The river rises; its reflection changes FIRST (the reflected pagoda becomes the pavilion, top tier first,
hidden by real ripples), then the solid building follows as one crisp SDF silhouette with real texture inside.
Guy-wires fade before the spire sinks. Mist is a thin band hugging the waterline (<= 0.25), never full-frame.
The pavilion's surroundings emerge out of that band. The camera lands with full frame coverage.

    python f6_transform_v5.py [--scale 0.5] [--frames 72]
Outputs (local): f6_strip_v5.jpg, f6_transform_v5.mp4
"""
import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy.interpolate import RBFInterpolator

REPO = Path(__file__).resolve().parents[3]
F = Path(__file__).parent
sys.path.insert(0, str(REPO / "studio" / "lib"))
from common import guided_filter  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--scale", type=float, default=0.5)
ap.add_argument("--frames", type=int, default=72)
ap.add_argument("--src-start", type=float, default=5.30)
a = ap.parse_args()
k = a.scale
OW, OH = int(1080 * k), int(1920 * k)

def ease(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)

# ---------------- sources
pag = cv2.imread(str(F / "longhua_clean.png")).astype(np.float32)
d = cv2.imread(str(F / "d_0909.png"), cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
gA = cv2.cvtColor(pag.astype(np.uint8), cv2.COLOR_BGR2GRAY)
matA = np.clip(guided_filter(gA, np.clip((d - 0.30) / 0.10, 0, 1), radius=4, eps=2e-4), 0, 1)
yyA, xxA = np.mgrid[0:2016, 0:1512]
spire_zone = (xxA >= 560) & (xxA <= 1100) & (yyA >= 170) & (yyA <= 720)
cables = (cv2.morphologyEx(gA, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))) > 9) & spire_zone
cables &= (yyA < 640)                                        # above the top roof only
cables &= ~((xxA > 790) & (xxA < 870))                      # never the spire body itself
cables = cv2.dilate(cables.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
matA = np.maximum(matA, cables)
structA = matA * (yyA < 1440)                                # hero = pagoda; trees/people below = ground
groundA = np.clip(matA - structA, 0, 1)

def sky_plate(img, skymask):
    small = cv2.resize(img.astype(np.uint8), (img.shape[1] // 6, img.shape[0] // 6), interpolation=cv2.INTER_AREA)
    hole = cv2.resize((skymask < 0.5).astype(np.uint8), (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    filled = cv2.inpaint(small, cv2.dilate(hole, np.ones((5, 5), np.uint8)), 9, cv2.INPAINT_TELEA)
    big = cv2.resize(cv2.GaussianBlur(filled, (0, 0), 2), (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    sm = skymask[..., None]
    return img * sm + big * (1 - sm)

skyA = sky_plate(pag, 1 - matA)
cap = cv2.VideoCapture(str(REPO / "Shanghai_Film/02_Original_Videos/IMG_1039.mov"))
cap.set(cv2.CAP_PROP_POS_MSEC, a.src_start * 1000)
vid = []
for _ in range(a.frames):
    ok, fr = cap.read()
    if not ok:
        break
    vid.append(fr.astype(np.float32))
BANK = 905                                                   # waterline row of the pavilion bank (video coords)
hero_poly = np.zeros((1920, 1080), np.uint8)
cv2.fillPoly(hero_poly, [np.array([[565, 470], [900, 470], [900, BANK], [565, BANK]], np.int32)], 1)
heroB, surB, skyB = [], [], []
rows = np.arange(1920, dtype=np.float32)[:, None]
for fr in vid:
    hsv = cv2.cvtColor(fr.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    sky = ((hsv[..., 2] > 150) & (hsv[..., 1] < 70) & (rows < 870)).astype(np.float32)
    sky = cv2.morphologyEx(sky, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    sky = np.clip(guided_filter(cv2.cvtColor(fr.astype(np.uint8), cv2.COLOR_BGR2GRAY), sky, radius=4, eps=2e-4), 0, 1)
    struct = (1 - sky) * (rows < BANK)
    heroB.append(struct * hero_poly)
    surB.append(struct * (1 - hero_poly))
    skyB.append(sky_plate(fr, sky))

# ---------------- correspondences (pagoda photo coords <-> pavilion video coords)
PA = np.array([[585, 705], [1085, 690], [830, 600], [580, 905], [1095, 900], [570, 1115], [1115, 1105],
               [550, 1360], [1150, 1340], [830, 190]], np.float32)
PB = np.array([[555, 590], [800, 585], [690, 550], [540, 675], [840, 700], [485, 780], [850, 820],
               [470, 905], [880, 905], [700, 515]], np.float32)
C0 = np.array([540, 960], np.float32)

def cam(s, c):
    return lambda p: (p - c) * s + C0

def warp(img, src, dst, s, c, border=cv2.BORDER_REPLICATE):
    inv = lambda q: (q - C0) / s + c
    ring = np.array([[x, y] for x in (-900, 540, 1980) for y in (-1500, 960, 3400) if not (x == 540 and y == 960)], np.float32)
    rbf = RBFInterpolator(np.vstack([dst, ring]), np.vstack([src, inv(ring)]), kernel="thin_plate_spline", smoothing=1.0)
    gy, gx = np.mgrid[0:OH:12, 0:OW:12].astype(np.float32)
    m = rbf(np.stack([gx.ravel() / k, gy.ravel() / k], -1)).reshape(gy.shape + (2,)).astype(np.float32)
    mx = cv2.resize(m[..., 0], (OW, OH), interpolation=cv2.INTER_CUBIC)
    my = cv2.resize(m[..., 1], (OW, OH), interpolation=cv2.INTER_CUBIC)
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=border, borderValue=0)

def sdf(mask):
    mk = (mask > 0.5).astype(np.uint8)
    return cv2.distanceTransform(mk, cv2.DIST_L2, 5) - cv2.distanceTransform(1 - mk, cv2.DIST_L2, 5)

def above(i, t, m, sA, cA, sB, cB, cable_fade, sur_alpha):
    """Composite of everything above the waterline for morph progress m."""
    pa_out, pb_out = cam(sA, cA)(PA), cam(sB, cB)(PB)
    p = (1 - m) * pa_out + m * pb_out
    A = warp(pag, PA, p, sA, cA, cv2.BORDER_CONSTANT)
    hA = warp(structA * (1 - cables * cable_fade), PA, p, sA, cA, cv2.BORDER_CONSTANT)
    grA = warp(groundA, PA, p, sA, cA, cv2.BORDER_CONSTANT)
    sA_ = warp(skyA, PA, p, sA, cA)
    B = warp(vid[i], PB, p, sB, cB)
    hB = warp(heroB[i], PB, p, sB, cB, cv2.BORDER_CONSTANT)
    suB = warp(surB[i], PB, p, sB, cB, cv2.BORDER_CONSTANT)
    sB_ = warp(skyB[i], PB, p, sB, cB)
    ws = ease((t - 0.05) / 0.55)
    out = sA_ * (1 - ws) + sB_ * ws                                      # skies cross
    out = out * (1 - grA[..., None]) + A * grA[..., None]                # Longhua ground (until the river takes it)
    sa = (suB * sur_alpha)[..., None]
    out = out * (1 - sa) + B * sa                                        # Zhujiajiao banks emerge
    sil = np.clip((sdf(hA) * (1 - m) + sdf(hB) * m + 1.2) / 2.4, 0, 1)   # one crisp hero silhouette
    lum = cv2.GaussianBlur(cv2.cvtColor(np.clip(A, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255, (0, 0), 2)
    w = ease(np.clip(m * 1.7 - (1 - lum) * 0.7, 0, 1))
    hasA, hasB = hA > 0.3, hB > 0.3
    w = np.where(hasA & ~hasB, np.minimum(w, 0.0), w)                    # pagoda-only pixels stay pagoda texture
    w = np.where(~hasA & hasB, 1.0, w)                                   # pavilion-only pixels are real pavilion texture
    w = np.where(~hasA & ~hasB, m, w)[..., None]
    hero = A * (1 - w) + B * w
    return out * (1 - sil[..., None]) + hero * sil[..., None], B

frames = []
n = len(vid)
for i in range(n):
    t = i / (n - 1)
    sA, cA = 0.95 - 0.25 * ease(t), np.array([830, 880 + 120 * ease(t)], np.float32)
    sB, cB = 1.42 - 0.27 * ease(t), np.array([690 - 130 * ease(t), 690 + 160 * ease(t)], np.float32)
    m = ease((t - 0.18) / 0.62)                       # the solid building
    m_lead = ease((t - 0.02) / 0.55)                  # the reflection changes first
    cable_fade = ease((t - 0.08) / 0.22)
    sur_alpha = ease((t - 0.42) / 0.33)
    top, B = above(i, t, m, sA, cA, sB, cB, cable_fade, sur_alpha)
    top_lead, _ = above(i, t, m_lead, sA, cA, sB, cB, cable_fade, sur_alpha)
    # waterline rises to the pavilion's bank, wavering (never a ruler-straight line)
    bank_y = cam(sB, cB)(np.array([[540, BANK]], np.float32))[0, 1] * k
    level0 = OH + 30 - (OH + 30 - bank_y) * ease((t - 0.06) / 0.58)
    xs = np.arange(OW, dtype=np.float32)
    level = level0 + (3 * np.sin(xs / (OW * 0.06) + t * 22) + 2 * np.sin(xs / (OW * 0.017) - t * 9)) * k * 2
    yy = np.arange(OH, dtype=np.float32)[:, None]
    under = np.clip((yy - level[None, :]) / 2.0, 0, 1)
    # reflection of the LEAD composite about the waterline, rippled by the real river texture
    gB = cv2.cvtColor(np.clip(B, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    hp = gB - cv2.GaussianBlur(gB, (0, 0), 6)
    dx = cv2.Sobel(hp, cv2.CV_32F, 1, 0, ksize=5) / 32
    depth = np.clip((yy - level[None, :]) / (OH * 0.4), 0, 1)
    amp = (2 + 10 * depth) * k * 2
    src_y = 2 * level[None, :] - yy + dx * amp * 0.5
    src_x = np.tile(xs[None, :], (OH, 1)) + dx * amp
    refl = cv2.remap(top_lead.astype(np.float32), src_x.astype(np.float32), src_y.astype(np.float32), cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_REPLICATE)
    R = (0.55 * np.exp(-depth / 0.45))[..., None]
    water = B * 0.82 * (1 - R) + refl * 0.78 * R
    meniscus = np.exp(-((yy - level[None, :] - 1.5) / 1.4) ** 2)[..., None] * 18
    frame = top * (1 - under[..., None]) + water * under[..., None] + meniscus
    # thin mist band hugging the waterline (<= 0.25), strongest mid-transformation
    mist = 0.25 * np.exp(-((yy - (level[None, :] - 50 * k * 2)) / (70 * k * 2)) ** 2) * np.exp(-((t - 0.48) / 0.22) ** 2)
    frame = frame * (1 - mist[..., None]) + np.array([222, 230, 236], np.float32) * mist[..., None]
    frames.append(np.clip(frame, 0, 255).astype(np.uint8))

keys = [0, 14, 26, 36, 46, 56, n - 1]
strip = np.hstack([cv2.resize(frames[j], (270, 480)) for j in keys])
for idx, j in enumerate(keys):
    cv2.putText(strip, f"{j / 24:.2f}s", (6 + idx * 270, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
cv2.imwrite(str(F / "f6_strip_v5.jpg"), strip, [cv2.IMWRITE_JPEG_QUALITY, 88])
p = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                      "-s", f"{OW}x{OH}", "-r", "24", "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                      str(F / "f6_transform_v5.mp4")], stdin=subprocess.PIPE)
for fr in frames:
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
print("wrote f6_strip_v5.jpg, f6_transform_v5.mp4")
