---
name: photo-animation
description: Turn still photographs into cinematic motion. Use when a shot in the film comes from a photo; covers choosing the technique (subtle push, 2.5D depth parallax, layered parallax with mattes, particles/atmosphere, CGI additions, AI image-to-video), the local tools, strengths that avoid artefacts, and finishing so stills cut with real video.
---

# Photo animation

Stills are memories. Move them the way memory moves: slowly, with depth, never like a slideshow.

## Choose the technique (cheapest that serves the beat)
1. **Static hold / slow push (2D)**: strong compositions, faces in close-up (no depth artefacts on faces).
2. **2.5D depth parallax** (`depth_parallax.py`): landscapes, streets, skylines, interiors with clear depth.
3. **Layered parallax**: matte the subject (`matte.py`), fill the background behind it (inpaint or AI fill),
   move layers separately in Blender or a compositor. Best quality for a person against the city.
4. **Atmosphere**: add real-feeling motion (rain, haze, neon flicker, river light, drifting clouds) as
   composited elements; keep it subtle and motivated by the place and weather in the photo.
5. **AI image-to-video** (cloud, needs approval): when real motion is required (people walking, water,
   traffic). Follow `ai-generation` and, if the client is in frame, `identity-preservation`.

## Local 2.5D parallax
```bash
$PY studio/lib/depth_parallax.py depth photo.jpg --out photo_depth.png        # inspect the depth map first
$PY studio/lib/depth_parallax.py move photo.jpg --depth photo_depth.png --out SH040_v001.mov \
    --move push --strength 0.04 --seconds 5 --size 1920x1080 --codec prores
```
- Moves: `push` (dolly in), `truck` (lateral), `crane` (vertical + push), `orbit` (gentle arc).
- Strength 0.02-0.06. Above that, edges stretch. Faces and hands near depth edges show artefacts first:
  check them frame by frame. Fix the depth map by hand (paint in an editor) when needed; the tool accepts it.
- Depth Anything V2 Small gives relative depth; sky and glass and reflections can be wrong. Clamp sky to far.
- Measured: depth ~1.3 s per photo; render ~0.2 s per 1080p frame.

## Finishing so stills cut with video
- Add the film's grain (same as video shots) and a touch of motion blur on faster moves.
- Match frame rate and shutter feel (24 fps). Keep moves eased; avoid linear zooms.
- Resolution: a 12 MP phone photo supports a 4K frame with modest push; check the final crop size.
- Never upscale blindly. If a photo is too small, decide: smaller in frame, a designed treatment, or
  AI upscaling with identity review.
