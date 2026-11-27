# Director's review: Production Plan v001 + Storyboard v001 (gate: Treatment -> Shot list + storyboard)

Date: 2026-11-27. Reviewer: creative-director (independent review). Film: SHANGHAI: BETWEEN TIME, Concept 2
"Against the Current".

**What I reviewed:** `PRODUCTION_PLAN_v001.md`, `TREATMENT_CONCEPTS_v001.md` and `SOURCE_MANIFEST.md`. Images
from `STORYBOARD_v001.jpg` and from `08_VFX_Compositing/feasibility/`:
- `f6_strip_v4_dense.jpg`, plus frames 24-56 of `f6_transform_v4.mp4`
- `f7_still.jpg`, plus frames 0/16/32/47 of `f7_reflection.mp4`
- `longhua_unbuild_strip.jpg`, `longhua_clean.png` (also with a contrast stretch) and `clean_detail.jpg`
- `f3_drop_strip.jpg`, `mattes_check.jpg` and `aircraft_crop.png`

**What I could not check here:**
- No audio was auditioned. No WAV has been downloaded yet.
- Motion was judged from extracted frames, not watched on a phone.
- No calibrated display was available.

---

## A. Verdict: APPROVE WITH CHANGES

The film's structure is right. This is the best version of Concept 2 so far:
- a three-state time grammar (REVERSE, HELD, FORWARD);
- reversals that grow in scale: a drop, then an aircraft, then a skyline;
- one unbroken 14.5-second movement through the turning point;
- six cuts in 38 seconds;
- the client never generated, and every image either their own or a CC0 photograph.

