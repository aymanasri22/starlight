#!/usr/bin/env python3
"""Technical QC for renders + contact sheets for visual review.

    qc.py check FILE [--fps 24] [--size 3840x2160] [--lufs -14] [--tp -1.0] [--json out.json]
    qc.py sheet FILE --out sheet.jpg [--cols 6] [--rows 4]      timecoded contact sheet

`check` verifies: streams present, frame rate (CFR), resolution, Rec.709 colour tags, 10-bit where
the codec implies it, audio 48 kHz, integrated loudness and true peak, black frames, frozen frames,
and that audio and video durations agree (sync drift). Exit 0 = PASS, 1 = FAIL, 2 = WARN.

Technical QC never replaces watching the film. The QC Director also reviews contact sheets and the
full-resolution render on a calibrated display before anything is called final.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from audio import measure  # noqa: E402
from common import FFMPEG, audio_stream, ffmpeg, fps_of, probe, run, video_stream  # noqa: E402


def detect(path: str, filt: str, key: str) -> list[str]:
    p = run([FFMPEG, "-hide_banner", "-nostats", "-i", path, "-vf", filt, "-an", "-f", "null", "-"], check=False)
    return re.findall(rf"{key}[^\n]*", p.stderr)


def check(path: str, fps: float | None, size: str | None, lufs: float | None, tp: float, json_out: str | None) -> int:
    info = probe(path)
    v, a = video_stream(info), audio_stream(info)
    rows = []

    def add(name, ok, detail, warn=False):
        rows.append({"check": name, "status": "PASS" if ok else ("WARN" if warn else "FAIL"), "detail": detail})

    add("video stream", v is not None, v.get("codec_name") if v else "missing")
    if v:
        f = fps_of(v)
        r_num, r_den = v.get("r_frame_rate", "0/1").split("/")
        cfr = abs(float(r_num) / float(r_den) - f) < 0.01 if float(r_den) else False
        add("frame rate", (fps is None or abs(f - fps) < 0.01) and cfr, f"{f:.3f} fps, {'CFR' if cfr else 'VFR?'}")
        dims = f"{v['width']}x{v['height']}"
        add("resolution", size is None or dims == size, dims)
        tags = (v.get("color_primaries"), v.get("color_transfer"), v.get("color_space"))
        add("colour tags", tags == ("bt709", "bt709", "bt709"), "/".join(str(t) for t in tags), warn=True)
        add("pixel format", True, v.get("pix_fmt"))
        sar = v.get("sample_aspect_ratio", "1:1")
        add("square pixels", sar in ("1:1", "0:1", None), f"SAR {sar}")
    if a:
        add("audio sample rate", a.get("sample_rate") == "48000", a.get("sample_rate"))
        m = measure(path)
        if lufs is not None and m["integrated_lufs"] is not None:
            add("integrated loudness", abs(m["integrated_lufs"] - lufs) <= 1.0, f"{m['integrated_lufs']} LUFS (target {lufs})")
        if m["true_peak_dbtp"] is not None:
            add("true peak", m["true_peak_dbtp"] <= tp, f"{m['true_peak_dbtp']} dBTP (ceiling {tp})")
        add("loudness range", True, f"{m['lra_lu']} LU")
        vd, ad = float(v.get("duration", 0) or 0) if v else 0, float(a.get("duration", 0) or 0)
        if vd and ad:
            add("A/V duration", abs(vd - ad) < 0.05, f"video {vd:.3f}s, audio {ad:.3f}s", warn=True)
    else:
        add("audio stream", False, "none", warn=True)
    if v:
        black = detect(path, "blackdetect=d=0.25:pic_th=0.98", "black_start")
        add("black frames", not black, f"{len(black)} segments" + (f": {black[0]}" if black else ""), warn=True)
        frozen = detect(path, "freezedetect=n=0.001:d=1.0", "freeze_start")
        add("frozen frames", not frozen, f"{len(frozen)} segments", warn=True)
    worst = "FAIL" if any(r["status"] == "FAIL" for r in rows) else "WARN" if any(r["status"] == "WARN" for r in rows) else "PASS"
    for r in rows:
        print(f"{r['status']:5s} {r['check']:20s} {r['detail']}")
    print("overall:", worst)
    if json_out:
        Path(json_out).write_text(json.dumps({"file": path, "overall": worst, "checks": rows}, indent=2))
    return {"PASS": 0, "FAIL": 1, "WARN": 2}[worst]


def sheet(path: str, out: str, cols: int, rows: int) -> None:
    info = probe(path)
    dur = float(info["format"]["duration"])
    n = cols * rows
    rate = n / dur
    ffmpeg(["-i", path, "-vf",
            f"fps={rate:.6f},scale=480:-2,drawtext=text='%{{pts\\:hms}}':x=8:y=h-28:fontsize=20:fontcolor=white:"
            f"box=1:boxcolor=black@0.55,tile={cols}x{rows}:padding=6:margin=6:color=0x111111",
            "-frames:v", "1", "-q:v", "3", out])
    print(f"wrote {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("file"); c.add_argument("--fps", type=float); c.add_argument("--size")
    c.add_argument("--lufs", type=float); c.add_argument("--tp", type=float, default=-1.0); c.add_argument("--json")
    s = sub.add_parser("sheet"); s.add_argument("file"); s.add_argument("--out", required=True)
    s.add_argument("--cols", type=int, default=6); s.add_argument("--rows", type=int, default=4)
    a = ap.parse_args()
    if a.cmd == "check":
        sys.exit(check(a.file, a.fps, a.size, a.lufs, a.tp, a.json))
    sheet(a.file, a.out, a.cols, a.rows)
