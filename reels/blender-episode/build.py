"""Build the 'Rate my prompt' episode in Blender: set, Maya, Claude, lights, animated cameras.
Everything is keyframed from lines.json (voices + mouth envelopes), so the saved .blend plays on its own.

  python build.py -- --save episode.blend                       # build + save
  python build.py -- --stills 2,8,16 --out stills --res 360x640  # quick check renders
  python build.py -- --render frames/ --res 720x1280 [--start N --end M]
"""
import bpy, bmesh, json, math, os, random, sys
import numpy as np
from mathutils import Vector, Quaternion, Euler, Matrix

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default
HERE = os.path.dirname(os.path.abspath(__file__))
EP = json.load(open(os.path.join(HERE, 'lines.json')))
FPS = EP['fps']; LINES = EP['lines']; DUR = EP['duration']
NFRAMES = int(DUR * FPS)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
coll = scene.collection

# ------------------------------------------------------------------ helpers
def srgb(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1.0,)

_mats = {}
def mat(color, rough=0.6, emit=None, strength=1.0, sss=0.0, sheen=0.0, metal=0.0, name=None):
    key = (color, rough, emit, strength, sss, sheen, metal)
    if key in _mats: return _mats[key]
    m = bpy.data.materials.new(name or f'm_{color}')
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = srgb(color)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (0.6, 0.25, 0.15)
        b.inputs['Subsurface Scale'].default_value = 0.02
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen
    if emit:
        b.inputs['Emission Color'].default_value = srgb(emit)
        b.inputs['Emission Strength'].default_value = strength
    _mats[key] = m
    return m

