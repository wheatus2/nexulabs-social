"""Renders the pictures for this Reel with Blender's Python module (pip install bpy brotli).

One made-up "Christmas opening hours" door calendar (print: art/prints.py) lying on a crimson table, shot from the
same side. It is a shallow card box: a printed front sheet with eight doors (24 to 31 December 2026), a well behind
each door that opens, and the hours printed at the bottom of the well.

  python3 build.py <shot> [draft|final] [regrade]        shot = a name in SHOTS, or "all"
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
TABLE = lin("#A3182B")
EXPOSURE = 0.88

# the card. Origin: the middle of door 25. x to the right, y up the sheet, z towards the reader.
D, G, HEAD = 7.0, 1.5, 7.5
X0, X1 = -(D / 2 + G + D + G), D / 2 + G + 2 * (D + G)          # -13.5 .. 22.0
Y0, Y1 = -(D / 2 + G + D + G), D / 2 + G                         # -13.5 .. 5.0 (no header)
DEPTH = 0.55                                                      # how deep the box is
def door_xy(n):                                                   # centre of door n (24..31)
    i = n - 24
    return ((i % 4) - 1) * (D + G), -(i // 4) * (D + G)
def uv(x, y):
    return ((x - X0) / (X1 - X0), (y - Y0) / (Y1 - Y0))

# doors: angle in degrees (0 shut). Camera and light per shot.
A = 76
SHOTS = {
    "1a": dict(cam="one", doors={}),
    "1b": dict(cam="one", doors={25: 14}),
    "1c": dict(cam="one", doors={25: 48}),
    "1d": dict(cam="one", doors={25: 88}),
    "1e": dict(cam="one", doors={25: A}),
    "2a": dict(cam="two", doors={25: A}),
    "2b": dict(cam="two", doors={25: A, 24: 16}),
    "2c": dict(cam="two", doors={25: A, 24: 52}),
    "2d": dict(cam="two", doors={25: A, 24: 92}),
    "2e": dict(cam="two", doors={25: A, 24: A + 3}),
    "3": dict(cam="three", doors={25: A, 24: A + 3}),
    "4": dict(cam="four", doors={25: A, 24: A + 3, 26: A - 4}),
}
CAMS = {
    "one": dict(loc=(13.0, -31.0, 37.0), aim=(0.5, -3.0, 0.0), lens=50, f=0.16, focus=(0, 0, 0.5), shift=(0.0, 0.20), yaw=-12),
    "two": dict(loc=(11.0, -30.0, 23.0), aim=(-4.0, -1.5, 0.5), lens=55, f=0.07, focus=(-6, 0, 0.5), shift=(0.0, 0.24), yaw=-12),
    "three": dict(loc=(2.76, -12.5, 35.6), aim=(0.6, -0.4, 0.0), lens=72, f=0.30, focus=(0.3, 0.0, 0.0), shift=(0.0, 0.255), yaw=-12),
    "four": dict(loc=(12.1, -33.0, 42.0), aim=(0.45, -1.0, 0.0), lens=47.5, f=0.16, focus=(0, 0, 0.3), shift=(0.0, 0.21), yaw=-12),
}
SAMPLES = {"1b": 24, "1c": 24, "1d": 24, "2b": 24, "2c": 24, "2d": 24}


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


def calendar(doors):
    """doors: {number: angle}. Returns the root empty."""
    root = bpy.data.objects.new("calendar", None); bpy.context.scene.collection.objects.link(root)
    front = card_mat("front", HERE / "front.png", perf=HERE / "perf.png")
    door_m = card_mat("door", HERE / "front.png")
    board = card_mat("board", tint=(0.76, 0.72, 0.62), rough=0.8)
    T = 0.07                                                      # the front sheet is this thick
    holes = {n: door_xy(n) for n in doors}
    # front sheet: a grid cut at every hole edge, with the holes left out
    xs = sorted({X0, X1, *[c[0] + s * D / 2 for c in holes.values() for s in (-1, 1)]})
    ys = sorted({Y0, Y1, *[c[1] + s * D / 2 for c in holes.values() for s in (-1, 1)]})
    verts, faces, uvs = [], [], []
    def quad(pts, tex=True):
        k = len(verts); verts.extend(pts); uvs.extend([uv(p[0], p[1]) if tex else (0.02, 0.98) for p in pts]); faces.append((k, k + 1, k + 2, k + 3))
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            if any(abs(cx - hx) < D / 2 and abs(cy - hy) < D / 2 for hx, hy in holes.values()):
                continue
            quad([(xs[i], ys[j], DEPTH), (xs[i + 1], ys[j], DEPTH), (xs[i + 1], ys[j + 1], DEPTH), (xs[i], ys[j + 1], DEPTH)])
    mesh("front", verts, faces, uvs, front, root)
    # the box: sides, and the cut edge of the sheet round each hole, then the well under it
    verts, faces, uvs = [], [], []
    for (ax, ay), (bx, by) in (((X0, Y0), (X1, Y0)), ((X1, Y0), (X1, Y1)), ((X1, Y1), (X0, Y1)), ((X0, Y1), (X0, Y0))):
        quad([(ax, ay, 0), (bx, by, 0), (bx, by, DEPTH), (ax, ay, DEPTH)], False)
    for hx, hy in holes.values():
        a, b, c, d = (hx - D / 2, hy - D / 2), (hx + D / 2, hy - D / 2), (hx + D / 2, hy + D / 2), (hx - D / 2, hy + D / 2)
        for (px, py), (qx, qy) in ((b, a), (c, b), (d, c), (a, d)):
            quad([(px, py, 0.02), (qx, qy, 0.02), (qx, qy, DEPTH), (px, py, DEPTH)], False)
    mesh("box", verts, faces, uvs, board, root)
    for n, ang in doors.items():
        hx, hy = holes[n]
        ins = card_mat(f"in{n}", HERE / f"in-{n}.png", rough=0.7)
        mesh(f"well{n}", [(hx - D / 2, hy - D / 2, 0.02), (hx + D / 2, hy - D / 2, 0.02), (hx + D / 2, hy + D / 2, 0.02), (hx - D / 2, hy + D / 2, 0.02)],
             [(0, 1, 2, 3)], [(0, 0), (1, 0), (1, 1), (0, 1)], ins, root)
        # the door: hinged on its left edge, with a soft crease at the hinge and a slight curl
        nu, nv = 24, 2
        verts, faces, uvs = [], [], []
        th = math.radians(ang)
        open_ = min(1.0, ang / 60)
        x, z = hx - D / 2, DEPTH + 0.005
        prof = [(x, z)]
        for i in range(nu):
            s = (i + 0.5) / nu
            a = th * min(1.0, (s * nu + 0.5) / 2.0) + open_ * math.radians(13) * (s - 0.35)      # crease over the first 2 segments, then a curl
            x += (D - 0.04) / nu * math.cos(a); z += (D - 0.04) / nu * math.sin(a)
            prof.append((x, z))
        for j in range(nv + 1):
            for i in range(nu + 1):
                y = hy - D / 2 + 0.02 + (D - 0.04) * j / nv
                verts.append((prof[i][0], y, prof[i][1])); uvs.append(uv(hx - D / 2 + D * i / nu, y))
        for j in range(nv):
            for i in range(nu):
                k = j * (nu + 1) + i
                faces.append((k, k + 1, k + nu + 2, k + nu + 1))
        ob = mesh(f"door{n}", verts, faces, uvs, door_m, root, smooth=True)
        ob.data.materials.append(board)
        so = ob.modifiers.new("t", "SOLIDIFY"); so.thickness = T * 0.8; so.offset = -1; so.material_offset = 1; so.material_offset_rim = 1
    return root


def build(name, quality, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = SAMPLES.get(name, 64) if final else 24
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
    bg.inputs["Color"].default_value = (1.0, 0.96, 0.9, 1); bg.inputs["Strength"].default_value = 0.14

    shot = SHOTS[name]; cm = CAMS[shot["cam"]]
    root = calendar(shot["doors"])
    root.rotation_euler.z = math.radians(cm["yaw"])

    me = bpy.data.meshes.new("table"); s = 3000
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    tb = bpy.data.objects.new("table", me); sc.collection.objects.link(tb); tb.location.z = -0.001
    tb.data.materials.append(table_mat())

    # key: a small window low, far off to the right and behind, raking across the sheet
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 110; key.size_y = 150
    key.energy = 52000 * 7.5 * 9 * 1.5; key.color = (1.0, 0.955, 0.90)
    ko = bpy.data.objects.new("key", key); sc.collection.objects.link(ko)
    ko.location = (520, 330, 300); aim(ko, (0, 0, 0))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 360; fl.energy = 5200 * 6 * 9 * 0.9; fl.color = (0.97, 0.98, 1.0)
    fo = bpy.data.objects.new("fill", fl); sc.collection.objects.link(fo)
    fo.location = (-200, -430, 240); aim(fo, (0, 0, 0))

    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 36
    co.location = cm["loc"]; aim(co, cm["aim"])
    cam.lens = cm["lens"]
    cam.shift_x, cam.shift_y = cm["shift"]
    cam.clip_start = 0.1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(cm["focus"]) - co.location).length
    cam.dof.aperture_fstop = cm["f"]
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region

    exr = str(TMP / f"nx-cal-{name}.exr")
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
    for nm in (list(SHOTS) if which == "all" else which.split(",")):
        exr = str(TMP / f"nx-cal-{nm}.exr")
        grade(exr if "regrade" in args else build(nm, quality), nm, quality)
