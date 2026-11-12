# Not published: held at the design review (12 Nov 2026, morning slot)

This carousel **was not posted**. Two scheduled runs worked on it on the morning of 12 Nov (08:33 and about 09:00). Neither reached the 8 out of 10 needed from the independent design review within its two rounds, so the slot was left empty as DESIGN.md says.

It is kept here, outside `posts/`, so nothing publishes it by accident. It is not in `queue.json` and not in `design-log.json`, so the topic, palette and typeface are not used up.

## What it is
- Topic: web design, text that is too faint to read (colour contrast), with a one-minute check.
- Idea: contrast as the picture, in plum and blush. The cover asks "Can your customers read this?" with "read this?" set at 1.5:1 and measured; an eye-test chart fades away; the last frame answers with the same words at 15.5:1.
- Now 4 frames (was 5). Typeface: Instrument Serif with Geist. Accent #FF4D8D.
- Facts: all five sources were opened again in the 09:00 run and match `sources.md`. WebAIM Million 2026 (83.9% of the top million home pages have low-contrast text; 79.1% in 2025), W3C WCAG 2.2 (4.5:1 for body text, 3:1 for large text), W3C on sunlight and glare, WebAIM's contrast checker. The independent fact-check subagent was not run on this 4-frame version, because the design review failed first. Run it before publishing.
- `python3 studio.py check` passed (it was run while the folder was in `posts/`).

## Design review history
- 08:33 run, 5 frames: 6.5, then 7.
- 09:00 run, round 1, 5 frames (new eye-chart frame 2, new macro phone frame 4): 7. Frames 1 and 2 scored 8. Frame 4 (the phone) scored 5.5; the lower half of frame 3 and frame 5 were called template-like in parts.
- 09:00 run, round 2, 4 frames (phone and site-card frames dropped, frame 3 rebuilt as type only, new closing frame "read this." at 15.5:1): **7.5**. Frames 2 and 4 "could plausibly sit on a Google Design or Material account" and were not called template-like. Frame 3 was called the "stock stat-slide layout". Frame 1 "partly" (the inspector card is a familiar device).

## What the last reviewer said would lift it to 9
1. Frame 3 (4.5:1): it states the ratio and does not show it. Rebuild it so it shows the threshold, for example the same word set just below and just above 4.5:1. Also: even out the space each side of the colon, match the colon dots to the full stop, resolve the empty bottom-right, drop the glow.
2. Frame 1: too many elements. Strip it to the headline and the faint "read this?" with one small ratio tag; lose the inspector card or shrink it a lot. Move "Check yours in one minute." off the cover.
3. Frame 2: "of home pages" comes within about 35px of the "4.5:1" label; the footer line breaks badly ("Top million home / pages worldwide").
4. Frame 4: straight apostrophe in "WebAIM's"; box padding is uneven (about 41px top, 68 left, 60 right, 50 bottom); the ratio badge sits close under the box.
5. Across the set: one pill shape (frame 1 is a capsule, frame 4 a rounded rectangle), one caption emphasis style, the same logo size.

To finish it: fix the above in `art/`, move the folder back to `posts/` under a new slot name, render, run `studio.py check`, then the design review and the fact-check before publishing.
