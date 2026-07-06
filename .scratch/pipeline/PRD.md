# PRD: The `thumb` pipeline — real build

Status: ready-for-agent

Synthesized 2026-07-06 from CONTEXT.md, ADRs 0001–0005, `docs/research/gemini-free-tier-viability.md`, the prototype verdict (`scratch/prototype/NOTES.md`), and `.scratch/pipeline/issues/01–05`. Supersedes nothing; the prototype in `scratch/prototype/` is throwaway and is deleted once its compositor recipe (§Implementation Decisions) is absorbed.

## Problem Statement

Srikar (the operator) sells done-for-you YouTube thumbnails to Indian tech-explainer/education Creators at ₹1,199–1,499 per Order, with no design training and no team. Today there is no production system — only a validated throwaway prototype. Without a real pipeline he cannot take an Order from Brief to Delivery repeatably: every step (wording, backgrounds, cutout, compositing, critique, review, revision) is manual script-poking, results aren't organized per Creator or per Order, quality depends on remembering an unwritten compositor recipe, and nothing enforces the conventions that make a thumbnail worth paying for.

The prototype also proved two things the build must respect: **unconditioned AI generation produces "competent amateur" output that nobody pays for — conditioning on curated reference thumbnails is what lifts it to payable**; and the automated judge cannot be trusted to rank, only to filter.

## Solution

A single `thumb` CLI over plain files (ADR-0004) that runs the whole business: onboard a Creator once into an Asset Pack, then per Order run Brief → Wording/Concepts → reference-conditioned Backgrounds → identity-preserving Subject compositing → programmatic Text → Critique (defect filter) → Contact Sheet in the browser → operator Curation → Delivery, with Revisions re-rendering only the affected Layer (ADR-0001).

The Style Library is a first-class pipeline input, not an add-on: niche-keyed reference thumbnails are analyzed once into style specs (palette, backdrop treatment, text devices, icon usage, subject treatment), and every Background prompt and Text treatment is conditioned on a chosen style spec. All model calls go through the three pluggable provider interfaces on paid Gemini (ADR-0002), with retry/backoff and a per-Order cost ledger.

Launch is face-only per ADR-0005: every Thumbnail has a Subject layer, but intake records face-on/faceless and data structures keep Subject optional so the faceless phase later is presets + lifting a gate.

## User Stories

### Onboarding & Asset Pack

1. As the operator, I want a `thumb onboard` command that creates a Creator folder from name, channel, niche, brand colors, and photos, so that every Creator's Asset Pack lives in one predictable place.
2. As the operator, I want onboarding to record whether the Creator is face-on or faceless, so that the faceless phase later needs no data migration (ADR-0005).
3. As the operator, I want faceless intake to be rejected at launch with a clear "not yet supported" message, so that I never half-serve an unsupported branch.
4. As the operator, I want a one-page source-photo capture guide I can send to every Creator, so that they shoot warm directional light AND an exaggerated-expression range instead of one or the other (issue 05).
5. As the operator, I want onboarding to run the capture-guide checklist against submitted photos and flag failures (flat light, neutral-only expressions, busy background, beauty filters), so that I reject or re-request photos before they become the quality ceiling of every Order.
6. As the operator, I want each Asset Pack photo analyzed once at onboarding for gesture direction, gaze direction, expression, clothing text, and usable crops, so that per-Order placement decisions read cached metadata instead of re-calling a VLM (issue 02).
7. As the operator, I want cutouts generated once per Asset Pack photo at onboarding, so that Orders reuse them instead of paying rembg time per Candidate.
8. As a Creator, I want to hand over only photos, brand colors, and thumbnails I like — once, so that ordering afterwards stays near-zero friction.

### Style Library & reference conditioning

9. As the operator, I want a Style Library folder keyed by niche holding reference thumbnails with their extracted style specs, so that niche taste lives in data, not code (ADR-0003).
10. As the operator, I want a `thumb style add` command that ingests a reference image and extracts a structured style spec (backdrop treatment, palette + accent color, text device, icon usage, subject treatment, composition), so that admired thumbnails become machine-usable conditioning in one step.
11. As the operator, I want every Background prompt built from a chosen style spec rather than from the Brief alone, so that generation targets the niche's actual visual language (flat graphic design) instead of the model's default cinematic scenes — the prototype's single biggest quality lever.
12. As the operator, I want Candidates within one Order spread across 2–3 different style specs, so that the Contact Sheet shows genuinely different directions instead of twelve variations of one look.
13. As the operator, I want a Creator's own admired-thumbnail references (from their Asset Pack) usable as additional style sources, so that Delivery matches what that specific Creator already responds to.
14. As the operator, I want the launch Style Library seeded with the two proven directions — black-editorial and red-chips — plus specs extracted from my curated references, so that the first real Order starts from the prototype's winning quality, not from zero.

