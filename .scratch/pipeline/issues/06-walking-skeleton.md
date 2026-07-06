# Walking skeleton: `thumb` CLI end-to-end on fake providers

Status: ready-for-agent

## Parent

`.scratch/pipeline/PRD.md` (Milestone 1). Stories 15, 28, 34, 36 (interfaces + fakes), 38.

## What to build

The tracer bullet: a `thumb` CLI that runs `onboard` → `order new` → `order run` → `order sheet` end-to-end on plain files with all three model roles behind provider interfaces bound to deterministic fakes. Output quality is irrelevant — placeholder backgrounds, naive compositing, plain text are fine. What matters is that every layer exists and connects: CLI subcommands mirroring the domain, Creators-as-folders / Orders-as-folders conventions, `Status:` line lifecycle on the Order, candidate images + per-candidate metadata written to the Order folder, a static HTML Contact Sheet, and the seam test harness (tests invoke the CLI against a temp directory and assert only on-disk outputs).

Also establish here, because every later ticket depends on them:

- The three role-specific provider interfaces (wording/concept LLM, background image model, critique VLM) with a `FakeProvider` for each — canned JSON, canned image fixtures, canned verdicts.
- Onboarding records face-on/faceless; faceless is rejected at intake with a clear "not yet supported" (ADR-0005). Candidate metadata represents Subject as an optional layer even though launch always fills it.
- No niche-specific branches in pipeline code (ADR-0003).

## Acceptance criteria

All at the CLI-over-disk seam, fake providers, temp working directory, no network and no API key:

- [ ] `thumb onboard` creates a Creator folder with recorded niche, brand colors, and face-on/faceless flag; onboarding a faceless Creator fails with a "not yet supported" message and creates no half-written folder.
- [ ] `thumb order new` on an onboarded Creator creates an Order folder containing the Brief and `Status: new`.
- [ ] `thumb order run` produces N candidate images at 1280×720, each with a metadata file alongside recording at minimum: wording, source photo, placement values, layout boxes. Order moves to `Status: generated`.
- [ ] `thumb order sheet` writes a self-contained static HTML Contact Sheet referencing every candidate, openable from disk with no server.
- [ ] `thumb order list` shows the Order and its current `Status:`.
- [ ] Running the same Order twice with fake providers yields identical outputs (determinism).
- [ ] The seam test harness exists and all of the above is covered by tests that assert only files, metadata content, and HTML content — no internals.

## Blocked by

None — can start immediately.
