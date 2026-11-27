# Shanghai Film: production workspace

Personal film about the client's experiences in Shanghai. Prepared 2026-11-27; creative development
has not started. Rules: see `/CLAUDE.md`. Tools: `/studio/` and the `studio-pipeline` skill.

| Folder | Contents | In git? |
|---|---|---|
| `00_Project_Direction/` | Production bible, decisions log, treatment; `identity_reference/` (client face references, never committed) | text only |
| `01_Original_Photos/` | Client's original photos: read-only, SHA-256 catalogued, never modified | no |
| `02_Original_Videos/` | Client's original videos: read-only, SHA-256 catalogued, never modified | no |
| `03_Selected_Media/` | Selects list, proxies (`proxies/`), working copies | text only |
| `04_AI_Generated_Assets/` | Generated images/video, each with a provenance sidecar JSON | text only |
| `05_Storyboards/` | Shot list (single source of truth), boards, animatic | text only |
| `06_CGI_3D/` | `blend/` scenes, `hdri/` (CC0), `renders/` | text only |
| `07_Motion_Graphics/` | `remotion/` project (source in git), renders | source only |
| `08_VFX_Compositing/` | Per-shot comps, mattes, clean plates | text only |
| `09_Audio_Music/` | `music/` (licensed), `sfx/`, `stems/`, `mix/` | text only |
| `10_Edit_Timeline/` | Edit decision JSON, OTIO/EDL/FCPXML exports, review cuts | timelines only |
| `11_Color_Grading/` | `luts/` (.cube in git), reference `stills/` | LUTs only |
| `12_Final_Renders/` | Masters and platform deliveries | no |
| `13_Project_Documentation/` | Readiness report, catalogue, licences, handoffs, QC reports, pipeline test evidence | text + test evidence |

Naming: `SH<nnn>_<desc>_v<nnn>.<ext>` using shot IDs from `05_Storyboards/SHOT_LIST.md`; version up,
never overwrite a reviewed file.
