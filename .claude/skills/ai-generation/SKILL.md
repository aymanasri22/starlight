---
name: ai-generation
description: Cloud AI image and video generation for the film (image-to-video, scene extension, background replacement, relighting, upscaling, frame interpolation, AI music/voice). Use before any generative step: covers the approval and cost gate, provider choice, prompt practice, provenance records, and the identity check. No GPU here, so all heavy generation is cloud-based and paid.
---

# AI generation protocol

## 0. Gate (mandatory)
Paid generation needs the client's explicit OK: provider, which shots, estimated cost. Ask once per
batch with a clear estimate. No API keys are configured in this environment (as of 2026-11-27); never
ask for a key in chat. Keys are added by the client in the cloud environment's settings (network
secrets), or a provider's official MCP server is connected (fal and Replicate offer official remote MCP
servers with their own sign-in).

## 1. What runs where
- **Local (CPU, free):** depth (Depth Anything V2 S), mattes (BiRefNet/U2-Net), face detection and identity
  embeddings (YuNet/SFace), 2.5D parallax, classical upscaling (Lanczos), FFmpeg `minterpolate` (weak).
- **Cloud (paid):** image generation/editing (FLUX family, Google Gemini/Imagen image models, Seedream,
  GPT-image class), image-to-video (Runway Gen-4.5, Kling 3.x/4.x, Seedance 2.x, Veo 3.1 via Vertex/
  Replicate, MiniMax Hailuo, open Wan/LTX models via fal/Replicate), AI upscaling (Topaz, Real-ESRGAN
  class), frame interpolation (RIFE/FILM class), video matting/rotoscoping (SAM 2 class), music/voice.
  Model rankings move monthly: check a current leaderboard (e.g. Artificial Analysis video arena) and
  the provider's pricing on the day. Sora's API was shut down in Sept 2026.
- Aggregators (fal, Replicate) give one key/one bill for many models: the most flexible starting point.

## 2. Prompting (see the vendored `cinematic-director` skill: prompt lexicon + model adapters)
- Describe like a cinematographer: subject, action, lens (mm), camera height and move, light source
  and direction, time of day, weather, texture, frame rate feel. One camera move per shot.
- Image-to-video from the client's real photos beats text-to-video. Use first/last frame control to
  land on real frames. Keep shots short (3-6 s) and motion moderate; long/fast shots drift.
- Chinese signage: either real legible characters you verify, or keep text out of focus/out of frame.
  Never ship garbled characters.

## 3. Provenance (every output)
Sidecar `<file>.json` in `04_AI_Generated_Assets/<shot>/`:
`{provider, model, model_version, endpoint, prompt, negative_prompt, seed, inputs[], settings{},
cost_usd, created, operator, identity_check{score, verdict, reviewer}, selected: bool, notes}`.
The `fal-client` and `replicate` Python clients are installed in the studio venv.

## 4. Acceptance
- Identity: `identity-preservation` skill (automated gate + side-by-side) for any shot with the client.
- Artefacts: hands, faces, morphing backgrounds, flicker, physics, scale, continuity with neighbours.
- Integration: grade, grain, sharpness and motion blur matched to the surrounding real shots.
- Honesty: generated scenes that depict events are discussed with the client; they decide what the film
  may imagine.
