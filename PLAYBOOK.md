# Nexulabs Instagram — daily posting playbook

Followed by the scheduled runs. **Three posts a day** (around 9am, 3pm and 8pm UK time) to the Nexulabs Instagram account and Facebook Page.

## Brand
- Business: Nexulabs, "Websites and CRM systems for small businesses" (nexulabs.co.uk). Custom CRMs for enquiries, quotes, jobs and bookings; websites; hosting; domains/email; branding. Based in the North East of England.
- Voice: UK English. Plain, direct, practical, like Lee talking to a customer. Short sentences. Address the reader as "you". No hype, no jargon, no emoji, no exclamation marks. See "Sound like a person".
- Visuals: rendered by `render.py`. Photos only from Lee's library in `photos/` (see "Photos from Lee's library"). Never the Unsplash API, scraped images, logos of other companies, or other stock sites.
  - Logo: the real Nexulabs wordmark from `brand/nexulabs-logo-white.svg` (render.py recolours it per theme). Never retype the logo as text.
  - Colours (from nexulabs.co.uk): ink #0B0B0C, paper #F5F5F7, accent blue #3B2BFF on light / #667DFF on dark (the logo's full stop). Accent is for one or two words or one data point per slide, never more. No other accent colours.
  - Type: Geist (headlines, numbers, body) and Geist Mono (labels, sources), the same as the website.
  - Note: the very first post (2026-11-06) used an earlier orange/Inter style; everything after it uses this brand.
  - Format: 1080×1350 (4:5). Carousels of 4–7 slides are the default; a single-slide post is fine for a strong quote or stat.
  - Alternate ink and paper slides. Cover and closing CTA are ink.

## What to post (Lee's direction, 6 Nov 2026)
Nexulabs posts are about **websites and CRM systems** first. Every post must be useful to a small business owner thinking about their website or their CRM.

**Research the UK first (Lee's rule).** Search UK sources and UK news first: BBC, gov.uk, ICO, HMRC, ONS, FSB, British Chambers of Commerce, Enterprise Nation, Ofcom, UK trade press (Computer Weekly, Startups.co.uk, Small Business UK, The Drum). Prefer UK stories, UK statistics and UK rules (GDPR/ICO, cookie rules, accessibility, Making Tax Digital, Companies House). Use US or global sources only when there's no UK equivalent, and say clearly in the caption that it's US/global data. North East angles are a bonus.

**Step 1: check the news first.** Search for tech news from the last 48 hours. Only use a story if it's directly about websites, web design, search/Google changes that affect small business websites, CRMs, online enquiries/bookings, or business software small firms use. If it qualifies, make a "news explained" post: what happened, what it means for a small business website or CRM, what to do. General tech, finance, security or AI stories that don't come back to websites/CRMs don't qualify.

**Step 2: if there's no qualifying news, rotate these** (don't repeat the same one two days running):
1. **Web design (main topic, at least every other day).** Homepage structure, what to put above the fold, mobile layout, calls to action, page speed, website copy, contact forms, booking pages, trust signals, before/after layouts. Use the `browser` mockup and `compare` slides so posts look designed and visual, not text-heavy.
2. **CRM.** Enquiry → quote → booking → job flows, follow-ups, getting off spreadsheets, what a CRM should do for a trades/service business. Use `flow`, `compare` and `list` slides.
3. **Websites + CRM together.** Enquiries going straight from the site into the CRM, one system from first click to finished job.
4. **Logos and branding.** What makes a logo work small, building a simple palette, consistency across van/website/socials. Use `palette` and `compare` slides.

**Look and feel:** posts must look sharp and visual. Prefer mockups, comparisons, flows and big bold statements over walls of text. Max ~30 words of body copy per slide. Statistics are optional; a strong practical point beats a weak number.

## Sound like a person, not AI (Lee's rule, 6 Nov 2026)
Posts must read as if Lee wrote them himself. If a line sounds like marketing copy or a chatbot, rewrite it.

