"""Caption pills (reference style) as transparent PNGs + the ffmpeg overlay filter that times them."""
import json, os
from PIL import Image, ImageDraw, ImageFont
EP = json.load(open('lines.json')); W, H = 720, 1280
FONT = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 26)
os.makedirs('captions', exist_ok=True)
def wrap(d, text, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=FONT) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    return lines + [cur]
filt, inputs = [], []
for i, l in enumerate(EP['lines']):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    lines = wrap(d, l['text'], 400); lh = 33
    tw = max(d.textlength(x, font=FONT) for x in lines); pw, ph = tw + 36, lh * len(lines) + 20
    x0, y0 = (W - pw) / 2, 150
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=12, fill=(28, 28, 38, 190))
    for k, x in enumerate(lines): d.text((W / 2, y0 + 10 + lh * k + lh / 2), x, font=FONT, fill='white', anchor='mm')
    path = f'captions/{i:02d}.png'; img.save(path); inputs.append(path)
    a, b = l['t'] - 0.05, l['t'] + l['d'] + 0.2
    filt.append((i, a, b))
open('captions.json', 'w').write(json.dumps({'files': inputs, 'times': filt}))
print(len(inputs), 'captions')
