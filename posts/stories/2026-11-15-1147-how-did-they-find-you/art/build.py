"""Renders the three pictures for this Story with Blender's Python module (pip install bpy brotli).

One chrome hand tally counter lying on its back on a chalk-pink table, its finger ring towards us. It has counted
the enquiries (0047) but nobody wrote down where they came from.
  1  the whole counter, low and from the right: how did they find you?
  2  right up against the number window, the button blurring away behind
  3  the same counter nearer and higher, now with a strip of green embossed label tape: GOOGLE

  python3 build.py <frame 1|2|3|all> [draft|final] [regrade]
writes art/render-0N.jpg (1080x1920). The type is set over it in slide-0N.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())

PINK = (0.70, 0.43, 0.40)            # the sweep, linear RGB (about #E3B1AC once graded)
R = 0.026                            # body radius
TOP = 0.019                          # height of the face
WIN = (0.0335, 0.0054)               # number window, x by y
WIN_Y = 0.0045                       # the window sits a little above the centre of the face
WHEEL_R, WHEEL_W, PITCH = 0.0082, 0.0066, 0.0078
DIGITS = "0047"


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def link(ob):
    bpy.context.scene.collection.objects.link(ob); return ob


def from_bm(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return link(bpy.data.objects.new(name, me))


def cylinder(name, r, depth, segs=160):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r, radius2=r, depth=depth)
    return from_bm(name, bm)


def box(name, sx, sy, sz):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    return from_bm(name, bm)


def bevel(ob, w, segs=8):
    m = ob.modifiers.new("bevel", "BEVEL"); m.width = w; m.segments = segs; m.limit_method = "ANGLE"
    m.harden_normals = False
    return m


def torus(name, R0, r0, n=160, m=48):
    verts, faces = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            verts.append(((R0 + r0 * math.cos(b)) * math.cos(a), (R0 + r0 * math.cos(b)) * math.sin(a), r0 * math.sin(b)))
    for i in range(n):
        for j in range(m):
            a = i * m + j; b = i * m + (j + 1) % m; c = ((i + 1) % n) * m + (j + 1) % m; d = ((i + 1) % n) * m + j
            faces.append((a, b, c, d))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    return link(bpy.data.objects.new(name, me))


def wheel(name, digit, x):
    """A number wheel, axis along x, with UVs so the strip of digits runs round it. The digit shown faces up (+z)
    and reads with its top towards +y (the button end)."""
    segs = 120
    verts, faces, uvs = [], [], []
    for s in range(segs + 1):
        a = 2 * math.pi * s / segs
        for side in (0, 1):
            verts.append(((side - 0.5) * WHEEL_W, WHEEL_R * math.sin(a), WHEEL_R * math.cos(a)))
    for s in range(segs):
        a, b = 2 * s, 2 * (s + 1)
        faces.append((a, a + 1, b + 1, b))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            s, side = divmod(vi, 2)
            # v runs down the strip as the angle grows; digit k is centred at v = 1 - (k + .5)/10
            uv.data[li].uv = (side, s / segs)
        poly.use_smooth = True
    ob = link(bpy.data.objects.new(name, me))
    # turn the wheel so the chosen digit is on top: digit k centre sits at angle (k + .5)/10 * 2pi
    ob.rotation_euler = (-(int(digit) + 0.5) / 10 * 2 * math.pi, 0, 0)
    ob.location = (x, WIN_Y, TOP - 0.0003 - WHEEL_R)
    return ob


def look(ob, target):
    f = (Vector(target) - ob.location).normalized()
    r = f.cross(Vector((0, 0, 1))).normalized()
    u = r.cross(f)
    ob.rotation_euler = Matrix((r, u, -f)).transposed().to_euler()


def area(name, loc, target, size, energy, colour=(1, 1, 1), size_y=None):
    l = bpy.data.lights.new(name, "AREA"); l.size = size; l.energy = energy; l.color = colour
    if size_y:
        l.shape = "RECTANGLE"; l.size_y = size_y
    o = link(bpy.data.objects.new(name, l))
    o.location = loc; look(o, target)
    return o


def card(name, loc, target, w, h, strength, colour=(1, 1, 1)):
    """A panel only reflections can see: it gives the chrome something to mirror."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
    o = link(bpy.data.objects.new(name, me)); o.location = loc; look(o, target)
    m, nt, p = mat(name)
    p.inputs["Base Color"].default_value = (0, 0, 0, 1)
    p.inputs["Emission Color"].default_value = (*colour, 1); p.inputs["Emission Strength"].default_value = strength
    me.materials.append(m)
    o.visible_camera = False; o.visible_diffuse = False; o.visible_shadow = False; o.visible_transmission = False
    return o


