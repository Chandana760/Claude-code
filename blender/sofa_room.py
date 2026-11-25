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


def hx(h):
    """'#RRGGBB' (sRGB) -> linear RGB."""
    def c(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return tuple(c(int(h[i:i + 2], 16)) for i in (1, 3, 5))


def throw_blanket(x0, x1, y_front, y_back, seat, body_y, nx=16, ny=12):
    """Rectangular throw (16x12 subdivided plane) draped over her hips and legs:
    a soft rounded body ridge from waist to feet, the front edge hanging down over
    the cushion edge, the back tucked against the backrest, and 3-4 gentle folds."""
    def h(u):                                   # blanket height over the seat along her body
        hip = 0.47 * math.exp(-((u - 0.10) / 0.42) ** 2)       # hip, highest at the waist end
        legs = 0.25 + 0.06 * math.cos(math.pi * min(1.0, u * 1.1))
        return max(hip, legs)

    def b(bm):
        grid = []
        nd = 3                                  # rows hanging over the front of the cushion
        for j in range(ny + 1):
            row = []
            for i in range(nx + 1):
                u = i / nx
                x = x0 + (x1 - x0) * u
                if j < nd:                      # front drape: falls down the cushion face
                    t = j / nd
                    y = y_front - 0.035 * (1 - t) + 0.012 * math.sin(2 * math.pi * 3.5 * u) * (1 - t)
                    z = 0.27 + (seat + 0.02 - 0.27) * t ** 0.8
                else:
                    v = (j - nd) / (ny - nd)
                    y = y_front + (y_back - y_front) * v
                    d = (y - body_y) / 0.27
                    ridge = math.exp(-d ** 4)                    # flat-topped ridge over her body
                    fold = 0.032 * math.sin(2 * math.pi * (1.75 * u + 0.55 * v)) * (0.35 + 0.65 * ridge)
                    z = seat + 0.02 + h(u) * ridge + fold
                    if j == nd:                 # rounded lip over the cushion edge
                        z -= 0.012
                row.append(bm.verts.new((x, y, z)))
            grid.append(row)
        for j in range(ny):
            for i in range(nx):
                bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    return b


def sleep_eye_lines(hz, xs=(0.078, -0.078), zc=0.004, half=0.026, dip=0.011, r=0.0042, n=10):
    """Two calm closed-eye curves (U-shaped lash lines) on the head surface, in the
    same root-space coordinates the dot eyes were built in."""
    R2 = 0.172 ** 2 + 0.078 ** 2 + 0.006 ** 2

    def surf(x, z):
        return -math.sqrt(max(1e-6, R2 - x * x - (z - hz) ** 2)) - 0.004

    def b(bm):
        for ex in xs:
            pts = []
            for k in range(n + 1):
                t = -1 + 2 * k / n
                x = ex + half * t
                z = hz + zc - dip * (1 - t * t)          # lowest in the middle: U shape
                pts.append(Vector((x, surf(x, z), z)))
            rings = []
            for k, p in enumerate(pts):
                tan = (pts[min(n, k + 1)] - pts[max(0, k - 1)]).normalized()
                nrm = Vector((0, -1, 0))
                side = tan.cross(nrm).normalized()
                taper = 0.55 + 0.45 * math.sin(math.pi * k / n)
                ring = []
                for a in range(6):
                    ang = 2 * math.pi * a / 6
                    off = side * math.cos(ang) * r * taper + nrm * math.sin(ang) * r * 0.5
                    ring.append(bm.verts.new(p + off))
                rings.append(ring)
            for k in range(n):
                for a in range(6):
                    bm.faces.new((rings[k][a], rings[k][(a + 1) % 6], rings[k + 1][(a + 1) % 6], rings[k + 1][a]))
            for ring in (rings[0], rings[-1]):
                bm.faces.new(ring)
    return b


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
HEAD = Vector((-0.56, 0.63, 0.86))     # centre of her head, resting on the pillow
HEAD_LOCAL_Z = 1.355                   # head-mesh centre height in her root space
PILLOW = Vector((-0.60, 0.62, 0.565))  # flat cream pillow on the left end of the seat
TILT = -78                             # lying on her side along the seat, head left, legs right
SEAT_TOP = 0.48
MASCOT = Vector((-0.24, -0.34, 0.47))  # Claude on the coffee table


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
    wall = _mat("M_Room_Wall", hx("#1A2426"))                  # dark slate-teal
    floor = _mat("M_Room_Floor", (0.28, 0.18, 0.10))         # light floor that catches the warm pool
    _mesh("Room_Floor", [_box((0, 0, -0.025), (8, 8, 0.05))], floor, room)
    _mesh("Room_Walls", [_box((0, 1.35, 1.6), (8, 0.1, 3.2)), _box((-2.2, 0, 1.6), (0.1, 6, 3.2))], wall, room)
    _mesh("Room_PictureFrame", [_box((0.85, 1.29, 1.55), (0.42, 0.03, 0.56), bevel=0.006)],
          _mat("M_Room_FrameWood", hx("#6E4228"), rough=0.7), room)    # warm wood frame border
    _mesh("Room_Picture", [_box((0.85, 1.27, 1.55), (0.34, 0.02, 0.48))], _mat("M_Room_Picture", (0.05, 0.04, 0.03)), room)

    sofa_m = _mat("M_Sofa_Green", hx("#2D5852"))              # teal-green
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

    # 3. Maya lies on her side along the seat: head on the pillow at the left
    #    armrest, body toward the right, bent arms together in front of her chest
    root = bpy.data.objects["Human_Root"]
    bpy.context.view_layer.update()
    rot = Euler((0, R(TILT), 0))
    root.rotation_euler = rot
    root.location = HEAD - rot.to_matrix() @ Vector((0, 0, HEAD_LOCAL_Z))
    bpy.context.view_layer.update()
    # soft, slightly squashed oval sofa pillow lying flat on the seat; her head
    # and glasses sink ~2 cm into its centre (no gap)
    _mesh("Pillow_Cream", [_ico(tuple(PILLOW), 1.0, scale=(0.27, 0.20, 0.088), sub=2)],
          _mat("M_Pillow_Cream", hx("#E8DEC8")), room)
    sc["head_pose_offset"] = (0.0, 0.0, 0.0)
    sc["lid_base"] = 0.0
    # Closed eyes: two calm U-shaped lash lines replace the dot eyes
    pupils = bpy.data.objects["Human_Pupils"]
    pupils.hide_render = pupils.hide_viewport = True
    sleep = _mesh("Human_SleepEyes", [sleep_eye_lines(1.34)], pupils.data.materials[0], room)
    room.objects.unlink(sleep)
    pupils.users_collection[0].objects.link(sleep)
    sleep.parent = pupils.parent
    sleep.matrix_parent_inverse = pupils.matrix_parent_inverse.copy()
    sleep.location, sleep.rotation_euler, sleep.scale = pupils.location, pupils.rotation_euler, pupils.scale
    # Throw blanket (#7D6B91) from her waist to the right armrest, over her hips and
    # legs and down over the front of the cushion; chest, arms and head stay uncovered
    waist = root.matrix_world @ Vector((0, 0, 0.72))
    blanket = _mesh("Blanket", [throw_blanket(waist.x - 0.04, 0.86, 0.30, 0.95, SEAT_TOP, waist.y)],
                    _mat("M_Blanket_Lavender", hx("#7D6B91"), rough=0.85), room)
    sol = blanket.modifiers.new("Thickness", "SOLIDIFY")
    sol.thickness, sol.offset = 0.03, -1.0
    # light cream/beige rug under the coffee table
    _mesh("Rug", [_box((-0.05, -0.30, 0.005), (1.8, 1.15, 0.01), bevel=0.004)], _mat("M_Rug_Beige", hx("#D6CFC2")), room)

    # 4. Claude on the coffee table
    mroot = bpy.data.objects["Mascot_Root"]
    mroot.location = MASCOT
    mroot.rotation_euler = (0, 0, R(-6))

    # 5. Lighting: warm lamp from front-right, soft fill, keep Maya/Claude accent lights
    for o in list(lights.objects) if lights else []:
        if o.name not in ("Key_MayaWarm", "Rim_MascotWarm"):
            bpy.data.objects.remove(o, do_unlink=True)
    lc = lights or room
    # soft warm overhead/front key (#FFE4C4) on couch, pillow and table: no harsh shadows
    _area("Key_SoftWarm", lc, (0.25, -1.55, 2.25), (-0.20, 0.45, 0.62), hx("#FFE4C4"), 170, 1.8)
    _area("Fill_RoomCool", lc, (-1.4, -1.6, 1.8), (0.0, 0.5, 0.5), (0.40, 0.48, 0.60), 35, 2.5)
    # Side lamp on a small dark wooden end table next to the left armrest:
    # wood table, brass base + stem, glowing shade, warm light inside the shade
    TX, TY, TOP = -1.33, 0.92, 0.56
    _mesh("EndTable", [_box((TX, TY, TOP - 0.015), (0.36, 0.36, 0.03), bevel=0.006)]
          + [_box((TX + dx, TY + dy, (TOP - 0.03) / 2), (0.03, 0.03, TOP - 0.03)) for dx in (-0.15, 0.15) for dy in (-0.15, 0.15)],
          _mat("M_EndTable_Wood", (0.05, 0.026, 0.014)), room)
    brass = _mat("M_Lamp_Brass", (0.55, 0.36, 0.12), rough=0.45)
    cyl = lambda loc, r, d, seg=12: (lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                                                                       radius1=r, radius2=r, depth=d,
                                                                       matrix=Matrix.Translation(loc)))
    _mesh("Lamp_Base", [cyl((TX, TY, TOP + 0.012), 0.08, 0.024)], brass, room)
    _mesh("Lamp_Stem", [cyl((TX, TY, TOP + 0.17), 0.012, 0.30, 8)], brass, room)
    _mesh("Lamp_Shade", [lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=10,
                                                         radius1=0.15, radius2=0.10, depth=0.20,
                                                         matrix=Matrix.Translation((TX, TY, TOP + 0.38)))],
          _mat("M_LampShade_Glow", (1.0, 0.62, 0.30), emit=2.5), room)
    ld = bpy.data.lights.get("Lamp_BehindArmrest") or bpy.data.lights.new("Lamp_BehindArmrest", "POINT")
    ld.color, ld.energy, ld.shadow_soft_size = (1.0, 0.58, 0.26), 140, 0.10
    lp = bpy.data.objects.new("Lamp_BehindArmrest", ld)
    lc.objects.link(lp)
    lp.location = (TX, TY, TOP + 0.36)
    # warm soft rim/fill (#FFE4C4) on her hair, the pillow and the top curve of the blanket
    _area("Rim_HairWarm", lc, (-0.85, 1.05, 1.25), tuple(HEAD), hx("#FFE4C4"), 16, 0.6)
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
    # angled medium-wide from the front-right: the whole sofa, her asleep on the
    # pillow under the throw, Claude on the coffee table in front
    _aim_cam("Cam_Wide", (1.10, -2.60, 1.34), (0.00, 0.40, 0.52), 29, 4.0)
    _aim_cam("Cam_Human", HEAD + Vector((0.42, -1.10, 0.22)), HEAD + Vector((0.12, 0, -0.04)), 40, 1.8, roll_deg=32)
    _aim_cam("Cam_Mascot", MASCOT + Vector((0.06, -0.88, 0.22)), MASCOT + Vector((0.02, 0, 0.16)), 45, 1.8)


apply_sofa_set()
