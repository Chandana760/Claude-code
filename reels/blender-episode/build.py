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

# ------------------------------------------------------------------ world + lights
world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = srgb('#1e2a33')
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.12

def area(name, color, energy, loc, target, size=1.0):
    L = bpy.data.lights.new(name, 'AREA'); L.color = srgb(color)[:3]; L.energy = energy; L.size = size
    o = link(bpy.data.objects.new(name, L), None, loc)
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o
area('key', '#ffb877', 55, (0.75, -0.35, 1.3), (0.0, 0.72, 1.12), 0.45)        # warm lamp-side key on Maya
area('claudeKey', '#ffbf86', 16, (0.25, -0.45, 1.0), (-0.22, -0.1, 0.84), 0.3)
area('fill', '#7f8cff', 3, (-1.2, -0.8, 1.3), (0.0, 0.4, 1.0), 1.5)
area('rim', '#ff4fa3', 75, (-0.8, 1.45, 2.0), (0.0, 0.72, 1.3), 0.6)       # magenta rim
area('rim2', '#6a5cff', 55, (0.8, 1.45, 1.9), (0.0, 0.72, 1.25), 0.6)        # violet rim
area('claudeRim', '#ff6aa8', 14, (-0.45, 0.35, 1.05), (-0.22, -0.1, 0.84), 0.3)

# ------------------------------------------------------------------ room: cosy home studio
DESK = 0.75
cube('floor', (8, 8, 0.02), mat('#6b4a36', 0.6), loc=(0, 1.0, -0.01))
WALL_Y = 1.75
cube('wall', (8, 0.1, 3.5), mat('#1f2c3a', 0.92, name='wall_paint'), loc=(0, WALL_Y, 1.75))
cube('skirting', (8, 0.04, 0.12), mat('#e9dfcf', 0.6), loc=(0, WALL_Y - 0.06, 0.06))
oak = mat('#c89a6a', 0.55, name='oak')
rnd = random.Random(5)
bookcols = ['#e07a5f', '#3d405b', '#81b29a', '#f2cc8f', '#c86b85', '#5b8fb9', '#efe3c8']
for (sx, sz, w) in ((-0.95, 1.45, 1.0), (-0.85, 1.9, 0.8), (1.05, 1.55, 0.9)):
    cube('shelf', (w, 0.24, 0.035), oak, loc=(sx, WALL_Y - 0.13, sz), bevel=0.006)
    x = sx - w / 2 + 0.05
    while x < sx + w / 2 - 0.08:
        if rnd.random() < 0.18:   # little potted plant
            cyl('pot', 0.045, 0.08, mat('#e9dfcf', 0.6), None, (x + 0.05, WALL_Y - 0.13, sz + 0.057))
            ico('shelf_plant', 0.06, mat('#4f8a5b', 0.7), None, (x + 0.05, WALL_Y - 0.13, sz + 0.13), sub=2, jitter=0.15, seed=int(x * 100))
            x += 0.13; continue
        bw = rnd.uniform(0.035, 0.065); bh = rnd.uniform(0.16, 0.25)
        cube('book', (bw, 0.18, bh), mat(rnd.choice(bookcols), 0.65), None, (x + bw / 2, WALL_Y - 0.13, sz + 0.018 + bh / 2), bevel=0.003)
        x += bw + 0.004
# framed doodle prints
for (fx, fz, fw, fh, c) in ((0.2, 2.15, 0.32, 0.42, '#f2cc8f'), (0.65, 2.2, 0.26, 0.26, '#81b29a')):
    cube('frame', (fw, 0.025, fh), mat('#2b2b2b', 0.5), loc=(fx, WALL_Y - 0.06, fz), bevel=0.004)
    cube('print', (fw - 0.05, 0.01, fh - 0.05), mat(c, 0.8), loc=(fx, WALL_Y - 0.075, fz))
# neon sign
def neon_text(body, loc, size, color, strength):
    cu = bpy.data.curves.new('neon', 'FONT'); cu.body = body; cu.size = size; cu.align_x = 'CENTER'
    cu.extrude = 0.004; cu.bevel_depth = 0.003
    o = link(bpy.data.objects.new('neon', cu), None, loc); o.rotation_euler = (math.pi / 2, 0, 0)
    o.data.materials.append(mat(color, 0.3, emit=color, strength=strength, name='neon_' + color))
    return o
