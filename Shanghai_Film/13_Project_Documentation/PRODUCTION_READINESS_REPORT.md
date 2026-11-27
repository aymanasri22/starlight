# Production-Readiness Report: Shanghai Film Studio

**Date:** 2026-11-27  **Scope:** preparation only. No film footage, storyboards, music or edits made.
**Verdict:** **Ready to begin creative development.** The local pipeline (ingest, photo animation, CGI
integration, 3D maps, motion graphics, editing, colour, sound, delivery, QC) is installed and passed a 17-stage
end-to-end test. Generative AI video/image work needs one paid cloud service you approve, and heavy 3D
rendering is limited by this machine having no GPU.

---

## 1. Hardware and environment

| Item | Finding | What it means |
|---|---|---|
| Machine | Cloud container, Ubuntu 24.04.5, Linux 6.18 | Runs on Anthropic's cloud, not your computer |
| CPU | 4 threads, Intel Xeon @ 2.1 GHz | Fine for editing/encoding; slow for 3D rendering |
| GPU / VRAM | **None** (no NVIDIA, no /dev/dri) | No local diffusion/video AI, no GPU rendering |
| RAM | 15 GB | Adequate for 4K editing and CPU AI models |
| Disk | ~60 GB free (252 GB volume) | Enough for a short film's working set; originals should also live in Drive |
| Network | Unrestricted outbound (via proxy) | PyPI, npm, Hugging Face, Blender, Poly Haven, GitHub reads all reachable |
| Persistence | **Ephemeral**: the container is reclaimed after inactivity | Code/docs are committed to git; media must live in Google Drive; tools rebuild via `studio/bootstrap.sh` |
| Display | None (headless) | No GUI apps; I review work by looking at rendered frames/contact sheets |
| API keys | None for AI generation (no fal, Replicate, Runway, OpenAI, ElevenLabs...) | Cloud generation needs your approval + a key |
| Pre-existing | Python 3.13, Node 22, FFmpeg 6.1.1, ImageMagick 6, Docker, LibreOffice, Playwright Chromium, uv, gh | Base was good for scripting; no creative apps installed |
| Repository | `aymanasri22/starlight` (an Astro Starlight starter) is **public** | Personal media must never be committed. Consider making it private |

## 2. Installed applications and tools

All installed, verified and exercised by the pipeline test unless marked otherwise.

| Discipline | Tool | Version | Status |
|---|---|---|---|
| Video engine | FFmpeg (BtbN static, GPL) | 9.0.2 (2026-11-26 build) | Installed, SHA-256 verified, tested. x264, x265 10-bit, SVT-AV1, ProRes, DNxHR, zscale, vid.stab, rubberband, libvmaf, libass |
| Video (Python) | PyAV, MoviePy, imageio, OpenCV 5.1 (contrib) | 19.0 / 2.1 / 2.38 / 5.1 | Installed, tested |
| Shot detection | PySceneDetect | 0.7.3 | Installed, tested |
| Timeline interchange | OpenTimelineIO + EDL, FCPXML, FCP7 XML adapters | 0.18.1 | Installed, tested (Resolve/Premiere/FCP can open the exports) |
| 3D / CGI | Blender (headless) | 5.2.5 LTS | Installed, SHA-256 verified, Cycles CPU + EEVEE (software GL) tested |
| Motion graphics | Remotion (React) + local Chromium | 4.0.547 | Installed, rendered ProRes 4444 with alpha |
| Image | Pillow, scikit-image, ImageMagick 6, OpenImageIO | 11.3 / 0.26 / 6.9 / 3.2 | Installed |
| Colour science | colour-science, OpenColorIO 2 | 0.4.7 / 2.6 | Installed; .cube LUT authoring tested |
| Audio | pedalboard, librosa, pyloudnorm, soundfile, SoX | 0.9.26 / 1.0.1 / - / 0.14 / 14.4.2 | Installed, tested |
| Local AI | onnxruntime, rembg, Depth Anything V2 S, YuNet + SFace, BiRefNet-portrait | see INSTALL_LOG | Installed, tested |
| Metadata | exiftool, mediainfo | 12.76 / Ubuntu | Installed, tested (EXIF time/GPS) |
| Typography | Noto Sans/Serif CJK (SC/TC/JP/KR), Inter, JetBrains Mono | system | Installed; CJK rendered in Remotion test |
| Cloud AI clients | fal-client, replicate (Python) | 1.0.3 / latest | Installed, **not used** (no keys, no approval) |

