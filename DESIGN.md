# Nexulabs design standard

**Read this before designing anything. It replaces the slide templates, the "five looks" and the mockup slide type.**

Lee, 11 Nov 2026: the posts were "very repetitive, very basic", and "look like something my 7 year old has put together". The standard he set: **"if Google, Apple or Nvidia were posting content to Instagram, what would that look like? This is the standard you need to be at."** And: "do not repeat designs", layouts or colours.

He was right. Every post had the same skeleton: logo top left, label top right, a headline, a list of small text, and a lot of empty flat colour. Changing the font and colour did not hide it.

**If a post can't reach this standard, it does not go out.** Skip the slot and say so in the summary. An empty slot is better than a weak post.

## How posts are made now

Every post is designed from scratch, as its own HTML and CSS, with `studio.py`. There are no templates.

1. `python3 studio.py recent` — see what the last posts used. Yours must be different.
2. Write the idea in one line (the `concept`). What is the one picture this post is?
3. Design each frame in `posts/<id>/art/slide-01.html`, `slide-02.html`… (a Reel is one `art/reel.html`).
4. Write `posts/<id>/design.json` (format, one composition name per frame, background colours, display font, accent, concept).
5. `python3 studio.py render posts/<id>` (or `reel`), then **open `.sheet.jpg` and every slide and look at them.**
6. Critique against the checklist below. Fix. Render again. Expect at least two rounds.
7. `python3 studio.py check posts/<id>` must pass. It fails on small text, clipped text, text outside the safe area, too many words, and repeats of recent posts.
8. **Second opinion.** Give a fresh subagent only the rendered images and this question: "Would Apple, Google or Nvidia post this? Score 1 to 10 for craft, and name the weakest frame and why." Under 8, or any frame called basic, generic or template-like: redesign that frame. Two failed rounds: don't post.
9. Publish as before (`publish.yml`), then `python3 studio.py log posts/<id>` and commit `design-log.json`.

`render.py`, `reel.py`, the looks and the `mockup` slide type are retired. Do not use them for new posts.

## What that standard actually looks like

Look at how those three post:

- **One idea per frame.** A frame says one thing. If it needs a list, it's two frames, or it belongs in the caption.
- **A hero.** Every frame has one thing the eye lands on first, and it is big: a product screen, a huge word, a number, an object. Not a headline plus supporting bullets.
- **Scale.** Their type is either very large or very small, rarely in between. Headlines run 110 to 260px on a 1080 frame, tight (line-height .84 to .95, letter-spacing -.03 to -.06em). Supporting text is 28 to 40px and there is little of it.
- **The frame is full.** Elements run to the edges and off them. Big empty areas only when the emptiness is the point.
- **Product, shown beautifully.** Interfaces are designed properly, lit, tilted in 3D, cropped, layered, with real shadows. Never a small flat screenshot in the middle.
- **Restraint with colour.** One background, one accent, neutrals. The accent appears in few places and means something.
- **Few words.** Feed frame 40 words at most, usually under 20. Story 32. Reel scene 22.
- **Craft.** Optical alignment, consistent radii, shadows that share one light direction, nothing nearly touching, nothing nearly aligned.

## Never again

- The old skeleton: logo top left + label top right + headline + small-text list. A logo is not needed on every frame; the last frame and sometimes the first is enough.
- Numbered lists of small text, comparison boxes, "myth / fact" cards, "01 02 03" rows.
- A frame that is mostly flat colour with text in one corner.
- The same composition twice in one post, or one used in the last 12 posts.
- The same opening background as any of the last 5 posts, or the same display typeface or accent as any of the last 3.
- Multi-colour gradient washes and blobs (they look AI-made). A single-hue glow as lighting behind an object is fine.
- Orange. Stock-photo clichés. Emoji as design. Clip-art icons.
- Text under 26px on a feed frame (interfaces inside a mockup are exempt: mark them `data-ui`).

## Building blocks (not templates)

Compositions to start from. Name yours in `design.json`; inventing new ones is better than reusing these.

