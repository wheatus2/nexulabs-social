"""Renders the pictures for this Story with Blender's Python module (pip install bpy brotli scipy).

Two brass keys for a made-up florist (Wrenfield Flowers), each with a manila key tag, on a honed graphite
slab. One tag is stamped wrenfield.co.uk, the other wrenfield.com. tex.py draws the tags.
  1  both keys and tags lying side by side: .com or .co.uk?
  2  low and close across the .co.uk tag, the .com one soft behind: it says you're in the UK
  3  both keys on one ring: get both, point the .com at the .co.uk

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

SLAB = (0.030, 0.032, 0.036)
MANILA = (0.62, 0.47, 0.25)
BRASS = (0.80, 0.56, 0.24)
STEEL = (0.62, 0.62, 0.63)

TAG_W, TAG_H = 0.060, 0.120
HOLE = (0.0, TAG_H / 2 - 0.011)          # in the tag's own frame, centred on the tag


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def link(ob):
    bpy.context.scene.collection.objects.link(ob); return ob


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


# ---------- the slab ----------
def slab():
    bpy.ops.mesh.primitive_plane_add(size=3.0)
    ob = bpy.context.object
    m, nt, p = mat("slab"); N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.42
    p.inputs["Specular IOR Level"].default_value = 0.22
    tc = N.new("ShaderNodeTexCoord")
    n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 30; n1.inputs["Detail"].default_value = 6
    n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 900; n2.inputs["Detail"].default_value = 2
    L.new(tc.outputs["Object"], n1.inputs[0]); L.new(tc.outputs["Object"], n2.inputs[0])
    c = N.new("ShaderNodeMix"); c.data_type = "RGBA"
    c.inputs["A"].default_value = (SLAB[0] * 0.85, SLAB[1] * 0.85, SLAB[2] * 0.85, 1)
    c.inputs["B"].default_value = (SLAB[0] * 1.18, SLAB[1] * 1.18, SLAB[2] * 1.18, 1)
    L.new(n1.outputs["Fac"], c.inputs["Factor"])
    L.new(c.outputs["Result"], p.inputs["Base Color"])
    rr = N.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.34; rr.inputs["To Max"].default_value = 0.55
    L.new(n1.outputs["Fac"], rr.inputs["Value"]); L.new(rr.outputs["Result"], p.inputs["Roughness"])
    b = N.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.06; b.inputs["Distance"].default_value = 0.0001
    L.new(n2.outputs["Fac"], b.inputs["Height"]); L.new(b.outputs["Normal"], p.inputs["Normal"])
    ob.data.materials.append(m)
    return ob


# ---------- a key ----------
def key_outline():
    """Outline of a pin-tumbler key in mm, bow centred at the origin, blade along +x. Returns (outer, hole)."""
    R = 12.5
    top, bot = 4.1, -4.1
    pts = []
    a0 = math.asin(5.2 / R); a1 = 2 * math.pi - math.asin(5.2 / R)
    # bow: from where its upper shoulder meets the neck, round the back, to the lower shoulder
    for i in range(0, 61):
        a = a0 + (a1 - a0) * i / 60
        pts.append((R * math.cos(a), R * math.sin(a)))
    # lower neck and shoulder
    pts += [(13.6, -5.2), (14.6, -5.6), (15.4, -5.6), (15.6, bot)]
    # bitting: five cuts of different depths along the lower edge
    x = 17.0
    depths = [1.6, 0.6, 2.3, 1.1, 1.9]
    pts.append((x, bot))
    for d in depths:
        pts += [(x + 1.2, bot + d), (x + 2.6, bot + d), (x + 3.8, bot)]
        x += 4.6
    pts += [(x + 1.0, bot), (x + 3.4, bot + 2.6), (x + 4.4, top - 0.9), (x + 4.0, top)]
    tip = x + 4.0
    pts += [(15.6, top), (15.4, 5.6), (14.6, 5.6), (13.6, 5.2)]
    pts = pts[::-1]
    hole = [(-6.2 + 2.9 * math.cos(2 * math.pi * i / 48), 2.9 * math.sin(2 * math.pi * i / 48)) for i in range(48)]
    return pts, hole, tip


def key(name):
    outer, hole, tip = key_outline()
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "2D"; cu.fill_mode = "BOTH"
    for poly in (outer, hole):
        sp = cu.splines.new("POLY"); sp.points.add(len(poly) - 1)
        for i, (x, y) in enumerate(poly):
            sp.points[i].co = (x * 0.001, y * 0.001, 0, 1)
        sp.use_cyclic_u = True
    cu.extrude = 0.00078
    cu.bevel_depth = 0.00030
    cu.bevel_resolution = 3
    ob = link(bpy.data.objects.new(name, cu))
    # convert so it can be shaded smooth by angle
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.convert(target="MESH")
    ob = bpy.context.view_layer.objects.active
    ob.select_set(False)
    try:
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True); bpy.context.view_layer.objects.active = ob
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    except Exception:
        for p in ob.data.polygons:
            p.use_smooth = False
    ob.data.materials.append(brass())
    # the blade's two milled grooves, as a shallow bump along x
    return ob


_brass = None


def brass():
    global _brass
    if _brass:
        return _brass
    m, nt, p = mat("brass"); N, L = nt.nodes, nt.links
    p.inputs["Metallic"].default_value = 1.0
    tc = N.new("ShaderNodeTexCoord")
    # scuffs: noise stretched one way, plus a fine tarnish
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (2600, 260, 2600)
    mp.inputs["Rotation"].default_value = (0, 0, 0.3)
    L.new(tc.outputs["Object"], mp.inputs[0])
    sc = N.new("ShaderNodeTexNoise"); sc.inputs["Scale"].default_value = 1; sc.inputs["Detail"].default_value = 10
    sc.inputs["Roughness"].default_value = 0.7
    L.new(mp.outputs[0], sc.inputs[0])
    tn = N.new("ShaderNodeTexNoise"); tn.inputs["Scale"].default_value = 160; tn.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], tn.inputs[0])
    rr = N.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.14; rr.inputs["To Max"].default_value = 0.30
    L.new(sc.outputs["Fac"], rr.inputs["Value"])
    L.new(rr.outputs["Result"], p.inputs["Roughness"])
    c = N.new("ShaderNodeMix"); c.data_type = "RGBA"
    c.inputs["A"].default_value = (*BRASS, 1); c.inputs["B"].default_value = (BRASS[0] * 0.62, BRASS[1] * 0.52, BRASS[2] * 0.36, 1)
    tr = N.new("ShaderNodeMapRange"); tr.inputs["From Min"].default_value = 0.52; tr.inputs["From Max"].default_value = 0.75
    tr.inputs["To Max"].default_value = 0.65
    L.new(tn.outputs["Fac"], tr.inputs["Value"]); L.new(tr.outputs["Result"], c.inputs["Factor"])
    L.new(c.outputs["Result"], p.inputs["Base Color"])
    b = N.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.08; b.inputs["Distance"].default_value = 0.00002
    L.new(sc.outputs["Fac"], b.inputs["Height"]); L.new(b.outputs["Normal"], p.inputs["Normal"])
    _brass = m
    return m


# ---------- a tag ----------
def tag(name, texfile, seed, curl=0.0016):
    """Flat-ish manila tag, origin at the centre of its punched hole, hanging along -y."""
    nx, ny = 60, 120
    verts, faces, uvs = [], [], []
    rng = np.random.default_rng(seed)
    ph = rng.random(3) * 6
    for j in range(ny + 1):
        for i in range(nx + 1):
            u, v = i / nx, j / ny
            x = (u - 0.5) * TAG_W; y = (v - 0.5) * TAG_H
            # card never lies flat: a soft bow across and a lift at the far end
            z = 0.00035 + curl * (u - 0.5) ** 2 * 1.3
            z += 0.0007 * max(0.0, (0.18 - v) / 0.18) ** 2
            z += 0.00012 * math.sin(9 * y + ph[0]) * math.sin(13 * x + ph[1])
            verts.append((x - HOLE[0], y - HOLE[1], z))
            uvs.append((u, v))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    uvl = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        poly.use_smooth = True
        for li in poly.loop_indices:
            uvl.data[li].uv = uvs[me.loops[li].vertex_index]
    ob = link(bpy.data.objects.new(name, me))
    sol = ob.modifiers.new("solid", "SOLIDIFY"); sol.thickness = 0.00028; sol.offset = -1

    m, nt, p = mat(name); N, L = nt.nodes, nt.links
    m.blend_method = "HASHED" if hasattr(m, "blend_method") else None
    p.inputs["Roughness"].default_value = 0.82
    p.inputs["Specular IOR Level"].default_value = 0.25
    uvn = N.new("ShaderNodeUVMap"); uvn.uv_map = "UVMap"
    tc = N.new("ShaderNodeTexCoord")
    ink = N.new("ShaderNodeTexImage"); ink.image = bpy.data.images.load(str(HERE / "tex" / texfile))
    ink.interpolation = "Cubic"; ink.extension = "CLIP"
    L.new(uvn.outputs["UV"], ink.inputs[0])
    mask = N.new("ShaderNodeTexImage"); mask.image = bpy.data.images.load(str(HERE / "tex" / "mask.png"))
    mask.image.colorspace_settings.name = "Non-Color"; mask.extension = "CLIP"; mask.interpolation = "Cubic"
    L.new(uvn.outputs["UV"], mask.inputs[0])
    ring = N.new("ShaderNodeTexImage"); ring.image = bpy.data.images.load(str(HERE / "tex" / "ring.png"))
    ring.image.colorspace_settings.name = "Non-Color"; ring.extension = "CLIP"
    L.new(uvn.outputs["UV"], ring.inputs[0])
    # manila: long fibres, a few darker flecks, a cleaner reinforcing ring round the hole
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1400, 300, 1400)
    L.new(tc.outputs["Object"], mp.inputs[0])
    fib = N.new("ShaderNodeTexNoise"); fib.inputs["Scale"].default_value = 1; fib.inputs["Detail"].default_value = 8
    L.new(mp.outputs[0], fib.inputs[0])
    blot = N.new("ShaderNodeTexNoise"); blot.inputs["Scale"].default_value = 45; blot.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], blot.inputs[0])
    c1 = N.new("ShaderNodeMix"); c1.data_type = "RGBA"
    c1.inputs["A"].default_value = (MANILA[0] * 0.90, MANILA[1] * 0.88, MANILA[2] * 0.84, 1)
    c1.inputs["B"].default_value = (MANILA[0] * 1.05, MANILA[1] * 1.05, MANILA[2] * 1.06, 1)
    L.new(fib.outputs["Fac"], c1.inputs["Factor"])
    c2 = N.new("ShaderNodeMix"); c2.data_type = "RGBA"; c2.blend_type = "MULTIPLY"; c2.inputs["Factor"].default_value = 0.12
    L.new(c1.outputs["Result"], c2.inputs["A"]); L.new(blot.outputs["Color"], c2.inputs["B"])
    c3 = N.new("ShaderNodeMix"); c3.data_type = "RGBA"
    c3.inputs["B"].default_value = (MANILA[0] * 0.80, MANILA[1] * 0.70, MANILA[2] * 0.52, 1)
    rf = N.new("ShaderNodeMath"); rf.operation = "MULTIPLY"; rf.inputs[1].default_value = 0.55
    L.new(ring.outputs["Color"], rf.inputs[0]); L.new(rf.outputs[0], c3.inputs["Factor"])
    L.new(c2.outputs["Result"], c3.inputs["A"])
    c4 = N.new("ShaderNodeMix"); c4.data_type = "RGBA"
    L.new(ink.outputs["Alpha"], c4.inputs["Factor"]); L.new(c3.outputs["Result"], c4.inputs["A"]); L.new(ink.outputs["Color"], c4.inputs["B"])
    L.new(c4.outputs["Result"], p.inputs["Base Color"])
    # ink sits a little glossier than the card
    rr = N.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.82; rr.inputs["To Max"].default_value = 0.55
    L.new(ink.outputs["Alpha"], rr.inputs["Value"]); L.new(rr.outputs["Result"], p.inputs["Roughness"])
    hgt = N.new("ShaderNodeMath"); hgt.operation = "MULTIPLY_ADD"; hgt.inputs[2].default_value = 0.0
    L.new(ring.outputs["Color"], hgt.inputs[0]); hgt.inputs[1].default_value = 0.6
    add = N.new("ShaderNodeMath"); add.operation = "MULTIPLY_ADD"
    L.new(fib.outputs["Fac"], add.inputs[0]); add.inputs[1].default_value = 0.25; L.new(hgt.outputs[0], add.inputs[2])
    b = N.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.25; b.inputs["Distance"].default_value = 0.0002
    L.new(add.outputs[0], b.inputs["Height"]); L.new(b.outputs["Normal"], p.inputs["Normal"])
    # cut the outline and the hole
    tr = N.new("ShaderNodeBsdfTransparent")
    mx = N.new("ShaderNodeMixShader")
    gt = N.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.5
    L.new(mask.outputs["Color"], gt.inputs[0])
    L.new(gt.outputs[0], mx.inputs[0]); L.new(tr.outputs[0], mx.inputs[1]); L.new(p.outputs[0], mx.inputs[2])
    out = nt.nodes["Material Output"]
    L.new(mx.outputs[0], out.inputs["Surface"])
    me.materials.append(m)
    return ob


# ---------- a split ring ----------
def split_ring(name, r=0.0105, wire=0.00075, turns=2.0, pitch=0.0016):
    n = 360
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"
    sp = cu.splines.new("POLY"); sp.points.add(n - 1)
    for i in range(n):
        t = i / (n - 1)
        a = 2 * math.pi * turns * t
        sp.points[i].co = (r * math.cos(a), r * math.sin(a), pitch * t, 1)
    cu.bevel_depth = wire; cu.bevel_resolution = 6; cu.use_fill_caps = True
    ob = link(bpy.data.objects.new(name, cu))
    m, nt, p = mat("steel")
    p.inputs["Base Color"].default_value = (*STEEL, 1); p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = 0.28
    cu.materials.append(m)
    return ob


def place(ob, xy, rot, z=0.0, tilt=(0.0, 0.0)):
    ob.location = (xy[0], xy[1], z)
    ob.rotation_euler = (math.radians(tilt[0]), math.radians(tilt[1]), math.radians(rot))


# where things lie (metres, on the slab). Each tag hangs from its key's bow.
LAYOUT = {
    "pair": dict(
        couk=dict(tag=((-0.044, -0.030), 7), key=((-0.040, 0.030), 104)),
        com=dict(tag=((0.040, -0.056), -9), key=((0.040, 0.006), 74)),
    ),
    "macro": dict(
        couk=dict(tag=((-0.020, -0.050), 6), key=((-0.016, 0.010), 100)),
        com=dict(tag=((0.040, 0.075), -14), key=((0.036, 0.135), 76)),
    ),
    "ring": dict(
        couk=dict(tag=((-0.036, -0.050), 4), key=((-0.030, 0.050), 0)),
        com=dict(tag=((0.036, -0.050), -11), key=((0.030, 0.050), 0)),
    ),
}

SHOTS = {
    1: dict(target=(-0.002, -0.020, 0.0), dist=0.52, az=-6, el=60, lens=60, f=8, focus=(0.0, -0.030, 0.0), shift=(0.0, -0.205),
            layout="pair"),
    2: dict(target="couk", dist=0.33, az=-16, el=50, lens=85, f=4.0, focus="couk", shift=(0.0, -0.23),
            layout="macro"),
    3: dict(target=(0.000, -0.020, 0.0), dist=0.45, az=4, el=40, lens=60, f=5.6, focus=(0.0, -0.025, 0.0), shift=(0.0, -0.17),
            layout="ring"),
}


def key_bow_hole_world(kob):
    """World position of the centre of the key's bow hole (key origin is the bow centre; hole at x=-6.2mm)."""
    return kob.matrix_world @ Vector((-0.0062, 0, 0))


