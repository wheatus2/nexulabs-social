#!/usr/bin/env python3
"""Pick and prepare a photo from the photos/ library for a post. Photos are NEVER reused.

File names: <photographer-name>--<short-description>--<unsplash-id>.jpg
  e.g. jane-smith--laptop-on-desk--AbC123xYz.jpg

  python3 photo.py list                         # unused photos (credit, description, id)
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
    bits = Path(path).stem.split("--")
    photographer = bits[0]
    desc = bits[1].replace("-", " ") if len(bits) > 2 else (bits[1].replace("-", " ") if len(bits) == 2 else "")
    pid = bits[2] if len(bits) > 2 else Path(path).stem
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
                    ids.add(parts(v)[2] if "/" in str(v) or "." in str(v) else str(v))
    return ids


def library():
    return [p for p in sorted(LIB.iterdir()) if p.is_file() and p.suffix.lower() in EXT]


def list_photos():
    used = used_ids()
    for p in library():
        ph, desc, pid = parts(p)
        if pid in used:
            continue
        print(json.dumps({"file": f"photos/{p.name}", "credit": credit_for(p), "description": desc, "id": pid}))


def prepare(src, dest, focus=(0.5, 0.5)):
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
        list_photos()
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
