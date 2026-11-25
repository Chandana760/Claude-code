"""
Alternate standard set: cozy night living room ("sofa").

Run AFTER cozy_desk_studio.py + desk_characters.py (animate.py does this with
`--set sofa`). It removes the desk room, builds the living room, lays Maya on
the sofa with her head on a pillow hugging a cushion, puts Claude on the coffee
table, relights the room with a warm lamp, and sets the three cameras:
  Cam_Wide   - sofa + coffee table
  Cam_Human  - tilted close-up of her face resting on the pillow
  Cam_Mascot - Claude on the table, Maya blurred behind
"""
import math

import bmesh
import bpy
from mathutils import Euler, Matrix, Quaternion, Vector

R = math.radians


def _mat(name, color, rough=0.8, emit=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
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


def _mesh(name, builders, material, coll, smooth=False):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for b in builders:
        b(bm)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def _box(loc, size, bevel=0.0, rot=(0, 0, 0)):
    mtx = Matrix.LocRotScale(Vector(loc), Euler(tuple(R(a) for a in rot)), Vector(size))

    def b(bm):
        vs = bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)["verts"]
        if bevel:
            es = list({e for v in vs for e in v.link_edges})
            bmesh.ops.bevel(bm, geom=vs + es, offset=bevel, segments=2, affect="EDGES", profile=0.5)
    return b


def _ico(loc, r, scale=(1, 1, 1), sub=2, rot=(0, 0, 0)):
    mtx = Matrix.LocRotScale(Vector(loc), Euler(tuple(R(a) for a in rot)), Vector(scale))
    return lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r, matrix=mtx)


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


def _aim_cam(name, loc, target, lens, fstop, roll_deg=0.0, focus=None):
    cam = bpy.data.objects[name]
    cam.location = loc
    q = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y")
    cam.rotation_euler = (q @ Quaternion((0, 0, 1), R(roll_deg))).to_euler()
    cam.data.lens = lens
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = fstop
    if focus is not None:
        cam.data.dof.focus_object = focus
    if "base_lens" in cam:
        del cam["base_lens"]


# Layout (metres)
HEAD = Vector((-0.40, 0.62, 0.86))     # Maya's head resting on the pillow
TILT = -42                             # she lies on her side, head toward frame left
MASCOT = Vector((-0.10, -0.32, 0.47))  # Claude on the coffee table


