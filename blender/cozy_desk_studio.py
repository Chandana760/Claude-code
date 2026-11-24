"""
Cozy low-poly nighttime desk studio — vertical 9:16 (1080x1920 @ 24 fps).

Run it any of these ways (Blender 4.2+ / 5.x):
  * Blender MCP: send this file's contents to the "execute Blender code" tool.
  * Blender UI:  Scripting workspace > Text Editor > Open > Run Script.
  * CLI:         blender -b -P cozy_desk_studio.py -- --save desk_studio.blend --render renders/

The script clears the current scene, then builds:
  Desk_Props  - wooden desk, angled monitor with emissive code bars, keyboard,
                ceramic mug, sticky-note stack, potted plant, desk lamp
  Background  - wall with a large dark window frame, twilight gradient sky,
                moon, stars, two layers of low-poly city silhouettes with
                glowing yellow / blue windows
  Characters  - placeholder low-poly human (right) and desk-companion robot
                mascot (foreground) so the cameras have subjects to frame
  Lighting    - warm orange desk key + lamp, purple window rim, faint monitor fill
  Cameras     - Cam_Wide, Cam_Human, Cam_Mascot (DoF on, f/2.8), bound to
                timeline markers so the cut plays back across 9 seconds

Every object uses flat shading and a Principled BSDF material at roughness 0.8.
"""

import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

R = math.radians


# --------------------------------------------------------------------------- #
# Scene reset
# --------------------------------------------------------------------------- #
def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    for datablocks in (bpy.data.meshes, bpy.data.materials, bpy.data.lights,
                       bpy.data.cameras, bpy.data.curves):
        for block in list(datablocks):
            datablocks.remove(block)
    bpy.context.scene.timeline_markers.clear()


def new_collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


# --------------------------------------------------------------------------- #
# Materials (Principled BSDF, roughness 0.8)
# --------------------------------------------------------------------------- #
def _principled(m):
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        nt.nodes.clear()
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        out.location = (300, 0)
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return bsdf


def _set(bsdf, names, value):
    for n in names:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = value
            return bsdf.inputs[n]
    return None


EMIT_COLOR = ("Emission Color", "Emission")


def mat(name, color, emit=0.0, emit_color=None):
    m = bpy.data.materials.new(name)
    bsdf = _principled(m)
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8
    _set(bsdf, ("Specular IOR Level", "Specular"), 0.3)
    if emit > 0:
        _set(bsdf, EMIT_COLOR, (*(emit_color or color), 1.0))
        _set(bsdf, ("Emission Strength",), emit)
    m.diffuse_color = (*color, 1.0)
    return m


def sky_mat():
    m = bpy.data.materials.new("M_TwilightSky")
    bsdf = _principled(m)
    bsdf.inputs["Roughness"].default_value = 0.8
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    tc.location, sep.location, ramp.location = (-900, 0), (-700, 0), (-500, 0)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    els = ramp.color_ramp.elements
    stops = [(0.40, (1.00, 0.42, 0.38)),   # warm coral at the horizon
             (0.50, (0.98, 0.25, 0.58)),   # hot pink
             (0.62, (0.45, 0.16, 0.70)),   # purple
             (0.76, (0.07, 0.04, 0.24))]   # deep indigo
    els[0].position, els[0].color = stops[0][0], (*stops[0][1], 1)
    els[1].position, els[1].color = stops[-1][0], (*stops[-1][1], 1)
    for pos, col in stops[1:-1]:
        e = els.new(pos)
        e.color = (*col, 1)
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    emit_in = _set(bsdf, EMIT_COLOR, (1, 1, 1, 1))
    nt.links.new(ramp.outputs["Color"], emit_in)
    _set(bsdf, ("Emission Strength",), 1.2)
    m.diffuse_color = (0.6, 0.3, 0.7, 1)
    return m


# --------------------------------------------------------------------------- #
# Low-poly mesh helpers (bmesh, no operators -> safe to run over MCP)
# --------------------------------------------------------------------------- #
def _euler(rot):
    return Euler(tuple(R(a) for a in rot))


def box(loc, size, rot=(0, 0, 0)):
    mtx = Matrix.LocRotScale(Vector(loc), _euler(rot), Vector(size))
    return lambda bm: bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)


