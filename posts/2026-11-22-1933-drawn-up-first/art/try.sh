#!/bin/sh
# try.sh <shot> "<letters>" : drafts, then a side-by-side strip in .try.jpg
for l in $2; do python3.13 build.py $1 $l draft 2>&1 | grep -E "Error|Traceback" ; done
python3.13 - "$1" $2 <<'P'
import sys
from PIL import Image, ImageDraw
s=sys.argv[1]; ls=sys.argv[2:]
ims=[Image.open(f".d-{s}{l}.jpg").resize((540,960)) for l in ls]
out=Image.new("RGB",(540*len(ims),960))
for i,im in enumerate(ims):
    d=ImageDraw.Draw(im); d.line([(0,110),(540,110)],fill=(255,255,0)); d.line([(0,770),(540,770)],fill=(255,255,0)); d.line([(38,0),(38,960)],fill=(255,255,0))
    d.rectangle([38,620,400,737],outline=(0,255,0))
    out.paste(im,(540*i,0))
out.save(".try.jpg",quality=85)
P
