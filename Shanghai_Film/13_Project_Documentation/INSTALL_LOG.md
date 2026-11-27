# Installation and configuration log

Session date: 2026-11-27. Container: Ubuntu 24.04.5, 4 vCPU Xeon @ 2.1 GHz, 15 GB RAM, no GPU.
The container is ephemeral: system-level installs below are rebuilt by `studio/bootstrap.sh`
(and by the cloud environment's setup script, if the client approves saving it).

## System (container, not in git)
| What | Version | Source / verification | Where |
|---|---|---|---|
| exiftool, mediainfo, sox, fonts-noto-cjk, Mesa GL/EGL libs | Ubuntu 24.04 packages | apt (archive.ubuntu.com) | system |
| FFmpeg static build | n9.0.2-982-g836df4e858-20261126 | BtbN/FFmpeg-Builds `latest` release, SHA-256 checked against the release's `checksums.sha256` | `/opt/studio/ffmpeg`, symlinked to `/usr/local/bin/ffmpeg`, `ffprobe` |
| Ubuntu FFmpeg (pre-existing) | 6.1.1-3ubuntu5 | kept untouched as fallback | `/usr/bin/ffmpeg` |
| Blender | 5.2.5 LTS (supported to July 2028) | download.blender.org, SHA-256 from `blender-5.2.5.sha256` | `/opt/studio/blender`, symlinked to `/usr/local/bin/blender` |
| Python venv | CPython 3.12 (via uv) | PyPI, `studio/requirements.txt` | `/opt/studio/venv` |
| Local models | see `/opt/studio/models/models_manifest.json` | Hugging Face, pinned revisions, SHA-256 recorded | `/opt/studio/models` |
| BiRefNet-portrait matte model (973 MB) | rembg default release | downloaded by rembg on first use | `/opt/studio/models/rembg` |

Why FFmpeg 9: the Ubuntu 6.1.1 package was last rebuilt April 2024 and predates upstream fixes for
2026 decoder CVEs (flagged by ffmpeg-skill's doctor); the 9.0 build also adds libvmaf, vvenc and
newer filters. Why Blender 5.2 LTS rather than 5.3: long-term support for the length of the production.

## Python packages (studio venv, resolved versions at install)
numpy 2.5.5, scipy 1.18.1, pillow 11.3.0, opencv-contrib-python-headless 5.1.0, scikit-image 0.26.0,
av 19.0.2, imageio 2.38.2 (+imageio-ffmpeg), moviepy 2.1.2, scenedetect 0.7.3, opentimelineio 0.18.1
(+ cmx_3600, fcpx_xml, fcp_xml adapters), colour-science 0.4.7, opencolorio 2.6.0, OpenImageIO 3.2.2,
librosa 1.0.1, soundfile 0.14.0, pyloudnorm, pedalboard 0.9.26, onnxruntime 1.32.0, rembg 2.0.69,
huggingface_hub 2.5.0, fal-client 1.0.3, replicate, matplotlib 3.11.2, shapely 2.2.0, requests, tqdm.

## Local AI models (all permissive licences)
| Model | Licence | Purpose |
|---|---|---|
| YuNet face detector (opencv_zoo, 2023mar) | MIT | face detection + landmarks |
| SFace face recognizer (opencv_zoo, 2021dec) | Apache-2.0 | identity embeddings for the likeness gate |
| Depth Anything V2 Small (onnx-community) | Apache-2.0 | monocular depth for 2.5D parallax |
| BiRefNet-portrait (via rembg) | MIT | person mattes |
Not installed on purpose: Depth Anything V2 Base/Large (CC-BY-NC), InsightFace models (non-commercial).

## Node (in git: package.json + lock; node_modules not in git)
Remotion 4.0.547, @remotion/cli 4.0.547, React 19.2.0, TypeScript 5.9.3 in
`Shanghai_Film/07_Motion_Graphics/remotion/`. Remotion uses the pre-installed Chromium headless shell
(`remotion.config.ts`). Remotion licence: free for individuals and companies of up to 3 people;
larger companies need a company licence (remotion.pro).

## Claude Code configuration (in git)
- `CLAUDE.md`: studio operating rules.
- `.claude/agents/`: 10 creative agents (see report section 4).
- `.claude/skills/`: 9 studio skills written for this project + 2 vendored third-party skills:
  - `ffmpeg-skill` from github.com/kajisho5/ffmpeg-skill @ b9087dc (MIT), audited, see its UPSTREAM.md
  - `cinematic-director` from github.com/wuwangzhang1216/DirectorSKILL @ c65ae0d (MIT), see UPSTREAM.md
- Pre-existing plugin skills used by the studio (not installed by me): `remotion:*`, `motion-reel`.
- No MCP servers were added. No API keys or credentials were created, stored or requested.

## Cloud environment
- Environment "mobile start" (personal): setup script added with the client's approval. It mirrors
  `studio/bootstrap.sh` (apt packages, FFmpeg 9.0 BtbN with SHA-256 check, Blender 5.2.5 LTS with
  SHA-256 check, studio venv, models, Remotion npm install), runs only when the starlight repo is
  present, and never fails the session start. Network policy unchanged (unrestricted).
- `.gitignore`: blocks all media under `Shanghai_Film/` (this repository is public).

## Assets downloaded (logged in asset_licences.json)
- Poly Haven `shanghai_bund` HDRI, 4k + 8k (CC0).
- OpenStreetMap buildings, Lujiazui test bbox (ODbL, credit required if used in the film).
- Pipeline-test only: NASA public-domain portraits (identity gate test), not part of the film.

## Not changed
- The Astro Starlight site files. No existing configuration was overwritten. No paid services used.
