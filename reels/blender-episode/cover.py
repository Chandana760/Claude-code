"""Reel cover (grid thumbnail): a frame + dark bottom fade + series tag pill + big bold title with one accent word.
Usage: python3 cover.py <frame.jpg> "<TAG>" "<title with *accent* words>" <out.jpg> [accent hex]"""
import sys
from PIL import Image, ImageDraw, ImageFont
src, tag, title, out = sys.argv[1:5]; accent = sys.argv[5] if len(sys.argv) > 5 else '#ffc83d'
F = '/usr/share/fonts/opentype/inter/'
im = Image.open(src).convert('RGB').resize((1080, 1920)); W, H = im.size
fade = Image.new('L', (1, H)); [fade.putpixel((0, y), int(235 * max(0, (y - H * 0.52) / (H * 0.48)) ** 1.3)) for y in range(H)]
im = Image.composite(Image.new('RGB', im.size, (8, 8, 14)), im, fade.resize(im.size))
d = ImageDraw.Draw(im)
big = ImageFont.truetype(F + 'InterDisplay-Black.otf', 112); small = ImageFont.truetype(F + 'Inter-ExtraBold.otf', 30)
words = [(w.strip('*'), w.startswith('*')) for w in title.split()]
lines, cur = [], []
for w in words:                      # wrap to 880 px
    if cur and d.textlength(' '.join(x for x, _ in cur + [w]), font=big) > 880: lines.append(cur); cur = []
    cur.append(w)
lines.append(cur)
lh = 118; y = H - 150 - lh * len(lines)
tw = d.textlength(tag, font=small); d.rounded_rectangle((80, y - 70, 80 + tw + 36, y - 20), radius=10, fill=accent)
d.text((98, y - 45), tag, font=small, fill=(20, 20, 28), anchor='lm')
for ln in lines:
    x = 80
    for w, acc in ln:
        d.text((x, y), w, font=big, fill=accent if acc else 'white'); x += d.textlength(w + ' ', font=big)
    y += lh
im.save(out, quality=92); print('wrote', out)
