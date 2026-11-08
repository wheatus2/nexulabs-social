#!/usr/bin/env python3
"""Publish a Nexulabs post straight to Instagram and the Facebook Page via Meta's Graph API.

Runs inside GitHub Actions (.github/workflows/publish.yml), so no Zapier tasks are used.
Standard library only. The token comes from the META_PAGE_TOKEN secret and is never printed.

Usage:
  python3 publish.py check
  python3 publish.py post  posts/<id>  [--platforms instagram,facebook] [--force]
  python3 publish.py story posts/stories/<id>  [--force]

post   folder with reel.mp4      -> Instagram Reel + Facebook Page video
       folder with slide-NN.jpg  -> Instagram single image or carousel + Facebook Page photo post
story  folder with slide-NN.jpg  -> one Instagram Story per frame, in order (Instagram only)

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
            print(f"media_publish retry after: {e}", flush=True)
            time.sleep(15)
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


def instagram_story(folder):
    imgs = slides(folder)
    if not imgs:
        raise GraphError("no slide-NN.jpg frames in folder")
    out = []
    for n in imgs:
        u = raw(folder, n)
        check_url(u)
        c = call("POST", f"{IG_USER}/media", {"media_type": "STORIES", "image_url": u})["id"]
        r = ig_publish(c)
        out.append({"frame": n, "media_id": r["media_id"]})
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["check", "post", "story"])
    ap.add_argument("folder", nargs="?")
    ap.add_argument("--platforms", default="instagram,facebook")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

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
            if p == "instagram":
                res = instagram_story(folder) if a.mode == "story" else instagram_post(folder)
            elif p == "facebook":
                res = facebook_post(folder)
            else:
                raise GraphError(f"unknown platform {p}")
            rec[p] = {"ok": True, "at": now(), **res}
        except GraphError as e:
            rec[p] = {"ok": False, "at": now(), "error": str(e)}
            failed.append(p)
        print(f"{p}: {json.dumps(rec[p])}", flush=True)
        rec_path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    if "instagram" in failed:
        return 1
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
