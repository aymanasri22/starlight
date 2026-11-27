"""Shared helpers for the studio toolchain (run with /opt/studio/venv/bin/python)."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FILM = Path(os.environ.get("STUDIO_FILM", REPO / "Shanghai_Film"))
MODELS = Path(os.environ.get("STUDIO_MODELS", "/opt/studio/models"))
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"
BLENDER = shutil.which("blender") or "/opt/studio/blender/blender"

# Delivery colour tags for SDR Rec.709 masters.
BT709_TAGS = ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv"]
# FFmpeg 7+ takes colour metadata from the frames, so the output flags above are ignored for untagged
# sources. Append this filter to every SDR output chain so files are tagged bt709/bt709/bt709 for real.
TAG709 = "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"


def run(cmd: list[str], quiet: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command from an argument list (never through a shell)."""
    cmd = [str(c) for c in cmd]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.stderr.write(f"\n$ {' '.join(cmd)}\n{p.stderr[-4000:]}\n")
        raise RuntimeError(f"command failed ({p.returncode}): {cmd[0]}")
    if not quiet:
        print(p.stdout)
    return p


def ffmpeg(args: list, quiet: bool = True) -> subprocess.CompletedProcess:
    return run([FFMPEG, "-hide_banner", "-nostdin", "-y", *args], quiet=quiet)


def probe(path: str | Path) -> dict:
    p = run([FFPROBE, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    return json.loads(p.stdout)


def video_stream(info: dict) -> dict | None:
    return next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)


def audio_stream(info: dict) -> dict | None:
    return next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)


def fps_of(stream: dict) -> float:
    num, den = stream.get("avg_frame_rate", "0/1").split("/")
    return float(num) / float(den) if float(den) else 0.0


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: str | Path, data) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    return path


def guided_filter(guide, src, radius: int = 8, eps: float = 1e-3):
    """Edge-aware guided filter (He et al. 2010), implemented with box filters.

    Self-contained because OpenCV 5's contrib build no longer exposes ximgproc.guidedFilter.
    guide: grey image (any dtype, scaled to 0..1); src: float32 map to filter.
    """
    import cv2
    import numpy as np
    I = guide.astype(np.float32)
    if I.max() > 1.0:
        I /= 255.0 if I.max() <= 255 else 65535.0
    p = src.astype(np.float32)
    k = (2 * radius + 1, 2 * radius + 1)
    box = lambda x: cv2.boxFilter(x, -1, k, borderType=cv2.BORDER_REFLECT)
    mI, mp = box(I), box(p)
    a = (box(I * p) - mI * mp) / (box(I * I) - mI * mI + eps)
    b = mp - a * mI
    return box(a) * I + box(b)
