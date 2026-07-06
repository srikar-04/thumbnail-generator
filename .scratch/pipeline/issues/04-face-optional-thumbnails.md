# Face-optional thumbnails (no-Subject path)

Status: wontfix (for launch — deferred by ADR-0005, not rejected; reopen as the work order for the faceless phase)

## Problem / opportunity

The pipeline assumes every Thumbnail has a Subject layer (creator's face cutout).
Some creators don't want their face on thumbnails (faceless channels are common in
tech-explainer/education). That's currently unserveable — a real product branch.

## Wanted

A no-Subject composition path: Background + Text (+ Icon, per issue 03), with layout
presets designed for it (text can take much more of the frame; the icon or a focal
object becomes the visual anchor — several of the operator's own reference thumbnails
are close to this already).

## Architecture flag

This is an architecture decision, not just a feature:

- ADR-0001 defines a Candidate as composited from three layers with the Subject
  identity-preserving cutout as a pillar. Making Subject optional needs an ADR
  (amend 0001 or add a new one) when triaged.
- CONTEXT.md glossary likely needs updating (Candidate/Layer definitions say "three
  Layers"; Asset Pack requires face photos — a faceless creator's Asset Pack is brand
  elements + style references only).
- Intake changes: Brief/Asset Pack must record whether the creator is face-on or
  faceless.

Do not implement before the ADR conversation happens.

## Comments

- 2026-07-06: ADR conversation happened during PRD synthesis. Decision: **face-only
  launch** (`docs/adr/0005-face-only-launch.md`). Subject stays required at launch,
  but intake records face-on/faceless and data structures treat Subject as optional,
  so this issue becomes a presets+gate change when reopened — no migration.
