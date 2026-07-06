# Icon-aware layout — don't bury the background's focal object

Status: ready-for-agent (triaged via PRD.md — launch = locate-and-avoid via VLM bounding box; fourth-layer alternative deferred, would amend ADR-0001)

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
