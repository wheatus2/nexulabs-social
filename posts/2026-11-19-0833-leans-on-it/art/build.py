"""Renders the pictures for this post with Blender's Python module (pip install bpy; run with python3.13).

One whiteboard on a green office wall: a made-up heating firm's week, written in marker (art/print.py).
Shot from the same side three ways, and the board changes each time:
  1  the whole week, the board running off the right and the bottom
  2  nearer: somebody has leant on Thursday
  3  the foot of the board and its pen tray: wiped, and used for the tea rota

  python3.13 build.py <1|2|3|all> [draft|final] [regrade]
writes art/render-0N.jpg (1080x1350). Units are centimetres. The type is set over it in slide-0N.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1350
TMP = Path(tempfile.gettempdir())
WALL = (0.010, 0.066, 0.040)       # bottle green, linear
EXPOSURE = 1.0
BW, BH = 150.0, 100.0              # the writing surface
FACE = -1.6                        # y of the surface (the wall is y = 0)
RED = (0.62, 0.012, 0.022)

SHOTS = {
    1: dict(loc=(-150, -215, 70), aim=(-12, 0, 70), lens=38, f=0.22, focus=(-30, FACE, 60), shift=(0.029, 0.022)),
    2: dict(loc=(-130, -91, 41), aim=(-45, 0, 41), lens=31.5, f=0.075, focus=(-30, FACE, 70), shift=(0.103, 0.484)),
    3: dict(loc=(-128, -118, 44), aim=(-50, 0, 44), lens=32.5, f=0.14, focus=(-50, FACE, 28), shift=(0.150, -0.345)),
}


PROBES = {"board TL": (-75, FACE, 100), "board TR": (75, FACE, 100), "board BL": (-75, FACE, 0), "board BR": (75, FACE, 0),
          "frame TL": (-77, -2.7, 102), "frame BL": (-77, -2.7, -2), "frame TR": (77, -2.7, 102), "frame BR": (77, -2.7, -2), "wed|thu": (47.4, FACE, 70), "thu|fri": (73, FACE, 70), "z41 left": (-75, FACE, 41), "sal text": (-52, FACE, 43.5), "kev": (-70, FACE, 76.5), "tea top": (-66, FACE, 55.8), "z41 right": (73, FACE, 41), "wed|thu top": (21.8, FACE, 100), "tue|wed top": (-3.8, FACE, 100), "tue|wed z37": (-3.8, FACE, 37),
          "thu|fri z37": (47.4, FACE, 37), "wed text": (-2.2, FACE, 80), "fri text end": (66, FACE, 80), "fri line": (73, FACE, 80), "z38 mid": (30, FACE, 38), "z58 right": (75, FACE, 58), "z30 left": (-75, FACE, 30.5), "z5 left": (-75, FACE, 5), "z5 right": (75, FACE, 5),
          "rota top": (-66, FACE, 56), "rota right": (-30, FACE, 30), "tray L": (-70, -9.6, -3), "tray R": (-14, -9.6, -3), "tray Rtop": (-14, -9.6, -1)}


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


def box(name, lo, hi, material, bevel=0.0, seg=3):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector(((v.co.x + .5) * (hi[0] - lo[0]) + lo[0], (v.co.y + .5) * (hi[1] - lo[1]) + lo[1], (v.co.z + .5) * (hi[2] - lo[2]) + lo[2]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(material)
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = seg; b.limit_method = "ANGLE"
        for p in me.polygons:
            p.use_smooth = True
    return ob


def cyl(name, p0, length, radius, material, axis="x", bevel=0.12, verts=48):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=radius, radius2=radius, depth=length)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(material)
    if axis == "x":
        ob.rotation_euler = (0, math.pi / 2, 0); ob.location = (p0[0] + length / 2, p0[1], p0[2])
    else:
        ob.rotation_euler = (math.pi / 2, 0, 0); ob.location = (p0[0], p0[1] - length / 2, p0[2])
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 3; b.limit_method = "ANGLE"; b.angle_limit = math.radians(50)
    for p in me.polygons:
        p.use_smooth = True
    return ob


def wall_mat():
    m, nt, p = mat("wall")
    N, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (*WALL, 1)
    p.inputs["Roughness"].default_value = 0.85; p.inputs["Specular IOR Level"].default_value = 0.08
    geo = N.new("ShaderNodeNewGeometry")
    a = N.new("ShaderNodeTexNoise"); a.inputs["Scale"].default_value = 9.0; a.inputs["Detail"].default_value = 5; a.inputs["Roughness"].default_value = 0.62
    b = N.new("ShaderNodeTexNoise"); b.inputs["Scale"].default_value = 0.22; b.inputs["Detail"].default_value = 3
    L.new(geo.outputs["Position"], a.inputs["Vector"]); L.new(geo.outputs["Position"], b.inputs["Vector"])
    add = N.new("ShaderNodeMath"); add.operation = "ADD"
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 5.0
    L.new(b.outputs["Fac"], mul.inputs[0]); L.new(a.outputs["Fac"], add.inputs[0]); L.new(mul.outputs["Value"], add.inputs[1])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.22; bump.inputs["Distance"].default_value = 0.035
    L.new(add.outputs["Value"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def board_mat(n):
    m, nt, p = mat("enamel")
    N, L = nt.nodes, nt.links
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / f".board-{n}.png")); tex.interpolation = "Cubic"; tex.extension = "EXTEND"
    L.new(tex.outputs["Color"], p.inputs["Base Color"])
    r = N.new("ShaderNodeTexImage"); r.image = bpy.data.images.load(str(HERE / f".rough-{n}.png")); r.image.colorspace_settings.name = "Non-Color"
    r.interpolation = "Cubic"; r.extension = "EXTEND"
    L.new(r.outputs["Color"], p.inputs["Roughness"])
    p.inputs["Specular IOR Level"].default_value = 0.5
    p.inputs["Coat Weight"].default_value = 0.35; p.inputs["Coat Roughness"].default_value = 0.07
    # enamelled steel is never dead flat: a long slow ripple
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.035; nz.inputs["Detail"].default_value = 1.5
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.10; bump.inputs["Distance"].default_value = 1.0
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"]); L.new(bump.outputs["Normal"], p.inputs["Coat Normal"])
    return m


def plain(name, col, rough, metal=0.0, coat=0.0):
    m, nt, p = mat(name)
    p.inputs["Base Color"].default_value = (*col, 1); p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal; p.inputs["Coat Weight"].default_value = coat
    return m


def brushed(name):
    m, nt, p = mat(name)
    N, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (0.62, 0.63, 0.64, 1); p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = 0.36; p.inputs["Anisotropic"].default_value = 0.6
    geo = N.new("ShaderNodeNewGeometry")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.3, 60, 60)
    L.new(geo.outputs["Position"], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3; nz.inputs["Detail"].default_value = 3
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def marker(x, y, z, colour, plastic, yaw=0.0):
    """A dry-wipe marker lying along x: pale barrel, coloured cap and end plug, a printed band."""
    root = link(bpy.data.objects.new("pen", None))
    cap = plain("cap", colour, 0.32, coat=0.3)
    parts = [cyl("barrel", (0, 0, 0), 9.4, 0.80, plastic),
             cyl("cap", (9.2, 0, 0), 4.3, 0.90, cap, bevel=0.2),
             cyl("clipring", (9.2, 0, 0), 0.5, 0.97, cap, bevel=0.08),
             cyl("plug", (-0.7, 0, 0), 0.9, 0.74, cap, bevel=0.2),
             cyl("band", (2.6, 0, 0), 4.4, 0.812, cap, bevel=0)]
    for o in parts:
        o.parent = root
    root.location = (x, y, z); root.rotation_euler = (0, 0, math.radians(yaw))
    return root


def scene(frame):
    sc = bpy.context.scene
    wall = bpy.data.meshes.new("wall"); s = 2500
    wall.from_pydata([(-s, 0, -s), (s, 0, -s), (s, 0, s), (-s, 0, s)], [], [(0, 1, 2, 3)])
    w = link(bpy.data.objects.new("wall", wall)); w.data.materials.append(wall_mat())

    # the writing surface
    me = bpy.data.meshes.new("board")
    me.from_pydata([(-BW / 2, FACE, 0), (BW / 2, FACE, 0), (BW / 2, FACE, BH), (-BW / 2, FACE, BH)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="uv")
    for lp, t in zip(me.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[lp.index].uv = t
    b = link(bpy.data.objects.new("board", me)); b.data.materials.append(board_mat(frame))

    alu = brushed("alu")
    F, D = 2.0, -2.7        # frame width, how far it stands off the wall
    for name, lo, hi in (("top", (-BW / 2 - F, D, BH), (BW / 2 + F, 0, BH + F)), ("bot", (-BW / 2 - F, D, -F), (BW / 2 + F, 0, 0)),
                         ("l", (-BW / 2 - F, D, 0), (-BW / 2, 0, BH)), ("r", (BW / 2, D, 0), (BW / 2 + F, 0, BH))):
        box(name, lo, hi, alu, bevel=0.35)
    grey = plain("corner", (0.045, 0.048, 0.05), 0.42)
    for sx in (-1, 1):
        for sz in (0, 1):
            x0 = sx * (BW / 2 + F / 2); z0 = BH + F / 2 if sz else -F / 2
            box("corner", (x0 - F / 2 - 0.25, D - 0.3, z0 - F / 2 - 0.25), (x0 + F / 2 + 0.25, 0, z0 + F / 2 + 0.25), grey, bevel=0.6, seg=5)
    # the pen tray, under the left half
    TX0, TX1 = -70.0, -14.0
    box("tray", (TX0, -9.6, -3.1), (TX1, D, -2.0), alu, bevel=0.3)
    box("lip", (TX0, -9.6, -3.1), (TX1, -9.0, -1.2), alu, bevel=0.22)
    for x in (TX0 - 0.5, TX1 - 0.3):
        box("end", (x, -9.9, -3.3), (x + 0.8, D + 0.2, -0.9), grey, bevel=0.3)

    plastic = plain("barrel", (0.80, 0.80, 0.78), 0.34, coat=0.2)
    marker(-57.5, -5.3, -1.19, RED, plastic, yaw=-3.5)
    marker(-41.0, -6.6, -1.19, (0.012, 0.012, 0.014), plastic, yaw=2.5)
    # the wiper
    felt = plain("felt", (0.03, 0.03, 0.034), 0.95)
    top = plain("grip", (0.02, 0.045, 0.035), 0.38, coat=0.25)
    ex, ey = -27.5, -3.0
    e1 = box("felt", (ex, ey - 4.6, -2.0), (ex + 11.5, ey, -0.9), felt, bevel=0.2)
    e2 = box("grip", (ex, ey - 4.6, -0.9), (ex + 11.5, ey, 2.6), top, bevel=0.5, seg=5)


def build(frame, quality, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 160 if final else 28
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 45
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.95, 0.97, 1.0, 1); bg.inputs["Strength"].default_value = 0.13

    scene(frame)
    shot = SHOTS[frame]

    # key: one window, high on the left and behind the camera, raking across the board
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 70; key.size_y = 95
    key.energy = 5.2e6; key.color = (1.0, 0.97, 0.93)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (-430, -330, 300); aim(ko, (0, 0, 45))
    # a flag between the window and the wall: the wall above the board falls into soft shade
    fm = bpy.data.meshes.new("flag")
    zl = lambda x: 207 - 0.093 * (x + 252)
    fm.from_pydata([(-900, -165, zl(-900)), (700, -165, zl(700)), (700, -165, 900), (-900, -165, 900)], [], [(0, 1, 2, 3)])
    fo_ = link(bpy.data.objects.new("flag", fm)); fo_.visible_camera = False; fo_.visible_glossy = False
    fo_.data.materials.append(plain("flagm", (0.02, 0.02, 0.02), 1.0))
    # a long strip light on the ceiling, for the shine along the frame and the pens
    st = bpy.data.lights.new("strip", "AREA"); st.shape = "RECTANGLE"; st.size = 240; st.size_y = 22
    st.energy = 5.5e5; st.color = (0.96, 0.98, 1.0)
    so = link(bpy.data.objects.new("strip", st)); so.location = (40, -150, 330); aim(so, (0, 0, 40))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 400; fl.energy = 3.2e5; fl.color = (0.95, 0.98, 1.0)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (260, -480, 120); aim(fo, (0, 0, 40))

    # the room the enamel mirrors: a window with glazing bars, off to the right and behind the camera
    em = bpy.data.materials.new("glass"); em.use_nodes = True
    e = em.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.92, 0.96, 1.0, 1); e.inputs["Strength"].default_value = 2.6
    em.node_tree.links.new(e.outputs["Emission"], em.node_tree.nodes["Material Output"].inputs["Surface"])
    for i in range(3):
        for j in range(2):
            pane = box("pane", (430, -520 + i * 96, 95 + j * 104), (431, -520 + i * 96 + 88, 95 + j * 104 + 96), em)
            pane.visible_camera = False; pane.visible_diffuse = False
    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]; cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"]
    if quality == "probe":
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update()
        for nm, pt in PROBES.items():
            v = world_to_camera_view(sc, co, Vector(pt))
            print(f"  f{frame} {nm:14s} x {v.x * W:7.0f}  y {(1 - v.y) * H:7.0f}")
        return None
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region
    exr = str(TMP / f"nx-board-{frame}.exr")
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
    x = np.clip(a, 0, None) * EXPOSURE
    x = np.where(x > 0.62, 0.62 + (1 - np.exp(-(x - 0.62) / 0.36)) * 0.34, x)     # a soft shoulder: the board stays off pure white
    x = np.clip(x, 0, 1)
    lum = (x * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    x = np.clip(lum + (x - lum) * 1.22, 0, 1)                                      # a little more colour in the paint and the red
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3 + frame)
    x += rng.normal(0, 0.007, (H, W, 1)).astype(np.float32)
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
        exr = str(TMP / f"nx-board-{fr}.exr")
        if quality == "probe":
            build(fr, quality); continue
        grade(exr if regrade else build(fr, quality), fr, quality)
