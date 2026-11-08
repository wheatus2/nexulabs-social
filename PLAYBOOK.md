# Nexulabs Instagram — daily posting playbook

> **Design update (Lee, 8 Nov 2026):** Lee said the posts looked "very AI generated" and chose the flat **product** style, built around real UI screens (see "Design direction" below). This replaces any instruction elsewhere, including in the scheduled task prompts, to use colourful gradient styles (aurora, neon, spectrum, glass), palettes or patterns. Use `"style": "product"` for every feed post, Reel, Story and LinkedIn image. In the logs, record `theme` and `screen` instead of `palette` and `pattern`.

> **Publishing update (Lee, 8 Nov 2026):** Zapier's task allowance ran out, so publishing moves to **GitHub Actions** (free, no task limits). See "Publishing via GitHub Actions" below. This replaces the Zapier publishing steps in the scheduled task prompts (Instagram `publish_media_v2` / `publish_video`, Facebook `page_stream` / `page_video`, Stories via "Make API Mutating Request", permalink lookups via "Make API GET Request"). Use Zapier only as the fallback described there. LinkedIn still uses Zapier.

Followed by the scheduled runs. **Three posts a day** (around 9am, 3pm and 8pm UK time) to the Nexulabs Instagram account and Facebook Page.

## Brand
- Business: Nexulabs, "Websites and CRM systems for all types of businesses" (nexulabs.co.uk; the site says "businesses of every kind"). Custom CRMs for enquiries, quotes, jobs and bookings; websites; hosting; domains/email; branding. Based in the North East of England.
- Voice: UK English. Plain, direct, practical, like Lee talking to a customer. Short sentences. Address the reader as "you". No hype, no jargon, no emoji, no exclamation marks. See "Sound like a person".
- Visuals: rendered by `render.py`. Photos only from the library in `photos/` (see "Photos from the library"). Never the Unsplash API, scraped images, logos of other companies, or other stock sites.
  - Logo: the real Nexulabs wordmark from `brand/nexulabs-logo-white.svg` (render.py recolours it per theme). Never retype the logo as text.
  - Colours (from nexulabs.co.uk): ink #0B0B0C, paper #F5F5F7, accent blue #3B2BFF on light / #667DFF on dark (the logo's full stop). Accent is for one or two words or one data point per slide, never more. No other accent colours.
  - Type: Geist (headlines, numbers, body) and Geist Mono (labels, sources), the same as the website.
  - Note: the very first post (2026-11-06) used an earlier orange/Inter style; everything after it uses this brand.
  - Format: 1080×1350 (4:5). Carousels of 4–7 slides are the default; a single-slide post is fine for a strong quote or stat.
  - Flat colour only: vary the `blue`, `ink`, `paper` and `lilac` themes across slides. See "Design direction".

## What to post (Lee's direction, 6 Nov 2026)
Nexulabs posts are about **websites and CRM systems** first, plus branding, hosting, domain names, AI and automation, and verified tech news. Every post must be useful to a UK business owner or manager thinking about their website, CRM or online presence.

