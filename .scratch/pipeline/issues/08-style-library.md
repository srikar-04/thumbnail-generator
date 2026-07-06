# Style Library: reference→style-spec extraction + seeded proven directions

Status: ready-for-agent

## Parent

`.scratch/pipeline/PRD.md` (Milestone 1). Stories 9, 10, 13, 14. The PRD's load-bearing finding: reference conditioning is what lifts output from "competent amateur" to payable — this is core pipeline, not an add-on.

## What to build

The Style Library as a first-class, niche-keyed data store (ADR-0003), plus the command that grows it:

- `thumb style add <image> --niche <niche>`: ingests a reference thumbnail and extracts a structured **style spec** via the critique VLM provider — backdrop treatment, palette + single accent color, text device, icon usage, subject treatment, composition/negative-space notes. The prototype's `style_spec.json` is the starting schema shape.
- Storage keyed by niche: references and their specs live together; adding a niche is adding files, never code.
- **Seed data**: the two operator-validated directions ship as specs — **black-editorial** (near-black textured backdrop, heavy white text, one red accent word, no bars) and **red-chips** (red-orange grunge wall, torn-paper white chips, black text, red accent word) — alongside specs extracted from the operator's curated reference images.
- A Creator's own admired-thumbnail references (from their Asset Pack, ticket 07) can be ingested as additional style sources scoped to that Creator.
- A read API/convention the Order pipeline uses to pick 2–3 specs for a given niche (consumed by ticket 09).

## Acceptance criteria

At the CLI-over-disk seam with fake VLM provider:

- [ ] `thumb style add` on a fixture image writes a style spec containing all schema fields (backdrop, palette + accent, text device, icon usage, subject treatment, composition) under the given niche.
- [ ] The two seeded specs (black-editorial, red-chips) exist as data for the tech-explainer niche and pass the same schema validation as extracted specs.
- [ ] A Creator-scoped reference from an Asset Pack can be ingested and is retrievable alongside the niche track.
- [ ] Listing available specs for a niche returns seeded + added specs; an unknown niche returns empty, not an error branch in pipeline code.
- [ ] No pipeline code contains a niche-specific branch (ADR-0003) — adding a second niche in a test is pure data setup.

## Blocked by

- 06-walking-skeleton
