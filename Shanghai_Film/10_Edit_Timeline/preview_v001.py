"""Preview cut v001 (animatic) of SHANGHAI: BETWEEN TIME -- picture.

Follows PRODUCTION_PLAN_v002 shot by shot, from the client's real media and the feasibility tests. It is a PREVIEW
for the client's approval gate, NOT a final render: 2D drop instead of the Blender drop, two-layer parallax (no
lamp-post layer), no grade pass, SH070 = feasibility v5, cranes not separated in SH050.

    python preview_v001.py [--shots SH100,SH010,...]
Outputs (local, git-ignored): 10_Edit_Timeline/preview_v001/SHxxx.mp4 and picture.mp4
"""
import argparse
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FILM = Path(__file__).resolve().parents[1]
FEAS = FILM / "08_VFX_Compositing/feasibility"
PHOTOS = FILM / "01_Original_Photos"
VIDEO = FILM / "02_Original_Videos/IMG_1039.mov"
OUT = Path(__file__).parent / "preview_v001"
OUT.mkdir(parents=True, exist_ok=True)
FPS, OW, OH = 24, 1080, 1920
CTR = np.array([OW / 2, OH / 2], np.float32)
# measured: the real Pearl Tower lower sphere is centred at screen (358, 948) in SH020's first frame (window x0 0);
# SH100 ends with the REFLECTED lower sphere on the same point, so SH010 -> SH020 is a position-locked match cut
TARGET = np.array([358.0, 948.0], np.float32)
DROP_R = 22
SHOTS = {"SH010": 72, "SH020": 108, "SH030": 72, "SH040": 48, "SH050": 132, "SH060": 48, "SH070": 72, "SH080": 96,
         "SH090": 96, "SH100": 168}                       # frames at 24 fps; 912 = 38.00 s
rng = np.random.default_rng(11)
GRAIN = [cv2.GaussianBlur(rng.normal(0, 2.0, (OH, OW)).astype(np.float32), (0, 0), 0.6) for _ in range(24)]
XX, YY = np.meshgrid(np.arange(OW, dtype=np.float32), np.arange(OH, dtype=np.float32))


def ease(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def ease5(x):
    x = np.clip(x, 0, 1)
    return x ** 3 * (x * (6 * x - 15) + 10)


def imread(p):
    im = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
    if im is None:
        raise SystemExit(f"cannot read {p}")
    return im


def view(img, s, c, border=cv2.BORDER_REFLECT101):
    """Camera: source point c lands on the screen centre, scaled by s."""
    M = np.float32([[s, 0, CTR[0] - c[0] * s], [0, s, CTR[1] - c[1] * s]])
    return cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=border)


def make_label():
    im = Image.new("L", (OW, OH), 0)
    f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 22)
    ImageDraw.Draw(im).text((36, 1860), "PREVIEW v001  ·  not final", font=f, fill=255)
    return (np.asarray(im, np.float32) / 255 * 0.55)[..., None]


LABEL = make_label()


def finish(fr, i):
    out = fr.astype(np.float32) + GRAIN[i % len(GRAIN)][..., None]
    out = out * (1 - LABEL) + 235 * LABEL
    return np.clip(out, 0, 255).astype(np.uint8)


class Writer:
    def __init__(self, name):
        self.path = OUT / f"{name}.mp4"
        self.p = subprocess.Popen(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s",
             f"{OW}x{OH}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
             "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
             str(self.path)], stdin=subprocess.PIPE)
        self.n = 0

    def write(self, fr):
        self.p.stdin.write(finish(fr, self.n).tobytes())
        self.n += 1

    def close(self, expect):
        self.p.stdin.close()
        self.p.wait()
        assert self.n == expect, (self.path.name, self.n, expect)
        print(f"{self.path.name}: {self.n} frames ({self.n / FPS:.2f} s)", flush=True)


