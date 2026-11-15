"""Renders the pictures for this post with Blender's Python module (pip install bpy brotli).

One black 3.5-inch floppy disk on a bone-white table, the only copy of a website, shot from the same side three ways:
  1  the whole disk, close and low, running off the right: the label says Website, the DATE line is empty
  2  right up against the label: the empty DATE line in focus, the shutter falling out of focus
  3  the disk again, later: DATE filled in, a red tick beside it

  python3 build.py <frame 1|2|3|all> [draft|final] [regrade]
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

# the disk, seen from its label side with the shutter at the top: 9.0 x 9.4 x 0.33 cm
DW, DH, DT = 9.0, 9.4, 0.33
TABLE = (0.80, 0.755, 0.665)       # bone, linear RGB

SHOTS = {
    1: dict(loc=(-1.4, -12.2, 8.8), aim=(-0.6, -0.9, 0.0), lens=33.5, f=3.2, focus=(-0.5, -1.6, 0.33), shift=(0.02, 0.15), rot=-8),
    2: dict(loc=(-2.6, -7.9, 4.6), aim=(-2.9, -3.5, 0.0), lens=48, f=2.4, focus=(-2.75, -1.85, 0.33), shift=(0.0, -0.17), rot=2),
    3: dict(loc=(1.5, -7.5, 14.0), aim=(0.2, -0.6, 0.0), lens=42, f=4.0, focus=(0.4, -1.6, 0.33), shift=(0.0, -0.25), rot=7),
}


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def outline(chamfer=True):
    """The disk's outline: a rounded rectangle with the top right corner cut off."""
    r, c = 0.28, 0.55
    x0, x1, y0, y1 = -DW / 2, DW / 2, -DH / 2, DH / 2
    pts = []

    def arc(cx, cy, a0, a1, n=8):
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    arc(x0 + r, y0 + r, 180, 270)
    arc(x1 - r, y0 + r, 270, 360)
    if chamfer:
        pts += [(x1, y1 - c), (x1 - c, y1)]
    else:
        arc(x1 - r, y1 - r, 0, 90)
    arc(x0 + r, y1 - r, 90, 180)
    return pts


