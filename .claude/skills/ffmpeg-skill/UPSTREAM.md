# Vendored third-party skill — ffmpeg-skill

- Source: https://github.com/kajisho5/ffmpeg-skill
- Pinned commit: b9087dce5cfc134689abaab89d0cb6f55e2a668d (2026-11-27)
- License: MIT (see LICENSE)
- Copied: SKILL.md, scripts/, references/, templates/, docs/contract.md, LICENSE.
  Not copied: demos/, assets/, the npm installer, the MCP server (Bash runs the scripts directly).
- Audit (2026-11-27): scripts are standard-library Python that call ffmpeg/ffprobe via argument
  lists; no network calls, no shell=True, no eval/exec, no telemetry (PRIVACY.md states none).
- Update: re-clone, re-audit, re-copy. Never pull updates blindly.