def apply_sofa_set():
    sc = bpy.context.scene
    sc["set"] = "sofa"

    # 1. Remove the desk room (keep characters, cameras and the render setup)
    for cname in ("Desk_Props", "Background"):
        coll = bpy.data.collections.get(cname)
        if coll:
            for o in list(coll.objects):
                bpy.data.objects.remove(o, do_unlink=True)
    for name in ("Human_Chair", "Practical_DeskLamp", "Rim_WindowPurple", "Fill_MonitorGlow", "Key_DeskWarm"):
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    room = bpy.data.collections.get("Background") or bpy.data.collections.new("Background")
    if room.name not in sc.collection.children:
        sc.collection.children.link(room)
    lights = bpy.data.collections.get("Lighting")

    # 2. Living room: dark walls, wooden floor, framed picture, sofa, pillows, coffee table, book
    wall = _mat("M_Room_Wall", (0.034, 0.048, 0.040))         # muted green-grey
    floor = _mat("M_Room_Floor", (0.10, 0.06, 0.035))
    _mesh("Room_Floor", [_box((0, 0, -0.025), (8, 8, 0.05))], floor, room)
    _mesh("Room_Walls", [_box((0, 1.35, 1.6), (8, 0.1, 3.2)), _box((-2.2, 0, 1.6), (0.1, 6, 3.2))], wall, room)
    _mesh("Room_PictureFrame", [_box((0.85, 1.29, 1.55), (0.42, 0.03, 0.56), bevel=0.006)],
          _mat("M_Room_FrameGold", (0.75, 0.45, 0.06), rough=0.5), room)
    _mesh("Room_Picture", [_box((0.85, 1.27, 1.55), (0.34, 0.02, 0.48))], _mat("M_Room_Picture", (0.05, 0.04, 0.03)), room)

    sofa_m = _mat("M_Sofa_Green", (0.035, 0.085, 0.06))
    _mesh("Sofa", [_box((0, 0.70, 0.22), (2.0, 0.80, 0.30), bevel=0.04),        # base
                   _box((0, 0.66, 0.42), (1.80, 0.72, 0.12), bevel=0.05),       # seat cushion
                   _box((0, 1.04, 0.70), (2.0, 0.22, 0.62), bevel=0.07),        # backrest
                   _box((-0.98, 0.70, 0.52), (0.22, 0.82, 0.32), bevel=0.07),   # armrests
                   _box((0.98, 0.70, 0.52), (0.22, 0.82, 0.32), bevel=0.07)], sofa_m, room)

    table_m = _mat("M_Table_Wood", (0.07, 0.035, 0.018))
    _mesh("CoffeeTable", [_box((0, -0.32, 0.445), (1.10, 0.52, 0.04), bevel=0.008)]
          + [_box((x, y, 0.21), (0.04, 0.04, 0.43)) for x in (-0.5, 0.5) for y in (-0.53, -0.11)], table_m, room)
    _mesh("Table_Book", [_box((0.30, -0.30, 0.48), (0.22, 0.15, 0.03), bevel=0.004, rot=(0, 0, 8))],
          _mat("M_Book", (0.04, 0.12, 0.11)), room)

    # 3. Maya lies on her side on the sofa, head on the pillow
    root = bpy.data.objects["Human_Root"]
    head = bpy.data.objects["Human_Head"]
    bpy.context.view_layer.update()
    local_head = head.matrix_local.translation.copy()           # head pivot in root space
    rot = Euler((0, R(TILT), R(-8)))
    root.rotation_euler = rot
    root.location = HEAD - rot.to_matrix() @ local_head
    bpy.context.view_layer.update()
    # cream pillow under her head; purple cushion hugged against her chest (below the face)
    pil = HEAD + Vector((-0.27, -0.01, -0.12))
    _mesh("Pillow_Cream", [_ico(tuple(pil), 0.23, scale=(0.95, 0.78, 0.85))],
          _mat("M_Pillow_Cream", (0.75, 0.62, 0.45)), room)
    # Soft dusty-pink blanket draped over her from the chest down along the sofa
    # (contrasts with her lavender jacket): overlapping soft lumps following her
    # body line, plus a rolled hem at the top that her arms rest on.
    mw = root.matrix_world
    lumps = []
    for k, lz in enumerate((0.90, 0.68, 0.46, 0.24, 0.02, -0.20)):
        c = mw @ Vector((0.0, -0.13 + 0.01 * k, lz))
        c.z = max(c.z, 0.56)                           # rests on the seat
        lumps.append(_ico(tuple(c), 0.21 - 0.008 * k, scale=(1.25, 0.95, 0.80), rot=(0, TILT * 0.6, 0)))
    hem_a, hem_b = mw @ Vector((-0.26, -0.24, 0.96)), mw @ Vector((0.26, -0.24, 0.80))
    for i in range(7):
        lumps.append(_ico(tuple(hem_a.lerp(hem_b, i / 6)), 0.065, scale=(1, 1, 1), sub=1))
    _mesh("Blanket", lumps, _mat("M_Blanket_DustyPink", (0.55, 0.20, 0.24)), room)

    # 4. Claude on the coffee table
    mroot = bpy.data.objects["Mascot_Root"]
    mroot.location = MASCOT
    mroot.rotation_euler = (0, 0, R(-6))

    # 5. Lighting: warm lamp from front-right, soft fill, keep Maya/Claude accent lights
    for o in list(lights.objects) if lights else []:
        if o.name not in ("Key_MayaWarm", "Rim_MascotWarm"):
            bpy.data.objects.remove(o, do_unlink=True)
    lc = lights or room
    _area("Key_LampWarm", lc, (1.1, -0.9, 1.2), (-0.25, 0.4, 0.65), (1.0, 0.52, 0.22), 160, 0.7)   # warm pool on the characters
    _area("Fill_RoomCool", lc, (-1.4, -1.6, 1.8), (0.0, 0.5, 0.5), (0.45, 0.50, 0.60), 60, 2.5)
    _area("Glow_LampBounce", lc, (0.9, 0.3, 1.0), (0.85, 1.29, 1.55), (1.0, 0.55, 0.25), 25, 0.6)
    k = bpy.data.objects.get("Key_MayaWarm")
    if k:
        k.location = HEAD + Vector((0.45, -0.65, 0.25))
        k.rotation_euler = (HEAD - k.location).to_track_quat("-Z", "Y").to_euler()
    rim = bpy.data.objects.get("Rim_MascotWarm")
    if rim:
        tgt = MASCOT + Vector((0, 0, 0.1))
        rim.location = tgt + Vector((0.35, 0.35, 0.40))
        rim.rotation_euler = (tgt - rim.location).to_track_quat("-Z", "Y").to_euler()
    world = sc.world
    if world and world.node_tree:
        bg = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
        if bg:
            bg.inputs["Color"].default_value = (0.012, 0.012, 0.016, 1)

    # 6. Cameras (focus targets stay on the characters)
    _aim_cam("Cam_Wide", (0.0, -1.95, 1.10), (-0.10, 0.25, 0.55), 32, 4.0)
    _aim_cam("Cam_Human", HEAD + Vector((0.32, -1.30, 0.10)), HEAD + Vector((0.02, 0, -0.10)), 44, 1.8, roll_deg=30)
    _aim_cam("Cam_Mascot", MASCOT + Vector((0.06, -0.88, 0.22)), MASCOT + Vector((0.02, 0, 0.16)), 45, 1.8)


apply_sofa_set()
