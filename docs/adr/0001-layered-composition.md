# Thumbnails are composed from layers, not generated single-shot

A Candidate is composited programmatically from three independent layers — an AI-generated Background, a Subject cutout from the creator's real photos, and programmatically rendered Text — rather than prompting an image model to generate the whole thumbnail in one pass. Single-shot generation was rejected because it drifts on the creator's facial identity (non-negotiable for recognizable creators), produces text typos/warping, and forces a full re-roll for any revision; layers keep face fidelity at 100%, make text pixel-perfect, and make revisions surgical (re-render one layer). The cost accepted: more upfront engineering (background removal, compositing, layout rules).

## Consequences

- Every order's intake must include usable creator face photos (good resolution, varied expressions).
- Design conventions are encoded as layout rules in code, compensating for the operator's lack of design training.
- Critique can score layers independently (e.g. text legibility is measurable in isolation).