**Never say "small business" or "small businesses" (Lee, 8 Nov 2026).** Not on slides, captions, Reels, Stories, hashtags (#smallbusiness etc.) or alt text. Nexulabs works with all types of businesses. Say "businesses", "business owners", "your business", or name the trade (cafés, trades, salons). The audience is still mostly owner-run UK firms, so keep the advice practical.

**Never mention Lee Wheatley in any post (Lee, 8 Nov 2026).** Not by name, initials or "our founder" on slides, captions, Reels, Stories, alt text, LinkedIn, Facebook or anywhere else that's published. Posts speak as Nexulabs ("we"), never as Lee personally.

**Research the UK first (Lee's rule).** Search UK sources and UK news first: BBC, gov.uk, ICO, HMRC, ONS, FSB, British Chambers of Commerce, Enterprise Nation, Ofcom, UK trade press (Computer Weekly, Startups.co.uk, Small Business UK, The Drum). Prefer UK stories, UK statistics and UK rules (GDPR/ICO, cookie rules, accessibility, Making Tax Digital, Companies House). Use US or global sources only when there's no UK equivalent, and say clearly in the caption that it's US/global data. North East angles are a bonus.

**Step 1: check the news desk first (every run).** See "News desk" below. If there's a verified, relevant tech story we haven't covered, make a "news explained" post. **If there's nothing relevant, that's fine (Lee, 8 Nov 2026): carry on with step 2 as normal.** Never force a weak story.

**Step 2: if there's no qualifying news, rotate these** (don't repeat the same one two days running):
1. **Web design (main topic, at least every other day).** Homepage structure, what to put above the fold, mobile layout, calls to action, page speed, website copy, contact forms, booking pages, trust signals, before/after layouts. Use `browser` and `screen` (`phone`) mockups and `compare` slides so posts look designed and visual, not text-heavy.
2. **CRM.** Enquiry → quote → booking → job flows, follow-ups, getting off spreadsheets, what a CRM should do for a trades/service business. Use `flow`, `compare` and `list` slides.
3. **Websites + CRM together, and the types of each (Lee, 8 Nov 2026).** Enquiries going straight from the site into the CRM, one system from first click to finished job. Also explainer series on:
   - **Types of website:**
     - Brochure or info site
     - Landing page
     - E-commerce shop
     - Booking site
     - Portfolio
     - Membership or customer-login site
     - Web app or customer portal
     - Directory
   - **Types of CRM:**
     - Off-the-shelf all-rounders, e.g. HubSpot, Zoho, Pipedrive
     - Industry-specific: trades, salons, travel
     - Spreadsheet "CRMs" and their limits
     - Custom-built CRMs (what Nexulabs does)
     - For each type: who it suits, what it costs in time and effort, and when to move up
   - **How websites and CRMs link:**
     - Web forms posting into the CRM
     - Embedded booking widgets
     - Integrations and APIs explained simply
     - Webhooks
     - Zapier/Make-style connectors
     - Customer portals that log in to CRM data
     - Two-way sync (stock, availability, prices)
     - What breaks when they aren't linked
   Good formats are "Which website does your business actually need?" and "3 ways to connect your website to a CRM". Use `flow`, `compare`, `list` and `browser` slides. Any claim about what a named product can do needs a fetched source.
4. **Logos and branding.** What makes a logo work small, building a simple palette, consistency across van/website/socials, brand voice, a brand kit. Use `palette` and `compare` slides.
5. **AI and automation in websites and CRMs (Lee, 8 Nov 2026).** Real, available things only:
   - Chat and booking assistants on websites.
   - Automatic enquiry replies and follow-ups.
   - Lead scoring.
   - AI-drafted quotes.
   - Auto-reminders and review requests.
   - Connecting forms to a CRM, and Zapier-style automations.
   - What AI assistants visiting your site means for you.
   - Where AI goes wrong: hallucinated answers, and data and privacy under UK GDPR.
   Name real tools only when a fetched source confirms the feature. Practical, not hype. Use `flow` and `compare` slides.
6. **Hosting (Lee, 8 Nov 2026).** Topics:
   - What hosting actually is.
   - Shared vs managed vs VPS in plain words.
   - Uptime, backups, SSL certificates and speed.
   - What happens when hosting lapses.
   - UK and EU data location, and email deliverability.
   - Why cheap hosting costs more.
   Facts from host or Google/web.dev documentation.
7. **Domain names (Lee, 8 Nov 2026).** Topics:
   - Why a good domain name matters: trust, being remembered, word of mouth, and email addresses customers type in.
   - What not to do:
     - Hyphens and numbers.
     - Names that are hard to spell or say out loud.
     - Names that are too long.
     - Odd endings customers won't guess.
     - Names that clash with someone else's trademark (check the UK IPO and Companies House).
     - Letting your web designer register it in their name.
     - Forgetting renewals.
   - Choosing a name.
   - .co.uk vs .uk vs .com.
   - Registering it in the business's own name and keeping control of it.
   - Renewals, and expired domains being snapped up.
   - Business email on your own domain, not Gmail.
   - DNS basics, domain scams and fake renewal invoices.
   UK facts from Nominet.

**Angles that work for every category (Lee, 8 Nov 2026):**
- Why it matters
- What not to do (mistakes)
- How to get it right (steps)
- This vs that
- Myth vs fact
- A labelled concept example
Rotate the angle as well as the topic.

Spread these across the week: web design stays the most frequent (at least every other day). Each of the other six (CRM, websites + CRM and types of each, branding, AI and automation, hosting, domains) should appear at least once a week. Tech news posts often land in category 5. Log the category in `log.json` so the mix can be checked.

**Look and feel:** posts must look sharp and visual. Prefer mockups, comparisons, flows and big bold statements over walls of text. Max ~30 words of body copy per slide. Statistics are optional; a strong practical point beats a weak number.

## News desk: keep up with real tech news (Lee's rule, 8 Nov 2026)
Lee: "the content should be relevant and factual, monitoring real world events around technology so we keep up to date with the latest tech." We follow the tech world properly and only report what's real.

**Scan (every feed run, about 10 minutes, all searches in one go).** Look at the last 7 days, newest first:
- UK news: BBC Technology, The Register, Computer Weekly, TechRadar UK, Wired UK, Sky News tech, The Guardian technology, Startups.co.uk, Small Business UK, Prolific North (North East and North angle).
- Web, search and SEO: Google Search Central blog, Google Search Status Dashboard, Search Engine Land, Search Engine Roundtable, Search Engine Journal, web.dev and Chrome releases, WordPress news, Shopify, Wix and Squarespace news.
- Platforms UK businesses use: Meta newsroom (Instagram, Facebook, WhatsApp Business), Microsoft (365, Copilot, Clarity, Bing), Google (Workspace, Business Profile, Gemini), Apple newsroom, OpenAI, Anthropic, HubSpot, Salesforce, Zoho, Xero, Square, Stripe.
- UK rules and safety: ICO, NCSC, gov.uk (DSIT), Ofcom, CMA, HMRC (Making Tax Digital).
Also read `newsdesk.json` so nothing is reported twice. Follow up developing stories, e.g. when a US-only feature reaches the UK.

**Relevance test.** All three must be yes:
1. It really happened. It was announced, launched, published or ruled on. Not a rumour, leak, "reportedly", "could", patent, analyst prediction or single-source scoop.
2. It affects how a UK business gets found, wins customers, runs its website or CRM, or keeps customer data safe. Examples:
   - Google Search and AI Overviews changes, and Google Business Profile.
   - AI assistants that now browse, book or recommend.
   - Website platforms (WordPress, Shopify, Wix).
   - Browser changes.
   - Instagram, Facebook and WhatsApp Business features.
   - Big outages, breaches and scams hitting UK firms, with NCSC advice.
   - UK rules: cookies, accessibility, data law, Online Safety Act, MTD.
   - CRM, booking, payment and AI tools that UK businesses use.
3. We can say clearly what a business owner should do, check or know because of it.

These don't qualify: gadgets and phone launches, games, funding rounds, share prices, celebrity tech, US politics, and anything only big companies care about.

**Two sources, one primary.** Every news fact needs:
- The primary source: the company's own announcement, help page or changelog, the regulator's notice, or gov.uk.
- At least one independent reputable outlet confirming it.
Before writing, fetch and read both in full (not just search snippets). Then check three things:
- The publish date, so you're not reporting an old story recycled with a new date. Search results often mix years, so check the year.
- What's live versus "coming soon".
- Whether it's available in the UK. Never say "now in the UK" unless the source says so.

**Record it.** Add every candidate to `newsdesk.json` with its status:
- `verified-unused`, `used` (with the post id) or `rejected` (with the reason).
- Its facts, each with a source URL, and any caveats.
Keep 60 days of items.

**Cadence.**
- Aim for one news post a day when a story passes. It takes whichever feed slot comes next: a Reel if it's a Reel slot, otherwise a carousel.
- At most two news posts a day, and the second only for a genuinely big story.
- **Fridays at 8:33am:** "This week in tech" carousel, made only if at least 3 verified stories from that week pass the relevance test. Use one slide per story, with one line on what happened and one on what it means for you. Otherwise do a normal post.
- News posts still follow every brand, design and "sound like a person" rule. Kicker for news: `NEWS` or the date.

## Facts and fact-checking (non-negotiable, Lee's rule 8 Nov 2026)
Lee: "I don't want to post rubbish." One wrong fact damages a web agency's credibility more than missing a day. When in doubt, cut it.
- **Every factual claim** (slides and caption, including tips presented as fact) goes in `posts/<id>/sources.md`. For each claim, record the exact claim, the URL it came from, a short excerpt or the number as the source states it, the source's publish date, and the date you checked it.
- **Numbers:**
  - Use the exact figure from the source. Only round in a way that keeps the meaning, and keep the units.
  - Say whose data it is ("Microsoft's own figures") and whether it's UK or global.
  - The source must be from the last 24 months, or 7 days for news.
- **Advice and best practice** must match an authoritative source. Examples: Google Search Central, web.dev, WCAG/W3C, gov.uk accessibility, ICO for cookies and data, NCSC for security, Nielsen Norman Group for usability. No legal advice: point people to the ICO or a professional.
- **Never** invent statistics, quotes, clients, testimonials, results or product features, or "studies show" claims. Never describe something as live when it's in beta or "rolling out".
- **Independent check before publishing.** Once the post is rendered, give a fresh subagent (Agent tool, general-purpose) only three things: the slide text, the caption and `sources.md`. Not your reasoning.
  - Ask it to open every source URL and confirm three things for each claim:
    - The claim says what the source says, with nothing overstated.
    - The date and UK availability are right.
    - The source is still live.
  - Ask it to reply PASS, or a list of problems.
  - Fix every problem and check again.
  - If a claim can't be verified, remove it.
  - If the post can't pass after two rounds, scrap it and publish an evergreen post with no claims that need checking.
- Stories also follow these rules. For stories, a self-check against `sources.md` is enough, with no subagent.

## Quality bar (every post, before it's published)
Make each post the way an award-winning studio would. Before publishing, score it honestly from 1 to 5 on each of these:
- **Relevant:** a UK business owner would care about it this week.
- **True:** the fact-check passed.
- **Useful:** there's one clear takeaway they can act on.
- **Specific:** it's concrete, not generic. "Compress your homepage hero image to under 200KB" is specific; "Make your site faster" isn't.
- **Hook:** the first slide or the first 2 seconds of a Reel stops the scroll. Write 3 hook options and pick the best.
- **Design:**
  - One focal point per slide and a clear hierarchy.
  - Readable on a phone.
  - On-brand, and different from the last post.
Anything under 4 gets reworked. Never publish something just to fill a slot if it's weak. Rework it, or switch to a stronger evergreen idea.

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

## What the big players do, and what we copy (research 8 Nov 2026)
Lee asked us to post like the big web design and CRM companies (HubSpot, Salesforce, Webflow, Shopify, Pipedrive, top design studios). Their pattern:
- **Format jobs:** Reels for reach (shown to non-followers), carousels for saves and engagement, Stories for daily connection. UK B2B service accounts do best with roughly **45–50% Reels, 35–40% carousels, 10–15% single images**, plus Stories most days.
- **Content mix (roughly 70/20/10):** 60% educational (tips, mistakes to avoid, how-tos, myth vs fact, checklists, step-by-step breakdowns), 15% proof/inspiration (before/after redesigns, design breakdowns, process), 15% entertaining/relatable (small-business website moments everyone recognises, this-or-that, hot takes), 10% promotional (what Nexulabs builds, how a project works, CTA).
- **Hooks:** the first slide or first 2 seconds of a Reel must stop the scroll: a bold claim, a number, a mistake, a question. On-screen text on every Reel (most people watch on mute).
- **Before/after:** the most-used format in web design. We have no client work to show yet, so use **clearly labelled concept redesigns** of fictional UK businesses ("Concept: how we'd redesign a café homepage"). Never present a concept as a real client.
- **Searchable, saveable:** write captions with the words people search (web design, business website, CRM, Sunderland/Newcastle/North East) and give people a reason to save or send.

## Feed schedule: three a day (Lee's rule, 6 Nov 2026; formats updated 8 Nov)
- **8:33am:** carousel (educational: tips, checklist, breakdown, myth vs fact).
- **2:33pm:** **Reel** (`reel.py`): a hook, 3–5 quick scenes, ending on a payoff or CTA. 12–25 seconds.
- **7:33pm:** **Reel on Mon, Wed, Fri, Sun**; on Tue, Thu, Sat a single image or short carousel (relatable, hot take, branding, before/after concept).

- Each run makes one post. Name the folder `posts/YYYY-MM-DD-HHMM-<slug>` (time of the run) so same-day posts don't clash.
- Each post must differ from the **previous post** (not just yesterday's) in category, style and cover theme. Over a day, cover three different categories from the seven in "What to post".
- News: see "News desk" cadence (aim for one a day when a verified story passes, max two), never the same story twice.
- No topic, headline or stat repeated within 30 days (that's about 90 posts, so keep ideas fresh).

## Design direction: real product screens, no AI look (Lee, 8 Nov 2026)
Lee: the posts were "looking very AI generated". He chose **direction B, real product screens**, from three samples (`design-samples/compare.jpg`). This replaces the colourful gradient styles from 6 Nov.

**Never use (they read as AI-generated):**
- The gradient styles `aurora`, `neon`, `spectrum` and `glass`.
- Mesh gradients, glowing orbs, rings, haze, frosted-glass panels and gradient-filled text.
- Background patterns (contours, waves, dots, plus and the rest), grain and grid overlays.
- Purple-to-pink colour blends.

`render.py` still has the old styles so older posts can be re-rendered. Don't use them for new posts.

**Use `"style": "product"` for every new post, Story, Reel and LinkedIn image:**
- **Flat colour backgrounds only.** Themes: `blue` (#3B2BFF), `ink`, `paper` and `lilac` (#E9E7FF). Colour comes from these flat fields and the UI itself, never from gradients.
- **Show the thing we build.** The hero of most posts (the cover, or the single LinkedIn image) is a believable product screen, using the `screen` slide type:
  - `table`: a CRM list, e.g. open quotes, enquiries or bookings, with status pills.
  - `board`: a pipeline, from new to quoted to booked to done.
  - `record`: a single enquiry or job, with an activity timeline.
  - `phone`: a mobile website, with notes alongside.
  - The existing `browser` slide gives a desktop website mockup.
- **Mockups must be honest.** Use made-up UK businesses, people and jobs only. Use round, plausible prices, and fake phone numbers such as 0191 000 0000. The screen always carries a small caption such as "Example screen" or "Concept for a made-up business". Never show a real company, client, review count or result.
- **Typography does the rest:** Geist, a big tight headline, plain-sentence labels (not uppercase mono kickers), one short sub-line, and lots of space. The accent colour goes on one word at most, and often none.
- **Inside carousels:** after the screen cover, use the plain types (`list`, `compare`, `flow`, `stat`, `quote`, `cta`) in the product style. They render flat, with no glow, grain or pattern.

**Variety without decoration.** Each post differs from the previous one in:
- Background theme (blue, ink, paper, lilac).
- Screen kind (table, board, record, phone, browser).
- Layout: screen with headline, screen with notes, or a text-only stat or quote.

Log `style`, `theme` and `screen` in `log.json` / `linkedin-log.json`. Don't repeat the same theme and screen kind two posts running.
- Colour stays in the brand family: ink, paper, blue, lilac, plus the pill colours in the UI (blue, green, grey). No orange.
- **Photos are a firm rule, not optional (Lee, 8 Nov 2026: "I haven't seen a post using an image yet").** Before building any feed post, check the last two feed posts in `log.json`. If neither used a library photo, **this post must use one**: a `photo` cover slide for a carousel or single image, or a photo scene in a Reel. That makes it at least one feed post in three. Pick the photo that best suits the topic from `python3 photo.py list`. If genuinely none fits, use the closest workspace, shopfront or desk photo rather than skipping. Prepare it with `photo.py prepare`, credit it on the slide and in the caption, and `retire` it after publishing. Log `"photo": "<file>"`.
- Photo slides in the product style come in three looks:
  - The default dark fade at the bottom.
  - `"shade": "blue"`, which adds a flat brand-blue band.
  - `"shade": "band"`, which adds a flat ink band.
  Headline text sits in the bottom area. Stories can use photos too.
- Readability check: phone-size text in the mockups must still be legible. If it isn't, cut rows or cards rather than shrinking the type.

## Reels (Lee's request, 8 Nov 2026)
- Build `posts/<id>/reel.json` and run `python3 reel.py posts/<id>/reel.json`, which gives `reel.mp4`, `cover.jpg` and `.reel-sheet.jpg`. Every slide type works as a scene; set `dur` per scene (2.5–4s). It takes 3–5 minutes to render.
- Scene 1 is the hook: big text, under 10 words. Then 2–5 scenes that each make one point. The last scene is a payoff or CTA. On-screen text must be large and readable without sound.
- Same design rules as posts: `"style": "product"`, flat themes, product screens; never the same theme and screen kind as the previous post. Photo scenes from the library are allowed (the no-reuse rule still applies).
- Look at `.reel-sheet.jpg` before publishing. Fix anything cramped, clipped or hard to read.
- The video has a silent audio track (trending audio can't be added through the API).
- Publish: Instagram via Zapier `publish_video` (tool `instagram_for_business_publish_video`, `video` = raw URL of reel.mp4, `caption`, `instagramPageId` 17841471856846758). Facebook via `page_video` (tool `facebook_pages_create_page_video`, `page` 1484176674771345, `source` = raw URL, `description` = caption).

## Stories (Lee's request, 8 Nov 2026)
- Twice a day at 11:47am and 5:47pm, made by the separate "Nexulabs stories" scheduled task. Instagram only (the Facebook connection can't post stories).
- **3–4 frames per Story run** (Lee, 8 Nov 2026, following the guidance: Dash Social's 2026 data found Stories do best at 30+ frames a week, about 4 a day; two runs of 3–4 frames gives roughly 6–8 a day). Build each run as a short sequence: frame 1 hooks, frames 2–3 make the point, the last frame lands it (answer, takeaway, or "see our latest post"). Made with `render.py` and `"format": "story"` (1080×1920). Every frame must earn its place: no filler frames to hit the count. Keep it casual and quick: a one-line tip, this-or-that, a myth vs fact, a "did you know" with a UK source, a peek at how we design (palette, wireframe, before/after concept), or a "new post" teaser for that day's feed post (say "see our latest post"; link stickers can't be added via the API).
- Same brand, variety and "sound like a person" rules. Keep the top 250px and bottom 300px clear of important text.
- Publish each frame in order: POST `https://graph.facebook.com/v21.0/17841471856846758/media` with `media_type=STORIES` and `image_url=<raw URL>` (Zapier Instagram "Make API Mutating Request", querystring), wait until the container's `status_code` is FINISHED, then POST `.../17841471856846758/media_publish` with `creation_id=<id>`.
- Log stories in `stories-log.json` (date, slot, theme, frames, media ids).

## Photos from the library (Lee's rules, 8 Nov 2026)
Claude curates free Unsplash photos for Lee (interactively, through Lee's browser) into `photos/`, named `<photographer>--<description>.<unsplash-id>.jpg`. Unsplash Licence: free commercial use, editing allowed. Never Unsplash+ (paid) photos. Do **not** use the Unsplash API or any other image source.
- **A photo is never used twice (Lee's rule).** `photo.py` enforces it: `prepare` refuses any photo whose id is in `photos/used-ids.txt`, `photos/used/` or `log.json`. Always `retire` a photo straight after publishing. Never edit `used-ids.txt` except through `retire`.
- Use a photo **roughly one post in three**, usually as the cover (`photo` slide type), with our type and logo over it. The rest stay as designed graphics.
- `python3 photo.py list` shows unused photos. Look at the photo before choosing it and only use one that genuinely suits the topic. If none fits or the folder is empty, make a designed post instead. Never let it stop a post going out.
- `python3 photo.py prepare photos/<file> posts/<id>/photo.jpg [--focus x,y]` crops to 4:5 and gives the credit line. Put it in the slide's `credit` field and as the last line of the caption.
- `shade`: default (dark fade at the bottom), `full` (overall darken) or `blue` (brand blue fade). Check the text is easy to read at phone size.
- If fewer than 5 unused photos are left, say so in the summary ("photo library running low") so Lee can ask Claude to top it up.

## Accuracy rules (see also "Facts and fact-checking")
- Every number on a slide must come from a source fetched during the run. UK sources first; non-UK only when there's no UK equivalent, and say so. Prefer primary sources (gov.uk, ONS, BCC, FSB, Ofcom, Enterprise Nation, vendor research with stated methodology).
- Put the source on the slide (`source` field) and name it in the caption.
- Check `log.json` and `newsdesk.json` and don't repeat a topic, story, headline stat or source used in the last 30 days.

## Caption format
Follow "Sound like a person" above. Roughly: an opening line that isn't a cliché, a couple of short paragraphs with the actual point, a light mention of what Nexulabs does (not every time), then 3–5 hashtags. Keep it under 120 words.

## Slide spec (post.json)
See `render.py` docstring. Post-level `"style": "product"`. **`screen`** (the default hero): `title`, optional `sub`/`kicker`/`caption` (defaults to "Example screen"), and `screen` = `{kind: table, title, tabs, columns, col_class (mono/dim), rows, pills {label: blue|solid|green|grey|ink}, highlight [row idx]}` or `{kind: board, title, tabs, pills, lanes: [{name, cards: [[title, sub, pill, highlight?]]}]}` or `{kind: record, title, tabs, pills, fields: [[label, value]], timeline_title, timeline: [[time, text]], highlight}` or `{kind: phone, brand, headline, lede, button, button2, items: [[label, price]]}` with slide-level `notes: [[title, text]]`. Working example: `design-samples/test/post.json`. Other types: cover, stat, bars, hbars, list, quote, cta, compare (instead/try), browser (website mockup with numbered pins), palette (colour swatches), flow (numbered steps). `*word*` = accent. `\n` = line break. Optional: `size` for headline/number size, `glow`, `glow_low`, `highlight`, `unit`, `max`.

## Quality check before publishing
- Render, then build a contact sheet and look at every slide: no text overflow, clipping, orphaned single words, overlapping elements, or awkward line breaks; numbers match the sources; the accent is used sparingly.
- Fix and re-render until every slide is clean.

## Daily routine (what the scheduled run does)
0. **Check `queue.json` first.** If it lists any posts, publish the first one exactly as it is (its images and caption are already in `posts/<id>/`), log it, remove it from `queue.json`, commit and push, and stop there. Don't create a new post that day.
1. Read this file, `log.json` and `newsdesk.json`. Run the news desk scan and update `newsdesk.json`. Use a verified, unused, relevant story if there is one (respecting the news cadence); otherwise pick from the rotation. Nothing used in the last 30 days.
2. Research: fetch and read the primary source for every fact you'll use. Write `posts/<id>/sources.md` as you go.
3. Create `posts/<id>/post.json` (or `reel.json`) and `caption.txt`. Render.
4. Build a contact sheet, look at every slide, fix and re-render until clean. Then run the independent fact-check subagent and the quality bar scorecard. Fix until it passes. In the log entry, mark the story as `used` in `newsdesk.json` and record `fact_check: "pass"`.
5. Commit and push to `main`. Confirm each image URL loads: `https://raw.githubusercontent.com/wheatus2/nexulabs-social/main/posts/<id>/slide-NN.jpg`.
6. Publish to Instagram via Zapier MCP: app Instagram for Business, action `publish_media_v2` (tool `instagram_for_business_publish_photo_s`), `instagramPageId` = `17841471856846758` (Nexulabs), `media` = list of the raw URLs in order, `caption` = caption.txt.
6b. Also publish to the Nexulabs Facebook Page via Zapier MCP: app Facebook Pages, action `page_stream` (tool `facebook_pages_create_page_post`), `page` = `1484176674771345` (the Nexulabs Page; confirm with inspect_zapier_actions if it ever fails), `source` = the same raw image URLs in order (up to 10), `message` = caption.txt. If Facebook Pages has no connection yet, skip this step and mention it in the summary. A Facebook failure must not stop or undo the Instagram post.
7. Fetch the permalink via the Make API GET Request action (`https://graph.facebook.com/v21.0/<media_id>?fields=permalink`), append an entry to `log.json` (include `style`, `cover_theme` and `facebook_post_id` if posted), commit and push.
8. If publishing fails: retry once after 2 minutes. If it's an auth/token error, tell Lee to reconnect Instagram at https://mcp.zapier.com/api/v1/connect-auth/InstagramBusinessCLIAPI?accountId=8724593.

## Publishing via GitHub Actions (Lee, 8 Nov 2026)
Workflow `.github/workflows/publish.yml` runs `publish.py`, which posts straight to Meta's Graph API with the `META_PAGE_TOKEN` repository secret (setup: `SETUP-META.md`). No Zapier tasks are used. The cloud session itself can't reach graph.facebook.com, so always go through the workflow.
1. Commit and push the post folder first (pull --rebase), and confirm the raw.githubusercontent.com URLs load.
2. Start the workflow with the GitHub MCP tool `actions_run_trigger`: method `run_workflow`, owner `wheatus2`, repo `nexulabs-social`, workflow_id `publish.yml`, ref `main`, inputs:
   - Feed post or Reel: `{"mode": "post", "folder": "posts/<id>"}` (posts to Instagram and the Facebook Page; `platforms` can narrow it).
   - Story: `{"mode": "story", "folder": "posts/stories/<id>"}` (Instagram only, frames in order).
   - Token test: `{"mode": "check"}`.
3. Find the run: `actions_list` → `list_workflow_runs` for `publish.yml` (event `workflow_dispatch`), the newest one created after you started it. Poll `actions_get` → `get_workflow_run` about every 30–60 seconds until `status` is `completed` (Reels take a few minutes).
4. `git pull --rebase`, then read `posts/<id>/published.json`: `instagram.media_id`, `instagram.permalink`, `facebook.id` (Stories: `instagram.media_ids`), or the `error` for each platform. Log from that file. It never double-posts: anything already marked `"ok": true` is skipped unless `force` is set.
5. **If it fails:**
   - `META_PAGE_TOKEN secret is not set`, or a check/token error (OAuthException, code 190): fall back to the old Zapier steps for this run, and tell Lee to follow `SETUP-META.md`.
   - Instagram failed for another reason: retry the workflow once after 2 minutes; if it fails again, stop and report the error from `published.json`.
   - Facebook failed but Instagram worked: carry on and mention it in the summary.
   - If Zapier is also out of tasks, leave the post committed, log it as not published, and notify Lee with the fix (`SETUP-META.md`, or top up Zapier at https://zapier.com/app/settings/billing).

## LinkedIn company page (Lee, 8 Nov 2026)
- **Always post as Nexulabs, never as Lee Wheatley (Lee, 8 Nov 2026).** The only allowed LinkedIn action is `create_company_update` with `company_id` = `146939776` (Nexulabs). Lee's personal profile is never used: the personal "share" and raw API actions have been removed from Zapier on purpose; never re-enable them. Never name Lee in LinkedIn posts.
- Page: linkedin.com/company/nexulabs (organisation ID 146939776). Posted by the "Nexulabs LinkedIn" scheduled task, Tue/Wed/Thu mornings. 3 posts a week maximum.
- Audience: business owners and managers deciding who to hire. Tone: same plain UK voice, slightly more businesslike than Instagram, no emoji. Never "small business(es)".
- What to post: pick the strongest recent Instagram/Facebook post (from `log.json`, last 7 days, not yet used on LinkedIn), or a verified news item from `newsdesk.json`, and make a LinkedIn version:
  - One image, 1080×1350, made with `render.py` as a single-slide post in `posts/linkedin/<YYYY-MM-DD>-<slug>/` that sums up the idea on its own (headline + 2–4 short points, or a stat with its source). Same brand and design rules: `"style": "product"`, usually a `screen` slide with the headline, the screen and a short sub-line.
  - Caption 80–200 words: a first line that earns the "see more" click, the practical point, what to do, one light line about Nexulabs at most, then 3 hashtags at most (e.g. #webdesign #crm #northeastbusiness). Fact rules and `sources.md` apply exactly as for feed posts, including the independent fact-check.
  - LinkedIn's API treats some characters as formatting: escape parentheses as `\(` `\)` and avoid `@`, `[`, `]`, `{`, `}`, `<`, `>`, `#` except in the hashtags at the end.
- Publish: Zapier LinkedIn `create_company_update` (tool `linkedin_create_company_update`), `company_id` = the Nexulabs page (resolve with inspect_zapier_actions if needed), `comment` = caption, `image_type` = `post_media`, `image` = raw URL of the image. If it fails with "Could not find entity", the Zapier connection is the problem: run `list_zapier_connections` for LinkedIn and pass the connection's numeric id (from `enable_zapier_action`'s `connection_id`, e.g. 67232197 for "Lee Wheatley #2", reconnected 8 Nov 2026) as `connection_id`. Log to `linkedin-log.json` (date, source post id, topic, image, style, theme, screen, response id).
- If LinkedIn isn't connected in Zapier, don't fail silently: say so in the summary with the link https://mcp.zapier.com/api/v1/connect-auth/LinkedInCLIAPI?accountId=8724593.

## Comments and messages (Lee, 8 Nov 2026)
The "Nexulabs comments summary" task runs daily at about 6:20pm. It never replies on Lee's behalf. It reads new comments from the last 24 hours on Instagram (Graph API via the Zapier Instagram "Make API GET Request": `/{ig-id}/media?fields=id,caption,permalink,timestamp,comments_count`, then `/{media-id}/comments?fields=id,text,username,timestamp,replies{text,username}`) and, where the Facebook Pages app allows it, Facebook Page comments; plus LinkedIn comments if that's connected. For each new comment it drafts a short reply in Lee's voice (helpful, specific, no sales push, no emoji spam), flags anything that needs Lee personally (a sales enquiry, a complaint, spam to delete), and records what it has seen in `comments-log.json` so nothing is reported twice. If there's nothing new, the summary is one line.

## Monthly review (Lee, 8 Nov 2026)
On the 1st of each month the "Nexulabs monthly review" task pulls the last month's results and writes `reports/YYYY-MM.md`:
- Instagram account insights (reach, profile views, follower change, website taps) and per-post insights (reach, saves, shares, likes, comments; plays and average watch time for Reels), Facebook Page insights where available, LinkedIn page stats if connected.
- What worked and what didn't, by format (carousel / Reel / single / Story), category, angle, style, time slot and news vs evergreen, with the actual numbers.
- Changes: it may adjust the weighting of formats, categories, angles and styles in this playbook, and move a slot by up to an hour, when the numbers clearly support it. It must not change Lee's own rules (posting volume, topics, wording, brand, fact-checking, no-reuse) without asking him. Every change is listed in the report and committed with a clear message.
- Summary for Lee: three findings, the changes made, and one question if a bigger decision is needed.

## TikTok (Lee, 8 Nov 2026)
TikTok has no posting connection we can use, so TikTok is set up separately once Lee has a TikTok Business account (he has to create it himself). Reels for TikTok need sound: `music.py` makes an original, royalty-free background track to put under a Reel (`python3 music.py posts/<id>/reel.mp4` → `reel-tiktok.mp4`). Never use copyrighted music.
