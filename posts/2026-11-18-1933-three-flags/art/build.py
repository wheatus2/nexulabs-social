"""Renders the pictures for this Reel with Blender's Python module
(python3.13 -m pip install bpy pillow numpy playwright --break-system-packages; prints: print.py).

One phone lying on a pale grey sweep, showing a made-up firm's website (Ashgarth Kitchens, invented),
and three pink page flags stuck on its glass, numbered 1 to 3 in marker, each pointing at one thing.

  python3.13 build.py <shot> [draft|final] [regrade]     shots: 1a 1b 1c 2 3 4
writes art/r-<shot>.jpg (1134x2016; drafts .d-<shot>.jpg). The type is set over it in reel.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1134, 2016
TMP = Path(tempfile.gettempdir())
MM = 0.001
PW, PH, PT, PR = 71.5 * MM, 147.0 * MM, 7.8 * MM, 11.5 * MM
SW, SH, SR = 65.0 * MM, 140.9 * MM, 8.6 * MM
FLAGS = {1: 33.7 * MM, 2: -2.3 * MM, 3: -38.4 * MM}      # where each flag points, y on the phone
TIP, FLEN, FWID = 20.0 * MM, 41.0 * MM, 12.0 * MM


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree, m.node_tree.nodes["Principled BSDF"]


def link(ob):
    bpy.context.scene.collection.objects.link(ob); return ob


def rrect(w, h, r, n=20):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for j in range(n + 1):
            a = math.radians(a0 + 90 * j / n)
            # a slightly squared corner, as phones have
            k = (abs(math.cos(a - math.radians(a0))) ** 2.6 + abs(math.sin(a - math.radians(a0))) ** 2.6) ** (-1 / 2.6)
            pts.append((cx + r * k * math.cos(a), cy + r * k * math.sin(a)))
    return pts


def look(ob, target):
    f = (Vector(target) - ob.location).normalized()
    r = f.cross(Vector((0, 0, 1))).normalized()
    u = r.cross(f)
    ob.rotation_euler = Matrix((r, u, -f)).transposed().to_euler()


def area(name, loc, target, size, energy, colour=(1, 1, 1), size_y=None):
    l = bpy.data.lights.new(name, "AREA"); l.size = size; l.energy = energy; l.color = colour
    if size_y:
        l.shape = "RECTANGLE"; l.size_y = size_y
    o = link(bpy.data.objects.new(name, l)); o.location = loc; look(o, target)
    return o


def phone():
    re_, n = 2.3 * MM, 10
    rings = []
    for j in range(n + 1):                       # bottom edge, rounding up into the band
        a = math.pi / 2 * j / n
        rings.append((re_ * (1 - math.sin(a)), re_ * (1 - math.cos(a))))
    for j in range(n + 1):                       # band rounding over to the glass
        a = math.pi / 2 * j / n
        rings.append((re_ * (1 - math.cos(a)), PT - re_ + re_ * math.sin(a)))
    verts, faces = [], []
    for d, z in rings:
        ring = rrect(PW - 2 * d, PH - 2 * d, PR - d * 0.6)
        verts += [(x, y, z) for x, y in ring]
    m = len(rrect(PW, PH, PR))
    for k in range(len(rings) - 1):
        for s in range(m):
            a, b = k * m + s, k * m + (s + 1) % m
            faces.append((a, b, b + m, a + m))
    faces.append(tuple(range(m - 1, -1, -1)))
    top = tuple(range((len(rings) - 1) * m, len(rings) * m))
    faces.append(top)
    me = bpy.data.meshes.new("phone"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = len(p.vertices) == 4
    band, nt, p = mat("band")
    p.inputs["Base Color"].default_value = (0.115, 0.118, 0.125, 1); p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = 0.36
    glass, nt2, g = mat("glass")
    g.inputs["Base Color"].default_value = (0.004, 0.004, 0.005, 1); g.inputs["Roughness"].default_value = 0.06
    g.inputs["Specular IOR Level"].default_value = 0.6
    me.materials.append(band); me.materials.append(glass)
    me.polygons[len(me.polygons) - 1].material_index = 1
    # the last two rings (the roll-over) are glass too
    for p_ in me.polygons:
        if len(p_.vertices) == 4 and min(me.vertices[v].co.z for v in p_.vertices) > PT - re_ * 0.42:
            p_.material_index = 1
    ob = link(bpy.data.objects.new("phone", me))
    # side buttons
    for x, y, ln in ((-1, 0.046, 0.006), (-1, 0.032, 0.0105), (-1, 0.018, 0.0105), (1, 0.026, 0.017)):
        sx, sy, sz = 0.0011, ln, 0.0030
        v = [(a * sx / 2, b * sy / 2, c * sz / 2) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
        f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        bm = bpy.data.meshes.new("btn"); bm.from_pydata(v, [], f); bm.materials.append(band)
        bo = link(bpy.data.objects.new("btn", bm)); bo.location = (x * (PW / 2 + 0.0002), y, PT / 2)
        bv = bo.modifiers.new("b", "BEVEL"); bv.width = 0.0004; bv.segments = 3
    # the screen, a hair above the glass
    pts = rrect(SW, SH, SR)
    sm = bpy.data.meshes.new("screen"); sm.from_pydata([(x, y, PT + 0.00003) for x, y in pts], [], [tuple(range(len(pts)))])
    uv = sm.uv_layers.new(name="uv")
    for lp in sm.loops:
        co = sm.vertices[lp.vertex_index].co
        uv.data[lp.index].uv = (co.x / SW + 0.5, co.y / SH + 0.5)
    s, nt3, sp = mat("screen")
    tex = nt3.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / "screen.png")); tex.extension = "EXTEND"; tex.interpolation = "Cubic"
    nt3.links.new(tex.outputs["Color"], sp.inputs["Emission Color"])
    sp.inputs["Emission Strength"].default_value = SCREEN_E
    dim = nt3.nodes.new("ShaderNodeMix"); dim.data_type = "RGBA"; dim.blend_type = "MULTIPLY"; dim.inputs["Factor"].default_value = 1.0
    dim.inputs["B"].default_value = (0.75, 0.75, 0.75, 1)
    nt3.links.new(tex.outputs["Color"], dim.inputs["A"]); nt3.links.new(dim.outputs["Result"], sp.inputs["Base Color"])
    sp.inputs["Roughness"].default_value = 0.10; sp.inputs["Specular IOR Level"].default_value = 0.45
    sm.materials.append(s)
    link(bpy.data.objects.new("screen", sm))
    return ob


def flag(n, lift=0.0):
    """A pink page flag: the pointed end stuck flat to the glass, the tail past the phone's edge curling up."""
    yc = FLAGS[n]
    nx, ny = 90, 8
    flat_to, R = PW / 2 + 0.0022, 0.030
    z0 = PT + 0.00012
    verts, uvs = [], []
    for i in range(nx + 1):
        u = i / nx
        s = u * FLEN                                    # distance along the flag from the point
        half = FWID / 2 * min(1.0, max(s, 1e-5) / (6.0 * MM))
        x = TIP + s
        if x > flat_to:
            th = (x - flat_to) / R
            px, pz = flat_to + R * math.sin(th), z0 + R * (1 - math.cos(th))
        else:
            px, pz = x, z0
        for j in range(ny + 1):
            v = j / ny
            verts.append((px + lift * 1.2, yc + (v - 0.5) * 2 * half, pz + lift))
            uvs.append((u, 0.5 + (v - 0.5) * 2 * half / FWID))
    faces = [(i * (ny + 1) + j, (i + 1) * (ny + 1) + j, (i + 1) * (ny + 1) + j + 1, i * (ny + 1) + j + 1) for i in range(nx) for j in range(ny)]
    me = bpy.data.meshes.new(f"flag{n}"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    uv = me.uv_layers.new(name="uv")
    for lp in me.loops:
        uv.data[lp.index].uv = uvs[lp.vertex_index]
    m, nt, p = mat(f"flag{n}")
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / f"flag-{n}.png")); tex.extension = "EXTEND"; tex.interpolation = "Cubic"
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"]); p.inputs["Emission Strength"].default_value = 0.08
    p.inputs["Roughness"].default_value = 0.42; p.inputs["Specular IOR Level"].default_value = 0.35
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent"); nt.links.new(tex.outputs["Color"], tr.inputs["Color"])
    mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.07
    nt.links.new(p.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    me.materials.append(m)
    ob = link(bpy.data.objects.new(f"flag{n}", me))
    so = ob.modifiers.new("s", "SOLIDIFY"); so.thickness = 0.00012; so.offset = 1
    return ob


SCREEN_E = 0.62
SHOTS = {
    # 1 low along the flags, 3 nearest; 2 flag 1 and the site's headline; 3 the three flags down the phone's edge; 4 flag 3 and the button
    "1": dict(target=(0.030, -0.018, PT), dist=0.245, az=-8, el=30, lens=85, f=4.5, focus=(0.0295, -0.0384, PT), shift=(0.0, 0.155), probe=(60, 300, 200, 400)),
    "2": dict(target=(0.004, 0.030, PT), dist=0.40, az=-14, el=48, lens=85, f=8, focus=(0.004, 0.032, PT), shift=(0.0, 0.10), probe=(700, 1000, 240, 420)),
    "3": dict(target=(0.040, -0.004, PT), dist=0.25, az=-20, el=29, lens=85, f=16, focus=(0.036, -0.002, PT), shift=(0.0, 0.073), probe=(60, 300, 240, 420)),
    "4": dict(target=(0.011, -0.040, PT), dist=0.235, az=-30, el=36, lens=85, f=8, focus=(0.008, -0.039, PT), shift=(0.0, 0.225), probe=(60, 300, 240, 420)),
}
STATE = {"2": ((1, 0), (2, 0)), "4": ((2, 0), (3, 0)), "1a": ((1, 0), (2, 0), (3, 0.016)), "1b": ((1, 0), (2, 0), (3, 0.005)), "1c": ((1, 0), (2, 0), (3, 0))}


def build(name, quality):
    shot = SHOTS[name[0]]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 128 if final else 20
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 8.0
    sc.render.threads_mode = "AUTO"
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.80, 0.81, 0.84, 1); bg.inputs["Strength"].default_value = 0.07

    prof = [(-4.0, 0.0), (0.55, 0.0)]
    R = 0.5
    for j in range(1, 25):
        a = math.pi / 2 * j / 24
        prof.append((0.55 + R * math.sin(a), R * (1 - math.cos(a))))
    prof.append((1.05, 4.0))
    verts = [(x, y, z) for (y, z) in prof for x in (-6.0, 6.0)]
    faces = [(2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2) for j in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    link(bpy.data.objects.new("sweep", me))
    sm, snt, sp = mat("sweep")
    sp.inputs["Base Color"].default_value = (0.74, 0.745, 0.76, 1)
    sp.inputs["Roughness"].default_value = 0.78; sp.inputs["Specular IOR Level"].default_value = 0.2
    nz = snt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 3
    bump = snt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.0002
    snt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); snt.links.new(bump.outputs["Normal"], sp.inputs["Normal"])
    me.materials.append(sm)

    phone()
    for n, lift in STATE.get(name, ((1, 0), (2, 0), (3, 0))):
        flag(n, lift)

    area("key", (-0.55, 0.50, 0.62), (0, 0, 0), 0.55, 12, (1.0, 0.985, 0.96))
    area("rake", (-0.50, -0.06, 0.13), (0.03, 0, 0.005), 0.04, 3.4, (1.0, 0.98, 0.95))
    area("fill", (0.6, -0.6, 0.5), (0, 0, 0), 1.0, 2.0, (0.94, 0.97, 1.0))

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 36
    az, el = math.radians(shot["az"]), math.radians(shot["el"])
    tg = Vector(shot["target"])
    co.location = tg + shot["dist"] * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    look(co, tg)
    cam.lens = shot["lens"]; cam.shift_x, cam.shift_y = shot["shift"]
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"]
    cam.clip_start = 0.01
    exr = str(TMP / f"nx-flag-{name}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def pixels(exr):
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32), w, h


TABLE = 0.78       # the table at the probe, linear, in every shot: one backdrop (about #E4E5E7)


def grade(exr, name, quality):
    from PIL import Image
    a, w, h = pixels(exr)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    a = np.clip(a, 0, None)
    x0, x1, y0, y1 = SHOTS[name[0]]["probe"]
    ref = np.median(a[y0:y1, x0:x1].reshape(-1, 3), 0)
    x = a * (TABLE / ref.mean())
    x *= (ref.mean() / ref)[None, None, :] * np.array([0.992, 0.997, 1.012])    # a neutral, slightly cool grey
    # a soft shoulder above 0.8 so the screen's white and the highlights roll off and do not clip hard
    k = 0.80
    x = np.where(x > k, k + (1 - k) * (1 - np.exp(-(x - k) / (1 - k))), x)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"r-{name}.jpg" if quality == "final" else f".d-{name}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst, "ref", ref)


if __name__ == "__main__":
    args = sys.argv[1:]
    quality = "final" if "final" in args else "draft"
    for name in [x for x in args if x in ("1a", "1b", "1c", "2", "3", "4")]:
        exr = str(TMP / f"nx-flag-{name}.exr")
        grade(exr if "regrade" in args else build(name, quality), name, quality)
