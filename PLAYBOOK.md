# Nexulabs Instagram — daily posting playbook

Followed by the daily scheduled run. One post per day to the Nexulabs Instagram Business account.

## Brand
- Business: Nexulabs, "Websites and CRM systems for small businesses" (nexulabs.co.uk). Custom CRMs for enquiries, quotes, jobs and bookings; websites; hosting; domains/email; branding. Based in the North East of England.
- Voice: UK English. Plain, direct, practical, quietly confident. Short sentences. Address the reader as "you". No hype, no jargon, no emoji in the body (→ arrows are fine), no exclamation marks.
- Visuals: rendered by `render.py` only. Never use stock photos, scraped images, logos of other companies, or images of real people.
  - Logo: the real Nexulabs wordmark from `brand/nexulabs-logo-white.svg` (render.py recolours it per theme). Never retype the logo as text.
  - Colours (from nexulabs.co.uk): ink #0B0B0C, paper #F5F5F7, accent blue #3B2BFF on light / #667DFF on dark (the logo's full stop). Accent is for one or two words or one data point per slide, never more. No other accent colours.
  - Type: Geist (headlines, numbers, body) and Geist Mono (labels, sources), the same as the website.
  - Note: the very first post (2026-11-06) used an earlier orange/Inter style; everything after it uses this brand.
  - Format: 1080×1350 (4:5). Carousels of 4–7 slides are the default; a single-slide post is fine for a strong quote or stat.
  - Alternate ink and paper slides. Cover and closing CTA are ink.

## What to post (Lee's direction, 6 Nov 2026)
Nexulabs posts are about **websites and CRM systems** first. Every post must be useful to a small business owner thinking about their website or their CRM.

**Step 1: check the news first.** Search for tech news from the last 48 hours. Only use a story if it's directly about websites, web design, search/Google changes that affect small business websites, CRMs, online enquiries/bookings, or business software small firms use. If it qualifies, make a "news explained" post: what happened, what it means for a small business website or CRM, what to do. General tech, finance, security or AI stories that don't come back to websites/CRMs don't qualify.

**Step 2: if there's no qualifying news, rotate these** (don't repeat the same one two days running):
1. **Web design (main topic, at least every other day).** Homepage structure, what to put above the fold, mobile layout, calls to action, page speed, website copy, contact forms, booking pages, trust signals, before/after layouts. Use the `browser` mockup and `compare` slides so posts look designed and visual, not text-heavy.
2. **CRM.** Enquiry → quote → booking → job flows, follow-ups, getting off spreadsheets, what a CRM should do for a trades/service business. Use `flow`, `compare` and `list` slides.
3. **Websites + CRM together.** Enquiries going straight from the site into the CRM, one system from first click to finished job.
4. **Logos and branding.** What makes a logo work small, building a simple palette, consistency across van/website/socials. Use `palette` and `compare` slides.

**Look and feel:** posts must look sharp and visual. Prefer mockups, comparisons, flows and big bold statements over walls of text. Max ~30 words of body copy per slide. Statistics are optional; a strong practical point beats a weak number.

## Accuracy rules (non-negotiable)
- Every number on a slide must come from a source fetched during the run, published within the last ~24 months, preferably UK. Prefer primary sources (gov.uk, ONS, BCC, FSB, Ofcom, Enterprise Nation, vendor research with stated methodology).
- Put the source on the slide (`source` field) and name it in the caption.
- Never invent statistics, quotes, clients, case studies or results. If a figure can't be verified, use a how-to or point-of-view post instead.
- Check `log.json` and don't repeat a topic, headline stat or source used in the last 30 days.

## Caption format
1. Hook line (the cover's idea in one sentence).
2. Blank line, 3–5 lines of substance (→ bullets fine), sources named.
3. One or two lines tying it to what Nexulabs does.
4. Soft CTA ("Send us a message or visit nexulabs.co.uk").
5. 6–9 hashtags, mixing broad (#SmallBusinessUK #SME #CRM) and local (#NorthEastBusiness #Sunderland #Newcastle) and topical. Max 2,200 characters.

## Slide spec (post.json)
See `render.py` docstring. Types: cover, stat, bars, hbars, list, quote, cta, compare (instead/try), browser (website mockup with numbered pins), palette (colour swatches), flow (numbered steps). `*word*` = accent. `\n` = line break. Optional: `size` for headline/number size, `glow`, `glow_low`, `highlight`, `unit`, `max`.

## Quality check before publishing
- Render, then build a contact sheet and look at every slide: no text overflow, clipping, orphaned single words, overlapping elements, or awkward line breaks; numbers match the sources; the accent is used sparingly.
- Fix and re-render until every slide is clean.

## Daily routine (what the scheduled run does)
1. Read this file and `log.json`. Check the news (see 'What to post'), otherwise pick today's topic from the rotation; nothing used in the last 30 days.
2. Research with web search; fetch and read the primary source for every figure you'll use.
3. Create `posts/YYYY-MM-DD-<slug>/post.json` and `caption.txt`. Render: `python3 render.py posts/<id>/post.json`.
4. Build a contact sheet, look at every slide, fix and re-render until clean.
5. Commit and push to `main`. Confirm each image URL loads: `https://raw.githubusercontent.com/wheatus2/nexulabs-social/main/posts/<id>/slide-NN.jpg`.
6. Publish via Zapier MCP: app Instagram for Business, action `publish_media_v2` (tool `instagram_for_business_publish_photo_s`), `instagramPageId` = `17841471856846758` (Nexulabs), `media` = list of the raw URLs in order, `caption` = caption.txt.
7. Fetch the permalink via the Make API GET Request action (`https://graph.facebook.com/v21.0/<media_id>?fields=permalink`), append an entry to `log.json`, commit and push.
8. If publishing fails: retry once after 2 minutes. If it's an auth/token error, tell Lee to reconnect Instagram at https://mcp.zapier.com/api/v1/connect-auth/InstagramBusinessCLIAPI?accountId=8724593.
