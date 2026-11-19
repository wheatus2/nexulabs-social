# Held: not published

19:33 slot, Thursday 19 Nov 2026. Carousel, 3 frames. Promotional, branding, "See what we build at nexulabs.co.uk".

The independent design review scored it 6.5 and then 6 (pass mark 7), and both reviews called frame 2 basic, so the scheduled run published nothing, as its instructions say. The fact-check passed. The carousel is complete (slide-01 to slide-03, caption.txt, sources.md) and can be published as it stands (publish.yml, mode post, this folder) if the owner says so.

## The idea
Branding for a business that doesn't exist. One roll of woven labels for a made-up knitwear maker (Thrumwick), rendered in Blender on sand linen: navy with the name in ivory on the front, the other way round on the back. "Thrumwick doesn't exist." / "We branded it anyway." / "Your business does. See what we build at nexulabs.co.uk". Both reviewers called the three lines the best thing in the post.

## Review 1: 6.5 (frames 7, 5, 6.5). First design, kept in art/v1
Eight rows of ribbon from above; a low shot along two rows; the roll with its cut tail. The lettering was cut down to a grid of threads so it stepped like a woven label: read as "low-resolution" and "pixelated", not as weave. Frame 2 basic: "a headline over a blurry diagonal stripe", both repeats of the name cut (one by blur, one by the edge), the ivory row lost on the sand cloth, half the frame empty. Also: near rows squashed by perspective, a tail end 20px off the type margin, a serif headline against a second serif on the label.

## Review 2: 6 (frames 6.5, 4.5, 7)
Reworked: smooth lettering at 50 to 60 px a millimetre; a long lens on frame 1 so every row is seen the same; frame 2 remade as three rows filling the frame, one name on each, the navy one in focus; Bricolage for the headline; the tail end on the margin. Frame 2 basic again: "nothing in the image is properly sharp", the thread shading inside the letters read as "an upscaled texture", the ivory rows melt into the cloth, and "it adds no new information" (a close-up of frame 1). Frame 3 was the best (7). Frame 1: the folds step 15px a row and land near the margin and the right edge without meeting either; the row shadows fall across the first letters of the ivory rows; the name appears 17 times and competes with the headline.

## For next time
- A close-up of the same ribbon is "a re-crop" however it is framed. The middle frame needs a new picture: the label sewn into something (a collar, a hem), or the brand on a second object.
- Weave drawn into the texture (stepped letters, thread stripes) reads as a bad texture at feed size. Leave the lettering clean, or model the threads as geometry and shoot them properly sharp.
- Depth of field at f/8.5-equivalent over 4 cm rows leaves nothing crisp at 1080px. Keep the hero row fully sharp (aperture_fstop 0.2 or more here).
- Ivory ribbon on sand cloth has no edge. Give the object's light side a backdrop it stands off from.
- One word on a two-colour ribbon was called thin proof of "branding". Show more of the brand: a mark, a second colour, two or three applications.
- Folds either sit on the type margin or bleed; with any perspective they step, so use an orthographic camera for a top-down pattern.
- The roll with its cut tail (frame 3) is the picture to build on. Its shadow should clear the frame edge or the roll should bleed.
- Timings on four cores: 1080x1350 at 128 samples in about 4 minutes a frame, three at once in about 7. Row-long repeating textures (REPEAT) keep the print sharp without a 30,000px image.
