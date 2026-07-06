# Operator tool is a CLI over plain files, with an HTML Contact Sheet for Curation

The phase-1 operator interface is a single `thumb` CLI whose subcommands mirror the domain (onboard, order, revise, deliver), storing everything as plain files — creators are folders, orders are folders, images are files, state is `Status:` lines in markdown. No web UI, no database. The one place a terminal fails — visually comparing ~20 Candidates during Curation — is covered by generating a static HTML Contact Sheet per Order (Candidates in a grid, ranked by Critique score) that opens in the browser.

Rejected: a Streamlit/Gradio web UI (2–4× build cost, UI code rots as the pipeline evolves, polishing an interface only the operator sees); Jupyter as the operating tool (hidden state, non-repeatable — fine for R&D only); a database (at tens of orders/month, folders + markdown are inspectable and sufficient; SQLite can be added later if cross-order queries become real).

## Consequences

- Every hour saved on interface goes into the pipeline and selling — the actual phase-1 priorities.
- If the workflow outgrows this (e.g. hiring an editor), Streamlit can be bolted onto the same plain files without migration.
