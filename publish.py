#!/usr/bin/env python3
"""Publish a Nexulabs post straight to Instagram and the Facebook Page via Meta's Graph API.

Runs inside GitHub Actions (.github/workflows/publish.yml), so no Zapier tasks are used.
Standard library only. The token comes from the META_PAGE_TOKEN secret and is never printed.

Usage:
  python3 publish.py check
  python3 publish.py post  posts/<id>  [--platforms instagram,facebook] [--force]
  python3 publish.py story posts/stories/<id>  [--force]
  python3 publish.py comments [--days 7]
  python3 publish.py insights [--month YYYY-MM]

post   folder with reel.mp4      -> Instagram Reel + Facebook Page video
       folder with slide-NN.jpg  -> Instagram single image or carousel + Facebook Page photo post
story  folder with slide-NN.jpg  -> one Instagram Story per frame, in order (Instagram only)
comments  read-only: prints recent Instagram and Facebook Page comments as JSON between
          ===COMMENTS-JSON=== markers, for the daily comments summary. Never replies or changes anything.
insights  read-only: last calendar month's Instagram account + per-post insights and Facebook Page
          stats (or --month YYYY-MM), saved to reports/data/<YYYY-MM>-insights.json for the monthly review.

Writes <folder>/published.json with media ids, permalinks and any errors. Already-published
platforms are skipped unless --force, so a re-run never double-posts.
Exit code 0 = everything requested succeeded; 1 = Instagram (or check) failed; 2 = only Facebook failed.
"""
import argparse, datetime, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

GRAPH = "https://graph.facebook.com/" + os.environ.get("GRAPH_VERSION", "v21.0")
IG_USER = os.environ.get("IG_USER_ID", "17841471856846758")   # Nexulabs Instagram
FB_PAGE = os.environ.get("FB_PAGE_ID", "1484176674771345")    # Nexulabs Facebook Page
REPO = os.environ.get("GITHUB_REPOSITORY", "wheatus2/nexulabs-social")
REF = os.environ.get("RAW_REF") or os.environ.get("GITHUB_SHA") or "main"


class GraphError(Exception):
    pass


def token():
    t = os.environ.get("META_PAGE_TOKEN", "").strip()
    if not t:
        raise GraphError("META_PAGE_TOKEN secret is not set. See SETUP-META.md.")
    return t


def call(method, path, params=None, timeout=120):
    params = dict(params or {})
    params["access_token"] = token()
    url = f"{GRAPH}/{path.lstrip('/')}"
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err = json.loads(body).get("error", {})
            msg = f"{err.get('type','')} {err.get('code','')}/{err.get('error_subcode','')}: {err.get('message','')}"
        except Exception:
            msg = body[:500]
        raise GraphError(f"{method} {path.split('?')[0]} -> HTTP {e.code} {msg}") from None
    except urllib.error.URLError as e:
        raise GraphError(f"{method} {path.split('?')[0]} -> network error {e.reason}") from None


def raw(folder, name):
    return f"https://raw.githubusercontent.com/{REPO}/{REF}/{folder.as_posix()}/{name}"


def check_url(url):
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            if r.status != 200:
                raise GraphError(f"media URL returned {r.status}: {url}")
    except urllib.error.HTTPError as e:
        raise GraphError(f"media URL returned {e.code}: {url} (is it committed and pushed?)") from None


def wait_ready(container, max_wait=900):
    """Poll an Instagram media container until it is FINISHED."""
    waited, delay = 0, 5
    while waited <= max_wait:
        st = call("GET", container, {"fields": "status_code,status"})
        code = st.get("status_code")
        if code in ("FINISHED", "PUBLISHED"):
            return
        if code in ("ERROR", "EXPIRED"):
            raise GraphError(f"container {container} {code}: {st.get('status','')}")
        time.sleep(delay)
        waited += delay
        delay = min(delay + 5, 20)
    raise GraphError(f"container {container} not ready after {max_wait}s")


