#!/usr/bin/env python3
"""Download the studio's local CPU models to $STUDIO_MODELS (default /opt/studio/models).

Only permissively licensed models are fetched. Revisions are pinned so a rebuild gets the
same bytes; the SHA-256 of every file is written to models_manifest.json for verification.

    /opt/studio/venv/bin/python studio/fetch_models.py
"""
import hashlib
import json
import os
import shutil
from pathlib import Path

from huggingface_hub import hf_hub_download

ROOT = Path(os.environ.get("STUDIO_MODELS", "/opt/studio/models"))

# (repo, revision, file in repo, local name, licence, purpose)
MODELS = [
    ("opencv/face_detection_yunet", "3cc26e7f", "face_detection_yunet_2023mar.onnx",
     "face_detection_yunet_2023mar.onnx", "MIT (opencv_zoo)", "face detection + 5 landmarks"),
    ("opencv/face_recognition_sface", "3d708243", "face_recognition_sface_2021dec.onnx",
     "face_recognition_sface_2021dec.onnx", "Apache-2.0 (opencv_zoo)", "identity embedding for likeness QC"),
    ("onnx-community/depth-anything-v2-small", "4472b736", "onnx/model.onnx",
     "depth_anything_v2_small.onnx", "Apache-2.0", "monocular depth for 2.5D parallax / relighting"),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for repo, rev, fname, local, lic, purpose in MODELS:
        dst = ROOT / local
        if not dst.exists():
            src = hf_hub_download(repo, fname, revision=rev)
            shutil.copy(src, dst)
        entry = {"file": local, "repo": repo, "revision": rev, "license": lic,
                 "purpose": purpose, "bytes": dst.stat().st_size, "sha256": sha256(dst)}
        manifest.append(entry)
        print(f"ok  {local:40s} {entry['bytes']/1e6:7.1f} MB  {lic}")
    (ROOT / "models_manifest.json").write_text(json.dumps(manifest, indent=2))
    print("manifest ->", ROOT / "models_manifest.json")


if __name__ == "__main__":
    main()
