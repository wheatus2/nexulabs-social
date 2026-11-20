"""Renders the pictures for this carousel with Blender's Python module (pip install bpy; run with python3.13).

One made-up breaker box on a plum wall: a white enclosure, four charcoal breakers with yellow levers,
a label under each (WEBSITE, EMAIL, DOMAIN, HOSTING) and a hand-filled "Who to ring" chart inside the open door.
Shot from the same side three ways, the box changing:
  1  the whole box, door open, the EMAIL breaker tripped
  2  right up against the chart inside the door, the row out of focus behind
  3  the row close up from below, all four on, a yellow Nexulabs sticker above them (the door is left out of this shot)
Prints: art/print.py.   python3.13 build.py <1|2|3|all> [draft|final|probe] [regrade]
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
PLUM = (0.036, 0.004, 0.048)
EXPOSURE = 1.0
UW, UH, FY = 15.0, 19.0, -7.5          # enclosure width, height, front plane
XS = (-3.6, -1.2, 1.2, 3.6)            # breaker centres
ZR = 11.5                              # row centre height
DOOR = 200.0                           # door swing, degrees about the hinge

SHOTS = {
    1: dict(loc=(46, -62, 17), aim=(-5, -7, 9.5), lens=58, f=0.9, focus=(0, -8, 11), shift=(-0.05, 0.081), off=(1,), chart="a", sticker=False),
    2: dict(loc=(6, -52, 13), aim=(-15, -11, 9.5), lens=58, f=0.14, focus=(-14, -11, 11), shift=(0.0424, 0.217), off=(1,), chart="a", sticker=False),
    3: dict(loc=(20, -36, 3), aim=(0.8, -7.5, 10.5), lens=40, f=0.9, focus=(0, -8.5, 11.5), shift=(0.1126, 0.17), off=(), chart="b", sticker=True, nodoor=True),
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


def plastic(name, col, rough, bump=0.05, scale=140, coat=0.15):
    m, nt, p = mat(name)
    N_, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (*col, 1); p.inputs["Roughness"].default_value = rough
    p.inputs["Coat Weight"].default_value = coat; p.inputs["Coat Roughness"].default_value = 0.2
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    b = N_.new("ShaderNodeBump"); b.inputs["Strength"].default_value = bump; b.inputs["Distance"].default_value = 0.006
    L.new(nz.outputs["Fac"], b.inputs["Height"]); L.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def printed(name, png, rough=0.6, paper=True):
    m, nt, p = mat(name)
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / png)); tex.interpolation = "Cubic"; tex.extension = "EXTEND"
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough; p.inputs["Specular IOR Level"].default_value = 0.3
    if paper:
        N_, L = nt.nodes, nt.links
        tc = N_.new("ShaderNodeTexCoord")
        nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60; nz.inputs["Detail"].default_value = 6
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        b = N_.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.10; b.inputs["Distance"].default_value = 0.008
        L.new(nz.outputs["Fac"], b.inputs["Height"]); L.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def box(name, lo, hi, material, bevel=0.0, seg=5):
    lo, hi = Vector(lo), Vector(hi)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((v.co.x + .5) * (hi.x - lo.x) + lo.x, (v.co.y + .5) * (hi.y - lo.y) + lo.y, (v.co.z + .5) * (hi.z - lo.z) + lo.z))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new(name, me))
    if material:
        ob.data.materials.append(material)
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = seg; b.limit_method = "ANGLE"; b.angle_limit = math.radians(50)
        for p in me.polygons:
            p.use_smooth = True
    return ob


def cut(ob, lo, hi, bevel=0.0):
    c = box("cutter", lo, hi, None); c.hide_render = True; c.display_type = "WIRE"
    m = ob.modifiers.new("cut", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = c; m.solver = "EXACT"
    if bevel:
        b = ob.modifiers.new("b2", "BEVEL"); b.width = bevel; b.segments = 3; b.limit_method = "ANGLE"; b.angle_limit = math.radians(60)


def hull(name, pts, material, bevel=0.0, seg=4):
    bm = bmesh.new()
    for p in pts:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(material)
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = seg; b.limit_method = "ANGLE"; b.angle_limit = math.radians(35)
    for p in me.polygons:
        p.use_smooth = True
    return ob


def cyl(name, a, b, rad, material, n=64, bevel=0.0):
    a, b = Vector(a), Vector(b)
    d = (b - a); L = d.length
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=rad, radius2=rad, depth=L)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(material)
    ob.location = (a + b) / 2
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    for p in me.polygons:
        p.use_smooth = len(p.vertices) == 4
    if bevel:
        m = ob.modifiers.new("b", "BEVEL"); m.width = bevel; m.segments = 3; m.limit_method = "ANGLE"; m.angle_limit = math.radians(60)
    return ob


def sheet(name, corners, material, uvs=((0, 0), (1, 0), (1, 1), (0, 1)), thick=0.02):
    """A printed sheet: four corners in order bottom-left, bottom-right, top-right, top-left as the reader sees it."""
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(c) for c in corners], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="uv")
    for lp in me.loops:
        uv.data[lp.index].uv = uvs[lp.vertex_index]
    ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(material)
    if thick:
        s = ob.modifiers.new("s", "SOLIDIFY"); s.thickness = thick; s.offset = -1
    return ob


def face_plate(name, xc, material):
    """The printed front of a breaker, with a hole where the lever slot is."""
    x0, x1, z0, z1 = xc - 1.17, xc + 1.17, ZR - 1.7, ZR + 1.7
    sx0, sx1, sz0, sz1 = xc - 0.52, xc + 0.52, ZR - 1.02, ZR + 1.02
    y = FY - 0.8 - 0.004
    V = [(x0, z0), (x1, z0), (x1, z1), (x0, z1), (sx0, sz0), (sx1, sz0), (sx1, sz1), (sx0, sz1)]
    F = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(name); me.from_pydata([(x, y, z) for x, z in V], [], F)
    uv = me.uv_layers.new(name="uv")
    for lp in me.loops:
        v = me.vertices[lp.vertex_index].co
        uv.data[lp.index].uv = ((v.x - x0) / (x1 - x0), (v.z - z0) / (z1 - z0))
    ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(material)
    return ob


def scene(frame):
    shot = SHOTS[frame]
    # the wall
    me = bpy.data.meshes.new("wall"); me.from_pydata([(-600, 0, -600), (600, 0, -600), (600, 0, 600), (-600, 0, 600)], [], [(0, 1, 2, 3)])
    wall = link(bpy.data.objects.new("wall", me))
    m, nt, p = mat("wall"); p.inputs["Base Color"].default_value = (*PLUM, 1); p.inputs["Roughness"].default_value = 0.92; p.inputs["Specular IOR Level"].default_value = 0.08
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.6
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.22; b.inputs["Distance"].default_value = 0.03
    nt.links.new(nz.outputs["Fac"], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    wall.data.materials.append(m)

    white = plastic("white", (0.78, 0.78, 0.76), 0.36)
    dark = plastic("dark", (0.011, 0.012, 0.014), 0.42, bump=0.08, scale=220)
    slot = plastic("slot", (0.004, 0.004, 0.004), 0.6)
    yel = plastic("lever", (0.90, 0.74, 0.012), 0.30, bump=0.03, coat=0.4)
    steel, nt, p = mat("steel"); p.inputs["Base Color"].default_value = (0.55, 0.55, 0.56, 1); p.inputs["Metallic"].default_value = 1; p.inputs["Roughness"].default_value = 0.32

    # enclosure, with the slot the breakers stand in
    body = box("body", (-UW / 2, FY, 0), (UW / 2, -4.6, UH), white, bevel=0.85, seg=8)
    box("base", (-UW / 2 + 0.22, -5.4, 0.22), (UW / 2 - 0.22, 0, UH - 0.22), white, bevel=0.5, seg=5)
    cut(body, (-4.86, FY - 1, ZR - 2.3), (4.86, FY + 1.0, ZR + 2.3), bevel=0.07)
    box("back", (-4.9, FY + 0.95, ZR - 2.4), (4.9, FY + 1.2, ZR + 2.4), slot)

    for i, xc in enumerate(XS):
        on = i not in shot["off"]
        pts = []
        for x in (xc - 1.17, xc + 1.17):
            pts += [(x, FY + 1.0, ZR - 2.25), (x, FY + 1.0, ZR + 2.25), (x, FY - 0.25, ZR - 2.25), (x, FY - 0.25, ZR + 2.25),
                    (x, FY - 0.8, ZR - 1.7), (x, FY - 0.8, ZR + 1.7)]
        nose = hull(f"nose{i}", pts, dark, bevel=0.06, seg=3)
        c = box("cutter", (xc - 0.5, FY - 1.5, ZR - 1.0), (xc + 0.5, FY - 0.1, ZR + 1.0), None); c.hide_render = True
        mm = nose.modifiers.new("cut", "BOOLEAN"); mm.operation = "DIFFERENCE"; mm.object = c; mm.solver = "EXACT"
        nose.modifiers.move(len(nose.modifiers) - 1, 0)
        box(f"well{i}", (xc - 0.5, FY - 0.12, ZR - 1.0), (xc + 0.5, FY - 0.05, ZR + 1.0), slot)
        face_plate(f"face{i}", xc, printed(f"face{i}", f".face-{i + 1}-{'on' if on else 'off'}.png", rough=0.45, paper=False))
        # the lever: a barrel on the pivot and a paddle, up for on
        a = math.radians(32 if on else -32)
        piv = Vector((xc, FY - 0.42, ZR))
        cyl(f"barrel{i}", piv + Vector((-0.44, 0, 0)), piv + Vector((0.44, 0, 0)), 0.56, yel, bevel=0.05)
        d = Vector((0, -math.cos(a), math.sin(a))); n = Vector((0, math.sin(a), math.cos(a)))
        pts = []
        for x in (-0.44, 0.44):
            for (t, hgt) in ((0.0, 0.42), (1.05, 0.34), (1.62, 0.24)):
                for s in (-1, 1):
                    pts.append(piv + Vector((x * (1.0 if t < 1.5 else 0.94), 0, 0)) + d * t + n * hgt * s)
        hull(f"lever{i}", pts, yel, bevel=0.09, seg=4)

    # the label strip under the row
    lab = printed("labels", ".labels.png")
    y = FY - 0.012
    sheet("labels", [(-4.8, y, 3.0), (4.8, y, 3.0), (4.8, y, 8.2), (-4.8, y, 8.2)], lab, thick=0.012)
    if shot["sticker"]:
        st = printed("sticker", ".sticker.png", rough=0.7, paper=False); st.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.1
        sheet("sticker", [(-4.8, y, 14.75), (4.8, y, 14.75), (4.8, y, 17.75), (-4.8, y, 17.75)], st, thick=0.012)

    # cover screws
    for sx, sz in ((6.25, 1.35), (6.25, UH - 1.35), (-6.25, 1.35), (-6.25, UH - 1.35)):
        cyl("screw", (sx, FY + 0.2, sz), (sx, FY - 0.07, sz), 0.36, steel, n=40, bevel=0.03)
        box("slotcut", (sx - 0.30, FY - 0.075, sz - 0.045), (sx + 0.30, FY - 0.06, sz + 0.045), slot)

    # conduit out of the bottom, down the wall
    cyl("gland", (0, -2.4, 0.3), (0, -2.4, -1.5), 1.45, white, bevel=0.12)
    cyl("conduit", (0, -2.4, -1.0), (0, -2.4, -300), 1.05, white)
    box("clip", (-2.3, -3.75, -19.2), (2.3, 0, -17.6), white, bevel=0.3)

    # the door, hinged on the left, swung right round; the chart is stuck inside it
    hinge = Vector((-UW / 2 - 0.35, FY - 0.1, 0))
    piv = link(bpy.data.objects.new("hinge", None)); piv.location = hinge; piv.rotation_euler = (0, 0, math.radians(shot.get("door", DOOR)))
    parts = [box("door", (0.35, -0.55, 0), (0.35 + UW, 0, UH), white, bevel=0.5, seg=6)]
    for lo, hi in (((0.6, 0, 0.25), (UW + 0.1, 0.55, 0.5)), ((0.6, 0, UH - 0.5), (UW + 0.1, 0.55, UH - 0.25)),
                   ((0.6, 0, 0.25), (0.85, 0.55, UH - 0.25)), ((UW - 0.15, 0, 0.25), (UW + 0.1, 0.55, UH - 0.25))):
        parts.append(box("rim", lo, hi, white, bevel=0.08, seg=3))
    parts.append(box("latch", (UW + 0.2, -0.3, UH / 2 - 1.1), (UW + 0.75, 0.25, UH / 2 + 1.1), white, bevel=0.12, seg=3))
    ch = printed("chart", f".chart-{shot['chart']}.png")
    x0, x1, z0, z1 = 1.85, 13.85, 0.9, 17.25
    parts.append(sheet("chart", [(x1, 0.012, z0), (x0, 0.012, z0), (x0, 0.012, z1), (x1, 0.012, z1)], ch, thick=0.012))
    for z in (3.6, UH - 3.6):
        parts.append(box("doorleaf", (-0.05, -0.5, z - 1.0), (0.7, -0.05, z + 1.0), white, bevel=0.05, seg=2))
    for ob in parts:
        ob.parent = piv
        ob.hide_render = bool(shot.get("nodoor"))
    for z in (() if shot.get("nodoor") else (3.6, UH - 3.6)):
        cyl("knuckle", hinge + Vector((0, 0, z - 1.3)), hinge + Vector((0, 0, z + 1.3)), 0.36, white, bevel=0.06)
        box("leaf", (-UW / 2 - 0.3, FY + 0.1, z - 1.0), (-UW / 2 + 0.1, FY + 1.4, z + 1.0), white, bevel=0.05, seg=2)


def build(frame, quality, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 160 if final else 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.render.threads_mode = "FIXED"; sc.render.threads = 4
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1.0, 0.95, 0.98, 1); bg.inputs["Strength"].default_value = 0.10

    scene(frame)
    shot = SHOTS[frame]
    T = (0, -6, 10)
    # key: a small window high on the left and in front, so levers, door and box all throw shadows down to the right
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 26; key.size_y = 36
    key.energy = 1.25e6; key.color = (1.0, 0.96, 0.90)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (-150, -185, 180); aim(ko, T)
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 320; fl.energy = 1.7e5; fl.color = (0.95, 0.94, 1.0)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (260, -380, 40); aim(fo, T)
    # panes of a window off to the right for the plastic to mirror
    em = bpy.data.materials.new("glass"); em.use_nodes = True
    e = em.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.95, 0.96, 1.0, 1); e.inputs["Strength"].default_value = 2.2
    em.node_tree.links.new(e.outputs["Emission"], em.node_tree.nodes["Material Output"].inputs["Surface"])
    for i in range(2):
        for j in range(3):
            me = bpy.data.meshes.new("pane")
            y0, z0 = -430 + i * 120, -40 + j * 100
            me.from_pydata([(420, y0, z0), (420, y0 + 108, z0), (420, y0 + 108, z0 + 90), (420, y0, z0 + 90)], [], [(0, 1, 2, 3)])
            po = link(bpy.data.objects.new("pane", me)); po.data.materials.append(em); po.visible_camera = False; po.visible_diffuse = False

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]; cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).dot((Vector(shot["aim"]) - co.location).normalized())
    cam.dof.aperture_fstop = shot["f"]
    if quality == "probe":
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update()
        hx, hy = -UW / 2 - 0.35, FY - 0.1
        c, s = math.cos(math.radians(shot.get("door", DOOR))), math.sin(math.radians(shot.get("door", DOOR)))
        dp = lambda lx, lz: (hx + lx * c, hy + lx * s, lz)
        P = {"box TL": (-UW / 2, FY, UH), "box TR": (UW / 2, FY, UH), "box BL": (-UW / 2, FY, 0), "box BR": (UW / 2, FY, 0),
             "door far T": dp(0.35 + UW, UH), "door far B": dp(0.35 + UW, 0), "chart TL": dp(13.85, 17.25), "chart TR": dp(1.85, 17.25),
             "chart BL": dp(13.85, 1.75), "chart BR": dp(1.85, 1.75), "row L": (-4.8, FY - 0.8, ZR), "row R": (4.8, FY - 0.8, ZR),
             "lab BL": (-4.8, FY, 3.0), "lab TR": (4.8, FY, 8.2), "stk TL": (-4.8, FY, 17.75), "stk BR": (4.8, FY, 14.75)}
        for nm, pt in P.items():
            v = world_to_camera_view(sc, co, Vector(pt))
            print(f"  f{frame} {nm:10s} x {v.x * W:7.0f}  y {(1 - v.y) * H:7.0f}")
        return None
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region
    exr = str(TMP / f"nx-box-{frame}.exr")
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
    x = np.where(x > 0.60, 0.60 + (1 - np.exp(-(x - 0.60) / 0.40)) * 0.36, x)     # a soft shoulder: white plastic stays off pure white
    x = np.clip(x, 0, 1)
    lum = (x * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    x = np.clip(lum + (x - lum) * 1.12, 0, 1)
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
        exr = str(TMP / f"nx-box-{fr}.exr")
        if quality == "probe":
            build(fr, quality); continue
        grade(exr if regrade else build(fr, quality), fr, quality)
