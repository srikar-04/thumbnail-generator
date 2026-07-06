# Gemini API free-tier viability for the thumbnail pipeline

> **Location note:** This file lives in `docs/research/` — a new directory. The repo previously had
> `docs/adr/` but no research convention; `docs/research/` is the sensible parallel home for
> investigation write-ups. Referenced by the plan in `docs/adr/0002`.
>
> **Method:** All claims checked against primary sources (Google `ai.google.dev` docs/terms, OpenAI
> developer docs, Replicate, fal.ai) on **2026-07-06**. Anything not verifiable from a primary source
> is flagged **UNVERIFIED**. Secondary sources (blogs, forums) were deliberately not used as evidence.

## TL;DR verdict table

| Role | Free tier viable as planned? | Why | Recommended fallback |
|---|---|---|---|
| 1. Background generation (image model) | **No** | Every Gemini/Imagen image-generation model is marked **"Not available"** on the free tier of the official pricing page. There is no free image generation via the Gemini API. | Paid Gemini `gemini-3.1-flash-lite-image` ($0.0336/1K image) or `gemini-2.5-flash-image` ($0.039/image) → ~$13–16/mo at 400 images. Cheapest overall: FLUX schnell on Replicate/fal.ai at ~$0.003/image (~$1.20/mo), with quality caveats. |
| 2. Critique / VLM-as-judge | **Yes, with caveats** | `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-3.5-flash` are "Free of charge" (input incl. images + output) on the free tier. Caveats: (a) Google **uses free-tier prompts and outputs to improve its products, incl. human review** — client images/briefs would be exposed; (b) exact free-tier RPM/RPD are no longer published (dashboard-only — UNVERIFIED); (c) free tier is **prohibited for API clients serving EEA/UK/Switzerland users**. | If caveats unacceptable: paid `gemini-2.5-flash-lite` — ~$0.11/mo for 400 judge calls (effectively free). |
| 3. Wording / concepts (LLM) | **Yes, with caveats** | Same free text models, trivial token volume. Same data-usage and EEA caveats as role 2 (briefs are client data). | Paid `gemini-2.5-flash-lite` — pennies per month. |

**Bottom line:** the "all three roles on the Gemini free tier" plan in ADR 0002 fails on role 1 —
image generation simply has no free tier. Roles 2 and 3 work on the free tier mechanically, but for a
commercial service the free-tier data-usage terms (training + human review of client content) argue
for just paying. The full paid-Gemini stack is ~**$14–28/month** (~$0.70–1.40/order); the cheapest
mixed stack is ~**$1.50–2/month** (~$0.07–0.10/order).

---

## Q1. Image-generation models on the Gemini API free tier

**Answer: none.** As of 2026-07-06 the official pricing page lists free-tier input/output as
**"Not available"** for every image-generation model:

- `gemini-3.1-flash-image` (Nano Banana 2) — free tier: Not available
- `gemini-3.1-flash-lite-image` — free tier: Not available
- `gemini-3-pro-image` (Nano Banana Pro) — free tier: Not available
- `gemini-2.5-flash-image` (Nano Banana, legacy) — free tier: Not available
- Imagen 4 (Fast/Standard/Ultra, now deprecated) — free tier: Not available

Source: [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) (accessed 2026-07-06).

