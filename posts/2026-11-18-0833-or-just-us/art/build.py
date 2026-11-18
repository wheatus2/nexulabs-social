"""Renders the pictures for this post with Blender's Python module (pip install bpy brotli).

White DL window envelopes (22 x 11 cm, printed by art/sheet.py) on a petrol-blue table, shot from the same side:
  1  three envelopes from three made-up companies as they landed, one on another: domain, hosting, email
  2  from straight above: the same three fanned like a hand of cards
  3  one envelope on its own, from Nexulabs: "About your website, hosting, domain and email."

  python3.13 build.py <frame 1|2|3|all> [draft|final] [regrade]
writes art/render-0N.jpg (1080x1350). Units are centimetres. The type is set over it in slide-0N.html.
"""
import sys, math, tempfile
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
W, H = 1080, 1350
TMP = Path(tempfile.gettempdir())
TABLE = (0.0044, 0.125, 0.185)      # petrol blue, linear RGB
EXPOSURE = 1.3
EW, EH, THICK = 22.0, 11.0, 0.11

# centre x, y, turn in degrees, print, bow (how far the middle arches), lift of the near right corner
PILE = [dict(c=(-0.6, 14.9), yaw=-4.0, img="env-1.png", bow=0.10, curl=0.2, seed=1),
        dict(c=(0.5, 7.4), yaw=0.5, img="env-2.png", bow=0.18, curl=0.3, seed=2),
        dict(c=(-0.2, 0.0), yaw=4.5, img="env-3.png", bow=0.16, curl=0.4, seed=3)]
ONE = [dict(c=(0.0, 0.0), yaw=-9.0, img="env-nx.png", bow=0.18, curl=0.4, seed=4)]


def fan():
    """Frame 2: the same three held like a hand of cards, all three sharing their top right corner, 30 degrees apart.
    Seen from straight above at 31 px to the cm, so the frame is 34.84 x 43.55 cm with its middle at the origin.
    The top card runs off the bottom of the frame between its subject line and its window."""
    px, py = 32.26 - 17.42, 6.5 - 21.775
    out = []
    for spec, th in zip(PILE, (-60.0, -30.0, 0.0)):
        a = math.radians(th); dx, dy = -11.0, -5.5
        out.append(dict(spec, c=(px + dx * math.cos(a) - dy * math.sin(a), py + dx * math.sin(a) + dy * math.cos(a)), yaw=th, curl=0.0))
    return out