### Orders & the pipeline

15. As the operator, I want a `thumb order new` command that takes a Creator and a Brief (title + 2–3 sentence hook), so that starting an Order is one command.
16. As the operator, I want the pipeline to propose 3–5 Wordings (3–5 words each, distinct from the video title), so that copywriting is handled without the Creator approving intermediate steps.
17. As the operator, I want Concepts derived from the Brief and the chosen style specs, so that each Candidate has a deliberate idea behind it rather than a random prompt.
18. As the operator, I want ~20 Candidates per Order composited from Background + Subject + Text layers, so that Curation picks from real variety (ADR-0001).
19. As the operator, I want subject placement decided per Candidate from the photo's cached content metadata and the background's structure — flip, side, scale, crop — so that gestures point into the composition instead of at empty space (issue 02).
20. As the operator, I want the flip decision to weigh readable clothing text against gesture direction, preferring a different photo when they conflict, so that neither mirrored shirt text nor backwards pointing ships.
21. As the operator, I want the background's focal icon located after generation and treated as a layout participant, so that text and subject never bury the one element carrying the Concept (issue 03).
22. As the operator, I want Text rendered programmatically with the proven styled devices (torn-paper chips, label bars, plain-with-accent-word) and hard safe margins, so that words are pixel-perfect, legible at small size, and never cropped.
23. As the operator, I want the compositor to apply the validated subject-integration recipe (palette tint, luminance match, feathered edge, clamped rim light, drop shadow — never a sticker outline, never AI-touching the face), so that the Subject looks lit by the Background while remaining unmistakably the Creator.
24. As the operator, I want every Candidate's metadata (style spec used, wording, photo, placement decisions, layout boxes, critique result, cost) written next to its image, so that I can debug any Candidate and Revisions know exactly what to re-render.

### Critique, Curation, Delivery, Revision

25. As the operator, I want Critique to run the universal checklist (face emotion, text legibility at small size, contrast, clutter) on every Candidate and drop clear defects, so that I never waste Curation time on broken output (issue 01).
26. As the operator, I want Critique used strictly as a filter — the Contact Sheet must not present its scores as a ranking, so that unreliable ordinal judgments don't anchor my eye.
27. As the operator, I want each surviving Candidate's Contact Sheet entry annotated with Critique's detected defects, so that the judge's real strength (catching flaws) is used where it works.
28. As the operator, I want a `thumb order sheet` command producing a static HTML Contact Sheet (grid, hover-zoom, per-Candidate metadata, small-size preview) that opens in my browser, so that Curation is one command away (ADR-0004).
29. As the operator, I want to mark 2–3 curated Candidates for Delivery from the CLI, so that the Order's state records what was sent.
30. As the operator, I want a `thumb order deliver` command that exports the curated Candidates at final 1280×720 with clean filenames into a deliverables folder, so that sending to the Creator is drag-and-drop.
31. As a Creator, I want to receive 2–3 finished Thumbnails to choose from, so that I pick a favorite without wading through twenty variants.
32. As a Creator, I want up to two Revision rounds where my change request is honored precisely, so that "different wording" or "other photo" doesn't come back as a whole new thumbnail.
33. As the operator, I want `thumb order revise` to re-render only the affected Layer (new Wording → re-run Text; different photo → re-run Subject; new direction → re-run Background) reusing everything else, so that Revisions cost minutes and paise, not a full re-roll (ADR-0001).
34. As the operator, I want Order state tracked as a `Status:` line through its lifecycle (new → generated → curated → delivered → in-revision → closed), so that `thumb order list` shows exactly where every commission stands.

### Cost, reliability, operations