**Do not present it to the client yet.** There are three reasons:
1. One client instruction (#4) has been reinterpreted instead of offered to them as a choice.
2. The loop that makes the film a palindrome does not add up as written.
3. The storyboard shows both signature moments (#3 and #5) in a state the plan itself calls unfinished.

Every note in C is either a change to the document or one more CPU pass of a test that already exists. Nothing
needs restructuring.

## B. Compliance with the 8 client instructions

1. **The client is central, their photos are real, their face is never generated: PASS with concern.**
   - What is right: no AI, no relighting, no smoothing, and two-layer parallax on their real pixels.
   - Concern: the plan has no identity gate and no side-by-side review step, and the reference set has not been
     enrolled (`identity_reference/` holds only a README).
   - Concern: they are on screen for about 8 s. Their point of view carries SH030-SH040 (eyeline), SH080 (their own
     footage from the boat) and SH100. The only stretch without them in any form is Longhua, 12.50-20.00.
2. **The reverse effect is selective: PASS for picture, CONCERN for sound.**
   - Picture: three REVERSE moments, never two at once.
   - Sound: reversed cues play under the HELD shots SH020, SH040 and SH060 (SYN2, M1, A8/A8b). That breaks the
     plan's own rule, so the ear hears one continuous rewind from 0 to 20 s.
3. **The pagoda-to-pavilion transformation is seamless and convincing: CONCERN (not yet).**
   - The geometry lands exactly on the real pavilion.
   - The middle of the morph (v4, 1.00-1.80 s) reads as a fog dissolve, with a cut-out silhouette and a
     ruler-straight water wipe.
4. **Authentic xiao/dizi, the note in the final 7 s, plus Concept 1's continuous note: CONCERN.**
   - The entrance in the final 7 s is well designed.
   - "Continuous" has been read as "unbroken within the last 7 s". Concept 2 already had that, so Concept 1's
     idea is not actually incorporated.
   - Authenticity rests on three Freesound files that nobody has heard at full quality.
5. **The Lujiazui reflection is extraordinary: CONCERN (not yet).**
   - The physics approach is sound: Fresnel, the real wave field, glints kept, boatman kept.
   - But in f7 the Pearl Tower is not recognisable. It is a magenta streak in the far third of the canal, and
     nobody questions what they cannot identify.
6. **The real locations' atmosphere and light are kept: PASS with concern.**
   - The real light carries the time arc (blue, then golden, then night in the water) without faking it.
   - Two atmospheres are invented: mist in a hard-blue Longhua (SH070), and film ageing in SH040.
7. **30-45 s, vertical 9:16: PASS.** 38.00 s, 1080x1920, 24 fps, with the safe area defined.
8. **Visual quality over number of effects: PASS with concern.**
   - The picture effects are mostly motivated.
   - The final 7 s stack five audio layers under "a single note".
   - SH040's ageing and the SYN2 pulse are decoration.

## C. Must-fix before presenting to the client

1. **Instruction 4 must go to the client as a choice (plan §5 "Interpretation of the brief", cue M4).**
   Present two options and recommend B.
   - **A. As planned.** The note exists only from 31.00 to 38.00, unbroken.
   - **B. "The fixed point in sound" (recommended).** The note's exact pitch (G6 +15 c) runs as a near-subliminal
     thread from 0:00, at -36 to -30 dBFS.
     - Build it from S01's own sustain (a spectral freeze with the breath removed), not from a synth.
     - It is never reversed and never changes pitch while everything around it reverses. It is to the sound what
       the HELD client is to the picture.
     - It stops for the two silences (19.50-20.00 and 30.20-31.00), so they are felt as a loss.
     - At 31.00 the real dizi breath takes over the same pitch. The dramatic entrance is a human breath arriving
       on a note that was always there.
     - It must pass a phone test for whine and fatigue.

   Both options satisfy "introduced dramatically in the final seven seconds". Only B incorporates Concept 1.

2. **The palindrome does not add up (SH010 to SH100, transition T1).**
   - SH010 is SH100's 35.00-38.00 played backwards. In SH100 the drop exists only from 36.20 to 36.60.
     Reversed, it lifts out of the water at 0:01.40 and is gone by 0:01.80, so at 0:03.00 there is no drop for
     T1's position-locked match.
   - The title (34.00-36.40) would also appear in SH010, sinking, from 0:01.60 to 0:03.00. SH010's description
     never mentions it.
   - **Fix (recommended):** SH010 = SH100's 36.60-38.00 played backwards.
     - 0:00.00-0:01.40: the rings converge.
     - 0:01.40: the drop lifts out of the water.
     - About 0:02.40 to the cut: the drop rises, slows, and **holds** at (384, 974). That is HELD, which fits the
       grammar.
     - No title in SH010.
     - The loop seam at 38.00 / 0:00 stays frame-exact.
   - Write the drop's full path, in SH100 time, into the plan.
   - Replace the SH010 storyboard panel. It shows the f3 rings, which the plan itself rejects.

3. **SH070 (0:20.00-0:23.00) needs one more iteration (v5) before the client sees it moving.**
   What frames 24-56 of v4 (1.00-2.33 s) show:
   - a) The rising river is a flat, ruler-straight horizontal edge with a pasted texture below it. It cuts
     through the Longhua trees and reads as a wipe.
   - b) Mist at strength 0.62 turns the whole frame milky for about 0.6 s. It reads as a disguised crossfade, and
     nothing in the hard-blue Longhua scene motivates it.
   - c) The silhouette's lower tiers are a flat dark fill with hard, splayed edges, like a paper cut-out
     (1.25-1.75 s).
   - d) A ghost spire hangs above the forming pavilion (about 1.67 s).
   - e) There are edge streaks at both frame edges, and the sky is smeared (2.33-2.96 s).

   Targets for v5:
   - a waterline in correct perspective, with ripples and reflection;
   - mist at 0.3 or less, confined to the waterline;
   - real texture inside the silhouette on every frame;
   - full-frame coverage;
   - the two fixes from the updated FX-07 row, which was edited while this review was being written. Its
     full-resolution pass found the guy-wires bent by the warp and the pavilion's eaves ghosting as grey "wings".
     That confirms c) above. Fade the cables out before the spire sinks, and let the eaves appear only through
     the silhouette edge.

   Also fix the plan's wording. §3 says "Method proven"; FX-07 correctly says "Feasible; 1-2 more iterations".
   Replace the single storyboard panel with three frames (start, middle, landing) from v5.

