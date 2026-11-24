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
HAIR = "sleek"          # "sleek" = straight jaw-length locks + fringe (reference) | "curtain" = centre part, two smooth curtains framing the face (reference) | "strands" = long locks from a side part (reference) | "bob" = chin-length bob, side fringe | "long" = long, middle part | "wavy" = short messy | "bun" = high bun
GLASSES = "big"         # "none" = no glasses | "big" = large thin black round (reference) | "round" = thin round | "rect" = chunky rectangular
STYLE = "chibi"         # "chibi" = big smooth head on a small low-poly body (reference mix) | "lowpoly" = all faceted
FACE = "dots"            # "dots" = small black dot eyes with a glint (reference) | "ovals" = white eyes, lids, lashes, brows
NECKLINE = "open"       # "crew" = smooth top with a rolled neckline | "open" = open jacket over a dark tee strip (reference)
OUTFIT = "lavender"     # "lavender" = lilac jacket + dark tee | "yellow" = yellow jacket + dark tee (reference) | "hoodie" = cobalt hoodie | "jacket" = olive jacket | "sweater" = burnt orange
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


def rbox(loc, size, bevel, segments=1):
    """Box of the given dimensions with all edges beveled (rounded corners)."""
    mtx = Matrix.LocRotScale(Vector(loc), None, Vector(size))

    def build(bm):
        vs = bmesh.ops.create_cube(bm, size=1.0, matrix=mtx)["verts"]
        es = list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=vs + es, offset=bevel, segments=segments,
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


