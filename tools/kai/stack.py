#!/usr/bin/env python3
"""Mise en page verticale : facecam de Kai en haut, jeu en bas (1080x1920, 30 fps).
Les cadres sont mesures sur la VOD 1080p (tools/kai : detection + verification visuelle)."""
import subprocess, sys
from pathlib import Path

CAM_DEFAULT = (384, 216, 0, 432)      # w, h, x, y dans la source 1920x1080
CAM = {"k01": (376, 212, 0, 374)}     # k01 : disposition differente (menu PS5)
GAME_DEFAULT = (889, 1080, 515, 0)    # recadrage jeu, ratio 1080/1312
GAME = {"k01": (576, 700, 1000, 262)}  # k01 : sous les icones d applis PS5, au-dessus du widget amis (regle "pas de logos")
TOP_H, BOT_H = 608, 1312

src_dir, out_dir = Path("clips/hd"), Path("clips/kai_v")
out_dir.mkdir(parents=True, exist_ok=True)
for cid in sys.argv[1:]:
    cw, ch, cx, cy = CAM.get(cid, CAM_DEFAULT)
    gw, gh, gx, gy = GAME.get(cid, GAME_DEFAULT)
    fc = (f"[0:v]split=2[a][b];"
          f"[a]crop={cw}:{ch}:{cx}:{cy},scale=1080:{TOP_H}:flags=lanczos,setsar=1[cam];"
          f"[b]crop={gw}:{gh}:{gx}:{gy},scale=1080:{BOT_H}:flags=lanczos,setsar=1[game];"
          f"[cam][game]vstack=2,fps=30[v]")
    out = out_dir / f"{cid}.mp4"
    r = subprocess.run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error", "-i", str(src_dir / f"{cid}.mp4"),
                        "-filter_complex", fc, "-map", "[v]", "-map", "0:a:0",
                        "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-600:])
    print(f"{cid} -> {out}", flush=True)
