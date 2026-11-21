# Blender episode — "Rate my prompt"

Maya and Claude built and animated entirely in Blender (Python), voiced with your ElevenLabs voices.

| File | What it is |
|---|---|
| `voices_el.py` | Script + ElevenLabs TTS (Maya `dzZghL9aPTcCifX82myZ`, Claude `K6tqiJ0lVwyTVpsyAgQq`) → `vo/`, `dialogue.wav`, `lines.json` |
| `build.py` | Builds the set, Maya, Claude, lights and cameras, keyframes every frame from `lines.json`, renders |
| `episode.blend` | The animated scene — open it in your Blender and render on your GPU (Cycles) |
| `rate-my-prompt-blender.mp4` | The finished reel |

Open `episode.blend` in Blender 4.2+, add `dialogue.wav` in the Video Sequencer at frame 1 for sound,
then Render → Render Animation. On a GPU set Cycles to 64–128 samples for the cleanest result.

```bash
python voices_el.py                       # needs an ElevenLabs key (the cloud session injects it)
pip install bpy==4.2.0                    # Python 3.11
python build.py -- --save episode.blend --render frames --res 720x1280 --samples 10
```

Edit `SCRIPT` in `voices_el.py` for a new episode (speaker, line, shot `maya|claude|wide`,
acting `crossed|gesture|lean` for Maya, `bounce|look-away|squint|excited|tilt` for Claude).
