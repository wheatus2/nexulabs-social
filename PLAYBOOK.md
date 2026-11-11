# Nexulabs Instagram — daily posting playbook

> **DESIGN STANDARD (Lee, 11 Nov 2026): read `DESIGN.md` before making any post, Reel or Story. It overrides every design instruction in this file.**
> - Lee: the posts looked "very repetitive, very basic". The bar is what Google, Apple or Nvidia would post.
> - Every post is now designed from scratch with `studio.py` (bespoke HTML and CSS per frame). `render.py`, `reel.py`, the five looks, the slide types and the `mockup` slide type are **retired**: do not use them for new posts. Where this file says to render with them, use `studio.py` instead.
> - No repeats: layouts, colours and typefaces must differ from recent posts. `python3 studio.py check` enforces this and must pass.
> - A post that can't reach the standard does not go out. Skip the slot and report it. This replaces "switch to an evergreen post" when the problem is the design.
> - After publishing: `python3 studio.py log posts/<id>` and commit `design-log.json`. In `log.json` record `"renderer": "studio"`.


> **Mockups (Lee, 10 Nov 2026):** posts must look like a marketing agency made them. Use the `mockup` slide type (a designed website for a made-up business on a laptop and phone) as described in "Mockups: post like an agency". This applies to every scheduled run from now on.
>
> **Design update (Lee, 9 Nov 2026):** No gradient styles (Lee, 8 Nov: posts looked "very AI generated"). Everything also looked the same (Lee, 9 Nov), so posts, Reels, Stories and LinkedIn now rotate through **five looks**: `product`, `journal`, `signal`, `soft` and `press`, each with its own fonts, colours and layout. See "Design direction: five looks" for the rotation rules. Photos must literally show the post's subject; see "Photos from the library". This replaces any older instruction, including in the scheduled tasks, to use only `"style": "product"`.

> **Publishing update (Lee, 8 Nov 2026):** Zapier's task allowance ran out, so publishing moves to **GitHub Actions** (free, no task limits). See "Publishing via GitHub Actions" below. This replaces the Zapier publishing steps in the scheduled task prompts (Instagram `publish_media_v2` / `publish_video`, Facebook `page_stream` / `page_video`, Stories via "Make API Mutating Request", permalink lookups via "Make API GET Request"). Use Zapier only as the fallback described there. LinkedIn still uses Zapier.

Followed by the scheduled runs. **Three posts a day** (around 9am, 3pm and 8pm UK time) to the Nexulabs Instagram account and Facebook Page.

## Brand
- Business: Nexulabs, "Websites and CRM systems for all types of businesses" (nexulabs.co.uk; the site says "businesses of every kind"). Custom CRMs for enquiries, quotes, jobs and bookings; websites; hosting; domains/email; branding. Based in the North East of England.
- Voice: UK English. Plain, direct, practical, like Lee talking to a customer. Short sentences. Address the reader as "you". No hype, no jargon, no emoji, no exclamation marks. See "Sound like a person".
- Visuals: rendered by `render.py`. Photos only from the library in `photos/` (see "Photos from the library"). Never the Unsplash API, scraped images, logos of other companies, or other stock sites.
  - Logo: the real Nexulabs wordmark from `brand/nexulabs-logo-white.svg` (render.py recolours it per theme). Never retype the logo as text.
  - Colours (from nexulabs.co.uk): ink #0B0B0C, paper #F5F5F7, accent Pigment blue #0C23A8 on light (the website's brand blue since November 2026; it replaced Indigo #3B2BFF) / #667DFF on ink (the logo's full stop) / light blue #B3BEFF on Pigment blue slides (6.4:1; ink on Pigment blue fails contrast). Accent is for one or two words or one data point per slide, never more. No other accent colours.
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

## Design direction: five looks, real screens, no AI look (Lee, 8 and 9 Nov 2026)
Lee, 8 Nov: the posts were "looking very AI generated". Lee, 9 Nov: *"you seem to use the same layout and design for every post. Normal posts, reels, stories all look the same, can you please mix this up, even the colours."*

