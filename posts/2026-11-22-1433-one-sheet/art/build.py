"""Renders the pictures for this Reel with Blender's Python module (pip install bpy; run with python3.13).

One made-up concertina leaflet standing on a red paper sweep: one sheet of white card, seven pages of
9 x 15 cm, a numeral and a name on each (art/print.py) and one red line running through every fold.
  1  the leaflet opens from behind page 1 (eight positions, one camera)
  2  one long picture of the whole leaflet, which reel.html tracks along (scenes 2 and 4)
  3  the fold between pages 1 and 2 from above, as it opens

  python3.13 print.py
  python3.13 build.py <scene> [draft|final] [state letter|all]
writes art/r-<scene><state>.jpg. Units are centimetres, so a real f/4 is aperture_fstop 0.04.
The type is set over the pictures in reel.html.
"""
import sys, math, tempfile, os
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.gettempdir())
PW, PH, NP = 9.0, 15.0, 7
THK = 0.05
RED = (0.56, 0.0125, 0.0215)       # the sweep, linear
EXPOSURE = 1.0

# state letter -> half angle of the zigzag in degrees (90 is shut)
OPEN1 = dict(a=87.0, b=84.0, c=76.0, d=64.0, e=52.0, f=43.0, g=37.5, h=35.0)
STATES = {1: OPEN1, 2: dict(a=35.0), 3: dict(a=41.5, b=40.6, c=39.0, d=37.4, e=36.2, f=35.4, g=35.0)}
SIZE = {1: (1134, 2016), 2: (3948, 2016), 3: (1134, 2016)}
TH1 = -30.0                         # page 1 keeps this heading while the rest opens behind it

# 1: 49 px to the cm at 1080 wide. 2: the long picture the Reel tracks along, 70 px to the cm, no perspective.
SHOTS = {
    1: dict(loc=(9.47, -110, 24), aim=(9.47, 0, 8.3), lens=101, f=0.10, focus=(4, -2, 8)),
    2: dict(loc=(33.0, -200, 37.3), aim=(33.0, 0, 9.2), ortho=27.43),
    3: dict(loc=(9.3, -44.5, 73), aim=(9.75, -1.5, 6.7), lens=190, f=0.30, focus=(7.8, -4.5, 9)),
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


def link(ob):
    bpy.context.scene.collection.objects.link(ob); return ob


def plan(phi):
    """The fold lines in plan: page 1 runs at TH1, every other page at TH1 + 2*phi."""
    pts = [(0.0, 0.0)]; hd = []
    for i in range(NP):
        th = math.radians(TH1 + (0 if i % 2 == 0 else 2 * phi))
        if phi > 80 and i % 2 == 1:
            th = math.radians(TH1 + 2 * phi)
        hd.append(th)
        pts.append((pts[-1][0] + PW * math.cos(th), pts[-1][1] + PW * math.sin(th)))
    return pts, hd


def leaflet(phi):
    pts, hd = plan(phi)
    rng = np.random.default_rng(7)
    NS = 28
    P, U = [], []
    R = 0.16                                   # the folds are scored, not sharp: this much of each page bends
    for i in range(NP):
        a, b = np.array(pts[i]), np.array(pts[i + 1])
        d = (b - a) / PW; n = np.array([-d[1], d[0]])
        bow = (0.10 + 0.05 * rng.random()) * (1 if i % 2 == 0 else -1) * min(1.0, (90 - phi) / 30 + 0.15)
        for k in range(NS + 1):
            t = k / NS
            if (k == 0 and i > 0):
                continue
            p = a + d * PW * t + n * bow * math.sin(math.pi * t)
            P.append(p); U.append((i + t) / NP)
    P = np.array(P); U = np.array(U)
    # round each fold: pull the fold point towards the chord of its neighbours
    for i in range(1, NP):
        j = i * NS
        P[j] = 0.5 * P[j] + 0.25 * (P[j - 1] + P[j + 1])
    n = len(P)
    verts, faces, uvs = [], [], []
    lean = 0.05 * np.sin(np.arange(n) * 0.11 + 1.0)
    for i in range(n):
        tx = P[i] if i == 0 else P[i]
        verts.append((P[i][0], P[i][1], 0.0)); verts.append((P[i][0], P[i][1] + lean[i] * 0.0, PH))
    for i in range(n - 1):
        faces.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
        uvs.append([(U[i], 0), (U[i + 1], 0), (U[i + 1], 1), (U[i], 1)])
    me = bpy.data.meshes.new("leaflet"); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name="uv")
    for poly, fu in zip(me.polygons, uvs):
        poly.use_smooth = True
        for j, li in enumerate(poly.loop_indices):
            uv.data[li].uv = fu[j]
    ob = link(bpy.data.objects.new("leaflet", me))
    ob.data.materials.append(paper("front", True))
    ob.data.materials.append(paper("back", False))
    so = ob.modifiers.new("s", "SOLIDIFY"); so.thickness = THK; so.offset = 1.0
    so.material_offset = 1; so.material_offset_rim = 1; so.use_even_offset = True
    return ob