- Giant type cropped by the frame edge, one word in the accent
- Interface tilted in 3D (CSS `perspective` + `rotateX/rotateZ`), bleeding off two edges, one element lit
- A single huge numeral or word filling the frame, with one line of meaning
- Words stacked and fading, the last one in a contrasting typeface
- Phone straight on, cropped at the bottom, with one floating card beside it on a strong colour field
- Exploded view: an interface pulled apart into floating layers
- Before and after as one object split down the middle (not two boxes)
- A diagram drawn precisely in SVG: orbits, flows, a grid, a timeline as one line
- A single component at enormous scale (one button, one form field, one search result)
- Type set on a curve, around a circle, or running vertically
- A browser window used as the frame for the whole slide
- Full-bleed photo with one line of very large type (photos: literal subject only, see PLAYBOOK)
- Split frame: half colour and type, half product
- A pattern of many small real things (40 favicons, a wall of page titles) with one highlighted
- Macro crop: a tiny part of an interface blown up until it's abstract
- Poster: centred, symmetrical, one serif word, lots of air (use rarely)

Techniques that lift the craft: film grain (`<!--grain:0.06-->`), layered shadows (one tight, one wide), a soft glow in the accent behind the hero, hairline borders one step lighter than the surface, skeleton bars for unimportant interface text so the one real label stands out, `mix-blend-mode`, `clip-path`, SVG for anything geometric.

**Palettes.** Build one per post: a background, a surface or two, a text colour, one accent. Draw from anywhere, and move a long way from the last few posts. For example: black with acid lime; bone with signal red; deep green with cream; cobalt with white; pale lilac with ink; chalk pink with oxblood; graphite with ice blue; butter yellow with black; plum with pale pink; sand with forest. The Nexulabs blue (`#0C23A8`, `#667DFF`) is one option, not the default.

**Type.** One display face and one text face per post. Available: Geist, GeistMono, InterTight (400–900), Instrument (serif, with italic), Unbounded, Fraun, News, Playfair, DMSerif, Brico, Arch, Grotesk, Outfit, Syne, Cond, Oswald. A serif italic word inside a heavy sans headline is a strong move; don't use it every time.

**Made-up businesses.** Concept sites and screens for invented businesses are still good content. Every one is a new design that suits its trade, and the caption says it's made up. Use phone numbers from 07700 900000–900999.

## Reels

`art/reel.html` is a row of `<section class="scene" data-dur="3.2">` blocks. Each scene is designed like a feed frame at 1080×1920, and it **moves**: things arrive, grow, slide, count, type on. Helpers: classes `up`, `fadein`, `pop`, `wipe`, `left`, `right`, with `style="--d:.4s"` for the delay inside the scene; or write your own keyframes with `animation-delay: calc(var(--t0) + 0.4s)`.

- 4 to 6 scenes, 12 to 20 seconds. The first second is the hook: the biggest, clearest frame.
- Keep text inside the safe area (top 220px and bottom 380px are covered by Instagram's interface).
- Motion with purpose: a card flying into a pipeline, a number counting up, a page assembling. Not just text fading in.
- Look at `.reel-sheet.jpg`, and step through the video frames if anything animates across text.

## Stories

1080×1920, 3 to 4 frames, top 250px and bottom 320px kept clear. Same standard, same no-repeat rules. A Story can be simpler than a feed post, but never plainer: one bold frame beats four dull ones.

## The checklist (step 6)

Look at the rendered image, not the code, and answer honestly:

1. Covered up the logo, would this pass for a post from a top technology brand?
2. What is the hero of each frame? Is it big enough that it's obvious at thumbnail size?
3. Is any area empty for no reason? Is anything small that should be huge?
4. Could any text be cut? Then cut it.
5. Do all the frames belong to one campaign (same palette and type), while each is composed differently?
6. Is anything overlapping badly, clipped, nearly touching or nearly aligned?
7. Have I seen this layout on this account before? Then change it.

The reference for the bar is `design-samples/standard/` (the 11 Nov "Enquiry in. Nothing lost." carousel). It is the minimum, and it must not be copied: its compositions and its lime-on-black palette are now used up.
