"""Renders the pictures for this Reel with Blender's Python module (pip install bpy brotli scipy).

A colour fan deck for one made-up logo on a plum paper sweep: five leaves on a steel rivet (cards.py prints their
faces). Shots:
  shut        the deck closed, close and low at the end away from the rivet: the top leaf says "Purple."   (scene 1)
  fan0..fan5  from above, the deck fanning open in six steps: the same word on five different purples    (scene 2)
  far, near   close on the open fan, focus first on a leaf behind, then on the top leaf, which now gives
              its code and has "This purple." printed across its own colour                              (scene 3)
  keep        the deck shut again from above, the code on top                                            (scene 4)

  python3 build.py <shot,shot|all> [draft|fast|final] [regrade]
writes art/render-<shot>.jpg, 10% larger than the frame so the Reel can move in on it without going soft.

Colour: the leaf that carries a code has to look like that code. There is no film curve; the lights are white; and
each picture's exposure is set from the render itself so that the top leaf's field measures #5B2A86 (see grade()).
"""
import sys, math, json, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

HERE = Path(__file__).resolve().parent
OVER = 1.1
W, H = int(1080 * OVER), int(1920 * OVER)
TMP = Path(tempfile.gettempdir())
META = json.loads((HERE / "tex" / "cards.json").read_text())
CW, CD, BAND, RAD = META["w"] / 1000, META["h"] / 1000, META["band"] / 1000, META["rad"] / 1000
THICK, GAP = 0.00062, 0.00006
PLUM = (0.016, 0.0028, 0.036)           # the paper sweep, linear RGB
RIVET = Vector((-0.070, 0.0))            # where the rivet is on the paper; it is 12.5 mm in from the left end of a leaf
PIVOT = CW / 2 - 0.0125                  # from a leaf's centre to its rivet hole
TARGET = (0x5B, 0x2A, 0x86)
STEP = 19.0                              # degrees between leaves when the fan is fully open


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def face_material(tex_name):
    m, nt, p = mat("face-" + tex_name)
    Nn, Ln = nt.nodes, nt.links
    tex = Nn.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / "tex" / f"{tex_name}.png"))
    tex.extension = "EXTEND"; tex.interpolation = "Cubic"
    Ln.new(tex.outputs["Color"], p.inputs["Base Color"])
    # uncoated card: almost no shine, so a dark colour is not lifted by reflections, and a fine tooth
    p.inputs["Roughness"].default_value = 0.85
    p.inputs["Specular IOR Level"].default_value = 0.06
    nz = Nn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1900; nz.inputs["Detail"].default_value = 3
    bump = Nn.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.00012
    Ln.new(nz.outputs["Fac"], bump.inputs["Height"]); Ln.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def plain(name, colour, rough=0.5, metallic=0.0):
    m, nt, p = mat(name)
    p.inputs["Base Color"].default_value = (*colour, 1); p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metallic
    return m


def leaf(name, tex_name, z, angle):
    """One leaf of the deck, turned by `angle` degrees about the rivet. Round corners in the mesh, a real thickness,
    and a white core showing at the edge."""
    ys = sorted(set([0.0, CD] + [RAD * (1 - math.cos(math.pi / 2 * j / 8)) for j in range(9)]
                    + [CD - RAD * (1 - math.cos(math.pi / 2 * j / 8)) for j in range(9)]
                    + list(np.linspace(RAD, CD - RAD, 12))))
    cols = 9
    verts, uvs, faces = [], [], []
    for v in ys:
        d = min(v, CD - v)
        hw = CW / 2 if d >= RAD else CW / 2 - RAD + math.sqrt(max(0.0, RAD * RAD - (RAD - d) ** 2))
        for c in range(cols):
            u = -hw + 2 * hw * c / (cols - 1)
            verts.append((u + PIVOT, v - CD / 2, 0.0))          # the rivet hole is the leaf's own origin
            uvs.append((u / CW + 0.5, v / CD))
    for r in range(len(ys) - 1):
        for c in range(cols - 1):
            a = r * cols + c
            faces.append((a, a + 1, a + cols + 1, a + cols))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name="uv")
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            uv.data[li].uv = uvs[vi]
    me.materials.append(face_material(tex_name))
    me.materials.append(plain("core", (0.84, 0.83, 0.80), 0.7))
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    so = ob.modifiers.new("thick", "SOLIDIFY"); so.thickness = THICK; so.offset = -1; so.use_rim = True; so.material_offset_rim = 1
    ob.location = (RIVET.x, RIVET.y, z); ob.rotation_euler = (0, 0, math.radians(angle))
    return ob


