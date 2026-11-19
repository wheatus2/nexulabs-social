"""Renders the pictures for this post with Blender's Python module (pip install bpy scipy).

An arcade cabinet seen from the player's side, one locked camera, three states of the screen (art/screen.py):
  1  GTA 6 IS OUT TODAY.  loading bar full, the start button lit
  2  SO IS HALF YOUR TEAM.  eight little players, four gone dim
  3  YOUR WEBSITE ISN'T.  still online, three new enquiries
  python3.13 build.py <frame 1|2|3|all> [draft|final] [regrade]
writes art/render-0N.jpg (1080x1350). Units are centimetres. The screen is a real light: it lights the panel and the stick.
Helpers (mat, grid, aim) come from the paper dart post's build.py.
"""
import sys, math, tempfile, importlib.util
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("dart", HERE.parents[1] / "2026-11-16-0833-somewhere-to-land/art/build.py")
D = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(D)
W, H = 1080, 1350
TMP = Path(tempfile.gettempdir())
SW, SH = 49.0, 57.0                 # the screen: 98 x 114 dots at half a centimetre
TILT = math.radians(9)              # the screen leans back
CAM = dict(loc=(-17.0, -104.0, 30.0), aim=(0.6, 0.0, 22.6), lens=37, f=0.09, focus=(0.0, 0.0, 30.0), shift=(0.0, 0.0))
GREEN = (0.06, 1.0, 0.26)
BADGE = 2.2


def plastic(name, col, rough, coat=0.0):
    m, nt, p = D.mat(name)
    p.inputs["Base Color"].default_value = (*col, 1); p.inputs["Roughness"].default_value = rough
    p.inputs["Coat Weight"].default_value = coat
    return m


