"""Feasibility F7 v3 (inverted Pearl Tower runs into the near water; graded; final framing): Lujiazui at night reflected in the Zhujiajiao canal (the closing image), preview res.

Plate: client photo 20261127_160211 (real canal, golden afternoon) -- unchanged above the waterline.
Reflection: CC0 Poly Haven 'shanghai_bund' HDRI (a real night photograph of Lujiazui), mirrored.
Water motion: REAL wave field measured from the client's 120 fps IMG_1039 (high-passed luminance ->
height -> gradient displacement), scaled with perspective (larger near camera).
Physics cues: Fresnel (reflection stronger toward the far end), vertical light pillars, dark water body,
the canal's own sun glints kept on top, bank-side tree reflections kept near the edges.

    python f7_reflection.py [--scale 0.5] [--frames 48]
Outputs (local): f7_still.jpg, f7_reflection.mp4
"""
import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "studio" / "lib"))
F = Path(__file__).parent
ap = argparse.ArgumentParser()
ap.add_argument("--scale", type=float, default=0.5)
ap.add_argument("--frames", type=int, default=48)
a = ap.parse_args()

canal = cv2.imread(str(REPO / "Shanghai_Film/01_Original_Photos/20261127_160211.jpg")).astype(np.float32)
H, W = canal.shape[:2]                                   # 2576 x 1450 (already ~9:16)
night = cv2.imread(str(F / "pearl_portrait.png")).astype(np.float32)
sky_part = night[520:1275, 150:950].copy()               # antenna tip -> river line, Pearl Tower centred
lum_n = cv2.cvtColor(sky_part.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
sky_part *= (0.22 + 0.78 * np.clip((lum_n - 0.10) / 0.28, 0, 1) ** 1.2)[..., None]   # crush only true sky; keep the lights
gray = cv2.cvtColor(np.clip(sky_part, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
sky_part = gray + (sky_part - gray) * 0.65                                                # desaturate 35 %
sky_part *= np.array([0.92, 1.0, 1.08], np.float32)                                        # warm toward the film

# --- water mask (photo coords): polygon of the canal surface, minus overhanging leaves
s = W / 1126.0
poly = (np.array([[430, 955], [600, 955], [700, 1060], [870, 1220], [1126, 1440], [1126, 2000],
                  [0, 2000], [0, 1450], [130, 1230], [300, 1070]], np.float32) * s).astype(np.int32)
water = np.zeros((H, W), np.float32)
cv2.fillPoly(water, [poly], 1.0)
hsv = cv2.cvtColor(canal.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
leaves = (hsv[..., 0] > 25) & (hsv[..., 0] < 90) & (hsv[..., 1] > 70) & (hsv[..., 2] > 70)
water[leaves] = 0
boat = (np.array([[640, 1060], [880, 1060], [880, 1225], [640, 1225]], np.float32) * s).astype(np.int32)
# protect only the boat and the boatman themselves (not a box): inside the box, keep pixels that are not dark water
box = np.zeros((H, W), np.uint8); cv2.fillPoly(box, [boat], 1)
v_ = hsv[..., 2]; sat_ = hsv[..., 1]
objects = (box > 0) & ((v_ > 62) | (sat_ > 95))
objects = cv2.morphologyEx(objects.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
objects = cv2.dilate(objects, np.ones((5, 5), np.uint8)).astype(np.float32)
water = np.minimum(water, 1 - cv2.GaussianBlur(objects, (0, 0), 2.5))   # the real boatman and the boat stay untouched
water = cv2.GaussianBlur(water, (0, 0), 3)
y_far = int(955 * s)                                     # waterline at the far end of the canal

# --- mirrored skyline, placed with its base on the far waterline
sc = 1.45 * s / 1.288 * 1.288 if False else 1.45
sk = cv2.resize(sky_part, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
mir = cv2.flip(sk, 0)
refl = np.zeros_like(canal)
refl[:] = (14, 8, 10)                                   # deep night sky colour beyond the plate (BGR)
x0 = 700 - mir.shape[1] // 2                              # tower axis on the canal's centreline
h_use = min(mir.shape[0], H - y_far)
xs0, xs1 = max(0, x0), min(W, x0 + mir.shape[1])
refl[y_far:y_far + h_use, xs0:xs1] = mir[:h_use, xs0 - x0:xs1 - x0]
refl[y_far + h_use:] = refl[y_far + h_use - 1:y_far + h_use].mean(axis=(0, 1))
# light pillars: bright lights smear vertically on moving water
bright = np.clip((cv2.cvtColor(refl.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) - 120) / 135, 0, 1)
pillars = cv2.GaussianBlur(refl * bright[..., None], (0, 0), sigmaX=1.0, sigmaY=9)
refl = refl * 0.95 + pillars * 0.45                      # light pillars halved: spheres stay round

# --- real wave field from IMG_1039 (lower water region), one frame per output frame
cap = cv2.VideoCapture(str(REPO / "Shanghai_Film/02_Original_Videos/IMG_1039.mov"))
cap.set(cv2.CAP_PROP_POS_MSEC, 1500)
waves = []
for _ in range(a.frames):
    ok, fr = cap.read()
    if not ok:
        break
    g = cv2.cvtColor(fr[1150:1900], cv2.COLOR_BGR2GRAY).astype(np.float32)
    hgt = cv2.GaussianBlur(g, (0, 0), 4) - cv2.GaussianBlur(g, (0, 0), 28)
    waves.append(hgt)
print("wave frames", len(waves))

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
persp = np.clip((yy - y_far) / (H - y_far), 0, 1)
fres = 0.92 - 0.55 * persp ** 0.8                        # grazing (far) reflects more than near
glints = np.clip((cv2.cvtColor(canal.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
                  - cv2.GaussianBlur(cv2.cvtColor(canal.astype(np.uint8), cv2.COLOR_BGR2GRAY), (0, 0), 6).astype(np.float32) - 18) / 60, 0, 1)
body = np.array([10, 12, 10], np.float32)
g0 = cv2.cvtColor(canal.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
own = cv2.GaussianBlur(g0, (0, 0), 2) - cv2.GaussianBlur(g0, (0, 0), 14)     # the photo's own wave pattern                # dark canal water body (BGR)
edge_keep = np.clip(1 - np.minimum(xx / (0.10 * W), (W - xx) / (0.10 * W)), 0, 1) * (persp > 0.15)

OW, OH = int(1080 * a.scale), int(1920 * a.scale)
frames = []
for i, hgt in enumerate(waves):
    t = i / max(1, len(waves) - 1)
    hg = cv2.resize(hgt, (W, H - y_far), interpolation=cv2.INTER_CUBIC)
    hfull = np.zeros((H, W), np.float32); hfull[y_far:] = hg
    dx = cv2.Sobel(hfull, cv2.CV_32F, 1, 0, ksize=5) / 64
    dy = cv2.Sobel(hfull, cv2.CV_32F, 0, 1, ksize=5) / 64
    amp = 1 + 16 * persp ** 1.8                            # calmer: the spheres must stay legible
    rmap_x = xx + dx * amp + own / 255 * 10 * persp
    rmap_y = yy + dy * amp * 1.8
    rip = cv2.remap(refl, rmap_x, rmap_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    night_water = rip * fres[..., None] + body * (1 - fres[..., None])
    night_water *= (0.80 + 0.35 * np.clip(own / 40 + 0.5, 0, 1))[..., None]   # keep the real wave shading
    # the impossible arrives: real afternoon reflection -> night city, the real glints stay on top
    reveal = np.clip((t * 1.4) - persp * 0.35, 0, 1)                  # far end turns first
    reveal = (reveal * reveal * (3 - 2 * reveal))[..., None]
    keep_real = edge_keep[..., None] * 0.6
    mixw = water[..., None] * reveal * (1 - keep_real)
    out = canal * (1 - mixw) + night_water * mixw
    out = out + glints[..., None] * water[..., None] * 90 * (0.6 + 0.4 * np.sin(i * 0.9 + xx * 0.02))[..., None]
    crop = out[(H - int(W * 16 / 9)) // 2:][:int(W * 16 / 9)] if H > W * 16 / 9 else out
    frames.append(cv2.resize(np.clip(crop, 0, 255).astype(np.uint8), (OW, OH), interpolation=cv2.INTER_AREA))
cv2.imwrite(str(F / "f7_still_v3.jpg"), np.hstack([cv2.resize(canal.astype(np.uint8), (OW, OH)), frames[-1]]),
            [cv2.IMWRITE_JPEG_QUALITY, 88])
p = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                      "-s", f"{OW}x{OH}", "-r", "24", "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                      str(F / "f7_reflection_v3.mp4")], stdin=subprocess.PIPE)
for fr in frames:
    p.stdin.write(fr.tobytes())
p.stdin.close(); p.wait()
# final framing (camera end of SH100): scale 1.35 x 0.745 about (855, 1452); reflected lower sphere -> screen (384, 974)
k_end = 0.745 * 1.35
M = np.float32([[k_end, 0, 540 - 855 * k_end], [0, k_end, 960 - 1452 * k_end]])
end = cv2.warpAffine(np.clip(out, 0, 255).astype(np.uint8), M, (1080, 1920), flags=cv2.INTER_LANCZOS4)
cv2.circle(end, (384, 974), 26, (90, 220, 255), 2, cv2.LINE_AA)
cv2.imwrite(str(F / "f7_v3_endframe.jpg"), cv2.resize(end, (540, 960)), [cv2.IMWRITE_JPEG_QUALITY, 88])
lower_sphere_y = y_far + int((1275 - 1112) * sc)
print("reflected lower sphere at photo", (700, lower_sphere_y), "| wrote f7_still_v3.jpg, f7_reflection_v3.mp4, f7_v3_endframe.jpg")
