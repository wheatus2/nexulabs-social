"""Renders the three pictures for this post with Blender's Python module (pip install bpy brotli).

One sign on one painted brick wall, and one camera that does not move: illuminated letters that spell .co.uk.
  1  lit            (a lapsed .uk name can stay on for a short while)
  2  switched off   (then the website and the email stop)
  3  taken down     (finally it is deleted: the paint the letters kept the weather off, the dirt
                     that ran down from them, and the studs)

  python3 build.py <frame 1|2|3|all> [draft|final] [regrade]
writes art/render-0N.jpg (1080x1350). The type is set over it in slide-0N.html.
"""
import sys, math, tempfile, random
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
W, H = 1080, 1350
TMP = Path(tempfile.gettempdir())

# ---------------------------------------------------------------- the sign
TEXT = ".co.uk"
SIZE = 0.95          # font size in metres
SPACING = 1.09       # a little air between the letters so the full stops stand clear
DEPTH = 0.065        # how deep the letters are (deeper, and their sides close the gaps between them from this angle)
GAP = 0.045          # how far they stand off the wall
WALL = (0.040, 0.085, 0.440)      # the paint as it is now, linear RGB
WALL_OLD = (0.120, 0.250, 0.950)  # the same paint where the letters kept the weather off it: cleaner and brighter
# the patch of wall the stain map covers (metres): x0, y0, width, height
STAIN = (-1.9, -1.15, 3.8, 1.8)

# the camera never moves: below and to the left of the sign, looking up at it
SHOT = dict(loc=(-1.95, -1.15, 3.3), aim=(-0.15, 0.40, 0.05), lens=32.3, f=4.0, focus=(-0.6, 0, 0.1), shift=-2)


def font_ttf():
    from fontTools.ttLib import TTFont
    out = TMP / "nx-unbounded-800.ttf"
    if not out.exists():
        f = TTFont(ROOT / "fonts" / "unbounded-latin-800-normal.woff2"); f.flavor = None; f.save(out)
    return str(out)


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def wall_material(stain=None):
    m, nt, p = mat("paint")
    N, L = nt.nodes, nt.links
    geo = N.new("ShaderNodeNewGeometry")
    brick = N.new("ShaderNodeTexBrick")
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.006
    brick.inputs["Mortar Smooth"].default_value = 0.35
    brick.inputs["Brick Width"].default_value = 0.225
    brick.inputs["Row Height"].default_value = 0.075
    brick.inputs["Color1"].default_value = (1, 1, 1, 1)
    brick.inputs["Color2"].default_value = (0.74, 0.74, 0.74, 1)
    brick.inputs["Mortar"].default_value = (0, 0, 0, 1)
    brick.offset = 0.5
    L.new(geo.outputs["Position"], brick.inputs["Vector"])
    # unevenness of each brick face, the brush marks in the paint, and weather in big soft patches
    big = N.new("ShaderNodeTexNoise"); big.inputs["Scale"].default_value = 9; big.inputs["Detail"].default_value = 6
    fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 160; fine.inputs["Detail"].default_value = 4
    patch = N.new("ShaderNodeTexNoise"); patch.inputs["Scale"].default_value = 1.3; patch.inputs["Detail"].default_value = 5
    for n in (big, fine, patch):
        L.new(geo.outputs["Position"], n.inputs["Vector"])

    def math_(op, a, b):
        n = N.new("ShaderNodeMath"); n.operation = op
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    height = math_("ADD", math_("ADD", math_("MULTIPLY", brick.outputs["Color"], 0.0045),
                                math_("MULTIPLY", big.outputs["Fac"], 0.0024)),
                   math_("MULTIPLY", fine.outputs["Fac"], 0.00035))
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 1.0; bump.inputs["Distance"].default_value = 1.0
    L.new(height, bump.inputs["Height"])
    L.new(bump.outputs["Normal"], p.inputs["Normal"])

    def mix(blend, fac, a, b):
        n = N.new("ShaderNodeMix"); n.data_type = "RGBA"; n.blend_type = blend
        for key, v in (("Factor", fac), ("A", a), ("B", b)):
            if isinstance(v, (int, float)):
                n.inputs[key].default_value = v
            elif isinstance(v, tuple):
                n.inputs[key].default_value = (*v, 1)
            else:
                L.new(v, n.inputs[key])
        return n.outputs["Result"]

    colour = WALL
    rough = 0.62
    if stain:
        mp = N.new("ShaderNodeMapping"); mp.vector_type = "POINT"
        x0, y0, w, h = STAIN
        mp.inputs["Scale"].default_value = (1 / w, 1 / h, 1)
        mp.inputs["Location"].default_value = (-x0 / w, -y0 / h, 0)
        L.new(geo.outputs["Position"], mp.inputs["Vector"])
        tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(stain); tex.image.colorspace_settings.name = "Non-Color"
        tex.extension = "CLIP"; tex.interpolation = "Cubic"
        L.new(mp.outputs["Vector"], tex.inputs["Vector"])
        sep = N.new("ShaderNodeSeparateColor"); L.new(tex.outputs["Color"], sep.inputs["Color"])
        under, dirt = sep.outputs["Red"], sep.outputs["Green"]
        colour = mix("MIX", under, WALL, WALL_OLD)                       # unfaded paint under the letters
        colour = mix("MULTIPLY", dirt, colour, (0.09, 0.09, 0.12))      # the dirt round them and below them
        rough = math_("ADD", 0.56, math_("MULTIPLY", dirt, 0.3))
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.28; ramp.color_ramp.elements[0].color = (0.72, 0.74, 0.78, 1)
    ramp.color_ramp.elements[1].position = 0.72; ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1)
    L.new(patch.outputs["Fac"], ramp.inputs["Fac"])
    colour = mix("MULTIPLY", 1.0, colour, ramp.outputs["Color"])
    colour = mix("MULTIPLY", 0.42, colour, brick.outputs["Color"])
    L.new(colour, p.inputs["Base Color"])
    if isinstance(rough, float):
        p.inputs["Roughness"].default_value = rough
    else:
        L.new(rough, p.inputs["Roughness"])
    p.inputs["Specular IOR Level"].default_value = 0.35
    return m


