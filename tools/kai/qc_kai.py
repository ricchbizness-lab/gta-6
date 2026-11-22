#!/usr/bin/env python3
"""Controle qualite des clips Kai Cenat : format, duree, loudness, crete, frames temoins."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import qc  # noqa: E402

qc.OUT = Path("out/kai")
qc.QC = Path("work/kai/qc")
ids = [m["id"].replace("kai-", "") for m in json.loads(Path("remotion/public/kai-meta.json").read_text())]
problems = []
for cid in ids:
    f = qc.OUT / f"{cid}.mp4"
    if not f.exists():
        problems.append(f"{cid}: manquant"); continue
    m = qc.probe(f)
    v = next(s for s in m["streams"] if s["codec_type"] == "video")
    dur = float(m["format"]["duration"])
    lufs, peak = qc.loudness(f)
    w, h = int(v["width"]), int(v["height"])
    if (w, h) != (1080, 1920): problems.append(f"{cid}: {w}x{h}")
    if not 15 <= dur <= 60: problems.append(f"{cid}: duree {dur:.1f}s")
    if lufs is None or abs(lufs + 14) > 1: problems.append(f"{cid}: {lufs} LUFS")
    if peak is not None and peak > -0.5: problems.append(f"{cid}: crete {peak}")
    qc.frames(f, cid, dur)
    print(f"{cid}  {dur:5.1f}s  {w}x{h}  {lufs} LUFS  crete {peak} dBFS  {f.stat().st_size/1e6:.1f} Mo")
print("\n" + ("PROBLEMES :\n  - " + "\n  - ".join(problems) if problems else "Aucun probleme automatique."))
