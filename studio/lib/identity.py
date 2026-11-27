#!/usr/bin/env python3
"""Likeness / identity-preservation gate (OpenCV YuNet detector + SFace embeddings, CPU).

    identity.py enroll REF_IMG [REF_IMG ...] --out ref.npz     build the reference set from real photos
    identity.py check ref.npz MEDIA [MEDIA ...] [--every 12] [--json out.json] [--sheet crops.jpg]

For every face found in MEDIA (stills, or video sampled every N frames) the best cosine similarity
against the reference set is reported. SFace's published operating point is cosine >= 0.363 for
"same person"; the studio is stricter:

    >= 0.50  PASS      strong match
    0.363 - 0.50 REVIEW  same-person range but weak: inspect side by side
    <  0.363 FAIL      likeness lost (or a different person)

This is an automated tripwire, not a judge of likeness. A pass does NOT prove a generated image
looks like the person (age, skin texture, proportions can drift while embeddings stay close), so
every AI-touched shot of the person still gets a side-by-side visual review against the originals.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from common import MODELS  # noqa: E402

DET = MODELS / "face_detection_yunet_2023mar.onnx"
REC = MODELS / "face_recognition_sface_2021dec.onnx"
PASS, MATCH = 0.50, 0.363


def _models():
    det = cv2.FaceDetectorYN.create(str(DET), "", (320, 320), score_threshold=0.8, nms_threshold=0.3, top_k=50)
    rec = cv2.FaceRecognizerSF.create(str(REC), "")
    return det, rec


def faces(img: np.ndarray, det, rec, max_side: int = 1600):
    """Return [(feature, box, score, aligned_crop)] for each detected face."""
    scale = min(1.0, max_side / max(img.shape[:2]))
    work = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA) if scale < 1 else img
    det.setInputSize((work.shape[1], work.shape[0]))
    _, found = det.detect(work)
    out = []
    for f in (found if found is not None else []):
        crop = rec.alignCrop(work, f)
        feat = rec.feature(crop).flatten()
        feat = feat / (np.linalg.norm(feat) + 1e-9)
        out.append((feat, (f[:4] / scale).round().astype(int).tolist(), float(f[-1]), crop))
    return out


def frames(path: Path, every: int):
    img = cv2.imread(str(path))
    if img is not None:
        yield 0, img
        return
    cap = cv2.VideoCapture(str(path))
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % every == 0:
            yield i, frame
        i += 1


def enroll(refs: list[str], out: str) -> None:
    det, rec = _models()
    feats = []
    for r in refs:
        img = cv2.imread(r)
        found = faces(img, det, rec) if img is not None else []
        if len(found) != 1:
            print(f"skip {r}: {len(found)} faces (reference photos must contain exactly one face)")
            continue
        feats.append(found[0][0])
        print(f"enrolled {r}")
    if not feats:
        sys.exit("no usable reference faces")
    np.savez(out, feats=np.stack(feats), refs=np.array(refs))
    print(f"reference set: {len(feats)} faces -> {out}")


def check(ref: str, media: list[str], every: int, json_out: str | None, sheet: str | None) -> int:
    det, rec = _models()
    ref_feats = np.load(ref)["feats"]
    results, crops, worst = [], [], "PASS"
    for m in media:
        for idx, img in frames(Path(m), every):
            for feat, box, score, crop in faces(img, det, rec):
                sim = float(np.max(ref_feats @ feat))
                verdict = "PASS" if sim >= PASS else ("REVIEW" if sim >= MATCH else "FAIL")
                results.append({"media": m, "frame": idx, "box": box, "det_score": round(score, 3),
                                "similarity": round(sim, 4), "verdict": verdict})
                crops.append((crop, verdict, sim))
                if verdict == "FAIL" or (verdict == "REVIEW" and worst == "PASS"):
                    worst = verdict
            if not any(r["media"] == m and r["frame"] == idx for r in results):
                results.append({"media": m, "frame": idx, "verdict": "NO_FACE"})
    for r in results:
        print(f"{r['verdict']:8s} sim={r.get('similarity', '-')!s:7s} {Path(r['media']).name} frame {r['frame']}")
    if json_out:
        Path(json_out).write_text(json.dumps({"thresholds": {"pass": PASS, "match": MATCH}, "overall": worst,
                                              "results": results}, indent=2))
    if sheet and crops:
        colours = {"PASS": (80, 200, 80), "REVIEW": (0, 190, 255), "FAIL": (60, 60, 230)}
        tiles = []
        for crop, v, s in crops[:48]:
            t = cv2.copyMakeBorder(cv2.resize(crop, (160, 160)), 6, 30, 6, 6, cv2.BORDER_CONSTANT, value=colours[v])
            cv2.putText(t, f"{v} {s:.2f}", (8, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            tiles.append(t)
        while len(tiles) % 6:
            tiles.append(np.zeros_like(tiles[0]))
        rows = [np.hstack(tiles[i:i + 6]) for i in range(0, len(tiles), 6)]
        cv2.imwrite(sheet, np.vstack(rows))
    print("overall:", worst)
    return {"PASS": 0, "REVIEW": 2, "FAIL": 1}[worst]


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("enroll"); e.add_argument("refs", nargs="+"); e.add_argument("--out", required=True)
    c = sub.add_parser("check"); c.add_argument("ref"); c.add_argument("media", nargs="+")
    c.add_argument("--every", type=int, default=12); c.add_argument("--json"); c.add_argument("--sheet")
    a = ap.parse_args()
    if a.cmd == "enroll":
        enroll(a.refs, a.out)
    else:
        sys.exit(check(a.ref, a.media, a.every, a.json, a.sheet))