def ig_publish(container):
    wait_ready(container)
    media_id = None
    for attempt in range(3):
        try:
            media_id = call("POST", f"{IG_USER}/media_publish", {"creation_id": container})["id"]
            break
        except GraphError as e:
            if attempt == 2:
                raise
            time.sleep(15)
            # Never double-post: if the container was published despite the error, stop here.
            st = call("GET", container, {"fields": "status_code"}).get("status_code")
            if st == "PUBLISHED":
                raise GraphError(f"container {container} was published but Meta returned an error ({e}); check the account before re-running")
            print(f"media_publish retry after: {e}", flush=True)
    link = None
    try:
        link = call("GET", media_id, {"fields": "permalink"}).get("permalink")
    except GraphError as e:
        print(f"permalink lookup failed: {e}", flush=True)
    return {"media_id": media_id, "permalink": link}


def slides(folder):
    return sorted(p.name for p in folder.glob("slide-[0-9][0-9].jpg"))


def caption(folder):
    p = folder / "caption.txt"
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


# ---------- Instagram ----------
def instagram_post(folder):
    cap = caption(folder)
    if (folder / "reel.mp4").exists():
        video = raw(folder, "reel.mp4")
        check_url(video)
        params = {"media_type": "REELS", "video_url": video, "caption": cap, "share_to_feed": "true"}
        if (folder / "cover.jpg").exists():
            params["cover_url"] = raw(folder, "cover.jpg")
        c = call("POST", f"{IG_USER}/media", params, timeout=300)["id"]
        return {"format": "reel", **ig_publish(c)}
    imgs = slides(folder)
    if not imgs:
        raise GraphError("no reel.mp4 or slide-NN.jpg in folder")
    if len(imgs) > 10:
        raise GraphError(f"{len(imgs)} slides; Instagram carousels take at most 10")
    urls = [raw(folder, n) for n in imgs]
    for u in urls:
        check_url(u)
    if len(urls) == 1:
        c = call("POST", f"{IG_USER}/media", {"image_url": urls[0], "caption": cap})["id"]
        return {"format": "single", **ig_publish(c)}
    children = []
    for u in urls:
        ch = call("POST", f"{IG_USER}/media", {"image_url": u, "is_carousel_item": "true"})["id"]
        wait_ready(ch, max_wait=300)
        children.append(ch)
    c = call("POST", f"{IG_USER}/media", {"media_type": "CAROUSEL", "children": ",".join(children), "caption": cap})["id"]
    return {"format": "carousel", "slides": len(urls), **ig_publish(c)}


def instagram_story(folder, done=None, on_frame=None):
    """Publish frames in order. `done` lists frames already published by an earlier run (skipped)."""
    imgs = slides(folder)
    if not imgs:
        raise GraphError("no slide-NN.jpg frames in folder")
    out = list(done or [])
    have = {f["frame"] for f in out}
    for n in imgs:
        if n in have:
            print(f"story frame {n} already published, skipping", flush=True)
            continue
        u = raw(folder, n)
        check_url(u)
        c = call("POST", f"{IG_USER}/media", {"media_type": "STORIES", "image_url": u})["id"]
        r = ig_publish(c)
        out.append({"frame": n, "media_id": r["media_id"]})
        if on_frame:
            on_frame(out)
        print(f"story frame {n} -> {r['media_id']}", flush=True)
    return {"format": "story", "frames": out, "media_ids": [f["media_id"] for f in out]}


