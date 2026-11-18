"""Renders the three pictures for this Story with Blender's Python module
(python3.13 -m pip install bpy brotli scipy pillow numpy --break-system-packages).

Product photography for a made-up chocolatier (Ottermoor Chocolate), so its concept homepage has
something real to show: hand-finished chocolates on a duck-egg sweep, one of them ruby pink.
  1  a loose line of chocolates, low and from the right, the ruby one sharp at the front
  2  the box of nine from higher up, the ruby one in the middle (the concept homepage's hero picture)
  3  right up against the ruby one, the rest a blur behind it

  python3.13 build.py <frame 1|2|3|all> [draft|final] [regrade]
writes art/render-0N.jpg (1080x1920). The type is set over it in slide-0N.html.
"""
import sys, math, random, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())

SWEEP = (0.205, 0.555, 0.50)
DARK = (0.030, 0.013, 0.007)
MILK = (0.155, 0.062, 0.026)
WHITE = (0.80, 0.66, 0.44)
RUBY = (0.34, 0.012, 0.055)
CREAM = (0.83, 0.74, 0.58)
GOLD = (1.0, 0.62, 0.20)


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def rounded(points, rad=0.0012, n=6):
    out = [points[0]]
    for a, b, c in zip(points, points[1:], points[2:]):
        A, B, C = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0)), Vector((c[0], c[1], 0))
        d1, d2 = (A - B).normalized(), (C - B).normalized()
        r = min(rad, (A - B).length / 2.2, (C - B).length / 2.2)
        p1, p2 = B + d1 * r, B + d2 * r
        for j in range(n + 1):
            u = j / n
            q = (1 - u) ** 2 * p1 + 2 * u * (1 - u) * B + u ** 2 * p2
            out.append((q.x, q.y))
    out.append(points[-1])
    return out


def loft(name, profile, n=2.0, segs=160):
    """A turned shape whose plan is a circle (n=2) or a rounded square (n=4 to 6)."""
    verts, faces = [], []
    for (r, z) in profile:
        for s in range(segs):
            a = 2 * math.pi * s / segs
            k = (abs(math.cos(a)) ** n + abs(math.sin(a)) ** n) ** (-1.0 / n)
            verts.append((r * k * math.cos(a), r * k * math.sin(a), z))
    for p in range(len(profile) - 1):
        for s in range(segs):
            a = p * segs + s; b = p * segs + (s + 1) % segs
            faces.append((a, b, b + segs, a + segs))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for poly in me.polygons:
        poly.use_smooth = True
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob


def box(name, size, loc, material, bevel=0.0):
    sx, sy, sz = size
    v = [(x * sx / 2, y * sy / 2, z * sz / 2) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f)
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; me.materials.append(material)
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 3
    return ob


def look(ob, target):
    f = (Vector(target) - ob.location).normalized()
    r = f.cross(Vector((0, 0, 1))).normalized()
    u = r.cross(f)
    ob.rotation_euler = Matrix((r, u, -f)).transposed().to_euler()


def area(name, loc, target, size, energy, colour=(1, 1, 1), size_y=None):
    l = bpy.data.lights.new(name, "AREA"); l.size = size; l.energy = energy; l.color = colour
    if size_y:
        l.shape = "RECTANGLE"; l.size_y = size_y
    o = bpy.data.objects.new(name, l); bpy.context.scene.collection.objects.link(o)
    o.location = loc; look(o, target)
    return o


