# Critique stage ranks unreliably — usable as filter only

Status: ready-for-agent (Milestone 1 ticket — see Parent / Acceptance / Blocked by below)

## Parent

`.scratch/pipeline/PRD.md` (Milestone 1). Stories 25–27. Launch scope: build Critique as a **defect filter with annotations** feeding an unranked Contact Sheet. The ranking-improvement ideas below (pairwise, ensembles, calibration) are post-launch — do not build them in this ticket.

## Problem

During the compositor prototype (scratch/prototype, 2026-07-06), the VLM judge
(`gemini-2.5-flash-lite` + rubric) proved directionally useful but unreliable as a
ranker:

- It correctly caught real defects (busy background in cand02, the over-strong pink
  rim light in the first round-B pass).
- But its ordinal rankings contradicted the human eye repeatedly: it scored the
  visibly best round-C candidates below weaker round-B ones, called a classic
  thumbnail-bait grimace "too aggressive," and its overall scores clustered in a
  mushy 5–7 band with high variance between reruns of similar images.

Operator decision for now: **judge scores are used only as a coarse filter (drop the
bottom half), never as the presentation order; the operator ranks by eye.**

## Ideas for the real build (untested)

- Stronger judge model for the final ranking pass (still pennies per order).
- Pairwise comparison prompts ("which of these two is better and why") instead of
  absolute 1-10 scores — ordinal judgments are usually more stable than scalar ones.
- Calibrate the rubric with few-shot examples from the Style Library annotations.
- Ensemble: 2-3 cheap judge calls per candidate, median score.

## Acceptance (original, superseded for Milestone 1)

The Critique stage's top-3 matches the operator's eyeball top-3 on a 20-candidate
order at least ~2 times out of 3, or the ranking role is formally dropped and
Critique is redefined as defect-filter only (would need a CONTEXT.md glossary edit).

> Milestone 1 takes the second branch by decision (PRD): filter-only ships now, the
> top-3 experiment stays post-launch. The CONTEXT.md glossary edit for Critique
> ("scores and ranks" → detects defects and filters) is in scope for this ticket.

## Acceptance criteria (Milestone 1)

At the CLI-over-disk seam with the fake critique VLM returning canned verdicts:

- [ ] Candidates the fake judge marks with a clear defect (illegible text, low
      contrast, missing face emotion, clutter) are dropped before the Contact Sheet;
      the drop and its reason are recorded in the Order folder.
- [ ] Surviving Candidates appear on the Contact Sheet annotated with any non-fatal
      defects the judge flagged.
- [ ] The Contact Sheet presents survivors grouped by style spec, in no score order,
      and displays no numeric scores anywhere.
- [ ] The Critique checklist is universal — no niche-specific items (ADR-0003).
- [ ] CONTEXT.md's Critique glossary entry is updated to the defect-filter definition.

## Blocked by

- 09-candidate-composition
