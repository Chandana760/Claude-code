"""Soft, click-free music bed: gentle electric-piano chords + bass only.
No drums, no hi-hats, no vinyl crackle, no caption pops (like the reference reel).
Usage: python3 soft_music.py <duration_s>   -> writes music_soft.wav (48 kHz stereo)"""
import sys
import wave

import numpy as np

SR = 48000
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
N = int(SR * DUR)
L = np.zeros(N)
R = np.zeros(N)


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    j = min(N, i + len(sig))
    if i >= N or j <= i:
        return
    s = sig[: j - i] * gain
    L[i:j] += s * (1 - pan) * 0.707
    R[i:j] += s * (1 + pan) * 0.707


def keys(freq, dur):
    """Soft electric-piano tone with a slow attack (no percussive click)."""
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 0.06) * np.exp(-t * 0.9)
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.0 * t)
    s = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 3)
    return s * env * trem


BPM = 72
bar = 4 * 60 / BPM
chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]  # Fmaj7 Em7 Dm7 Cmaj7
t0, b = 0.0, 0
while t0 < DUR:
    ch = chords[b % 4]
    for k, m in enumerate(ch):
        add(keys(midi(m), bar + 1.5), t0 + k * 0.05, pan=(k - 1.5) * 0.25, gain=0.08)
    add(keys(midi(ch[0] - 12), bar + 1.0), t0, gain=0.10)
    t0 += bar
    b += 1

fade = np.ones(N)
fi, fo = int(SR * 1.0), int(SR * 2.0)
fade[:fi] = np.linspace(0, 1, fi)
fade[-fo:] = np.linspace(1, 0, fo)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L /= peak / 0.8
R /= peak / 0.8
data = (np.stack([L, R], 1) * 32767).astype("<i2")
with wave.open("music_soft.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(data.tobytes())
print("wrote music_soft.wav", DUR, "s")
