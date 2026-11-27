#!/usr/bin/env bash
# Rebuild the studio toolchain in a fresh container. Idempotent: skips what is already installed.
# Every download is checksum-verified. Run from the repository root:  bash studio/bootstrap.sh
# Takes about 1-2 minutes on a fresh Ubuntu 24.04 container with network access (measured 64 s).
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STUDIO=/opt/studio
mkdir -p "$STUDIO"
log() { printf '\n== %s\n' "$*"; }

log "1/6 system packages (metadata, audio, CJK fonts, Mesa GL for Blender)"
if ! command -v exiftool >/dev/null || ! fc-list | grep -qi "Noto Sans CJK"; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libimage-exiftool-perl mediainfo sox fonts-noto-cjk \
    libgl1 libegl1 libgl1-mesa-dri libxxf86vm1 libxfixes3 libxi6 libxkbcommon0 libsm6 libxrender1 libxext6
fi

log "2/6 FFmpeg 9.0 static build (BtbN, GPL), verified against the release checksum file"
if ! /opt/studio/ffmpeg/bin/ffmpeg -version 2>/dev/null | grep -q "version n9"; then
  B=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest
  F=ffmpeg-n9.0-latest-linux64-gpl-9.0.tar.xz
  T=$(mktemp -d)
  curl -fsSL -o "$T/$F" "$B/$F"
  curl -fsSL -o "$T/checksums.sha256" "$B/checksums.sha256"
  (cd "$T" && grep " $F\$" checksums.sha256 | sha256sum -c -)
  tar -xf "$T/$F" -C "$T"
  rm -rf "$STUDIO/ffmpeg" && mv "$T"/ffmpeg-n9.0*/ "$STUDIO/ffmpeg" && rm -rf "$T"
fi
ln -sf "$STUDIO/ffmpeg/bin/ffmpeg" /usr/local/bin/ffmpeg
ln -sf "$STUDIO/ffmpeg/bin/ffprobe" /usr/local/bin/ffprobe

log "3/6 Blender 5.2.5 LTS, verified against blender.org SHA-256"
if ! "$STUDIO/blender/blender" --version 2>/dev/null | grep -q "5.2.5"; then
  T=$(mktemp -d)
  curl -fsSL -o "$T/blender.tar.xz" https://download.blender.org/release/Blender5.2/blender-5.2.5-linux-x64.tar.xz
  curl -fsSL -o "$T/blender.sha256" https://download.blender.org/release/Blender5.2/blender-5.2.5.sha256
  echo "$(grep linux-x64.tar.xz "$T/blender.sha256" | awk '{print $1}')  $T/blender.tar.xz" | sha256sum -c -
  tar -xf "$T/blender.tar.xz" -C "$T"
  rm -rf "$STUDIO/blender" && mv "$T/blender-5.2.5-linux-x64" "$STUDIO/blender" && rm -rf "$T"
fi
ln -sf "$STUDIO/blender/blender" /usr/local/bin/blender

log "4/6 Python 3.12 studio venv"
if [ ! -x "$STUDIO/venv/bin/python" ]; then
  uv venv --python 3.12 "$STUDIO/venv"
fi
VIRTUAL_ENV="$STUDIO/venv" uv pip install -q -r "$REPO/studio/requirements.txt"

log "5/6 local models (pinned revisions, SHA-256 manifest)"
"$STUDIO/venv/bin/python" "$REPO/studio/fetch_models.py"

log "6/6 Remotion project dependencies"
if [ -f "$REPO/Shanghai_Film/07_Motion_Graphics/remotion/package.json" ]; then
  (cd "$REPO/Shanghai_Film/07_Motion_Graphics/remotion" && npm install --no-audit --no-fund --silent)
fi

log "done"
ffmpeg -version | head -1
blender --version | head -1
"$STUDIO/venv/bin/python" -c "import cv2, av, opentimelineio, pedalboard, rembg; print('python stack ok, OpenCV', cv2.__version__)"
echo "Self-test (optional, ~12 min): $STUDIO/venv/bin/python studio/tests/run_pipeline_test.py"
