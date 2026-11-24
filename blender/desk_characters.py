"""
Original low-poly characters for the cozy desk studio.

Run AFTER cozy_desk_studio.py, in the same Blender session / .blend:
  * Blender MCP: send this file's contents to the "execute Blender code" tool.
  * Blender UI:  Scripting > Text Editor > Open > Run Script.
  * CLI:         blender desk_studio.blend -b -P desk_characters.py -- --save desk_studio.blend

It replaces anything in the "Characters" collection (the placeholders) with:
  Human_Root   - seated chibi creator behind the desk (right), arms folded on the desk
                 Human_Head  (empty) - rotate it to nod / tilt the whole head
                 Human_Mouth     shape keys: Closed (basis), Talk_Open, Smile
                 Human_Eyelids   shape keys: Open (basis), Blink
  Mascot_Root  - small desk companion in front of the keyboard
                 custom props  hop (0..1)  and  tilt (-1..1)  drive Mascot_Bounce;
                 move / rotate / keyframe the root itself for bigger moves.

All parts are flat-shaded with Principled BSDF materials at roughness 0.8.
Pick the variant for each bracketed option below.
"""

import math
import random
import sys

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

# ----------------------------- variant switches ----------------------------- #
HAIR = "long"           # "long" = long dark hair, middle part | "wavy" = short messy wavy | "bun" = high bun + side bangs
GLASSES = "round"       # "round"  = thin round frames       | "rect" = chunky rectangular frames
OUTFIT = "hoodie"       # "hoodie" = cobalt blue hoodie | "jacket" = olive utility jacket | "sweater" = burnt orange sweater
MASCOT_SHAPE = "claude"  # "claude" = orange lobed Claude blob | "robot" = round robot cube | "fox" = crystal fox | "cactus" = geometric cactus
MASCOT_COLOR = "orange"  # "orange" (Claude) | "mint" | "coral" | "yellow"
DEMO_ANIMATION = True   # blinks + talk on the Cam_Human shot, hop/tilt on the Cam_Mascot shot
# ---------------------------------------------------------------------------- #

R = math.radians
HUMAN_POS, HUMAN_ROT_Z = (0.45, 0.50, 0.0), -10
MASCOT_POS, MASCOT_ROT_Z = (0.14, -0.20, 0.75), -10
HZ = 1.34                                   # head centre height (root space)


# ------------------------------- helpers ------------------------------------ #
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
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return bsdf


def mat(name, color, emit=0.0):
    m = bpy.data.materials.new(name)
    bsdf = _principled(m)
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8
    for n, v in (("Specular IOR Level", 0.3), ("Specular", 0.3)):
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = v
            break
    if emit > 0:
        for n in ("Emission Color", "Emission"):
            if n in bsdf.inputs:
                bsdf.inputs[n].default_value = (*color, 1.0)
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = (*color, 1.0)
    return m


def _euler(rot):
    return Euler(tuple(R(a) for a in rot))


def box(loc, size, rot=(0, 0, 0)):
    mtx = Matrix.LocRotScale(Vector(loc), _euler(rot), Vector(size))
    return lambda bm: bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)


def rbox(loc, size, bevel):
    """Chamfered (one-segment bevel) box: reads as a rounded low-poly cube."""
    mtx = Matrix.LocRotScale(Vector(loc), None, Vector(size))

    def build(bm):
        vs = bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)["verts"]
        es = list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=vs + es, offset=bevel, segments=1,
                        affect="EDGES", profile=0.5)
    return build


def cyl(loc, r1, r2, depth, seg=8, rot=(0, 0, 0), scale=(1, 1, 1)):
    mtx = Matrix.LocRotScale(Vector(loc), _euler(rot), Vector(scale))
    return lambda bm: bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=seg,
        radius1=r1, radius2=r2, depth=depth, matrix=mtx)


def ico(loc, r, sub=1, scale=(1, 1, 1), rot=(0, 0, 0), cut=None):
    """Icosphere; `cut(co) -> bool` deletes matching verts (used for hairlines)."""
    mtx = Matrix.LocRotScale(Vector(loc), _euler(rot), Vector(scale))

    def build(bm):
        vs = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r, matrix=mtx)["verts"]
        if cut:
            kill = [v for v in vs if cut(v.co)]
            if kill:
                bmesh.ops.delete(bm, geom=kill, context="VERTS")
    return build


