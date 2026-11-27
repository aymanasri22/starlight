---
name: studio-pipeline
description: Technical reference for this repository's film studio. Use whenever working on the Shanghai film (or any film in this repo) to know which tools exist, where files go, how to run each stage (ingest, photo motion, CGI, motion graphics, edit, grade, sound, delivery, QC), what renders cost in time on this CPU-only machine, and how to rebuild the environment in a fresh container.
---

# Studio pipeline: tools, paths, commands

Run Python tools with the studio venv: `PY=/opt/studio/venv/bin/python`. Every tool is a CLI with `--help`.
If `/opt/studio` is missing (fresh container), run `bash studio/bootstrap.sh` first (about 1-2 min).

## Environment (verified 2026-11-27)
- 4 CPU threads (Xeon 2.1 GHz), 15 GB RAM, **no GPU**, ~60 GB free disk. Ephemeral container: anything not
  committed or exported is lost when the session ends. Personal media is never committed (public repo).
- FFmpeg 9.0.2 static (BtbN, GPL: x264, x265 10-bit, SVT-AV1, ProRes, DNxHR, zscale, libplacebo, vid.stab,
  rubberband, libvmaf, libass) at `/usr/local/bin/ffmpeg`; Ubuntu FFmpeg 6.1 remains at `/usr/bin/ffmpeg`.
- Blender 5.2.5 LTS (`blender`), Cycles CPU + OIDN; EEVEE via software OpenGL (slow, for previs).
- Python 3.12 venv: OpenCV 5.1 (contrib), PyAV, MoviePy 2, PySceneDetect, OpenTimelineIO (+EDL/FCPXML/FCP7
  adapters), colour-science, OpenColorIO 2.6, OpenImageIO 3.2, librosa, pyloudnorm, pedalboard,
  onnxruntime, rembg, fal-client, replicate.
- Node 22 + Remotion 4.0.547 project in `Shanghai_Film/07_Motion_Graphics/remotion/` (local Chromium).
- Local models (`/opt/studio/models`): YuNet + SFace (faces/identity), Depth Anything V2 Small (depth),
  BiRefNet-portrait (mattes, auto-downloads on first use, ~1 GB).
- exiftool, mediainfo, sox, ImageMagick 6, Noto CJK fonts (SC/TC/JP/KR), Inter, JetBrains Mono.

## Stage commands (`studio/lib/`)
| Stage | Command |
|---|---|
| Ingest (copy, hash, lock, catalogue, proxies) | `$PY studio/lib/ingest.py import <dir>` / `verify` |
| Contact sheet | `$PY studio/lib/qc.py sheet <video> --out sheet.jpg` then Read the image |
| Depth + 2.5D move | `$PY studio/lib/depth_parallax.py move <photo> --out shot.mov --move push|truck|crane|orbit --strength 0.04` |
| Person matte (still) | `$PY studio/lib/matte.py <img> --out cut.png --refine` |
| Identity gate | `$PY studio/lib/identity.py enroll <refs...> --out ref.npz`; `check ref.npz <media...> --sheet s.jpg` |
| CC0 HDRI / plates / OSM | `$PY studio/lib/assets.py hdri <id>`; `plate <hdr> --yaw --pitch --fov`; `osm-buildings --bbox S,W,N,E` |
| CGI integration | `blender -b --factory-startup --python studio/blender/integrate_cgi.py -- --hdri X.hdr --out fg.png --plate-out bg.png` |
| 3D city / map basis | `blender -b --factory-startup --python studio/blender/osm_city.py -- --osm lujiazui.json --out city.png` |
| Titles / graphics | `cd Shanghai_Film/07_Motion_Graphics/remotion && npx remotion render src/index.ts <Comp> out/x.mov --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le` |
| Edit render + timeline export | `$PY studio/lib/timeline.py render edit.json --out cut.mov`; `export edit.json --out-dir 10_Edit_Timeline/` |
| HDR phone footage -> Rec.709 | `$PY studio/lib/grade.py hdr2sdr in.mov out.mov` |
| Look LUT / apply | `$PY studio/lib/grade.py look --out look.cube`; `apply in.mov out.mov --lut look.cube --grain 0.2` |
| SFX / mix / master | `$PY studio/lib/audio.py sfx riser --out r.wav`; `mix a.wav@-6@0 b.wav@-3@2.5 --out mix.wav`; `master mix.wav out.wav --lufs -14` |
| Delivery | `$PY studio/lib/deliver.py master.mov --profile hd_h264|uhd_h265_10bit|uhd_h264|vertical_9x16_h264|master_prores_hq|master_dnxhr_hqx` |
| QC | `$PY studio/lib/qc.py check out.mp4 --fps 24 --size 1920x1080 --lufs -14 --tp -1` |
| Precise FFmpeg ops | vendored `ffmpeg-skill` (`.claude/skills/ffmpeg-skill/scripts/*.py`) |
| Full self-test | `$PY studio/tests/run_pipeline_test.py` (results in `13_Project_Documentation/pipeline_test/`) |

## Measured costs on this machine (pipeline test)
See `Shanghai_Film/13_Project_Documentation/pipeline_test/RESULTS.md` for the latest numbers. Rules of thumb:
- Photo parallax 1080p: ~0.23 s/frame (a 5 s shot renders in ~30 s); depth map ~1.3 s per photo.
- Cycles 720p at 64 spp (simple scene): ~45 s/frame. 1080p at 128 spp: expect several minutes per frame,
  so a 5 s CGI shot can take many hours. Prefer stills + parallax, EEVEE previs, short CGI inserts, or
  cloud/GPU rendering for heavy shots.
- Remotion 1080p graphics with alpha: ~8 frames/s. Edit render (4 conformed clips, ramp, dissolve, 11 s
  1080p ProRes): ~30 s. BiRefNet matte: ~38 s per image.
- Encodes for 11 s of 1080p24: H.264 1080p ~26 s (2.3x slower than real time); **4K HEVC 10-bit slow
  ~350 s (about 32x slower than real time)**. Run long encodes in the background; use `--preset medium`
  for drafts.

## File conventions
- Shot IDs from SHOT_LIST.md everywhere: `SH040_parallax_v003.mov`. Version up, never overwrite a reviewed file.
- Masters: ProRes 422 HQ 10-bit, Rec.709 tags, 24 fps, PCM 48 kHz/24-bit. Graphics with alpha: ProRes 4444.
- Originals in 01/02 are read-only and hash-verified. Never write into them; never commit media.
- Large outputs leave the container through Google Drive (connector) or as files sent to the user.
