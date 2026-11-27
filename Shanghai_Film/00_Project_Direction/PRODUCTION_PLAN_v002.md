# SHANGHAI: BETWEEN TIME — Production Plan v002 (Concept 2, "Against the Current" / 逆流)

Status: **for client approval of timeline + storyboard. No final rendering has started.**
Supersedes v001 after an independent director's review (`13_Project_Documentation/handoffs/20261127_creative-director_production-plan-review.md`, verdict: approve with changes; every must-fix is addressed below, see §9).
Deliverable: 38.00 s, 1080x1920 (9:16), 24 fps, SDR Rec.709, -14 LUFS / -1 dBTP, Instagram Reels + TikTok.
Storyboard: `05_Storyboards/STORYBOARD_v002.jpg` (local only; contains the client's photos). Cue chart: `09_Audio_Music/CUE_CHART_v002.png`.
Sources and licences: `13_Project_Documentation/SOURCE_MANIFEST.md` + `source_manifest.json`.

---

## 1. Director's intent

One person stands still while their city runs backwards through its own history. The reversal is a disturbance
that grows: it leaks into the present (a drop, an aircraft), takes over at Longhua (the skyline unbuilds
itself), stops in silence, and turns forward in the water town, where time moves at the speed of an oar.
Water is the medium of time throughout: the film opens in water, the transformation happens first in water,
and it ends on the impossible image of tomorrow's city reflected in yesterday's canal, held by one breath
of a real dizi. Then a drop falls, and the film begins again.

### Time grammar
| State | Meaning | Where (picture) |
|---|---|---|
| REVERSE | the rewind, shown only by elements whose direction reads unmistakably | SH010 drop, SH030 aircraft, SH050 unbuilding |
| HELD | time stopped; stillness = presence | SH020 + SH090 (the client), SH040 (frozen flags), SH060 (pagoda alone), end of SH010 (the drop refuses to fall) |
| FORWARD | time restarting, first in deep slow motion | SH070 onward |

Rules: visible reversals escalate (a drop → an aircraft → a skyline), never two at once. The client is
always HELD, never reversed, generated or redrawn. **Sound obeys the same grammar**: reversed sound only under
REVERSE picture, with exactly three named exceptions where sound leads picture across a cut (the aircraft
pre-lap at 7.00, the rewind hit landing on 12.50, the reversed bell into the silence at 19.45).

---

## 2. Timeline (exact media per shot)

| Shot | Timecode | Dur | State | Media file(s) | Source range / framing (output 1080x1920) | Camera |
|---|---|---|---|---|---|---|
| SH010 | 0:00.00-0:03.00 | 3.00 | REVERSE → HELD | SH100 36.60-38.00 composite (reversed) + new drop hold | final framing of SH100 | locked |
| SH020 | 0:03.00-0:07.50 | 4.50 | HELD | IMG_1006.jpg, **un-mirrored** | full height → scale 0.745; window x0 0 → 483 | truck R from the Pearl sphere to the client; push 1.00 → 1.06 |
| SH030 | 0:07.50-0:10.50 | 3.00 | REVERSE (aircraft only) | IMG_1009.jpg | window x0 0, width 1134 → 0.952; aircraft at src (893, 94) | push 1.00 → 1.25 toward the aircraft |
| SH040 | 0:10.50-0:12.50 | 2.00 | HELD | IMG_1750.jpg | native 9:16 → 0.960 | tilt up + push 1.00 → 1.08 to the clock tower |
| SH050 | 0:12.50-0:18.00 | 5.50 | REVERSE | IMG_0909.jpg + unbuild layers | window x0 263, width 1134 → 0.952 | push 1.00 → 1.05 |
| SH060 | 0:18.00-0:20.00 | 2.00 | HELD | `longhua_clean` (= SH050's last frame, by construction) | same | tilt down, frame centre src y 600 → 880 |
| SH070 | 0:20.00-0:23.00 | 3.00 | FORWARD begins | `longhua_clean` → IMG_1039.mov **5.300-5.900 s** (72 fr, 5x slow) | pagoda 0.95 → 0.70; video 1.42 → 1.15, centre x 690 → 560 | descend + pull back |
| SH080 | 0:23.00-0:27.00 | 4.00 | FORWARD | IMG_1039.mov **5.900-6.700 s** (96 fr, 5x slow; canopy-free, measured) | 1.15 → 1.00 | pull back, then the clip's own bob |
| SH090 | 0:27.00-0:31.00 | 4.00 | HELD (client) in a moving world | IMG_1062.jpg + IMG_1039 wave field | full height → 0.745; window x0 483 | push 1.00 → 1.04; sun bloom 29.80-30.20 |
| SH100 | 0:31.00-0:38.00 | 7.00 | FORWARD | 20261127_160211.jpg + CC0 `shanghai_bund_8k.hdr` (Pearl Tower portrait plate) + IMG_1039 wave field + CG drop | whole photo → 0.745 at start | travels along the inverted tower toward the far end: scale 1.00 → 1.80, ending with the reflected lower sphere at screen (384, 974) |

Six cuts in 38 s. SH050 → SH080 is one unbroken 14.5 s movement.

### The drop and the palindrome (exact)
- SH100: the drop enters at the top of frame at 36.05, falls (accelerating, motion-blurred) and strikes the
  **reflected lower sphere of the Pearl Tower** at screen (384, 974) at **36.60**. Rings spread to 38.00.
- SH010 0:00.00-0:01.40 = SH100 38.00 → 36.60 played backwards: the rings converge onto the reflected sphere.
- SH010 0:01.40-0:03.00 (new, not a reversal): the drop lifts out of the surface and rises, slows and **holds**
  at (384, 930), just above the reflected sphere: the drop refuses to fall (HELD).
- T1 at 0:03.00: reflected sphere + drop → the real Pearl Tower sphere at (384, 974) in SH020: **sphere → drop →
  sphere**. No title appears in SH010. The loop seam 38.00 → 0:00.00 is frame-exact.

---

## 3. Shot notes and compositing instructions

**SH010** Night city lights broken by ripples in dark water; the rings converge on the inverted Pearl Tower's
lower sphere; a drop lifts out and hangs in the air. Rings: 2-4 irregular rings displacing the SH100 composite
(not the even, glossy rings of test f3). Drop: Blender 5.2 Cycles, refracting the plate.

**SH020** Two-layer parallax becomes **three layers**: client (BiRefNet matte, tested), the lamp-post behind the client's
head (its own matte: it is close to camera), and the river/skyline. Background reveal behind the client's edge is under
30 px and in-painted. Un-mirrored (plate text and jacket patch read correctly) — **requires the client's explicit
approval** (people know their face mirrored). Forward sound only until the aircraft pre-lap at 7.00.

**SH030** The frozen flag (held); the aircraft (28x11 px, nose left) cut out, its position filled with sky,
travelling ~150 px right, tail-first, with motion blur. Readability is tested on a phone; if it fails, the fix is
the full-resolution original and a stronger push, never a redrawn aircraft.

**SH040** Frozen flags; we hear them snapping forward in the wind and the halyard knocking the mast (S16): HELD
reads as stopped time because something we hear refuses to stop. **No film-ageing effect** (gate weave,
projector, halation removed: a stock "vintage" signal and not a progression).

**SH050** The half-built towers lose floors from the top down; the climbing cranes ride the top floor down; the
right-hand block goes the same way; the sky empties. Rhythm accelerates 2 → 10 floors/s on reversed metal thuds.
**No per-floor flash** (it would strobe and break under compression). Cranes are a separate layer moving with the
cut line. Protect pagoda, guy-wires, gold needle; rebuild the right tree crown organically (the test showed a
carved, smeared edge); de-grain and re-grain the whole sky so the filled areas cannot reappear under grading
(a 6x contrast stretch shows faint tower ghosts today).

**SH060** Continuous. The clean plate IS SH050's last frame (implemented and verified: max difference 0). Tilt
down from the finial; a reversed temple bell blooms into its strike at 19.45; 0.5 s of absolute silence.

**SH070 (signature)** Time turns forward, and water is its medium (v5 design, tested):
1. The river rises from the bottom of frame with a wavering, living waterline (not a straight wipe), its surface
   the real Zhujiajiao water, a meniscus highlight at the edge.
2. **The reflection changes first**: in the rising river, the reflected pagoda becomes the reflected pavilion,
   tier by tier from the top, hidden by real ripples; then the solid building follows.
3. The solid building is one crisp silhouette (signed-distance-field interpolation) with real texture inside on
   every frame; the guy-wires fade before the spire sinks into the pavilion's ridge (tested).
4. Skies cross blue → golden. A thin mist (≤ 0.25) hugs the waterline only; the pavilion's banks emerge from it.
5. The camera lands at full frame coverage (tested: no edge streaks).
Status and the open middle half-second: see §7 FX-07 and the decision in §8.

**SH080** The real footage, untouched except grade and high-frequency stabilisation: the sculling boat crosses in
front of the pavilion at 5x slow motion. The best moving image in the film; it is the reward after the morph.

**SH090** The client HELD on the bridge while the canal behind them **flows**, driven by IMG_1039's real wave field
(director's note D3; same proven tool as SH100, free). Three-layer parallax as SH020. Clean the green lens-flare
ghost on the client's jacket. At 29.80 the sun's flare blooms to white over 0.40 s; the white keeps a trace of image (the
sun core and the client's silhouette at ~95 %), never a flat white card.

**SH100** Out of the white, the client's point of view down the canal at golden hour. The reflection turns to night, far
end first: **the Pearl Tower, inverted and unmistakable** (tested at 1:1: both spheres, shaft and antenna
legible), running from the far end into the canal; the trees above stay golden; the real boatman and the boat
are untouched (tested; final adds the boat's own faint reflection). Colours graded into the film (neon pulled
~35 %). The camera travels along the inverted tower toward the far end. Title **35.00-36.40** inside the water,
rippled (the reflection gets ~3 s alone before any text). The drop strikes the reflected sphere at 36.60.

Title: **SHANGHAI: BETWEEN TIME / 上海 · 时光之间** (Chinese wording confirmed by a native reader before use). Noto
Serif CJK SC Light, wide tracking, warm white; inside the TikTok/Reels safe area (x 54-929, y < 1498).

---

## 4. Transitions

| # | At | From → To | Type | Motivation |
|---|---|---|---|---|
| T1 | 0:03.00 | SH010 → SH020 | match cut, position-locked | reflected sphere + drop → real Pearl sphere |
| T2 | 0:07.50 | SH020 → SH030 | eyeline cut, motivated by sound | reversed aircraft pre-laps from 7.00 |
| T3 | 0:10.50 | SH030 → SH040 | cut on movement | aircraft drifting right → tilt up |
| T4 | 0:12.50 | SH040 → SH050 | hard cut | the single rewind hit lands on the cut |
| T5-T7 | 18.00 / 20.00 / 23.00 | SH050 → SH080 | none (continuous) | one movement through the hinge |
| T8 | 0:27.00 | SH080 → SH090 | cut on an oar stroke | — |
| T9 | 0:29.80-0:31.60 | SH090 → SH100 | sun bloom to near-white (image trace kept), silence, fade from white | the client looks into the light; we see what they see |
| T10 | 0:38.00 → 0:00.00 | SH100 → SH010 | loop | the drop falls / the drop rises |

---

## 5. Music and sound

Mode **G shang (商) pentatonic**, G A C D F (F-gong system). The note S01 sounds at G6 +15 c; the xiao S02 moves on
C D F G; the erhu S03 holds F5: all in the mode, **no instrument is pitch-shifted**; drones fine-tuned +15 c. Levels
are mix-bus peak dBFS; master -14 LUFS, -1 dBTP. Sub events carry 80-200 Hz harmonics for phone speakers.

### Client choice 1: how Concept 1's continuous note enters (recommend B)
- **A. The note only at the end.** Silence of the dizi until 0:31.00, then one unbroken breath to 0:38.00.
- **B. "The fixed point in sound" (recommended).** The note's exact pitch runs from 0:00 as a near-subliminal
  thread (-36 to -30 dBFS), built from S01's own sustain (spectral freeze, breath removed), never reversed, never
  changing pitch while everything around it reverses: it is to the sound what the HELD client is to the picture.
  It stops for both silences (19.50-20.00, 30.20-31.00), so they are felt as a loss. At 0:31.00 the real dizi
  breath arrives on the note that was always there. Must pass a phone test for whine and fatigue.
Both introduce the dizi dramatically in the final seven seconds; only B also carries Concept 1's continuous note.

### Cue sheet (option B shown; option A = delete cue TH)
| Cue | In | Out | Element (source) | State | Level / automation |
|---|---|---|---|---|---|
| TH | 0:00.00 | 0:19.50 and 0:20.00-0:30.20 | the thread: S01 frozen sustain, G6 | never reversed | -36, rising to -30 by 0:12.50; holds -30; hard stop at each silence; replaced by M4 at 0:31.00 |
| A1 | 0:00.00 | 0:01.40 | canal water + drop (S12, S06), REVERSED | REVERSE | water -34; drop "inhale" peak -14 at 0:01.38 |
| A1b | 0:01.40 | 0:03.00 | one high, held water-glint tone (from S06 tail, frozen) | HELD | -30 |
| A2 | 0:03.00 | 0:12.30 | Bund city bed (S09), forward | the present | -30; fades to -50 over 10.50-12.30 |
| A3 | 0:03.00 | 0:12.30 | wind (S11), forward | — | -32 |
| A4 | **0:07.00** | 0:10.50 | aircraft fly-by (S07), REVERSED, panned L → R; **pre-lap exception** | REVERSE | peak -20 at 0:10.00 |
| M1 | 0:07.50 | 0:10.50 | erhu F5 (S03), REVERSED, its bow attack landing on T3 | REVERSE | -28 → -16 |
| A5 | 0:10.50 | 0:12.50 | flag flapping + halyard on the mast (S16), forward | HELD picture, living sound | -24 |
| SYN2 | 0:12.00 | 0:12.50 | single reverse swell landing on the cut T4; **lead-in exception** | — | peak -10 at 0:12.50 |
| A6 | 0:12.50 | 0:17.80 | metal thuds (S10), REVERSED, one per floor, 2/s → 10/s | REVERSE | each -22 |
| M2 | 0:12.50 | 0:17.95 | strings cluster (S14), REVERSED crescendo, hard stop at 18.00 | REVERSE | -30 → -10 |
| A7 | 0:12.50 | 0:18.00 | eave bells (S05), REVERSED, sparse | REVERSE | -34 |
| A8 | 0:18.00 | 0:19.45 | temple bell (S04), REVERSED bloom into strike; **hinge exception** | — | strike -12 at 0:19.45 |
| S1 | 0:19.50 | 0:20.00 | **absolute silence** | — | — |
| A9 | 0:20.00 | 0:29.90 | first FORWARD sound: one wooden creak (S13, or the client's own S15 if suitable), then canal water (S12) | FORWARD | creak -22; water -30 → -28; out 29.00-29.90 |
| A10 | 0:21.20 | 0:22.50 | one eave bell, forward (S05) | — | -30 |
| M3 | 0:21.00 | 0:29.80 | xiao (S02): phrase A = recording 8.6-13.2 s, phrase B = 28.4-35.2 s (to audition) | — | -20 → -18; out 28.00-29.80 |
| SYN4 | 0:22.00 | 0:30.20 | sub drone G1 (+15 c) + harmonics | — | -28 → -24; out 29.50-30.20 |
| S2 | 0:30.20 | 0:31.00 | **silence** on the near-white bloom | — | — |
| **M4** | **0:31.00** | **0:38.00** | **THE NOTE: dizi G6, one real breath (S01), unedited** | — | natural attack (20-50 ms anti-click ramp only), -16 rising to -12 at 35.20; **alone with the water after 36.60**; release 37.20-38.00 |
| A11 | 0:31.00 | 0:38.00 | canal water (S12) | — | -32; -28 after impact; -45 by 38.00 |
| A12 | 0:36.60 | 0:37.40 | the drop's impact (S06), forward | — | -10 |
| alt | 0:31.40 | 0:36.60 | **A/B comparison only, not the plan:** sub drone, octave halo, string harmonics, shimmer | — | added only if a phone test shows the note needs support |

### Client choice 2: source of the dizi / xiao / erhu (recommend A first, then B if needed)
- **A. Selected CC0 / CC-BY recordings** (free, available now): S01 dizi, S02 xiao, S03 erhu. Analysed from previews
  (real players: natural vibrato and drift); **the WAVs are not yet auditioned**.
- **B. A commissioned dizi/xiao player recording to picture** (remote session): the most authentic, a note played
  for this film. Cost estimate first; needs the client's OK.
- **C. A licensed sample library.**
If S01 does not sound like a living human breath at full quality, go to B. If the client's own boat audio (S15)
is usable, it outranks any library file for the forward half.

---

## 6. Assets

**Generative AI: none required.** Every image of the client is their real photograph; every environment is their
real photo/video or a licensed CC0 photograph.

| Asset | Shots | Method | Status |
|---|---|---|---|
| Longhua unbuild layers + clean plate (one source of truth) | SH050-SH070 | depth + colour segmentation, fitted sky, thin-remnant sweep | tested; continuity exact |
| Pagoda → pavilion (v5: reflection-led) | SH070 | TPS warp, SDF silhouette, rising river with reflection, waterline mist | tested v1-v5 |
| Night reflection (Pearl Tower portrait plate) | SH100, SH010 | CC0 plate, real wave field, Fresnel, graded | tested v3.1 at 1:1 |
| Canal flow behind the client | SH090 | real wave field from IMG_1039 | same tool as SH100; untested on this plate |
| CG drop + rings | SH100, SH010 | Blender 5.2 Cycles; 2-4 irregular rings | look-dev pending |
| Three-layer parallax (client, lamp-post, background) | SH020; SH090 two layers | BiRefNet mattes | mattes tested |
| Aircraft cut-out | SH030 | 2D | trivial |
| Title EN + 中文 in the water | SH100 | Remotion + water displacement | components tested |

Optional, paid, client's decision (none is required):
- **OPT-1** AI first/last-frame interpolation **for SH070's middle second only**: our two real endpoint frames,
  already geometrically aligned by the TPS warp, as first and last frame; no person in the shot (no identity risk).
  Cost estimate on request.
- **OPT-2** AI background motion behind the client in SH020 (now largely replaced by the free SH090 canal flow).

---

## 7. Feasibility (tests on the real media, 2026-11-27)

| ID | Effect | Evidence | Result | Status | Risk |
|---|---|---|---|---|---|
| FX-01 | Drop + rings | `f3_drop.py` | mechanism works; look rejected (even, glossy rings) | Feasible, look-dev | Low-med |
| FX-02 | Client mattes / parallax | `mattes_check.jpg` | clean hair, glasses, collar on all 3 photos | **Proven** | Low |
| FX-03 | Aircraft tail-first | aircraft located 28x11 px | composite trivial; phone readability untested | Feasible | Med |
| FX-05 | Clean plate + unbuild | `f5_cleanplate.py` | sky seamless at normal contrast, guy-wires kept, **end frame = clean plate (max diff 0)**; open: needle tip, tree crown, sky re-grain | Proven + 3 fixes | Low-med |
| FX-07 | Pagoda → pavilion | `f6_transform.py` … `_v5.py`, `f6_strip_v5.jpg`, full-res pass | v1 ghosting → v2 double exposure → v3 cut-out → v4 fog dissolve → **v5**: living waterline with reflection, cables fade cleanly, thin mist only, **full coverage at landing**, geometry lands exactly on the real pavilion; **the middle ~0.5 s (21.3-21.8) still reads as a collage** (sky-reconstruction streaks, hard silhouette base) | **Feasible, not yet at the brief** | **Med-high** |
| FX-08 | 120 fps conform / canopy | per-frame scan | canopy at 0-0.53, 1.81-2.89, 4.39-5.21 s; assigned 5.30-6.70 s clean | **Proven** | Low |
| FX-09 | Night reflection | `f7_reflection_v3.py`, `f7_v31_check.jpg` | inverted Pearl Tower legible at 1:1; boatman protected by a shape mask; colours graded | Feasible, near final | Low-med |
| FX-10 | Near-white bloom with image trace | standard | — | Proven | Low |
| FX-11 | Title in water | Remotion + CJK proven | — | Components proven | Low |
| FX-12 | Grade continuity | selfie (front camera) softer than other sources | grain unify | Feasible | Med |
| AX-01 | The note | S01 preview: G6 1581.6 Hz, 8.6 s, 3 Hz natural vibrato, CC0 | one breath covers 7.0 s | **Feasible (preview analysis); WAV not auditioned** | Low-med |
| AX-02 | Mode alignment | erhu F5 (9.1 s, ±6 c); xiao held C D F G | all in G shang, no shifting | Feasible (previews) | Low |
| AX-03 | Reversals, synthesis, mix, master | pipeline test (-14.0 LUFS) | — | **Proven** | Low |
| AX-04 | Client's own boat audio | tonal, 63 % in 300-3000 Hz | voices or song? | **Client must listen** | — |

Compute on this machine (1080x1920): SH070 ~1.5 min per pass (measured 84 s for v4; v5 ~2x), SH100 ~1 min per
second of shot, CG drop ~25 min; total well under 2 hours plus encodes.

### Identity steps (shots SH020, SH090)
1. Enroll the reference set (client chooses 5-10 photos; IMG_1062 is the strongest candidate here).
2. Run `identity.py check` on first, middle and last frame of both final shots.
3. Side-by-side review against the originals at full resolution (the gate cannot see subtle changes).
4. Client signs off; recorded in the provenance sidecar. Expected outcome: unaltered real pixels pass trivially;
   the steps exist to catch any accidental change from parallax warping or grading.

---

## 8. Decisions requested from the client

1. **Approve the timeline (§2) and storyboard v002**, or give notes. Final rendering waits for this.
2. **Choice 1**: the note A or **B (recommended)** (§5).
3. **Choice 2**: music source **A first (recommended)**, B commissioned, or C library (§5).
4. **SH070's middle second**: (a) one or two more local iterations (art-directed tier-by-tier swap, proper sky
   reconstruction) — free, no guarantee; or (b) OPT-1 AI interpolation between our two real aligned frames — paid,
   estimate first. Recommendation: (a), with (b) as the fallback if (a) does not reach the brief.
5. Approve the **un-mirrored** selfie in SH020.
6. Listen to IMG_1039's own audio: boatman's song, guide, or chatter?
7. Full-resolution originals of IMG_1006, IMG_1009, IMG_1062, IMG_1750, IMG_0909, 20261127_160211 (the uploads were
   resized and stripped of metadata) — they improve SH030 readability and all push-ins.
8. A free Freesound login (or download the listed WAVs yourself) for the selected sounds.
9. Chinese title wording 上海 · 时光之间 (or your phrasing), native-reader checked.
10. Jacket logo visible in SH020 and SH090: keep as is?

---

## 9. How the director's review was resolved

| Note | Resolution |
|---|---|
| C1 instruction 4 as a choice | §5 Choice 1 (A/B), B recommended |
| C2 palindrome | §2 "The drop and the palindrome": SH010 = SH100 36.60-38.00 reversed + HELD drop; drop path written; no title in SH010; storyboard SH010 replaced |
| C3 SH070 v5 | built and tested (§3, FX-07); waterline, mist ≤ 0.25 at the waterline only, real texture inside the silhouette, full coverage, cables fade; middle half-second remains open → decision §8.4; storyboard shows start / middle / landing, labelled TEST |
| C4 SH100 recognisable + camera along it + grade | Pearl Tower portrait plate, inverted tower runs into the canal, legible at 1:1; camera travels along it to the reflected sphere; neon pulled ~35 %; boat-shape protection; storyboard labelled TEST with placeholder title |
| C5 sound grammar | reversed sound only under REVERSE picture + three named exceptions; SYN2 reduced to one hit; A8b removed; SYN3 removed |
| C6 identity | §7 identity steps; un-mirror approval §8.5; lamp-post as a third parallax layer |
| C7 music source | §5 Choice 2; AX-01 reworded; audio logged in asset_licences.json on download |
| C8 clean plate | continuity exact by construction (verified); crown, sky re-grain, needle listed |
| D1 water as the medium | adopted in SH070 v5 |
| D2 drop on the reflected sphere | adopted (T1 sphere → drop → sphere) |
| D3 canal flows behind the client | adopted in SH090 (free; replaces most of OPT-2) |
| D4 single note, natural attack | adopted; supports only as A/B |
| D5 title later | 35.00-36.40 |
| D6 sound makes cuts legible | aircraft pre-lap 7.00; flags heard in SH040 |
| E clichés | film ageing removed; per-floor flash removed; mist confined; T9 keeps image; SH100 hold limited by the camera move |