**Captions**
- 40–120 words. Short paragraphs, the way you'd write a message to a customer. Contractions (it's, you'll, don't). Plain words.
- No bullet lists with arrows or emoji. No bold claims. At most one question, and don't open with a question every time. Vary the first line from post to post.
- 3–5 hashtags at the very end, lowercase is fine. Never more than 5.
- Name sources in normal words ("a survey from X this week found…"), not in brackets with full citations.
- No invented anecdotes, clients or "a customer told us".

**Never use** (captions or slides): unlock, elevate, seamless, game-changer, leverage, streamline, robust, empower, supercharge, transform, journey, landscape, delve, harness, "in today's…", "here's what/how/the thing", "let's dive in", "the truth is", "it's not X, it's Y" / "not just X", "from X to Y" slogans, "ready to…?", "quietly", "impossible to miss", "level up", "next level", "say goodbye to", "the secret", "ever wondered", groups of three adjectives, em dashes (—), "→" bullets, exclamation marks.

**Slides**
- Write slide text the way people talk: short, specific, a bit dry. One idea per slide.
- Kicker labels are optional. Use them on one or two slides at most, not every slide.
- Vary the format: some days a single image, some days 3–5 slides, occasionally 6–7. Only end with the CTA slide about every other post.
- Rotate layouts so posts don't all look the same: change which slide types you use, and swap ink/paper order.

