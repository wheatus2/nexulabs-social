#!/usr/bin/env python3
"""Pick and prepare a photo from the photos/ library for a post.

  python3 photo.py list                         # unused photos with their credits
  python3 photo.py prepare photos/<file> posts/<id>/photo.jpg [--focus 0.5,0.4]
      -> crops to 4:5, resizes to 2160x2700, prints the credit line
  python3 photo.py retire photos/<file>         # move to photos/used/ after publishing
"""
import json, re, shutil, sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
LIB = ROOT / "photos"
EXT = {".jpg", ".jpeg", ".png", ".webp"}


def credit_for(path):
    stem = Path(path).stem.split("--")[0]
    name = " ".join(w.capitalize() for w in re.split(r"[-_\s]+", stem) if w)
    return f"Photo: {name} on Unsplash"


def list_photos():
    for p in sorted(LIB.iterdir()):
        if p.suffix.lower() in EXT:
            desc = p.stem.split("--")[1].replace("-", " ") if "--" in p.stem else ""
            with Image.open(p) as im:
                w, h = im.size
            print(json.dumps({"file": f"photos/{p.name}", "credit": credit_for(p), "description": desc, "size": f"{w}x{h}"}))


def prepare(src, dest, focus=(0.5, 0.5)):
    im = ImageOps.exif_transpose(Image.open(ROOT / src)).convert("RGB")
    im = ImageOps.fit(im, (2160, 2700), Image.LANCZOS, centering=focus)
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=90)
    print(json.dumps({"saved": str(dest), "credit": credit_for(src)}))


def retire(src):
    p = ROOT / src
    shutil.move(str(p), str(LIB / "used" / p.name))
    print(f"moved {src} -> photos/used/{p.name}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["list"]:
        list_photos()
    elif a[:1] == ["prepare"] and len(a) >= 3:
        f = (0.5, 0.5)
        if "--focus" in a:
            f = tuple(float(x) for x in a[a.index("--focus") + 1].split(","))
        prepare(a[1], a[2], f)
    elif a[:1] == ["retire"] and len(a) == 2:
        retire(a[1])
    else:
        print(__doc__); sys.exit(1)
