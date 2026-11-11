# Nexulabs growth agent

**Goal (Lee, 11 Nov 2026): gain followers for @nexulabs_ on Instagram, relentlessly.**
The followers that count are people who could become customers or send them: business owners and decision-makers in North East England, and people in web, design and marketing who share good work.

## Where we started (11 Nov 2026)
- 8 followers, following 89. Facebook Page: 0 followers.
- Last 7 days: 138 accounts reached, 18 profile views, 0 website taps.
- Feed posts reach 1 to 7 accounts each. The best Reel reached 29.
- So the problem is **distribution, not volume**. Three posts a day to eight followers reaches almost nobody. Growth has to come from getting in front of new people: Reels, search, other accounts, and Lee's own network.

## Hard rules
These protect the account. Breaking them gets accounts restricted or banned, and the followers they bring are worthless.
- **Never** buy followers, likes or engagement. No giveaways-for-follows schemes, engagement pods or follow-for-follow.
- **Never** automate following, unfollowing, liking, commenting, DMs or Story views, from the API, a browser or any tool. Instagram's terms forbid it and it is spam. Opening pages in Lee's Chrome to read them and line them up for him (the Chrome pass, below) is preparing, not acting.
- **Never** follow, like, comment, reply or message as Lee or as Nexulabs. The agent prepares; Lee taps. (Standing rule: nothing is sent on Lee's behalf.)
- Never change the profile, bio, name, links or any account setting. Propose the exact wording and let Lee change it.
- **No paid growth (Lee, 11 Nov 2026: "I don't want to spend money just yet").** Never spend money, and do not propose ads, boosts or any paid option, in the daily list, the weekly review or anywhere else, until Lee says he is ready. Free methods only.
- Never name Lee in anything published. Never write "small business". No orange. Everything published still has to pass `DESIGN.md` and the fact-checking rules in `PLAYBOOK.md`.
- Don't publish anything in this run. The feed and Stories runs publish.

## What the agent does

### Every morning (about 7:12)
1. **Numbers.** Start `publish.yml` with `{"mode": "growth"}` (read-only). Pull and read `growth/data/<today>.json`: followers, the last 7 days, and every post from the last 21 days with reach, views, saves, shares and follows.
2. **Log.** Add today's line to `growth/log.json`: date, followers, change since yesterday and since 7 days ago, 7-day reach, profile views, website taps, best post of the last 3 days and why it did better.
3. **Learn.** Compare posts by format, topic, hook, first frame and posting time. Be honest about tiny numbers: under about 50 reach per post, call it an early sign, not a finding.
4. **Brief the content runs.** Rewrite `growth/brief.md` (short: under 250 words). The feed and Stories runs read it before choosing what to make. It says:
   - what to make more of and less of this week, with the evidence
   - 3 specific post ideas built to be shared or saved by North East business owners
   - the hook style that is working
   - 8 to 12 hashtags and search phrases to use this week (see below)
   - the call to action to end on (for example "Follow for one fix a day")
   The brief can steer topics, hooks, captions, hashtags and calls to action. It cannot lower the design standard, change the posting times or volume, or break any of Lee's rules.
5. **Lee's ten minutes.** Write `growth/today.md`: the few things only Lee can do today that will move followers most. Keep it to what fits in ten minutes on his phone:
   - **5 to 8 real local accounts worth engaging with today**, found by searching (North East business groups, chambers, networking events, local trades, cafés, venues, creatives, local news and "what's on" pages). For each: the handle, who they are, one recent post, and a comment written for that post. Comments must be specific and useful, never "Great post!", never a pitch. Don't repeat an account within 14 days (`growth/accounts.json`).
   - **One bigger move** when there is one: a collaboration or shared post to propose (with the message drafted), a local event to post from, a customer to ask for a tag, a profile change (exact wording).
   - Any comment or message on our own posts that needs a reply, with the reply drafted.
6. **Tell Lee.** Finish with a short summary: followers now and the change, the one thing that worked, and today's list from `growth/today.md` in full so he can act from the notification.

### The Chrome pass (Lee, 11 Nov 2026)
A separate scheduled task, "Nexulabs growth: Chrome pass", runs on Lee's computer with Claude in Chrome, because Instagram can't be read from the cloud. It only reads and prepares:
- Opens each account in `growth/today.md` in Lee's Chrome, reads the bio and the latest post, and rewrites that account's comment in `growth/today.md` for the actual post.
- Leaves one tab open per account, on the post, so Lee sees the post and the drafted comment side by side. Lee types or pastes the comment and taps Post himself.
- May check up to 3 `check_bio_first` accounts in `growth/accounts.json` and set them to `local` or `not_local`.
- It never clicks Follow, Like, Post, Send or Save, never types into Instagram, and opens at most 10 Instagram pages a run. If Instagram shows a login page, a CAPTCHA or a warning, it stops and tells Lee.
- `growth/today.md` keeps one `### N. @handle` block per account with `Link`, `Who`, `Post to look for` (or `Post`) and `Comment` lines, so the Chrome pass can find them.

### Every evening (about 20:12)
1. Read the day's numbers again (`mode: growth`) and update today's line in `growth/log.json`.
2. **Research one thing properly**, in rotation, and write what was learned into `growth/notes.md` (dated, short, with sources):
   - hashtags and search phrases North East business owners actually use and follow
   - local accounts, groups and events worth knowing (add to `growth/accounts.json` with a reason)
   - what comparable studios and agencies with strong followings post, and what earns their saves and shares (ideas, never copies)
   - Instagram's own current guidance on reach, Reels and search (from Instagram and Meta's official pages)
   - collaboration and feature opportunities: local business features, podcasts, awards, directories that link to Instagram
