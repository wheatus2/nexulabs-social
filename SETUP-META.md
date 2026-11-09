# Posting without Zapier: one-off Meta setup

Publishing now runs through GitHub Actions (`.github/workflows/publish.yml` + `publish.py`), which talks to Meta's Graph API directly. It's free and doesn't use Zapier tasks. It needs one thing: a **Page access token** saved as a GitHub secret called `META_PAGE_TOKEN`.

The token is a password. Never paste it into a file, a commit, a chat or a post. It only goes into GitHub's secret box (step 6). This repo is public.

## Steps (about 20–30 minutes, signed in to Facebook as the Nexulabs Page admin)

1. **Create a Meta app.** Go to https://developers.facebook.com/apps and click **Create app**. Name: `Nexulabs Publisher`. Contact email: yours. When asked for a use case, choose **Other**, then app type **Business**. (Meta changes these screens often; anything that ends in a Business-type app is fine.) Link it to the Nexulabs business portfolio if asked. Leave the app in **Development** mode: that's fine for posting to your own accounts.
2. **Open the Graph API Explorer**: https://developers.facebook.com/tools/explorer/
   - **Meta App**: `Nexulabs Publisher`.
   - **User or Page**: `Get User Access Token`.
   - **Permissions**: add `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`, `business_management`, plus `instagram_manage_comments` and `pages_read_user_content` so the daily comments summary can read comments.
   - Click **Generate Access Token**. In the pop-up, choose the **Nexulabs** Page and the **Nexulabs Instagram** account and allow everything listed.
3. **Make it long-lived.** Click the blue **i** next to the token, then **Open in Access Token Tool**. At the bottom, click **Extend Access Token** and copy the new (long-lived) user token.
4. **Get the Page token.** Back in the Explorer, paste the long-lived token into the Access Token box, then run `GET me/accounts`. Find the entry with id `1484176674771345` (Nexulabs) and copy its `access_token`.
5. **Check it never expires.** Paste that Page token into https://developers.facebook.com/tools/debug/accesstoken/ and click **Debug**. It should say **Expires: Never** and list the permissions from step 2. If it shows an expiry date, repeat steps 3–4.
6. **Save it in GitHub.** Go to https://github.com/wheatus2/nexulabs-social/settings/secrets/actions → **New repository secret**. Name: `META_PAGE_TOKEN`. Secret: the Page token. **Add secret**.
7. **Test it.** Go to https://github.com/wheatus2/nexulabs-social/actions/workflows/publish.yml → **Run workflow** → mode `check` → **Run workflow**. Open the run: the Publish step should print `"ok": true`, the Page name and the Instagram username. (Or just tell Claude "the token's in" and it'll run the check.)

## If something goes wrong later
- **Error 190 / "session has been invalidated"**: the token stopped working (password change, removed admin, or permissions revoked). Redo steps 2–6.
- **Error 10 / 200 permissions**: a permission from step 2 is missing; redo steps 2–6 with all of them ticked.
- **Instagram account not found**: in step 2, make sure the Instagram account was ticked in the pop-up, and that it's a Business account linked to the Nexulabs Page.

## How the scheduled runs use it
Claude commits the post, then starts the workflow with `mode: post` (or `story`) and the post folder. The workflow posts to Instagram (and the Facebook Page for feed posts), then saves `published.json` in the post folder with the media ids and permalink. A post that's already in `published.json` is never posted twice unless `force` is ticked. Until the secret exists, the runs fall back to Zapier.
