"""Cue sheet v002 data: the single source for CUE_CHART_v002.png (cue_chart.py) and the preview mix
(preview_mix_v001.py). Mirrors PRODUCTION_PLAN_v002 section 5. Levels are mix-bus peak dBFS."""


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