def build(frame, quality, region=None):
    shot = SHOTS[frame]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 72 if final else 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"
    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    # a room for the brass to mirror: a warm window band above a darker floor
    wn = world.node_tree.nodes; wl = world.node_tree.links
    bg = wn["Background"]
    grad = wn.new("ShaderNodeTexGradient"); grad.gradient_type = "LINEAR"
    tcw = wn.new("ShaderNodeTexCoord")
    sep = wn.new("ShaderNodeSeparateXYZ"); wl.new(tcw.outputs["Generated"], sep.inputs[0])
    ramp = wn.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[0].color = (0.010, 0.010, 0.012, 1)
    ramp.color_ramp.elements[1].position = 0.80; ramp.color_ramp.elements[1].color = (0.50, 0.47, 0.42, 1)
    wl.new(sep.outputs["Z"], ramp.inputs[0])
    wl.new(ramp.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.05

    slab()
    lay = LAYOUT[shot["layout"]]
    keys = {}
    for nm, seed in (("couk", 5), ("com", 9)):
        k = key(f"key-{nm}")
        (kx, ky), kr = lay[nm]["key"]
        place(k, (kx, ky), kr)
        keys[nm] = k
        bpy.context.view_layer.update()
        hole = key_bow_hole_world(k)
        t = tag(f"tag-{nm}", f"tag-{nm}.png", seed)
        (tx, ty), tr = lay[nm]["tag"]
        place(t, (tx, ty), tr)
        bpy.context.view_layer.update()
        # move the tag so its hole sits a ring's width from the key's hole, along the line between them
        th = t.matrix_world.translation.copy()
        d = (Vector((th.x, th.y, 0)) - Vector((hole.x, hole.y, 0))).normalized()
        if shot["layout"] in ("pair", "macro"):
            ringc = Vector((hole.x, hole.y, 0)) + d * 0.0105
            t.location = (ringc + d * 0.0100).to_tuple()[:2] + (0.0,)
            t.rotation_euler.z = math.atan2(d.y, d.x) + math.pi / 2 + math.radians(tr)
            rg = split_ring(f"ring-{nm}")
            rg.location = (ringc.x, ringc.y, 0.0012)
            rg.rotation_euler = (math.radians(4), math.radians(-3), math.atan2(d.y, d.x))
            # key bow and tag rest on the ring wire
            k.location.z = 0.0018; k.rotation_euler.x = math.radians(2.5)
            t.location.z = 0.0003
    if shot["layout"] == "ring":
        # one bigger ring through both bows and both tags
        rg = split_ring("ring", r=0.016, wire=0.0009)
        rg.location = (0.0, 0.012, 0.0015)
        rg.rotation_euler = (math.radians(3), math.radians(2), math.radians(30))
        c = Vector((0.0, 0.012, 0.0))
        for nm in ("couk", "com"):
            k = keys[nm]
            (kx, ky), kr = LAYOUT["ring"][nm]["key"]
            u = (Vector((kx, ky, 0)) - c).normalized()
            org = c + u * (0.016 + 0.0062)
            k.location = (org.x, org.y, 0.0022 if nm == "couk" else 0.0030)
            k.rotation_euler = (math.radians(2), 0, math.atan2(u.y, u.x) + math.radians(kr))
        for nm in ("couk", "com"):
            t = bpy.data.objects[f"tag-{nm}"]
            (tx, ty), _ = LAYOUT["ring"][nm]["tag"]
            v = Vector((tx, ty, 0)) - c
            pos = c + v.normalized() * 0.016
            t.location = (pos.x, pos.y, 0.0016 if nm == "couk" else 0.0006)
            t.rotation_euler.z = math.atan2(v.y, v.x) + math.pi / 2 + math.radians(LAYOUT["ring"][nm]["tag"][1])

    # light: one low warm key from the upper left so every edge throws a shadow; a cool fill; a window strip for the brass
    area("key", (-0.62, 0.40, 0.20), (0, 0, 0), 0.08, 36, (1.0, 0.92, 0.80))
    area("fill", (0.60, -0.45, 0.50), (0, 0, 0), 1.2, 1.4, (0.86, 0.92, 1.0))
    area("strip", (0.10, 0.70, 0.45), (0, 0, 0), 0.08, 18, (1.0, 0.98, 0.95), size_y=1.2)

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 36
    az, el = math.radians(shot["az"]), math.radians(shot["el"])
    def resolve(v):
        if isinstance(v, str):
            return bpy.data.objects[f"tag-{v}"].matrix_world @ Vector((0.0, -0.053, 0.0004))
        return Vector(v)
    bpy.context.view_layer.update()
    tg = resolve(shot["target"])
    co.location = tg + shot["dist"] * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    look(co, tg)
    cam.lens = shot["lens"]; cam.shift_x, cam.shift_y = shot["shift"]
    cam.dof.use_dof = True
    cam.dof.focus_distance = (resolve(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"]
    cam.clip_start = 0.005
    exr = str(TMP / f"nx-keys-{frame}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def pixels(exr):
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32), w, h


EXPOSURE = 0.30


def grade(exr, frame, quality):
    from PIL import Image
    a, w, h = pixels(exr)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    a = np.clip(a, 0, None)
    # a little bloom on the brass highlights
    from scipy.ndimage import gaussian_filter
    hi = np.clip(a - 1.2, 0, None)
    a = a + 0.10 * np.stack([gaussian_filter(hi[..., c], 14) for c in range(3)], -1)
    x = a * EXPOSURE
    x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.18 * np.clip(r - 0.5, 0, 1) ** 1.5)[..., None]
    rng = np.random.default_rng(frame)
    x += rng.normal(0, 0.009, (H, W, 1)).astype(np.float32)
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
        exr = str(TMP / f"nx-keys-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
