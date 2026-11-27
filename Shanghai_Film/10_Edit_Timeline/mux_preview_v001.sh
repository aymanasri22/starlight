#!/usr/bin/env bash
# Mux preview v001 picture + preview master (-14 LUFS, -1 dBTP) into one review file, then run basic technical QC.
# Local outputs only (git-ignored). Not a final deliverable.
set -euo pipefail
cd "$(dirname "$0")"
PIC=preview_v001/picture.mp4
AUD=../09_Audio_Music/mix/preview_master_v001.wav
OUT=preview_v001/SHANGHAI_BETWEEN_TIME_preview_v001.mp4
ffmpeg -hide_banner -loglevel error -y -i "$PIC" -i "$AUD" -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset slow -crf 19 -profile:v high -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart -t 38.0 "$OUT"
echo "== streams"
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames,duration,sample_rate,channels,color_primaries \
  -of compact "$OUT"
echo "== size"; du -h "$OUT"
echo "== loudness (EBU R128, from the muxed AAC)"
ffmpeg -hide_banner -nostats -i "$OUT" -map 0:a -af ebur128=peak=true -f null - 2>&1 | grep -A12 "Summary:" | grep -E "I:|LRA:|Peak:"
echo "== black frames (> 0.2 s)"
ffmpeg -hide_banner -nostats -i "$OUT" -vf blackdetect=d=0.2:pix_th=0.08 -an -f null - 2>&1 | grep -c blackdetect || true
