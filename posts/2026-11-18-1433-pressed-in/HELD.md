# Held: not published

14:33 slot, Wednesday 18 Nov 2026. Reel, 4 scenes, 15.6 seconds. Promotional, branding, "See what we build at nexulabs.co.uk".

The independent design review scored it 6.5 twice (pass mark 7) and the second review called scene 1 basic, so the scheduled run published nothing, as its instructions say. The fact-check passed. The Reel is complete (reel.mp4, cover.jpg, caption.txt) and can be published as it stands (publish.yml, mode post, this folder) if the owner says so.

## The idea
Branding you can watch happen. Bottle-green soap for a made-up maker (Tidewrack Soap Co.) on a sand sweep, rendered in Blender. A blank bar: "Good soap. No name." The name presses into it: "So we gave it one." The bar in a cream paper band: "Now it's a brand." Banded bars in a row: "Let's brand yours."

## Review 1: 6.5 (scenes 6, 7.5, 5, 6)
Scene 1 (three blank bars, wide) was called basic. Scene 3 was the weakest: the pressed name on the out-of-focus bars was mush with bright speckles, the pressed K showed past the edge of the paper band, two bars nearly touched. Scene 4: a seam in the backdrop, the wordmark and the web address both saying "nexulabs" within 110px, the address line wider than the headline.

## Review 2: 6.5 (scenes 6, 7.5, 7, 6)
Reworked: scene 1 became the same locked close-up as scene 2 with the bar still blank; blank bars under every band; kelp flecks and more translucency in the soap; thicker paper; a gentler sweep; no wordmark, the call to action on two lines. Scene 3 rose from 5 to 7. Still marked down:
- Scene 1 "basic": a blank green slab under two lines of type, and it is the frame that has to stop the scroll.
- Scene 4 the weakest: the product is at its smallest when the call to action lands, the bars behind are blurred blobs, the backdrop is warmer than the other scenes.
- The soap "reads as silicone or plastic" both times. Flecks did not fix it.
- The pressed wordmark (thickened for the die) and the printed one look like two logos. A fleck sat under a letter. The bar under the band looked a different shape from the pressed one.

## For next time
- A blank object cannot be the opening frame, however well it is lit. Open on the pressed name and tell the "before" some other way, or in the caption.
- The close-up of the pressed name scored 7.5 both times: a deboss as real geometry (art/build.py, bar_mesh) under one low light is worth using again.
- End on the biggest picture of the product, not a row of small ones.
- One wordmark drawing for the die and the print. Keep flecks away from lettering.
- Grade every scene to one backdrop colour by sampling it, not by eye.
- Timings on four cores: a 1134x2016 frame at 112 samples took 5 to 9 minutes, at 48 samples about 3. Two rounds of thirteen frames took about 100 minutes.
- Tools: bpy and playwright run under python3.13 here; the pip playwright wants chromium_headless_shell-1255, so link /opt/pw-browsers/chromium_headless_shell-1243 to that name. Fonts do not load with page.set_content: write the HTML to a file and open it.
