#!/usr/bin/env python3
"""Delivery encodes from a graded master (ProRes 422 HQ / 4444).

    deliver.py MASTER --profile PROFILE [--out-dir 12_Final_Renders] [--name NAME]
    deliver.py --list

Profiles (SDR Rec.709 unless noted). Bitrates are ceilings tuned for grain-preserving quality.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import BT709_TAGS, FILM, TAG709, ffmpeg  # noqa: E402

PROFILES = {
    # name: (description, size or None, video args, audio args, extension)
    "master_prores_hq": ("Archive/intermediate master, ProRes 422 HQ 10-bit", None,
                         ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le", "-vendor", "apl0"],
                         ["-c:a", "pcm_s24le", "-ar", "48000"], "mov"),
    "master_dnxhr_hqx": ("Avid/Resolve-friendly master, DNxHR HQX 10-bit", None,
                         ["-c:v", "dnxhd", "-profile:v", "dnxhr_hqx", "-pix_fmt", "yuv422p10le"],
                         ["-c:a", "pcm_s24le", "-ar", "48000"], "mov"),
    "uhd_h265_10bit": ("4K UHD HEVC Main10, high quality (YouTube / Vimeo / TV)", "3840:2160",
                       ["-c:v", "libx265", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p10le", "-tag:v", "hvc1",
                        "-x265-params", "aq-mode=3:no-sao=1:deblock=-1,-1:colorprim=bt709:transfer=bt709:colormatrix=bt709"],
                       ["-c:a", "aac", "-b:a", "320k", "-ar", "48000"], "mp4"),
    "uhd_h264": ("4K UHD H.264 High, maximum compatibility", "3840:2160",
                 ["-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", "-profile:v", "high",
                  "-tune", "film", "-x264-params", "aq-mode=3"],
                 ["-c:a", "aac", "-b:a", "320k", "-ar", "48000"], "mp4"),
    "hd_h264": ("1080p H.264 High (review links, messaging)", "1920:1080",
                ["-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high",
                 "-tune", "film", "-maxrate", "30M", "-bufsize", "60M"],
                ["-c:a", "aac", "-b:a", "256k", "-ar", "48000"], "mp4"),
    "vertical_9x16_h264": ("1080x1920 vertical (Reels/TikTok/Shorts); centre crop, reframe in edit for real shots", "crop916",
                           ["-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high"],
                           ["-c:a", "aac", "-b:a", "256k", "-ar", "48000"], "mp4"),
    "square_1x1_h264": ("1080x1080 square; centre crop", "crop11",
                        ["-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p"],
                        ["-c:a", "aac", "-b:a", "256k", "-ar", "48000"], "mp4"),
}


def deliver(master: str, profile: str, out_dir: Path, name: str | None) -> Path:
    desc, size, vargs, aargs, ext = PROFILES[profile]
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{name or Path(master).stem}_{profile}.{ext}"
    vf = []
    if size == "crop916":  # even-pixel crop; odd/fractional crops made the scaler emit non-square pixels
        vf = ["crop=trunc(ih*9/16/2)*2:ih", "scale=1080:1920:flags=lanczos"]
    elif size == "crop11":
        vf = ["crop=ih:ih", "scale=1080:1080:flags=lanczos"]
    elif size:
        vf = [f"scale={size}:flags=lanczos:force_original_aspect_ratio=decrease", f"pad={size}:(ow-iw)/2:(oh-ih)/2"]
    args = ["-i", master, "-map", "0:v:0", "-map", "0:a?", "-vf", ",".join([*vf, "setsar=1", TAG709])]
    ffmpeg([*args, *vargs, *BT709_TAGS, *aargs, "-movflags", "+faststart" if ext == "mp4" else "+write_colr", str(out)])
    print(f"wrote {out}  ({desc})")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("master", nargs="?")
    ap.add_argument("--profile", choices=sorted(PROFILES))
    ap.add_argument("--out-dir", default=str(FILM / "12_Final_Renders"))
    ap.add_argument("--name")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.master:
        for k, v in PROFILES.items():
            print(f"{k:22s} {v[0]}")
    else:
        deliver(a.master, a.profile, Path(a.out_dir), a.name)
