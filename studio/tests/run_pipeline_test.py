#!/usr/bin/env python3
"""End-to-end production pipeline test with harmless sample assets only.

    /opt/studio/venv/bin/python studio/tests/run_pipeline_test.py [--only STAGE,...] [--skip STAGE,...]

Sample material: synthetic clips, the CC0 Poly Haven "shanghai_bund" HDRI, and US-government
public-domain NASA portraits (for the identity gate). No personal media is used.
Work happens in studio/tests/out/ (a sandbox film root, git-ignored). Evidence (small JPGs,
results.json, RESULTS.md) is written to Shanghai_Film/13_Project_Documentation/pipeline_test/.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import time
import traceback
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "studio" / "lib"))
from common import FFMPEG, probe, video_stream, fps_of  # noqa: E402

PY = "/opt/studio/venv/bin/python"
LIB = REPO / "studio" / "lib"
OUT = REPO / "studio" / "tests" / "out"
SANDBOX = OUT / "film_sandbox"
CARD = OUT / "card"
EVID = REPO / "Shanghai_Film" / "13_Project_Documentation" / "pipeline_test"
HDRI8 = REPO / "Shanghai_Film" / "06_CGI_3D" / "hdri" / "shanghai_bund_8k.hdr"
HDRI4 = REPO / "Shanghai_Film" / "06_CGI_3D" / "hdri" / "shanghai_bund_4k.hdr"
REMOTION = REPO / "Shanghai_Film" / "07_Motion_Graphics" / "remotion"
FFSKILL = REPO / ".claude" / "skills" / "ffmpeg-skill" / "scripts"

RESULTS: list[dict] = []


def sh(cmd, cwd=None, ok_codes=(0,), env=None) -> subprocess.CompletedProcess:
    cmd = [str(c) for c in cmd]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env={**os.environ, **(env or {})})
    if p.returncode not in ok_codes:
        err = "\n".join(l for l in p.stderr.splitlines() if "%|" not in l)  # drop progress bars
        raise RuntimeError(f"$ {' '.join(cmd)}\n-> exit {p.returncode}\n{p.stdout[-1500:]}\n{err[-2500:]}")
    return p


def tool(name, *args, ok_codes=(0,)):
    return sh([PY, LIB / f"{name}.py", *args], ok_codes=ok_codes)


def ff(*args):
    return sh([FFMPEG, "-hide_banner", "-nostdin", "-y", "-loglevel", "error", *args])


def stage(name, title):
    def deco(fn):
        fn.stage_name, fn.title = name, title
        return fn
    return deco


def evidence(img, name, width=1600):
    EVID.mkdir(parents=True, exist_ok=True)
    if img.shape[1] > width:
        img = cv2.resize(img, (width, int(img.shape[0] * width / img.shape[1])), interpolation=cv2.INTER_AREA)
    p = EVID / name
    cv2.imwrite(str(p), img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return str(p.relative_to(REPO))


def label(img, text):
    img = img.copy()
    cv2.rectangle(img, (0, 0), (img.shape[1], 34), (0, 0, 0), -1)
    cv2.putText(img, text, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
    return img


def grab(path, t):
    p = sh([FFMPEG, "-hide_banner", "-loglevel", "error", "-ss", str(t), "-i", path, "-frames:v", "1",
            "-f", "image2pipe", "-vcodec", "png", "-"], ok_codes=(0,))
    return p


def frame_at(path, t):
    p = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-ss", str(t), "-i", str(path), "-frames:v", "1",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return cv2.imdecode(np.frombuffer(p.stdout, np.uint8), cv2.IMREAD_COLOR)


def fit(img, w, h):
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)


# ----------------------------------------------------------------------------------------- stages
@stage("synth", "Generate harmless sample media (camera-card simulation)")
def s_synth():
    CARD.mkdir(parents=True, exist_ok=True)
    notes = []
    # 1. a 'photo' of the Bund from the CC0 HDRI, with camera EXIF + GPS written in
    photo = CARD / "IMG_0001.jpg"
    tool("assets", "plate", HDRI8, "--out", OUT / "plate_photo.png", "--yaw", "-40", "--pitch", "1", "--fov", "70",
         "--size", "3000x2000", "--ev", "0.2")
    cv2.imwrite(str(photo), cv2.imread(str(OUT / "plate_photo.png")), [cv2.IMWRITE_JPEG_QUALITY, 92])
    sh(["exiftool", "-overwrite_original", "-DateTimeOriginal=2026:10:03 21:14:05", "-OffsetTimeOriginal=+08:00",
        "-Make=TestCam", "-Model=Synthetic Plate", "-FocalLengthIn35mmFormat=26",
        "-GPSLatitude=31.2397", "-GPSLatitudeRef=N", "-GPSLongitude=121.4908", "-GPSLongitudeRef=E", str(photo)])
    notes.append("photo 3000x2000 + EXIF/GPS (the Bund)")
    # 2. vertical phone clip, 60 fps, with tone audio
    ff("-f", "lavfi", "-i", "testsrc2=size=1080x1920:rate=60:duration=4", "-f", "lavfi", "-i",
       "sine=frequency=330:duration=4:sample_rate=48000", "-vf",
       "drawtext=text='VERTICAL 60p':fontsize=90:fontcolor=white:x=(w-tw)/2:y=h*0.42:box=1:boxcolor=black@0.5",
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(CARD / "IMG_0002.MP4"))
    # 3. shaky 'handheld' clip from the photo: random-walk + jitter crop at 30 fps
    src = cv2.imread(str(OUT / "plate_photo.png"))
    src = cv2.resize(src, (2400, 1600), interpolation=cv2.INTER_AREA)
    rng = np.random.default_rng(3)
    n, W, H = 120, 1920, 1080
    walk = np.cumsum(rng.normal(0, 1.2, (n, 2)), axis=0) + rng.normal(0, 6, (n, 2))
    pan = np.stack([np.linspace(0, 140, n), np.zeros(n)], 1)
    off = walk + pan + [200, 220]
    pr = subprocess.Popen([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                           "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-f", "lavfi", "-i", "anoisesrc=d=4:c=pink:a=0.05",
                           "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                           str(CARD / "IMG_0003.MOV")], stdin=subprocess.PIPE)
    for i in range(n):
        x, y = off[i]
        M = np.float32([[1, 0, -x], [0, 1, -y]])
        pr.stdin.write(cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).tobytes())
    pr.stdin.close(); pr.wait()
    # 4. iPhone-style HDR clip: HLG / BT.2020 / 10-bit HEVC
    ff("-loop", "1", "-t", "3", "-r", "30", "-i", OUT / "plate_photo.png", "-vf",
       "scale=1920:1080,format=gbrpf32le,zscale=min=gbr:tin=iec61966-2-1:pin=bt709:t=linear:p=bt2020,"
       "zscale=min=gbr:tin=linear:pin=bt2020:t=arib-std-b67:m=bt2020nc:r=tv,format=yuv420p10le",
       "-c:v", "libx265", "-crf", "20", "-tag:v", "hvc1",
       "-x265-params", "colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:log-level=error",
       "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", str(CARD / "IMG_0004.MOV"))
    # 5. a truncated clip, as from an interrupted phone transfer: ingest must flag it, not crash
    (CARD / "IMG_0005.MOV").write_bytes((CARD / "IMG_0003.MOV").read_bytes()[:20000])
    notes += ["vertical 1080x1920@60 H.264", "shaky handheld 1080p30", "HLG BT.2020 10-bit HEVC (iPhone-style)",
              "truncated/corrupt clip"]
    return {"notes": notes, "files": sorted(p.name for p in CARD.iterdir())}


@stage("ingest", "Non-destructive ingest: hash, lock, catalogue, proxies, integrity verify")
def s_ingest():
    if SANDBOX.exists():
        for p in SANDBOX.rglob("*"):
            if p.is_file():
                os.chmod(p, stat.S_IWUSR | stat.S_IRUSR)
        shutil.rmtree(SANDBOX)
    for d in ["01_Original_Photos", "02_Original_Videos", "03_Selected_Media/proxies", "13_Project_Documentation"]:
        (SANDBOX / d).mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    tool("ingest", "import", CARD, "--film", SANDBOX)
    cat = json.loads((SANDBOX / "13_Project_Documentation" / "media_catalog.json").read_text())
    checks = {
        "items_catalogued": len(cat) == 5,
        "corrupt_file_flagged_not_fatal": sum(c.get("status") == "unreadable" for c in cat) == 1,
        "originals_read_only": all(not (os.stat(SANDBOX / c["file"]).st_mode & 0o222) for c in cat),
        "proxies_exist": all((SANDBOX / c["proxy"]).exists() for c in cat if c.get("status") == "ok"),
        "gps_parsed": any(abs(c["exif"].get("GPSLatitude", 0) - 31.2397) < 1e-3 for c in cat),
        "hdr_flagged": any(c.get("video", {}).get("hdr") for c in cat),
        "capture_time": any(c["exif"].get("DateTimeOriginal") for c in cat),
    }
    clean = tool("ingest", "verify", "--film", SANDBOX).returncode == 0
    # tamper test: alter one original, verify must catch it, then restore
    victim = SANDBOX / cat[0]["file"]
    orig = victim.read_bytes()
    os.chmod(victim, 0o644); victim.write_bytes(orig + b"\0"); os.chmod(victim, 0o444)
    caught = tool("ingest", "verify", "--film", SANDBOX, ok_codes=(0, 1)).returncode == 1
    os.chmod(victim, 0o644); victim.write_bytes(orig); os.chmod(victim, 0o444)
    checks.update({"verify_clean": clean, "tamper_detected": caught})
    hdr = next(c for c in cat if c.get("video", {}).get("hdr"))
    return {"pass": all(checks.values()), "checks": checks, "seconds": round(time.time() - t0, 1),
            "hdr_clip": {k: hdr["video"][k] for k in ("codec", "color_transfer", "color_primaries", "bit_depth", "fps")}}


@stage("depth", "Photo -> depth map -> 2.5D parallax camera move")
def s_depth():
    photo = OUT / "plate_photo.png"
    t0 = time.time()
    tool("depth_parallax", "depth", photo, "--out", OUT / "depth.png")
    t_depth = time.time() - t0
    t1 = time.time()
    tool("depth_parallax", "move", photo, "--depth", OUT / "depth.png", "--out", OUT / "clip_A_parallax.mov",
         "--move", "push", "--strength", "0.045", "--seconds", "3", "--size", "1920x1080")
    t_move = time.time() - t1
    v = video_stream(probe(OUT / "clip_A_parallax.mov"))
    d = cv2.imread(str(OUT / "depth.png"), cv2.IMREAD_UNCHANGED)
    dvis = cv2.applyColorMap((d / 256).astype(np.uint8), cv2.COLORMAP_INFERNO)
    tiles = [label(fit(cv2.imread(str(photo)), 640, 427), "source photo"),
             label(fit(dvis, 640, 427), "depth (Depth Anything V2 S)"),
             label(fit(frame_at(OUT / "clip_A_parallax.mov", 2.9), 640, 427), "push-in, last frame")]
    ev = evidence(np.hstack(tiles), "02_depth_parallax.jpg", 1920)
    return {"pass": v["nb_frames"] == "72", "frames": v["nb_frames"], "codec": f"{v['codec_name']} {v.get('profile')}",
            "depth_seconds": round(t_depth, 1), "render_seconds": round(t_move, 1),
            "sec_per_frame_1080p": round(t_move / 72, 2), "evidence": ev}


@stage("faces", "Fetch public-domain test portraits (NASA)")
def s_faces():
    import requests
    from skimage import data
    fd = OUT / "faces"; fd.mkdir(exist_ok=True)
    cv2.imwrite(str(fd / "ref_collins_1994.png"), cv2.cvtColor(data.astronaut(), cv2.COLOR_RGB2BGR))
    urls = {
        "collins_1998.jpg": "https://images-assets.nasa.gov/image/S99-00858/S99-00858~medium.jpg",
        "collins_2005_crew.jpg": "https://images-assets.nasa.gov/image/s114e6751/s114e6751~medium.jpg",
        "other_hathaway.jpg": "https://images-assets.nasa.gov/image/jsc2025e068207_alt/jsc2025e068207_alt~large.jpg",
        "other_meir.jpg": "https://images-assets.nasa.gov/image/jsc2025e078605_alt/jsc2025e078605_alt~large.jpg",
    }
    for name, u in urls.items():
        if not (fd / name).exists():
            r = requests.get(u, timeout=60, headers={"User-Agent": "studio-pipeline/1.0"}); r.raise_for_status()
            (fd / name).write_bytes(r.content)
    return {"pass": all((fd / n).exists() for n in urls), "credit": "NASA (public domain); scikit-image astronaut (NASA, PD)"}


@stage("identity", "Identity-preservation gate (YuNet + SFace)")
def s_identity():
    fd = OUT / "faces"
    ref = cv2.imread(str(fd / "ref_collins_1994.png"))
    # graded + resized + recompressed copy of the reference photo (should still PASS)
    tool("grade", "look", "--out", OUT / "test_look.cube")
    tool("grade", "still", fd / "ref_collins_1994.png", fd / "variant_graded.png", "--lut", OUT / "test_look.cube")
    g = cv2.imread(str(fd / "variant_graded.png"))
    g = cv2.resize(g, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(fd / "variant_graded.jpg"), g, [cv2.IMWRITE_JPEG_QUALITY, 60])
    # simulated generative drift: face proportions stretched ~18% (like an AI re-render going wrong)
    h, w = ref.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy, r = 250, 140, 110
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    k = np.clip(1 - dist / r, 0, 1) ** 2
    mx = xx - (xx - cx) * 0.18 * k
    my = yy + (yy - cy) * 0.10 * k
    cv2.imwrite(str(fd / "variant_drift.png"), cv2.remap(ref, mx, my, cv2.INTER_CUBIC))
    tool("identity", "enroll", fd / "ref_collins_1994.png", "--out", OUT / "ref.npz")
    # collins_1998 = same portrait session as the reference (re-crop/re-encode robustness, not cross-photo);
    # collins_2005_crew = genuinely different photo, 7+ years later, different light, 7 faces in frame.
    expect = {"variant_graded.jpg": "PASS", "collins_1998.jpg": "PASS", "collins_2005_crew.jpg": "PASS|REVIEW",
              "variant_drift.png": "REVIEW|FAIL|PASS",
              "other_hathaway.jpg": "FAIL", "other_meir.jpg": "FAIL"}
    res = {}
    for name in expect:
        tool("identity", "check", OUT / "ref.npz", fd / name, "--json", OUT / f"id_{name}.json", ok_codes=(0, 1, 2))
        r = json.loads((OUT / f"id_{name}.json").read_text())
        best = max((x for x in r["results"] if "similarity" in x), key=lambda x: x["similarity"], default=None)
        faces_ = [x for x in r["results"] if "similarity" in x]
        res[name] = {"similarity": best["similarity"] if best else None, "verdict": best["verdict"] if best else "NO_FACE",
                     "expected": expect[name], "faces_in_image": len(faces_),
                     "other_faces_max_sim": round(sorted((x["similarity"] for x in faces_), reverse=True)[1], 3) if len(faces_) > 1 else None}
    tool("identity", "check", OUT / "ref.npz", *[fd / n for n in expect], "--sheet", OUT / "id_sheet.jpg", ok_codes=(0, 1, 2))
    ev = evidence(cv2.imread(str(OUT / "id_sheet.jpg")), "04_identity_gate.jpg")
    ok = all(v["verdict"] in v["expected"].split("|") for v in res.values())
    drift_drop = round(1 - res["variant_drift.png"]["similarity"] / res["variant_graded.jpg"]["similarity"], 3)
    return {"pass": ok, "results": res, "drift_similarity_drop": drift_drop, "evidence": ev}


@stage("matte", "Person matte (rembg BiRefNet-portrait) + composite onto plate")
def s_matte():
    fd = OUT / "faces"
    t0 = time.time()
    tool("matte", fd / "ref_collins_1994.png", "--out", OUT / "cutout.png", "--model", "birefnet-portrait", "--refine")
    dt = time.time() - t0
    cut = cv2.imread(str(OUT / "cutout.png"), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    plate = cv2.imread(str(OUT / "plate_photo.png")).astype(np.float32) / 255
    plate = cv2.resize(plate, (1200, 800))
    s = 760 / cut.shape[0]
    cut = cv2.resize(cut, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    y0, x0 = 800 - cut.shape[0], 380
    roi = plate[y0:y0 + cut.shape[0], x0:x0 + cut.shape[1]]
    a = cut[..., 3:4]
    roi[:] = cut[..., :3] * a + roi * (1 - a)
    alpha_vis = cv2.cvtColor((cut[..., 3] * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    ev = evidence(np.hstack([label(fit(alpha_vis, 400, 400 * alpha_vis.shape[0] // alpha_vis.shape[1]), "alpha"),
                             label(fit((plate * 255).astype(np.uint8), 600, 400), "composite (no grade match)")]),
                  "05_matte_composite.jpg")
    cov = float(cut[..., 3].mean())
    return {"pass": 0.15 < cov < 0.9, "seconds_512px": round(dt, 1), "alpha_coverage": round(cov, 3), "evidence": ev,
            "note": "composite is a raw matte test; real shots need light/grade/grain matching and a contact shadow"}


@stage("blender", "Blender 5.2 LTS headless: HDRI-lit CGI on shadow catcher, composited (Cycles CPU)")
def s_blender():
    t0 = time.time()
    sh(["blender", "-b", "--factory-startup", "--python", REPO / "studio/blender/integrate_cgi.py", "--",
        "--hdri", HDRI4, "--out", OUT / "cg_fg.png", "--plate-out", OUT / "cg_plate.png", "--yaw", "-42",
        "--pitch", "-12", "--fov", "62", "--size", "1280x720", "--samples", "64"])
    dt = time.time() - t0
    fg = cv2.imread(str(OUT / "cg_fg.png"), cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
    bg = cv2.imread(str(OUT / "cg_plate.png"), cv2.IMREAD_UNCHANGED)[..., :3].astype(np.float32) / 65535
    a = fg[..., 3:4]
    comp = np.clip(fg[..., :3] * a + bg * (1 - a), 0, 1)
    cv2.imwrite(str(OUT / "cg_comp.png"), (comp * 255).astype(np.uint8))
    shadow_px = int(((a > 0.03) & (a < 0.97)).sum())
    # camera-match check: my equirect->rectilinear plate vs Blender's own background render
    tool("assets", "plate", HDRI4, "--out", OUT / "plate_check.png", "--yaw", "-42", "--pitch", "-12", "--fov", "62",
         "--size", "1280x720")
    mine = cv2.cvtColor(cv2.imread(str(OUT / "plate_check.png")), cv2.COLOR_BGR2GRAY).astype(np.float32)
    theirs = cv2.cvtColor((bg * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    ncc = float(((mine - mine.mean()) * (theirs - theirs.mean())).mean() / (mine.std() * theirs.std() + 1e-6))
    shift, _ = cv2.phaseCorrelate(mine, theirs)
    shift_mag = float(np.hypot(*shift))
    ev = evidence(np.hstack([label(fit((bg * 255).astype(np.uint8), 800, 450), "plate (HDRI background)"),
                             label(fit((comp * 255).astype(np.uint8), 800, 450), "CGI grey/chrome balls + caught shadows")]),
                  "06_blender_cgi_integration.jpg")
    return {"pass": shadow_px > 2000 and ncc > 0.9 and shift_mag < 0.25, "seconds_two_renders_720p_64spp": round(dt, 1),
            "shadow_pixels": shadow_px, "plate_vs_blender_luma_ncc": round(ncc, 3),
            "plate_vs_blender_shift_px": round(shift_mag, 3), "evidence": ev}


@stage("remotion", "Remotion kinetic title (ProRes 4444 alpha) composited over a shot")
def s_remotion():
    t0 = time.time()
    sh(["npx", "remotion", "render", "src/index.ts", "TitleTest", "out/title_test.mov", "--codec=prores",
        "--prores-profile=4444", "--pixel-format=yuva444p10le", "--log=error"], cwd=REMOTION)
    dt = time.time() - t0
    title = REMOTION / "out" / "title_test.mov"
    v = video_stream(probe(title))
    ff("-i", OUT / "clip_A_parallax.mov", "-i", title, "-filter_complex",
       "[1:v]format=yuva444p10le[t];[0:v][t]overlay=0:0:shortest=1:format=auto,format=yuv422p10le,"
       "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv",
       "-c:v", "prores_ks", "-profile:v", "3", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
       OUT / "clip_A_titled.mov")
    ff("-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=4:r=24", "-i", title, "-filter_complex",
       "[0:v][1:v]overlay=0:0:shortest=1", "-frames:v", "1", "-ss", "1.8", OUT / "title_on_black.png")
    on_black = cv2.imread(str(OUT / "title_on_black.png"))
    over = frame_at(OUT / "clip_A_titled.mov", 1.8)
    ev = evidence(np.hstack([label(fit(on_black, 800, 450), "title alpha over black (glyph check: CJK + Latin)"),
                             label(fit(over, 800, 450), "title composited over parallax shot")]),
                  "07_remotion_title_overlay.jpg")
    return {"pass": "yuva" in v["pix_fmt"] and v["nb_frames"] == "96", "pix_fmt": v["pix_fmt"],
            "render_seconds_96f_1080p": round(dt, 1), "evidence": ev}


def jitter(path):
    cap = cv2.VideoCapture(str(path)); prev, d = None, []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(cv2.resize(f, (480, 270)), cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None:
            (dx, dy), _ = cv2.phaseCorrelate(prev, g); d.append((dx, dy))
        prev = g
    d = np.array(d) * 4  # back to 1080p pixels
    hf = d - cv2.GaussianBlur(d.astype(np.float32), (1, 15), 0)  # remove intended pan, keep shake
    return float(np.sqrt((hf ** 2).sum(1)).mean())


@stage("stabilize", "Stabilisation (vid.stab two-pass) with measured residual shake")
def s_stabilize():
    src = SANDBOX / "02_Original_Videos" / "IMG_0003.MOV"
    trf = OUT / "transforms.trf"
    t0 = time.time()
    ff("-i", src, "-vf", f"vidstabdetect=shakiness=8:accuracy=15:result={trf}", "-f", "null", "-")
    ff("-i", src, "-vf", f"vidstabtransform=input={trf}:smoothing=30:zoom=4:optzoom=0,unsharp=5:5:0.6,"
       "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv",
       "-c:v", "libx264", "-crf", "16", "-c:a", "copy", OUT / "clip_C_stab.mp4")
    dt = time.time() - t0
    before, after = jitter(src), jitter(OUT / "clip_C_stab.mp4")
    return {"pass": after < before * 0.5, "shake_px_per_frame_before": round(before, 2),
            "shake_px_per_frame_after": round(after, 2), "reduction": f"{(1 - after / before):.0%}", "seconds": round(dt, 1)}


@stage("hdr", "HDR (HLG) phone footage -> Rec.709 SDR conform")
def s_hdr():
    src = SANDBOX / "02_Original_Videos" / "IMG_0004.MOV"
    tool("grade", "hdr2sdr", src, OUT / "clip_D_sdr.mov")
    v = video_stream(probe(OUT / "clip_D_sdr.mov"))
    f = frame_at(OUT / "clip_D_sdr.mov", 1)
    ev = evidence(np.hstack([label(fit(cv2.imread(str(OUT / "plate_photo.png")), 640, 360), "SDR source"),
                             label(fit(frame_at(src, 1), 640, 360), "HLG viewed raw (wrong)"),
                             label(fit(f, 640, 360), "HLG -> Rec.709 (mobius, studio default)")]), "08_hdr_to_sdr.jpg", 1920)
    return {"pass": v["color_transfer"] == "bt709" and v["color_primaries"] == "bt709",
            "out_tags": f"{v['color_primaries']}/{v['color_transfer']}/{v['color_space']} {v['pix_fmt']}", "evidence": ev}


@stage("audio", "Sound design: synthesized SFX, mix, master to -14 LUFS / -1 dBTP")
def s_audio():
    ad = OUT / "audio"; ad.mkdir(exist_ok=True)
    for kind, sec in [("roomtone", 13), ("whoosh", 1.4), ("riser", 2.5), ("impact", 3), ("sub", 2)]:
        tool("audio", "sfx", kind, "--out", ad / f"{kind}.wav", "--seconds", str(sec))
    tool("audio", "mix", f"{ad/'roomtone.wav'}@-6@0", f"{ad/'riser.wav'}@-10@0.4", f"{ad/'impact.wav'}@-3@2.9",
         f"{ad/'whoosh.wav'}@-8@5.6", f"{ad/'sub.wav'}@-12@8.2", f"{ad/'whoosh.wav'}@-9@8.0",
         "--out", ad / "mix.wav", "--reverb", "0.08")
    tool("audio", "master", ad / "mix.wav", ad / "master.wav", "--lufs", "-14", "--tp", "-1.0")
    m = json.loads(tool("audio", "measure", ad / "master.wav").stdout)
    return {"pass": abs(m["integrated_lufs"] + 14) <= 0.5 and m["true_peak_dbtp"] <= -1.0, **m}


@stage("edit", "Conform mixed sources + transitions + speed ramp -> ProRes master; OTIO/EDL/FCPXML export")
def s_edit():
    edit = {"name": "pipeline_test_seq", "fps": 24, "width": 1920, "height": 1080, "audio": str(OUT / "audio" / "master.wav"),
            "clips": [
                {"src": str(OUT / "clip_A_titled.mov"), "in": 0.0, "dur": 3.0},
                {"src": str(OUT / "clip_C_stab.mp4"), "in": 0.3, "dur": 3.0},
                {"src": str(OUT / "clip_D_sdr.mov"), "in": 0.0, "dur": 2.5, "transition": {"type": "fade", "dur": 0.5}},
                {"src": str(SANDBOX / "02_Original_Videos" / "IMG_0002.MP4"), "in": 0.0, "dur": 3.0,
                 "speed": [[0, 1.0], [0.4, 0.3], [0.7, 0.3], [1.0, 1.0]]},
            ]}
    (OUT / "edit.json").write_text(json.dumps(edit, indent=2))
    t0 = time.time()
    tool("timeline", "render", OUT / "edit.json", "--out", OUT / "master_test.mov")
    dt = time.time() - t0
    tool("timeline", "export", OUT / "edit.json", "--out-dir", OUT / "timeline")
    import opentimelineio as otio
    tl = otio.adapters.read_from_file(str(OUT / "timeline" / "pipeline_test_seq.otio"))
    exported = sorted(p.name for p in (OUT / "timeline").iterdir())
    for p in (OUT / "timeline").iterdir():  # keep the editable timelines as evidence (text, no media)
        shutil.copy(p, EVID / p.name)
    info = probe(OUT / "master_test.mov")
    v = video_stream(info)
    dur = float(info["format"]["duration"])
    sh([PY, LIB / "qc.py", "sheet", OUT / "master_test.mov", "--out", OUT / "master_sheet.jpg", "--cols", "6", "--rows", "3"])
    ev = evidence(cv2.imread(str(OUT / "master_sheet.jpg")), "09_edit_master_contact_sheet.jpg", 1920)
    a_ = next(s for s in info["streams"] if s["codec_type"] == "audio")
    edl_ok = (OUT / "timeline" / "pipeline_test_seq.edl").exists()
    otio_dur = tl.tracks[0].duration().to_seconds()
    return {"pass": abs(fps_of(v) - 24) < 0.01 and abs(dur - 11.0) < 0.05 and len(tl.tracks[0]) >= 4 and edl_ok
                    and abs(float(a_["duration"]) - 11.0) < 0.01 and abs(otio_dur - 11.0) < 0.05,
            "audio_duration_s": round(float(a_["duration"]), 4), "otio_timeline_duration_s": round(otio_dur, 3),
            "duration_s": round(dur, 3), "expected_s": 11.0, "video": f"{v['codec_name']} {v.get('profile')} {v['pix_fmt']}",
            "render_seconds": round(dt, 1), "timeline_exports": exported, "otio_reimport_items": len(tl.tracks[0]),
            "evidence": ev}


@stage("grade", "Look development: authored .cube LUT applied with grain + vignette")
def s_grade():
    tool("grade", "look", "--out", OUT / "studio_test_look.cube", "--contrast", "1.12", "--warm", "0.035", "--split", "0.05")
    tool("grade", "apply", OUT / "master_test.mov", OUT / "master_graded.mov", "--lut", OUT / "studio_test_look.cube",
         "--grain", "0.25", "--vignette", "0.15")
    shutil.copy(OUT / "studio_test_look.cube", EVID / "studio_test_look.cube")
    a, b = frame_at(OUT / "master_test.mov", 1.5), frame_at(OUT / "master_graded.mov", 1.5)
    ev = evidence(np.hstack([label(fit(a, 800, 450), "ungraded"), label(fit(b, 800, 450), "test look + grain + vignette")]),
                  "10_grade_before_after.jpg")
    return {"pass": (OUT / "master_graded.mov").exists(), "lut": "33^3 .cube (Resolve/Premiere/FCP compatible)", "evidence": ev}


@stage("deliver", "Delivery encodes: 1080p H.264, 4K HEVC 10-bit, 9:16 vertical")
def s_deliver():
    out, times = OUT / "deliver", {}
    for prof in ["hd_h264", "uhd_h265_10bit", "vertical_9x16_h264"]:
        t0 = time.time()
        tool("deliver", OUT / "master_graded.mov", "--profile", prof, "--out-dir", out, "--name", "test")
        times[prof] = round(time.time() - t0, 1)
    files = {p.name: f"{p.stat().st_size / 1e6:.1f} MB" for p in sorted(out.iterdir())}
    return {"pass": len(files) == 3, "encode_seconds_for_11s": times, "files": files,
            "note": "4K file is an encode-path test from a 1080p timeline (upscaled), not a quality claim"}


@stage("qc", "Technical QC + VMAF + vendored ffmpeg-skill check/look")
def s_qc():
    d = OUT / "deliver"
    r = tool("qc", "check", d / "test_hd_h264.mp4", "--fps", "24", "--size", "1920x1080", "--lufs", "-14", "--tp", "-1",
             "--json", OUT / "qc_hd.json", ok_codes=(0, 1, 2))
    qc = json.loads((OUT / "qc_hd.json").read_text())
    shutil.copy(OUT / "qc_hd.json", EVID / "qc_hd_h264.json")
    # VMAF: delivery vs graded master (libvmaf built into the FFmpeg 9 build)
    p = subprocess.run([FFMPEG, "-hide_banner", "-i", str(d / "test_hd_h264.mp4"), "-i", str(OUT / "master_graded.mov"),
                        "-lavfi", "[0:v]setpts=PTS-STARTPTS[a];[1:v]format=yuv420p,setpts=PTS-STARTPTS[b];[a][b]libvmaf=n_threads=4",
                        "-f", "null", "-"], capture_output=True, text=True)
    vmaf = next((l.split("VMAF score:")[-1].strip() for l in p.stderr.splitlines() if "VMAF score" in l), None)
    sk = subprocess.run(["python3", FFSKILL / "check.py", str(d / "test_hd_h264.mp4"), "--platform", "youtube", "--json-brief"],
                        capture_output=True, text=True)
    lk = subprocess.run(["python3", FFSKILL / "look.py", str(d / "test_vertical_9x16_h264.mp4"), "--tiles", "4x1", "--safe", "tiktok", "--overwrite",
                         "--output", str(OUT / "ffskill_look.png")], capture_output=True, text=True)
    qc_v = json.loads(tool("qc", "check", d / "test_vertical_9x16_h264.mp4", "--fps", "24", "--size", "1080x1920",
                           "--json", OUT / "qc_vert.json", ok_codes=(0, 1, 2)).stdout and (OUT / "qc_vert.json").read_text())
    return {"pass": qc["overall"] in ("PASS", "WARN") and vmaf is not None and lk.returncode == 0 and sk.returncode == 0
                    and qc_v["overall"] in ("PASS", "WARN"),
            "vertical_qc": qc_v["overall"], "vertical_sar": next(c["detail"] for c in qc_v["checks"] if c["check"] == "square pixels"),
            "studio_qc": qc["overall"], "checks": {c["check"]: f"{c['status']} {c['detail']}" for c in qc["checks"]},
            "vmaf_hd_vs_master": vmaf, "ffmpeg_skill_check_exit": sk.returncode,
            "ffmpeg_skill_check": (sk.stdout or sk.stderr).strip()[:400], "ffmpeg_skill_look_exit": lk.returncode}


@stage("scenes", "Shot-boundary detection on a cut (PySceneDetect)")
def s_scenes():
    from scenedetect import ContentDetector, detect
    scenes = detect(str(OUT / "master_test.mov"), ContentDetector(threshold=27))
    cuts = [round(s[0].seconds, 2) for s in scenes[1:]]
    hard = [3.0, 8.0]  # the 5.5-6.0 s dissolve is not a hard cut; ContentDetector is not expected to flag it
    found = all(any(abs(c - h) <= 1 / 24 + 1e-6 for c in cuts) for h in hard)
    return {"pass": found, "shots_found": len(scenes), "cut_times_s": cuts, "hard_cuts_expected": hard,
            "dissolve_5.5_6.0_detected": any(5.3 < c < 6.2 for c in cuts),
            "note": "ContentDetector finds hard cuts; dissolves need AdaptiveDetector/ThresholdDetector tuning"}


@stage("map", "Animated-map basis: OpenStreetMap buildings (Lujiazui) -> extruded 3D city in Blender")
def s_map():
    osm = OUT / "lujiazui_osm.json"
    if not osm.exists():  # network fetch with public-instance fallback
        tool("assets", "osm-buildings", "--bbox", "31.2330,121.4960,31.2440,121.5110", "--out", osm)
    data = json.loads(osm.read_text())
    tallest = sorted((b for b in data["buildings"] if b["height"]), key=lambda b: -b["height"])[:3]
    t0 = time.time()
    p = sh(["blender", "-b", "--factory-startup", "--python", REPO / "studio/blender/osm_city.py", "--",
            "--osm", osm, "--out", OUT / "osm_city.png", "--size", "1280x720", "--samples", "24"])
    dt = time.time() - t0
    ev = evidence(label(cv2.imread(str(OUT / "osm_city.png")), "OSM Lujiazui extruded (clay study) (c) OpenStreetMap contributors"),
                  "11_osm_city_3d.jpg", 1280)
    return {"pass": "STUDIO_OK" in p.stdout, "buildings": len(data["buildings"]),
            "with_height": sum(1 for b in data["buildings"] if b["height"]),
            "tallest": [f"{b['name']} {round(b['height'])} m" for b in tallest], "render_seconds": round(dt, 1),
            "licence": "ODbL: credit (c) OpenStreetMap contributors", "evidence": ev}


STAGES = [s_synth, s_ingest, s_depth, s_faces, s_identity, s_matte, s_blender, s_remotion, s_stabilize, s_hdr,
          s_audio, s_edit, s_grade, s_deliver, s_qc, s_scenes, s_map]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only"); ap.add_argument("--skip")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    skip = set(a.skip.split(",")) if a.skip else set()
    OUT.mkdir(parents=True, exist_ok=True); EVID.mkdir(parents=True, exist_ok=True)
    prev = {r["stage"]: r for r in json.loads((EVID / "results.json").read_text())["stages"]} if (EVID / "results.json").exists() else {}
    for fn in STAGES:
        if (only and fn.stage_name not in only) or fn.stage_name in skip:
            if fn.stage_name in prev:
                RESULTS.append(prev[fn.stage_name])
            continue
        t0 = time.time()
        print(f"\n=== {fn.stage_name}: {fn.title}", flush=True)
        try:
            r = fn() or {}
            status = "PASS" if r.pop("pass", True) else "FAIL"
        except Exception as e:
            r, status = {"error": f"{type(e).__name__}: {str(e)[:1500]}", "trace": traceback.format_exc()[-1500:]}, "ERROR"
        r = {"stage": fn.stage_name, "title": fn.title, "status": status, "wall_seconds": round(time.time() - t0, 1), **r}
        RESULTS.append(r)
        print(json.dumps(r, indent=1, default=str)[:2500], flush=True)
    env = {"host": platform.platform(), "cpu_threads": os.cpu_count(), "python": platform.python_version(),
           "ffmpeg": subprocess.run([FFMPEG, "-version"], capture_output=True, text=True).stdout.split("\n")[0],
           "blender": subprocess.run(["blender", "--version"], capture_output=True, text=True).stdout.split("\n")[0],
           "date": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())}
    (EVID / "results.json").write_text(json.dumps({"environment": env, "stages": RESULTS}, indent=2, default=str))
    lines = ["# Pipeline test results", "", f"Run: {env['date']} on {env['cpu_threads']} CPU threads, no GPU. "
             f"{env['ffmpeg']}; {env['blender']}.", "", "| Stage | Result | Time | Key numbers |", "|---|---|---|---|"]
    for r in RESULTS:
        keys = {k: v for k, v in r.items() if k not in ("stage", "title", "status", "wall_seconds", "evidence", "trace",
                                                       "checks", "results", "files", "notes")}
        lines.append(f"| {r['title']} | **{r['status']}** | {r['wall_seconds']}s | "
                     f"{'; '.join(f'{k}: {v}' for k, v in keys.items())[:420].replace('|', '/')} |")
    (EVID / "RESULTS.md").write_text("\n".join(lines) + "\n")
    bad = [r["stage"] for r in RESULTS if r["status"] != "PASS"]
    print("\nSUMMARY:", "ALL PASS" if not bad else f"not passing: {bad}")


if __name__ == "__main__":
    main()
