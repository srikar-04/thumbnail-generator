# Real Gemini providers + first real Order to a judged Contact Sheet

Status: ready-for-human (code implemented via TDD 2026-07-08; the manual milestone-exit run is the operator's)

## Parent

`.scratch/pipeline/PRD.md` (Milestone 1 exit). Stories 35 (raw writes only), 36, 39, and the real-world proof of 11.

## What to build

Bind the three provider interfaces to paid Gemini (ADR-0002) and run the milestone-closing real Order:

- Concrete providers: the current flash-lite text/VLM model for the LLM and critique roles, the current flash-lite image model at 16:9 for Backgrounds — verify model names and pricing at implementation time (ADR-0002 warns they shift). No pipeline code changes: if a pipeline edit is needed to swap fake→real, that's a seam violation to fix here.
- **Retry-with-backoff on 503/429 inside the provider layer** — the prototype hit frequent transient 503s; a half-finished Order must never die to one.
- **Key hygiene**: key loaded from `.env` / environment at startup, never printed, never committed (the repo's gitignore already covers `.env`).
- **Raw cost ledger writes**: every real provider call appends tokens/images/cost to a per-Order ledger file. No reporting command, no summaries — that's next milestone; the data just has to land.
- **The milestone exit run** (manual): onboard the operator's own Asset Pack, `order new` with a real Brief, `order run` + `order sheet` against real Gemini, operator judges the Contact Sheet.

## Acceptance criteria

Automated, at the CLI-over-disk seam:

- [ ] A fake provider scripted to fail twice with 503 then succeed results in a completed `order run` (retry/backoff proven at the seam, no real network needed).
- [ ] Switching between fake and real providers is configuration, not a code change.
- [ ] After any provider-backed run, the Order folder contains a ledger file with one entry per model call (role, units, cost); entries sum without a reporting layer.
- [ ] The API key appears in no output, no metadata file, no ledger entry, and no Contact Sheet.

Manual (milestone exit, operator-performed):

- [ ] One real Order runs Brief → Contact Sheet on paid Gemini for roughly the projected ~₹65–70, verified from the raw ledger.
- [ ] The operator judges the Contact Sheet: candidates are at or above the prototype's round-D quality bar (black-editorial / red-chips level). This judgment closes Milestone 1 — or files the issues for what's blocking it.

## Blocked by

- 01-critique-ranking-unreliable (defect filter + unranked sheet)
- 02-compose-aware-subject-placement
- 03-icon-aware-layout

## Comments

- 2026-07-08: Implemented red→green in 4 cycles at the established seam
  (tests/test_provider_layer.py), on the operator's explicit instruction —
  note the Blocked-by list above is still open: the *code* (bindings, retry,
  ledger, key hygiene) doesn't depend on 01–03, but the milestone-exit
  Contact-Sheet judgment does, so expect fixed placement and no defect filter
  when judging. Notes for reviewers:
  - Model names/pricing re-verified against ai.google.dev/gemini-api/docs/pricing
    on 2026-07-08: `gemini-2.5-flash-lite` $0.10/$0.40 per M and
    `gemini-3.1-flash-lite-image` $0.0336 per 1K image — binding matches the
    PRD, no mismatch. One catch: `gemini-3.1-flash-lite-preview` is
    discontinued 2026-07-09; the binding pins the stable IDs.
  - `src/thumb/gemini.py` fills all three seats (ADR-0002) + rembg cutouts,
    reusing the prototype's proven call shapes (JSON-mode text calls,
    `ImageConfig(aspect_ratio="16:9")`, inline_data extraction). Deps are the
    `real` optional group in pyproject; fake mode imports none of it.
  - Retry/backoff (`retry_transient`, 5 attempts, exponential, transient =
    TransientProviderError or HTTP 429/503) lives in the provider layer.
    Proven at the seam by scripting the fake to 503 twice
    (`THUMB_FAKE_503S`); bite-proven by removing the decorator (run dies).
  - Per-Order ledger `orders/<id>/ledger.jsonl` (raw writes, story 35): one
    JSON line per model call (role/method/model/units/cost_usd), verified
    1:1 against the fake journal. Non-Order calls bill to
    `.thumb/ledger.jsonl`. Text-only image-model refusals bill their tokens
    honestly before retrying. Determinism test now excludes the ledger —
    a re-run genuinely spends again; resetting it would falsify accounts.
  - Key hygiene: env or workspace `.env` (gitignored), read only by
    `gemini._load_key`; hygiene seam test sweeps all CLI output + every
    file on disk for a sentinel key, bite-proven via an injected metadata
    leak. Candidate `cost_usd` stays a placeholder — the ledger is the
    ground truth; per-candidate attribution is the reporting milestone's.
  - Real-API code paths are deliberately not CI-tested (no credits in CI,
    per the PRD's testing decisions) — first exercised by the operator's
    staged manual run (2–3 candidates first, then 20).
  34 tests green. New: `docs/reference-curation.md` (manual Style Library
  growth playbook). Milestone-exit run instructions delivered to operator.