def cyl_between(p1, p2, r, seg=8):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    mtx = Matrix.LocRotScale((p1 + p2) / 2, d.to_track_quat("Z", "Y"), None)
    return lambda bm: bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=seg,
        radius1=r, radius2=r, depth=d.length, matrix=mtx)


def torus(loc, major, minor, rot=(90, 0, 0), seg=16, mseg=4):
    mtx = Matrix.LocRotScale(Vector(loc), _euler(rot), None)

    def build(bm):
        rings = []
        for i in range(seg):
            a = math.tau * i / seg
            ring = []
            for j in range(mseg):
                b = math.tau * j / mseg
                rr = major + minor * math.cos(b)
                ring.append(bm.verts.new(mtx @ Vector((rr * math.cos(a), rr * math.sin(a),
                                                       minor * math.sin(b)))))
            rings.append(ring)
        for i in range(seg):
            n = (i + 1) % seg
            for j in range(mseg):
                m = (j + 1) % mseg
                bm.faces.new((rings[i][j], rings[n][j], rings[n][m], rings[i][m]))
    return build


def obj(name, parts, material, coll, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for build in parts:
        build(bm)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = False
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = _euler(rot)
    if parent is not None:
        ob.parent = parent
    return ob


def empty(name, coll, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), size=0.05, shape="PLAIN_AXES"):
    e = bpy.data.objects.new(name, None)
    coll.objects.link(e)
    e.empty_display_type = shape
    e.empty_display_size = size
    e.location = loc
    e.rotation_euler = _euler(rot)
    if parent is not None:
        e.parent = parent
    return e


def add_shape_keys(ob, basis_name, keys):
    ob.shape_key_add(name=basis_name, from_mix=False)
    out = {}
    for name, fn in keys.items():
        k = ob.shape_key_add(name=name, from_mix=False)
        for i, v in enumerate(ob.data.vertices):
            k.data[i].co = fn(v.co.copy())
        out[name] = k
    return out


# ------------------------------ cleanup ------------------------------------- #
def remove_old_characters():
    coll = bpy.data.collections.get("Characters")
    doomed = set(coll.all_objects) if coll else set()
    doomed |= {o for o in bpy.data.objects if o.name.startswith(("Human", "Mascot"))}
    for o in doomed:
        bpy.data.objects.remove(o, do_unlink=True)
    if coll:
        bpy.data.collections.remove(coll)
    for dbs in (bpy.data.meshes, bpy.data.materials):
        for block in list(dbs):
            if block.users == 0:
                dbs.remove(block)
    c = bpy.data.collections.new("Characters")
    bpy.context.scene.collection.children.link(c)
    return c


# --------------------------- main character --------------------------------- #
OUTFITS = {
    "hoodie": (0.06, 0.20, 0.78),    # cobalt blue
    "jacket": (0.33, 0.38, 0.17),    # olive green
    "sweater": (0.80, 0.33, 0.10),   # burnt orange
}


