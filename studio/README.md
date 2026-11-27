# studio/: the production toolchain

Reusable, tested tools for the film studio. Everything is a CLI (`--help` on each).

```
studio/
  bootstrap.sh          rebuild the toolchain in a fresh container (idempotent, checksum-verified)
  requirements.txt      Python 3.12 studio venv (/opt/studio/venv)
  fetch_models.py       local CPU models, pinned + SHA-256 manifest
  lib/
    common.py           shared helpers (run, probe, sha256, bt709 tagging, guided filter)
    ingest.py           non-destructive ingest: copy, hash, lock, catalogue, proxies; verify
    identity.py         likeness gate: enroll reference faces, check stills/video (YuNet + SFace)
    depth_parallax.py   photo -> depth -> 2.5D camera move
    matte.py            person/subject mattes (rembg BiRefNet / U2-Net)
    assets.py           Poly Haven CC0 HDRIs, HDRI -> perspective plate, OpenStreetMap buildings
    grade.py            HDR -> Rec.709, look LUT authoring (.cube), LUT/grain/vignette apply
    audio.py            SFX synthesis, stem mixing, loudness mastering, EBU R128 measurement
    timeline.py         edit JSON -> conformed render; OTIO / EDL / FCPXML / FCP7 XML export
    deliver.py          delivery profiles (ProRes/DNxHR masters, 4K HEVC/H.264, 1080p, 9:16, 1:1)
    qc.py               technical QC report + timecoded contact sheets
  blender/
    integrate_cgi.py    HDRI-lit CGI on a shadow catcher with a matched camera (Cycles/EEVEE)
    osm_city.py         OpenStreetMap footprints -> extruded 3D city
  tests/
    run_pipeline_test.py  end-to-end test with harmless assets; evidence -> Shanghai_Film/13_Project_Documentation/pipeline_test/
```

Run Python tools with `/opt/studio/venv/bin/python`. Outputs of the self-test go to `studio/tests/out/`
(git-ignored).
