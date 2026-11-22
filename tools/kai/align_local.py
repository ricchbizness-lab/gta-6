#!/usr/bin/env python3
"""Calage local : fenetre VOD contrainte, plusieurs gabarits de 6 s dans le clip."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from align import decode, env  # noqa
from align_batch import ncc_search  # noqa

FPS = 100
vod = np.load(sorted(Path("work/kai/vod47").glob("env_*.npy"))[-1])
YT = "input/kai_run.mp4"
jobs = {  # id: (debut, fin, fenetre VOD min, max)
    "k06": (5305.0, 5337.3, 7400, 7650),
    "k08": (5769.6, 5815.0, 7950, 8200),
    "k09": (5909.7, 5929.6, 8100, 8300),
    "k10": (7051.0, 7092.7, 9750, 9900),
    "k12": (7153.8, 7178.7, 10050, 10180),
}
res = {}
for k, (a, b, lo, hi) in jobs.items():
    seg = vod[int(lo * FPS):int(hi * FPS)]
    offs = []
    t = a
    while t + 6 <= b + 0.01:
        tpl = env(decode(["-ss", str(t), "-t", "6", "-i", YT]))
        pos, sc, sc2 = ncc_search(seg, tpl)
        offs.append((round(t, 1), round(lo + pos - t, 2), round(sc, 2), round(sc2, 2)))
        t += 4
    good = [o for o in offs if o[2] > 0.45 and o[2] > 1.5 * o[3]]
    print(f"{k}: " + " | ".join(f"{o[0]}:{o[1]:+.2f}({o[2]}/{o[3]})" for o in offs))
    if good:
        vals = sorted(o[1] for o in good)
        print(f"     -> {len(good)}/{len(offs)} fiables, decalages {vals[0]:+.2f} .. {vals[-1]:+.2f}")
    res[k] = offs
Path("work/kai/align_local.json").write_text(json.dumps(res, indent=1))
