#!/usr/bin/env python3
"""Non-destructive media ingest.

    ingest.py import SRC_DIR [--film DIR]   copy originals in, hash, lock read-only, catalogue, proxies
    ingest.py verify [--film DIR]           re-hash every original against the catalogue

Originals are COPIED (never moved) into 01_Original_Photos / 02_Original_Videos, made read-only,
and catalogued with SHA-256 plus camera/lens/GPS/time/colour metadata. All later work uses
proxies in 03_Selected_Media/proxies or derived copies; the originals are never written again.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import FILM, ffmpeg, fps_of, probe, run, sha256, video_stream, write_json  # noqa: E402

PHOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tif", ".tiff", ".dng", ".cr2", ".cr3", ".nef", ".arw", ".raf", ".webp"}
VIDEO_EXT = {".mov", ".mp4", ".m4v", ".mkv", ".avi", ".mts", ".m2ts", ".mxf", ".insv", ".360"}
EXIF_KEYS = ["DateTimeOriginal", "CreateDate", "OffsetTimeOriginal", "Make", "Model", "LensModel", "FocalLength",
             "FocalLengthIn35mmFormat", "FNumber", "ExposureTime", "ISO", "ImageWidth", "ImageHeight", "Orientation",
             "GPSLatitude", "GPSLongitude", "GPSAltitude", "ProfileDescription", "ColorSpace", "Duration",
             "VideoFrameRate", "CompressorName"]


def exif(path: Path) -> dict:
    p = run(["exiftool", "-json", "-n", *[f"-{k}" for k in EXIF_KEYS], str(path)], check=False)
    try:
        return json.loads(p.stdout)[0]
    except Exception:
        return {}


def video_meta(path: Path) -> dict:
    info = probe(path)
    v = video_stream(info) or {}
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    trc = v.get("color_transfer", "")
    return {
        "codec": v.get("codec_name"), "profile": v.get("profile"), "width": v.get("width"), "height": v.get("height"),
        "fps": round(fps_of(v), 3), "pix_fmt": v.get("pix_fmt"), "bit_depth": v.get("bits_per_raw_sample"),
        "color_primaries": v.get("color_primaries"), "color_transfer": trc, "color_space": v.get("color_space"),
        "hdr": trc in ("arib-std-b67", "smpte2084"),  # HLG / PQ (iPhone HDR is usually HLG + Dolby Vision)
        "dolby_vision": any("DOVI" in str(sd) or "Dolby" in str(sd) for sd in v.get("side_data_list", []) or []),
        "rotation": rot, "duration": float(info.get("format", {}).get("duration", 0) or 0),
        "audio": [s.get("codec_name") for s in info["streams"] if s.get("codec_type") == "audio"],
    }


def make_proxy(src: Path, kind: str, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    if kind == "photo":
        dst = dst_dir / (src.stem + "_proxy.jpg")
        # ImageMagick handles HEIC/RAW previews where delegates exist; -auto-orient bakes EXIF rotation.
        run(["convert", str(src) + "[0]", "-auto-orient", "-resize", "2048x2048>", "-quality", "90", str(dst)])
    else:
        dst = dst_dir / (src.stem + "_proxy.mp4")
        meta = video_meta(src)
        vf = "scale=-2:'min(1080,ih)':flags=lanczos"
        if meta["hdr"]:  # view proxies in SDR so grading decisions are not made on clipped HDR
            vf = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:desat=0,"
                  "zscale=t=bt709:m=bt709:r=tv,format=yuv420p," + vf)
        ffmpeg(["-i", str(src), "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(dst)])
    return dst


def cmd_import(src_dir: Path, film: Path) -> None:
    catalogue_path = film / "13_Project_Documentation" / "media_catalog.json"
    catalogue = json.loads(catalogue_path.read_text()) if catalogue_path.exists() else []
    known = {c["sha256"] for c in catalogue}
    files = sorted(p for p in src_dir.rglob("*") if p.is_file() and p.suffix.lower() in PHOTO_EXT | VIDEO_EXT)
    for src in files:
        kind = "photo" if src.suffix.lower() in PHOTO_EXT else "video"
        digest = sha256(src)
        if digest in known:
            print(f"skip (already ingested) {src.name}")
            continue
        dest_dir = film / ("01_Original_Photos" if kind == "photo" else "02_Original_Videos")
        dst = dest_dir / src.name
        n = 1
        while dst.exists():
            dst = dest_dir / f"{src.stem}_{n}{src.suffix}"
            n += 1
        shutil.copy2(src, dst)
        if sha256(dst) != digest:
            raise RuntimeError(f"copy verification failed for {src}")
        os.chmod(dst, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # read-only original
        entry = {"file": str(dst.relative_to(film)), "kind": kind, "sha256": digest, "bytes": dst.stat().st_size,
                 "source_name": src.name, "exif": exif(dst), "status": "ok"}
        try:
            if kind == "video":
                entry["video"] = video_meta(dst)
            entry["proxy"] = str(make_proxy(dst, kind, film / "03_Selected_Media" / "proxies").relative_to(film))
        except Exception as e:  # truncated / corrupt / unsupported: keep the original, flag it, carry on
            entry["status"] = "unreadable"
            entry["error"] = str(e)[:300]
            print(f"WARNING unreadable {kind} {dst.name}: kept and flagged, no proxy ({e})")
        catalogue.append(entry)
        known.add(digest)
        if entry["status"] == "ok":
            print(f"ingested {kind:5s} {dst.name}")
    write_json(catalogue_path, catalogue)
    print(f"catalogue: {len(catalogue)} items -> {catalogue_path}")


def cmd_verify(film: Path) -> int:
    catalogue = json.loads((film / "13_Project_Documentation" / "media_catalog.json").read_text())
    bad = [c["file"] for c in catalogue if not (film / c["file"]).exists() or sha256(film / c["file"]) != c["sha256"]]
    print(f"verified {len(catalogue) - len(bad)}/{len(catalogue)} originals intact")
    for b in bad:
        print("  MISMATCH or MISSING:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["import", "verify"])
    ap.add_argument("src", nargs="?")
    ap.add_argument("--film", default=str(FILM))
    a = ap.parse_args()
    if a.command == "import":
        cmd_import(Path(a.src), Path(a.film))
    else:
        sys.exit(cmd_verify(Path(a.film)))
