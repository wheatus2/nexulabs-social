# Sources

Post: 2026-11-13-0925-missing-key (carousel, 3 frames; a new design of the held 08:33 post, same facts). Every page below was opened on 13 Nov 2026 in this run, each after a web search returned its URL.

## 1. Chrome labels a site "Not secure" when it doesn't use a private connection
- Used on: frame 2 ("Chrome calls that “Not secure”"), frame 1 ("Open your website in Chrome."), caption ("If the address starts http and the bar says "Not secure", the s is missing. Chrome's help page says that means the site doesn't use a private connection, and what's sent through it could be viewed or changed.").
- Source: Google Chrome Help, "Check if a site's connection is secure". https://support.google.com/chrome/answer/95617?hl=en-GB
- As the source states it: the security statuses listed are "Default (Secure)", "Info or Not secure" and "Not secure or Dangerous". Under "Info or Not secure": "The site doesn't use a private connection." "Someone may be able to view and change the information that you send and receive through this site."
- Date: no date on the page. Checked 13 Nov 2026.
- Care taken: Chrome can also show "Not secure" on an https address whose certificate is broken ("Not secure or Dangerous"). So the caption says "If the address starts http and the bar says "Not secure"", not that "Not secure" always means the s is missing.

## 2. Only the site owner can fix it, by moving the site to HTTPS
- Used on: frame 3 ("Ask your host for the s." "It’s called HTTPS"), caption ("Only the site owner can fix it. Ask whoever hosts your site to switch on HTTPS.").
- Source: the same Chrome Help page. https://support.google.com/chrome/answer/95617?hl=en-GB
- As the source states it: "To resolve this issue, the site owner must secure the site and your data with HTTPS."
- Date: no date on the page. Checked 13 Nov 2026.
- "Ask whoever hosts your site" is our suggestion for who to ask; the source only says the site owner must do it.

## 3. Chrome now asks for permission before opening a site without HTTPS, the first time someone visits it
- Used on: frame 2 ("Now it asks before opening your site." "Google, 21 October 2026."), caption ("Google said on 21 October that Chrome now also asks people for permission the first time they visit a site without HTTPS.").
- Source (primary): Google, "Chrome Now Warns Before Insecure HTTP Connections", Chrome's Secure Web and Networking Team, 21 Oct 2026. https://blog.google/security/chrome-now-warns-before-insecure-http-connections/
- As the source states it: "we have now rolled out a change where Chrome explicitly asks users for permission before making an insecure HTTP connection." "now we extended this protection to all users by default." "Chrome will ask the user to approve the use of HTTP the first time they visit the site." "Chrome will not warn again until the user has not visited the site for at least two weeks."
- Limits the source gives: "By default, warnings are also not shown on sites that cannot get a publicly-trusted HTTPS certificate" (for example local addresses such as 192.168.0.1). A business's public website is not one of those.
- Independent outlet: Help Net Security, 22 Oct 2026, reports the same: "The protection is now enabled by default for all users."
- Background (the plan, announced a year earlier): Google, "HTTPS by default", 28 Oct 2025, https://blog.google/security/https-by-defau/ ; Chrome Enterprise release notes, "Always use secure connections by default", https://support.google.com/chrome/a/answer/10314655?hl=en ("This means Chrome will ask for the user's permission before the first access to any public site without HTTPS.").
- Date: 21 Oct 2026. Checked 13 Nov 2026. Global, not UK-specific; the post does not say otherwise.

## 4. Let's Encrypt is a free certificate authority
- Used on: frame 3 ("It’s called HTTPS, and it can be free."), caption ("Let's Encrypt issues certificates free.").
- Source: Let's Encrypt, "About Let's Encrypt". https://www.letsencrypt.org/about/
- As the source states it: "Let’s Encrypt is a free, automated, and open Certificate Authority (CA), run for the public’s benefit. It is a service provided by the Internet Security Research Group (ISRG)."
- Date: page says "Last updated: February 12, 2021"; footer © 2026; live when checked 13 Nov 2026. No number is taken from it.
- "It can be free" means a free certificate exists. Whether a particular host charges for setting it up is not claimed.

## Not claims
- Frame 1's headline ("Is your web address missing a letter?") is a question. The keyboard is a drawing: keys spelling "http" with the next key missing is the picture of the idea, a web address that starts http has no s. It is not a real product.
- "A one-minute check." and "Send this to whoever runs your website." are our own suggestion and call to action.
- "Follow for one website fix a day." is the account's standing call to action from growth/brief.md (12 Nov 2026), a promise about our own posts, not an outside fact.
