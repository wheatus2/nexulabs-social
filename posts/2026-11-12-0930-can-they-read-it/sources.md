# Sources

Post: 2026-11-12-0930-can-they-read-it (carousel, 3 frames). All five pages were opened again on 12 Nov 2026 in this run, each after a web search returned its URL.

## 1. Low-contrast text is the most common accessibility fault found on home pages; 83.9% of home pages have it
- Used on: frame 1 ("Faint text on home pages. The most common accessibility fault."), frame 2 ("83.9% of home pages have text with low contrast.", "WebAIM Million, February 2026. The world's top million home pages."), caption.
- Source: WebAIM, "The WebAIM Million: The 2026 report on the accessibility of the top 1,000,000 home pages". https://webaim.org/projects/million/
- As the source states it: "Low contrast text, below the WCAG 2 AA thresholds, was found on 83.9% of home pages, an increase from 79.1% in 2025. This was the most commonly-detected accessibility issue." The table "Percentage of pages with most common errors" lists "Low contrast text | 83.9%". "Results below are from February 2026".
- Date: analysis February 2026; page footer "Last updated: Mar 30, 2026". Checked 12 Nov 2026.
- Scope: global, not UK-only. "The million home page list was derived from the Tranco ranking". Automated testing: "The evaluation was conducted using the WAVE stand-alone API". The caption says "the world's top million home pages".
- Checked for anything newer: WebAIM's "Million Update" page (https://webaim.org/projects/million/update) is an August 2019 re-analysis, so February 2026 is the latest figure.
- Note on frame 2: the last row, "low contrast.", is set at 1.5:1, which is below the WCAG AA thresholds for both body text and large text, so it is itself low-contrast text.

## 2. Body text needs a contrast of at least 4.5:1; large text can be 3:1
- Used on: frame 3 ("Body text needs at least 4.5:1."), caption (the 4.5 to 1 figure). The 3:1 figure for large text is not used in the post.
- Source: W3C WAI, "Understanding Success Criterion 1.4.3: Contrast (Minimum)" (WCAG 2.2, Level AA). https://w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- As the source states it: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1, except for the following:" "Large-scale text and images of large-scale text have a contrast ratio of at least 3:1". Large scale means "at least 18 point or 14 point bold".
- Date: "Updated 04 October 2026". Checked 12 Nov 2026.

## 3. The contrast ratios shown on the frames
- Used on:
  - frame 1: the tag "1.5:1" (with a cross) for text #4A3045 on background #2B0F26.
  - frame 2 (rows on #F6C8D8, labelled 1 to 4): #2B0F26 11.8:1, #745266 4.5:1, #B38A9D 2:1, #CDA2B4 1.5:1.
  - frame 3: the tag "15.5:1" (with a tick) for text #2B0F26 on background #FBEEF2.
- How: worked out in this run with the WCAG formula from the same W3C page, "(L1 + 0.05) / (L2 + 0.05)", using the relative luminance of each colour. Results: 1.50; 11.82, 4.51, 2.01, 1.50; 15.52.
- These are our own colours, measured. They can be checked by typing the two hex codes into WebAIM's contrast checker.

## 4. Good contrast keeps a page readable in sunlight and glare
- Used on: caption ("Take your phone outside and open your website. If the words wash out in daylight, make them darker.").
- Source: W3C WAI, "Colors with Good Contrast" (Web Accessibility Perspectives). https://www.w3.org/WAI/perspective-videos/contrast
- As the source states it: "Content works in different lighting conditions, such as sunlight and glare." The video description: "Sun glares on the phone but the text is still readable."
- Date: page footer "Updated: 15 July 2024". Checked 12 Nov 2026.
- The daylight test itself is our suggestion, not a W3C procedure.

## 5. WebAIM's contrast checker is free and gives the ratio for two colours
- Used on: caption only ("WebAIM's contrast checker is free and gives you the ratio for any two colours.").
- Source: WebAIM, "Contrast Checker". https://webaim.org/resources/contrastchecker/
- As the source shows it: inputs for a foreground colour and a background colour; it returns a contrast ratio and pass or fail for WCAG AA and AAA. "WCAG 2.0 level AA requires a contrast ratio of at least 4.5:1 for normal text and 3:1 for large text." No charge, sign-up or login is shown on the page.
- Date: no date on the page (©2026 WebAIM). Checked 12 Nov 2026.
