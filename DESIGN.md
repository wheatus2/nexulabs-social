# Nexulabs design standard

**Read this before designing anything. It replaces the slide templates, the "five looks" and the mockup slide type.**

Lee, 11 Nov 2026: the posts were "very repetitive, very basic", and "look like something my 7 year old has put together". The standard he set: **"if Google, Apple or Nvidia were posting content to Instagram, what would that look like? This is the standard you need to be at."** And: "do not repeat designs", layouts or colours.

He was right. Every post had the same skeleton: logo top left, label top right, a headline, a list of small text, and a lot of empty flat colour. Changing the font and colour did not hide it.

**Aim for the pass mark every time.** Until 13 Nov 2026 a post under the mark was held. Since then it still goes out after a second, different design: see "Always post" below.

**Pass mark (Lee, 12 Nov 2026): 7 out of 10 or above from the independent second opinion.** It was 8. On 12 Nov the same carousel was reviewed eleven times and scored 6.5 to 7.5 whatever was changed, so Lee approved it himself and set the mark to 7. Under 7, or a frame the reviewer plainly calls basic, is still held. Always report the score.

## Always post (Lee, 13 Nov 2026)

Lee, after the 08:33 carousel was held on 13 Nov: "try again with a new post, dont just skip always post".

- A feed slot is not left empty because of the design score. The review is still run and the pass mark is still the aim.
- If the first design misses the mark, make a **new design with a different visual idea**. Don't patch the same one. (The flat type version of the HTTPS post scored 6.5 twice; the keyboard version of the same facts scored 6.5, then 7.)
- After the second review, fix what the reviewer named and publish the stronger version, with the score stated plainly in the summary and the log.
- Facts are different: a claim that can't be verified is still cut. Post advice that needs no outside facts if it comes to that.
- The scheduled task prompts were written before this and still say "publish nothing" after two failed rounds. Until Lee changes them, say in the summary which rule the run followed.

## Mix it up: photo posts too (Lee, 12 Nov 2026)

Lee: "We should always mix up posts and include images sometimes." Type and interface posts are not the only kind.

- Before designing, look at the `photo` field of the last five feed entries in `log.json`. If none of them used a library photo, make this post photo-led when a cleared photo literally shows the subject (`python3 photo.py list`, rules in PLAYBOOK "Photos from the library"). No fitting photo is not a reason to skip the slot: design it instead.
- A photo post is still designed from scratch: the photo is the hero, with one line of very large type. It goes through the same check, design review and fact-check.
- Remove any other company's logo, phone number or name that is readable in the photo.
- Log `"photo": "<unsplash id>"` in `log.json`, credit the photographer in the caption, and `python3 photo.py retire` the photo after publishing.
- Learned on the first one (the yellow phone, 12 Nov): the reviewer scored a headline stacked over a stock photo 6.5 ("a template"), and type warped onto a photo's floor and ceiling 5.5 ("pasted on"). Lee approved the phone post himself. Next time make the type and the photo interlock for real (the subject in front of the type), or let the photo fill the frame with very few words.

## How posts are made now

Every post is designed from scratch, as its own HTML and CSS, with `studio.py`. There are no templates.

1. `python3 studio.py recent` — see what the last posts used. Yours must be different.
2. Write the idea in one line (the `concept`). What is the one picture this post is?
3. Design each frame in `posts/<id>/art/slide-01.html`, `slide-02.html`… (a Reel is one `art/reel.html`).
4. Write `posts/<id>/design.json` (format, one composition name per frame, background colours, display font, accent, concept).
5. `python3 studio.py render posts/<id>` (or `reel`), then **open `.sheet.jpg` and every slide and look at them.**
6. Critique against the checklist below. Fix. Render again. Expect at least two rounds.
7. `python3 studio.py check posts/<id>` must pass. It fails on small text, clipped text, text outside the safe area, too many words, and repeats of recent posts.
8. **Second opinion.** Give a fresh subagent only the rendered images and this question: "Would Apple, Google or Nvidia post this? Score 1 to 10 for craft, and name the weakest frame and why." **Pass mark: 7 or above** (Lee, 12 Nov 2026). Under 7, or a frame the reviewer plainly calls basic: redesign and ask again. Two failed rounds: don't post. When it passes, still fix the quick, specific faults the reviewer named before publishing, and put the score in the summary and in the log.
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
- Technical notes from the first studio Reel (`posts/2026-11-12-1433-count-your-fonts/art/reel.html`, 12 Nov 2026): `studio.py check` counts the text of every scene unless hidden scenes are `visibility:hidden`, so copy that reel's `.scene` rule (the `sv` keyframes, which run 0.02s past the scene's end so no black frame appears at a cut). Set `.scene{overflow:visible}` if a hero bleeds off the frame. A word split into one element per letter is counted as one word per letter: put `data-ui` on the wrapper and allow reading time for the real word count yourself.

