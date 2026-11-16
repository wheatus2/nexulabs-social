"""Renders the pictures for this Story with Blender's Python module (pip install bpy brotli scipy).

A round rubber stamp for a made-up bakery (Halfloaf Bakehouse) and the one-ink print it leaves on a flat kraft
paper bag, on a pale steel-blue table. tex.py draws the logo, the print and the mirrored die.
  1  the bag and the stamp standing beside its print: could your logo be a stamp?
  2  right up against the print on the kraft: one ink, still yours
  3  the stamp lying on its side, die towards us, the print soft behind: ask for the one-colour version

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

TABLE = (0.22, 0.30, 0.37)
KRAFT = (0.72, 0.70, 0.65)
INK = (0.026, 0.003, 0.125)
RUBBER = (0.15, 0.050, 0.042)
WOOD = (0.17, 0.095, 0.050)

BAG_W, BAG_L = 0.19, 0.30
PRINT_D = 0.064
PRINT_AT = (0.0, -0.045)         # centre of the print on the bag (bag's own x, y)
DIE_R, MOUNT_R = 0.034, 0.036


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def link(ob):
    bpy.context.scene.collection.objects.link(ob); return ob


def lathe(name, profile, segs=128):
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
    return link(bpy.data.objects.new(name, me))


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


# ---------- the bag ----------
def bag(rot):
    nx, ny = 190, 300
    verts, faces = [], []
    rng = np.random.default_rng(3)
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = -BAG_W / 2 + BAG_W * i / nx; y = -BAG_L / 2 + BAG_L * j / ny
            # a flattened bag is never flat: a soft bow across, a lift at the folded bottom, the gussets proud
            z = 0.0012 + 0.0016 * (1 - (2 * x / BAG_W) ** 2) * 0.6
            z += 0.0022 * max(0, (y - (BAG_L / 2 - 0.05)) / 0.05) ** 2
            for gx in (-BAG_W / 2 + 0.028, BAG_W / 2 - 0.028):
                z += 0.0007 * math.exp(-((x - gx) / 0.004) ** 2)
            z += 0.00025 * math.sin(7 * y + 1.3) * math.sin(11 * x)
            verts.append((x, y, z))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    me = bpy.data.meshes.new("bag"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    ob = link(bpy.data.objects.new("bag", me))
    ob.rotation_euler = (0, 0, math.radians(rot))
    # thickness so the edge throws a line of shadow
    sol = ob.modifiers.new("solid", "SOLIDIFY"); sol.thickness = 0.0009; sol.offset = -1

    m, nt, p = mat("kraft"); N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.78
    p.inputs["Specular IOR Level"].default_value = 0.3
    tc = N.new("ShaderNodeTexCoord")
    # fibres: noise stretched along the bag
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (900, 120, 900)
    L.new(tc.outputs["Object"], mp.inputs[0])
    fib = N.new("ShaderNodeTexNoise"); fib.inputs["Scale"].default_value = 1.0; fib.inputs["Detail"].default_value = 8
    fib.inputs["Roughness"].default_value = 0.65
    L.new(mp.outputs[0], fib.inputs[0])
    blot = N.new("ShaderNodeTexNoise"); blot.inputs["Scale"].default_value = 30; blot.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], blot.inputs[0])
    flk = N.new("ShaderNodeTexVoronoi"); flk.inputs["Scale"].default_value = 260
    L.new(tc.outputs["Object"], flk.inputs[0])
    flkr = N.new("ShaderNodeMapRange"); flkr.inputs["From Min"].default_value = 0.0; flkr.inputs["From Max"].default_value = 0.07
    flkr.inputs["To Min"].default_value = 0.93; flkr.inputs["To Max"].default_value = 1.0; flkr.clamp = True
    L.new(flk.outputs["Distance"], flkr.inputs["Value"])
    c1 = N.new("ShaderNodeMix"); c1.data_type = "RGBA"
    c1.inputs["A"].default_value = (KRAFT[0] * 0.92, KRAFT[1] * 0.91, KRAFT[2] * 0.89, 1)
    c1.inputs["B"].default_value = (KRAFT[0] * 1.03, KRAFT[1] * 1.03, KRAFT[2] * 1.03, 1)
    L.new(fib.outputs["Fac"], c1.inputs["Factor"])
    c2 = N.new("ShaderNodeMix"); c2.data_type = "RGBA"; c2.blend_type = "MULTIPLY"; c2.inputs["Factor"].default_value = 0.10
    L.new(c1.outputs["Result"], c2.inputs["A"]); L.new(blot.outputs["Color"], c2.inputs["B"])
    c3 = N.new("ShaderNodeMix"); c3.data_type = "RGBA"; c3.blend_type = "MULTIPLY"; c3.inputs["Factor"].default_value = 1.0
    L.new(c2.outputs["Result"], c3.inputs["A"]); L.new(flkr.outputs["Result"], c3.inputs["B"])
    # the print, projected straight down
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    u = N.new("ShaderNodeMath"); u.operation = "MULTIPLY_ADD"; u.inputs[1].default_value = 1 / PRINT_D; u.inputs[2].default_value = 0.5 - PRINT_AT[0] / PRINT_D
    v = N.new("ShaderNodeMath"); v.operation = "MULTIPLY_ADD"; v.inputs[1].default_value = 1 / PRINT_D; v.inputs[2].default_value = 0.5 - PRINT_AT[1] / PRINT_D
    L.new(sep.outputs["X"], u.inputs[0]); L.new(sep.outputs["Y"], v.inputs[0])
    cmb = N.new("ShaderNodeCombineXYZ"); L.new(u.outputs[0], cmb.inputs[0]); L.new(v.outputs[0], cmb.inputs[1])
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / "tex" / "print.png"))
    tex.extension = "CLIP"; tex.interpolation = "Cubic"
    L.new(cmb.outputs[0], tex.inputs[0])
    # ink sinks into the fibres: thinner where the paper is high
    thin = N.new("ShaderNodeMapRange"); thin.inputs["To Min"].default_value = 1.0; thin.inputs["To Max"].default_value = 0.95
    L.new(fib.outputs["Fac"], thin.inputs["Value"])
    mk = N.new("ShaderNodeMath"); mk.operation = "MULTIPLY"
    L.new(tex.outputs["Alpha"], mk.inputs[0]); L.new(thin.outputs["Result"], mk.inputs[1])
    ink = N.new("ShaderNodeMix"); ink.data_type = "RGBA"
    L.new(mk.outputs[0], ink.inputs["Factor"]); L.new(c3.outputs["Result"], ink.inputs["A"]); ink.inputs["B"].default_value = (*INK, 1)
    L.new(ink.outputs["Result"], p.inputs["Base Color"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.22; bump.inputs["Distance"].default_value = 0.00008
    L.new(fib.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    me.materials.append(m)
    return ob


# ---------- the stamp ----------
def wood_material():
    m, nt, p = mat("beech"); N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.60
    p.inputs["Specular IOR Level"].default_value = 0.32
    p.inputs["Coat Weight"].default_value = 0.0
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, 1)
    L.new(tc.outputs["Object"], mp.inputs[0])
    wave = N.new("ShaderNodeTexWave"); wave.wave_type = "BANDS"; wave.bands_direction = "X"
    wave.inputs["Scale"].default_value = 140; wave.inputs["Distortion"].default_value = 1.5
    wave.inputs["Detail"].default_value = 3; wave.inputs["Detail Scale"].default_value = 1.5
    L.new(mp.outputs[0], wave.inputs[0])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 400; nz.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], nz.inputs[0])
    c = N.new("ShaderNodeMix"); c.data_type = "RGBA"
    c.inputs["A"].default_value = (*WOOD, 1); c.inputs["B"].default_value = (WOOD[0] * 0.82, WOOD[1] * 0.78, WOOD[2] * 0.75, 1)
    r = N.new("ShaderNodeMapRange"); r.inputs["From Min"].default_value = 0.55; r.inputs["From Max"].default_value = 1.0
    L.new(wave.outputs["Fac"], r.inputs["Value"]); L.new(r.outputs["Result"], c.inputs["Factor"])
    c2 = N.new("ShaderNodeMix"); c2.data_type = "RGBA"; c2.blend_type = "MULTIPLY"; c2.inputs["Factor"].default_value = 0.30
    L.new(c.outputs["Result"], c2.inputs["A"]); L.new(nz.outputs["Color"], c2.inputs["B"])
    L.new(c2.outputs["Result"], p.inputs["Base Color"])
    return m


def die_material():
    m, nt, p = mat("rubber"); N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.55
    tc = N.new("ShaderNodeTexCoord")
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / "tex" / "die.png"))
    tex.image.colorspace_settings.name = "Non-Color"; tex.extension = "CLIP"
    L.new(tc.outputs["UV"], tex.inputs[0])
    st = N.new("ShaderNodeMapRange"); st.inputs["From Min"].default_value = 0.55; st.inputs["From Max"].default_value = 0.85
    L.new(tex.outputs["Color"], st.inputs["Value"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], nz.inputs[0])
    stain = N.new("ShaderNodeMix"); stain.data_type = "RGBA"
    blot = N.new("ShaderNodeTexNoise"); blot.inputs["Scale"].default_value = 140; blot.inputs["Detail"].default_value = 5
    L.new(tc.outputs["Object"], blot.inputs[0])
    br = N.new("ShaderNodeMapRange"); br.inputs["From Min"].default_value = 0.35; br.inputs["From Max"].default_value = 0.75
    br.inputs["To Min"].default_value = 0.0; br.inputs["To Max"].default_value = 0.28
    L.new(blot.outputs["Fac"], br.inputs["Value"]); L.new(br.outputs["Result"], stain.inputs["Factor"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.10; bump.inputs["Distance"].default_value = 0.00002
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    stain.inputs["A"].default_value = (*RUBBER, 1); stain.inputs["B"].default_value = (*INK, 1)
    c = N.new("ShaderNodeMix"); c.data_type = "RGBA"
    L.new(st.outputs["Result"], c.inputs["Factor"]); L.new(stain.outputs["Result"], c.inputs["A"]); c.inputs["B"].default_value = (0.032, 0.010, 0.085, 1)
    L.new(c.outputs["Result"], p.inputs["Base Color"])
    rr = N.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.72; rr.inputs["To Max"].default_value = 0.42
    L.new(st.outputs["Result"], rr.inputs["Value"]); L.new(rr.outputs["Result"], p.inputs["Roughness"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.15; bump.inputs["Distance"].default_value = 0.00003
    return m


def stamp():
    """Built with the die face at z=0 facing down, the knob up. Returns the root empty."""
    root = link(bpy.data.objects.new("stamp", None))
    wm = wood_material()
    # rubber cushion and die
    n = 420
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=n, y_segments=n, size=DIE_R)
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for l in f.loops:
            co = l.vert.co
            l[uv].uv = (co.x / (2 * DIE_R) + 0.5, co.y / (2 * DIE_R) + 0.5)
    kill = [v for v in bm.verts if v.co.xy.length > DIE_R * 0.985]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    me = bpy.data.meshes.new("die"); bm.to_mesh(me); bm.free()
    die = link(bpy.data.objects.new("die", me)); die.parent = root
    die.rotation_euler = (math.pi, 0, 0)            # face down; the mirrored art reads right in the print
    die.location = (0, 0, 0.0012)
    img = bpy.data.images.load(str(HERE / "tex" / "die.png")); img.colorspace_settings.name = "Non-Color"
    t = bpy.data.textures.new("dieh", "IMAGE"); t.image = img; t.extension = "CLIP"
    dm = die.modifiers.new("disp", "DISPLACE"); dm.texture = t; dm.texture_coords = "UV"; dm.strength = 0.0012; dm.mid_level = 0.0
    dm.direction = "NORMAL"
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(die_material())
    # the rubber sheet under the die, a step thicker
    pad = lathe("pad", [(0, 0.0015), (DIE_R * 0.99, 0.0015), (DIE_R, 0.0018), (DIE_R, 0.0040), (0, 0.0040)])
    pad.parent = root
    rm, _, rp = mat("rubberbody"); rp.inputs["Base Color"].default_value = (*RUBBER, 1); rp.inputs["Roughness"].default_value = 0.6
    pad.data.materials.append(rm)
    # the turned beech mount and knob
    prof = [(0, 0.0040), (MOUNT_R - 0.0015, 0.0040), (MOUNT_R, 0.0055), (MOUNT_R, 0.0150), (MOUNT_R - 0.002, 0.0175),
            (0.020, 0.0195), (0.0105, 0.0240), (0.0080, 0.0300), (0.0072, 0.0420), (0.0085, 0.0500),
            (0.0135, 0.0590), (0.0165, 0.0680), (0.0160, 0.0740), (0.0130, 0.0790), (0.0075, 0.0818), (0, 0.0826)]
    # smooth the profile a little
    pts = []
    for a, b in zip(prof, prof[1:]):
        for k in range(6):
            u = k / 6; pts.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    pts.append(prof[-1])
    arr = np.array(pts)
    sm = arr.copy()
    for _ in range(3):
        sm[1:-1] = (sm[:-2] + 2 * sm[1:-1] + sm[2:]) / 4
    sm[:4] = arr[:4]
    knob = lathe("mount", [tuple(x) for x in sm]); knob.parent = root
    knob.data.materials.append(wm)
    return root


def sweep(sc):
    prof = [(-4.0, 0.0), (0.45, 0.0)]
    R = 0.5
    for j in range(1, 25):
        a = math.pi / 2 * j / 24
        prof.append((0.45 + R * math.sin(a), R * (1 - math.cos(a))))
    prof.append((0.95, 4.0))
    verts = [(x, y, z) for (y, z) in prof for x in (-6.0, 6.0)]
    faces = [(2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2) for j in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    ob = link(bpy.data.objects.new("sweep", me))
    m, nt, p = mat("table")
    p.inputs["Base Color"].default_value = (*TABLE, 1)
    p.inputs["Roughness"].default_value = 0.62; p.inputs["Specular IOR Level"].default_value = 0.3
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 600; nz.inputs["Detail"].default_value = 3
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.05; b.inputs["Distance"].default_value = 0.0002
    nt.links.new(nz.outputs["Fac"], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    me.materials.append(m)


BAG_ROT = -8
# where the stamp stands in frame 1 (world), and how it lies in frame 3
SHOTS = {
    1: dict(target=(0.010, -0.008, 0.02), dist=0.585, az=10, el=36, lens=70, f=11, focus=(0.0, -0.02, 0.01), shift=(0.0, 0.17),
            stamp="stand"),
    2: dict(target=(0.03, -0.12, 0.03), dist=0.36, az=10, el=16, lens=85, f=5.6, focus=(0.03, -0.14, 0.035), shift=(0.0, 0.10),
            stamp="side"),
    3: dict(target=(-0.020, -0.006, 0.004), dist=0.25, az=10, el=24, lens=55, f=5.6, focus=(-0.026, -0.022, 0.002), shift=(-0.014, -0.13),
            stamp="behind"),
}


def place_stamp(root, how):
    if how == "behind":
        root.location = (-0.004, 0.075, 0.0027)
        root.rotation_euler = (0, 0, math.radians(20))
    elif how == "stand":
        root.location = (0.038, 0.034, 0.0027)
        root.rotation_euler = (0, 0, math.radians(20))
    else:
        # lying on its side: the mount's rim and the knob's ball touch the table; die faces the camera (-y)
        tilt = math.asin((MOUNT_R - 0.0165) / (0.068 - 0.010))
        root.rotation_euler = (math.radians(90) + tilt * 0, 0, 0)
        root.rotation_euler = Matrix.Rotation(-math.pi / 2 - tilt, 4, "X").to_euler()
        root.location = (0.03, -0.14, MOUNT_R)
        root.rotation_euler.z = math.radians(-14)


def build(frame, quality):
    shot = SHOTS[frame]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 110 if final else 20
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
    bg.inputs["Color"].default_value = (0.42, 0.47, 0.52, 1); bg.inputs["Strength"].default_value = 0.06

    sweep(sc)
    b = bag(BAG_ROT)
    b.location = (-0.02, 0.02, 0)
    st = stamp(); place_stamp(st, shot["stamp"])

    area("key", (-0.70, -0.20, 0.30), (0, 0, 0.02), 0.40, 40, (1.0, 0.97, 0.92))
    area("rim", (0.50, 0.55, 0.35), (0, 0, 0.03), 0.25, 9, (0.90, 0.95, 1.0), size_y=0.8)
    area("fill", (0.45, -0.65, 0.30), (0, 0, 0.02), 1.0, 3.5, (0.95, 0.97, 1.0))

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
    exr = str(TMP / f"nx-stamp-{frame}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def pixels(exr):
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32), w, h


EXPOSURE = 0.46


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


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 and args[1] in ("draft", "final") else "draft"
    regrade = "regrade" in args
    for fr in ([1, 2, 3] if which == "all" else [int(which)]):
        exr = str(TMP / f"nx-stamp-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
