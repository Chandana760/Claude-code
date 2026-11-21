"""frames (rendered on twos) + caption overlays + voices/music -> phone-friendly MP4.
Usage: python3 assemble.py <frames dir> <out.mp4>"""
import glob, json, os, subprocess, sys, tempfile
frames, out = sys.argv[1], sys.argv[2]
cap = json.load(open('captions.json'))
seq = tempfile.mkdtemp()
for i, f in enumerate(sorted(glob.glob(os.path.join(frames, 'f*.jpg')))): os.symlink(os.path.abspath(f), f'{seq}/{i:05d}.jpg')
cmd = ['ffmpeg', '-v', 'error', '-y', '-framerate', '12', '-i', f'{seq}/%05d.jpg']
for f in cap['files']: cmd += ['-i', f]
cmd += ['-i', 'mix.wav']
chain, last = [], '[0:v]fps=24'
chain.append(f'{last}[v0]'); last = '[v0]'
for k, (i, a, b) in enumerate(cap['times']):
    chain.append(f"{last}[{k + 1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{k + 1}]"); last = f'[v{k + 1}]'
cmd += ['-filter_complex', ';'.join(chain), '-map', last, '-map', f'{len(cap["files"]) + 1}:a',
        '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.0', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-movflags', '+faststart', '-shortest', out]
subprocess.run(cmd, check=True); print('wrote', out)
