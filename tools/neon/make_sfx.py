#!/usr/bin/env python3
"""Bruitages du format neon, synthetises (aucun son sous droits, aucune IA) : pop, impact, whoosh."""
import wave, sys
from pathlib import Path
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def save(path, x):
    x = np.clip(x / (np.abs(x).max() + 1e-9) * 0.89, -1, 1)
    st = (np.stack([x, x], 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())


def lowpass(x, a):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc); y[i] = acc
    return y


out = Path(sys.argv[1] if len(sys.argv) > 1 else "remotion/public/neon/sfx")
out.mkdir(parents=True, exist_ok=True)

t = np.arange(int(0.12 * SR)) / SR                     # pop : sinus glissant 700->1300 Hz, decroissance rapide
f = 700 + 600 * (t / t[-1])
save(out / "pop.wav", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 32) * np.minimum(1, t / 0.003))

t = np.arange(int(0.5 * SR)) / SR                      # impact : basse 55 Hz + bruit grave
boom = np.sin(2 * np.pi * (55 + 40 * np.exp(-t * 18)) * t) * np.exp(-t * 6.5)
noise = lowpass(rng.standard_normal(len(t)), 0.05) * np.exp(-t * 14) * 3
save(out / "impact.wav", boom + noise)

t = np.arange(int(0.5 * SR)) / SR                      # whoosh : bruit filtre, enveloppe en cloche
env = np.sin(np.pi * np.clip(t / 0.5, 0, 1)) ** 2
n = rng.standard_normal(len(t))
save(out / "whoosh.wav", (n - lowpass(n, 0.06)) * env)
print("sfx ->", out, sorted(p.name for p in out.glob("*.wav")))
