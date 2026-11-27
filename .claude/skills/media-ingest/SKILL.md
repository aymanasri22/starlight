---
name: media-ingest
description: Bring the client's photos and videos into the film non-destructively. Use when the client uploads media, shares a Google Drive folder, or asks to "add/import/use these photos/videos"; covers download, SHA-256 catalogue, read-only originals, metadata (time, GPS, camera, HDR), proxies, contact sheets and selects.
---

# Media ingest (originals are sacred)

## Getting the files into the container
1. **Google Drive (preferred for many/large files):** the client puts originals in a Drive folder; use the
   Google Drive connector (`search_files`, `download_file_content`) to download them into a staging
   folder outside git, e.g. `/tmp/ingest_<date>/`. (`studio/tests/out/` is for synthetic test data only.)
2. **Direct upload** into the session: files land in the session's upload location; move a COPY to staging.
3. Ask for full-quality originals (iPhone: "Export Unmodified Original", or AirDrop/Drive with original
   quality). Messaging apps (WeChat, WhatsApp) recompress: avoid them as a source.

## Ingest
```bash
PY=/opt/studio/venv/bin/python
$PY studio/lib/ingest.py import /tmp/ingest_<date>/        # copy + hash + read-only + catalogue + proxies
$PY studio/lib/ingest.py verify                              # re-hash all originals against the catalogue
```
- Originals go to `Shanghai_Film/01_Original_Photos` / `02_Original_Videos`, chmod 444, SHA-256 in
  `13_Project_Documentation/media_catalog.json` (git-ignored with the rest of the media).
- Running as root makes file permissions advisory; the hash catalogue is the real integrity check. Run
  `verify` before every final render.
- Corrupt or truncated files are kept, flagged `"status": "unreadable"`, and reported; ask the client
  to re-send them.

## What to read from the catalogue
- `exif.DateTimeOriginal` + `OffsetTimeOriginal` (+08:00 = Shanghai) -> chronology of the trip.
- `exif.GPSLatitude/Longitude` -> places on the map (Bund, Lujiazui, Yu Garden, French Concession...).
- `video.hdr` / `color_transfer` (`arib-std-b67` = HLG, `smpte2084` = PQ) -> must go through
  `grade.py hdr2sdr` before grading; `video.dolby_vision`; `fps` (30/60 phone footage), `rotation`.
- Camera/lens -> which shots can cut together; resolution -> what each shot can honestly support.

## After ingest
1. Make contact sheets of every clip (`qc.py sheet`) and a grid of photos; LOOK at them.
2. Cinematographer grades selects A/B/C; Director picks story moments. Record selects in
   `03_Selected_Media/SELECTS.md` (file, why, rating, notes). Proxies live in `03_Selected_Media/proxies/`.
3. Identity references: with the client, choose 5-10 clear photos of their face (front, 3/4, both sides,
   different light), copy them into `00_Project_Direction/identity_reference/`, and enroll
   (`identity-preservation` skill).