# ---------------------------------------------------------------- chocolate
def chocolate(name, colour, rough=0.26, decor=None, seed=0):
    """Tempered chocolate: a hard shine that is not quite even, and a little light in the edges."""
    m, nt, p = mat(name)
    N, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (*colour, 1)
    p.inputs["Specular IOR Level"].default_value = 0.55
    p.inputs["Subsurface Weight"].default_value = 0.5 if colour[1] > 0.3 else 0.10
    p.inputs["Subsurface Radius"].default_value = (1.0, 0.5, 0.3)
    p.inputs["Subsurface Scale"].default_value = 0.0012
    p.inputs["Coat Weight"].default_value = 0.35
    p.inputs["Coat Roughness"].default_value = 0.06
    tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Location"].default_value = (seed * 1.7, seed * 0.9, seed * 0.3)
    L.new(tc.outputs["Object"], mp.inputs[0])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 90; nz.inputs["Detail"].default_value = 3
    L.new(mp.outputs[0], nz.inputs["Vector"])
    rr = N.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = rough - 0.05; rr.inputs["To Max"].default_value = rough + 0.09
    L.new(nz.outputs["Fac"], rr.inputs["Value"])
    rough_out = rr.outputs[0]
    base_out = None
    if decor == "stripe":
        # one brush of cocoa butter across the top, dragged, with a broken edge
        sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
        d = N.new("ShaderNodeMath"); d.operation = "MULTIPLY_ADD"; d.inputs[1].default_value = 0.82; d.inputs[2].default_value = 0.0
        L.new(sep.outputs["X"], d.inputs[0])
        d2 = N.new("ShaderNodeMath"); d2.operation = "MULTIPLY_ADD"; d2.inputs[1].default_value = 0.57
        L.new(sep.outputs["Y"], d2.inputs[0]); L.new(d.outputs[0], d2.inputs[2])
        n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 160; n2.inputs["Detail"].default_value = 2
        mp2 = N.new("ShaderNodeMapping"); mp2.inputs["Scale"].default_value = (0.08, 1, 1); mp2.inputs["Rotation"].default_value = (0, 0, math.radians(-35))
        L.new(tc.outputs["Object"], mp2.inputs[0]); L.new(mp2.outputs[0], n2.inputs["Vector"])
        wob = N.new("ShaderNodeMath"); wob.operation = "MULTIPLY_ADD"; wob.inputs[1].default_value = 0.0016; wob.inputs[2].default_value = -0.0008
        L.new(n2.outputs["Fac"], wob.inputs[0])
        dd = N.new("ShaderNodeMath"); dd.operation = "ADD"; L.new(d2.outputs[0], dd.inputs[0]); L.new(wob.outputs[0], dd.inputs[1])
        ab = N.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; L.new(dd.outputs[0], ab.inputs[0])
        lt = N.new("ShaderNodeMapRange"); lt.inputs["From Min"].default_value = 0.0030; lt.inputs["From Max"].default_value = 0.0036
        lt.inputs["To Min"].default_value = 1; lt.inputs["To Max"].default_value = 0
        L.new(ab.outputs[0], lt.inputs["Value"])
        mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
        mix.inputs["A"].default_value = (*colour, 1); mix.inputs["B"].default_value = (0.78, 0.66, 0.48, 1)
        L.new(lt.outputs[0], mix.inputs["Factor"]); base_out = mix.outputs["Result"]
    elif decor == "speckle":
        # sprayed colour, deeper towards the base; a flick of pale cocoa butter in two sizes; one fleck of gold leaf
        sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
        gz = N.new("ShaderNodeMapRange"); gz.inputs["From Min"].default_value = 0.0; gz.inputs["From Max"].default_value = 0.017
        L.new(sep.outputs["Z"], gz.inputs["Value"])
        spray = N.new("ShaderNodeMix"); spray.data_type = "RGBA"
        spray.inputs["A"].default_value = (colour[0] * 0.55, colour[1] * 0.5, colour[2] * 0.6, 1); spray.inputs["B"].default_value = (colour[0] * 1.05, colour[1] * 1.2, colour[2] * 1.1, 1)
        L.new(gz.outputs[0], spray.inputs["Factor"])
        cur = spray.outputs["Result"]
        for scale, thr, smin, smax, col in ((1500, 0.80, 0.05, 0.30, (0.78, 0.50, 0.50, 1)), (520, 0.93, 0.10, 0.26, (0.84, 0.60, 0.58, 1))):
            vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = scale; vo.inputs["Randomness"].default_value = 1.0
            L.new(mp.outputs[0], vo.inputs["Vector"])
            pick = N.new("ShaderNodeTexWhiteNoise"); L.new(vo.outputs["Color"], pick.inputs["Vector"])
            sel = N.new("ShaderNodeMath"); sel.operation = "GREATER_THAN"; sel.inputs[1].default_value = thr
            L.new(pick.outputs["Value"], sel.inputs[0])
            size = N.new("ShaderNodeMapRange"); size.inputs["To Min"].default_value = smin; size.inputs["To Max"].default_value = smax
            pick2 = N.new("ShaderNodeTexWhiteNoise"); L.new(vo.outputs["Position"], pick2.inputs["Vector"])
            L.new(pick2.outputs["Value"], size.inputs["Value"])
            dot = N.new("ShaderNodeMath"); dot.operation = "LESS_THAN"; L.new(vo.outputs["Distance"], dot.inputs[0]); L.new(size.outputs[0], dot.inputs[1])
            both = N.new("ShaderNodeMath"); both.operation = "MULTIPLY"; L.new(dot.outputs[0], both.inputs[0]); L.new(sel.outputs[0], both.inputs[1])
            mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs["B"].default_value = col
            L.new(cur, mix.inputs["A"]); L.new(both.outputs[0], mix.inputs["Factor"]); cur = mix.outputs["Result"]
        # gold leaf: a torn scrap laid just off the top, towards the camera
        off = N.new("ShaderNodeVectorMath"); off.operation = "SUBTRACT"; off.inputs[1].default_value = (0.0030, -0.0052, 0.0152)
        L.new(tc.outputs["Object"], off.inputs[0])
        ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; L.new(off.outputs[0], ln.inputs[0])
        gn = N.new("ShaderNodeTexNoise"); gn.inputs["Scale"].default_value = 520; gn.inputs["Detail"].default_value = 7; gn.inputs["Roughness"].default_value = 0.7
        L.new(tc.outputs["Object"], gn.inputs["Vector"])
        ga = N.new("ShaderNodeMath"); ga.operation = "MULTIPLY_ADD"; ga.inputs[1].default_value = 0.0042; L.new(gn.outputs["Fac"], ga.inputs[0]); L.new(ln.outputs["Value"], ga.inputs[2])
        gm = N.new("ShaderNodeMath"); gm.operation = "LESS_THAN"; gm.inputs[1].default_value = 0.0052; L.new(ga.outputs[0], gm.inputs[0])
        mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs["B"].default_value = (*GOLD, 1)
        L.new(cur, mix.inputs["A"]); L.new(gm.outputs[0], mix.inputs["Factor"]); base_out = mix.outputs["Result"]
        L.new(gm.outputs[0], p.inputs["Metallic"])
        p.inputs["Emission Color"].default_value = (1.0, 0.55, 0.12, 1); em_ = N.new("ShaderNodeMath"); em_.operation = "MULTIPLY"; em_.inputs[1].default_value = 0.5
        L.new(gm.outputs[0], em_.inputs[0]); L.new(em_.outputs[0], p.inputs["Emission Strength"])
        r2 = N.new("ShaderNodeMix"); r2.data_type = "FLOAT"; r2.inputs[3].default_value = 0.34
        L.new(gm.outputs[0], r2.inputs[0]); L.new(rough_out, r2.inputs[2]); rough_out = r2.outputs[0]
        leafbump = (gn, gm)
    elif decor == "gold":
        # a corner brushed with gold lustre
        sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
        s = N.new("ShaderNodeMath"); s.operation = "ADD"; L.new(sep.outputs["X"], s.inputs[0]); L.new(sep.outputs["Y"], s.inputs[1])
        n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 1500; n2.inputs["Detail"].default_value = 6
        L.new(tc.outputs["Object"], n2.inputs["Vector"])
        w = N.new("ShaderNodeMath"); w.operation = "MULTIPLY_ADD"; w.inputs[1].default_value = 0.016; L.new(n2.outputs["Fac"], w.inputs[0]); L.new(s.outputs[0], w.inputs[2])
        th = N.new("ShaderNodeMapRange"); th.inputs["From Min"].default_value = 0.0115; th.inputs["From Max"].default_value = 0.0135
        L.new(w.outputs[0], th.inputs["Value"])
        mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
        mix.inputs["A"].default_value = (*colour, 1); mix.inputs["B"].default_value = (*GOLD, 1)
        L.new(th.outputs[0], mix.inputs["Factor"]); base_out = mix.outputs["Result"]
        L.new(th.outputs[0], p.inputs["Metallic"])
        p.inputs["Emission Color"].default_value = (1.0, 0.55, 0.12, 1); em_ = N.new("ShaderNodeMath"); em_.operation = "MULTIPLY"; em_.inputs[1].default_value = 0.5
        L.new(th.outputs[0], em_.inputs[0]); L.new(em_.outputs[0], p.inputs["Emission Strength"])
        r2 = N.new("ShaderNodeMix"); r2.data_type = "FLOAT"; r2.inputs[3].default_value = 0.42
        L.new(th.outputs[0], r2.inputs[0]); L.new(rough_out, r2.inputs[2]); rough_out = r2.outputs[0]
    if base_out is not None:
        L.new(base_out, p.inputs["Base Color"])
    L.new(rough_out, p.inputs["Roughness"])
    # the surface is never optically flat
    n3 = N.new("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 55; n3.inputs["Detail"].default_value = 2
    L.new(mp.outputs[0], n3.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.0004
    L.new(n3.outputs["Fac"], bump.inputs["Height"])
    if decor == "speckle":
        # the leaf is crinkled and stands a hair proud
        cr = N.new("ShaderNodeTexNoise"); cr.inputs["Scale"].default_value = 2600; cr.inputs["Detail"].default_value = 3
        L.new(tc.outputs["Object"], cr.inputs["Vector"])
        hm = N.new("ShaderNodeMath"); hm.operation = "MULTIPLY"; L.new(cr.outputs["Fac"], hm.inputs[0]); L.new(leafbump[1].outputs[0], hm.inputs[1])
        b2 = N.new("ShaderNodeBump"); b2.inputs["Strength"].default_value = 0.6; b2.inputs["Distance"].default_value = 0.00025
        L.new(hm.outputs[0], b2.inputs["Height"]); L.new(bump.outputs["Normal"], b2.inputs["Normal"]); L.new(b2.outputs["Normal"], p.inputs["Normal"])
    else:
        L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def dome_profile(R=0.0148, Ht=0.0170, e=0.62):
    """A moulded dome: a clean base with a hair of a chamfer, no foot."""
    pts = [(0.0, 0.0), (R - 0.0004, 0.0), (R, 0.0005)]
    for j in range(1, 49):
        t = math.pi / 2 * j / 48
        pts.append((R * math.cos(t) ** e, 0.0005 + (Ht - 0.0005) * math.sin(t)))
    pts[-1] = (0.0, Ht)
    return pts


def palet_profile(R=0.0142, Ht=0.0125):
    pts = [(0.0, 0.0), (R + 0.0006, 0.0), (R + 0.0006, 0.0008), (R, 0.0016), (R - 0.0005, Ht - 0.0012), (R - 0.0018, Ht), (0.0, Ht)]
    return rounded(pts, 0.0011)


def ridged_profile(R=0.0138, Ht=0.0150):
    pts = [(0.0, 0.0), (R + 0.0006, 0.0), (R + 0.0006, 0.0008), (R, 0.0016), (R - 0.0003, Ht - 0.0016), (R - 0.0016, Ht)]
    pts = rounded(pts + [(R - 0.003, Ht)], 0.0010)[:-1]
    r0 = R - 0.0018
    for j in range(1, 81):
        r = r0 * (1 - j / 80)
        pts.append((r, Ht + 0.00045 * (math.cos(2 * math.pi * 4.5 * (r0 - r) / r0) - 1) / 2 * (1 if r > 0.0012 else r / 0.0012)))
    pts[-1] = (0.0, pts[-1][1])
    return pts


def truffle(name, m, seed):
    ob = loft(name, [(0.0128 * math.sin(math.pi * j / 60) + (0 if 0 < j < 60 else 0), 0.0128 * (1 - math.cos(math.pi * j / 60)) * 0.94) for j in range(61)], segs=120)
    tx = bpy.data.textures.new(name, "CLOUDS"); tx.noise_scale = 0.008
    d = ob.modifiers.new("d", "DISPLACE"); d.texture = tx; d.strength = 0.0022; d.texture_coords = "GLOBAL"
    ob.data.materials.append(m)
    return ob


def salt(parent_loc, top_z, rng, m, n=13, spread=0.0085):
    for i in range(n):
        s = rng.uniform(0.0007, 0.0017)
        a = rng.uniform(0, 6.28); r = spread * math.sqrt(rng.uniform(0, 1))
        o = box(f"salt{i}", (s, s * rng.uniform(0.6, 1), s * rng.uniform(0.25, 0.6)),
                (parent_loc[0] + r * math.cos(a), parent_loc[1] + r * math.sin(a), top_z + s * 0.15), m)
        o.rotation_euler = (rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), rng.uniform(0, 3.14))


MATS = {}


def piece(kind, loc, rot=0.0, seed=0):
    """kind: ruby, stripe, gold, salt, white, truffle, plain, milkdome"""
    x, y = loc[0], loc[1]; z = loc[2] if len(loc) > 2 else 0.0
    rng = random.Random(seed * 7 + 3)

    def M(key, *a, **k):
        if key not in MATS:
            MATS[key] = chocolate(key, *a, **k)
        return MATS[key]
    if kind == "ruby":
        ob = loft("ruby", dome_profile()); ob.data.materials.append(M("ruby", RUBY, 0.14, "speckle", 3))
    elif kind == "stripe":
        ob = loft("stripe", dome_profile(0.0145, 0.0160, 0.66)); ob.data.materials.append(M("stripe", DARK, 0.20, "stripe", 5))
    elif kind == "gold":
        ob = loft("gold", palet_profile(), n=5.0); ob.data.materials.append(M("gold", DARK, 0.22, "gold", 9))
    elif kind == "salt":
        ob = loft("saltp", palet_profile(), n=5.0); ob.data.materials.append(M("milk", MILK, 0.26, None, 2))
        if "saltm" not in MATS:
            sm, snt, sp = mat("saltm"); sp.inputs["Base Color"].default_value = (0.9, 0.9, 0.88, 1); sp.inputs["Roughness"].default_value = 0.25
            sp.inputs["Transmission Weight"].default_value = 0.5; MATS["saltm"] = sm
        salt((x, y), z + 0.0125, rng, MATS["saltm"])
    elif kind == "white":
        ob = loft("white", ridged_profile()); ob.data.materials.append(M("white", WHITE, 0.30, None, 4))
    elif kind == "milkridge":
        ob = loft("milkr", ridged_profile()); ob.data.materials.append(M("milk", MILK, 0.26, None, 2))
    elif kind == "plain":
        ob = loft("plain", palet_profile(), n=5.0); ob.data.materials.append(M("dark", DARK, 0.20, None, 7))
    elif kind == "milkdome":
        ob = loft("milkd", dome_profile(0.0145, 0.0160, 0.66)); ob.data.materials.append(M("milk", MILK, 0.26, None, 2))
    elif kind == "truffle":
        if "cocoa" not in MATS:
            cm, cnt, cp = mat("cocoa"); cp.inputs["Base Color"].default_value = (0.060, 0.026, 0.013, 1); cp.inputs["Roughness"].default_value = 0.95
            cp.inputs["Specular IOR Level"].default_value = 0.1; cp.inputs["Sheen Weight"].default_value = 0.6
            nzz = cnt.nodes.new("ShaderNodeTexNoise"); nzz.inputs["Scale"].default_value = 1800; nzz.inputs["Detail"].default_value = 4
            bb = cnt.nodes.new("ShaderNodeBump"); bb.inputs["Strength"].default_value = 0.5; bb.inputs["Distance"].default_value = 0.0003
            cnt.links.new(nzz.outputs["Fac"], bb.inputs["Height"]); cnt.links.new(bb.outputs["Normal"], cp.inputs["Normal"])
            MATS["cocoa"] = cm
        ob = truffle("truffle", MATS["cocoa"], seed)
    ob.location = (x, y, z); ob.rotation_euler = (0, 0, math.radians(rot))
    return ob


def card_material():
    m, nt, p = mat("card")
    p.inputs["Base Color"].default_value = (*CREAM, 1); p.inputs["Roughness"].default_value = 0.8
    p.inputs["Specular IOR Level"].default_value = 0.2
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 4
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.08; b.inputs["Distance"].default_value = 0.0002
    nt.links.new(nz.outputs["Fac"], b.inputs["Height"]); nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def tray(centre, rot_deg, cell=0.0375, hgt=0.019, t=0.0016):
    """An open card box, three by three."""
    m = card_material()
    root = bpy.data.objects.new("tray", None); bpy.context.scene.collection.objects.link(root)
    inner = cell * 3 + t * 2
    parts = [box("base", (inner + 2 * t, inner + 2 * t, t), (0, 0, t / 2), m)]
    for s in (-1, 1):
        parts.append(box("wx", (t, inner + 2 * t, hgt), (s * (inner / 2 + t / 2), 0, hgt / 2), m))
        parts.append(box("wy", (inner, t, hgt), (0, s * (inner / 2 + t / 2), hgt / 2), m))
        parts.append(box("dx", (t, inner, hgt - 0.004), (s * (cell / 2 + t / 2), 0, (hgt - 0.004) / 2), m))
        parts.append(box("dy", (inner, t, hgt - 0.0043), (0, s * (cell / 2 + t / 2), (hgt - 0.0043) / 2), m))
    for o in parts:
        o.parent = root
    root.location = (centre[0], centre[1], 0); root.rotation_euler = (0, 0, math.radians(rot_deg))
    cells = {}
    c, s_ = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            lx, ly = i * (cell + t), j * (cell + t)
            cells[(i, j)] = (centre[0] + lx * c - ly * s_, centre[1] + lx * s_ + ly * c, t)
    return cells


SHOTS = {
    1: dict(target=(0.0, 0.02, 0.012), dist=0.33, az=24, el=12, lens=85, f=9, focus=(0.030, -0.040, 0.012), shift=(0.03, 0.11),
            key=((-0.62, 0.05, 0.17), 0.40, 36)),
    2: dict(target=(0.0, 0.0, 0.01), dist=0.43, az=24, el=52, lens=85, f=13, focus=(0.0, 0.0, 0.016), shift=(-0.055, 0.335),
            key=((-0.55, 0.10, 0.42), 0.45, 23)),
    3: dict(target=(0.030, -0.045, 0.011), dist=0.150, az=24, el=15, lens=100, f=11, focus=(0.034, -0.056, 0.012), shift=(-0.13, -0.274),
            key=((-0.62, 0.05, 0.17), 0.40, 36)),
}

LINE = [("ruby", (0.030, -0.045), 0, 1), ("gold", (-0.012, -0.010), 24, 2), ("stripe", (0.052, 0.012), 200, 3),
        ("salt", (-0.050, 0.030), -18, 4), ("white", (0.012, 0.050), 0, 5), ("truffle", (-0.022, 0.088), 0, 6),
        ("plain", (0.062, 0.095), 38, 7), ("milkdome", (-0.085, 0.120), 0, 8), ("milkridge", (0.020, 0.150), 0, 9),
        ("stripe", (-0.045, 0.195), 120, 10), ("gold", (0.085, 0.215), -30, 11)]

BOX = {(-1, 1): "stripe", (0, 1): "salt", (1, 1): "white",
       (-1, 0): "gold", (0, 0): "ruby", (1, 0): "truffle",
       (-1, -1): "milkridge", (0, -1): "plain", (1, -1): "milkdome"}


def build(frame, quality):
    shot = SHOTS[frame]
    MATS.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 128 if final else 24
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
    bg.inputs["Color"].default_value = (0.20, 0.42, 0.40, 1)
    bg.inputs["Strength"].default_value = 0.06

    prof = [(-4.0, 0.0), (0.45, 0.0)]
    R = 0.45
    for j in range(1, 25):
        a = math.pi / 2 * j / 24
        prof.append((0.45 + R * math.sin(a), R * (1 - math.cos(a))))
    prof.append((0.90, 4.0))
    verts = [(x, y, z) for (y, z) in prof for x in (-6.0, 6.0)]
    faces = [(2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2) for j in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    sweep = bpy.data.objects.new("sweep", me); sc.collection.objects.link(sweep)
    sm, snt, sp = mat("sweep")
    sp.inputs["Base Color"].default_value = (*SWEEP, 1)
    sp.inputs["Roughness"].default_value = 0.72
    sp.inputs["Specular IOR Level"].default_value = 0.25
    nz = snt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 700; nz.inputs["Detail"].default_value = 3
    bump = snt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.04; bump.inputs["Distance"].default_value = 0.0002
    snt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); snt.links.new(bump.outputs["Normal"], sp.inputs["Normal"])
    me.materials.append(sm)

    if frame == 2:
        cells = tray((0.0, 0.0), -9)
        for k, kind in BOX.items():
            piece(kind, cells[k], rot={"gold": 14, "plain": -4, "salt": 3, "stripe": 150}.get(kind, 0), seed=hash(k) % 50)
    else:
        for kind, loc, rot, seed in LINE:
            piece(kind, loc, rot, seed)

    kl, ks, ke = shot["key"]
    area("key", kl, (0, 0.02, 0.01), ks, ke, (1.0, 0.97, 0.93))
    area("rim", (0.45, 0.50, 0.30), (0, 0.03, 0.02), 0.20, 7, (0.92, 0.97, 1.0), size_y=0.7)
    area("fill", (0.45, -0.55, 0.25), (0, 0, 0.02), 0.9, 3.0, (0.95, 0.98, 1.0))
    # a window that only the shine sees: a tall card, split by one glazing bar
    for i, (dx, wdt) in enumerate(((-0.085, 0.15), (0.095, 0.17))):
        cmh = bpy.data.meshes.new("card"); cmh.from_pydata([(0, -wdt / 2, 0), (0, wdt / 2, 0), (0, wdt / 2, 0.55), (0, -wdt / 2, 0.55)], [], [(0, 1, 2, 3)])
        cd = bpy.data.objects.new("card", cmh); sc.collection.objects.link(cd)
        cd.rotation_euler = (0, math.radians(-18), math.radians(40))
        cd.location = (-0.36 + dx * math.sin(math.radians(40)) * -1, -0.22 + dx * math.cos(math.radians(40)), 0.02)
        em, ent, ep = mat("cardm"); ep.inputs["Emission Color"].default_value = (1, 0.98, 0.95, 1); ep.inputs["Emission Strength"].default_value = 2.2
        ep.inputs["Base Color"].default_value = (0, 0, 0, 1); cmh.materials.append(em)
        cd.visible_camera = False; cd.visible_diffuse = False; cd.visible_shadow = False; cd.visible_transmission = False

    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 36
    az, el = math.radians(shot["az"]), math.radians(shot["el"])
    tg = Vector(shot["target"])
    co.location = tg + shot["dist"] * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    look(co, tg)
    cam.lens = shot["lens"]
    cam.shift_x, cam.shift_y = shot["shift"]
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"]
    cam.clip_start = 0.01

    exr = str(TMP / f"nx-choc-{frame}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def pixels(exr):
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32), w, h


EXPOSURE = 0.60


def grade(exr, frame, quality):
    """A film curve, the top of the frame falling off (Instagram's white name sits there), and grain."""
    from PIL import Image
    a, w, h = pixels(exr)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    a = np.clip(a, 0, None)
    x = a * EXPOSURE * {2: 0.86}.get(frame, 1.0)   # frame 2 is lit from higher up; bring its sweep to the same duck egg
    x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    yy, xx = np.mgrid[0:H, 0:W]
    top = np.clip(1 - yy / 330.0, 0, 1) ** 1.6
    x *= (1 - 0.40 * top)[..., None]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.10 * np.clip(r - 0.6, 0, 1) ** 1.5)[..., None]
    rng = np.random.default_rng(frame)
    x += rng.normal(0, 0.007, (H, W, 1)).astype(np.float32)
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
        exr = str(TMP / f"nx-choc-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