def fill_behind(img, alpha, dil):
    """Background layer for parallax: the area behind the client (plus a margin) in-painted at 1/4 res."""
    hole = cv2.dilate((alpha > 0.02).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * dil + 1,) * 2))
    h, w = hole.shape
    small = cv2.resize(np.clip(img, 0, 255).astype(np.uint8), (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    hs = cv2.resize(hole, (w // 4, h // 4), interpolation=cv2.INTER_NEAREST)
    filled = cv2.inpaint(small, hs, 9, cv2.INPAINT_TELEA)
    big = cv2.resize(cv2.GaussianBlur(filled, (0, 0), 1.5), (w, h), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    soft = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 3)[..., None]
    return img * (1 - soft) + big * soft


def wave_fields(start_ms, n):
    """Real wave field from the client's 120 fps canal clip: high-passed luminance of the water, one per frame."""
    cap = cv2.VideoCapture(str(VIDEO))
    cap.set(cv2.CAP_PROP_POS_MSEC, start_ms)
    out = []
    while len(out) < n:
        ok, fr = cap.read()
        if not ok:
            cap.set(cv2.CAP_PROP_POS_MSEC, start_ms)      # never happens for the ranges used; safety loop
            continue
        g = cv2.cvtColor(fr[1150:1900], cv2.COLOR_BGR2GRAY).astype(np.float32)
        out.append(cv2.GaussianBlur(g, (0, 0), 4) - cv2.GaussianBlur(g, (0, 0), 28))
    return out


def draw_drop(fr, x, y, r, vy, alpha=1.0, shutter=1 / 48):
    """2D refracting water drop (inverted, magnified view of the frame), rim shading, specular, motion blur."""
    streak = abs(vy) * shutter
    n = max(1, int(streak / 2.5) + 1)
    x0, x1 = int(x - r - 4), int(x + r + 5)
    y0, y1 = int(y - streak - r - 4), int(y + r + 5)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(OW, x1), min(OH, y1)
    if x1 <= x0 or y1 <= y0:
        return fr
    px, py = XX[y0:y1, x0:x1], YY[y0:y1, x0:x1]
    acc_c = np.zeros((y1 - y0, x1 - x0, 3), np.float32)
    acc_a = np.zeros((y1 - y0, x1 - x0), np.float32)
    for yk in np.linspace(y - streak, y, n):
        d = np.sqrt((px - x) ** 2 + (py - yk) ** 2)
        a = np.clip(r - d + 0.5, 0, 1)
        sx = x - (px - x) * 2.2
        sy = yk - (py - yk) * 2.2 - r * 1.5
        col = cv2.remap(fr, sx.astype(np.float32), sy.astype(np.float32), cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_REFLECT101).astype(np.float32)
        q = np.clip(d / r, 0, 1)
        col = col * (0.62 + 0.38 * (1 - q ** 4))[..., None] + 12
        spec = np.exp(-(((px - (x - 0.35 * r)) ** 2 + (py - (yk - 0.40 * r)) ** 2) / (2 * (0.16 * r) ** 2)))
        col = col + spec[..., None] * 210
        acc_c += col * a[..., None]
        acc_a += a
    acc_c /= n
    acc_a = (acc_a / n * alpha)[..., None]
    patch = fr[y0:y1, x0:x1].astype(np.float32)
    fr = fr.copy()
    fr[y0:y1, x0:x1] = patch * (1 - acc_a) + acc_c * alpha
    return fr


def rings(fr, cx, cy, tau, aspect=0.42):
    """2-4 irregular rings spreading on the water (seen at a grazing angle) displacing the composite."""
    R = 260
    x0, x1 = int(max(0, cx - R)), int(min(OW, cx + R))
    y0, y1 = int(max(0, cy - R * aspect)), int(min(OH, cy + R * aspect))
    px, py = XX[y0:y1, x0:x1], YY[y0:y1, x0:x1]
    dx, dy = px - cx, (py - cy) / aspect
    rho = np.sqrt(dx * dx + dy * dy) + 1e-3
    th = np.arctan2(dy, dx)
    disp = np.zeros_like(rho)
    for v, lam, a0, ph in ((150, 26, 10.0, 0.0), (112, 20, 7.0, 1.3), (80, 16, 5.0, 2.1), (55, 13, 3.0, 0.7)):
        rk = v * tau * (1 + 0.05 * np.sin(3 * th + ph) + 0.03 * np.sin(5 * th + 2 * ph))
        env = np.exp(-((rho - rk) / (lam * 1.2)) ** 2)
        disp += a0 * np.exp(-tau / 0.8) * np.sin(2 * np.pi * (rho - rk) / lam) * env
    fade = np.clip((R - rho) / 40, 0, 1)
    disp *= fade
    mx = px - disp * dx / rho
    my = py - disp * dy / rho * aspect
    out = fr.copy()
    patch = cv2.remap(fr, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR,
                      borderMode=cv2.BORDER_REFLECT101).astype(np.float32)
    out[y0:y1, x0:x1] = np.clip(patch * (1 + 0.012 * disp[..., None]), 0, 255)
    return out


def title_layer():
    """Title in warm white, wide tracking, inside the Reels/TikTok safe area (x 54-929, y < 1498)."""
    im = Image.new("L", (OW, OH), 0)
    d = ImageDraw.Draw(im)
    cx = (54 + 929) / 2
    for text, size, track, y in (("SHANGHAI: BETWEEN TIME", 34, 0.32, 1290), ("上海 · 时光之间", 56, 0.18, 1352)):
        f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", size)
        widths = [d.textlength(ch, font=f) for ch in text]
        total = sum(widths) + track * size * (len(text) - 1)
        x = cx - total / 2
        for ch, w in zip(text, widths):
            d.text((x, y), ch, font=f, fill=255)
            x += w + track * size
    return np.asarray(im, np.float32) / 255


# ------------------------------------------------------------------------------------------------------------- shots
def sh100():
    """Golden canal -> night Lujiazui reflection, camera along the inverted tower, title, the drop, rings."""
    canal = imread(PHOTOS / "20261127_160211.jpg").astype(np.float32)
    H, W = canal.shape[:2]
    night = imread(FEAS / "pearl_portrait.png").astype(np.float32)
    sky_part = night[520:1275, 150:950].copy()
    lum_n = cv2.cvtColor(sky_part.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    sky_part *= (0.22 + 0.78 * np.clip((lum_n - 0.10) / 0.28, 0, 1) ** 1.2)[..., None]
    gray = cv2.cvtColor(np.clip(sky_part, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
    sky_part = (gray + (sky_part - gray) * 0.65) * np.array([0.92, 1.0, 1.08], np.float32)
    s = W / 1126.0
    poly = (np.array([[430, 955], [600, 955], [700, 1060], [870, 1220], [1126, 1440], [1126, 2000], [0, 2000],
                      [0, 1450], [130, 1230], [300, 1070]], np.float32) * s).astype(np.int32)
    water = np.zeros((H, W), np.float32)
    cv2.fillPoly(water, [poly], 1.0)
    hsv = cv2.cvtColor(canal.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    water[(hsv[..., 0] > 25) & (hsv[..., 0] < 90) & (hsv[..., 1] > 70) & (hsv[..., 2] > 70)] = 0
    boat = (np.array([[640, 1060], [880, 1060], [880, 1225], [640, 1225]], np.float32) * s).astype(np.int32)
    box = np.zeros((H, W), np.uint8)
    cv2.fillPoly(box, [boat], 1)
    objects = (box > 0) & ((hsv[..., 2] > 62) | (hsv[..., 1] > 95))
    objects = cv2.morphologyEx(objects.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    objects = cv2.dilate(objects, np.ones((5, 5), np.uint8)).astype(np.float32)
    water = np.minimum(water, 1 - cv2.GaussianBlur(objects, (0, 0), 2.5))     # the boatman and the boat untouched
    water = cv2.GaussianBlur(water, (0, 0), 3)
    y_far = int(955 * s)
    sk = cv2.resize(sky_part, None, fx=1.45, fy=1.45, interpolation=cv2.INTER_AREA)
    mir = cv2.flip(sk, 0)
    refl = np.zeros_like(canal)
    refl[:] = (14, 8, 10)
    x0 = 700 - mir.shape[1] // 2
    h_use = min(mir.shape[0], H - y_far)
    xs0, xs1 = max(0, x0), min(W, x0 + mir.shape[1])
    refl[y_far:y_far + h_use, xs0:xs1] = mir[:h_use, xs0 - x0:xs1 - x0]
    refl[y_far + h_use:] = refl[y_far + h_use - 1:y_far + h_use].mean(axis=(0, 1))
    bright = np.clip((cv2.cvtColor(refl.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) - 120) / 135, 0, 1)
    refl = refl * 0.95 + cv2.GaussianBlur(refl * bright[..., None], (0, 0), sigmaX=1.0, sigmaY=9) * 0.45
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    persp = np.clip((yy - y_far) / (H - y_far), 0, 1)
    fres = 0.92 - 0.55 * persp ** 0.8
    g0 = cv2.cvtColor(canal.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    glints = np.clip((g0 - cv2.GaussianBlur(g0, (0, 0), 6) - 18) / 60, 0, 1)
    body = np.array([10, 12, 10], np.float32)
    own = cv2.GaussianBlur(g0, (0, 0), 2) - cv2.GaussianBlur(g0, (0, 0), 14)
    edge_keep = np.clip(1 - np.minimum(xx / (0.10 * W), (W - xx) / (0.10 * W)), 0, 1) * (persp > 0.15)
    amp = 1 + 16 * persp ** 1.8
    waves = wave_fields(1500, SHOTS["SH100"])
    title = title_layer()
    P = np.array([700, 1449], np.float32)                                     # reflected lower sphere centre (photo), measured on render
    S0 = OW / W
    sp0 = (P - np.array([W / 2, H / 2], np.float32)) * S0 + CTR
    t_hit, t_drop = 5.60, 5.05                                                 # 36.60 and 36.05 in film time
    tail = {}
    wr = Writer("SH100")
    for i in range(SHOTS["SH100"]):
        u = i / FPS
        hfull = np.zeros((H, W), np.float32)
        hfull[y_far:] = cv2.resize(waves[i], (W, H - y_far), interpolation=cv2.INTER_CUBIC)
        dx = cv2.Sobel(hfull, cv2.CV_32F, 1, 0, ksize=5) / 64
        dy = cv2.Sobel(hfull, cv2.CV_32F, 0, 1, ksize=5) / 64
        calm = float(1 - 0.7 * ease((u - 3.4) / 1.6))                             # the water stills before the drop
        rip = cv2.remap(refl, xx + (dx * amp + own / 255 * 10 * persp) * calm, yy + dy * amp * 1.8 * calm, cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_REFLECT)
        night_water = rip * fres[..., None] + body * (1 - fres[..., None])
        night_water *= (0.80 + 0.35 * np.clip(own / 40 + 0.5, 0, 1))[..., None]
        live = cv2.remap(canal, xx + dx * amp * 0.35, yy + dy * amp * 0.6, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        base = canal * (1 - water[..., None]) + live * water[..., None]          # the real canal moves from 31.00
        tr = np.clip((u - 0.6) / 2.4, 0, 1)
        reveal = np.clip(tr * 1.4 - persp * 0.35, 0, 1)
        reveal = (reveal * reveal * (3 - 2 * reveal))[..., None]
        mixw = water[..., None] * reveal * (1 - edge_keep[..., None] * 0.6)
        comp = base * (1 - mixw) + night_water * mixw
        comp += glints[..., None] * water[..., None] * 90 * (0.6 + 0.4 * np.sin(i * 0.9 + xx * 0.02))[..., None]
        e = ease5(u / 5.3)
        sc = S0 * 1.8 ** e
        c = P - (sp0 + (TARGET - sp0) * e - CTR) / sc
        fr = view(np.clip(comp, 0, 255), sc, c).astype(np.float32)
        # title 35.00-36.40, rippled inside the water
        ta = ease((u - 4.0) / 0.45) * (1 - ease((u - 5.0) / 0.4))
        if ta > 0:
            ox = 2.5 * np.sin(YY / 23 + u * 5) + 1.5 * np.sin(YY / 9 - u * 7)
            oy = 1.2 * np.sin(XX / 31 + u * 4)
            tl = cv2.remap(title, XX + ox, YY + oy, cv2.INTER_LINEAR)[..., None] * 0.85 * ta
            fr = fr * (1 - tl) + np.array([220, 236, 245], np.float32) * tl
        clean = fr.copy()
        if t_drop <= u < t_hit:                                                # the drop falls, accelerating
            tau = (u - t_drop) / (t_hit - t_drop)
            y = -50 + (TARGET[1] - 8 + 50) * tau * tau
            fr = draw_drop(fr, TARGET[0], y, DROP_R, 2 * (TARGET[1] + 42) * tau / (t_hit - t_drop), shutter=1 / 120)
        if u >= t_hit:                                                         # strike on the reflected sphere
            tau = u - t_hit
            fr = rings(fr, TARGET[0], TARGET[1], tau)
            clean = fr
            fl = np.exp(-tau / 0.05) * np.exp(-(((XX - TARGET[0]) ** 2) + ((YY - TARGET[1]) / 0.5) ** 2) / (2 * 9 ** 2))
            fr = fr + fl[..., None] * 120
        w = 0.95 * (1 - ease(u / 0.6))                                         # out of the near-white bloom
        fr = fr * (1 - w) + 255 * w
        if i >= 134:
            tail[i] = np.clip(clean, 0, 255)                                   # frame 134 kept without the drop
        wr.write(np.clip(fr, 0, 255).astype(np.uint8))
    wr.close(SHOTS["SH100"])
    np.savez_compressed(OUT / "sh100_tail.npz", **{str(k): v.astype(np.uint8) for k, v in tail.items()})


def sh010():
    """The ending reversed: rings converge on the reflected sphere; then a drop lifts out and holds (HELD)."""
    z = np.load(OUT / "sh100_tail.npz")
    tail = {int(k): z[k].astype(np.float32) for k in z.files}
    wr = Writer("SH010")
    for j in range(SHOTS["SH010"]):
        if j <= 33:
            fr = tail[167 - j]
        else:
            fr = tail[134]                                                     # calm water, time held
            tau = min(1.0, (j - 33) / FPS / 0.7)
            y = TARGET[1] - 8 - 40 * (1 - (1 - tau) ** 3)                      # rises, slows, holds 48 px above
            vy = 40 * 3 * (1 - tau) ** 2 / 0.7
            fr = draw_drop(fr, TARGET[0], y, DROP_R, vy, alpha=min(1.0, (j - 33) / 3))
        wr.write(np.clip(fr, 0, 255).astype(np.uint8))
    wr.close(SHOTS["SH010"])


def sh020():
    """The fixed point (HELD): sphere -> the client, truck right + push; client and background as two layers."""
    img = imread(FEAS / "IMG_1006_unmirrored.png").astype(np.float32)
    a = imread(FEAS / "m_1006.png")[..., 3].astype(np.float32) / 255
    bg = fill_behind(img, a, 45)
    S0 = OH / img.shape[0]
    c0 = np.array([OW / S0 / 2, img.shape[0] / 2], np.float32)                 # window x0 0 (left edge)
    wr = Writer("SH020")
    for i in range(SHOTS["SH020"]):
        e = ease5(i / FPS / 4.5)
        c = c0 + np.array([483 * e, 0], np.float32)
        s = S0 * (1 + 0.06 * e)
        cf, sf = c0 + (c - c0) * 1.07, s * (1 + 0.015 * e)                    # the client is nearer: moves more
        av = view(a, sf, cf, cv2.BORDER_CONSTANT)[..., None]
        fr = view(bg, s, c) * (1 - av) + view(img, sf, cf) * av
        wr.write(np.clip(fr, 0, 255).astype(np.uint8))
    wr.close(SHOTS["SH020"])


def sh030():
    """The retreating aircraft (REVERSE, aircraft only): cut out, sky filled, it travels tail-first."""
    img = imread(PHOTOS / "IMG_1009.jpg")
    ax, ay = 893, 94
    hole = np.zeros(img.shape[:2], np.uint8)
    hole[ay - 12:ay + 12, ax - 22:ax + 22] = 1
    clean = cv2.inpaint(img, hole, 7, cv2.INPAINT_TELEA).astype(np.float32)
    img = img.astype(np.float32)
    by0, by1, bx0, bx1 = ay - 14, ay + 14, ax - 24, ax + 24
    diff = np.abs(img[by0:by1, bx0:bx1] - clean[by0:by1, bx0:bx1]).sum(2)
    alpha = cv2.GaussianBlur(np.clip((diff - 8) / 40, 0, 1), (0, 0), 0.6)
    sprite = img[by0:by1, bx0:bx1]
    S0 = OH / img.shape[0]
    c0, c1 = np.array([567, 1008], np.float32), np.array([720, 810], np.float32)
    wr = Writer("SH030")
    for i in range(SHOTS["SH030"]):
        u = i / FPS
        plate = clean.copy()
        off = 150 * u / 3.0                                                   # constant speed, tail-first
        M = np.float32([[1, 0, bx0 + off], [0, 1, by0]])
        sw = cv2.warpAffine(sprite, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR)
        aw = cv2.warpAffine(alpha, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR)[..., None]
        plate = plate * (1 - aw) + sw * aw
        e = ease5(u / 3.0)
        fr = view(plate, S0 * (1 + 0.25 * e), c0 + (c1 - c0) * e)
        wr.write(np.clip(fr, 0, 255).astype(np.uint8))
    wr.close(SHOTS["SH030"])


def sh040():
    """The Bund holds its breath (HELD): tilt up + push to the clock tower. No film ageing."""
    img = imread(PHOTOS / "IMG_1750.jpg").astype(np.float32)
    S0 = OH / img.shape[0]
    c0, c1 = np.array([img.shape[1] / 2, img.shape[0] / 2], np.float32), np.array([770, 1195], np.float32)
    wr = Writer("SH040")
    for i in range(SHOTS["SH040"]):
        e = ease5(i / FPS / 2.0)
        wr.write(np.clip(view(img, S0 * (1 + 0.08 * e), c0 + (c1 - c0) * e), 0, 255).astype(np.uint8))
    wr.close(SHOTS["SH040"])


def thud_times():
    t, rate, out = 12.5, 2.0, []
    while t < 17.8:
        out.append(t - 12.5)
        rate = 2 + 8 * (t - 12.5) / 5.3
        t += 1 / rate
    return out


def sh050_060():
    """Unbuilding (REVERSE): floors vanish top-down, one per reversed thud (2 -> 10 /s); then the pagoda alone."""
    im = imread(PHOTOS / "IMG_0909.jpg").astype(np.float32)
    clean = imread(FEAS / "longhua_clean.png").astype(np.float32)
    remove = imread(FEAS / "longhua_remove_mask.png").astype(np.float32) / 255
    H, W = remove.shape
    cols = remove > 0.5
    has = cols.any(axis=0)
    top_of = np.where(has, np.argmax(cols, axis=0), H)
    bottom_of = np.where(has, H - np.argmax(cols[::-1], axis=0), 0)
    floor = 34
    yy = np.arange(H, dtype=np.float32)[:, None]
    thuds = thud_times()
    N = len(thuds)
    cache = {}

    def state(k):
        if k not in cache:
            line = top_of + (bottom_of + floor - top_of) * (k / N)
            line = np.floor(line / floor) * floor
            keep = cv2.GaussianBlur((yy >= line[None, :]).astype(np.float32), (0, 0), 0.8)
            cache[k] = im + (clean - im) * (1 - keep[..., None])
        return cache[k]

    S0 = OH / H
    c50 = np.array([830, 1008], np.float32)
    wr = Writer("SH050")
    for i in range(SHOTS["SH050"]):
        u = i / FPS
        k = sum(1 for t in thuds if t <= u + 1e-6)
        wr.write(np.clip(view(state(k), S0 * (1 + 0.05 * ease5(u / 5.5)), c50), 0, 255).astype(np.uint8))
    wr.close(SHOTS["SH050"])
    print(f"SH050: {N} floors on {N} thuds; last thud at {12.5 + thuds[-1]:.2f}s", flush=True)
    # SH060: continuous; from SH050's last framing to SH070's first (pagoda layer s 0.95, centre (830, 880))
    s0, s1 = S0 * 1.05, 0.95
    c1 = np.array([830, 880], np.float32)
    wr = Writer("SH060")
    for i in range(SHOTS["SH060"]):
        e = ease5(i / (SHOTS["SH060"] - 1))
        fr = view(clean, s0 + (s1 - s0) * e, c50 + (c1 - c50) * e, cv2.BORDER_REPLICATE)
        wr.write(np.clip(fr, 0, 255).astype(np.uint8))
    wr.close(SHOTS["SH060"])


def sh070():
    """Pagoda -> pavilion (signature): the full-resolution feasibility render v5, unchanged."""
    cap = cv2.VideoCapture(str(OUT.parent.parent / "08_VFX_Compositing/preview_v001/sh070_full.mp4"))
    wr = Writer("SH070")
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        wr.write(fr)
    wr.close(SHOTS["SH070"])


def sh080():
    """The crossing: the real footage at 5x slow (120 fps conform), pulling back to full frame."""
    cap = cv2.VideoCapture(str(VIDEO))
    cap.set(cv2.CAP_PROP_POS_MSEC, 5300)
    for _ in range(72):                                                        # SH070 used 5.300-5.892 s
        cap.read()
    c0, c1 = np.array([560, 850], np.float32), CTR
    wr = Writer("SH080")
    for i in range(SHOTS["SH080"]):
        ok, fr = cap.read()
        assert ok, i
        e = ease5(i / FPS / 2.2)
        wr.write(np.clip(view(fr.astype(np.float32), 1.15 + (1.0 - 1.15) * e, c0 + (c1 - c0) * e), 0, 255).astype(np.uint8))
    wr.close(SHOTS["SH080"])


def sh090():
    """The witness (HELD) while the canal behind flows (real wave field); sun bloom to near-white, image trace."""
    img = imread(PHOTOS / "IMG_1062.jpg")
    # the green lens-flare ghost on the jacket (not the face): small in-paint
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    yy0, xx0 = np.mgrid[0:img.shape[0], 0:img.shape[1]]
    near = (xx0 - 1106) ** 2 + (yy0 - 1887) ** 2 < 45 ** 2
    b, g, r = [img[..., k].astype(np.int32) for k in range(3)]
    ghost = near & (g > r + 25) & (g > b + 15) & (hsv[..., 2] > 70)
    ghost = cv2.dilate(ghost.astype(np.uint8), np.ones((7, 7), np.uint8))
    img = cv2.inpaint(img, ghost, 5, cv2.INPAINT_TELEA).astype(np.float32)
    print(f"SH090 flare ghost px: {int(ghost.sum())}", flush=True)
    a = imread(FEAS / "m_1062.png")[..., 3].astype(np.float32) / 255
    bg = fill_behind(img, a, 30)
    H, W = a.shape
    poly = np.array([[1240, 1262], [1350, 1300], [1588, 1440], [1932, 1610], [1932, 1840], [1560, 1870],
                     [1480, 2280], [1240, 2280]], np.int32)
    wm = np.zeros((H, W), np.float32)
    cv2.fillPoly(wm, [poly], 1.0)
    wm *= (cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2HSV)[..., 2] > 85)
    wm = cv2.GaussianBlur(wm, (0, 0), 4)
    y0, y1, x0, x1 = 1240, 2300, 1220, W
    sub_bg = bg[y0:y1, x0:x1]
    syy, sxx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    persp = np.clip((syy - 1262) / (2280 - 1262), 0, 1)
    amp = 2 + 10 * persp ** 1.5
    waves = wave_fields(3000, SHOTS["SH090"])
    S0 = OH / H
    c = np.array([1208, 1288], np.float32)
    sun = np.array([845, 684], np.float32)
    frozen = None
    wr = Writer("SH090")
    for i in range(SHOTS["SH090"]):
        u = i / FPS
        if u >= 3.20 and frozen is not None:                                   # time stops in the white
            wr.write(frozen)
            continue
        h = cv2.resize(waves[i], (x1 - x0, y1 - y0), interpolation=cv2.INTER_CUBIC)
        dx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=5) / 64
        dy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=5) / 64
        moved = cv2.remap(sub_bg, sxx + dx * amp - x0, syy + dy * amp * 1.5 - y0, cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT101)
        bgi = bg.copy()
        m = wm[y0:y1, x0:x1][..., None]
        bgi[y0:y1, x0:x1] = sub_bg * (1 - m) + moved * m
        e = ease5(u / 4.0)
        s = S0 * (1 + 0.04 * e)
        sf = s * (1 + 0.012 * e)
        av = view(a, sf, c, cv2.BORDER_CONSTANT)[..., None]
        fr = view(bgi, s, c) * (1 - av) + view(img, sf, c) * av
        g_ = ease((u - 2.80) / 0.40)                                           # 29.80-30.20 bloom
        if g_ > 0:
            sp = (sun - c) * s + CTR
            rad = 60 + 900 * g_
            glow = np.exp(-((XX - sp[0]) ** 2 + (YY - sp[1]) ** 2) / (2 * rad ** 2))[..., None]
            fr = fr + glow * 255 * g_
            w = 0.95 * g_
            fr = fr * (1 - w) + 255 * w
        out = np.clip(fr, 0, 255).astype(np.uint8)
        if u + 1 / FPS >= 3.20:
            frozen = out
        wr.write(out)
    wr.close(SHOTS["SH090"])


RENDER = {"SH100": sh100, "SH010": sh010, "SH020": sh020, "SH030": sh030, "SH040": sh040, "SH050": sh050_060,
          "SH070": sh070, "SH080": sh080, "SH090": sh090}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default=",".join(RENDER))
    a = ap.parse_args()
    for name in a.shots.split(","):
        RENDER[name]()
    order = list(SHOTS)
    if all((OUT / f"{n}.mp4").exists() for n in order):
        (OUT / "concat.txt").write_text("".join(f"file '{n}.mp4'\n" for n in order))
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i",
                        str(OUT / "concat.txt"), "-c", "copy", str(OUT / "picture.mp4")], check=True)
        print("wrote", OUT / "picture.mp4")