4. **SH100 (0:31.00-0:38.00): the reflection must be recognisable, and the camera must travel along it.**
   - a) Make the inverted Pearl Tower readable at phone size. Its two spheres must be legible within about 1 s
     of the far end turning to night.
   - b) The plan pushes and tilts into the near water (1.00 to 1.35 by 36.60). But `f7_reflection.py` places
     the mirrored skyline only from the far waterline downwards (`y_far`) and fills the rest with a flat mean.
     The camera therefore ends on empty black water. Extend the inverted tower from the far end into the near
     water, so the move travels down it and ends on the reflected lower sphere (see D2).
   - c) Grade the HDRI's magenta and cyan into the film's palette. At full saturation in a golden frame they read
     as a neon overlay, not as a reflection.
   - Label the SH100 storyboard panel as a test, including the placeholder sans-serif title.

5. **The sound must obey its own grammar under HELD shots, starting with the client's first appearance.**
   - §1 says "reversed sounds only in REVERSE moments". Yet:
     - SYN2 (eight reversed sub swells, 3.00-12.00) plays under SH020 and SH040;
     - M1 runs into SH040;
     - A8 and A8b sit under SH060.
   - Fix:
     - SH020 (3.00-7.50) introduces the client and is the present: forward sound only.
     - The first reversed sound is the aircraft at 7.50.
     - Cut SYN2, or keep only the hit at 12.00, where the rewind engages.
     - The reversed bell into the silence (A8, 19.45) can stay, if the plan names it as a deliberate exception:
       the sound leads the picture into the hinge.

6. **The identity steps are missing (SH020, SH090).**
   - Add the identity-preservation steps:
     - enroll the reference set;
     - run the gate on the first, middle and last frames of both final shots;
     - do the side-by-side review;
     - record the client's sign-off in the provenance sidecar.
   - Add to §8: the client explicitly approves the **un-mirrored** SH020. People know their own face from mirrors
     and selfies, so the corrected orientation can feel wrong to them even though it is true to the place.
   - SH020 layers: in IMG_1006 the lamp-post behind their head is close to the camera. In a two-layer parallax it
     slides with the skyline and visibly moves against the edge of their head. Matte it as a third, middle layer,
     or keep it in the foreground layer.

7. **The music source is the client's decision, and nothing is "Proven" yet (AX-01, §8).**
   - The note, the xiao phrases and the erhu are three Freesound files analysed from previews only. Nobody has
     heard the WAVs.
   - The plan assumes S02 contains "two long low breathy phrases". That is unverified.
   - The client called the soundtrack extremely important. Add the choice to §8:
     - (A) the selected CC0 / CC-BY recordings: free, available now;
     - (B) a commissioned remote dizi/xiao player recording to picture: cost estimate first, client's OK needed;
     - (C) a licensed sample library.
   - Recommendation:
     - Download and audition option A first. If S01 does not sound like a living human breath, go to option B.
     - If S15 (the client's own canal audio) is usable, their recording outranks any library file for the forward
       half.
   - Paperwork:
     - Change AX-01 to "Feasible (preview analysis); WAV not auditioned".
     - Log each audio source in `asset_licences.json` when it is downloaded (studio rule 5). Today that file
       holds only the HDRI and the OSM data.

8. **SH050 and SH060 clean-plate continuity.**
   - a) The unbuild strip's end frame, labelled "t=1 (clean)", still shows the modern block on the right.
     `longhua_clean.png` has it removed. SH050's last frame must equal the plate SH060 continues on, or the block
     will pop out at 0:18.00.
   - b) In `longhua_clean.png`, the crown of the right-hand tree is carved into straight-edged notches where the
     building was, then smeared. Rebuild an organic crown edge; colour decontamination alone will not fix it.
   - c) Under a contrast stretch, faint crane outlines remain in the left sky. The grade and sharpening will
     bring them out, so clean them now.
   - d) The finial needle fix is already listed in the plan.

## D. Strong suggestions

