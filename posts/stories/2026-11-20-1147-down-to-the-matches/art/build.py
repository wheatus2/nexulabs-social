"""Renders the pictures for this Story with Blender's Python module (pip install bpy; run with python3.13).

Branding for a made-up restaurant (Oxlip) on an olive cloth: a lilac matchbox, a stack of coasters, a table card.
Shot from the same side three ways, the props changing:
  1  the set: the matchbox leaning on the coasters, the Reserved card behind
  2  right up against the matchbox, its tray pulled out: black tray, lilac match heads
  3  the Oxlip box lying open in front of a blank white box standing behind it
Prints: art/print.py.   python3.13 build.py <1|2|3|all> [draft|final]
writes art/render-0N.jpg (1080x1920). Units are centimetres. The type is set over it in slide-0N.html.
"""
import sys, math, random, tempfile
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())
OLIVE = (0.062, 0.070, 0.012)
EXPOSURE = 1.0
BL, BW, BH = 5.3, 3.6, 1.6        # matchbox

SHOTS = {
    1: dict(loc=(-15, -46, 35), aim=(1.0, 2.0, 2.0), lens=50, f=0.5, focus=(0, -3, 1.5), shift=(0.0, 0.185)),
    2: dict(loc=(-9, -29, 17), aim=(0.0, -6.0, 1.0), lens=49, f=0.3, focus=(-1.5, -7.0, 1.3), shift=(0.010, 0.115)),
    3: dict(loc=(-12, -34, 20), aim=(0.9, -2.0, 1.8), lens=53, f=0.5, focus=(0, -4, 1.8), shift=(0.0, 0.10)),
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


def link(ob, parent=None):
    bpy.context.scene.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    return ob


def paper_nodes(nt, p, rough=0.6, scale=70, strength=0.10):
    N_, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = rough; p.inputs["Specular IOR Level"].default_value = 0.3
    p.inputs["Sheen Weight"].default_value = 0.12
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.7
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = strength; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])


_mats = {}
def card(col, name=None, rough=0.6):
    key = name or str(col)
    if key not in _mats:
        m, nt, p = mat(key); p.inputs["Base Color"].default_value = (*col, 1); paper_nodes(nt, p, rough)
        _mats[key] = m
    return _mats[key]


def printed(png, rough=0.55):
    if png not in _mats:
        m, nt, p = mat(png)
        tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / png)); tex.interpolation = "Cubic"; tex.extension = "EXTEND"
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
        paper_nodes(nt, p, rough)
        _mats[png] = m
    return _mats[png]


def panel(name, o, u, v, front, back, thick=0.05, parent=None):
    """A sheet of card: corners o, o+u, o+u+v, o+v. The printed face looks along u x v; the card thickens behind it."""
    o, u, v = Vector(o), Vector(u), Vector(v)
    me = bpy.data.meshes.new(name)
    me.from_pydata([o, o + u, o + u + v, o + v], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="uv")
    for lp, c in zip(me.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[lp.index].uv = c
    me.materials.append(front); me.materials.append(back)
    ob = link(bpy.data.objects.new(name, me), parent)
    s = ob.modifiers.new("s", "SOLIDIFY"); s.thickness = thick; s.offset = -1; s.material_offset = 1; s.material_offset_rim = 1
    return ob


def head_mat():
    if "head" in _mats:
        return _mats["head"]
    m, nt, p = mat("head")
    p.inputs["Base Color"].default_value = (0.42, 0.30, 0.86, 1); p.inputs["Roughness"].default_value = 0.72; p.inputs["Specular IOR Level"].default_value = 0.35
    N_, L = nt.nodes, nt.links
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 26; nz.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35; bump.inputs["Distance"].default_value = 0.012
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    _mats["head"] = m
    return m


def wood_mat():
    if "wood" in _mats:
        return _mats["wood"]
    m, nt, p = mat("wood")
    N_, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.62
    tc = N_.new("ShaderNodeTexCoord"); info = N_.new("ShaderNodeObjectInfo")
    mp = N_.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.2, 40, 40)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 3
    L.new(mp.outputs["Vector"], nz.inputs["Vector"]); L.new(info.outputs["Random"], nz.inputs["W"]) if "W" in nz.inputs else None
    ramp = N_.new("ShaderNodeMix"); ramp.data_type = "RGBA"
    ramp.inputs["A"].default_value = (0.80, 0.66, 0.42, 1); ramp.inputs["B"].default_value = (0.66, 0.50, 0.28, 1)
    L.new(nz.outputs["Fac"], ramp.inputs["Factor"]); L.new(ramp.outputs["Result"], p.inputs["Base Color"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.inputs["Distance"].default_value = 0.006
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    _mats["wood"] = m
    return m


def striker_mat(png):
    key = "st" + png
    if key in _mats:
        return _mats[key]
    m, nt, p = mat(key)
    N_, L = nt.nodes, nt.links
    tex = N_.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / png)); tex.extension = "EXTEND"
    L.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.7
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 160; nz.inputs["Detail"].default_value = 2
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.5; bump.inputs["Distance"].default_value = 0.01
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    _mats[key] = m
    return m


