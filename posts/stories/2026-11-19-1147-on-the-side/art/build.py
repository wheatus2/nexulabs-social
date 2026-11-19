"""Renders the pictures for this Story with Blender's Python module (pip install bpy uharfbuzz; run with python3.13).

One felt letter board, the kind a cafe writes its menu on: plum felt in slats, push-in plastic letters, an oak frame,
standing on a pale pink counter. Shot from the same side three ways, and the words change each time:
  1  low and close from the left: ON THE MENU / YOUR / NEW / WEBSITE
  2  square on, the felt filling the frame: SIDES / HOSTING / DOMAINS / EMAIL / SAME KITCHEN
  3  the foot of the board and the counter: TO ORDER / BOOK / A CALL

  python3.13 build.py <1|2|3|all> [draft|final|probe] [regrade]
writes art/render-0N.jpg (1080x1920). Units are centimetres. Only the last line of frame 3 is HTML.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())
EXPOSURE = 1.0
P = 0.635                      # slat pitch, a quarter inch
NS = 92
BW, BH = 38.0, NS * P          # felt area
Z0 = 2.0                       # foot of the felt (the bottom rail is under it)
FACE = -1.3                    # y of the felt's front (the wall is y = 0)
EXT = 0.11                     # half thickness of a letter
PLUM = (0.062, 0.011, 0.070)
PINK = (0.88, 0.40, 0.50)
IVORY = (0.84, 0.81, 0.73)
COUNTER = (0.80, 0.55, 0.58)
TRACK = 0.045                  # em
XL = -10.4                     # left edge of every line

BIG, SMALL = None, None        # em sizes, set in sizes()

BOARDS = {
    1: [("s", "ON THE MENU", 51), ("b", "YOUR", 42), ("b", "NEW", 33), ("b", "WEBSITE", 24)],
    2: [("s", "SIDES", 51), ("b", "HOSTING", 42), ("b", "DOMAINS", 33), ("b", "EMAIL", 24), ("s", "SAME KITCHEN", 19)],
    3: [("s", "TO ORDER", 31), ("b", "BOOK", 22), ("b", "A CALL", 13), ("s", "AT NEXULABS.CO.UK", 8)],
}   # kind, words, the slat its baseline sits on

SHOTS = {
    1: dict(loc=(-38, -44, 12), aim=(-0.6, FACE, 29.0), lens=50, f=5.6, focus=(-6, FACE, 24), shift=(0, -0.045)),
    2: dict(loc=(-30, -70, 22), aim=(-0.3, FACE, 27.5), lens=55, f=8, focus=(-4, FACE, 27), shift=(0, -0.052)),
    3: dict(loc=(-34, -56, 3.2), aim=(-0.5, FACE, 13.0), lens=50, f=8, focus=(-5, FACE, 10), shift=(0, -0.031)),
}


def ttf():
    out = TMP / "nx-oswald-700.ttf"
    if not out.exists():
        from fontTools.ttLib import TTFont
        f = TTFont(str(ROOT / "fonts" / "oswald-latin-700-normal.woff2")); f.flavor = None; f.save(str(out))
    return str(out)


def shape(text):
    """Pen positions (in em) for each glyph, with the font's own kerning, plus tracking."""
    import uharfbuzz as hb
    blob = hb.Blob.from_file_path(ttf()); face = hb.Face(blob); font = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True})
    x, out = 0.0, []
    for ch, pos in zip(text, buf.glyph_positions):
        out.append((ch, x / face.upem)); x += pos.x_advance * (0.62 if ch == ' ' else 1.0) + TRACK * face.upem
    return out, (x - TRACK * face.upem) / face.upem


def metrics():
    from fontTools.ttLib import TTFont
    f = TTFont(ttf()); gs = f.getGlyphSet(); cm = f.getBestCmap(); up = f["head"].unitsPerEm
    from fontTools.pens.boundsPen import BoundsPen
    def b(ch):
        bp = BoundsPen(gs); gs[cm[ord(ch)]].draw(bp); return [v / up for v in bp.bounds]
    return b


