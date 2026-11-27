"""Sound & music cue chart v002 for SHANGHAI: BETWEEN TIME (data mirrors PRODUCTION_PLAN_v002 section 5).

Each lane is one cue; the filled envelope is its mix-bus peak level over time (lane height = -60..0 dBFS).
Output: 09_Audio_Music/CUE_CHART_v002.png  (palette validated with the dataviz validator, dark mode).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

OUT = Path(__file__).parent / "CUE_CHART_v002.png"
SURF, PAGE, INK, INK2, GRID, AXIS = "#191919", "#0b0b0b", "#efefef", "#9c9c9c", "#303030", "#474747"
CAT = {"rev": ("Reversed sound", "#338ced"), "amb": ("Forward ambience / SFX", "#e76624"),
       "trad": ("Traditional instruments (xiao, erhu)", "#00a888"), "note": ("THE NOTE, dizi G6 (thread TH + breath M4)", "#d28e05"),
       "syn": ("Synth drones / strings", "#e24d8b")}

def pulses(times, width, peak, rise=True):
    pts = []
    for t in times:
        pts += [(t, -60), (t + width * 0.95, peak), (t + width, -60)] if rise else [(t, peak), (t + width, -60)]
    return pts

thuds, t, rate = [], 12.5, 2.0
while t < 17.8:
    thuds.append(t); rate = 2 + 8 * (t - 12.5) / 5.3; t += 1 / rate
# (id, name, category, envelope points (time s, dBFS), style); None breaks a lane into separate segments
# (hard stops); style "alt" = A/B comparison only, not the plan
LANES = [
    ("TH", "the thread (S01 frozen, G6)", "note", [(0, -36), (12.5, -30), (19.5, -30), None,
                                                    (20.0, -30), (30.2, -30)], ""),
    ("A1", "water + drop (rev)", "rev", [(0, -34), (1.2, -28), (1.38, -14), (1.40, -60)], ""),
    ("A1b", "held water-glint tone", "amb", [(1.40, -30), (3.0, -30), (3.01, -60)], ""),
    ("A2", "Bund city bed", "amb", [(3.0, -30), (10.5, -30), (12.3, -50), (12.31, -60)], ""),
    ("A3", "wind", "amb", [(3.0, -32), (12.3, -32), (12.31, -60)], ""),
    ("A4", "aircraft (rev)", "rev", [(7.0, -50), (10.0, -20), (10.45, -60)], ""),
    ("M1", "erhu F5 (rev)", "trad", [(7.5, -28), (10.45, -16), (10.5, -60)], ""),
    ("A5", "flag + halyard (S16)", "amb", [(10.5, -24), (12.5, -24), (12.51, -60)], ""),
    ("SYN2", "single reverse swell", "syn", [(12.0, -60), (12.48, -10), (12.5, -60)], ""),
    ("A6", "metal thuds (rev)", "rev", pulses(thuds, 0.09, -22), ""),
    ("M2", "strings (rev)", "syn", [(12.5, -30), (17.95, -10), (17.96, -60)], ""),
    ("A7", "eave bells (rev)", "rev", [(12.5, -34), (18.0, -34), (18.01, -60)], ""),
    ("A8", "temple bell (rev)", "rev", [(18.0, -40), (19.45, -12), (19.46, -60)], ""),
    ("A9", "creak, then canal", "amb", [(20.0, -22), (20.3, -34), (21.0, -30), (27.0, -28), (29.0, -28), (29.9, -60)], ""),
    ("A10", "eave bell (fwd)", "amb", [(21.2, -30), (22.5, -50), (22.51, -60)], ""),
    ("M3", "xiao", "trad", [(21.0, -20), (27.0, -18), (28.0, -18), (29.8, -40), (29.81, -60)], ""),
    ("SYN4", "sub drone G1", "syn", [(22.0, -28), (27.0, -24), (29.5, -24), (30.2, -60)], ""),
    ("M4", "THE NOTE (one breath)", "note", [(31.0, -60), (31.05, -18), (31.4, -16), (35.2, -12), (36.6, -12),
                                              (37.2, -12.5), (38.0, -60)], ""),
    ("A11", "canal water", "amb", [(31.0, -32), (36.6, -32), (36.7, -28), (38.0, -45)], ""),
    ("A12", "drop impact", "amb", [(36.6, -10), (37.4, -50), (37.41, -60)], ""),
    ("alt", "support layers (A/B only)", "syn", [(31.4, -40), (32.4, -26), (36.6, -26), (36.61, -60)], "alt"),
]
# the three named exceptions to "sound follows the picture's time state"
EXCEPTIONS = [("A4", 7.0, "pre-lap"), ("SYN2", 12.5, "lead-in"), ("A8", 19.45, "hinge")]
SHOTS = [("SH010", 0, 3, "REV>HELD"), ("SH020", 3, 7.5, "HELD"), ("SH030", 7.5, 10.5, "REV"), ("SH040", 10.5, 12.5, "HELD"),
         ("SH050", 12.5, 18, "REV"), ("SH060", 18, 20, "HELD"), ("SH070", 20, 23, "FWD"), ("SH080", 23, 27, "FWD"),
         ("SH090", 27, 31, "HELD"), ("SH100", 31, 38, "FWD")]
SILENCE = [(19.5, 20.0), (30.2, 31.0)]

n = len(LANES)
fig, ax = plt.subplots(figsize=(16, 11), dpi=120)
fig.patch.set_facecolor(PAGE); ax.set_facecolor(SURF)
top = n + 1.6
for s in range(0, 39):
    ax.axvline(s, color=GRID, lw=0.6, zorder=0)
for sid, a, b, st in SHOTS:
    ax.add_patch(Rectangle((a + 0.04, n + 0.25), b - a - 0.08, 1.1, color="#2a2a2a", zorder=1, lw=0))
    ax.text((a + b) / 2, n + 0.95, sid, ha="center", va="center", color=INK, fontsize=9, fontweight="bold")
    ax.text((a + b) / 2, n + 0.55, st, ha="center", va="center", color=INK2, fontsize=8)
    ax.axvline(a, color=AXIS, lw=1.0, zorder=1)
for a, b in SILENCE:
    ax.add_patch(Rectangle((a, -0.2), b - a, n + 0.4, facecolor="none", edgecolor=INK2, hatch="////", lw=0, zorder=3))
    ax.text((a + b) / 2, -0.55, "SILENCE", ha="center", va="top", color=INK, fontsize=8)
row_of = {}
for i, (cid, name, cat, pts, style) in enumerate(LANES):
    base = n - 1 - i
    row_of[cid] = base
    col = CAT[cat][1]
    alt = style == "alt"
    segs, cur = [], []
    for p in pts + [None]:
        if p is None:
            segs.append(cur); cur = []
        else:
            cur.append(p)
    for seg in segs:
        xs = [q[0] for q in seg]; ys = [base + 0.08 + 0.80 * (max(q[1], -60) + 60) / 60 for q in seg]
        xs = [xs[0]] + xs + [xs[-1]]; ys = [base + 0.08] + ys + [base + 0.08]     # hard edges at both ends
        ax.fill_between(xs, base + 0.08, ys, color=col, alpha=0.18 if alt else 0.55, lw=0, zorder=2)
        ax.plot(xs, ys, color=col, lw=1.6 if alt else 2, ls=(0, (3, 2)) if alt else "-", zorder=4,
                solid_capstyle="round")
    ax.axhline(base + 0.08, color=GRID, lw=0.5, zorder=1)
    ax.text(-0.35, base + 0.45, f"{cid}  {name}", ha="right", va="center", color=INK2 if alt else INK, fontsize=8.5)
starts = {cid: next(p for p in pts if p is not None)[0] for cid, _, _, pts, _ in LANES}
for cid, t, label in EXCEPTIONS:
    ax.text(starts[cid] - 0.12, row_of[cid] + 0.45, f"exception: {label}", ha="right", va="center", color=INK,
            fontsize=7.5, fontstyle="italic", zorder=6)
ax.set_xlim(0, 38); ax.set_ylim(-1.0, top)
ax.set_xticks(range(0, 39, 2)); ax.set_xticklabels([f"0:{s:02d}" for s in range(0, 39, 2)], color=INK2, fontsize=8)
ax.set_yticks([])
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color(AXIS)
ax.tick_params(axis="x", colors=INK2, length=3)
ax.set_xlabel("film time (s)", color=INK2, fontsize=9)
fig.suptitle("SHANGHAI: BETWEEN TIME  -  sound & music cue chart v002", color=INK, fontsize=15, x=0.02, ha="left", y=0.985)
fig.text(0.02, 0.940, "Each lane: mix-bus peak level over time (lane height = -60 to 0 dBFS). Master -14 LUFS, -1 dBTP. "
         "Mode: G shang pentatonic.\n"
         "Option B shown (option A = delete lane TH). M4 enters 0:31.00; after the drop at 0:36.60 only the note and the water remain. "
         "Labels mark the 3 exceptions to the time grammar.",
         color=INK2, fontsize=9.5, ha="left")
leg = ax.legend(handles=[Patch(color=c, label=l) for l, c in CAT.values()], loc="upper left", bbox_to_anchor=(0.0, -0.06),
                ncol=5, frameon=False, fontsize=9, labelcolor=INK)
fig.subplots_adjust(left=0.16, right=0.985, top=0.915, bottom=0.10)
fig.savefig(OUT, facecolor=PAGE)
print("wrote", OUT)
