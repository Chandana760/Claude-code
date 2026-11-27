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
from mathutils import Vector

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
    for name, (loc, tgt, lens, fstop) in cams.items():
        cam = bpy.data.objects[name]
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = lens
        cam.data.dof.aperture_fstop = fstop
        if "base_lens" in cam:
            del cam["base_lens"]


# ---------------------------------------------------------------- animation
SHOT_CAM = {"maya": "Cam_Human", "claude": "Cam_Mascot", "wide": "Cam_Wide"}


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
        cam.data.lens = base
        cam.data.keyframe_insert("lens", frame=start)
        cam.data.lens = base * 1.05
        cam.data.keyframe_insert("lens", frame=end)
    sc.camera = bpy.data.objects[SHOT_CAM[segs[0][1]]]

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
            chin = fade_in if act == "chin" else 0.0
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
