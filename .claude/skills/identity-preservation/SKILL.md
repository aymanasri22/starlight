---
name: identity-preservation
description: Protocol for any image or video that shows the client (the person the film is about). Use before generating, editing, relighting, upscaling, restoring, compositing or animating anything with their face or body, and when reviewing such shots; covers the reference set, the automated identity gate, side-by-side review and what to reject.
---

# Identity preservation

The client's real appearance is part of the truth of the film. A generated face that is "close" is a
different person. Treat every AI/VFX touch on the client as a potential identity change until proven not.

## 1. Reference set (once, with the client)
- 5-10 sharp original photos: frontal, 3/4 left, 3/4 right, profile, smiling and neutral, daylight and
  night, glasses on/off if relevant. Same period of life as the Shanghai trip.
- Store in `Shanghai_Film/00_Project_Direction/identity_reference/` (git-ignored: never committed).
- Enroll: `$PY studio/lib/identity.py enroll <ref photos> --out Shanghai_Film/00_Project_Direction/identity_reference/ref.npz`
- Write a short description sheet with the client: face shape, eye colour, hair, skin tone and texture,
  distinguishing marks, typical clothing from the trip, glasses/jewellery. That sheet guides prompts and reviews.

## 2. Rules for any shot with the client
- Prefer techniques that keep real pixels: parallax on the real photo, real video, compositing the real
  person into an extended environment. Generate the world around them, not them.
- If a model must re-render the person (image-to-video, relighting), use the highest-fidelity reference
  conditioning available, low motion strength, short shots, and first/last frames from real photos.
- Never change age, weight, facial proportions, skin tone, or features; no beautification or skin
  smoothing unless the client asks. Keep natural skin texture (pores, fine lines).
- Wardrobe, hair and accessories stay consistent within a scene (continuity bible).

## 3. Automated gate (tripwire)
```bash
$PY studio/lib/identity.py check ref.npz <frames or video> --every 6 --json id.json --sheet id_sheet.jpg
```
- PASS >= 0.50 cosine, REVIEW 0.363-0.50, FAIL < 0.363 (SFace). Video: every sampled frame must pass,
  because identity often drifts mid-shot.
- Measured on public-domain NASA test portraits (pipeline_test/RESULTS.md):
  graded + downscaled + JPEG-60 copy 0.90 PASS; a genuinely different photo of the same person taken
  seven years later, in a 7-person group shot, 0.67 PASS while the other six faces scored <= 0.15;
  two different people 0.12 and 0.18 FAIL.
- **Known blind spot (measured):** a simulated 18% facial-proportion warp of the reference still scored
  0.96 PASS. Embeddings are built to be robust to exactly the kind of drift generative tools cause
  (proportions, age cues, skin texture, expression). The gate catches "wrong person"; it does NOT catch
  "subtly altered person". Passing it is necessary, never sufficient: section 4 is where likeness is judged.

## 4. Human/visual review (required)
Side-by-side at full resolution, generated frame next to the closest real reference: eyes (shape,
spacing, colour), nose, mouth, jaw, hairline, ears, skin texture, age cues, teeth, hands. Check the first,
middle and last frame of video plus any frame where the head turns. Any doubt -> reject or ask the client.

## 5. Record
Every accepted shot with the client gets an entry in its provenance sidecar: gate score(s), reviewer,
date, and "client approved" when they have seen it. The client signs off every such shot before final.
