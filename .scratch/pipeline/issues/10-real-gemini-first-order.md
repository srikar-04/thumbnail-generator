# Real Gemini providers + first real Order to a judged Contact Sheet

Status: ready-for-agent

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