35. As the operator, I want every model call logged to a per-Order cost ledger with a running total, so that I can verify each Order stays around ₹65–70 (<6% of price).
36. As the operator, I want all three model roles behind pluggable provider interfaces with retry/backoff for 503/429, so that Gemini's frequent transient failures never kill a half-finished Order and any role can be swapped without touching the pipeline (ADR-0002).
37. As the operator, I want a crashed or interrupted Order run to resume from completed work (existing backgrounds, cutouts, candidates on disk) instead of regenerating, so that a crash never burns paid credits twice.
38. As the operator, I want a fake-provider mode, so that I can exercise the whole pipeline (and its tests) without spending API credits.
39. As the operator, I want the API key loaded from the environment/.env and never printed or committed, and Creator photos kept out of git, so that client faces and credentials stay private.
40. As the operator, I want adding a new Niche to require only Style Library references and an optional layout preset — no code (ADR-0003), so that expansion beyond tech-explainer is curation work.

## Implementation Decisions

- **One deliverable: the `thumb` CLI** (Python, same stack the prototype validated: google-genai, rembg, Pillow, python-dotenv), subcommands mirroring the domain: `onboard`, `style`, `order` (with `new`, `run`, `sheet`, `curate`, `deliver`, `revise`, `list`), per ADR-0004. Plain files only: Creators are folders, Orders are folders inside them, state is `Status:` lines in markdown, images are files. No DB, no web UI.
- **Three provider interfaces** (ADR-0002): wording/concept LLM, background image model, critique VLM. Concrete launch bindings: `gemini-2.5-flash-lite` for LLM and VLM roles, `gemini-3.1-flash-lite-image` at 16:9 for Backgrounds (prototype showed the 2× pricier model buys nothing visible). Retry-with-backoff on 503/429 lives inside the provider layer, not the pipeline. Every provider call reports token/image cost to the Order's ledger. A `FakeProvider` implementation of each interface ships as part of the package (used by tests and `--fake` runs).
- **Style spec is the contract between the Style Library and generation.** A style spec is structured data extracted once per reference image by the VLM: backdrop treatment, palette + single accent color, text device, icon usage, subject treatment, composition/negative-space notes. Background prompts are assembled from style spec + Concept + the prototype's restraint rules ("one focal element, generous negative space, one accent color, no clutter/dense texture"). The prototype's `style_spec.json` shape is the starting schema; the two proven directions (black-editorial, red-chips) are seeded as data.
- **Asset Pack photo metadata is computed at onboarding, cached, and reused** (issue 02): per photo — gesture direction, gaze direction, expression label, clothing-text presence, viable crops — via one cheap VLM call per photo. The per-Candidate placement decision (flip / side / scale / crop) is a pure function of photo metadata + background metadata + layout preset, and its output is persisted in candidate metadata so it is observable at the filesystem seam.
- **Icon-aware layout** (issue 03): after Background generation, one cheap VLM call locates the focal object's bounding box; text blocks and Subject placement avoid it. The alternative (Icon as a fourth programmatic layer) is explicitly deferred — it would amend ADR-0001 and is not launch work; the locate-and-avoid approach is.
- **Critique is a defect filter, not a ranker** (issue 01): checklist-based defect detection (face emotion missing, text illegible at small size, low contrast, clutter, composition collisions), dropping clear failures and annotating survivors. The Contact Sheet presents survivors unranked (grouped by style spec), never ordered by score. Ranking-improvement ideas (pairwise judging, ensembles) are future work behind the same provider interface; the acceptance bar in issue 01 stands.
- **Compositor recipe is fixed as the launch baseline** (from the prototype, absorb then delete `scratch/prototype/`): flip only when placement logic says so; LANCZOS resize; autocontrast + unsharp; ~15% palette tint toward background mean + luminance match; feathered alpha edge (no sticker outline); thin rim light clamped inside the silhouette; drop shadow; balanced 2-line Text with hard safe margins; styled text devices (chips / label bars / plain-accent). The rim-light clamp encodes the one hard-won geometry decision (prototype-derived):

  ```python
  shifted = offset(alpha, dx, dy)              # small offset, e.g. (7, 3)
  edge = subtract(alpha, shifted).blur(1.5)    # tight blur — wide blur = halo
  edge = multiply(edge, alpha)                 # clamp: never spills outside subject
  edge = edge * 0.65                           # subtle, not neon
  ```