def box(name, size, loc, material, bevel=0.3, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 4
    o.data.materials.append(material)
    for pl in o.data.polygons: pl.use_smooth = True
    return o


def lathe(name, profile, material, loc, steps=72):
    """Turn a profile [(r, z), ...] round the z axis."""
    verts, faces = [], []
    n = len(profile)
    for s in range(steps):
        a = 2 * math.pi * s / steps
        for r, z in profile:
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for s in range(steps):
        s2 = (s + 1) % steps
        for i in range(n - 1):
            faces.append((s * n + i, s2 * n + i, s2 * n + i + 1, s * n + i + 1))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(material); o.location = loc
    return o


def cabinet(frame):
    sc = bpy.context.scene
    root = bpy.data.objects.new("screen", None); sc.collection.objects.link(root)
    # the tube: a gently bulged sheet that gives off the picture, under a glossy face
    m, nt, p = D.mat("tube")
    N, L = nt.nodes, nt.links
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / f".screen-{frame}.png")); tex.interpolation = "Cubic"
    tex.extension = "EXTEND"
    p.inputs["Base Color"].default_value = (0.004, 0.004, 0.008, 1)
    p.inputs["Roughness"].default_value = 0.07
    L.new(tex.outputs["Color"], p.inputs["Emission Color"]); p.inputs["Emission Strength"].default_value = 7.0

    def tube(u, v):
        x, z = (u - 0.5) * SW, (v - 0.5) * SH
        bulge = 1.6 * (1 - (2 * u - 1) ** 2) * (1 - (2 * v - 1) ** 2) ** 0.6
        return (x, -bulge, z), (u, v)
    t = D.grid("tube", tube, 48, 60, m); t.parent = root
    # the cabinet front: one black face with the screen set back in a bevelled opening
    bz = plastic("bezel", (0.006, 0.006, 0.010), 0.30)
    FY, hw, hh = -6.5, SW / 2 + 0.1, SH / 2 + 0.1
    ox, top, bot = 110.0, 80.0, -45.0
    o4 = [(-ox, FY, bot), (ox, FY, bot), (ox, FY, top), (-ox, FY, top)]
    i4 = [(-hw, FY, -hh), (hw, FY, -hh), (hw, FY, hh), (-hw, FY, hh)]
    b4 = [(-hw + 0.9, 0.6, -hh + 0.9), (hw - 0.9, 0.6, -hh + 0.9), (hw - 0.9, 0.6, hh - 0.9), (-hw + 0.9, 0.6, hh - 0.9)]
    faces = []
    for k in range(4):
        k2 = (k + 1) % 4
        faces.append((k, k2, 4 + k2, 4 + k)); faces.append((4 + k, 4 + k2, 8 + k2, 8 + k))
    me = bpy.data.meshes.new("front"); me.from_pydata(o4 + i4 + b4, [], faces)
    fr = bpy.data.objects.new("front", me); sc.collection.objects.link(fr); fr.data.materials.append(bz); fr.parent = root
    bv = fr.modifiers.new("b", "BEVEL"); bv.width = 0.9; bv.segments = 5; bv.limit_method = "ANGLE"
    wall = plastic("wall", (0.004, 0.004, 0.007), 0.75); fr.data.materials.append(wall)
    for pl in me.polygons:
        pl.use_smooth = True
        if pl.index % 2: pl.material_index = 1          # the walls of the opening are matt, so they don't mirror the letters
    # the maker's badge under the screen: the Nexulabs wordmark, lit from behind
    m2, nt2, p2 = D.mat("badge")
    tx = nt2.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(str(HERE / ".logo.png")); tx.extension = "CLIP"
    p2.inputs["Base Color"].default_value = (0.006, 0.006, 0.010, 1); p2.inputs["Roughness"].default_value = 0.30
    nt2.links.new(tx.outputs["Color"], p2.inputs["Emission Color"]); p2.inputs["Emission Strength"].default_value = BADGE
    bw_, bh_ = 13.0, 13.0 * 440 / 2100
    bx, bzz = SW / 2 - 2.0 - bw_ / 2 + 0.3, -hh - 4.4
    mb = bpy.data.meshes.new("badge")
    mb.from_pydata([(bx - bw_ / 2, FY - 0.02, bzz - bh_ / 2), (bx + bw_ / 2, FY - 0.02, bzz - bh_ / 2), (bx + bw_ / 2, FY - 0.02, bzz + bh_ / 2), (bx - bw_ / 2, FY - 0.02, bzz + bh_ / 2)], [], [(0, 1, 2, 3)])
    uvl = mb.uv_layers.new(name="uv")
    for lp, uv in zip(mb.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): uvl.data[lp.index].uv = uv
    bo = bpy.data.objects.new("badge", mb); sc.collection.objects.link(bo); bo.data.materials.append(m2); bo.parent = root
    root.rotation_euler = (-TILT, 0, 0)
    root.location = (0, 0, 30.0)
    # the control panel: a deep shelf under the screen, sloping to the player, glossy enough to carry the screen's light
    m, nt, p = D.mat("panel")
    N, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (0.006, 0.006, 0.012, 1); p.inputs["Roughness"].default_value = 0.20
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 8
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.30; mr.inputs["To Max"].default_value = 0.44
    L.new(nz.outputs["Fac"], mr.inputs["Value"]); L.new(mr.outputs["Result"], p.inputs["Roughness"])
    slope = math.radians(7)
    PY, PZ = -29.0, -8.0                         # the middle of the panel
    box("panel", (240, 46, 4), (0, PY, PZ), m, bevel=0.8, rot=(slope, 0, 0))

    def on_panel(x, d):                           # a point on the panel top, d cm towards the player from its middle
        return Vector((x, PY - d * math.cos(slope), PZ + 2.0 * math.cos(slope) - d * math.sin(slope)))
    # the stick: black collar, steel shaft, a ball top in the one green
    steel, nt, p = D.mat("steel"); p.inputs["Metallic"].default_value = 1; p.inputs["Roughness"].default_value = 0.18
    p.inputs["Base Color"].default_value = (0.62, 0.63, 0.66, 1)
    black = plastic("black", (0.008, 0.008, 0.010), 0.28)
    ball = plastic("ball", (0.012, 0.42, 0.10), 0.10, coat=1.0)
    j = bpy.data.objects.new("stick", None); sc.collection.objects.link(j)
    for o in (lathe("collar", [(0, 0.0), (3.4, 0.0), (3.3, 0.35), (1.6, 0.9), (0, 0.9)], black, (0, 0, 0)),
              lathe("shaft", [(0.55, 0.5), (0.55, 6.6)], steel, (0, 0, 0))):
        o.parent = j
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=2.1, location=(0, 0, 7.6))
    b = bpy.context.object; b.data.materials.append(ball); b.parent = j
    for pl in b.data.polygons: pl.use_smooth = True
    j.location = on_panel(-13.0, -7.0); j.rotation_euler = (slope + math.radians(5), math.radians(-7), 0)
    # three buttons: a black ring, a dished cap; the one being pressed this frame glows
    for k, x in enumerate((6.0, 13.0, 20.0)):
        lit = (k == frame - 1)
        cap, nt, p = D.mat(f"cap{k}")
        p.inputs["Base Color"].default_value = (0.02, 0.30, 0.08, 1) if lit else (0.05, 0.05, 0.07, 1)
        p.inputs["Roughness"].default_value = 0.16 if lit else 0.5; p.inputs["Coat Weight"].default_value = 1.0 if lit else 0.0
        if lit:
            p.inputs["Emission Color"].default_value = (*GREEN, 1); p.inputs["Emission Strength"].default_value = 3.2
        g = bpy.data.objects.new(f"button{k}", None); sc.collection.objects.link(g)
        ring = lathe(f"ring{k}", [(0, 0.0), (2.3, 0.0), (2.3, 0.45), (2.05, 0.7), (1.75, 0.7), (1.75, 0.2), (0, 0.2)], black, (0, 0, 0))
        dish = [(1.62 * math.sin(t), 0.95 - 0.16 * math.cos(t) ** 2 - (0.55 if False else 0) + (-0.5 if False else 0)) for t in [i * math.pi / 2 / 12 for i in range(13)]]
        capo = lathe(f"capo{k}", [(0, 0.80)] + [(r, z) for r, z in dish[1:]] + [(1.66, 0.82), (1.66, 0.2)], cap, (0, 0, -0.18 if lit else 0))
        ring.parent = g; capo.parent = g
        g.location = on_panel(x - 1.0, -11.0 + 1.8 * (k % 2)); g.rotation_euler = (slope, 0, 0)


