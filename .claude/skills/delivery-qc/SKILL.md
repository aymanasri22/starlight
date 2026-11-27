---
name: delivery-qc
description: Final delivery and quality control for the film: master formats, platform encodes (4K HEVC/H.264, 1080p, 9:16, 1:1), technical QC (fps, resolution, colour tags, loudness, true peak, sync, black/frozen frames, VMAF), artistic QC checklist, and how deliverables leave the container. Use before sending any review or final file to the client.
---

# Delivery and QC

## Masters and encodes (`studio/lib/deliver.py --list`)
| Profile | Use |
|---|---|
| `master_prores_hq` | Archive master, ProRes 422 HQ 10-bit, PCM 24-bit |
| `master_dnxhr_hqx` | Avid/Resolve interchange master |
| `uhd_h265_10bit` | 4K HEVC Main10 (YouTube/Vimeo/TV), hvc1-tagged for Apple players |
| `uhd_h264` | 4K H.264 maximum compatibility |
| `hd_h264` | 1080p review/sharing |
| `vertical_9x16_h264`, `square_1x1_h264` | Social cut-downs (centre crop: reframe real shots in the edit) |

4K only when the sources honestly support it (most phone video and photos do at modest crops; check
each shot). Never upscale or interpolate blindly; note any shot that was upscaled and how.
Frame rate: 24 fps by default; keep 30/60 only if the film is conceived for it.

## Technical QC (every deliverable)
```bash
$PY studio/lib/qc.py check out.mp4 --fps 24 --size 3840x2160 --lufs -14 --tp -1 --json qc.json
python3 .claude/skills/ffmpeg-skill/scripts/check.py out.mp4 --platform youtube     # platform spec table
ffmpeg -i out.mp4 -i master.mov -lavfi "[0:v]setpts=PTS-STARTPTS[a];[1:v]format=yuv420p,setpts=PTS-STARTPTS[b];[a][b]libvmaf=n_threads=4" -f null -
$PY studio/lib/qc.py sheet out.mp4 --out sheet.jpg      # then LOOK at it
$PY studio/lib/ingest.py verify                          # originals untouched
```
VMAF >= 95 expected for high-bitrate deliveries; < 93 needs a look.

## Artistic QC checklist
- Story: does every shot earn its place? Pacing at the start and end?
- Identity: every shot with the client passed the gate AND side-by-side review; client approved.
- Continuity: wardrobe, light, weather, screen direction; no flash frames, no unintended jump cuts.
- AI/VFX artefacts: hands, faces, edges, flicker, morphing, signage. CGI shadows and grain match.
- Text: spelling in English and Chinese, safe areas per platform, credits complete; OSM/CC-BY credits
  present; music licence covers the platforms.
- Sound: sync, no clicks or dropouts, loudness on target, listened on headphones and phone speaker.

## Getting files out (the container is ephemeral)
- Small files: send to the client in the session (SendUserFile).
- Large masters: upload to the client's Google Drive via the connector, or let the client download.
- Never commit media to git (public repo). Keep the editable project (edit JSON, OTIO/FCPXML, LUTs,
  Blender/Remotion sources) in git.
