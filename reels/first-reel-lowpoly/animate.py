"""
"My first reel" in the low-poly night desk studio.

Builds the set + characters from ../../blender/*.py, then keyframes the whole
episode from ../first-reel/lines.json (ElevenLabs voices: timings, shots,
acting tags and per-frame loudness envelopes):
  * camera cuts per line (maya -> Cam_Human, claude -> Cam_Mascot, wide -> Cam_Wide)
    with a slow push-in inside each shot
  * Maya: Talk_Open from her voice envelope, Smile / Blink / brows / head per acting tag,
    natural blinks, turns toward Claude while listening
  * Claude mascot: squash/stretch + wobble with its voice, hop / tilt / look-away /
    squint / excited per acting tag, idle breathing, eye blinks

Usage (bpy as a Python module, or Blender's own python); --ep picks the episode folder
(lines.json, dialogue.wav, mix.wav; default ../first-reel):
  python3 animate.py -- --ep ../idea-reel --blend episode.blend
  python3 animate.py -- --frames frames --step 2 [--start 1 --end 400] [--res 720x1280 --samples 16]
Rendering skips frames that already exist, so it can be resumed in chunks.
"""
import json
import math
import os
import random
import sys

import bpy
from mathutils import Quaternion, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "blender"))
_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
EP_DIR = os.path.abspath(_argv[_argv.index("--ep") + 1]) if "--ep" in _argv else \
    os.path.normpath(os.path.join(HERE, "..", "first-reel"))


def arg(name, default=None):
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default


SET = arg("--set", "desk")                     # "desk" (standard) | "sofa" (living room)


# ---------------------------------------------------------------- build scene
def build():
    saved = sys.argv
    sys.argv = [saved[0]]                      # keep the build scripts' own CLI flags quiet
    if SET == "sofa":
        os.environ["HAIR_FALL"] = "0.12"       # lying down: back hair tucks behind the pillow
        os.environ["HAIR_FRAME"] = "1"         # middle part, face-framing strands curving in, back tucked
    try:
        for fn in ("cozy_desk_studio.py", "desk_characters.py"):
            src = open(os.path.join(BLENDER_DIR, fn)).read()
            src = src.replace("DEMO_ANIMATION = True", "DEMO_ANIMATION = False")
            exec(compile(src, fn, "exec"), {"__name__": "__main__", "__file__": os.path.join(BLENDER_DIR, fn)})
        if SET != "desk":                     # alternate standard set, e.g. --set sofa
            fn = os.path.join(BLENDER_DIR, f"{SET}_room.py")
            exec(compile(open(fn).read(), fn, "exec"), {"__name__": "__main__", "__file__": fn})
    finally:
        sys.argv = saved


# ------------------------------------------------------------------- helpers
EP = json.load(open(os.path.join(EP_DIR, "lines.json")))
FPS = EP["fps"]
LINES = EP["lines"]
import subprocess as _sp
AUDIO_LEN = float(_sp.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                           os.path.join(EP_DIR, "mix.wav")], capture_output=True, text=True).stdout.strip())
LAST_FRAME = int(math.ceil(AUDIO_LEN * FPS))
CUT_LEAD = 0.2                                 # cut to the speaker slightly before they talk


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def env_at(t, who):
    for l in LINES:
        if l["who"] == who and l["t"] <= t < l["t"] + l["d"]:
            e = l["env"]
            return e[min(len(e) - 1, int((t - l["t"]) * FPS))]
    return 0.0


def env_s(t, who):
    d = 1.0 / FPS
    return (env_at(t - d, who) + 2 * env_at(t, who) + env_at(t + d, who)) / 4


def line_at(t):
    """Line whose shot is on screen at time t (cuts happen CUT_LEAD early)."""
    cur = LINES[0]
    for l in LINES:
        if t >= l["t"] - CUT_LEAD:
            cur = l
    return cur


def speaking(t, who):
    for l in LINES:
        if l["who"] == who and l["t"] <= t < l["t"] + l["d"]:
            return l
    return None


def last_line_of(t, who):
    """Most recent line by `who` that started at or before t (for lingering acting)."""
    best = None
    for l in LINES:
        if l["who"] == who and l["t"] <= t:
            best = l
    return best


def k(obj, path, value, frame, index=-1):
    if index >= 0:
        getattr(obj, path)[index] = value
        obj.keyframe_insert(path, index=index, frame=frame)
    else:
        setattr(obj, path, value)
        obj.keyframe_insert(path, frame=frame)


# ------------------------------------------------------------ voice analysis
LEAD_FRAMES = 1        # mouth shapes land a frame before the sound (reads as in sync)


