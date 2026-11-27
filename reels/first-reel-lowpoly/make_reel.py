"""Caption pills + frames (rendered on twos) + voices/music -> 1080x1920 phone-ready MP4.

Usage: python3 make_reel.py [frames_dir] [out.mp4] [episode_dir]
Reads ../first-reel/lines.json (caption text + timing) and ../first-reel/mix.wav (voices + music).
"""
import glob
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
EP_DIR = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else os.path.normpath(os.path.join(HERE, "..", "first-reel"))
FRAMES = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "frames")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "first-reel-lowpoly.mp4")
W, H = 1080, 1920
CAP_Y = int(os.environ.get("CAP_Y", "290"))
FONT = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 36)

lines = json.load(open(os.path.join(EP_DIR, "lines.json")))["lines"]
cap_dir = os.path.join(EP_DIR, "captions")
os.makedirs(cap_dir, exist_ok=True)


def wrap(d, text, maxw):
    words, out, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=FONT) > maxw and cur:
            out.append(cur)
            cur = w
        else:
            cur = t
    return out + [cur]


caps = []
for i, l in enumerate(lines):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rows = wrap(d, l["text"], 620)
    lh = 50
    tw = max(d.textlength(r, font=FONT) for r in rows)
    pw, ph = tw + 56, lh * len(rows) + 30
    # Instagram-safe: below the Reels header and inside the 3:4 profile-grid crop
    # (the grid cuts 240 px off the top of a 1080x1920 reel)
    x0, y0 = (W - pw) / 2, CAP_Y
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=18, fill=(28, 28, 38, 190))
    for k, r in enumerate(rows):
        d.text((W / 2, y0 + 15 + lh * k + lh / 2), r, font=FONT, fill="white", anchor="mm")
    path = os.path.join(cap_dir, f"{i:02d}.png")
    img.save(path)
    caps.append((path, l["t"] - 0.05, l["t"] + l["d"] + 0.2))

seq = tempfile.mkdtemp()
frames = sorted(glob.glob(os.path.join(FRAMES, "f*.jpg")))
for i, f in enumerate(frames):
    os.symlink(os.path.abspath(f), f"{seq}/{i:05d}.jpg")

nums = [int(os.path.basename(f)[1:6]) for f in frames]
step = (nums[1] - nums[0]) if len(nums) > 1 else 2          # rendered on ones (1) or twos (2)
cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(24 // step), "-i", f"{seq}/%05d.jpg"]
for p, _, _ in caps:
    cmd += ["-i", p]
cmd += ["-i", os.path.join(EP_DIR, "mix.wav")]
chain = [f"[0:v]fps=24,scale={W}:{H}:flags=lanczos[v0]"]
last = "[v0]"
for k, (_, a, b) in enumerate(caps):
    chain.append(f"{last}[{k + 1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{k + 1}]")
    last = f"[v{k + 1}]"
cmd += ["-filter_complex", ";".join(chain), "-map", last, "-map", f"{len(caps) + 1}:a",
        "-c:v", "libx264", "-profile:v", "high", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", "-shortest", OUT]
subprocess.run(cmd, check=True)
print(f"wrote {OUT} from {len(frames)} frames")
