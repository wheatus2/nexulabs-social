"""Renders the pictures for this Reel with Blender's Python module
(python3.13 -m pip install bpy brotli scipy pillow numpy --break-system-packages).

Branding for a made-up soap maker (Tidewrack Soap Co.): bars of bottle-green soap on a sand sweep.
  1  three blank bars, one leaning on two: good soap, no name
  2  right up against the leaning bar's face as the name presses in (states a to g, the die going deeper)
  3  the same bar in its paper band, a bare pressed bar lying in front
  4  banded bars standing in a row, arriving one at a time (states a to e)

  python3.13 build.py <shot> <state|all> [draft|final] [regrade]
writes art/r-<shot><state>.jpg (1134x2016; the Reel shows them at 1080x1920 and pushes in a little).
The artwork (die and band print) comes from prints.py. The type is set over the pictures in reel.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix
from PIL import Image, ImageFilter
from scipy.ndimage import map_coordinates

HERE = Path(__file__).resolve().parent
W, H = 1134, 2016
TMP = Path(tempfile.gettempdir())

# the bar, in metres: 90 x 58 x 26mm, a pillow with a pressed top
A, B, T = 0.045, 0.029, 0.013
RC, RF = 0.011, 0.006            # plan corner radius, edge fillet
CROWN = 0.0013
DEPTH = 0.0011
PT = 0.0004                      # the paper sits this far off the soap
BAND = 0.056

SAND = (0.560, 0.395, 0.225)
SOAP = (0.008, 0.072, 0.042)


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def look(ob, target):
    f = (Vector(target) - ob.location).normalized()
    r = f.cross(Vector((0, 0, 1))).normalized()
    u = r.cross(f)
    ob.rotation_euler = Matrix((r, u, -f)).transposed().to_euler()


def area(name, loc, target, size, energy, colour=(1, 1, 1), size_y=None):
    l = bpy.data.lights.new(name, "AREA"); l.size = size; l.energy = energy; l.color = colour
    if size_y:
        l.shape = "RECTANGLE"; l.size_y = size_y
    o = bpy.data.objects.new(name, l); bpy.context.scene.collection.objects.link(o)
    o.location = loc; look(o, target)
    return o


# ---------------------------------------------------------------- the bar
def sdf(x, y):
    qx, qy = np.abs(x) - (A - RC), np.abs(y) - (B - RC)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - RC


_die = None


def die():
    """The die as a height map, 0 to 1, with a soft shoulder."""
    global _die
    if _die is None:
        im = Image.open(HERE / "die.png").convert("L").filter(ImageFilter.GaussianBlur(4.2))
        a = np.asarray(im, dtype=np.float32) / 255.0
        t = np.clip((a - 0.16) / (0.84 - 0.16), 0, 1)
        _die = t * t * (3 - 2 * t)
    return _die


_meshes = {}


def bar_mesh(n, depth):
    key = (n, round(depth, 4))
    if key in _meshes:
        return _meshes[key]
    k = 2 * n + 1
    u, v = np.meshgrid(np.linspace(-1, 1, k), np.linspace(-1, 1, k), indexing="ij")
    m = np.maximum(np.abs(u), np.abs(v))
    ln = np.hypot(u, v); ln[n, n] = 1.0
    dx, dy = u / ln, v / ln
    lo, hi = np.zeros_like(m), np.full_like(m, A + B)
    for _ in range(44):
        mid = (lo + hi) / 2
        inside = sdf(mid * dx, mid * dy) < 0
        lo = np.where(inside, mid, lo); hi = np.where(inside, hi, mid)
    s = lo * np.sin(np.pi * m / 2)
    x, y = s * dx, s * dy
    d = np.clip(-sdf(x, y), 0, None)
    d[m >= 1.0] = 0.0
    zf = np.where(d < RF, np.sqrt(np.clip(RF ** 2 - (RF - d) ** 2, 0, None)), RF)
    cx = np.clip(1 - (x / (A - RF)) ** 2, 0, 1) ** 2
    cy = np.clip(1 - (y / (B - RF)) ** 2, 0, 1) ** 2
    top = (T - RF) + zf + CROWN * cx * cy
    if depth > 0:
        hm = die()
        hh, hw = hm.shape
        px = (x + A) / (2 * A) * (hw - 1)
        py = (B - y) / (2 * B) * (hh - 1)
        top = top - depth * DEPTH * map_coordinates(hm, [py, px], order=1, mode="nearest")
    bot = -(T - RF) - zf
    vt = np.stack([x, y, top], -1).reshape(-1, 3)
    vb = np.stack([x, y, bot], -1).reshape(-1, 3)
    idx = np.arange(k * k).reshape(k, k)
    q = np.stack([idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]], -1).reshape(-1, 4)
    qb = q[:, ::-1] + k * k
    per = np.concatenate([idx[:-1, 0], idx[-1, :-1], idx[:0:-1, -1], idx[0, :0:-1]])
    nxt = np.roll(per, -1)
    wall = np.stack([per, per + k * k, nxt + k * k, nxt], -1)
    faces = np.concatenate([q, qb, wall])
    me = bpy.data.meshes.new(f"bar{n}-{depth}")
    me.from_pydata(np.concatenate([vt, vb]).tolist(), [], faces.tolist())
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.update()
    _meshes[key] = me
    return me


def soap_material():
    m, nt, p = mat("soap")
    N, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (*SOAP, 1)
    p.inputs["Specular IOR Level"].default_value = 0.5
    p.inputs["Subsurface Weight"].default_value = 0.40
    p.inputs["Subsurface Radius"].default_value = (0.35, 1.0, 0.6)
    p.inputs["Subsurface Scale"].default_value = 0.0035
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60; nz.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    rr = N.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.42; rr.inputs["To Max"].default_value = 0.58
    L.new(nz.outputs["Fac"], rr.inputs["Value"]); L.new(rr.outputs[0], p.inputs["Roughness"])
    # milled soap: a very fine tooth, and a slow unevenness under it
    n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 2600; n2.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], n2.inputs["Vector"])
    b1 = N.new("ShaderNodeBump"); b1.inputs["Strength"].default_value = 0.10; b1.inputs["Distance"].default_value = 0.00008
    L.new(n2.outputs["Fac"], b1.inputs["Height"])
    n3 = N.new("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 45; n3.inputs["Detail"].default_value = 2
    L.new(tc.outputs["Object"], n3.inputs["Vector"])
    b2 = N.new("ShaderNodeBump"); b2.inputs["Strength"].default_value = 0.12; b2.inputs["Distance"].default_value = 0.0005
    L.new(n3.outputs["Fac"], b2.inputs["Height"]); L.new(b1.outputs["Normal"], b2.inputs["Normal"])
    L.new(b2.outputs["Normal"], p.inputs["Normal"])
    # sea kelp in it: sparse dark flecks, and the colour never quite even
    vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 520; vo.inputs["Randomness"].default_value = 1.0
    L.new(tc.outputs["Object"], vo.inputs["Vector"])
    pick = N.new("ShaderNodeTexWhiteNoise"); L.new(vo.outputs["Color"], pick.inputs["Vector"])
    sel = N.new("ShaderNodeMath"); sel.operation = "GREATER_THAN"; sel.inputs[1].default_value = 0.90
    L.new(pick.outputs["Value"], sel.inputs[0])
    dot = N.new("ShaderNodeMath"); dot.operation = "LESS_THAN"; dot.inputs[1].default_value = 0.22
    L.new(vo.outputs["Distance"], dot.inputs[0])
    both = N.new("ShaderNodeMath"); both.operation = "MULTIPLY"; L.new(dot.outputs[0], both.inputs[0]); L.new(sel.outputs[0], both.inputs[1])
    fk = N.new("ShaderNodeMath"); fk.operation = "MULTIPLY"; fk.inputs[1].default_value = 0.8; L.new(both.outputs[0], fk.inputs[0])
    n4 = N.new("ShaderNodeTexNoise"); n4.inputs["Scale"].default_value = 28; n4.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], n4.inputs["Vector"])
    mot = N.new("ShaderNodeMix"); mot.data_type = "RGBA"
    mot.inputs["A"].default_value = (SOAP[0] * 0.80, SOAP[1] * 0.84, SOAP[2] * 0.84, 1); mot.inputs["B"].default_value = (SOAP[0] * 1.2, SOAP[1] * 1.16, SOAP[2] * 1.14, 1)
    L.new(n4.outputs["Fac"], mot.inputs["Factor"])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs["B"].default_value = (0.004, 0.022, 0.014, 1)
    L.new(mot.outputs["Result"], mix.inputs["A"]); L.new(fk.outputs[0], mix.inputs["Factor"])
    L.new(mix.outputs["Result"], p.inputs["Base Color"])
    return m


# ---------------------------------------------------------------- the paper band
def band_loop(steps=14):
    """The band's cross-section, from the middle of the underside, up the front, over the top and down the back."""
    bb, tt, rr = B + PT, T + PT, RF + PT
    pts = [(0.0, -tt)]
    for j in range(steps + 1):
        a = math.radians(-90 - 90 * j / steps)
        pts.append((-(bb - rr) + rr * math.cos(a), -(tt - rr) + rr * math.sin(a)))
    for j in range(steps + 1):
        a = math.radians(180 - 90 * j / steps)
        pts.append((-(bb - rr) + rr * math.cos(a), (tt - rr) + rr * math.sin(a)))
    for j in range(1, 40):
        y = -(bb - rr) + 2 * (bb - rr) * j / 40
        pts.append((y, tt + CROWN * (1 - (y / (bb - rr)) ** 2) ** 2))
    for j in range(steps + 1):
        a = math.radians(90 - 90 * j / steps)
        pts.append(((bb - rr) + rr * math.cos(a), (tt - rr) + rr * math.sin(a)))
    for j in range(steps + 1):
        a = math.radians(0 - 90 * j / steps)
        pts.append(((bb - rr) + rr * math.cos(a), -(tt - rr) + rr * math.sin(a)))
    pts.append((0.0, -tt))
    s = [0.0]
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        s.append(s[-1] + math.hypot(y1 - y0, z1 - z0))
    return pts, s


