"""Renders the pictures for this Story with Blender's Python module (pip install bpy; run with python3.13).

A wall of yellow sticky notes in handwriting (a made-up firm's enquiries, quotes and bookings), shot from the left three ways:
  1  the wall of notes
  2  low under the bottom row: one note has let go and is in mid-air, its place on the wall empty
  3  the floor: every yellow note in a heap, and one blue Nexulabs note still on the wall
Prints: art/print.py.   python3.13 build.py <1|2|3|all> [draft|final|probe] [regrade]
writes art/render-0N.jpg (1080x1920). Units are centimetres. The type is set over it in slide-0N.html.
"""
import sys, math, random, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix, Euler

HERE = Path(__file__).resolve().parent
W, H = 1080, 1920
TMP = Path(tempfile.gettempdir())
WALL = (0.150, 0.132, 0.118)
YEL = (0.905, 0.760, 0.150)
BLU = (0.004, 0.017, 0.392)
EXPOSURE = 1.0
NS, PITCH, COLS, ROWS, TOP = 7.6, 8.5, 6, 6, 150.0
SLOT = (5, 1)                      # row, column of the note that falls

SHOTS = {
    1: dict(loc=(-40, -95, 140), aim=(0, 0, 140), lens=50, f=0.35, focus=(-18, 0, 135), shift=(-0.191, 0.104), key=(0, 0, 125)),
    2: dict(loc=(-30, -46, 80), aim=(-9, 0, 94), lens=40, f=0.16, focus=(-11.5, -8, 90), shift=(0.0, -0.06), key=(0, 0, 100)),
    3: dict(loc=(-17, -58, 7.0), aim=(2, 0, 19), lens=56, f=0.26, focus=(0, 0, 20), shift=(0.106, 0.088), key=(0, 0, 25)),
}
FALL = dict(loc=(-9.8, -4.8, 91.2), rot=(22, 27, -22))
NX = dict(x=1.0, top=22.0)


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


