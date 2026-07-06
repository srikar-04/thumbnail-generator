# Launch is face-only; the Subject layer is required at launch but optional in the data model

The service launches serving only face-on Creators: every delivered Thumbnail includes a Subject layer (identity-preserving cutout per ADR-0001). Faceless channels — common in the tech-explainer/education niche — are deliberately deferred to a later phase. The compositor prototype (2026-07-06) showed that a no-Subject path is a real product branch, not a variant: it needs its own layout presets (text/icon become the visual anchor), its own Critique expectations (no face-emotion check), and a different Asset Pack intake (brand elements + style references, no face photos). Building that second path before the first paying order would roughly double pre-revenue layout and Critique work; face-only is the smaller surface on which to validate ₹1,199 demand.

To keep the deferral cheap to reverse, the restriction lives at the edges, not in the core:

- **Intake records the branch.** Onboarding captures whether a Creator is face-on or faceless. At launch, faceless intake is rejected with a clear "not yet supported" — but the field exists from day one.
- **Data structures treat Subject as optional.** Candidate metadata, layout presets, and the composition pipeline are written so that "no Subject layer" is a representable state (an absent layer, not a crash). Only the launch-phase intake gate enforces face-only.
- **Pipeline code contains no face-always assumptions** beyond that gate — the same discipline ADR-0003 applies to niches. A hardcoded "there is always a face" branch deep in compositing or Critique is a bug.

Enabling the faceless phase later should therefore be: new layout presets (data, per ADR-0003), a faceless Critique checklist variant, capture-guide/intake copy, and lifting the gate — plus amending ADR-0001's three-layer definition and the CONTEXT.md glossary (Candidate, Layer, Asset Pack) at that time. No storage or pipeline migration.

## Consequences

- Phase 0 outreach should target face-on creators; a faceless prospect is a "later phase" conversation, not an order.
- `.scratch/pipeline/issues/04-face-optional-thumbnails.md` is deferred by this ADR, not rejected — it becomes the work order for the faceless phase.
- The CONTEXT.md glossary keeps its three-layer language until the faceless phase actually amends it.
