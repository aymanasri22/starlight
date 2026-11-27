#!/usr/bin/env python3
"""Edit decision list -> conformed render + editable timeline exports (OTIO / EDL / FCPXML / FCP7 XML).

    timeline.py render EDIT.json --out cut.mov [--codec prores|h264]
    timeline.py export EDIT.json --out-dir 10_Edit_Timeline/

EDIT.json:
{
  "name": "seq_test", "fps": 24, "width": 1920, "height": 1080,
  "clips": [
    {"src": "a.mov", "in": 0.0, "dur": 3.0},
    {"src": "b.mp4", "in": 1.0, "dur": 3.0, "transition": {"type": "fade", "dur": 0.5},
     "speed": [[0, 1.0], [0.5, 0.25], [1.0, 1.0]]}          # optional speed ramp (time-normalised)
  ],
  "audio": "mix.wav"                                          # optional
}

Every clip is conformed to the sequence fps/size (scale+pad, CFR, Rec.709 tags) before joining,
so mixed phone footage (30/60 fps, portrait, HDR already converted) cuts together cleanly.
Transitions are FFmpeg xfade types (fade, dissolve, fadeblack, smoothleft, circleopen, ...): use them
sparingly; the default cut is a straight cut. Speed ramps are frame-blended time remaps.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import opentimelineio as otio

sys.path.insert(0, str(Path(__file__).parent))
from common import BT709_TAGS, TAG709, ffmpeg, fps_of, probe, video_stream  # noqa: E402


def ramp_expr(points: list[list[float]], dur: float) -> tuple[str, float]:
    """Build a setpts expression for a piecewise-linear speed curve. Returns (expr, source_seconds)."""
    # integrate 1/speed over output time to map output t -> source t, sampled finely
    ts = np.linspace(0, 1, 400)
    sp = np.interp(ts, [p[0] for p in points], [p[1] for p in points])
    src_rate = np.cumsum(sp) / len(ts)  # source seconds per output-normalised unit
    src_total = float(src_rate[-1] * dur)
    # setpts maps source PTS -> output PTS; invert the curve numerically
    src_norm = src_rate / src_rate[-1]
    knots = np.linspace(0, 1, 24)
    out_at = np.interp(knots, src_norm, ts)
    # piecewise-linear map in normalised source time u = T/src_total, as nested ifs from the end
    u = f"(T/{src_total:.6f})"
    expr = f"{out_at[-1]:.6f}"
    for i in reversed(range(len(knots) - 1)):
        a0, a1, b0, b1 = knots[i], knots[i + 1], out_at[i], out_at[i + 1]
        seg = f"({b0:.6f}+({u}-{a0:.6f})*{(b1 - b0) / (a1 - a0):.6f})"
        expr = f"if(lt({u},{a1:.6f}),{seg},{expr})"
    return f"({expr})*{dur:.6f}/TB", src_total


def conform(clip: dict, seq: dict, tmp: Path, i: int) -> Path:
    out = tmp / f"c{i:03d}.mov"
    W, H, fps = seq["width"], seq["height"], seq["fps"]
    vf = [f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos",
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black", "setsar=1"]
    src_dur = clip["dur"]
    if clip.get("speed"):
        expr, src_dur = ramp_expr(clip["speed"], clip["dur"])
        vf += [f"setpts='{expr}'", f"minterpolate=fps={fps}:mi_mode=blend"]  # quoted: expr contains commas
    vf += [f"fps={fps}", f"trim=duration={clip['dur']}", "setpts=PTS-STARTPTS", "format=yuv422p10le", TAG709]
    ffmpeg(["-ss", str(clip.get("in", 0)), "-t", f"{src_dur + 0.1:.3f}", "-i", clip["src"], "-an",
            "-vf", ",".join(vf), "-c:v", "prores_ks", "-profile:v", "3", *BT709_TAGS, str(out)])
    return out


def render(edit: dict, out: str, codec: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        parts = [conform(c, edit, tmp, i) for i, c in enumerate(edit["clips"])]
        inputs, chain, last, t = [], [], "[s0]", edit["clips"][0]["dur"]
        for i, p in enumerate(parts):
            inputs += ["-i", str(p)]
            # one timebase for every branch: concat emits 1/1000000 (AVTB) and xfade needs equal timebases
            chain.append(f"[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[s{i}]")
        for i, c in enumerate(edit["clips"][1:], start=1):
            tr = c.get("transition")
            if tr:
                d = tr.get("dur", 0.5)
                chain.append(f"{last}[s{i}]xfade=transition={tr.get('type', 'fade')}:duration={d}:offset={t - d:.4f}[v{i}]")
                t += c["dur"] - d
            else:
                chain.append(f"{last}[s{i}]concat=n=2:v=1:a=0[v{i}]")
                t += c["dur"]
            last = f"[v{i}]"
        args = [*inputs]
        if edit.get("audio"):
            args += ["-i", edit["audio"]]
        fc = ";".join(chain) + f";{last}{TAG709}[vout]"
        if edit.get("audio"):  # pad/trim audio to exactly the picture length (-shortest cut ~80 ms early)
            fc += f";[{len(parts)}:a]apad,atrim=end={t:.6f},asetpts=PTS-STARTPTS[aout]"
        args += ["-filter_complex", fc, "-map", "[vout]"]
        if edit.get("audio"):
            args += ["-map", "[aout]", "-c:a", "pcm_s24le" if codec == "prores" else "aac"]
        args += ["-t", f"{t:.6f}"]
        enc = (["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"] if codec == "prores"
               else ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p"])
        ffmpeg([*args, *enc, *BT709_TAGS, "-r", str(edit["fps"]), out])
    print(f"wrote {out}: {len(parts)} clips, {t:.2f}s")


def export(edit: dict, out_dir: str) -> list[str]:
    fps = edit["fps"]
    tl = otio.schema.Timeline(name=edit["name"])
    tl.global_start_time = otio.opentime.RationalTime(86400 * fps, fps)  # 01:00:00:00, editorial convention
    track = otio.schema.Track(name="V1", kind=otio.schema.TrackKind.Video)
    tl.tracks.append(track)
    for i, c in enumerate(edit["clips"]):
        info = probe(c["src"])
        v = video_stream(info) or {}
        src_fps = fps_of(v) or fps
        full = float(info["format"].get("duration", c["dur"]))
        ref = otio.schema.ExternalReference(
            target_url=Path(c["src"]).resolve().as_uri(),
            available_range=otio.opentime.TimeRange(otio.opentime.RationalTime(0, src_fps),
                                                    otio.opentime.RationalTime(round(full * src_fps), src_fps)))
        start_f = round(c.get("in", 0) * fps)
        dur_f = round(c["dur"] * fps)
        if c.get("transition") and i > 0:
            # The render overlaps the clips by d (xfade). NLEs centre a dissolve on the cut: the outgoing
            # clip ends d/2 early (its last d/2 is the out-handle), the incoming clip starts d/2 late
            # (its first d/2 is the in-handle). Total length stays identical to the render.
            half = round(c["transition"].get("dur", 0.5) * fps / 2)
            prev = track[-1]
            prev.source_range = otio.opentime.TimeRange(prev.source_range.start_time,
                                                        prev.source_range.duration - otio.opentime.RationalTime(half, fps))
            start_f, dur_f = start_f + half, dur_f - half
            d = otio.opentime.RationalTime(half, fps)
            track.append(otio.schema.Transition(transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
                                                in_offset=d, out_offset=d))
        clip = otio.schema.Clip(name=Path(c["src"]).stem, media_reference=ref,
                                source_range=otio.opentime.TimeRange(otio.opentime.RationalTime(start_f, fps),
                                                                     otio.opentime.RationalTime(dur_f, fps)))
        if c.get("speed"):
            clip.metadata["studio"] = {"speed_ramp": c["speed"], "note": "ramp is baked in the studio render; rebuild in NLE"}
        track.append(clip)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for ext, adapter in [("otio", "otio_json"), ("edl", "cmx_3600"), ("fcpxml", "fcpx_xml"), ("xml", "fcp_xml")]:
        p = out / f"{edit['name']}.{ext}"
        try:
            otio.adapters.write_to_file(tl, str(p), adapter_name=adapter)
            written.append(str(p))
        except Exception as e:  # EDL cannot express some things (e.g. >1 track); report, don't hide
            print(f"warn: {adapter} export failed: {e}")
    for w in written:
        print("wrote", w)
    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["render", "export"])
    ap.add_argument("edit")
    ap.add_argument("--out")
    ap.add_argument("--out-dir")
    ap.add_argument("--codec", default="prores", choices=["prores", "h264"])
    a = ap.parse_args()
    edit = json.loads(Path(a.edit).read_text())
    if a.cmd == "render":
        render(edit, a.out, a.codec)
    else:
        export(edit, a.out_dir)
