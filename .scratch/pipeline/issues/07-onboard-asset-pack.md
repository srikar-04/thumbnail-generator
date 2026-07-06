# Onboarding: real Asset Pack intake with capture checklist, photo metadata, cutouts

Status: ready-for-agent

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

- [ ] `thumb onboard` with a photo set writes, per accepted photo: a cached metadata record (gesture, gaze, expression, clothing text, crops) and a cutout file with transparency.
- [ ] Photos failing checklist items are flagged in an onboarding report on disk; a photo set with zero expression variety (all neutral) produces a failure the operator can read.
- [ ] Checklist items are data, not hardcoded prose — the evaluated items in the report match the checklist source.
- [ ] The capture guide document exists in the repo and its checklist items are the same source the onboard command evaluates.
- [ ] Re-running onboard does not re-analyze or re-cut photos whose outputs already exist.
- [ ] Faceless rejection from the skeleton still holds; a face-on Creator's Asset Pack records their style-reference images.
- [ ] Manual (not CI): the operator's own 9 photos onboard successfully end-to-end.

## Blocked by

- 06-walking-skeleton
