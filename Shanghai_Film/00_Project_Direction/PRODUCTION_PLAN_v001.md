# SHANGHAI: BETWEEN TIME — Production Plan v001 (Concept 2, "Against the Current" / 逆流)

Status: **awaiting client approval of timeline + storyboard. No final rendering has started.**
Deliverable: 38.00 s, 1080x1920 (9:16), 24 fps, SDR Rec.709, -14 LUFS / -1 dBTP, Reels + TikTok.
Storyboard: `05_Storyboards/STORYBOARD_v001.jpg` (local only: contains the client's photos).
Feasibility evidence: `08_VFX_Compositing/feasibility/` (scripts in git; frames/clips local only).
Sources and licences: `13_Project_Documentation/SOURCE_MANIFEST.md` + `source_manifest.json`.

---

## 1. Director's intent

One person stands still while their city runs backwards through its own history. The reversal is not a filter;
it is a disturbance that grows. It leaks into the present (a drop, an aircraft), takes over at Longhua
(the skyline unbuilds itself), stops in silence, and turns forward in the water town, where time moves
again at the speed of an oar. The last seven seconds give the film its voice: one breath of a real dizi,
held over the impossible image of tomorrow's city reflected in yesterday's canal. Then a drop falls, and
the film begins again, because its first shot is its last shot played backwards.

### Time grammar (the rule that keeps the effect selective)
| State | Meaning | Where |
|---|---|---|
| **REVERSE** | the rewind, visible only in elements whose direction reads unmistakably | SH010 drop, SH030 aircraft, SH050 unbuilding |
| **HELD** | time stopped; stillness = presence | SH020, SH090 (the client), SH040 (frozen flags), SH060 (the pagoda alone) |
| **FORWARD** | time restarting, first in deep slow motion | SH070 onward |

- Visible reversals escalate in scale: a drop → an aircraft → an entire skyline. Never two at once.
- The client is always HELD: never reversed, never generated, never redrawn.
- Sound follows the same grammar: reversed sounds only in REVERSE moments; the present stays forward
  underneath, so the rewind is felt as an intrusion, not a gimmick.

---

## 2. Shot-by-shot timeline (exact media per shot)

Output frame 1080x1920. "Scale" = output pixels per source pixel. Source times for IMG_1039 are in the
original clip (120 fps); 5x slow motion = 1 source frame per output frame.

| Shot | Timecode | Dur | State | Media file(s) | Source range / framing | Camera |
|---|---|---|---|---|---|---|
| SH010 | 0:00.00-0:03.00 | 3.00 | REVERSE | SH100's final 3.00 s composite, time-reversed (20261127_160211.jpg + CC0 `shanghai_bund_8k.hdr` night plate + CG drop) | as SH100 end framing | as SH100, reversed |
| SH020 | 0:03.00-0:07.50 | 4.50 | HELD | IMG_1006.jpg **un-mirrored** | full height 2576 px → scale 0.745; 9:16 window x0 0 → 483 | truck right from the Pearl Tower sphere to the client; push 1.00 → 1.06 |
| SH030 | 0:07.50-0:10.50 | 3.00 | REVERSE (aircraft only) | IMG_1009.jpg | window x0 0, width 1134 → scale 0.952; aircraft at src (893, 94) | push 1.00 → 1.25 toward the aircraft, drift up-right |
| SH040 | 0:10.50-0:12.50 | 2.00 | HELD | IMG_1750.jpg | native 9:16 (1125x2000) → scale 0.960 | tilt up + push 1.00 → 1.08 toward the clock tower |
| SH050 | 0:12.50-0:18.00 | 5.50 | REVERSE | IMG_0909.jpg + derived clean plate `longhua_clean` | window x0 263, width 1134 → scale 0.952 | slow push 1.00 → 1.05 on the pagoda |
| SH060 | 0:18.00-0:20.00 | 2.00 | HELD | `longhua_clean` (continuous, no cut) | same | tilt down: frame centre src y 600 → 880 (spire → tiers 1-3) |
| SH070 | 0:20.00-0:23.00 | 3.00 | FORWARD begins | `longhua_clean` → IMG_1039.mov | IMG_1039 **5.300-5.900 s** (72 frames, 5x slow) | descend + pull back; pagoda scale 0.95 → 0.70, video scale 1.42 → 1.15 |
| SH080 | 0:23.00-0:27.00 | 4.00 | FORWARD | IMG_1039.mov (continuous, no cut) | **5.900-6.700 s** (96 frames, 5x slow); canopy-free range (measured) | pull back 1.15 → 1.00 over 1.5 s, then the clip's own gentle bob |
| SH090 | 0:27.00-0:31.00 | 4.00 | HELD | IMG_1062.jpg | full height → scale 0.745; window x0 483; sun at src (850, 689) | push 1.00 → 1.04 toward the face; sun bloom 29.80-30.20 |
| SH100 | 0:31.00-0:38.00 | 7.00 | FORWARD | 20261127_160211.jpg + CC0 `shanghai_bund_8k.hdr` + IMG_1039 wave field + CG drop | full photo (native 9:16) → scale 0.745 | their point of view down the canal; push + tilt to the near water 1.00 → 1.35 by 36.60 |

Cuts: six in 38 seconds. SH050 → SH080 is one unbroken 14.5-second movement.

---

## 3. Shot notes and compositing instructions

**SH010 THE DROP (reverse)** — the end played backwards. Coloured city lights shimmer in dark water;
ripples converge; the reflection breaks up; one drop lifts out of the surface and rises to screen point
(384, 974), the exact position of the Pearl Tower's lower sphere in SH020's first frame.
Build: render SH100's last 72 frames, reverse them. Ripples: 2-4 irregular rings (not the even rings of
test f3), displacing the composite; ring crests catch only what the water reflects (no white stripes).
Drop: Cycles CG droplet, refracting the same plate, motion-blurred, 1080x1920.

