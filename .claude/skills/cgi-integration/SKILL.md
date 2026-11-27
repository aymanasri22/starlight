---
name: cgi-integration
description: Headless Blender CGI for the film: HDRI lighting, shadow-catcher integration into real photos/plates, camera matching, CC0 assets from Poly Haven, 3D city/maps from OpenStreetMap, render budgeting on a CPU-only machine, and compositing CGI over plates. Use for any 3D or CGI shot.
---

# CGI integration (Blender 5.2 LTS, headless)

## Reference recipe (verified)
```bash
blender -b --factory-startup --python studio/blender/integrate_cgi.py -- \
  --hdri Shanghai_Film/06_CGI_3D/hdri/shanghai_bund_4k.hdr --out fg.png --plate-out bg.png \
  --yaw -42 --pitch -12 --fov 62 --size 1280x720 --samples 64 [--blend scene.blend]
```
Produces a straight-alpha RGBA foreground (CGI + caught shadows) and a matched plate. Composite:
`out = fg.rgb * fg.a + plate * (1 - fg.a)` (see `run_pipeline_test.py` stage `blender`).
`assets.py plate` extracts a perspective plate from an HDRI that matches Blender's camera to sub-pixel
accuracy (measured 0.02 px shift), useful for 360-camera stills too.

## Matching a real photo plate
1. Lens: from EXIF `FocalLengthIn35mmFormat` -> horizontal FOV = 2*atan(36/(2*f)). Phones: main ~26 mm,
   ultrawide ~13 mm, tele 52-120 mm.
2. Camera height and horizon: find the horizon line and vanishing points; people's eye level ~1.6 m.
3. Light: direction and softness from real shadows; colour from neutral surfaces; for night city scenes
   use the CC0 `shanghai_bund` HDRI or a matching Poly Haven HDRI as a base, then add practicals.
4. Always render the grey ball + chrome ball check and compare to the plate before the hero asset.
5. Finish: match black level, grain, defocus, motion blur, chromatic aberration, lens distortion.

## Assets (licences logged automatically)
- Poly Haven (CC0): `assets.py hdri-list --category urban`, `assets.py hdri <id> --res 4k|8k`.
  Downloaded: `shanghai_bund_4k.hdr`, `shanghai_bund_8k.hdr` (night, the Bund promenade, Lujiazui skyline).
- OpenStreetMap buildings (ODbL, credit required): `assets.py osm-buildings --bbox 31.2330,121.4960,31.2440,121.5110 --out lujiazui.json`
  (276 buildings, 53 with real heights incl. Shanghai Tower 632 m, SWFC 492 m, Jin Mao 420 m), then
  `blender -b --factory-startup --python studio/blender/osm_city.py -- --osm lujiazui.json --out city.png`
  extrudes them into a 3D city (clay study; ~16 s at 720p). Animate the camera for map flights.
  overpass-api.de drops connections through this environment's proxy; the tool falls back to other
  public Overpass instances automatically.
- Both Blender scripts check their own render and exit with STUDIO_FAIL on a flat/empty frame (a camera
  beyond its clip range once produced a blank frame that still "succeeded"). Keep that check in new scripts.
- Other open sources: ambientCG (CC0 materials), Poly Pizza / Sketchfab (check each model's licence).

## Render budget (4 CPU threads, no GPU)
- Cycles 720p 64 spp: tens of seconds per frame. 1080p 128 spp: minutes per frame. Plan accordingly:
  short shots, lower samples + OIDN denoise, render stills and animate in 2.5D, EEVEE for previs only.
- Heavy shots (long camera moves, volumetrics, many frames): flag for cloud GPU rendering or for the client's
  own GPU machine; the `.blend` files are portable.

## Not available here
GUI Blender (no display), GPU rendering, Blender MCP live control (needs the GUI app on the client's
machine), Unreal Engine.
