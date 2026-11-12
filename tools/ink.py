import sys
from PIL import Image
# usage: ink.py image [x0 x1] -> horizontal ink bands (y ranges) and for each band the x extent
im=Image.open(sys.argv[1]).convert('RGB'); W,H=im.size
x0=int(sys.argv[2]) if len(sys.argv)>2 else 0; x1=int(sys.argv[3]) if len(sys.argv)>3 else W
bg=im.getpixel((6,6)); px=im.load()
def diff(p): return max(abs(p[i]-bg[i]) for i in range(3))
thr=int(sys.argv[4]) if len(sys.argv)>4 else 14
rows=[]
for y in range(H):
    xs=[x for x in range(x0,x1,2) if diff(px[x,y])>thr]
    rows.append((min(xs),max(xs)) if xs else None)
bands=[];start=None
for y,r in enumerate(rows+[None]):
    if r and start is None: start=y;lo,hi=r
    elif r: lo=min(lo,r[0]);hi=max(hi,r[1])
    elif start is not None:
        if y-start>3: bands.append((start,y-1,lo,hi))
        start=None
for b in bands: print("y %4d-%4d (h %3d)  x %4d-%4d"%(b[0],b[1],b[1]-b[0]+1,b[2],b[3]))
