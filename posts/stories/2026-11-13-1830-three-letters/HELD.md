# Held: not published

This Story was made by a second firing of the 17:47 task on Fri 13 Nov 2026 (it started about 18:27, after the first run's Story for the same slot had already been held). It **was not published**. Do not publish it from a scheduled run. It needs Lee's say-so, or a rework and a fresh design review that passes.

**Why.** The independent design review scored it 6.5 out of 10, twice (pass mark 7). The second reviewer scored frames 1 and 2 at 7 each and frame 3 at 5.5, and called frame 3's layout basic ("headline, two stacked boxes, footer"). The Story task says two failed rounds means nothing goes out. DESIGN.md's "Always post" rule is written for feed slots, so it was not applied here.

**The idea.** Web design, did you know (UK source): a limited company's website has to show four things. One engraved brass nameplate for a made-up company, Kittiwake & Quay Ltd, on an oxblood front door. Oxblood, brass and cream; Outfit for the headlines, Newsreader capitals cut into the plates.
- Frame 1: "Limited company?" The plate runs towards us along the door until LTD is the biggest thing in the picture.
- Frame 2: "Those three letters come with a list." Right up against LTD, with the end of the plate and its two screws.
- Frame 3: "Your website has to show all four. Check your footer tonight. Source: gov.uk, Running a limited company". The end of the name plate, and a second plate under it: Registered in England and Wales, Company No. 24601357, Registered office 12 Quay Row, Sunderland.

**What the reviewers said**
- Round 1 (6.5; frames 6.5, 5.5, 7). The first build drew the plate in CSS with blur and bevel filters and set the headlines in Anton. "A faux-3D effect, not a photograph or a proper render", the condensed headline face "reads as a template", and the close-up of LTD looked like "a low-res upscale". It also faulted two question marks stacked on frame 1, headlines at two very different sizes, a plate that changed shape between frames, a placeholder company number of all zeros and streaks in the background.
- Round 2 (6.5; frames 7, 7, 5.5), after a full rebuild (see below). Frame 1 was called the boldest and frame 2 the cleanest. Frame 3 was called basic, and its faults were: the name cropped mid-word ("AKE & QUAY LTD"), the two plates in slightly different perspective, the gloss stripe running through LTD, the plates about 40px apart with one's shadow on the other, the lower plate's left edge lining up with nothing, the last engraved line close to the screws, the small engraving looking printed, "all four" not shown as four things, and five levels of text.
- Across the set in round 2: the same two-stripe gloss on every plate "is the biggest sign that it is an effect, not lighting", and the brass is too even (no reflection of a room, no wear). On frame 1, "Kittiwake" is too small to read at the far end and the D looks stretched. On frame 2, the plate stops about 80px short of the right edge. Tight headline tracking: tt in "letters", th in "three", ck and ft in the footer line.

**If it is reworked**
- Frame 3 is the problem. Give it one object and one camera: for example the same close-up as frame 2, pulled back just far enough to show a second plate under the first, with the four things as four clear lines. Or put the four on the name plate itself, so nothing is stacked. Show the whole name or crop to "& QUAY LTD", never mid-word.
- Draw a different reflection on each plate, and keep it off LTD.
- Ease frame 1's angle a little so "Kittiwake" can be read.
- Headline letter-spacing at about -.02em, not -.035em.

**What is fine.** The claim is sourced (see sources.md; the GOV.UK page was opened in the run). `studio.py check` passes. The Websites highlight cover is already out, so no cover is needed. Not in design-log.json, so the palette and typeface are not used up.

**How it is built.** `art/build.py` draws each plate face flat in HTML (brass, bevel, screws, letters cut with an SVG lighting filter), then places the door, shadows, plate sides and face with a small pinhole camera in Python and writes `art/bg-0N.jpg`; the slide files put the headline over that picture. Run `python3 posts/stories/2026-11-13-1830-three-letters/art/build.py`, then `python3 studio.py render` on the folder. It is worth reusing for any drawn object seen at an angle.