Studio tools written for this project (`studio/lib/`, all CLIs, all exercised by the test): `ingest`,
`identity`, `depth_parallax`, `matte`, `assets`, `grade`, `audio`, `timeline`, `deliver`, `qc`, plus
Blender scripts `integrate_cgi.py` and `osm_city.py`. Full list and versions: `INSTALL_LOG.md`.

**Considered and not installed (with reasons)**

| Candidate | Reason |
|---|---|
| DaVinci Resolve / Fusion | Needs a GPU and a GUI; cannot run here. Our LUTs (.cube) and timelines (FCPXML/EDL/OTIO) open in Resolve on your computer |
| Adobe After Effects / Premiere | Licensed GUI software for Windows/macOS; not available here |
| Natron | Development has largely stalled (last stable release 2.5, 2022); Blender's compositor + Python + FFmpeg cover it |
| Unreal Engine | Needs a GPU, about 100 GB, GUI; not practical in this container |
| ComfyUI / Stable Diffusion / FLUX locally | Need a GPU; CPU inference is impractically slow. Same models are reachable via cloud APIs |
| Manim | Built for mathematical animation; Remotion + Blender suit this film better |
| GSAP / Lottie / three.js | Not pre-installed as separate projects; available from npm when the Motion Designer needs them (three.js is already used by the `motion-reel` skill) |
| Real-ESRGAN / RIFE locally | GPU tools (Vulkan/CUDA); cloud versions recommended. FFmpeg `minterpolate` exists locally but is low quality |

## 3. GitHub skills and repositories

**Installed (vendored, pinned, audited):**