def match(parent, x0, y, z, length, rng, yaw=0.0):
    """One match along x from x0, its head at the far (+x) end."""
    me = bpy.data.meshes.new("stick"); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me); bm.free()
    st = link(bpy.data.objects.new("stick", me), parent)
    st.scale = (length, 0.21, 0.21); st.location = (x0 + length / 2, y, z); st.rotation_euler = (rng.uniform(-0.2, 0.2), 0, yaw)
    b = st.modifiers.new("b", "BEVEL"); b.width = 0.012; b.segments = 2
    st.data.materials.append(wood_mat())
    me = bpy.data.meshes.new("head"); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    for v in bm.verts:
        t = (v.co.x + 1) / 2                      # a bulb: fuller at the tip, drawn in where it meets the stick
        k = 0.80 + 0.20 * math.sin(math.pi * min(1, t * 1.15))
        v.co.y *= k; v.co.z *= k
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    hd = link(bpy.data.objects.new("head", me), parent)
    hd.scale = (0.34, 0.185 + rng.uniform(-0.01, 0.012), 0.185 + rng.uniform(-0.01, 0.012))
    hd.location = (x0 + length + 0.06 + (length / 2) * 0, y + math.sin(yaw) * length / 2, z); hd.rotation_euler = (rng.uniform(0, 3), 0, yaw)
    hd.data.materials.append(head_mat())


def matchbox(name, sleeve_png, striker_png, core, slide=0.0, tray_col=(0.012, 0.011, 0.011), matches=True, seed=1):
    """A matchbox with its origin at the centre of its base. The tray slides out along -x by `slide`."""
    root = link(bpy.data.objects.new(name, None))
    T = 0.055
    inner = card(core, "core" + name)
    top = printed(sleeve_png)
    side = striker_mat(striker_png)
    plain = card((0.50, 0.37, 0.90), "lilacplain") if sleeve_png == ".sleeve.png" else card((0.90, 0.88, 0.80), "whiteplain")
    panel("top", (-BL / 2, -BW / 2, BH), (BL, 0, 0), (0, BW, 0), top, inner, T, root)
    panel("bottom", (-BL / 2, BW / 2, 0), (BL, 0, 0), (0, -BW, 0), plain, inner, T, root)
    panel("front", (-BL / 2, -BW / 2, 0), (BL, 0, 0), (0, 0, BH), side, inner, T, root)
    panel("back", (BL / 2, BW / 2, 0), (-BL, 0, 0), (0, 0, BH), side, inner, T, root)
    # the tray
    tr = link(bpy.data.objects.new("tray", None), root); tr.location = (-slide, 0, 0)
    tc = card(tray_col, "tray" + name, 0.7)
    tl, tw, th, z0 = BL - 0.06, BW - 2 * T - 0.05, BH - 2 * T - 0.16, T + 0.02
    panel("floor", (-tl / 2, -tw / 2, z0 + 0.04), (tl, 0, 0), (0, tw, 0), tc, tc, 0.04, tr)
    panel("w1", (-tl / 2, -tw / 2, z0), (tl, 0, 0), (0, 0, th), tc, tc, 0.04, tr)
    panel("w2", (tl / 2, tw / 2, z0), (-tl, 0, 0), (0, 0, th), tc, tc, 0.04, tr)
    panel("w3", (-tl / 2, tw / 2, z0), (0, -tw, 0), (0, 0, th), tc, tc, 0.04, tr)
    panel("w4", (tl / 2, -tw / 2, z0), (0, tw, 0), (0, 0, th), tc, tc, 0.04, tr)
    if matches:
        rng = random.Random(seed)
        n = 13; pitch = (tw - 0.14) / n
        for layer in range(6):
            for i in range(n - (layer % 2)):
                y = -tw / 2 + 0.07 + pitch * (i + 0.5 + 0.5 * (layer % 2)) + rng.uniform(-0.012, 0.012)
                z = z0 + 0.04 + 0.115 + layer * 0.205
                L_ = 4.30 + rng.uniform(-0.05, 0.05)
                # heads at the -x end (the end that comes out): build towards +x then turn round
                match(tr, 0, 0, 0, L_, rng) if False else None
                me_parent = link(bpy.data.objects.new("m", None), tr)
                me_parent.location = (-tl / 2 + 0.60 + L_ + rng.uniform(-0.05, 0.05), y, z); me_parent.rotation_euler = (0, 0, math.pi + (rng.uniform(-0.012, 0.012) if layer == 5 else 0))
                match(me_parent, 0, 0, 0, L_, rng)
    return root


