"""Renders the pictures for this Story with Blender's Python module (pip install bpy; run with python3.13).

One rotary card file on a teal sweep: ivory customer cards, buff A to Z index tabs, a satin black frame.
Shot from the same side three ways, the wheel turning between frames 2 and 3:
  1  the whole file, open at one typed customer card (DUNN, Mrs P.)
  2  right up against that card: a name, a number and a pencil note that says "ask Dave"
  3  the wheel turned on to N: one pink Nexulabs card
Prints: art/print.py.   python3.13 build.py <1|2|3|all> [draft|final|probe] [regrade]
writes art/render-0N.jpg (1080x1920). Units are centimetres. The type is set over it in slide-0N.html.
"""
import sys, math, random, string, tempfile
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())
TEAL = (0.0030, 0.038, 0.050)
EXPOSURE = 1.0
CW, CH, TABH, TABW = 10.2, 5.7, 0.9, 1.9
R0, AZ = 1.9, 10.4               # inner radius of the cards, height of the axle
OPEN, FRONT = 13.0, -70.0        # lean of the open card (back from upright), and of the front group
N = 236

SHOTS = {
    1: dict(loc=(-19, -44, 29), aim=(0.5, 0, 10.5), lens=46, f=0.30, focus=(0, 1.2, 15), shift=(-0.02, 0.16), letter="D", hide="F"),
    2: dict(loc=(-10.5, -25, 22.5), aim=(0.2, 1, 15.6), lens=47, f=0.10, focus=(-1, 1.2, 15.5), shift=(-0.10, 0.04), letter="D", hide="F"),
    3: dict(loc=(-17, -37, 37), aim=(0.3, 0.5, 14.0), lens=54, f=0.22, focus=(0, 1.2, 15), shift=(-0.07, 0.145), letter="N", hide="Q"),
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


def plain(name, col, rough, metal=0.0, coat=0.0):
    m, nt, p = mat(name)
    p.inputs["Base Color"].default_value = (*col, 1); p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal; p.inputs["Coat Weight"].default_value = coat
    return m


def paper_nodes(nt, p, rough=0.62):
    """Paper: a fine fibre bump and a little sheen."""
    N_, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = rough; p.inputs["Specular IOR Level"].default_value = 0.25
    p.inputs["Sheen Weight"].default_value = 0.15
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 55; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.7
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.12; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])


def paper_plain(name, a, b):
    """Plain stock, each card a slightly different white."""
    m, nt, p = mat(name)
    N_, L = nt.nodes, nt.links
    info = N_.new("ShaderNodeObjectInfo")
    mix = N_.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*a, 1); mix.inputs["B"].default_value = (*b, 1)
    L.new(info.outputs["Random"], mix.inputs["Factor"]); L.new(mix.outputs["Result"], p.inputs["Base Color"])
    paper_nodes(nt, p)
    return m


def paper_print(name, png):
    m, nt, p = mat(name)
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / png)); tex.interpolation = "Cubic"; tex.extension = "EXTEND"
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    paper_nodes(nt, p)
    return m


def arc(cx, cz, r, a0, a1, n=7):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def card_mesh(name, tab=None, thick=0.03):
    """A card in the plane y = 0, x across, z up from R0. Printed face towards -y. tab = 0..4 adds an index tab."""
    x0, x1, z0, z1, r = -CW / 2, CW / 2, R0, R0 + CH, 0.42
    pts = [(x0, z0), (x1, z0)]
    pts += arc(x1 - r, z1 - r, r, 0, 90)
    if tab is not None:
        tx0 = x0 + 0.35 + tab * TABW; tx1 = tx0 + TABW; q = 0.22
        pts += [(tx1 + 0.12, z1)] + arc(tx1 - q, z1 + TABH - q, q, 0, 90, 4) + arc(tx0 + q, z1 + TABH - q, q, 90, 180, 4) + [(tx0 - 0.12, z1)]
    pts += arc(x0 + r, z1 - r, r, 90, 180)
    top = z1 + (TABH if tab is not None else 0)
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x, 0, z) for x, z in pts], [], [list(range(len(pts)))])
    uv = me.uv_layers.new(name="uv")
    for lp in me.loops:
        v = me.vertices[lp.vertex_index].co
        uv.data[lp.index].uv = ((v.x - x0) / CW, (v.z - z0) / (top - z0))
    return me


def hull(name, pts, material, bevel=0.0, seg=4):
    bm = bmesh.new()
    for p in pts:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(material)
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = seg; b.limit_method = "ANGLE"; b.angle_limit = math.radians(40)
        w = ob.modifiers.new("w", "WEIGHTED_NORMAL"); w.keep_sharp = True
    for p in me.polygons:
        p.use_smooth = True
    return ob


