# Candidate composition: style-conditioned generation + the validated compositor recipe

Status: ready-for-human (implemented via TDD 2026-07-07; awaiting operator review)

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

## Comments

- 2026-07-07: Implemented red→green in 6 cycles at the established seam
  (tests/test_candidate_composition.py). The prototype recipe now lives in
  `src/thumb/compositor.py` (prep_subject, drop_shadow, styled text devices,
  compose); `pipeline.run_order` defaults to 20 Candidates spread round-robin
  across ≤3 specs from `library.list_specs`, composites from Asset Pack
  *cutouts*, and persists each background layer to `orders/<id>/backgrounds/`
  (resumability groundwork + ticket 03's icon-locate input). Notes for
  reviewers:
  - Real defect caught by strengthening a weak test: Pillow's LANCZOS resize
    premultiplies RGBA, so `autocontrast` saw the transparent region as black
    and blew flat subjects to white. Fix: histogram masked to the subject
    (`opaque`) and skipped entirely when `_trimmed_span < 64` (nothing to
    recover). The subject-presence test was proven able to bite via an
    injected skip of `alpha_composite`; the safe-margin test via an injected
    zone x0=4.
  - `propose_concepts` joined the LLM provider seat (Concepts derive from
    Brief + spec backdrop, per PRD story 17).
  - Placement is still the fixed rule (side=right, scale=0.88, flip=False —
    "flip only when placement logic says so"); ticket 02 upgrades it.
  - `limitation: "source-photo limitation: …"` appears in candidate metadata
    when no cutout exists (ADR-0001); `cost_usd: 0.0` placeholder until the
    real ledger (ticket 10).
  - Skeleton tests that encoded the old 3-candidate default now pass `--n 3`.
  30 tests green. `scratch/prototype/` is now absorbable — deleting it is the
  separate cleanup the PRD names. Unblocks ticket 10 (real Gemini) and 01–03.