## Stories

1080×1920, 3 to 4 frames, top 250px and bottom 320px kept clear. Same standard, same no-repeat rules. A Story can be simpler than a feed post, but never plainer: one bold frame beats four dull ones.

## What the reviews taught us (12 Nov 2026)

One carousel (the colour-contrast post) went through eleven independent reviews in one morning. Read this before designing: it is what the reviewers actually reward and punish.

**How the reviewer behaves**
- Scores sat between 6.5 and 7.5 every time. Two reviewers can differ by a point or more on the same frame (the eye-chart frame got 8 three times, then 6 twice). Don't rebuild a frame because one reviewer disliked it; fix what is objective, and what two reviewers agree on.
- Every reviewer says the same thing about the ceiling: type-led explainers read as "a good design studio" (Figma, Linear, Stripe, Google Design), and Apple and Nvidia post product and photography. An 8 needs a real product render or photograph, or a typographic idea with no loose ends at all.

**What scored well**
- Frames where the design does the thing it talks about (faint words measured as faint; the answer set in the same words at full strength).
- One idea, one hero, and a callback between the first frame and the last.
- Fewer frames. Three strong frames beat five with a weak one. Cut the weakest frame; don't patch it.

**What scored badly, every time**
- Devices drawn in CSS (a phone scored 5.5: "a real render or no device at all").
- Infographic furniture: waffle grids, "Aa" scales, before and after sliders, inspector cards with many parts, three pills in a row.
- A frame that states a fact and shows nothing. A gradient on hero type.
- A frame on a different grid from its neighbours.
- A chat or text-message bubble as the hero (12 Nov evening, held): called basic by two reviewers running, first as a flat bubble on a dark frame ("a stock trope"), then rebuilt as a raised object in the post's own material ("a green rounded rectangle with text in it"). The same post's two switch frames were called strong. Show the message another way, or cut the frame.

- A drawn browser window with skeleton bars (13 Nov, held at 6.5): "a generic skeleton mock-up of the kind every SaaS template ships with". The same frame rebuilt as two giant words plus a statement also scored 6.5: "only words on a flat colour", two headlines competing. A middle frame has to show the thing, made properly, or be cut.
- Display type left at its default letter fit (13 Nov). Reviewers now zoom in and measure the gaps between letters in words set at 250px and over. Kern big words by hand so the gaps are equal by eye, and watch for crossbars that merge (tt) and letters that nearly touch.
- A crop that only shaves a letter. Bleed it boldly off the edge or keep it inside the margin.

- What lifted the same post from 6.5 to 7 (13 Nov): swapping flat type for an object with light and depth (keys on a deck), a zoom from frame to frame (five keys, two, one), a true recess for the missing key (no raised rim, inner shadow, a ghost of the letter) and a cover headline big enough to fill the frame. A small hero floating between two equal voids was called basic.