def sizes():
    global BIG, SMALL
    b = metrics()
    cap = b("H")[3]
    BIG = 5.5 * P / cap * 1.0          # caps five and a half slats tall
    # the widest big word must fit 20.8 cm
    widest = max(shape(w)[1] for k, w, _ in sum(BOARDS.values(), []) if k == "b")
    BIG = min(BIG * 1.6, 20.8 / widest)
    BIG = math.floor(BIG * cap / P * 2) / 2 * P / cap      # cap height a whole number of half slats
    SMALL = 2.5 * P / cap
    return cap


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


def plain(name, col, rough, coat=0.0, spec=0.5):
    m, nt, p = mat(name)
    p.inputs["Base Color"].default_value = (*col, 1); p.inputs["Roughness"].default_value = rough
    p.inputs["Coat Weight"].default_value = coat; p.inputs["Specular IOR Level"].default_value = spec
    return m


def felt_mat():
    m, nt, p = mat("felt")
    N, L = nt.nodes, nt.links
    geo = N.new("ShaderNodeNewGeometry")
    fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 38.0; fine.inputs["Detail"].default_value = 6; fine.inputs["Roughness"].default_value = 0.7
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 1.0, 3.0)
    L.new(geo.outputs["Position"], mp.inputs["Vector"]); L.new(mp.outputs["Vector"], fine.inputs["Vector"])
    slow = N.new("ShaderNodeTexNoise"); slow.inputs["Scale"].default_value = 0.9; slow.inputs["Detail"].default_value = 3
    L.new(geo.outputs["Position"], slow.inputs["Vector"])
    ramp = N.new("ShaderNodeMixRGB"); ramp.blend_type = "MIX"
    ramp.inputs["Color1"].default_value = (PLUM[0] * 0.72, PLUM[1] * 0.72, PLUM[2] * 0.72, 1)
    ramp.inputs["Color2"].default_value = (PLUM[0] * 1.45, PLUM[1] * 1.5, PLUM[2] * 1.45, 1)
    mix = N.new("ShaderNodeMath"); mix.operation = "MULTIPLY_ADD"; mix.inputs[1].default_value = 0.75; mix.inputs[2].default_value = 0.12
    L.new(fine.outputs["Fac"], mix.inputs[0])
    add = N.new("ShaderNodeMath"); add.operation = "MULTIPLY_ADD"; add.inputs[1].default_value = 0.25; add.use_clamp = True
    L.new(slow.outputs["Fac"], add.inputs[0]); L.new(mix.outputs["Value"], add.inputs[2])
    L.new(add.outputs["Value"], ramp.inputs["Fac"]); L.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 1.0; p.inputs["Specular IOR Level"].default_value = 0.1
    p.inputs["Sheen Weight"].default_value = 0.9; p.inputs["Sheen Roughness"].default_value = 0.55
    p.inputs["Sheen Tint"].default_value = (0.75, 0.45, 0.80, 1)
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.55; bump.inputs["Distance"].default_value = 0.03
    L.new(fine.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def oak_mat():
    m, nt, p = mat("oak")
    N, L = nt.nodes, nt.links
    geo = N.new("ShaderNodeNewGeometry")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.35, 9.0, 9.0)
    L.new(geo.outputs["Position"], mp.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 7; nz.inputs["Roughness"].default_value = 0.68
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    ramp = N.new("ShaderNodeMixRGB")
    ramp.inputs["Color1"].default_value = (0.33, 0.235, 0.135, 1); ramp.inputs["Color2"].default_value = (0.58, 0.46, 0.30, 1)
    L.new(nz.outputs["Fac"], ramp.inputs["Fac"]); L.new(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.52; p.inputs["Specular IOR Level"].default_value = 0.35
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.18; bump.inputs["Distance"].default_value = 0.02
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def plaster(name, col):
    m, nt, p = mat(name)
    N, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (*col, 1); p.inputs["Roughness"].default_value = 0.62; p.inputs["Specular IOR Level"].default_value = 0.3
    geo = N.new("ShaderNodeNewGeometry")
    a = N.new("ShaderNodeTexNoise"); a.inputs["Scale"].default_value = 6.0; a.inputs["Detail"].default_value = 5
    L.new(geo.outputs["Position"], a.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.10; bump.inputs["Distance"].default_value = 0.02
    L.new(a.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def letter(ch, size, material, loc, rot):
    cu = bpy.data.curves.new("g", "FONT"); cu.body = ch; cu.font = letter.font; cu.size = size * 1.352        # Blender draws this font at 0.74 of its em
    cu.extrude = EXT; cu.bevel_depth = 0.022; cu.bevel_resolution = 2; cu.resolution_u = 10
    ob = link(bpy.data.objects.new("g", cu)); ob.data.materials.append(material)
    ob.location = loc; ob.rotation_euler = rot
    return ob


def line(text, size, material, slat):
    glyphs, width = shape(text)
    b = metrics()
    lsb = b(text[0])[0]                     # ink starts exactly on XL
    z = Z0 + slat * P
    for ch, x in glyphs:
        if ch != " ":
            letter(ch, size, material, (XL + (x - lsb) * size, FACE - EXT - 0.012, z), (math.pi / 2, 0, 0))
    return XL, XL + (width - lsb) * size, z, z + b("H")[3] * size


def scene(frame):
    wall = bpy.data.meshes.new("wall"); s = 900
    wall.from_pydata([(-s, 0, 0), (s, 0, 0), (s, 0, s), (-s, 0, s)], [], [(0, 1, 2, 3)])
    pm = plaster("counter", COUNTER)
    link(bpy.data.objects.new("wall", wall)).data.materials.append(pm)
    fl = bpy.data.meshes.new("counter")
    fl.from_pydata([(-s, -s, 0), (s, -s, 0), (s, 0, 0), (-s, 0, 0)], [], [(0, 1, 2, 3)])
    link(bpy.data.objects.new("counter", fl)).data.materials.append(pm)

    felt = felt_mat()
    for i in range(NS):
        z = Z0 + i * P
        box("slat", (-BW / 2, -0.5, z + 0.035), (BW / 2, FACE, z + P - 0.035), felt, bevel=0.13, seg=4)
    box("back", (-BW / 2, -0.3, Z0), (BW / 2, -0.75, Z0 + BH), plain("dark", (0.004, 0.002, 0.005), 1.0))
    oak = oak_mat()
    F, D = 2.0, -2.5
    for name, lo, hi in (("top", (-BW / 2 - F, D, Z0 + BH), (BW / 2 + F, 0, Z0 + BH + F)), ("bot", (-BW / 2 - F, D, 0), (BW / 2 + F, 0, Z0)),
                         ("l", (-BW / 2 - F, D, Z0), (-BW / 2, 0, Z0 + BH)), ("r", (BW / 2, D, Z0), (BW / 2 + F, 0, Z0 + BH))):
        box(name, lo, hi, oak, bevel=0.22, seg=4)

    letter.font = bpy.data.fonts.load(ttf())
    ivory = plain("ivory", IVORY, 0.38, coat=0.15)
    pink = plain("pink", PINK, 0.38, coat=0.15)
    out = {}
    if frame == 3:
        wm, nt, p = mat("mark"); N, L = nt.nodes, nt.links
        tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / ".wordmark.png")); tex.extension = "CLIP"
        mixc = N.new("ShaderNodeMixRGB"); mixc.inputs["Color1"].default_value = (0.47, 0.36, 0.22, 1); mixc.inputs["Color2"].default_value = (0.045, 0.012, 0.045, 1)
        L.new(tex.outputs["Alpha"], mixc.inputs["Fac"]); L.new(mixc.outputs["Color"], p.inputs["Base Color"]); L.new(tex.outputs["Alpha"], p.inputs["Alpha"])
        p.inputs["Roughness"].default_value = 0.5
        hgt = 1.05; wid = hgt * tex.image.size[0] / tex.image.size[1]; z0 = (Z0 - hgt) / 2
        me = bpy.data.meshes.new("mark")
        me.from_pydata([(XL, -2.512, z0), (XL + wid, -2.512, z0), (XL + wid, -2.512, z0 + hgt), (XL, -2.512, z0 + hgt)], [], [(0, 1, 2, 3)])
        uv = me.uv_layers.new(name="uv")
        for lp, t in zip(me.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            uv.data[lp.index].uv = t
        o = link(bpy.data.objects.new("mark", me)); o.data.materials.append(wm); o.visible_shadow = False
        out["mark"] = (XL, XL + wid, z0, z0 + hgt)
    for kind, text, slat in BOARDS[frame]:
        out[text] = line(text, BIG if kind == "b" else SMALL, ivory if kind == "b" else pink, slat)
    return out


def build(frame, quality, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 128 if final else 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.render.threads_mode = "AUTO"
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1.0, 0.95, 0.97, 1); bg.inputs["Strength"].default_value = 0.10

    sizes()
    marks = scene(frame)
    shot = SHOTS[frame]

    # key: one small window high on the left, raking across the felt so every letter and slat throws a shadow
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 26; key.size_y = 34
    key.energy = 1.25e6; key.color = (1.0, 0.96, 0.91)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (-210, -150, 250); aim(ko, (0, 0, 22))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 300; fl.energy = 1.1e5; fl.color = (0.95, 0.96, 1.0)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (190, -330, 90); aim(fo, (0, 0, 22))

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]; cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"] / 100.0        # the scene is in centimetres, Blender reads metres
    if quality == "probe":
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update()
        pts = {"felt BL": (-BW / 2, FACE, Z0), "felt BR": (BW / 2, FACE, Z0), "felt TL": (-BW / 2, FACE, Z0 + BH), "felt TR": (BW / 2, FACE, Z0 + BH), "foot L": (-BW / 2, -2.5, 0), "foot R": (BW / 2, -2.5, 0)}
        for gx in (-10, -5, 0, 5, 10, 15):
            for gy in (-6, -10, -14, -18, -24):
                pts[f"c {gx} {gy}"] = (gx, gy, 0)
        for t, (x0, x1, z0, z1) in marks.items():
            pts[t + " bl"] = (x0, FACE, z0); pts[t + " tr"] = (x1, FACE, z1); pts[t + " br"] = (x1, FACE, z0); pts[t + " tl"] = (x0, FACE, z1)
        for nm, pt in pts.items():
            v = world_to_camera_view(sc, co, Vector(pt))
            print(f"  f{frame} {nm:18s} x {v.x * W:7.0f}  y {(1 - v.y) * H:7.0f}")
        print("  BIG em", round(BIG, 3), "SMALL em", round(SMALL, 3), {k: tuple(round(v, 2) for v in m) for k, m in marks.items()})
        return None
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region
    exr = str(TMP / f"nx-menu-{frame}.exr")
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
    x = np.clip(a, 0, None) * EXPOSURE      # frame 2 is lit at a lower angle: bring its ivory level with the others
    x = np.where(x > 0.60, 0.60 + (1 - np.exp(-(x - 0.60) / 0.40)) * 0.36, x)     # a soft shoulder
    x = np.clip(x, 0, 1)
    lum = (x * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    x = np.clip(lum + (x - lum) * 1.12, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(11 + frame)
    x += rng.normal(0, 0.008, (H, W, 1)).astype(np.float32)
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
        exr = str(TMP / f"nx-menu-{fr}.exr")
        if quality == "probe":
            build(fr, quality); continue
        grade(exr if regrade else build(fr, quality), fr, quality)