**Never use (they read as AI-generated):**
- The gradient styles `aurora`, `neon`, `spectrum` and `glass`.
- Mesh gradients, glowing orbs, haze, frosted glass and gradient text.
- Background patterns, grain and grid overlays.
- Purple-to-pink blends.
- Orange.

### The five looks
Post-level `"style"` picks the look. Each look is its own design system, with its own typefaces, colours, layout and photo treatment. Every slide's `"theme"` must be one of that look's themes. See `design-samples/looks.jpg`.

| Look (`style`) | Character | Themes (use 2–3 per post) | Photo treatment | Best for |
|---|---|---|---|---|
| `product` | Geist, brand blue, real UI screens | `blue`, `ink`, `paper`, `lilac` | full bleed with a flat band (`shade`: blue / band) | CRM and web screens, how we build |
| `journal` | editorial magazine: Fraunces serif, italic accent word, hairline rules, headline at the top | `cream`, `forest`, `stone` | inset photo with an italic caption underneath | guides, explainers, branding, design process |
| `signal` | loud poster: Anton condensed capitals, thick frame, highlighted word, hard-shadow screens | `lemon`, `black`, `sky` | full bleed, headline set as yellow or black blocks | myths, "what not to do", this vs that, strong opinions |
| `soft` | friendly, centred: Bricolage Grotesque, rounded cards, chunky offset shadows | `mint`, `navy`, `blush` | rounded, slightly tilted photo card | tips, checklists, quick wins, Stories |
| `press` | newspaper: Newsreader serif, double rule masthead, red kicker, italic standfirst | `newsprint`, `night`, `red` | edge-to-edge photo with a caption line | tech news, "this week in tech", data and stats |

### Rotation rules (enforced every run)
- **No back-to-back looks.**
  - A feed post never uses the same look as the previous feed post.
  - A Story never uses the same look as the previous Story.
  - The LinkedIn post never uses the same look as the previous LinkedIn post.
- **Daily spread.** Across a day's 3 feed posts and 2 Stories, use at least 4 different looks, and no look more than twice.
- **Mix the cover layout too.** Rotate between:
  - headline cover
  - photo cover
  - screen cover
  - big-number stat cover
  - quote cover
  - this-vs-that compare cover

  Never use the same cover layout two posts running.
- **Stay inside the look.** Within a post, alternate between that look's themes. Never mix another look's themes in.
- **Log it.** Add `style`, `themes` and `cover` to `log.json`, `stories-log.json` and `linkedin-log.json`. Check the last 5 entries of each before choosing.

### Content rules that apply in every look
- **Show the thing we build.** Product screens (`screen` slide: table, board, record, phone; `browser` slide) work in every look. In `signal` they get a hard shadow, in `soft` rounded corners, and in `journal` and `press` square corners.
- **Mockups must be honest.**
  - Use made-up UK businesses, people and jobs only.
  - Use round prices and fake phone numbers such as 0191 000 0000.
  - Always add a caption such as "Example screen".
  - Never show a real company, client, review count or result.
- **One accent word at most per headline, often none.**
  - In `journal` it turns italic.
  - In `signal` it becomes a highlighted block.
  - In `press` it turns red.
- **Readability.** Phone-size text must stay legible. Cut rows or words rather than shrinking type.
- **Photos follow "Photos from the library":** literal, on-point, and optional.