1. **Make water the medium of time in SH070.**
   - Let the swap happen first in the rising river's reflection, tier by tier from the top down, and let the
     solid building follow.
   - The ripples hide every seam a morph leaves, and the mist can go.
   - Reason: a building morphing in mid-air is a 1990s effect. A reflection that remembers a different building
     is the film's own idea, the same one as SH010 and SH100. The film then has one motif instead of three
     effects.
2. **Land the drop on the reflected Pearl Tower's lower sphere.**
   - Played backwards in SH010, the drop rises out of the reflected sphere and holds where the real sphere stands
     in SH020.
   - Reason: T1 becomes sphere, drop, sphere. That is a match with meaning instead of an arbitrary screen point,
     and the loop closes on the film's thesis: old water holding the new city.
3. **Show the logline once: make the canal flow behind the held client in SH090.**
   - Drive the canal in IMG_1062 with IMG_1039's real wave field. It is the same tool as SH100: local and free.
   - Reason: "one person stands still while their city moves" never appears on screen as planned, because every frame of
     the client is still and so is everything around them. This is the one shot where their stillness can read as
     a choice rather than as a photograph. Prefer this to the paid OPT-1.
4. **Keep the note single, and let it begin with its own breath.**
   - Default the final 7 s to dizi plus canal water. Add the sub only if a phone test needs it.
   - Keep M4b, M5 and SYN6 as an A/B comparison, not as the plan.
   - Replace the 0.9 s fade-in (31.00-31.90) with the dizi's natural attack, behind a 20-50 ms ramp that only
     prevents clicks.
   - Reason: the client asked for a single note from an authentic recording. The breath onset is the most
     authentic part of it, and coming out of 0.8 s of silence it is the drama. A fade-in turns a player into a
     pad.
5. **Give the reflection room before the title.**
   - Move the title to about 35.00-36.40, or shorten it, so the night reflection has about 3 s alone after the
     fade from white.
   - Reason: instruction 5 asks the audience to question what they see. On a phone, text pulls every eye to read
     it, and that ends the questioning.
6. **Let sound make the cuts and the stillness legible.**
   - Pre-lap the reversed aircraft sound 0.5 s into SH020 (from 7.00), so the eyeline cut T2 is motivated by
     hearing. A still photo cannot "look up", so the eyeline alone does not justify the cut.
   - In SH040, let the flags be heard snapping forward in the wind while they hang frozen.
   - Reason: in a film made of stills, HELD only reads as stopped time when something we hear refuses to stop.

## E. Clichés, unmotivated choices, and what may look cheap on a phone

- **SH040 film ageing** (gate weave, projector sound S08, halation ramp) is the stock "vintage" signal. It is not
  even a progression, because SH050 cuts back to a crisp plate. Cut the gate weave and the projector sound. Keep
  a grain and saturation shift only if it carries on through SH050-SH060.
- **The reverse "inhale" sounds** (SYN2 rewind pulse, SYN3 reverse boom, M2 reversed crescendo, A6 reversed thuds)
  are four uses of one device in 18 s. That is trailer-riser grammar; by the third, the ear hears a sound pack
  instead of time. Use reversed sound only where the picture reverses (C5).
- **SH050's "1-frame bright edge per floor"** at up to 10 floors per second will strobe like a scan or glitch
  effect and will break up under platform compression. Drop it. The reversed thud already marks each floor.
- **The SH070 mist at 0.62** is a fog dissolve. On a phone, 0.6 s of milky frame reads as "the transition".
- **The f3 rings** (even, concentric, glossy white) look like a filter, and the drop is a white ellipse. They are
  the first second of the film, so they must look like water.
- **The night reflection's colour:** at full magenta and cyan inside a golden-hour frame, it tips into
  neon-cyberpunk Shanghai. The colours are real; how strong they are is a grading decision.
- **T9 white:** 0.8 s of flat white with digital silence at 30.20 is a blank phone screen at the 30-second mark,
  which is when people swipe away. Keep a trace of image inside the white (the sun core and their silhouette at
  about 95 %), not a flat white card.
- **SH100's stillness:** a still photograph with only the water moving is the cinemagraph look. Frozen leaves are
  acceptable for 2-3 s under a moving camera. Do not hold the wide frame any longer than the plan does.