def paper(name, printed):
    m, nt, p = mat(name)
    N, L = nt.nodes, nt.links
    if printed:
        tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / ".sheet.png")); tex.interpolation = "Cubic"; tex.extension = "EXTEND"
        L.new(tex.outputs["Color"], p.inputs["Base Color"])
    else:
        p.inputs["Base Color"].default_value = (0.94, 0.93, 0.90, 1)
    p.inputs["Roughness"].default_value = 0.62
    p.inputs["Specular IOR Level"].default_value = 0.12
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 90; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.7
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.10; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def sweep():
    m, nt, p = mat("sweep")
    N, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (*RED, 1)
    p.inputs["Roughness"].default_value = 0.85; p.inputs["Specular IOR Level"].default_value = 0.18
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 55; nz.inputs["Detail"].default_value = 5
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    Y0, RR, S = 150.0, 90.0, 1500.0
    prof = [(-S, 0.0), (Y0, 0.0)]
    for k in range(1, 25):
        a = math.pi / 2 * k / 24
        prof.append((Y0 + RR * math.sin(a), RR - RR * math.cos(a)))
    prof.append((Y0 + RR, S))
    verts, faces = [], []
    for y, z in prof:
        verts += [(-S, y, z), (S, y, z)]
    for i in range(len(prof) - 1):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for q in me.polygons:
        q.use_smooth = True
    ob = link(bpy.data.objects.new("sweep", me)); ob.data.materials.append(m)


def build(scene, quality, letter):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    hero = letter == sorted(STATES[scene])[-1]
    sc.cycles.samples = (120 if hero else 48) if final else 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.threads_mode = "FIXED"; sc.render.threads = int(os.environ.get("NX_THREADS", "4"))
    W, H = SIZE[scene]
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1.0, 0.96, 0.94, 1); bg.inputs["Strength"].default_value = 0.14

    sweep()
    leaflet(STATES[scene][letter])
    shot = SHOTS[scene]

    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 70; key.size_y = 110
    key.energy = 10.0e6; key.color = (1.0, 0.97, 0.93)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (-560, -260, 300); aim(ko, (20, 0, 0))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 500; fl.energy = 0.45e6; fl.color = (1.0, 0.97, 0.96)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (480, -520, 300); aim(fo, (20, 0, 0))

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 36
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.clip_start = 1
    if "ortho" in shot:
        cam.type = "ORTHO"; cam.ortho_scale = shot["ortho"]
    else:
        cam.lens = shot["lens"]
        cam.dof.use_dof = True
        cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
        cam.dof.aperture_fstop = shot["f"]
    exr = str(TMP / f"nx-sheet-{scene}{letter}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def grade(exr, scene, quality, letter):
    from PIL import Image
    W, H = SIZE[scene]
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    x = np.clip(a, 0, None) * EXPOSURE
    x = np.where(x > 0.72, 0.72 + (1 - np.exp(-(x - 0.72) / 0.30)) * 0.25, x)     # a soft shoulder: the card stays off pure white
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3 + scene)
    x += rng.normal(0, 0.006, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"r-{scene}{letter}.jpg" if quality == "final" else f".d-{scene}{letter}.jpg")
    out.save(dst, quality=93, subsampling=0)
    print("wrote", dst, flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    scene = int(args[0])
    quality = args[1] if len(args) > 1 else "draft"
    which = args[2] if len(args) > 2 else sorted(STATES[scene])[-1]
    letters = sorted(STATES[scene]) if which == "all" else list(which)
    for letter in letters:
        exr = str(TMP / f"nx-sheet-{scene}{letter}.exr")
        grade(exr if "regrade" in args else build(scene, quality, letter), scene, quality, letter)
    (HERE / f".done-{scene}-{quality}").write_text("ok")
