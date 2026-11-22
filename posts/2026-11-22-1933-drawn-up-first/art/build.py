"""Renders the pictures for this Reel with Blender's Python module (pip install bpy; run with python3.13).

One blueprint of a homepage (art/print.py) unrolling towards the camera on a plaster-pink table: a sheet 30 x 100 cm,
blue with white line on the front, plain white on the back, so the roll is white. A pencil lies beside it.
Three shots, the roll further on in each:
  1  wide and high: the first screen of the plan comes into view
  2  low and close, along the roll from its open end
  3  low and from the front: the title block, with the wordmark, as the roll moves off it
(The first design, reviewed at 6, had a fourth shot from directly above, called basic: it is in art/v1.)
python3.13 build.py <shot> <state letter|all> [draft|mid|final|probe]   -> art/r-<shot><letter>.jpg (drafts: .d-...)
Units are centimetres. The type is set over the pictures in reel.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())
TABLE = (0.700, 0.430, 0.375)
BACK = (0.86, 0.86, 0.83)
EXPOSURE = 1.0
SW, SL = 30.0, 100.0            # the sheet
Y0 = 50.0                       # world y of the sheet's top edge
RIN, PITCH = 2.0, 0.25          # the roll: inner radius, gap between turns
A = PITCH / (2 * math.pi)


NS = 12


def ease(n, a, b):
    return [a + (b - a) * (0.5 - 0.5 * math.cos(math.pi * i / (n - 1))) for i in range(n)]


SHOTS = {
    1: dict(loc=(26, -90, 122), aim=(0, 12, 0), lens=58, f=0.22, focus=(0, 14, 0), pin=((0, Y0 - 55.2, 0), (430, 1020)), states=ease(NS, 36.0, 55.2)),
    2: dict(loc=(60, -76.5, 46), aim=(6, -16.5, 2), lens=64, f=0.09, focus=(9, -17.5, 1), pin=((15, Y0 - 70.5, 2.3), (700, 1010)), states=ease(NS, 61.0, 70.5), pencil=(-22.5, 6.0, 80)),
    3: dict(loc=(6, -122, 52), aim=(0, -26, 0), lens=47, f=0.07, focus=(0, -24.5, 0), pin=((0, Y0 - 88.0, 0), (548, 1000)), states=ease(NS, 73.5, 88.0)),
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


def roll_r(yc):
    return math.sqrt(RIN * RIN + 2 * A * (SL - yc))


def sheet_mesh(yc, ds=0.2, m=30):
    """Flat from the top edge to s = yc, then wound up and back over itself as a spiral. Never stretched."""
    R = roll_r(yc)
    n = int(round(SL / ds))
    vs, uvs = [], []
    RF, CF = 30.0, 6.0                      # the top end still wants to curl: the last 7 cm lift
    for i in range(n + 1):
        s = i * ds
        if s <= yc:
            if s < CF:
                t = (CF - s) / RF
                y = Y0 - CF + RF * math.sin(t); z = RF * (1 - math.cos(t))
            else:
                y = Y0 - s; z = 0.0
            # the flat sheet is not dead flat: a long low swell
            z += 0.035 + 0.05 * (0.5 + 0.5 * math.sin(s * 0.19 + 0.8)) * min(1.0, max(0.0, (yc - s) / 6.0))
            dx = 0.0
        else:
            w = s - yc
            phi = (R - math.sqrt(max(R * R - 2 * A * w, 0.0))) / A
            r = R - A * phi
            y = Y0 - yc - r * math.sin(phi); z = 0.035 + R - r * math.cos(phi)
            dx = 0.22 * (R - r) / max(R - RIN, 1e-6)
        for j in range(m + 1):
            u = j / m
            # the long edges of a sheet that has been rolled lift a little off the table, more in some places than others
            edge = math.exp(-min(u, 1 - u) * SW / 1.3)
            wob = 0.0 if s > yc else (0.03 * math.sin(u * 5.1 + s * 0.11) + 0.22 * edge * (0.55 + 0.45 * math.sin(s * 0.23 + (2.0 if u > 0.5 else 0.0)))) * min(1.0, max(0.0, (yc - s) / 6.0))
            vs.append(((u - 0.5) * SW + dx, y, z + wob)); uvs.append((u, 1 - s / SL))
    fs = []
    for i in range(n):
        for j in range(m):
            a = i * (m + 1) + j
            fs.append((a, a + m + 1, a + m + 2, a + 1))
    me = bpy.data.meshes.new("sheet"); me.from_pydata(vs, [], fs)
    uv = me.uv_layers.new(name="uv")
    for lp in me.loops:
        uv.data[lp.index].uv = uvs[lp.vertex_index]
    for p in me.polygons:
        p.use_smooth = True
    return me


def paper():
    m, nt, p = mat("paper")
    N_, L = nt.nodes, nt.links
    tex = N_.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / ".plan.png")); tex.interpolation = "Cubic"; tex.extension = "EXTEND"
    geo = N_.new("ShaderNodeNewGeometry")
    tc = N_.new("ShaderNodeTexCoord")
    # cyanotype is never an even blue: a slow mottle in the print
    mo = N_.new("ShaderNodeTexNoise"); mo.inputs["Scale"].default_value = 0.35; mo.inputs["Detail"].default_value = 5; mo.inputs["Roughness"].default_value = 0.6
    L.new(tc.outputs["Object"], mo.inputs["Vector"])
    ramp = N_.new("ShaderNodeMapRange"); ramp.inputs["From Min"].default_value = 0.3; ramp.inputs["From Max"].default_value = 0.7
    ramp.inputs["To Min"].default_value = 0.90; ramp.inputs["To Max"].default_value = 1.06
    L.new(mo.outputs["Fac"], ramp.inputs["Value"])
    mul = N_.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs["Factor"].default_value = 1.0
    L.new(tex.outputs["Color"], mul.inputs["A"]); L.new(ramp.outputs["Result"], mul.inputs["B"])
    mix = N_.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["B"].default_value = (*BACK, 1)
    L.new(geo.outputs["Backfacing"], mix.inputs["Factor"]); L.new(mul.outputs["Result"], mix.inputs["A"])
    L.new(mix.outputs["Result"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.58; p.inputs["Specular IOR Level"].default_value = 0.30; p.inputs["Sheen Weight"].default_value = 0.10
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 55; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.7
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.10; bump.inputs["Distance"].default_value = 0.008
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    tr = N_.new("ShaderNodeBsdfTranslucent"); L.new(mix.outputs["Result"], tr.inputs["Color"])
    ms = N_.new("ShaderNodeMixShader"); ms.inputs["Fac"].default_value = 0.06
    L.new(p.outputs["BSDF"], ms.inputs[1]); L.new(tr.outputs["BSDF"], ms.inputs[2])
    L.new(ms.outputs["Shader"], nt.nodes["Material Output"].inputs["Surface"])
    return m


def pencil(place=None):
    """A hexagonal drawing pencil, black lacquer, cut to a long point. Local +x is the point."""
    r, Lb, Lc, Lg = 0.37, 15.2, 2.1, 0.55
    vs, fs, mi = [], [], []
    def ring(x, rad, k=6, off=0.0):
        i0 = len(vs)
        for i in range(k):
            a = off + i * 2 * math.pi / k
            vs.append((x, rad * math.cos(a), rad * math.sin(a)))
        return i0
    def band(a, b, k, midx):
        for i in range(k):
            fs.append((a + i, a + (i + 1) % k, b + (i + 1) % k, b + i)); mi.append(midx)
    off = math.pi / 6
    e0 = ring(-Lb / 2 - 0.0, r * 0.9, 6, off); b0 = ring(-Lb / 2 + 0.12, r, 6, off); b1 = ring(Lb / 2, r, 6, off)
    fs.append(tuple(range(e0, e0 + 6))[::-1]); mi.append(3)
    band(e0, b0, 6, 3); band(b0, b1, 6, 0)
    k = 24
    c0 = ring(Lb / 2, r * 0.985, k, off); c1 = ring(Lb / 2 + Lc, 0.11, k, off); c2 = ring(Lb / 2 + Lc + Lg, 0.012, k, off)
    band(c0, c1, k, 1); band(c1, c2, k, 2)
    me = bpy.data.meshes.new("pencil"); me.from_pydata(vs, [], fs)
    for p, i in zip(me.polygons, mi):
        p.material_index = i; p.use_smooth = i in (1, 2)
    m0, _, p0 = mat("lacquer"); p0.inputs["Base Color"].default_value = (0.012, 0.012, 0.016, 1); p0.inputs["Roughness"].default_value = 0.22; p0.inputs["Coat Weight"].default_value = 0.6
    m1, nt, p1 = mat("wood"); p1.inputs["Base Color"].default_value = (0.62, 0.40, 0.24, 1); p1.inputs["Roughness"].default_value = 0.7
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 1.6; wv.inputs["Distortion"].default_value = 3.0
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["A"].default_value = (0.66, 0.44, 0.27, 1); mx.inputs["B"].default_value = (0.50, 0.30, 0.17, 1)
    nt.links.new(wv.outputs["Fac"], mx.inputs["Factor"]); nt.links.new(mx.outputs["Result"], p1.inputs["Base Color"])
    m2, _, p2 = mat("lead"); p2.inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1); p2.inputs["Roughness"].default_value = 0.35; p2.inputs["Metallic"].default_value = 0.6
    m3, _, p3 = mat("dip"); p3.inputs["Base Color"].default_value = (0.80, 0.80, 0.78, 1); p3.inputs["Roughness"].default_value = 0.3
    for m in (m0, m1, m2, m3):
        me.materials.append(m)
    ob = link(bpy.data.objects.new("pencil", me))
    ob.location = (-19.5, 22.0, r * math.cos(math.pi / 6) + 0.0)
    ob.rotation_euler = (0, 0, math.radians(84))
    if place:                               # moved along the table for the low shot, so it is still in the picture
        ob.location.x, ob.location.y = place[0], place[1]; ob.rotation_euler = (0, 0, math.radians(place[2]))
    return ob


def scene(yc, pencil_at=None):
    me = bpy.data.meshes.new("table"); me.from_pydata([(-3000, -3000, 0), (3000, -3000, 0), (3000, 3000, 0), (-3000, 3000, 0)], [], [(0, 1, 2, 3)])
    tb = link(bpy.data.objects.new("table", me))
    m, nt, p = mat("table"); p.inputs["Base Color"].default_value = (*TABLE, 1); p.inputs["Roughness"].default_value = 0.62; p.inputs["Specular IOR Level"].default_value = 0.30
    N_, L = nt.nodes, nt.links
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.65
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    tb.data.materials.append(m)
    sh = link(bpy.data.objects.new("sheet", sheet_mesh(yc)))
    sh.data.materials.append(paper())
    pencil(pencil_at)


def build(shot_n, letter, quality):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = {"final": 128, "mid": 16, "draft": 20}.get(quality, 20)
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 40 if quality == "draft" else 100
    sc.render.threads_mode = "FIXED"; sc.render.threads = 4
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1.0, 0.95, 0.93, 1); bg.inputs["Strength"].default_value = 0.30

    shot = SHOTS[shot_n]
    yc = shot["states"][ord(letter) - 97]
    scene(yc, shot.get("pencil"))
    # key: a window a long way off to the left and behind, low, so the roll and the pencil throw long shadows forward
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 130; key.size_y = 170
    key.energy = 1.05e7; key.color = (1.0, 0.95, 0.88)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (600, 240, 320); aim(ko, (0, 0, 0))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 500; fl.energy = 1.1e6; fl.color = (0.92, 0.95, 1.0)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (-260, -520, 420); aim(fo, (0, 0, 0))

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]
    # lens shift slides the picture without changing the perspective: put the pinned point on its pixel
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    v = world_to_camera_view(sc, co, Vector(shot["pin"][0]))
    cam.shift_x = (v.x * W - shot["pin"][1][0]) / H; cam.shift_y = (shot["pin"][1][1] - (1 - v.y) * H) / H
    cam.clip_start = 1; cam.clip_end = 20000
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).dot((Vector(shot["aim"]) - co.location).normalized())
    cam.dof.aperture_fstop = shot["f"]
    if quality == "probe":
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update()
        R = roll_r(yc)
        P = {"top L": (-15, Y0, 0), "top R": (15, Y0, 0), "roll L": (-15, Y0 - yc, R), "roll R": (15, Y0 - yc, R), "roll top": (0, Y0 - yc, 2 * R),
             "roll front": (0, Y0 - yc - R, R), "tb TL": (-14, Y0 - 66, 0), "tb TR": (14, Y0 - 66, 0), "tb BL": (-14, Y0 - 79, 0), "tb BR": (14, Y0 - 79, 0),
             "pencil": (-19.5, 22, 0), "hero": (-8.5, Y0 - 13, 0), "form": (-8.5, Y0 - 52, 0)}
        for nm, pt in P.items():
            v = world_to_camera_view(sc, co, Vector(pt))
            print(f"  {shot_n}{letter} {nm:10s} x {v.x * W:7.0f}  y {(1 - v.y) * H:7.0f}")
        return None
    exr = str(TMP / f"nx-plan-{shot_n}{letter}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def grade(exr, shot_n, letter, quality):
    from PIL import Image
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    x = np.clip(a, 0, None) * EXPOSURE
    ramp = np.clip(np.arange(H, dtype=np.float32) / 320.0, 0, 1)                    # a little shade at the very top, under Instagram's white name
    x = x * (0.90 + 0.10 * ramp * ramp * (3 - 2 * ramp))[:, None, None]
    x = np.where(x > 0.62, 0.62 + (1 - np.exp(-(x - 0.62) / 0.42)) * 0.36, x)     # a soft shoulder
    x = np.clip(x, 0, 1)
    lum = (x * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    x = np.clip(lum + (x - lum) * 1.06, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3 + shot_n)
    x += rng.normal(0, 0.006, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f".d-{shot_n}{letter}.jpg" if quality == "draft" else f"r-{shot_n}{letter}.jpg")
    out.save(dst, quality=(93 if quality == "final" else 88), subsampling=0)
    print("wrote", dst, flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    shot_n = int(args[0]); which = args[1] if len(args) > 1 else "a"
    quality = args[2] if len(args) > 2 else "draft"
    letters = [chr(97 + i) for i in range(len(SHOTS[shot_n]["states"]))] if which == "all" else list(which)
    for le in letters:
        if quality == "probe":
            build(shot_n, le, quality); continue
        grade(build(shot_n, le, quality), shot_n, le, quality)
