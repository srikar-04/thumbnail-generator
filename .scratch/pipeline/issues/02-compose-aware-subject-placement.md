# Compose-aware subject placement

Status: ready-for-agent (Milestone 1 ticket — see Parent / Acceptance / Blocked by below)

## Parent

`.scratch/pipeline/PRD.md` (Milestone 1). Stories 19, 20. The photo-analysis half of this issue moved to ticket 07 (metadata is computed and cached at onboarding); this ticket is the per-Candidate decision that consumes it.

## Problem

The prototype compositor applies fixed rules: always flip (to fix mirrored selfie
shirt text), always anchor bottom-right, fixed scale. This ignores what is actually
*in* the photo and *in* the background:

- d03: the flip reversed the operator's pointing gesture so he points at empty space
  instead of at the text; his hand was also partially cropped by the frame edge.
- Side/scale are constants, so a photo whose composition wants the left side (or a
  tighter head-and-shoulders crop) gets the same treatment as everything else.

## Wanted

Per-candidate placement decisions driven by photo content and background structure:

- Detect gesture/gaze direction (cheap VLM call per Asset Pack photo, cached) and
  choose flip + side so gestures point INTO the composition (toward text/focal area).
- Choose crop (full torso vs head-and-shoulders) per layout preset.
- Flip decision must weigh readable clothing text vs gesture direction — when they
  conflict, gesture direction usually wins (or pick a different photo).
- Respect the background's focal space (overlaps with issue 03).

Photo-content metadata belongs in the Asset Pack (analyzed once at onboarding, not
per order).

## Acceptance criteria

At the CLI-over-disk seam with fake providers, using fixture photo metadata (e.g. one
photo pointing left, one pointing right, one with clothing text):

- [ ] Placement (flip / side / scale / crop) is decided per Candidate and recorded in
      its metadata file — no fixed always-flip / always-bottom-right constants.
- [ ] For a Candidate whose photo has a gesture, the recorded flip+side result has the
      gesture pointing toward the text/focal area, not off-frame (assertable from
      metadata: post-flip gesture direction faces the text box's side).
- [ ] When gesture direction and readable clothing text conflict, the pipeline either
      picks a different photo or resolves per the documented rule (gesture wins), and
      the metadata records which rule fired.
- [ ] Crop choice (full torso vs head-and-shoulders) follows the layout preset and is
      recorded in metadata.
- [ ] The decision is a pure function of cached photo metadata + background metadata +
      layout preset: same inputs, same recorded decision across runs.
- [ ] No VLM call happens during `order run` for photo analysis (fake provider call
      log shows zero per-photo analysis calls — it all came from the Asset Pack cache).

## Blocked by

- 09-candidate-composition
