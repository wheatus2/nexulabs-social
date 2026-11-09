#!/usr/bin/env python3
"""Pick and prepare a photo from the photos/ library for a post. Photos are NEVER reused.

File names: <photographer-name>--<short-description>.<unsplash-id>.jpg
  e.g. jane-smith--laptop-on-desk.-8-2YWKt8Ag.jpg  (ids can contain - and _)

  python3 photo.py list [--topic <topic>]       # unused, cleared photos: credit, what it shows, what it may be used for
  python3 photo.py topics                       # how many unused photos per topic
      topics: web-design, crm, websites-crm, branding, ai-automation, hosting, domains,
              tech-news, business-types (trades, shops, hospitality...), north-east
  python3 photo.py prepare photos/<file> posts/<id>/photo.jpg [--focus 0.5,0.4]
      -> refuses if the photo was used before; crops to 4:5, 2160x2700; prints the credit
  python3 photo.py retire photos/<file>         # after publishing: move to photos/used/ and
                                                #   record the id in photos/used-ids.txt
  python3 photo.py check                        # fail if any library photo was used before

The no-reuse rule (Lee's rule): a photo id in photos/used-ids.txt, in photos/used/, or in
log.json can never be used again, even if the same photo is re-added to the library.
"""
import json, re, shutil, sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
LIB = ROOT / "photos"
USED_DIR = LIB / "used"
USED_IDS = LIB / "used-ids.txt"
EXT = {".jpg", ".jpeg", ".png", ".webp"}


def parts(path):
    """<photographer>--<description>.<unsplash-id>.jpg -> (photographer, description, id)"""
    stem = Path(str(path)).name
    stem = stem[: stem.rfind(".")] if "." in stem else stem      # drop extension
    if "." in stem:
        head, pid = stem.split(".", 1)
    else:
        head, pid = stem, stem
    bits = head.split("--", 1)
    photographer = bits[0]
    desc = bits[1].replace("-", " ") if len(bits) > 1 else ""
    return photographer, desc, pid


def credit_for(path):
    name = " ".join(w.capitalize() for w in re.split(r"[-_\s]+", parts(path)[0]) if w)
    return f"Photo: {name} on Unsplash"


def used_ids():
    ids = set()
    if USED_IDS.exists():
        ids |= {l.strip() for l in USED_IDS.read_text().splitlines() if l.strip()}
    if USED_DIR.exists():
        ids |= {parts(p)[2] for p in USED_DIR.iterdir() if p.suffix.lower() in EXT}
    log = ROOT / "log.json"
    if log.exists():
        for e in json.loads(log.read_text()):
            for k in ("photo", "photo_file", "photo_id", "unsplash_photo_id"):
                v = e.get(k)
                if v:
                    v = str(v)
                    ids.add(parts(v)[2] if v.lower().endswith(tuple(EXT)) else v)
    return ids


def library():
    return [p for p in sorted(LIB.iterdir()) if p.is_file() and p.suffix.lower() in EXT]


TOPICS = LIB / "topics.json"


def topics():
    return json.loads(TOPICS.read_text()) if TOPICS.exists() else {}


def list_photos(topic=None):
    used = used_ids()
    tags = topics()
    for p in library():
        ph, desc, pid = parts(p)
        if pid in used:
            continue
        info = tags.get(p.name)
        if not info:
            continue  # untagged photos are not cleared for use
        if topic and topic not in info["topics"]:
            continue
        print(json.dumps({"file": f"photos/{p.name}", "credit": credit_for(p), "shows": info["shows"],
                          "use_only_for": info["use_only_for"], "topics": info["topics"], "id": pid}))


def summary():
    used = used_ids()
    tags = topics()
    from collections import Counter
    c = Counter(t for p in library() if parts(p)[2] not in used for t in tags.get(p.name, {"topics": ["untagged"]})["topics"])
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"{k:16} {v}")


def prepare(src, dest, focus=(0.5, 0.5)):
    if "not-engaging" in str(src):
        sys.exit("REFUSED: photos in photos/not-engaging/ were rejected (Lee: only engaging, on-point photos).")
    if Path(str(src)).name not in topics():
        sys.exit("REFUSED: this photo isn't in photos/topics.json, so it hasn't been cleared for use.")
    pid = parts(src)[2]
    if pid in used_ids():
        sys.exit(f"REFUSED: photo {pid} has already been used. Photos are never reused (Lee's rule).")
    im = ImageOps.exif_transpose(Image.open(ROOT / src)).convert("RGB")
    im = ImageOps.fit(im, (2160, 2700), Image.LANCZOS, centering=focus)
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=90)
    print(json.dumps({"saved": str(dest), "credit": credit_for(src), "id": pid}))


def retire(src):
    p = ROOT / src
    pid = parts(p)[2]
    USED_DIR.mkdir(exist_ok=True)
    shutil.move(str(p), str(USED_DIR / p.name))
    tags = topics()
    if p.name in tags:
        tags.pop(p.name)
        TOPICS.write_text(json.dumps(tags, indent=1))
    with open(USED_IDS, "a") as f:
        f.write(pid + "\n")
    print(f"retired {pid}: moved to photos/used/{p.name}")


def check():
    used = used_ids()
    bad = [p.name for p in library() if parts(p)[2] in used]
    if bad:
        sys.exit("Already-used photos found in the library (remove them): " + ", ".join(bad))
    print(f"ok: {len(library())} unused photos, {len(used)} used ids on record")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["list"]:
        list_photos(a[a.index("--topic") + 1] if "--topic" in a else None)
    elif a[:1] == ["topics"]:
        summary()
    elif a[:1] == ["check"]:
        check()
    elif a[:1] == ["prepare"] and len(a) >= 3:
        f = (0.5, 0.5)
        if "--focus" in a:
            f = tuple(float(x) for x in a[a.index("--focus") + 1].split(","))
        prepare(a[1], a[2], f)
    elif a[:1] == ["retire"] and len(a) == 2:
        retire(a[1])
    else:
        print(__doc__); sys.exit(1)
