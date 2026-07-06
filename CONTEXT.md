# Thumbnail Generator

An AI-assisted thumbnail business for YouTube long-form creators — first run as a done-for-you service, later possibly a self-serve product.

## Language

**Creator**:
A YouTube long-form channel owner, roughly 10k–500k subscribers, who commissions thumbnails. The paying customer.
_Avoid_: content creator, user, client, YouTuber

**Thumbnail**:
The 1280×720 image attached to a YouTube long-form video to drive click-through.
_Avoid_: cover, preview image

**Asset Pack**:
The per-Creator collection gathered once at onboarding: 10–20 varied-expression face photos, brand colors/logo, and example thumbnails they like. Reused across all their orders.
_Avoid_: onboarding files, client folder

**Brief**:
The per-order input: video title plus 2–3 sentences on the video's hook. Deliberately tiny to keep ordering friction near zero.
_Avoid_: request, ticket, order form

**Order**:
One commission: Brief in, final Thumbnail out, including up to two Revision rounds. Further changes are a new Order.
_Avoid_: job, project, request

**Concept**:
A proposed background/scene idea for an Order, derived from the Brief and the Style Library. One axis of Candidate variation.
_Avoid_: idea, direction

**Delivery**:
Sending the Creator 2–3 finished thumbnails to choose from.
_Avoid_: handoff, submission

**Revision**:
A creator-requested change after Delivery, executed by re-rendering only the affected Layer. Two rounds are included per Order.
_Avoid_: edit, redo, iteration

**Wording**:
The 3–5 words rendered on the Thumbnail — copywriting distinct from the video title, proposed by the pipeline unless the Creator overrides.
_Avoid_: title, caption, headline

**Candidate**:
One generated thumbnail variant, not yet chosen for delivery. Many Candidates are produced per order; few survive Critique and Curation.
_Avoid_: draft, option, output

**Layer**:
One of the three independently produced parts of a Candidate: Background, Subject, or Text. Candidates are composited from Layers, never generated single-shot.

**Background**:
The Layer behind the Subject — an AI-generated scene or stylized video still.
_Avoid_: backdrop, scene

**Subject**:
The identity-preserving cutout of the Creator from their real photos, background-removed and color-graded.
_Avoid_: face, portrait, person layer

**Text**:
The Layer of programmatically rendered words (real fonts, stroke, shadow) — never AI-painted text.
_Avoid_: caption, title overlay

**Critique**:
The automated stage that scores and ranks Candidates against the thumbnail convention checklist (face emotion, text legibility at small size, contrast, clutter).
_Avoid_: review, QA, evaluation

**Contact Sheet**:
The static HTML grid of an Order's Candidates, ranked by Critique score with annotations, that the operator reviews in a browser to perform Curation.
_Avoid_: gallery, preview page, results page

**Curation**:
The human step where the operator picks the deliverable from top-ranked Candidates using the convention checklist.
_Avoid_: selection, approval

**Niche**:
A content category (e.g. tech-explainer, education, entertainment) with its own thumbnail conventions, expressed as a Style Library track and layout presets — never as pipeline code.
_Avoid_: category, genre, vertical

**Style Library**:
The curated collection of proven high-CTR reference thumbnails, organized by niche, used to condition generation and calibrate Curation.
_Avoid_: inspiration folder, moodboard
