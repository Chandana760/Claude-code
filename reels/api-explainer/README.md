# "What is an API?" reel

A 39-second vertical (1080×1920, 30 fps) low-poly explainer in the style of the
AI Explainer Channel character sheet: Maya (host) asks, Claude explains with the whiteboard.
Everything is code: three.js scene, Playwright frame renderer, numpy soundtrack.

| File | What it is |
|---|---|
| `scene.html` | The whole film: studio set, Maya, Claude, whiteboard drawing, script (`LINES`), shots, captions |
| `render.mjs` | Renders frames headlessly and pipes them to ffmpeg |
| `gen_audio.py` | Lo-fi music bed + caption pops → `audio.wav` |
| `api-explainer-reel.mp4` | The finished reel |
| `studio.glb` | The set and characters (pose at 4 s) for Blender: File → Import → glTF 2.0 |

## Make it again / make a new episode

```bash
npm install                                   # three.js
node render.mjs stills 1.5,10,24 stills 540x960   # quick check frames
node render.mjs video video.mp4               # full render, ~15 min on CPU
python3 gen_audio.py 39 0.3,3.2,5.6,7.8,11.8,15.6,19.4,22.8,25.4,28.6,31.6,34.4
ffmpeg -i video.mp4 -i audio.wav -c:v copy -c:a aac -b:a 192k -shortest api-explainer-reel.mp4
node render.mjs glb studio.glb                # export the set for Blender
```

To make a new topic, edit `LINES` (text, speaker, shot, expression, pointer target),
`drawBoard()` (what gets drawn and when) and `DURATION` in `scene.html`, then pass the new
line start times to `gen_audio.py`. Shots: `wide`, `mayaWide`, `board`, `boardWide`, `claude`, `maya`.
Maya expressions: `curious`, `skeptical`, `thinking`, `amused`. Claude moods: `attentive`, `excited`, `tilt`.
