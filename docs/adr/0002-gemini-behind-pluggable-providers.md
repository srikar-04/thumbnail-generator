# All model roles run on the paid Gemini API, behind pluggable provider interfaces

The pipeline's three model roles — Wording/Concept generation (LLM), Critique (VLM-as-judge), and Background generation (image model) — all use Google's Gemini API **paid tier** (billing enabled on the Google project), each wrapped behind a role-specific interface (e.g. `generate_background(prompt) -> image`) so any single role can be swapped to another provider without touching the pipeline.

Originally this decision targeted the **free tier**; research (see `docs/research/gemini-free-tier-viability.md`, 2026-07-06) invalidated that: image generation is not available on the Gemini free tier at all, free-tier content is subject to Google human review (unacceptable for client face photos), and free tier is contractually barred when serving EEA/UK/Switzerland users. The paid tier fixes all three at ~$0.70–1.35 per order (~$14–27/month at full volume) — under 10% of the ₹1,199–1,499 order price.

Alternatives rejected for launch: **FLUX schnell via Replicate/fal.ai** (~$0.003/image — cheapest, but the speed-distilled model has the weakest prompt adherence, and Backgrounds are the only layer where model quality is visible; also adds a second provider for a solo operator) and **OpenAI gpt-image** (strong quality, but a second account/billing relationship for a marginal delta, and Gemini would still be needed for the other two roles). One provider = one key, one bill, one failure surface, and the same provider's LLM writes the prompts its image model consumes.

## Consequences

- If Gemini background quality disappoints in real Contact Sheets, swap only the background provider to OpenAI gpt-image or FLUX (one function, one setting) — the decision is made with order evidence, not upfront.
- All Gemini-generated images carry an invisible SynthID watermark (no opt-out); commercial use and resale are permitted, but deliverables are detectable as AI-generated.
- The Critique seat is permanently filled by whatever capable VLM is cheapest; there is no planned "upgrade" path for the judge.
- Verify current Gemini model names and pricing at implementation time — they shift frequently.