def analyze_voice():
    """Per-frame visemes from the voices-only track (dialogue.wav).

    Returns {who: {frame: (open, wide, round)}} where
      open  = loudness, normalised per line, gated so pauses close the mouth
      wide  = share of high-frequency energy (ee / s / t sounds -> wide, flat mouth)
      round = share of low-frequency energy (oo / oh -> small round mouth)
    """
    import subprocess
    import numpy as np
    sr = 16000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(EP_DIR, "dialogue.wav"),
                          "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32)
    hop, win = sr // FPS, 1024
    window = np.hanning(win)
    freqs = np.fft.rfftfreq(win, 1.0 / sr)
    low = (freqs >= 150) & (freqs < 900)
    mid = (freqs >= 900) & (freqs < 2500)
    high = (freqs >= 2500) & (freqs < 7500)

    out = {"M": {}, "C": {}}
    for l in LINES:
        f0 = int(l["t"] * FPS)
        f1 = int((l["t"] + l["d"]) * FPS) + 2
        rows = []
        for f in range(f0, f1):
            c = int((f + 0.5) / FPS * sr)
            seg = audio[max(0, c - win // 2): c + win // 2]
            if len(seg) < win:
                seg = np.pad(seg, (0, win - len(seg)))
            spec = np.abs(np.fft.rfft(seg * window)) ** 2
            el, em, eh = spec[low].sum(), spec[mid].sum(), spec[high].sum()
            rms = float(np.sqrt(np.mean(seg ** 2)))
            tot = el + em + eh + 1e-12
            rows.append((f, rms, eh / tot, el / tot))
        peak = np.percentile([r[1] for r in rows], 92) + 1e-9
        prev = 0.0
        for f, rms, hi, lo in rows:
            o = max(0.0, min(1.0, rms / peak))
            o = 0.0 if o < 0.12 else (o - 0.12) / 0.88          # gate: pauses / m b p close fully
            o = o ** 0.8
            o = 0.6 * o + 0.4 * max(o, prev * 0.55)              # quick attack, soft release
            prev = o
            wide = max(0.0, min(1.0, (hi - 0.06) / 0.22))
            rnd = max(0.0, min(1.0, (lo - 0.86) / 0.1))
            out[l["who"]][f + 1 - LEAD_FRAMES] = (o, wide, rnd)   # frame numbers are 1-based
    return out


def add_mouth_visemes():
    """Extra mouth shape keys on the plane mouth: Talk_Wide (ee/s) and Talk_O (oo/oh)."""
    ob = bpy.data.objects["Human_Mouth"]
    kb = ob.data.shape_keys.key_blocks
    if "Talk_Wide" in kb and "Talk_O" in kb:
        return
    basis = [v.co.copy() for v in ob.data.vertices]
    mz = sum(c.z for c in basis) / len(basis)

    def make(name, fn):
        k = ob.shape_key_add(name=name, from_mix=False)
        for i, c in enumerate(basis):
            k.data[i].co = fn(c.copy())

    def wide(c):                      # stretched sideways, slightly parted
        inner = abs(c.x) < 0.015
        c.x *= 1.28
        if c.z < mz:
            c.z -= 0.009 if inner else 0.004
        elif inner:
            c.z += 0.002
        return c

    def round_o(c):                   # narrow and tall, rounded
        inner = abs(c.x) < 0.015
        c.x *= 0.5
        if c.z < mz:
            c.z -= 0.022 if inner else 0.015
        else:
            c.z += 0.006 if inner else 0.003
        return c
    make("Talk_Wide", wide)
    make("Talk_O", round_o)


def add_arm_poses():
    """Desk set: shape keys that lift her top forearm + hand off the desk.
    Arm_Chin  - hand up at her cheek/chin (thinking, listening)
    Arm_Raise - hand raised in front of her chest (gesturing while talking)
    Only the pose changes; the sleeve, hand and outfit stay exactly the same."""
    if bpy.context.scene.get("set", "desk") != "desk":
        return False
    body, hands = bpy.data.objects["Human_Body"], bpy.data.objects["Human_Hands"]
    if body.data.shape_keys and "Arm_Chin" in body.data.shape_keys.key_blocks:
        return True
    E = Vector((-0.27, -0.22, 0.87))          # elbow of the top forearm (root space)
    H = Vector((0.175, -0.345, 0.905))        # its hand
    L0, L1 = Vector((0.27, -0.21, 0.83)), Vector((-0.11, -0.30, 0.85))   # lower forearm (stays put)

    import bmesh as _bm

    def piece(ob, near, along=None):
        """Vertex indices of the loose mesh piece (one sleeve tube / one hand) at `near`."""
        bm = _bm.new(); bm.from_mesh(ob.data); bm.verts.ensure_lookup_table()
        seen, best = set(), None
        for v in bm.verts:
            if v.index in seen:
                continue
            comp, stack = [], [v]
            seen.add(v.index)
            while stack:
                x = stack.pop(); comp.append(x.index)
                for e in x.link_edges:
                    o = e.other_vert(x)
                    if o.index not in seen:
                        seen.add(o.index); stack.append(o)
            c = sum((bm.verts[i].co for i in comp), Vector()) / len(comp)
            score = (c - near).length
            if along is not None:      # the tube must run along the forearm direction
                ext = max((bm.verts[i].co - c).dot(along) for i in comp)
                score += 0.0 if ext > 0.15 else 1.0
            if best is None or score < best[0]:
                best = (score, set(comp))
        bm.free()
        return best[1]

    fore = piece(body, (E + H) / 2, (H - E).normalized())
    hand_v = piece(hands, H)

    def pose(target):
        q = (H - E).rotation_difference(target - E)
        return lambda p: E + q @ (p - E)          # rigid swing about the elbow: sleeve keeps its shape

    for ob, sel in ((body, fore), (hands, hand_v)):
        if not ob.data.shape_keys:
            ob.shape_key_add(name="Basis", from_mix=False)
        basis = [v.co.copy() for v in ob.data.vertices]
        for name, target in (("Arm_Chin", Vector((0.115, -0.27, 1.19))),
                             ("Arm_Raise", Vector((0.23, -0.50, 1.10)))):
            kb = ob.shape_key_add(name=name, from_mix=False)
            mv = pose(target)
            for i, c in enumerate(basis):
                kb.data[i].co = mv(c) if i in sel else c
    return True


def style_for_episode():
    """Reference-style tweaks: darker, smaller mouth; tighter close-up on Maya;
    shallow depth of field so the window lights turn into big bokeh."""
    m = bpy.data.materials.get("M_Char_Mouth")
    if m:
        bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = (0.07, 0.015, 0.02, 1)
    cams = {"Cam_Human": ((0.22, -0.98, 1.40), (0.45, 0.45, 1.27), 36, 1.6),   # headroom for captions
            "Cam_Mascot": ((0.06, -1.02, 0.98), (0.14, -0.20, 0.85), 45, 1.6),   # her face sits above the caption band
            "Cam_Wide": ((-0.02, -1.85, 1.16), (0.04, 0.30, 1.03), 35, 2.8)}   # tighter, desk-level, monitor in frame (reference)
    if bpy.context.scene.get("set", "desk") != "desk":
        return                                  # the alternate set placed its own cameras
    sp = os.path.join(EP_DIR, "script.py")     # an episode can frame its own shots (CAMS in script.py)
    if os.path.exists(sp):
        import importlib.util
        spec = importlib.util.spec_from_file_location("ep_cams", sp)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        cams.update(getattr(mod, "CAMS", {}))
        sky = bpy.data.materials.get("M_TwilightSky")
        stops = getattr(mod, "SKY_STOPS", None)     # (position, (r, g, b)) bottom -> top
        if sky and stops:
            ramp = next(n for n in sky.node_tree.nodes if n.type == "VALTORGB").color_ramp
            while len(ramp.elements) > 1:
                ramp.elements.remove(ramp.elements[-1])
            ramp.elements[0].position, ramp.elements[0].color = stops[0][0], (*stops[0][1], 1)
            for pos, col in stops[1:]:
                ramp.elements.new(pos).color = (*col, 1)
        if hasattr(mod, "EXPOSURE"):
            bpy.context.scene.view_settings.exposure = mod.EXPOSURE
    for name, (loc, tgt, lens, fstop) in cams.items():
        cam = bpy.data.objects[name]
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        cam.data.dof.aperture_fstop = fstop
        if "base_lens" in cam:
            del cam["base_lens"]


# ---------------------------------------------------------------- classroom board
MARKER = {"blue": (47, 95, 208), "red": (216, 58, 58), "green": (46, 158, 91), "black": (34, 34, 34)}


def classroom_board():
    """Classroom set: the whiteboard is written on line by line (marker handwriting,
    strike-throughs, little drawings, arrows, wipes) from the episode's BOARD list, and
    Claude's pointer swings to whatever was just written.
    BOARD entries: (line_index, seconds_into_line, op, ...)
      ("title", text)                       title + underline across the top
      ("write", id, text, (u, v), colour[, size])   words, u/v in 0..1 of the board
      ("strike", id)                        red line through an item
      ("draw", id, kind, (u, v), size[, colour])    kind: stick | box | circle | check
      ("arrow", id, (u0, v0), (u1, v1), colour)
      ("wipe",)                             eraser clears the board"""
    sc = bpy.context.scene
    if sc.get("set") != "classroom":
        return
    sp = os.path.join(EP_DIR, "script.py")
    events = []
    if os.path.exists(sp):
        import importlib.util
        spec = importlib.util.spec_from_file_location("ep_board", sp)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        events = list(getattr(mod, "BOARD", []))
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1400, 990
    font_path = sc.get("board_font")
    fonts = {}

    def font(size):
        if size not in fonts:
            fonts[size] = ImageFont.truetype(font_path, size)
        return fonts[size]

    # ---- timeline of states: each event becomes a few reveal steps
    steps = []                                   # (time, op, args, progress)
    for ev in events:
        line, dt, op, *args = ev
        t0 = LINES[line]["t"] + dt
        if op in ("write", "title"):
            text = args[1] if op == "write" else args[0]
            dur, n = min(1.4, 0.06 * len(text) + 0.25), 6
        elif op == "wipe":
            dur, n = 0.6, 4
        else:
            dur, n = 0.45, 4
        for k in range(1, n + 1):
            steps.append((t0 + dur * k / n, op, args, k / n))
    steps.sort(key=lambda x: x[0])

    items = {}                                   # id -> dict
    order = []

    def bbox(it):
        if it["op"] in ("write", "title"):
            f = font(it["size"])
            x0, y0, x1, y1 = f.getbbox(it["text"])
            cx, cy = it["xy"]
            if it["op"] == "title":
                return (cx - (x1 - x0) / 2, cy - (y1 - y0) / 2 - 8, cx + (x1 - x0) / 2, cy + (y1 - y0) / 2 + 8)
            return (cx, cy - (y1 - y0) / 2 - 6, cx + (x1 - x0), cy + (y1 - y0) / 2 + 6)
        if it["op"] == "draw":
            cx, cy = it["xy"]; r = it["size"]
            return (cx - r, cy - r, cx + r, cy + r)
        if it["op"] == "arrow":
            (x0, y0), (x1, y1) = it["p0"], it["p1"]
            return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        return (0, 0, 0, 0)

    def render(path, wipe_band=None):
        img = Image.new("RGB", (W, H), (246, 246, 242))
        d = ImageDraw.Draw(img)
        for iid in order:
            it = items[iid]
            p = it["p"]
            col = MARKER.get(it.get("col", "black"), (34, 34, 34))
            if it["op"] in ("write", "title"):
                f = font(it["size"])
                layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ld = ImageDraw.Draw(layer)
                anchor = "mm" if it["op"] == "title" else "lm"
                ld.text(it["xy"], it["text"], font=f, fill=(*col, 255), anchor=anchor, stroke_width=3, stroke_fill=(*col, 255))   # marker weight
                x0, y0, x1, y1 = bbox(it)
                cut = int(x0 + (x1 - x0) * min(1.0, p * 1.05))
                if p < 1:
                    layer.paste((0, 0, 0, 0), (max(0, cut), 0, W, H))
                img.paste(layer, (0, 0), layer)
                if it["op"] == "title":
                    ux = 120 + (W - 240) * min(1.0, max(0.0, p * 1.4 - 0.4))
                    if ux > 120:
                        d.line((120, y1 + 18, ux, y1 + 18), fill=(34, 34, 34), width=10)
            elif it["op"] == "draw":
                cx, cy = it["xy"]; r = it["size"]; w = 11
                if it["kind"] == "stick":
                    strokes = [("ell", (cx - r * 0.28, cy - r, cx + r * 0.28, cy - r * 0.45)),
                               ("ln", (cx, cy - r * 0.45, cx, cy + r * 0.35)),
                               ("ln", (cx - r * 0.45, cy - r * 0.15, cx + r * 0.45, cy - r * 0.15)),
                               ("ln", (cx, cy + r * 0.35, cx - r * 0.35, cy + r)),
                               ("ln", (cx, cy + r * 0.35, cx + r * 0.35, cy + r))]
                elif it["kind"] == "box":
                    strokes = [("ln", (cx - r, cy - r * 0.8, cx + r, cy - r * 0.8)), ("ln", (cx - r * 0.85, cy - r * 0.8, cx - r * 0.85, cy + r)),
                               ("ln", (cx + r * 0.85, cy - r * 0.8, cx + r * 0.85, cy + r)), ("ln", (cx - r * 0.85, cy + r, cx + r * 0.85, cy + r))]
                elif it["kind"] == "circle":
                    strokes = [("ell", (cx - r, cy - r, cx + r, cy + r))]
                else:                                       # check mark
                    strokes = [("ln", (cx - r, cy, cx - r * 0.3, cy + r * 0.7)), ("ln", (cx - r * 0.3, cy + r * 0.7, cx + r, cy - r * 0.8))]
                n = max(1, int(round(len(strokes) * p)))
                for kind, xy in strokes[:n]:
                    if kind == "ell":
                        d.ellipse(xy, outline=col, width=w)
                    else:
                        d.line(xy, fill=col, width=w)
            elif it["op"] == "arrow":
                (x0, y0), (x1, y1) = it["p0"], it["p1"]
                ex, ey = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
                d.line((x0, y0, ex, ey), fill=col, width=11)
                if p >= 1:
                    ang = math.atan2(y1 - y0, x1 - x0)
                    for da in (2.6, -2.6):
                        d.line((x1, y1, x1 + 42 * math.cos(ang + da), y1 + 42 * math.sin(ang + da)), fill=col, width=11)
            if it.get("strike", 0) > 0:
                x0, y0, x1, y1 = bbox(it)
                ym = (y0 + y1) / 2
                d.line((x0 - 8, ym, x0 - 8 + (x1 - x0 + 16) * it["strike"], ym), fill=MARKER["red"], width=12)
        if wipe_band is not None:                           # eraser sweeping across
            d.rectangle((0, 0, int(W * wipe_band), H), fill=(246, 246, 242))
        img.save(path)

    out = os.path.join(EP_DIR, "board")
    seq = os.path.join(out, "seq")
    os.makedirs(seq, exist_ok=True)
    for fn in os.listdir(seq):
        os.remove(os.path.join(seq, fn))
    states = []                                  # (time, png)
    first = os.path.join(out, "state_000.png")
    render(first)
    states.append((-1e9, first))                 # (a title with a negative time is already on the board)
    targets = []                                 # (time, (u, v)) - where the pointer goes
    for k, (t, op, args, p) in enumerate(steps):
        band = None
        if op == "title":
            it = items.setdefault("_title", {"op": "title", "text": args[0], "size": 104, "xy": (W / 2, 105), "p": 0})
            if "_title" not in order:
                order.insert(0, "_title")
            it["p"] = p
        elif op == "write":
            iid, text, uv, col, *rest = args
            if iid not in items:
                items[iid] = {"op": "write", "text": text, "size": rest[0] if rest else 96, "col": col,
                              "xy": (uv[0] * W, uv[1] * H), "p": 0}
                order.append(iid)
                targets.append((t, uv))
            items[iid]["p"] = p
        elif op == "strike":
            items[args[0]]["strike"] = p
            if p == 1.0 or len(targets) == 0 or targets[-1][1] != items[args[0]]["xy"]:
                it = items[args[0]]
                targets.append((t, (it["xy"][0] / W + 0.06, it["xy"][1] / H)))
        elif op == "draw":
            iid, kind, uv, size, *rest = args
            if iid not in items:
                items[iid] = {"op": "draw", "kind": kind, "xy": (uv[0] * W, uv[1] * H), "size": size,
                              "col": rest[0] if rest else "black", "p": 0}
                order.append(iid)
                targets.append((t, uv))
            items[iid]["p"] = p
        elif op == "arrow":
            iid, p0, p1, col = args
            if iid not in items:
                items[iid] = {"op": "arrow", "p0": (p0[0] * W, p0[1] * H), "p1": (p1[0] * W, p1[1] * H), "col": col, "p": 0}
                order.append(iid)
                targets.append((t, p1))
            items[iid]["p"] = p
        elif op == "wipe":
            band = p
            if p >= 1.0:
                items.clear(); order.clear(); band = None
        path = os.path.join(out, f"state_{k + 1:03d}.png")
        render(path, band)
        states.append((t, path))

    # one image per frame (symlinks to the state shown at that frame) -> image sequence
    si = 0
    for f in range(1, LAST_FRAME + 1):
        t = (f - 1) / FPS
        while si + 1 < len(states) and states[si + 1][0] <= t:
            si += 1
        os.symlink(os.path.abspath(states[si][1]), os.path.join(seq, f"{f:04d}.png"))
    mat = bpy.data.materials.get("M_Board_Face")
    tex = mat.node_tree.nodes.get("BoardImage")
    img = bpy.data.images.load(os.path.join(seq, "0001.png"), check_existing=False)
    img.source = "SEQUENCE"
    tex.image = img
    tex.image_user.frame_duration = LAST_FRAME
    tex.image_user.frame_start = 1
    tex.image_user.frame_offset = 0
    tex.image_user.use_auto_refresh = True

    # ---- pointer: swings to the newest item, taps while Claude talks
    ptr = bpy.data.objects.get("Claude_Pointer")
    if not ptr:
        return
    bx, by, bz, bw, bh = sc["board_geom"]
    pivot = Vector(sc["pointer_pivot"])

    def world(uv):
        return Vector((bx + (uv[0] - 0.5) * bw, by, bz + (0.5 - uv[1]) * bh))
    rest_uv = (0.25, 0.85)
    prev_q = None
    for f in range(1, LAST_FRAME + 1, 1):
        t = (f - 1) / FPS
        cur = rest_uv
        t_set, prev_uv = 0.0, rest_uv
        for tt, uv in targets:
            if tt - 0.35 <= t:                     # lead the writing a little
                prev_uv, cur, t_set = cur, uv, tt - 0.35
        k = ease((t - t_set) / 0.4)
        uv = (prev_uv[0] + (cur[0] - prev_uv[0]) * k, prev_uv[1] + (cur[1] - prev_uv[1]) * k)
        d = (world(uv) - pivot).normalized()
        q = Vector((0, 0, 1)).rotation_difference(d)
        cl = speaking(t, "C")
        if cl:                                     # little teaching taps while he talks
            side = d.cross(Vector((0, 0, 1))).normalized()
            q = Quaternion(side, 0.035 * math.sin(t * 9.0)) @ q
        ptr.rotation_quaternion = q
        ptr.keyframe_insert("rotation_quaternion", frame=f)


# ---------------------------------------------------------------- animation
SHOT_CAM = {"maya": "Cam_Human", "claude": "Cam_Mascot", "wide": "Cam_Wide", "board": "Cam_Board"}


def animate():
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, LAST_FRAME
    sc.render.fps = FPS
    try:                                         # per-frame keys: no Bezier overshoot
        bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
    except Exception:
        pass

    style_for_episode()

    # Camera cuts + slow push-in (lens +5% across each shot)
    sc.timeline_markers.clear()
    moves = {}
    sp = os.path.join(EP_DIR, "script.py")
    if os.path.exists(sp):
        import importlib.util
        spec = importlib.util.spec_from_file_location("ep_moves", sp)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        moves = {i: (a, b) for i, _cam, a, b in getattr(mod, "CAM_MOVES", [])}
    segs = []
    for i, l in enumerate(LINES):
        start = 1 if i == 0 else int(round((l["t"] - CUT_LEAD) * FPS)) + 1
        segs.append((start, l["shot"]))
    for i, (start, shot) in enumerate(segs):
        end = segs[i + 1][0] - 1 if i + 1 < len(segs) else LAST_FRAME
        cam = bpy.data.objects[SHOT_CAM[shot]]
        m = sc.timeline_markers.new(f"{i:02d}_{shot}", frame=start)
        m.camera = cam
        base = cam.get("base_lens") or cam.data.lens
        cam["base_lens"] = base
        lens0, lens1 = base, base * 1.05
        if i in moves:                            # episode-specific move (e.g. the ending pulls back)
            lens0, lens1 = moves[i]
        cam.data.lens = lens0
        cam.data.keyframe_insert("lens", frame=start)
        cam.data.lens = lens1
        cam.data.keyframe_insert("lens", frame=end)
        if i in moves:                            # hold the camera's normal lens on its other shots
            cam.data.lens = base
            cam.data.keyframe_insert("lens", frame=start - 1)
    sc.camera = bpy.data.objects[SHOT_CAM[segs[0][1]]]
    classroom_board()

    head = bpy.data.objects["Human_Head"]
    brows = bpy.data.objects["Human_Eyebrows"]
    brow_base = brows.location.copy()
    mouth = bpy.data.objects["Human_Mouth"].data.shape_keys.key_blocks
    lids = bpy.data.objects["Human_Eyelids"].data.shape_keys.key_blocks
    root = bpy.data.objects["Mascot_Root"]
    root_rz = root.rotation_euler.z
    root_loc = root.location.copy()
    eyes = bpy.data.objects["Mascot_Eyes"]

    # Dot-eye face: blinks squash the dots into lines (pupils scaled about their centre)
    pupils = bpy.data.objects["Human_Pupils"]
    dot_eyes = bpy.data.objects["Human_EyeWhites"].hide_render
    if dot_eyes:
        pm = pupils.data
        pc = sum((v.co for v in pm.vertices), Vector()) / len(pm.vertices)
        for v in pm.vertices:
            v.co -= pc
        pupils.location = pupils.location + pc

    # Re-centre the mascot eyes' origin so they squint/blink in place
    me = eyes.data
    c = sum((v.co for v in me.vertices), Vector()) / len(me.vertices)
    for v in me.vertices:
        v.co -= c
    eyes.location = c

    vis = analyze_voice()
    pose_off = tuple(bpy.context.scene.get("head_pose_offset", (0.0, 0.0, 0.0)))   # set-specific resting pose
    lid_base = float(bpy.context.scene.get("lid_base", 0.0))                       # tired: lids rest lower
    add_mouth_visemes()
    arms = add_arm_poses()
    arm_keys = [o.data.shape_keys.key_blocks for o in (bpy.data.objects['Human_Body'], bpy.data.objects['Human_Hands'])] if arms else []

    # Natural blinks for Maya (every 2.5-4.5 s) and the mascot (every 3-6 s)
    rnd = random.Random(7)
    maya_blinks, t = [], 1.5
    while t < AUDIO_LEN:
        maya_blinks.append(t)
        t += rnd.uniform(2.5, 4.5)
    mascot_blinks, t = [], 2.7
    while t < AUDIO_LEN:
        mascot_blinks.append(t)
        t += rnd.uniform(3.0, 6.0)

    def blink_amount(t, times, dur=0.17):
        for b in times:
            if b <= t < b + dur:
                x = (t - b) / dur
                return 1 - abs(2 * x - 1)
        return 0.0

    for f in range(1, LAST_FRAME + 1):
        t = (f - 1) / FPS

        # ---------------- Maya ----------------
        me_env = env_s(t, "M")
        ml = speaking(t, "M")
        last_m = last_line_of(t, "M")
        act = last_m["act"] if last_m else "flat"
        since = t - last_m["t"] if last_m else 0.0
        fade_in = ease(since / 0.35) if last_m else 0.0

        o, wd, rd = vis["M"].get(f, (0.0, 0.0, 0.0))
        talk = clamp(0.95 * o * (1 - 0.5 * wd) * (1 - 0.6 * rd))  # "ah" (subtle, like the reference)
        talk_w = clamp(0.8 * o * wd)                         # "ee" / "s"
        talk_o = clamp(0.8 * o * rd)                         # "oo" / "oh"
        me_env = o
        smile = 0.0
        lid = blink_amount(t, maya_blinks)
        brow_dz = 0.0
        hx = hy = hz = 0.0

        if act == "worried":
            brow_dz, hy, hx = 0.006, 0.10, 0.04
        elif act == "flat":
            lid = max(lid, 0.32 * fade_in)           # deadpan half-lidded
        elif act == "surprised":
            brow_dz, hx = 0.014 * fade_in, -0.07 * fade_in
            talk = clamp(talk + 0.25 * fade_in) if ml else talk
        elif act == "thinking":
            hx, hy, hz = -0.07 * fade_in, -0.14 * fade_in, 0.10 * fade_in
        elif act == "chin":                          # cheek resting on her hand
            hy, hz = 0.10 * fade_in, -0.05 * fade_in
        elif act == "gesture":
            hx = -0.03 * fade_in
        elif act == "sleepy":                        # eyes half closed, head sinking into the pillow
            lid = max(lid, 0.80 * fade_in)
            hx += 0.06 * fade_in
            last_maya = [l for l in LINES if l["who"] == "M"][-1]
            if last_m is last_maya and t > last_m["t"] + last_m["d"]:   # she drifts off: eyes close
                drift = ease((t - last_m["t"] - last_m["d"] - 0.3) / 1.4)
                lid = max(lid, 0.80 + 0.20 * drift)
                hx += 0.03 * drift
        elif act == "wink":
            smile = 0.8 * fade_in
            hy = 0.14 * fade_in
            if ml and abs(t - (ml["t"] + ml["d"] - 0.25)) < 0.12:   # playful blink at the end
                lid = 1.0
        if ml:
            hx += me_env * 0.035                     # little nods on stressed syllables
        hx += 0.018 * math.sin(t * 0.7)              # slow idle head drift
        hy += 0.03 * math.sin(t * 0.45 + 1.0)

        # While Claude talks, Maya turns toward the mascot (down and to her right)
        cl = speaking(t, "C")
        listen = 0.0
        if cl:
            listen = ease((t - cl["t"]) / 0.5)
        elif last_line_of(t, "C") and not ml:
            lc = last_line_of(t, "C")
            listen = 1 - ease((t - (lc["t"] + lc["d"])) / 0.5)
        # Reference: while Claude talks she stays still in the background
        # (no turn toward him; idle drift eases out)
        hx -= 0.018 * math.sin(t * 0.7) * listen
        hy -= 0.03 * math.sin(t * 0.45 + 1.0) * listen

        # Warm ending: she smiles at the final "Especially those."
        if t >= LINES[-1]["t"] - 0.2 and act != "sleepy":
            smile = max(smile, 0.7 * ease((t - LINES[-1]["t"] + 0.2) / 0.6))
            lid = max(lid if lid >= 0.9 else 0.0, 0.0)

        mouth["Talk_Open"].value = talk
        mouth["Talk_Open"].keyframe_insert("value", frame=f)
        mouth["Talk_Wide"].value = talk_w
        mouth["Talk_Wide"].keyframe_insert("value", frame=f)
        mouth["Talk_O"].value = talk_o
        mouth["Talk_O"].keyframe_insert("value", frame=f)
        mouth["Smile"].value = smile
        mouth["Smile"].keyframe_insert("value", frame=f)
        if arm_keys:
            # chin: hand rests at her cheek while the 'chin' line and Claude's reply play;
            # gesture: hand lifts while she talks, then settles back to the desk
            chin = 0.0
            if act == "chin" and last_m:
                end = last_m["t"] + last_m["d"]
                chin = fade_in * (1 - ease((t - end - 0.3) / 0.6)) if t > end + 0.3 else fade_in
            raise_ = 0.0
            if act == "gesture" and last_m:
                end = last_m["t"] + last_m["d"]
                raise_ = fade_in * (1 - ease((t - end) / 0.5)) if t > end else fade_in
                raise_ *= 1 + 0.08 * math.sin(t * 5.0) * (1 if ml else 0)     # small beat while speaking
            prev = last_m and LINES.index(last_m) > 0 and [l for l in LINES[:LINES.index(last_m)] if l["who"] == "M"]
            if prev and prev[-1]["act"] == "chin" and act != "chin" and since < 0.5:   # ease the hand back down
                chin = max(chin, 1 - ease(since / 0.5))
            for kb in arm_keys:
                kb["Arm_Chin"].value = clamp(chin)
                kb["Arm_Chin"].keyframe_insert("value", frame=f)
                kb["Arm_Raise"].value = clamp(raise_)
                kb["Arm_Raise"].keyframe_insert("value", frame=f)
        lid = max(lid, lid_base)
        lids["Blink"].value = clamp(lid)
        lids["Blink"].keyframe_insert("value", frame=f)
        if dot_eyes:
            pupils.scale = (1.0, 1.0, 1.0 - 0.85 * clamp(lid))
            pupils.keyframe_insert("scale", index=2, frame=f)
        brows.location = brow_base + Vector((0, 0, brow_dz))
        brows.keyframe_insert("location", index=2, frame=f)
        # resting pose like the reference: head turned a little and tipped down
        head.rotation_euler = (hx + 0.07 + pose_off[0], hy + 0.06 + pose_off[1], hz - 0.12 + pose_off[2])
        head.keyframe_insert("rotation_euler", frame=f)

        # ---------------- Claude mascot ----------------
        ce = vis["C"].get(f, (0.0, 0.0, 0.0))[0]
        cl_line = cl
        last_c = last_line_of(t, "C")
        cact = last_c["act"] if last_c else ""
        csince = t - last_c["t"] if last_c else 0.0
        hop = 0.0
        squash = 0.035 * math.sin(t * 2.2)           # gentle idle breathing
        tilt = 0.0                                   # stays upright: no talking lean
        rz = root_rz
        eye_z = 1.0

        def bump(x, a, b):                           # 0 -> 1 -> 0 between a and b
            return math.sin(math.pi * clamp((x - a) / (b - a))) if a <= x <= b else 0.0

        jx = jy = jr = 0.0
        if cl_line:
            squash += -0.10 * ce                     # tiny upright pulse on syllables
            # Reference: a slight vibration while talking (tiny frame-to-frame jitter)
            rr = random.Random(f * 7919)
            amp = 0.35 + ce
            jx = (rr.random() - 0.5) * 0.006 * amp
            jy = (rr.random() - 0.5) * 0.003 * amp
            jr = (rr.random() - 0.5) * math.radians(3.0) * amp
            # ...and a quick little hop as each line starts
            if cact not in ("bounce", "excited"):
                s0 = t - cl_line["t"]
                hop = max(hop, 0.18 * bump(s0, 0.04, 0.34))
                squash += 0.16 * bump(s0, 0.0, 0.06) + 0.18 * bump(s0, 0.34, 0.46)
        if cact in ("bounce", "excited") and last_c:
            hops = (0.0,) if cact == "bounce" else (0.0, 0.62)
            amp = 0.32 if cact == "bounce" else 0.45
            for h0 in hops:
                s = csince - h0
                squash += 0.30 * bump(s, 0.0, 0.10)              # anticipation squat
                air = bump(s, 0.10, 0.50)
                hop = max(hop, amp * air)
                squash -= 0.22 * air                              # stretch in the air
                squash += 0.32 * bump(s, 0.50, 0.66)             # landing squash
        if cact == "look-away" and last_c:
            w = ease(csince / 0.35) * (1 - ease((csince - last_c["d"] - 0.3) / 0.4))
            rz = root_rz - math.radians(25) * w      # turns away, no lean
        if cact == "squint" and last_c:
            w = ease((csince - 0.1) / 0.3) * (1 - ease((csince - last_c["d"] - 0.4) / 0.3))
            eye_z = 1 - 0.7 * w
        if cact == "tilt" and last_c:                # brief curious head-tilt, then upright
            w = ease(csince / 0.3) * (1 - ease((csince - 0.9) / 0.4))
            tilt = 0.22 * w
        eye_z *= 1 - 0.18 * ce                        # eyes flex with the voice
        eye_z *= 1 - 0.72 * blink_amount(t, mascot_blinks, 0.16)   # blink: eyes squash to small squares

        root["hop"], root["tilt"], root["squash"] = clamp(hop), clamp(tilt, -1, 1), clamp(squash, -1, 1)
        for p in ("hop", "tilt", "squash"):
            root.keyframe_insert(f'["{p}"]', frame=f)
        root.rotation_euler.z = rz + jr
        root.keyframe_insert("rotation_euler", index=2, frame=f)
        root.location = root_loc + Vector((jx, jy, 0.0))
        root.keyframe_insert("location", frame=f)
        eyes.scale = (1.0, 1.0, eye_z)
        eyes.keyframe_insert("scale", index=2, frame=f)

    # Lip sync / acting curves: linear between per-frame keys
    for ob in (bpy.data.objects["Human_Mouth"].data.shape_keys, bpy.data.objects["Human_Eyelids"].data.shape_keys,
               brows, head, root, eyes):
        ad = ob.animation_data
        if ad and ad.action:
            for fc in getattr(ad.action, "fcurves", []):
                for kp in fc.keyframe_points:
                    kp.interpolation = "LINEAR"


# ------------------------------------------------------------------ render
def setup_render(res, samples):
    sc = bpy.context.scene
    w, h = (int(x) for x in res.split("x"))
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.adaptive_threshold = 0.05
    sc.cycles.max_bounces, sc.cycles.diffuse_bounces, sc.cycles.glossy_bounces = 4, 2, 1
    sc.render.use_persistent_data = True
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 92


def render(out_dir, step, start, end):
    sc = bpy.context.scene
    os.makedirs(out_dir, exist_ok=True)
    for f in range(start, end + 1, step):
        path = os.path.join(out_dir, f"f{f:05d}.jpg")
        if os.path.exists(path):
            continue
        sc.frame_set(f)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print(f"frame {f}/{end}", flush=True)


if __name__ == "__main__":
    build()
    animate()
    blend = arg("--blend")
    if blend:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(blend))
    frames = arg("--frames")
    if frames:
        setup_render(arg("--res", "720x1280"), int(arg("--samples", "16")))
        step = int(arg("--step", "2"))
        render(os.path.abspath(frames), step, int(arg("--start", "1")), int(arg("--end", str(LAST_FRAME))))
    print("episode frames:", LAST_FRAME)
