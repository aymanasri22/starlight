# Pipeline test results

Run: 2026-11-27 10:52 UTC on 4 CPU threads, no GPU. ffmpeg version n9.0.2-982-g836df4e858-20261126 Copyright (c) 2000-2026 the FFmpeg developers; Blender 5.2.5 LTS.

| Stage | Result | Time | Key numbers |
|---|---|---|---|
| Generate harmless sample media (camera-card simulation) | **PASS** | 21.8s |  |
| Non-destructive ingest: hash, lock, catalogue, proxies, integrity verify | **PASS** | 10.5s | seconds: 10.5; hdr_clip: {'codec': 'hevc', 'color_transfer': 'arib-std-b67', 'color_primaries': 'bt2020', 'bit_depth': None, 'fps': 30.0} |
| Photo -> depth map -> 2.5D parallax camera move | **PASS** | 18.0s | frames: 72; codec: prores HQ; depth_seconds: 1.5; render_seconds: 14.9; sec_per_frame_1080p: 0.21 |
| Fetch public-domain test portraits (NASA) | **PASS** | 0.3s | credit: NASA (public domain); scikit-image astronaut (NASA, PD) |
| Identity-preservation gate (YuNet + SFace) | **PASS** | 3.6s | drift_similarity_drop: -0.062 |
| Person matte (rembg BiRefNet-portrait) + composite onto plate | **PASS** | 36.9s | seconds_512px: 36.6; alpha_coverage: 0.509; note: composite is a raw matte test; real shots need light/grade/grain matching and a contact shadow |
| Blender 5.2 LTS headless: HDRI-lit CGI on shadow catcher, composited (Cycles CPU) | **PASS** | 58.5s | seconds_two_renders_720p_64spp: 56.7; shadow_pixels: 44108; plate_vs_blender_luma_ncc: 0.952; plate_vs_blender_shift_px: 0.031 |
| Remotion kinetic title (ProRes 4444 alpha) composited over a shot | **PASS** | 21.5s | pix_fmt: yuva444p12le; render_seconds_96f_1080p: 12.7 |
| Stabilisation (vid.stab two-pass) with measured residual shake | **PASS** | 11.0s | shake_px_per_frame_before: 10.64; shake_px_per_frame_after: 0.31; reduction: 97%; seconds: 9.7 |
| HDR (HLG) phone footage -> Rec.709 SDR conform | **PASS** | 9.1s | out_tags: bt709/bt709/bt709 yuv422p10le |
| Sound design: synthesized SFX, mix, master to -14 LUFS / -1 dBTP | **PASS** | 9.2s | integrated_lufs: -14.0; lra_lu: 2.0; true_peak_dbtp: -2.8 |
| Conform mixed sources + transitions + speed ramp -> ProRes master; OTIO/EDL/FCPXML export | **PASS** | 35.8s | audio_duration_s: 11.0; otio_timeline_duration_s: 11.0; duration_s: 11.0; expected_s: 11.0; video: prores HQ yuv422p10le; render_seconds: 33.0; timeline_exports: ['pipeline_test_seq.edl', 'pipeline_test_seq.fcpxml', 'pipeline_test_seq.otio', 'pipeline_test_seq.xml']; otio_reimport_items: 5 |
| Look development: authored .cube LUT applied with grain + vignette | **PASS** | 27.3s | lut: 33^3 .cube (Resolve/Premiere/FCP compatible) |
| Delivery encodes: 1080p H.264, 4K HEVC 10-bit, 9:16 vertical | **PASS** | 403.3s | encode_seconds_for_11s: {'hd_h264': 25.7, 'uhd_h265_10bit': 355.3, 'vertical_9x16_h264': 22.4}; note: 4K file is an encode-path test from a 1080p timeline (upscaled), not a quality claim |
| Technical QC + VMAF + vendored ffmpeg-skill check/look | **PASS** | 15.7s | vertical_qc: PASS; vertical_sar: SAR 1:1; studio_qc: PASS; vmaf_hd_vs_master: 97.142365; ffmpeg_skill_check_exit: 0; ffmpeg_skill_check: {
  "status": "completed",
  "output": null,
  "dry_run": false,
  "verified": false,
  "commands": 1,
  "lossless": false,
  "platform": "youtube",
  "checks": [
    {
      "check": "duration",
      "status": "PASS",
      "value": "11.00s",
      "expected": "<= 43200s",
      " |
| Shot-boundary detection on a cut (PySceneDetect) | **PASS** | 2.7s | shots_found: 3; cut_times_s: [3.0, 8.0]; hard_cuts_expected: [3.0, 8.0]; dissolve_5.5_6.0_detected: False; note: ContentDetector finds hard cuts; dissolves need AdaptiveDetector/ThresholdDetector tuning |
| Animated-map basis: OpenStreetMap buildings (Lujiazui) -> extruded 3D city in Blender | **PASS** | 12.7s | buildings: 276; with_height: 53; tallest: ['上海中心大厦 632 m', '上海环球金融中心 492 m', '金茂大厦 420 m']; render_seconds: 12.7; licence: ODbL: credit (c) OpenStreetMap contributors |