def slab(name, pts, z0, z1, bevel=0.0, holes=()):
    """Extrude a 2D outline (with optional rectangular holes) between two heights, bevel the edges."""
    bm = bmesh.new()
    def ring(p, z):
        return [bm.verts.new((x, y, z)) for x, y in p]
    loops = [pts] + [list(h) for h in holes]
    bot, top = [], []
    for lp in loops:
        bot.append(ring(lp, z0)); top.append(ring(lp, z1))
    for b, t in zip(bot, top):
        n = len(b)
        for i in range(n):
            bm.faces.new((b[i], b[(i + 1) % n], t[(i + 1) % n], t[i]))
    me = bpy.data.meshes.new(name)
    if holes:
        # faces with holes: let Blender fill them from the edge loops
        edges_top = [e for lp in top for e in [bm.edges.get((lp[i], lp[(i + 1) % len(lp)])) for i in range(len(lp))]]
        edges_bot = [e for lp in bot for e in [bm.edges.get((lp[i], lp[(i + 1) % len(lp)])) for i in range(len(lp))]]
        bmesh.ops.triangle_fill(bm, edges=edges_top, use_beauty=True)
        bmesh.ops.triangle_fill(bm, edges=edges_bot, use_beauty=True)
        bmesh.ops.dissolve_limit(bm, angle_limit=0.01, verts=bm.verts, edges=bm.edges)
    else:
        bm.faces.new(top[0]); bm.faces.new(list(reversed(bot[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    if bevel:
        md = ob.modifiers.new("bevel", "BEVEL"); md.width = bevel; md.segments = 4; md.limit_method = "ANGLE"
        md.angle_limit = math.radians(40); md.harden_normals = False
    md = ob.modifiers.new("wn", "WEIGHTED_NORMAL"); md.keep_sharp = True
    for p in me.polygons:
        p.use_smooth = True
    return ob


def rect(x0, y0, x1, y1, r=0.0, n=4):
    if not r:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = []
    for cx, cy, a0 in ((x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def plastic():
    m, nt, p = mat("abs")
    N, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (0.012, 0.012, 0.014, 1)
    p.inputs["Roughness"].default_value = 0.42
    p.inputs["Specular IOR Level"].default_value = 0.38
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 260; nz.inputs["Detail"].default_value = 2
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.10; bump.inputs["Distance"].default_value = 0.02
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    # a little unevenness in the shine, like a moulded part that has been handled
    nz2 = N.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 0.9; nz2.inputs["Detail"].default_value = 3
    L.new(geo.outputs["Position"], nz2.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.26; mr.inputs["To Max"].default_value = 0.40
    L.new(nz2.outputs["Fac"], mr.inputs["Value"]); L.new(mr.outputs["Result"], p.inputs["Roughness"])
    return m


def metal():
    m, nt, p = mat("shutter")
    N, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (0.62, 0.63, 0.65, 1)
    p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = 0.24
    p.inputs["Anisotropic"].default_value = 0.6
    geo = N.new("ShaderNodeNewGeometry")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (40, 0.6, 1)   # brushed across
    L.new(geo.outputs["Position"], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 30; nz.inputs["Detail"].default_value = 8
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.18; mr.inputs["To Max"].default_value = 0.30
    L.new(nz.outputs["Fac"], mr.inputs["Value"]); L.new(mr.outputs["Result"], p.inputs["Roughness"])
    return m


def paper(img):
    m, nt, p = mat("label")
    N, L = nt.nodes, nt.links
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(img)); tex.interpolation = "Cubic"
    L.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.78
    p.inputs["Specular IOR Level"].default_value = 0.3
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 140; nz.inputs["Detail"].default_value = 6
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def table_mat():
    m, nt, p = mat("table")
    N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.86
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 3
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.94; mr.inputs["To Max"].default_value = 1.03
    L.new(nz.outputs["Fac"], mr.inputs["Value"])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1
    mix.inputs["A"].default_value = (*TABLE, 1)
    comb = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(mr.outputs["Result"], comb.inputs[k])
    L.new(comb.outputs["Color"], mix.inputs["B"]); L.new(mix.outputs["Result"], p.inputs["Base Color"])
    fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 90; fine.inputs["Detail"].default_value = 6
    L.new(geo.outputs["Position"], fine.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.02
    L.new(fine.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def dark(name, c=(0.006, 0.005, 0.005), rough=0.5):
    m, nt, p = mat(name)
    p.inputs["Base Color"].default_value = (*c, 1); p.inputs["Roughness"].default_value = rough
    return m


def aim(ob, target, up=(0, 0, 1)):
    f = (Vector(target) - ob.location).normalized()
    r = f.cross(Vector(up)).normalized()
    u = r.cross(f)
    ob.rotation_euler = Matrix((r, u, -f)).transposed().to_euler()


def disk(state):
    """Build the disk around the origin, lying label side up. Returns the parent empty."""
    root = bpy.data.objects.new("disk", None); bpy.context.scene.collection.objects.link(root)
    parts = []
    # body, with the write-protect window (bottom left) and the density hole (bottom right) cut through
    hole_l = rect(-DW / 2 + 0.35, -DH / 2 + 0.35, -DW / 2 + 0.75, -DH / 2 + 0.80, 0.04, 2)
    hole_r = rect(DW / 2 - 0.75, -DH / 2 + 0.35, DW / 2 - 0.35, -DH / 2 + 0.80, 0.04, 2)
    body = slab("body", outline(), 0, DT, bevel=0.035, holes=(hole_l, hole_r)); body.data.materials.append(plastic()); parts.append(body)
    # the slider inside the write-protect window, flush with the back
    sl = slab("slider", rect(-DW / 2 + 0.36, -DH / 2 + 0.36, -DW / 2 + 0.74, -DH / 2 + 0.58), 0.0, 0.14)
    sl.data.materials.append(dark("slider", (0.02, 0.02, 0.022), 0.6)); parts.append(sl)
    # shutter recess: a shallow channel across the top where the shutter slides
    sx0, sx1, sy0 = -2.55, 2.45, DH / 2 - 3.0
    recess = slab("recess", rect(-3.6, sy0 - 0.12, 3.25, DH / 2 + 0.02), DT - 0.035, DT + 0.002)
    recess.display_type = "WIRE"; recess.hide_render = True
    bo = body.modifiers.new("recess", "BOOLEAN"); bo.object = recess; bo.operation = "DIFFERENCE"; bo.solver = "EXACT"
    body.modifiers.move(len(body.modifiers) - 1, 0)
    # the shutter: brushed metal with a window onto the brown disk inside
    win = rect(-0.55 - 0.35, DH / 2 - 2.55, 0.55 - 0.35, DH / 2 - 0.32, 0.06, 3)
    sh = slab("shutter", rect(sx0, sy0, sx1, DH / 2 + 0.005, 0.03, 2), DT - 0.03, DT - 0.008, bevel=0.006, holes=(win,))
    sh.data.materials.append(metal()); parts.append(sh)
    cut = slab("wincut", [(x, y) for x, y in win], 0.12, DT + 0.05)
    cut.hide_render = True; cut.display_type = "WIRE"; parts.append(cut)
    bo = body.modifiers.new("win", "BOOLEAN"); bo.object = cut; bo.operation = "DIFFERENCE"; bo.solver = "EXACT"
    body.modifiers.move(len(body.modifiers) - 1, 0)
    media = slab("media", rect(-1.2, DH / 2 - 2.9, 0.6, DH / 2 - 0.1), 0.10, 0.135)
    media.data.materials.append(dark("media", (0.10, 0.05, 0.022), 0.22)); parts.append(media)
    # the label recess and the label in it
    lx0, ly0, lx1, ly1 = -3.5, -DH / 2 + 0.45, 3.5, -DH / 2 + 0.45 + 5.4
    lrec = slab("lrec", rect(lx0 - 0.08, ly0 - 0.08, lx1 + 0.08, ly1 + 0.08, 0.1), DT - 0.022, DT + 0.01)
    lrec.hide_render = True; lrec.display_type = "WIRE"
    bo = body.modifiers.new("lrec", "BOOLEAN"); bo.object = lrec; bo.operation = "DIFFERENCE"; bo.solver = "EXACT"
    body.modifiers.move(len(body.modifiers) - 1, 1)
    me = bpy.data.meshes.new("label")
    zl = DT - 0.012
    me.from_pydata([(lx0, ly0, zl), (lx1, ly0, zl), (lx1, ly1, zl), (lx0, ly1, zl)], [], [(0, 1, 2, 3)])
    me.uv_layers.new(name="uv")
    for li, uv in zip(me.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        me.uv_layers[0].data[li.index].uv = uv
    lab = bpy.data.objects.new("label", me); bpy.context.scene.collection.objects.link(lab)
    md = lab.modifiers.new("sub", "SUBSURF"); md.subdivision_type = "SIMPLE"; md.levels = md.render_levels = 3
    lab.data.materials.append(paper(HERE / f"label-{state}.png")); parts.append(lab)
    # the embossed arrow, top left, that points into the drive
    me = bpy.data.meshes.new("arrow")
    ax, ay = -DW / 2 + 0.55, DH / 2 - 0.9
    me.from_pydata([(ax - 0.17, ay - 0.12, DT + 0.004), (ax + 0.17, ay - 0.12, DT + 0.004), (ax, ay + 0.16, DT + 0.004)], [], [(0, 1, 2)])
    ar = bpy.data.objects.new("arrow", me); bpy.context.scene.collection.objects.link(ar)
    ar.modifiers.new("s", "SOLIDIFY").thickness = 0.012
    ar.data.materials.append(dark("arrow", (0.02, 0.02, 0.022), 0.3)); parts.append(ar)
    for o in parts + [recess, lrec]:
        o.parent = root
    return root


def build(frame, quality):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 192 if final else 32
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
    bg.inputs["Color"].default_value = (0.95, 0.93, 0.90, 1); bg.inputs["Strength"].default_value = 0.10

    shot = SHOTS[frame]
    root = disk("done" if frame == 3 else "blank")
    root.rotation_euler.z = math.radians(shot["rot"])

    me = bpy.data.meshes.new("table"); s = 200
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    tb = bpy.data.objects.new("table", me); sc.collection.objects.link(tb); tb.location.z = -0.0005
    tb.data.materials.append(table_mat())

    # key: one soft window high behind and to the left, so the disk throws its shadow toward us and to the right
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 14; key.size_y = 26
    key.energy = 20000; key.color = (1.0, 0.975, 0.94)
    ko = bpy.data.objects.new("key", key); sc.collection.objects.link(ko)
    ko.location = (-34, 30, 40); aim(ko, (0, 0, 0))
    # a long strip above and behind for the shutter's reflection, seen only by the disk
    st = bpy.data.lights.new("strip", "AREA"); st.shape = "RECTANGLE"; st.size = 40; st.size_y = 4
    st.energy = 900; st.color = (0.96, 0.97, 1.0)
    so = bpy.data.objects.new("strip", st); sc.collection.objects.link(so)
    so.location = (0, 26, 22); aim(so, (0, 0, 0))
    only = bpy.data.collections.new("disk-only"); sc.collection.children.link(only)
    for o in root.children:
        only.objects.link(o)
    so.light_linking.receiver_collection = only
    # fill from the camera side, low
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 30; fl.energy = 2000; fl.color = (0.98, 0.97, 1.0)
    fo = bpy.data.objects.new("fill", fl); sc.collection.objects.link(fo)
    fo.location = (14, -40, 18); aim(fo, (0, 0, 0))

    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]
    cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 0.1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"]

    exr = str(TMP / f"nx-floppy-{frame}.exr")
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
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.10 * np.clip(r - 0.6, 0, 1) ** 1.5)[..., None]
    rng = np.random.default_rng(3 + frame)
    x += rng.normal(0, 0.009, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"render-{frame:02d}.jpg" if quality == "final" else f".draft-{frame:02d}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst)


EXPOSURE = 1.12

if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 else "draft"
    regrade = "regrade" in args
    for fr in ([1, 2, 3] if which == "all" else [int(which)]):
        exr = str(TMP / f"nx-floppy-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