def coaster(z, rng):
    r, t = 4.7, 0.17
    bm = bmesh.new(); n = 160
    top = [bm.verts.new((r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), t)) for i in range(n)]
    bot = [bm.verts.new((v.co.x, v.co.y, 0)) for v in top]
    ft = bm.faces.new(top); bm.faces.new(bot[::-1])
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((bot[i], bot[j], top[j], top[i])); f.material_index = 1; f.smooth = True
    uvl = bm.loops.layers.uv.new("uv")
    for lp in ft.loops:
        lp[uvl].uv = (0.5 + lp.vert.co.x / (2 * r), 0.5 + lp.vert.co.y / (2 * r))
    me = bpy.data.meshes.new("coaster"); bm.to_mesh(me); bm.free()
    me.materials.append(printed(".coaster.png", 0.72)); me.materials.append(card((0.78, 0.72, 0.58), "pulp", 0.8))
    ob = link(bpy.data.objects.new("coaster", me))
    b = ob.modifiers.new("b", "BEVEL"); b.width = 0.03; b.segments = 2; b.limit_method = "ANGLE"; b.angle_limit = math.radians(60)
    ob.location.z = z
    return ob


def tent(loc, yaw):
    root = link(bpy.data.objects.new("tent", None)); root.location = loc; root.rotation_euler = (0, 0, yaw)
    w, h, half = 10.0, 7.4, 2.3
    zt = math.sqrt(h * h - half * half)
    cream = card((0.84, 0.79, 0.64), "cream")
    panel("f", (-w / 2, -half, 0), (w, 0, 0), (0, half, zt), printed(".tent.png"), cream, 0.05, root)
    panel("b", (w / 2, half, 0), (-w, 0, 0), (0, -half, zt), cream, cream, 0.05, root)
    return root