SHOTS = {
    1: dict(loc=(8.0, -24.0, 50.0), aim=(0.5, 7.5, 0.0), lens=43.5, f=0.3, focus=(0.5, 6.0, 0.3), shift=(-0.045, 0.125)),
    2: dict(loc=(0.0, 0.0, 120.0), aim=(0.0, 0.0, 0.0), up=(0, 1, 0), lens=82.66, f=0.5, focus=(0.0, 0.0, 0.2), shift=(0.0, 0.0),
            key=(430, -330, 120)),
    3: dict(loc=(8.0, -23.0, 24.0), aim=(0.0, 0.5, 0.0), lens=28.3, f=0.09, focus=(-2.0, 1.0, 0.2), shift=(0.0, -0.14)),
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


def paper_mat(img, name):
    """Matt envelope paper with the print on it; the window film is glossy."""
    m, nt, p = mat(name)
    N, L = nt.nodes, nt.links
    geo = N.new("ShaderNodeNewGeometry")
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(str(HERE / img)); tex.interpolation = "Cubic"; tex.extension = "EXTEND"
    L.new(tex.outputs["Color"], p.inputs["Base Color"])
    msk = N.new("ShaderNodeTexImage"); msk.image = bpy.data.images.load(str(HERE / "env-mask.png")); msk.image.colorspace_settings.name = "Non-Color"
    msk.extension = "EXTEND"
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.74; mr.inputs["To Max"].default_value = 0.16
    L.new(msk.outputs["Color"], mr.inputs["Value"]); L.new(mr.outputs["Result"], p.inputs["Roughness"])
    p.inputs["Specular IOR Level"].default_value = 0.3
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 140; nz.inputs["Detail"].default_value = 6
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    inv = N.new("ShaderNodeMapRange"); inv.inputs["To Min"].default_value = 0.07; inv.inputs["To Max"].default_value = 0.0
    L.new(msk.outputs["Color"], inv.inputs["Value"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Distance"].default_value = 0.01
    L.new(inv.outputs["Result"], bump.inputs["Strength"])
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


def table_mat():
    m, nt, p = mat("table")
    N, L = nt.nodes, nt.links
    p.inputs["Roughness"].default_value = 0.8
    p.inputs["Specular IOR Level"].default_value = 0.3
    geo = N.new("ShaderNodeNewGeometry")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.25; nz.inputs["Detail"].default_value = 3
    L.new(geo.outputs["Position"], nz.inputs["Vector"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.95; mr.inputs["To Max"].default_value = 1.03
    L.new(nz.outputs["Fac"], mr.inputs["Value"])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1
    mix.inputs["A"].default_value = (*TABLE, 1)
    comb = N.new("ShaderNodeCombineColor")
    for k in ("Red", "Green", "Blue"):
        L.new(mr.outputs["Result"], comb.inputs[k])
    L.new(comb.outputs["Color"], mix.inputs["B"]); L.new(mix.outputs["Result"], p.inputs["Base Color"])
    fine = N.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value = 110; fine.inputs["Detail"].default_value = 6
    L.new(geo.outputs["Position"], fine.inputs["Vector"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.05; bump.inputs["Distance"].default_value = 0.02
    L.new(fine.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


class Envelope:
    """A stiff envelope with a letter in it: a shallow pillow, arched a little along its length, one corner lifted.
    It is laid as a rigid plate on whatever is already there (the table and the envelopes under it)."""

    def __init__(self, spec, under):
        self.s = spec
        a = math.radians(spec["yaw"]); self.ca, self.sa = math.cos(a), math.sin(a)
        self.plane = (0.0, 0.0, 0.0)
        # rest it: least-squares plane through what is underneath, then lifted clear
        pts = []
        for i in range(23):
            for j in range(12):
                u, v = i / 22, j / 11
                X, Y = self.world(u, v)
                sup = max([0.0] + [e.top(X, Y) for e in under])
                pts.append((X, Y, sup - self.under(u, v)))
        A = np.array([[x, y, 1] for x, y, _ in pts]); z = np.array([p[2] for p in pts])
        if under:
            sol = np.linalg.lstsq(A, z, rcond=None)[0]
            sol[2] += float(np.max(z - A @ sol)) + 0.004
            self.plane = tuple(sol)

    def world(self, u, v):
        x, y = (u - 0.5) * EW, (v - 0.5) * EH
        return self.s["c"][0] + x * self.ca - y * self.sa, self.s["c"][1] + x * self.sa + y * self.ca

    def local(self, X, Y):
        dx, dy = X - self.s["c"][0], Y - self.s["c"][1]
        return (dx * self.ca + dy * self.sa) / EW + 0.5, (-dx * self.sa + dy * self.ca) / EH + 0.5

    def under(self, u, v):
        """The underside, above the resting plane: arched along its length, the near right corner lifted."""
        s = self.s
        return s["bow"] * math.sin(math.pi * u) * (0.75 + 0.25 * math.sin(math.pi * v)) + s["curl"] * ((1 - u) ** 3) * ((1 - v) ** 2)

    def pillow(self, u, v):
        e = lambda t: 1 - abs(2 * t - 1) ** 10
        return 0.012 + THICK * e(u) * e(v) ** 0.6

    def z(self, u, v, top=True):
        X, Y = self.world(u, v)
        a, b, c = self.plane
        return a * X + b * Y + c + self.under(u, v) + (self.pillow(u, v) if top else 0.0)

    def top(self, X, Y):
        u, v = self.local(X, Y)
        if not (0 <= u <= 1 and 0 <= v <= 1):
            return 0.0
        return self.z(u, v)

    def mesh(self, material):
        nu, nv = 88, 44
        verts, uvs, faces = [], [], []
        for top in (True, False):
            for j in range(nv + 1):
                for i in range(nu + 1):
                    u, v = i / nu, j / nv
                    X, Y = self.world(u, v)
                    verts.append((X, Y, self.z(u, v, top))); uvs.append((u, v) if top else (0.02, 0.98))
        n = (nu + 1) * (nv + 1)
        for j in range(nv):
            for i in range(nu):
                a = j * (nu + 1) + i
                faces.append((a, a + 1, a + nu + 2, a + nu + 1))
                faces.append((n + a, n + a + nu + 1, n + a + nu + 2, n + a + 1))
        # the edge all the way round
        ring = [i for i in range(nu)] + [nu + j * (nu + 1) for j in range(nv)] + [nv * (nu + 1) + nu - i for i in range(nu)] + [(nv - j) * (nu + 1) for j in range(nv)]
        for k in range(len(ring)):
            a, b = ring[k], ring[(k + 1) % len(ring)]
            faces.append((a, n + a, n + b, b))
        me = bpy.data.meshes.new("env"); me.from_pydata(verts, [], faces)
        uv = me.uv_layers.new(name="uv")
        for lp in me.loops:
            uv.data[lp.index].uv = uvs[lp.vertex_index]
        for p in me.polygons:
            p.use_smooth = True
        ob = bpy.data.objects.new("env", me); bpy.context.scene.collection.objects.link(ob)
        ob.data.materials.append(material)
        return ob


def build(frame, quality, region=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    final = quality == "final"
    sc.cycles.samples = 176 if final else 32
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100 if final else 40
    sc.render.threads_mode = "AUTO"
    sc.view_settings.view_transform = "Raw"
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"

    world = bpy.data.worlds.new("room"); world.use_nodes = True; sc.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1.0, 0.97, 0.90, 1); bg.inputs["Strength"].default_value = 0.16

    shot = SHOTS[frame]
    laid = []
    for spec in (ONE if frame == 3 else fan() if frame == 2 else PILE):
        e = Envelope(spec, laid)
        e.mesh(paper_mat(spec["img"], spec["img"]))
        laid.append(e)

    me = bpy.data.meshes.new("table"); s = 3000
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
    tb = bpy.data.objects.new("table", me); sc.collection.objects.link(tb); tb.location.z = -0.0005
    tb.data.materials.append(table_mat())

    # key: a small window low behind and to the right, raking, so every edge throws a shadow towards us and to the left
    key = bpy.data.lights.new("key", "AREA"); key.shape = "RECTANGLE"; key.size = 70; key.size_y = 100
    key.energy = 52000 * 7.5 * 9 * 2.0; key.color = (1.0, 0.965, 0.92)
    ko = bpy.data.objects.new("key", key); sc.collection.objects.link(ko)
    ko.location = shot.get("key", (520, 170, 125)); aim(ko, (0, 8, 0))
    fl = bpy.data.lights.new("fill", "AREA"); fl.size = 360; fl.energy = 5200 * 6 * 9 * 0.6; fl.color = (0.97, 0.98, 1.0)
    fo = bpy.data.objects.new("fill", fl); sc.collection.objects.link(fo)
    fo.location = (-150, -450, 225); aim(fo, (0, 8, 0))

    cam = bpy.data.cameras.new("cam"); co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    cam.sensor_fit = "VERTICAL"; cam.sensor_height = 30
    co.location = shot["loc"]; aim(co, shot["aim"], shot.get("up", (0, 0, 1)))
    cam.lens = shot["lens"]
    cam.shift_x, cam.shift_y = shot["shift"]
    cam.clip_start = 0.1
    cam.dof.use_dof = True
    cam.dof.focus_distance = (Vector(shot["focus"]) - co.location).length
    cam.dof.aperture_fstop = shot["f"]
    if region:
        sc.render.use_border = True
        sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = region

    exr = str(TMP / f"nx-env-{frame}.exr")
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
    a = np.clip(a, 0, None)
    x = a * EXPOSURE
    x = np.where(x > 0.6, 0.6 + (1 - np.exp(-(x - 0.6) / 0.42)) * 0.4, x)
    x = np.clip(x, 0, 1)
    x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)
    rng = np.random.default_rng(3 + frame)
    x += rng.normal(0, 0.008, (H, W, 1)).astype(np.float32)
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
        exr = str(TMP / f"nx-env-{fr}.exr")
        grade(exr if regrade else build(fr, quality), fr, quality)
