"""Lo-fi music bed + caption pops for the reel. Writes audio.wav (48 kHz stereo).
Usage: python3 gen_audio.py [duration] [comma-separated caption times]"""
import sys, wave
import numpy as np

SR = 48000
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 39.0
POPS = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else []
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def midi(m): return 440 * 2 ** ((m - 69) / 12)

def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR); j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[: j - i] * gain
    L[i:j] += s * (1 - pan) * 0.5 ** 0.5 * 1.2
    R[i:j] += s * (1 + pan) * 0.5 ** 0.5 * 1.2

def keys(freq, dur):  # soft electric-piano tone
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 0.01) * np.exp(-t * 1.6)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
    s = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 4) + 0.1 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t * 7)
    return s * env * trem

def kick(dur=0.35):
    t = np.arange(int(SR * dur)) / SR
    f = 50 + 70 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

def hat(dur=0.05):
    t = np.arange(int(SR * dur)) / SR
    n = rng.standard_normal(len(t)); n = np.diff(n, prepend=0)
    return n * np.exp(-t * 80) * 0.25

def snare(dur=0.2):
    t = np.arange(int(SR * dur)) / SR
    n = rng.standard_normal(len(t))
    return (n * 0.5 + np.sin(2 * np.pi * 190 * t)) * np.exp(-t * 22) * 0.5

def pop(freq=900):
    t = np.arange(int(SR * 0.09)) / SR
    f = freq * (1 + 0.6 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)

BPM = 78; beat = 60 / BPM; bar = 4 * beat
chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]  # Fmaj7 Em7 Dm7 Cmaj7
t0 = 0.0; b = 0
while t0 < DUR:
    ch = chords[b % 4]
    for k, m in enumerate(ch):                      # rolled chord
        add(keys(midi(m), bar + 1.0), t0 + k * 0.03, pan=(k - 1.5) * 0.25, gain=0.09)
    add(keys(midi(ch[0] - 12), bar), t0, gain=0.12)  # bass
    mel = [ch[3] + 12, ch[2] + 12, ch[1] + 12, ch[2] + 12]
    for k in range(4):
        if (b + k) % 3 != 2:
            add(keys(midi(mel[k]), beat * 1.5), t0 + k * beat + beat * 0.5, pan=0.3, gain=0.04)
    if t0 > bar * 0.99:  # drums come in after the first bar
        for k in range(4):
            tb = t0 + k * beat
            if k in (0, 2): add(kick(), tb, gain=0.28)
            if k in (1, 3): add(snare(), tb + 0.01, gain=0.10)
            for h in (0, 0.55):  # swung hats
                add(hat(), tb + h * beat, pan=0.4, gain=0.6)
    t0 += bar; b += 1

# vinyl crackle + hiss
crack = np.zeros(N)
idx = rng.integers(0, N, int(DUR * 9)); crack[idx] = rng.standard_normal(len(idx)) * 0.25
hiss = np.convolve(rng.standard_normal(N), np.ones(8) / 8, mode='same') * 0.006
L += crack + hiss; R += np.roll(crack, 37) + hiss

# warm low-pass on the music bed
def lp(x, a=0.22):
    y = np.empty_like(x); acc = 0.0
    for i in range(0, len(x), 4096):  # chunked one-pole filter
        seg = x[i:i + 4096]; out = np.empty_like(seg)
        for k, v in enumerate(seg): acc += a * (v - acc); out[k] = acc
        y[i:i + 4096] = out
    return y
L = lp(L); R = lp(R)

for p in POPS:  # caption pops stay bright
    add(pop(880 + (hash(p) % 5) * 60), p, gain=0.14)

fade = np.ones(N); fi = int(SR * 0.6); fo = int(SR * 1.6)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
L *= fade; R *= fade
peak = max(np.abs(L).max(), np.abs(R).max()); L /= peak / 0.8; R /= peak / 0.8
data = (np.stack([L, R], 1) * 32767).astype('<i2')
with wave.open('audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
print('wrote audio.wav', DUR, 's')
