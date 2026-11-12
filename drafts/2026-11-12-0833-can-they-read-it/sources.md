# Sources

Post: 2026-11-12-0833-can-they-read-it (carousel, 5 frames). All pages opened on 12 Nov 2026, after a web search returned the URL.

## 1. Low-contrast text is the most common accessibility fault found on home pages; 83.9% of home pages have it
- Used on: frame 1 ("Faint text is the most common accessibility fault found on home pages"), frame 2 ("83.9% of home pages have low-contrast text.", "WebAIM Million, February 2026", "Top million home pages worldwide"), caption.
- Source: WebAIM, "The WebAIM Million: The 2026 report on the accessibility of the top 1,000,000 home pages". https://webaim.org/projects/million/
- As the source states it: the table "Percentage of pages with most common errors" lists "Low contrast text: 83.9%" (79.1% in 2025). "This was the most commonly-detected accessibility issue." "Results below are from February 2026." "For the eighth consecutive year, WebAIM conducted an accessibility evaluation of the home pages for the top 1,000,000 web sites."
- Date: analysis February 2026; page last updated 30 March 2026. Checked 12 Nov 2026.
- Scope: global (the list comes from the Tranco ranking), automated testing with WebAIM's WAVE engine. Not UK-only; the caption says "the world's top million home pages".
- Note: the grid on frame 2 shows 100 pages, 84 faint and 16 dark, as a picture of 83.9%.

## 2. Body text needs a contrast of at least 4.5:1; large text can be 3:1
- Used on: frame 3 ("4.5:1. The minimum contrast for body text.", "Big headings can go as low as 3:1.", "W3C, WCAG 2.2"), caption (the 4.5 to 1 figure).
- Source: W3C WAI, "Understanding Success Criterion 1.4.3: Contrast (Minimum)" (WCAG 2.2, Level AA). https://w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- As the source states it: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1, except for the following:" "Large-scale text and images of large-scale text have a contrast ratio of at least 3:1;". Large scale means "at least 18 point or 14 point bold".
- Date: page updated 4 October 2026. Checked 12 Nov 2026.

## 3. The contrast ratios shown on the frames
- Used on: frame 1 (1.5:1 for text #4A3045 on background #2B0F26), frame 3 (six "Aa" samples on #FBEEF2: #D2C3CA 1.5, #B9A8B2 2, #9A8692 3, #7E6877 4.5, #624A5C 7, #2B0F26 15.5), frame 4 and frame 5 (2:1 for #B9A8B2 on #FBEEF2), frame 5 (15.5:1 for #2B0F26 on #FBEEF2).
- How: worked out in this run with the WCAG formula from the same W3C page, "(L1 + 0.05) / (L2 + 0.05)", using the relative luminance of each colour. Results: 1.50, 1.50, 2.00, 3.00, 4.50, 7.02, 15.52.
- These are our own colours, measured. They can be checked by typing the two hex codes into WebAIM's contrast checker.

## 4. Good contrast keeps a page readable in sunlight and glare
- Used on: frame 4 ("Take your phone outside. Open your website in daylight. If the words wash out, they're too faint."), caption.
- Source: W3C WAI, "Colors with Good Contrast" (Web Accessibility Perspectives). https://www.w3.org/WAI/perspective-videos/contrast
- As the source states it: "Content works in different lighting conditions, such as sunlight and glare." The video transcript: "Sun glares on the phone but the text is still readable."
- Date: page footer "Updated: 15 July 2024". Checked 12 Nov 2026.
- The daylight test itself is our suggestion, not a W3C procedure.

## 5. WebAIM's contrast checker is free and gives the ratio for two colours
- Used on: frame 5 ("Check any two colours free with WebAIM's contrast checker."), caption.
- Source: WebAIM, "Contrast Checker". https://webaim.org/resources/contrastchecker/
- As the source shows it: inputs for a foreground colour and a background colour; it returns a "Contrast Ratio" and pass or fail for WCAG AA and AAA. "WCAG 2.0 level AA requires a contrast ratio of at least 4.5:1 for normal text and 3:1 for large text." No charge or sign-up is shown on the page.
- Date: no date on the page (©2026 WebAIM). Checked 12 Nov 2026.

## Made up
- "Hartwell Kitchens", its website and its wording are invented for the example. The caption says so.
