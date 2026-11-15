"""Renders the pictures for this Reel with Blender's Python module (pip install bpy brotli).

One chrome counter bell on a lagoon-blue counter, and what comes back when it is rung: a till slip.
  1   the bell, low and from the right, button up            (1b: the same camera, button pressed)
  2   right up against the button and the top of the dome
  3   the slip lying in front of the bell, its head resting on the bell's foot
  4   right up against the slip's big line: WE'LL REPLY BY 10AM MON

  python3 build.py <1|1b|2|3|4|all> [draft|final] [regrade]
writes art/render-0N.jpg (1188x2112; shown at 1080x1920 and pushed in a little). Type is set in reel.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1188, 2112
TMP = Path(tempfile.gettempdir())
AQUA = (0.006, 0.21, 0.30)
SLIP_W, SLIP_L = 0.058, 0.101
SLIP_C, SLIP_YAW = (-0.030, -0.083), math.radians(13)


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def link(ob):
    bpy.context.scene.collection.objects.link(ob); return ob


def lathe(name, prof, segs=200):
    verts, faces = [], []
    n = len(prof)
    for i in range(segs):
        a = 2 * math.pi * i / segs
        for (r, z) in prof:
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for i in range(segs):
        for j in range(n - 1):
            a = i * n + j; b = ((i + 1) % segs) * n + j
            faces.append((a, b, b + 1, a + 1))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    return link(bpy.data.objects.new(name, me))


def arc(cx, cz, r, a0, a1, n=10):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


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
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
    o = link(bpy.data.objects.new(name, me)); o.location = loc; look(o, target)
    m, nt, p = mat(name)
    p.inputs["Base Color"].default_value = (0, 0, 0, 1)
    p.inputs["Emission Color"].default_value = (*colour, 1); p.inputs["Emission Strength"].default_value = strength
    me.materials.append(m)
    o.visible_camera = False; o.visible_diffuse = False; o.visible_shadow = False; o.visible_transmission = False
    return o


BASE_R, BASE_H = 0.047, 0.010
DOME_R, DOME_H = 0.041, 0.031
TOPZ = BASE_H + DOME_H

SHOTS = {
    "1": dict(target=(0.0, 0.0, 0.030), dist=0.42, az=24, el=20, lens=85, f=11, focus=(0.0, -0.02, 0.04), shift=(-0.085, 0.17)),
    "2": dict(target=(0.0, 0.0, TOPZ + 0.006), dist=0.21, az=24, el=27, lens=100, f=11, focus=(0.0, -0.004, TOPZ + 0.012), shift=(-0.04, 0.19)),
    "3": dict(target=(-0.025, -0.06, 0.0), dist=0.44, az=24, el=40, lens=85, f=9, focus=(-0.03, -0.085, 0.002), shift=(-0.07, 0.17), slip=True),
    "4": dict(target=(-0.0254, -0.1030, 0.002), dist=0.27, az=24, el=38, lens=100, f=6.3, focus=(-0.0254, -0.1030, 0.002), shift=(0.0, 0.27), slip=True),
}
SHOTS["1b"] = dict(SHOTS["1"], press=True)


def build(frame, quality):
    shot = SHOTS[frame]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 112 if final else 16
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 10
    sc.cycles.sample_clamp_indirect = 8.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 30
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    # the room: dim for light, but bright and soft for mirrors, so the chrome reads as chrome
    wn, wl = world.node_tree.nodes, world.node_tree.links
    lp = wn.new("ShaderNodeLightPath")
    grad = wn.new("ShaderNodeTexGradient"); tc = wn.new("ShaderNodeTexCoord"); mp = wn.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, math.radians(-90), 0)
    wl.new(tc.outputs["Generated"], mp.inputs["Vector"]); wl.new(mp.outputs["Vector"], grad.inputs["Vector"])
    ramp = wn.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[0].color = (0.10, 0.16, 0.19, 1)
    ramp.color_ramp.elements[1].position = 0.95; ramp.color_ramp.elements[1].color = (0.85, 0.90, 0.92, 1)
    wl.new(grad.outputs["Fac"], ramp.inputs["Fac"])
    mixw = wn.new("ShaderNodeMix"); mixw.data_type = "RGBA"
    wl.new(lp.outputs["Is Glossy Ray"], mixw.inputs["Factor"])
    mixw.inputs["A"].default_value = (0.03, 0.05, 0.06, 1)
    wl.new(ramp.outputs["Color"], mixw.inputs["B"])
    wl.new(mixw.outputs["Result"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0

    prof = [(-4.0, 0.0), (0.45, 0.0)]
    Rs = 0.55
    for j in range(1, 25):
        a = math.pi / 2 * j / 24
        prof.append((0.45 + Rs * math.sin(a), Rs * (1 - math.cos(a))))
    prof.append((1.0, 5.0))
    verts = [(x, y, z) for (y, z) in prof for x in (-8.0, 8.0)]
    faces = [(2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2) for j in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    link(bpy.data.objects.new("sweep", me))
    sm, snt, sp = mat("aqua")
    sp.inputs["Base Color"].default_value = (*AQUA, 1)
    sp.inputs["Roughness"].default_value = 0.62
    sp.inputs["Specular IOR Level"].default_value = 0.25
    nz = snt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 700; nz.inputs["Detail"].default_value = 3
    bump = snt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.0002
    snt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); snt.links.new(bump.outputs["Normal"], sp.inputs["Normal"])
    me.materials.append(sm)

    blk, _, bp = mat("enamel")
    bp.inputs["Base Color"].default_value = (0.010, 0.011, 0.014, 1); bp.inputs["Roughness"].default_value = 0.22
    bp.inputs["Coat Weight"].default_value = 0.6; bp.inputs["Coat Roughness"].default_value = 0.06
    cm, cnt, cp = mat("chrome")
    cp.inputs["Base Color"].default_value = (0.88, 0.88, 0.89, 1)
    cp.inputs["Metallic"].default_value = 1.0
    cp.inputs["Roughness"].default_value = 0.06
    cz = cnt.nodes.new("ShaderNodeTexNoise"); cz.inputs["Scale"].default_value = 2500; cz.inputs["Detail"].default_value = 2
    cb = cnt.nodes.new("ShaderNodeBump"); cb.inputs["Strength"].default_value = 0.025; cb.inputs["Distance"].default_value = 0.00002
    cnt.links.new(cz.outputs["Fac"], cb.inputs["Height"]); cnt.links.new(cb.outputs["Normal"], cp.inputs["Normal"])

    # foot: black enamel, a stepped disc with rounded shoulders
    foot = [(0.0, 0.0), (BASE_R - 0.001, 0.0)] + arc(BASE_R - 0.001, 0.001, 0.001, -90, 0, 6) + [(BASE_R, 0.0045)] \
        + arc(BASE_R - 0.003, 0.0045, 0.003, 0, 90, 10) + [(DOME_R + 0.0025, 0.0075), (DOME_R + 0.0018, BASE_H), (0.0, BASE_H)]
    lathe("foot", foot).data.materials.append(blk)
    # dome: a rolled lip, then a flattened half-ellipse up to a small collar
    dome = arc(DOME_R + 0.0008, BASE_H + 0.0012, 0.0012, -90, 90, 10)
    for k in range(0, 61):
        t = math.radians(4 + 80 * k / 60)
        dome.append((DOME_R * math.cos(t), BASE_H + 0.0022 + (DOME_H - 0.0022) * math.sin(t) / math.sin(math.radians(84))))
    rc = DOME_R * math.cos(math.radians(84))
    dome += [(rc, TOPZ), (0.0, TOPZ)]
    lathe("dome", dome).data.materials.append(cm)
    # collar, stem and button
    col = [(0.0074, TOPZ - 0.002), (0.0074, TOPZ + 0.0030)] + arc(0.0064, TOPZ + 0.0030, 0.001, 0, 90, 6) + [(0.0, TOPZ + 0.0040)]
    lathe("collar", col, 96).data.materials.append(cm)
    dz = -0.0062 if shot.get("press") else 0.0
    z0 = TOPZ + 0.0040
    stem = [(0.0029, z0 - 0.004), (0.0029, z0 + 0.010 + dz)]
    lathe("stem", stem, 64).data.materials.append(cm)
    bz = z0 + 0.0085 + dz
    btn = [(0.0, bz), (0.0078, bz)] + arc(0.0078, bz + 0.0016, 0.0016, -90, 0, 8) + [(0.0094, bz + 0.0030)] \
        + arc(0.0074, bz + 0.0030, 0.0020, 0, 60, 8)
    r1, zt = btn[-1]
    for k in range(1, 13):                       # a shallow domed top
        btn.append((r1 * (1 - k / 12), zt + 0.0012 * (1 - (1 - k / 12) ** 2)))
    lathe("button", btn, 120).data.materials.append(cm)

    if shot.get("slip"):
        pm, pnt, pp = mat("slip")
        Nn, Ln = pnt.nodes, pnt.links
        tex = Nn.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / "tex" / "slip.png"))
        tex.extension = "CLIP"; tex.interpolation = "Cubic"
        geo = Nn.new("ShaderNodeNewGeometry")
        mix = Nn.new("ShaderNodeMix"); mix.data_type = "RGBA"
        Ln.new(geo.outputs["Backfacing"], mix.inputs["Factor"])
        dim = Nn.new("ShaderNodeMix"); dim.data_type = "RGBA"; dim.blend_type = "MULTIPLY"; dim.inputs["Factor"].default_value = 1.0
        Ln.new(tex.outputs["Color"], dim.inputs["A"]); dim.inputs["B"].default_value = (0.86, 0.86, 0.85, 1)
        Ln.new(dim.outputs["Result"], mix.inputs["A"]); mix.inputs["B"].default_value = (0.80, 0.795, 0.77, 1)
        Ln.new(mix.outputs["Result"], pp.inputs["Base Color"]); Ln.new(tex.outputs["Alpha"], pp.inputs["Alpha"])
        pp.inputs["Roughness"].default_value = 0.5; pp.inputs["Specular IOR Level"].default_value = 0.3
        fz = Nn.new("ShaderNodeTexNoise"); fz.inputs["Scale"].default_value = 1800; fz.inputs["Detail"].default_value = 4
        fb = Nn.new("ShaderNodeBump"); fb.inputs["Strength"].default_value = 0.06; fb.inputs["Distance"].default_value = 0.00005
        Ln.new(fz.outputs["Fac"], fb.inputs["Height"]); Ln.new(fb.outputs["Normal"], pp.inputs["Normal"])
        # a strip that bends one way only: its head lifts on to the bell's foot, its tail curls up like till roll
        ns, nu = 220, 8
        d = (math.sin(SLIP_YAW), -math.cos(SLIP_YAW)); q = (math.cos(SLIP_YAW), math.sin(SLIP_YAW))
        # profile in (run, z) by arc length
        run, z, pts = 0.0, 0.0, []
        ds = SLIP_L / ns
        for i in range(ns + 1):
            s = i * ds
            head = max(0.0, (0.034 - s) / 0.034)           # 1 at the head, 0 from 34 mm down
            tail = max(0.0, (s - (SLIP_L - 0.030)) / 0.030)
            ang = -math.radians(34) * head ** 1.5 + math.radians(30) * tail ** 2   # slope of the paper
            pts.append((run, z))
            run += ds * math.cos(ang); z += ds * math.sin(ang)
        zmin = min(p[1] for p in pts)
        vs, fs = [], []
        for i, (rr, zz) in enumerate(pts):
            for j in range(nu + 1):
                u = j / nu
                # the faintest cup across the width so it catches the light unevenly
                cup = 0.0006 * (2 * u - 1) ** 2
                x = SLIP_C[0] + (rr - SLIP_L / 2) * d[0] + (u - 0.5) * SLIP_W * q[0]
                y = SLIP_C[1] + (rr - SLIP_L / 2) * d[1] + (u - 0.5) * SLIP_W * q[1]
                vs.append((x, y, zz - zmin + 0.0004 + cup))
        for i in range(ns):
            for j in range(nu):
                a = i * (nu + 1) + j
                fs.append((a, a + nu + 1, a + nu + 2, a + 1))
        sme = bpy.data.meshes.new("slip"); sme.from_pydata(vs, [], fs)
        uv = sme.uv_layers.new()
        for poly in sme.polygons:
            poly.use_smooth = True
            for li in poly.loop_indices:
                vi = sme.loops[li].vertex_index
                i, j = divmod(vi, nu + 1)
                uv.data[li].uv = (j / nu, 1 - i / ns)
        so = link(bpy.data.objects.new("slip", sme)); sme.materials.append(pm)

    # light: a small box low on the left so everything throws a long shadow, a strip behind right for a rim, soft fill
    area("key", (0.85, -0.42, 0.30), (0, 0, 0.02), 0.40, 120, (1.0, 0.97, 0.93))
    area("rim", (-0.65, 0.60, 0.45), (0, 0, 0.02), 0.25, 20, (0.93, 0.97, 1.0), size_y=0.9)
    area("fill", (-0.6, -0.9, 0.5), (0, 0, 0.02), 1.4, 4, (1.0, 0.98, 0.97))
    # things for the chrome to mirror
    card("c1", (-0.30, -0.22, 0.22), (0, 0, 0.03), 0.14, 0.60, 3.2)
    card("c2", (0.22, -0.30, 0.50), (0, 0, 0.03), 0.60, 0.10, 1.6, (1.0, 0.96, 0.93))
    card("strip", (-0.10, 0.48, 0.20), (0, 0, 0.03), 1.4, 0.03, 4.0)

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

    exr = str(TMP / f"nx-bell-{frame}-{quality}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def pixels(exr):
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32), w, h


EXPOSURE = 0.55


def grade(exr, frame, quality):
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
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.10 * np.clip(r - 0.6, 0, 1) ** 1.5)[..., None]
    rng = np.random.default_rng(7)
    x += rng.normal(0, 0.007, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"render-{frame}.jpg" if quality == "final" else f".draft-{frame}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst)


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 and args[1] in ("draft", "final") else "draft"
    regrade = "regrade" in args
    for fr in (["1", "1b", "2", "3", "4"] if which == "all" else [which]):
        exr = str(TMP / f"nx-bell-{fr}-{quality}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