def lathe(name, profile, segs=96):
    verts, faces = [], []
    for (r, z) in profile:
        for s in range(segs):
            a = 2 * math.pi * s / segs
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for p in range(len(profile) - 1):
        for s in range(segs):
            a = p * segs + s; b = p * segs + (s + 1) % segs
            faces.append((a, b, b + segs, a + segs))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for poly in me.polygons:
        poly.use_smooth = True
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob


def deck(spread, top="c0"):
    """Five leaves on the rivet. spread 0 is shut (not quite square, as a deck never is), 1 is fully open.
    The top leaf swings towards the camera and the bottom one away, so every band shows."""
    shut = [SHUT0, -0.6, 0.2, -1.4, -0.3]                    # top to bottom, degrees: the others show below the top leaf, never above it
    for k in range(5):
        open_a = (k - 2) * STEP                              # top leaf at -36, bottom at +36
        a = shut[k] + spread * (open_a - shut[k])
        leaf(f"leaf-{k}", top if k == 0 else f"c{k}", (4 - k) * (THICK + GAP) + THICK, a)
    # the rivet: a low domed steel head with a turned edge
    h0 = 5 * (THICK + GAP)
    prof = [(0.0001, h0 + 0.0019)]
    for j in range(1, 15):
        t = j / 14
        prof.append((0.0052 * math.sin(t * math.pi / 2), h0 + 0.0004 + 0.0015 * math.cos(t * math.pi / 2)))
    prof += [(0.0054, h0 + 0.0002), (0.0054, h0 - 0.0004)]
    rv = lathe("rivet", prof); rv.location = (RIVET.x, RIVET.y, 0)
    rv.data.materials.append(plain("steel", (0.80, 0.80, 0.82), 0.16, 1.0))


def look(ob, target, roll=0.0):
    f = (Vector(target) - ob.location).normalized()
    r = f.cross(Vector((0, 0, 1))).normalized()
    u = r.cross(f)
    m = Matrix((r, u, -f)).transposed()
    ob.rotation_euler = (m @ Matrix.Rotation(math.radians(roll), 3, "Z")).to_euler()


def area(name, loc, target, size, energy, colour=(1, 1, 1), size_y=None):
    l = bpy.data.lights.new(name, "AREA"); l.size = size; l.energy = energy; l.color = colour
    if size_y:
        l.shape = "RECTANGLE"; l.size_y = size_y
    o = bpy.data.objects.new(name, l); bpy.context.scene.collection.objects.link(o)
    o.location = loc; look(o, target)
    return o


def on_leaf(k_angle, x, y, z=0.004):
    """A point given on a leaf (metres from its rivet hole) as a point in the room, for a leaf turned k_angle degrees."""
    a = math.radians(k_angle)
    return (RIVET.x + x * math.cos(a) - y * math.sin(a), RIVET.y + x * math.sin(a) + y * math.cos(a), z)


