"""Renders the three pictures for this Story with Blender's Python module (pip install bpy brotli).

One fortune cookie on a sage table, and the slip that came out of it. The slip is what a website's chatbot
said when it was asked a question it had no answer for.
  1  the cookie and its slip, from the front and a little above: "Yes, we're open on Sundays."
  2  right up against the slip, the cookie a blur behind it
  3  nearer and higher, the same cookie, a new slip: "I'll check with the team."

  python3 build.py <frame 1|2|3|all> [draft|final] [regrade]
writes art/render-0N.jpg (1080x1920). The type is set over it in slide-0N.html; tex.py prints the slips.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())

SAGE = (0.33, 0.40, 0.27)
DOUGH = (0.50, 0.31, 0.10)
TOAST = (0.22, 0.11, 0.03)

R, A, ALPHA, PUFF = 0.040, 0.0030, math.radians(118), 0.0085


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


def cookie():
    """A disc folded in half, then the fold bent round tight in the middle so both corners come down.
    The two layers stay pinched at the fold and puff apart towards the open edge."""
    N, M = 200, 100
    # the fold line: tight in the middle, easing out to the corners
    ss = np.linspace(-R, R, N + 1)
    alpha = np.sign(ss) * ALPHA * (np.abs(ss) / R) ** 0.55
    C = np.zeros((N + 1, 3)); mid = N // 2
    for i in range(mid + 1, N + 1):
        ds = ss[i] - ss[i - 1]; a = 0.5 * (alpha[i] + alpha[i - 1])
        C[i] = C[i - 1] + ds * np.array([math.cos(a), 0, -math.sin(a)])
    for i in range(mid - 1, -1, -1):
        ds = ss[i + 1] - ss[i]; a = 0.5 * (alpha[i] + alpha[i + 1])
        C[i] = C[i + 1] - ds * np.array([math.cos(a), 0, -math.sin(a)])
    verts, rim = [], []
    for i in range(N + 1):
        s = float(ss[i]); al = float(alpha[i])
        w = max(math.sqrt(max(R * R - s * s, 0)), 0.0006)
        n = Vector((math.sin(al), 0, math.cos(al)))
        for j in range(M + 1):
            t = -w + 2 * w * j / M
            at = abs(t); sg = 1 if t >= 0 else -1
            u = at / R
            # pinched at the fold, puffed in the middle of the body, a little open at the edge
            h = A * (1 - math.cos(min(at / A, math.pi / 2))) * 0.5 + PUFF * math.sin(math.pi * min(u / 0.9, 1) ** 0.8) * (1 - (abs(s) / R) ** 2) ** 0.5 + 0.0025 * u ** 2
            h += 0.0005 * math.sin(7 * s / R + 3 * t / R) + 0.0003 * math.sin(13 * t / R)
            P = Vector(tuple(C[i])) + Vector((0, at, 0)) + sg * h * n
            verts.append(P)
            rim.append(math.hypot(s, t) / R)
    faces = []
    for i in range(N):
        for j in range(M):
            a = i * (M + 1) + j
            faces.append((a, a + M + 1, a + M + 2, a + 1))
    me = bpy.data.meshes.new("cookie"); me.from_pydata([tuple(v) for v in verts], [], faces)
    for p in me.polygons:
        p.use_smooth = True
    at = me.color_attributes.new("rim", "FLOAT_COLOR", "POINT")
    for k, r in enumerate(rim):
        at.data[k].color = (r, r, r, 1)
    ob = bpy.data.objects.new("cookie", me); bpy.context.scene.collection.objects.link(ob)
    sol = ob.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.0016; sol.offset = 0
    sub = ob.modifiers.new("sub", "SUBSURF"); sub.levels = 1; sub.render_levels = 1
    # stand it on the table: the two corners down
    bpy.context.view_layer.update()
    zmin = min((ob.matrix_world @ Vector(v)).z for v in verts)
    ob.location.z = -zmin - 0.0012
    m, nt, p = mat("dough")
    N_, L = nt.nodes, nt.links
    attr = N_.new("ShaderNodeAttribute"); attr.attribute_name = "rim"
    ramp = N_.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[0].color = (*DOUGH, 1)
    ramp.color_ramp.elements[1].position = 1.0; ramp.color_ramp.elements[1].color = (*TOAST, 1)
    L.new(attr.outputs["Fac"], ramp.inputs[0])
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 28; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.62
    mix = N_.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs["Factor"].default_value = 0.18
    L.new(ramp.outputs["Color"], mix.inputs["A"]); mix.inputs["B"].default_value = (*TOAST, 1)
    fr = N_.new("ShaderNodeMapRange"); fr.inputs["From Min"].default_value = 0.42; fr.inputs["From Max"].default_value = 0.72
    L.new(nz.outputs["Fac"], fr.inputs["Value"])
    fac = N_.new("ShaderNodeMath"); fac.operation = "MULTIPLY"; fac.inputs[1].default_value = 0.55
    L.new(fr.outputs["Result"], fac.inputs[0]); L.new(fac.outputs[0], mix.inputs["Factor"])
    L.new(mix.outputs["Result"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.5
    p.inputs["Specular IOR Level"].default_value = 0.45
    p.inputs["Subsurface Weight"].default_value = 0.25
    p.inputs["Subsurface Radius"].default_value = (1.0, 0.6, 0.3)
    p.inputs["Subsurface Scale"].default_value = 0.002
    # baked surface: fine pits and a few blisters
    pz = N_.new("ShaderNodeTexNoise"); pz.inputs["Scale"].default_value = 900; pz.inputs["Detail"].default_value = 3
    vz = N_.new("ShaderNodeTexVoronoi"); vz.inputs["Scale"].default_value = 260
    add = N_.new("ShaderNodeMath"); add.operation = "MULTIPLY_ADD"; add.inputs[1].default_value = 0.5
    L.new(vz.outputs["Distance"], add.inputs[0]); L.new(pz.outputs["Fac"], add.inputs[2])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.6; bump.inputs["Distance"].default_value = 0.0002
    L.new(add.outputs[0], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    me.materials.append(m)
    return ob


def slip(key, loc, rot, curl):
    L_, W_ = 0.066, 0.0114
    nu, nv = 140, 10
    verts, uvs = [], []
    for i in range(nu + 1):
        u = i / nu
        x = (u - 0.5) * L_
        e = abs(u - 0.5) * 2
        z = 0.0007 + curl * max(0.0, (e - 0.62) / 0.38) ** 2 + 0.0003 * math.sin(u * 9)
        for j in range(nv + 1):
            v = j / nv
            y = (v - 0.5) * W_
            verts.append((x, y, z + 0.0004 * (v - 0.5) ** 2 * 4)); uvs.append((u, v))
    faces = [(i * (nv + 1) + j, (i + 1) * (nv + 1) + j, (i + 1) * (nv + 1) + j + 1, i * (nv + 1) + j + 1)
             for i in range(nu) for j in range(nv)]
    me = bpy.data.meshes.new("slip"); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new()
    for poly in me.polygons:
        poly.use_smooth = True
        for li in poly.loop_indices:
            uv.data[li].uv = uvs[me.loops[li].vertex_index]
    ob = bpy.data.objects.new("slip", me); bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler = (0, 0, math.radians(rot))
    sol = ob.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.00012
    m, nt, p = mat("paper")
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / "tex" / f"slip-{key}.png"))
    tex.interpolation = "Cubic"; tex.image.colorspace_settings.name = "sRGB"
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.78
    p.inputs["Specular IOR Level"].default_value = 0.3
    p.inputs["Subsurface Weight"].default_value = 0.2
    p.inputs["Subsurface Scale"].default_value = 0.001
    me.materials.append(m)
    return ob


SHOTS = {
    1: dict(target=(0.0, -0.02, 0.016), dist=0.36, az=10, el=26, lens=85, f=11, focus=(0.0, -0.04, 0.008),
            shift=(-0.03, 0.085), slip="guess"),
    2: dict(target=(0.0225, -0.0497, 0.0), dist=0.105, az=10, el=30, lens=100, f=8, focus=(0.0225, -0.0497, 0.0),
            shift=(-0.0175, 0.07), slip="guess"),
    3: dict(target=(0.001, -0.033, 0.006), dist=0.275, az=12, el=52, lens=100, f=5.6, focus=(0.002, -0.047, 0.0),
            shift=(0.0, -0.10), slip="check"),
}
SLIP = dict(loc=(0.002, -0.047, 0.0), rot=-7, curl=0.0035)


def build(frame, quality):
    shot = SHOTS[frame]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 110 if final else 24
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
    bg.inputs["Color"].default_value = (0.30, 0.36, 0.28, 1)
    bg.inputs["Strength"].default_value = 0.05

    prof = [(-4.0, 0.0), (0.30, 0.0)]
    Rs = 0.45
    for j in range(1, 25):
        a = math.pi / 2 * j / 24
        prof.append((0.30 + Rs * math.sin(a), Rs * (1 - math.cos(a))))
    prof.append((0.75, 4.0))
    verts = [(x, y, z) for (y, z) in prof for x in (-6.0, 6.0)]
    faces = [(2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2) for j in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    sweep = bpy.data.objects.new("sweep", me); sc.collection.objects.link(sweep)
    sm, snt, sp = mat("sage")
    sp.inputs["Base Color"].default_value = (*SAGE, 1)
    sp.inputs["Roughness"].default_value = 0.75
    sp.inputs["Specular IOR Level"].default_value = 0.25
    nz = snt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 700; nz.inputs["Detail"].default_value = 3
    bump = snt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.04; bump.inputs["Distance"].default_value = 0.0002
    snt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); snt.links.new(bump.outputs["Normal"], sp.inputs["Normal"])
    me.materials.append(sm)

    ck = cookie()
    ck.rotation_euler = (0, 0, math.radians(-28))
    ck.location.x = 0.002; ck.location.y = -0.012
    slip(shot["slip"], **SLIP)

    area("key", (-0.60, -0.20, 0.20), (0, 0, 0.02), 0.30, 30, (1.0, 0.96, 0.90))
    area("rim", (0.42, 0.45, 0.28), (0, 0, 0.03), 0.20, 7, (0.92, 0.96, 1.0), size_y=0.7)
    area("fill", (0.40, -0.60, 0.25), (0, 0, 0.02), 0.9, 3.0, (0.95, 0.97, 1.0))

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
    cam.clip_start = 0.005

    exr = str(TMP / f"nx-cookie-{frame}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def pixels(exr):
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32), w, h


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
    top = np.clip(1 - yy / 330.0, 0, 1) ** 1.6
    x *= (1 - 0.40 * top)[..., None]
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
        exr = str(TMP / f"nx-cookie-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
