"""Renders the pictures for this Story with Blender's Python module (pip install bpy; run with python3.13).

One red-and-blue pencil (a checking pencil: red lead one end, blue the other) on bone paper, sharpened at both ends,
foil-stamped WEBSITE towards the red end, CRM towards the blue end and the real Nexulabs wordmark across the join.
Shot from the front left three ways:
  1  the red point, near, the pencil running away up the frame
  2  the blue point, far end, the red half soft in front
  3  the join, from higher: red meets blue under the wordmark
Stamp: art/print.py.   python3.13 build.py <1|2|3|all> [draft|final|probe] [regrade]
writes art/render-0N.jpg (1080x1920). Units are centimetres. The type is set over it in slide-0N.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())
TABLE = (0.80, 0.745, 0.61)
EXPOSURE = 1.20
L_, A_, TAN, RLEAD, FLAT = 17.5, 0.35, 0.2, 0.165, 0.40
RED, BLUE = (0.52, 0.004, 0.010), (0.008, 0.040, 0.46)
YAW = 0.0


def orbit(t, az, el, d):
    az, el = math.radians(az), math.radians(el)
    return (t[0] - d * math.cos(el) * math.sin(az), t[1] - d * math.cos(el) * math.cos(az), t[2] + d * math.sin(el))


SHOTS = {
    1: dict(aim=(3.6, 1.3, 0), o=(38, 44, 21), lens=50, f=0.5, focus=(2.0, 0.5, 0.2), shift=(0.0, 0.14)),
    2: dict(aim=(15.0, 1.5, 0), o=(38, 44, 21), lens=50, f=0.5, focus=(15.6, 0.8, 0.2), shift=(0.0, 0.17)),
    3: dict(aim=(6.9, 0, 0.3), o=(74, 26, 23), lens=50, f=1.8, focus=(6.5, 0, 0.35), shift=(-0.04, 0.055)),
}
import json
_o = HERE / ".shots.json"
if _o.exists():
    for k, v in json.loads(_o.read_text()).items():
        SHOTS[int(k)].update(v)
for _s in SHOTS.values():
    _s["loc"] = orbit(_s["aim"], *_s["o"])


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


def pencil():
    NA = 144
    xs = [0.11]
    while xs[-1] < 2.3: xs.append(round(xs[-1] + 0.008, 4))
    while xs[-1] < L_ - 2.3: xs.append(round(xs[-1] + 0.05, 4))
    while xs[-1] < L_ - 0.11 - 1e-6: xs.append(round(xs[-1] + 0.008, 4))
    xs[-1] = L_ - 0.11
    vs, lac, lead = [], [], []
    for x in xs:
        rc = TAN * min(x, L_ - x)
        for k in range(NA):
            th = 2 * math.pi * k / NA
            phi = math.radians((math.degrees(th) % 60) - 30)
            rh = min(A_ / math.cos(phi), 1.105 * A_)
            r = min(rh, rc)
            vs.append((x, r * math.cos(th), r * math.sin(th) + A_))
            lac.append(rc - rh); lead.append(RLEAD - rc)
    fs = []
    for i in range(len(xs) - 1):
        for k in range(NA):
            a = i * NA + k; b = i * NA + (k + 1) % NA
            fs.append((a, a + NA, b + NA, b))
    n0 = len(vs); vs.append((0.085, 0, A_)); lac.append(-1); lead.append(1)
    n1 = len(vs); vs.append((L_ - 0.085, 0, A_)); lac.append(-1); lead.append(1)
    last = (len(xs) - 1) * NA
    for k in range(NA):
        fs.append((n0, k, (k + 1) % NA)); fs.append((n1, last + (k + 1) % NA, last + k))
    me = bpy.data.meshes.new("pencil"); me.from_pydata(vs, [], fs)
    al = me.attributes.new("lac", "FLOAT", "POINT"); al.data.foreach_set("value", lac)
    ad = me.attributes.new("lead", "FLOAT", "POINT"); ad.data.foreach_set("value", lead)
    uv = me.uv_layers.new(name="uv")
    for p in me.polygons:
        p.use_smooth = True
        c = p.center; th = math.degrees(math.atan2(c.z - A_, c.y)) % 360
        on = 120 < th < 180 and len(p.vertices) == 4
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            if on:
                t = math.degrees(math.atan2(v.z - A_, v.y)) % 360
                t = min(max(t, 120), 180)
                uv.data[li].uv = (v.x / L_, 0.5 - A_ * math.tan(math.radians(t - 150)) / FLAT)
            else:
                uv.data[li].uv = (-0.5, -0.5)
    me.update()
    ob = link(bpy.data.objects.new("pencil", me)); ob.rotation_euler = (0, 0, YAW)

    m, nt, p = mat("pencil"); N_, Lk = nt.nodes, nt.links
    def attr(n):
        a = N_.new("ShaderNodeAttribute"); a.attribute_name = n
        g = N_.new("ShaderNodeMath"); g.operation = "GREATER_THAN"; g.inputs[1].default_value = 0.0
        Lk.new(a.outputs["Fac"], g.inputs[0]); return g.outputs[0]
    f_lac, f_lead = attr("lac"), attr("lead")
    tc = N_.new("ShaderNodeTexCoord"); sp = N_.new("ShaderNodeSeparateXYZ"); Lk.new(tc.outputs["Object"], sp.inputs[0])
    lt = N_.new("ShaderNodeMath"); lt.operation = "LESS_THAN"; lt.inputs[1].default_value = L_ / 2; Lk.new(sp.outputs["X"], lt.inputs[0])
    def mix(fac, a, b):
        mx = N_.new("ShaderNodeMix"); mx.data_type = "RGBA"
        for s, v in ((mx.inputs["Factor"], fac), (mx.inputs["A"], a), (mx.inputs["B"], b)):
            if isinstance(v, tuple): s.default_value = (*v, 1)
            elif isinstance(v, float): s.default_value = v
            else: Lk.new(v, s)
        return mx.outputs["Result"]
    def mixf(fac, a, b):
        mx = N_.new("ShaderNodeMix"); mx.data_type = "FLOAT"
        for s, v in ((mx.inputs["Factor"], fac), (mx.inputs["A"], a), (mx.inputs["B"], b)):
            if isinstance(v, float): s.default_value = v
            else: Lk.new(v, s)
        return mx.outputs["Result"]
    lacq = mix(lt.outputs[0], BLUE, RED)
    leadc = mix(lt.outputs[0], (0.02, 0.06, 0.42), (0.50, 0.012, 0.02))
    # wood: grain along the pencil
    mp = N_.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.2, 55, 55); Lk.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 6; Lk.new(mp.outputs[0], nz.inputs["Vector"])
    wood = mix(nz.outputs["Fac"], (0.62, 0.43, 0.27), (0.80, 0.63, 0.44))
    tex = N_.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / ".stamp.png")); tex.image.colorspace_settings.name = "Non-Color"
    tex.extension = "CLIP"; tex.interpolation = "Cubic"
    st = N_.new("ShaderNodeMath"); st.operation = "MULTIPLY"; Lk.new(tex.outputs["Color"], st.inputs[0]); Lk.new(f_lac, st.inputs[1])
    stamp = st.outputs[0]
    base = mix(f_lac, wood, lacq); base = mix(f_lead, base, leadc); base = mix(stamp, base, (0.86, 0.85, 0.80))
    Lk.new(base, p.inputs["Base Color"])
    rough = mixf(f_lac, 0.72, 0.20); rough = mixf(f_lead, rough, 0.50); rough = mixf(stamp, rough, 0.30)
    Lk.new(rough, p.inputs["Roughness"])
    Lk.new(stamp, p.inputs["Metallic"])
    ct = N_.new("ShaderNodeMath"); ct.operation = "SUBTRACT"; Lk.new(f_lac, ct.inputs[0]); Lk.new(stamp, ct.inputs[1])
    cw = N_.new("ShaderNodeMath"); cw.operation = "MULTIPLY"; cw.inputs[1].default_value = 0.3; Lk.new(ct.outputs[0], cw.inputs[0])
    Lk.new(cw.outputs[0], p.inputs["Coat Weight"]); p.inputs["Coat Roughness"].default_value = 0.06
    # the stamp is pressed in a touch; the wood has a fine tooth from the sharpener
    neg = N_.new("ShaderNodeMath"); neg.operation = "MULTIPLY"; neg.inputs[1].default_value = -1.0; Lk.new(stamp, neg.inputs[0])
    wb = N_.new("ShaderNodeMath"); wb.operation = "MULTIPLY"; wb.inputs[1].default_value = 0.5; Lk.new(nz.outputs["Fac"], wb.inputs[0])
    hgt = mixf(f_lac, wb.outputs[0], neg.outputs[0])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35; bump.inputs["Distance"].default_value = 0.01
    Lk.new(hgt, bump.inputs["Height"]); Lk.new(bump.outputs["Normal"], p.inputs["Normal"])
    ob.data.materials.append(m)
    return ob


def scene(frame):
    me = bpy.data.meshes.new("table"); me.from_pydata([(-900, -900, 0), (900, -900, 0), (900, 900, 0), (-900, 900, 0)], [], [(0, 1, 2, 3)])
    tb = link(bpy.data.objects.new("table", me))
    m, nt, p = mat("table"); p.inputs["Base Color"].default_value = (*TABLE, 1); p.inputs["Roughness"].default_value = 0.9; p.inputs["Specular IOR Level"].default_value = 0.0
    N_, L = nt.nodes, nt.links
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 26; nz.inputs["Detail"].default_value = 9; nz.inputs["Roughness"].default_value = 0.75
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.12; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    # what the pencil has written (art/page.py): a transparent print laid on the paper
    X0, Y0, PW, PH = -5.0, -1.0, 28.0, 9.0
    mp = N_.new("ShaderNodeMapping"); mp.inputs["Location"].default_value = (-X0 / PW, -Y0 / PH, 0); mp.inputs["Scale"].default_value = (1 / PW, 1 / PH, 1)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    tex = N_.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / f".page-{frame}.png")); tex.extension = "CLIP"; tex.interpolation = "Cubic"
    L.new(mp.outputs[0], tex.inputs["Vector"])
    mx = N_.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["A"].default_value = (*TABLE, 1)
    L.new(tex.outputs["Alpha"], mx.inputs["Factor"]); L.new(tex.outputs["Color"], mx.inputs["B"]); L.new(mx.outputs["Result"], p.inputs["Base Color"])
    tb.data.materials.append(m)
    pencil()


def probe(frame, sc, co):
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    P = {"red tip": (0.1, 0, .35), "red scallop": (1.9, 0, .7), "WEB start": (3.05, -.3, .55), "WEB end": (5.0, -.3, .55), "join": (8.75, -.3, .55),
         "CRM start": (12.75, -.3, .55), "CRM end": (13.6, -.3, .55), "blue scallop": (15.6, 0, .7), "blue tip": (17.4, 0, .35)}
    for nm, pt in P.items():
        v = world_to_camera_view(sc, co, Vector(pt))
        print(f"  f{frame} {nm:14s} x {v.x * W:7.0f}  y {(1 - v.y) * H:7.0f}")


def build(frame, quality):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 160 if final else 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.render.threads_mode = "FIXED"; sc.render.threads = 4
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.92, 0.94, 1.0, 1); bg.inputs["Strength"].default_value = 0.52

    scene(frame)
    shot = SHOTS[frame]
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.2; sun.angle = math.radians(1.6); sun.color = (1.0, 0.95, 0.88)
    so = link(bpy.data.objects.new("sun", sun)); so.location = shot.get("sun", (-60, 52, 30)); aim(so, (0, 0, 0))
    me = bpy.data.meshes.new("box"); me.from_pydata([(-40, -7, 0), (40, -7, 0), (40, 7, 0), (-40, 7, 0)], [], [(0, 1, 2, 3)])
    bo = link(bpy.data.objects.new("box", me)); bo.location = shot.get("box", (52, 53, 58)); aim(bo, (8, 0, 0))
    bm, bnt, bp = mat("box"); em = bnt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = shot.get("boxe", 1.1)
    bnt.links.new(em.outputs[0], bnt.nodes["Material Output"].inputs["Surface"]); bo.data.materials.append(bm)
    bo.visible_camera = False; bo.visible_diffuse = False; bo.visible_shadow = False

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]; cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).dot((Vector(shot["aim"]) - co.location).normalized())
    cam.dof.aperture_fstop = shot["f"]
    if quality == "probe":
        probe(frame, sc, co); return None
    exr = str(TMP / f"nx-pencil-{frame}.exr")
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
    x = np.clip(a, 0, None) * EXPOSURE
    ramp = np.clip(np.arange(H, dtype=np.float32) / 420.0, 0, 1)                    # shade the top, where Instagram's white name and bars sit
    x = x * (0.62 + 0.38 * ramp * ramp * (3 - 2 * ramp))[:, None, None]
    x = np.where(x > 0.70, 0.70 + (1 - np.exp(-(x - 0.70) / 0.30)) * 0.28, x)     # a soft shoulder
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3 + frame)
    x += rng.normal(0, 0.006, (H, W, 1)).astype(np.float32)
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
        exr = str(TMP / f"nx-pencil-{fr}.exr")
        if quality == "probe":
            build(fr, quality); continue
        grade(exr if regrade else build(fr, quality), fr, quality)
