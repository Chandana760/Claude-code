"""
Alternate set: night "classroom" lesson.

Run AFTER cozy_desk_studio.py + desk_characters.py (animate.py does this with
`--set classroom`). Keeps the window, city and sky of the standard room and turns
the desk corner into a little lesson:
  * whiteboard on an easel behind the desk (text from the episode's BOARD_IMAGE,
    or a blank title line for a test)
  * Claude standing on a stack of coloured books on the desk, holding a pointer
  * Maya in her chair on the right, turned toward the board, arms crossed
  * bookshelf, hanging ivy and pink neon strips; mug, pencil cup, notebook
Maya and Claude themselves are unchanged (character lock). Cameras:
  Cam_Wide   - the whole lesson: board, Claude on the books, Maya at the right
  Cam_Mascot - Claude close with his pointer, room lights soft behind
  Cam_Human  - Maya three-quarter, looking at the board / Claude
"""
import math
import os

import bmesh
import bpy
from mathutils import Euler, Matrix, Quaternion, Vector

R = math.radians


def hx(h):
    def c(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return tuple(c(int(h[i:i + 2], 16)) for i in (1, 3, 5))


def _mat(name, color, rough=0.8, emit=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        for n in ("Emission Color", "Emission"):
            if n in b.inputs:
                b.inputs[n].default_value = (*color, 1)
                break
        b.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = (*color, 1)
    return m


def _mesh(name, builders, material, coll, parent=None):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for b in builders:
        b(bm)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = False
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if parent:
        ob.parent = parent
    return ob


def _box(loc, size, bevel=0.0, rot=(0, 0, 0)):
    mtx = Matrix.LocRotScale(Vector(loc), Euler(tuple(R(a) for a in rot)), Vector(size))

    def b(bm):
        vs = bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)["verts"]
        if bevel:
            es = list({e for v in vs for e in v.link_edges})
            bmesh.ops.bevel(bm, geom=vs + es, offset=bevel, segments=2, affect="EDGES", profile=0.5)
    return b


def _cyl(p1, p2, r, seg=8):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    mtx = Matrix.Translation((p1 + p2) / 2) @ q.to_matrix().to_4x4()
    return lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                                            radius1=r, radius2=r, depth=d.length, matrix=mtx)


def _leaf(loc, size, rot):
    mtx = Matrix.LocRotScale(Vector(loc), Euler(tuple(R(a) for a in rot)), Vector((size, size * 0.12, size * 0.75)))
    return lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mtx)


def _area(name, coll, loc, target, color, energy, size):
    ld = bpy.data.lights.get(name) or bpy.data.lights.new(name, "AREA")
    ld.color, ld.energy, ld.size = color, energy, size
    ob = bpy.data.objects.new(name, ld)
    coll.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if hasattr(ob, "visible_camera"):
        ob.visible_camera = False
    return ob


def _aim_cam(name, loc, target, lens, fstop, focus=None):
    cam = bpy.data.objects[name]
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = fstop
    if focus is not None:
        cam.data.dof.focus_object = focus
    if "base_lens" in cam:
        del cam["base_lens"]


def board_texture(path, title="", lines=()):
    """Whiteboard face: marker title + rule (and optional lines) as an image."""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1400, 980
    img = Image.new("RGB", (W, H), (246, 246, 242))
    d = ImageDraw.Draw(img)
    font_t = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 78)
    font_l = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 58)
    if title:
        d.text((W / 2, 120), title, font=font_t, fill=(30, 32, 40), anchor="mm")
    d.line((140, 200, W - 140, 200), fill=(30, 32, 40), width=8)
    for k, (txt, col) in enumerate(lines):
        d.text((180, 300 + k * 110), txt, font=font_l, fill=col, anchor="lm")
    img.save(path)
    return path


# Layout (metres)
DESK_X = -0.48                                  # desk slides left; Maya's chair sits at the right
PODIUM = Vector((-0.84, -0.04, 0.75))           # Claude's little wooden step podium on the desk
BOARD = Vector((-0.10, 0.55, 1.62))             # whiteboard centre (on its easel)
BOARD_W, BOARD_H = 1.10, 0.78
MAYA = Vector((0.74, -0.04, 0.0))                # her chair
MAYA_YAW = -92                                  # turned toward the board / Claude
FONT_HAND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "PatrickHand-Regular.ttf")


