# Icon-aware layout — don't bury the background's focal object

Status: ready-for-agent (Milestone 1 ticket — see Parent / Acceptance / Blocked by below)

## Parent

`.scratch/pipeline/PRD.md` (Milestone 1). Story 21. Launch scope is **locate-and-avoid** only; the Icon-as-fourth-layer alternative below stays deferred (it would amend ADR-0001).

## Problem

Round D backgrounds contain a deliberate focal icon (e.g. d02's glossy black infinity
symbol on paper). The compositor placed text bars and the subject with no knowledge of
where that icon is, half-burying it — the one element carrying the concept.

## Wanted

- Locate the background's focal object after generation (cheap VLM call returning a
  bounding box, or request the icon at a known position in the generation prompt and
  trust-but-verify).
- Text block and subject placement must avoid the icon's box (treat it as a third
  layout participant: subject / text / icon).
- Alternative worth testing: composite the icon as a SEPARATE programmatic layer
  (like Text) instead of asking the image model for it — full position control,
  reusable icon set per niche, one less thing generation can get wrong. This would
  extend ADR-0001's layer model from 3 layers to 4 (Background, Icon, Subject, Text).
  **Deferred — out of Milestone 1 scope (would amend ADR-0001).**

## Acceptance criteria

At the CLI-over-disk seam with the fake critique VLM returning a canned focal-object
bounding box for fixture backgrounds:

- [ ] After Background generation, the focal object's bounding box is recorded in the
      Candidate's metadata.
- [ ] Text layout boxes in metadata do not intersect the icon's box.
- [ ] The Subject's placement box does not cover the icon's box (small tolerance
      overlap is acceptable if the layout preset defines one — the rule and tolerance
      must be observable in metadata, not implicit).
- [ ] A background where the fake VLM reports no focal object composes exactly as
      before (no icon box in metadata, no layout restriction applied).
- [ ] Placement (ticket 02) and icon avoidance compose: a fixture combining a
      gesture photo + an icon background yields metadata satisfying both tickets'
      geometry rules.

## Blocked by

- 09-candidate-composition
