#!/usr/bin/env python3
"""Contrôle qualité des clips finaux : format, durée, loudness, frames témoins."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "out"
QC = ROOT / "work" / "qc"


def probe(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def loudness(path):
    r = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", str(path), "-af", "ebur128=peak=true",
         "-f", "null", "-"], capture_output=True, text=True)
    i = tp = None
    tail = r.stderr[-1800:]
    for line in tail.splitlines():
        line = line.strip()
        if line.startswith("I:") and "LUFS" in line:
            i = float(line.split()[1])
        if line.startswith("Peak:") and "dBFS" in line:
            tp = float(line.split()[1])
    return i, tp


def frames(path, cid, duration):
    QC.mkdir(parents=True, exist_ok=True)
    times = [1.2, duration * 0.35, duration * 0.65, max(0.0, duration - 1.2)]
    paths = []
    for n, t in enumerate(times, 1):
        p = QC / f"{cid}_{n}.jpg"
        subprocess.run(
            ["ffmpeg", "-nostdin", "-loglevel", "error", "-ss", f"{t:.2f}",
             "-i", str(path), "-frames:v", "1", "-vf", "scale=360:-2",
             str(p), "-y"], check=True)
        paths.append(p)
    sheet = QC / f"{cid}_sheet.jpg"
    subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error",
         *sum([["-i", str(p)] for p in paths], []),
         "-filter_complex", "[0][1][2][3]hstack=4", str(sheet), "-y"], check=True)
    return sheet


def main():
    clips = json.loads((ROOT / "clips.json").read_text(encoding="utf-8"))
    rows, problems = [], []
    for c in clips:
        cid = c["id"]
        f = OUT / f"{cid}.mp4"
        if not f.is_file():
            problems.append(f"{cid}: fichier manquant")
            continue
        meta = probe(f)
        v = next(s for s in meta["streams"] if s["codec_type"] == "video")
        a = next((s for s in meta["streams"] if s["codec_type"] == "audio"), None)
        dur = float(meta["format"]["duration"])
        w, h = int(v["width"]), int(v["height"])
        fps = eval(v["r_frame_rate"])  # noqa: S307  (valeur issue de ffprobe)
        lufs, peak = loudness(f)

        if (w, h) != (1080, 1920):
            problems.append(f"{cid}: résolution {w}x{h} au lieu de 1080x1920")
        if not 15 <= dur <= 60:
            problems.append(f"{cid}: durée {dur:.1f}s hors 15-60s")
        if abs(fps - 30) > 0.01:
            problems.append(f"{cid}: {fps} fps au lieu de 30")
        if a is None:
            problems.append(f"{cid}: pas de piste audio")
        if lufs is not None and abs(lufs + 14) > 1.0:
            problems.append(f"{cid}: loudness {lufs} LUFS (cible -14)")
        if peak is not None and peak > -0.5:
            problems.append(f"{cid}: crête {peak} dBFS (risque de saturation)")

        sheet = frames(f, cid, dur)
        rows.append({
            "id": cid, "duree": round(dur, 1), "res": f"{w}x{h}",
            "fps": round(fps, 2), "lufs": lufs, "peak": peak,
            "taille_mo": round(f.stat().st_size / 1e6, 1), "sheet": str(sheet),
        })
        print(f"{cid}  {dur:5.1f}s  {w}x{h}  {fps:.0f}fps  "
              f"{lufs} LUFS  crête {peak} dBFS  {rows[-1]['taille_mo']} Mo")

    print()
    if problems:
        print("PROBLÈMES :")
        for p in problems:
            print("  -", p)
    else:
        print("Aucun problème automatique détecté.")
    (ROOT / "work" / "qc_report.json").write_text(
        json.dumps({"rows": rows, "problems": problems}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
