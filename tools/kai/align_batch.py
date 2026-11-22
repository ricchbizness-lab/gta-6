#!/usr/bin/env python3
"""Cale chaque clip (timeline YouTube) sur la VOD Twitch, debut ET fin separement.
Un ecart different entre debut et fin = coupe du monteur YouTube a l'interieur du clip."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from align import decode, env, env_stream  # noqa: E402

VDIR = Path("work/kai/vod47")
YT = "input/kai_run.mp4"
FPS = 100
WIN = 12.0  # secondes de gabarit


def vod_env():
    names = [l for l in (VDIR / "index.m3u8").read_text().splitlines() if l and not l.startswith("#")]
    segs = []
    for n in names:
        p = VDIR / "seg" / n
        if not p.exists():
            break
        segs.append(p)
    cache = VDIR / f"env_{len(segs)}.npy"
    if cache.exists():
        return np.load(cache), len(segs)
    lst = VDIR / "concat_proto.txt"
    # protocole concat de ffmpeg : lecture en flux, sans gros fichier intermediaire
    proto = "concat:" + "|".join(str(p) for p in segs)
    lst.write_text(proto)
    e = env_stream(["-i", proto, "-map", "0:a:0"])
    np.save(cache, e)
    return e, len(segs)


def ncc_search(vod, tpl):
    m = len(tpl)
    L = 1 << int(np.ceil(np.log2(len(vod) + m)))
    corr = np.fft.irfft(np.fft.rfft(vod, L) * np.conj(np.fft.rfft(tpl, L)), L)[:len(vod) - m + 1]
    c2 = np.cumsum(np.r_[0, vod ** 2]); c1 = np.cumsum(np.r_[0, vod])
    var = (c2[m:] - c2[:-m]) - (c1[m:] - c1[:-m]) ** 2 / m
    ncc = corr / (np.sqrt(np.maximum(var, 1e-9)) * np.sqrt(m))
    i = int(np.argmax(ncc))
    far = np.r_[ncc[:max(0, i - 500)], ncc[i + 500:]]
    return i / FPS, float(ncc[i]), float(far.max()) if far.size else 0.0


def main():
    clips = json.loads(Path(sys.argv[1]).read_text())
    vod, nseg = vod_env()
    print(f"VOD couverte : {nseg*10/3600:.2f} h")
    out = []
    for c in clips:
        s, e = c["start"], c["end"]
        r = {}
        for tag, t0 in (("debut", s), ("fin", e - WIN)):
            tpl = env(decode(["-ss", str(t0), "-t", str(WIN), "-i", YT]))
            pos, sc, sc2 = ncc_search(vod, tpl)
            r[tag] = {"vod": round(pos, 2), "offset": round(pos - t0, 2), "score": round(sc, 3), "second": round(sc2, 3)}
        ok = all(r[k]["score"] > 0.35 and r[k]["score"] > 1.8 * r[k]["second"] for k in r)
        coupe = abs(r["debut"]["offset"] - r["fin"]["offset"]) > 0.25
        print(f'{c["id"]}: debut VOD {r["debut"]["vod"]:8.2f}s (off {r["debut"]["offset"]:+.2f}, '
              f'score {r["debut"]["score"]}/{r["debut"]["second"]}) | fin off {r["fin"]["offset"]:+.2f} '
              f'(score {r["fin"]["score"]}/{r["fin"]["second"]}) | {"FIABLE" if ok else "DOUTEUX"}'
              f'{" | COUPE INTERNE" if coupe else ""}')
        out.append(dict(c, align=r, fiable=ok, coupe_interne=coupe))
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
