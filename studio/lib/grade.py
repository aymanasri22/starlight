#!/usr/bin/env python3
"""Colour pipeline: author looks as .cube LUTs, apply them, normalise HDR phone footage to Rec.709.

    grade.py look   --out look.cube [--size 33] [--contrast 1.15] [--warm 0.04] [--split 0.05]
                    [--sat 0.92] [--toe 0.03] [--shoulder 0.9]       author a film-style look LUT
    grade.py apply  IN OUT --lut look.cube [--grain 0.0] [--vignette 0.0] [--codec prores|h264]
    grade.py hdr2sdr IN OUT [--npl 100] [--tonemap mobius|hable|reinhard]  HLG/PQ -> Rec.709 SDR
                    (default mobius/npl 100: measured closest to SDR intent; hable/npl 203 rendered
                    at about half brightness in the pipeline test. Compare per scene on real footage.)
    grade.py still  IN.png OUT.png --lut look.cube                     apply a LUT to a still (ref frames)

LUTs are Rec.709-in / Rec.709-out display-referred, the standard .cube format DaVinci Resolve,
Premiere and Final Cut load directly (Resolve: Project Settings > Color Management > LUT folders).
For scene-referred (ACES / DaVinci Wide Gamut) grading the same looks belong in Resolve; this tool
is for previs, dailies, and pipelines that render here.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from common import BT709_TAGS, TAG709, ffmpeg  # noqa: E402

LUMA = np.array([0.2126, 0.7152, 0.0722])


def filmic(x, contrast, toe, shoulder):
    """Smooth S-curve around mid-grey with lifted toe and soft shoulder (display-referred)."""
    mid = 0.435
    y = mid + (x - mid) * contrast
    y = np.where(y < mid, mid - (mid - y) / (1 + np.maximum(mid - y, 0) * (contrast - 1) * 2), y)
    y = toe + (1 - toe) * y
    hi = y > shoulder
    y = np.where(hi, shoulder + (1 - shoulder) * np.tanh((y - shoulder) / (1 - shoulder)), y)
    return np.clip(y, 0, 1)


def make_look(size: int, contrast: float, warm: float, split: float, sat: float, toe: float, shoulder: float):
    r = np.linspace(0, 1, size)
    # .cube ordering: red changes fastest
    b, g, rr = np.meshgrid(r, r, r, indexing="ij")
    rgb = np.stack([rr, g, b], axis=-1)
    y = filmic(rgb, contrast, toe, shoulder)
    luma = (y @ LUMA)[..., None]
    y = luma + (y - luma) * sat                              # global saturation (gentle compression)
    hi_w, lo_w = np.clip((luma - 0.5) * 2, 0, 1), np.clip((0.5 - luma) * 2, 0, 1)
    y = y + hi_w * np.array([warm, warm * 0.35, -warm]) * split / 0.05   # warm highlights
    y = y + lo_w * np.array([-split * 0.6, split * 0.1, split]) * 0.8    # teal-leaning shadows
    # protect skin hue band (approx. orange, r>g>b) from the split-tone shift
    skin = np.clip(1 - np.abs(((rgb[..., 0] - rgb[..., 1]) - 0.12) / 0.12), 0, 1) * (rgb[..., 1] > rgb[..., 2])
    y = y * (1 - 0.5 * skin[..., None]) + filmic(rgb, contrast, toe, shoulder) * 0.5 * skin[..., None]
    return np.clip(y, 0, 1).reshape(-1, 3)


def write_cube(path: str, table: np.ndarray, size: int, title: str) -> None:
    with open(path, "w") as f:
        f.write(f'TITLE "{title}"\nLUT_3D_SIZE {size}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
        for v in table:
            f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")


def enc(codec: str):
    return (["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"] if codec == "prores"
            else ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p"])


def apply(src: str, dst: str, lut: str, grain: float, vignette: float, codec: str) -> None:
    chain = [f"lut3d=file='{lut}':interp=tetrahedral"]
    if vignette > 0:
        chain.append(f"vignette=angle={0.35 + vignette:.3f}:mode=forward")
    if grain > 0:  # temporal luma grain, strength in 0..1
        chain.append(f"noise=c0s={int(grain * 20)}:c0f=t+u")
    chain.append(TAG709)
    ffmpeg(["-i", src, "-vf", ",".join(chain), *enc(codec), *BT709_TAGS, "-c:a", "copy", dst])
    print(f"wrote {dst}")


def hdr2sdr(src: str, dst: str, npl: int, tonemap: str) -> None:
    vf = (f"zscale=t=linear:npl={npl},format=gbrpf32le,zscale=p=bt709,tonemap={tonemap}:desat=0,"
          "zscale=t=bt709:m=bt709:r=tv,format=yuv422p10le," + TAG709)
    ffmpeg(["-i", src, "-vf", vf, "-c:v", "prores_ks", "-profile:v", "3", *BT709_TAGS, "-c:a", "copy", dst])
    print(f"wrote {dst} (Rec.709 SDR, tonemap={tonemap}, npl={npl})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("look"); l.add_argument("--out", required=True); l.add_argument("--size", type=int, default=33)
    for k, v in dict(contrast=1.15, warm=0.04, split=0.05, sat=0.92, toe=0.03, shoulder=0.9).items():
        l.add_argument(f"--{k}", type=float, default=v)
    p = sub.add_parser("apply"); p.add_argument("src"); p.add_argument("dst"); p.add_argument("--lut", required=True)
    p.add_argument("--grain", type=float, default=0.0); p.add_argument("--vignette", type=float, default=0.0)
    p.add_argument("--codec", default="prores", choices=["prores", "h264"])
    h = sub.add_parser("hdr2sdr"); h.add_argument("src"); h.add_argument("dst"); h.add_argument("--npl", type=int, default=100)
    h.add_argument("--tonemap", default="mobius", choices=["mobius", "hable", "reinhard"])
    s = sub.add_parser("still"); s.add_argument("src"); s.add_argument("dst"); s.add_argument("--lut", required=True)
    a = ap.parse_args()
    if a.cmd == "look":
        write_cube(a.out, make_look(a.size, a.contrast, a.warm, a.split, a.sat, a.toe, a.shoulder), a.size,
                   Path(a.out).stem)
        print(f"wrote {a.out}")
    elif a.cmd == "apply":
        apply(a.src, a.dst, a.lut, a.grain, a.vignette, a.codec)
    elif a.cmd == "hdr2sdr":
        hdr2sdr(a.src, a.dst, a.npl, a.tonemap)
    else:
        ffmpeg(["-i", a.src, "-vf", f"lut3d=file='{a.lut}':interp=tetrahedral", a.dst])
        print(f"wrote {a.dst}")