# ---------- Facebook Page ----------
def facebook_post(folder):
    cap = caption(folder)
    if (folder / "reel.mp4").exists():
        r = call("POST", f"{FB_PAGE}/videos", {"file_url": raw(folder, "reel.mp4"), "description": cap}, timeout=600)
        return {"format": "video", "id": r.get("id")}
    urls = [raw(folder, n) for n in slides(folder)]
    if not urls:
        raise GraphError("no reel.mp4 or slide-NN.jpg in folder")
    if len(urls) == 1:
        r = call("POST", f"{FB_PAGE}/photos", {"url": urls[0], "caption": cap, "published": "true"})
        return {"format": "photo", "id": r.get("post_id") or r.get("id")}
    ids = [call("POST", f"{FB_PAGE}/photos", {"url": u, "published": "false"})["id"] for u in urls]
    params = {"message": cap}
    for i, pid in enumerate(ids):
        params[f"attached_media[{i}]"] = json.dumps({"media_fbid": pid})
    r = call("POST", f"{FB_PAGE}/feed", params)
    return {"format": "photos", "photos": len(ids), "id": r.get("id")}


def check():
    page = call("GET", FB_PAGE, {"fields": "name,instagram_business_account"})
    ig = call("GET", IG_USER, {"fields": "username,name"})
    out = {"facebook_page": page.get("name"), "page_linked_ig": (page.get("instagram_business_account") or {}).get("id"),
           "instagram": ig.get("username")}
    try:
        lim = call("GET", f"{IG_USER}/content_publishing_limit", {"fields": "quota_usage,config"})
        out["publishing_limit"] = (lim.get("data") or [{}])[0]
    except GraphError as e:
        out["publishing_limit_error"] = str(e)
    return out


def comments(days=7):
    """Read-only. Recent comments on Nexulabs' Instagram posts and Facebook Page posts."""
    since = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
    out = {"since": since.isoformat(timespec="seconds"), "instagram": [], "facebook": [], "errors": {}}
    try:
        media = call("GET", f"{IG_USER}/media", {"fields": "id,caption,permalink,timestamp,comments_count", "limit": 30})
        for m in media.get("data", []):
            if not m.get("comments_count"):
                continue
            cs = call("GET", f"{m['id']}/comments",
                      {"fields": "id,text,username,timestamp,replies{text,username}", "limit": 50})
            out["instagram"].append({"media": m["id"], "permalink": m.get("permalink"),
                                     "caption": (m.get("caption") or "")[:120], "timestamp": m.get("timestamp"),
                                     "comments": cs.get("data", [])})
    except GraphError as e:
        out["errors"]["instagram"] = str(e)
    try:
        posts = call("GET", f"{FB_PAGE}/posts", {
            "fields": "id,message,permalink_url,created_time,"
                      "comments.limit(50){id,message,from,created_time,comments{message,from}}",
            "since": int(since.timestamp()), "limit": 50})
        for po in posts.get("data", []):
            cs = (po.get("comments") or {}).get("data", [])
            if cs:
                out["facebook"].append({"post": po["id"], "permalink": po.get("permalink_url"),
                                        "message": (po.get("message") or "")[:120],
                                        "created_time": po.get("created_time"), "comments": cs})
    except GraphError as e:
        out["errors"]["facebook"] = str(e)
    return out


def _month_range(month):
    today = datetime.date.today()
    if month:
        y, m = (int(x) for x in month.split("-"))
    else:
        y, m = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
    start = datetime.datetime(y, m, 1, tzinfo=datetime.timezone.utc)
    end = datetime.datetime(y + (m == 12), m % 12 + 1, 1, tzinfo=datetime.timezone.utc)
    return f"{y:04d}-{m:02d}", start, end


def _metrics(path, metrics, extra=None):
    """Ask for all metrics at once; if that errors, one by one so one bad metric doesn't lose the rest."""
    vals, errs = {}, {}
    def grab(names):
        r = call("GET", path, {"metric": ",".join(names), **(extra or {})})
        for d in r.get("data", []):
            if "total_value" in d:
                vals[d["name"]] = d["total_value"].get("value")
            elif d.get("values"):
                v = d["values"]
                vals[d["name"]] = v[-1].get("value") if len(v) == 1 else [{"end_time": x.get("end_time"), "value": x.get("value")} for x in v]
    try:
        grab(metrics)
    except GraphError:
        for m in metrics:
            try:
                grab([m])
            except GraphError as e:
                errs[m] = str(e)
    return vals, errs


