"""Renders the picture for this post with Blender's Python module (pip install bpy).

A gallery wall in plum paint. A gilt frame with a bone-white mount and nothing in it, lit by one
track spot. Beside it, nearer the camera and in focus, the wall label: Untitled (404), Page not found,
Still linked from the homepage. The camera stands to the right and looks along the wall, so the label
is big and the empty frame recedes behind it.

  python3 build.py [draft|final]     writes art/render-01.jpg (1080x1350). The type is set over it in slide-01.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy, bmesh
from mathutils import Vector

HERE = Path(__file__).resolve().parent
W, H = 1080, 1350
TMP = Path(tempfile.gettempdir())

WALL = (0.060, 0.016, 0.040)        # plum paint, linear RGB
GILT = (0.78, 0.62, 0.36)           # pale gold leaf
MOUNT = (0.80, 0.76, 0.68)          # bone-white board
BACK = (0.70, 0.66, 0.58)           # the backing board seen through the window, a shade down

# the picture: mount 0.62 x 0.80 m, window 0.40 x 0.54, frame moulding 0.10 wide
MOUNT_W, MOUNT_H = 0.62, 0.80
WIN_W, WIN_H, WIN_DROP = 0.40, 0.54, -0.015   # window a touch above centre, the bottom border heavier
FRAME_C = Vector((-0.78, 0.10))               # centre of the picture on the wall
LABEL_C = Vector((-0.20, -0.11))              # centre of the label
LABEL_W, LABEL_H = 0.200, 0.110

CAM = dict(loc=(0.12, -0.06, 0.40), aim=(-0.32, 0.10, 0.0), lens=28.0, f=6.0)
import os, json as _json
if os.environ.get("CAM"):
    CAM.update(_json.loads(os.environ["CAM"]))


def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def noise_into(nt, socket, scale, lo, hi, detail=4.0):
    N, L = nt.nodes, nt.links
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = detail
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = lo; mr.inputs["To Max"].default_value = hi
    L.new(nz.outputs["Fac"], mr.inputs["Value"]); L.new(mr.outputs["Result"], socket)
    return nz


def wall_mat():
    m, nt, p = mat("wall")
    p.inputs["Base Color"].default_value = (*WALL, 1)
    p.inputs["Specular IOR Level"].default_value = 0.3
    noise_into(nt, p.inputs["Roughness"], 30, 0.62, 0.78)
    N, L = nt.nodes, nt.links
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 420; nz.inputs["Detail"].default_value = 3
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.10; bump.inputs["Distance"].default_value = 0.0004
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def gilt_mat():
    m, nt, p = mat("gilt")
    N, L = nt.nodes, nt.links
    p.inputs["Metallic"].default_value = 1.0
    noise_into(nt, p.inputs["Roughness"], 90, 0.20, 0.42)
    # leaf rubbed thin in the hollows: the ground shows through, darker and duller
    ao = N.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.012
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (0.30, 0.25, 0.17, 1)
    mix.inputs["B"].default_value = (*GILT, 1)
    L.new(ao.outputs["AO"], mix.inputs["Factor"])
    L.new(mix.outputs["Result"], p.inputs["Base Color"])
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 260; nz.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08; bump.inputs["Distance"].default_value = 0.0005
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def board_mat(name, colour):
    m, nt, p = mat(name)
    p.inputs["Base Color"].default_value = (*colour, 1)
    p.inputs["Roughness"].default_value = 0.85
    p.inputs["Specular IOR Level"].default_value = 0.2
    N, L = nt.nodes, nt.links
    tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 2
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.06; bump.inputs["Distance"].default_value = 0.0002
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def label_mat():
    m, nt, p = mat("label")
    N, L = nt.nodes, nt.links
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / "label.png"))
    tex.interpolation = "Cubic"
    L.new(tex.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.7
    p.inputs["Specular IOR Level"].default_value = 0.25
    return m


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def mesh_obj(name, verts, faces, material, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces); me.update()
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    ob = link(bpy.data.objects.new(name, me))
    ob.data.materials.append(material)
    return ob


def profile():
    """Cross-section of the moulding: (u outward from the sight edge, v off the wall), metres.
    A small bead at the sight edge, a cove, a big round ovolo and a stepped outer edge."""
    pts = [(0.0, 0.010), (0.0, 0.020)]
    for t in np.linspace(0, math.pi, 9)[1:]:                           # sight-edge bead
        pts.append((0.006 - 0.006 * math.cos(t), 0.020 + 0.006 * math.sin(t)))
    pts.append((0.014, 0.020))
    for t in np.linspace(0, math.pi / 2, 7)[1:]:                       # cove, falling and rising
        pts.append((0.014 + 0.020 * math.sin(t), 0.020 - 0.006 * math.sin(t) + 0.004 * (1 - math.cos(t))))
    for t in np.linspace(math.pi, 0, 15)[1:]:                          # ovolo
        pts.append((0.060 + 0.026 * math.cos(t), 0.020 + 0.030 * math.sin(t)))
    pts += [(0.088, 0.026), (0.092, 0.026), (0.092, 0.018), (0.100, 0.016), (0.100, 0.0)]
    return pts


def frame(mt):
    """The moulding swept round the mount: one loop of the profile per side, mitred at the corners."""
    hw, hh = MOUNT_W / 2, MOUNT_H / 2
    cx, cy = FRAME_C
    P = profile()
    verts, faces = [], []
    sides = [((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))]
    for (ax, ay), (bx, by) in sides:
        base = len(verts)
        for u, v in P:
            verts.append((cx + ax * (hw + u), cy + ay * (hh + u), v))
            verts.append((cx + bx * (hw + u), cy + by * (hh + u), v))
        for i in range(len(P) - 1):
            a, b = base + 2 * i, base + 2 * (i + 1)
            faces.append((a, a + 1, b + 1, b))
    ob = mesh_obj("frame", verts, faces, mt, smooth=True)
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(ob.data); bm.free()
    return ob


def mount(mt_mount, mt_back):
    """Bone board 3 mm thick, with a bevelled window cut showing its white core, and the empty backing."""
    t, b = 0.003, 0.003
    cx, cy = FRAME_C
    hw, hh = MOUNT_W / 2, MOUNT_H / 2
    ww, wh = WIN_W / 2, WIN_H / 2
    oy = cy + WIN_DROP * -1
    z0 = 0.008
    outer = [(cx - hw, cy - hh), (cx + hw, cy - hh), (cx + hw, cy + hh), (cx - hw, cy + hh)]
    top = [(cx - ww - b, oy - wh - b), (cx + ww + b, oy - wh - b), (cx + ww + b, oy + wh + b), (cx - ww - b, oy + wh + b)]
    bot = [(cx - ww, oy - wh), (cx + ww, oy - wh), (cx + ww, oy + wh), (cx - ww, oy + wh)]
    verts = [(x, y, z0 + t) for x, y in outer] + [(x, y, z0 + t) for x, y in top] + [(x, y, z0) for x, y in bot]
    faces = []
    for i in range(4):
        j = (i + 1) % 4
        faces.append((i, j, 4 + j, 4 + i))
        faces.append((4 + i, 4 + j, 8 + j, 8 + i))
    m = mesh_obj("mount", verts, faces, mt_mount)
    bv = [(x, y, z0 - 0.0005) for x, y in outer]
    mesh_obj("backing", bv, [(0, 1, 2, 3)], mt_back)
    return m


def label(mt):
    cx, cy = LABEL_C
    hw, hh, t = LABEL_W / 2, LABEL_H / 2, 0.005
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, t / 2))
    card = bpy.context.active_object; card.scale = (LABEL_W, LABEL_H, t)
    edge = board_mat("edge", (0.78, 0.75, 0.70))
    card.data.materials.append(edge)
    face = mesh_obj("label-face", [(cx - hw, cy - hh, t + 0.0002), (cx + hw, cy - hh, t + 0.0002),
                                   (cx + hw, cy + hh, t + 0.0002), (cx - hw, cy + hh, t + 0.0002)],
                    [(0, 1, 2, 3)], mt)
    uv = face.data.uv_layers.new()
    for i, (u, v) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = (u, v)


def look(loc, aim, up=(0, 1, 0)):
    """Rotation that points a camera from loc at aim with the wall's up (+Y) as up in the picture."""
    from mathutils import Matrix
    f = (Vector(aim) - Vector(loc)).normalized()
    r = f.cross(Vector(up)).normalized()
    u = r.cross(f)
    return Matrix((r, u, -f)).transposed().to_euler()


