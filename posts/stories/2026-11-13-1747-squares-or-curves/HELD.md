# Held: not published

This Story was made by the 17:47 run on Fri 13 Nov 2026 and **was not published**. Do not publish it from a scheduled run. It needs Lee's say-so, or a rework and a fresh design review that passes.

**Why.** The independent design review scored it 6.5 out of 10, twice (pass mark 7). Both reviewers named frame 2, the pixel frame, as the weakest, and the second called it "borderline basic". The Story task says two failed rounds means nothing goes out, so the slot was left empty. DESIGN.md's "Always post" rule is written for feed slots, so it was not applied here.

**The idea.** Branding, this or that: zoom in on your logo, squares or curves? One made-up logo mark (a ring and a stem) in two colours, electric violet and bone, Syne and Outfit.
- Frame 1: "Zoom in on your logo." over the solid mark, with a selection box the shape of the Story frame on the notch where the ring meets the stem. "Squares or curves?"
- Frame 2: exactly that patch as a small picture stores it, nine pixels by sixteen. "A JPG or a PNG is only a picture. Bigger picture, bigger squares." and "Squares."
- Frame 3: the same mark as a path, two anchor points and their handles on a symmetrical arch. "Curves. That's the logo itself. A vector file: SVG, AI or EPS. Sharp on a pen. Sharp on the side of a van. Ask whoever made your logo for it."

**What the reviewers said**
- Both liked the idea carrying across three frames, the strict two-colour palette, the matching margins and the copy ("Sharp on a pen. Sharp on the side of a van." was picked out twice).
- Round 1 (frames 6.5, 6, 7). Frame 2 was a real small JPG blown up under a hairline grid: "the lower 40% is basic", grid lines through the type, tiles that looked dirty. Frame 1's selection box was too small and a strip of violet ran beside the stem. Frame 3's handles followed three different rules.
- Round 2 (frames 7.5, 5.5, 7), after a rebuild. Frame 2: the copy at the top and the word at the bottom read as "three unrelated bands", the copy runs in the opposite order to frame 3, the stem reads as "a stripe, not pixels", and the palest tiles nearly vanish. Across the set: "Squares." and "Curves." are different sizes because each was fitted to the measure. Frame 1: selection handles that did not match, the counter nearly tangent to the bottom edge, the question is the only right-aligned copy. Frame 3: slivers where the handle lines meet the curves, r and v tight in "Curves.".
- Both said the ceiling for a flat diagram is about here, and that the idea wants motion (zoom, pixelate, resolve).

**Fixed in this draft after round 2 (not re-scored).** Matching selection handles, tiles in clear quarter steps, the r and v, the wordmark on the last line's baseline.

**If it is reworked**
- Frame 2 is the problem. Set "Squares." and "Curves." at one size, put the copy under the headline on both, and give the pixels something real to sit on, or cut to two frames.
- It would make a good Reel: the selection box grows to fill the frame, the patch goes to squares, then the squares resolve into the curve with its handles.
- Frame 1: move the mark so the counter bleeds well past the bottom edge.

**What is fine.** The facts are sourced (see sources.md; Adobe and MDN, both opened in the run). `studio.py check` passes. The Branding highlight cover is already out, so no cover is needed. Not in design-log.json, so the palette and typeface are not used up. `art/build.py` rebuilds the frames and `art/pixels.png`.
