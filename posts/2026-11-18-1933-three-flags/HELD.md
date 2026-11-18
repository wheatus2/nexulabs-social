# Held: not published

19:33 slot, Wednesday 18 Nov 2026. Reel, 4 scenes, 16.2 seconds. Promotional, websites, offer: free website review, "Book a call at nexulabs.co.uk".

The independent design review scored it 5, then 5.5 after a redesign (pass mark 7), and called scenes 1 and 4 basic both times, so the scheduled run published nothing, as its instructions say. The fact-check passed on the second round. The Reel is complete (reel.mp4, cover.jpg, caption.txt) and can be published as it stands (publish.yml, mode post, this folder) if the owner says so.

## The idea
The free website review as three pink page flags. One phone on a pale grey sweep showing a made-up firm's ordinary website (Ashgarth Kitchens: "Welcome to our website"), rendered in Blender, with three pink flags numbered 1, 2, 3 in marker stuck on its glass. "What would we change?" / "We'll look at your website." / "And send back three things." / "Free website review. Book a call at nexulabs.co.uk".

## Review 1: 5 (scenes 5, 4, 6, 6)
Version 1 had the whole phone in scenes 1 and 4. Scene 1 "basic: small phone floating in empty grey". Scene 2 the weakest: a numeral clipped by the frame edge, the site's small print smeared, dead space under the headline. Scene 4 "a stock end-card": headline, address, logo, mockup. Throughout: the flags pointed at nothing in particular, their shadows were pink smudges, the reel never shows what the three things are.

## Review 2: 5.5 (scenes 5, 7, 6, 4.5)
Redesigned as four close shots, each flag on a specific thing (headline, small print, Read more button), sharper screen texture, harder shadows, no wordmark. Scene 2 (flag 1 at the whole headline, phone legible) rose to 7. Still marked down:
- Scene 1 "basic": about 70% of the frame is blur, and the one sharp flag points at an unreadable grey bar.
- Scene 4 the weakest: the call to action line sits on the blurred corner of the phone, the sharpest words in the picture are the made-up site's "Read more", no end card or wordmark, a render artefact near the home bar.
- Scene 3: flag 1's point clipped by the left edge, cut-off word fragments down the left edge, flags pointing at blank white.
- The headline in the same place at the same size in every scene "reads as a template". The flags "flat, plasticky magenta", the phone "a generic render". The pink of the word "three" not matched to the flags.

## For next time
- A phone mock-up scores as "a small-agency template" however it is lit: 5 whole, 5.5 close. The frame where the screen was legible and the flag met a readable headline was the only 7.
- A flag or pointer has to point at something the viewer can read in that frame, and the reel has to pay off what it promises ("three things" with no things was faulted twice).
- Shallow depth of field over most of a frame is "blur", not depth. Keep what the scene is about sharp, and keep type off blurred objects.
- The last scene needs a clean field for the call to action and the wordmark; without the wordmark it was "no end card", with it over a mockup it was "a stock end-card".
- Screen textures: 6x the CSS size and cubic filtering made 38px headlines sharp at this distance; 10px body copy still smears. Leave small print out of the screen or go closer.
- Technical: the scene is in real metres, so real f-stops apply (f/4.5 to f/16). A screen that is part emission (0.62) and part lit surface takes shadows from things lying on it. A frame takes 4 to 6 minutes at 128 samples on four cores; two rounds cost about 80 minutes of rendering.