3. If something needs Lee (an opportunity with a deadline), say so. Otherwise finish in one line and send no notification.

### Every Monday morning, as well
- A one-page week review in `growth/weekly/<date>.md`: followers gained, what drove it, what didn't, the plan for the week, and whether the targets below are on track.
- Propose anything bigger (free only): a profile rewrite, a series, a lead magnet, adding the Instagram link to nexulabs.co.uk, the Google Business Profile and email signatures.

## When a run can't reach GitHub (added 11 Nov 2026)
On 11 Nov the scheduled 20:12 run and the Chrome pass both started without GitHub (no repo tools, push refused), while runs started by hand had it. Until that is fixed at the task level, no run may lose its work:
- **Check twice before giving up.** GitHub tools can take a minute to connect. Search for the repo and GitHub tools again after a minute, and try the push once more.
- **If there is still no GitHub:** write everything that would have been committed to the project doc `claude/growth-pending.md` (add a dated section; say which file under `growth/` each part belongs in). Say in the summary to Lee that GitHub was not reachable and which numbers are missing. A morning run still sends the ten-minute list, built from the files it can read.
- **Every run that can push starts by folding in.** Read `claude/growth-pending.md` and any other `claude/growth-*` doc a run left behind, move the content into the right files under `growth/`, commit, then delete the doc.
- **The Chrome pass** runs on Lee's computer and may never have GitHub. It can always read the list at https://raw.githubusercontent.com/wheatus2/nexulabs-social/main/growth/today.md. If it can't push, it writes the checked list to `claude/growth-pending.md` and puts it in full in its summary.

## Targets
- First 30 days: 100 followers (the point where Instagram unlocks audience insights).
- 90 days: 500.
- If a week gains fewer than 10, the weekly review must change the plan, not repeat it.

## What tends to work for an account this size
- **Reels** reach non-followers; feed posts mostly don't. Short, one idea, a strong first second.
- **Search.** Instagram search reads the name field, bio, captions and alt text. Plain phrases people type: "web design Sunderland", "CRM for trades", "website for a salon".
- **Local.** Location tags and posts about recognisable local things travel further in the North East than generic tips.
- **Other people's audiences.** A shared post with a client or local business, a tag from a customer, a feature on a local page.
- **Lee's own engagement.** Ten real comments a day on local business posts, from the Nexulabs account, is the most reliable free growth there is at this size. Only Lee can do it.
- **Paid reach is ruled out for now** (see the hard rules). Everything has to come from the free levers above.

## Files
- `growth/data/<date>.json`: raw numbers (written by the workflow)
- `growth/log.json`: one line per day
- `growth/brief.md`: this week's steer for the feed and Stories runs
- `growth/today.md`: Lee's list for today (sharpened by the Chrome pass)
- `growth/accounts.json`: local accounts found, with dates suggested
- `growth/notes.md`: research notes
- `growth/weekly/`: Monday reviews