def _tube(points, r0, r1, seg=10):
    """Swept tube through points (simple frames), capped - for legs."""
    def b(bm):
        P = [Vector(p) for p in points]
        rings, ref = [], Vector((1, 0, 0))
        for k, p in enumerate(P):
            tan = (P[min(len(P) - 1, k + 1)] - P[max(0, k - 1)]).normalized()
            side = tan.cross(ref)
            if side.length < 1e-3:
                side = tan.cross(Vector((0, 1, 0)))
            side.normalize()
            up = side.cross(tan).normalized()
            r = r0 + (r1 - r0) * k / (len(P) - 1)
            rings.append([bm.verts.new(p + (side * math.cos(2 * math.pi * a / seg) + up * math.sin(2 * math.pi * a / seg)) * r)
                          for a in range(seg)])
        for k in range(len(rings) - 1):
            for a in range(seg):
                bm.faces.new((rings[k][a], rings[k][(a + 1) % seg], rings[k + 1][(a + 1) % seg], rings[k + 1][a]))
        for ring in (rings[0], rings[-1]):
            bm.faces.new(ring)
    return b


def _ico(loc, r, scale=(1, 1, 1), sub=2):
    mtx = Matrix.LocRotScale(Vector(loc), None, Vector(scale))
    return lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r, matrix=mtx)


def build_seated_body(root, coll):
    """Her lower body for sitting (hips, legs, sneakers) - the bust above is untouched."""
    pants = _mat("M_Char_Pants", hx("#3B4A6B"), rough=0.85)            # mid denim
    shoe = _mat("M_Char_Sneaker", hx("#EEE7DA"), rough=0.6)
    sole = _mat("M_Char_SneakerSole", hx("#B9AFA2"), rough=0.7)
    legs = []
    legs.append(_box((0, 0.02, 0.63), (0.40, 0.36, 0.20), bevel=0.06))       # hips / seat of the trousers
    for sx in (1, -1):
        x = sx * 0.105
        legs.append(_tube([(x, 0.02, 0.62), (x, -0.20, 0.615), (x * 1.04, -0.40, 0.60)], 0.095, 0.085))   # thigh
        legs.append(_ico((x * 1.04, -0.41, 0.585), 0.085, sub=2))                                       # knee
        legs.append(_tube([(x * 1.04, -0.42, 0.57), (x * 1.06, -0.44, 0.32), (x * 1.06, -0.45, 0.12)], 0.078, 0.068))  # shin
    ob = _mesh("Human_Legs", legs, pants, coll, parent=root)
    shoes = []
    for sx in (1, -1):
        x = sx * 0.112
        shoes.append(_box((x, -0.52, 0.055), (0.115, 0.24, 0.09), bevel=0.03))
    sh = _mesh("Human_Shoes", shoes, shoe, coll, parent=root)
    _mesh("Human_ShoeSoles", [_box((sx * 0.112, -0.52, 0.012), (0.12, 0.245, 0.024), bevel=0.008) for sx in (1, -1)],
          sole, coll, parent=root)
    return ob


def build_chair(root, coll):
    """Ergonomic office chair: padded waterfall seat, lumbar-curved back, armrests,
    gas lift and a five-star base on caster wheels (mustard upholstery, graphite frame)."""
    up = _mat("M_Chair_Mustard", hx("#D6A23A"), rough=0.8)
    frame = _mat("M_Chair_Frame", hx("#2B2B31"), rough=0.4)
    wheel = _mat("M_Chair_Wheel", hx("#151518"), rough=0.5)
    seat = [_box((0, 0.06, 0.505), (0.50, 0.46, 0.08), bevel=0.035),               # padded seat
            _box((0, -0.16, 0.49), (0.48, 0.06, 0.06), bevel=0.025, rot=(-25, 0, 0))]  # waterfall front edge
    back = []
    for k, (y, z, h, tilt) in enumerate(((0.30, 0.66, 0.16, -2), (0.32, 0.80, 0.16, -8), (0.345, 0.95, 0.18, -14))):
        back.append(_box((0, y, z), (0.46 - 0.02 * k, 0.07, h), bevel=0.03, rot=(tilt, 0, 0)))   # lumbar -> upper back curve
    _mesh("Maya_Chair_Cushions", seat + back, up, coll, parent=root)
    parts = [_cyl((0, 0.06, 0.46), (0, 0.06, 0.16), 0.03),                          # gas lift
             _cyl((0, 0.06, 0.16), (0, 0.06, 0.10), 0.045),
             _box((0, 0.06, 0.455), (0.26, 0.24, 0.03)),                           # seat mechanism
             _box((0, 0.27, 0.55), (0.06, 0.05, 0.14), rot=(-10, 0, 0))]            # back bracket
    for sx in (1, -1):                                                              # armrests
        parts += [_box((sx * 0.27, 0.12, 0.56), (0.035, 0.05, 0.16)),
                  _box((sx * 0.27, 0.06, 0.645), (0.07, 0.28, 0.035), bevel=0.014)]
    wheels = []
    for k in range(5):                                                              # star base + casters
        a = math.radians(90 + k * 72)
        end = (0.31 * math.cos(a), 0.06 + 0.31 * math.sin(a))
        parts.append(_cyl((0, 0.06, 0.11), (end[0], end[1], 0.075), 0.022))
        parts.append(_cyl((end[0], end[1], 0.075), (end[0], end[1], 0.055), 0.012))
        wheels.append(_cyl((end[0] - 0.025, end[1], 0.03), (end[0] + 0.025, end[1], 0.03), 0.03, seg=10))
    _mesh("Maya_Chair_Frame", parts, frame, coll, parent=root)
    _mesh("Maya_Chair_Wheels", wheels, wheel, coll, parent=root)