def band_print():
    """One strip of paper: the top panel over the middle of the top, a green panel on each wall."""
    pts, s = band_loop()
    Lm = s[-1]
    ppm = 20000.0
    hpx = int(round(Lm * ppm))
    im = Image.new("RGB", (1120, hpx), "#EBE2CC")
    top = Image.open(HERE / "band-top.png").convert("RGB")
    side = Image.open(HERE / "band-side.png").convert("RGB")
    def at(sv):
        return int(round((1 - sv / Lm) * hpx))
    s_top = Lm / 2
    arc = (RF + PT) * math.pi / 2
    s_front = (B - RF) + arc + (T - RF)
    s_back = Lm - s_front
    im.paste(top, (0, at(s_top) - top.size[1] // 2))
    im.paste(side, (0, at(s_front) - side.size[1] // 2))
    im.paste(side, (0, at(s_back) - side.size[1] // 2))
    dst = HERE / ".band.png"; im.save(dst)
    return dst


def band_object(name, material):
    pts, s = band_loop()
    Lm = s[-1]
    xs = [-BAND / 2 + BAND * i / 6 for i in range(7)]
    verts = [(x, y, z) for (y, z) in pts for x in xs]
    faces, uvs = [], []
    for j in range(len(pts) - 1):
        for i in range(6):
            a = j * 7 + i
            faces.append((a, a + 1, a + 8, a + 7))
            uvs += [(i / 6, s[j] / Lm), ((i + 1) / 6, s[j] / Lm), ((i + 1) / 6, s[j + 1] / Lm), (i / 6, s[j + 1] / Lm)]
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name="uv")
    for l, c in zip(uv.data, uvs):
        l.uv = c
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    so = ob.modifiers.new("t", "SOLIDIFY"); so.thickness = 0.0003; so.offset = 1.0
    return ob


def paper_material():
    m, nt, p = mat("paper")
    N, L = nt.nodes, nt.links
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(band_print())); tex.extension = "EXTEND"
    L.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.78
    p.inputs["Specular IOR Level"].default_value = 0.25
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1400; nz.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    b = N.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.10; b.inputs["Distance"].default_value = 0.00015
    L.new(nz.outputs["Fac"], b.inputs["Height"]); L.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


M = {}


def bar(name, loc, rz=0.0, alpha=0.0, depth=0.0, n=150, band=False):
    """alpha tips the bar up about its long edge, its face turning to the camera; rz turns it on the table."""
    if "soap" not in M:
        M["soap"] = soap_material()
    me = bar_mesh(n, depth)
    if not me.materials:
        me.materials.append(M["soap"])
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.rotation_mode = "ZXY"
    ob.rotation_euler = (math.radians(alpha), 0, math.radians(rz))
    ob.location = loc
    if band:
        if "paper" not in M:
            M["paper"] = paper_material()
        bd = band_object(name + "-band", M["paper"])
        bd.parent = ob
    return ob


def rest_height(alpha):
    a = math.radians(alpha)
    return (B - RF) * abs(math.sin(a)) + (T - RF) * abs(math.cos(a)) + RF


# ---------------------------------------------------------------- the set
LEAN = 64.0


def lean_set(state_depth, banded, blank_others, front=True):
    """One bar leaning on a stack of two, and one lying in front to the right."""
    a = math.radians(LEAN)
    pad = PT if banded else 0.0
    cz = rest_height(LEAN) + pad
    cy = 0.0
    p0y, p0z = cy + (T + pad) * math.sin(a), cz - (T + pad) * math.cos(a)
    fz = 4 * T - RF
    fy = p0y + (RF + math.cos(a) * (fz - p0z)) / math.sin(a)
    sy = fy - RF + B
    d_other = 0.0 if blank_others else 1.0
    bar("lean", (0, cy, cz), 0, LEAN, depth=0.0 if banded else state_depth, n=120 if banded else 400, band=banded)
    bar("stack1", (0.006, sy + 0.004, T), 5, 0, depth=0.0, n=120)
    bar("stack2", (0.0, sy, 3 * T), 0, 0, depth=d_other, n=400 if d_other else 120)
    if front:
        bar("front", (0.074, -0.082, T), 24, 0, depth=d_other, n=400)


ROW = [(0.030, -0.040, -3), (-0.018, 0.035, 4), (-0.066, 0.110, -2), (-0.114, 0.185, 3), (-0.162, 0.260, -4)]


def row_set(count):
    """Banded bars standing on their long edge, one behind another."""
    for i, (x, y, rz) in enumerate(ROW[:count]):
        bar(f"row{i}", (x, y, B + PT), rz, 90, depth=0.0, n=120, band=True)


SHOTS = {
    "1": dict(target=(0.030, -0.02, 0.034), dist=0.62, az=26, el=12, lens=85, f=11, focus=(0.0, -0.01, 0.04), shift=(0.0, 0.10),
              key=((-0.70, -0.10, 0.22), 0.45, 60)),
    "2": dict(target=(0.0, 0.0, 0.034), dist=0.47, az=15, el=24, lens=85, f=16, focus=(0.0, -0.012, 0.036), shift=(0.006, 0.10),
              key=((-0.70, -0.10, 0.20), 0.40, 60)),
    "3": dict(target=(0.0, 0.0, 0.036), dist=0.52, az=38, el=20, lens=85, f=11, focus=(0.0, -0.012, 0.036), shift=(-0.01, 0.10),
              key=((-0.70, -0.10, 0.22), 0.45, 60)),
    "4": dict(target=(-0.060, 0.06, 0.030), dist=0.78, az=40, el=10, lens=85, f=8, focus=(0.030, -0.066, 0.030), shift=(0.02, 0.10),
              key=((-0.80, -0.25, 0.30), 0.80, 80)),
}
STATES = {"1": ["a"], "2": list("abcdefg"), "3": ["a"], "4": list("abcd")}
PRESS = {"a": 0.0, "b": 0.10, "c": 0.28, "d": 0.50, "e": 0.72, "f": 0.90, "g": 1.0}


def build(shot_id, state, quality):
    shot = SHOTS[shot_id]
    M.clear(); _meshes.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    hero = final and state == STATES[shot_id][-1]
    sc.cycles.samples = (112 if hero else 48) if final else 20
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 4.0; sc.cycles.sample_clamp_direct = 12.0
    sc.render.threads_mode = "FIXED"; sc.render.threads = 4
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 36
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.55, 0.47, 0.36, 1)
    bg.inputs["Strength"].default_value = 0.08

    prof = [(-4.0, 0.0), (1.6, 0.0)]
    R = 1.4
    for j in range(1, 25):
        a = math.pi / 2 * j / 24
        prof.append((1.6 + R * math.sin(a), R * (1 - math.cos(a))))
    prof.append((3.0, 7.0))
    verts = [(x, y, z) for (y, z) in prof for x in (-7.0, 7.0)]
    faces = [(2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2) for j in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    sweep = bpy.data.objects.new("sweep", me); sc.collection.objects.link(sweep)
    sm, snt, sp = mat("sweep")
    sp.inputs["Base Color"].default_value = (*SAND, 1)
    sp.inputs["Roughness"].default_value = 0.80
    sp.inputs["Specular IOR Level"].default_value = 0.2
    nz = snt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 3
    bump = snt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.0002
    snt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); snt.links.new(bump.outputs["Normal"], sp.inputs["Normal"])
    me.materials.append(sm)

    if shot_id == "1":
        lean_set(0.0, False, True)
    elif shot_id == "2":
        lean_set(PRESS[state], False, True, front=False)
    elif shot_id == "3":
        lean_set(0.0, True, True, front=False)
    else:
        row_set("abcde".index(state) + 1)

    kl, ks, ke = shot["key"]
    area("key", kl, (0, 0.0, 0.03), ks, ke, (1.0, 0.96, 0.90))
    area("rim", (0.50, 0.60, 0.35), (0, 0.03, 0.03), 0.25, 14, (0.94, 0.97, 1.0), size_y=0.8)
    area("fill", (0.50, -0.70, 0.30), (0, 0, 0.03), 1.0, 3.0, (0.97, 0.98, 1.0))
    area("wall", (0.0, 0.9, 2.6), (0, 3.0, 1.6), 3.0, 600, (1.0, 0.97, 0.92))
    # a window that only the shine sees
    for i, (dx, wdt) in enumerate(((-0.10, 0.17), (0.11, 0.20))):
        cmh = bpy.data.meshes.new("card"); cmh.from_pydata([(0, -wdt / 2, 0), (0, wdt / 2, 0), (0, wdt / 2, 0.60), (0, -wdt / 2, 0.60)], [], [(0, 1, 2, 3)])
        cd = bpy.data.objects.new("card", cmh); sc.collection.objects.link(cd)
        cd.rotation_euler = (0, math.radians(-18), math.radians(40))
        cd.location = (-0.42 - dx * math.sin(math.radians(40)), -0.30 + dx * math.cos(math.radians(40)), 0.03)
        em, ent, ep = mat("cardm"); ep.inputs["Emission Color"].default_value = (1, 0.98, 0.95, 1); ep.inputs["Emission Strength"].default_value = 2.0
        ep.inputs["Base Color"].default_value = (0, 0, 0, 1); cmh.materials.append(em)
        cd.visible_camera = False; cd.visible_diffuse = False; cd.visible_shadow = False; cd.visible_transmission = False

    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
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
    cam.clip_start = 0.01

    exr = str(TMP / f"nx-soap-{shot_id}{state}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def pixels(exr):
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32), w, h


EXPOSURE = 0.50


def grade(exr, shot_id, state, quality):
    a, w, h = pixels(exr)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    a = np.clip(a, 0, None)
    x = a * EXPOSURE
    x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.10 * np.clip(r - 0.6, 0, 1) ** 1.5)[..., None]
    rng = np.random.default_rng(int(shot_id))
    x += rng.normal(0, 0.006, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"r-{shot_id}{state}.jpg" if quality == "final" else f".draft-{shot_id}{state}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst, flush=True)


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    shot_id, which = args[0], args[1]
    quality = args[2] if len(args) > 2 and args[2] in ("draft", "final") else "draft"
    regrade = "regrade" in args
    for st in (STATES[shot_id] if which == "all" else list(which)):
        exr = str(TMP / f"nx-soap-{shot_id}{st}.exr")
        grade(exr if regrade else build(shot_id, st, quality), shot_id, st, quality)