- **Identity preservation is absolute** (ADR-0001): the Subject is only ever geometrically and photometrically adjusted — never AI-regenerated, repainted, or restyled. If no Asset Pack photo fits a Concept, the pipeline surfaces "source-photo limitation" rather than degrading identity.
- **Face-only launch gate** (ADR-0005): intake records face-on/faceless; faceless is rejected at the intake edge only. Candidate metadata and layout presets represent Subject as an optional layer; no code deeper than intake may assume a face exists.
- **Resumability**: every pipeline stage writes its outputs (and metadata) to the Order folder as it goes; re-running an Order skips work whose outputs already exist. This is the same mechanism as Revision's re-render-one-Layer.
- **Capture guide ships as a document** generated/maintained in the repo and doubles as the onboarding acceptance checklist (issue 05) — checklist items are data the onboard command evaluates, not prose only.
- **Niche remains data** (ADR-0003): layout presets and Style Library tracks are niche-keyed files; pipeline code has no niche branches.

## Testing Decisions

- **One seam** (operator-confirmed): tests invoke the `thumb` CLI end-to-end against a temp working directory with all three provider interfaces bound to deterministic fakes (canned wording JSON, canned generated-image fixtures, canned critique verdicts). Assertions run only against what lands on disk: folder structure, `Status:` lines, candidate images existing at 1280×720, candidate metadata (placement decisions, layout boxes, style spec attribution), Contact Sheet HTML content, cost ledger totals, deliverable exports.
- A good test asserts external behavior — "after `order run`, every candidate's text box lies inside safe margins and outside the icon's box (per its metadata)" — never internal call order or private function results. Placement/layout logic is deliberately made observable through persisted metadata precisely so tests never need a second seam.
- Golden-path scenarios to cover at that seam: onboard (accept + checklist-reject + faceless-reject), style add, order new→run→sheet→curate→deliver, each Revision type re-rendering only its Layer (assert untouched layers' files are byte-identical), crash-resume (delete half the outputs, re-run, assert completion without regenerating survivors), cost ledger arithmetic, fake-provider determinism (two runs, identical output).
- Real-API quality is validated manually: an occasional real-provider smoke Order whose Contact Sheet the operator eyeballs. Image *quality* is not assertable in CI; image *geometry and bookkeeping* are.
- Prior art: none — this is a greenfield repo; these tests establish the house pattern. The prototype had no tests by design.

## Out of Scope

- **Faceless/no-Subject thumbnails** — deferred by ADR-0005; issue 04 is the reopened work order when the phase arrives. Launch only keeps the door open (intake field, optional-Subject data shapes).
- **Icon as a fourth programmatic layer** — noted in issue 03 as an alternative; launch uses locate-and-avoid. Revisiting means amending ADR-0001.
- **Fixing Critique ranking** — Critique ships as filter-only; the ranking experiments in issue 01 are post-launch.
- **Self-serve product, web UI, database, auth** — phase-1 is operator-only CLI over plain files (ADR-0004).
- **Payments and invoicing automation** — UPI collection stays manual.
- **Niches beyond tech-explainer/education** — extension is Style Library curation (ADR-0003), not build work.
- **Prospecting/outreach tooling** — the Phase-0 channel lists (style sources + prospects) are business ops running alongside the build, not pipeline code.
- **Deleting `scratch/prototype/`** — happens after the compositor recipe is absorbed, as its own small cleanup.

## Further Notes

- **Milestone 1** (from the confirmed plan): one real Order end-to-end — `onboard` (operator's own Asset Pack) → `order new/run/sheet` → curated Contact Sheet — before Delivery/Revision polish. The Style Library seeding (two proven specs + operator references) is inside Milestone 1 because reference conditioning is load-bearing.
- Unit economics guardrail: ~₹65–70 per 20-candidate Order on `gemini-3.1-flash-lite-image`; if the ledger ever shows a real Order drifting past ~10% of price, that's a stop-and-look signal, not a shrug.
- All Gemini images carry SynthID watermarks (ADR-0002); deliverables are detectable as AI-generated. Commercial use is permitted; no client-facing claim should say otherwise.
- Verify current Gemini model names/pricing at implementation time (ADR-0002) — they shift frequently.
- Existing issues 01–05 in this directory map into this PRD as follows: 01 → Critique-as-filter decision, 02 → placement metadata decisions, 03 → icon locate-and-avoid, 04 → deferred (ADR-0005), 05 → capture guide + onboarding checklist. They stay as the granular work orders under this PRD.