def cyl(loc, r1, r2, depth, seg=8, rot=(0, 0, 0), scale=(1, 1, 1)):
    mtx = Matrix.LocRotScale(Vector(loc), _euler(rot), Vector(scale))
    return lambda bm: bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=seg,
        radius1=r1, radius2=r2, depth=depth, matrix=mtx)


def ico(loc, r, sub=1, scale=(1, 1, 1)):
    mtx = Matrix.LocRotScale(Vector(loc), None, Vector(scale))
    return lambda bm: bmesh.ops.create_icosphere(
        bm, subdivisions=sub, radius=r, matrix=mtx)


def cyl_between(p1, p2, r, seg=6):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    mtx = Matrix.LocRotScale((p1 + p2) / 2, d.to_track_quat("Z", "Y"), None)
    return lambda bm: bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=seg,
        radius1=r, radius2=r, depth=d.length, matrix=mtx)


def obj(name, parts, material, coll, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for build in parts:
        build(bm)
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:          # flat shading everywhere
        poly.use_smooth = False
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = _euler(rot)
    if parent is not None:
        ob.parent = parent
    return ob


def empty(name, coll, loc=(0, 0, 0), rot=(0, 0, 0), size=0.08):
    e = bpy.data.objects.new(name, None)
    coll.objects.link(e)
    e.location = loc
    e.rotation_euler = _euler(rot)
    e.empty_display_size = size
    return e


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_desk_and_props(C):
    rnd = random.Random(11)
    wood = mat("M_WarmWood", (0.46, 0.25, 0.11))
    wood_dark = mat("M_WarmWoodDark", (0.30, 0.15, 0.07))
    DESK_Z = 0.75

    # Desk --------------------------------------------------------------
    desk = empty("Desk", C)
    obj("Desk_Top", [box((0, 0, 0.725), (1.70, 0.70, 0.05))], wood, C, desk)
    obj("Desk_Apron", [box((0, -0.33, 0.655), (1.58, 0.03, 0.09)),
                       box((0, 0.33, 0.655), (1.58, 0.03, 0.09))], wood_dark, C, desk)
    obj("Desk_Legs", [box((x, y, 0.35), (0.05, 0.05, 0.70))
                      for x in (-0.80, 0.80) for y in (-0.30, 0.30)], wood_dark, C, desk)

    # Monitor (left, turned inward) -------------------------------------
    plastic = mat("M_MonitorPlastic", (0.07, 0.07, 0.09))
    screen = mat("M_ScreenDark", (0.015, 0.015, 0.03), emit=0.6,
                 emit_color=(0.04, 0.05, 0.11))
    mon = empty("Monitor", C, loc=(-0.42, 0.10, DESK_Z), rot=(0, 0, 25))
    obj("Monitor_Stand", [box((0, 0.0, 0.008), (0.22, 0.15, 0.016)),
                          box((0, 0.03, 0.15), (0.04, 0.03, 0.28))], plastic, C, mon)
    obj("Monitor_Bezel", [box((0, 0, 0.42), (0.62, 0.035, 0.37))], plastic, C, mon)
    obj("Monitor_Screen", [box((0, -0.0185, 0.425), (0.58, 0.002, 0.33))], screen, C, mon)

    code_cols = {
        "Pink": (1.00, 0.35, 0.60), "Cyan": (0.30, 0.85, 1.00),
        "Yellow": (1.00, 0.80, 0.30), "Green": (0.45, 1.00, 0.50),
        "Purple": (0.70, 0.50, 1.00), "Gray": (0.45, 0.45, 0.55),
    }
    bars = {k: [] for k in code_cols}
    x0, x1, y = -0.255, 0.265, -0.0205
    indent = 0
    for i in range(12):
        z = 0.575 - i * 0.024
        bars["Gray"].append(box((-0.272, y, z), (0.012, 0.002, 0.012)))  # gutter
        if i in (5, 9):                       # blank line
            continue
        indent = max(0, min(3, indent + rnd.choice((-1, 0, 0, 1))))
        x = x0 + indent * 0.035
        for _ in range(rnd.choice((1, 2, 2, 3))):
            length = rnd.uniform(0.04, 0.16)
            if x + length > x1:
                break
            col = rnd.choice(("Pink", "Cyan", "Yellow", "Green", "Purple"))
            bars[col].append(box((x + length / 2, y, z), (length, 0.002, 0.013)))
            x += length + 0.015
    for name, parts in bars.items():
        if parts:
            strength = 1.5 if name == "Gray" else 3.0
            obj(f"Screen_Code_{name}", parts,
                mat(f"M_Code_{name}", code_cols[name], emit=strength), C, mon)

    # Keyboard (center) --------------------------------------------------
    kb = empty("Keyboard", C, loc=(0.12, 0.02, DESK_Z), rot=(0, 0, -4))
    obj("Keyboard_Base", [box((0, 0, 0.01), (0.44, 0.15, 0.02))],
        mat("M_KeyboardBase", (0.12, 0.12, 0.15)), C, kb)
    keys, accents = [], []
    for row in range(5):
        ky = -0.052 + row * 0.027
        if row == 0:
            for kx in (-0.17, -0.141, -0.112, 0.112, 0.141, 0.17):
                keys.append(box((kx, ky, 0.025), (0.024, 0.022, 0.012)))
            keys.append(box((0, ky, 0.025), (0.19, 0.022, 0.012)))   # spacebar
            continue
        for col in range(14):
            kx = -0.1885 + col * 0.029
            target = accents if (row == 4 and col == 0) or (row == 2 and col == 13) else keys
            target.append(box((kx, ky, 0.025), (0.024, 0.022, 0.012)))
    obj("Keyboard_Keys", keys, mat("M_Keycaps", (0.76, 0.73, 0.82)), C, kb)
    obj("Keyboard_AccentKeys", accents, mat("M_KeycapsAccent", (1.0, 0.45, 0.62)), C, kb)

    # Ceramic mug ---------------------------------------------------------
    ceramic = mat("M_WhiteCeramic", (0.92, 0.90, 0.86))
    mug = empty("Mug", C, loc=(0.52, -0.12, DESK_Z), rot=(0, 0, -35))
    obj("Mug_Body", [cyl((0, 0, 0.05), 0.042, 0.042, 0.10, seg=12),
                     box((0.056, 0, 0.078), (0.030, 0.012, 0.010)),
                     box((0.056, 0, 0.027), (0.030, 0.012, 0.010)),
                     box((0.068, 0, 0.0525), (0.010, 0.012, 0.061))], ceramic, C, mug)
    obj("Mug_Coffee", [cyl((0, 0, 0.1005), 0.036, 0.036, 0.002, seg=12)],
        mat("M_Coffee", (0.18, 0.09, 0.05)), C, mug)

    # Sticky-note stack ----------------------------------------------------
    notes = empty("StickyNotes", C, loc=(-0.20, -0.20, DESK_Z), rot=(0, 0, 12))
    note_mats = [mat("M_NoteYellow", (1.0, 0.85, 0.30)), mat("M_NotePink", (1.0, 0.52, 0.66))]
    for i in range(5):
        obj(f"StickyNote_{i + 1}", [box((0, 0, 0.002 + i * 0.0045), (0.075, 0.075, 0.004))],
            note_mats[i % 2], C, notes, rot=(0, 0, rnd.uniform(-9, 9)))
    obj("StickyNote_Scribble", [box((0, 0.012 - j * 0.014, 0.0245), (0.045 - j * 0.01, 0.004, 0.001))
                                for j in range(3)], mat("M_Ink", (0.15, 0.12, 0.25)), C, notes)

    # Potted plant (far left) ------------------------------------------------
    plant = empty("Plant", C, loc=(-0.72, 0.12, DESK_Z))
    obj("Plant_Pot", [cyl((0, 0, 0.055), 0.065, 0.08, 0.11, seg=8),
                      cyl((0, 0, 0.115), 0.086, 0.086, 0.022, seg=8)],
        mat("M_Terracotta", (0.72, 0.33, 0.20)), C, plant)
    obj("Plant_Soil", [cyl((0, 0, 0.127), 0.074, 0.074, 0.004, seg=8)],
        mat("M_Soil", (0.15, 0.09, 0.05)), C, plant)
    stems = []
    leaves_a, leaves_b = [], []
    for i in range(7):
        ang = i / 7 * math.tau + rnd.uniform(-0.3, 0.3)
        rr = rnd.uniform(0.03, 0.08)
        tip = (math.cos(ang) * rr, math.sin(ang) * rr, rnd.uniform(0.22, 0.34))
        stems.append(cyl_between((0, 0, 0.12), tip, 0.004, seg=5))
        leaf = ico(tip, rnd.uniform(0.035, 0.05), sub=1,
                   scale=(1.0, rnd.uniform(0.6, 0.9), rnd.uniform(0.55, 0.8)))
        (leaves_a if i % 2 else leaves_b).append(leaf)
    obj("Plant_Stems", stems, mat("M_Stem", (0.20, 0.40, 0.18)), C, plant)
    obj("Plant_LeavesA", leaves_a, mat("M_LeafA", (0.18, 0.50, 0.25)), C, plant)
    obj("Plant_LeavesB", leaves_b, mat("M_LeafB", (0.28, 0.62, 0.30)), C, plant)

    # Desk lamp (right back corner) — source of the warm practical light --------
    lamp = empty("DeskLamp", C, loc=(0.78, 0.22, DESK_Z))
    lamp_metal = mat("M_LampMetal", (0.85, 0.45, 0.20))
    obj("DeskLamp_Body", [cyl((0, 0, 0.01), 0.06, 0.06, 0.02, seg=10),
                          cyl_between((0, 0, 0.02), (-0.02, 0.0, 0.30), 0.009),
                          cyl_between((-0.02, 0.0, 0.30), (-0.10, -0.05, 0.37), 0.009),
                          cyl((-0.10, -0.05, 0.36), 0.07, 0.025, 0.09, seg=10)],
        lamp_metal, C, lamp)
    obj("DeskLamp_Bulb", [ico((-0.10, -0.05, 0.315), 0.022, sub=1)],
        mat("M_LampBulb", (1.0, 0.75, 0.45), emit=8.0, emit_color=(1.0, 0.65, 0.35)), C, lamp)
    return {"lamp_bulb_world": (0.78 - 0.10, 0.22 - 0.05, DESK_Z + 0.30)}


def build_background(C):
    rnd = random.Random(3)
    wall = mat("M_Wall", (0.08, 0.06, 0.11))
    frame = mat("M_WindowFrame", (0.03, 0.025, 0.04))
    floor = mat("M_Floor", (0.12, 0.08, 0.07))

    obj("Floor", [box((0, 0, -0.025), (7, 7, 0.05))], floor, C)

    # Wall with a large opening (x -1.05..1.05, z 0.95..2.75) at y = 1.35
    WY, T = 1.35, 0.10
    obj("Wall", [box((-2.025, WY, 1.8), (1.95, T, 3.6)),
                 box((2.025, WY, 1.8), (1.95, T, 3.6)),
                 box((0, WY, 0.475), (2.10, T, 0.95)),
                 box((0, WY, 3.175), (2.10, T, 0.85))], wall, C)
    obj("Window_Frame", [box((-1.01, WY, 1.85), (0.08, 0.14, 1.80)),
                         box((1.01, WY, 1.85), (0.08, 0.14, 1.80)),
                         box((0, WY, 2.71), (2.10, 0.14, 0.08)),
                         box((0, WY - 0.06, 0.99), (2.20, 0.26, 0.08)),   # sill
                         box((0, WY, 1.85), (0.05, 0.10, 1.80)),          # mullion
                         box((0, WY, 1.95), (2.02, 0.10, 0.05))],         # transom
        frame, C)

    # Twilight sky, moon, stars
    sky = obj("Sky", [box((0, 6.0, 1.5), (16, 0.05, 10))], sky_mat(), C)
    # The sky is a backdrop only: don't let its glow wash the room in purple.
    for attr in ("visible_diffuse", "visible_glossy", "visible_transmission",
                 "visible_volume_scatter", "visible_shadow"):
        if hasattr(sky, attr):
            setattr(sky, attr, False)
    obj("Moon", [ico((1.25, 5.9, 3.45), 0.30, sub=1)],
        mat("M_Moon", (1.0, 0.93, 0.86), emit=3.0), C)
    stars = [box((rnd.uniform(-2.6, 2.6), 5.95, rnd.uniform(2.9, 4.3)), (0.025,) * 3)
             for _ in range(28)]
    obj("Stars", stars, mat("M_Stars", (1.0, 0.95, 1.0), emit=4.0), C)

    # City silhouettes: far (hazy, taller) and near (darker) layers
    def city_layer(tag, y_range, top_range, color, win_size, win_pitch, lit_p, win_emit):
        blds, yellow, blue = [], [], []
        x = -4.2
        while x < 4.2:
            w = rnd.uniform(0.35, 0.85)
            d = rnd.uniform(0.4, 0.8)
            top = rnd.uniform(*top_range)
            yc = rnd.uniform(*y_range)
            base = -4.0
            cx = x + w / 2
            blds.append(box((cx, yc, (top + base) / 2), (w, d, top - base)))
            if rnd.random() < 0.4:                                     # rooftop detail
                blds.append(box((cx + rnd.uniform(-w / 4, w / 4), yc, top + 0.06),
                                (w * 0.3, d * 0.4, 0.12)))
            if rnd.random() < 0.25:                                    # antenna
                blds.append(cyl((cx, yc, top + 0.2), 0.008, 0.008, 0.4, seg=4))
            fy = yc - d / 2 - 0.006
            cols = int((w - 0.06) // win_pitch[0])
            ox = cx - (cols - 1) * win_pitch[0] / 2
            z = top - 0.12
            while z > 0.3:
                for c in range(cols):
                    if rnd.random() < lit_p:
                        p = box((ox + c * win_pitch[0], fy, z), (win_size[0], 0.01, win_size[1]))
                        (yellow if rnd.random() < 0.7 else blue).append(p)
                z -= win_pitch[1]
            x += w + rnd.uniform(0.0, 0.18)
        obj(f"City_{tag}_Buildings", blds, mat(f"M_City_{tag}", color), C)
        if yellow:
            obj(f"City_{tag}_LightsYellow", yellow,
                mat(f"M_CityLight_{tag}_Yellow", (1.0, 0.78, 0.35), emit=win_emit), C)
        if blue:
            obj(f"City_{tag}_LightsBlue", blue,
                mat(f"M_CityLight_{tag}_Blue", (0.35, 0.60, 1.0), emit=win_emit), C)

    city_layer("Far", (4.6, 5.3), (1.2, 2.7), (0.10, 0.06, 0.17),
               (0.03, 0.045), (0.075, 0.10), 0.20, 2.5)
    city_layer("Near", (2.6, 3.4), (0.85, 1.9), (0.035, 0.028, 0.065),
               (0.045, 0.07), (0.11, 0.14), 0.28, 4.0)


def build_characters(C):
    # --- Main character (placeholder), seated behind the desk on the right ---
    skin = mat("M_Skin", (0.86, 0.62, 0.48))
    hoodie = mat("M_Hoodie", (0.16, 0.32, 0.38))
    hair = mat("M_Hair", (0.12, 0.07, 0.05))
    dark = mat("M_FaceDark", (0.05, 0.04, 0.06))
    chair = mat("M_Chair", (0.15, 0.10, 0.18))

    h = empty("Human", C, loc=(0.45, 0.62, 0.0))
    obj("Human_Chair", [box((0, 0.05, 0.48), (0.46, 0.42, 0.06)),
                        box((0, 0.27, 0.86), (0.46, 0.05, 0.62)),
                        cyl((0, 0.05, 0.24), 0.03, 0.03, 0.45, seg=6),
                        cyl((0, 0.05, 0.02), 0.22, 0.22, 0.04, seg=5)], chair, C, h)
    obj("Human_Torso", [cyl((0, 0, 1.02), 0.19, 0.16, 0.50, seg=8, scale=(1.2, 0.8, 1.0)),
                        cyl_between((0.20, 0, 1.22), (0.12, -0.30, 0.95), 0.05),     # R upper arm
                        cyl_between((0.12, -0.30, 0.95), (-0.20, -0.55, 0.80), 0.045),
                        cyl_between((-0.20, 0, 1.22), (-0.26, -0.25, 0.95), 0.05),   # L upper arm
                        cyl_between((-0.26, -0.25, 0.95), (-0.42, -0.55, 0.80), 0.045),
                        cyl((0, 0.06, 1.25), 0.11, 0.13, 0.08, seg=8)],               # hood collar
        hoodie, C, h)
    obj("Human_Skin", [cyl((0, 0, 1.30), 0.045, 0.045, 0.08, seg=6),
                       ico((0, 0, 1.43), 0.115, sub=2, scale=(1.0, 0.95, 1.08)),
                       ico((-0.20, -0.57, 0.80), 0.035, sub=1),
                       ico((-0.42, -0.57, 0.80), 0.035, sub=1)], skin, C, h)
    obj("Human_Hair", [ico((0, 0.04, 1.49), 0.125, sub=2, scale=(1.03, 1.0, 0.85))], hair, C, h)
    obj("Human_Face", [ico((0.04, -0.103, 1.43), 0.012, sub=1),
                       ico((-0.04, -0.103, 1.43), 0.012, sub=1),
                       box((0, -0.106, 1.38), (0.03, 0.005, 0.006))], dark, C, h)
    head_focus = empty("Human_FocusTarget", C, loc=(0.45, 0.52, 1.42), size=0.04)

    # --- Desk companion robot mascot (foreground) ---
    cream = mat("M_MascotCream", (0.95, 0.88, 0.75))
    orange = mat("M_MascotOrange", (1.0, 0.50, 0.25))
    m = empty("Mascot", C, loc=(0.20, -0.24, 0.75), rot=(0, 0, -15))
    obj("Mascot_Body", [box((0, 0, 0.05), (0.075, 0.06, 0.07)),
                        box((0, 0, 0.125), (0.11, 0.085, 0.08)),
                        cyl((0, 0, 0.18), 0.004, 0.004, 0.03, seg=5)], cream, C, m)
    obj("Mascot_Trim", [box((0, -0.031, 0.05), (0.04, 0.003, 0.03)),
                        box((0.058, 0, 0.125), (0.008, 0.03, 0.03)),
                        box((-0.058, 0, 0.125), (0.008, 0.03, 0.03)),
                        cyl_between((0.04, 0, 0.07), (0.055, -0.01, 0.035), 0.009, seg=5),
                        cyl_between((-0.04, 0, 0.07), (-0.055, -0.01, 0.035), 0.009, seg=5)],
        orange, C, m)
    obj("Mascot_Feet", [box((0.022, 0, 0.008), (0.028, 0.04, 0.016)),
                        box((-0.022, 0, 0.008), (0.028, 0.04, 0.016))],
        mat("M_MascotFeet", (0.20, 0.17, 0.25)), C, m)
    obj("Mascot_FaceScreen", [box((0, -0.0435, 0.125), (0.085, 0.003, 0.055))],
        mat("M_MascotScreen", (0.03, 0.03, 0.06), emit=0.5, emit_color=(0.05, 0.05, 0.12)), C, m)
    obj("Mascot_Eyes", [box((0.02, -0.0455, 0.13), (0.014, 0.002, 0.02)),
                        box((-0.02, -0.0455, 0.13), (0.014, 0.002, 0.02)),
                        box((0, -0.0455, 0.11), (0.02, 0.002, 0.004))],
        mat("M_MascotEyes", (0.30, 0.90, 1.0), emit=6.0), C, m)
    obj("Mascot_AntennaTip", [ico((0, 0, 0.20), 0.01, sub=1)],
        mat("M_MascotAntenna", (1.0, 0.40, 0.65), emit=6.0), C, m)
    mascot_focus = empty("Mascot_FocusTarget", C, loc=(0.20, -0.255, 0.87), size=0.03)
    return head_focus, mascot_focus


def build_lights(C, lamp_pos):
    def area(name, loc, target, color, energy, size, size_y=None):
        ld = bpy.data.lights.new(name, "AREA")
        ld.color, ld.energy = color, energy
        if size_y:
            ld.shape, ld.size, ld.size_y = "RECTANGLE", size, size_y
        else:
            ld.size = size
        ob = bpy.data.objects.new(name, ld)
        C.objects.link(ob)
        ob.location = loc
        aim(ob, target)
        return ob

    area("Key_DeskWarm", (0.95, -1.10, 1.80), (0.15, 0.25, 0.95), (1.0, 0.50, 0.20), 156, 1.0)   # 260 -40%: front-facing
    area("Rim_WindowPurple", (0.10, 1.22, 2.00), (0.35, 0.50, 1.20), (0.62, 0.38, 1.0), 220, 1.6, 1.0)
    area("Fill_MonitorGlow", (-0.30, -0.10, 1.00), (0.20, 0.30, 1.10), (0.45, 0.60, 1.0), 4.8, 0.4)   # 8 -40%: front fill

    pd = bpy.data.lights.new("Practical_DeskLamp", "POINT")
    pd.color, pd.energy, pd.shadow_soft_size = (1.0, 0.55, 0.25), 45, 0.05
    p = bpy.data.objects.new("Practical_DeskLamp", pd)
    C.objects.link(p)
    p.location = lamp_pos

    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    try:
        world.use_nodes = True
    except Exception:
        pass
    bg = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
    if bg:
        bg.inputs["Color"].default_value = (0.03, 0.02, 0.06, 1)
        bg.inputs["Strength"].default_value = 1.0
    world.color = (0.03, 0.02, 0.06)


def build_cameras(C, focus_wide, focus_human, focus_mascot):
    def cam(name, loc, target, lens, focus_obj):
        cd = bpy.data.cameras.new(name)
        cd.lens = lens
        cd.sensor_fit = "AUTO"
        cd.clip_start = 0.01
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = 2.8
        cd.dof.focus_object = focus_obj
        ob = bpy.data.objects.new(name, cd)
        C.objects.link(ob)
        ob.location = loc
        aim(ob, target)
        return ob

    wide = cam("Cam_Wide", (0.0, -2.70, 1.45), (0.0, 0.30, 1.30), 32, focus_wide)
    human = cam("Cam_Human", (0.15, -0.75, 1.38), (0.45, 0.62, 1.30), 55, focus_human)
    mascot = cam("Cam_Mascot", (0.08, -0.72, 0.88), (0.20, -0.24, 0.86), 50, focus_mascot)
    return wide, human, mascot


def setup_render(cams):
    sc = bpy.context.scene
    r = sc.render
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 1920, 100
    r.fps, r.fps_base = 24, 1.0
    sc.frame_start, sc.frame_end = 1, 216          # 9 s
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            r.engine = eng
            break
        except TypeError:
            continue
    for attr, val in (("taa_render_samples", 64), ("use_gtao", True),
                      ("use_shadows", True), ("use_bloom", True)):
        if hasattr(sc.eevee, attr):
            try:
                setattr(sc.eevee, attr, val)
            except Exception:
                pass
    # AgX + Punchy with exposure pulled down keeps the flat colours rich
    # without blowing out faces under the warm key.
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
        sc.view_settings.exposure = -1.0
    except TypeError:
        pass

    wide, human, mascot = cams
    sc.camera = wide
    for frame, name, c in ((1, "Wide", wide), (73, "Human", human), (145, "Mascot", mascot)):
        mk = sc.timeline_markers.new(name, frame=frame)
        mk.camera = c


def main():
    clear_scene()
    c_props = new_collection("Desk_Props")
    c_bg = new_collection("Background")
    c_chars = new_collection("Characters")
    c_lights = new_collection("Lighting")
    c_cams = new_collection("Cameras")

    info = build_desk_and_props(c_props)
    build_background(c_bg)
    human_focus, mascot_focus = build_characters(c_chars)
    build_lights(c_lights, info["lamp_bulb_world"])
    wide_focus = empty("Wide_FocusTarget", c_cams, loc=(0.25, 0.30, 1.05), size=0.04)
    cams = build_cameras(c_cams, wide_focus, human_focus, mascot_focus)
    setup_render(cams)
    return cams


# --------------------------------------------------------------------------- #
# Optional CLI: --save file.blend  --render out_dir/
# --------------------------------------------------------------------------- #
def _cli_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    opts = {}
    for i, a in enumerate(argv):
        if a in ("--save", "--render") and i + 1 < len(argv):
            opts[a[2:]] = argv[i + 1]
    return opts


cams = main()
_opts = _cli_args()
if "save" in _opts:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(_opts["save"]))
if "render" in _opts:
    out = os.path.abspath(_opts["render"])
    os.makedirs(out, exist_ok=True)
    for c in cams:
        bpy.context.scene.camera = c
        bpy.context.scene.render.filepath = os.path.join(out, c.name + ".png")
        bpy.ops.render.render(write_still=True)
    bpy.context.scene.camera = cams[0]
print("Cozy desk studio built:", [c.name for c in cams])