def xcyl(name, x0, x1, rad, material, flutes=0, bevel=0.1, n=96):
    """A cylinder along x. flutes > 0 cuts shallow grooves round it (a knob you can grip)."""
    bm = bmesh.new()
    ring0, ring1 = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = rad - (0.11 * max(0.0, math.cos(a * flutes)) ** 3 if flutes else 0)
        ring0.append(bm.verts.new((x0, r * math.cos(a), AZ + r * math.sin(a)))); ring1.append(bm.verts.new((x1, r * math.cos(a), AZ + r * math.sin(a))))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))
    bm.faces.new(ring0[::-1]); bm.faces.new(ring1)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(material)
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 4; b.limit_method = "ANGLE"; b.angle_limit = math.radians(60)
    for p in me.polygons:
        p.use_smooth = len(p.vertices) == 4
    return ob


def black_plastic():
    m, nt, p = mat("frame")
    N_, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (0.012, 0.013, 0.015, 1); p.inputs["Roughness"].default_value = 0.34
    p.inputs["Coat Weight"].default_value = 0.25; p.inputs["Coat Roughness"].default_value = 0.12
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 90; nz.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.10; bump.inputs["Distance"].default_value = 0.008
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def sequence(letter):
    """What sits on the wheel, starting with the open card and going back round to the front group."""
    L = string.ascii_uppercase; i = L.index(letter)
    seq = [("open", letter)] + [("card", letter)] * 5
    for k in range(1, 26):
        l = L[(i + k) % 26]
        seq += [("tab", l)] + [("card", l)] * 8
    seq += [("tab", letter)] + [("card", letter)] * 2
    return seq


def scene(frame):
    shot = SHOTS[frame]
    # the sweep
    prof = [(-900, 0), (150, 0)] + [(150 + 70 * math.sin(math.radians(a)), 70 - 70 * math.cos(math.radians(a))) for a in range(5, 91, 5)] + [(220, 1500)]
    vs = [(sx * 2500, y, z) for y, z in prof for sx in (-1, 1)]
    fs = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(vs, [], fs)
    for p in me.polygons:
        p.use_smooth = True
    sw = link(bpy.data.objects.new("sweep", me))
    m, nt, p = mat("sweep"); p.inputs["Base Color"].default_value = (*TEAL, 1); p.inputs["Roughness"].default_value = 0.78; p.inputs["Specular IOR Level"].default_value = 0.2
    sw.data.materials.append(m)

    ivory = paper_plain("ivory", (0.86, 0.82, 0.70), (0.80, 0.75, 0.62))
    buffb = paper_plain("buff", (0.66, 0.54, 0.28), (0.62, 0.50, 0.26))
    plain_card = card_mesh("card"); plain_card.materials.append(ivory); plain_card.materials.append(ivory)
    rng = random.Random(7)
    seq = sequence(shot["letter"])
    step = (360 + FRONT - OPEN) / (len(seq) - 1)
    tabmesh = {}
    for i, (kind, l) in enumerate(seq):
        phi = OPEN + i * step + (rng.uniform(-0.4, 0.4) * step if 0 < i < len(seq) - 1 else 0)
        if kind == "open":
            me = card_mesh("open")
            me.materials.append(paper_print("print", ".card-nx.png" if frame == 3 else ".card-dunn.png"))
            me.materials.append(plain("pinkback", (0.72, 0.02, 0.19), 0.6) if frame == 3 else ivory)
        elif kind == "tab":
            k = string.ascii_uppercase.index(l) % 5
            if l not in tabmesh:
                me = card_mesh("tab" + l, tab=k); me.materials.append(paper_print("tab" + l, ".tab-blank.png" if l in shot["hide"] else f".tab-{l}.png")); me.materials.append(buffb)
                tabmesh[l] = me
            me = tabmesh[l]
        else:
            me = plain_card
        ob = link(bpy.data.objects.new(kind, me))
        ob.location = (rng.uniform(-0.035, 0.035) if kind != "open" else 0, 0, AZ)
        ob.scale = (1, 1, 1 + (rng.uniform(-0.006, 0.006) if kind == "card" else 0))
        ob.rotation_euler = (-math.radians(phi), 0, 0)
        s = ob.modifiers.new("s", "SOLIDIFY"); s.thickness = 0.05 if kind == "tab" else 0.03; s.offset = -1
        s.material_offset = 1; s.material_offset_rim = 1

    blk = black_plastic()
    for sx in (-1, 1):
        xa, xb = sx * (CW / 2 + 0.35), sx * (CW / 2 + 0.95)
        pts = []
        for x in (xa, xb):
            pts += [(x, 2.7 * math.cos(math.radians(a)), AZ + 2.7 * math.sin(math.radians(a))) for a in range(0, 360, 6)]
            pts += [(x, -6.2, 0), (x, 6.2, 0), (x, -6.2, 0.9), (x, 6.2, 0.9)]
        hull("side", pts, blk, bevel=0.18)
        xcyl("hub", sx * (CW / 2 + 0.9), sx * (CW / 2 + 1.35), 1.5, blk, bevel=0.12)
        xcyl("knob", sx * (CW / 2 + 1.3), sx * (CW / 2 + 2.9), 2.5, blk, flutes=18, bevel=0.22)
    xcyl("core", -CW / 2 - 0.4, CW / 2 + 0.4, R0 - 0.15, blk, bevel=0)
    pts = [(x, y, z) for x in (-CW / 2 - 0.5, CW / 2 + 0.5) for y in (-5.85, 5.85) for z in (0, 0.78)]
    hull("base", pts, blk, bevel=0.18)