**SH020 THE FIXED POINT (held)** — first frame: the Pearl Tower sphere where the drop was. The camera
trucks right across the river to the client, perfectly still. Two-layer parallax: BiRefNet matte
(tested, clean hair and sunglasses edges) as the foreground layer; background strip behind their edge
in-painted (parallax reveal is under 30 px). Selfie un-mirrored (lamp-post text and jacket patch now read
correctly). No relighting, no smoothing of the face. Grade: crisp Bund morning blue.

**SH030 THE RETREATING AIRCRAFT** — they look up; cut to the sky. The frozen flag on the old tower
(held). The aircraft (28x11 px, nose pointing left) is cut out, its original position filled with sky,
and it travels ~150 output px to the right, tail-first, with matching motion blur. The push-in makes it
readable on a phone; the reversed jet sound sells the direction.

**SH040 THE BUND HOLDS ITS BREATH** — flags frozen mid-flutter. As we tilt up to the clock tower the
image ages: grain 0.10 → 0.35, saturation -10 %, a breath of halation on highlights, 1 px gate weave in
the last 0.5 s. The present recedes in the sound.

**SH050 UNBUILDING** — the signature reversal. Behind the pagoda, the half-built towers lose their floors
from the top down, the climbing cranes riding the top floor down as real tower cranes climb up; the
modern block on the right dissolves the same way; the sky empties. Rhythm accelerates 2 → 10 floors per
second, each floor landing on a reversed metal thud. Build: clean plate (tested), per-column descending
cut line quantised to ~34 px floors, 1-frame bright edge per floor, cranes as a separate layer translated
with the cut line. Protect: pagoda, guy-wires (tested), gold finial needle (fix), foliage edge on the
right (foliage matte + colour decontamination; test showed a smear).

**SH060 THE PAGODA ALONE** — continuous from SH050. The sky is clean; the camera tilts down from the
finial to the upper tiers. A reversed temple bell blooms into its strike at 19.45. Then 0.5 s of absolute
silence (19.50-20.00), the hinge of the film.