def spot(name, loc, target, energy, size, blend, radius=0.03):
    d = bpy.data.lights.new(name, "SPOT")
    d.energy = energy; d.spot_size = math.radians(size); d.spot_blend = blend; d.shadow_soft_size = radius
    d.color = (1.0, 0.97, 0.92)
    ob = link(bpy.data.objects.new(name, d)); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return ob


def build(quality):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    final = quality == "final"
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 140 if final else 28
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = 0.0
    sc.render.image_settings.file_format = "PNG"
    world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.006, 0.004, 0.005, 1)

    # wall
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-0.6, 0, 0))
    wall = bpy.context.active_object; wall.scale = (5, 4, 1); wall.data.materials.append(wall_mat())
    frame(gilt_mat())
    mount(board_mat("mount", MOUNT), board_mat("back", BACK))
    label(label_mat())

    # light: one track spot on the picture from high up and in front, one smaller on the label
    spot("key", (-0.60, 1.55, 1.25), (FRAME_C.x - 0.02, FRAME_C.y - 0.02, 0), 230, 34, 0.55)
    spot("label", (0.12, 1.20, 0.95), (LABEL_C.x, LABEL_C.y + 0.02, 0), 30, 20, 0.7)
    # a faint fill from the room behind the camera
    fill = bpy.data.lights.new("fill", "AREA"); fill.energy = 6; fill.size = 2.0; fill.color = (1.0, 0.95, 0.95)
    f = link(bpy.data.objects.new("fill", fill)); f.location = (0.9, -0.2, 2.2)
    f.rotation_euler = (Vector((-0.5, 0, 0)) - f.location).to_track_quat("-Z", "Y").to_euler()

    cd = bpy.data.cameras.new("cam"); cd.lens = CAM["lens"]; cd.sensor_width = 36; cd.sensor_fit = "VERTICAL"
    cd.sensor_height = 36 * 1.25 * 0.8
    cam = link(bpy.data.objects.new("cam", cd)); cam.location = CAM["loc"]
    cam.rotation_euler = look(CAM["loc"], CAM["aim"])
    cd.dof.use_dof = True; cd.dof.aperture_fstop = CAM["f"]
    cd.dof.focus_distance = (Vector((LABEL_C.x, LABEL_C.y, 0.005)) - Vector(CAM["loc"])).length
    sc.camera = cam

    out = str(TMP / "nx-missing-raw.png")
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    return out


def finish(png, quality):
    from PIL import Image
    im = np.asarray(Image.open(png).convert("RGB")).astype(np.float32) / 255
    h, w = im.shape[:2]
    rng = np.random.default_rng(7)
    im = im + rng.normal(0, 0.012, (h, w, 1))
    im = np.clip(im, 0, 1)
    out = Image.fromarray((im * 255).astype(np.uint8))
    if quality != "final":
        out = out.resize((W, H), Image.LANCZOS)
    name = os.environ.get("OUT", "render-01.jpg")
    out.save(HERE / name, quality=95)
    print(name)


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "draft"
    finish(build(q), q)
