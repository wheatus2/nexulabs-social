"""Renders the pictures for this carousel with Blender's Python module (pip install bpy; run with python3.13).

A made-up bakery's packaging on pink paper: three card boxes stacked, then a paper bag beside them.
Before, every piece carries a different logo (prints: art/print.py). After, one brand on all of them.
Shot from the same side three ways:
  1  the whole stack of three, three logos
  2  low and close on the bag, a rubber stamp with a fourth logo, the stack behind it
  3  from higher, the same stack and bag in one brand
python3.13 build.py <1|2|3|all> [draft|final]   writes art/render-0N.jpg (1080x1350). Units are centimetres.
The type is set over the picture in slide-0N.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1350
TMP = Path(tempfile.gettempdir())
EXPOSURE = 1.0
SUN = 3.2
PINK = "#F2A0BC"
CARD, CREAM, OX = "#F3EEE3", "#F6EBDD", "#6E1423"

# name: (width, depth, height), position x, y, yaw in degrees
STACK = [("1", (30, 30, 11), (0.0, 0.0), 5), ("2", (24.5, 24.5, 10), (-1.2, 0.8), -7), ("3", (19, 19, 9), (0.6, 0.2), 8)]
BW, BD, BH = 17.0, 9.5, 33.0

SHOTS = {
    1: dict(loc=(68, -105, 66), aim=(0, 0, 13), lens=59.5, f=0.8, focus=(4, -14, 16), shift=(0.035, 0.116), state="a", bag=None),
    2: dict(loc=(52, -118, 62), aim=(8, -8, 14), lens=46, f=0.8, focus=(10, -18, 16), shift=(0.067, 0.11), state="a", bag=(31.0, -20.0, 20)),
    3: dict(loc=(78, -122, 118), aim=(-10, -6, 12), lens=52, f=0.8, focus=(-4, -14, 16), shift=(-0.0025, 0.130), state="b", bag=(-33.0, -16.0, 16)),
}


def lin(hexcol):
    c = [int(hexcol[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def aim(ob, target, up=(0, 0, 1)):
    f = (Vector(target) - ob.location).normalized()
    r = f.cross(Vector(up)).normalized()
    u = r.cross(f)
    ob.rotation_euler = Matrix((r, u, -f)).transposed().to_euler()


def link(ob):
    bpy.context.scene.collection.objects.link(ob); return ob


def paper_bump(nt, p, strength=0.10, scale=60, crumple=0.0):
    N_, L = nt.nodes, nt.links
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    b = N_.new("ShaderNodeBump"); b.inputs["Strength"].default_value = strength; b.inputs["Distance"].default_value = 0.008
    L.new(nz.outputs["Fac"], b.inputs["Height"])
    if crumple:
        n2 = N_.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 0.22; n2.inputs["Detail"].default_value = 2
        L.new(tc.outputs["Object"], n2.inputs["Vector"])
        b2 = N_.new("ShaderNodeBump"); b2.inputs["Strength"].default_value = crumple; b2.inputs["Distance"].default_value = 0.5
        L.new(n2.outputs["Fac"], b2.inputs["Height"]); L.new(b.outputs["Normal"], b2.inputs["Normal"])
        L.new(b2.outputs["Normal"], p.inputs["Normal"])
    else:
        L.new(b.outputs["Normal"], p.inputs["Normal"])


_mats = {}


def printed(png, rough=0.62, crumple=0.0):
    key = (png, crumple)
    if key in _mats:
        return _mats[key]
    m, nt, p = mat(png)
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / png)); tex.interpolation = "Cubic"; tex.extension = "EXTEND"
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough; p.inputs["Specular IOR Level"].default_value = 0.3
    paper_bump(nt, p, crumple=crumple)
    _mats[key] = m
    return m


def plain(hexcol, rough=0.62, crumple=0.0):
    key = (hexcol, crumple)
    if key in _mats:
        return _mats[key]
    m, nt, p = mat(hexcol)
    p.inputs["Base Color"].default_value = (*lin(hexcol), 1)
    p.inputs["Roughness"].default_value = rough; p.inputs["Specular IOR Level"].default_value = 0.3
    paper_bump(nt, p, crumple=crumple)
    _mats[key] = m
    return m


def quads(name, faces, thick=0.0, bevel=0.0, parent=None, smooth=False):
    """faces: list of (corners BL BR TR TL as the reader sees them, material). Each face has its own vertices and a 0..1 UV."""
    V, F, mats, mi = [], [], [], []
    for corners, m in faces:
        n = len(V); V += [tuple(c) for c in corners]; F.append(tuple(range(n, n + len(corners))))
        if m not in mats:
            mats.append(m)
        mi.append(mats.index(m))
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F)
    uv = me.uv_layers.new(name="uv")
    for poly in me.polygons:
        poly.material_index = mi[poly.index]; poly.use_smooth = smooth
        if len(poly.loop_indices) == 4:
            for k, li in enumerate(poly.loop_indices):
                uv.data[li].uv = ((0, 0), (1, 0), (1, 1), (0, 1))[k]
    for m in mats:
        me.materials.append(m)
    ob = link(bpy.data.objects.new(name, me))
    if thick:
        w = ob.modifiers.new("w", "WELD"); w.merge_threshold = 0.001
        s = ob.modifiers.new("s", "SOLIDIFY"); s.thickness = thick; s.offset = -1; s.use_even_offset = True
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 3; b.limit_method = "ANGLE"; b.angle_limit = math.radians(50)
        b.material = -1
    if parent:
        ob.parent = parent
    return ob


def cardbox(name, size, pos, z0, yaw, mats):
    """A two-piece card box: a base and a deep lift-off lid that stops short of the table. mats: front, right, top, rest, base."""
    w, d, h = size
    piv = link(bpy.data.objects.new(name, None)); piv.location = (pos[0], pos[1], z0); piv.rotation_euler = (0, 0, math.radians(yaw))
    gap = 0.6
    x0, x1, y0, y1, za, zb = -w / 2, w / 2, -d / 2, d / 2, gap, h
    faces = [
        ([(x0, y0, za), (x1, y0, za), (x1, y0, zb), (x0, y0, zb)], mats["front"]),
        ([(x1, y0, za)] + [(x1, 1.7 * math.cos(math.pi - i / 20 * math.pi), za + 1.7 * math.sin(i / 20 * math.pi)) for i in range(21)] + [(x1, y1, za), (x1, y1, zb), (x1, y0, zb)], mats["right"]),
        ([(x1, y1, za), (x0, y1, za), (x0, y1, zb), (x1, y1, zb)], mats["rest"]),
        ([(x0, y1, za), (x0, y0, za), (x0, y0, zb), (x0, y1, zb)], mats["rest"]),
        ([(x0, y0, zb), (x1, y0, zb), (x1, y1, zb), (x0, y1, zb)], mats["top"]),
    ]
    quads(name + "-lid", faces, thick=0.16, bevel=0.07, parent=piv)
    i = 0.24
    bx0, bx1, by0, by1 = x0 + i, x1 - i, y0 + i, y1 - i
    b = mats["base"]
    quads(name + "-base", [
        ([(bx0, by0, 0), (bx1, by0, 0), (bx1, by0, h - 0.4), (bx0, by0, h - 0.4)], b),
        ([(bx1, by0, 0), (bx1, by1, 0), (bx1, by1, h - 0.4), (bx1, by0, h - 0.4)], b),
        ([(bx1, by1, 0), (bx0, by1, 0), (bx0, by1, h - 0.4), (bx1, by1, h - 0.4)], b),
        ([(bx0, by1, 0), (bx0, by0, 0), (bx0, by0, h - 0.4), (bx0, by1, h - 0.4)], b),
    ], thick=0.14, bevel=0.05, parent=piv)
    return piv


def bag(pos, front, body, flap):
    """A flat-bottomed paper bag: square at the foot, its gussets folding in as the mouth closes, the top turned over."""
    piv = link(bpy.data.objects.new("bag", None)); piv.location = (pos[0], pos[1], 0); piv.rotation_euler = (0, 0, math.radians(pos[2]))
    nz, nx = 44, 14
    def ring(k):
        t = k / nz; z = t * BH
        s = min(1.0, max(0.0, (t - 0.42) / 0.58)); s = s * s * (3 - 2 * s)
        d = BD * (1 - 0.955 * s)
        inn = math.sqrt(max(0.0, (BD / 2) ** 2 - (d / 2) ** 2)) * 0.96
        bulge = 0.55 * math.sin(math.pi * min(1.0, t / 0.8)) * (1 - s)
        return z, d, inn, bulge
    def panel(name, fn, n, m, uvfn=None):
        V, F = [], []
        for k in range(nz + 1):
            for j in range(n + 1):
                V.append(fn(k, j / n))
        for k in range(nz):
            for j in range(n):
                a = k * (n + 1) + j
                F.append((a, a + 1, a + n + 2, a + n + 1))
        me = bpy.data.meshes.new(name); me.from_pydata(V, [], F)
        uv = me.uv_layers.new(name="uv")
        for lp in me.loops:
            k, j = divmod(lp.vertex_index, n + 1)
            uv.data[lp.index].uv = (j / n, k / nz)
        for p in me.polygons:
            p.use_smooth = True
        me.materials.append(m)
        ob = link(bpy.data.objects.new(name, me)); ob.parent = piv
        return ob
    def fr(k, u):
        z, d, inn, b = ring(k); return (-BW / 2 + u * BW, -d / 2 - b * math.sin(math.pi * u), z)
    def bk(k, u):
        z, d, inn, b = ring(k); return (BW / 2 - u * BW, d / 2 + b * math.sin(math.pi * u), z)
    def g(side, half):
        def fn(k, u):
            z, d, inn, b = ring(k)
            x_out, x_in = side * BW / 2, side * (BW / 2 - inn)
            if half == 0:      # from the front corner to the crease
                return (x_out + (x_in - x_out) * u, -d / 2 * (1 - u), z)
            return (x_in + (x_out - x_in) * u, d / 2 * u, z)
        return fn
    panel("bag-front", fr, nx, front)
    panel("bag-back", bk, nx, body)
    for side in (1, -1):
        for half in (0, 1):
            panel(f"bag-g{side}{half}", g(side, half), 1, body)
    # the turned-over top
    z, d, inn, b = ring(nz)
    zf = BH - 3.6
    k2 = int(zf / BH * nz); z2, d2, _, _ = ring(k2)
    quads("bag-flap", [
        ([(-BW / 2, -d2 / 2 - 0.22, zf), (BW / 2, -d2 / 2 - 0.22, zf), (BW / 2, -d / 2 - 0.06, BH + 0.05), (-BW / 2, -d / 2 - 0.06, BH + 0.05)], flap),
        ([(-BW / 2, -d / 2 - 0.06, BH + 0.05), (BW / 2, -d / 2 - 0.06, BH + 0.05), (BW / 2, d / 2 + 0.03, BH + 0.05), (-BW / 2, d / 2 + 0.03, BH + 0.05)], flap),
    ], thick=0.05, parent=piv)
    return piv


def scene(frame):
    shot = SHOTS[frame]
    # the paper sweep: a floor running up into a wall
    V, F = [(-9000, -9000, 0), (9000, -9000, 0), (9000, 9000, 0), (-9000, 9000, 0)], [(0, 1, 2, 3)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(V, [], F)
    sw = link(bpy.data.objects.new("sweep", me))
    m, nt, p = mat("sweep"); p.inputs["Base Color"].default_value = (*lin(PINK), 1); p.inputs["Roughness"].default_value = 0.9; p.inputs["Specular IOR Level"].default_value = 0.1
    paper_bump(nt, p, strength=0.05, scale=40)
    sw.data.materials.append(m)

    st = shot["state"]
    z = 0.0
    for nm, size, pos, yaw in STACK:
        if st == "a":
            mm = dict(front=printed(f".a-{nm}.png"), right=plain(CARD), top=plain(CARD), rest=plain(CARD), base=plain(CARD))
        else:
            col = OX if nm == "2" else CREAM
            mm = dict(front=printed(f".b-{nm}.png"), right=plain(col), top=printed(".b-top.png") if nm == "3" else plain(col), rest=plain(col), base=plain(OX if nm != "2" else CREAM))
        cardbox("box" + nm, size, pos, z, yaw, mm)
        z += size[2] + 0.03
    if shot["bag"]:
        if st == "a":
            bag(shot["bag"], printed(".a-bag.png", crumple=0.35), plain(CARD, crumple=0.35), plain(CARD))
        else:
            bag(shot["bag"], printed(".b-bag.png", crumple=0.35), plain(CREAM, crumple=0.35), plain(OX))


def build(frame, quality):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 160 if final else 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 45
    sc.render.threads_mode = "FIXED"; sc.render.threads = 4
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1.0, 0.93, 0.95, 1); bg.inputs["Strength"].default_value = 0.16

    scene(frame)
    shot = SHOTS[frame]
    T = (0, 0, 14)
    # key: a small window high on the left and a little in front, so every box and the bag throw a shadow to the right
    key = bpy.data.lights.new("key", "SUN"); key.energy = SUN; key.angle = math.radians(5); key.color = (1.0, 0.965, 0.92)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (-200, -380, 500); aim(ko, (0, 0, 0))
    fl = bpy.data.lights.new("fill", "SUN"); fl.energy = SUN * 0.16; fl.angle = math.radians(60); fl.color = (1.0, 0.95, 0.97)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (420, -420, 200); aim(fo, (0, 0, 0))

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]; cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 1; cam.clip_end = 30000
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).dot((Vector(shot["aim"]) - co.location).normalized())
    cam.dof.aperture_fstop = shot["f"]
    if quality == "probe":
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update()
        for grp in ("box", "bag"):
            xs, ys = [], []
            for ob in sc.objects:
                if ob.type == "MESH" and ob.name.startswith(grp):
                    for c in ob.bound_box:
                        v = world_to_camera_view(sc, co, ob.matrix_world @ Vector(c)); xs.append(v.x * W); ys.append((1 - v.y) * H)
            if xs:
                print(f"  f{frame} {grp}: x {min(xs):.0f}..{max(xs):.0f}  y {min(ys):.0f}..{max(ys):.0f}")
        for nm, size, pos, yaw in STACK:
            piv = sc.objects["box" + nm]
            for lab, pt in (("frontR", (size[0] / 2, -size[1] / 2, 0.6)), ("frontR top", (size[0] / 2, -size[1] / 2, size[2])), ("frontL", (-size[0] / 2, -size[1] / 2, 0.6)), ("backR top", (size[0] / 2, size[1] / 2, size[2]))):
                v = world_to_camera_view(sc, co, piv.matrix_world @ Vector(pt)); print(f"     box{nm} {lab:10s} {v.x * W:6.0f} {(1 - v.y) * H:6.0f}")
        return None
    exr = str(TMP / f"nx-bake-{frame}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def grade(exr, frame, quality):
    from PIL import Image
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    x = np.clip(a, 0, None) * EXPOSURE
    x = np.where(x > 0.66, 0.66 + (1 - np.exp(-(x - 0.66) / 0.34)) * 0.30, x)     # a soft shoulder: white card stays off pure white
    x = np.clip(x, 0, 1)
    lum = (x * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    x = np.clip(lum + (x - lum) * 1.06, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3 + frame)
    x += rng.normal(0, 0.006, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"render-{frame:02d}.jpg" if quality == "final" else f".draft-{frame:02d}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst)


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 else "draft"
    for fr in ([1, 2, 3] if which == "all" else [int(which)]):
        if quality == "probe":
            build(fr, quality)
        elif "regrade" in args:
            grade(str(TMP / f"nx-bake-{fr}.exr"), fr, quality)
        else:
            grade(build(fr, quality), fr, quality)
