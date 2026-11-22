# Held: not published

19:33 slot, Sunday 22 Nov 2026. Reel, 3 scenes, 12.4 seconds. Promotional, websites, the free homepage concept, "Book a call at nexulabs.co.uk".

The independent design review scored it 6 and then 6 (pass mark 7). The first review called the overhead scene basic; the second called the last scene basic. So the scheduled run published nothing, as its instructions say (DESIGN.md "Always post" says a slot is not left empty; the task prompt says publish nothing after two failed rounds, and this run followed the task prompt). The fact-check passed. The Reel is complete (reel.mp4, cover.jpg, caption.txt) and can be published as it stands (publish.yml, mode post, this folder) if the owner says so.

## The idea
The free homepage concept as a blueprint. One made-up drawing of a homepage, white line on blue (nav, "Your headline.", a Book a call button, a photo box, What you do, an enquiry form, and a title block: Free homepage concept, over the Nexulabs wordmark), on a plaster-pink table with a black pencil beside it, rendered in Blender. The sheet is white on the back, so it unrolls as a white roll towards the headline. "Your new homepage." / "Mocked up free, before you commit." / "Book a call at nexulabs.co.uk".

## Review 1: 6 (scenes 6.5, 5, 7, 6.5). First design, four scenes, kept in art/v1
Wide from high on the right; square on from directly above; low along the roll from its open end; the title block from the front. Marked down: the overhead scene was basic ("a 2D wireframe graphic with a white bar across it, nothing in it needed 3D"); scenes 1 and 4 near-duplicates in angle; the roll cutting through cards, a button and the balloons A, B, C on the hold frames; words cut by the frame edge (the vertical "First screen" label in three scenes); a patch of a different blue behind the PHOTO label; a sawtooth at the end of the roll; a heavy brown shadow; the same static headline in the same place four times. The low shot along the roll was "the only one with real photographic character".

## Review 2: 6 (scenes 6.5, 7, 5.5)
Reworked: the overhead scene cut; the last scene re-shot low and from the front; balloons and the vertical label taken off the print; dimension lines broken round their words; the sheet's long edges lifted; softer light; the headline in the blue of the sheet. Still marked down:
- Scene 3 basic: "a centred product shot on a flat backdrop with a caption underneath", and it is the scene with the logo. From a low camera the far half of the print is a smear, and before the roll moves off the wordmark the frame has no brand in it.
- "A good mockup template rather than a directed film": one prop, a flat backdrop with no room, static type.
- Mid-move frames show two renders at once (the swap is a hard cut, but a frame grabbed on the swap read as a see-through roll).
- The roll is wider than the sheet (the turns are drawn stepping sideways) and stays thick when the sheet has run out.
- The lifted edge on one side reads as a wobble because the other side is straight.
- Cards and a button cut by the right edge in the low shot; the wordmark 25px above the roll; the gap from roll to headline different in each scene (95, 125 and 175px); 495px of nothing between roll and headline when scene 1 opens.

## For next time
- The low shot along the roll from its open end (art/build.py, shot 2) scored 7 both times: the spiral of paper edges sharp, the plan going soft behind it. Build on that. The whole sheet seen from above or from the front scored 5 to 6.5 every time: a flat printed sheet is a mockup, however it is lit.
- A roll of paper is very quick: 9 seconds a draft, 3 minutes a 1080x1920 frame at 128 samples, 45 seconds an in-between at 16. Two designs (84 frames) took about 95 minutes of rendering.
- Pin a world point to a pixel with lens shift (the `pin` in SHOTS): it made composing each shot a one-line change.
- Anything printed near the edge of a long sheet gets cut by the frame in every close shot. Keep words in the middle third.
- Type below the object (the roll comes towards the headline) passed the checks, but both reviewers counted the bare table between them as dead space. Start each scene with the roll already close.
- The reviewers asked for a room: something for the table to end against, a second prop that does something, type that moves.
- Tools: python3.13 for bpy and for studio.py (PIL is broken under python3 here); playwright under python3.13 needs executable_path /opt/pw-browsers/chromium.
