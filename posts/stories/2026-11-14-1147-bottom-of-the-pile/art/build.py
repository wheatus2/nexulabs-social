"""Renders the three pictures for this Story with Blender's Python module (pip install bpy brotli scipy).

One bill spike on a jade counter, with a week of printed enquiry dockets on it (dockets.py prints them).
  1  the pile as it was left: Friday 16:42 on top, and the tail of Monday 09:05 sticking out underneath
  2  right up against that tail
  3  the pile turned over: Monday 09:05 on top, hanging down the front

The paper is not simulated. Each docket is a strip that bends one way only, like paper: it is laid on
whatever is already on the spike, bridging the bumps and drooping where nothing holds it up.

  python3 build.py <frame 1|2|3|all> [draft|final] [regrade | region]
writes art/render-0N.jpg (1080x1920). The type is set over it in slide-0N.html.
A final frame takes 10 to 25 minutes on two cores (frame 2, all paper, is the slow one). "region" renders only a
window of a frame (the spike of frame 3), which takes half a minute: it was used to try reflections on the spike.
"""
import sys, math, json, random, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())
META = json.loads((HERE / "tex" / "dockets.json").read_text())
N = len(META)

JADE = (0.006, 0.200, 0.098)          # the counter and the wall behind it, linear RGB
PAPER_W = 0.080                       # a till roll is 80 mm wide
BASE_R, BASE_H = 0.046, 0.009         # the spike's foot
ROD_R, ROD_TOP = 0.0020, 0.205
GREEN_HOLD = 0.38

# ---------------------------------------------------------------- the pile
CELL = 0.001
HALF = 0.30
GN = int(2 * HALF / CELL)