def scene(frame):
    # the cloth: a sweep
    prof = [(-900, 0), (190, 0)] + [(190 + 80 * math.sin(math.radians(a)), 80 - 80 * math.cos(math.radians(a))) for a in range(5, 91, 5)] + [(270, 1500)]
    vs = [(sx * 2500, y, z) for y, z in prof for sx in (-1, 1)]
    fs = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(prof) - 1)]
    me = bpy.data.meshes.new("sweep"); me.from_pydata(vs, [], fs)
    for p in me.polygons:
        p.use_smooth = True
    sw = link(bpy.data.objects.new("sweep", me))
    m, nt, p = mat("sweep"); p.inputs["Base Color"].default_value = (*OLIVE, 1); p.inputs["Roughness"].default_value = 0.9; p.inputs["Specular IOR Level"].default_value = 0.04
    p.inputs["Sheen Weight"].default_value = 0.0
    N_, L = nt.nodes, nt.links
    tc = N_.new("ShaderNodeTexCoord")
    hs = []
    for ax in (0, 1):                               # a plain weave: threads both ways
        mp = N_.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, math.radians(90 * ax + 8))
        wv = N_.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 7.0; wv.inputs["Distortion"].default_value = 0.6; wv.inputs["Detail"].default_value = 1.5
        L.new(tc.outputs["Object"], mp.inputs["Vector"]); L.new(mp.outputs["Vector"], wv.inputs["Vector"]); hs.append(wv)
    mx = N_.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
    L.new(hs[0].outputs["Fac"], mx.inputs[0]); L.new(hs[1].outputs["Fac"], mx.inputs[1])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.22 if frame != 1 else 0.12; bump.inputs["Distance"].default_value = 0.02
    L.new(mx.outputs["Value"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    sw.data.materials.append(m)

    rng = random.Random(4)
    if frame == 1:
        nco = 8
        for i in range(nco):
            c = coaster(i * 0.172, rng)
            cx, cy = (0, 3.0) if frame == 1 else (5.6, 7.0)
            c.location.x = cx + (rng.uniform(-0.25, 0.25) if i < nco - 1 else 0); c.location.y = cy + (rng.uniform(-0.25, 0.25) if i < nco - 1 else 0)
            c.rotation_euler = (0, 0, math.radians(rng.uniform(0, 360) if i < nco - 1 else (-12 if frame == 1 else -20)))
        if frame == 1:
            tent((5.0, 15.0, 0), math.radians(-9))
    if frame == 1:
        # the matchbox leaning on the stack: near long edge on the cloth, underside on the rim
        t = math.radians(27.5); top = nco * 0.172
        ye = 3.0 - 4.7 + 0.55
        yn = ye - BW * math.cos(t)
        mb = matchbox("ox", ".sleeve.png", ".striker.png", (0.86, 0.84, 0.78))
        mb.rotation_euler = (t, 0, 0)
        # origin is the centre of the base: put the near bottom edge on (y = yn, z = 0)
        mb.location = (0.9, yn + (BW / 2) * math.cos(t), (BW / 2) * math.sin(t) + 0.02)
    if frame == 2:
        mb = matchbox("ox", ".sleeve.png", ".striker.png", (0.86, 0.84, 0.78), slide=2.9)
        mb.rotation_euler = (0, 0, math.radians(24)); mb.location = (1.6, -6.0, 0)
    if frame == 3:
        mb = matchbox("ox", ".sleeve.png", ".striker.png", (0.86, 0.84, 0.78))
        mb.rotation_euler = (math.radians(90 - 5), 0, math.radians(-17)); mb.location = (-1.6, -6.0, BW / 2)
        bl = matchbox("blank", ".blank.png", ".striker-blank.png", (0.86, 0.84, 0.78), tray_col=(0.80, 0.78, 0.70), matches=False)
        # standing on its long side, its plain face to the camera
        bl.rotation_euler = (math.radians(90 - 5), 0, math.radians(-6)); bl.location = (3.6, 3.4, BW / 2)


def build(frame, quality):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()
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
    bg.inputs["Color"].default_value = (1.0, 0.97, 0.9, 1); bg.inputs["Strength"].default_value = 0.10

    scene(frame)
    shot = SHOTS[frame]
    # key: a small window low on the left and behind, so every edge throws a shadow towards the camera's right
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 50; key.size_y = 60
    key.energy = 2.9e6; key.color = (1.0, 0.95, 0.88)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (-290, -90, 250); aim(ko, (0, 0, 2))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 320; fl.energy = 4.6e5; fl.color = (0.94, 0.97, 1.0)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (120, -420, 260); aim(fo, (0, 0, 2))

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]; cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).dot((Vector(shot["aim"]) - co.location).normalized())
    cam.dof.aperture_fstop = shot["f"]
    exr = str(TMP / f"nx-match-{frame}.exr")
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
    x = np.where(x > 0.60, 0.60 + (1 - np.exp(-(x - 0.60) / 0.40)) * 0.36, x)
    x = np.clip(x, 0, 1)
    lum = (x * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    x = np.clip(lum + (x - lum) * 1.12, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3 + frame)
    x += rng.normal(0, 0.007, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"render-{frame:02d}.jpg" if quality == "final" else f".draft-{frame:02d}.jpg")
    out.save(dst, quality=95, subsampling=0)
    print("wrote", dst)


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    which = args[0] if args else "all"
    quality = args[1] if len(args) > 1 else "draft"
    for fr in ([1, 2, 3] if which == "all" else [int(which)]):
        exr = str(TMP / f"nx-match-{fr}.exr")
        grade(exr if "regrade" in args else build(fr, quality), fr, quality)