def build_human(C):
    rnd = random.Random(5)
    skin = mat("M_Char_Skin", (0.88, 0.64, 0.50))
    cloth = mat("M_Char_Outfit", OUTFITS[OUTFIT])
    cloth_dark = mat("M_Char_OutfitTrim", tuple(c * 0.7 for c in OUTFITS[OUTFIT]))
    hair = mat("M_Char_Hair", (0.045, 0.028, 0.025))
    ink = mat("M_Char_FaceInk", (0.03, 0.03, 0.04))
    white = mat("M_Char_EyeWhite", (0.95, 0.95, 0.93))
    frame_col = (0.06, 0.05, 0.07) if GLASSES == "round" else (0.12, 0.06, 0.05)
    frames = mat("M_Char_Glasses", frame_col)

    root = empty("Human_Root", C, loc=HUMAN_POS, rot=(0, 0, HUMAN_ROT_Z), size=0.25, shape="CIRCLE")
    head = empty("Human_Head", C, root, loc=(0, 0, HZ), size=0.12, shape="SPHERE")
    hp = dict(parent=head, loc=(0, 0, -HZ))   # head parts: mesh coords in root space

    # Chair
    obj("Human_Chair", [box((0, 0.10, 0.48), (0.46, 0.42, 0.06)),
                        box((0, 0.30, 0.86), (0.46, 0.05, 0.62)),
                        cyl((0, 0.10, 0.24), 0.03, 0.03, 0.45, seg=6),
                        cyl((0, 0.10, 0.02), 0.22, 0.22, 0.04, seg=5)],
        mat("M_Char_Chair", (0.15, 0.10, 0.18)), C, root)

    # Bust + folded arms resting on the desk (desk top z = 0.75)
    body = [cyl((0, 0, 0.92), 0.20, 0.15, 0.40, seg=8, scale=(1.2, 0.85, 1.0)),
            ico((0.20, -0.01, 1.06), 0.075, sub=1),             # shoulders
            ico((-0.20, -0.01, 1.06), 0.075, sub=1),
            cyl_between((0.21, -0.02, 1.04), (0.25, -0.20, 0.82), 0.055),   # upper arms
            cyl_between((-0.21, -0.02, 1.04), (-0.25, -0.20, 0.82), 0.055),
            ico((0.25, -0.20, 0.81), 0.058, sub=1),             # elbows on the desk
            ico((-0.25, -0.20, 0.81), 0.058, sub=1),
            cyl_between((-0.25, -0.21, 0.80), (0.15, -0.29, 0.81), 0.055),  # lower forearm
            cyl_between((0.25, -0.23, 0.85), (-0.15, -0.33, 0.855), 0.055)]  # upper forearm
    obj("Human_Body", body, cloth, C, root)
    obj("Human_Hands", [ico((0.17, -0.30, 0.83), 0.038, sub=1, scale=(0.9, 1.0, 0.8)),
                        ico((-0.17, -0.335, 0.87), 0.038, sub=1, scale=(0.9, 1.0, 0.8))],
        skin, C, root)

    # Outfit details
    if OUTFIT == "hoodie":
        obj("Human_Outfit_Hood", [ico((0, 0.12, 1.13), 0.15, sub=1, scale=(1.15, 0.7, 0.5)),
                                  cyl((0, 0.01, 1.125), 0.11, 0.095, 0.035, seg=8)],
            cloth_dark, C, root)
        obj("Human_Outfit_Strings", [cyl_between((0.04, -0.15, 1.10), (0.05, -0.19, 0.98), 0.006, 5),
                                     cyl_between((-0.04, -0.15, 1.10), (-0.05, -0.19, 0.98), 0.006, 5)],
            mat("M_Char_Strings", (0.92, 0.92, 0.90)), C, root)
    elif OUTFIT == "jacket":
        obj("Human_Outfit_Collar", [box((0.065, -0.10, 1.11), (0.085, 0.025, 0.07), rot=(20, 0, -25)),
                                    box((-0.065, -0.10, 1.11), (0.085, 0.025, 0.07), rot=(20, 0, 25)),
                                    box((0.12, -0.165, 0.99), (0.07, 0.02, 0.06)),   # chest pockets
                                    box((-0.12, -0.165, 0.99), (0.07, 0.02, 0.06))],
            cloth_dark, C, root)
        obj("Human_Outfit_Tee", [box((0, -0.155, 1.02), (0.09, 0.02, 0.18))],
            mat("M_Char_Tee", (0.08, 0.08, 0.10)), C, root)
    else:  # sweater
        obj("Human_Outfit_Ribbing", [cyl((0, 0, 1.125), 0.10, 0.085, 0.035, seg=8),
                                     cyl((0.15, -0.29, 0.81), 0.06, 0.06, 0.03, seg=8, rot=(0, 90, -10)),
                                     cyl((-0.15, -0.33, 0.855), 0.06, 0.06, 0.03, seg=8, rot=(0, 90, 10))],
            cloth_dark, C, root)

    # Neck + big rounded head
    obj("Human_Neck", [cyl((0, 0, 1.13), 0.05, 0.05, 0.07, seg=6)], skin, C, root)
    obj("Human_HeadMesh", [ico((0, 0, HZ), 0.20, sub=2, scale=(1.0, 0.92, 0.95)),
                           ico((0.198, 0.0, HZ - 0.01), 0.03, sub=1, scale=(0.5, 1, 1)),   # ears
                           ico((-0.198, 0.0, HZ - 0.01), 0.03, sub=1, scale=(0.5, 1, 1)),
                           ico((0, -0.183, HZ - 0.035), 0.016, sub=1)],                   # nose
        skin, C, **hp)

    # Eyes: white ovals + black pupils
    obj("Human_EyeWhites", [ico((x, -0.172, HZ), 0.035, sub=2, scale=(0.8, 0.35, 1.1)) for x in (0.07, -0.07)],
        white, C, **hp)
    obj("Human_Pupils", [ico((x * 0.97, -0.186, HZ - 0.004), 0.016, sub=2, scale=(0.8, 0.4, 1.1))
                         for x in (0.07, -0.07)], ink, C, **hp)

    # Eyelids (shape keys: Open / Blink): curved skin lids that follow the eye
    # outline, plus a lash line on the lid edge that is driven by Blink.
    HW, N = 0.033, 9

    def ell(dx):
        return math.sqrt(max(0.0, 1.0 - (dx / HW) ** 2))

    def lid_top(dx):
        return HZ + 0.047 * ell(dx)

    def lid_edge(dx):            # open: thin crescent above the eye
        return HZ + 0.036 * ell(dx)

    def lid_edge_closed(dx):     # closed: edge follows the bottom of the eye
        return HZ - 0.040 * ell(dx)

    lid_targets, lash_targets = [], []

    def strip(y, top_fn, bot_fn, targets, closed_top, closed_bot, flick=False):
        def build(bm):
            for cx in (0.07, -0.07):
                xs = [cx - HW + 2 * HW * i / (N - 1) for i in range(N)]
                top = [bm.verts.new((x, y, top_fn(x - cx))) for x in xs]
                bot = [bm.verts.new((x, y, bot_fn(x - cx))) for x in xs]
                targets.extend([closed_top(x - cx) for x in xs] + [closed_bot(x - cx) for x in xs])
                for i in range(N - 1):
                    bm.faces.new((bot[i], bot[i + 1], top[i + 1], top[i]))
                if flick:                                   # little outer lash flick
                    s = 1 if cx > 0 else -1
                    o = top[-1] if s > 0 else top[0]
                    a = bm.verts.new((cx + s * (HW + 0.012), y, HZ + 0.012))
                    b = bm.verts.new((cx + s * (HW - 0.004), y, HZ + 0.010))
                    bm.faces.new((o, a, b))
                    targets.extend([HZ - 0.004, HZ - 0.006])
        return build

    lids = obj("Human_Eyelids", [strip(-0.199, lid_top, lid_edge, lid_targets,
                                       lid_top, lid_edge_closed)],
               mat("M_Char_Eyelid", (0.84, 0.60, 0.47)), C, **hp)
    lashes = obj("Human_Lashes", [strip(-0.2005, lambda d: lid_edge(d) + 0.004,
                                        lambda d: lid_edge(d) - 0.002, lash_targets,
                                        lambda d: lid_edge_closed(d) + 0.002,
                                        lambda d: lid_edge_closed(d) - 0.004, flick=True)],
                 ink, C, **hp)

    def key_from_targets(ob, basis, name, targets):
        ob.shape_key_add(name=basis, from_mix=False)
        k = ob.shape_key_add(name=name, from_mix=False)
        for i, z in enumerate(targets):
            k.data[i].co.z = z
        return k
    lid_keys = {"Blink": key_from_targets(lids, "Open", "Blink", lid_targets)}
    lash_key = key_from_targets(lashes, "Open", "Blink", lash_targets)
    fc = lash_key.driver_add("value")                    # lashes follow the eyelids
    v = fc.driver.variables.new()
    v.name, v.type = "blink", "SINGLE_PROP"
    v.targets[0].id_type = "KEY"
    v.targets[0].id = lids.data.shape_keys
    v.targets[0].data_path = 'key_blocks["Blink"].value'
    fc.driver.expression = "blink"

    # Soft blush
    obj("Human_Blush", [ico((s * 0.105, -0.158, HZ - 0.052), 0.022, sub=1, scale=(1.3, 0.25, 0.7))
                        for s in (1, -1)], mat("M_Char_Blush", (0.95, 0.45, 0.45)), C, **hp)

    # Flat plane eyebrows
    brows = []
    for s in (1, -1):
        brows.append(box((s * 0.075, -0.164, HZ + 0.082), (0.05, 0.002, 0.008), rot=(-12, s * 6, 0)))
    obj("Human_Eyebrows", brows, hair, C, **hp)

    # Mouth: dark 4x2-vertex plane (shape keys: Closed / Talk_Open / Smile)
    MZ, MY = HZ - 0.085, -0.174
    xs = (-0.026, -0.009, 0.009, 0.026)

    def mouth_plane(bm):
        top = [bm.verts.new((x, MY, MZ + 0.003)) for x in xs]
        bot = [bm.verts.new((x, MY, MZ - 0.003)) for x in xs]
        for i in range(3):
            bm.faces.new((bot[i], bot[i + 1], top[i + 1], top[i]))
    mouth = obj("Human_Mouth", [mouth_plane], mat("M_Char_Mouth", (0.55, 0.10, 0.16)), C, **hp)

    def talk(co):
        inner, lower = abs(co.x) < 0.015, co.z < MZ
        if inner:
            co.z += -0.026 if lower else 0.003
        else:
            co.z += -0.010 if lower else 0.0
            co.x *= 0.85
        return co

    def smile(co):
        if abs(co.x) > 0.015:
            co.z += 0.012
            co.x *= 1.12
        elif co.z < MZ:
            co.z -= 0.004
        return co
    mouth_keys = add_shape_keys(mouth, "Closed", {"Talk_Open": talk, "Smile": smile})

    # Glasses
    if GLASSES == "round":
        parts = [torus((x, -0.215, HZ), 0.055, 0.0045) for x in (0.075, -0.075)]
        parts.append(cyl_between((-0.022, -0.215, HZ + 0.01), (0.022, -0.215, HZ + 0.01), 0.004, 5))
        side_x = 0.13
    else:
        parts = []
        for x in (0.077, -0.077):
            w, h, t = 0.125, 0.09, 0.018
            parts += [box((x, -0.215, HZ + h / 2), (w, 0.016, t)),
                      box((x, -0.215, HZ - h / 2), (w, 0.016, t)),
                      box((x - w / 2, -0.215, HZ), (t, 0.016, h + t)),
                      box((x + w / 2, -0.215, HZ), (t, 0.016, h + t))]
        parts.append(box((0, -0.215, HZ + 0.02), (0.035, 0.014, 0.014)))
        side_x = 0.14
    for s in (1, -1):
        parts.append(cyl_between((s * side_x, -0.212, HZ + 0.01), (s * 0.205, -0.02, HZ + 0.015), 0.005, 5))
    obj("Human_Glasses", parts, frames, C, **hp)

    # Hair: cap with the face cut out + style details
    def face_cut(co, bottom):
        return (co.y < -0.05 and co.z < HZ + 0.09) or co.z < bottom

    if HAIR == "long":
        # Cap with only the face cut out, a long back panel past the shoulders,
        # side curtains framing the face and a middle-parted fringe sweeping out.
        hair_parts = [ico((0, 0.03, HZ + 0.04), 0.215, sub=2, scale=(1.04, 1.0, 0.9),
                          cut=lambda co: co.y < -0.05 and co.z < HZ + 0.09),
                      ico((0, 0.10, HZ - 0.14), 0.20, sub=2, scale=(1.08, 0.55, 1.45),
                          cut=lambda co: co.y < 0.0),
                      ico((0.172, -0.06, HZ - 0.12), 0.055, sub=2, scale=(0.85, 0.9, 3.4), rot=(0, -6, 0)),
                      ico((-0.172, -0.06, HZ - 0.12), 0.055, sub=2, scale=(0.85, 0.9, 3.4), rot=(0, 6, 0)),
                      ico((0.075, -0.14, HZ + 0.125), 0.07, sub=2, scale=(1.3, 0.4, 0.42), rot=(0, 26, 0)),
                      ico((-0.075, -0.14, HZ + 0.125), 0.07, sub=2, scale=(1.3, 0.4, 0.42), rot=(0, -26, 0))]
    elif HAIR == "wavy":
        hair_parts = [ico((0, 0.03, HZ + 0.04), 0.215, sub=2, scale=(1.04, 1.0, 0.9),
                          cut=lambda co: face_cut(co, HZ - 0.07))]
        for _ in range(11):                                    # messy wavy tufts
            a = rnd.uniform(0, math.tau)
            el = rnd.uniform(R(10), R(70))
            d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el) * 0.9 + 0.12,
                        math.sin(el))).normalized()
            if d.y < -0.35 and d.z < 0.6:
                d.y = -0.35
            p = Vector((0, 0.03, HZ + 0.04)) + d * 0.2
            hair_parts.append(ico(tuple(p), rnd.uniform(0.05, 0.075), sub=1,
                                  scale=(1.2, 0.8, 0.65), rot=(rnd.uniform(-30, 30), rnd.uniform(-40, 40),
                                                               rnd.uniform(0, 180))))
        for x, tilt in ((-0.10, 25), (-0.035, 10), (0.03, -15), (0.10, -30)):   # bangs
            hair_parts.append(ico((x, -0.165, HZ + 0.135), 0.048, sub=1,
                                  scale=(1.25, 0.6, 0.7), rot=(0, tilt, 0)))
    else:  # high bun with side bangs
        hair_parts = [ico((0, 0.03, HZ + 0.04), 0.215, sub=2, scale=(1.04, 1.0, 0.9),
                          cut=lambda co: face_cut(co, HZ - 0.12)),
                      ico((0, 0.06, HZ + 0.26), 0.095, sub=2),                     # bun
                      ico((0.135, -0.14, HZ - 0.02), 0.045, sub=1, scale=(0.7, 0.55, 2.2), rot=(0, -8, 0)),
                      ico((-0.135, -0.14, HZ - 0.02), 0.045, sub=1, scale=(0.7, 0.55, 2.2), rot=(0, 8, 0)),
                      ico((-0.05, -0.165, HZ + 0.13), 0.06, sub=1, scale=(1.8, 0.55, 0.6), rot=(0, 12, 0))]
        obj("Human_HairTie", [torus((0, 0.05, HZ + 0.185), 0.06, 0.012, rot=(0, 0, 0), seg=10)],
            mat("M_Char_HairTie", (0.95, 0.45, 0.55)), C, **hp)
    obj("Human_Hair", hair_parts, hair, C, **hp)

    focus = empty("Human_FocusTarget", C, head, loc=(0, -0.18, 0), size=0.03)
    return root, focus, mouth_keys, lid_keys