def insights(month=None):
    """Read-only. Monthly numbers for the review."""
    label, start, end = _month_range(month)
    since = int(start.timestamp())
    until = min(int(end.timestamp()), int(time.time()) - 60)  # never ask for the future
    out = {"month": label, "fetched": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "instagram": {"account": {}, "posts": []}, "facebook": {}, "errors": {}}
    ig = out["instagram"]
    try:
        ig["account"].update(call("GET", IG_USER, {"fields": "username,followers_count,follows_count,media_count"}))
        # Meta allows at most 30 days per request, so a 31-day month is read in two halves.
        mid = since + 15 * 86400 if until - since > 30 * 86400 else until
        windows, all_errs = [], {}
        for a, b in [(since, mid), (mid, until)] if mid < until else [(since, until)]:
            vals, errs = _metrics(f"{IG_USER}/insights",
                                  ["reach", "views", "profile_views", "website_clicks", "accounts_engaged",
                                   "total_interactions", "likes", "comments", "shares", "saves"],
                                  {"period": "day", "metric_type": "total_value", "since": a, "until": b})
            windows.append({"since": datetime.datetime.fromtimestamp(a, datetime.timezone.utc).date().isoformat(),
                            "until": datetime.datetime.fromtimestamp(b, datetime.timezone.utc).date().isoformat(),
                            **vals})
            all_errs.update(errs)
        additive = ["views", "profile_views", "website_clicks", "total_interactions", "likes", "comments", "shares", "saves"]
        totals = {k: sum(w[k] for w in windows if isinstance(w.get(k), (int, float))) for k in additive
                  if any(isinstance(w.get(k), (int, float)) for w in windows)}
        ig["account"]["month_totals"] = totals
        ig["account"]["windows"] = windows
        ig["account"]["note"] = ("reach and accounts_engaged are unique counts per window; with two windows "
                                 "don't add them, quote them per half-month") if len(windows) > 1 else ""
        if all_errs:
            out["errors"]["instagram_account_metrics"] = all_errs
        try:  # daily follower gains; Meta only serves the last 30 days
            v, e = _metrics(f"{IG_USER}/insights", ["follower_count"], {"period": "day", "since": since, "until": until})
            if v:
                ig["account"]["follower_count_daily"] = v.get("follower_count")
        except GraphError:
            pass
    except GraphError as e:
        out["errors"]["instagram_account"] = str(e)
    try:
        nxt, params = f"{IG_USER}/media", {"fields": "id,caption,media_type,media_product_type,permalink,timestamp,like_count,comments_count", "limit": 50}
        done = False
        while nxt and not done:
            r = call("GET", nxt, params)
            for m in r.get("data", []):
                ts = datetime.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
                if ts >= end:
                    continue
                if ts < start:
                    done = True
                    break
                base = ["reach", "views", "saved", "shares", "likes", "comments", "total_interactions"]
                if m.get("media_product_type") == "REELS":
                    base += ["ig_reels_avg_watch_time", "ig_reels_video_view_total_time"]
                vals, errs = _metrics(f"{m['id']}/insights", base)
                ig["posts"].append({"media_id": m["id"], "type": m.get("media_product_type") or m.get("media_type"),
                                    "media_type": m.get("media_type"), "permalink": m.get("permalink"),
                                    "timestamp": m["timestamp"], "caption": (m.get("caption") or "")[:100],
                                    "insights": vals, **({"insight_errors": errs} if errs else {})})
            nxt = (r.get("paging") or {}).get("next")
            if nxt:  # the next URL already has every parameter; strip host + token, keep the rest
                u = urllib.parse.urlparse(nxt)
                q = dict(urllib.parse.parse_qsl(u.query)); q.pop("access_token", None)
                nxt, params = u.path.split("/", 2)[-1], q
    except GraphError as e:
        out["errors"]["instagram_posts"] = str(e)
    try:
        out["facebook"]["page"] = call("GET", FB_PAGE, {"fields": "name,followers_count,fan_count"})
        vals, errs = _metrics(f"{FB_PAGE}/insights",
                              ["page_impressions_unique", "page_post_engagements", "page_views_total",
                               "page_follows", "page_daily_follows_unique", "page_media_view"],
                              {"period": "day", "since": since, "until": until})
        out["facebook"]["insights_daily"] = vals
        out["facebook"]["month_totals"] = {k: sum(x["value"] for x in v if isinstance(x.get("value"), (int, float)))
                                           for k, v in vals.items() if isinstance(v, list)}
        if errs:
            out["errors"]["facebook_insights"] = errs
    except GraphError as e:
        out["errors"]["facebook"] = str(e)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["check", "post", "story", "comments", "insights"])
    ap.add_argument("folder", nargs="?")
    ap.add_argument("--platforms", default="instagram,facebook")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--month", default="")
    a = ap.parse_args()

    if a.mode == "insights":
        if a.month and not (len(a.month) == 7 and a.month[4] == "-" and a.month.replace("-", "").isdigit()):
            print(f"bad month: {a.month} (use YYYY-MM)")
            return 1
        try:
            token()
        except GraphError as e:
            print(json.dumps({"ok": False, "error": str(e)}))
            return 1
        res = insights(a.month or None)
        path = Path("reports/data") / f"{res['month']}-insights.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
        print(json.dumps({"saved": str(path), "posts": len(res["instagram"]["posts"]), "errors": res["errors"]}, indent=1))
        return 1 if "instagram_account" in res["errors"] and "instagram_posts" in res["errors"] else 0

    if a.mode == "comments":
        try:
            token()
        except GraphError as e:
            print(json.dumps({"ok": False, "error": str(e)}))
            return 1
        res = comments(a.days)
        print("===COMMENTS-JSON===")
        print(json.dumps(res, ensure_ascii=False))
        print("===END-COMMENTS-JSON===", flush=True)
        return 1 if len(res["errors"]) == 2 else 0

    if a.mode == "check":
        try:
            print(json.dumps({"ok": True, **check()}, indent=1))
            return 0
        except GraphError as e:
            print(json.dumps({"ok": False, "error": str(e)}, indent=1))
            return 1

    if not a.folder:
        ap.error("folder is required for post/story")
    folder = Path(a.folder.strip().rstrip("/"))
    if folder.is_absolute() or ".." in folder.parts or not folder.is_dir() or folder.parts[0] != "posts":
        print(f"bad folder: {a.folder}")
        return 1
    rec_path = folder / "published.json"
    rec = json.loads(rec_path.read_text()) if rec_path.exists() else {}
    plats = ["instagram"] if a.mode == "story" else [p.strip() for p in a.platforms.split(",") if p.strip()]
    now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    failed = []
    for p in plats:
        if rec.get(p, {}).get("ok") and not a.force:
            print(f"{p}: already published ({rec[p].get('media_id') or rec[p].get('id')}), skipping")
            continue
        try:
            if p == "instagram" and a.mode == "story":
                prev = [] if a.force else rec.get(p, {}).get("frames", [])
                def save_partial(frames):
                    rec[p] = {"ok": False, "at": now(), "partial": True, "frames": list(frames)}
                    rec_path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
                res = instagram_story(folder, prev, save_partial)
            elif p == "instagram":
                res = instagram_post(folder)
            elif p == "facebook":
                res = facebook_post(folder)
            else:
                raise GraphError(f"unknown platform {p}")
            rec[p] = {"ok": True, "at": now(), **res}
        except GraphError as e:
            keep = {"frames": rec[p]["frames"]} if rec.get(p, {}).get("frames") else {}
            rec[p] = {"ok": False, "at": now(), "error": str(e), **keep}
            failed.append(p)
        print(f"{p}: {json.dumps(rec[p])}", flush=True)
        rec_path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    if "instagram" in failed:
        return 1
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
