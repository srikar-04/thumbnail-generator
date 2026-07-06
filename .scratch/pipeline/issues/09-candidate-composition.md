# Candidate composition: style-conditioned generation + the validated compositor recipe

Status: ready-for-agent

## Parent

`.scratch/pipeline/PRD.md` (Milestone 1). Stories 11, 12, 16–18, 22–24.

## What to build

Replace the skeleton's placeholder `order run` with the real generation pipeline (still provider-agnostic — fake providers in tests, real ones arrive in ticket 10):

- **Wording**: 3–5 proposals per Order (3–5 words each, distinct from the video title) from the LLM provider.
- **Concepts**: derived from the Brief + the chosen style specs, so each Candidate has a deliberate idea.
- **Style-conditioned Background prompts**: assembled from style spec + Concept + the prototype's restraint rules — one focal element, generous negative space, one accent color, no clutter / no dense texture. Never from the Brief alone.
- **Spread**: an Order's ~20 Candidates cover 2–3 different style specs (picked via ticket 08's read API), so the Contact Sheet shows genuinely different directions.
- **Compositor** (the prototype recipe, absorbed here as the launch baseline): LANCZOS resize, autocontrast + unsharp, ~15% palette tint toward background mean + luminance match, feathered alpha edge (never a sticker outline), drop shadow, and the thin rim light clamped inside the silhouette — the one hard-won geometry decision (prototype-derived):

  ```python
  shifted = offset(alpha, dx, dy)              # small offset, e.g. (7, 3)
  edge = subtract(alpha, shifted).blur(1.5)    # tight blur — wide blur = halo
  edge = multiply(edge, alpha)                 # clamp: never spills outside subject
  edge = edge * 0.65                           # subtle, not neon
  ```

  The Subject is only ever geometrically/photometrically adjusted — never AI-regenerated (ADR-0001).
- **Styled Text devices**: torn-paper chips, label bars, plain-with-accent-word — chosen per style spec, balanced 2-line layout, hard safe margins.
- **Per-candidate metadata**: style spec used, wording, source photo, placement values, layout boxes (text, subject), device style, provider costs — everything ticket 02/03/01 and the tests need to observe.

Placement in this ticket may remain the skeleton's simple rule (fixed side/scale); ticket 02 upgrades it. Icon handling arrives in ticket 03.

## Acceptance criteria

At the CLI-over-disk seam with fake providers:

- [ ] `order run` produces ~20 Candidates spanning at least 2 style specs, each metadata file recording which spec, wording, and photo it used.
- [ ] Every rendered Wording is 3–5 words and differs from the Brief's title.
- [ ] Every text layout box in candidate metadata lies fully inside the safe margins; no candidate's text box exceeds the frame.
- [ ] The text device recorded in metadata matches the device its style spec calls for.
- [ ] Background prompts sent to the provider (observable via the fake's recorded calls persisted to the Order folder) contain the style spec's backdrop/palette language and the restraint rules.
- [ ] Composite output is 1280×720 with the Subject cutout present; the source cutout file is byte-unchanged (no AI touching).
- [ ] Two identical fake runs produce identical candidates (determinism).

## Blocked by

- 07-onboard-asset-pack
- 08-style-library
