# Sources: 2026-11-09-1933-short-contact-form (Reel, web design: contact forms)

Checked 9 Nov 2026. Evergreen best-practice post; no statistics.

| # | Claim (slides / caption) | Source | Excerpt (verbatim) | Source date |
|---|---|---|---|---|
| 1 | Don't ask for data you don't need; cut unnecessary boxes ("Cut it back", caption "Google's web.dev guide to address and payment forms is blunt: don't ask for data you don't need") | https://web.dev/articles/payment-and-address-form-best-practices (web.dev is Google's web developer site) | "Don't ask for data you don't need!" / "The simplest way to reduce form complexity is to remove unnecessary fields." (section "Only ask for the data you need") | Last updated 22 Oct 2026 |
| 2 | Put a visible label above each box; grey hint (placeholder) text vanishes once you type | https://web.dev/articles/payment-and-address-form-best-practices | "Don't use placeholders on their own instead of labels." "Once you start entering text in an input, the placeholder is hidden, so it can be easy to forget what the input is for." | Last updated 22 Oct 2026 |
| 2b | Same point, UK government design guidance | https://design-system.service.gov.uk/components/text-input/ | "Do not use placeholder text in place of a label, or for hints or examples, as:" ... it "vanishes when the user starts typing". Also: "You should align labels above the text input they refer to." (source for "labels above the boxes") | GOV.UK Design System, changelog to Jun 2026 |
| 3 | A proper phone field (type="tel") opens the number keypad on a phone | https://web.dev/articles/payment-and-address-form-best-practices | "For telephone numbers, use type="tel" to get the appropriate keyboard on mobile." | Last updated 22 Oct 2026 |
| 4 | Switch autocomplete on so the browser can fill in details | https://design-system.service.gov.uk/components/text-input/ | "Use the autocomplete attribute on text inputs to help users complete forms more quickly." | GOV.UK Design System, changelog to Jun 2026 |
| 4b | Same point (autofill of name) | https://web.dev/articles/payment-and-address-form-best-practices | Section "Enable name autofill": "Use name for a full name:" autocomplete="name" | Last updated 22 Oct 2026 |

Not factual claims (advice/opinion, labelled): "Ten boxes before they can say hello" (illustrative example, not a statistic); "Three quick fixes"; the self-test steps; the phone form is an example screen for a made-up business (Example Plumbing Co., 0191 498 0000 from Ofcom's drama/fiction range).

Fact-check round 1 (independent subagent): fixed made-up business name (was a real NE trader's name), "Most" -> "Plenty of", web.dev page described as address and payment forms guide, "Three quick fixes", labels-above sourced to GOV.UK, exact web.dev placeholder quote.
Fact-check round 2: PASS (applied optional tweak: 'The browser can fill in saved details.')