def cone_between(p1, p2, r1, r2, seg=7):
    """Tapered segment from p1 (radius r1) to p2 (radius r2)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    mtx = Matrix.LocRotScale((p1 + p2) / 2, d.to_track_quat("Z", "Y"), None)
    return lambda bm: bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=seg,
        radius1=r1, radius2=r2, depth=d.length, matrix=mtx)


def puff_chain(p1, p2, r, spacing=0.8, squash=(1.0, 1.0, 1.0)):
    """Puffy quilted sleeve: overlapping soft bulges from p1 to p2."""
    p1, p2 = Vector(p1), Vector(p2)
    n = max(2, int((p2 - p1).length / (r * spacing)) + 1)
    return [ico(tuple(p1.lerp(p2, i / (n - 1))), r * (0.92 + 0.08 * ((i % 2) == 0)), sub=2, scale=squash)
            for i in range(n)]


def hair_lock(points, r0, r1, seg=8, normal_from=None, flat=(1.8, 0.5), tip=0.35):
    """A lock of hair swept as ONE continuous tube along `points`: flat
    elliptical cross-section (wide across the head, thin outward) tapering from
    r0 to a near-point tip, so locks lie on the head like smooth strands."""
    pts = [Vector(p) for p in points]
    n = len(pts)
    centre = Vector(normal_from) if normal_from is not None else None

    def build(bm):
        rings = []
        for i, p in enumerate(pts):
            tan = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
            radial = (p - centre) if centre is not None else Vector((0, -1, 0))
            x = tan.cross(radial)
            if x.length < 1e-6:
                x = tan.orthogonal()
            x.normalize()
            y = tan.cross(x).normalized()
            t = i / (n - 1)
            r = r0 + (r1 - r0) * t
            if i == n - 1:
                r *= tip                                     # soft tapered tip
            ring = []
            for k in range(seg):
                a = 2 * math.pi * k / seg
                ring.append(bm.verts.new(p + x * (math.cos(a) * r * flat[0]) + y * (math.sin(a) * r * flat[1])))
            rings.append(ring)
        for i in range(n - 1):
            for k in range(seg):
                k2 = (k + 1) % seg
                bm.faces.new((rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]))
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    return [build]


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
    "yellow": (0.60, 0.46, 0.0),     # lemon-shifted so it still reads yellow under the warm key
    "lavender": (0.26, 0.13, 0.58),  # lavender / lilac (deep enough to survive the warm key)
    "sweater": (0.80, 0.33, 0.10),   # burnt orange
}


def build_human(C):
    rnd = random.Random(5)
    skin = mat("M_Char_Skin", (0.85, 0.31, 0.19))      # warm peach-pink (reference)
    _sb = _principled(skin)
    for n, v in (("Subsurface Weight", 0.35), ("Subsurface", 0.35), ("Subsurface Scale", 0.03),
                 ("Roughness", 0.55), ("Specular IOR Level", 0.35), ("Sheen Weight", 0.15)):
        if n in _sb.inputs:
            _sb.inputs[n].default_value = v
    if "Subsurface Radius" in _sb.inputs:
        _sb.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.2)
    cloth = mat("M_Char_Outfit", OUTFITS[OUTFIT])
    cloth_dark = mat("M_Char_OutfitTrim", tuple(c * 0.7 for c in OUTFITS[OUTFIT]))
    hair = mat("M_Char_Hair", (0.008, 0.006, 0.006))      # near-black (reference)
    _principled(hair).inputs["Roughness"].default_value = 0.65  # soft highlight, no plastic sheen
    ink = mat("M_Char_FaceInk", (0.03, 0.03, 0.04))
    white = mat("M_Char_EyeWhite", (0.95, 0.95, 0.93))
    frame_col = {"big": (0.008, 0.008, 0.01), "round": (0.06, 0.05, 0.07)}.get(GLASSES, (0.12, 0.06, 0.05))
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
    puffy = OUTFIT in ("yellow", "lavender")
    if puffy:
        # Soft puffy jacket (reference): rounded torso, quilted sleeves, arms
        # crossed on the desk
        torso = ico((0, 0.01, 0.95), 0.20, sub=2, scale=(1.22, 0.86, 1.15))
        if NECKLINE == "open":   # dark tee body; the jacket is two smooth panels left open at the front
            obj("Human_Torso", [torso], mat("M_Char_Tee", (0.03, 0.03, 0.035)), C, root)
            body = [ico((sx * 0.125, -0.002, 0.95), 0.20, sub=2, scale=(0.62, 0.9, 1.15)) for sx in (1, -1)]
        else:
            body = [torso]
        body += [
                ico((0.20, 0.0, 1.06), 0.10, sub=2), ico((-0.20, 0.0, 1.06), 0.10, sub=2)]
        def sleeve(pts, r0, r1):                     # smooth puffy tube (reference sleeves)
            return hair_lock(pts, r0, r1, seg=12, flat=(1.0, 1.0), tip=1.0)
        for sx in (1, -1):                           # upper arms with soft elbows
            body += sleeve([(sx * 0.22, 0.0, 1.05), (sx * 0.265, -0.07, 0.98), (sx * 0.28, -0.15, 0.89),
                            (sx * 0.27, -0.19, 0.85)], 0.088, 0.08)
            body.append(ico((sx * 0.27, -0.20, 0.845), 0.082, sub=2))
        body += sleeve([(0.27, -0.21, 0.83), (0.10, -0.27, 0.84), (-0.11, -0.30, 0.85)], 0.074, 0.066)   # lower forearm
        body += sleeve([(-0.27, -0.22, 0.87), (-0.08, -0.30, 0.885), (0.12, -0.335, 0.90)], 0.074, 0.066)  # upper forearm
    else:
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
    hands = ([ico((-0.165, -0.31, 0.855), 0.044, sub=2, scale=(1.1, 0.9, 0.85)),   # peeking from the cuffs
              ico((0.175, -0.345, 0.905), 0.044, sub=2, scale=(1.1, 0.9, 0.85))] if OUTFIT in ("yellow", "lavender") else
             [ico((0.17, -0.30, 0.83), 0.038, sub=1, scale=(0.9, 1.0, 0.8)),
              ico((-0.17, -0.335, 0.87), 0.038, sub=1, scale=(0.9, 1.0, 0.8))])
    obj("Human_Hands", hands,
        skin, C, root)

    # Outfit details
    if OUTFIT == "hoodie":
        obj("Human_Outfit_Hood", [ico((0, 0.12, 1.13), 0.15, sub=1, scale=(1.15, 0.7, 0.5)),
                                  cyl((0, 0.01, 1.125), 0.11, 0.095, 0.035, seg=8)],
            cloth_dark, C, root)
        obj("Human_Outfit_Strings", [cyl_between((0.04, -0.15, 1.10), (0.05, -0.19, 0.98), 0.006, 5),
                                     cyl_between((-0.04, -0.15, 1.10), (-0.05, -0.19, 0.98), 0.006, 5)],
            mat("M_Char_Strings", (0.92, 0.92, 0.90)), C, root)
    elif OUTFIT in ("yellow", "lavender"):   # puffy jacket: soft lapels over a dark tee
        # Neckline: a soft rolled collar around the base of the neck (both styles)
        obj("Human_Outfit_TeeCollar", [torus((0, -0.015, 1.105), 0.078, 0.03, rot=(-12, 0, 0), seg=20, mseg=8)],
            cloth_dark if NECKLINE == "crew" else cloth, C, root)
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
    neck_m = skin                                   # bare neck above the crew-neck collar
    obj("Human_Neck", [cyl((0, 0, 1.13), 0.05, 0.05, 0.07, seg=6)], neck_m, C, root)
    head_mesh = obj("Human_HeadMesh", [ico((0, 0, HZ), 0.20, sub=3 if STYLE == "chibi" else 2, scale=(1.0, 0.92, 1.03)),   # slightly oval: adult chin
                           ico((0.198, 0.0, HZ - 0.01), 0.03, sub=1, scale=(0.5, 1, 1)),   # ears
                           ico((-0.198, 0.0, HZ - 0.01), 0.03, sub=1, scale=(0.5, 1, 1)),
                           ico((0, -0.182, HZ - 0.035), 0.016 if FACE != "dots" else 0.014, sub=1, scale=(0.9, 1.0, 1.15))],  # nose
        skin, C, **hp)

    # Eyes: white ovals + black pupils
    obj("Human_EyeWhites", [ico((x, -0.172, HZ), 0.035, sub=2, scale=(0.8, 0.35, 1.1)) for x in (0.07, -0.07)],
        white, C, **hp)
    if FACE == "dots":
        # Reference style: small black dot eyes, each with a tiny white glint
        def glint(loc):
            mtx = Matrix.LocRotScale(Vector(loc), None, Vector((1.0, 0.5, 1.0)))

            def b(bm):
                vs = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.0055, matrix=mtx)["verts"]
                for fc in {fc for v in vs for fc in v.link_faces}:
                    fc.material_index = 1
            return b
        parts = []
        for x in (0.078, -0.078):                 # adult proportions: smaller, higher, wider apart
            parts.append(ico((x, -0.169, HZ + 0.006), 0.016, sub=2, scale=(0.8, 0.35, 1.05)))
            parts.append(glint((x + 0.005, -0.1755, HZ + 0.012)))
        pupils = obj("Human_Pupils", parts, ink, C, **hp)
        pupils.data.materials.append(mat("M_Char_EyeGlint", (1.0, 1.0, 1.0), emit=2.0))
    else:
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
    MZ, MY = HZ - 0.105, -0.163                # lower mouth reads older
    xs = (-0.019, -0.0065, 0.0065, 0.019)           # small mouth

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
    if GLASSES == "big":                     # large thin black round frames (reference)
        parts = [torus((x, -0.212, HZ + 0.004), 0.08, 0.0028, seg=28) for x in (0.086, -0.086)]
        parts.append(cyl_between((-0.009, -0.214, HZ + 0.004), (0.009, -0.214, HZ + 0.004), 0.0028, 5))
        side_x = 0.168
    elif GLASSES == "round":
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

    if HAIR == "sleek":
        # Reference (front + profile): sleek, straight, thick flat locks that
        # hug the head from the crown, then fall vertically to jaw/shoulder
        # level; a fringe of locks falls over the forehead to just above the
        # glasses; side locks hang in front of the ears.
        hc = Vector((0, 0.015, HZ + 0.005))
        hr = 0.232
        bottom = HZ - 0.25                                   # jaw / top-of-shoulder length

        def on_head(d, r=hr):
            d = Vector(d).normalized()
            return hc + Vector((d.x * r * 1.04, d.y * r * 0.97, d.z * r))

        def path(d0, d1, steps=8, r=hr):
            a0, a1 = Vector(d0).normalized(), Vector(d1).normalized()
            return [on_head(a0.slerp(a1, i / steps), r) for i in range(steps + 1)]

        def fall(pts, length_to, flare=0.012, steps=4):
            """Continue a lock straight down to z = length_to with a tiny outward flare."""
            p = pts[-1]
            out = Vector((p.x - hc.x, p.y - hc.y, 0))
            out = out.normalized() * flare if out.length > 1e-6 else Vector()
            return pts + [p + out * (k / steps) + Vector((0, 0, (length_to - p.z) * k / steps)) for k in range(1, steps + 1)]

        rnd_h = random.Random(33)
        hair_parts = [ico((0, 0.02, HZ + 0.02), 0.222, sub=2, scale=(1.05, 1.0, 0.95),
                          cut=lambda co: co.y < -0.05 and co.z < HZ + 0.06)]
        part_x = -0.02
        # sides + back: from the crown, over the head, then straight down
        for i in range(20):
            az = math.radians(-22 + i * (224 / 19))                     # cheek -> back -> other cheek (face stays clear)
            root = (part_x + 0.03 * math.cos(az), 0.25 + 0.15 * math.sin(az), 1.0)
            r_i = hr + (0.01 if i % 2 else 0.0)                          # neighbouring locks overlap: grooves
            pts = path(root, (math.cos(az), math.sin(az), 0.05), 7, r_i)
            pts = fall(pts, bottom + rnd_h.uniform(-0.025, 0.02))
            hair_parts += hair_lock(pts, 0.05, 0.03, seg=6, normal_from=hc, flat=(2.2, 0.75), tip=0.25)
        # fringe: from the front of the part, forward and down over the forehead
        for az_deg, el in ((-52, 0.24), (-66, 0.32), (-79, 0.40), (-101, 0.40), (-114, 0.32), (-128, 0.24)):   # parted in the middle
            az = math.radians(az_deg)
            root = (part_x, -0.15, 1.0)
            pts = path(root, (math.cos(az), math.sin(az), el), 8, hr + 0.006)
            hair_parts += hair_lock(pts, 0.045, 0.02, seg=6, normal_from=hc, flat=(2.2, 0.7), tip=0.3)
    elif HAIR == "curtain":
        # Reference hair: near-centre part; a few wide, smooth bands sweep from
        # the part down each side as two curtains over the forehead corners,
        # framing the face and falling past the shoulders. Middle of the
        # forehead stays visible under the part.
        hc = Vector((0, 0.02, HZ + 0.01))
        hr = 0.258                                           # fuller top volume

        def on_head(d, r=hr):
            d = Vector(d).normalized()
            return hc + Vector((d.x * r * 1.04, d.y * r * 0.98, d.z * r))

        def path(d0, d1, steps=8, r=hr):
            a0, a1 = Vector(d0).normalized(), Vector(d1).normalized()
            return [on_head(a0.slerp(a1, i / steps), r) for i in range(steps + 1)]

        hair_parts = [ico((0, 0.03, HZ + 0.03), 0.226, sub=2, scale=(1.06, 1.0, 0.95),
                          cut=lambda co: co.y < -0.05 and co.z < HZ + 0.07)]
        N = 7
        rnd_h = random.Random(21)
        for side in (1, -1):
            for j in range(N):
                t = j / (N - 1)
                root = (side * 0.035 - 0.03, -0.85 + 1.4 * t, 1.0)       # along the part, front hairline -> crown
                az = math.radians(-36 + 126 * t)                         # front clumps arc over the forehead to the temples
                el = 0.14 - 0.26 * t
                end = (side * math.cos(az), math.sin(az), el)
                # alternate clumps sit slightly proud of their neighbours: dark grooves between clumps
                pts = path(root, end, r=hr + (0.012 if j % 2 else 0.0))
                hang = Vector((side * math.cos(az), math.sin(az), 0)) * 0.075      # wide silhouette
                drop = 0.50 + rnd_h.uniform(-0.05, 0.05)                         # long: down to the chest
                fwd = -0.014 if j <= 2 else 0.004                                # front clumps fall over the shoulders
                pts += [pts[-1] + hang * (k / 5) * (1 + 0.12 * k) + Vector((0, fwd * k, -drop * k / 5))
                        for k in (1, 2, 3, 4, 5)]
                # thick faceted clumps (visible edge thickness), pointed tips
                w, flat = (0.04, (2.0, 0.8)) if j == 0 else (0.058, (2.4, 0.8))
                hair_parts += hair_lock(pts, w, 0.026, seg=6, normal_from=hc, flat=flat, tip=0.15)
    elif HAIR == "strands":
        # Reference hair: dark cap, then chunky locks from a side part that run
        # over the head and hang behind to the shoulders; a swept fringe of locks
        # across the forehead and two locks framing the face to chin level.
        hc = Vector((0, 0.02, HZ + 0.01))
        hr = 0.242                                           # volume: locks sit off the head

        def on_head(d):
            d = Vector(d).normalized()
            return hc + Vector((d.x * hr * 1.04, d.y * hr * 0.98, d.z * hr))

        def path(d0, d1, steps=8):
            a0, a1 = Vector(d0).normalized(), Vector(d1).normalized()
            return [on_head(a0.slerp(a1, i / steps)) for i in range(steps + 1)]

        part = (-0.32, -0.12, 1.0)                           # side part, her right
        hair_parts = [ico((0, 0.03, HZ + 0.03), 0.222, sub=2, scale=(1.06, 1.0, 0.94),
                          cut=lambda co: co.y < -0.05 and co.z < HZ + 0.07)]
        for i in range(28):                                  # over the head, then down the back
            az = math.radians(-25 + i * (230 / 27))          # side -> back -> other side
            end = (math.cos(az), math.sin(az), -0.15)
            root_dir = (-0.30, -0.22 + 0.50 * (i / 27), 1.0)   # roots spread along a part line, not one point
            pts = path(root_dir, end)
            out = Vector((math.cos(az), math.sin(az), 0)) * 0.04
            base = pts[-1]
            pts += [base + out * (k / 4) + Vector((0, 0, -0.085 * k)) for k in (1, 2, 3, 4)]
            hair_parts += hair_lock(pts, 0.042, 0.02, normal_from=hc, flat=(2.2, 0.5))
        # Side-swept fringe: from the part, diagonally across the forehead and
        # down past her left temple (an adult swoop, not a straight-cut bang)
        for az_deg, el, w in ((-105, 0.62, 0.036), (-90, 0.50, 0.038), (-72, 0.38, 0.038),
                              (-55, 0.22, 0.036), (-40, 0.05, 0.034)):
            az = math.radians(az_deg)
            hair_parts += hair_lock(path(part, (math.cos(az), math.sin(az), el), 9), w, 0.013, normal_from=hc)
        for az_deg in (-40, -140, -30, -150):               # face-framing locks: hug the head, then fall
            az = math.radians(az_deg)
            c, sn = math.cos(az), math.sin(az)
            pts = path((c * 0.6, sn * 0.6, 0.8), (c, sn, -0.2), 6)
            out = Vector((c, sn, 0)) * 0.012
            pts += [pts[-1] + out * k + Vector((0, 0.006 * k, -0.07 * k)) for k in (1, 2, 3, 4)]
            hair_parts += hair_lock(pts, 0.038, 0.016, normal_from=hc, flat=(2.2, 0.45))
    elif HAIR == "bob":
        # Shoulder-length bob ("lob"): top cap, then a ring of chunky faceted
        # strands hanging from the crown around the sides and back, two longer
        # face-framing locks, and a big side-swept fringe across the forehead.
        hair_parts = [ico((0, 0.03, HZ + 0.04), 0.222, sub=2, scale=(1.06, 1.0, 0.92),
                          cut=lambda co: co.y < -0.05 and co.z < HZ + 0.085)]

        def strand(angle_deg, radius, length, width, tilt_out=7.0, drop=0.0):
            a = R(angle_deg)
            d = Vector((math.cos(a), math.sin(a), 0.0))
            tangent = Vector((-math.sin(a), math.cos(a), 0.0))
            rot = Matrix.Rotation(R(-tilt_out), 4, tangent) @ Matrix.Rotation(a + R(90), 4, "Z")
            centre = Vector((0, 0.03, HZ - 0.12 - drop)) + d * radius
            mtx = Matrix.Translation(centre) @ rot @ Matrix.Diagonal((width, width * 0.7, length, 1.0))

            def build(bm):
                bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mtx)
            return build

        for i in range(9):                                   # behind the ears + back only
            ang = 10 + i * 20
            hair_parts.append(strand(ang, 0.215, 0.26 + 0.015 * math.sin(i * 1.7),
                                     0.085, tilt_out=9 + 3 * math.cos(i), drop=-0.01))
        hair_parts += [ico((-0.03, -0.15, HZ + 0.118), 0.11, sub=2, scale=(1.5, 0.36, 0.52), rot=(0, 16, 0)),
                       ico((0.12, -0.125, HZ + 0.09), 0.065, sub=2, scale=(1.0, 0.45, 0.85), rot=(0, 30, 0))]
    elif HAIR == "long":
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
    hair_ob = obj("Human_Hair", hair_parts, hair, C, **hp)

    focus = empty("Human_FocusTarget", C, head, loc=(0, -0.18, 0), size=0.03)
    if GLASSES == "none":
        g = bpy.data.objects.get("Human_Glasses")
        if g:
            bpy.data.objects.remove(g, do_unlink=True)
    if STYLE == "chibi":
        # Chibi mix: oversized, smooth-shaded head and hair on the faceted body;
        # the head sits low on the collar so the neck disappears.
        head.scale = (1.08, 1.08, 1.08)            # big head, but adult (not baby) proportions
        head.location.z = HZ + 0.015
        for poly in head_mesh.data.polygons:      # smooth face; hair stays faceted like the reference
            poly.use_smooth = True
    if FACE == "dots":     # reference face: no eye whites, lids, lashes, blush or brows
        for name in ("Human_EyeWhites", "Human_Eyelids", "Human_Lashes", "Human_Blush", "Human_Eyebrows"):
            o = bpy.data.objects.get(name)
            if o:
                o.hide_render = o.hide_viewport = True
    return root, focus, mouth_keys, lid_keys


# ------------------------------ mascot -------------------------------------- #
MASCOT_COLORS = {"orange": (0.8, 0.12, 0.01), "mint": (0.45, 0.92, 0.72), "coral": (1.0, 0.50, 0.45), "yellow": (1.0, 0.90, 0.50)}


def hex_linear(h):
    """'#RRGGBB' (sRGB) -> linear RGB tuple, as Blender's colour fields expect."""
    def ch(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(ch(int(h[i:i + 2], 16)) for i in (1, 3, 5))


def hex_mat(name, hex_color, roughness, subsurface=0.0, specular=None):
    m = mat(name, hex_linear(hex_color))
    bsdf = _principled(m)
    bsdf.inputs["Roughness"].default_value = roughness
    if specular is not None:
        for n in ("Specular IOR Level", "Specular"):
            if n in bsdf.inputs:
                bsdf.inputs[n].default_value = specular
                break
    if subsurface:
        for n in ("Subsurface Weight", "Subsurface"):
            if n in bsdf.inputs:
                bsdf.inputs[n].default_value = subsurface
                break
        if "Subsurface Scale" in bsdf.inputs:       # mascot is only ~24 cm tall
            bsdf.inputs["Subsurface Scale"].default_value = 0.01
    return m


CLAUDE_WIDTH = 0.25           # metres on the desk, body width (it's wider than tall)
CLAUDE_TARGET_FACES = 220     # COLLAPSE decimate target: bold, even facets
CLAUDE_VOXEL = 0.035          # voxel remesh that fuses the cubes into one solid


def _evaluated_mesh(ob):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    return bpy.data.meshes.new_from_object(ob.evaluated_get(dg))


def build_claude_mascot(C, parent):
    """Solid, crease-free body from beveled cubes (no metaballs): torso + crest
    + four side bumps, fused by a voxel remesh, decimated to ~220 flat facets.
    Beveled cube feet, flush vertical eyes. Built in design units, scaled to
    desk size with the origin (0, 0, 0) at the bottom of the feet."""
    body_m = hex_mat("M_Claude_Body", "#D9531E", 0.85, specular=0.2)   # burnt coral
    eye_m = hex_mat("M_Claude_Eyes", "#080808", 0.9)

    # 1. Body parts: dimensions (X, Y, Z), centre, bevel width, 3 segments ----
    parts = [rbox((0, 0, 0.52), (1.15, 0.68, 0.72), 0.18, 3),          # main wide torso
             rbox((0, 0, 0.86), (0.46, 0.56, 0.32), 0.12, 3)]          # short flat crest
    for x in (-0.54, 0.54):                                            # side bumps
        for z in (0.66, 0.36):
            parts.append(rbox((x, 0, z), (0.30, 0.56, 0.26), 0.10, 3))
    me = bpy.data.meshes.new("Claude_Parts")
    bm = bmesh.new()
    for build in parts:
        build(bm)
    bm.to_mesh(me)
    bm.free()
    tmp = bpy.data.objects.new("Claude_FuseTmp", me)
    C.objects.link(tmp)

    # 2. Union via voxel remesh (fuses overlapping cubes into one solid), then
    #    COLLAPSE decimate to ~220 faces for crisp, even triangles.
    rm = tmp.modifiers.new("Fuse", "REMESH")
    rm.mode, rm.voxel_size = "VOXEL", CLAUDE_VOXEL
    if hasattr(rm, "use_smooth_shade"):
        rm.use_smooth_shade = False
    fused = _evaluated_mesh(tmp)
    tmp.modifiers.remove(rm)
    tmp.data = fused
    bpy.data.meshes.remove(me)
    dc = tmp.modifiers.new("Facets", "DECIMATE")
    dc.decimate_type = "COLLAPSE"
    tris = sum(len(p.vertices) - 2 for p in fused.polygons)
    dc.ratio = CLAUDE_TARGET_FACES / tris
    for _ in range(3):
        body_me = _evaluated_mesh(tmp)
        n = len(body_me.polygons)
        if abs(n - CLAUDE_TARGET_FACES) <= 15:
            break
        dc.ratio *= CLAUDE_TARGET_FACES / max(n, 1)
        bpy.data.meshes.remove(body_me)
    print(f"Claude mascot: {len(body_me.polygons)} faces (decimate ratio {dc.ratio:.4f})")
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.meshes.remove(fused)

    # 3. Tucked stubby feet: beveled low-poly cubes under the bottom edge
    feet_parts = [rbox((x, -0.04, 0.11), (0.28, 0.38, 0.18), 0.06, 2) for x in (-0.28, 0.28)]
    foot_bottom = 0.11 - 0.09

    # Scale to desk size (by width); origin (0, 0, 0) at the bottom of the feet
    width = max(v.co.x for v in body_me.vertices) - min(v.co.x for v in body_me.vertices)
    k = CLAUDE_WIDTH / width
    to_world = Matrix.Diagonal((k, k, k, 1.0)) @ Matrix.Translation((0, 0, -foot_bottom))
    body_me.transform(to_world)
    for p in body_me.polygons:                     # shade_flat()
        p.use_smooth = False
    body_me.materials.clear()
    body_me.materials.append(body_m)
    body_me.name = "Mascot_Body"
    body = bpy.data.objects.new("Mascot_Body", body_me)
    C.objects.link(body)
    body.parent = parent
    feet = obj("Mascot_Feet", feet_parts, body_m, C, body)
    feet.data.transform(to_world)

    # 4. Bold vertical eyes: bars 0.08 x 0.05 x 0.24 at (+/-0.18, -0.34, 0.52),
    # depth fitted to the faceted front so they sit flush.
    from mathutils.bvhtree import BVHTree
    tree = BVHTree.FromPolygons([v.co.copy() for v in body_me.vertices],
                                [tuple(p.vertices) for p in body_me.polygons])
    eye_parts = []
    ew, ed, eh = 0.08 * k, 0.05 * k, 0.24 * k
    ez = (0.52 - foot_bottom) * k
    for ex in (-0.18 * k, 0.18 * k):
        hits = [tree.ray_cast(Vector((ex + dx, -1.0, ez + dz)), Vector((0, 1, 0)))[0]
                for dx in (-ew / 2, 0, ew / 2) for dz in (-eh / 2, 0, eh / 2)]
        ys = [h.y for h in hits if h is not None] or [-0.34 * k]
        back = max(ys) + 0.002                      # tucked just inside the surface
        front = min(back - ed, min(ys) - 0.0015)    # never behind the most forward facet
        eye_parts.append(box((ex, (front + back) / 2, ez), (ew, back - front, eh)))
    eyes = obj("Mascot_Eyes", eye_parts, eye_m, C, body)
    if hasattr(eyes, "visible_shadow"):
        eyes.visible_shadow = False
    return body


def add_squash_rig(root, body):
    """root['squash']: +1 = squashed flat, -1 = stretched tall; volume-preserving,
    scaling around the body origin at the bottom of the feet."""
    root["squash"] = 0.0
    try:
        root.id_properties_ui("squash").update(min=-1.0, max=1.0,
                                               description="Squash (+) / stretch (-) about the feet")
    except Exception:
        pass
    for i in range(3):
        fc = body.driver_add("scale", i)
        v = fc.driver.variables.new()
        v.name, v.type = "s", "SINGLE_PROP"
        v.targets[0].id = root
        v.targets[0].data_path = '["squash"]'
        fc.driver.expression = "1 - 0.25 * s" if i == 2 else "1 / sqrt(1 - 0.25 * s)"


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
        body = build_claude_mascot(C, bounce)
        add_squash_rig(root, body)
        top = max(v.co.z for v in body.data.vertices)
        focus = empty("Mascot_FocusTarget", C, bounce, loc=(0, -0.09, top * 0.5), size=0.03)
        return root, focus
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
    eyes = obj("Mascot_Eyes", [box((x, eye_y, ez), eye) for x in (ex, -ex)], eye_m, C, bounce)
    if hasattr(eyes, "visible_shadow"):
        eyes.visible_shadow = False          # no dark smudge from the key light
    focus = empty("Mascot_FocusTarget", C, bounce, loc=(0, -0.08, 0.128), size=0.03)
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
    place("Cam_Mascot", (0.06, -0.95, 0.99), (0.14, -0.20, 0.86), 42, mascot_focus)


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
    if "squash" in mascot_root:                    # anticipation / stretch / landing squash
        key_prop("squash", [(147, 0.0), (150, 0.6), (152, -0.5), (154, 0.0), (157, -0.3),
                            (158, 0.6), (160, -0.2), (162, 0.0), (166, 0.5), (169, 0.0),
                            (193, 0.0), (196, 0.6), (198, -0.5), (200, 0.0), (204, 0.6), (207, 0.0)])


def add_mascot_rim_light():
    """Warm #FF8C42 area light from the mascot's upper-right-back at 45 deg, so
    each facet has a lit side and a crisp shadow side."""
    old = bpy.data.objects.get("Rim_MascotWarm")
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    ld = bpy.data.lights.get("Rim_MascotWarm") or bpy.data.lights.new("Rim_MascotWarm", "AREA")
    ld.color = hex_linear("#FF8C42")
    ld.energy = 150
    ld.size = 0.12                       # small source = crisp facet shadows
    ob = bpy.data.objects.new("Rim_MascotWarm", ld)
    coll = bpy.data.collections.get("Lighting") or bpy.context.scene.collection
    coll.objects.link(ob)
    target = Vector(MASCOT_POS) + Vector((0, 0, 0.12))
    # 45 deg elevation, coming from behind-right (+x, +y) of the mascot
    d = Vector((math.cos(R(45)), math.sin(R(45)), 0)) * math.cos(R(45))
    d.z = math.sin(R(45))
    ob.location = target + d * 0.55
    ob.rotation_euler = (target - ob.location).to_track_quat("-Z", "Y").to_euler()
    if hasattr(ob, "visible_camera"):
        ob.visible_camera = False
    # Light linking: this rim light only reaches the mascot, so the desk and
    # the character behind it don't get washed out.
    if hasattr(ob, "light_linking"):
        recv = bpy.data.collections.get("Mascot_RimReceivers") or bpy.data.collections.new("Mascot_RimReceivers")
        for o in list(recv.objects):
            recv.objects.unlink(o)
        for name in ("Mascot_Body", "Mascot_Feet", "Mascot_Eyes"):
            o = bpy.data.objects.get(name)
            if o:
                recv.objects.link(o)
        ob.light_linking.receiver_collection = recv


def add_character_key_light():
    """Warm #FF9A5C key on Maya's face from front-right (frame right), light-linked
    to her only: gives the glowing peach skin and golden jacket of the reference
    without brightening the room."""
    old = bpy.data.objects.get("Key_MayaWarm")
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    ld = bpy.data.lights.get("Key_MayaWarm") or bpy.data.lights.new("Key_MayaWarm", "AREA")
    ld.color = hex_linear("#FFB07A")
    ld.energy = 45
    ld.size = 0.45
    ob = bpy.data.objects.new("Key_MayaWarm", ld)
    (bpy.data.collections.get("Lighting") or bpy.context.scene.collection).objects.link(ob)
    head = Vector(HUMAN_POS) + Vector((0, -0.08, HZ))
    ob.location = head + Vector((0.42, -0.55, 0.30))
    ob.rotation_euler = (head - ob.location).to_track_quat("-Z", "Y").to_euler()
    if hasattr(ob, "visible_camera"):
        ob.visible_camera = False
    if hasattr(ob, "light_linking"):
        recv = bpy.data.collections.get("Maya_KeyReceivers") or bpy.data.collections.new("Maya_KeyReceivers")
        for o in list(recv.objects):
            recv.objects.unlink(o)
        for o in bpy.data.objects:
            if o.name.startswith("Human_") and o.type == "MESH" and o.name != "Human_Hair":
                recv.objects.link(o)
        ob.light_linking.receiver_collection = recv


def main():
    C = remove_old_characters()
    _, human_focus, mouth_keys, lid_keys = build_human(C)
    mascot_root, mascot_focus = build_mascot(C)
    retarget_cameras(human_focus, mascot_focus)
    add_mascot_rim_light()
    add_character_key_light()
    if DEMO_ANIMATION:
        demo_animation(mouth_keys, lid_keys, mascot_root)
    bpy.context.view_layer.update()


main()
_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if "--save" in _argv and _argv.index("--save") + 1 < len(_argv):
    bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(_argv[_argv.index("--save") + 1]))
print(f"Characters built: hair={HAIR} glasses={GLASSES} outfit={OUTFIT} "
      f"mascot={MASCOT_SHAPE}/{MASCOT_COLOR}")
