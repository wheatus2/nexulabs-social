"""Renders the pictures for this Reel with Blender's Python module (pip install bpy brotli).

Two black tent cards on one butter-yellow table, both for table 4 at 19:30 (made-up bookings), shot from the
same side (front left):
  1  both cards, low, the wall above them for the question
  2  close on the left card alone (Ellis, booked on the website)
  3  high and close on the right card alone (Patel, booked by phone)
  4  the same camera as 3, the same card now reading 20:00: with one diary, the phone booking is offered the next slot

  python3 build.py <1|2|3|4|all> [draft|final] [regrade]
writes art/render-0N.jpg at 1188x2112 (1.1x, so the Reel can push in without going soft). Units are centimetres.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1188, 2112
TMP = Path(tempfile.gettempdir())
BUTTER = (0.90, 0.60, 0.13)     # linear RGB, the table and the wall

CW, CH, LEAN = 9.0, 6.5, 17      # card face width, face height, lean from vertical (degrees)
CARDS = {"a": dict(x=-5.6, y=0.0, rot=7), "b": dict(x=5.4, y=1.6, rot=-5)}

SHOTS = {
    1: dict(loc=(-6.0, -34.0, 9.5), aim=(-0.3, 0.8, 3.0), lens=26, f=6.3, focus=(-5.6, -0.8, 3.2), shift=(0.0, 0.11), cards="ab"),
    2: dict(loc=(-13.0, -28.0, 9.0), aim=(-5.0, 0.0, 3.0), lens=46, f=2.8, focus=(-5.2, -0.9, 3.4), shift=(-0.035, 0.08), cards="a"),
    3: dict(loc=(3.0, -16.4, 22.0), aim=(5.6, 1.2, 2.0), lens=38, f=3.5, focus=(5.5, 0.7, 3.3), shift=(-0.015, 0.19), cards="b"),
    4: dict(loc=(3.0, -16.4, 22.0), aim=(5.6, 1.2, 2.0), lens=38, f=3.5, focus=(5.5, 0.7, 3.3), shift=(-0.015, 0.19), cards="b", tex={"b": "c"}),
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


def butter():
    m, nt, p = mat("butter")
    N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.62
    p.inputs["Specular IOR Level"].default_value = 0.35
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.25; nz.inputs["Detail"].default_value = 3
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.96; mr.inputs["To Max"].default_value = 1.03
    L.new(nz.outputs["Fac"], mr.inputs["Value"])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1
    mix.inputs["A"].default_value = (*BUTTER, 1)
    comb = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(mr.outputs["Result"], comb.inputs[k])
    L.new(comb.outputs["Color"], mix.inputs["B"]); L.new(mix.outputs["Result"], p.inputs["Base Color"])
    # painted wood: a faint grain under the paint and a fine orange-peel
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.6, 14, 1)
    L.new(geo.outputs["Position"], mp.inputs["Vector"])
    wv = N.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 0.6; wv.inputs["Distortion"].default_value = 6
    wv.inputs["Detail"].default_value = 4
    L.new(mp.outputs["Vector"], wv.inputs["Vector"])
    fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 70; fine.inputs["Detail"].default_value = 6
    L.new(geo.outputs["Position"], fine.inputs["Vector"])
    add = N.new("ShaderNodeMath"); add.operation = "ADD"
    sc1 = N.new("ShaderNodeMath"); sc1.operation = "MULTIPLY"; sc1.inputs[1].default_value = 0.35
    L.new(wv.outputs["Fac"], sc1.inputs[0]); L.new(sc1.outputs[0], add.inputs[0]); L.new(fine.outputs["Fac"], add.inputs[1])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.06; bump.inputs["Distance"].default_value = 0.02
    L.new(add.outputs[0], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def card_mat(img):
    m, nt, p = mat("print-" + img.stem)
    N, L = nt.nodes, nt.links
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(img)); tex.interpolation = "Cubic"
    # the png is sRGB; darken the black board a touch so it reads as black card, not grey
    L.new(tex.outputs["Color"], p.inputs["Base Color"])
    # the cream print is a little glossier than the soft-touch black board around it
    sep = N.new("ShaderNodeSeparateColor"); L.new(tex.outputs["Color"], sep.inputs["Color"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.02; mr.inputs["From Max"].default_value = 0.8
    mr.inputs["To Min"].default_value = 0.52; mr.inputs["To Max"].default_value = 0.34
    L.new(sep.outputs["Red"], mr.inputs["Value"]); L.new(mr.outputs["Result"], p.inputs["Roughness"])
    p.inputs["Specular IOR Level"].default_value = 0.42
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 160; nz.inputs["Detail"].default_value = 6
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def plain_card():
    m, nt, p = mat("board")
    p.inputs["Base Color"].default_value = (0.0055, 0.0055, 0.006, 1)
    p.inputs["Roughness"].default_value = 0.5
    p.inputs["Specular IOR Level"].default_value = 0.42
    return m


def tent(key, tex=None):
    """A folded A-frame card standing on the table, the printed face towards -y. Returns the parent empty."""
    c = CARDS[key]
    root = bpy.data.objects.new("tent-" + key, None); bpy.context.scene.collection.objects.link(root)
    a = math.radians(LEAN)
    th = 0.045                                  # board thickness
    zt = CH * math.cos(a)                       # height of the ridge
    dy = CH * math.sin(a)                       # how far each foot stands out from the ridge
    parts = []
    for side, sgn in (("front", -1), ("back", 1)):
        # the face as a plane from foot to ridge, solidified into board
        me = bpy.data.meshes.new(f"{key}-{side}")
        v = [(-CW / 2, sgn * dy, 0.0), (CW / 2, sgn * dy, 0.0), (CW / 2, 0.0, zt), (-CW / 2, 0.0, zt)]
        me.from_pydata(v, [], [(0, 1, 2, 3)] if sgn < 0 else [(3, 2, 1, 0)])
        me.uv_layers.new(name="uv")
        uvs = ((0, 0), (1, 0), (1, 1), (0, 1)) if sgn < 0 else ((0, 1), (1, 1), (1, 0), (0, 0))
        for li, uv in zip(me.loops, uvs):
            me.uv_layers[0].data[li.index].uv = uv
        ob = bpy.data.objects.new(f"{key}-{side}", me); bpy.context.scene.collection.objects.link(ob)
        sd = ob.modifiers.new("solid", "SOLIDIFY"); sd.thickness = th; sd.offset = 1.0; sd.use_rim = True
        sd.material_offset = 1; sd.material_offset_rim = 1
        bv = ob.modifiers.new("bevel", "BEVEL"); bv.width = 0.012; bv.segments = 2; bv.limit_method = "ANGLE"
        for p in me.polygons:
            p.use_smooth = False
        if sgn < 0:
            ob.data.materials.append(card_mat(HERE / f"card-{tex or key}.png"))
        else:
            ob.data.materials.append(plain_card())
        ob.data.materials.append(plain_card())
        ob.parent = root; parts.append(ob)
    # the fold: a small half-round along the ridge so the top is a bend, not a seam
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=th * 1.1, depth=CW, location=(0, 0, zt - th * 0.4),
                                        rotation=(0, math.radians(90), 0))
    fold = bpy.context.active_object; fold.data.materials.append(plain_card()); fold.parent = root
    for p in fold.data.polygons:
        p.use_smooth = True
    root.location = (c["x"], c["y"], 0)
    root.rotation_euler.z = math.radians(c["rot"])
    return root


def sweep():
    """Table and wall as one seamless curve: flat to y=26, a 22 cm cove, then straight up."""
    prof = [(-400.0, 0.0), (26.0, 0.0)]
    R = 22.0
    for i in range(1, 17):
        t = math.radians(90 * i / 16)
        prof.append((26.0 + R * math.sin(t), R - R * math.cos(t)))
    prof.append((26.0 + R, 300.0))
    bm = bmesh.new()
    rows = []
    for x in (-300.0, 300.0):
        rows.append([bm.verts.new((x, y, z)) for (y, z) in prof])
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    me = bpy.data.meshes.new("sweep"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("sweep", me); bpy.context.scene.collection.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = True
    ob.data.materials.append(butter())
    return ob


def build(frame, quality, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 96 if final else 24
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
    bg.inputs["Color"].default_value = (1.0, 0.95, 0.86, 1); bg.inputs["Strength"].default_value = 0.08

    shot = SHOTS[frame]
    sweep()
    cards = [tent(k, shot.get("tex", {}).get(k)) for k in shot["cards"]]

    # key: a small, hard-ish window low on the left and a little behind, so each card throws a long shadow
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 5; key.size_y = 9
    key.energy = 16000; key.color = (1.0, 0.96, 0.90)
    ko = bpy.data.objects.new("key", key); sc.collection.objects.link(ko)
    ko.location = (-46, 18, 26); aim(ko, (0, 0, 2))
    # a long soft strip high in front, for the sheen across the black card
    st = bpy.data.lights.new("strip", "AREA"); st.shape = "RECTANGLE"; st.size = 36; st.size_y = 3
    st.energy = 1100; st.color = (1.0, 0.99, 0.97)
    so = bpy.data.objects.new("strip", st); sc.collection.objects.link(so)
    so.location = (4, -30, 30); aim(so, (0, 0, 3))
    only = bpy.data.collections.new("cards-only"); sc.collection.children.link(only)
    for r in cards:
        for o in r.children:
            only.objects.link(o)
    so.light_linking.receiver_collection = only
    # fill from the camera side so the shadows stay coloured, not black
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 60; fl.energy = 3000; fl.color = (1.0, 0.97, 0.92)
    fo = bpy.data.objects.new("fill", fl); sc.collection.objects.link(fo)
    fo.location = (20, -70, 40); aim(fo, (0, 0, 0))

    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]
    cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 0.1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"]

    exr = str(TMP / f"nx-table-{frame}.exr")
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
    x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    x = np.clip(x, 0, 1)
    # grade every frame to one backdrop: the wall at the top of the frame matches WALL (sRGB) in all four
    lin = lambda c: ((c / 255 + 0.055) / 1.055) ** 2.4
    med = np.median(x[int(H * 0.05):int(H * 0.21)].reshape(-1, 3), 0)
    x = x * np.clip(np.array([lin(c) for c in WALL]) / np.maximum(med, 1e-4), 0.8, 1.25)[None, None, :]
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.10 * np.clip(r - 0.6, 0, 1) ** 1.5)[..., None]
    rng = np.random.default_rng(3 + frame)
    x += rng.normal(0, 0.008, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"render-{frame:02d}.jpg" if quality == "final" else f".draft-{frame:02d}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst)


EXPOSURE = 2.0
WALL = (206, 176, 65)

if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 else "draft"
    regrade = "regrade" in args
    for fr in ([1, 2, 3, 4] if which == "all" else [int(which)]):
        exr = str(TMP / f"nx-table-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