def apply_classroom_set():
    sc = bpy.context.scene
    sc["set"] = "classroom"
    room = bpy.data.collections.get("Background")
    lights = bpy.data.collections.get("Lighting")
    chars = bpy.data.collections.get("Characters") or room

    # 1. Clean lesson desk: mug at one end, pen holder + notebook at the other
    for name in ("Monitor", "Keyboard", "DeskLamp", "Plant", "StickyNotes"):
        root = bpy.data.objects.get(name)
        if root:
            for o in [root] + list(root.children_recursive):
                bpy.data.objects.remove(o, do_unlink=True)
    desk = bpy.data.objects["Desk"]
    desk.location.x = DESK_X
    top_ob = bpy.data.objects.get("Desk_Top")
    if top_ob:
        top_ob.scale.x = 0.80                                  # shorter desk: she sits right at its end
    old_legs = bpy.data.objects.get("Desk_Legs")
    if old_legs:
        legs_mat = old_legs.data.materials[0]
        bpy.data.objects.remove(old_legs, do_unlink=True)
        _mesh("Desk_Legs", [_box((DESK_X + (0.34 if sx > 0 else -0.56), sy * 0.27, 0.35), (0.05, 0.05, 0.70)) for sx in (1, -1) for sy in (1, -1)],
              legs_mat, room)
    mug = bpy.data.objects.get("Mug")
    if mug:
        mug.location.x, mug.location.y = -1.06, -0.14
    PX, PY, PZ = 0.04, 0.02, 0.75
    _mesh("Pencil_Cup", [lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.042,
                                                          radius2=0.046, depth=0.11, matrix=Matrix.Translation((PX, PY, PZ + 0.055)))],
          _mat("M_PencilCup", hx("#3E5C76"), rough=0.6), room)
    pens = [(_cyl((PX + dx, PY + dy, PZ + 0.03), (PX + dx * 2.4, PY + dy * 2.4, PZ + 0.20), 0.0065, seg=6), c)
            for (dx, dy), c in (((0.012, 0.0), "#F2C14E"), ((-0.011, 0.01), "#E24B5B"), ((0.0, -0.013), "#3D7DD8"))]
    for k, (b, c) in enumerate(pens):
        _mesh(f"Pen_{k}", [b], _mat(f"M_Pen_{k}", hx(c), rough=0.5), room)
    _mesh("Notebook", [_box((-0.16, -0.12, 0.765), (0.22, 0.16, 0.03), bevel=0.004, rot=(0, 0, 6)),
                       _box((-0.155, -0.12, 0.79), (0.20, 0.15, 0.02), bevel=0.004, rot=(0, 0, -4))],
          _mat("M_Notebook", hx("#7FB7A4"), rough=0.7), room)

    # 2. Claude on a small wooden step podium, with his teaching pointer
    wood = _mat("M_Podium_Wood", hx("#B98552"), rough=0.6)
    top_m = _mat("M_Podium_Top", hx("#F1E6D2"), rough=0.7)
    PH = 0.27                                                     # podium height (about the reference's book stack)
    _mesh("Claude_Podium", [_box((PODIUM.x, PODIUM.y, PODIUM.z + PH / 2), (0.30, 0.26, PH), bevel=0.012),
                            _box((PODIUM.x + 0.18, PODIUM.y - 0.02, PODIUM.z + 0.07), (0.10, 0.22, 0.14), bevel=0.01),     # step
                            _box((PODIUM.x + 0.25, PODIUM.y - 0.02, PODIUM.z + 0.035), (0.08, 0.22, 0.07), bevel=0.01)],   # lower step
          wood, room)
    _mesh("Claude_Podium_Top", [_box((PODIUM.x, PODIUM.y, PODIUM.z + PH + 0.004), (0.31, 0.27, 0.008))], top_m, room)
    top = PODIUM.z + PH + 0.008
    mroot = bpy.data.objects["Mascot_Root"]
    mroot.location = (PODIUM.x, PODIUM.y, top)
    mroot.rotation_euler = (0, 0, R(-8))
    bounce = bpy.data.objects.get("Mascot_Bounce") or mroot
    bpy.context.view_layer.update()
    # pointer pivots at his right side; animate.py swings it to whatever is being written
    ptr_m = _mat("M_Pointer", hx("#EFE4CC"), rough=0.5)
    ptr = _mesh("Claude_Pointer", [_cyl((0, 0, 0), (0, 0, 0.78), 0.0075, seg=6),
                                   _cyl((0, 0, 0.78), (0, 0, 0.80), 0.010, seg=6)], ptr_m, room)
    pivot_world = mroot.matrix_world @ Vector((0.11, -0.05, 0.10))   # held right at his side
    ptr.parent = bounce
    ptr.matrix_parent_inverse = bounce.matrix_world.inverted()
    ptr.location = pivot_world
    ptr.rotation_mode = "QUATERNION"
    rest_dir = (Vector((BOARD.x - 0.30, BOARD.y, BOARD.z - 0.20)) - pivot_world).normalized()
    ptr.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(rest_dir)
    sc["pointer_pivot"] = tuple(pivot_world)

    # 3. Whiteboard on an easel, marker tray with markers; animate.py writes on it line by line
    frame_m = _mat("M_Board_Frame", (0.62, 0.63, 0.66), rough=0.35)
    bw, bh = BOARD_W, BOARD_H
    _mesh("Board_Frame", [_box((BOARD.x, BOARD.y + 0.012, BOARD.z), (bw + 0.05, 0.03, bh + 0.05), bevel=0.006),
                          _box((BOARD.x, BOARD.y - 0.025, BOARD.z - bh / 2 - 0.035), (bw * 0.75, 0.07, 0.015))],
          frame_m, room)
    for k, c in enumerate(("#2F5FD0", "#D83A3A", "#2E9E5B", "#222222")):
        _mesh(f"Board_Marker_{k}", [_cyl((BOARD.x - 0.30 + k * 0.09, BOARD.y - 0.035, BOARD.z - bh / 2 - 0.020),
                                         (BOARD.x - 0.23 + k * 0.09, BOARD.y - 0.035, BOARD.z - bh / 2 - 0.020), 0.009, seg=6)],
              _mat(f"M_Marker_{k}", hx(c), rough=0.4), room)
    legs_m = _mat("M_Easel", (0.10, 0.10, 0.12), rough=0.5)
    _mesh("Board_Easel", [_cyl((BOARD.x - 0.42, BOARD.y + 0.06, 0.0), (BOARD.x - 0.38, BOARD.y + 0.04, BOARD.z + 0.30), 0.014),
                          _cyl((BOARD.x + 0.42, BOARD.y + 0.06, 0.0), (BOARD.x + 0.38, BOARD.y + 0.04, BOARD.z + 0.30), 0.014),
                          _cyl((BOARD.x, BOARD.y + 0.50, 0.0), (BOARD.x, BOARD.y + 0.05, BOARD.z + 0.30), 0.012)],
          legs_m, room)
    test_png = os.path.join(os.environ.get("BOARD_DIR") or os.path.dirname(bpy.data.filepath) or ".", "board_blank.png")
    img_path = board_texture(test_png, title="")
    bm_mat = bpy.data.materials.new("M_Board_Face")
    bm_mat.use_nodes = True
    nt = bm_mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = 0.35
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.name = "BoardImage"
    tex.image = bpy.data.images.load(img_path, check_existing=False)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    for n in ("Emission Color", "Emission"):
        if n in bsdf.inputs:
            nt.links.new(tex.outputs["Color"], bsdf.inputs[n])
            break
    bsdf.inputs["Emission Strength"].default_value = 0.35
    me = bpy.data.meshes.new("Board_Face")
    bmx = bmesh.new()
    uv = bmx.loops.layers.uv.new()
    vs = [bmx.verts.new((BOARD.x + sx * bw / 2, BOARD.y - 0.004, BOARD.z + sz * bh / 2)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    f = bmx.faces.new(vs)
    for loop, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop[uv].uv = (u, v)
    bmx.to_mesh(me)
    bmx.free()
    me.materials.append(bm_mat)
    room.objects.link(bpy.data.objects.new("Board_Face", me))
    sc["board_geom"] = (BOARD.x, BOARD.y - 0.004, BOARD.z, bw, bh)
    sc["board_font"] = FONT_HAND

    # 4. Maya: seated properly in her chair at the right, turned to the board
    root = bpy.data.objects["Human_Root"]
    old_chair = bpy.data.objects.get("Human_Chair")
    if old_chair:
        bpy.data.objects.remove(old_chair, do_unlink=True)
    root.location = MAYA
    root.rotation_euler = (0, 0, R(MAYA_YAW))
    build_seated_body(root, chars)
    build_chair(root, chars)
    sc["head_pose_offset"] = (R(-8), 0.0, R(16))        # chin up a touch, eyes on the board (cancels the desk-set turn)

    # 5. Room dressing: bookshelf, ivy, pink neon strips
    shelf_m = _mat("M_Shelf_Wood", (0.16, 0.08, 0.04), rough=0.7)
    SX, SY = 1.55, 1.05
    parts = [_box((SX, SY, z), (0.70, 0.30, 0.03)) for z in (0.85, 1.25, 1.65, 2.05)]
    parts += [_box((SX - 0.36, SY, 1.10), (0.03, 0.30, 2.20)), _box((SX + 0.36, SY, 1.10), (0.03, 0.30, 2.20)),
              _box((SX, SY + 0.14, 1.10), (0.70, 0.02, 2.20))]
    _mesh("Bookshelf", parts, shelf_m, room)
    cols = ("#E24B5B", "#3D7DD8", "#F2C14E", "#4E8B5A", "#8E5BD0", "#F08A3C", "#2FA7A0", "#EDE4D3")
    k = 0
    for shelf_z in (0.865, 1.265, 1.665):
        x = SX - 0.32
        while x < SX + 0.30:
            w = 0.035 + 0.02 * ((k * 7) % 3) / 2
            h = 0.22 + 0.06 * ((k * 5) % 4) / 3
            tilt = 8 if k % 9 == 4 else 0
            _mesh(f"Shelf_Book_{k}", [_box((x + w / 2, SY - 0.02, shelf_z + h / 2), (w, 0.20, h), rot=(0, tilt, 0))],
                  _mat(f"M_ShelfBook_{k % len(cols)}", hx(cols[k % len(cols)]), rough=0.7), room)
            x += w + 0.006
            k += 1
    leaf_m = _mat("M_Ivy", hx("#4F8A3C"), rough=0.7)
    leaves = []
    for strand, (x0, len_) in enumerate(((-1.05, 0.9), (-0.92, 0.6), (-0.80, 1.1), (1.20, 0.7), (1.32, 1.0))):
        n = int(len_ / 0.07)
        for i in range(n):
            z = 2.70 - i * 0.07
            x = x0 + 0.03 * math.sin(i * 1.3 + strand)
            leaves.append(_leaf((x, 1.12, z), 0.045, (90, (i * 47 + strand * 30) % 360, (i * 33) % 50 - 25)))
    _mesh("Ivy_Leaves", leaves, leaf_m, room)
    neon = _mat("M_Neon_Pink", hx("#FF4FB0"), emit=6.0)
    _mesh("Neon_Strips", [_box((-1.18, 1.14, 1.85), (0.025, 0.02, 1.5)), _box((1.18, 1.14, 1.85), (0.025, 0.02, 1.5)),
                          _box((0.0, 1.14, 2.80), (2.30, 0.02, 0.025))], neon, room)

    # city right behind the board, seen through the window: dark towers with lit windows
    tower = _mat("M_City_Tower", (0.035, 0.03, 0.06), rough=0.9)
    warm = _mat("M_City_Window_Warm", (1.0, 0.70, 0.35), emit=5.0)
    cool = _mat("M_City_Window_Cool", (0.55, 0.80, 1.0), emit=4.0)
    blds, win_w, win_c = [], [], []
    for k, (x, w, h) in enumerate(((-0.95, 0.42, 1.95), (-0.48, 0.36, 2.25), (-0.05, 0.48, 1.80), (0.42, 0.34, 2.10), (0.85, 0.40, 1.70))):
        y = 2.05 + 0.15 * (k % 2)
        blds.append(_box((x, y, h / 2), (w, 0.30, h)))
        for r in range(int((h - 1.0) / 0.12)):
            for c in range(int(w / 0.09)):
                if (k * 7 + r * 3 + c * 5) % 4 == 0:
                    zz = 1.05 + r * 0.12
                    xx = x - w / 2 + 0.06 + c * 0.09
                    (win_c if (k + r + c) % 7 == 0 else win_w).append(_box((xx, y - 0.16, zz), (0.045, 0.01, 0.06)))
    _mesh("City_BehindBoard", blds, tower, room)
    if win_w:
        _mesh("City_BehindBoard_WinWarm", win_w, warm, room)
    if win_c:
        _mesh("City_BehindBoard_WinCool", win_c, cool, room)

    # 6. Lighting
    for name in ("Fill_MonitorGlow", "Practical_DeskLamp"):
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    lc = lights or room
    _area("Neon_PinkSpill_L", lc, (-1.10, 0.95, 1.9), (-0.4, 0.0, 1.2), hx("#FF4FB0"), 25, 0.4)
    _area("Neon_PinkSpill_R", lc, (1.10, 0.95, 1.9), (0.8, 0.0, 1.2), hx("#FF4FB0"), 22, 0.4)
    _area("Board_Fill", lc, (-0.10, -0.80, 2.30), tuple(BOARD), (1.0, 0.92, 0.82), 40, 1.0)
    _area("Room_Fill", lc, (0.6, -2.0, 1.2), (0.3, 0.2, 0.6), (0.85, 0.80, 1.0), 30, 2.0)
    k = bpy.data.objects.get("Key_MayaWarm")
    head = MAYA + Vector((0, 0, 1.36))
    if k:
        k.location = head + Vector((-0.55, -0.55, 0.30))
        k.rotation_euler = (head - k.location).to_track_quat("-Z", "Y").to_euler()
    claude = Vector((PODIUM.x, PODIUM.y, top + 0.12))
    rim = bpy.data.objects.get("Rim_MascotWarm")
    if rim:
        rim.location = claude + Vector((0.35, 0.35, 0.40))
        rim.rotation_euler = (claude - rim.location).to_track_quat("-Z", "Y").to_euler()
    key = bpy.data.objects.get("Key_DeskWarm")
    if key:
        key.location = (0.2, -1.4, 2.0)
        key.rotation_euler = (Vector((-0.2, 0.2, 1.0)) - key.location).to_track_quat("-Z", "Y").to_euler()

    # 7. Cameras (four shots, like the reference): wide, board, Claude, Maya
    if "Cam_Board" not in bpy.data.objects:
        cd = bpy.data.cameras.new("Cam_Board")
        cb = bpy.data.objects.new("Cam_Board", cd)
        (bpy.data.collections.get("Cameras") or sc.collection).objects.link(cb)
        cd.sensor_fit = bpy.data.objects["Cam_Wide"].data.sensor_fit
    _aim_cam("Cam_Wide", (0.02, -2.20, 1.12), (-0.06, 0.30, 1.30), 23, 4.0)                  # low wide: board high
    _aim_cam("Cam_Board", (-0.50, -1.80, 1.05), (-0.38, 0.45, 1.36), 26, 4.0)               # board + Claude pointing
    _aim_cam("Cam_Mascot", claude + Vector((0.30, -0.85, -0.04)), claude + Vector((0.08, 0.0, 0.12)), 36, 1.8,
             focus=bpy.data.objects.get("Mascot_FocusTarget"))
    _aim_cam("Cam_Human", head + Vector((-1.00, -0.85, -0.12)), head + Vector((0.0, 0.0, -0.14)), 40, 1.8,
             focus=bpy.data.objects.get("Human_FocusTarget"))


apply_classroom_set()
