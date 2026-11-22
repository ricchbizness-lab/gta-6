#!/usr/bin/env python3
"""Decoupe chaque clip en morceaux a decalage constant (coupes du monteur YouTube).
Sortie : liste de morceaux VOD [debut, fin] a concatener pour reproduire le clip en HD."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from align import decode, env  # noqa
from align_batch import ncc_search  # noqa

FPS = 100
vod = np.load(sorted(Path("work/kai/vod47").glob("env_*.npy"))[-1])
YT = "input/kai_run.mp4"
# id: (debut YT, fin YT, decalage connu le plus proche)
clips = {
    "k01": (36.6, 68.0, 475.03), "k03": (3361.0, 3386.3, 1936.21), "k05": (5090.8, 5129.0, 2162.49),
    "k06": (5305.0, 5337.3, 2162.51), "k07": (5527.6, 5567.0, 2232.86), "k08": (5769.6, 5815.0, 2262.0),
    "k09": (5909.7, 5929.6, 2316.28), "k10": (7051.0, 7092.7, 2770.0), "k12": (7153.8, 7178.7, 2950.0),
}
STEP, W = 1.0, 3.0
out = {}
for k, (a, b, off0) in clips.items():
    lo, hi = a + off0 - 120, b + off0 + 120
    seg = vod[int(lo * FPS):int(hi * FPS)]
    pts = []
    t = a
    while t + W <= b + 0.01:
        tpl = env(decode(["-ss", f"{t:.2f}", "-t", str(W), "-i", YT]))
        pos, sc, sc2 = ncc_search(seg, tpl)
        pts.append((t, lo + pos - t, sc, sc2))
        t += STEP
    # decalages fiables, puis regroupement en paliers (tolerance 0.15 s)
    good = [(t, o) for t, o, sc, sc2 in pts if sc > 0.5 and sc > 1.6 * sc2]
    pal = []
    for t, o in good:
        if pal and abs(pal[-1]["off"] - o) < 0.15:
            pal[-1]["t1"] = t + W
            pal[-1]["n"] += 1
        else:
            pal.append({"off": o, "t0": t, "t1": t + W, "n": 1})
    pal = [p for p in pal if p["n"] >= 2] or pal
    # bornes : debut/fin du clip aux extremites, coupes au milieu des zones d'incertitude
    pieces = []
    for i, p in enumerate(pal):
        s = a if i == 0 else (pal[i - 1]["t1"] + p["t0"]) / 2
        e = b if i == len(pal) - 1 else (p["t1"] + pal[i + 1]["t0"]) / 2
        pieces.append({"yt": [round(s, 2), round(e, 2)], "offset": round(p["off"], 2),
                       "vod": [round(s + p["off"], 2), round(e + p["off"], 2)]})
    out[k] = {"yt": [a, b], "pieces": pieces, "fiables": f"{len(good)}/{len(pts)}"}
    desc = " + ".join(f'VOD {q["vod"][0]:.1f}-{q["vod"][1]:.1f}' for q in pieces)
    dur = sum(q["vod"][1] - q["vod"][0] for q in pieces)
    print(f"{k}: {len(pieces)} morceau(x), {out[k]['fiables']} gabarits fiables, {dur:.1f}s -> {desc}")
Path("work/kai/pieces.json").write_text(json.dumps(out, indent=1))