def plain(name, colour, rough=0.4, metallic=0.0, coat=0.0):
    m, nt, p = mat(name)
    p.inputs["Base Color"].default_value = (*colour, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = 0.16
    return m


def glow(name, colour, strength, uneven=0.0):
    m, nt, p = mat(name)
    p.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)
    p.inputs["Roughness"].default_value = 0.25
    p.inputs["Emission Color"].default_value = (*colour, 1)
    p.inputs["Emission Strength"].default_value = strength
    if uneven:
        # the lamps behind an acrylic face never light it quite evenly
        N, L = nt.nodes, nt.links
        geo = N.new("ShaderNodeNewGeometry")
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 7.0; nz.inputs["Detail"].default_value = 1.0
        L.new(geo.outputs["Position"], nz.inputs["Vector"])
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.3; mr.inputs["From Max"].default_value = 0.7
        mr.inputs["To Min"].default_value = strength * (1 - uneven); mr.inputs["To Max"].default_value = strength
        L.new(nz.outputs["Fac"], mr.inputs["Value"])
        L.new(mr.outputs["Result"], p.inputs["Emission Strength"])
    return m


def text_mesh(name="sign"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = TEXT
    cu.font = bpy.data.fonts.load(font_ttf(), check_existing=True)
    cu.size = SIZE
    cu.space_character = SPACING
    cu.align_x = "CENTER"; cu.align_y = "CENTER"
    cu.extrude = DEPTH / 2
    cu.bevel_depth = 0.006; cu.bevel_resolution = 3
    cu.resolution_u = 24
    ob = bpy.data.objects.new(name + "-curve", cu)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


def fixings(sign):
    """Where each letter is fixed to the wall: points well inside the strokes, spread out."""
    bm = bmesh.new(); bm.from_mesh(sign.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    seen, islands = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, isl = [v], []
        seen.add(v.index)
        while stack:
            a = stack.pop(); isl.append(a)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen:
                    seen.add(b.index); stack.append(b)
        islands.append(isl)
    verts = [v.co.copy() for v in bm.verts]
    front = [[v.index for v in f.verts] for f in bm.faces if f.normal.z > 0.9]
    side = [[v.index for v in f.verts] for f in bm.faces if abs(f.normal.z) < 0.5]
    bvh_front = BVHTree.FromPolygons(verts, front)
    bvh_side = BVHTree.FromPolygons(verts, side)
    pts = []
    for isl in islands:
        xs = [v.co.x for v in isl]; ys = [v.co.y for v in isl]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        cand, step = [], 0.012
        x = x0
        while x <= x1:
            y = y0
            while y <= y1:
                if bvh_front.ray_cast(Vector((x, y, 1.0)), Vector((0, 0, -1)))[0] is not None:
                    near = bvh_side.find_nearest(Vector((x, y, 0.0)))
                    cand.append((math.hypot(near[0].x - x, near[0].y - y), x, y))
                y += step
            x += step
        if not cand:
            continue
        dmax = max(c[0] for c in cand)
        good = [c for c in cand if c[0] > 0.8 * dmax]
        if (x1 - x0) < 0.2:
            chosen = [max(good)]                      # a full stop hangs on one stud, in its middle
        else:                                         # a letter on four, one towards each corner
            chosen = [max(good, key=lambda c: sx * c[1] + sy * c[2]) for sx, sy in ((-1, 2), (1, 2), (-1, -2), (1, -2))]
        pts += [(c[1], c[2]) for c in chosen]
    bm.free()
    return pts


def stain_map(sign):
    """What years behind a sign leave on a wall, drawn from the letters themselves (1 px = 1 mm):
    red = wall that was under a letter, green = dirt: a line round each letter and runs below it."""
    from PIL import Image, ImageDraw
    from scipy.ndimage import gaussian_filter, binary_dilation, gaussian_filter1d
    x0, y0, w, h = STAIN
    res = 1000
    Wp, Hp = int(w * res), int(h * res)
    im = Image.new("L", (Wp, Hp), 0); d = ImageDraw.Draw(im)
    me = sign.data
    for p in me.polygons:
        if p.normal.z > 0.9:
            d.polygon([((me.vertices[i].co.x - x0) * res, (y0 + h - me.vertices[i].co.y) * res) for i in p.vertices], fill=255)
    S = np.asarray(im, dtype=np.float32) / 255
    B = S > 0.5
    under = gaussian_filter(S, 1.2)
    rim = gaussian_filter((binary_dilation(B, iterations=9) & ~B).astype(np.float32), 2.0)
    halo = gaussian_filter(S, 26) * (1 - S) * 0.5
    # runs: start under each letter's lower edges and fade on the way down
    rng = np.random.default_rng(11)
    col = gaussian_filter1d(rng.random(Wp).astype(np.float32), 3)
    col = np.clip((col - col.min()) / (col.max() - col.min()), 0, 1) ** 2.2
    reach = gaussian_filter1d(rng.random(Wp).astype(np.float32), 9)
    reach = 0.9930 + 0.0055 * (reach - reach.min()) / (reach.max() - reach.min())     # how far each run gets
    runs = np.zeros_like(S); cur = np.zeros(Wp, dtype=np.float32)
    for y in range(1, Hp):
        edge = (B[y - 1] & ~B[y]).astype(np.float32)
        cur = np.maximum(edge, cur * reach)
        cur[B[y]] = 0
        runs[y] = cur
    runs = gaussian_filter(runs * col[None, :], (3, 1.2)) * (1 - S)
    dirt = np.clip(rim * 0.85 + halo + runs * 0.9, 0, 1)
    out = np.zeros((Hp, Wp, 3), dtype=np.uint8)
    out[..., 0] = (np.clip(under, 0, 1) * 255).astype(np.uint8)
    out[..., 1] = (dirt * 255).astype(np.uint8)
    path = str(TMP / "nx-lights-out-stain.png")
    Image.fromarray(out, "RGB").save(path)
    return path


def aim(ob, target, up=(0, 1, 0)):
    """Point a camera or light at a place on the wall, keeping the wall's up as up."""
    f = (Vector(target) - ob.location).normalized()
    r = f.cross(Vector(up)).normalized()
    u = r.cross(f)
    ob.rotation_euler = Matrix((r, u, -f)).transposed().to_euler()


def build(frame, quality):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 160 if final else 32
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.sample_clamp_indirect = 8.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("dusk"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.22, 0.28, 0.46, 1)
    bg.inputs["Strength"].default_value = 0.20

    sign = text_mesh()
    sign.location.z = GAP + DEPTH / 2
    pts = fixings(sign)
    bb = [sign.matrix_world @ Vector(c) for c in sign.bound_box]
    print("SIGN", min(b.x for b in bb), max(b.x for b in bb), min(b.y for b in bb), max(b.y for b in bb), len(pts))

    me = bpy.data.meshes.new("wall")
    s = 60
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    wall = bpy.data.objects.new("wall", me); sc.collection.objects.link(wall)
    wall.data.materials.append(wall_material(stain_map(sign) if frame == 3 else None))

    steel = plain("steel", (0.46, 0.47, 0.49), rough=0.55, metallic=1.0)
    out = 0.035 if frame == 3 else GAP + 0.012      # how far each stud stands out of the wall
    rnd = random.Random(7)
    for (x, y) in pts:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.009, depth=out, location=(x, y, out / 2))
        c = bpy.context.active_object; c.data.materials.append(steel); bpy.ops.object.shade_smooth()
        if frame == 3:
            c.rotation_euler = (rnd.uniform(-.07, .07), rnd.uniform(-.07, .07), 0)
            bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.021, depth=0.003, location=(x, y, 0.002))
            bpy.context.active_object.data.materials.append(steel)

    if frame in (1, 2):
        lit = frame == 1
        face = glow("face", (1.0, 0.95, 0.88), 1.9, uneven=0.16) if lit else plain("face-off", (0.50, 0.52, 0.56), rough=0.20, coat=1.0)
        back = glow("back", (1.0, 0.95, 0.88), 24.0) if lit else plain("back-off", (0.5, 0.5, 0.5), rough=0.5)
        ret = plain("return", (0.60, 0.61, 0.64) if lit else (0.10, 0.105, 0.12), rough=0.34)
        for m in (face, back, ret):
            sign.data.materials.append(m)
        for p in sign.data.polygons:
            p.material_index = 0 if p.normal.z > 0.9 else (1 if p.normal.z < -0.9 else 2)
            p.use_smooth = abs(p.normal.z) <= 0.9
    else:
        bpy.data.objects.remove(sign)

    # the light that is left when the sign is not: a cold evening sky, high and to the left
    key = bpy.data.lights.new("sky", "AREA"); key.shape = "DISK"; key.size = 5.0
    key.color = (0.78, 0.86, 1.0)
    key.energy = 90 if frame == 1 else 170
    ko = bpy.data.objects.new("sky", key); sc.collection.objects.link(ko)
    ko.location = (-4.2, 4.6, 3.4)
    aim(ko, (0, 0.1, 0))

    if frame == 2:
        # what a dead acrylic face still does: it mirrors the last of the sky behind the camera, softly
        sk = bpy.data.lights.new("sheen", "AREA"); sk.shape = "RECTANGLE"; sk.size = 5.0; sk.size_y = 1.6
        sk.color = (0.80, 0.88, 1.0); sk.energy = 70
        so = bpy.data.objects.new("sheen", sk); sc.collection.objects.link(so)
        only = bpy.data.collections.new("sign-only"); sc.collection.children.link(only); only.objects.link(sign)
        so.light_linking.receiver_collection = only     # it lights the sign and nothing else, so the wall is exactly the wall of the last frame
        so.location = (2.4, 1.9, 3.3)
        aim(so, (0.2, 0.0, 0.1))

    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = SHOT["loc"]
    aim(co, SHOT["aim"])
    cam.lens = SHOT["lens"]
    cam.shift_x = SHOT["shift"] / H      # slide the picture sideways by so many pixels so the full stop sits on the type's margin
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(SHOT["focus"]) - co.location).length
    cam.dof.aperture_fstop = SHOT["f"]

    exr = str(TMP / f"nx-lights-out-{frame}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def grade(exr, frame, quality):
    """Camera work done after the render: bloom round the light, a film curve, a little grain."""
    from scipy.ndimage import gaussian_filter
    from PIL import Image
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    a = np.clip(a, 0, None)
    if frame == 1:
        hot = np.clip(a - 1.3, 0, 30)
        bloom = sum(wt * np.stack([gaussian_filter(hot[..., c], r) for c in range(3)], -1)
                    for r, wt in ((5, 0.16), (18, 0.11), (60, 0.08), (150, 0.05)))
        a = a + bloom
    # film curve (Narkowicz ACES fit), then sRGB
    x = a * 0.72
    x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.16 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None]
    rng = np.random.default_rng(3)
    x += rng.normal(0, 0.011, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"render-{frame:02d}.jpg" if quality == "final" else f".draft-{frame:02d}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst)


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 else "draft"
    regrade = "regrade" in args      # grade the last render again without rendering
    for fr in ([1, 2, 3] if which == "all" else [int(which)]):
        exr = str(TMP / f"nx-lights-out-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
