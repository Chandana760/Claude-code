"""Cut the character art out of the master sheet crops for the Remotion reel -> public/chars/*.png"""
from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage as nd
C = 'reels/characters/'
def up(im, k): return im.resize((im.width * k, im.height * k), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=2))
def cut(im, bg, tol, feather=2.5):
    a = np.asarray(im.convert('RGB')).astype(float); d = np.sqrt(((a - np.array(bg)) ** 2).sum(-1))
    fg = nd.binary_opening(d > tol, iterations=2)
    lab, n = nd.label(fg); sizes = nd.sum(fg, lab, range(1, n + 1)); keep = lab == (np.argmax(sizes) + 1)  # biggest blob only
    keep = nd.binary_fill_holes(nd.binary_closing(keep, iterations=6))                                      # fill dark-hair holes
    m = Image.fromarray((keep * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(feather))
    out = im.convert('RGBA'); out.putalpha(m); return out
names = ['talk', 'surprised', 'thinking', 'happy', 'worried', 'flat', 'laugh', 'wink']
for i, n in enumerate(names):
    im = Image.open(f'{C}expr/e{i}.png').convert('RGB'); w, h = im.size
    cut(up(im.crop((5, 0, w - 2, int(h * 0.9))), 5), (34, 29, 36), 30).save(f'public/chars/maya_{n}.png')
# Claude: find each figure in the turnaround by colour saturation (the floor shadow is greyish, so it drops out)
cl = Image.open(f'{C}claude_turnaround.jpg').convert('RGB')
big = up(cl, 3); A = np.asarray(big.convert('HSV')).astype(float)
fg = nd.binary_opening(A[..., 1] > 110, iterations=2)
fg = nd.binary_fill_holes(nd.binary_closing(fg, iterations=4))
lab, n = nd.label(fg); objs = sorted(nd.find_objects(lab), key=lambda sl: sl[1].start)
objs = [o for o in objs if (o[0].stop - o[0].start) > big.height * 0.4]
for j, name in [(0, 'front'), (1, 'three_quarter')]:
    sl = objs[j]; k = lab[sl] == lab[sl][lab[sl] > 0][0]
    k = nd.binary_fill_holes(lab[sl] > 0)
    hsv = A[sl]; k &= ~((hsv[..., 2] > 170) & (hsv[..., 1] < 90))   # drop the pale floor showing between the feet
    m = Image.fromarray((k * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.5))
    out = big.crop((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)).convert('RGBA'); out.putalpha(m)
    out.save(f'public/chars/claude_{name}.png')
for s in ['scene_desk', 'scene_desk2', 'scene_whiteboard', 'scene_sofa']:
    Image.open(f'{C}{s}.jpg').save(f'public/chars/{s}.jpg', quality=95)
