"""Renders the pictures for this Reel with Blender's Python module (pip install bpy brotli).

A printed homepage design for a made-up joinery firm (art/prints.py) lying on a charcoal table, with a blue swing
tag on it: Homepage concept. Yours. Free when you book a call. Shot from the same side four ways.

  python3 build.py <shot> [draft|final] [regrade]        shot = one, two, three, four (comma separated) or all
writes art/r-<shot>.jpg (1134x2016, shown at 1080x1920 in reel.html). Units are centimetres.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1134, 2016
TMP = Path(tempfile.gettempdir())
lin = lambda h: tuple(((int(h[i:i + 2], 16) / 255 + 0.055) / 1.055) ** 2.4 if int(h[i:i + 2], 16) / 255 > 0.04045 else int(h[i:i + 2], 16) / 255 / 12.92 for i in (1, 3, 5))
TABLE = lin("#2A2C33")
EXPOSURE = 1.08
SW, SH = 30.0, 42.0            # the proof
TW, TH = 6.0, 12.0             # the tag
TAG_AT, TAG_ROT = (9.0, 14.3), 14.0

CAMS = {
    "one": dict(loc=(-5.0, -62.0, 44.0), aim=(0.0, -1.0, 0.0), lens=55, f=0.22, focus=(2.0, 6.0, 0.3), shift=(0.0, 0.13)),
    "two": dict(loc=(-11.0, -21.0, 25.0), aim=(-2.1, 8.5, 0.0), lens=32.5, f=0.08, focus=(-5.0, 8.5, 0.2), shift=(0.0, 0.16)),
    "three": dict(loc=(5.0, -8.4, 24.6), aim=(10.0, 14.7, 0.0), lens=47, f=0.14, focus=(9.0, 13.5, 0.3), shift=(0.0, 0.115)),
    "four": dict(loc=(12.5, -3.0, 36.0), aim=(9.3, 14.3, 0.0), lens=53, f=0.2, focus=(9.0, 14.3, 0.3), shift=(0.0, 0.16)),
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


def mesh(name, verts, faces, uvs, material, parent=None, smooth=False):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    if uvs:
        layer = me.uv_layers.new(name="uv")
        for lp in me.loops:
            layer.data[lp.index].uv = uvs[lp.vertex_index]
    for p in me.polygons:
        p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(material)
    if parent:
        ob.parent = parent
    return ob


def card_mat(name, img=None, tint=(0.8, 0.78, 0.72), back=None, perf=None, rough=0.62):
    """Printed card. Front: the print. Back (if given): plain board."""
    m, nt, p = mat(name)
    N, L = nt.nodes, nt.links
    geo = N.new("ShaderNodeNewGeometry")
    if img:
        tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(img)); tex.interpolation = "Cubic"
        tex.extension = "EXTEND"
        if back is not None:
            mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
            L.new(geo.outputs["Backfacing"], mix.inputs["Factor"])
            L.new(tex.outputs["Color"], mix.inputs["A"]); mix.inputs["B"].default_value = (*back, 1)
            L.new(mix.outputs["Result"], p.inputs["Base Color"])
        else:
            L.new(tex.outputs["Color"], p.inputs["Base Color"])
    else:
        p.inputs["Base Color"].default_value = (*tint, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = 0.35
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 90; nz.inputs["Detail"].default_value = 6
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"])
    if perf:
        pt = N.new("ShaderNodeTexImage"); pt.image = bpy.data.images.load(str(perf)); pt.image.colorspace_settings.name = "Non-Color"
        b2 = N.new("ShaderNodeBump"); b2.inputs["Strength"].default_value = 0.9; b2.inputs["Distance"].default_value = 0.03
        L.new(pt.outputs["Color"], b2.inputs["Height"]); L.new(bump.outputs["Normal"], b2.inputs["Normal"])
        L.new(b2.outputs["Normal"], p.inputs["Normal"])
    else:
        L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def table_mat():
    m, nt, p = mat("table")
    N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.95
    p.inputs["Specular IOR Level"].default_value = 0.12
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.2; nz.inputs["Detail"].default_value = 3
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.94; mr.inputs["To Max"].default_value = 1.04
    L.new(nz.outputs["Fac"], mr.inputs["Value"])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1
    mix.inputs["A"].default_value = (*TABLE, 1)
    comb = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(mr.outputs["Result"], comb.inputs[k])
    L.new(comb.outputs["Color"], mix.inputs["B"]); L.new(mix.outputs["Result"], p.inputs["Base Color"])
    fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 60; fine.inputs["Detail"].default_value = 8
    L.new(geo.outputs["Position"], fine.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.10; bump.inputs["Distance"].default_value = 0.03
    L.new(fine.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m



def sheet_z(x, y):
    """The proof is not dead flat: a long soft wave, and the far right corner lifts."""
    c = max(0.0, (x / 15 + y / 21 - 1.15)) ** 2 * 5.0
    return 0.03 + 0.20 * (1 + math.sin(x * 0.16 + y * 0.07)) + 0.06 * (1 + math.sin(y * 0.33 - x * 0.1)) + c


def grid(name, fn, nu, nv, material):
    verts, uvs, faces = [], [], []
    for j in range(nv + 1):
        for i in range(nu + 1):
            p, t = fn(i / nu, j / nv); verts.append(p); uvs.append(t)
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            faces.append((a, a + 1, a + nu + 2, a + nu + 1))
    return mesh(name, verts, faces, uvs, material, smooth=True)


def tag_point(u, v):
    """u across, v up the tag (0 at the foot, 1 at the hole end). It rests on the proof and curls up a little at the foot."""
    lx, ly = (u - 0.5) * TW, (v - 0.5) * TH
    a = math.radians(TAG_ROT)
    x = TAG_AT[0] + lx * math.cos(a) - ly * math.sin(a); y = TAG_AT[1] + lx * math.sin(a) + ly * math.cos(a)
    lift = 0.10 + 0.9 * max(0.0, 0.42 - v) ** 2 + 0.25 * max(0.0, v - 0.8) ** 2 + 0.05 * (u - 0.5)
    return x, y, sheet_z(x, y) + lift


def build_scene():
    paper = card_mat("proof", HERE / "proof.png", rough=0.55)
    grid("proof", lambda u, v: (((u - .5) * SW, (v - .5) * SH, sheet_z((u - .5) * SW, (v - .5) * SH)), (u, v)), 60, 84, paper)
    # tag: print with the hole in its alpha
    m, nt, p = mat("tag")
    N, L = nt.nodes, nt.links
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / "tag.png")); tex.interpolation = "Cubic"; tex.extension = "CLIP"
    L.new(tex.outputs["Color"], p.inputs["Base Color"]); L.new(tex.outputs["Alpha"], p.inputs["Alpha"])
    p.inputs["Roughness"].default_value = 0.42; p.inputs["Specular IOR Level"].default_value = 0.45
    geo = N.new("ShaderNodeNewGeometry"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 70; nz.inputs["Detail"].default_value = 6
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    grid("tag", lambda u, v: (tag_point(u, v), (u, v)), 12, 40, m)
    # a second, white layer just under it: the board the tag is printed on shows at the edges
    under, nt2, p2 = mat("tagboard")
    t2 = nt2.nodes.new("ShaderNodeTexImage"); t2.image = tex.image; t2.extension = "CLIP"
    nt2.links.new(t2.outputs["Alpha"], p2.inputs["Alpha"]); p2.inputs["Base Color"].default_value = (0.86, 0.85, 0.82, 1); p2.inputs["Roughness"].default_value = 0.8
    for k in (1, 2, 3):
        grid(f"tagboard{k}", lambda u, v, k=k: ((lambda q: (q[0], q[1], q[2] - 0.018 * k))(tag_point(u, v)), (u, v)), 12, 40, under)
    # brass eyelet
    hx, hy, hz = tag_point(0.5, 0.9)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.075, major_segments=64, minor_segments=16, location=(hx, hy, hz + 0.02))
    ey = bpy.context.object; bpy.ops.object.shade_smooth()
    em, _, ep = mat("eyelet"); ep.inputs["Base Color"].default_value = (0.78, 0.74, 0.66, 1); ep.inputs["Metallic"].default_value = 1; ep.inputs["Roughness"].default_value = 0.32
    ey.data.materials.append(em)
    # the string: up through the eyelet, a loop, then away across the proof and off onto the table
    def on(dx, dy, up):
        x, y = hx + dx, hy + dy
        base = sheet_z(x, y) if abs(x) <= SW / 2 and abs(y) <= SH / 2 else 0.0
        return (x, y, base + up)
    pts = [(hx - 0.25, hy - 0.2, hz - 0.3), (hx, hy, hz + 0.18), on(0.5, 0.9, 0.34), on(1.6, 2.4, 0.16), on(0.9, 4.6, 0.12), on(-1.2, 5.6, 0.12),
           on(-2.8, 4.2, 0.13), on(-1.6, 2.6, 0.26), on(1.4, 2.5, 0.34), on(4.2, 4.4, 0.14), on(6.4, 8.0, 0.11), on(9.5, 9.5, 0.11),
           on(13.0, 7.0, 0.11), on(17.0, 9.0, 0.11), on(22.0, 15.0, 0.11)]
    cu = bpy.data.curves.new("string", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.085; cu.bevel_resolution = 6; cu.resolution_u = 24
    sp = cu.splines.new("NURBS"); sp.points.add(len(pts) - 1)
    for q, c in zip(sp.points, pts):
        q.co = (*c, 1)
    sp.use_endpoint_u = True; sp.order_u = 4
    so = bpy.data.objects.new("string", cu); bpy.context.scene.collection.objects.link(so)
    sm, snt, spb = mat("cotton"); spb.inputs["Base Color"].default_value = (0.84, 0.82, 0.76, 1); spb.inputs["Roughness"].default_value = 0.9
    w = snt.nodes.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value = 14; w.inputs["Distortion"].default_value = 1.5
    sb = snt.nodes.new("ShaderNodeBump"); sb.inputs["Strength"].default_value = 0.6; sb.inputs["Distance"].default_value = 0.03
    snt.links.new(w.outputs["Fac"], sb.inputs["Height"]); snt.links.new(sb.outputs["Normal"], spb.inputs["Normal"])
    so.data.materials.append(sm)


def build(name, quality, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 72 if final else 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 36
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"
    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.9, 0.94, 1.0, 1); bg.inputs["Strength"].default_value = 0.10
    cm = CAMS[name]
    build_scene()
    me = bpy.data.meshes.new("table"); s = 3000
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    tb = bpy.data.objects.new("table", me); sc.collection.objects.link(tb); tb.location.z = -0.001
    tb.data.materials.append(table_mat())
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 120; key.size_y = 160
    key.energy = 52000 * 7.5 * 9 * 1.25; key.color = (1.0, 0.96, 0.91)
    ko = bpy.data.objects.new("key", key); sc.collection.objects.link(ko)
    ko.location = (480, 380, 300); aim(ko, (0, 0, 0))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 360; fl.energy = 5200 * 6 * 9 * 0.7; fl.color = (0.95, 0.97, 1.0)
    fo = bpy.data.objects.new("fill", fl); sc.collection.objects.link(fo)
    fo.location = (-200, -430, 240); aim(fo, (0, 0, 0))
    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 36
    co.location = cm["loc"]; aim(co, cm["aim"])
    cam.lens = cm["lens"]; cam.shift_x, cam.shift_y = cm["shift"]; cam.clip_start = 0.1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(cm["focus"]) - co.location).length
    cam.dof.aperture_fstop = cm["f"]
    exr = str(TMP / f"nx-tag-{name}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def grade(exr, name, quality):
    from PIL import Image
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    x = np.clip(a, 0, None) * EXPOSURE
    x = np.where(x > 0.6, 0.6 + (1 - np.exp(-(x - 0.6) / 0.42)) * 0.4, x)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(7)
    x += rng.normal(0, 0.007, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"r-{name}.jpg" if quality == "final" else f".draft-{name}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst)


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 else "draft"
    for nm in (list(CAMS) if which == "all" else which.split(",")):
        exr = str(TMP / f"nx-tag-{nm}.exr")
        grade(exr if "regrade" in args else build(nm, quality), nm, quality)
