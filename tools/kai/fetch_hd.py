#!/usr/bin/env python3
"""Reconstitue chaque clip en HD depuis la VOD Twitch : telecharge les segments utiles,
coupe chaque morceau a la frame pres, puis les enchaine. Sortie : clips/hd/<id>.mp4 (1920x1080, 30 fps)."""
import json, subprocess, sys
from pathlib import Path

HD = Path("work/kai/hd")
OUT = Path("clips/hd"); OUT.mkdir(parents=True, exist_ok=True)
SEG = HD / "seg"; SEG.mkdir(exist_ok=True)

lines = (HD / "index.m3u8").read_text().splitlines()
base = (HD / "m3u8_url.txt").read_text().strip().rsplit("/", 1)[0]
segs, t, dur = [], 0.0, None
for l in lines:
    if l.startswith("#EXTINF:"):
        dur = float(l.split(":")[1].split(",")[0])
    elif l and not l.startswith("#"):
        segs.append((l, t, dur)); t += dur


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"echec : {' '.join(map(str, cmd))[:200]}\n{r.stderr[-800:]}")


def fetch(i):
    name = segs[i][0]
    p = SEG / name
    if not p.exists() or p.stat().st_size == 0:
        run(["curl", "-sS", "--retry", "3", "-o", str(p), f"{base}/{name}"])
    return p


def piece(clip_id, k, a, b):
    i0 = max(i for i, s in enumerate(segs) if s[1] <= a)
    i1 = max(i for i, s in enumerate(segs) if s[1] <= b)
    raw = HD / f"{clip_id}_p{k}.ts"
    with raw.open("wb") as f:
        for i in range(i0, i1 + 1):
            f.write(fetch(i).read_bytes())
    dst = HD / f"{clip_id}_p{k}.mp4"
    run(["ffmpeg", "-y", "-nostdin", "-i", str(raw), "-ss", f"{a - segs[i0][1]:.3f}",
         "-t", f"{b - a:.3f}", "-map", "0:v:0", "-map", "0:a:0", "-r", "30",
         "-c:v", "libx264", "-crf", "16", "-preset", "veryfast",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(dst)])
    raw.unlink()
    return dst


clips = json.loads(Path(sys.argv[1]).read_text())
for c in clips:
    parts = [piece(c["id"], k, a, b) for k, (a, b) in enumerate(c["source_hd"]["morceaux"])]
    out = OUT / f"{c['id']}.mp4"
    if len(parts) == 1:
        parts[0].replace(out)
    else:
        lst = HD / f"{c['id']}_list.txt"
        lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
        run(["ffmpeg", "-y", "-nostdin", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
        for p in parts: p.unlink()
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                        "default=nw=1:nk=1", str(out)], capture_output=True, text=True).stdout.strip()
    print(f"{c['id']}: {len(parts)} morceau(x) -> {out} ({float(d):.1f}s)", flush=True)
