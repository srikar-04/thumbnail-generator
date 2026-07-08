# Reference-thumbnail curation playbook

Manual operator work, done outside the pipeline and fed in via `thumb style add`
(ADR-0003: niche taste lives in data, not code). The prototype proved reference
conditioning is the difference between "competent amateur" and payable output —
so the Style Library must grow deliberately, not from whatever thumbnails happen
to be at hand. This is the repeatable process.

## Where references come from — two lists, two jobs

**1. Style sources (big creators, ~15 channels, study only — never prospects).**
Channels at 500k+ subs in or adjacent to the niche whose thumbnails are clearly
*designed* (consistent visual system across their grid, not one-off luck).
Their scale means a real designer is behind the style — that's the craft we
borrow. Find them from YouTube search on the niche's core topics, "best X
channels" roundups, and who the niche's mid-tier creators visibly imitate.

**2. Working thumbnails from mid/small creators (traction evidence).**
A big channel's thumbnail works partly because the channel is big. A 20k-sub
channel whose video far outperforms its baseline is evidence the *packaging*
worked. Only harvest the outliers:

- Open the channel's Videos tab sorted by Popular and by Recent.
- Eyeball the channel's typical views per video (its median, roughly).
- A video at **~3× or more of that channel's typical views**, from the last
  ~year, is an outlier worth studying. Views on the video alone mean nothing —
  the ratio to the channel's own baseline is the signal.
- Discard outliers explained by something other than packaging (a collab, a
  trend spike, an external share you know about).

The YouTube Data API can accelerate list-building (channel search, per-video
view counts to compute outlier ratios) — that's a one-off research script for
Phase 0 outreach, not pipeline code, and the judgment calls below stay manual.

## What makes a good reference

Take it only if all of these hold:

- **Readable at 120px.** Shrink it to search-result size; if the text or focal
  element dies, the style doesn't matter.
- **Flat graphic design language** — textured color-field backdrop, text on a
  graphic device, one simple icon, studio-lit subject. That's the niche's real
  visual language (prototype finding), not cinematic AI scenes.
- **One idea.** One focal element, one accent color, generous negative space.
  If you can't say in one sentence what the thumbnail is doing, skip it.
- **The style is separable from the person.** We extract backdrop/palette/text
  device — if the thumbnail only works because of who's in it, it teaches the
  library nothing.
- **You'd be comfortable delivering it.** Every spec is a direction real
  Candidates will take.

Save at roughly 1280×720, named descriptively (`black-editorial-heavy-type.png`,
not `img_0231.png`) — the filename becomes the spec's name.

## How many, and when to cull

- **2–4 references per direction.** One reference per direction is enough to
  extract a spec; a second or third confirms the direction is a *style*, not a
  one-off. Don't add near-duplicates of a direction already in the library.
- **3–5 directions per niche.** An Order spreads ~20 Candidates across 2–3
  specs; more than ~5 live directions per niche means none get exercised enough
  to judge.
- **Per-Creator references** (thumbnails the client says they admire) go in via
  `thumb style add <img> --niche <niche> --creator <slug>` — they condition
  that Creator's Orders on top of the niche track.
- **Cull on evidence.** After each judged Contact Sheet, note which specs
  produced the picks and which produced the discards. A spec whose Candidates
  are never picked across 2–3 Orders gets retired. The library is a portfolio,
  not an archive.

## The loop, end to end

1. Collect candidates for the two lists (manual browsing; optionally the
   Data API script for the outlier math).
2. Screen against "what makes a good reference"; save the keepers.
3. `thumb style add <image> --niche tech-explainer` per keeper.
4. Read the extracted spec JSON — if the backdrop/palette/text-device the VLM
   extracted doesn't match what your eye sees, fix the JSON by hand; the spec
   is the artifact, the extraction is just a head start.
5. `thumb style list --niche tech-explainer` and check the spread: at least
   two visibly different directions before running a real Order.
6. Revisit monthly-ish: harvest new outliers, retire specs that never win.