neon_text('hello, world', (0.55, WALL_Y - 0.07, 1.5), 0.13, '#ff5a8a', 22)
L = bpy.data.lights.new('neon_glow', 'AREA'); L.color = srgb('#ff8a6a')[:3]; L.energy = 6; L.size = 0.8
g = link(bpy.data.objects.new('neon_glow', L), None, (0.55, WALL_Y - 0.3, 1.55)); g.rotation_euler = (math.pi / 2, 0, 0)
# string lights draped across the wall
bulb = mat('#ffe2a8', 0.4, emit='#ffcf80', strength=30, name='bulb')
for k in range(34):
    u = k / 33; x = -2.2 + u * 4.4
    z = 1.82 - 0.22 * math.sin(math.pi * ((u * 2) % 1.0))
    uvsphere('bulb', 0.018, bulb, None, (x, WALL_Y - 0.09, z), seg=12, ring=8)
# pendant lamp, big plant
cyl('cord', 0.004, 1.2, mat('#222222', 0.5), None, (-0.75, 0.9, 2.9))
cyl('shade', 0.16, 0.18, mat('#e9dfcf', 0.6), None, (-0.75, 0.9, 2.22), r2=0.05)
uvsphere('pend_bulb', 0.04, bulb, None, (-0.75, 0.9, 2.15))
Lp = bpy.data.lights.new('pendant', 'POINT'); Lp.color = srgb('#ffc98a')[:3]; Lp.energy = 25; Lp.shadow_soft_size = 0.1
link(bpy.data.objects.new('pendant', Lp), None, (-0.75, 0.9, 2.1))
pl = empty('plant', loc=(1.5, 1.35, 0))
cyl('pot', 0.2, 0.42, mat('#e07a5f', 0.6), pl, (0, 0, 0.21), r2=0.16)
for k in range(13):
    a = k * 2.4; h = 0.45 + (k % 5) * 0.14
    leaf = uvsphere('leaf', 0.16, mat('#3f7d4e' if k % 2 else '#2e6440', 0.55), pl, (math.cos(a) * 0.18, math.sin(a) * 0.18, 0.42 + h), scale=(0.75, 0.12, 0.55))
    leaf.rotation_euler = (math.sin(a) * 0.6, -math.cos(a) * 0.6, a)

# ------------------------------------------------------------------ desk + props
wood = mat('#b07d52', 0.45, name='desk_oak')
cube('desk', (2.0, 0.95, 0.05), wood, loc=(0.1, 0.12, DESK - 0.025), bevel=0.012)
for x, y in ((-0.85, -0.3), (1.05, -0.3), (-0.85, 0.55), (1.05, 0.55)):
    cyl('leg', 0.022, DESK - 0.05, mat('#2b2b2b', 0.4, metal=0.6), None, (x, y, (DESK - 0.05) / 2))
