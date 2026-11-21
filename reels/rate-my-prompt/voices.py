"""Voice every line with Kokoro TTS, lay them out on a timeline, and write
dialogue.wav plus lines.json (timings + 30 fps mouth envelopes for lip-sync).
Usage: python voices.py <kokoro dir>"""
import json, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

K = sys.argv[1] if len(sys.argv) > 1 else 'kokoro'
kok = Kokoro(f'{K}/kokoro-v1.0.int8.onnx', f'{K}/voices-v1.0.bin')
VOICE = {'M': ('af_heart', 1.0), 'C': ('am_puck', 1.02)}
# who, text, shot, acting, pause-before (s)
SCRIPT = [
  ('M', 'Claude. Rate my prompt. Honestly.', 'maya', 'crossed', 0.5),
  ('C', 'Ten out of ten.', 'claude', 'bounce', 0.35),
  ('M', "I haven't sent it yet.", 'maya', 'crossed', 0.45),
  ('C', '...Based on vibes. Ten out of ten.', 'claude', 'look-away', 0.6),
  ('M', 'It says: "make it good."', 'wide', 'gesture', 0.5),
  ('C', "That's... a choice.", 'claude', 'squint', 0.7),
  ('M', 'You said ten!', 'maya', 'lean', 0.25),
  ('C', 'Make what good? For who? How long?', 'claude', 'bounce', 0.35),
  ('M', '...A birthday message. For my mum. Short.', 'maya', 'gesture', 0.6),
  ('C', "Now that's a prompt.", 'claude', 'excited', 0.4),
  ('M', 'So it was bad.', 'maya', 'crossed', 0.5),
  ('C', 'It was a start. Every good one starts there.', 'claude', 'tilt', 0.45),
  ('M', '...Okay. Write it.', 'wide', 'crossed', 0.7),
  ('C', "Already did. She'll cry.", 'claude', 'bounce', 0.4),
  ('M', 'Happy crying?', 'maya', 'lean', 0.45),
  ('C', '...Mostly.', 'claude', 'look-away', 0.8),
]
SR = 24000
t = 0.4; clips = []; lines = []
for who, text, shot, act, pause in SCRIPT:
    t += pause
    voice, speed = VOICE[who]
    audio, sr = kok.create(text.replace('...', ''), voice=voice, speed=speed, lang='en-us')
    assert sr == SR
    # trim silence at the ends
    a = np.abs(audio); nz = np.where(a > 0.01)[0]
    audio = audio[max(0, nz[0] - 600): nz[-1] + 1200]
    d = len(audio) / SR
    hop = SR // 30
    env = [float(np.sqrt(np.mean(audio[i:i + hop] ** 2))) for i in range(0, len(audio), hop)]
    m = max(env) or 1
    lines.append({'t': round(t, 3), 'd': round(d, 3), 'who': who, 'text': text, 'shot': shot, 'act': act,
                  'env': [round(min(1, e / m * 1.2), 3) for e in env]})
    clips.append((t, audio)); t += d
total = t + 1.6
mix = np.zeros(int(total * SR) + SR)
for st, a in clips: i = int(st * SR); mix[i:i + len(a)] += a
sf.write('dialogue.wav', mix / max(1e-6, np.abs(mix).max()) * 0.9, SR)
json.dump({'duration': round(total, 2), 'lines': lines}, open('lines.json', 'w'))
for l in lines: print(f"{l['t']:6.2f} {l['d']:5.2f} {l['who']} {l['text']}")
print('total', round(total, 2))
