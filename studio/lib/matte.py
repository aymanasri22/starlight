#!/usr/bin/env python3
"""Person / subject mattes for stills (rembg, ONNX, CPU).

    matte.py IMAGE --out cutout.png [--model birefnet-portrait|u2net_human_seg|isnet-general-use]
                   [--alpha alpha.png] [--refine]

Outputs an RGBA cutout (straight alpha) and optionally the alpha alone. --refine runs an
edge-aware guided filter on the alpha for hair/fine edges. Models download on first use into
$U2NET_HOME (default /opt/studio/models/rembg). For video rotoscoping on this CPU-only machine use
the cloud (SAM 2 class models) or matte key frames here and track them in the composite.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("U2NET_HOME", "/opt/studio/models/rembg")

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from rembg import new_session, remove  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from common import guided_filter  # noqa: E402


def matte(src: str, out: str, model: str, alpha_out: str | None, refine: bool) -> float:
    t0 = time.time()
    img = Image.open(src).convert("RGB")
    a = np.array(remove(img, session=new_session(model), only_mask=True)).astype(np.float32) / 255.0
    rgb = np.array(img)
    if refine:
        guide = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        a = np.clip(guided_filter(guide, a, radius=4, eps=1e-4), 0, 1)
    rgba = np.dstack([rgb, (a * 255).astype(np.uint8)])
    Image.fromarray(rgba, "RGBA").save(out)
    if alpha_out:
        Image.fromarray((a * 255).astype(np.uint8)).save(alpha_out)
    dt = time.time() - t0
    print(f"wrote {out} ({model}, {dt:.1f}s, coverage {a.mean():.1%})")
    return dt


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image"); ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="birefnet-portrait"); ap.add_argument("--alpha"); ap.add_argument("--refine", action="store_true")
    a = ap.parse_args()
    matte(a.image, a.out, a.model, a.alpha, a.refine)
    sys.exit(0)
