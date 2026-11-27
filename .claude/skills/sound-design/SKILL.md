---
name: sound-design
description: Sound for the film: location audio clean-up, Shanghai ambience beds, designed transitions (risers, impacts, whooshes, sub drops), music selection/licensing and editing to picture, mixing and loudness-compliant mastering (-14 LUFS web, -23 EBU R128), stems and sync checks. Use whenever audio is touched.
---

# Sound design and mix

## Building blocks (`studio/lib/audio.py`, verified)
```bash
$PY studio/lib/audio.py sfx riser   --out 09_Audio_Music/sfx/riser_01.wav --seconds 2.5
$PY studio/lib/audio.py sfx impact  --out .../impact_01.wav     # also: whoosh, roomtone, sub
$PY studio/lib/audio.py mix bed.wav@-6@0 riser.wav@-10@0.4 impact.wav@-3@2.9 --out mix.wav --reverb 0.08
$PY studio/lib/audio.py master mix.wav master.wav --lufs -14 --tp -1.0
$PY studio/lib/audio.py measure master.wav                          # EBU R128 integrated / LRA / true peak
```
`STEM@gain_dB@start_seconds`: place sounds on the timeline by the cut times from the edit JSON.
pedalboard is available for EQ, compression, reverb, delay, chorus, pitch shift and limiting in custom
scripts; librosa for tempo/beat/onset detection to align cuts with music phrases.

## Layers and intent
1. **Production sound** from the client's videos: extract (`ffmpeg -i clip -vn -c:a pcm_s24le`), clean
   (high-pass, de-noise gently), keep real voices and real city.
2. **Ambience beds** per location: the Bund (river, horns, crowds), metro, alleys (lilong), markets,
   rain. Prefer the client's own recordings; otherwise licensed libraries or Freesound CC0/CC-BY
   (attribute). Synthesized roomtone fills gaps.
3. **Spot effects** synced to visible actions.
4. **Designed transitions** that match picture motion and land on cuts. Restraint: if everything
   whooshes, nothing does.
5. **Music**: licensed only. Options to present to the client: a library subscription (e.g. Artlist,
   Musicbed, Epidemic Sound), a commissioned/original score, CC-BY tracks with attribution, or AI music
   only from services whose terms grant the needed rights. Log every licence in asset_licences.json.

## Mix and master
- Dialogue/voice (if any) is king; music ducks under it (sidechain or manual rides).
- Targets: web/streaming -14 LUFS integrated, true peak <= -1 dBTP; broadcast/festival -23 LUFS
  (EBU R128) or -24 LKFS (ATSC A/85) on request. 48 kHz / 24-bit masters.
- Deliver stems (DX/MX/FX) and an M&E mix alongside the full mix.
- QC: `qc.py check` reports loudness, true peak and A/V duration; listen to the whole film start to end
  on headphones AND small speakers (phones are where most people will hear it).
