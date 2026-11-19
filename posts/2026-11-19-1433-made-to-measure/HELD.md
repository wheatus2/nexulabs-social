# Held: not published

14:33 slot, Thursday 19 Nov 2026. Reel, 4 scenes, 15.4 seconds. Promotional, websites, "See what we build at nexulabs.co.uk".

The independent design review scored it 6 and then 6.5 (pass mark 7), and both reviews called the last scene basic, so the scheduled run published nothing, as its instructions say. The fact-check passed. The Reel is complete (reel.mp4, cover.jpg, caption.txt) and can be published as it stands (publish.yml, mode post, this folder) if the owner says so.

## The idea
Websites made to measure. One made-up tailor's tape measure standing on its edge on a lilac cloth, rendered in Blender: ivory with a numeral at every centimetre on the front, violet with kinds of business on the back, a brass end, and the Nexulabs wordmark printed on it as the maker's mark. "Is your business a standard size?" / "We build websites made to measure." / "Whatever business you're in." / "See what we build at nexulabs.co.uk".

## Review 1: 6 (scenes 6.5, 5.5, 6.5, 6). First design, kept in art/v1
A coil that sprang open, one loop seen twice (numerals in focus, then the back in focus), the brass end under the headline. Marked down: the coil swelled with nothing feeding it and the rest barely moved; the trade words that carry the idea were out of focus in scene 2 and only one showed in scene 3; "the loop measures nothing"; words and numerals cut by the frame edge; the tape looked like a clean CG strip; the last scene was "a standard end card" (basic).

## Review 2: 6.5 (scenes 6.5, 6, 7.5, 6)
Reworked: the tape is drawn out of the coil; the loop goes round the headline; the tape folded into five rows, DENTISTS, FLORISTS and BUILDERS sliding into place between two rows of numerals; the last scene stacked as coil, brass end and wordmark, call to action. Scene 3 at rest was called "the only frame near big-brand level". Still marked down:
- Scene 4 basic: it holds still for three seconds, and "take away the 3D tape and it is a logo over a line of text". It also repeats scene 1's set-up. The 20 on the coil is half hidden behind the tape end.
- The tens (the larger violet 20, 30, 40) touch the numeral before them: "2930", "4950". On every scene.
- Scene 2 early: the loop's back is empty except for the tail of BAKERS cut by the left edge, while the headline is already up. The loop is cut by the left edge, so it reads as an arc, not a loop round the words.
- Numerals cut by the left edge where the tape leaves the frame; the coil soft while the type is sharp; one lilac backdrop for all 15 seconds.
- Scene 3: the folds sit 15px from the left edge and 45px from the right; the headline is left-aligned and the trades are centred.

## For next time
- The folded tape (art/build.py, scene 3) is the picture to build on: rows there and back, the back of every other row carrying one word, placed by its distance along the tape (print.py, BACKS). It scored 7.5 and the motion (words one way, numerals the other) is cheap.
- Give the tens the same size as the other numerals, or leave a gap. Reviewers read "2930" as a collision.
- A last scene that holds still is called basic even with the product and the wordmark in it. Keep the tape moving to the end: draw the brass end in from the right and stop it on the type margin.
- A tape that leaves the frame always cuts a numeral. Let it leave between two numerals (blank the print for a centimetre at the edge) or turn inside the frame.
- A tape on its edge is quick: 10 seconds a draft, under 4 minutes for a 1134x2016 frame at 110 samples, 1.5 minutes for an in-between at 40. Two rounds of 25 frames took about 95 minutes in all.
- Tools: python3.13 for bpy; the pip playwright there needs executable_path pointing at /opt/pw-browsers/chromium-*/chrome-linux*/chrome.
