"""Renders the three pictures for this Story with Blender's Python module (pip install bpy brotli scipy).

Two white eggs in two glazed ink-black egg cups on a lilac sweep. Each egg carries an ink stamp, the way UK
eggs carry a date: one says (c) 2019, the other (c) 2026 (stamp.py prints them). The year at the bottom of a
homepage, read like a best-before date.
  1  both eggs, low and from the right: which one's fresh?
  2  right up against the 2019 stamp, the 2026 egg a blur in front of it
  3  the 2026 egg, nearer and higher, the 2019 one gone soft behind it

  python3 build.py <frame 1|2|3|all> [draft|final] [regrade]
writes art/render-0N.jpg (1080x1920). The type is set over it in slide-0N.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())

LILAC = (0.47, 0.40, 0.80)          # the sweep, linear RGB
INK = (0.010, 0.008, 0.020)         # the egg cups' glaze
SHELL = (0.80, 0.765, 0.70)
RED = (0.30, 0.004, 0.014)          # the stamp ink

EGG_H, EGG_R = 0.057, 0.0218
CUP_Z = 0.026                       # where the bottom of the egg sits inside the cup
STAMP_W, STAMP_Z = 0.025, 0.030     # stamp width, and its centre measured up the egg
EGGS = {"2019": -0.031, "2026": 0.031}


def egg_profile(n=90):
    pts = []
    for j in range(n + 1):
        t = math.pi * j / n
        z = EGG_H * (1 - math.cos(t)) / 2
        r = EGG_R * math.sin(t) * (1 + 0.13 * math.cos(t)) / 1.0
        pts.append((max(r, 0.0), z))
    pts[0] = (0.0, 0.0); pts[-1] = (0.0, EGG_H)
    return pts


def egg_r_at(z):
    p = egg_profile(400)
    zs = [q[1] for q in p]; rs = [q[0] for q in p]
    return float(np.interp(z, zs, rs))


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def lathe(name, profile, segs=160):
    verts, faces = [], []
    for (r, z) in profile:
        for s in range(segs):
            a = 2 * math.pi * s / segs
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for p in range(len(profile) - 1):
        for s in range(segs):
            a = p * segs + s; b = p * segs + (s + 1) % segs
            faces.append((a, b, b + segs, a + segs))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for poly in me.polygons:
        poly.use_smooth = True
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob


def rounded(points, rad=0.0012, n=6):
    out = [points[0]]
    for a, b, c in zip(points, points[1:], points[2:]):
        A, B, C = Vector(a), Vector(b), Vector(c)
        d1, d2 = (A - B).normalized(), (C - B).normalized()
        r = min(rad, (A - B).length / 2.2, (C - B).length / 2.2)
        p1, p2 = B + d1 * r, B + d2 * r
        for j in range(n + 1):
            u = j / n
            out.append(tuple((1 - u) ** 2 * p1 + 2 * u * (1 - u) * B + u ** 2 * p2))
    out.append(points[-1])
    return out


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


def shell_material(year):
    """Eggshell: chalky, a little light through it, fine pores; the stamp printed on the front by projection."""
    m, nt, p = mat(f"shell-{year}")
    N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.62
    p.inputs["Specular IOR Level"].default_value = 0.32
    p.inputs["Subsurface Weight"].default_value = 0.35
    p.inputs["Subsurface Radius"].default_value = (0.9, 0.75, 0.6)
    p.inputs["Subsurface Scale"].default_value = 0.0025
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    sh = STAMP_W * 768 / 2048
    u = N.new("ShaderNodeMath"); u.operation = "MULTIPLY_ADD"; u.inputs[1].default_value = 1 / STAMP_W; u.inputs[2].default_value = 0.5
    L.new(sep.outputs["X"], u.inputs[0])
    v = N.new("ShaderNodeMath"); v.operation = "MULTIPLY_ADD"; v.inputs[1].default_value = 1 / sh; v.inputs[2].default_value = 0.5 - STAMP_Z / sh
    L.new(sep.outputs["Z"], v.inputs[0])
    cmb = N.new("ShaderNodeCombineXYZ"); L.new(u.outputs[0], cmb.inputs[0]); L.new(v.outputs[0], cmb.inputs[1])
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / "tex" / f"stamp-{year}.png"))
    tex.extension = "CLIP"; tex.interpolation = "Cubic"
    L.new(cmb.outputs[0], tex.inputs[0])
    front = N.new("ShaderNodeMath"); front.operation = "LESS_THAN"; front.inputs[1].default_value = -0.004
    L.new(sep.outputs["Y"], front.inputs[0])
    mask = N.new("ShaderNodeMath"); mask.operation = "MULTIPLY"
    L.new(tex.outputs["Alpha"], mask.inputs[0]); L.new(front.outputs[0], mask.inputs[1])
    # the shell itself is not one flat white: a faint mottle
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 140; nz.inputs["Detail"].default_value = 4
    tint = N.new("ShaderNodeMix"); tint.data_type = "RGBA"
    tint.inputs["A"].default_value = (*SHELL, 1); tint.inputs["B"].default_value = (SHELL[0] * 0.95, SHELL[1] * 0.93, SHELL[2] * 0.90, 1)
    L.new(nz.outputs["Fac"], tint.inputs["Factor"])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
    L.new(mask.outputs[0], mix.inputs["Factor"]); L.new(tint.outputs["Result"], mix.inputs["A"]); mix.inputs["B"].default_value = (*RED, 1)
    L.new(mix.outputs["Result"], p.inputs["Base Color"])
    # pores: a very fine bump
    pz = N.new("ShaderNodeTexNoise"); pz.inputs["Scale"].default_value = 2600; pz.inputs["Detail"].default_value = 2
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.10; bump.inputs["Distance"].default_value = 0.00004
    L.new(pz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def cup_profile():
    rim = egg_r_at(0.047 - CUP_Z) + 0.0016          # the rim sits just clear of the egg
    outer = [(0.0, 0.0), (0.0225, 0.0), (0.0225, 0.0035), (0.0105, 0.0105), (0.0085, 0.017),
             (0.0125, 0.026), (rim + 0.0025, 0.0405), (rim + 0.0021, 0.047)]
    inner = [(rim, 0.047), (rim - 0.0012, 0.040), (egg_r_at(0.004) * 0.7, CUP_Z + 0.002), (0.0, CUP_Z + 0.0015)]
    return rounded(outer + inner, 0.0014)


SHOTS = {
    1: dict(target=(0.0, 0.0, 0.045), dist=0.53, az=14, el=12, lens=85, f=11, focus=(0.0, -0.01, 0.05), shift=(-0.005, 0.12)),
    2: dict(target=(-0.031, -0.018, 0.058), dist=0.150, az=16, el=8, lens=100, f=4.0, focus=(-0.031, -0.021, 0.057), shift=(0.10, -0.05)),
    3: dict(target=(0.031, 0.0, 0.045), dist=0.38, az=20, el=18, lens=100, f=5.6, focus=(0.031, -0.020, 0.055), shift=(-0.07, -0.20), only="2026"),
}


def build(frame, quality):
    shot = SHOTS[frame]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 100 if final else 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 8.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.30, 0.26, 0.45, 1)
    bg.inputs["Strength"].default_value = 0.05

    # the table runs back and curves up into the wall, in one colour
    prof = [(-4.0, 0.0), (0.35, 0.0)]
    R = 0.45
    for j in range(1, 25):
        a = math.pi / 2 * j / 24
        prof.append((0.35 + R * math.sin(a), R * (1 - math.cos(a))))
    prof.append((0.80, 4.0))
    verts = [(x, y, z) for (y, z) in prof for x in (-6.0, 6.0)]
    faces = [(2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2) for j in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    sweep = bpy.data.objects.new("sweep", me); sc.collection.objects.link(sweep)
    sm, snt, sp = mat("lilac")
    sp.inputs["Base Color"].default_value = (*LILAC, 1)
    sp.inputs["Roughness"].default_value = 0.7
    sp.inputs["Specular IOR Level"].default_value = 0.25
    nz = snt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 700; nz.inputs["Detail"].default_value = 3
    bump = snt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.04; bump.inputs["Distance"].default_value = 0.0002
    snt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); snt.links.new(bump.outputs["Normal"], sp.inputs["Normal"])
    me.materials.append(sm)

    cm, cnt, cp = mat("glaze")
    cp.inputs["Base Color"].default_value = (*INK, 1)
    cp.inputs["Roughness"].default_value = 0.22
    cp.inputs["Coat Weight"].default_value = 1.0
    cp.inputs["Coat Roughness"].default_value = 0.04

    cam_xy = None
    for year, x in EGGS.items():
        if shot.get("only") and year != shot["only"]:
            continue
        cup = lathe(f"cup-{year}", cup_profile())
        cup.location = (x, 0, 0); cup.data.materials.append(cm)
        egg = lathe(f"egg-{year}", egg_profile())
        egg.location = (x, 0, CUP_Z)
        egg.data.materials.append(shell_material(year))
        egg.shadow_terminator_geometry_offset = 0.3; egg.shadow_terminator_shading_offset = 0.05
        # turn the stamp to face this frame's camera
        az = math.radians(shot["az"]); el = math.radians(shot["el"])
        tg = Vector(shot["target"])
        cpos = tg + shot["dist"] * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
        d = Vector((cpos.x - x, cpos.y, 0)).normalized()
        egg.rotation_euler = (0, 0, math.atan2(d.x, -d.y) + math.radians({1: -6, 2: -10, 3: -8}[frame]))
        cam_xy = cpos

    # light: one soft box low on the left so the eggs throw long shadows across the table, a strip behind on the right
    # to rim the shells and the glaze, and a little fill from the front
    area("key", (-0.62, -0.12, 0.16), (0, 0, 0.04), 0.45, 34, (1.0, 0.97, 0.93))
    area("rim", (0.45, 0.45, 0.30), (0, 0, 0.05), 0.20, 6, (0.92, 0.95, 1.0), size_y=0.7)
    area("fill", (0.45, -0.55, 0.22), (0, 0, 0.04), 0.9, 3.0, (0.95, 0.95, 1.0))
    # a tall card that only the glaze sees, so the black cups carry one long clean highlight
    cmh = bpy.data.meshes.new("card"); cmh.from_pydata([(0, -0.15, 0), (0, 0.15, 0), (0, 0.15, 0.5), (0, -0.15, 0.5)], [], [(0, 1, 2, 3)])
    cd = bpy.data.objects.new("card", cmh); sc.collection.objects.link(cd); cd.location = (-0.30, -0.25, -0.05)
    cd.rotation_euler = (0, 0, math.radians(35))
    em, ent, ep = mat("card"); ep.inputs["Emission Color"].default_value = (1, 1, 1, 1); ep.inputs["Emission Strength"].default_value = 2.0
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

    exr = str(TMP / f"nx-egg-{frame}.exr")
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
    x *= (1 - 0.42 * top)[..., None]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.12 * np.clip(r - 0.6, 0, 1) ** 1.5)[..., None]
    rng = np.random.default_rng(frame)
    x += rng.normal(0, 0.008, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"render-{frame:02d}.jpg" if quality == "final" else f".draft-{frame:02d}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst)


EXPOSURE = 0.56

if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 and args[1] in ("draft", "final") else "draft"
    regrade = "regrade" in args
    for fr in ([1, 2, 3] if which == "all" else [int(which)]):
        exr = str(TMP / f"nx-egg-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
