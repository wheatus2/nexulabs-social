# Not published: held at the design review (12 Nov 2026, 08:33 slot)

This carousel was made by the 08:33 scheduled run and **was not posted**. It did not reach the 8 out of 10 needed from the independent design review, in two rounds, so the slot was left empty as DESIGN.md says.

It is kept here, outside `posts/`, so nothing publishes it by accident. It is not in `queue.json` and not in `design-log.json`.

## What it is
- Topic: web design, text that is too faint to read (colour contrast), with a one-minute check.
- Idea: contrast as the picture. Plum and blush, the faint words measured the way a designer would measure them.
- Typeface: Instrument Serif with Geist. Accent #FF4D8D.
- Facts: checked and passed (see `sources.md`). WebAIM Million 2026 (83.9% of the top million home pages have low-contrast text), W3C WCAG 2.2 (4.5:1 for body text, 3:1 for large text), W3C on sunlight and glare, WebAIM's contrast checker.
- `python3 studio.py check` passed.

## Design review
- Round 1: 6.5 out of 10. Weakest: frame 4 (a dark tilted phone that did not read as daylight). Frames 2 and 5 called partly generic.
- Round 2, after rebuilding frame 4 and reworking 1, 2, 3 and 5: 7 out of 10. Frames 1, 3 and 5 scored 7.5 to 8 and were not called template-like. Frames 2 and 4 were.

## What the reviewer said would lift it
1. Frame 4: the phone is a flat vector mockup with stock glare stripes and a slab shadow, and the left half is empty. It needs a far more refined device, one shadow style, and the left column filled or restructured.
2. Frame 2: the 10 by 10 grid is a standard waffle chart, and the eye goes to the 16 dark pages, which are the ones that pass. Make the 84 faint pages the subject, and give the caption room.
3. A kerning and word-spacing pass on the serif headlines and big numerals ("Take your" is too tight).
4. Near-miss alignments: frame 1 (selection box against the card), frame 5 (badge insets, the slider line poking above the card).

To finish it: fix the above in `art/`, move the folder back to `posts/` under a new slot name, render, run `studio.py check`, and put it through the design review again before publishing.