# laptop facing Maya (lid back toward camera, with a sticker)
lap = empty('laptop', loc=(0.55, 0.2, DESK)); lap.rotation_euler = (0, 0, 0.35)
alu = mat('#c9ccd3', 0.35, metal=0.5, name='alu')
cube('lap_base', (0.34, 0.24, 0.014), alu, lap, (0, 0, 0.007), bevel=0.004)
lid = empty('lid', lap, (0, -0.12, 0.014)); lid.rotation_euler = (-1.85, 0, 0)
cube('lap_lid', (0.34, 0.012, 0.23), alu, lid, (0, 0, 0.115), bevel=0.004)
uvsphere('sticker', 0.03, mat('#e8743b', 0.6), lid, (0.05, -0.007, 0.13), scale=(1, 0.08, 1))
Ls = bpy.data.lights.new('screen_glow', 'AREA'); Ls.color = srgb('#a8c4ff')[:3]; Ls.energy = 4; Ls.size = 0.3
link(bpy.data.objects.new('screen_glow', Ls), lid, (0, 0.03, 0.12)).rotation_euler = (math.pi / 2, 0, 0)
# desk lamp
dl = empty('desk_lamp', loc=(0.95, 0.35, DESK))
lampm = mat('#e07a5f', 0.45, name='lamp_coral')
cyl('lamp_base', 0.07, 0.02, lampm, dl, (0, 0, 0.01))
cyl('lamp_arm', 0.008, 0.42, lampm, dl, (0, -0.04, 0.21), rot=(0.2, 0, 0))
cyl('lamp_head', 0.07, 0.1, lampm, dl, (0, -0.12, 0.42), r2=0.03, rot=(-0.9, 0, 0))
uvsphere('lamp_bulb', 0.025, bulb, dl, (0, -0.15, 0.39))
Ll = bpy.data.lights.new('desk_lamp_light', 'POINT'); Ll.color = srgb('#ffc98a')[:3]; Ll.energy = 12; Ll.shadow_soft_size = 0.05
link(bpy.data.objects.new('desk_lamp_light', Ll), dl, (0, -0.16, 0.36))
# mug, notebook, pen, cactus
mug = empty('mug', loc=(-0.55, 0.12, DESK))
teal = mat('#2a9d8f', 0.4, name='mug_teal')
cyl('mug_body', 0.045, 0.1, teal, mug, (0, 0, 0.05))
cyl('tea', 0.04, 0.005, mat('#8a5a2b', 0.2), mug, (0, 0, 0.095))
torus('mug_handle', 0.028, 0.008, teal, mug, (0.05, 0, 0.05), rot=(math.pi / 2, 0, 0))
cube('notebook', (0.17, 0.23, 0.014), mat('#3d405b', 0.7), loc=(0.2, -0.18, DESK + 0.007), rot=(0, 0, 0.15), bevel=0.003)
cube('notebook_pages', (0.16, 0.22, 0.004), mat('#f5f0e6', 0.8), loc=(0.2, -0.18, DESK + 0.016), rot=(0, 0, 0.15))
cyl('pen', 0.004, 0.14, mat('#f2cc8f', 0.4), None, (0.3, -0.2, DESK + 0.022), rot=(math.pi / 2, 0, 0.5))
cyl('cactus_pot', 0.035, 0.05, mat('#e9dfcf', 0.6), None, (-0.7, -0.15, DESK + 0.025))
uvsphere('cactus', 0.03, mat('#5a9b6a', 0.6), None, (-0.7, -0.15, DESK + 0.075), scale=(1, 1, 1.5))

# ------------------------------------------------------------------ CLAUDE (faceted orange cloud with feet)
CL = Vector((-0.22, -0.1, DESK))
orange = mat('#ea6a34', 0.6, name='claude_orange')
claude = empty('claude', loc=CL)
cbody = empty('claude_body', claude, (0, 0, 0.0))
def faceted_cloud(name, parts, m, parent, seed=21):
    """Union of jittered icospheres -> one flat-shaded low-poly mesh (like the reference mascot)."""
    bm = bmesh.new(); rnd = random.Random(seed)
    for (c, r, sc) in parts:
        mtx = Matrix.Translation(Vector(c)) @ Matrix.Diagonal(Vector((sc[0], sc[1], sc[2], 1)))
        res = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r, matrix=mtx)
        for v in res['verts']: v.co += Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * r * 0.03
    return from_bm(name, bm, m, parent, smooth=False)
parts = [((0, 0, 0.095), 0.066, (1, 0.72, 0.95))]
for k in range(8):
    a = k / 8 * 2 * math.pi + math.pi / 8
    parts.append(((math.cos(a) * 0.058, 0.0, 0.095 + math.sin(a) * 0.052), 0.034, (1, 0.8, 1)))
body = facet(faceted_cloud('claude_shape', parts, orange, cbody), 1100)
eyem = mat('#111111', 0.4, name='eye_black')
c_eyes = []
for s in (-1, 1):
    e = cube(f'claude_eye{s}', (0.012, 0.01, 0.03), eyem, cbody, (s * 0.022, -0.05, 0.1), bevel=0.0015)
    c_eyes.append(e)