SHUT0 = 1.0
TOP_OPEN = -2 * STEP
BX, BY = PIVOT + CW / 2 - 0.035, CD / 2 - BAND / 2          # the middle of the printed name, on a leaf
SHOTS = {
    "shut": dict(spread=0.0, top="c0", target=on_leaf(SHUT0, BX - 0.008, BY - 0.012), dist=0.36, az=8, el=38, lens=85, f=9,
                 focus=on_leaf(SHUT0, BX, BY), shift=(0.066, 0.11), probe=(0.505, 0.734)),      # the usual probe point is out of this frame
    "keep": dict(spread=0.0, top="c0code", target=(0.0, 0.0, 0.0), dist=0.74, az=6, el=62, lens=70, f=11,
                 focus=(0.02, 0.0, 0.004), shift=(0.0, -0.17), roll=-9),
}
for n, s in enumerate([0.0, 0.16, 0.42, 0.70, 0.90, 1.0]):
    SHOTS[f"fan{n}"] = dict(spread=s, top="c0", target=(0.0, 0.0, 0.0), dist=0.715, az=0, el=62, lens=60, f=10,
                            focus=(0.03, -0.02, 0.003), shift=(0.0, -0.105))
_close = dict(spread=1.0, top="c0this", target=on_leaf(TOP_OPEN, BX - 0.016, 0.004), dist=0.96, az=-32, el=46, lens=85, f=3.2,
              shift=(-0.100, 0.05))
SHOTS["near"] = dict(_close, focus=on_leaf(TOP_OPEN, BX - 0.010, 0.006))
SHOTS["far"] = dict(_close, focus=on_leaf(TOP_OPEN + 2 * STEP, BX, BY))
PROBE = (0.055, -0.020)                  # where the top leaf's colour is measured: on its field, clear of anything printed


def build(name, quality):
    shot = SHOTS[name]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = {"final": 96, "fast": 32, "draft": 24}[quality]
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.sample_clamp_indirect = 8.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = {"final": 100, "fast": 100, "draft": 40}[quality]
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.10, 0.03, 0.18, 1)
    bg.inputs["Strength"].default_value = 0.05

    # the paper runs back and curves up into the wall, in one colour
    prof = [(-4.0, 0.0), (1.3, 0.0)]
    R = 0.9
    for j in range(1, 25):
        a = math.pi / 2 * j / 24
        prof.append((1.3 + R * math.sin(a), R * (1 - math.cos(a))))
    prof.append((2.2, 5.0))
    verts = [(x, y, z) for (y, z) in prof for x in (-6.0, 6.0)]
    faces = [(2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2) for j in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    sweep = bpy.data.objects.new("sweep", me); sc.collection.objects.link(sweep)
    jm, jnt, jp = mat("plum")
    jp.inputs["Base Color"].default_value = (*PLUM, 1)
    jp.inputs["Roughness"].default_value = 0.8
    jp.inputs["Specular IOR Level"].default_value = 0.15
    nz = jnt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1400; nz.inputs["Detail"].default_value = 4
    bump = jnt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08; bump.inputs["Distance"].default_value = 0.0002
    jnt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); jnt.links.new(bump.outputs["Normal"], jp.inputs["Normal"])
    me.materials.append(jm)

    deck(shot["spread"], shot["top"])

    # light: one soft box high on the left, small enough that the leaves throw real shadows on each other; a low
    # strip from behind on the right for the edges and the rivet; a little fill from the front. All white.
    area("key", (-0.50, -0.30, 0.78), (0, 0.0, 0.0), 0.26, 30)
    area("rim", (0.70, 0.62, 0.24), (0, 0.0, 0.0), 0.20, 5, size_y=1.0)
    area("fill", (0.6, -0.8, 0.5), (0, 0.0, 0.0), 0.9, 2.0)
    # a white card that only shiny things can see, so the rivet has something to reflect
    cm = bpy.data.meshes.new("card"); cm.from_pydata([(-0.5, -0.3, 0), (0.5, -0.3, 0), (0.5, 0.3, 0), (-0.5, 0.3, 0)], [], [(0, 1, 2, 3)])
    cd = bpy.data.objects.new("card", cm); sc.collection.objects.link(cd); cd.location = (-0.15, -0.25, 0.6); look(cd, (RIVET.x, 0, 0))
    em, ent, ep = mat("card"); ep.inputs["Emission Color"].default_value = (1, 1, 1, 1); ep.inputs["Emission Strength"].default_value = 4.0
    ep.inputs["Base Color"].default_value = (0, 0, 0, 1); cm.materials.append(em)
    cd.visible_camera = False; cd.visible_diffuse = False; cd.visible_shadow = False; cd.visible_transmission = False

    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 36
    az, el = math.radians(shot["az"]), math.radians(shot["el"])
    tg = Vector(shot["target"])
    co.location = tg + shot["dist"] * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    look(co, tg, shot.get("roll", 0.0))
    cam.lens = shot["lens"]
    cam.shift_x, cam.shift_y = shot["shift"]
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"]
    cam.clip_start = 0.02

    # where the colour probe lands in the picture
    bpy.context.view_layer.update()
    top_angle = SHUT0 + shot["spread"] * (TOP_OPEN - SHUT0)
    pv = world_to_camera_view(sc, co, Vector(on_leaf(top_angle, *PROBE, z=5 * (THICK + GAP))))
    (TMP / f"nx-fan-{name}-{quality}.json").write_text(json.dumps([pv.x, 1 - pv.y]))

    exr = str(TMP / f"nx-fan-{name}-{quality}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def pixels(exr):
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32), w, h


