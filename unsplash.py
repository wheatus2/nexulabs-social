#!/usr/bin/env python3
"""Find and download an Unsplash photo for a post.

Usage:
  python3 unsplash.py search "laptop desk minimal" [--n 8]      # list candidates (id, description, photographer, url)
  python3 unsplash.py get <photo_id> posts/<id>/photo.jpg        # download 1080x1350 crop + print credit line

Needs network access to api.unsplash.com and images.unsplash.com. The API key is added
automatically by the environment's network secret (header: Authorization: Client-ID <key>).
If UNSPLASH_ACCESS_KEY is set, it's used instead.

Unsplash API rules followed here: the download endpoint is triggered for every photo used,
and the photographer is credited ("Photo: <name> on Unsplash") in the caption.
"""
import json, os, sys, urllib.parse, urllib.request

API = "https://api.unsplash.com"


def _get(url, raw=False):
    req = urllib.request.Request(url, headers={"Accept-Version": "v1"})
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if key:
        req.add_header("Authorization", f"Client-ID {key}")
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    return data if raw else json.loads(data)


def search(query, n=8):
    q = urllib.parse.urlencode({"query": query, "per_page": n, "orientation": "portrait", "content_filter": "high"})
    res = _get(f"{API}/search/photos?{q}")
    for p in res.get("results", []):
        print(json.dumps({
            "id": p["id"],
            "description": p.get("alt_description") or p.get("description"),
            "photographer": p["user"]["name"],
            "preview": p["urls"]["small"],
        }))


def get(photo_id, dest):
    p = _get(f"{API}/photos/{photo_id}")
    _get(p["links"]["download_location"])  # required by Unsplash API guidelines
    url = p["urls"]["raw"] + "&" + urllib.parse.urlencode({"w": 2160, "h": 2700, "fit": "crop", "crop": "entropy", "fm": "jpg", "q": 85})
    with open(dest, "wb") as f:
        f.write(_get(url, raw=True))
    credit = f"Photo: {p['user']['name']} on Unsplash"
    print(json.dumps({"saved": dest, "credit": credit, "photographer_url": p["user"]["links"]["html"]}))


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 8
        search(sys.argv[2], n)
    elif len(sys.argv) == 4 and sys.argv[1] == "get":
        get(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(1)