**Model lineup and 16:9 support** (from the [image generation docs](https://ai.google.dev/gemini-api/docs/image-generation), accessed 2026-07-06):

- Four models: `gemini-3.1-flash-lite-image` (fastest/cheapest), `gemini-3.1-flash-image`
  (workhorse), `gemini-3-pro-image` (premium), `gemini-2.5-flash-image` (legacy).
- Supported aspect ratios include **16:9** (full list: 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16,
  16:9, 21:9).
- Resolutions: "512px (0.5K), 1K, 2K, and 4K visuals"; the Lite model supports 1K only;
  3.1 Flash adds 0.5K; 3 Pro and 3.1 Flash support 1K/2K/4K.
- A 1K 16:9 output is comfortably croppable/downscalable to 1280×720. **UNVERIFIED:** the exact
  pixel dimensions per aspect ratio (e.g. 1344×768 for 1K 16:9) — the docs' dimension table was not
  retrievable in this session; verify against the docs table before hardcoding dimensions.
- "All generated images include a SynthID watermark." (Same page — see Q3.)

So the free tier fails role 1 outright, irrespective of rate limits.

## Q2. Free-tier rate limits

**Google no longer publishes per-model free-tier RPM/RPD tables.** The
[rate limits page](https://ai.google.dev/gemini-api/docs/rate-limits) (accessed 2026-07-06) now says
rate limits "depend on a variety of factors (such as your usage tier) and can be viewed in Google AI
Studio," linking to the logged-in [AI Studio rate-limit dashboard](https://aistudio.google.com/rate-limit).
The page documents only the tier structure and dimensions:

- Dimensions: requests/minute (RPM), input tokens/minute (TPM), requests/day (RPD), plus
  model-specific limits such as images/minute (IPM).
- Tiers: Free (active project, no billing) → Tier 1 (billing linked, $250 spend cap, instant
  upgrade) → Tier 2/3. Tier 1 also has a $10 / 10-minute rolling spend cap.

**UNVERIFIED:** exact free-tier RPM/RPD for `gemini-2.5-flash`, `gemini-2.5-flash-lite`,
`gemini-3.5-flash`. No live primary source publishes numbers; third-party pages claim ~10 RPM /
~1,500 RPD for Flash-class models but that could not be confirmed from Google. Check the AI Studio
dashboard on the actual project before relying on this.

**Fit assessment (conditional):**
- (a) Image model: moot — no free tier at all (Q1).
- (b) VLM judge: one order = ~20 calls in one sitting. At any plausible Flash free-tier limit
  (historically ≥10 RPM, ≥250 RPD) this fits trivially, even with retries; 5 orders/week ≈ 100
  calls/week is far below any plausible daily cap. But this is inference on unverified numbers —
  a 429-aware retry/queue in the provider interface is cheap insurance.
- (c) Text model: trivial volume, fits under any conceivable limit.

## Q3. Commercial use, data usage, watermarking (free tier)

Source: [Gemini API Additional Terms of Service](https://ai.google.dev/gemini-api/terms) (accessed 2026-07-06).

**Commercial use of outputs — permitted.** The terms do not prohibit commercial use of free-tier
("Unpaid Services") outputs. On ownership: "Google won't claim ownership over that content"
(generated output). "You're responsible for your use of generated content, and for the use of that
content by anyone you share it with," and you must "comply with applicable law in using generated
content, which may require the provision of attribution to your users."

**But — free-tier data is used for training, including human review:**

> "When you use Unpaid Services, including, for example, Google AI Studio and the unpaid quota on
> Gemini API, Google uses the content you submit to the Services and any generated responses to
> provide, improve, and develop Google products and services."

> "To help with quality and improve our products, human reviewers may read, annotate, and process
> your API input and output."

For a commercial service this matters: client briefs, candidate thumbnails (possibly containing
client faces/branding) sent through the free tier may be read by human reviewers and used to train
Google products. Paid Services flip this: "Google doesn't use your prompts … or responses to improve
our products" (logging only for abuse detection).

**Geographic restriction — significant for a commercial service:** "You may use only Paid Services
when making API Clients available to users in the European Economic Area, Switzerland, or the United
Kingdom." If any client is in the EEA/UK/CH, the free tier is off the table contractually.
Also: "You must be 18 years of age or older to use the APIs."

**SynthID watermarking:** "All generated images include a SynthID watermark"
([image generation docs](https://ai.google.dev/gemini-api/docs/image-generation), accessed
2026-07-06). It is an invisible watermark on all Gemini-generated images, free and paid alike —
there is no way to opt out on these models. Nothing in the terms restricts selling watermarked
images; practical effect is only that the images are machine-identifiable as AI-generated (arguably
a plus for AI-content-disclosure compliance). The terms themselves contain no watermarking clauses.

## Q4. Paid-tier Gemini fallback cost (~400 image gens + 400 vision calls + text / month)

Prices from [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) (accessed 2026-07-06):

| Item | Model | Unit price | Monthly (≈400 units) |
|---|---|---|---|
| Images (cheapest) | `gemini-3.1-flash-lite-image`, 1K | $0.0336/image | **$13.44** |
| Images (legacy flat) | `gemini-2.5-flash-image` | $0.039/image | $15.60 |
| Images (workhorse) | `gemini-3.1-flash-image`, 1K | $0.067/image ($0.045 at 0.5K) | $26.80 |
| Images (premium) | `gemini-3-pro-image`, 1K/2K | $0.134/image | $53.60 |
| VLM judge | `gemini-2.5-flash-lite` ($0.10/M in, $0.40/M out) | ~1.5K in + ~0.3K out tokens/call (est.) | **~$0.11** |
| Text/concepts | `gemini-2.5-flash-lite` | trivial tokens | <$0.05 |

(Batch API halves image prices — e.g. $0.0168 per 1K Lite image — but batch is asynchronous and
awkward for a one-sitting order flow.)

**Total paid-Gemini stack: ~$14–27/month, i.e. ~$0.70–1.35 per 20-image order.** The judge and
text roles are rounding errors; images dominate. Token estimate for the judge call is my
calculation, not a quoted price.

## Q5. Cheapest viable alternatives per role

**Image generation:**

| Option | Price | Source (accessed 2026-07-06) |
|---|---|---|
| FLUX schnell (Replicate) | "$3.00 / thousand output images" = $0.003/image | [replicate.com/pricing](https://replicate.com/pricing) |
| FLUX schnell (fal.ai) | "$0.003 per megapixel", rounded up per MP → ~$0.003 for a ~1MP 16:9 image | [fal.ai/models/fal-ai/flux/schnell](https://fal.ai/models/fal-ai/flux/schnell) |
| FLUX Dev (Replicate) | $0.025/image | [replicate.com/pricing](https://replicate.com/pricing) |
| FLUX 1.1 Pro (Replicate) | $0.04/image | same |
| OpenAI `gpt-image-1-mini` | ~$0.011–0.015/image (medium), ~$0.005–0.006 (low) | [OpenAI image generation guide](https://developers.openai.com/api/docs/guides/image-generation) |
| OpenAI `gpt-image-2` (current flagship; also `gpt-image-1.5`) | ~$0.041/image (medium landscape), $0.005–0.006 (low), $0.165 (high landscape); token-priced at $8/M in, $30/M out | [OpenAI pricing](https://developers.openai.com/api/docs/pricing) + guide |

Notes: FLUX.1 [schnell] weights are Apache 2.0 ("can be used for personal, scientific, and
commercial purposes" — [Replicate model page](https://replicate.com/black-forest-labs/flux-schnell));
fal.ai states "Commercial-ready outputs with full usage rights." OpenAI `gpt-image-2` supports
landscape 1536×1024 (and arbitrary sizes up to 3840px, multiples of 16). **UNVERIFIED:** exact 16:9
dimension presets on Replicate/fal schnell endpoints (both advertise preset/custom sizes; confirm
`aspect_ratio`/`image_size` params in the endpoint schema). Quality caveat: schnell is a 4-step
distilled model — cheapest by 10x, but for sellable tech/AI-concept art, FLUX Dev, `gpt-image-1-mini`
(medium), or Gemini 3.1 Flash Lite Image are the realistic quality floor; test before committing.

**VLM judge (cheapest capable):**

| Option | Price /1M tokens (in / out) | ~400 calls/mo | Source |
|---|---|---|---|
| `gemini-2.5-flash-lite` (paid) | $0.10 / $0.40 | ~$0.11 | [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| OpenAI `gpt-5.4-nano` | $0.20 / $1.25 | ~$0.25 | [OpenAI pricing](https://developers.openai.com/api/docs/pricing) |
| OpenAI `gpt-5.4-mini` | $0.75 / $4.50 | ~$1 | same |
| `gemini-2.5-flash` (paid) | $0.30 / $2.50 | ~$0.5 | Gemini pricing |

**Text/concepts:** any of the above nano/lite models; cost is noise (<$0.05/mo).

**Cheapest viable full stack per order (20 images + 20 judge calls + text):**
FLUX schnell ($0.06) + paid `gemini-2.5-flash-lite` judge (~$0.006) + flash-lite text (~$0.001)
≈ **$0.07/order, ~$1.50/month at 5 orders/week.** A quality-safe stack (FLUX Dev or
`gpt-image-1-mini` medium + flash-lite judge) is ~$0.25–0.55/order, still under $11/month.
Per-order arithmetic is mine; unit prices are cited above.

## Q6. Verdict per role

1. **Background generation — free tier NOT viable.** No image model has any free-tier quota on the
   Gemini API (Q1). Recommended fallback: link billing (Tier 1 is instant per the
   [rate-limits page](https://ai.google.dev/gemini-api/docs/rate-limits)) and use
   `gemini-3.1-flash-lite-image` ($0.0336/image, 16:9, 1K) to stay on one provider — ~$13/month.
   If cost floor matters more than prompt-following/text-in-image quality, put FLUX (schnell or Dev)
   on Replicate/fal.ai behind the pluggable provider interface — $0.003–0.025/image.

2. **Critique / VLM judge — free tier viable with caveats.** Free-of-charge Flash models handle
   image+rubric calls; ~20 calls per sitting almost certainly fits (limits themselves UNVERIFIED —
   confirm in AI Studio; build 429 backoff regardless). The real issue is contractual: free-tier
   inputs/outputs feed Google's training with possible human review, and EEA/UK/CH clients require
   paid. Since paid costs ~$0.11/month at this volume, recommendation: **run this role paid** once
   billing is enabled for role 1 anyway — the free tier saves nothing meaningful and costs the
   data-usage terms.

3. **Wording/concepts — free tier viable with caveats.** Same as role 2: mechanically fine at
   trivial volume, same data-usage/EEA caveats over client briefs, and effectively free on paid
   anyway. Same recommendation.

**Net recommendation for ADR 0002:** abandon "free tier for all three roles." Enable billing on the
Gemini project (one provider, one key, ~$14/month all-in at 5 orders/week, no training on client
data, no EEA restriction), and keep the pluggable image-provider interface pointed at FLUX/OpenAI
as the cost/quality escape hatch. Revisit only if image volume grows ~10x, where FLUX-class pricing
starts to matter.

---

### Source index (all accessed 2026-07-06)

- Gemini API pricing — https://ai.google.dev/gemini-api/docs/pricing
- Gemini API rate limits — https://ai.google.dev/gemini-api/docs/rate-limits
- Gemini image generation docs — https://ai.google.dev/gemini-api/docs/image-generation
- Gemini API Additional Terms of Service — https://ai.google.dev/gemini-api/terms
- OpenAI API pricing — https://developers.openai.com/api/docs/pricing
- OpenAI image generation guide — https://developers.openai.com/api/docs/guides/image-generation
- Replicate pricing — https://replicate.com/pricing
- Replicate FLUX schnell model page — https://replicate.com/black-forest-labs/flux-schnell
- fal.ai FLUX schnell model page — https://fal.ai/models/fal-ai/flux/schnell

### Unverified items (explicit)

1. Exact free-tier RPM/RPD/TPM per model — Google removed public tables; dashboard-only
   (login required). Third-party figures (~10 RPM / ~1,500 RPD Flash) NOT confirmed.
2. Exact pixel dimensions per aspect ratio for Gemini image models (e.g. 1K 16:9 = 1344×768?) —
   docs table not retrieved; 16:9 support itself IS verified.
3. Exact 16:9 size presets on Replicate/fal FLUX schnell endpoints — both advertise preset/custom
   sizes but the parameter tables weren't retrievable this session.
4. Judge-call token counts (and therefore judge-role dollar figures) are estimates from cited
   per-token prices, not quoted per-call prices.