# ------------------------------ mascot -------------------------------------- #
MASCOT_COLORS = {"orange": (0.92, 0.17, 0.02), "mint": (0.45, 0.92, 0.72), "coral": (1.0, 0.50, 0.45), "yellow": (1.0, 0.90, 0.50)}


def build_mascot(C):
    base_col = MASCOT_COLORS[MASCOT_COLOR]
    body_m = mat("M_Mascot_Body", base_col)
    dark_m = mat("M_Mascot_Feet", tuple(c * 0.6 for c in base_col))
    eye_m = mat("M_Mascot_Eyes", (0.02, 0.02, 0.02))
    accent_m = mat("M_Mascot_Accent", (1.0, 0.98, 0.92))

    root = empty("Mascot_Root", C, loc=MASCOT_POS, rot=(0, 0, MASCOT_ROT_Z), size=0.09, shape="CIRCLE")
    root["hop"] = 0.0
    root["tilt"] = 0.0
    try:
        root.id_properties_ui("hop").update(min=0.0, max=1.0, description="Hop height (0..1 -> 0..6 cm)")
        root.id_properties_ui("tilt").update(min=-1.0, max=1.0, description="Side tilt (-1..1 -> +/-15 deg)")
    except Exception:
        pass
    bounce = empty("Mascot_Bounce", C, root, size=0.05)
    for idx, expr, var in ((2, "hop * 0.06", "hop"), (None, "tilt * 0.2618", "tilt")):
        fc = bounce.driver_add("location", idx) if idx is not None else bounce.driver_add("rotation_euler", 1)
        drv = fc.driver
        drv.type = "SCRIPTED"
        v = drv.variables.new()
        v.name, v.type = var, "SINGLE_PROP"
        v.targets[0].id = root
        v.targets[0].data_path = f'["{var}"]'
        drv.expression = expr

    feet = [cyl((x, -0.005, 0.0125), 0.021, 0.019, 0.025, seg=6) for x in (0.032, -0.032)]
    eye = (0.013, 0.004, 0.030)   # vertical black rectangle
    feet_m = dark_m

    if MASCOT_SHAPE == "claude":
        # Faceted orange blob: a core with seven round lobes around its edge
        # (gap at the bottom for the feet), two tall black eyes, round feet.
        cz, ring = 0.13, 0.058
        lobes = [ico((0, 0, cz), 0.084, sub=2, scale=(1.0, 0.8, 0.98))]
        for i in range(7):
            a = R(90 + i * 360 / 7)
            lobes.append(ico((ring * math.cos(a), 0.004, cz + ring * math.sin(a)), 0.046, sub=2,
                             scale=(1.0, 0.8, 1.0)))
        obj("Mascot_Body", lobes, body_m, C, bounce)
        feet = [ico((x, -0.006, 0.02), 0.024, sub=2, scale=(1.05, 1.0, 0.8)) for x in (0.032, -0.032)]
        feet_m = body_m
        eye = (0.0125, 0.004, 0.036)
        eye_pos, eye_y = (0.026, 0.14), -0.066
    elif MASCOT_SHAPE == "robot":
        obj("Mascot_Body", [rbox((0, 0, 0.095), (0.14, 0.13, 0.135), 0.022)], body_m, C, bounce)
        obj("Mascot_Details", [cyl((0, 0, 0.18), 0.005, 0.005, 0.035, seg=5),
                               cyl((0.073, 0, 0.10), 0.018, 0.018, 0.012, seg=6, rot=(0, 90, 0)),
                               cyl((-0.073, 0, 0.10), 0.018, 0.018, 0.012, seg=6, rot=(0, 90, 0))],
            dark_m, C, bounce)
        obj("Mascot_AntennaBall", [ico((0, 0, 0.203), 0.013, sub=1)], accent_m, C, bounce)
        obj("Mascot_Cheeks", [box((x, -0.066, 0.085), (0.018, 0.003, 0.008)) for x in (0.045, -0.045)],
            mat("M_Mascot_Cheeks", (1.0, 0.55, 0.60)), C, bounce)
        eye_pos, eye_y = (0.026, 0.11), -0.067
    elif MASCOT_SHAPE == "fox":
        obj("Mascot_Body", [ico((0, 0.01, 0.075), 0.065, sub=1, scale=(1.0, 0.95, 0.95)),
                            ico((0, -0.01, 0.165), 0.065, sub=1, scale=(1.1, 0.9, 0.9)),
                            cyl((0.04, 0, 0.225), 0.028, 0.0, 0.06, seg=3, rot=(0, 15, 0)),
                            cyl((-0.04, 0, 0.225), 0.028, 0.0, 0.06, seg=3, rot=(0, -15, 0)),
                            cyl((0, -0.075, 0.15), 0.028, 0.0, 0.045, seg=4, rot=(90, 0, 0)),
                            cyl((0, 0.08, 0.075), 0.032, 0.012, 0.10, seg=4, rot=(-60, 0, 0))],
            body_m, C, bounce)
        obj("Mascot_Details", [ico((0, 0.123, 0.10), 0.016, sub=1),                     # tail tip
                               ico((0, -0.03, 0.095), 0.035, sub=1, scale=(0.9, 0.6, 1.1))],  # chest
            accent_m, C, bounce)
        obj("Mascot_Nose", [ico((0, -0.098, 0.15), 0.008, sub=1)], eye_m, C, bounce)
        eye_pos, eye_y = (0.025, 0.182), -0.068
    else:  # cactus
        obj("Mascot_Body", [cyl((0, 0, 0.095), 0.055, 0.055, 0.14, seg=8),
                            ico((0, 0, 0.165), 0.055, sub=1, scale=(1, 1, 0.7)),
                            cyl_between((-0.05, 0, 0.09), (-0.088, 0, 0.09), 0.021, 6),
                            cyl_between((-0.088, 0, 0.09), (-0.088, 0, 0.145), 0.021, 6),
                            ico((-0.088, 0, 0.145), 0.021, sub=1),
                            cyl_between((0.05, 0, 0.075), (0.085, 0, 0.075), 0.019, 6),
                            cyl_between((0.085, 0, 0.075), (0.085, 0, 0.11), 0.019, 6),
                            ico((0.085, 0, 0.11), 0.019, sub=1)], body_m, C, bounce)
        obj("Mascot_Details", [box((x, y, z), (0.004, 0.004, 0.012))
                               for x, y, z in ((0.035, -0.045, 0.06), (-0.04, -0.04, 0.15),
                                               (0.05, 0.02, 0.14), (-0.05, 0.03, 0.06),
                                               (0.0, 0.055, 0.12))], accent_m, C, bounce)
        obj("Mascot_Flower", [cyl((0, 0, 0.205), 0.022, 0.008, 0.018, seg=5)],
            mat("M_Mascot_Flower", (1.0, 0.45, 0.65)), C, bounce)
        eye_pos, eye_y = (0.022, 0.12), -0.055

    obj("Mascot_Feet", feet, feet_m, C, bounce)
    ex, ez = eye_pos
    obj("Mascot_Eyes", [box((x, eye_y, ez), eye) for x in (ex, -ex)], eye_m, C, bounce)
    focus = empty("Mascot_FocusTarget", C, bounce, loc=(0, -0.066, 0.13), size=0.03)
    return root, focus


