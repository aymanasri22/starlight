#!/usr/bin/env python3
"""Sound design + mix + master.

    audio.py sfx KIND --out x.wav [--seconds 3]      synthesize: riser | impact | whoosh | roomtone | sub
    audio.py mix --out mix.wav STEM[@gain_db[@start_s]] ...   [--reverb 0.0] [--sr 48000]
    audio.py master IN OUT [--lufs -14] [--tp -1.0]  loudness-normalise with a true-peak ceiling
    audio.py measure FILE                            integrated LUFS, true peak, LRA (EBU R128)

Targets: streaming/web -14 LUFS, -1 dBTP;  Apple/podcast -16;  broadcast EBU R128 -23;  cinema: mix
to dialnorm at 85 dB SPL monitoring (not measurable here; done in a calibrated room).
Synthesized SFX are original and royalty-free. Music must come from a licensed source (see report).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from pedalboard import Compressor, HighpassFilter, Limiter, LowpassFilter, Pedalboard, Reverb

sys.path.insert(0, str(Path(__file__).parent))
from common import FFMPEG, run  # noqa: E402

SR = 48000
rng = np.random.default_rng(7)


def _env(n, a=0.01, r=0.3):
    t = np.linspace(0, 1, n)
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))


def synth(kind: str, seconds: float) -> np.ndarray:
    n = int(SR * seconds)
    t = np.arange(n) / SR
    if kind == "riser":  # rising filtered noise + pitch sweep, ends on a hard stop
        sweep = np.sin(2 * np.pi * np.cumsum(np.geomspace(80, 1800, n)) / SR)
        noise = rng.standard_normal(n)
        sig = 0.5 * sweep * (t / seconds) ** 2 + 0.4 * noise * (t / seconds) ** 3
        sig = Pedalboard([HighpassFilter(200), Reverb(room_size=0.6, wet_level=0.25)])(sig.astype(np.float32), SR)
    elif kind == "impact":  # sub drop + transient + noise tail
        sub = np.sin(2 * np.pi * np.cumsum(np.geomspace(90, 32, n)) / SR) * _env(n, 0.002, 0.35)
        click = rng.standard_normal(n) * _env(n, 0.0005, 0.01)
        tail = rng.standard_normal(n) * _env(n, 0.003, 0.18) * 0.3
        sig = Pedalboard([Reverb(room_size=0.85, wet_level=0.3)])((sub + click + tail).astype(np.float32), SR)
    elif kind == "whoosh":  # band-passed noise with a moving centre and swelling envelope
        noise = rng.standard_normal(n).astype(np.float32)
        env = np.sin(np.pi * t / seconds) ** 2
        lo = Pedalboard([LowpassFilter(900)])(noise, SR)
        hi = Pedalboard([HighpassFilter(2500)])(noise, SR)
        mixw = np.clip(t / seconds, 0, 1)
        sig = (lo * (1 - mixw) + hi * mixw) * env
    elif kind == "roomtone":  # pink-ish city air bed
        white = rng.standard_normal(n)
        pink = np.cumsum(white)
        pink -= np.convolve(pink, np.ones(4800) / 4800, mode="same")
        sig = Pedalboard([LowpassFilter(6000), HighpassFilter(40)])((pink / np.abs(pink).max() * 0.2).astype(np.float32), SR)
    elif kind == "sub":
        sig = np.sin(2 * np.pi * 45 * t) * _env(n, 0.02, 0.6)
    else:
        raise SystemExit(f"unknown sfx kind {kind}")
    sig = np.asarray(sig, dtype=np.float32)
    sig /= np.abs(sig).max() + 1e-9
    stereo = np.stack([sig, np.roll(sig, 12)], axis=1) * 0.7  # tiny inter-channel offset for width
    return stereo.astype(np.float32)


def load(path: str, sr: int = SR) -> np.ndarray:
    data, fs = sf.read(path, dtype="float32", always_2d=True)
    if fs != sr:
        import librosa
        data = librosa.resample(data.T, orig_sr=fs, target_sr=sr).T
    if data.shape[1] == 1:
        data = np.repeat(data, 2, axis=1)
    return data[:, :2]


def mix(stems: list[str], out: str, reverb: float, sr: int) -> None:
    layers, length = [], 0
    for spec in stems:
        parts = spec.split("@")
        path, gain, start = parts[0], float(parts[1]) if len(parts) > 1 else 0.0, float(parts[2]) if len(parts) > 2 else 0.0
        a = load(path, sr) * (10 ** (gain / 20))
        off = int(start * sr)
        layers.append((off, a))
        length = max(length, off + len(a))
    bus = np.zeros((length, 2), np.float32)
    for off, a in layers:
        bus[off:off + len(a)] += a
    board = Pedalboard([HighpassFilter(25), Compressor(threshold_db=-18, ratio=2.0, attack_ms=15, release_ms=200)])
    if reverb > 0:
        board.append(Reverb(room_size=0.5, wet_level=reverb))
    bus = board(bus.T, sr).T
    sf.write(out, bus, sr, subtype="PCM_24")
    print(f"wrote {out}: {len(stems)} stems, {length / sr:.2f}s")


def measure(path: str) -> dict:
    p = run([FFMPEG, "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], check=False)
    tail = p.stderr[p.stderr.rfind("Summary:"):]
    get = lambda k: float(re.search(rf"{k}:\s+(-?[\d.]+|-inf)", tail).group(1)) if re.search(rf"{k}:\s+(-?[\d.]+)", tail) else None
    return {"integrated_lufs": get("I"), "lra_lu": get("LRA"), "true_peak_dbtp": get("Peak")}


def master(src: str, dst: str, lufs: float, tp: float) -> dict:
    data, sr = sf.read(src, dtype="float32", always_2d=True)
    meter = pyln.Meter(sr)
    loud = meter.integrated_loudness(data)
    data = pyln.normalize.loudness(data, loud, lufs)
    # true-peak-safe limiting: 4x oversampled limiter at the ceiling, then re-trim to target
    board = Pedalboard([Limiter(threshold_db=tp - 0.3, release_ms=80)])
    data = board(data.T, sr).T
    data = pyln.normalize.loudness(data, meter.integrated_loudness(data), lufs)
    peak = np.abs(data).max()
    ceiling = 10 ** ((tp - 0.5) / 20)
    if peak > ceiling:
        data *= ceiling / peak
    sf.write(dst, data, sr, subtype="PCM_24")
    m = measure(dst)
    print(f"wrote {dst}: {json.dumps(m)}")
    return m


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sfx"); s.add_argument("kind"); s.add_argument("--out", required=True); s.add_argument("--seconds", type=float, default=3)
    m = sub.add_parser("mix"); m.add_argument("stems", nargs="+"); m.add_argument("--out", required=True)
    m.add_argument("--reverb", type=float, default=0.0); m.add_argument("--sr", type=int, default=SR)
    ms = sub.add_parser("master"); ms.add_argument("src"); ms.add_argument("dst")
    ms.add_argument("--lufs", type=float, default=-14.0); ms.add_argument("--tp", type=float, default=-1.0)
    me = sub.add_parser("measure"); me.add_argument("file")
    a = ap.parse_args()
    if a.cmd == "sfx":
        sf.write(a.out, synth(a.kind, a.seconds), SR, subtype="PCM_24"); print(f"wrote {a.out}")
    elif a.cmd == "mix":
        mix(a.stems, a.out, a.reverb, a.sr)
    elif a.cmd == "master":
        master(a.src, a.dst, a.lufs, a.tp)
    else:
        print(json.dumps(measure(a.file), indent=2))
