#!/usr/bin/env python3
"""Classe les voix par hauteur fondamentale médiane (proxy objectif de l'âge perçu).

Plus la F0 médiane d'une voix masculine est haute, plus elle sonne jeune.
Repères usuels pour une voix d'homme : ~85-115 Hz = grave/mature,
~115-135 Hz = moyenne, ~135 Hz et plus = claire/jeune.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent
CACHE = ROOT / "work" / "voices" / "previews"
SR = 16000
FMIN, FMAX = 70.0, 320.0


def fetch(name, url):
    CACHE.mkdir(parents=True, exist_ok=True)
    raw = CACHE / f"{name}.bin"
    if not raw.exists() or raw.stat().st_size == 0:
        r = subprocess.run(["curl", "-sS", "--retry", "3", "-o", str(raw), url])
        if r.returncode != 0:
            return None
    wav = CACHE / f"{name}.f32"
    if not wav.exists():
        p = subprocess.run(
            ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(raw),
             "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
            capture_output=True)
        if p.returncode != 0 or not p.stdout:
            return None
        wav.write_bytes(p.stdout)
    return np.frombuffer(wav.read_bytes(), dtype=np.float32)


def f0_median(x):
    """F0 par autocorrélation, médiane sur les trames voisées."""
    win = int(0.04 * SR)
    hop = int(0.01 * SR)
    lo, hi = int(SR / FMAX), int(SR / FMIN)
    rms_all = np.sqrt(np.mean(x ** 2)) if x.size else 0.0
    if rms_all <= 0:
        return None
    vals = []
    for s in range(0, max(0, len(x) - win), hop):
        fr = x[s:s + win].astype(np.float64)
        rms = np.sqrt(np.mean(fr ** 2))
        if rms < 0.35 * rms_all:          # trame trop faible : silence ou souffle
            continue
        fr = fr - fr.mean()
        ac = np.correlate(fr, fr, mode="full")[win - 1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        seg = ac[lo:hi]
        if seg.size == 0:
            continue
        k = int(np.argmax(seg))
        if seg[k] < 0.35:                 # pic trop mou : trame non voisée
            continue
        vals.append(SR / (lo + k))
    if len(vals) < 12:
        return None
    return float(np.median(vals))


def main():
    voices = json.loads((ROOT / "work" / "voices" / "males.json").read_text())
    rows = []
    for name, vid, url in voices:
        x = fetch(name, url)
        if x is None or x.size < SR // 2:
            print(f"  {name}: aperçu illisible", file=sys.stderr)
            continue
        f0 = f0_median(x)
        if f0 is None:
            print(f"  {name}: F0 non mesurable", file=sys.stderr)
            continue
        rows.append({"nom": name, "voice_id": vid, "f0_hz": round(f0, 1)})

    rows.sort(key=lambda r: -r["f0_hz"])
    (ROOT / "work" / "voices" / "f0.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{'voix':<12} {'F0 médiane':>11}   profil")
    print("-" * 46)
    for r in rows:
        f = r["f0_hz"]
        prof = ("claire / jeune" if f >= 135 else
                "moyenne" if f >= 115 else
                "grave / mature")
        print(f"{r['nom']:<12} {f:>8.1f} Hz   {prof}")


if __name__ == "__main__":
    main()