- A drawn paper object can pass (13 Nov, the business card Story, 7 first time): one card for a made-up firm, lying, then in close-up, then standing, with a painted edge, paper grain and focus falling off behind the line that matters. For a close-up, build the object at its real size with CSS `zoom`, not `transform: scale()`: a scaled layer is enlarged after it is drawn, so type and filter edges go soft and blocky. Keep a pale surface out of the top 250px of a Story (Instagram's white name and bars sit there): shade it.

- Put the punchline in the headline, not the footer (13 Nov, the Microsoft outage post): the twist of a three-frame joke was set as small footer text and the reviewer called it buried. A last frame of two small labelled buttons was called "a settings screen"; the same hero object, bigger, in a new state, was the fix.
- Drawn objects need real form to pass (13 Nov): a dished cap, a dark clearance gap between the part and its surround, a tight contact shadow and a glass highlight on a light. Soft gradients on their own were called "2020 Dribbble neumorphism".

- Shoot a drawn object close up, not whole (13 Nov, the stopwatch Reel, `posts/2026-11-13-1433-how-fast-is-your-website/art/build.py`). The same stopwatch was reviewed four times. Whole and centred on a colour field with a headline above it, it was called basic twice ("a polished app icon on a gradient"). Cropped close and off centre, with the hand as one long line down a side, the type anchored against the dial and the rest falling out of focus, the same drawing scored about 8 a frame. What made the close-ups read as real: ticks with a lit edge and a soft shadow, a turned tick track a step below the dial, numerals printed on the dial so the object says the number itself, and depth of field (a `backdrop-filter: blur()` layer with a radial mask, with the hand drawn after it so it stays sharp).
- Every frame of a post in the same world. Two close-ups on a pale dial between an opener and a closer on a blue field were marked down as "two visual worlds". And don't shoot the opener and closer with one camera: it was called a repeat, not a callback.
- A pointer either meets its mark exactly or crosses it boldly. The hand's tip was faulted for stopping 15px short of the scale, then 180px short, then for lying 35px over a tick. It passed with the point touching the tick's inner end.

- A clean diagram of an idea is not enough (13 Nov evening, the "squares or curves" Story, held at 6.5 twice, draft in `posts/stories/2026-11-13-1747-squares-or-curves`). One made-up logo mark in two flat colours, shown solid, then as pixels, then as a path with its handles. Both reviewers liked the idea and both called the pixel frame the weakest: first a real small JPG blown up under a hairline grid ("dirty tiles", "a headline and a paragraph on graph paper"), then clean averaged tiles with the copy above and one word below ("three unrelated bands", "a stripe, not pixels"). No frame had an object with light on it. Next time show the pixels on a real thing, or cut the frame.
- Paired frames are compared side by side (same review). Two one-word headlines that answer each other are set at one size, not each stretched to fill the measure, and their copy runs in the same order. Handles on a selection box all look the same. A big shape either clears the frame edge or bleeds well past it: one nearly tangent to the bottom was marked down.

- A drawn object needs a real camera, and the last frame needs it most (13 Nov evening, the "three letters" Story in `posts/stories/2026-11-13-1830-three-letters`: held at 6.5 twice, then reworked and published at 6.5 when Lee said to post it). A brass nameplate drawn in CSS with blur and bevel filters was called "a faux-3D effect", and its close-up "a low-res upscale". Rebuilt with true perspective, sides and shadows (`art/build.py` there: each face drawn flat, then placed by a small camera in Python), the angled shot and the close-up scored 7 each. The payoff frame, two plates square on between a headline and a footer, scored 5.5: "basic: headline, two stacked boxes, footer". Give the last frame the same kind of shot as the others, and one object, not a stack.
- The same highlight on every object reads as an effect (same review): one two-stripe gloss repeated on each plate in all three frames was called "the biggest sign that it is an effect, not lighting". Draw a different reflection for each view, and keep it off the letters the post is about. An even metal with no room reflected in it was called "2012-era skeuomorphism".
- Never crop a word in the middle on an object ("AKE & QUAY LTD" was read as a mistake). Show the whole word or cut between words. Two objects on one wall share one perspective and sit well apart, or touch.
- Technical: the browser's own CSS 3D leaves out parts of a layer that is very large or close to the camera (anything past about 4,000px wide at 2x). Use the camera in that `build.py` for big objects at steep angles. Headline letter-spacing tighter than about -.03em makes tt, th and ft touch in Outfit.
- What the rework of that Story added (two more reviews, 6.5 each, the close-up frame 7.5 both times). Shoot every frame from the same side, so a close-up reads as the camera moving in: a view from the right followed by one from the left was called a flip. A long thin object seen whole along its length crushes its far letters; show the end of it at a readable angle and let the rest run off between words. One plain reflection used on every plate (a strip of sky above the letters) drew no complaint, where stripes and mottling did. A list engraved on a plate stays small however it is shot: about 30 characters a line is all a Story frame holds at a readable size.

- An object drawn in the browser's 3D tops out at 6.5 (13 Nov evening, the tear-off calendar Reel, held at 6.5 five times, draft in `posts/2026-11-13-1933-who-reminds-them`, `art/build.py`). Five reviewers liked the idea, the dates, the palette (chocolate, cream, one pink page), the serif headlines and the inked stamp, and all five said the pad "reads as a browser-made 3D object". What moved single frames from 5.5 to 7.5: the pad's thickness and its shadow in every shot, a round date stamp with uneven ink (a PNG mask), the page under a lifted corner, one left margin for everything printed on the page. What did not move the total: texture, blur, re-framing. Next time start from a photograph or a proper render when the post is one object.
- A held frame of "time passes" is the weak one whatever is done to it (same Reel): cropped it was "thin", whole it was "a stock calendar in the middle of a gradient". Cutting the scene was right; the pages now fall at the start of the next scene. A closer that mirrors the opener was called a repeat again, and a wordmark on the headline's last baseline was read as part of the sentence.
- Tell the reviewer the truth about Instagram's bands and no more: its buttons and caption sit over the top 220px and bottom 380px and the picture shows through. Called "covered", every reviewer marked down dates and labels in those bands.
- Technical, CSS 3D (same Reel): a layer that is clipped (`clip-path`, or `overflow:hidden` with a radius) loses its lower part when it is tall and close to the camera, so clip only small pads. Two sheets a unit or two apart in depth draw stray lines across each other from a low camera; paint the pages under the top sheet as stripes on the sheet itself. `mask-image` from a file does not load in the render; inline it as a data URI. Text inside a `data-bleed` element is not checked against the safe area, so measure it yourself. `filter: blur()` on a falling layer reads as motion blur; an SVG one-way blur came out in steps.

- A library photo with type over it scores 5.5 to 6 however it is fitted (13 Nov night, the OPEN sign, held, draft in `posts/2026-11-13-2140-does-google-agree`). The idea was rated about 8 by three reviewers: a shop's own OPEN sign, and under it "Does Google agree?". The execution was called a template three ways: as lettering on the window, as a line hung at the sign's tilt, and as a two-line headline cut to the sign's width over a darkened lower half. What was learned: reviewers zoom in, and a 1,280px crop is soft and noisy beside crisp type; heavy retouching shows (a painted-out disc left the cords cut off in mid-air, a toned-down lamp left a ghost), so crop a distraction out or leave it in; the eye lines type up with the main object, not with a hairline elsewhere in the picture; photo plus scrim plus condensed capitals plus small logo is "the Canva formula". A photo post needs a sharper photograph than the library holds at this size, or the type has to be inside the picture.
- A drawn split-flap departures board passed first time at 7 (14 Nov, the US flights post, `posts/2026-11-14-0015-every-departure-stopped`): the object carries the headline itself, one yellow row a frame, three distances. Named faults fixed before publishing: the board and the type share one side margin, the letters sit on the axle so the seam does not notch the crossbars, a light shadow under the seam so yellow stays yellow, no half-fallen leaves (they read as rendering mistakes at feed size), a source line on every news frame.

- A proper 3D render is now possible in a scheduled run, and it passed (14 Nov, the .co.uk sign, `posts/2026-11-14-0837-lights-out/art/build.py`, 6.5 then 7). `pip install bpy brotli --break-system-packages` gives Blender as a Python module (Cycles, no window needed); the repo's woff2 fonts convert to TTF with fontTools. The script builds the scene, renders a 32-bit EXR, then does bloom, the film curve and grain in numpy. The type is ordinary HTML over the picture. Timings on the two-core runner: a draft (40% size, 32 samples) in about 30 seconds, a final 1080x1350 frame at 160 samples in 4 to 7 minutes, so settle the cameras on drafts first.
- What the reviewers said about it. Three different cameras on one object scored 6.5: "three separate renders". One locked camera with only the object changing (lit, off, gone) scored 7 and was praised as "a three-state animation". This is the one case where the frames of a carousel should share a composition; say so in the summary. An unlit object in plain grey was called "default 3D text" twice: give a switched-off thing a real material (dark returns, a glossy face, a reflection from a light linked to that object only, so the wall does not brighten). Extruded letters close up their own gaps when seen from the side: keep them shallow and add letter-spacing. A thin dangling cable read as a hair. A ghost of removed letters reads best as cleaner, brighter paint with a dirt outline, not as a darker patch.
- Lens shift (`cam.shift_x`) slides the picture sideways without changing the perspective: use it to put an object's edge exactly on the type's margin. The printed footprint of an object on the wall sits to the camera's side of the object itself, so measure the finished render, not the draft's glow.
- Reviewers now measure headline letter gaps in pixels. InterTight 700 at 164px needs these pairs opened by hand: Fo, rg, ot, to, re, ew, ts, yo, rs. Letters wrapped one by one count as one word each in `studio.py check` and are measured by their line box: put `data-ui` on the headline, measure the ink yourself with `tools/ink.py`, and note the real word count in the file.
- Facts: the independent fact-check caught that Nominet's day counts for a lapsed .uk name (30, 90 and 95 days) change on 9 February 2027. Ask the checker to flag anything "true today but misleading for someone acting on it in the coming months", and prefer the order of events over day counts when a rule is about to change.

- A real still life in 3D passes first time (14 Nov, the bill spike Story, `posts/stories/2026-11-14-1147-bottom-of-the-pile/art/build.py`, 7 twice, no frame called basic). One spike with 36 printed dockets on it. The paper is not simulated: each docket is a strip that bends one way only, laid on whatever is already there (a height map), bridging the bumps, drooping where nothing holds it, and curling up at both ends like till roll. The print is HTML shot to PNG with the tear bar's saw edge in the alpha (`art/dockets.py`). The close-up of the bottom docket under the tower scored 8: "the one image that looks like it came from a top-tier brand account".
- What the two reviewers marked down, both times: the last frame, shot from above, where the spike reads as a different object (wider, flatter) and shows no hole where it goes through the paper. Seen from above a polished rod mirrors only what is under it and looks like glass; two cards that only reflections can see gave it a lit and a dark side, and it was then called "a blade". Next time keep the spike small in every frame, or model the pucker in the paper where it goes through.
- Reviewers compare the headline's left edge from frame to frame (70, 207 and 276px were called a jump on tap-through) and the green from frame to frame (darker behind frame 1's headline). Lining type up with something in each picture is not enough: keep one margin, and grade the three pictures to one backdrop.
- Timings: paper is slow. A 1080x1920 frame that is all paper took 26 minutes at 144 samples on two cores; the wide frame took 11 at 104. Two frames at once take as long as one after the other. `python3 build.py 3 final region` re-renders only a window of a frame in half a minute: use it to try a material or a light on one small object before paying for a whole frame. Allow 90 minutes of rendering for a three-frame Story like this one.
- White type on a bright green has too little contrast (2.6 to 1). The grade now holds saturated colours down (`GREEN_HOLD` in that script) and leaves the paper alone, which took the headline to about 4 to 1.

**The craft list that came up in every review**
- Measure, don't eyeball: `python3 tools/ink.py posts/<id>/slide-01.jpg` prints where the ink is, so gaps and padding can be made equal on purpose.
- Nothing within about 40px of anything else unless it is meant to touch. Padding inside a box equal on all four sides (measured from the ink, not the CSS box). The gap above a block and the gap below it equal, or clearly different.
- Letter-spacing no tighter than -.03em on serif display type; italics close to 0. Check for letters that touch at large sizes.
- One tag or pill component, one footer (a bold line, a muted line, the logo on the right) and one margin across every frame of a post. Small labels at 32px or more.
- Curly apostrophes, no orphan words, no footer that repeats the headline.
- Read the frames in order as a stranger would: the last frame's line must follow from the first.

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
