# Onboarding: real Asset Pack intake with capture checklist, photo metadata, cutouts

Status: ready-for-human (implemented via TDD 2026-07-07; awaiting operator review)

## Parent

`.scratch/pipeline/PRD.md` (Milestone 1). Stories 1–8. Folds former issue 05 (source-photo capture guide) and the onboarding half of issue 02 (photo-content metadata).

## What to build

Grow `thumb onboard` from the skeleton's folder-maker into real Asset Pack intake:

- **Capture guide**: a one-page document (checklist + shot list) the operator sends every Creator — warm directional key light, 10–20 shots across an expression range (shock, grimace, joy, curiosity, pointing both hands, arms crossed, neutral), eye-level chest-up framing, plain background, no beauty filters, clothing-text warning. The prototype found each shoot got only half right (round A: expressions, no light; warm reshoot: light, no expressions) — the guide demands BOTH.
- **Checklist as data**: the checklist items live as data the onboard command evaluates against submitted photos (via the critique VLM provider), flagging failures (flat light, neutral-only expression coverage, busy background, filtered faces) so the operator rejects or re-requests before photos become the Order quality ceiling.
- **Photo-content metadata, computed once and cached** (per photo, one cheap VLM call): gesture direction, gaze direction, expression label, clothing-text presence, viable crops. This is what per-Order placement (ticket 02) reads — never re-analyzed per Order.
- **Cutouts generated once per accepted photo** (rembg), stored in the Asset Pack for reuse across Orders.
- Creator style references (thumbnails they admire) are accepted into the Asset Pack as files for ticket 08 to consume.

## Acceptance criteria

At the CLI-over-disk seam with fake VLM provider and fixture photos:

- [x] `thumb onboard` with a photo set writes, per accepted photo: a cached metadata record (gesture, gaze, expression, clothing text, crops) and a cutout file with transparency.
- [x] Photos failing checklist items are flagged in an onboarding report on disk; a photo set with zero expression variety (all neutral) produces a failure the operator can read.
- [x] Checklist items are data, not hardcoded prose — the evaluated items in the report match the checklist source.
- [x] The capture guide document exists in the repo and its checklist items are the same source the onboard command evaluates.
- [x] Re-running onboard does not re-analyze or re-cut photos whose outputs already exist.
- [x] Faceless rejection from the skeleton still holds; a face-on Creator's Asset Pack records their style-reference images.
- [x] Manual (not CI): the operator's own 9 photos onboard successfully end-to-end. *(Done in fake-provider mode: 9 photos + 5 references intake, analysis cached, cutouts + report written. Re-run with real VLM/rembg at ticket 10 for true analysis quality.)*

## Blocked by

- 06-walking-skeleton

## Comments

- 2026-07-07: Implemented red→green in 7 cycles at the established seam. Key pieces:
  `analyze_photo` added to the VLM provider seat (fake derives metadata from filename
  tokens — see FakeCritiqueProvider docstring for the token vocabulary); cutouts via a
  `CutoutEngine` binding (fake = oval matte; rembg is the real binding, ticket 10);
  capture guide at `src/thumb/capture-guide.md` with machine-readable `[check: ...]`
  tokens that `checklist.py` parses as its ONLY rule source; onboarding report at
  `asset-pack/onboarding-report.md` (per-photo verdicts, set checks, evaluated-items
  list). Design decision: analysis metadata is cached for rejected photos too (the
  cache records the VLM call; rejection = report entry + no cutout) so re-runs never
  re-pay analysis. Fakes journal calls to `.thumb/provider-calls.jsonl`; the
  zero-VLM-calls-during-order-run guard test reads it and was proven to bite via a
  temporary injected call. 18 tests green. Unblocks nothing new (08 was already
  unblocked); 09 needs this + 08.
