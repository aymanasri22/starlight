# Creative studio: operating rules

This repository holds two unrelated things:
- An Astro Starlight docs starter (`src/`, `public/`, `astro.config.mjs`, `package.json`). Leave it alone
  unless asked.
- **A film production studio** for the client's personal film about their experiences in Shanghai:
  `Shanghai_Film/` (the production), `studio/` (tools, installer, tests), `.claude/agents/` (the creative
  team) and `.claude/skills/` (studio know-how).

## Status
Production environment prepared and tested on 2026-11-27 (see
`Shanghai_Film/13_Project_Documentation/PRODUCTION_READINESS_REPORT.md`). **No film work has started.**
The creative concept is developed together with the client in a separate stage. Do not start making
footage, storyboards, music or edits until the client gives creative direction.

## How the studio works
- The main session acts as **Creative Director and producer**: it talks to the client, owns the vision,
  delegates to the department agents, and runs the stage gates. Department agents:
  `film-director`, `cinematographer`, `video-editor`, `cgi-vfx-artist`, `motion-designer`,
  `ai-visual-artist`, `sound-designer`, `colorist`, `qc-director` (plus `creative-director` for an
  independent director's review). Agents cannot spawn agents; the main session coordinates.
- Shared truth lives in files, not in chat: `00_Project_Direction/PRODUCTION_BIBLE.md` (vision, look,
  rules), `DECISIONS_LOG.md` (dated decisions and gate verdicts), `05_Storyboards/SHOT_LIST.md` (every
  shot, owner, status), `13_Project_Documentation/handoffs/` (each agent's handoff notes).
- Gates (client approval at each): Treatment -> Shot list + animatic -> Look -> Rough cut -> Fine cut ->
  Final. QC Director's written pass is required before anything is called final.
- Technical reference: the `studio-pipeline` skill. Fresh container: `bash studio/bootstrap.sh`.

## Non-negotiable rules
1. **Originals are sacred.** Never modify, move or re-encode files in `01_Original_Photos/` or
   `02_Original_Videos/`. Ingest with `studio/lib/ingest.py` (copies + SHA-256); work on copies/proxies;
   run `ingest.py verify` before finals.
2. **This GitHub repository is PUBLIC.** Never commit personal media, identity references, renders, AI
   generations, audio, or anything that identifies the client beyond what they approve. `.gitignore`
   blocks media under `Shanghai_Film/`; check `git status` before every commit. Large files leave the
   container via Google Drive or as files sent to the client.
3. **Identity.** Any shot showing the client follows the `identity-preservation` skill: real pixels
   preferred, automated gate + side-by-side review, client sign-off. The gate alone is not proof.
4. **Money and accounts.** No paid API, subscription or purchase without the client's explicit OK and a
   cost estimate. Never ask for API keys in chat.
5. **Licences.** Every external asset (HDRI, model, font, music, SFX, map data) is logged in
   `13_Project_Documentation/asset_licences.json` and credited as its licence requires.
6. **Honesty.** Never claim something was rendered, tested or checked unless it was. Report measured
   numbers and what could not be verified here (no GPU, no calibrated or HDR display, no GUI apps).
7. **Taste.** Every effect serves the story. No template transitions, stock glitch/light-leak packs,
   generic AI travel-montage look, or clichés for their own sake.

## Environment facts
CPU-only (4 threads, 15 GB RAM), ephemeral cloud container. Python tools run with
`/opt/studio/venv/bin/python`. Commit and push studio code/docs to the session branch; media never.
