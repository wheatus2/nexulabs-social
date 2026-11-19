"""Renders the pictures for this Reel with Blender's Python module (pip install bpy; run with python3.13).

One made-up tailor's tape measure standing on its edge on a lilac cloth: ivory with a numeral at every
centimetre on the front, violet with kinds of business on the back (art/print.py draws both sides).
Shot from the same side four ways, and the tape is laid differently each time:
  1  the coil, with the first 30 cm swept across in front of it; the coil springs open
  2  one long sweep running away to the right; the tape is drawn through
  3  the back of the tape in a wide bay: cafes, joiners, salons; drawn through the other way
  4  the brass end and the maker's mark, close

  python3.13 print.py
  python3.13 build.py <scene> [draft|final|probe] [state letter|all]
writes art/r-<scene><state>.jpg (1134x2016, shown at 1080x1920). Units are centimetres, so a real
f/4 is aperture_fstop 0.04. The type is set over the pictures in reel.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1134, 2016
TMP = Path(tempfile.gettempdir())
TOTAL = 160.0                 # cm of tape in the print (90 mm lead + 1500 mm + 10 mm)
LEAD = 9.0
WID = 2.0                     # the tape is 2 cm wide
THK = 0.045
CLOTH = (0.47, 0.42, 0.80)    # lilac, linear
EXPOSURE = 1.0

# state letter -> parameter. Scene 1: how far the coil has sprung open (0 to 1).
# Scenes 2 and 3: how far the tape has been drawn through, in cm.
STATES = {
    1: dict(a=0.0, b=1.2, c=3.2, d=5.8, e=8.2, f=10.0, g=11.2, h=12.0),
    2: dict(a=0.0, b=1.3, c=3.0, d=4.9, e=6.6, f=7.9, g=8.7, h=9.0),
    3: dict(a=-7.0, b=-6.0, c=-4.5, d=-2.9, e=-1.6, f=-0.7, g=-0.2, h=0.0),
    4: dict(a=0.0),
}

SHOTS = {
    1: dict(loc=(3.5, -27, 21), aim=(3.5, 1, 0), lens=50, f=0.10, focus=(-2, -3.5, 1.0), shift=(0, 0.12)),
    2: dict(loc=(-3, -24, 27), aim=(-1.5, 1, 0), lens=50, f=0.22, focus=(-4, 2, 1.0), shift=(0, 0.07)),
    3: dict(loc=(0, -25, 27), aim=(0, 3.2, 0), lens=50, f=0.16, focus=(0, 1, 1.0), shift=(0, 0.07)),
    4: dict(loc=(4.95, -33, 19), aim=(4.95, 0, 0), lens=50, f=0.09, focus=(1, -1, 1.0), shift=(0, -0.07)),
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


def link(ob):
    bpy.context.scene.collection.objects.link(ob); return ob


# ---------------------------------------------------------------- the path the tape stands along
DS = 0.05


def run(pieces, start=(0.0, 0.0), heading=0.0):
    """pieces: (length, curvature at start, curvature at end). Returns xy points and headings, DS apart."""
    pts, hd = [start], [heading]
    x, y, th = start[0], start[1], heading
    for ln, k0, k1 in pieces:
        n = max(1, int(round(ln / DS)))
        for i in range(n):
            k = k0 + (k1 - k0) * (i + 0.5) / n
            th += k * DS * 0.5
            x += math.cos(th) * DS; y += math.sin(th) * DS
            th += k * DS * 0.5
            pts.append((x, y)); hd.append(th)
    return pts, hd


def spiral(pts, hd, length, r_in, pitch, lead_in=7.0):
    """Carries the path on into a coil wound to the left: the radius falls by `pitch` a turn."""
    x, y = pts[-1]; th = hd[-1]
    r_out = math.sqrt(r_in ** 2 + pitch * length / math.pi)
    k_prev = 0.0
    n = int(lead_in / DS)
    for i in range(n):                       # ease from the tail's curve into the coil's
        t = (i + 1) / n; k = (1 / r_out) * (3 * t * t - 2 * t * t * t)
        th += k * DS * 0.5; x += math.cos(th) * DS; y += math.sin(th) * DS; th += k * DS * 0.5
        pts.append((x, y)); hd.append(th)
    r = r_out; s = 0.0
    while s < length and r > r_in * 0.98:
        k = 1 / r
        th += k * DS * 0.5; x += math.cos(th) * DS; y += math.sin(th) * DS; th += k * DS * 0.5
        r -= pitch / (2 * math.pi * r) * DS; s += DS
        pts.append((x, y)); hd.append(th)
    return pts, hd


def layout(scene, p):
    """Returns (points, headings, tape coordinate of the first point in cm, +1 if the coordinate rises along the path)."""
    if scene == 1:
        # the tape is drawn out of the coil, to the left: p is how many centimetres have come out
        pts, hd = run([(14, 0.0, 0.035), (16, 0.035, 0.06), (6, 0.06, 0.02)], start=(-21, -6.5), heading=math.radians(-4))
        pts, hd = spiral(pts, hd, 110.0 - p * 2.2, 1.5, 0.52)
        return pts, hd, 4.0 + p, 1
    if scene == 2:
        pts, hd = run([(18, 0.0, 0.03), (20, 0.03, 0.10), (22, 0.10, 0.10), (16, 0.10, 0.04)], start=(-24, -10), heading=math.radians(8))
        return pts, hd, 22.0 + p, 1
    if scene == 3:
        # five rows, there and back: every other row shows the back of the tape
        R, LR, RP = 1.7, 9.0, 0.5
        k = 1 / R; arc = (math.pi - k * RP) / k
        pieces = [(18.0, 0, 0)]
        for i in range(4):
            sg = -1 if i % 2 == 0 else 1
            pieces += [(RP, 0, sg * k), (arc, sg * k, sg * k), (RP, sg * k, 0), (LR, 0, 0)]
        pieces += [(14.0, 0, 0)]
        pts, hd = run(pieces, start=(4.5 + 18.0 - LR, -4.0), heading=math.pi)
        return pts, hd, 30.0 + p, 1
    if scene == 4:
        pts, hd = run([(5.4, 0.0, 0.02), (3, 0.02, 0.1)], start=(-1.4, -1.0), heading=math.radians(2))
        pts, hd = spiral(pts, hd, 70.0, 1.5, 0.45, lead_in=5.0)
        return pts, hd, 0.0, 1


def tape(scene, p):
    pts, hd, c0, sgn = layout(scene, p)
    n = len(pts)
    P = np.array(pts); TH = np.array(hd)
    nrm = np.stack([-np.sin(TH), np.cos(TH)], 1)          # left of the heading: the back of the tape
    s = np.arange(n) * DS
    c = c0 + sgn * s                                      # tape coordinate, cm from the brass end
    keep = (c >= 0) & (c <= TOTAL)
    P, nrm, c, s = P[keep], nrm[keep], c[keep], s[keep]
    n = len(P)
    lean = 0.035 * np.sin(s * 0.21 + scene) + 0.02 * np.sin(s * 0.57)     # the top edge wanders a little
    verts, faces, uvs, mats = [], [], [], []
    for side, off in ((0, -THK / 2), (1, THK / 2)):
        for i in range(n):
            bx, by = P[i] + nrm[i] * off
            tx, ty = P[i] + nrm[i] * (off + lean[i])
            verts.append((bx, by, 0.0)); verts.append((tx, ty, WID))
    def vid(side, i, top):
        return side * 2 * n + i * 2 + top
    for i in range(n - 1):
        u0, u1 = c[i] / TOTAL, c[i + 1] / TOTAL
        faces.append((vid(0, i, 0), vid(0, i + 1, 0), vid(0, i + 1, 1), vid(0, i, 1)))        # front, faces -n
        uvs.append([(u0, 0), (u1, 0), (u1, 1), (u0, 1)]); mats.append(0)
        faces.append((vid(1, i + 1, 0), vid(1, i, 0), vid(1, i, 1), vid(1, i + 1, 1)))        # back, faces +n
        uvs.append([(1 - u1, 0), (1 - u0, 0), (1 - u0, 1), (1 - u1, 1)]); mats.append(1)
        faces.append((vid(0, i, 1), vid(0, i + 1, 1), vid(1, i + 1, 1), vid(1, i, 1)))        # top edge
        uvs.append([(0, 0)] * 4); mats.append(2)
    for i in (0, n - 1):
        f = (vid(0, i, 0), vid(0, i, 1), vid(1, i, 1), vid(1, i, 0))
        faces.append(f if i == 0 else f[::-1]); uvs.append([(0, 0)] * 4); mats.append(2)
    me = bpy.data.meshes.new("tape"); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name="uv")
    k = 0
    for poly, fu, mi in zip(me.polygons, uvs, mats):
        poly.material_index = mi; poly.use_smooth = mi != 2
        for j, li in enumerate(poly.loop_indices):
            uv.data[li].uv = fu[j]
    ob = link(bpy.data.objects.new("tape", me))
    ob.data.materials.append(print_mat("front", ".tape-front.png"))
    ob.data.materials.append(print_mat("back", f".tape-back-{scene}.png"))
    m, nt, pr = mat("edge"); pr.inputs["Base Color"].default_value = (0.74, 0.70, 0.60, 1); pr.inputs["Roughness"].default_value = 0.6
    ob.data.materials.append(m)
    if c[0] < 0.2:
        brass_end(P[0], nrm[0], lean[0])
    return ob


def print_mat(name, file):
    m, nt, p = mat(name)
    N, L = nt.nodes, nt.links
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / file)); tex.interpolation = "Cubic"; tex.extension = "EXTEND"
    L.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.42
    p.inputs["Specular IOR Level"].default_value = 0.45
    p.inputs["Coat Weight"].default_value = 0.18; p.inputs["Coat Roughness"].default_value = 0.22
    # the weave of a glass-fibre tape, under its coating
    uvn = N.new("ShaderNodeUVMap")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (TOTAL * 26, WID * 26, 1)
    L.new(uvn.outputs["UV"], mp.inputs["Vector"])
    wx = N.new("ShaderNodeTexWave"); wx.wave_type = "BANDS"; wx.bands_direction = "X"; wx.inputs["Scale"].default_value = 1.0; wx.inputs["Distortion"].default_value = 0.6
    wy = N.new("ShaderNodeTexWave"); wy.wave_type = "BANDS"; wy.bands_direction = "Y"; wy.inputs["Scale"].default_value = 1.0; wy.inputs["Distortion"].default_value = 0.6
    L.new(mp.outputs["Vector"], wx.inputs["Vector"]); L.new(mp.outputs["Vector"], wy.inputs["Vector"])
    mx = N.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
    L.new(wx.outputs["Fac"], mx.inputs[0]); L.new(wy.outputs["Fac"], mx.inputs[1])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.5; bump.inputs["Distance"].default_value = 0.006
    L.new(mx.outputs["Value"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def brass_end(p0, n0, lean0):
    """The crimped brass tip: a folded plate over the first 1.1 cm, with two pressed ribs."""
    m, nt, p = mat("brass")
    p.inputs["Base Color"].default_value = (0.86, 0.62, 0.26, 1); p.inputs["Metallic"].default_value = 1.0; p.inputs["Roughness"].default_value = 0.26
    N, L = nt.nodes, nt.links
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14; nz.inputs["Detail"].default_value = 4
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    rr = N.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.18; rr.inputs["To Max"].default_value = 0.40
    L.new(nz.outputs["Fac"], rr.inputs["Value"]); L.new(rr.outputs["Result"], p.inputs["Roughness"])
    th = math.atan2(-n0[0], n0[1])       # heading of the tape at its end
    root = link(bpy.data.objects.new("end", None)); root.location = (p0[0], p0[1], 0); root.rotation_euler = (0, 0, th)
    def part(name, lo, hi, bevel):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
        for v in bm.verts:
            v.co = Vector(((v.co.x + .5) * (hi[0] - lo[0]) + lo[0], (v.co.y + .5) * (hi[1] - lo[1]) + lo[1], (v.co.z + .5) * (hi[2] - lo[2]) + lo[2]))
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(m); ob.parent = root
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 4; b.limit_method = "ANGLE"
        for q in me.polygons:
            q.use_smooth = True
        return ob
    t = 0.05
    part("plate", (-0.06, -THK / 2 - t, -0.03), (0.86, THK / 2 + t, WID + 0.03), 0.03)
    for x in (0.24, 0.52):
        part("rib", (x, -THK / 2 - t - 0.05, 0.2), (x + 0.12, THK / 2 + t + 0.05, WID - 0.2), 0.045)


def cloth():
    m, nt, p = mat("cloth")
    N, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (*CLOTH, 1)
    p.inputs["Roughness"].default_value = 0.9; p.inputs["Specular IOR Level"].default_value = 0.12
    p.inputs["Sheen Weight"].default_value = 0.35; p.inputs["Sheen Roughness"].default_value = 0.5
    geo = N.new("ShaderNodeNewGeometry")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (30, 30, 30); mp.inputs["Rotation"].default_value = (0, 0, math.radians(31))
    L.new(geo.outputs["Position"], mp.inputs["Vector"])
    wx = N.new("ShaderNodeTexWave"); wx.bands_direction = "X"; wx.inputs["Scale"].default_value = 1.0; wx.inputs["Distortion"].default_value = 1.2; wx.inputs["Detail"].default_value = 2
    wy = N.new("ShaderNodeTexWave"); wy.bands_direction = "Y"; wy.inputs["Scale"].default_value = 1.0; wy.inputs["Distortion"].default_value = 1.2; wy.inputs["Detail"].default_value = 2
    L.new(mp.outputs["Vector"], wx.inputs["Vector"]); L.new(mp.outputs["Vector"], wy.inputs["Vector"])
    mx = N.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
    L.new(wx.outputs["Fac"], mx.inputs[0]); L.new(wy.outputs["Fac"], mx.inputs[1])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60; nz.inputs["Detail"].default_value = 3
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    add = N.new("ShaderNodeMath"); add.operation = "ADD"
    L.new(mx.outputs["Value"], add.inputs[0]); L.new(nz.outputs["Fac"], add.inputs[1])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.30; bump.inputs["Distance"].default_value = 0.012
    L.new(add.outputs["Value"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    me = bpy.data.meshes.new("table"); s = 3000
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    ob = link(bpy.data.objects.new("table", me)); ob.data.materials.append(m)


def build(scene, quality, letter, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    hero = letter == sorted(STATES[scene])[-1]
    sc.cycles.samples = (110 if hero else 40) if final else 24
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
    bg.inputs["Color"].default_value = (0.93, 0.94, 1.0, 1); bg.inputs["Strength"].default_value = 0.22

    cloth()
    tape(scene, STATES[scene][letter])
    shot = SHOTS[scene]

    # key: a small window low on the left and in front, raking across the cloth so the tape throws a shadow
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 60; key.size_y = 90
    key.energy = 8.5e6; key.color = (1.0, 0.96, 0.90)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (-560, -330, 330); aim(ko, (0, 0, 0))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 500; fl.energy = 0.8e6; fl.color = (0.92, 0.94, 1.0)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (420, -520, 380); aim(fo, (0, 0, 0))
    # something for the brass and the coating to mirror: a window with glazing bars
    em = bpy.data.materials.new("glass"); em.use_nodes = True
    e = em.node_tree.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (1.0, 0.97, 0.92, 1); e.inputs["Strength"].default_value = 5.0
    em.node_tree.links.new(e.outputs["Emission"], em.node_tree.nodes["Material Output"].inputs["Surface"])
    for i in range(2):
        for j in range(2):
            me = bpy.data.meshes.new("pane"); x0 = -130 + i * 62; z0 = 60 + j * 74
            me.from_pydata([(x0, -260, z0), (x0 + 56, -260, z0), (x0 + 56, -260, z0 + 68), (x0, -260, z0 + 68)], [], [(0, 1, 2, 3)])
            pane = link(bpy.data.objects.new("pane", me)); pane.data.materials.append(em)
            pane.visible_camera = False; pane.visible_diffuse = False

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 36
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]; cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"]
    if quality == "probe":
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update()
        pts, hd, c0, sgn = layout(scene, STATES[scene][letter])
        for i in range(0, len(pts), int(5 / DS)):
            for z in (0, WID):
                v = world_to_camera_view(sc, co, Vector((pts[i][0], pts[i][1], z)))
                print(f"  s{scene} c={c0 + sgn * i * DS:6.1f} z={z:3.1f}  x {v.x * 1080:7.0f}  y {(1 - v.y) * 1920:7.0f}")
        return None
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region
    exr = str(TMP / f"nx-tape-{scene}{letter}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def grade(exr, scene, quality, letter):
    from PIL import Image
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    x = np.clip(a, 0, None) * EXPOSURE
    x = np.where(x > 0.70, 0.70 + (1 - np.exp(-(x - 0.70) / 0.30)) * 0.27, x)     # a soft shoulder: the ivory stays off pure white
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3 + scene)
    x += rng.normal(0, 0.006, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"r-{scene}{letter}.jpg" if quality == "final" else f".d-{scene}{letter}.jpg")
    out.save(dst, quality=93, subsampling=0)
    print("wrote", dst, flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    scene = int(args[0])
    quality = args[1] if len(args) > 1 else "draft"
    which = args[2] if len(args) > 2 else sorted(STATES[scene])[-1]
    letters = sorted(STATES[scene]) if which == "all" else list(which)
    for letter in letters:
        if quality == "probe":
            build(scene, quality, letter); continue
        exr = str(TMP / f"nx-tape-{scene}{letter}.exr")
        grade(exr if "regrade" in args else build(scene, quality, letter), scene, quality, letter)
    (HERE / f".done-{scene}-{quality}").write_text("ok")