def paper(name, png, back):
    """Printed on the front, plain on the back, a fine fibre bump and a little light coming through."""
    m, nt, p = mat(name)
    N_, L = nt.nodes, nt.links
    tex = N_.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / png)); tex.interpolation = "Cubic"; tex.extension = "EXTEND"
    geo = N_.new("ShaderNodeNewGeometry")
    mix = N_.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["B"].default_value = (*back, 1)
    L.new(geo.outputs["Backfacing"], mix.inputs["Factor"]); L.new(tex.outputs["Color"], mix.inputs["A"])
    L.new(mix.outputs["Result"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.66; p.inputs["Specular IOR Level"].default_value = 0.22; p.inputs["Sheen Weight"].default_value = 0.12
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.7
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.10; bump.inputs["Distance"].default_value = 0.008
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    # a little translucency: a lifted note glows where the light is behind it
    tr = N_.new("ShaderNodeBsdfTranslucent"); L.new(mix.outputs["Result"], tr.inputs["Color"])
    ms = N_.new("ShaderNodeMixShader"); ms.inputs["Fac"].default_value = 0.12
    L.new(p.outputs["BSDF"], ms.inputs[1]); L.new(tr.outputs["BSDF"], ms.inputs[2])
    L.new(ms.outputs["Shader"], nt.nodes["Material Output"].inputs["Surface"])
    return m


def note_mesh(name, R, lift, twist, strip=1.7, centre=False, n=28, m=10):
    """A note that bends one way only. Local: x across, z down from the top edge, -y out into the room.
    The top `strip` cm is flat (the glue); below it the sheet leaves the wall at `lift` degrees and curls with radius R.
    twist makes one bottom corner lift more than the other."""
    vs, uvs = [], []
    for j in range(m + 1):
        u = j / m; x = (u - 0.5) * NS
        k = (1.0 / R) * (1 + twist * (u - 0.5) * 2)
        th0 = math.radians(lift) * (1 + twist * (u - 0.5) * 2)
        y = z = 0.0; ds = NS / n
        vs.append((x, 0, 0)); uvs.append((u, 1))
        for i in range(1, n + 1):
            s = i * ds
            th = 0.0 if s <= strip else th0 + (s - strip) * k
            y -= math.sin(th) * ds; z -= math.cos(th) * ds
            vs.append((x, y, z)); uvs.append((u, 1 - i / n))
    fs = []
    for j in range(m):
        for i in range(n):
            a = j * (n + 1) + i; b = (j + 1) * (n + 1) + i
            fs.append((a, a + 1, b + 1, b))
    if centre:
        c = Vector(vs[(m // 2) * (n + 1) + n // 2]); vs = [tuple(Vector(v) - c) for v in vs]
    me = bpy.data.meshes.new(name); me.from_pydata(vs, [], fs)
    uv = me.uv_layers.new(name="uv")
    for lp in me.loops:
        uv.data[lp.index].uv = uvs[lp.vertex_index]
    for p in me.polygons:
        p.use_smooth = True
    return me


def slot_xy(r, c):
    return (c - (COLS - 1) / 2) * PITCH, TOP - r * PITCH


def scene(frame):
    rng = random.Random(11)
    # wall, floor, skirting
    me = bpy.data.meshes.new("wall"); me.from_pydata([(-900, 0, -5), (900, 0, -5), (900, 0, 600), (-900, 0, 600)], [], [(0, 1, 2, 3)])
    wall = link(bpy.data.objects.new("wall", me))
    m, nt, p = mat("wall"); p.inputs["Base Color"].default_value = (*WALL, 1); p.inputs["Roughness"].default_value = 0.82; p.inputs["Specular IOR Level"].default_value = 0.25
    N_, L = nt.nodes, nt.links
    tc = N_.new("ShaderNodeTexCoord")
    nz = N_.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.2; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.62
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N_.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.16; bump.inputs["Distance"].default_value = 0.02
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    wall.data.materials.append(m)
    me = bpy.data.meshes.new("floor"); me.from_pydata([(-900, -900, 0), (900, -900, 0), (900, 0, 0), (-900, 0, 0)], [], [(0, 1, 2, 3)])
    fl = link(bpy.data.objects.new("floor", me))
    m2, nt2, p2 = mat("floor"); p2.inputs["Base Color"].default_value = (0.060, 0.054, 0.050, 1); p2.inputs["Roughness"].default_value = 0.36; p2.inputs["Specular IOR Level"].default_value = 0.4
    fl.data.materials.append(m2)
    me = bpy.data.meshes.new("skirt"); me.from_pydata([(-900, -1.4, 0), (900, -1.4, 0), (900, -1.4, 8.5), (-900, -1.4, 8.5), (900, 0, 8.5), (-900, 0, 8.5)], [], [(0, 1, 2, 3), (3, 2, 4, 5)])
    sk = link(bpy.data.objects.new("skirt", me)); sk.data.materials.append(m)

    back = YEL
    mats = [paper(f"n{i}", f".note-{i:02d}.png", back) for i in range(18)]
    hero = paper("hero", ".hero.png", back)
    blank = paper("blank", ".note-blank.png", back)
    order = list(range(18)) * 4; rng.shuffle(order)
    k = 0
    if frame in (1, 2):
        for r in range(ROWS):
            for c in range(COLS):
                x, z = slot_xy(r, c)
                is_slot = (r, c) == SLOT
                R = rng.uniform(9, 30); lift = rng.uniform(3, 13); tw = rng.uniform(-0.5, 0.5); roll = rng.uniform(-6.5, 6.5)
                dx, dz = rng.uniform(-1.1, 1.1), rng.uniform(-1.1, 1.1)
                mm = mats[(4 * r + c + (7 if c > 3 else 0)) % 18]; k += 1
                if is_slot and frame == 2:
                    continue
                if frame == 2 and c == 0:
                    mm = blank                      # cut by the left edge in this shot: no sliced writing
                if (frame == 1 and (r, c) == (1, 1)) or (frame == 2 and False):
                    mm = hero; R, lift = 9.5, 12
                ob = link(bpy.data.objects.new("note", note_mesh("note", R, lift, tw)))
                ob.data.materials.append(mm)
                ob.location = (x + dx, -0.03 - 0.02 * ((r * 7 + c * 5) % 11), z + dz); ob.rotation_euler = (0, math.radians(roll), 0)
    if frame == 2:
        ob = link(bpy.data.objects.new("fall", note_mesh("fall", 7.5, 0, 0.45, strip=0.0, centre=True, n=40, m=16)))
        ob.data.materials.append(hero)
        ob.location = FALL["loc"]; ob.rotation_euler = Euler([math.radians(a) for a in FALL["rot"]], "XYZ")
        # it is moving: a short fall and turn across the shutter
        sc = bpy.context.scene
        ob.location.z += 0.45; ob.rotation_euler.x -= math.radians(2.2); ob.keyframe_insert("location", frame=0); ob.keyframe_insert("rotation_euler", frame=0)
        ob.location.z -= 0.90; ob.rotation_euler.x += math.radians(4.4); ob.keyframe_insert("location", frame=2); ob.keyframe_insert("rotation_euler", frame=2)
        for fc in ob.animation_data.action.fcurves if hasattr(ob.animation_data.action, "fcurves") else []:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
        sc.frame_set(1); sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.16
    if frame == 3:
        nxm = paper("nx", ".nx.png", BLU)
        ob = link(bpy.data.objects.new("nx", note_mesh("nx", 30, 4.5, 0.3, n=40, m=16)))
        ob.data.materials.append(nxm); ob.location = (NX["x"], -0.03, NX["top"]); ob.rotation_euler = (0, math.radians(-1.6), 0)
        # the heap: every yellow note, laid on whatever is already there (a coarse height map)
        G = 1.0; hm = {}
        for i in range(72):
            x = rng.gauss(NX["x"] - 3, 13); y = -4.5 - abs(rng.gauss(0, 14))
            if i % 3 == 0:
                x = rng.gauss(NX["x"] - 2, 6); y = -5 - abs(rng.gauss(0, 5))
            cells = [(cx, cy) for cx in range(int((x - 4) / G), int((x + 4) / G) + 1) for cy in range(int((y - 4) / G), int((y + 4) / G) + 1)]
            h = max(hm.get(cc, 0.0) for cc in cells)
            up = rng.random() < 0.55
            R = rng.uniform(9, 26)
            ob = link(bpy.data.objects.new("heap", note_mesh("heap", R, 0, rng.uniform(-0.5, 0.5), strip=0.0, centre=True)))
            ob.data.materials.append(hero if i == 71 else mats[order[i % len(order)]])
            sag = NS * NS / (8 * R)
            ob.location = (x, y, h + (0.08 if up else sag + 0.08))
            ob.rotation_euler = Euler((math.radians((90 if up else -90) + rng.uniform(-7, 7)), math.radians(rng.uniform(-7, 7)), math.radians(rng.uniform(0, 360))), "XYZ")
            for cc in cells:
                hm[cc] = h + sag * 0.46 + 0.10


def build(frame, quality, region=None):
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
    bg.inputs["Color"].default_value = (0.92, 0.96, 1.0, 1); bg.inputs["Strength"].default_value = 0.16

    scene(frame)
    shot = SHOTS[frame]
    kx, ky, kz = shot["key"]
    # key: a small window to the left and a little above, raking along the wall, so every lifted edge throws a shadow
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 40; key.size_y = 70
    key.energy = 2.6e6; key.color = (1.0, 0.95, 0.88)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (kx - 300, ky - 210, kz + 150); aim(ko, (kx, ky, kz))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 300; fl.energy = 3.0e5; fl.color = (0.90, 0.96, 1.0)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (kx + 160, ky - 420, kz + 40); aim(fo, (kx, ky, kz))
    if frame == 3:
        fl.energy *= 2.4

    cam = bpy.data.cameras.new("cam"); co = link(bpy.data.objects.new("cam", cam)); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"])
    cam.lens = shot["lens"]; cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).dot((Vector(shot["aim"]) - co.location).normalized())
    cam.dof.aperture_fstop = shot["f"]
    if quality == "probe":
        from bpy_extras.object_utils import world_to_camera_view
        bpy.context.view_layer.update()
        P = {}
        if frame in (1, 2):
            for r, c in ((0, 0), (0, COLS - 1), (ROWS - 1, 0), (ROWS - 1, COLS - 1), SLOT):
                x, z = slot_xy(r, c)
                P[f"note {r},{c} TL"] = (x - NS / 2, 0, z); P[f"note {r},{c} BR"] = (x + NS / 2, 0, z - NS)
        if frame == 2:
            P["fall"] = FALL["loc"]
        if frame == 3:
            P["nx TL"] = (NX["x"] - NS / 2, 0, NX["top"]); P["nx BR"] = (NX["x"] + NS / 2, 0, NX["top"] - NS); P["skirt top"] = (0, -1.4, 8.5); P["floor"] = (0, -1.4, 0)
        for nm, pt in P.items():
            v = world_to_camera_view(sc, co, Vector(pt))
            print(f"  f{frame} {nm:14s} x {v.x * W:7.0f}  y {(1 - v.y) * H:7.0f}")
        return None
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region
    exr = str(TMP / f"nx-notes-{frame}.exr")
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
    x = x * (0.50 + 0.50 * ramp * ramp * (3 - 2 * ramp))[:, None, None]
    x = np.where(x > 0.60, 0.60 + (1 - np.exp(-(x - 0.60) / 0.40)) * 0.36, x)     # a soft shoulder
    x = np.clip(x, 0, 1)
    lum = (x * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
    x = np.clip(lum + (x - lum) * 1.10, 0, 1)
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
    regrade = "regrade" in args
    for fr in ([1, 2, 3] if which == "all" else [int(which)]):
        exr = str(TMP / f"nx-notes-{fr}.exr")
        if quality == "probe":
            build(fr, quality); continue
        grade(exr if regrade else build(fr, quality), fr, quality)
