"""Renders the three pictures for this carousel with Blender's Python module (pip install bpy; run with python3.13).

A roll of woven labels for a made-up knitwear maker (Thrumwick), standing on its edge on a sand linen cloth:
navy with the name woven in ivory on the front, the same the other way round on the back (art/print.py).
  1  the ribbon folded into six rows, there and back
  2  two rows close up, the weave showing
  3  the roll itself with its cut tail drawn out

  python3.13 print.py
  python3.13 build.py <frame> [draft|final|probe]
writes art/render-0<frame>.jpg (1080x1350). Units are centimetres, so a real f/4 is aperture_fstop 0.04.
The type is set over the pictures in slide-0N.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix
import geom

HERE = Path(__file__).resolve().parent
W, H = 1080, 1350
TMP = Path(tempfile.gettempdir())
WID = geom.WID
THK = 0.05
CLOTH = (0.66, 0.54, 0.35)    # sand, linear
EXPOSURE = 1.0

SHOTS = {
    1: dict(loc=(-0.6, -58, 72), aim=(-0.6, 0.0, 0), lens=118, f=0.45, focus=(0, -3, 1.0), shift=(0, 0.145)),
    2: dict(loc=(-5.0, -19.9, 15.5), aim=(0.0, -0.4, 0.8), lens=70, f=0.085, focus=(0, 0, 1.1), shift=(0, 0.13)),
    3: dict(loc=(-0.66, -27, 20), aim=(-0.66, 0, 0), lens=61, f=0.14, focus=(-3, -1, 1.0), shift=(0, 0.215)),
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


def ribbon(scene):
    L = geom.layout(scene)
    P = np.array(L["pts"]); TH = np.array(L["hd"]); total = L["period"]; u0 = L["u0"]
    n = len(P)
    nrm = np.stack([-np.sin(TH), np.cos(TH)], 1)          # left of the heading: the back of the ribbon
    s = np.arange(n) * geom.DS
    lean = 0.012 * np.sin(s * 0.21 + scene) + 0.008 * np.sin(s * 0.57)     # the top edge wanders a little
    verts, faces, uvs, mats = [], [], [], []
    for side, off in ((0, -THK / 2), (1, THK / 2)):
        for i in range(n):
            bx, by = P[i] + nrm[i] * off
            tx, ty = P[i] + nrm[i] * (off + lean[i])
            verts.append((bx, by, 0.0)); verts.append((tx, ty, WID))
    def vid(side, i, top):
        return side * 2 * n + i * 2 + top
    for i in range(n - 1):
        ua, ub = (s[i] - u0) / total, (s[i + 1] - u0) / total
        faces.append((vid(0, i, 0), vid(0, i + 1, 0), vid(0, i + 1, 1), vid(0, i, 1)))
        uvs.append([(ua, 0), (ub, 0), (ub, 1), (ua, 1)]); mats.append(0)
        faces.append((vid(1, i + 1, 0), vid(1, i, 0), vid(1, i, 1), vid(1, i + 1, 1)))
        uvs.append([(1 - ub, 0), (1 - ua, 0), (1 - ua, 1), (1 - ub, 1)]); mats.append(1)
        faces.append((vid(0, i, 1), vid(0, i + 1, 1), vid(1, i + 1, 1), vid(1, i, 1)))
        uvs.append([(0, 0)] * 4); mats.append(2)
    for i in (0, n - 1):
        f = (vid(0, i, 0), vid(0, i, 1), vid(1, i, 1), vid(1, i, 0))
        faces.append(f if i == 0 else f[::-1]); uvs.append([(0, 0)] * 4); mats.append(2)
    me = bpy.data.meshes.new("ribbon"); me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name="uv")
    for poly, fu, mi in zip(me.polygons, uvs, mats):
        poly.material_index = mi; poly.use_smooth = mi != 2
        for j, li in enumerate(poly.loop_indices):
            uv.data[li].uv = fu[j]
    ob = link(bpy.data.objects.new("ribbon", me))
    ext = "EXTEND" if scene == 3 else "REPEAT"
    ob.data.materials.append(weave("front", f".rib-{scene}-front", ext))
    ob.data.materials.append(weave("back", f".rib-{scene}-back", ext))
    m, nt, pr = mat("edge"); pr.inputs["Base Color"].default_value = (0.30, 0.30, 0.42, 1); pr.inputs["Roughness"].default_value = 0.8
    ob.data.materials.append(m)
    return ob


def weave(name, stem, ext):
    m, nt, p = mat(name)
    N, L = nt.nodes, nt.links
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / (stem + ".png"))); tex.interpolation = "Cubic"; tex.extension = ext
    L.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.62
    p.inputs["Specular IOR Level"].default_value = 0.2
    p.inputs["Sheen Weight"].default_value = 0.15; p.inputs["Sheen Roughness"].default_value = 0.4
    ht = N.new("ShaderNodeTexImage"); ht.image = bpy.data.images.load(str(HERE / (stem + "-h.png"))); ht.image.colorspace_settings.name = "Non-Color"
    ht.interpolation = "Cubic"; ht.extension = ext
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.7; bump.inputs["Distance"].default_value = 0.008
    L.new(ht.outputs["Color"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def cloth():
    m, nt, p = mat("cloth")
    N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.92; p.inputs["Specular IOR Level"].default_value = 0.10
    p.inputs["Sheen Weight"].default_value = 0.3; p.inputs["Sheen Roughness"].default_value = 0.5
    geo = N.new("ShaderNodeNewGeometry")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (24, 24, 24); mp.inputs["Rotation"].default_value = (0, 0, math.radians(27))
    L.new(geo.outputs["Position"], mp.inputs["Vector"])
    wx = N.new("ShaderNodeTexWave"); wx.bands_direction = "X"; wx.inputs["Scale"].default_value = 1.0; wx.inputs["Distortion"].default_value = 1.6; wx.inputs["Detail"].default_value = 2
    wy = N.new("ShaderNodeTexWave"); wy.bands_direction = "Y"; wy.inputs["Scale"].default_value = 1.0; wy.inputs["Distortion"].default_value = 1.6; wy.inputs["Detail"].default_value = 2
    L.new(mp.outputs["Vector"], wx.inputs["Vector"]); L.new(mp.outputs["Vector"], wy.inputs["Vector"])
    mx = N.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
    L.new(wx.outputs["Fac"], mx.inputs[0]); L.new(wy.outputs["Fac"], mx.inputs[1])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 50; nz.inputs["Detail"].default_value = 3
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    add = N.new("ShaderNodeMath"); add.operation = "ADD"
    L.new(mx.outputs["Value"], add.inputs[0]); L.new(nz.outputs["Fac"], add.inputs[1])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35; bump.inputs["Distance"].default_value = 0.014
    L.new(add.outputs["Value"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    # the linen's slubs: a little colour in the threads
    cr = N.new("ShaderNodeMixRGB"); cr.inputs["Color1"].default_value = (*CLOTH, 1); cr.inputs["Color2"].default_value = (CLOTH[0] * 0.86, CLOTH[1] * 0.85, CLOTH[2] * 0.82, 1)
    L.new(mx.outputs["Value"], cr.inputs["Fac"]); L.new(cr.outputs["Color"], p.inputs["Base Color"])
    me = bpy.data.meshes.new("table"); s = 3000
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    ob = link(bpy.data.objects.new("table", me)); ob.data.materials.append(m)


def build(scene, quality, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 128 if final else 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 50
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1.0, 0.96, 0.90, 1); bg.inputs["Strength"].default_value = 0.20

    cloth()
    ribbon(scene)
    shot = SHOTS[scene]

    # key: a small window low on the left and in front, raking across the cloth so every row throws a shadow
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 60; key.size_y = 90
    key.energy = 8.5e6; key.color = (1.0, 0.95, 0.88)
    ko = link(bpy.data.objects.new("key", key)); ko.location = (-560, -330, 330); aim(ko, (0, 0, 0))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 500; fl.energy = 0.8e6; fl.color = (0.94, 0.95, 1.0)
    fo = link(bpy.data.objects.new("fill", fl)); fo.location = (420, -520, 380); aim(fo, (0, 0, 0))

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
        L = geom.layout(scene)
        for i in range(0, len(L["pts"]), int(0.5 / geom.DS)):
            for z in (0, WID):
                v = world_to_camera_view(sc, co, Vector((L["pts"][i][0], L["pts"][i][1], z)))
                print(f"  f{scene} s={i * geom.DS:6.1f} z={z:3.1f}  x {v.x * W:7.0f}  y {(1 - v.y) * H:7.0f}")
        return None
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region
    exr = str(TMP / f"nx-rib-{scene}.exr")
    sc.render.filepath = exr
    bpy.ops.render.render(write_still=True)
    return exr


def grade(exr, scene, quality):
    from PIL import Image
    img = bpy.data.images.load(exr)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(a)
    a = a.reshape(h, w, 4)[::-1, :, :3].astype(np.float32)
    if (w, h) != (W, H):
        a = np.stack([np.array(Image.fromarray(a[..., c], mode="F").resize((W, H), Image.BICUBIC)) for c in range(3)], -1)
    x = np.clip(a, 0, None) * EXPOSURE
    x = np.where(x > 0.70, 0.70 + (1 - np.exp(-(x - 0.70) / 0.30)) * 0.27, x)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3 + scene)
    x += rng.normal(0, 0.006, (H, W, 1)).astype(np.float32)
    out = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    dst = HERE / (f"render-0{scene}.jpg" if quality == "final" else f".d-{scene}.jpg")
    out.save(dst, quality=94, subsampling=0)
    print("wrote", dst, flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    scene = int(args[0])
    quality = args[1] if len(args) > 1 else "draft"
    if quality == "probe":
        build(scene, quality)
    else:
        grade(build(scene, quality), scene, quality)
        (HERE / f".done-{scene}-{quality}").write_text("ok")
