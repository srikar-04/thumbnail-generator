# Niche specificity lives in data, never in pipeline code

The pipeline launches serving one niche (Indian tech-explainer/education creators) but must extend to arbitrary niches without engineering work. Therefore all niche-specific knowledge lives in data: the Style Library is keyed by niche (reference thumbnails per niche) and layout rules are niche-tunable preset files. Pipeline code — Brief intake, generation, Critique, Curation, Delivery — contains no niche-specific logic or branches. Adding a niche means curating ~20–30 reference thumbnails and optionally a layout preset, nothing else.

## Consequences

- A hardcoded tech-explainer assumption anywhere in pipeline code is a bug, even while tech-explainer is the only niche served.
- The Critique checklist stays universal (face emotion, text legibility, contrast, clutter); niche taste enters only through the Style Library references.