## Three posts a day (Lee's rule, 6 Nov 2026)
- Each run makes one post. Name the folder `posts/YYYY-MM-DD-HHMM-<slug>` (time of the run) so same-day posts don't clash.
- Each post must differ from the **previous post** (not just yesterday's) in category, style and cover theme. Over a day, try to cover three different categories.
- Rough shape for the day: **morning** a meatier carousel (web design or CRM), **afternoon** something quick and visual (a single image or 3 slides: a before/after, a tip, a mockup), **evening** a lighter or more conversational one (a point of view, branding, a question to the audience). Mix it up; this is a guide, not a template.
- News: at most one news post per day, and never the same story twice.
- No topic, headline or stat repeated within 30 days (that's about 90 posts, so keep ideas fresh).

## Make every post look different (Lee's rule, 6 Nov 2026)
Lee noticed the first posts all looked the same. Every post must look clearly different from the one before it.
- Set a post-level `"style"` in post.json. Five styles exist in render.py:
  - `studio`: grid, soft blue glow, logo top-left
  - `editorial`: magazine feel, thin rules above and below, lighter headline weight, square corners
  - `bold`: heavy type, logo moved to the bottom, works best with a `blue` cover
  - `minimal`: centred, no decoration, small centred logo
  - `poster`: big outlined numbers or a character in the background (`"deco"` per slide; `"deco": ""` to hide), pill-shaped header
- Never use the same style as the previous post (check the last entries in `log.json`, which record `style`). Cycle through all five before repeating one.
- Mix the three themes: `ink` (dark), `paper` (light) and `blue` (brand blue background). Change the cover theme from post to post, and don't always alternate dark/light in the same order.
- Vary the structure too: single image vs carousel, slide count, which slide types are used.

## Photos from Lee's library (Lee's idea, 8 Nov 2026)
Lee downloads photos he likes from unsplash.com (Unsplash Licence: free commercial use, editing allowed) and uploads them to `photos/` in this repo, named after the photographer (`jane-smith.jpg`, optionally `jane-smith--short-description.jpg`). Do **not** use the Unsplash API or any other image source: its API terms forbid editing/re-hosting and automated use.
- Use a photo **roughly one post in three**, usually as the cover (`photo` slide type), with our type and logo over it. The rest stay as designed graphics.
- `python3 photo.py list` shows unused photos. Look at the photo before choosing it and only use one that genuinely suits the topic. If none fits, or the folder is empty, make a designed post instead. Never let it stop a post going out.
- `python3 photo.py prepare photos/<file> posts/<id>/photo.jpg [--focus x,y]` crops it to 4:5 and gives the credit line. Put that in the slide's `credit` field and as the last line of the caption.
- `shade`: default (dark fade at the bottom), `full` (overall darken for busy photos) or `blue` (brand blue fade). Check the text is easy to read at phone size.
- After publishing, `python3 photo.py retire photos/<file>` (moves it to `photos/used/`) and record the file in `log.json`, so it's never reused.
- If the library has fewer than 3 unused photos, say so in the summary so Lee can add more.

## Accuracy rules (non-negotiable)
- Every number on a slide must come from a source fetched during the run, published within the last ~24 months. UK sources first; non-UK only when there's no UK equivalent, and say so. Prefer primary sources (gov.uk, ONS, BCC, FSB, Ofcom, Enterprise Nation, vendor research with stated methodology).
- Put the source on the slide (`source` field) and name it in the caption.
- Never invent statistics, quotes, clients, case studies or results. If a figure can't be verified, use a how-to or point-of-view post instead.
- Check `log.json` and don't repeat a topic, headline stat or source used in the last 30 days.

## Caption format
Follow "Sound like a person" above. Roughly: an opening line that isn't a cliché, a couple of short paragraphs with the actual point, a light mention of what Nexulabs does (not every time), then 3–5 hashtags. Keep it under 120 words.

## Slide spec (post.json)
See `render.py` docstring. Types: cover, stat, bars, hbars, list, quote, cta, compare (instead/try), browser (website mockup with numbered pins), palette (colour swatches), flow (numbered steps). `*word*` = accent. `\n` = line break. Optional: `size` for headline/number size, `glow`, `glow_low`, `highlight`, `unit`, `max`.

## Quality check before publishing
- Render, then build a contact sheet and look at every slide: no text overflow, clipping, orphaned single words, overlapping elements, or awkward line breaks; numbers match the sources; the accent is used sparingly.
- Fix and re-render until every slide is clean.

## Daily routine (what the scheduled run does)
0. **Check `queue.json` first.** If it lists any posts, publish the first one exactly as it is (its images and caption are already in `posts/<id>/`), log it, remove it from `queue.json`, commit and push, and stop there. Don't create a new post that day.
1. Read this file and `log.json`. Check the news (see 'What to post'), otherwise pick today's topic from the rotation; nothing used in the last 30 days.
2. Research with web search; fetch and read the primary source for every figure you'll use.
3. Create `posts/YYYY-MM-DD-<slug>/post.json` and `caption.txt`. Render: `python3 render.py posts/<id>/post.json`.
4. Build a contact sheet, look at every slide, fix and re-render until clean.
5. Commit and push to `main`. Confirm each image URL loads: `https://raw.githubusercontent.com/wheatus2/nexulabs-social/main/posts/<id>/slide-NN.jpg`.
6. Publish to Instagram via Zapier MCP: app Instagram for Business, action `publish_media_v2` (tool `instagram_for_business_publish_photo_s`), `instagramPageId` = `17841471856846758` (Nexulabs), `media` = list of the raw URLs in order, `caption` = caption.txt.
6b. Also publish to the Nexulabs Facebook Page via Zapier MCP: app Facebook Pages, action `page_stream` (tool `facebook_pages_create_page_post`), `page` = `1484176674771345` (the Nexulabs Page; confirm with inspect_zapier_actions if it ever fails), `source` = the same raw image URLs in order (up to 10), `message` = caption.txt. If Facebook Pages has no connection yet, skip this step and mention it in the summary. A Facebook failure must not stop or undo the Instagram post.
7. Fetch the permalink via the Make API GET Request action (`https://graph.facebook.com/v21.0/<media_id>?fields=permalink`), append an entry to `log.json` (include `style`, `cover_theme` and `facebook_post_id` if posted), commit and push.
8. If publishing fails: retry once after 2 minutes. If it's an auth/token error, tell Lee to reconnect Instagram at https://mcp.zapier.com/api/v1/connect-auth/InstagramBusinessCLIAPI?accountId=8724593.