def lay(order, hero, seed, away=0):
    """Lay the dockets on the spike one at a time. Returns a list of sheets: dict(i, pts=[(s, z)], t, w, pu, pin, L)."""
    rnd = random.Random(seed)
    ax = (np.arange(GN) + 0.5) * CELL - HALF
    X, Y = np.meshgrid(ax, ax, indexing="xy")
    Hm = np.where(np.hypot(X, Y) <= BASE_R, BASE_H, 0.0).astype(np.float64)
    S = np.arange(-0.26, 0.26, CELL)
    sheets = []
    for k, i in enumerate(order):
        L = META[i]["mm"] / 1000
        h = hero.get(i, {})
        top = k == len(order) - 1
        yaw = rnd.uniform(0, 360)
        if away and k >= len(order) - away and not top:
            # a pile turned over in one go: the dockets just under the top one lie squarely under it
            hh = hero[order[-1]]
            yaw = hh["yaw"] + rnd.uniform(-2.5, 2.5)
            h = dict(h, pu=max(0.004, hh["pu"] + rnd.uniform(-0.002, 0.003)), pin=hh["pin"] + rnd.uniform(0.005, 0.010))   # a little further up, so no foot shows below the top one
        a = math.radians(h.get("yaw", yaw))           # which way the foot of the docket points
        pin = h.get("pin", rnd.uniform(0.34, 0.62) * L)               # how far down the docket the spike goes through
        pu = h.get("pu", PAPER_W / 2 + rnd.uniform(-0.012, 0.012))
        stiff = h.get("stiff", rnd.uniform(2.5, 6.0))                 # droop: metres of fall per metre squared of overhang
        gap = h.get("gap", rnd.uniform(0.00035, 0.00115))
        press = 0.25 + 0.75 * k / len(order)
        curl = h.get("curl", (rnd.uniform(0.0005, 0.007) * press, rnd.uniform(0.0005, 0.007) * press))
        t = np.array([math.cos(a), math.sin(a)]); w = np.array([-math.sin(a), math.cos(a)])
        cs = np.arange(-pu, PAPER_W - pu + 1e-9, 0.002)
        # what is under the docket at each step along it
        px = S[:, None] * t[0] + cs[None, :] * w[0]; py = S[:, None] * t[1] + cs[None, :] * w[1]
        ix = np.clip(((px + HALF) / CELL).astype(int), 0, GN - 1); iy = np.clip(((py + HALF) / CELL).astype(int), 0, GN - 1)
        under = Hm[iy, ix].max(axis=1) + gap
        s0, s1 = -pin, L - pin
        for _ in range(3):
            inside = (S >= s0) & (S <= s1)
            hh = np.where(inside, under, -1.0)
            q = (hh[None, :] - stiff * (S[:, None] - S[None, :]) ** 2).max(axis=1)      # stiff paper over the bumps
            q = np.maximum(q, under)
            from scipy.ndimage import gaussian_filter1d
            q = gaussian_filter1d(q, 2.5)
            q += max(0.0, float((under - q)[inside].max()))
            if h.get("lift"):                                           # the free end curls up off the counter
                amt, over = h["lift"]
                q = q + amt * np.clip((S - (s1 - over)) / over, 0, 1) ** 2
            # till paper remembers the roll: both ends lift a little, less so under the weight of the pile
            d1, d0 = 0.5 * (L - pin), 0.5 * pin
            q = q + curl[1] * np.clip((S - (s1 - d1)) / d1, 0, 1) ** 2 + curl[0] * np.clip(((s0 + d0) - S) / d0, 0, 1) ** 2
            # walk along the paper from the spike both ways until its length is used up
            ds = np.hypot(np.diff(S), np.diff(q))
            j0 = int(np.argmin(np.abs(S)))
            arc = np.concatenate([[0], np.cumsum(ds)]); arc -= arc[j0]
            s0 = float(np.interp(-pin, arc, S)); s1 = float(np.interp(L - pin, arc, S))
        arcs = np.linspace(-pin, L - pin, int(L / 0.0012))
        ss = np.interp(arcs, arc, S); zz = np.interp(arcs, arc, q)
        sheets.append(dict(i=i, s=ss, z=zz, arc=arcs, t=t, w=w, pu=pu, pin=pin, L=L, top=top))
        # the docket is now part of what the next one lies on
        sg = X * t[0] + Y * t[1]; cg = X * w[0] + Y * w[1]
        m = (sg >= s0) & (sg <= s1) & (cg >= -pu) & (cg <= PAPER_W - pu)
        Hm[m] = np.maximum(Hm[m], np.interp(sg[m], S, q))
    return sheets, float(Hm[np.hypot(X, Y) < 0.004].max())


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def plain(name, colour, rough=0.4, metallic=0.0, coat=0.0):
    m, nt, p = mat(name)
    p.inputs["Base Color"].default_value = (*colour, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = 0.1
    return m


def paper_material(i, full):
    from PIL import Image
    src = HERE / "tex" / f"docket-{i:02d}.png"
    if not full:                              # only the dockets the camera reads need every pixel
        small = TMP / f"nx-pile-docket-{i:02d}.png"
        if not small.exists():
            im = Image.open(src); im.resize((im.width // 3, im.height // 3), Image.LANCZOS).save(small)
        src = small
    m, nt, p = mat(f"docket-{i:02d}")
    Nn, Ln = nt.nodes, nt.links
    tex = Nn.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(src)); tex.extension = "CLIP"
    tex.interpolation = "Cubic"
    geo = Nn.new("ShaderNodeNewGeometry")
    mix = Nn.new("ShaderNodeMix"); mix.data_type = "RGBA"
    Ln.new(geo.outputs["Backfacing"], mix.inputs["Factor"])
    dim = Nn.new("ShaderNodeMix"); dim.data_type = "RGBA"; dim.blend_type = "MULTIPLY"; dim.inputs["Factor"].default_value = 1.0
    Ln.new(tex.outputs["Color"], dim.inputs["A"]); dim.inputs["B"].default_value = (0.84, 0.84, 0.83, 1)
    Ln.new(dim.outputs["Result"], mix.inputs["A"])
    mix.inputs["B"].default_value = (0.80, 0.795, 0.77, 1)            # the back of a docket is blank
    Ln.new(mix.outputs["Result"], p.inputs["Base Color"])
    Ln.new(tex.outputs["Alpha"], p.inputs["Alpha"])
    p.inputs["Roughness"].default_value = 0.42
    p.inputs["Specular IOR Level"].default_value = 0.35
    p.inputs["Sheen Weight"].default_value = 0.0
    # thin paper lets a little light through
    tr = Nn.new("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = (0.95, 0.94, 0.90, 1)
    tp = Nn.new("ShaderNodeBsdfTransparent")
    ms = Nn.new("ShaderNodeMixShader"); ms.inputs["Fac"].default_value = 0.16
    ma = Nn.new("ShaderNodeMixShader")
    out = nt.nodes["Material Output"]
    Ln.new(p.outputs["BSDF"], ms.inputs[1]); Ln.new(tr.outputs["BSDF"], ms.inputs[2])
    Ln.new(tex.outputs["Alpha"], ma.inputs["Fac"]); Ln.new(tp.outputs["BSDF"], ma.inputs[1]); Ln.new(ms.outputs["Shader"], ma.inputs[2])
    Ln.new(ma.outputs["Shader"], out.inputs["Surface"])
    return m


def sheet_object(sh, full):
    cols = [0.0, 0.25, 0.5, 0.75, 1.0]
    verts, uvs, faces = [], [], []
    n = len(sh["s"])
    for r in range(n):
        for c in cols:
            off = c * PAPER_W - sh["pu"]
            p = sh["s"][r] * sh["t"] + off * sh["w"]
            verts.append((float(p[0]), float(p[1]), float(sh["z"][r])))
            uvs.append((c, 1 - (sh["arc"][r] + sh["pin"]) / sh["L"]))
    k = len(cols)
    for r in range(n - 1):
        for c in range(k - 1):
            a = r * k + c
            faces.append((a, a + k, a + k + 1, a + 1))
    me = bpy.data.meshes.new(f"docket-{sh['i']:02d}")
    me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name="uv")
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            uv.data[li].uv = uvs[vi]
        poly.use_smooth = True
    me.materials.append(paper_material(sh["i"], full))
    ob = bpy.data.objects.new(me.name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def lathe(name, profile, segs=128):
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


def rounded(points, rad=0.0012, n=6):
    """Round the corners of a lathe profile so one smooth-shaded mesh has soft, lit edges."""
    out = [points[0]]
    for a, b, c in zip(points, points[1:], points[2:]):
        A, B, C = Vector(a), Vector(b), Vector(c)
        d1, d2 = (A - B).normalized(), (C - B).normalized()
        r = min(rad, (A - B).length / 2.2, (C - B).length / 2.2)
        p1, p2 = B + d1 * r, B + d2 * r
        for j in range(n + 1):
            u = j / n
            out.append(tuple((1 - u) ** 2 * p1 + 2 * u * (1 - u) * B + u ** 2 * p2))
    out.append(points[-1])
    return out


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


# ---------------------------------------------------------------- the three shots
# pile A is the week as it was left (Monday underneath, its long tail towards the camera); pile B is the same week turned over
A_ORDER = list(range(N))
A_HERO = {0: dict(yaw=-84, pin=0.030, pu=0.047, stiff=3.0, gap=0.0003, lift=(0.010, 0.050), curl=(0, 0)),
          N - 1: dict(yaw=-101, pin=0.024, pu=0.006, stiff=5.0, curl=(0.002, 0.007))}
B_ORDER = list(range(N - 1, -1, -1))
B_HERO = {0: dict(yaw=-97, pin=0.024, pu=0.006, stiff=5.0, gap=0.0008, curl=(0.004, 0.018))}

SHOTS = {
    1: dict(pile="A", target=(0.0, -0.012, 0.062), dist=1.184, az=8, el=22, lens=85, f=11, focus=(0, -0.05, 0.03), shift=(-0.0365, 0.120)),
    2: dict(pile="A", target=(0.010, -0.106, 0.012), dist=0.43, az=4, el=27, lens=85, f=8, focus=(0.010, -0.092, 0.008), shift=(-0.032, 0.055)),
    3: dict(pile="B", target=(0.024, -0.043, 0.093), dist=0.72, az=-8, el=50, lens=85, f=16, focus=(0.02, -0.075, 0.10), shift=(0.080, 0.109), card=True, rim=14,
            region=(0.165, 0.275, 0.47, 0.80)),
}


def build(frame, quality, region=None):
    shot = SHOTS[frame]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 104 if final else 28
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.transparent_max_bounces = 48
    sc.cycles.sample_clamp_indirect = 8.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 50
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.05, 0.16, 0.11, 1)
    bg.inputs["Strength"].default_value = 0.22

    # the counter runs back and curves up into the wall, in one colour
    prof = [(-4.0, 0.0), (1.1, 0.0)]
    R = 0.9
    for j in range(1, 25):
        a = math.pi / 2 * j / 24
        prof.append((1.1 + R * math.sin(a), R * (1 - math.cos(a))))
    prof.append((2.0, 5.0))
    verts = [(x, y, z) for (y, z) in prof for x in (-6.0, 6.0)]
    faces = [(2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2) for j in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    sweep = bpy.data.objects.new("sweep", me); sc.collection.objects.link(sweep)
    jm, jnt, jp = mat("jade")
    jp.inputs["Base Color"].default_value = (*JADE, 1)
    jp.inputs["Roughness"].default_value = 0.46
    jp.inputs["Specular IOR Level"].default_value = 0.4
    nz = jnt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 3
    bump = jnt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.035; bump.inputs["Distance"].default_value = 0.0002
    jnt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); jnt.links.new(bump.outputs["Normal"], jp.inputs["Normal"])
    me.materials.append(jm)

    # the spike: a heavy enamelled foot and a polished steel rod ground to a point
    foot = lathe("foot", rounded([(0.0, 0.0), (BASE_R, 0.0), (BASE_R, BASE_H * 0.45), (BASE_R - 0.004, BASE_H), (0.0, BASE_H)], 0.0016))
    foot.data.materials.append(plain("enamel", (0.012, 0.013, 0.014), rough=0.22, coat=0.6))
    rod = lathe("rod", [(0.0052, BASE_H), (0.0052, BASE_H + 0.004), (ROD_R, BASE_H + 0.0075), (ROD_R, ROD_TOP - 0.030),
                        (ROD_R * 0.55, ROD_TOP - 0.012), (0.00012, ROD_TOP), (0.0, ROD_TOP)], 48)
    rod.data.materials.append(plain("steel", (0.78, 0.79, 0.80), rough=0.085, metallic=1.0))

    sheets, top = lay(A_ORDER if shot["pile"] == "A" else B_ORDER, A_HERO if shot["pile"] == "A" else B_HERO, 21 if shot["pile"] == "A" else 34, 0 if shot["pile"] == "A" else 8)
    print("PILE HEIGHT", round(top * 1000, 1), "mm")
    for sh in sheets:
        sheet_object(sh, full=sh["i"] in (0, N - 1) or sh["top"])

    # light: one big soft box high on the left, a strip behind on the right to rim the paper and the rod
    area("key", (-0.62, -0.50, 0.95), (0, 0, 0.03), 0.95, 42, (1.0, 0.98, 0.95))
    area("rim", (0.75, 0.70, 0.42), (0, 0, 0.06), 0.30, shot.get("rim", 30), (0.95, 1.0, 0.97), size_y=1.1)
    area("fill", (0.9, -0.9, 0.35), (0, 0, 0.05), 0.8, 4, (0.9, 1.0, 0.95))

    # two tall white cards that only the steel sees, so the rod reads as polished metal and not as a black line
    for nm, x in (("card-l", -0.5), ("card-r", 0.55)):
        cm = bpy.data.meshes.new(nm); cm.from_pydata([(0, -0.25, 0), (0, 0.25, 0), (0, 0.25, 1.2), (0, -0.25, 1.2)], [], [(0, 1, 2, 3)])
        cd = bpy.data.objects.new(nm, cm); sc.collection.objects.link(cd); cd.location = (x, -0.55, -0.1)
        em, ent, ep = mat(nm); ep.inputs["Emission Color"].default_value = (1, 1, 1, 1); ep.inputs["Emission Strength"].default_value = 2.2 if x < 0 else 0.9
        ep.inputs["Base Color"].default_value = (0, 0, 0, 1); cm.materials.append(em)
        cd.visible_camera = False; cd.visible_diffuse = False; cd.visible_shadow = False; cd.visible_transmission = False

    if shot.get("card"):
        # seen from above, a polished rod mirrors only the counter and the paper under it, and reads as glass. Two cards
        # just above the pile that only reflections can see, and only from above, give it a lit side and a dark side
        for nm, x0, x1, col, st in (("card-lit", -1.2, 0.0, (1, 1, 1), 1.5), ("card-dark", 0.0, 1.2, (0.02, 0.075, 0.052), 1.0)):
            cm = bpy.data.meshes.new(nm); cm.from_pydata([(x0, -1.2, 0), (x1, -1.2, 0), (x1, 1.2, 0), (x0, 1.2, 0)], [], [(0, 1, 2, 3)])
            cd = bpy.data.objects.new(nm, cm); sc.collection.objects.link(cd); cd.location = (0.0005, 0, top + 0.0004)
            em = bpy.data.materials.new(nm); em.use_nodes = True; nt = em.node_tree
            e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*col, 1); e.inputs["Strength"].default_value = st
            tp = nt.nodes.new("ShaderNodeBsdfTransparent"); g = nt.nodes.new("ShaderNodeNewGeometry"); mx = nt.nodes.new("ShaderNodeMixShader")
            nt.links.new(g.outputs["Backfacing"], mx.inputs["Fac"]); nt.links.new(e.outputs["Emission"], mx.inputs[1]); nt.links.new(tp.outputs["BSDF"], mx.inputs[2])
            nt.links.new(mx.outputs["Shader"], nt.nodes["Material Output"].inputs["Surface"])
            cm.materials.append(em)
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
    cam.clip_start = 0.05

    exr = str(TMP / f"nx-pile-{frame}.exr")
    if region:
        # render only a window of the frame (x0, x1, y0, y1 as fractions, y from the bottom): used to redo the spike of
        # frame 3 once it had its card, without rendering the paper again
        sc.render.use_border = True; sc.render.use_crop_to_border = False
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region
        exr = str(TMP / f"nx-pile-{frame}-region.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def pixels(exr):
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32), w, h


def grade(exr, frame, quality):
    """Camera work done after the render: a film curve, a little fall-off and grain."""
    from PIL import Image
    from scipy.ndimage import gaussian_filter
    a, w, h = pixels(exr)
    patch = TMP / f"nx-pile-{frame}-region.exr"
    if SHOTS[frame].get("region") and patch.exists() and quality == "final":
        b, _, _ = pixels(str(patch))
        x0, x1, y0, y1 = SHOTS[frame]["region"]
        m = np.zeros((h, w), dtype=np.float32)
        m[int((1 - y1) * h) + 8:int((1 - y0) * h) - 8, int(x0 * w) + 8:int(x1 * w) - 8] = 1
        m = gaussian_filter(m, 3)[..., None]
        a = a * (1 - m) + b * m
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    a = np.clip(a, 0, None)
    x = a * 0.62
    x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)       # film curve (Narkowicz ACES fit)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    # the grade: hold the jade down so white type reads on it (4:1 or better), and leave the paper alone
    mx, mn = x.max(axis=-1, keepdims=True), x.min(axis=-1, keepdims=True)
    sat = np.where(mx > 1e-4, (mx - mn) / np.maximum(mx, 1e-4), 0)
    x = x * (1 - GREEN_HOLD * sat ** 1.5)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.14 * np.clip(r - 0.6, 0, 1) ** 1.5)[..., None]
    rng = np.random.default_rng(3)
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
        exr = str(TMP / f"nx-pile-{fr}.exr")
        if "region" in args:                 # python3 build.py 3 final region: redo only the window, then grade
            build(fr, quality, SHOTS[fr]["region"]); regrade = True
        grade(exr if regrade else build(fr, quality), fr, quality)
