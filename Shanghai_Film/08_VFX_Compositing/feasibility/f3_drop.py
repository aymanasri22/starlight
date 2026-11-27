"""Feasibility F3: opening 'reverse drop' on the real canal water (previs frames).

Ripples are analytic damped ring waves (radius shrinking = time running backwards) displacing the real
water of 20261127_160211; the rising drop is previs-only here (production: Cycles droplet render with
refraction of this same plate, 1080x1920, ~72 frames).
"""
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[3]
F = Path(__file__).parent
canal = cv2.imread(str(REPO / "Shanghai_Film/01_Original_Photos/20261127_160211.jpg")).astype(np.float32)
H, W = canal.shape[:2]
# the opening frame is a tight, top-down feel on the darkest water: lower-centre crop, 9:16
cw = int(W * 0.62); ch = int(cw * 16 / 9)
x0 = int(W * 0.22); y0 = H - ch
plate = canal[y0:y0 + ch, x0:x0 + cw].copy()
h, w = plate.shape[:2]
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
cx, cy = w * 0.5, h * 0.56
r = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.9) ** 2)       # ellipse: water seen at an angle


def frame(t):
    """t: 0 = wide rings (start of film), 1 = rings converged, drop leaving the surface."""
    R = (1 - t) * 0.55 * w + 6                               # ring front radius shrinking (reverse time)
    k = 2 * np.pi / (w * 0.035)
    env = np.exp(-((r - R) / (w * 0.12)) ** 2) * (0.35 + 0.65 * (1 - t))
    wave = np.sin(k * (r - R)) * env
    gx = cv2.Sobel(wave, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(wave, cv2.CV_32F, 0, 1, ksize=3)
    out = cv2.remap(plate, xx + gx * 22, yy + gy * 22, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    spec = np.clip(gx * -0.6 + gy * -0.9, 0, None)[..., None] * 160    # sky light catching ring crests
    out = out + spec
    if t > 0.8:                                               # previs drop: lifts off the converged centre
        lift = (t - 0.8) / 0.2
        dy = cy - lift * h * 0.18
        cv2.ellipse(out, (int(cx), int(dy)), (int(w * 0.016), int(w * 0.022)), 0, 0, 360, (225, 228, 230), -1, cv2.LINE_AA)
    return np.clip(out, 0, 255).astype(np.uint8)


strip = np.hstack([cv2.resize(frame(t), (360, 640), interpolation=cv2.INTER_AREA) for t in (0.0, 0.45, 0.8, 0.95)])
cv2.imwrite(str(F / "f3_drop_strip.jpg"), strip, [cv2.IMWRITE_JPEG_QUALITY, 88])
cv2.imwrite(str(F / "f3_drop_key.png"), frame(0.45))
print("wrote f3_drop_strip.jpg")