def add_bump(m, kind='noise', scale=60.0, strength=0.15):
    nt = m.node_tree; bsdf = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    if kind == 'strands':   # soft vertical hair clumps
        tex = nt.nodes.new('ShaderNodeTexWave'); tex.wave_type = 'BANDS'; tex.bands_direction = 'X'
        tex.inputs['Scale'].default_value = scale; tex.inputs['Distortion'].default_value = 7.0; tex.inputs['Detail'].default_value = 3
    else:                   # fleece / knit
        tex = nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = scale; tex.inputs['Detail'].default_value = 6
    nt.links.new(tc.outputs['Object'], tex.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = strength
    nt.links.new(tex.outputs['Fac'] if 'Fac' in tex.outputs else tex.outputs[0], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m

def link(o, parent=None, loc=(0, 0, 0)):
    coll.objects.link(o)
    if parent: o.parent = parent
    o.location = loc
    return o

def empty(name, parent=None, loc=(0, 0, 0)):
    return link(bpy.data.objects.new(name, None), parent, loc)

def from_bm(name, bm, m, parent=None, loc=(0, 0, 0), smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = smooth
    me.materials.append(m)
    return link(bpy.data.objects.new(name, me), parent, loc)

def uvsphere(name, r, m, parent=None, loc=(0, 0, 0), scale=(1, 1, 1), seg=32, ring=16):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=ring, radius=r)
    o = from_bm(name, bm, m, parent, loc); o.scale = scale; return o

def ico(name, r, m, parent=None, loc=(0, 0, 0), sub=2, jitter=0.1, seed=1, scale=(1, 1, 1), smooth=False):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    rnd = random.Random(seed)
    for v in bm.verts: v.co += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * r * jitter
    o = from_bm(name, bm, m, parent, loc, smooth=smooth); o.scale = scale; return o

def cube(name, size, m, parent=None, loc=(0, 0, 0), bevel=0.0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    o = from_bm(name, bm, m, parent, loc, smooth=False); o.rotation_euler = rot
    if bevel:
        mod = o.modifiers.new('bevel', 'BEVEL'); mod.width = bevel; mod.segments = 3; mod.limit_method = 'NONE'
        o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
        o.data.shade_smooth() if hasattr(o.data, 'shade_smooth') else None
    return o

def cyl(name, r, h, m, parent=None, loc=(0, 0, 0), seg=24, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r2 if r2 is not None else r, depth=h)
    o = from_bm(name, bm, m, parent, loc); o.rotation_euler = rot
    return o

def torus(name, R, r, m, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    seg, ss = 40, 10
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        row = []
        for j in range(ss):
            b = 2 * math.pi * j / ss
            row.append(bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
        verts.append(row)
    for i in range(seg):
        for j in range(ss):
            bm.faces.new((verts[i][j], verts[(i + 1) % seg][j], verts[(i + 1) % seg][(j + 1) % ss], verts[i][(j + 1) % ss]))
    o = from_bm(name, bm, m, parent, loc); o.rotation_euler = rot
    return o

_mbn = [0]
EXT = 0.574  # visible radius of a metaball ball at threshold 0.6, per unit radius
def blob(name, elems, m, parent=None, loc=(0, 0, 0), res=0.006):
    """Metaball soft union -> mesh. elems: (center, (ex, ey, ez)) extents in metres, or negative ones."""
    _mbn[0] += 1
    mb = bpy.data.metaballs.new(f'MB{_mbn[0]}'); mb.resolution = res; mb.render_resolution = res; mb.threshold = 0.6
    o = bpy.data.objects.new(f'MBobj{_mbn[0]}x', mb); coll.objects.link(o)
    for el in elems:
        c, ext = el[0], el[1]
        e = mb.elements.new(type='ELLIPSOID')
        base = max(ext); e.radius = base / EXT
        e.size_x, e.size_y, e.size_z = (x / base for x in ext)
        e.co = c
        if len(el) > 2 and el[2] == 'neg': e.use_negative = True
    for x in bpy.context.view_layer.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target='MESH')
    o = bpy.context.view_layer.objects.active
    o.name = name; o.data.materials.clear(); o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = True
    if parent:
        o.parent = parent
    o.location = loc
    return o

def facet(o, target_faces):
    """Soft low-poly look: decimate to about target_faces and flat-shade (like the reference renders)."""
    n = len(o.data.polygons)
    if n > target_faces:
        d = o.modifiers.new('facet', 'DECIMATE'); d.ratio = target_faces / n
    for p in o.data.polygons: p.use_smooth = False
    return o

def smooth(o, levels=1):
    """Smooth stylised look: subdivision + smooth shading."""
    for p in o.data.polygons: p.use_smooth = True
    if levels:
        m = o.modifiers.new('subd', 'SUBSURF'); m.levels = levels; m.render_levels = levels
    return o

def strand(name, pts, r0, r1, m, parent, bulge=False):
    """A tapered hair clump along a smooth bezier through pts (parent space)."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = 1.0; cu.bevel_resolution = 4; cu.resolution_u = 10; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for k, (bp, co) in enumerate(zip(sp.bezier_points, pts)):
        bp.co = co; bp.handle_left_type = bp.handle_right_type = 'AUTO'
        u = k / (len(pts) - 1); bp.radius = (max(r0, r1) * (0.25 + 0.75 * math.sin(math.pi * min(1, u * 1.3)))) if bulge else (r0 + (r1 - r0) * u)
    cu.materials.append(m)
    o = link(bpy.data.objects.new(name, cu), parent)
    return o

def image(name, arr):
    h, w, _ = arr.shape
    img = bpy.data.images.new(name, w, h, alpha=False)
    img.pixels.foreach_set(np.ascontiguousarray(arr[::-1]).astype(np.float32).ravel())
    img.pack()
    return img

def emit_plane(name, img, w, h, strength, parent=None, loc=(0, 0, 0), rot=(math.pi / 2, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    uv = bm.loops.layers.uv.new()
    for f in bm.faces:
        for l in f.loops: l[uv].uv = (l.vert.co.x + 0.5, l.vert.co.y + 0.5)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * h, 0))
    m = bpy.data.materials.new(name + '_m'); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(tex.outputs['Color'], em.inputs['Color']); nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    o = from_bm(name, bm, m, parent, loc, smooth=False); o.rotation_euler = rot
    o.visible_shadow = False
    return o

# ------------------------------------------------------------------ world + lights (night tech studio, per the character sheet)
world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = srgb('#141b33')
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.25

def area(name, color, energy, loc, target, size=1.0):
    L = bpy.data.lights.new(name, 'AREA'); L.color = srgb(color)[:3]; L.energy = energy; L.size = size
    o = link(bpy.data.objects.new(name, L), None, loc)
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o
area('key', '#ffc08a', 60, (0.8, -0.3, 1.45), (0.0, 0.72, 1.15), 0.5)          # warm desk-lamp key
area('claudeKey', '#ffc08a', 18, (0.3, -0.5, 1.05), (-0.22, -0.1, 0.84), 0.35)
area('fill', '#6f86ff', 8, (-1.2, -0.9, 1.4), (0.0, 0.4, 1.0), 1.6)           # cool night fill
area('rim', '#7b8cff', 70, (-0.7, 1.6, 1.9), (0.0, 0.72, 1.25), 0.8)          # window rim (blue)
area('rim2', '#b06bff', 45, (0.8, 1.6, 1.8), (0.0, 0.72, 1.2), 0.8)           # purple rim
area('claudeRim', '#8f9cff', 12, (-0.45, 0.4, 1.05), (-0.22, -0.1, 0.84), 0.3)

# ------------------------------------------------------------------ room: night tech studio with a city window
DESK = 0.75
cube('floor', (8, 8, 0.02), mat('#4a3328', 0.6), loc=(0, 1.0, -0.01))
WALL_Y = 2.2
wallm = mat('#1b2240', 0.9, name='wall_navy')
cube('wall_low', (8, 0.1, 0.75), wallm, loc=(0, WALL_Y, 0.375))
cube('wall_top', (8, 0.1, 0.7), wallm, loc=(0, WALL_Y, 3.05))
for x in (-2.75, 2.75): cube('wall_side', (2.5, 0.1, 2.0), wallm, loc=(x, WALL_Y, 1.75))
frm = mat('#0e1222', 0.5)
for x in (-1.5, -0.5, 0.5, 1.5): cube('mullion', (0.05, 0.12, 1.95), frm, loc=(x, WALL_Y - 0.02, 1.72))
cube('transom', (3.0, 0.12, 0.05), frm, loc=(0, WALL_Y - 0.02, 1.85))
cube('sill', (3.1, 0.25, 0.04), mat('#262e52', 0.6), loc=(0, WALL_Y - 0.12, 0.76))
def city_image(w=1024, h=640, seed=3):
    rnd = np.random.default_rng(seed)
    y = np.linspace(0, 1, h)[:, None]
    top, low = np.array([0.03, 0.04, 0.12]), np.array([0.16, 0.12, 0.38])
    img = np.repeat((top + (low - top) * y)[:, None, :], w, axis=1).reshape(h, w, 3)
    xs = 0
    while xs < w:
        bw = rnd.integers(40, 110); bh = rnd.integers(int(h * 0.3), int(h * 0.85))
        img[h - bh:, xs:xs + bw] = np.array([0.025, 0.03, 0.08])
        for _ in range(int(bw * bh / 380)):
            wx, wy = xs + rnd.integers(4, max(5, bw - 6)), h - bh + rnd.integers(6, bh - 4)
            img[wy:wy + 4, wx:wx + 5] = [1.0, 0.82, 0.5] if rnd.random() < 0.75 else [0.55, 0.75, 1.0]
        xs += bw + rnd.integers(0, 10)
    k = np.exp(-np.linspace(-2, 2, 7) ** 2); k /= k.sum()
    for ax in (0, 1): img = np.apply_along_axis(lambda v: np.convolve(v, k, mode='same'), ax, img)
    return np.dstack([np.clip(img, 0, 4), np.ones((h, w))])
emit_plane('city', image('city', city_image()), 11, 6.5, 1.4, loc=(0, 6.0, 2.2))
# bookshelf (left) with warm books
shelf = empty('shelf', loc=(-1.75, 1.75, 0)); shelf.rotation_euler = (0, 0, 0.3)
cube('shelf_body', (0.9, 0.35, 2.1), mat('#3d2a22', 0.7), shelf, (0, 0, 1.05))
rnd = random.Random(5); bookcols = ['#c8553d', '#2f7f7a', '#e0b84a', '#6a4bb5', '#d98c5f', '#3f6fb5', '#e46a8a', '#9bb84a']
for sh_i in range(4):
    z = 0.22 + sh_i * 0.48; x = -0.4
    while x < 0.38:
        w = rnd.uniform(0.04, 0.075); hh = rnd.uniform(0.22, 0.36)
        cube('book', (w, 0.26, hh), mat(rnd.choice(bookcols), 0.6), shelf, (x + w / 2, -0.06, z + hh / 2), bevel=0.004)
        x += w + 0.005
# purple bean bag + plant (right)
facet(uvsphere('beanbag', 0.45, mat('#7c3fc4', 0.75, sheen=0.3), None, (1.65, 1.5, 0.28), scale=(1.2, 1.05, 0.62)), 500)
pl = empty('plant', loc=(-1.2, 1.9, 0))
cyl('pot', 0.17, 0.36, mat('#d9c6aa', 0.6), pl, (0, 0, 0.18), r2=0.13)
for k in range(13):
    a = k * 2.4; h = 0.4 + (k % 5) * 0.13
    leaf = uvsphere('leaf', 0.14, mat('#3f8a4f' if k % 2 else '#2f6e40', 0.6), pl, (math.cos(a) * 0.14, math.sin(a) * 0.14, 0.36 + h), scale=(0.6, 0.14, 0.9))
    leaf.rotation_euler = (math.sin(a) * 0.5, -math.cos(a) * 0.5, a)
# whiteboard on an easel (left back) with "What is an API?"
wb = empty('whiteboard', loc=(-0.95, 1.35, 0)); wb.rotation_euler = (0, 0, 0.25)
cube('wb_frame', (0.95, 0.03, 0.65), mat('#c7ccd6', 0.4, metal=0.3), wb, (0, 0, 1.45), bevel=0.01)
cube('wb_board', (0.9, 0.035, 0.6), mat('#f6f7fa', 0.35), wb, (0, -0.003, 1.45))
for sx in (-1, 1): cube('wb_leg', (0.03, 0.03, 1.15), mat('#8a919f', 0.5), wb, (sx * 0.4, 0.04, 0.575))
def board_text(body, loc, size, color):
    cu = bpy.data.curves.new('txt', 'FONT'); cu.body = body; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = 0.0005
    o = link(bpy.data.objects.new('txt', cu), wb, loc); o.rotation_euler = (math.pi / 2, 0, 0)
    o.data.materials.append(mat(color, 0.5)); return o
board_text('WHAT IS AN API?', (0, -0.025, 1.64), 0.06, '#1d2433')
board_text('You ask  ->  API  ->  Answer', (0, -0.025, 1.42), 0.045, '#2f6fd6')

# ------------------------------------------------------------------ desk + props (from the prop sheet)
wood = mat('#8a5a3c', 0.5, name='desk_wood')
cube('desk', (2.0, 0.95, 0.05), wood, loc=(0.1, 0.12, DESK - 0.025), bevel=0.012)
for x, y in ((-0.85, -0.3), (1.05, -0.3), (-0.85, 0.55), (1.05, 0.55)):
    cube('leg', (0.05, 0.05, DESK - 0.05), mat('#2b2018', 0.6), None, (x, y, (DESK - 0.05) / 2))
# monitor with code (right back)
mon = empty('monitor', loc=(0.72, 0.38, DESK)); mon.rotation_euler = (0, 0, 0.4)
dark = mat('#1b1d26', 0.4)
cube('mon_base', (0.2, 0.14, 0.015), dark, mon, (0, 0, 0.008), bevel=0.004)
cube('mon_neck', (0.04, 0.03, 0.22), dark, mon, (0, 0.02, 0.12))
cube('mon_body', (0.6, 0.035, 0.37), dark, mon, (0, 0, 0.41), bevel=0.01)
def code_image(w=512, h=300, seed=42):
    rnd = np.random.default_rng(seed)
    img = np.zeros((h, w, 3)) + [0.02, 0.03, 0.07]
    cols = [[0.45, 0.6, 1.0], [1.0, 0.5, 0.2], [0.35, 0.9, 0.75], [0.8, 0.55, 0.95], [0.85, 0.86, 0.9]]
    for i in range(16):
        x = 16 + 24 * rnd.integers(0, 3)
        for _ in range(rnd.integers(1, 5)):
            ww = rnd.integers(20, 90); img[12 + i * 17: 20 + i * 17, x:x + ww] = cols[rnd.integers(0, 5)]; x += ww + 8
    return np.dstack([img, np.ones((h, w))])
emit_plane('mon_screen', image('code', code_image()), 0.56, 0.33, 2.0, mon, (0, -0.018, 0.41))
# laptop in front of Maya (lid toward camera)
lap = empty('laptop', loc=(0.22, 0.18, DESK)); lap.rotation_euler = (0, 0, 0.15)
alu = mat('#aeb4c2', 0.35, metal=0.5, name='alu')
cube('lap_base', (0.3, 0.21, 0.012), alu, lap, (0, 0, 0.006), bevel=0.004)
lid = empty('lap_lid_pivot', lap, (0, -0.105, 0.012)); lid.rotation_euler = (-1.9, 0, 0)
cube('lap_lid', (0.3, 0.01, 0.2), alu, lid, (0, 0, 0.1), bevel=0.004)
Ls = bpy.data.lights.new('screen_glow', 'AREA'); Ls.color = srgb('#9fbaff')[:3]; Ls.energy = 3; Ls.size = 0.25
link(bpy.data.objects.new('screen_glow', Ls), lid, (0, 0.03, 0.1)).rotation_euler = (math.pi / 2, 0, 0)
# desk lamp (right, warm) - the key light's motivation
dl = empty('desk_lamp', loc=(1.0, 0.0, DESK)); dl.rotation_euler = (0, 0, 0.6)
lampm = mat('#2a2f45', 0.45, name='lamp_navy')
cyl('lamp_base', 0.07, 0.02, lampm, dl, (0, 0, 0.01))
cyl('lamp_arm', 0.009, 0.45, lampm, dl, (0, 0.03, 0.22), rot=(-0.15, 0, 0))
cyl('lamp_head', 0.08, 0.11, lampm, dl, (0, -0.06, 0.45), r2=0.035, rot=(-1.0, 0, 0))
bulb = mat('#ffe2a8', 0.4, emit='#ffcf80', strength=25, name='bulb')
uvsphere('lamp_bulb', 0.028, bulb, dl, (0, -0.09, 0.42))
Ll = bpy.data.lights.new('desk_lamp_light', 'POINT'); Ll.color = srgb('#ffc98a')[:3]; Ll.energy = 10; Ll.shadow_soft_size = 0.05
link(bpy.data.objects.new('desk_lamp_light', Ll), dl, (0, -0.1, 0.38))
# mug, pen cup, books, small plant
mug = empty('mug', loc=(-0.55, 0.1, DESK))
cyl('mug_body', 0.045, 0.1, mat('#f4efe6', 0.35), mug, (0, 0, 0.05))
cyl('coffee', 0.04, 0.005, mat('#4a2a1a', 0.2), mug, (0, 0, 0.095))
torus('mug_handle', 0.028, 0.008, mat('#f4efe6', 0.35), mug, (0.05, 0, 0.05), rot=(math.pi / 2, 0, 0))
pc = empty('pencup', loc=(-0.7, 0.3, DESK))
cyl('cup', 0.04, 0.1, mat('#2f7f7a', 0.5), pc, (0, 0, 0.05))
for k, c in enumerate(['#e8743b', '#5fd6b8', '#7c3fc4', '#e0b84a']):
    cyl('pencil', 0.005, 0.15, mat(c, 0.5), pc, ((k - 1.5) * 0.013, 0, 0.12), rot=(0, (k - 1.5) * 0.12, 0))
for k, (c, hh) in enumerate([('#3f9a5a', 0.035), ('#7c3fc4', 0.03), ('#e5c04a', 0.035)]):
    cube('deskbook', (0.22, 0.16, hh), mat(c, 0.6), loc=(-0.62, -0.25, DESK + hh / 2 + k * 0.034), rot=(0, 0, 0.1 * (k - 1)), bevel=0.003)
cyl('desk_pot', 0.045, 0.07, mat('#d9c6aa', 0.6), None, (0.6, -0.25, DESK + 0.035))
for k in range(6):
    a = k * 1.05
    lf = uvsphere('dleaf', 0.05, mat('#3f8a4f', 0.6), None, (0.6 + math.cos(a) * 0.03, -0.25 + math.sin(a) * 0.03, DESK + 0.12), scale=(0.5, 0.15, 1.0))
    lf.rotation_euler = (math.sin(a) * 0.5, -math.cos(a) * 0.5, a)

# ------------------------------------------------------------------ CLAUDE (orange faceted cloud: no arms, no mouth)
CL = Vector((-0.22, -0.1, DESK))
orange = mat('#f2792c', 0.55, name='claude_orange')
claude = empty('claude', loc=CL)
cbody = empty('claude_body', claude, (0, 0, 0.0))
def faceted_cloud(name, parts, m, parent, seed=21):
    bm = bmesh.new(); rnd = random.Random(seed)
    for (c, r, sc) in parts:
        mtx = Matrix.Translation(Vector(c)) @ Matrix.Diagonal(Vector((sc[0], sc[1], sc[2], 1)))
        res = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r, matrix=mtx)
        for v in res['verts']: v.co += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * r * 0.03
    return from_bm(name, bm, m, parent, smooth=False)
parts = [((0, 0, 0.078), 0.07, (1.05, 0.75, 0.9))]
for k in range(7):   # cloud bumps on top and sides, flatter bottom
    a = k / 6 * math.pi
    parts.append(((math.cos(a) * 0.064, 0.0, 0.088 + math.sin(a) * 0.045), 0.036, (1, 0.8, 1)))
body = facet(faceted_cloud('claude_shape', parts, orange, cbody), 1800)
eyem = mat('#111111', 0.4, name='eye_black')
c_eyes = []
for s in (-1, 1):
    c_eyes.append(cube(f'claude_eye{s}', (0.012, 0.01, 0.03), eyem, cbody, (s * 0.022, -0.052, 0.098), bevel=0.0015))
c_feet = []
for i, (x, y) in enumerate(((-0.036, -0.022), (0.036, -0.022), (-0.03, 0.025), (0.03, 0.025))):
    c_feet.append(facet(ico(f'claude_foot{i}', 0.02, mat('#e5692a', 0.6), claude, (x, y, 0.016), sub=3, jitter=0.03, seed=10 + i), 90))
ticks = empty('claude_ticks', cbody, (0, 0, 0.19))
for i, a in enumerate((-0.45, 0, 0.45)):
    t = cube('tick', (0.006, 0.006, 0.028), mat('#ffd23f', 0.5, emit='#ffd23f', strength=2), ticks, (math.sin(a) * 0.06, 0, math.cos(a) * 0.02))
    t.rotation_euler = (0, a, 0)

# ------------------------------------------------------------------ MAYA (per the character sheet: soft low-poly facets)
skin = mat('#f2c4a6', 0.45, sss=0.2, name='skin')
jacket = add_bump(mat('#1f5f63', 0.8, sheen=0.3, name='jacket_teal'), 'noise', 300, 0.03)
creamtop = mat('#f1e6d2', 0.8, name='top_cream')
hairm = mat('#24161a', 0.5, sheen=0.15, name='hair_darkbrown')
glassm = mat('#111111', 0.3, name='glasses_black')
pantsm = mat('#d9c3a0', 0.8, name='pants_beige')
yellow = jacket
MY = 0.74
maya = empty('maya', loc=(0.0, MY, 0))
chair = mat('#1f6a6e', 0.6, name='chair_teal')
cube('seat', (0.46, 0.44, 0.06), chair, maya, (0, 0.05, 0.47), bevel=0.02)
cube('back', (0.46, 0.06, 0.6), chair, maya, (0, 0.3, 0.82), bevel=0.02)
cyl('post', 0.025, 0.42, mat('#2a2f45', 0.5), maya, (0, 0.05, 0.24))
for s in (-1, 1):   # beige cargo pants + white sneakers
    facet(cyl('thigh', 0.075, 0.4, pantsm, maya, (s * 0.09, -0.12, 0.53), rot=(math.pi / 2, 0, 0)), 120)
    facet(cyl('shin', 0.07, 0.45, pantsm, maya, (s * 0.09, -0.3, 0.27)), 120)
    facet(uvsphere('shoe', 0.07, mat('#f4f1ea', 0.6), maya, (s * 0.09, -0.36, 0.04), scale=(0.9, 1.4, 0.55)), 100)

torso = empty('torso', maya, (0, 0, 0.52))
facet(blob('jacket', [
    ((0, 0, 0.2), (0.165, 0.125, 0.22)),
    ((-0.13, 0, 0.33), (0.095, 0.095, 0.085)), ((0.13, 0, 0.33), (0.095, 0.095, 0.085)),
    ((0, 0.01, 0.06), (0.17, 0.13, 0.08)),
    ((-0.075, -0.06, 0.37), (0.06, 0.05, 0.05)), ((0.075, -0.06, 0.37), (0.06, 0.05, 0.05)),   # collar
    ((0, -0.15, 0.27), (0.045, 0.05, 0.2), 'neg'),                                               # open front
], jacket, torso), 1400)
facet(uvsphere('top', 0.05, creamtop, torso, (0, -0.075, 0.25), scale=(1.15, 0.9, 2.6)), 200)        # cream top inside the open jacket
cyl('neck', 0.04, 0.09, skin, torso, (0, 0, 0.43))

head = empty('head', torso, (0, 0, 0.385))
HC = Vector((0, 0, 0.15)); R = 0.15
facet(uvsphere('head_skin', R, skin, head, HC, scale=(1.0, 0.95, 0.98), seg=48, ring=24), 1100)
facet(uvsphere('nose', 0.012, skin, head, HC + Vector((0, -0.142, -0.022)), scale=(1, 0.8, 0.8)), 40)
# long, voluminous, wavy hair with a swept fringe
hair = [
    (HC + Vector((0, 0.03, 0.04)), (0.158, 0.152, 0.15)),              # crown
    (HC + Vector((-0.04, -0.1, 0.1)), (0.11, 0.055, 0.06)),            # fringe swept to one side
    (HC + Vector((0.065, -0.1, 0.085)), (0.085, 0.05, 0.055)),
    (HC + Vector((0.125, -0.07, 0.04)), (0.05, 0.06, 0.07)),
    (HC + Vector((-0.13, -0.06, 0.05)), (0.05, 0.06, 0.07)),
]
for s in (-1, 1):          # wavy side curtains down past the shoulders
    for k in range(7):
        wave = math.sin(k * 1.3) * 0.022
        hair.append((HC + Vector((s * (0.15 + k * 0.01 + wave), 0.0 + k * 0.01, -0.03 - k * 0.062)), (0.05, 0.065, 0.06)))
for k in range(6):         # full back
    for s in (-1, 0, 1):
        hair.append((HC + Vector((s * 0.1 + math.sin(k * 1.1 + s) * 0.02, 0.1, -0.02 - k * 0.06)), (0.1, 0.08, 0.08)))
facet(blob('hair', hair, hairm, head, res=0.007), 2400)
def clump(pts, r0, r1):
    o = strand('clump', pts, r0, r1, hairm, head, bulge=True)
    o.data.bevel_resolution = 1; o.data.resolution_u = 5   # chunky facets, like the sheet
    return o
for s in (-1, 1):
    for j in range(6):   # wavy locks from the crown down past the shoulders
        y0 = -0.07 + j * 0.04
        pts = [HC + Vector((s * 0.03, y0, 0.17))]
        for k in range(1, 6):
            pts.append(HC + Vector((s * (0.165 + k * 0.014 + math.sin(k * 1.4 + j) * 0.02), y0 + k * 0.012, 0.13 - k * 0.085)))
        clump(pts, 0.034, 0.014)
for j in range(4):       # fringe swept across the forehead
    clump([HC + Vector((-0.02 + j * 0.01, -0.05, 0.17)), HC + Vector((0.03 + j * 0.025, -0.135, 0.12 - j * 0.008)),
           HC + Vector((0.11 + j * 0.012, -0.11, 0.06 - j * 0.012))], 0.022, 0.008)
# face: dot eyes with a highlight, big round black glasses, small mouth
m_eyes, brows = [], []
for s in (-1, 1):
    eg = empty(f'eyeball{s}', head, HC + Vector((s * 0.056, -0.14, -0.004)))
    uvsphere('eye', 0.011, eyem, eg, (0, 0, 0), scale=(0.85, 0.5, 1.2))
    uvsphere('catchlight', 0.0032, mat('#ffffff', 0.2, emit='#ffffff', strength=3), eg, (0.004, -0.006, 0.005), scale=(1, 0.4, 1))
    m_eyes.append(eg)
    torus(f'glasses{s}', 0.05, 0.0032, glassm, head, HC + Vector((s * 0.06, -0.152, 0.0)), rot=(math.pi / 2, 0, -s * 0.12))
    b = uvsphere(f'brow{s}', 0.016, mat('#2a1a18', 0.6), head, HC + Vector((s * 0.058, -0.138, 0.072)), scale=(1.5, 0.3, 0.18))
    b.rotation_euler = (0, s * 0.1, 0); brows.append(b)
cube('bridge', (0.02, 0.004, 0.004), glassm, head, HC + Vector((0, -0.157, 0.005)))
mouth = uvsphere('mouth', 0.011, mat('#5a2420', 0.5), head, HC + Vector((0, -0.141, -0.07)), scale=(1.3, 0.3, 0.25))

# arms: shoulder pivot -> upper arm, elbow pivot -> forearm + mitten (no fingers)
def capsule(name, r, length, m, parent):
    return blob(name, [((0, 0, -length * 0.15), (r, r, r)), ((0, 0, -length * 0.5), (r, r, r)), ((0, 0, -length * 0.85), (r * 0.95, r * 0.95, r * 0.95))], m, parent, res=0.006)
arms = {}
for s in (-1, 1):
    sh = empty(f'shoulder{s}', torso, (s * 0.165, 0, 0.34)); sh.rotation_mode = 'QUATERNION'
    facet(capsule(f'upper{s}', 0.056, 0.2, jacket, sh), 260)
    el = empty(f'elbow{s}', sh, (0, 0, -0.19)); el.rotation_mode = 'QUATERNION'
    facet(capsule(f'fore{s}', 0.051, 0.19, jacket, el), 260)
    facet(uvsphere(f'hand{s}', 0.042, skin, el, (0, 0, -0.205), scale=(0.95, 0.8, 1.1)), 140)
    arms[s] = (sh, el)

# ------------------------------------------------------------------ animation
def line_at(t):
    L = LINES[0]
    for l in LINES:
        if t >= l['t'] - 0.25: L = l
    return L
def env_at(t, who):
    for l in LINES:
        if l['who'] == who and l['t'] <= t < l['t'] + l['d']:
            return l['env'][min(len(l['env']) - 1, int((t - l['t']) * FPS))]
    return 0.0
def env_s(t, who): return (env_at(t - 1 / FPS, who) + 2 * env_at(t, who) + env_at(t + 1 / FPS, who)) / 4
clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def prog(t, a, d): return clamp((t - a) / d)
wob = lambda t, f, s=0: math.sin(t * f + s)
def D(x, y, z): return Vector((x, y, z)).normalized()
POSES = {  # torso-space directions (x right, -y toward camera, z up): upper arm, forearm
    'crossed': lambda s: (D(s * 0.12, -0.78, -0.6), D(-s * 0.92, -0.36, 0.03 + (0.06 if s < 0 else 0))),
    'gesture': lambda s: (D(0.35, -0.5, -0.8), D(0.12, -0.55, 0.83)) if s > 0 else (D(-0.12, -0.78, -0.6), D(0.92, -0.36, 0.09)),
}
def pose_name(L): return 'gesture' if (L['who'] == 'M' and L['act'] == 'gesture') else 'crossed'
DOWN = Vector((0, 0, -1))
def aim(sh, el, upper, fore):
    q = DOWN.rotation_difference(upper); sh.rotation_quaternion = q
    el.rotation_quaternion = DOWN.rotation_difference(q.inverted() @ fore)

cam_data = bpy.data.cameras.new('cam'); cam = link(bpy.data.objects.new('cam', cam_data)); scene.camera = cam
cam_data.sensor_fit = 'VERTICAL'; cam_data.sensor_height = 24
cam_data.dof.use_dof = True
cam.rotation_mode = 'QUATERNION'
def look(pos, target):
    return (Vector(target) - Vector(pos)).to_track_quat('-Z', 'Y')
def head_world():
    bpy.context.view_layer.update()
    return head.matrix_world @ HC
def shot(name, u):
    p = ease(u)
    if name == 'maya':
        h = head_world(); pos = h + Vector((-0.2, -1.2 + p * 0.08, -0.05))
        return pos, h + Vector((0, 0, -0.11)), 40, (pos - h).length, 1.2
    if name == 'claude':
        c = CL + Vector((0, 0, 0.1)); pos = c + Vector((-0.26, -0.72 + p * 0.05, 0.08))
        return pos, c + Vector((0.04, 0, 0.03)), 35, (pos - c).length, 1.1
    if name == 'wide':
        h = head_world(); pos = Vector((0.4 - p * 0.05, -1.65 + p * 0.1, 1.18))
        return pos, Vector((-0.08, 0.35, 0.98)), 30, (pos - h).length, 4.0

def animate(t):
    L = line_at(t); i = LINES.index(L); since = t - L['t']
    # Claude
    ce = env_s(t, 'C')
    bounce = abs(math.sin(t * 2.2)) * 0.003 + ce * 0.014
    if L['who'] == 'C' and L['act'] == 'excited': bounce += abs(math.sin(since * 10)) * 0.035 * clamp(1 - since / 1.2)
    if L['who'] == 'C' and L['act'] == 'bounce': bounce += abs(math.sin(since * 8)) * 0.012 * clamp(1 - since / 0.6)
    cbody.location.z = bounce
    sq = 1 + ce * 0.07 + math.sin(t * 2.2) * 0.008
    cbody.scale = (1 / math.sqrt(sq), 1 / math.sqrt(sq), sq)
    yaw = -0.15 if L['who'] == 'C' else 0.75; roll = 0; eye_x = 0; eye_h = 1
    if L['who'] == 'C' and L['act'] == 'look-away':
        k = ease(prog(since, 0, 0.35)) * (1 - ease(prog(since, L['d'] + 0.1, 0.4))); yaw = -0.15 - 0.75 * k; eye_x = -0.006 * k
    if L['who'] == 'C' and L['act'] == 'tilt': roll = 0.22 * ease(prog(since, 0, 0.4))
    if L['who'] == 'C' and L['act'] == 'squint': eye_h = 1 - 0.68 * ease(prog(since, 0.1, 0.3))
    if L['who'] == 'M' and L['act'] == 'lean': yaw = 0.95
    claude.rotation_euler = (0, 0, yaw)
    cbody.rotation_euler = (0, roll + wob(t, 1.3) * 0.02, 0)
    blink = 0.12 if ((t + 0.4) % 3.3) < 0.11 else 1
    for k, e in enumerate(c_eyes):
        e.scale = (1, 1, eye_h * blink); e.location.x = (1 if k else -1) * 0.022 + eye_x
    ticks.scale = (1, 1, 1) if (L['who'] == 'C' and L['act'] == 'excited' and since < 1.6) else (0, 0, 0)
    # Maya
    me = env_s(t, 'M')
    lean = ease(prog(since, -0.2, 0.35)) * (1 - ease(prog(since, L['d'] + 0.2, 0.5))) if (L['who'] == 'M' and L['act'] == 'lean') else 0
    torso.rotation_euler = (0.13 + lean * 0.15 + wob(t, 1.1) * 0.01, 0, 0)
    torso.location.z = 0.52 + wob(t, 1.6) * 0.002
    hx = 0.12 - lean * 0.08 + me * 0.05 * math.sin(t * 9)
    hz = -0.3 + wob(t, 0.6) * 0.04 + (-0.05 if L['who'] == 'C' else 0)
    hy = (0.07 if (L['who'] == 'M' and L['act'] == 'gesture') else 0) + wob(t, 0.8) * 0.02
    head.rotation_euler = (hx, hy, hz)
    mouth.scale = (1.3 - me * 0.25, 0.35, 0.22 + me * 1.3)
    by = 0.065 + me * 0.008 - (0.006 if (L['who'] == 'C' and L['act'] in ('look-away', 'squint')) else 0)
    for b in brows: b.location.z = HC.z + by + 0.007
    mb = 0.1 if ((t + 1.3) % 4.1) < 0.13 else 1
    sq = 0.3 if (L['who'] == 'C' and L['act'] in ('look-away', 'squint')) else 0.0
    for e in m_eyes:
        e.scale = (1, 1, max(0.08, mb * (1 - sq)))
        e.location.x = (1 if e.name.endswith('1') and not e.name.endswith('-1') else -1) * 0.056 - 0.004
    k = ease(prog(t, L['t'] - 0.3, 0.45)); P = LINES[i - 1] if i else L
    for s, (sh, el) in arms.items():
        a0, b0 = POSES[pose_name(P)](s); a1, b1 = POSES[pose_name(L)](s)
        up = a0.lerp(a1, k).normalized(); fo = b0.lerp(b1, k).normalized()
        if s > 0 and L['who'] == 'M' and L['act'] == 'gesture':
            fo = (Quaternion((1, 0, 0), me * 0.3 * math.sin(t * 6)) @ fo)
        aim(sh, el, up, fo)
    # camera (cuts on line changes, slow push inside a shot)
    start = 0 if i == 0 else L['t'] - 0.25
    end = LINES[i + 1]['t'] - 0.25 if i + 1 < len(LINES) else DUR
    pos, tgt, lens, focus, fstop = shot(L['shot'], clamp((t - start) / (end - start)))
    pos = pos + Vector((wob(t, 0.9) * 0.002, 0, wob(t, 1.3, 1) * 0.002))
    cam.location = pos; cam.rotation_quaternion = look(pos, tgt)
    cam_data.lens = lens; cam_data.dof.focus_distance = focus; cam_data.dof.aperture_fstop = fstop

ANIM = [cbody, claude, ticks, torso, head, mouth, cam] + c_eyes + brows + m_eyes + [x for p in arms.values() for x in p]
def key_all(f):
    for o in ANIM:
        o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f)
        o.keyframe_insert('rotation_quaternion' if o.rotation_mode == 'QUATERNION' else 'rotation_euler', frame=f)
    cam_data.keyframe_insert('lens', frame=f)
    cam_data.dof.keyframe_insert('focus_distance', frame=f); cam_data.dof.keyframe_insert('aperture_fstop', frame=f)

# ------------------------------------------------------------------ render settings
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 1, NFRAMES
res = arg('--res', '720x1280').split('x')
scene.render.resolution_x, scene.render.resolution_y = int(res[0]), int(res[1])
scene.render.engine = arg('--engine', 'CYCLES')
scene.render.use_persistent_data = True
if scene.render.engine == 'BLENDER_EEVEE_NEXT':
    scene.eevee.taa_render_samples = int(arg('--samples', 32)); scene.eevee.use_shadows = True
scene.cycles.device = 'CPU'
scene.cycles.samples = int(arg('--samples', 20))
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 4; scene.cycles.diffuse_bounces = 2; scene.cycles.glossy_bounces = 2; scene.cycles.transmission_bounces = 2
scene.cycles.use_adaptive_sampling = True
scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Punchy'
scene.view_settings.exposure = 0.0
scene.render.image_settings.file_format = 'JPEG'; scene.render.image_settings.quality = 92
# audio in the .blend so it plays in sync when opened
if os.path.exists(os.path.join(HERE, 'dialogue.wav')):
    try:
        scene.sequence_editor_create()
        scene.sequence_editor.sequences.new_sound('dialogue', os.path.join(HERE, 'dialogue.wav'), 1, 1)
    except RuntimeError as e:
        print('audio strip skipped:', e)

if '--stills' in argv:
    out = arg('--out', 'stills'); os.makedirs(out, exist_ok=True)
    for t in [float(x) for x in arg('--stills').split(',')]:
        animate(t); bpy.context.view_layer.update()
        scene.render.filepath = os.path.abspath(os.path.join(out, f't{t:06.2f}.jpg'))
        bpy.ops.render.render(write_still=True); print('still', t)
else:
    s0, s1 = int(arg('--start', 1)), int(arg('--end', NFRAMES))
    for f in range(1, NFRAMES + 1):
        animate((f - 1) / FPS); key_all(f)
    for o in ANIM:
        ad = o.animation_data
        if ad and ad.action:
            for fc in ad.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    if '--save' in argv:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(arg('--save')), compress=True); print('saved')
    if '--render' in argv:
        out = os.path.abspath(arg('--render')); os.makedirs(out, exist_ok=True)
        for f in range(s0, s1 + 1, int(arg('--step', 1))):
            scene.frame_set(f); scene.render.filepath = os.path.join(out, f'f{f:05d}.jpg')
            bpy.ops.render.render(write_still=True)
            print('frame', f, flush=True)
