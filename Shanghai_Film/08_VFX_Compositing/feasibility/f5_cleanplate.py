"""Feasibility F5: Longhua clean plate (towers + cranes removed) and 'unbuilding' layer masks.

Outputs (local, git-ignored): longhua_clean.png, longhua_remove_mask.png, longhua_unbuild_tXX.jpg
"""
import sys
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "studio" / "lib"))
from common import guided_filter  # noqa: E402

F = Path(__file__).parent
im = cv2.imread(str(REPO / "Shanghai_Film/01_Original_Photos/IMG_0909.jpg"))
d = cv2.imread(str(F / "d_0909.png"), cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
H, W = d.shape
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.float32)
b, g, r = [im[..., i].astype(np.float32) for i in range(3)]

# sky: blue, bright, far
sky = (hsv[..., 0] > 95) & (hsv[..., 0] < 120) & (hsv[..., 1] > 60) & (hsv[..., 2] > 150) & (d < 0.05)
sky = cv2.morphologyEx(sky.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)).astype(bool)

# keep: pagoda, trees, people (near). Soft edge refined against the photo.
near = np.clip((d - 0.30) / 0.10, 0, 1)
near = np.clip(guided_filter(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), near, radius=6, eps=2e-4), 0, 1)
# remove = not sky and not near (towers, cranes, distant buildings)
remove = np.clip((1 - near) * (1 - sky.astype(np.float32)), 0, 1)
# the modern block right of the pagoda sits at tree-like depth: remove its non-green pixels by region
hue, sat, val = hsv[..., 0], hsv[..., 1], hsv[..., 2]
green = (hue > 25) & (hue < 95) & (sat > 50)
yy0, xx0 = np.mgrid[0:H, 0:W]
right_block = (xx0 >= 1215) & (yy0 >= 1050) & (yy0 <= 1820) & ~green & ~sky
remove = np.maximum(remove, cv2.GaussianBlur(right_block.astype(np.float32), (0, 0), 1.5))
remove = cv2.dilate(remove, np.ones((5, 5), np.uint8))
remove = cv2.GaussianBlur(remove, (0, 0), 1.2)
remove = np.minimum(remove, 1 - near)
# protect the pagoda's own guy-wires (thin dark cables spire -> top roof): never remove non-sky pixels there
spire_zone = (xx0 >= 560) & (xx0 <= 1100) & (yy0 >= 170) & (yy0 <= 720)
cables = spire_zone & (val < 150)
cables = cv2.dilate(cables.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
remove[cables] = 0.0

# sky model: 2D quadratic per channel fitted on clean sky pixels
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
xn, yn = xx / W, yy / H
A = np.stack([np.ones_like(xn), xn, yn, xn * xn, xn * yn, yn * yn], -1)
idx = np.where(sky.ravel())[0]
idx = idx[:: max(1, len(idx) // 60000)]
model = np.zeros_like(im, dtype=np.float32)
for c in range(3):
    coef, *_ = np.linalg.lstsq(A.reshape(-1, 6)[idx], im[..., c].ravel()[idx].astype(np.float32), rcond=None)
    model[..., c] = (A @ coef)
# match the photo's sky grain (measured from real sky residual)
resid = (im.astype(np.float32) - model)[sky]
grain_sd = float(np.median(np.abs(resid - np.median(resid, 0)), 0).mean() * 1.4826)
rng = np.random.default_rng(1)
grain = cv2.GaussianBlur(rng.normal(0, grain_sd, (H, W)).astype(np.float32), (0, 0), 0.7)[..., None]
sky_fill = model + grain
clean = im.astype(np.float32) * (1 - remove[..., None]) + sky_fill * remove[..., None]
# faint thin remnants (crane jibs, cables of the cranes) in the sky outside the pagoda zone: detect with a
# black top-hat on the clean plate's sky and replace by the sky model
gclean = cv2.cvtColor(np.clip(clean, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
thin = cv2.morphologyEx(gclean, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 6
thin &= (near < 0.2) & ~spire_zone & (yy0 < 1450)
thin = cv2.dilate(thin.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32)
thin = cv2.GaussianBlur(thin, (0, 0), 1.0)[..., None]
clean = clean * (1 - thin) + sky_fill * thin
remove = np.maximum(remove, thin[..., 0])
print(f"thin remnants cleaned: {(thin[..., 0] > 0.5).sum()} px")
cv2.imwrite(str(F / "longhua_clean.png"), np.clip(clean, 0, 255).astype(np.uint8))
cv2.imwrite(str(F / "longhua_remove_mask.png"), (remove * 255).astype(np.uint8))
print(f"sky px {sky.sum()}, removed area {remove.mean():.1%}, sky grain sd {grain_sd:.2f}")

# unbuilding preview: floors vanish top-down; the cut line descends in floor-sized steps (~34 px)
cols = remove > 0.5
top_of = np.full(W, H, int)
ys = np.argmax(cols, axis=0)
has = cols.any(axis=0)
top_of[has] = ys[has]
floor = 34
bottom_of = np.where(has, H - np.argmax(cols[::-1], axis=0), 0)
def unbuild(t):
    # t=0 full towers, t=1 gone; per column the cut line descends from the top to the bottom of the removed
    # region, so the last frame of SH050 IS the clean plate SH060 continues on (no pop at 0:18.00)
    line = top_of + (bottom_of + floor - top_of) * (np.floor(t * 40) / 40)
    line = np.floor(line / floor) * floor
    keep_tower = cv2.GaussianBlur((yy >= line[None, :]).astype(np.float32), (0, 0), 0.8)   # soften the cut line only
    m = remove * (1 - keep_tower)           # removed so far; the removal mask itself is never re-blurred
    return im.astype(np.float32) * (1 - m[..., None]) + sky_fill * m[..., None]
frames = [unbuild(t) for t in (0.0, 0.35, 0.7, 1.0)]
h = 720
row = np.hstack([cv2.resize(np.clip(f, 0, 255).astype(np.uint8), (int(W * h / H), h)) for f in frames])
for i, t in enumerate(("t=0", "t=0.35", "t=0.7", "t=1 (clean)")):
    cv2.putText(row, t, (10 + i * int(W * h / H), 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
cv2.imwrite(str(F / "longhua_unbuild_strip.jpg"), row, [cv2.IMWRITE_JPEG_QUALITY, 85])

# continuity check: SH050's last frame must equal the clean plate SH060 continues on
end_frame = unbuild(1.0)
diff = np.abs(end_frame - clean)
print(f"unbuild(1.0) vs clean plate: mean abs diff {diff.mean():.3f}, max {diff.max():.1f}, "
      f"pixels > 4 levels: {(diff.max(axis=2) > 4).sum()}")

# production rule: ONE source of truth. The clean plate that SH060/SH070 use is the unbuild's own last frame.
cv2.imwrite(str(F / "longhua_clean.png"), np.clip(end_frame, 0, 255).astype(np.uint8))
chk = cv2.imread(str(F / "longhua_clean.png")).astype(np.float32)
print("clean plate rewritten from unbuild(1.0); re-check max diff:",
      float(np.abs(chk - np.clip(end_frame, 0, 255).astype(np.uint8)).max()))
