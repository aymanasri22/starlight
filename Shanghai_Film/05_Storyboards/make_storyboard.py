"""Build the v1 storyboard sheet (10 panels, true 9:16 framings) from real media + feasibility frames.

Output (local only, contains the client's photos): 05_Storyboards/STORYBOARD_v001.jpg
"""
from pathlib import Path

import cv2
import numpy as np

FILM = Path(__file__).resolve().parents[1]
FX = FILM / "08_VFX_Compositing/feasibility"
PH = FILM / "01_Original_Photos"
PW, PHH = 360, 640


def crop916(img, x0=None, y0=0, scale=1.0):
    h, w = img.shape[:2]
    ch = int(h / scale)
    cw = int(ch * 9 / 16)
    if cw > w:
        cw = w; ch = int(cw * 16 / 9)
    x0 = (w - cw) // 2 if x0 is None else min(max(0, x0), w - cw)
    y0 = min(max(0, y0), h - ch)
    return cv2.resize(img[y0:y0 + ch, x0:x0 + cw], (PW, PHH), interpolation=cv2.INTER_AREA)


def video_frame(t):
    cap = cv2.VideoCapture(str(FILM / "02_Original_Videos/IMG_1039.mov"))
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, f = cap.read()
    return f


def mp4_frame(path, idx):
    cap = cv2.VideoCapture(str(path)); f = None
    for _ in range(idx + 1):
        ok, f2 = cap.read()
        if not ok:
            break
        f = f2
    return f


def arrow(p, a, b, col=(80, 220, 255)):
    cv2.arrowedLine(p, a, b, col, 2, cv2.LINE_AA, tipLength=0.18)
    return p


un = cv2.imread(str(FX / "IMG_1006_unmirrored.png"))
panels = []
# SH010: SH100's 36.60-38.00 reversed: rings converge on the REFLECTED lower sphere, the drop lifts and HOLDS
full = cv2.imread(str(FX / "f7_v31_full.png"))            # whole canal photo at 1080x1920 with the v3.1 reflection
p = cv2.resize(full[550:1617, 308:908], (PW, PHH))
cv2.ellipse(p, (int(384 / 1080 * PW), int(930 / 1920 * PHH)), (5, 7), 0, 0, 360, (235, 238, 240), -1, cv2.LINE_AA)
panels.append(("SH010", "0:00.0-0:03.0", "DROP RISES FROM REFLECTED SPHERE", p))
p = crop916(un, x0=300); arrow(p, (110, 360), (300, 360)); panels.append(("SH020", "0:03.0-0:07.5", "THE FIXED POINT (held)", p))
im = cv2.imread(str(PH / "IMG_1009.jpg")); p = crop916(im, x0=0)
cx, cy = int(893 / 1134 * PW), int(94 / 2016 * PHH); cv2.circle(p, (cx, cy), 14, (80, 220, 255), 1, cv2.LINE_AA); arrow(p, (cx + 18, cy + 18), (cx + 70, cy + 18))
panels.append(("SH030", "0:07.5-0:10.5", "AIRCRAFT FLIES TAIL-FIRST", p))
p = crop916(cv2.imread(str(PH / "IMG_1750.jpg"))); arrow(p, (330, 520), (330, 380)); panels.append(("SH040", "0:10.5-0:12.5", "THE BUND HOLDS ITS BREATH", p))
strip = cv2.imread(str(FX / "longhua_unbuild_strip.jpg")); sw = strip.shape[1] // 4
panels.append(("SH050", "0:12.5-0:18.0", "UNBUILDING (reverse)", crop916(strip[40:, sw:2 * sw])))
p = crop916(cv2.imread(str(FX / "longhua_clean.png")), x0=263); arrow(p, (330, 120), (330, 330)); panels.append(("SH060", "0:18.0-0:20.0", "PAGODA ALONE + SILENCE", p))
v5 = FX / "f6_transform_v5.mp4"
panels.append(("SH070a", "0:20.0 (start)", "RIVER RISES, CABLES FADE [TEST v5]", cv2.resize(mp4_frame(v5, 14), (PW, PHH))))
panels.append(("SH070b", "0:21.5 (middle)", "MIDDLE: NOT YET AT BRIEF [TEST v5]", cv2.resize(mp4_frame(v5, 36), (PW, PHH))))
panels.append(("SH070c", "0:22.6 (landing)", "LANDS ON REAL PAVILION [TEST v5]", cv2.resize(mp4_frame(v5, 56), (PW, PHH))))
panels.append(("SH080", "0:23.0-0:27.0", "THE CROSSING (real, 5x slow)", cv2.resize(video_frame(6.30), (PW, PHH))))
panels.append(("SH090", "0:27.0-0:31.0", "WITNESS (held), CANAL FLOWS", crop916(cv2.imread(str(PH / "IMG_1062.jpg")), x0=483)))
p = cv2.resize(full, (PW, PHH))
cv2.putText(p, "title: placeholder", (90, 560), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)
panels.append(("SH100", "0:31.0-0:38.0", "REFLECTION + THE NOTE [TEST v3.1]", p))
cards = []
for sid, tc, title, img in panels:
    card = np.full((PHH + 64, PW, 3), 18, np.uint8)
    card[64:] = img
    cv2.putText(card, f"{sid}  {tc}", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (240, 240, 240), 1, cv2.LINE_AA)
    cv2.putText(card, title, (8, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.47, (120, 200, 255), 1, cv2.LINE_AA)
    cards.append(cv2.copyMakeBorder(card, 6, 6, 6, 6, cv2.BORDER_CONSTANT, value=(40, 40, 40)))
rows = [np.hstack(cards[i:i + 6]) for i in (0, 6)]
head = np.full((70, rows[0].shape[1], 3), 12, np.uint8)
cv2.putText(head, "SHANGHAI: BETWEEN TIME  -  storyboard v002 (previs from real media + feasibility tests; [TEST] = not final look)",
            (14, 44), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (235, 235, 235), 1, cv2.LINE_AA)
sheet = np.vstack([head] + rows)
cv2.imwrite(str(FILM / "05_Storyboards/STORYBOARD_v002.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
print("wrote", FILM / "05_Storyboards/STORYBOARD_v002.jpg", sheet.shape)
