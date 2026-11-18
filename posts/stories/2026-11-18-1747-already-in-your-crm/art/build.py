"""Renders the three pictures for this Story with Blender's Python module
(python3.13 -m pip install bpy brotli pillow numpy Hershey-Fonts playwright --break-system-packages; python3.13 print.py first).

One duplicate book on a blue table. The white top sheet is the website enquiry, filled in by hand;
the yellow sheet under it is the CRM copy, with the same writing come through in carbon.
  1  the bottom of the top sheet rolled back, the last line of the copy showing under it
  2  the top sheet lifted right up, the whole copy in view, close
  3  the top sheet torn out and laid across the copy, the same number on both

  python3.13 build.py <frame 1|2|3|all> [draft|final] [regrade]
writes art/render-0N.jpg (1080x1920). The type is set over it in slide-0N.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())
SW, SL, PADH = 0.105, 0.148, 0.0065          # sheet width, length, pad thickness (metres)
TABLE = (0.014, 0.050, 0.560)
PAPER = (0.905, 0.890, 0.835)


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def box(name, size, loc, material, bevel=0.0):
    sx, sy, sz = size
    v = [(x * sx / 2, y * sy / 2, z * sz / 2) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f)
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.location = loc; me.materials.append(material)
    if bevel:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 3
    return ob


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


def paper(name, image, press=None, back=PAPER):
    """Uncoated paper: the print on the face, plain on the back, a fine tooth, and the pen pressed in."""
    m, nt, p = mat(name)
    N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.78
    p.inputs["Specular IOR Level"].default_value = 0.28
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / image)); tex.extension = "EXTEND"
    geo = N.new("ShaderNodeNewGeometry")
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs["B"].default_value = (*back, 1)
    L.new(tex.outputs["Color"], mix.inputs["A"]); L.new(geo.outputs["Backfacing"], mix.inputs["Factor"])
    L.new(mix.outputs["Result"], p.inputs["Base Color"])
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2600; nz.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    b = N.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.10; b.inputs["Distance"].default_value = 0.00012
    L.new(nz.outputs["Fac"], b.inputs["Height"])
    out = b.outputs["Normal"]
    if press:
        pt = N.new("ShaderNodeTexImage"); pt.image = bpy.data.images.load(str(HERE / press)); pt.image.colorspace_settings.name = "Non-Color"
        inv = N.new("ShaderNodeMath"); inv.operation = "MULTIPLY"; inv.inputs[1].default_value = -1.0
        front = N.new("ShaderNodeMath"); front.operation = "SUBTRACT"; front.inputs[0].default_value = 1.0
        L.new(geo.outputs["Backfacing"], front.inputs[1])
        fr = N.new("ShaderNodeMath"); fr.operation = "MULTIPLY"; L.new(pt.outputs["Color"], fr.inputs[0]); L.new(front.outputs[0], fr.inputs[1])
        L.new(fr.outputs[0], inv.inputs[0])
        b2 = N.new("ShaderNodeBump"); b2.inputs["Strength"].default_value = 0.3; b2.inputs["Distance"].default_value = 0.00012
        L.new(inv.outputs[0], b2.inputs["Height"]); L.new(out, b2.inputs["Normal"]); out = b2.outputs["Normal"]
    L.new(out, p.inputs["Normal"])
    return m


def sheet(name, material, bend=None, nx=140, ny=320, z0=0.0, torn=False, wave=0.0):
    """A sheet lying in x,y (top edge at +y). bend = (distance from the top edge, tilt in degrees, theta(s))
    rolls everything beyond that line; it never stretches the paper."""
    verts, faces, uvs = [], [], []
    if bend:
        dtop, tilt, curve = bend
        P0 = Vector((0.0, SL / 2 - dtop)); n = Vector((math.sin(math.radians(tilt)), -math.cos(math.radians(tilt))))
        # integrate the profile once
        S = np.linspace(0, SL * 1.3, 2600); ds = S[1] - S[0]
        th = np.array([curve(s) for s in S])
        A = np.concatenate([[0], np.cumsum(np.cos(th[:-1]) * ds)]); Z = np.concatenate([[0], np.cumsum(np.sin(th[:-1]) * ds)])
    for j in range(ny + 1):
        for i in range(nx + 1):
            u, v = i / nx, j / ny
            x, y = (u - 0.5) * SW, (v - 0.5) * SL
            if torn and j == ny:
                y -= 0.00035 * (0.5 + 0.5 * math.cos(2 * math.pi * x / 0.0019))
            z = z0 + wave * math.sin(x * 55 + 0.6) * math.sin(y * 31 + 1.1)
            if bend:
                d = (Vector((x, y)) - P0).dot(n)
                if d > 0:
                    a = float(np.interp(d, S, A)); zz = float(np.interp(d, S, Z))
                    q = Vector((x, y)) - n * d + n * a
                    x, y, z = q.x, q.y, z + zz
            verts.append((x, y, z)); uvs.append((u, v))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name="uv")
    for poly in me.polygons:
        poly.use_smooth = True
        for li in poly.loop_indices:
            uv.data[li].uv = uvs[me.loops[li].vertex_index]
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return ob


def roll(R0, tighten, tmax):
    return lambda s: min(math.radians(tmax), (s / R0) * (1 + tighten * s))


def stand(R0, t1, lean):
    def f(s):
        t = s / R0
        if t > math.radians(t1):
            t = math.radians(t1) + (s - R0 * math.radians(t1)) * lean
        return t
    return f


SHOTS = {
    1: dict(target=(0.0, -0.015, 0.0), dist=0.62, az=26, el=42, lens=85, f=20, focus=(0.01, -0.058, 0.008), shift=(0.03, 0.225)),
    2: dict(target=(0.0, 0.0, 0.0), dist=0.65, az=26, el=52, lens=85, f=22, focus=(0.0, 0.02, 0.007), shift=(0.012, -0.175)),
    3: dict(target=(0.0, 0.0, 0.0), dist=0.715, az=26, el=58, lens=85, f=20, focus=(0.0, 0.0, 0.007), shift=(-0.02, 0.19)),
}


def build(frame, quality):
    shot = SHOTS[frame]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 128 if final else 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 8.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.10, 0.16, 0.50, 1)
    bg.inputs["Strength"].default_value = 0.08

    # the table runs up into a sweep so there is no horizon
    prof = [(-4.0, 0.0), (0.55, 0.0)]
    R = 0.45
    for j in range(1, 25):
        a = math.pi / 2 * j / 24
        prof.append((0.55 + R * math.sin(a), R * (1 - math.cos(a))))
    prof.append((1.0, 4.0))
    verts = [(x, y, z) for (y, z) in prof for x in (-6.0, 6.0)]
    faces = [(2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2) for j in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    sweep = bpy.data.objects.new("sweep", me); sc.collection.objects.link(sweep)
    sm, snt, sp = mat("sweep")
    sp.inputs["Base Color"].default_value = (*TABLE, 1)
    sp.inputs["Roughness"].default_value = 0.85
    sp.inputs["Specular IOR Level"].default_value = 0.15
    nz = snt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 3
    bump = snt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.04; bump.inputs["Distance"].default_value = 0.0002
    snt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); snt.links.new(bump.outputs["Normal"], sp.inputs["Normal"])
    me.materials.append(sm)

    # the book: grey board, a block of leaves (white, yellow, white, yellow...), cloth tape along the top
    bm, bnt, bp = mat("board"); bp.inputs["Base Color"].default_value = (0.20, 0.19, 0.17, 1); bp.inputs["Roughness"].default_value = 0.9
    box("board", (SW + 0.002, SL + 0.002, 0.0014), (0, 0, 0.0007), bm)
    lm, lnt, lp = mat("leaves"); lp.inputs["Roughness"].default_value = 0.85
    tc = lnt.nodes.new("ShaderNodeTexCoord"); sep = lnt.nodes.new("ShaderNodeSeparateXYZ"); lnt.links.new(tc.outputs["Object"], sep.inputs[0])
    wv = lnt.nodes.new("ShaderNodeMath"); wv.operation = "MULTIPLY"; wv.inputs[1].default_value = 2 * math.pi / 0.00042
    lnt.links.new(sep.outputs["Z"], wv.inputs[0])
    sn = lnt.nodes.new("ShaderNodeMath"); sn.operation = "SINE"; lnt.links.new(wv.outputs[0], sn.inputs[0])
    mr = lnt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -0.3; mr.inputs["From Max"].default_value = 0.3
    lnt.links.new(sn.outputs[0], mr.inputs["Value"])
    mx = lnt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["A"].default_value = (*PAPER, 1); mx.inputs["B"].default_value = (0.86, 0.66, 0.07, 1)
    lnt.links.new(mr.outputs[0], mx.inputs["Factor"]); lnt.links.new(mx.outputs["Result"], lp.inputs["Base Color"])
    top = 0.0014 + PADH
    box("leaves", (SW, SL, PADH), (0, 0, 0.0014 + PADH / 2), lm)
    tm, tnt, tp = mat("tape"); tp.inputs["Base Color"].default_value = (0.012, 0.014, 0.022, 1); tp.inputs["Roughness"].default_value = 0.85; tp.inputs["Specular IOR Level"].default_value = 0.2
    wz = tnt.nodes.new("ShaderNodeTexWave"); wz.inputs["Scale"].default_value = 2600; wz.inputs["Distortion"].default_value = 0.4
    tb = tnt.nodes.new("ShaderNodeBump"); tb.inputs["Strength"].default_value = 0.35; tb.inputs["Distance"].default_value = 0.0002
    tnt.links.new(wz.outputs["Fac"], tb.inputs["Height"]); tnt.links.new(tb.outputs["Normal"], tp.inputs["Normal"])
    box("tape", (SW + 0.0012, 0.0086, top + 0.0009), (0, SL / 2 - 0.0086 / 2 + 0.0006, (top + 0.0009) / 2), tm, bevel=0.0004)

    copy = sheet("copy", paper("copy", ".copy.png", back=(0.86, 0.66, 0.07)), z0=top + 0.00012, nx=20, ny=20)
    white = paper("white", ".top.png", press=".press.png")
    if frame == 1:
        sheet("top", white, bend=(0.1135, -4, roll(0.0082, 9.0, 205)), z0=top + 0.00035, wave=0.00012)
    elif frame == 2:
        pass   # the top copy has been torn out; what is left is the copy that stays in the book
    else:
        t = sheet("top", white, bend=(0.118, 28, roll(0.05, 4.0, 22)), z0=0.0, torn=True, wave=0.00010)
        t.location = (0.002, -0.044, top + 0.0006); t.rotation_euler = (0, 0, math.radians(4.0))

    area("key", (-1.10, 0.77, 0.62), (0, 0, 0.0), 0.40, 78, (1.0, 0.97, 0.93))
    area("fill", (0.50, -0.55, 0.45), (0, 0, 0.0), 1.0, 4.0, (0.94, 0.97, 1.0))
    area("top", (0.0, 0.1, 0.9), (0, 0, 0.0), 1.2, 6.0, (1, 1, 1))

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
    cam.clip_start = 0.01

    exr = str(TMP / f"nx-dup-{frame}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def pixels(exr):
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32), w, h


EXPOSURE = 0.62


def grade(exr, frame, quality):
    """A film curve, the top of the frame falling off (Instagram's white name sits there), and grain."""
    from PIL import Image
    a, w, h = pixels(exr)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    a = np.clip(a, 0, None)
    x = a * EXPOSURE
    x = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    yy, xx = np.mgrid[0:H, 0:W]
    top = np.clip(1 - yy / 330.0, 0, 1) ** 1.6
    x *= (1 - 0.40 * top)[..., None]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    x *= (1 - 0.10 * np.clip(r - 0.6, 0, 1) ** 1.5)[..., None]
    rng = np.random.default_rng(frame)
    x += rng.normal(0, 0.007, (H, W, 1)).astype(np.float32)
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
        exr = str(TMP / f"nx-dup-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
