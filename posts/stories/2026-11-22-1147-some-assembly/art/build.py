"""Renders the pictures for this Story with Blender's Python module (pip install bpy; run with python3.13).

A website as a model kit: one sprue of ivory plastic on a violet sweep, the parts of a web page still on their
runners (address bar, three menu items, a picture frame, lines of text, a Book now button, a pointer, a form field)
and the Nexulabs wordmark moulded into the maker's tab. Shot from the same side three ways, the kit changing:
  1  the whole sprue, every part attached
  2  close on the Book now button, cut free and lying across its bay
  3  the page put together, lying on its own empty sprue
python3.13 build.py <1|2|3|all> [draft|final|probe] [regrade]   writes art/render-0N.jpg (1080x1920). Units: cm.
The type is set over the picture in slide-0N.html. Nothing here is a real product: the kit is made up.
"""
import sys, math, tempfile, re
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())
VIOLET = (0.075, 0.018, 0.33)
IVORY = (0.86, 0.80, 0.665)
EXPOSURE = 1.0
SW, SH = 16.6, 24.8            # sprue outline
RR = 0.16                      # runner radius
ZM = 0.16                      # mid-plane of the sprue
TH = 0.22                      # part thickness
YAW = {1: -14.0, 2: -14.0, 3: -14.0}

# loc, aim and focus are in the sprue's own frame (x across, y up the sprue), turned by YAW into the world
SHOTS = {
    1: dict(loc=(-6, -60, 74), aim=(0.3, 1.6, 0), lens=65, f=0.9, focus=(0, -3, 0), shift=(0.043, 0.109)),
    2: dict(loc=(-3, -22, 38), aim=(0.2, 9.6, 0.2), lens=63, f=0.16, focus=(0.4, 12.6, 0.3), shift=(0.0, 0.025)),
    3: dict(loc=(-3, -33, 60), aim=(0.6, 3.6, 0.4), lens=62, f=0.6, focus=(0, 1, 0.5), shift=(-0.029, 0.187)),
}


def link(ob):
    bpy.context.scene.collection.objects.link(ob); return ob


def aim(ob, target, up=(0, 0, 1)):
    f = (Vector(target) - ob.location).normalized()
    r = f.cross(Vector(up)).normalized()
    u = r.cross(f)
    ob.rotation_euler = Matrix((r, u, -f)).transposed().to_euler()


def ttf(name):
    out = TMP / (name + ".ttf")
    if not out.exists():
        from fontTools.ttLib import TTFont
        f = TTFont(str(ROOT / "fonts" / (name + ".woff2"))); f.flavor = None; f.save(str(out))
    return bpy.data.fonts.load(str(out))


def plastic():
    m = bpy.data.materials.new("plastic"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*IVORY, 1)
    p.inputs["Roughness"].default_value = 0.27
    p.inputs["Subsurface Weight"].default_value = 0.12
    p.inputs["Subsurface Radius"].default_value = (0.25, 0.2, 0.12)
    p.inputs["Subsurface Scale"].default_value = 0.3
    p.inputs["Coat Weight"].default_value = 0.12; p.inputs["Coat Roughness"].default_value = 0.2
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 140; nz.inputs["Detail"].default_value = 3
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.035; bump.inputs["Distance"].default_value = 0.004
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def rrect(w, h, r, n=10):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        pts += [(cx + r * math.cos(math.radians(a0 + 90 * i / n)), cy + r * math.sin(math.radians(a0 + 90 * i / n))) for i in range(n + 1)]
    return pts


