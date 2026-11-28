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
DESK_X = -0.45                                  # desk slides left; Maya's chair sits at the right
BOOKS = Vector((-0.62, -0.06, 0.75))            # book stack on the desk (Claude's podium)
BOARD = Vector((-0.12, 0.55, 1.55))             # whiteboard centre (on its easel)
MAYA = Vector((0.80, 0.02, 0.0))                # her chair
MAYA_YAW = -68                                  # turned toward the board / Claude


def apply_classroom_set():
    sc = bpy.context.scene
    sc["set"] = "classroom"
    room = bpy.data.collections.get("Background")
    lights = bpy.data.collections.get("Lighting")

    # 1. Desk corner -> lesson desk: keep desk, mug and notes; drop monitor, keyboard, lamp, plant
    for name in ("Monitor", "Keyboard", "DeskLamp", "Plant"):
        root = bpy.data.objects.get(name)
        if root:
            for o in [root] + list(root.children_recursive):
                bpy.data.objects.remove(o, do_unlink=True)
    desk = bpy.data.objects["Desk"]
    desk.location.x = DESK_X
    for name, loc in (("Mug", (-0.22, -0.20)), ("StickyNotes", (-0.95, -0.20))):
        o = bpy.data.objects.get(name)
        if o:
            o.location.x, o.location.y = loc

    # 2. Book stack + Claude with his pointer
    stack = []
    for k, (col, rz, h) in enumerate(((hx("#4E8B5A"), 4, 0.075), (hx("#6B4E9B"), -5, 0.07), (hx("#D9A93A"), 3, 0.07))):
        z = BOOKS.z + sum(x[2] for x in ((0, 0, 0.075), (0, 0, 0.07), (0, 0, 0.07))[:k])
        stack.append((col, rz, h, z))
    for k, (col, rz, h, z) in enumerate(stack):
        _mesh(f"Books_{k}", [_box((BOOKS.x, BOOKS.y, z + h / 2), (0.36 - 0.02 * k, 0.27, h), bevel=0.008, rot=(0, 0, rz))],
              _mat(f"M_Book_{k}", col, rough=0.75), room)
        _mesh(f"Books_{k}_Pages", [_box((BOOKS.x + 0.004, BOOKS.y - 0.004, z + h / 2), (0.34 - 0.02 * k, 0.262, h * 0.7), rot=(0, 0, rz))],
              _mat("M_BookPages", (0.92, 0.89, 0.80)), room)
    top = stack[-1][3] + stack[-1][2]
    mroot = bpy.data.objects["Mascot_Root"]
    mroot.location = (BOOKS.x, BOOKS.y, top)
    mroot.rotation_euler = (0, 0, R(-8))
    # pointer: from Claude's right side up toward the board (rides along with his hops)
    bounce = bpy.data.objects.get("Mascot_Bounce") or mroot
    ptr = _mesh("Claude_Pointer", [_cyl((0.15, -0.02, 0.10), (0.42, 0.30, 0.62), 0.0075, seg=6),
                                   _cyl((0.42, 0.30, 0.62), (0.44, 0.32, 0.65), 0.009, seg=6)],
                _mat("M_Pointer", (0.85, 0.78, 0.62), rough=0.5), room, parent=bounce)

    # 3. Whiteboard on an easel (episode can supply its own board image)
    frame_m = _mat("M_Board_Frame", (0.55, 0.56, 0.60), rough=0.4)
    bw, bh = 1.05, 0.74
    _mesh("Board_Frame", [_box((BOARD.x, BOARD.y + 0.012, BOARD.z), (bw + 0.05, 0.03, bh + 0.05), bevel=0.006),
                          _box((BOARD.x, BOARD.y - 0.02, BOARD.z - bh / 2 - 0.035), (bw * 0.7, 0.07, 0.015))],   # marker tray
          frame_m, room)
    legs_m = _mat("M_Easel", (0.12, 0.12, 0.14), rough=0.5)
    _mesh("Board_Easel", [_cyl((BOARD.x - 0.40, BOARD.y + 0.06, 0.0), (BOARD.x - 0.36, BOARD.y + 0.04, BOARD.z + 0.25), 0.014),
                          _cyl((BOARD.x + 0.40, BOARD.y + 0.06, 0.0), (BOARD.x + 0.36, BOARD.y + 0.04, BOARD.z + 0.25), 0.014),
                          _cyl((BOARD.x, BOARD.y + 0.45, 0.0), (BOARD.x, BOARD.y + 0.05, BOARD.z + 0.25), 0.012)],
          legs_m, room)
    img_path = sc.get("board_image") or board_texture(os.path.join(os.environ.get("BOARD_DIR") or os.path.dirname(bpy.data.filepath) or ".", "board_test.png"),
                                                      title="Today's lesson")
    bm_mat = bpy.data.materials.new("M_Board_Face")
    bm_mat.use_nodes = True
    nt = bm_mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = 0.35
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(img_path, check_existing=False)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    for n in ("Emission Color", "Emission"):
        if n in bsdf.inputs:
            nt.links.new(tex.outputs["Color"], bsdf.inputs[n])
            break
    bsdf.inputs["Emission Strength"].default_value = 0.35            # board stays readable in the night room
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

    # 4. Maya in her chair at the right, turned to the board, arms crossed
    root = bpy.data.objects["Human_Root"]
    root.location = MAYA
    root.rotation_euler = (0, 0, R(MAYA_YAW))
    sc["head_pose_offset"] = (R(-6), 0.0, R(-6))       # chin up a touch: watching the board

    # 5. Room dressing: bookshelf, ivy, neon strips, pencil cup, notebook
    shelf_m = _mat("M_Shelf_Wood", (0.16, 0.08, 0.04), rough=0.7)
    SX, SY = 1.55, 1.05
    parts = [_box((SX, SY, 0.85), (0.70, 0.30, 0.03)), _box((SX, SY, 1.25), (0.70, 0.30, 0.03)),
             _box((SX, SY, 1.65), (0.70, 0.30, 0.03)), _box((SX, SY, 2.05), (0.70, 0.30, 0.03)),
             _box((SX - 0.36, SY, 1.10), (0.03, 0.30, 2.20)), _box((SX + 0.36, SY, 1.10), (0.03, 0.30, 2.20)),
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
    cup_m = _mat("M_PencilCup", hx("#2F6F6A"), rough=0.6)
    PX, PY, PZ = -0.10, 0.10, 0.75
    _mesh("Pencil_Cup", [lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=10, radius1=0.04,
                                                          radius2=0.045, depth=0.11, matrix=Matrix.Translation((PX, PY, PZ + 0.055)))],
          cup_m, room)
    pencils = [_cyl((PX + dx, PY + dy, PZ + 0.03), (PX + dx * 2.2, PY + dy * 2.2, PZ + 0.19), 0.006, seg=6)
               for dx, dy in ((0.012, 0.0), (-0.01, 0.01), (0.0, -0.012))]
    _mesh("Pencils", pencils, _mat("M_Pencil", hx("#F2C14E"), rough=0.6), room)
    _mesh("Notebook", [_box((-0.98, 0.05, 0.765), (0.22, 0.16, 0.03), bevel=0.004, rot=(0, 0, 12))],
          _mat("M_Notebook", hx("#E85D8C"), rough=0.7), room)

    # 6. Lighting: remove the desk lamp / monitor glow, add the neon pink spill
    for name in ("Fill_MonitorGlow", "Practical_DeskLamp"):
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    lc = lights or room
    _area("Neon_PinkSpill_L", lc, (-1.10, 0.95, 1.9), (-0.4, 0.0, 1.2), hx("#FF4FB0"), 25, 0.4)
    _area("Neon_PinkSpill_R", lc, (1.10, 0.95, 1.9), (0.8, 0.0, 1.2), hx("#FF4FB0"), 22, 0.4)
    _area("Board_Fill", lc, (-0.10, -0.80, 2.30), tuple(BOARD), (1.0, 0.92, 0.82), 40, 1.0)
    k = bpy.data.objects.get("Key_MayaWarm")
    head = MAYA + Vector((0, 0, 1.36))
    if k:
        k.location = head + Vector((-0.55, -0.55, 0.30))
        k.rotation_euler = (head - k.location).to_track_quat("-Z", "Y").to_euler()
    rim = bpy.data.objects.get("Rim_MascotWarm")
    if rim:
        tgt = Vector((BOOKS.x, BOOKS.y, top + 0.12))
        rim.location = tgt + Vector((0.35, 0.35, 0.40))
        rim.rotation_euler = (tgt - rim.location).to_track_quat("-Z", "Y").to_euler()
    key = bpy.data.objects.get("Key_DeskWarm")
    if key:
        key.location = (0.2, -1.4, 2.0)
        key.rotation_euler = (Vector((-0.2, 0.2, 1.0)) - key.location).to_track_quat("-Z", "Y").to_euler()

    # 7. Cameras
    claude = Vector((BOOKS.x, BOOKS.y, top + 0.12))
    _aim_cam("Cam_Wide", (0.12, -2.55, 1.32), (0.10, 0.30, 1.22), 30, 4.0)
    _aim_cam("Cam_Mascot", claude + Vector((0.32, -0.95, 0.10)), claude + Vector((0.05, 0.0, 0.04)), 38, 1.8,
             focus=bpy.data.objects.get("Mascot_FocusTarget"))
    _aim_cam("Cam_Human", head + Vector((-0.95, -1.15, -0.06)), head + Vector((0.0, 0.0, -0.20)), 40, 1.8,
             focus=bpy.data.objects.get("Human_FocusTarget"))


apply_classroom_set()
