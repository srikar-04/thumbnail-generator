# Compose-aware subject placement

Status: ready-for-agent (triaged via PRD.md — photo metadata cached at onboarding; placement is a pure function persisted in candidate metadata)

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
