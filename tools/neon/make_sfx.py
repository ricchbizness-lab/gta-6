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

# --- Transitions douces (retour du 26/11 : le whoosh bruit blanc etait trop agressif) ---------------
def sweep_band(n, centers, bw_oct=1.0, fmax=3500, win=1024):
    """Filtre passe-bande glissant par overlap-add FFT : centers[i] = frequence centrale par trame."""
    hop = win // 2; w = np.hanning(win); y = np.zeros(len(n) + win)
    fr = np.fft.rfftfreq(win, 1 / SR); nb = (len(n) - win) // hop + 1
    for k in range(nb):
        c = centers[min(len(centers) - 1, int(k / nb * len(centers)))]
        mask = np.exp(-0.5 * (np.log2(np.maximum(fr, 1) / c) / (bw_oct / 2)) ** 2) * (fr < fmax)
        seg = n[k * hop:k * hop + win] * w
        y[k * hop:k * hop + win] += np.fft.irfft(np.fft.rfft(seg) * mask, win) * w
    return y[:len(n)]

def pink(n):
    X = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR); X[1:] /= np.sqrt(f[1:]); X[0] = 0
    return np.fft.irfft(X, n)

# trans_air : souffle d'air feutre, bande qui monte puis redescend, rien au-dessus de 3,5 kHz
L = int(0.45 * SR); t = np.arange(L) / SR
cent = np.concatenate([np.geomspace(280, 1600, 60), np.geomspace(1600, 450, 60)])
env = np.where(t < 0.2, (t / 0.2) ** 2, np.exp(-(t - 0.2) * 14))
save(out / "trans_air.wav", sweep_band(pink(L), cent, 1.2) * env)

# trans_synth : nappe tonale (quinte la/mi, legere montee) + petit sub feutre a la fin, sans bruit
L = int(0.5 * SR); t = np.arange(L) / SR
rise = 1 + 0.06 * (t / t[-1])
pad = sum(a * np.sin(2 * np.pi * np.cumsum(f0 * rise) / SR) for f0, a in [(220, 1), (330, .7), (440, .35), (221.5, .6)])
pad *= np.where(t < 0.32, (t / 0.32) ** 2.5, np.exp(-(t - 0.32) * 22))
ts = np.clip(t - 0.3, 0, None); sub = np.sin(2 * np.pi * 58 * ts) * np.exp(-ts * 16) * (t >= 0.3) * 1.6
save(out / "trans_synth.wav", pad * 0.5 + sub)
print("sfx ->", out, sorted(p.name for p in out.glob("*.wav")))
