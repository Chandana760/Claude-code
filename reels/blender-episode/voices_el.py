"""Voice the script with the user's ElevenLabs voices (API key injected by the network proxy),
lay the lines out on a timeline, write dialogue.wav + lines.json (timings + 24 fps mouth envelopes)."""
import json, os, subprocess, urllib.request
import numpy as np

VOICES = {'M': 'dzZghL9aPTcCifX82myZ', 'C': 'K6tqiJ0lVwyTVpsyAgQq'}
FPS = 24
# who, text, shot, acting, pause-before (s)
SCRIPT = [
  ('M', 'Claude. Rate my prompt. Honestly.', 'maya', 'crossed', 0.5),
  ('C', 'Ten out of ten.', 'claude', 'bounce', 0.45),
  ('M', "I haven't sent it yet.", 'maya', 'crossed', 0.5),
  ('C', '...Based on vibes. Ten out of ten.', 'claude', 'look-away', 0.7),
  ('M', 'It says: "make it good."', 'wide', 'gesture', 0.55),
  ('C', "That's... a choice.", 'claude', 'squint', 0.8),
  ('M', 'You said ten!', 'maya', 'lean', 0.3),
  ('C', 'Make what good? For who? How long?', 'claude', 'bounce', 0.4),
  ('M', '...A birthday message. For my mum. Short.', 'maya', 'gesture', 0.7),
  ('C', "Now that's a prompt.", 'claude', 'excited', 0.5),
  ('M', 'So it was bad.', 'maya', 'crossed', 0.6),
  ('C', 'It was a start. Every good one starts there.', 'claude', 'tilt', 0.5),
  ('M', '...Okay. Write it.', 'wide', 'crossed', 0.8),
  ('C', "Already did. She'll cry.", 'claude', 'bounce', 0.45),
  ('M', 'Happy crying?', 'maya', 'lean', 0.5),
  ('C', '...Mostly.', 'claude', 'look-away', 0.9),
]
SR = 44100
os.makedirs('vo', exist_ok=True)

def tts(i, who, text):
    path = f'vo/{i:02d}_{who}.mp3'
    if not os.path.exists(path):
        body = json.dumps({'text': text, 'model_id': 'eleven_multilingual_v2',
                           'voice_settings': {'stability': 0.45, 'similarity_boost': 0.8, 'style': 0.25, 'use_speaker_boost': True}}).encode()
        req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICES[who]}?output_format=mp3_44100_128',
                                     data=body, headers={'xi-api-key': 'proxy-injected', 'Content-Type': 'application/json'})
        open(path, 'wb').write(urllib.request.urlopen(req).read())
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)

t = 0.4; clips = []; lines = []
for i, (who, text, shot, act, pause) in enumerate(SCRIPT):
    a = tts(i, who, text)
    nz = np.where(np.abs(a) > 0.012)[0]
    a = a[max(0, nz[0] - 800): nz[-1] + 2000]
    t += pause; d = len(a) / SR
    hop = SR // FPS
    env = np.array([np.sqrt(np.mean(a[k:k + hop] ** 2)) for k in range(0, len(a), hop)])
    env = np.clip(env / (env.max() or 1) * 1.25, 0, 1)
    lines.append({'t': round(t, 3), 'd': round(d, 3), 'who': who, 'text': text, 'shot': shot, 'act': act, 'env': [round(float(e), 3) for e in env]})
    clips.append((t, a)); t += d
total = round(t + 1.6, 2)
mix = np.zeros(int(total * SR) + SR, np.float32)
for st, a in clips: k = int(st * SR); mix[k:k + len(a)] += a
mix = mix / max(1e-6, np.abs(mix).max()) * 0.9
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', 'dialogue.wav'], input=mix.tobytes())
json.dump({'duration': total, 'fps': FPS, 'lines': lines}, open('lines.json', 'w'))
for l in lines: print(f"{l['t']:6.2f} {l['d']:5.2f} {l['who']} {l['text']}")
print('total', total)