**SH070 THE TRANSFORMATION (signature)** — continuous. Time turns forward. Method proven in tests v1-v4
(`f6_transform_v4.py`):
1. Ten matched points (eave tips of tiers 1-4, roof crown, spire top → pavilion ridge) drive a
   thin-plate-spline warp of BOTH images inside one camera move (descend + pull back).
2. One crisp silhouette: signed-distance-field interpolation between the pagoda and pavilion mattes
   (no transparency, no double exposure). Inside it, dark rooflines persist longest; the spire sinks into
   the pavilion's ridge.
3. Skies cross separately: Longhua's hard blue → Zhujiajiao's golden haze.
4. Surroundings exchange behind a brief river mist (peak at 0:21.00, strength 0.62), Zhujiajiao's banks
   emerging from it; the hero roofline stays readable through the mist.
5. The river rises from the bottom of frame to the pavilion's bank, swallowing Longhua's trees.
To finish for final: rippled, reflective rising waterline (re-use the SH100 water model); feathered base
of the silhouette; land the camera at full frame coverage (no edge streaks); grain-match; full res.

**SH080 THE CROSSING** — the real footage, forward, at 5x slow motion: the sculling boat crosses in front
of the pavilion. The camera finishes its pull-back to 1:1. Untouched except grade and light
stabilisation of high-frequency jitter (keep the natural bob).

**SH090 THE WITNESS (held)** — the client on the bridge, sun above and to the left of their head. Two-layer
parallax (tested matte), push toward their face. Clean up the green lens-flare ghost on their jacket. At
29.80 the sun's flare blooms to white over 0.40 s.

**SH100 THE REFLECTION** — out of white, the client's point of view: the canal below the bridge, golden afternoon.
As the note enters, the reflection in the water turns to night: Lujiazui, inverted, shimmering in an
ancient canal while the trees above stay golden (method proven in `f7_reflection.py`: CC0 night
photograph, real wave field from IMG_1039, Fresnel, light pillars, near-black water, the real boatman and
the boat untouched). The far end turns first. The title rises inside the water (34.00-36.40), rippled by
the same waves. A drop falls (36.20-36.60) and strikes at 36.60; rings spread; the note continues alone
and fades by 38.00; loop to SH010. To finish: crisper far-field so the inverted Pearl Tower is
unmistakable; 2-4 irregular rings; title look-dev.

Title: **SHANGHAI: BETWEEN TIME** / **上海 · 时光之间** (Chinese wording to be confirmed by a native reader).
Noto Serif CJK SC Light for both scripts, wide tracking, warm white; rendered in Remotion, then passed
through the water displacement. Placement inside the TikTok/Reels safe area (x 54-929, y < 1498).

---

## 4. Transitions

| # | At | From → To | Type | Motivation |
|---|---|---|---|---|
| T1 | 0:03.00 | SH010 → SH020 | match cut, position-locked | rising drop → Pearl Tower sphere (same screen point, similar size) |
| T2 | 0:07.50 | SH020 → SH030 | eyeline cut | the client looks up → the sky |
| T3 | 0:10.50 | SH030 → SH040 | cut on movement | aircraft drifting right → tilt up the facade |
| T4 | 0:12.50 | SH040 → SH050 | hard cut on the reversed erhu's attack | the rewind engages |
| T5 | 0:18.00 | SH050 → SH060 | none (continuous) | — |
| T6 | 0:20.00 | SH060 → SH070 | none: morph begins out of silence | time turns forward |
| T7 | 0:23.00 | SH070 → SH080 | none: lands in live footage | — |
| T8 | 0:27.00 | SH080 → SH090 | cut on an oar stroke (sound) | the crossing → the witness |
| T9 | 0:29.80-0:31.60 | SH090 → SH100 | sun bloom to white, 0.8 s white + silence, fade from white | the client looks into the light; we see what they see |
| T10 | 0:38.00 → 0:00.00 | SH100 → SH010 | loop (palindrome) | the drop falls / the drop rises |

No other transitions. No template effects.

---

## 5. Music and sound cue sheet