c_feet = []
for i, (x, y) in enumerate([(-0.034, -0.025), (0.034, -0.025), (-0.03, 0.025), (0.03, 0.025)]):
    c_feet.append(ico(f'claude_foot{i}', 0.02, mat('#d9622e', 0.6), claude, (x, y, 0.017), sub=2, jitter=0.08, seed=10 + i))
ticks = empty('claude_ticks', cbody, (0, 0, 0.2))
for i, a in enumerate((-0.45, 0, 0.45)):
    t = cube('tick', (0.006, 0.006, 0.028), mat('#ffd23f', 0.5, emit='#ffd23f', strength=2), ticks, (math.sin(a) * 0.06, 0, math.cos(a) * 0.02))
    t.rotation_euler = (0, a, 0)

# ------------------------------------------------------------------ MAYA (smooth stylised host)
skin = mat('#f2c1a0', 0.5, sss=0.15, name='skin')
hoodie = add_bump(mat('#1f6f68', 0.85, sheen=0.5, name='hoodie_teal'), 'noise', 180, 0.12)
cuffm = mat('#185953', 0.85, sheen=0.4, name='hoodie_rib')
creamtop = mat('#f1e6d2', 0.8, name='top_cream')
hairm = add_bump(mat('#5a3424', 0.4, name='hair_chestnut'), 'strands', 11, 0.06)
glassm = mat('#1c1410', 0.3, name='glasses_dark')
yellow = hoodie
blacktop = creamtop
MY = 0.74
maya = empty('maya', loc=(0.0, MY, 0))
# chair
chair = mat('#2c2f3d', 0.6)
cube('seat', (0.46, 0.44, 0.06), chair, maya, (0, 0.05, 0.47), bevel=0.02)
cube('back', (0.46, 0.06, 0.6), chair, maya, (0, 0.3, 0.82), bevel=0.02)
cyl('post', 0.025, 0.42, chair, maya, (0, 0.05, 0.24))
# legs (mostly hidden by desk)
pants = mat('#2d2d35', 0.7)
for s in (-1, 1):
    cyl('thigh', 0.07, 0.4, pants, maya, (s * 0.09, -0.12, 0.53), rot=(math.pi / 2, 0, 0))
    cyl('shin', 0.065, 0.45, pants, maya, (s * 0.09, -0.3, 0.27))

torso = empty('torso', maya, (0, 0, 0.52))
facet(blob('hoodie', [
    ((0, 0, 0.2), (0.165, 0.125, 0.22)),
    ((-0.13, 0, 0.33), (0.095, 0.095, 0.085)), ((0.13, 0, 0.33), (0.095, 0.095, 0.085)),   # shoulders
    ((0, 0.01, 0.05), (0.17, 0.13, 0.07)),                                                  # hem band
], hoodie, torso), 520)
facet(blob('hood', [((0, 0.09, 0.4), (0.12, 0.07, 0.07)), ((-0.08, 0.06, 0.41), (0.06, 0.06, 0.05)), ((0.08, 0.06, 0.41), (0.06, 0.06, 0.05))], cuffm, torso), 160)
torus('tee_collar', 0.046, 0.009, creamtop, torso, (0, -0.004, 0.425), rot=(0.15, 0, 0))
for sx in (-1, 1):
    cyl('drawstring', 0.0045, 0.16, creamtop, torso, (sx * 0.035, -0.128, 0.3), rot=(0.12, 0, 0))
    uvsphere('aglet', 0.007, creamtop, torso, (sx * 0.035, -0.138, 0.22))
cyl('neck', 0.04, 0.09, skin, torso, (0, 0, 0.43))