| Repository | What it adds | Audit |
|---|---|---|
| [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) @ `b9087dc`, MIT | 42 tested FFmpeg tools with a machine-readable contract: precise cuts, multicam/audio sync, speed ramps, stabilise, captions, loudness, platform compliance `check.py`, contact sheets `look.py` | Active (commits today). Standard-library Python calling ffmpeg with argument lists; no network calls, no `shell=True`/eval/exec, no telemetry. Copied the skill only (no npm installer, no MCP server). Tested: `check.py` and `look.py` ran in the pipeline test |
| [wuwangzhang1216/DirectorSKILL](https://github.com/wuwangzhang1216/DirectorSKILL) @ `c65ae0d`, MIT (as skill `cinematic-director`) | Director's toolkit: beat sheets, blocking, shot lists, coverage, prompt lexicon for AI video/image models, failure-diagnosis manual, 20 director-style lenses (including Wong Kar-wai, Bi Gan, Hou Hsiao-hsien, Zhang Yimou) used as *methods*, never to copy | Markdown only, no executable code. Last update Aug 2026, so its AI-model notes may lag current models |

**Already available in this account and used by the studio:** the Remotion skill set
(`remotion:*`, official Remotion skills) and `motion-reel` (code-rendered motion films with three.js,
synthesized score, beat grid).

**Evaluated and not installed:**

| Repository | Why not |
|---|---|
| [OpenMontageInc/OpenMontage](https://github.com/OpenMontageInc/OpenMontage) (AGPL-3.0) | A complete agentic video framework (about 2,300 files, 12 pipelines) that would replace rather than extend our studio; AGPL copyleft; very large provider/dependency surface. Its very high star count for an 8-month-old repo could not be independently verified |
| [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) (MIT) | Excellent for live Blender control, but needs Blender's GUI running on your machine. Executes arbitrary Python by design; telemetry on by default (set `DISABLE_TELEMETRY=true`). **Recommended for your own computer** if you want to watch/steer 3D work live |
| [samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp) (MIT) | Drives DaVinci Resolve Studio; needs Resolve running on your machine. **Recommended for your computer** if you finish in Resolve |
| [digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) (MIT) | Strong toolkit, oriented to explainer/product videos; its notable part (open models on rented GPUs via Modal/RunPod) is a paid route we can adopt later if you want self-hosted open models |
| [arjun988/blender-skills](https://github.com/arjun988/blender-skills) (MIT) | 94 skills mostly for game art; would add noise. Our focused `cgi-integration` skill covers the film's needs |
| [artokun/comfyui-mcp](https://github.com/artokun/comfyui-mcp) (MIT) | Requires a running ComfyUI (GPU). Relevant only if you add a GPU machine |
| Small FFmpeg/video MCP servers (e.g. misbahsy/video-audio-mcp) | Thin wrappers over FFmpeg; no gain over direct FFmpeg + ffmpeg-skill |
| Official remote MCP servers: [fal](https://fal.ai/docs/model-apis/mcp), [Replicate](https://mcp.replicate.com/), [ElevenLabs](https://github.com/elevenlabs/elevenlabs-mcp) | Legitimate and useful, but each needs a paid account. Not connected without your approval (section 7) |

## 4. Creative agents and skills

The main session acts as **Creative Director/producer** and coordinates the department agents (Claude
Code agents cannot spawn other agents). They collaborate through shared files: the Production Bible,
Decisions Log, Shot List, and dated handoff notes. Stage gates: Treatment, Shot list + animatic, Look,
Rough cut, Fine cut, Final, each approved by you, with the QC Director's written pass before "final".

| Agent (`.claude/agents/`) | Responsibilities |
|---|---|
| `creative-director` | Vision, treatment, visual identity, gate reviews, cuts anything that does not serve the story |
| `film-director` | Beat sheet, scenes, shot list with coverage, animatic, pacing, directing CGI/AI shots like a shoot |
| `cinematographer` | Technical grading of your media, framing, virtual camera moves, lens/light matching for CGI |
| `video-editor` | Selects, animatic, cuts, transitions, speed ramps, conform, OTIO/EDL/FCPXML exports |
| `cgi-vfx-artist` | Blender, HDRI lighting, shadow-catcher integration, 3D maps from OpenStreetMap, compositing |
| `motion-designer` | Bilingual typography (Latin + Chinese), titles, maps, graphic transitions, credits (Remotion) |
| `ai-visual-artist` | Cloud image/video generation under cost approval, provenance records, identity checks |
| `sound-designer` | Ambiences, designed transitions, licensed music, mix, -14 LUFS / EBU R128 masters, stems |
| `colorist` | HDR phone footage normalisation, shot matching, looks (.cube), skin protection, grain |
| `qc-director` | Independent technical + artistic QC, identity and licence checks, go/no-go reports |

Studio skills (`.claude/skills/`): `studio-pipeline` (tools, paths, commands, render budgets),
`media-ingest`, `identity-preservation`, `photo-animation`, `cgi-integration`, `color-pipeline`,
`sound-design`, `ai-generation`, `delivery-qc`, plus vendored `ffmpeg-skill` and `cinematic-director`.
`CLAUDE.md` holds the non-negotiable rules (originals untouched, public repo, identity, money, licences,
honesty, taste).

Workspace: `Shanghai_Film/00_Project_Direction` ... `13_Project_Documentation` as you specified, with
templates for the Production Bible, Decisions Log, Shot List, Selects and handoff notes.

## 5. AI generation capabilities

| Capability | Where | Status |
|---|---|---|
| Analysing your photos/videos (composition, light, story value, continuity) | Claude (vision) on frames and contact sheets | Available |
| Monocular depth for 2.5D parallax | Local, Depth Anything V2 Small | Tested: 1.3 s/photo; parallax 0.23 s per 1080p frame |
| Person/subject mattes (stills) | Local, BiRefNet-portrait | Tested: ~38 s per image on CPU, clean hair edges |
| Face detection + identity similarity | Local, YuNet + SFace | Tested (section 8) |
| Image generation and editing (scene extension, background replacement) | Cloud only (FLUX family, Gemini image models, Seedream, GPT-image class) | **Needs approval + key** |
| Image-to-video (animating your photos with real motion) | Cloud only (Runway Gen-4.5, Kling, Seedance, Veo 3.1 via Vertex/Replicate, open Wan/LTX via fal/Replicate) | **Needs approval + key** |
| AI upscaling, frame interpolation, video rotoscoping (SAM 2 class) | Cloud (GPU) | **Needs approval + key** |
| AI music, voice, sound effects | Cloud (e.g. ElevenLabs), licence terms matter | **Needs approval** |
| Claude generating images itself | Not possible | I direct, prompt, review and composite; models generate |

Model landscape (Nov 2026, from current comparisons, verify on the day): Runway Gen-4.5 and Kling
lead image-to-video consistency; Seedance offers longer and native-4K takes; Veo 3.1 for realism and
native audio (now via Vertex AI/Replicate/Runway); OpenAI's Sora API was shut down in Sept 2026.

## 6. Missing capabilities and limitations

1. **No GPU.** Local generative AI is impractical; Cycles renders a simple 720p frame at 64 samples in
   ~45 s (plate + CGI pass with Blender start-up: 59 s). Long or complex CGI shots need cloud GPU or your
   own GPU machine.
2. **4K HEVC encoding is slow:** 350-400 s for 11 s of 4K HEVC 10-bit (slow preset), 32-36x slower than real time.
   A 5-minute film's 4K HEVC delivery takes roughly 2.5-3 hours here (1080p H.264: 2.3x slower than real time).
3. **No GUI applications** (Resolve, After Effects, Premiere, Blender UI). Everything is scripted and
   reviewed through rendered frames. Optional finishing on your computer is supported via LUTs and
   FCPXML/EDL/OTIO exports.
4. **No calibrated or HDR display.** Grades are verified numerically and on frames; final colour should
   be checked by you on a good screen (and a phone). HDR delivery cannot be verified here.
5. **Identity gate blind spot (measured):** it reliably separates people (different people scored
   0.08-0.18; the same person seven years later 0.67), but an 18% facial-proportion warp still passed
   at 0.96. It cannot detect subtle drift; side-by-side human review and your approval are mandatory.
6. **Video rotoscoping** (moving mattes) is not practical on CPU at quality; stills only locally.
7. **Ephemeral container:** installed tools disappear when the session ends. Rebuild measured at about
   1 minute (64 s for FFmpeg, Blender, Python stack; the 1 GB matte model downloads on first use) with
   `studio/bootstrap.sh`, or automatically if you approve the environment setup script. Media must be
   kept in Google Drive.
8. **Music:** no licensed music library is connected. Synthesized SFX are fine; music needs a licence.
9. **Network quirk:** `overpass-api.de` (OpenStreetMap queries) drops connections through this
   environment's proxy; the tool falls back to another public instance (verified working).
10. Dissolves are not flagged by the content shot detector (hard cuts are); not a production issue.

## 7. Paid tools and APIs that would materially improve production (need your approval)

Ranked by impact. Prices change often; I will quote exact costs before any spend.

1. **A cloud generation aggregator: fal.ai or Replicate** (pay per use, no subscription). One account
   unlocks image editing, image-to-video, upscaling, interpolation and video matting across many models.
   Both have official MCP servers. **Highest value.** A short film with careful use might need tens of
   generated clips; expect tens to a few hundred USD depending on models, resolution and iterations.
2. **Music licence** (e.g. Artlist, Musicbed, Epidemic Sound subscription, or a commissioned score).
   Essential for a film you will publish.
3. **Runway** (subscription) if you want its strongest image-to-video and video-to-video tools directly.
4. **Cloud GPU time** (e.g. RunPod/Modal, roughly USD 0.5-3 per GPU-hour) for heavy Blender shots or open
   models; or use your own GPU computer.
5. **ElevenLabs** for designed sound effects or a voice, if the film needs narration.
6. Optional on your computer: **DaVinci Resolve Studio** (one-time licence; the free version is also
   capable) for a final interactive grade, and **Topaz Video** for upscaling/restoration.

## 8. Pipeline test results (harmless assets only)

Assets: synthetic clips; the CC0 Poly Haven `shanghai_bund` HDRI (a real 360-degree photograph of the
Bund at night, also usable in the film); US-government public-domain NASA portraits for the identity gate.
None of your media was used. Evidence images and editable timelines:
`13_Project_Documentation/pipeline_test/` (`RESULTS.md`, `results.json`, `*.jpg`, `.otio/.edl/.fcpxml/.xml`, `.cube`).

Final clean run: **17 of 17 stages PASS** (12.4 min end to end, 4 CPU threads, FFmpeg 9.0.2, Blender 5.2.5 LTS; the portrait download step is folded into row 4).

| # | Stage | Result | Measured |
|---|---|---|---|
| 1 | Sample media: photo with EXIF/GPS, 60p vertical clip, shaky handheld clip, iPhone-style HLG HDR clip, a truncated clip | PASS | Simulated camera card |
| 2 | Non-destructive ingest | PASS | Read-only originals, SHA-256 catalogue, proxies, GPS/time parsed, HLG flagged, corrupt file flagged not fatal, tampering detected by `verify` |
| 3 | Photo to depth to 2.5D push-in (1080p ProRes) | PASS | Depth 1.5 s; 0.21 s per frame |
| 4 | Identity gate (YuNet + SFace) | PASS | Same person, graded copy 0.90; same person 7 years later in a 7-face group 0.67 (others <= 0.15); different people 0.12 / 0.18; **18% face warp 0.96 (not caught, see limitations)** |
| 5 | Person matte (BiRefNet) + composite | PASS | 37 s per image; clean hair edge |
| 6 | Blender CGI on shadow catcher over HDRI plate (Cycles CPU, 720p, 64 spp) | PASS | 57 s for plate + CGI; camera match 0.03 px |
| 7 | Remotion bilingual title, ProRes 4444 alpha, composited | PASS | 96 frames in 12.7 s; CJK glyphs verified |
| 8 | Stabilisation (vid.stab) | PASS | Shake 10.6 to 0.31 px/frame (-97%) |
| 9 | HLG HDR to Rec.709 | PASS | Correct tags; mobius default (brightness within 2% of intent) |
| 10 | Sound: synthesized SFX, mix, master | PASS | -14.0 LUFS, true peak -2.8 dBTP |
| 11 | Edit: 4 mixed sources conformed to 24p, dissolve, speed ramp, audio | PASS | 11.000 s picture and audio; EDL + FCPXML + FCP7 XML + OTIO exported and re-imported |
| 12 | Grade: authored .cube look + grain + vignette | PASS | 33-point LUT, Resolve-compatible (a test look, not a creative choice) |
| 13 | Delivery encodes (11 s) | PASS | 1080p H.264 27 s; 9:16 26 s; **4K HEVC 10-bit 350-400 s** |
| 14 | QC: specs, loudness, black/frozen frames, VMAF, ffmpeg-skill checks | PASS | VMAF 97.1 (1080p vs master); all checks PASS |
| 15 | Shot detection | PASS | Both hard cuts found; dissolve not flagged (expected) |
| 16 | 3D Lujiazui from OpenStreetMap | PASS | 276 buildings (Shanghai Tower 632 m, SWFC 492 m, Jin Mao 420 m), 13 s render |

Evidence: `02_depth_parallax.jpg`, `04_identity_gate.jpg`, `05_matte_composite.jpg`,
`06_blender_cgi_integration.jpg`, `07_remotion_title_overlay.jpg`, `08_hdr_to_sdr.jpg`,
`09_edit_master_contact_sheet.jpg`, `10_grade_before_after.jpg`, `11_osm_city_3d.jpg`.

**Problems the testing found and fixed** (this is why the test exists):
- Ingest crashed on a truncated video; now flags it and continues (a corrupt file is part of the test).
- HDR phone-footage conversion: the common internet recipe (hable, npl 203) rendered footage at half
  brightness; switched the default to mobius/npl 100 (within 2% of the intended brightness).
- FFmpeg 9 silently ignored colour tags on untagged sources; every tool now tags Rec.709 explicitly.
- HDRI plate extraction had a half-pixel offset (0.94 px); fixed to 0.03 px against Blender's camera.
- OpenCV 5 removed the guided filter used for matte/depth edges; replaced with our own implementation.
- Edit render: speed-ramp expression parsing, transition timebases, and audio ending 77 ms early, all fixed.
- EDL export failed on dissolves; transitions are now modelled the way NLEs expect (centred, with handles).
- The 3D map render produced a blank frame yet reported success (camera beyond its clip range); fixed,
  and both Blender scripts now fail loudly on a flat/empty render.
- Light title text vanished over the bright night skyline; the test title now has a legibility
  treatment, and the Motion Designer's brief requires one.
- The 9:16 vertical export stored non-square pixels (SAR 1216:1215), caught by the vendored ffmpeg-skill;
  all delivery profiles now force square pixels and our QC checks it.
- The git ignore rules would have committed 5,197 `node_modules` files; fixed before any commit.

## 9. Overall production readiness

| Area | Readiness |
|---|---|
| Ingest, organisation, source protection | **Ready** |
| Editing, transitions, speed ramps, conform of phone footage (incl. HDR) | **Ready** |
| Photo animation (2.5D parallax, mattes) | **Ready** (stills); moving mattes need cloud |
| Motion graphics, bilingual typography, titles, 3D maps (OpenStreetMap data) | **Ready** |
| CGI integration (Blender) | **Ready with limits**: short shots/stills on CPU; heavy shots need GPU |
| Colour (normalise, match, looks, grain, LUTs for Resolve) | **Ready**; final check on your display |
| Sound design, mix, mastering | **Ready**; music needs a licence |
| Generative AI (image/video) | **Needs one approved cloud service** |
| Identity preservation | **Ready as a process** (automated gate + mandatory human review) |
| Delivery (ProRes/DNxHR masters, 4K HEVC/H.264, 1080p, 9:16, 1:1) and QC (incl. VMAF) | **Ready**; 4K encodes are slow |

## 10. What I need from you next

1. **Privacy:** consider making `aymanasri22/starlight` private (GitHub > Settings > General > Danger
   Zone > Change visibility). The setup already keeps media out of git either way.
2. **Media delivery:** put your full-quality originals (iPhone: unmodified originals, not via WeChat/
   WhatsApp) in a Google Drive folder and share the folder name; I will ingest them non-destructively.
3. **Identity references:** 5-10 clear photos of your face from the Shanghai period.
4. **Paid services:** whether to set up fal or Replicate (and a budget ceiling), and how you want to
   license music.
5. **Environment setup script:** approve saving the toolchain install to this cloud environment so
   future sessions start ready (you will see an approval prompt).
6. **Creative direction:** when you are ready, we start with your memories of Shanghai, the people and
   moments that matter, and the feeling the film should leave behind.