Mode: **G shang (商) pentatonic**, G A C D F (F-gong system), a traditional Chinese mode. The note (S01)
sounds at G6 +15 cents; the xiao recording (S02) moves on C, D, F, G and the erhu (S03) holds F5: both
already belong to the mode, so **no instrument is pitch-shifted**; drones sit on G, fine-tuned +15 cents
to the dizi. Levels are mix-bus peaks in dBFS before mastering; master
-14 LUFS integrated, -1 dBTP. Sub events carry a saturated 80-200 Hz layer so phones reproduce them; the
note (1.58 kHz) sits in the phone's most sensitive band and is kept smooth (gentle 3-6 kHz control).
Source IDs → `SOURCE_MANIFEST.md`. SYN = synthesised in-house (original).

**Interpretation of the brief:** the note from Concept 1 is introduced dramatically at 0:31.00 and is
*continuous* from there: one unbroken breath to the end. Nothing before 0:31.00 uses the dizi, so its first
appearance is its entrance.

| Cue | In | Out | Element (source) | Processing | Level / automation |
|---|---|---|---|---|---|
| A1 | 0:00.00 | 0:02.92 | Canal water (S12) + water drop (S06), REVERSED | drop reversed = an inhale | water -34; drop peak -14 at 0:02.70; 80 ms gap before cut |
| SYN1 | 0:00.00 | 0:02.92 | reverse sub swell (G1 + harmonics) | reversed decay | -40 → -12 at 0:02.90 |
| A2 | 0:03.00 | 0:12.30 | Bund city bed (S09), FORWARD (the present) | LPF 8 kHz | -30; fades to -50 over 0:10.50-0:12.30 |
| A3 | 0:03.00 | 0:12.30 | wind (S11), forward | — | -32 |
| SYN2 | 0:03.00 | 0:12.00 | "rewind pulse": reversed sub hits at 3.00, 4.50, 6.00, 7.50, 9.00, 10.50, 11.25, 12.00 | 500 ms reverse swells | each peak -12 |
| A4 | 0:07.50 | 0:10.50 | aircraft fly-by (S07), REVERSED, panned L → R with the aircraft | Doppler reversed | peak -20 at 0:10.00 |
| M1 | 0:08.00 | 0:12.45 | erhu sustained F5 (S03), REVERSED, unshifted (the mode's b7, unresolved tension) | bow attack lands at the cut | -28 → -16 at 0:12.45 |
| A5 | 0:10.50 | 0:12.50 | film projector texture (S08) | band-passed | -38 → -32 |
| M2 | 0:12.50 | 0:17.95 | strings cluster (S14, VSCO 2 CE), REVERSED crescendo | sul tasto, cluster around G | -30 → -9 at 0:17.90 |
| A6 | 0:12.50 | 0:17.80 | metal thuds (S10), REVERSED, one per floor (2/s → 10/s) | + saturated sub layer | each -22 |
| A7 | 0:12.50 | 0:18.00 | eave wind-bells (S05), REVERSED | sparse | -34 |
| SYN3 | 0:16.60 | 0:17.95 | reverse boom ("inhale") | hard stop at 0:18.00 | peak -6 at 0:17.95 |
| A8 | 0:18.00 | 0:19.45 | temple bell (S04), REVERSED: bloom swells into the strike | — | strike -12 at 0:19.45 |
| A8b | 0:18.00 | 0:19.45 | wind (S11), reversed | — | -36 |
| **S1** | **0:19.50** | **0:20.00** | **absolute silence** (digital zero) | — | — |
| A9 | 0:20.00 | 0:29.90 | first FORWARD sound: one wooden creak (S13, or the client's own audio S15 if suitable), then canal water (S12) | — | creak -22 at 0:20.00; water -30 → -28, fade out 0:29.00-0:29.90 |
| A10 | 0:21.20 | 0:22.50 | eave bell (S05), one soft forward chime at the mist's peak | — | -30 |
| M3 | 0:21.00 | 0:29.80 | xiao (S02): phrase A = recording 8.6-13.2 s (F4 → G4), phrase B = 28.4-35.2 s (D4 → the long 4.3 s F4), to audition | 3.5 s hall reverb | -20 → -18; fade 0:28.00-0:29.80 to -40 |
| SYN4 | 0:22.00 | 0:30.20 | sub drone G1 (49 Hz +15 c) + harmonics | slow swell | -28 → -24 by 0:27.00; fade 0:29.50-0:30.20 |
| **S2** | **0:30.20** | **0:31.00** | **silence** on the white bloom | — | — |
| **M4 THE NOTE** | **0:31.00** | **0:38.00** | **dizi, G6, one real breath (S01), unedited: no loop, no stretch** | natural vibrato; 2.5 s plate reverb | fade-in -60 → -16 over 0:31.00-0:31.90; rises to -12 at 0:35.20; **alone after 0:36.60**; release 0:37.20-0:38.00 to silence |
| M4b | 0:32.50 | 0:36.60 | octave halo: S01 +12 st (optional) | very soft | -32; cut at 0:36.60 |
| SYN5 | 0:31.40 | 0:36.60 | sub drone G1 + harmonics | — | -22; **cut at 0:36.60** |
| M5 | 0:33.00 | 0:36.60 | strings, high harmonics ppp (S14) | — | -30; **cut at 0:36.60** |
| SYN6 | 0:33.50 | 0:36.60 | granular shimmer made from the note | — | -32; **cut at 0:36.60** |
| A11 | 0:31.00 | 0:38.00 | canal water (S12), forward | — | -32; -28 after impact; fade to -45 by 0:38.00 |
| A12 | 0:36.60 | 0:37.40 | water drop (S06), forward, impact + ripple tail | — | -10; **at impact everything except the note and the water stops (10 ms)** |

Loop point: 0:38.00 is near-silent water; 0:00.00 begins with reversed water. The picture loops exactly;
the sound loops without a bump.

---

## 6. CGI and generated assets

**Generative AI: none required.** Every image of the client is their real photograph. All environments are
their real photographs/video or a licensed CC0 photograph (the Bund HDRI).

| Asset | Shots | Method | Status |
|---|---|---|---|
| Longhua clean plate (towers, cranes, right block removed) | SH050-SH070 | depth + colour segmentation, fitted sky with matched grain | tested; finial-needle and foliage-edge fixes listed |
| Unbuilding layers (per-floor masks, crane layer) | SH050 | 2D, procedural | tested (stepwise) |
| Pagoda → pavilion morph | SH070 | TPS warp + SDF silhouette + mist + rising river | tested v1-v4 |
| Night reflection | SH100, SH010 | CC0 night plate, real wave field, Fresnel, light pillars | tested v2 |
| CG water drop | SH100, SH010 | Blender 5.2 Cycles, refracting the plate | method proven in pipeline test; look-dev pending |
| Converging/expanding ripples | SH010, SH100 | analytic rings displacing the comp | mechanism tested; look to refine |
| Aircraft cut-out + sky fill | SH030 | 2D | trivial |
| Two-layer parallax (client) | SH020, SH090 | BiRefNet mattes + small background fill | mattes tested |
| Title EN + 中文 in the water | SH100 | Remotion + water displacement | components tested |

Optional, paid, not required (client's call, cost estimate on request):
- OPT-1 AI image-to-video of the **background only** in SH020 (Huangpu water and clouds moving, reversed)
  behind the matted, untouched client. Adds life to the "held man in a moving world"; must not alter
  landmarks.
- Not recommended: AI upscaling of the resized uploads (it would touch the client's face). Full-resolution
  originals solve this better.

---

## 7. Technical feasibility check (tests run on the real media, 2026-11-27)

| ID | Effect | Test / evidence | Result | Status | Risk |
|---|---|---|---|---|---|
| FX-01 | Reverse drop + rings | `f3_drop.py`, `f3_drop_strip.jpg` | mechanism works; rings too even and glossy | Feasible, look-dev | Low-med |
| FX-02 | Client mattes / parallax | `mattes_check.jpg` (BiRefNet, 35-67 s each) | clean hair, glasses, collar edges on all 3 photos | **Proven** | Low |
| FX-03 | Aircraft tail-first | aircraft located, 28x11 px, nose left | trivial composite; small on phones | Proven; readability med | Med |
| FX-04 | Texture ageing | pipeline test grade/grain | standard | **Proven** | Low |
| FX-05 | Longhua clean plate | `f5_cleanplate.py`, `clean_detail.jpg` | sky seamless; guy-wires protected; needle tip thinned; foliage smear right | Proven + 2 fixes | Low-med |
| FX-06 | Unbuilding | `longhua_unbuild_strip.jpg` | floors vanish top-down convincingly | **Proven** | Low |
| FX-07 | Pagoda → pavilion | `f6_transform.py` → `_v4.py`, strips v1-v4, full-res pass `f6_full_crops.jpg` | v1 ghosting, v2 double exposure, v3 cut-out look, **v4 reads as a transformation**; geometry lands exactly on the real pavilion; full 1080x1920 pass in 84 s: landed frame crisp at 1.15x; mid-morph shows (a) guy-wires bent by the warp, (b) the pavilion's eaves ghosting as grey "wings" in the mist. Fixes: fade the cables out before the spire sinks; let the pavilion eaves appear only through the SDF silhouette edge | Feasible; 1-2 more iterations | **Med** |
| FX-08 | 120 fps conform / canopy | per-frame scan of IMG_1039 | canopy at 0-0.53, 1.81-2.89, 4.39-5.21 s; **assigned 5.30-6.70 s is clean** | **Proven** | Low |
| FX-09 | Night reflection | `f7_reflection.py`, `f7_still.jpg` | v1 rejected (boatman painted out, purple paint); v2 near-black water, light pillars, boatman kept | Feasible, look-dev | Low-med |
| FX-10 | Sun bloom to white | standard | — | **Proven** | Low |
| FX-11 | Title in the water | Remotion + CJK proven in pipeline test | — | Components proven | Low |
| FX-12 | Grade continuity | sources: front-camera selfie softer than the rest | unify with grain + sharpening restraint | Feasible | Med |
| AX-01 | The note | S01 preview analysis: G6 1581.6 Hz, 8.6 s sustain, 3 Hz natural vibrato, CC0 | one breath covers the 7.0 s | **Proven** (WAV to download) | Low |
| AX-02 | Mode alignment | erhu F5 697 Hz (9.1 s, ±6 c); xiao held notes C5 D4 F4 G4 C4 (4.3 s F4 at 30.8 s) | all in G shang pentatonic: no pitch-shifting | **Proven** | Low |
| AX-03 | Reversals, synthesis, mix, master | pipeline test (-14.0 LUFS achieved) | — | **Proven** | Low |
| AX-04 | Client's own boat audio | analysis: 63 % energy 300-3000 Hz, tonal | likely voices or song: **client must listen** | Open | — |

Estimated compute for finals on this machine (1080x1920): SH070 ~1.5 min per pass (measured 84 s), SH100 ~5 min, CG drop
~25 min, all other shots minutes; total under 1.5 hours plus encodes. Reels and TikTok cap at 1080x1920,
so a 1080x1920 master is the right delivery; the uploaded photos support it.

---

## 8. Open items and approvals needed

1. **Approve this timeline and the storyboard** (or give notes). Final rendering waits for this.
2. **Listen to IMG_1039's own audio**: is it a boatman's song, a guide, or chatter? (decides cue A9)
3. Full-resolution originals of IMG_1006, IMG_1062, IMG_1009, IMG_1750, IMG_0909 and 20261127_160211
   (the uploads were resized and stripped of metadata).
4. Freesound WAV downloads for the selected sounds (a free Freesound login; list in the manifest).
5. Chinese title wording: 上海 · 时光之间 (or your preferred phrasing), checked by a native reader.
6. The jacket logo is visible in SH020 and SH090: keep as is?
7. OPT-1 (paid AI background motion in SH020): yes / no.
