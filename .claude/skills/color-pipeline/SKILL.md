---
name: color-pipeline
description: Colour management and grading for the film. Use when footage comes from phones (HLG/Dolby Vision/PQ HDR), mixed cameras, photos, CGI or AI sources; when building or applying a look; when matching shots; protecting skin tones; adding grain/film texture; or preparing LUTs and stills for DaVinci Resolve.
---

# Colour pipeline

## 1. Normalise sources (before any creative grade)
- Check `media_catalog.json` -> `video.color_transfer`: `arib-std-b67` (HLG, iPhone default since 12),
  `smpte2084` (PQ/HDR10, Dolby Vision base layer), `bt709` (SDR). Photos: sRGB or Display P3 (HEIC).
- HDR -> SDR Rec.709: `$PY studio/lib/grade.py hdr2sdr in.mov out.mov` (default `--tonemap mobius --npl 100`).
  Measured on a known round trip: mobius/100 kept brightness within 2% of the SDR intent (25 dB PSNR);
  hable/203 (a common internet recipe) came out at half brightness. Hable can still suit shots with
  extreme highlights (night neon, sun): compare per scene on a contact sheet with the first real clips.
  Saturation drops ~10% through BT.2020 -> 709 conversion; restore it in the balance pass.
  Never let HLG play untagged as Rec.709: it looks flat and washed out (pipeline_test/08_hdr_to_sdr.jpg).
- Display P3 photos: convert to Rec.709 with ImageMagick/OpenImageIO colour management before
  animating, or saturated reds (taxis, neon, lanterns) will clip or shift.
- Generating SDR test HLG with zscale requires `min=gbr` on RGB input (learned in testing).

## 2. Balance and match
- Per shot: exposure, white balance, contrast, then match shots within each scene to a hero shot.
- Use waveform/vectorscope numerically: FFmpeg `signalstats`, or OpenCV histograms on frame grabs.
- Skin tones sit near the skin-tone line on the vectorscope (~123 degrees on a Rec.709 vectorscope).
  Check the client's skin under every look; keep texture (no smoothing).

## 3. Look development
```bash
$PY studio/lib/grade.py look --out 11_Color_Grading/luts/LOOK_name_v001.cube --contrast 1.12 --warm 0.035 --split 0.05 --sat 0.92
$PY studio/lib/grade.py apply cut.mov cut_graded.mov --lut 11_Color_Grading/luts/LOOK_name_v001.cube --grain 0.2 --vignette 0.1
$PY studio/lib/grade.py still frame.png frame_look.png --lut ...       # quick look comparisons
```
- Build 2-3 look candidates on the same 6-8 reference frames (day street, night neon, interior,
  close-up of the client, skyline, river). Present them as a still grid; the Creative Director and the
  client choose. Looks are motivated by the story, not by a trend.
- Unify texture last: one grain structure over everything (real, CGI, AI), optional halation for
  night practicals, gentle vignette only where it helps the eye.

## 4. Resolve hand-off (optional, on the client's machine)
.cube LUTs load in Resolve (Project Settings > Color Management > Lookup Tables). Export the edit with
`timeline.py export` (FCPXML/EDL/OTIO) and relink to the original media. For a scene-referred finish,
use DaVinci Wide Gamut / ACES there; this CPU pipeline is display-referred Rec.709.

## 5. Delivery
SDR Rec.709 with bt709 tags (all deliver.py profiles). HDR delivery only if requested AND reviewable on
an HDR reference display, which this environment cannot provide.