# ------------------------- cameras + demo animation ------------------------- #
def retarget_cameras(human_focus, mascot_focus):
    def place(name, loc, target, lens, focus):
        cam = bpy.data.objects.get(name)
        if not cam or cam.type != "CAMERA":
            return
        cam.location = loc
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = 2.8
        cam.data.dof.focus_object = focus

    place("Cam_Human", (0.20, -0.85, 1.32), (0.45, 0.50, 1.22), 50, human_focus)
    place("Cam_Mascot", (0.05, -0.80, 0.89), (0.14, -0.20, 0.86), 45, mascot_focus)


def demo_animation(mouth_keys, lid_keys, mascot_root):
    def key(kb, pairs):
        for f, v in pairs:
            kb.value = v
            kb.keyframe_insert("value", frame=f)

    blink = []
    for f in (40, 96, 130, 190):
        blink += [(f, 0.0), (f + 2, 1.0), (f + 4, 0.0)]
    key(lid_keys["Blink"], blink)

    talk = [(78, 0.0)]
    for i, f in enumerate(range(80, 122, 3)):
        talk.append((f, 0.8 if i % 2 == 0 else 0.15))
    talk.append((124, 0.0))
    key(mouth_keys["Talk_Open"], talk)
    key(mouth_keys["Smile"], [(124, 0.0), (128, 1.0), (142, 1.0), (146, 0.0)])

    def key_prop(prop, pairs):
        for f, v in pairs:
            mascot_root[prop] = v
            mascot_root.keyframe_insert(data_path=f'["{prop}"]', frame=f)
    key_prop("hop", [(150, 0.0), (154, 1.0), (158, 0.0), (162, 0.6), (166, 0.0),
                     (196, 0.0), (200, 1.0), (204, 0.0)])
    key_prop("tilt", [(166, 0.0), (172, 0.6), (180, -0.6), (188, 0.3), (194, 0.0)])


def main():
    C = remove_old_characters()
    _, human_focus, mouth_keys, lid_keys = build_human(C)
    mascot_root, mascot_focus = build_mascot(C)
    retarget_cameras(human_focus, mascot_focus)
    if DEMO_ANIMATION:
        demo_animation(mouth_keys, lid_keys, mascot_root)
    bpy.context.view_layer.update()


main()
_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if "--save" in _argv and _argv.index("--save") + 1 < len(_argv):
    bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(_argv[_argv.index("--save") + 1]))
print(f"Characters built: hair={HAIR} glasses={GLASSES} outfit={OUTFIT} "
      f"mascot={MASCOT_SHAPE}/{MASCOT_COLOR}")