class Kit:
    def __init__(self):
        self.mat = plastic()
        self.font = ttf("Geist-Bold")
        self.parts = {}

    def empty(self, name, parent=None):
        e = link(bpy.data.objects.new(name, None))
        if parent: e.parent = parent
        return e

    def shape(self, name, loops, parent, thick=TH, bevel=0.035, z=0.0):
        """Flat plate from closed outlines (the first is the outside, the rest are holes), centred on z."""
        cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "2D"; cu.fill_mode = "BOTH"
        for pts in loops:
            s = cu.splines.new("POLY"); s.points.add(len(pts) - 1); s.use_cyclic_u = True
            for p, (x, y) in zip(s.points, pts):
                p.co = (x, y, 0, 1)
        cu.extrude = thick / 2 - bevel; cu.bevel_depth = bevel; cu.bevel_resolution = 3
        ob = link(bpy.data.objects.new(name, cu)); ob.data.materials.append(self.mat); ob.parent = parent; ob.location.z = z
        return ob

    def text(self, name, body, size, parent, x=0, y=0, z=TH / 2, raise_=0.07, track=1.05):
        cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.font = self.font; cu.size = size
        cu.align_x = "CENTER"; cu.align_y = "CENTER"; cu.space_character = track
        cu.extrude = raise_; cu.bevel_depth = 0.012; cu.bevel_resolution = 2; cu.resolution_u = 8
        ob = link(bpy.data.objects.new(name, cu)); ob.data.materials.append(self.mat); ob.parent = parent
        ob.location = (x, y, z - 0.02)
        return ob

    def tube(self, name, paths, parent, rad=RR, cyclic=False):
        cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"
        for pts in paths:
            s = cu.splines.new("POLY"); s.points.add(len(pts) - 1); s.use_cyclic_u = cyclic
            for p, c in zip(s.points, pts):
                p.co = (c[0], c[1], c[2] if len(c) > 2 else 0, 1)
        cu.bevel_depth = rad; cu.bevel_resolution = 6; cu.use_fill_caps = True
        ob = link(bpy.data.objects.new(name, cu)); ob.data.materials.append(self.mat); ob.parent = parent
        return ob

    def cone(self, name, a, b, ra, rb, parent):
        a, b = Vector(a), Vector(b)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=ra, radius2=rb, depth=(b - a).length)
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = len(p.vertices) == 4
        ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(self.mat); ob.parent = parent
        ob.location = (a + b) / 2
        ob.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
        return ob

    def disc(self, name, x, y, r, h, parent, z=0.0):
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=40, radius1=r, radius2=r, depth=h)
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = len(p.vertices) == 4
        ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(self.mat); ob.parent = parent; ob.location = (x, y, z)
        b = ob.modifiers.new("b", "BEVEL"); b.width = 0.02; b.segments = 2; b.limit_method = "ANGLE"
        return ob

    def wordmark(self, parent, width, z):
        svg = (ROOT / "brand" / "nexulabs-logo-white.svg").read_text()
        d = re.search(r'<path[^>]*\sd="([^"]+)"', svg)
        paths = re.findall(r'<path[^>]*\sd="([^"]+)"', svg)
        loops = []
        for d in paths:
            tok = re.findall(r"[MLQCZHVmlqczhv]|-?\d*\.?\d+(?:e-?\d+)?", d)
            i, cur, start, loop, cmd = 0, (0, 0), None, [], None
            def num():
                nonlocal i
                v = float(tok[i]); i += 1; return v
            while i < len(tok):
                if tok[i].isalpha():
                    cmd = tok[i]; i += 1
                if cmd == "M":
                    if loop: loops.append(loop)
                    cur = (num(), num()); loop = [cur]; cmd = "L"
                elif cmd == "L":
                    cur = (num(), num()); loop.append(cur)
                elif cmd == "H":
                    cur = (num(), cur[1]); loop.append(cur)
                elif cmd == "V":
                    cur = (cur[0], num()); loop.append(cur)
                elif cmd == "Q":
                    c = (num(), num()); e = (num(), num())
                    for k in range(1, 9):
                        t = k / 8
                        loop.append(((1 - t) ** 2 * cur[0] + 2 * t * (1 - t) * c[0] + t * t * e[0], (1 - t) ** 2 * cur[1] + 2 * t * (1 - t) * c[1] + t * t * e[1]))
                    cur = e
                elif cmd == "C":
                    c1 = (num(), num()); c2 = (num(), num()); e = (num(), num())
                    for k in range(1, 11):
                        t = k / 10; u = 1 - t
                        loop.append((u ** 3 * cur[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * e[0], u ** 3 * cur[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * e[1]))
                    cur = e
                elif cmd in "Zz":
                    if loop: loops.append(loop)
                    loop = []
                else:
                    raise ValueError(cmd)
            if loop: loops.append(loop)
        xs = [p[0] for l in loops for p in l]; ys = [p[1] for l in loops for p in l]
        s = width / (max(xs) - min(xs)); cx = (max(xs) + min(xs)) / 2; cy = (max(ys) + min(ys)) / 2
        loops = [[((x - cx) * s, -(y - cy) * s) for x, y in l] for l in loops]
        ob = self.shape("wordmark", loops, parent, thick=0.20, bevel=0.012, z=z)
        return ob

    # ---- the parts, each in its own frame, lying in z = +-TH/2 ----
    def make_parts(self):
        P = {}
        def part(name):
            P[name] = self.empty(name); return P[name]
        e = part("bar")
        self.shape("bar", [rrect(10.4, 1.3, 0.38)], e)
        for k in range(3):
            self.disc("dot", -4.55 + k * 0.5, 0, 0.15, 0.12, e, z=TH / 2)
        self.shape("addr", [rrect(6.2, 0.74, 0.37), rrect(6.02, 0.56, 0.28)], e, thick=0.12, bevel=0.012, z=TH / 2)
        self.text("url", "yourbusiness.co.uk", 0.47, e, x=0.6, y=0.0, raise_=0.07, track=1.03)
        for i, w in enumerate(("Home", "About", "Contact")):
            e = part("nav%d" % i)
            self.shape("nav", [rrect(3.3, 1.06, 0.53)], e)
            self.text("navt", w, 0.66, e, y=0.0, track=1.02)
        e = part("pic")
        self.shape("pic", [rrect(5.4, 3.7, 0.4), rrect(4.7, 3.0, 0.16)], e)
        for i, w in enumerate((4.3, 4.3, 2.7)):
            e = part("line%d" % i)
            self.shape("line", [rrect(w, 0.52, 0.26)], e)
        e = part("button")
        self.shape("button", [rrect(6.2, 1.9, 0.95)], e)
        self.text("bt", "Book now", 1.16, e, y=0.0, raise_=0.09, track=1.04)
        e = part("pointer")
        a = [(0, 0), (0, -2.05), (0.50, -1.60), (0.90, -2.48), (1.24, -2.32), (0.85, -1.46), (1.50, -1.46)]
        self.shape("pointer", [[(x - 0.7, y + 1.25) for x, y in a]], e, bevel=0.05)
        e = part("field")
        self.shape("field", [rrect(6.2, 1.3, 0.3)], e)
        self.shape("rim", [rrect(6.2, 1.3, 0.3), rrect(5.98, 1.08, 0.2)], e, thick=0.12, bevel=0.012, z=TH / 2)
        self.text("ft", "Your name", 0.62, e, x=-1.25, y=0.0, raise_=0.085)
        e = part("send")
        self.shape("send", [rrect(2.9, 1.3, 0.3)], e)
        self.text("st", "Send", 0.64, e, y=0.0, raise_=0.085)
        self.parts = P
        return P


# where each part sits on the sprue, and which runner points feed it: (x, y), [(gate from, gate to)]
SPRUE = {
    "bar": ((0, 8.95), [((-3.2, 10.84), (-3.2, 9.6)), ((3.2, 10.84), (3.2, 9.6)), ((0, 8.36), (0, 8.3))]),
    "nav0": ((-3.65, 6.3), [((-3.65, 7.24), (-3.65, 6.8)), ((-3.65, 5.16), (-3.65, 5.8))]),
    "nav1": ((0, 6.3), [((0, 7.24), (0, 6.8)), ((0, 5.16), (0, 5.8))]),
    "nav2": ((3.65, 6.3), [((3.65, 7.24), (3.65, 6.8)), ((3.65, 5.16), (3.65, 5.8))]),
    "pic": ((-3.3, 1.75), [((-3.3, 4.84), (-3.3, 3.6)), ((-3.3, -1.34), (-3.3, -0.1)), ((-8.14, 1.75), (-6.0, 1.75))]),
    "line0": ((4.05, 3.3), [((1.16, 3.3), (1.9, 3.3))]),
    "line1": ((4.05, 1.75), [((1.16, 1.75), (1.9, 1.75))]),
    "line2": ((3.25, 0.2), [((1.16, 0.2), (1.9, 0.2))]),
    "button": ((0, 12.4), [((-1.7, 13.64), (-1.7, 13.35)), ((1.7, 13.64), (1.7, 13.35)), ((0, 11.16), (0, 11.45))]),
    "pointer": ((4.3, -4.0), [((4.3, -1.66), (3.63, -2.75)), ((8.14, -4.4), (5.08, -4.4))]),
    "field": ((-2.9, -4.0), [((-2.9, -1.66), (-2.9, -3.35)), ((-2.9, -6.34), (-2.9, -4.65))]),
    "send": ((4.6, -8.7), [((4.6, -6.66), (4.6, -8.05)), ((8.14, -8.7), (6.05, -8.7))]),
}
RUNNERS = [[(-8.3, 11.0), (8.3, 11.0)], [(-8.3, 7.4), (8.3, 7.4)], [(-8.3, 5.0), (8.3, 5.0)], [(-8.3, -1.5), (8.3, -1.5)], [(-8.3, -6.5), (8.3, -6.5)],
           [(1.0, 5.0), (1.0, -1.5)], [(1.4, -1.5), (1.4, -6.5)], [(1.25, -6.5), (1.25, -11.0)]]
TABS = [(-8.3, 6.3, "1", "r"), (-8.3, 3.9, "2", "r"), (1.0, 4.2, "3", "l"), (-8.3, -4.0, "4", "r"), (8.3, -2.6, "5", "l"), (8.3, 9.0, "6", "l"), (6.4, -11.0, "7", "u")]
# where each part sits on the finished page (page frame), z above the page
PAGE = {"bar": (0, 6.35), "nav0": (-3.65, 4.8), "nav1": (0, 4.8), "nav2": (3.65, 4.8), "pic": (-2.5, 1.85),
        "line0": (3.05, 3.0), "line1": (3.05, 1.95), "line2": (2.25, 0.9), "button": (-2.1, -1.55), "field": (-2.1, -4.6), "send": (3.0, -4.6)}


def scene(frame):
    k = Kit()
    # the sweep
    prof = [(-900, 0), (190, 0)] + [(190 + 80 * math.sin(math.radians(a)), 80 - 80 * math.cos(math.radians(a))) for a in range(5, 91, 5)] + [(270, 1500)]
    vs = [(sx * 2500, y, z) for y, z in prof for sx in (-1, 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(vs, [], [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(prof) - 1)])
    for p in me.polygons: p.use_smooth = True
    sw = link(bpy.data.objects.new("sweep", me))
    m = bpy.data.materials.new("sweep"); m.use_nodes = True; p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*VIOLET, 1); p.inputs["Roughness"].default_value = 0.72; p.inputs["Specular IOR Level"].default_value = 0.25
    sw.data.materials.append(m)

    root = k.empty("sprue"); root.rotation_euler.z = math.radians(YAW[frame]); root.location.z = ZM
    out = [(x, y + 1.4) for x, y in rrect(SW, SH, 0.9, 12)]
    k.tube("outer", [out], root, cyclic=True)
    k.tube("runners", RUNNERS, root)
    for path in RUNNERS:
        for x, y in path:
            k.disc("pin", x, y, 0.27, 0.40, root)
    for x, y in ((-7.5, 11 - 0.9 * 0), ):
        pass
    for x, y, n, d in TABS:
        t = k.empty("tab", root)
        dx, dy = {"u": (0, 0.42), "d": (0, -0.42), "l": (-0.42, 0), "r": (0.42, 0)}[d]
        t.location = (x + dx, y + dy, 0)
        k.shape("tab", [rrect(0.86, 0.86, 0.2)], t, thick=0.14)
        k.text("n", n, 0.50, t, z=0.07, raise_=0.05)
    # maker's tab, moulded into the bottom row
    mk = k.empty("maker", root); mk.location = (-3.5, -8.7, 0)
    k.shape("maker", [rrect(5.6, 1.7, 0.3)], mk)
    k.wordmark(mk, 4.3, TH / 2 + 0.02)
    k.cone("mg", (-3.5, -6.66, 0), (-3.5, -7.85, 0), 0.13, 0.13, root); k.cone("mg", (-3.5, -10.84, 0), (-3.5, -9.55, 0), 0.13, 0.13, root)

    P = k.make_parts()
    free = {1: [], 2: ["button"], 3: list(PAGE) + ["pointer"]}[frame]
    for name, ((x, y), gates) in SPRUE.items():
        e = P[name]
        cut = name in free
        for a, b in gates:
            a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
            if cut:      # a stub left on the runner
                k.cone("stub", a, a + (b - a).normalized() * 0.2, 0.11, 0.09, root)
            else:
                k.cone("gate", a, b, 0.11, 0.055, root)
        if not cut:
            e.parent = root; e.location = (x, y, 0)
    if frame == 2:
        e = P["button"]; e.parent = root
        e.location = (0.8, 12.95, 0.112); e.rotation_euler = (math.radians(9.5), 0, math.radians(-5))
        for gx, gy in ((-1.7, 0.95), (1.7, 0.95), (0, -0.95)):        # the nubs the cutters left on it
            k.cone("nub", (gx, gy, 0), (gx, gy + (0.1 if gy > 0 else -0.1), 0), 0.07, 0.06, e)
    if frame == 3:
        pg = k.empty("page", root); pg.location = (0, 2.7, RR + 0.11); pg.rotation_euler.z = math.radians(0)
        k.shape("page", [[(x, y + 0.85) for x, y in rrect(11.4, 13.3, 0.55)]], pg, thick=0.2)
        for name, (x, y) in PAGE.items():
            P[name].parent = pg; P[name].location = (x, y, 0.1 + TH / 2 - 0.01)
        e = P["pointer"]; e.parent = pg
        e.location = (1.32, -2.45, 0.1 + TH + TH / 2 + 0.03); e.scale = (0.85, 0.85, 1); e.rotation_euler = (math.radians(4), math.radians(-5), math.radians(4))


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
    sc.render.threads_mode = "FIXED"; sc.render.threads = 4
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.95, 0.93, 1.0, 1); bg.inputs["Strength"].default_value = 0.07

    scene(frame)
    shot = SHOTS[frame]
    # key: a small window low on the left and behind, so every runner throws a long shadow towards the camera
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 50; key.size_y = 60
    key.energy = 2.4e6; key.color = (1.0, 0.96, 0.90)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (-340, 170, 150); aim(ko, (0, 0, 0))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 320; fl.energy = 0.12e5; fl.color = (0.93, 0.93, 1.0)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (160, -420, 260); aim(fo, (0, 0, 0))
    st = bpy.data.lights.new("strip", "AREA"); st.shape = "RECTANGLE"; st.size = 520; st.size_y = 26; st.energy = 1.5e6; st.color = (1.0, 0.98, 0.95)
    so = link(bpy.data.objects.new("strip", st)); so.location = (40, 330, 200); aim(so, (0, 0, 0))
    top = bpy.data.lights.new("top", "AREA"); top.size = 200; top.energy = 0.8e5
    to = link(bpy.data.objects.new("top", top)); to.location = (60, 60, 420); aim(to, (0, 0, 0), up=(0, 1, 0))

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    yw = math.radians(YAW[frame]); cy_, sy_ = math.cos(yw), math.sin(yw)
    wl = lambda p: (p[0] * cy_ - p[1] * sy_, p[0] * sy_ + p[1] * cy_, p[2])
    shot = dict(shot, loc=wl(shot["loc"]), aim=wl(shot["aim"]), focus=wl(shot["focus"]))
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]; cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).dot((Vector(shot["aim"]) - co.location).normalized())
    cam.dof.aperture_fstop = shot["f"]
    if quality == "probe":
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update()
        yaw = math.radians(YAW[frame]); c, s = math.cos(yaw), math.sin(yaw)
        for nm, (x, y) in {"TL": (-8.3, 13.8), "TR": (8.3, 13.8), "btn": (0.45, 12.95), "pgT": (0, 10.2), "pgB": (0, -4.8), "barL": (-5.2, 8.95), "barR": (5.2, 8.95), "nvL": (-5.3, 6.3), "nvR": (5.3, 6.3), "BL": (-8.3, -11), "BR": (8.3, -11), "C": (0, 0)}.items():
            v = world_to_camera_view(sc, co, Vector((x * c - y * s, x * s + y * c, 0.2)))
            print(f"  f{frame} {nm:3s} x {v.x * W:7.0f}  y {(1 - v.y) * H:7.0f}")
        return None
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region
    exr = str(TMP / f"nx-kit-{frame}.exr")
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
    x = np.where(x > 0.60, 0.60 + (1 - np.exp(-(x - 0.60) / 0.40)) * 0.36, x)
    x = np.clip(x, 0, 1)
    lum = (x * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    x = np.clip(lum + (x - lum) * 1.10, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3 + frame)
    x += rng.normal(0, 0.006, (H, W, 1)).astype(np.float32)
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
        exr = str(TMP / f"nx-kit-{fr}.exr")
        if quality == "probe":
            build(fr, quality); continue
        grade(exr if regrade else build(fr, quality), fr, quality)