## Reels (Lee's request, 8 Nov 2026)
- Build `posts/<id>/reel.json` and run `python3 reel.py posts/<id>/reel.json`, which gives `reel.mp4`, `cover.jpg` and `.reel-sheet.jpg`. Every slide type works as a scene; set `dur` per scene (2.5–4s). It takes 3–5 minutes to render.
- Scene 1 is the hook: big text, under 10 words. Then 2–5 scenes that each make one point. The last scene is a payoff or CTA. On-screen text must be large and readable without sound.
- Same design rules as posts: pick one of the five looks (never the previous feed post's look), and use that look's themes for every scene. Photo scenes only when a cleared photo literally shows the subject; no reuse.
- Look at `.reel-sheet.jpg` before publishing. Fix anything cramped, clipped or hard to read.
- The video has a silent audio track (trending audio can't be added through the API).
- Publish: Instagram via Zapier `publish_video` (tool `instagram_for_business_publish_video`, `video` = raw URL of reel.mp4, `caption`, `instagramPageId` 17841471856846758). Facebook via `page_video` (tool `facebook_pages_create_page_video`, `page` 1484176674771345, `source` = raw URL, `description` = caption).

## Stories (Lee's request, 8 Nov 2026)
- Twice a day at 11:47am and 5:47pm, made by the separate "Nexulabs stories" scheduled task. Instagram only (the Facebook connection can't post stories).
- **3–4 frames per Story run** (Lee, 8 Nov 2026, following the guidance: Dash Social's 2026 data found Stories do best at 30+ frames a week, about 4 a day; two runs of 3–4 frames gives roughly 6–8 a day). Build each run as a short sequence: frame 1 hooks, frames 2–3 make the point, the last frame lands it (answer, takeaway, or "see our latest post"). Made with `render.py` and `"format": "story"` (1080×1920). Every frame must earn its place: no filler frames to hit the count. Keep it casual and quick: a one-line tip, this-or-that, a myth vs fact, a "did you know" with a UK source, a peek at how we design (palette, wireframe, before/after concept), or a "new post" teaser for that day's feed post (say "see our latest post"; link stickers can't be added via the API).
- Same brand, variety and "sound like a person" rules. Stories rotate the five looks too: never the same look as the previous Story or the feed post just before it (`soft` and `signal` suit Stories well). Keep the top 250px and bottom 300px clear of important text.
- Publish each frame in order: POST `https://graph.facebook.com/v21.0/17841471856846758/media` with `media_type=STORIES` and `image_url=<raw URL>` (Zapier Instagram "Make API Mutating Request", querystring), wait until the container's `status_code` is FINISHED, then POST `.../17841471856846758/media_publish` with `creation_id=<id>`.
- Log stories in `stories-log.json` (date, slot, style, themes, frames, media ids).

## Highlight covers (Lee, 9 Nov 2026)
Lee: *"the highlight cover doesn't fit the circle, please can you choose something circle."*
- **The covers.** `brand/highlight-covers/` holds one cover per highlight, made by `brand/highlight_covers.py`. Each is a flat ink background with a white line icon and a blue accent, matching the profile picture. The icon sits inside the centre 380px of a 1080×1920 frame, so it survives Instagram's circle crop. The highlight name sits low in the frame, outside the circle. `preview.jpg` shows them as profile circles.

  | Highlight | Cover file |
  |---|---|
  | Websites | `websites` |
  | CRM | `crm` |
  | Web + CRM | `web-crm` |
  | Branding | `branding` |
  | Domains | `domains` |
  | Hosting | `hosting` |
  | AI & automation | `ai-automation` |
  | Tech news | `tech-news` |
  | Book a call | `book-call` |

- **Why covers go out as a Story.** Instagram on the web can only pick a cover from Stories already in the highlight. So the first time a highlight is needed, its cover is published once as a one-frame Story from `posts/stories/<date>-highlight-cover-<slug>/slide-01.jpg`. The weekly Highlights run then adds that frame to the front of the highlight and picks it as the cover.
- **Never use a content frame as a cover.** Text gets cropped in the circle.
- **If "Select cover" shows no thumbnails.** On a short browser window, Instagram's web dialog collapses the thumbnail strip to 0px high. Run JavaScript in the dialog to hide the preview and give the second child of the scrolling div a height of 300px. Then click the icon frame, put the preview back, and click Done. That's how the CRM cover was set on 9 Nov 2026.
- **Phone alternative.** The `-square.jpg` versions are for uploading from a phone's camera roll ("Edit highlight" → "Edit cover").

## Opening web pages in unattended runs (10 Nov 2026)
On 9 and 10 Nov most scheduled runs could not open source pages: a permission prompt appeared and nobody was there to answer it. The news desk found nothing it could verify, sourced Stories were dropped, and the LinkedIn post was held.
- **Search first, then open.** A page opens without a prompt when its exact URL came back from a web search in the same run. Run the web search (extended mode for news), then open the URL exactly as the search returned it.
- **Never type a URL from memory, from `sources.md`, from `newsdesk.json` or from this file and open it directly.** Search for the page title or the site name plus the topic, and open the result.
- **The fact-check subagent has the same limit.** Tell it to search for each source by title and site, then open the URL its own search returned.
- **If a page still won't open after a search, try once more with a different search, then move on.** Don't wait on a prompt. Say in the summary which sources could not be opened.
- **A run where nothing can be opened still posts**, using advice that needs no outside facts, as it did on 10 Nov. It must say "web pages could not be opened" in its summary so Lee knows.

## Publishing errors are not always failures (10 Nov 2026)
Meta can publish a post and still return an error. On 10 Nov the 19:33 carousel was reported as "refused" twice and went live both times.
- `publish.py` now looks at the account before publishing and after any error. If a post with the same caption is live, it records that post and does not publish again.
- **Never re-run a failed publish by hand before checking the Instagram profile.** You should not need to: the workflow retries on its own until the post is out (see "If it fails" below), and the hourly `retry.yml` sweep picks up anything left. Only a dead token (code 190) or missing files stop it, and those need Lee.
- Facebook has its own check against the Page, and Story frames are checked against the live Stories, so retries are safe there too.
- Report "published, Meta returned an error" as published, with the permalink.

## Mockups: post like an agency (Lee, 10 Nov 2026)
Lee: *"these posts need to look way more professional"*, *"you need to be creating mockups, and making things look like a full marketing agency has posted them"*, and *"you need to create a different mockup each time, it has to look world class with all the correct colours and fonts to suit the post."*

- **Show finished-looking work.** The slide type `mockup` puts a designed website for a made-up business on a laptop, a phone, or both (`"device": "duo" | "laptop" | "phone"`). See `design-samples/mockups.jpg`.
- **How often.**
  - Every web design, branding, and websites + CRM post has at least one `mockup` slide, usually the cover.
  - At least one feed post a day opens with a mockup cover.
  - Stories use `"device": "phone"`.
  - CRM posts keep using `screen` slides (table, board, record).

### Every mockup is a new design
Never reuse a mockup. Before designing one, read the last 10 entries with a `mockup` field in `log.json` and `stories-log.json`. The new one must differ from **all** of them in business, and from the last **three** in every one of these:

| Choice | Options |
|---|---|
| Site layout (`layout`) | `split` (text left, photo right), `full` (full-bleed photo hero), `center` (centred headline over a wide photo), `booking` (headline plus a booking widget, needs no photo), `shop` (headline plus four product or menu tiles) |
| Headline font (`font`) | serif: `Fraun`, `News`, `Playfair`, `DMSerif`; sans: `Disp`, `Brico`, `Grotesk`, `Outfit`, `Syne`; condensed capitals: `Cond`, `Oswald` |
| Colours | `bg`, `ink`, `accent`, and `on_accent` (text colour on buttons) |
| Buttons (`buttons`) | `round`, `soft`, `square` |
| Device | `duo`, `laptop`, `phone` |
| Trade | a different kind of business each time |

### Colours and fonts must suit the trade and the post
Design the made-up site the way an agency would for that client, then pick the Nexulabs look and theme for the slide so the two sit well together (a light site on a dark slide, or a dark site on a light slide; never the same background colour on both).

| Trade | Fonts that suit | Colour direction |
|---|---|---|
| Barbers, tattoo studios | `DMSerif`, `Playfair`, `Oswald` | cream or charcoal with oxblood, bottle green or brass |
| Pubs, restaurants | `Playfair`, `Fraun`, `News` | dark wood tones, deep green, cream, gold buttons with dark text |
| Bakeries, cafés, gift shops | `Syne`, `Brico`, `Outfit` | blush, butter, berry, warm brown |
| Florists, salons, beauty | `Fraun`, `Outfit`, `Playfair` | soft greens, off-white, plum, sage |
| Builders, joiners, roofers | `Cond`, `Oswald`, `Grotesk` | near-black or white with a strong blue or yellow |
| Electricians, plumbers, garages | `Grotesk`, `Disp`, `Oswald` | charcoal with signal yellow, or white with a clear blue or red |
| Accountants, solicitors, clinics, dentists | `News`, `Disp`, `Outfit` | white, navy, calm teal or green |
| Gyms, coaches | `Oswald`, `Cond`, `Syne` | black with one loud colour |

- **No orange** in any made-up site either. Use oxblood, brick red or brass where a warm colour is needed.
- **Check contrast.** Button text must be easy to read on the accent colour: set `on_accent` to a dark colour on yellow, gold or pale accents.
- **Write it like a real client pitch:**
  - a believable local business name and trade (North East towns, no real companies)
  - a short, confident headline, one line of supporting copy, one clear button
  - real-sounding services or prices, and a short trust strip
  - fake phone numbers such as 0191 000 0000, and "(example)" after any rating
- **Photo inside the site.** Use a prepared library photo that literally shows that trade (`photo.py list --topic business-types`), credit it in the caption, and retire it after publishing. If none fits, use the `booking` layout, which needs no photo.
- **Keep the slide simple.** One headline, at most one supporting line, the device, and the caption "Concept for a made-up business." No lists or extra boxes on a mockup slide.
- **Look at it before publishing.** Open the rendered slide. Reject and redo it if text is clipped, a button is hidden, the phone covers the headline of the site, or it looks like a template.
- **Log it.** Add `"cover": "mockup"` and `"mockup": {"business", "trade", "layout", "font", "accent", "bg", "device"}` to the log entry.

## Photos from the library (Lee's rules, updated 9 Nov 2026)
Lee, 9 Nov 2026: *"I have no idea what this image has to do with domain names... the images you choose must be relevant to what you are posting about"* and *"we are a design company, so the images we choose have to be on point."*

- **The photo must literally show what the post is about.** Some examples:
  - a hosting post shows servers or a data centre
  - a post on booking sites for barbers shows a barbershop
  - a logo post shows logo sketches
  - a post on card payments shows a card payment

  If someone seeing only the photo and the headline would not instantly get the connection, don't use it.
- **No metaphors and no clichés, ever.** That rules out:
  - door numbers or street signs for domains
  - padlocks for security
  - robots or glowing lines for AI
  - stars for reviews
  - keys or model houses for ownership
  - handshakes, high-fives, or people smiling at phones and laptops
- **Domain names, AI and automation, and tech-news posts are designed, not photo posts.** Use the layouts in "Looks" instead.
- **The library is curated, with 71 photos as of 9 Nov 2026.** `photos/topics.json` lists, for every cleared photo:
  - what it `shows`
  - what it may be used for (`use_only_for`)
- **Only use a photo if this post's subject matches its `use_only_for`.**
  - `python3 photo.py list --topic <topic>` lists cleared photos. Topics: web-design, branding, crm, websites-crm, hosting, business-types, north-east.
  - North East landmarks only go on posts that are explicitly local.
  - Open the photo and look at it before using it.
- **Rejected photos are never used.** They are in `photos/not-engaging/`, and `photo.py` refuses them, plus anything not in `topics.json`.
- **A photo is never used twice.** `photo.py` enforces this.
  - `prepare` refuses any id in `photos/used-ids.txt`, `photos/used/` or `log.json`.
  - `retire` the photo straight after publishing.
- **Photos are optional.** Use one only when it fits the post as well as a designed slide would. Most posts will be designed. Never let a missing photo stop a post going out.
- **Preparing and crediting:**
  - `python3 photo.py prepare photos/<file> posts/<id>/photo.jpg [--focus x,y]` crops to 4:5 and gives the credit line.
  - Put the credit in the slide's `credit` field and as the last line of the caption.
  - How the photo sits on the slide depends on the post's look (see "Looks").
- **Topping up the library.** Only Claude in a chat with Lee adds photos, to the same standard:
  - editorial-quality light and composition
  - real places and people working, not posed stock
  - no other companies' logos
  - no AI images

## Accuracy rules (see also "Facts and fact-checking")
- Every number on a slide must come from a source fetched during the run. UK sources first; non-UK only when there's no UK equivalent, and say so. Prefer primary sources (gov.uk, ONS, BCC, FSB, Ofcom, Enterprise Nation, vendor research with stated methodology).
- Put the source on the slide (`source` field) and name it in the caption.
- Check `log.json` and `newsdesk.json` and don't repeat a topic, story, headline stat or source used in the last 30 days.

## Caption format
Follow "Sound like a person" above. Roughly: an opening line that isn't a cliché, a couple of short paragraphs with the actual point, a light mention of what Nexulabs does (not every time), then 3–5 hashtags. Keep it under 120 words.

## Slide spec (post.json)
See `render.py` docstring. Post-level `"style"` = one of the five looks, and slide `theme`s from that look. **`screen`** (the default hero): `title`, optional `sub`/`kicker`/`caption` (defaults to "Example screen"), and `screen` = `{kind: table, title, tabs, columns, col_class (mono/dim), rows, pills {label: blue|solid|green|grey|ink}, highlight [row idx]}` or `{kind: board, title, tabs, pills, lanes: [{name, cards: [[title, sub, pill, highlight?]]}]}` or `{kind: record, title, tabs, pills, fields: [[label, value]], timeline_title, timeline: [[time, text]], highlight}` or `{kind: phone, brand, headline, lede, button, button2, items: [[label, price]]}` with slide-level `notes: [[title, text]]`. Or `{kind: shot, image: "shots/x.jpg", crop, bar, bar_bg}`: a **real screenshot** of our own website or app (never a client's live data) in a full-size, realistic phone (metal edge, side buttons, Dynamic Island, status bar, home bar) on the right of the slide, with the title, `notes` and caption in a column beside it (Lee asked for a bigger phone that looks like a phone, 9 Nov 2026). `crop` cuts that many CSS px off the top of the 390px page (to lose half-cut text above a floating nav); `bar: "light"` gives a white status bar for a light screen, `bar_bg` its colour. Keep titles short: the column is narrow, so break them by hand with `\n`. Take shots at 390px wide and 3x with a made-up booking or record, and set the slide's `caption` to say it's a real screen with made-up details. Working example: `design-samples/test/post.json`. Other types: cover, stat, bars, hbars, list, quote, cta, compare (instead/try), browser (website mockup with numbered pins), palette (colour swatches), flow (numbered steps). `*word*` = accent. `\n` = line break. Optional: `size` for headline/number size, `glow`, `glow_low`, `highlight`, `unit`, `max`.

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
   - Instagram failed for another reason: **it keeps trying on its own (Lee, 10 Nov 2026: "try again until it posts").** The run retries after 1, 2, 5 and 10 minutes, then every 15 minutes for up to 5 hours, checking the account before each try so nothing posts twice. After that, `.github/workflows/retry.yml` tries again every hour for two days. So a run can take a long time: keep polling for up to 20 minutes, and if it is still going, log the post as `"status": "retrying"`, tell Lee it is still being retried, and stop. Do not start a second run for the same folder and do not use `force`. The next scheduled run reads `published.json` for any `retrying` entry and fills in the log.
   - Facebook failed but Instagram worked: carry on and mention it in the summary. It is retried the same way.
   - If Zapier is also out of tasks, leave the post committed, log it as not published, and notify Lee with the fix (`SETUP-META.md`, or top up Zapier at https://zapier.com/app/settings/billing).

## LinkedIn company page (Lee, 8 Nov 2026)
- **Always post as Nexulabs, never as Lee Wheatley (Lee, 8 Nov 2026).** The only allowed LinkedIn action is `create_company_update` with `company_id` = `146939776` (Nexulabs). Lee's personal profile is never used: the personal "share" and raw API actions have been removed from Zapier on purpose; never re-enable them. Never name Lee in LinkedIn posts.
- Page: linkedin.com/company/nexulabs (organisation ID 146939776). Posted by the "Nexulabs LinkedIn" scheduled task, Tue/Wed/Thu mornings. 3 posts a week maximum.
- Audience: business owners and managers deciding who to hire. Tone: same plain UK voice, slightly more businesslike than Instagram, no emoji. Never "small business(es)".
- What to post: pick the strongest recent Instagram/Facebook post (from `log.json`, last 7 days, not yet used on LinkedIn), or a verified news item from `newsdesk.json`, and make a LinkedIn version:
  - One image, 1080×1350, made with `render.py` as a single-slide post in `posts/linkedin/<YYYY-MM-DD>-<slug>/` that sums up the idea on its own (headline + 2–4 short points, or a stat with its source). Same brand and design rules: rotate the five looks (never the same as the previous LinkedIn post), often a `screen` slide with the headline, the screen and a short sub-line.
  - Caption 80–200 words: a first line that earns the "see more" click, the practical point, what to do, one light line about Nexulabs at most, then 3 hashtags at most (e.g. #webdesign #crm #northeastbusiness). Fact rules and `sources.md` apply exactly as for feed posts, including the independent fact-check.
  - LinkedIn's API treats some characters as formatting: escape parentheses as `\(` `\)` and avoid `@`, `[`, `]`, `{`, `}`, `<`, `>`, `#` except in the hashtags at the end.
- Publish: Zapier LinkedIn `create_company_update` (tool `linkedin_create_company_update`), `company_id` = the Nexulabs page (resolve with inspect_zapier_actions if needed), `comment` = caption, `image_type` = `post_media`, `image` = raw URL of the image. If it fails with "Could not find entity", the Zapier connection is the problem: run `list_zapier_connections` for LinkedIn and pass the connection's numeric id (from `enable_zapier_action`'s `connection_id`, e.g. 67232197 for "Lee Wheatley #2", reconnected 8 Nov 2026) as `connection_id`. Log to `linkedin-log.json` (date, source post id, topic, image, style, theme, screen, response id).
- If LinkedIn isn't connected in Zapier, don't fail silently: say so in the summary with the link https://mcp.zapier.com/api/v1/connect-auth/LinkedInCLIAPI?accountId=8724593.

## Comments and messages (Lee, 8 Nov 2026)
The "Nexulabs comments summary" task runs daily at about 6:20pm. It never replies on Lee's behalf. It reads comments through GitHub Actions, not Zapier (Lee, 9 Nov 2026): it starts `publish.yml` with `mode: comments`, which runs `publish.py comments` (read-only, Meta Graph API with the `META_PAGE_TOKEN` secret) and prints recent Instagram and Facebook Page comments as JSON between `===COMMENTS-JSON===` markers in the run log. LinkedIn comments aren't readable yet and are skipped. For each new comment it drafts a short reply in Lee's voice (helpful, specific, no sales push, no emoji spam), flags anything that needs Lee personally (a sales enquiry, a complaint, spam to delete), and records what it has seen in `comments-log.json` so nothing is reported twice. If there's nothing new, the summary is one line.

## Monthly review (Lee, 8 Nov 2026)
On the 1st of each month the "Nexulabs monthly review" task pulls the last month's results and writes `reports/YYYY-MM.md`:
- Numbers come from GitHub Actions, not Zapier (Lee, 9 Nov 2026): run `publish.yml` with `mode: insights` (optional `month: YYYY-MM`). It runs `publish.py insights` (read-only) and commits `reports/data/YYYY-MM-insights.json` with the Instagram account totals, every post's insights (plus like and comment counts) and Facebook Page stats, and an `errors` block for anything Meta refused. Reach/views/saves/shares need the token permissions `instagram_manage_insights` and `read_insights` (SETUP-META.md step 2).
- Instagram account insights (reach, profile views, follower change, website taps) and per-post insights (reach, saves, shares, likes, comments; plays and average watch time for Reels), Facebook Page insights where available, LinkedIn page stats if connected.
- What worked and what didn't, by format (carousel / Reel / single / Story), category, angle, style, time slot and news vs evergreen, with the actual numbers.
- Changes: it may adjust the weighting of formats, categories, angles and styles in this playbook, and move a slot by up to an hour, when the numbers clearly support it. It must not change Lee's own rules (posting volume, topics, wording, brand, fact-checking, no-reuse) without asking him. Every change is listed in the report and committed with a clear message.
- Summary for Lee: three findings, the changes made, and one question if a bigger decision is needed.

## TikTok (Lee, 8 Nov 2026)
TikTok has no posting connection we can use, so TikTok is set up separately once Lee has a TikTok Business account (he has to create it himself). Reels for TikTok need sound: `music.py` makes an original, royalty-free background track to put under a Reel (`python3 music.py posts/<id>/reel.mp4` → `reel-tiktok.mp4`). Never use copyrighted music.