head = empty('head', torso, (0, 0, 0.385))
HC = Vector((0, 0, 0.15)); R = 0.15
facet(uvsphere('head_skin', R, skin, head, HC, scale=(1.0, 0.95, 0.98), seg=48, ring=24), 420)
for s in (-1, 1): uvsphere('ear', 0.028, skin, head, HC + Vector((s * 0.148, 0.0, -0.01)), scale=(0.5, 0.8, 1))
uvsphere('nose', 0.012, skin, head, HC + Vector((0, -0.142, -0.02)), scale=(1, 0.8, 0.8))
# hair: top bun, centre-parted curtain bangs, face-framing strands, short nape
hair_elems = [
    (HC + Vector((0, 0.04, 0.04)), (0.152, 0.148, 0.15)),              # cap
    (HC + Vector((-0.07, -0.1, 0.07)), (0.065, 0.04, 0.05)),           # curtain bang left
    (HC + Vector((0.07, -0.1, 0.07)), (0.065, 0.04, 0.05)),            # curtain bang right
    (HC + Vector((-0.11, -0.085, 0.035)), (0.04, 0.035, 0.05)),
    (HC + Vector((0.11, -0.085, 0.035)), (0.04, 0.035, 0.05)),
    (HC + Vector((-0.125, -0.055, -0.01)), (0.026, 0.03, 0.08)),       # face-framing strands
    (HC + Vector((0.125, -0.055, -0.01)), (0.026, 0.03, 0.08)),
    (HC + Vector((-0.13, -0.045, -0.09)), (0.022, 0.028, 0.06)),
    (HC + Vector((0.13, -0.045, -0.09)), (0.022, 0.028, 0.06)),
    (HC + Vector((0, 0.11, -0.07)), (0.12, 0.07, 0.09)),               # short nape
]
facet(blob('hair', hair_elems, hairm, head, res=0.007), 650)
facet(uvsphere('bun', 0.075, hairm, head, HC + Vector((0, 0.075, 0.205)), scale=(1, 1, 0.9)), 90)
torus('hair_tie', 0.045, 0.011, mat('#e07a5f', 0.5), head, HC + Vector((0, 0.06, 0.155)), rot=(0.35, 0, 0))
# face
m_eyes, brows = [], []
for s in (-1, 1):
    ring = torus(f'glasses{s}', 0.047, 0.0026, glassm, head, HC + Vector((s * 0.058, -0.145, 0.0)), rot=(math.pi / 2, 0, -s * 0.15))
    eye = uvsphere(f'eye{s}', 0.0085, eyem, head, HC + Vector((s * 0.056, -0.141, -0.004)), scale=(0.85, 0.5, 1.2))
    m_eyes.append(eye)
    b = uvsphere(f'brow{s}', 0.016, mat('#3a2418', 0.6), head, HC + Vector((s * 0.058, -0.137, 0.065)), scale=(1.4, 0.3, 0.16))
    b.rotation_euler = (0, s * 0.08, 0); brows.append(b)
cube('bridge', (0.022, 0.004, 0.004), glassm, head, HC + Vector((0, -0.152, 0.005)))
mouth = uvsphere('mouth', 0.01, mat('#2a1414', 0.6), head, HC + Vector((0, -0.142, -0.068)), scale=(1.3, 0.3, 0.25))

# arms: shoulder pivot -> upper arm, elbow pivot -> forearm + mitten
def capsule(name, r, length, m, parent):
    return blob(name, [((0, 0, -length * 0.15), (r, r, r)), ((0, 0, -length * 0.5), (r, r, r)), ((0, 0, -length * 0.85), (r * 0.95, r * 0.95, r * 0.95))], m, parent, res=0.006)
arms = {}
for s in (-1, 1):
    sh = empty(f'shoulder{s}', torso, (s * 0.165, 0, 0.34)); sh.rotation_mode = 'QUATERNION'
    facet(capsule(f'upper{s}', 0.055, 0.2, yellow, sh), 140)
    el = empty(f'elbow{s}', sh, (0, 0, -0.19)); el.rotation_mode = 'QUATERNION'
    facet(capsule(f'fore{s}', 0.05, 0.19, yellow, el), 140)
    facet(uvsphere(f'hand{s}', 0.04, skin, el, (0, 0, -0.205), scale=(0.95, 0.8, 1.1)), 80)
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
    mouth.scale = (1.3 - me * 0.3, 0.3, 0.22 + me * 1.5)
    by = 0.065 + me * 0.008 - (0.006 if (L['who'] == 'C' and L['act'] in ('look-away', 'squint')) else 0)
    for b in brows: b.location.z = HC.z + by
    mb = 0.1 if ((t + 1.3) % 4.1) < 0.13 else 1
    for e in m_eyes: e.scale = (0.85, 0.5, 1.2 * mb)
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
