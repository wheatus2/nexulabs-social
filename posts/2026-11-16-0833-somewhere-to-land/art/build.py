"""Renders the pictures for this post with Blender's Python module (pip install bpy brotli).

One paper dart folded from a printed A4 quote (art/sheet.py), on a butter-yellow table, shot from the same side:
  1  the whole dart, low, nose towards us: QUOTE on one wing, VALID FOR 30 DAYS on the other
  2  right up against the 30 DAYS wing
  3  from higher: the dart has come down on an open diary, nose beside Thursday's entry

  python3 build.py <frame 1|2|3|all> [draft|final] [regrade]
writes art/render-0N.jpg (1080x1350). Units are centimetres. The type is set over it in slide-0N.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1350
TMP = Path(tempfile.gettempdir())
TABLE = (0.90, 0.64, 0.085)        # butter yellow, linear RGB
TEAL = (0.004, 0.102, 0.125)
EXPOSURE = 1.3

# the dart: A4, 21 x 29.7. Local axes: nose at y=0, tail at y=29.7, keel fold along the y axis at z=0.
SW, SL = 21.0, 29.7
KEEL = 2.2                          # depth of the keel
TAN = math.tan(math.radians(22.5))  # the leading edge runs at 22.5 degrees to the centre fold
Y0 = KEEL / TAN                     # where the wing starts
DIHEDRAL = math.radians(9)
ROLL = math.radians(21.0)           # it rests on its keel and one wing tip

def others(seed=11, n=44):
    """Where the earlier quotes came down: scattered behind the newest one, none touching."""
    import random
    rnd = random.Random(seed)
    placed = [(-4.4, 14.3), (-8.0, 44.0), (14.0, 40.0)]                      # the newest dart's middle
    out = []
    tries = 0
    while len(out) < n and tries < 4000:
        tries += 1
        cy = rnd.uniform(42, 330); cx = rnd.uniform(-20 - 0.42 * cy, 26 + 0.42 * cy)
        if any(math.hypot(cx - px, cy - py) < 31 for px, py in placed):
            continue
        yaw = rnd.uniform(-180, 180); a = math.radians(yaw)
        placed.append((cx, cy))
        out.append((cx + 15 * math.sin(a), cy - 15 * math.cos(a), yaw, rnd.choice((-1, 1))))
    return out


SHOTS = {
    1: dict(loc=(12.0, -21.0, 27.0), aim=(-2.5, 19.0, 0.0), lens=38, f=0.11, focus=(-3.0, 22.0, 2.5), shift=(-0.13, 0.075),
            yaw=30, pos=(0, 0, 0)),
    2: dict(loc=(10.0, -27.0, 18.0), aim=(-4.8, 18.0, 0.0), lens=42, f=0.06, focus=(-3.0, 22.0, 2.5), shift=(0.03, -0.095),
            yaw=17, pos=(0, 0, 0)),
    3: dict(loc=(19.0, -22.0, 36.0), aim=(10.0, 3.2, 0.0), lens=38, f=0.05, focus=(8.5, 11.5, 0.75), shift=(0.11, -0.08),
            yaw=-44, pitch=-1.54, pos=(11.9, 8.6, 0.80), diary=(0, 0, 0, 0)),
}


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def aim(ob, target, up=(0, 0, 1)):
    f = (Vector(target) - ob.location).normalized()
    r = f.cross(Vector(up)).normalized()
    u = r.cross(f)
    ob.rotation_euler = Matrix((r, u, -f)).transposed().to_euler()


def grid(name, fn, nu, nv, material):
    """A surface from fn(i/nu, j/nv) -> ((x, y, z), (u, v))."""
    verts, uvs, faces = [], [], []
    for j in range(nv + 1):
        for i in range(nu + 1):
            p, t = fn(i / nu, j / nv); verts.append(p); uvs.append(t)
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            faces.append((a, a + 1, a + nu + 2, a + nu + 1))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name="uv")
    for lp in me.loops:
        uv.data[lp.index].uv = uvs[lp.vertex_index]
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(material)
    return ob


def paper_mat(img=None, tint=(0.93, 0.925, 0.90), back=None, name="paper"):
    """Matt paper. The print is on the front; the back is plain with a little of the light coming through."""
    m, nt, p = mat(name)
    N, L = nt.nodes, nt.links
    geo = N.new("ShaderNodeNewGeometry")
    if img:
        tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(img)); tex.interpolation = "Cubic"
        tex.extension = "EXTEND"
        if back is not None:
            mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
            L.new(geo.outputs["Backfacing"], mix.inputs["Factor"])
            L.new(tex.outputs["Color"], mix.inputs["A"]); mix.inputs["B"].default_value = (*back, 1)
            L.new(mix.outputs["Result"], p.inputs["Base Color"])
        else:
            L.new(tex.outputs["Color"], p.inputs["Base Color"])
    else:
        p.inputs["Base Color"].default_value = (*tint, 1)
    p.inputs["Roughness"].default_value = 0.72
    p.inputs["Specular IOR Level"].default_value = 0.25
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 160; nz.inputs["Detail"].default_value = 6
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.06; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    # a little light through the sheet
    out = N["Material Output"]
    tr = N.new("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = (0.9, 0.88, 0.82, 1)
    ms = N.new("ShaderNodeMixShader"); ms.inputs["Fac"].default_value = 0.10
    L.new(p.outputs["BSDF"], ms.inputs[1]); L.new(tr.outputs["BSDF"], ms.inputs[2]); L.new(ms.outputs["Shader"], out.inputs["Surface"])
    return m


def table_mat():
    m, nt, p = mat("table")
    N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.82
    p.inputs["Specular IOR Level"].default_value = 0.3
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.25; nz.inputs["Detail"].default_value = 3
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.95; mr.inputs["To Max"].default_value = 1.03
    L.new(nz.outputs["Fac"], mr.inputs["Value"])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1
    mix.inputs["A"].default_value = (*TABLE, 1)
    comb = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(mr.outputs["Result"], comb.inputs[k])
    L.new(comb.outputs["Color"], mix.inputs["B"]); L.new(mix.outputs["Result"], p.inputs["Base Color"])
    fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 110; fine.inputs["Detail"].default_value = 6
    L.new(geo.outputs["Position"], fine.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.02
    L.new(fine.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def dart():
    """The folded dart, resting on its keel and its right wing tip. Returns the parent empty."""
    root = bpy.data.objects.new("dart", None); bpy.context.scene.collection.objects.link(root)
    printed = paper_mat(HERE / "quote.png", back=(0.90, 0.895, 0.87), name="quote")
    plain = paper_mat(None, name="plain")
    parts = []

    def splay(y):                       # half the gap at the top of the keel
        return 0.04 + 0.30 * (y / SL)

    def width(y):                       # wing width at y, measured from the keel fold
        return max(0.0, min(y * TAN, SW / 2) - KEEL)

    for sx in (-1, 1):
        d = DIHEDRAL + (math.radians(2.5) if sx < 0 else 0)
        out = Vector((sx * math.cos(d), 0, math.sin(d)))
        up = Vector((-sx * math.sin(d), 0, math.cos(d)))

        def wing(a, b, sx=sx, out=out, up=up, lift=0.0):
            y = Y0 + (SL - Y0) * b
            w = width(y) * a
            # paper is never dead flat: the wing bows a little along its length and lifts at the trailing corner
            bow = 0.22 * math.sin(math.pi * b) * (w / 8.3) - 0.10 * (w / 8.3) ** 2 * b + 0.16 * (w / 8.3) ** 3 * b ** 3
            p = Vector((sx * splay(y), y, KEEL)) + out * w + up * (bow + lift * (1 - 0.92 * a) * (0.25 + 0.75 * b))
            sheet_x = SW / 2 + sx * (KEEL + w)
            return tuple(p), (sheet_x / SW, y / SL)
        parts.append(grid(f"wing{sx}", wing, 24, 48, printed))
        # the flap folded under the wing, sprung a little open towards the keel
        parts.append(grid(f"flap{sx}", lambda a, b: (wing(a, b, lift=-0.34)[0], (0.5, 0.02)), 16, 32, plain))

        def keel(a, b, sx=sx):
            y = SL * b
            top = min(y * TAN, KEEL)            # the keel is a triangle near the nose
            h = top * a
            belly = 0.05 * math.sin(math.pi * a) * math.sin(math.pi * b)
            p = (sx * (splay(y) * (h / KEEL) + belly), y, h)
            return p, ((SW / 2 + sx * h) / SW, y / SL)
        k = grid(f"keel{sx}", keel, 8, 48, printed)
        if sx > 0:                              # keep the print on the inside of the keel on both sides
            k.data.flip_normals()
        parts.append(k)
    # normals: wings face up
    for o in parts:
        if o.name.startswith("wing-") or o.name.startswith("flap-"):
            o.data.flip_normals()
    for o in parts:
        o.parent = root
    root.rotation_mode = "YXZ"
    root.rotation_euler = (0, ROLL, 0)
    return root, parts


def diary():
    """An open A5 day-to-a-page diary: gutter along the local y axis at x=0, foot of the pages at y=0."""
    root = bpy.data.objects.new("diary", None); bpy.context.scene.collection.objects.link(root)
    PW, PH, COVER = 14.8, 21.0, 0.28
    parts = []
    m, nt, p = mat("cloth")
    p.inputs["Base Color"].default_value = (*TEAL, 1); p.inputs["Roughness"].default_value = 0.6
    N, L = nt.nodes, nt.links
    geo = N.new("ShaderNodeNewGeometry")
    wv = N.new("ShaderNodeTexNoise"); wv.inputs["Scale"].default_value = 60; wv.inputs["Detail"].default_value = 4
    L.new(geo.outputs["Position"], wv.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.inputs["Distance"].default_value = 0.02
    L.new(wv.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    cloth = m
    # the block of pages seen edge on: fine stripes
    m, nt, p = mat("edges")
    N, L = nt.nodes, nt.links
    geo = N.new("ShaderNodeNewGeometry")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.2, 0.2, 90)
    L.new(geo.outputs["Position"], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 6; nz.inputs["Detail"].default_value = 2
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.3; mr.inputs["From Max"].default_value = 0.7
    mr.inputs["To Min"].default_value = 0.55; mr.inputs["To Max"].default_value = 0.95
    L.new(nz.outputs["Fac"], mr.inputs["Value"])
    comb = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(mr.outputs["Result"], comb.inputs[k])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1
    mix.inputs["A"].default_value = (0.90, 0.86, 0.74, 1); L.new(comb.outputs["Color"], mix.inputs["B"])
    L.new(mix.outputs["Result"], p.inputs["Base Color"]); p.inputs["Roughness"].default_value = 0.8
    edges = m

    for sx, T, img in ((-1, 1.45, "diary-left.png"), (1, 0.42, "diary-right.png")):
        pm = paper_mat(HERE / img, name=f"page{sx}")

        def z_at(x, T=T):
            return COVER + T * (1 - 0.86 * math.exp(-x / (0.45 + 0.9 * T)))

        def top(a, b, sx=sx, T=T):
            x = PW * a ** 1.6                    # more rows near the gutter, where it curves
            u = (x / PW) if sx > 0 else 1 - x / PW
            return (sx * x, PH * b, z_at(x)), (u, b)
        t = grid(f"page{sx}", top, 40, 8, pm)
        if sx < 0:
            t.data.flip_normals()
        parts.append(t)
        # the sides of the block: fore-edge and foot and head
        bm = bmesh.new()
        n = 40
        for y, flip in ((0, False), (PH, True)):
            prev = None
            for i in range(n + 1):
                x = PW * (i / n) ** 1.6
                a = bm.verts.new((sx * x, y, COVER)); b = bm.verts.new((sx * x, y, z_at(x)))
                if prev:
                    f = bm.faces.new((prev[0], a, b, prev[1]))
                prev = (a, b)
        zt = z_at(PW)
        bm.faces.new([bm.verts.new(v) for v in ((sx * PW, 0, COVER), (sx * PW, PH, COVER), (sx * PW, PH, zt), (sx * PW, 0, zt))])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(f"block{sx}"); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(f"block{sx}", me); bpy.context.scene.collection.objects.link(ob)
        ob.data.materials.append(edges); parts.append(ob)
    # the cover: one board under everything, a little bigger than the pages
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * (2 * PW + 0.7), v.co.y * (PH + 0.7) + PH / 2, (v.co.z + 0.5) * COVER))
    me = bpy.data.meshes.new("cover"); bm.to_mesh(me); bm.free()
    cv = bpy.data.objects.new("cover", me); bpy.context.scene.collection.objects.link(cv)
    bv = cv.modifiers.new("b", "BEVEL"); bv.width = 0.08; bv.segments = 3
    cv.data.materials.append(cloth); parts.append(cv)
    # the ribbon: down the gutter, out at the foot and across the table
    path = [(0.0, 9.0, COVER + 0.26), (0.02, 3.0, COVER + 0.26), (0.05, 0.4, COVER + 0.27), (0.14, -0.38, COVER + 0.22), (0.45, -0.75, 0.03),
            (1.6, -1.5, 0.02), (3.4, -2.3, 0.02), (5.4, -2.8, 0.02), (7.4, -2.7, 0.02), (9.0, -2.1, 0.02)]
    cu = bpy.data.curves.new("ribbon", "CURVE"); cu.dimensions = "3D"
    sp = cu.splines.new("NURBS"); sp.points.add(len(path) - 1)
    for pt, c in zip(sp.points, path):
        pt.co = (*c, 1)
    sp.use_endpoint_u = True; sp.order_u = 4; cu.resolution_u = 24
    cu.extrude = 0.32; cu.twist_mode = "Z_UP"
    rb = bpy.data.objects.new("ribbon", cu); bpy.context.scene.collection.objects.link(rb)
    m, nt, p = mat("satin"); p.inputs["Base Color"].default_value = (0.006, 0.15, 0.18, 1); p.inputs["Roughness"].default_value = 0.38
    p.inputs["Sheen Weight"].default_value = 0.5
    rb.data.materials.append(m); parts.append(rb)
    for o in parts:
        o.parent = root
    return root


def build(frame, quality, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 176 if final else 32
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1.0, 0.97, 0.90, 1); bg.inputs["Strength"].default_value = 0.16

    shot = SHOTS[frame]
    root, parts = dart()
    root.rotation_euler = (math.radians(shot.get("pitch", 0)), ROLL + math.radians(shot.get("roll", 0)), math.radians(shot["yaw"]))
    root.location = shot["pos"]
    if frame == 2:
        # the quotes that went out before this one, where they came down
        for x, y, yaw, side in others():
            r2, _ = dart()
            r2.rotation_euler = (0, ROLL * side, math.radians(yaw)); r2.location = (x, y, 0)
    if frame == 3:
        d = diary()
        d.location = shot["diary"][:3]; d.rotation_euler.z = math.radians(shot["diary"][3])

    me = bpy.data.meshes.new("table"); s = 3000
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    tb = bpy.data.objects.new("table", me); sc.collection.objects.link(tb); tb.location.z = -0.0005
    tb.data.materials.append(table_mat())

    # key: a small window low behind and to the right, raking, so every fold throws a shadow towards us and to the left
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 132; key.size_y = 180
    key.energy = 52000 * 7.5 * 9; key.color = (1.0, 0.965, 0.92)
    ko = bpy.data.objects.new("key", key); sc.collection.objects.link(ko)
    ko.location = (378, 429, 345); aim(ko, (0, 8, 0))
    # fill from the camera side, low and big
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 360; fl.energy = 5200 * 6 * 9; fl.color = (0.97, 0.98, 1.0)
    fo = bpy.data.objects.new("fill", fl); sc.collection.objects.link(fo)
    fo.location = (-150, -450, 225); aim(fo, (0, 8, 0))

    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]
    cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 0.1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"]
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region

    exr = str(TMP / f"nx-dart-{frame}.exr")
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
    a = np.clip(a, 0, None)
    x = a * EXPOSURE
    # a gentle shoulder only: keeps the yellow a yellow and the paper off pure white
    x = np.where(x > 0.6, 0.6 + (1 - np.exp(-(x - 0.6) / 0.42)) * 0.4, x)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3 + frame)
    x += rng.normal(0, 0.008, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"render-{frame:02d}.jpg" if quality == "final" else f".draft-{frame:02d}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst)


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 else "draft"
    regrade = "regrade" in args
    for fr in ([1, 2, 3] if which == "all" else [int(which)]):
        exr = str(TMP / f"nx-dart-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
