# "Rate my prompt" — voiced episode

Desk-chat episode in the style of the reference reels: Maya and Claude talk in alternating
close-ups with shallow depth of field, real voices, lip-sync and acting.

| File | What it is |
|---|---|
| `voices.py` | The script (`SCRIPT`: speaker, line, shot, acting, pause) → Kokoro TTS voices, `dialogue.wav`, `lines.json` |
| `lines.json` | Line timings + 30 fps loudness envelopes that drive Maya's mouth and Claude's squash |
| `scene.html` | The set, characters, acting, cameras, depth of field, captions |
| `render.mjs` | Headless frame renderer → ffmpeg |
| `mix.wav` | Voices + lo-fi bed (music ducks under speech) |
| `rate-my-prompt-reel.mp4` | The finished reel |

Acting cues for Maya: `crossed`, `gesture`, `lean`. For Claude: `bounce`, `look-away`, `squint`, `excited`, `tilt`.
Shots: `maya`, `claude`, `wide`.

```bash
pip install kokoro-onnx soundfile   # plus kokoro-v1.0.int8.onnx + voices-v1.0.bin from the kokoro-onnx releases
python voices.py <folder with the model files>
npm install && node render.mjs video video.mp4
python3 gen_audio.py 30.5 && mv audio.wav music.wav   # then mix (see commit history) and mux
```

Voices: Maya = `af_heart`, Claude = `am_puck` (change `VOICE` in `voices.py`).