SHOTS = {
    1: dict(target=(0.0, -0.006, 0.012), dist=0.28, az=22, el=33, lens=85, f=11, focus=(0.0, -0.004, 0.015), shift=(0.012, 0.15)),
    2: dict(target=(0.0118, WIN_Y, TOP - 0.001), dist=0.125, az=22, el=38, lens=100, f=14, focus=(0.0105, WIN_Y - 0.001, TOP - 0.0004), shift=(0.0, 0.17)),
    3: dict(target=(0.0, -0.008, TOP), dist=0.285, az=22, el=52, lens=100, f=10, focus=(0.0, -0.0098, TOP + 0.0004), shift=(0.055, 0.19), label=True),
}


def build(frame, quality):
    shot = SHOTS[frame]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 128 if final else 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 10
    sc.cycles.sample_clamp_indirect = 8.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.05, 0.045, 0.045, 1)
    bg.inputs["Strength"].default_value = 1.0

    # table running back and curving up into the wall, one colour
    prof = [(-4.0, 0.0), (0.30, 0.0)]
    Rs = 0.40
    for j in range(1, 25):
        a = math.pi / 2 * j / 24
        prof.append((0.30 + Rs * math.sin(a), Rs * (1 - math.cos(a))))
    prof.append((0.70, 4.0))
    verts = [(x, y, z) for (y, z) in prof for x in (-6.0, 6.0)]
    faces = [(2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2) for j in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    link(bpy.data.objects.new("sweep", me))
    sm, snt, sp = mat("pink")
    sp.inputs["Base Color"].default_value = (*PINK, 1)
    sp.inputs["Roughness"].default_value = 0.75
    sp.inputs["Specular IOR Level"].default_value = 0.2
    nz = snt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 3
    bump = snt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.0002
    snt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); snt.links.new(bump.outputs["Normal"], sp.inputs["Normal"])
    me.materials.append(sm)

    satin, snt2, sp2 = mat("satin")
    sp2.inputs["Base Color"].default_value = (0.80, 0.80, 0.81, 1)
    sp2.inputs["Metallic"].default_value = 1.0
    sp2.inputs["Roughness"].default_value = 0.20
    sp2.inputs["Anisotropic"].default_value = 0.6
    blk, _, bp = mat("black")
    bp.inputs["Base Color"].default_value = (0.012, 0.012, 0.014, 1); bp.inputs["Roughness"].default_value = 0.55
    # chrome, with the faintest brushed variation so it is not a perfect mirror
    cm, cnt, cp = mat("chrome")
    cp.inputs["Base Color"].default_value = (0.86, 0.86, 0.87, 1)
    cp.inputs["Metallic"].default_value = 1.0
    cp.inputs["Roughness"].default_value = 0.075
    cz = cnt.nodes.new("ShaderNodeTexNoise"); cz.inputs["Scale"].default_value = 3000; cz.inputs["Detail"].default_value = 2
    cb = cnt.nodes.new("ShaderNodeBump"); cb.inputs["Strength"].default_value = 0.03; cb.inputs["Distance"].default_value = 0.00002
    cnt.links.new(cz.outputs["Fac"], cb.inputs["Height"]); cnt.links.new(cb.outputs["Normal"], cp.inputs["Normal"])


    # body: a short drum with rounded edges; the window cut out of the face
    body = cylinder("body", R, TOP - 0.002); body.location = (0, 0, 0.002 + (TOP - 0.002) / 2)
    for p in body.data.polygons:
        p.use_smooth = True
        p.material_index = 1 if p.normal.z > 0.5 else 0   # the face is satin, the rest polished
    bv = bevel(body, 0.0042, 12); bv.harden_normals = True
    cut = box("cut", WIN[0], WIN[1], 0.03); cut.location = (0, WIN_Y, TOP + 0.003)
    for p in cut.data.polygons:
        p.use_smooth = False
    b = body.modifiers.new("win", "BOOLEAN"); b.object = cut; b.operation = "DIFFERENCE"; b.solver = "EXACT"
    b.material_mode = "TRANSFER"
    cut.hide_render = True
    cut.data.materials.append(blk)
    body.data.materials.append(cm)
    body.data.materials.append(satin)
    # a thin raised bezel round the window
    bz = cylinder("feet", R * 0.62, 0.002, 96); bz.location = (0, 0, 0.001); bz.data.materials.append(cm)

    # inside the window: a black well and four wheels
    wm, wnt, wp = mat("wheel")
    tex = wnt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / "tex" / "wheel.png"))
    tex.interpolation = "Cubic"
    wnt.links.new(tex.outputs["Color"], wp.inputs["Base Color"])
    wp.inputs["Roughness"].default_value = 0.45
    for i, dg in enumerate(DIGITS):
        w = wheel(f"wheel{i}", dg, (i - 1.5) * PITCH)
        w.data.materials.append(wm)
    # glass over the window: thin, very clear, one reflection
    gm, _, gp = mat("glass")
    gp.inputs["Transmission Weight"].default_value = 1.0; gp.inputs["Roughness"].default_value = 0.0; gp.inputs["IOR"].default_value = 1.5
    # (no glass: it only mirrored the table back over the numbers)

    # the button, pointing away from us (+y), and the reset knob on the right
    st = cylinder("stem", 0.0032, 0.007, 64); st.rotation_euler = (math.pi / 2, 0, 0); st.location = (0, R + 0.0025, 0.0105)
    st.data.materials.append(cm)
    cap = cylinder("cap", 0.0068, 0.0048, 96); cap.rotation_euler = (math.pi / 2, 0, 0); cap.location = (0, R + 0.0075, 0.0105)
    bevel(cap, 0.0016, 6); cap.data.materials.append(cm)
    kn = cylinder("knob", 0.0052, 0.0055, 96); kn.rotation_euler = (0, math.pi / 2, 0); kn.location = (R + 0.0018, 0.004, 0.0105)
    bevel(kn, 0.0012, 5); kn.data.materials.append(cm)
    # the finger ring towards us, lying on the table, joined by a short lug
    ring = torus("ring", 0.0125, 0.0024); ring.location = (0, -(R + 0.0125 + 0.0012), 0.0024); ring.data.materials.append(cm)
    lug = box("lug", 0.006, 0.006, 0.0048); lug.location = (0, -(R + 0.0006), 0.0034); bevel(lug, 0.0012, 4)
    lug.data.materials.append(cm)

    if shot.get("label"):
        # embossed label tape stuck across the face below the window
        TW, TH = 0.0295, 0.0065
        lm, lnt, lp = mat("tape")
        N, L = lnt.nodes, lnt.links
        tc = N.new("ShaderNodeTexImage"); tc.image = bpy.data.images.load(str(HERE / "tex" / "dymo.png")); tc.interpolation = "Cubic"
        th = N.new("ShaderNodeTexImage"); th.image = bpy.data.images.load(str(HERE / "tex" / "dymo-h.png")); th.interpolation = "Cubic"
        th.image.colorspace_settings.name = "Non-Color"
        L.new(tc.outputs["Color"], lp.inputs["Base Color"])
        bmp = N.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = 0.9; bmp.inputs["Distance"].default_value = 0.0003
        L.new(th.outputs["Color"], bmp.inputs["Height"]); L.new(bmp.outputs["Normal"], lp.inputs["Normal"])
        lp.inputs["Roughness"].default_value = 0.32
        lp.inputs["Coat Weight"].default_value = 0.5; lp.inputs["Coat Roughness"].default_value = 0.2
        tme = bpy.data.meshes.new("tape")
        nx = 60
        vs, fs, uvl = [], [], []
        for i in range(nx + 1):
            u = i / nx
            for j in (0, 1):
                vs.append(((u - 0.5) * TW, (j - 0.5) * TH, 0.0))
        for i in range(nx):
            a = 2 * i
            fs.append((a, a + 2, a + 3, a + 1))
        tme.from_pydata(vs, [], fs)
        uv = tme.uv_layers.new()
        for poly in tme.polygons:
            for li in poly.loop_indices:
                vi = tme.loops[li].vertex_index
                i, j = divmod(vi, 2)
                uv.data[li].uv = (i / nx, j)
        tape = link(bpy.data.objects.new("tape", tme)); tape.data.materials.append(lm)
        tape.location = (0.0, -0.0098, TOP + 0.00035); tape.rotation_euler = (0, 0, math.radians(-2.2))
        sol = tape.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.0003; sol.offset = -1

    # light: a soft box low on the left so the counter throws a long shadow over the table, a strip behind on
    # the right for a rim, a little fill from the front
    area("key", (-0.55, -0.10, 0.20), (0, 0, 0.01), 0.40, 30, (1.0, 0.97, 0.93))
    area("rim", (0.40, 0.42, 0.28), (0, 0, 0.01), 0.18, 7, (0.93, 0.96, 1.0), size_y=0.6)
    area("fill", (0.40, -0.55, 0.25), (0, 0, 0.01), 0.9, 2.5, (1.0, 0.97, 0.96))
    # things for the chrome to mirror: one tall white card on the left, a dark one overhead-right, a warm low strip
    card("c1", (-0.18, -0.10, 0.12), (0, 0, 0.01), 0.10, 0.40, 3.0)
    card("c2", (0.10, 0.20, 0.30), (0, 0, 0.01), 0.40, 0.08, 1.2, (1.0, 0.95, 0.92))
    # a big dark board behind and above, so the face mirrors dark with one white strip across it, not the pink wall
    card("dark", (0.0, 0.32, 0.20), (0, 0, 0.01), 0.9, 0.35, 0.0)
    card("strip", (-0.08, 0.30, 0.095), (0, 0, 0.01), 0.9, 0.022, 4.0)

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 36
    az, el = math.radians(shot["az"]), math.radians(shot["el"])
    tg = Vector(shot["target"])
    co.location = tg + shot["dist"] * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    look(co, tg)
    cam.lens = shot["lens"]
    cam.shift_x, cam.shift_y = shot["shift"]
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"]
    cam.clip_start = 0.005

    exr = str(TMP / f"nx-tally-{frame}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def pixels(exr):
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32), w, h


def grade(exr, frame, quality):
    """A film curve, the top of the frame falling off (Instagram's white name sits there), and grain."""
    from PIL import Image
    a, w, h = pixels(exr)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    a = np.clip(a, 0, None)
    x = a * EXPOSURE
    x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    yy, xx = np.mgrid[0:H, 0:W]
    top = np.clip(1 - yy / 330.0, 0, 1) ** 1.6
    x *= (1 - 0.30 * top)[..., None]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.12 * np.clip(r - 0.6, 0, 1) ** 1.5)[..., None]
    rng = np.random.default_rng(frame)
    x += rng.normal(0, 0.008, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"render-{frame:02d}.jpg" if quality == "final" else f".draft-{frame:02d}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst)


EXPOSURE = 0.62

if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 and args[1] in ("draft", "final") else "draft"
    regrade = "regrade" in args
    for fr in ([1, 2, 3] if which == "all" else [int(which)]):
        exr = str(TMP / f"nx-tally-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
