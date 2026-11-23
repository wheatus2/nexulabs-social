"""Renders the pictures for this Story with Blender's Python module (pip install bpy; run with python3.13).

Embossing label tape on a sky-blue table, shot from the front left three ways:
  1  a black tape off its roll, pressed with YOURNAME.CO.UK
  2  from higher: a second label, HELLO@, going down in front of the name, one end still lifted, its backing paper beside it
  3  low and close: both labels down, and a roll of white Nexulabs tape (the real wordmark, "Hosting, domains and email") laid in front
Prints: art/print.py, shapes: art/geom.py.   python3.13 build.py <1|2|3|all> [draft|final] [regrade]
writes art/render-0N.jpg (1080x1920). Units are centimetres. The type is set over it in slide-0N.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import geom

W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())
TABLE = (0.165, 0.385, 0.760)
EXPOSURE = 0.92
NXO = (-0.7, -4.5)
MAIL = (-3.0, -2.1)          # the email label: x of its left end, y of its centre line
BACK = (-2.4, -6.6, -24)      # its backing paper             # white tape: x of its cut end, y of its centre line

def orbit(t, az, el, d):
    """Camera position: d from target t, az degrees round from the front (-y) towards the left (-x), el degrees up."""
    az, el = math.radians(az), math.radians(el)
    return (t[0] - d * math.cos(el) * math.sin(az), t[1] - d * math.cos(el) * math.cos(az), t[2] + d * math.sin(el))


SHOTS = {
    1: dict(aim=(3.3, -1.7, 1.5), o=(62, 32, 30), lens=50, f=0.45, focus=(3.0, 0, 0), shift=(0.05, 0.19)),
    2: dict(aim=(2.5, -3.0, 0), o=(22, 62, 36.5), lens=50, f=0.3, focus=(2, -1.9, 0), shift=(-0.012, 0.175)),
    3: dict(aim=(4.0, -4.6, 1.4), o=(50, 36, 45), lens=50, f=0.6, focus=(4, -3.5, 0), shift=(-0.002, 0.178)),
}
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


def tape_mat(name, png, rough=0.2, back=(0.55, 0.55, 0.56)):
    m, nt, p = mat(name)
    N_, L = nt.nodes, nt.links
    tex = N_.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / png)); tex.interpolation = "Cubic"; tex.extension = "EXTEND"
    geo = N_.new("ShaderNodeNewGeometry")
    mix = N_.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs["B"].default_value = (*back, 1)
    L.new(geo.outputs["Backfacing"], mix.inputs["Factor"]); L.new(tex.outputs["Color"], mix.inputs["A"])
    L.new(mix.outputs["Result"], p.inputs["Base Color"])
    # the stressed white of a pressed letter is matt; the tape round it is gloss
    lum = N_.new("ShaderNodeRGBToBW"); L.new(tex.outputs["Color"], lum.inputs["Color"])
    mr = N_.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = rough; mr.inputs["To Max"].default_value = 0.55 if rough < 0.3 else rough
    L.new(lum.outputs["Val"], mr.inputs["Value"]); L.new(mr.outputs["Result"], p.inputs["Roughness"])
    p.inputs["Specular IOR Level"].default_value = 0.5
    p.inputs["Coat Weight"].default_value = 0.25 if rough < 0.3 else 0.0; p.inputs["Coat Roughness"].default_value = 0.08
    return m


def ribbon(name, pts, width, ox, y0, m, texlen, mirror=False, height=None, across=None, thick=0.03, yaw=0.0):
    """pts: [(x, z, s)]. mirror: the tape runs towards -x from ox, and still reads left to right."""
    na = across or max(4, int(width / 0.0125))
    vs, uvs = [], []
    for (x, z, s) in pts:
        for j in range(na + 1):
            v = j / na
            vs.append(((-x if mirror else x), (v - 0.5) * width, z))
            uvs.append(((1 - s / texlen) if mirror else s / texlen, v))
    fs = []
    for i in range(len(pts) - 1):
        for j in range(na):
            a = i * (na + 1) + j; b = a + na + 1
            fs.append((a, b, b + 1, a + 1) if not mirror else (a, a + 1, b + 1, b))
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], fs)
    uv = me.uv_layers.new(name="uv")
    for lp in me.loops:
        uv.data[lp.index].uv = uvs[lp.vertex_index]
    for p in me.polygons:
        p.use_smooth = True
    me.update()
    if me.polygons[0].normal.z < 0:
        me.flip_normals()
    ob = link(bpy.data.objects.new(name, me)); ob.data.materials.append(m)
    ob.location = (ox, y0, 0.031); ob.rotation_euler = (0, 0, yaw)
    if height:
        t = bpy.data.textures.new(name + "h", "IMAGE"); t.image = bpy.data.images.load(str(HERE / height)); t.extension = "EXTEND"
        t.image.colorspace_settings.name = "Non-Color"
        d = ob.modifiers.new("press", "DISPLACE"); d.texture = t; d.texture_coords = "UV"; d.strength = 0.050; d.mid_level = 0.0
    so = ob.modifiers.new("thick", "SOLIDIFY"); so.thickness = thick; so.offset = -1
    return ob


def roll(name, centre, r_out, r_in, width, ox, y0, side, lines):
    n = 160; vs = []; fs = []
    for i in range(n):
        a = 2 * math.pi * i / n
        for rr in (r_out, r_in):
            for y in (-width / 2, width / 2):
                vs.append((rr * math.cos(a), y, rr * math.sin(a)))
    for i in range(n):
        a = i * 4; b = ((i + 1) % n) * 4
        fs += [(a, b, b + 2, a + 2), (a + 1, a + 3, b + 3, b + 1), (a + 2, b + 2, b + 3, a + 3), (a, a + 1, b + 1, b)]
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], fs)
    ob = link(bpy.data.objects.new(name, me)); ob.location = (ox + centre[0], y0, centre[1] + 0.031)
    m, nt, p = mat(name); N_, L = nt.nodes, nt.links
    p.inputs["Base Color"].default_value = (*side, 1); p.inputs["Roughness"].default_value = 0.42
    tc = N_.new("ShaderNodeTexCoord"); sp = N_.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sp.inputs[0])
    le = N_.new("ShaderNodeVectorMath"); le.operation = "LENGTH"
    cb = N_.new("ShaderNodeCombineXYZ"); L.new(sp.outputs["X"], cb.inputs["X"]); L.new(sp.outputs["Z"], cb.inputs["Z"]); L.new(cb.outputs[0], le.inputs[0])
    mu = N_.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = 2 * math.pi / 0.05; L.new(le.outputs["Value"], mu.inputs[0])
    sn = N_.new("ShaderNodeMath"); sn.operation = "SINE"; L.new(mu.outputs[0], sn.inputs[0])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.5; bump.inputs["Distance"].default_value = 0.01
    L.new(sn.outputs[0], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    if lines:
        mr = N_.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -1; mr.inputs["To Min"].default_value = 0.72; mr.inputs["To Max"].default_value = 1.0
        L.new(sn.outputs[0], mr.inputs["Value"])
        mx = N_.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1; mx.inputs["A"].default_value = (*side, 1)
        L.new(mr.outputs["Result"], mx.inputs["B"]); L.new(mx.outputs["Result"], p.inputs["Base Color"])
    ob.data.materials.append(m)
    # hub
    hv = []; hf = []
    for i in range(n):
        a = 2 * math.pi * i / n
        for rr in (r_in, r_in - 0.16):
            for y in (-width / 2 - 0.02, width / 2 + 0.02):
                hv.append((rr * math.cos(a), y, rr * math.sin(a)))
    for i in range(n):
        a = i * 4; b = ((i + 1) % n) * 4
        hf += [(a, b, b + 2, a + 2), (a + 1, a + 3, b + 3, b + 1), (a + 2, b + 2, b + 3, a + 3), (a, a + 1, b + 1, b)]
    me = bpy.data.meshes.new(name + "hub"); me.from_pydata(hv, [], hf)
    hb = link(bpy.data.objects.new(name + "hub", me)); hb.location = ob.location
    m2, nt2, p2 = mat(name + "hub"); p2.inputs["Base Color"].default_value = (0.80, 0.78, 0.74, 1); p2.inputs["Roughness"].default_value = 0.35
    hb.data.materials.append(m2)


def scene(frame):
    me = bpy.data.meshes.new("table"); me.from_pydata([(-900, -900, 0), (900, -900, 0), (900, 900, 0), (-900, 900, 0)], [], [(0, 1, 2, 3)])
    tb = link(bpy.data.objects.new("table", me))
    m, nt, p = mat("table"); p.inputs["Base Color"].default_value = (*TABLE, 1); p.inputs["Roughness"].default_value = 0.9; p.inputs["Specular IOR Level"].default_value = 0.0
    N_, L = nt.nodes, nt.links
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 30; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.7
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    tb.data.materials.append(m)

    LN = geom.LENGTHS
    black = tape_mat("name", ".name-c.png")
    pts, c = geom.tail_profile(geom.NAME_FLAT)
    if frame in (1, 2, 3):
        ribbon("name", pts, 1.2, 0, 0, black, LN["name"], height=".name-h.png")
        roll("roll", c, geom.R - 0.03, 1.15, 1.19, 0, 0, (0.012, 0.012, 0.014), False)
    else:
        ribbon("name", [q for q in pts if q[2] <= geom.NAME_FLAT], 1.2, 0, 0, black, LN["name"], height=".name-h.png")
    hm = tape_mat("hello", ".hello-c.png")
    if frame == 2:
        ribbon("mail", geom.curl_profile(8.2, 7.0, 0.40), 1.2, MAIL[0] + geom.MAIL_LEN, MAIL[1], hm, LN["hello"], mirror=True, height=".hello-h.png")
    if frame == 3:
        ribbon("mail", geom.curl_profile(geom.MAIL_LEN - 0.02, 400, 0.00005), 1.2, MAIL[0] + geom.MAIL_LEN, MAIL[1], hm, LN["hello"], mirror=True, height=".hello-h.png")
        wm = tape_mat("nx", ".nx.png", rough=0.34, back=(0.8, 0.8, 0.8))
        wp, wc = geom.tail_profile(geom.NX_FLAT, r=2.3, step=0.03)
        ribbon("nx", wp, 1.9, NXO[0], NXO[1], wm, LN["nx"], across=8)
        roll("nxroll", wc, 2.3 - 0.03, 1.2, 1.89, NXO[0], NXO[1], (0.66, 0.65, 0.63), True)


def probe(frame, sc, co):
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    _, c = geom.tail_profile(geom.NAME_FLAT); _, wc = geom.tail_profile(geom.NX_FLAT, r=2.3, step=0.05)
    P = {"A cut": (0, 0, 0), "A Y": (0.62, 0, 0), "A K": (7.6, 0, 0), "A roll c": (c[0], -0.6, c[1]), "A roll top": (c[0], -0.6, 4.4), "A roll right": (c[0] + 2.2, -0.6, 2.2)}
    if frame > 1:
        P.update({"B left": (MAIL[0], MAIL[1], 0), "B right": (MAIL[0] + 11.2, MAIL[1], 0), "back": (BACK[0], BACK[1], 0)})
    if frame == 3:
        P.update({"C left": (NXO[0], NXO[1] - .95, 0), "C flat end": (NXO[0] + geom.NX_FLAT, NXO[1], 0), "C roll c": (NXO[0] + wc[0], NXO[1] - .95, wc[1]), "C roll top": (NXO[0] + wc[0], NXO[1] - .95, 5.2), "C roll right": (NXO[0] + wc[0] + 2.3, NXO[1] - .95, 2.3)})
    for nm, pt in P.items():
        v = world_to_camera_view(sc, co, Vector(pt))
        print(f"  f{frame} {nm:14s} x {v.x * W:7.0f}  y {(1 - v.y) * H:7.0f}")


def build(frame, quality):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 144 if final else 24
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
    bg.inputs["Color"].default_value = (0.90, 0.95, 1.0, 1); bg.inputs["Strength"].default_value = 0.40

    scene(frame)
    shot = SHOTS[frame]
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.2; sun.angle = math.radians(2.2); sun.color = (1.0, 0.96, 0.90)
    so = link(bpy.data.objects.new("sun", sun)); so.location = (-60, 45, 42); aim(so, (0, 0, 0))
    # a long soft box above and in front: the stripe of light along the gloss
    me = bpy.data.meshes.new("box"); me.from_pydata([(-70, 0, -8), (70, 0, -8), (70, 0, 8), (-70, 0, 8)], [], [(0, 1, 2, 3)])
    bo = link(bpy.data.objects.new("box", me)); bo.location = (10, 70, 26)
    bm, bnt, bp = mat("box"); em = bnt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 2.6
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
    exr = str(TMP / f"nx-tape-{frame}.exr")
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
    ramp = np.clip(np.arange(H, dtype=np.float32) / 380.0, 0, 1)                    # shade the top, where Instagram's white name and bars sit
    x = x * (0.74 + 0.26 * ramp * ramp * (3 - 2 * ramp))[:, None, None]
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
        exr = str(TMP / f"nx-tape-{fr}.exr")
        if quality == "probe":
            build(fr, quality); continue
        grade(exr if regrade else build(fr, quality), fr, quality)