def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def grade(exr, name, quality):
    """Camera work done after the render. The exposure is whatever makes the top leaf's field measure its code."""
    from PIL import Image
    a, w, h = pixels(exr)
    px, py = SHOTS[name].get("probe") or json.loads((TMP / f"nx-fan-{name}-{quality}.json").read_text())
    cx, cy = int(px * w), int(py * h)
    r = max(3, w // 90)
    patch = a[cy - r:cy + r, cx - r:cx + r].reshape(-1, 3)
    got = np.median(patch, axis=0)
    want = np.array([lin(c) for c in TARGET])
    exposure = float((want / got).mean()) if (0 < px < 1 and 0 < py < 1) else None
    # pictures that are cut together inside one scene share one exposure, and so does a shot whose probe is out of frame
    store = HERE / "tex" / "exposure.json"
    known = json.loads(store.read_text()) if store.exists() else {}
    lead = "fan5" if name.startswith("fan") else {"far": "near"}.get(name, name)
    if lead != name or exposure is None or not (0.2 < exposure < 3):
        exposure = known[lead]
    elif quality != "draft":
        known[name] = exposure; store.write_text(json.dumps(known, indent=1))
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    x = np.clip(a, 0, None) * exposure
    x = np.where(x <= 0.9, x, 0.9 + 0.1 * (1 - np.exp(-(x - 0.9) / 0.1)))        # a soft shoulder for the whites only
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    yy, xx = np.mgrid[0:H, 0:W]
    rr = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.10 * np.clip(rr - 0.75, 0, 1) ** 1.5)[..., None]
    x += np.random.default_rng(3).normal(0, 0.0045, (H, W, 1)).astype(np.float32)      # a little grain, so the dark paper does not band when the video is compressed
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"render-{name}.jpg" if quality in ("final", "fast") else f".{quality}-{name}.jpg")
    out.save(dst, quality=94, subsampling=0)
    X, Y = int(px * W), int(py * H)
    print("wrote", dst.name, "exposure %.3f" % exposure, "probe", (X, Y), "reads #%02X%02X%02X" % out.getpixel((min(W - 1, max(0, X)), min(H - 1, max(0, Y)))))


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 and args[1] in ("draft", "fast", "final") else "draft"
    for nm in (list(SHOTS) if which == "all" else which.split(",")):
        exr = str(TMP / f"nx-fan-{nm}-{quality}.exr")
        grade(exr if "regrade" in args else build(nm, quality), nm, quality)
