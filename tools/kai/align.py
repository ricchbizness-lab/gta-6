#!/usr/bin/env python3
"""Cale un extrait de la video YouTube sur la VOD Twitch par correlation d'enveloppe audio.
usage: align.py YT_AUDIO START DUR VOD_DIR [N_SEGMENTS]
"""
import subprocess, sys
from pathlib import Path
import numpy as np

SR = 8000
HOP = 80  # 10 ms


def decode(args):
    out = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", *args,
                          "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32)


NFFT = 256
EDGES = np.unique(np.geomspace(2, NFFT // 2, 25).astype(int))


def env_stream(args, chunk_s=60):
    """Meme enveloppe que env(), calculee en flux par blocs : memoire bornee."""
    import subprocess as sp
    proc = sp.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", *args,
                     "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], stdout=sp.PIPE)
    blk = chunk_s * SR
    carry = np.zeros(0, dtype=np.float32)
    prev_last = None
    parts = []
    while True:
        raw = proc.stdout.read(blk * 4)
        if not raw:
            break
        x = np.concatenate([carry, np.frombuffer(raw, dtype=np.float32)])
        n = (len(x) - NFFT) // HOP
        if n <= 0:
            carry = x
            continue
        idx = np.arange(NFFT)[None, :] + HOP * np.arange(n)[:, None]
        fr = (x[idx] * np.hanning(NFFT).astype(np.float32))
        spec = np.abs(np.fft.rfft(fr, axis=1)).astype(np.float32) ** 2
        bands = np.stack([spec[:, a:b].sum(1) for a, b in zip(EDGES[:-1], EDGES[1:])], 1)
        logb = np.log(bands + 1e-6)
        if prev_last is not None:
            logb_full = np.vstack([prev_last[None, :], logb])
            on = np.maximum(0, np.diff(logb_full, axis=0)).sum(1)
        else:
            on = np.concatenate([[0], np.maximum(0, np.diff(logb, axis=0)).sum(1)])
        parts.append(on.astype(np.float32))
        prev_last = logb[-1]
        carry = x[n * HOP:]
    proc.wait()
    o = np.concatenate(parts) if parts else np.zeros(1, np.float32)
    return (o - o.mean()) / (o.std() + 1e-9)


def env(x):
    """Enveloppe d'attaques multi-bandes : bien plus discriminante qu'une
    simple enveloppe d'energie (la parole et le jeu ont des attaques uniques)."""
    n = (len(x) - NFFT) // HOP
    if n <= 1:
        return np.zeros(1)
    idx = np.arange(NFFT)[None, :] + HOP * np.arange(n)[:, None]
    fr = x[idx] * np.hanning(NFFT)
    spec = np.abs(np.fft.rfft(fr, axis=1)) ** 2
    bands = np.stack([spec[:, a:b].sum(1) for a, b in zip(EDGES[:-1], EDGES[1:])], 1)
    logb = np.log(bands + 1e-6)
    onset = np.maximum(0, np.diff(logb, axis=0)).sum(1)
    onset = np.concatenate([[0], onset])
    return (onset - onset.mean()) / (onset.std() + 1e-9)


def main():
    yt, start, dur, vdir = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), Path(sys.argv[4])
    nmax = int(sys.argv[5]) if len(sys.argv) > 5 else 10**9
    tpl = env(decode(["-ss", str(start), "-t", str(dur), "-i", yt]))
    names = [l for l in (vdir / "index.m3u8").read_text().splitlines() if l and not l.startswith("#")]
    segs = []
    for name in names[:nmax]:
        p = vdir / "seg" / name
        if not p.exists():
            break
        segs.append(p)
    # Les segments MPEG-TS se concatenent octet par octet ; on ne garde que l'audio
    # (les pistes timed_id3 de Twitch cassent le demuxeur concat).
    big = vdir / "joined.ts"
    with big.open("wb") as out:
        for p in segs:
            out.write(p.read_bytes())
    vod = env(decode(["-i", str(big), "-map", "0:a:0"]))
    m = len(tpl)
    if len(vod) < m:
        sys.exit("pas assez d'audio VOD")
    # correlation normalisee par FFT
    f = np.fft.rfft
    L = 1 << int(np.ceil(np.log2(len(vod) + m)))
    corr = np.fft.irfft(f(vod, L) * np.conj(f(tpl, L)), L)[:len(vod) - m + 1]
    c2 = np.cumsum(np.concatenate([[0], vod ** 2]))
    c1 = np.cumsum(np.concatenate([[0], vod]))
    var = (c2[m:] - c2[:-m]) - (c1[m:] - c1[:-m]) ** 2 / m
    ncc = corr / (np.sqrt(np.maximum(var, 1e-9)) * np.sqrt(m))
    i = int(np.argmax(ncc))
    srt = np.sort(ncc)[::-1]
    print(f"VOD couverte : {len(vod)/100/60:.1f} min | meilleur score {ncc[i]:.3f} "
          f"(2e pic hors voisinage ~{np.max(np.r_[ncc[:max(0,i-500)], ncc[i+500:]]) if len(ncc)>1000 else 0:.3f})")
    print(f"position VOD = {i/100:.2f} s  -> decalage VOD - YouTube = {i/100 - start:+.2f} s")


if __name__ == "__main__":
    main()