def build(frame, quality, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 144 if final else 24
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
    bg.inputs["Color"].default_value = (0.9, 0.97, 1.0, 1); bg.inputs["Strength"].default_value = 0.10

    scene(frame)
    shot = SHOTS[frame]

    # key: a small window high on the left and a little in front, so every card throws a shadow on the next
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 46; key.size_y = 60
    key.energy = 2.6e6; key.color = (1.0, 0.96, 0.90)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (-250, -190, 300); aim(ko, (0, 0, 12))
    # rim from behind on the right: a bright edge along the card tops and the knob
    rim = bpy.data.lights.new("rim", "AREA"); rim.shape = "RECTANGLE"; rim.size = 30; rim.size_y = 120
    rim.energy = 9.0e5; rim.color = (0.90, 0.97, 1.0)
    ro = link(bpy.data.objects.new("rim", rim)); ro.location = (260, 130, 210); aim(ro, (0, 0, 12))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 300; fl.energy = 2.2e5; fl.color = (0.92, 0.98, 1.0)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (140, -420, 120); aim(fo, (0, 0, 12))
    # something for the black plastic to mirror: a tall window off to the left, out of shot
    em = bpy.data.materials.new("glass"); em.use_nodes = True
    e = em.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (0.92, 0.96, 1.0, 1); e.inputs["Strength"].default_value = 3.0
    em.node_tree.links.new(e.outputs["Emission"], em.node_tree.nodes["Material Output"].inputs["Surface"])
    for i in range(2):
        for j in range(3):
            me = bpy.data.meshes.new("pane")
            y0, z0 = -420 + i * 110, 60 + j * 95
            me.from_pydata([(-420, y0, z0), (-420, y0 + 100, z0), (-420, y0 + 100, z0 + 86), (-420, y0, z0 + 86)], [], [(0, 1, 2, 3)])
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
        s, c = math.sin(math.radians(OPEN)), math.cos(math.radians(OPEN))
        P = {"card TL": (-CW / 2, (R0 + CH) * s, AZ + (R0 + CH) * c), "card TR": (CW / 2, (R0 + CH) * s, AZ + (R0 + CH) * c),
             "card BL": (-CW / 2, R0 * s, AZ + R0 * c), "card BR": (CW / 2, R0 * s, AZ + R0 * c),
             "knob L": (-CW / 2 - 2.9, 0, AZ), "knob R": (CW / 2 + 2.9, 0, AZ), "base FL": (-CW / 2 - 0.95, -6.2, 0), "base FR": (CW / 2 + 0.95, -6.2, 0)}
        for nm, pt in P.items():
            v = world_to_camera_view(sc, co, Vector(pt))
            print(f"  f{frame} {nm:10s} x {v.x * W:7.0f}  y {(1 - v.y) * H:7.0f}")
        return None
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region
    exr = str(TMP / f"nx-cards-{frame}.exr")
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
    x = np.where(x > 0.60, 0.60 + (1 - np.exp(-(x - 0.60) / 0.40)) * 0.36, x)     # a soft shoulder: paper stays off pure white
    x = np.clip(x, 0, 1)
    lum = (x * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    x = np.clip(lum + (x - lum) * 1.16, 0, 1)
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
        exr = str(TMP / f"nx-cards-{fr}.exr")
        if quality == "probe":
            build(fr, quality); continue
        grade(exr if regrade else build(fr, quality), fr, quality)
