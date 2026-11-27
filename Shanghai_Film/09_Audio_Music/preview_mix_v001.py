"""Preview mix v001 for SHANGHAI: BETWEEN TIME, built from cue sheet v002 (option B: the thread).

Sources: the Freesound PREVIEW mp3s of the selected sounds (sfx/previews/, local, git-ignored; same works as the
originals at lower quality) + studio synthesis. S14 (VSCO 2 CE strings) is not downloaded yet: M2 is a synthesised
string cluster placeholder. Not a final mix: no stem review, previews only, auditioned by measurement, not by ear.

    python preview_mix_v001.py
Outputs (local): mix/preview_mix_v001.wav (bus), mix/preview_master_v001.wav (-14 LUFS, -1 dBTP)
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from pedalboard import HighpassFilter, LowpassFilter, Pedalboard, Reverb

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "studio" / "lib"))
sys.path.insert(0, str(HERE))
import audio  # noqa: E402
from cue_sheet_v002 import LANES  # noqa: E402

SR = 48000
DUR = 38.0
N = int(DUR * SR)
PV = HERE / "sfx" / "previews"
ENV = {cid: pts for cid, _, _, pts, _ in LANES}
rng = np.random.default_rng(3)
bus = np.zeros((N, 2), np.float32)


def dec(name):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(PV / name), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def seg(x, t0, t1):
    return x[int(t0 * SR):int(t1 * SR)].copy()


def mono(x):
    m = x.mean(1)
    return np.stack([m, m], 1)


def peak_norm(x):
    return x / (np.abs(x).max() + 1e-9)


def fade(x, fin=0.01, fout=0.01):
    x = x.copy()
    a, b = int(fin * SR), int(fout * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)[:, None]
    if b:
        x[-b:] *= np.linspace(1, 0, b)[:, None]
    return x


def db_env(pts, t):
    """Gain curve (linear) from cue-sheet points (time, dBFS); -60 or below is silence."""
    pts = [p for p in pts if p is not None]
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts], float)
    g = 10 ** (np.interp(t, xs, ys) / 20)
    g[(t < xs[0]) | (t > xs[-1])] = 0
    g[np.interp(t, xs, ys) <= -59.9] = 0
    return g


def place(x, t0, gain=None, peak_db=None):
    """Add x at film time t0. gain: per-sample curve over film time (array of len(x)) or None; peak_db: flat level."""
    i0 = int(round(t0 * SR))
    x = x.copy()
    if peak_db is not None:
        x = peak_norm(x) * 10 ** (peak_db / 20)
    if gain is not None:
        x = x * gain[:, None]
    a, b = max(0, i0), min(N, i0 + len(x))
    if b > a:
        bus[a:b] += x[a - i0:b - i0]


def lane(x, t0, cid):
    """Peak-normalise x and automate it with the cue sheet lane cid (levels are absolute dBFS)."""
    t = t0 + np.arange(len(x)) / SR
    place(peak_norm(x), t0, gain=db_env(ENV[cid], t))


def verb(x, room=0.5, wet=0.25):
    return Pedalboard([Reverb(room_size=room, wet_level=wet, dry_level=1.0)])(x.T.astype(np.float32), SR).T


def strikes(x, min_gap=0.3, rise_db=8):
    e = np.sqrt(np.convolve((x.mean(1)) ** 2, np.ones(480) / 480, "same"))
    d = 20 * np.log10(e + 1e-9)
    hop = 240
    dd = d[::hop]
    out = []
    for i in range(10, len(dd)):
        if dd[i] - dd[i - 10] > rise_db and dd[i] > dd.max() - 24 and (not out or i * hop / SR - out[-1] > min_gap):
            out.append(i * hop / SR)
    return out


# ------------------------------------------------------------------------------------------------- the dizi note
S01 = dec("384952.mp3")
F0 = 1581.6                                              # measured: G6 +15 c


def thread(seconds):
    """TH: the note's exact pitch, built from S01's own sustain spectrum (partials only, breath removed, never bends)."""
    s = S01[int(1.0 * SR):int(5.0 * SR)].mean(1)
    spec = np.abs(np.fft.rfft(s * np.hanning(len(s))))
    fr = np.fft.rfftfreq(len(s), 1 / SR)
    amps = []
    for k in range(1, 7):
        band = (fr > k * F0 * 0.985) & (fr < k * F0 * 1.015)
        amps.append(spec[band].max() if band.any() else 0)
    amps = np.array(amps) / max(amps)
    t = np.arange(int(seconds * SR)) / SR
    sig = np.zeros_like(t)
    for k, a in enumerate(amps, 1):
        if a < 0.01 or k * F0 > 18000:
            continue
        am = 1 + 0.06 * np.sin(2 * np.pi * rng.uniform(0.07, 0.23) * t + rng.uniform(0, 6.28))
        sig += a * am * np.sin(2 * np.pi * k * F0 * t + rng.uniform(0, 6.28))
    print("TH partial amplitudes (rel.):", np.round(amps, 3))
    return np.stack([sig, sig], 1).astype(np.float32)


th = thread(30.2)
for a, b in ((0.0, 19.5), (20.0, 30.2)):                 # hard stops at both silences
    x = fade(th[int(a * SR):int(b * SR)], 0.01 if a else 0.3, 0.01)
    t = a + np.arange(len(x)) / SR
    place(x / np.abs(th).max(), a, gain=db_env(ENV["TH"], t))

# M4: THE NOTE, one real breath, unedited; 30 ms anti-click ramp only
m4 = fade(S01[:int(7.0 * SR)], 0.03, 0.0)
lane(m4, 31.0, "M4")

# ------------------------------------------------------------------------------------------------ SH010 (0-3 s)
S12 = dec("S12_389411.mp3")
S06 = dec("S06_533146.mp3")
lane(seg(S12, 10.0, 11.4)[::-1], 0.0, "A1")                          # canal water, reversed
drop_r = mono(verb(mono(S06), 0.35, 0.2))[::-1]                     # the drop reversed: an "inhale" into the surface
pk = int(np.argmax(np.abs(drop_r).mean(1)))
place(fade(drop_r, 0.005, 0.005), 1.38 - pk / SR, peak_db=-14)
tail = S06[int(0.36 * SR):int(0.60 * SR)].mean(1)                   # A1b: the drop's tail, frozen and held
spec = np.abs(np.fft.rfft(tail * np.hanning(len(tail))))
held = np.fft.irfft(spec * np.exp(1j * rng.uniform(0, 2 * np.pi, len(spec))), n=len(tail))
held = np.tile(held, int(1.7 / (len(tail) / SR)) + 2)[:int(1.6 * SR)]
held = Pedalboard([LowpassFilter(9000)])(held.astype(np.float32), SR)
place(fade(np.stack([held, held], 1), 0.04, 0.01), 1.40, peak_db=-30)

# ------------------------------------------------------------------------------------- SH020-SH040 (3.0-12.5 s)
lane(seg(dec("S09_846247.mp3"), 10.0, 19.4), 3.0, "A2")             # the Bund city bed, forward
lane(seg(dec("S11_726319.mp3"), 0.5, 9.9), 3.0, "A3")               # wind, forward
S07 = dec("S07_383068.mp3")
air = seg(S07, 42.36 - 0.45, 42.36 + 3.05)[::-1].copy()            # fly-by reversed: peak at 10.00
pan = np.linspace(-0.8, 0.8, len(air))
m = air.mean(1)
air = np.stack([m * np.sqrt((1 - pan) / 2), m * np.sqrt((1 + pan) / 2)], 1)
lane(fade(air, 0.2, 0.01), 7.0, "A4")
S03 = dec("467482.mp3")
erhu = seg(S03, 0.0, 3.0)[::-1].copy()                               # erhu F5 reversed; bow attack lands on T3
lane(fade(erhu, 0.3, 0.005), 7.5, "M1")
S16 = dec("S16_146272.mp3")
lane(fade(seg(S16, 54.3, 56.3), 0.01, 0.01), 10.5, "A5")            # flag + halyard, forward (HELD picture)
imp = audio.synth("impact", 1.5)[::-1].copy()                       # SYN2: one reverse swell into the cut T4
imp = imp[-int(0.5 * SR):]
place(fade(imp, 0.15, 0.003), 12.0, peak_db=-10)

# -------------------------------------------------------------------------------------- SH050-SH060 (12.5-20 s)
S10 = dec("S10_438134.mp3")
hits = [0.17, 0.46, 0.9, 3.12, 3.36]
thud_t, t_, rate = [], 12.5, 2.0
while t_ < 17.8:
    thud_t.append(t_); rate = 2 + 8 * (t_ - 12.5) / 5.3; t_ += 1 / rate
for j, tt in enumerate(thud_t):                                     # one reversed thud per vanishing floor
    gap = (thud_t[j + 1] - tt) if j + 1 < len(thud_t) else 0.2
    L = min(0.22, gap * 0.9)
    h = hits[j % len(hits)]
    x = mono(seg(S10, h - 0.005, h + L))[::-1].copy()
    pk = int(np.argmax(np.abs(x).mean(1)))
    place(fade(x, 0.01, 0.003), tt - pk / SR, peak_db=-22 + rng.uniform(-1.5, 1.5))


def string_cluster(seconds):
    """M2 placeholder (S14 not downloaded): G shang cluster G3 A3 C4 D4 F4 (+15 c), struck, reversed."""
    t = np.arange(int(seconds * SR)) / SR
    cents = 2 ** (15 / 1200)
    sig = np.zeros((len(t), 2))
    for f in (196.0, 220.0, 261.63, 293.66, 349.23):
        for ch, det in ((0, -4), (1, 4)):
            ff = f * cents * 2 ** (det / 1200) * (1 + 0.0045 * np.sin(2 * np.pi * 5.2 * t + rng.uniform(0, 6)))
            ph = 2 * np.pi * np.cumsum(ff) / SR
            v = sum(np.sin(k * ph) / k for k in range(1, 12))
            sig[:, ch] += v
    sig *= np.exp(-t / 1.6)[:, None]
    sig = Pedalboard([LowpassFilter(2600), HighpassFilter(90), Reverb(room_size=0.8, wet_level=0.35)])(
        sig.T.astype(np.float32), SR).T
    return sig[::-1].copy()


m2 = string_cluster(5.45)
lane(fade(m2, 0.2, 0.004), 12.5, "M2")
S05 = dec("S05_874641.mp3")
chimes = strikes(S05, 0.25, 6)
print("chime strikes:", [round(c, 2) for c in chimes[:10]])
for j, tt in enumerate((13.3, 14.6, 15.8, 16.9)):                   # sparse eave bells, reversed
    h = chimes[(j * 2 + 1) % len(chimes)]
    x = verb(mono(seg(S05, h - 0.005, h + 0.9)), 0.6, 0.3)[::-1].copy()
    pk = int(np.argmax(np.abs(x).mean(1)))
    place(fade(x, 0.05, 0.003), tt - pk / SR, peak_db=-34)
S04 = dec("S04_423401.mp3")
# A8 (hinge): S04 is a continuous ringing bed with no isolated strike (measured), so its real ring is shaped into a
# strike decay (3 ms attack, 0.45 s decay, room), then reversed: it blooms into the strike at 19.45.
# Placeholder until a single-strike temple-bell recording is sourced.
ring = seg(S04, 24.0, 25.8)
tt = np.arange(len(ring)) / SR
strike = ring * (np.minimum(1, tt / 0.003) * np.exp(-tt / 0.45))[:, None]
strike = verb(strike, 0.85, 0.35)[:int(1.45 * SR)]
bell = strike[::-1].copy()
place(fade(bell, 0.3, 0.002), 19.45 - len(bell) / SR, peak_db=-12)

# ----------------------------------------------------------------------------------- SH070-SH090 (20.0-30.2 s)
S13 = dec("S13_91071.mp3")
cands = [o for o in strikes(S13, 0.4, 8) if o < 180]
def flat(o):                                                         # most tonal onset = a creak, not a splash
    s = seg(S13, o, o + 0.3).mean(1)
    p = np.abs(np.fft.rfft(s * np.hanning(len(s)))) + 1e-9
    return np.exp(np.mean(np.log(p))) / np.mean(p)
creak_t = min(cands[:40], key=flat)
print(f"creak at S13 {creak_t:.2f}s (flatness {flat(creak_t):.3f})")
creak = fade(seg(S13, creak_t - 0.01, creak_t + 0.6), 0.005, 0.15)
place(creak, 20.0, peak_db=-22)                                     # the first forward sound
water = seg(S12, 30.0, 39.9)
t = 20.3 + np.arange(len(water)) / SR
place(peak_norm(fade(water, 0.3, 0.01)), 20.3, gain=db_env([(20.3, -34), (21.0, -30), (27.0, -28), (29.0, -28), (29.9, -60)], t))
h = chimes[min(5, len(chimes) - 1)]
place(fade(verb(mono(seg(S05, h - 0.005, h + 1.3)), 0.6, 0.25), 0.003, 0.2), 21.2, peak_db=-30)   # one bell, forward
S02 = dec("161912.mp3")
pa = fade(seg(S02, 8.6, 13.2), 0.15, 0.3)
pb = fade(seg(S02, 28.4, 32.8), 0.3, 0.01)
xiao = np.zeros((int(8.8 * SR), 2), np.float32)
xiao[:len(pa)] += pa
o = int(4.3 * SR)
xiao[o:o + len(pb)] += pb[:len(xiao) - o]
lane(xiao, 21.0, "M3")
t = np.arange(int(8.2 * SR)) / SR
g1 = 49.0 * 2 ** (15 / 1200)
sub = sum(a * np.sin(2 * np.pi * k * g1 * t) for k, a in ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.18)))
sub *= 1 + 0.08 * np.sin(2 * np.pi * 0.17 * t)
lane(fade(np.stack([sub, sub], 1).astype(np.float32), 0.5, 0.01), 22.0, "SYN4")

# ------------------------------------------------------------------------------------------- SH100 (31-38 s)
water2 = seg(S12, 50.0, 57.0)
t = 31.0 + np.arange(len(water2)) / SR
place(peak_norm(fade(water2, 0.6, 0.01)), 31.0, gain=db_env(ENV["A11"], t))
place(fade(verb(mono(S06), 0.45, 0.25), 0.001, 0.05), 36.60 - int(np.argmax(np.abs(S06).mean(1))) / SR, peak_db=-10)

# --------------------------------------------------------------------------------------- silences + bus + master
for a, b in ((19.50, 20.00), (30.20, 31.00)):
    i, j = int(a * SR), int(b * SR)
    bus[i - 240:i] *= np.linspace(1, 0, 240)[:, None]
    bus[i:j] = 0
bus = Pedalboard([HighpassFilter(25)])(bus.T.astype(np.float32), SR).T
for a, b in ((19.50, 20.00), (30.20, 31.00)):
    bus[int(a * SR):int(b * SR)] = 0
(HERE / "mix").mkdir(exist_ok=True)
import soundfile as sf  # noqa: E402
raw = HERE / "mix" / "preview_mix_v001.wav"
sf.write(raw, bus, SR, subtype="PCM_24")
print(f"bus peak {20 * np.log10(np.abs(bus).max()):.1f} dBFS, {len(bus) / SR:.3f} s")
audio.master(str(raw), str(HERE / "mix" / "preview_master_v001.wav"), -14.0, -1.0)