def build(frame, quality, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 128 if final else 36
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
    bg.inputs["Color"].default_value = (0.012, 0.014, 0.05, 1); bg.inputs["Strength"].default_value = 0.12
    cabinet(frame)
    # the arcade behind the player: one long soft strip high on the left, cool, so the black plastic has an edge
    for nm, loc, size, energy, col in (("strip", (-160, -120, 190), (40, 260), 2.2e6, (0.55, 0.62, 1.0)),
                                       ("far", (210, -60, 120), (30, 160), 0.7e6, (0.75, 0.60, 1.0))):
        l = bpy.data.lights.new(nm, "AREA"); l.shape = "RECTANGLE"; l.size, l.size_y = size; l.energy = energy; l.color = col
        o = bpy.data.objects.new(nm, l); sc.collection.objects.link(o); o.location = loc; D.aim(o, (0, -20, 5))
    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = CAM["loc"]; D.aim(co, CAM["aim"])
    cam.lens = CAM["lens"]; cam.shift_x, cam.shift_y = CAM["shift"]; cam.clip_start = 0.5
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(CAM["focus"]) - co.location).length
    cam.dof.aperture_fstop = CAM["f"]
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region
    exr = str(TMP / f"nx-arcade-{frame}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def grade(exr, frame, quality):
    """Camera work after the render: bloom round the lit dots, a film curve, a little grain."""
    from scipy.ndimage import gaussian_filter
    from PIL import Image
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    a = np.clip(a, 0, None)
    hot = np.clip(a - 1.0, 0, 30)
    bloom = sum(wt * np.stack([gaussian_filter(hot[..., c], r) for c in range(3)], -1)
                for r, wt in ((4, 0.10), (14, 0.07), (48, 0.05), (130, 0.035)))
    a = a + bloom
    x = a * 0.80
    x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3)
    x += rng.normal(0, 0.010, (H, W, 1)).astype(np.float32)
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
        exr = str(TMP / f"nx-arcade-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