## F. My honest read of the storyboard and test frames

**What already works:**
- The board reads as one film: the blue Bund, the blue Longhua, the golden water town, then night in the water.
  The real light carries the time arc, with no grading trick.
- **The Longhua unbuild** is the strongest test. Floors go from the top down believably. The pagoda, its
  guy-wires and its eave bells are intact. The emptied sky is credible at normal contrast.
- **The mattes** are clean on all three photos of the client, including hair and collar edges, and no pixel of
  their face is altered. This makes the "client is always real" promise technically safe.
- **The SH070 landing** (v4, from about 2.0 s) puts the silhouette exactly on the real pavilion's roofline, and
  the eave rhyme is genuine. The idea is right; the middle of the morph is unfinished.
- **SH080** (IMG_1039, 5.90-6.70 s, 5x slow) is the best moving image in the film. Placing it untouched straight
  after the morph is the right call: real footage as the reward.
- **f7's physics are right.** The water goes dark because the sky it reflects is now night. The glints stay, the
  boatman stays, and the trees stay golden. The impossible combination is there in principle.
- The time-grammar table, the two silences and the palindrome idea show that the plan thinks like a director,
  not like a template editor.

**What does not work yet:**
- **The middle of f6 v4** (1.00-1.80 s): a wipe-like waterline, a fog veil, a cut-out silhouette, a ghost spire,
  and edge streaks (C3).
- **f7** has no recognisable Pearl Tower, and the night lives in the far third of the canal while the camera
  heads for black near water (C4).
- **f3:** the rings and the drop look generated, and this is the opening hook.
- **The clean plate:** a carved tree crown, faint crane outlines, and an end state that differs from the unbuild's
  last frame (C8).
- **SH030:** the aircraft is 28x11 px in the source, so about 33 px wide at the end of the 1.25x push. At arm's
  length on a phone, "tail-first" will not read; only the reversed Doppler sound will. Test it on a phone. If it
  fails, the fix is the full-resolution original (open item 3) and a stronger push, not a redrawn aircraft.

## Decisions, owners, next steps

| # | Action | Owner |
|---|---|---|
| C1, C7, C6 (un-mirror approval) | Add the client choices to plan §8; append the gate verdict to DECISIONS_LOG.md (not edited by this review, as instructed) | Main session (producer) |
| C2, D2 | Write the drop's path in SH100 time; SH010 = SH100's 36.60-38.00 reversed, then HELD | cgi-vfx-artist |
| C3, D1 | SH070 v5 (waterline, mist, silhouette interior, coverage); swap first in the reflection | cgi-vfx-artist |
| C4, D2 | SH100 v3: readable inverted tower running into the near water; drop lands on the reflected sphere | cgi-vfx-artist, then colorist (C4c) |
| C5, C1-B prototype, C7 audition, D4, D6 | Fix the sound grammar; build the thread; download and audition S01, S02, S03 and S15 | sound-designer |
| C6 | Enroll the reference set; gate + side-by-side on SH020 and SH090; third parallax layer for the lamp-post | cgi-vfx-artist + Creative Director review |
| C8 | Clean-plate fixes; match the unbuild's end frame to `longhua_clean` | cgi-vfx-artist |
| D3 | SH090 canal flowing behind the held client | cinematographer + cgi-vfx-artist |
| E | SH040: cut gate weave and projector sound; SH050: drop the bright edges; T9: keep image in the white | colorist, video-editor, sound-designer |

**After that:** the Creative Director re-reviews the SH070 v5, SH100 v3 and SH010 frames and the audio auditions.
Then the plan goes to the client as v002, with options A/B for the note and A/B/C for the music source.

Proposed DECISIONS_LOG line:
`2026-11-27 | Creative Director (independent review) | Treatment -> Shot list gate: CHANGES (8 must-fix notes; handoffs/20261127_creative-director_production-plan-review.md) | Structure approved; instruction 4 needs a client choice; palindrome timing; SH070/SH100 not yet at the brief; sound grammar; identity steps | cgi-vfx-artist + sound-designer, then client`
