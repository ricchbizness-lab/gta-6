#!/usr/bin/env python3
"""clip_pipeline.py — étapes mécaniques du workflow de clipping.

Trois sous-commandes :
  prep        audio léger + copie proxy basse définition (pour analyser sans la vidéo lourde)
  transcribe  transcription locale faster-whisper -> JSON (mots horodatés), SRT, TXT
  cut         découpe des clips depuis la vidéo ORIGINALE à partir d'un clips.json

Exemples :
  python clip_pipeline.py prep input/source.mp4 --out work
  python clip_pipeline.py transcribe work/audio.ogg --out work --model small --lang en
  python clip_pipeline.py cut input/source.mp4 clips.json --out clips/raw --vertical

Format de clips.json :
  [{"id": "c01", "start": "00:12:34.5", "end": "00:13:20"}, ...]
  (start/end : secondes ou "SS", "MM:SS", "HH:MM:SS(.ms)")
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    r = subprocess.run([str(c) for c in cmd])
    if r.returncode != 0:
        sys.exit(f"Commande échouée (code {r.returncode})")


def need(tool):
    if shutil.which(tool) is None:
        sys.exit(f"'{tool}' est introuvable dans le PATH. Installe-le d'abord.")


def decode_audio_ffmpeg(path, sampling_rate=16000):
    """Décode l'audio en float32 mono via ffmpeg (contourne PyAV).

    faster-whisper 1.2.x appelle av.open(..., metadata_errors=...), argument
    supprimé dans PyAV >= 19 ; model.transcribe() accepte un numpy array, donc
    on décode nous-mêmes avec ffmpeg (déjà requis par le reste du pipeline).
    """
    import numpy as np
    need("ffmpeg")
    cmd = ["ffmpeg", "-nostdin", "-threads", "1", "-i", str(path),
           "-f", "f32le", "-ac", "1", "-ar", str(sampling_rate), "-vn", "-"]
    print("+", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if r.returncode != 0 or not r.stdout:
        sys.exit("Décodage audio ffmpeg échoué")
    return np.frombuffer(r.stdout, dtype=np.float32).copy()


def to_seconds(value):
    """Accepte 12.5, "12.5", "MM:SS", "HH:MM:SS(.ms)"."""
    if isinstance(value, (int, float)):
        return float(value)
    parts = str(value).strip().split(":")
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"Timecode invalide : {value!r}")
    seconds = 0.0
    for p in parts:
        seconds = seconds * 60 + float(p)
    return seconds


def hms(t):
    t = max(0.0, float(t))
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def srt_ts(t):
    return hms(t).replace(".", ",")


# ---------------------------------------------------------------- prep
def cmd_prep(a):
    need("ffmpeg")
    src = Path(a.video)
    if not src.is_file():
        sys.exit(f"Fichier introuvable : {src}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    audio = out / "audio.ogg"
    run(["ffmpeg", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000",
         "-c:a", "libopus", "-b:a", "24k", audio])
    print(f"Audio : {audio} ({audio.stat().st_size / 1e6:.1f} Mo)")
    if not a.audio_only:
        proxy = out / "proxy.mp4"
        run(["ffmpeg", "-y", "-i", src, "-vf", f"scale=-2:{a.proxy_height}", "-r", "24",
             "-c:v", "libx264", "-crf", "32", "-preset", "veryfast", "-an", proxy])
        print(f"Proxy : {proxy} ({proxy.stat().st_size / 1e6:.1f} Mo)")


# ---------------------------------------------------------- transcribe
def cmd_transcribe(a):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper manquant : pip install faster-whisper")
    audio = Path(a.audio)
    if not audio.is_file():
        sys.exit(f"Fichier introuvable : {audio}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    print(f"Chargement du modèle '{a.model}' (device={a.device}, compute={a.compute})...", flush=True)
    model = WhisperModel(a.model, device=a.device, compute_type=a.compute)
    segments, info = model.transcribe(
        decode_audio_ffmpeg(audio), language=a.lang,
        word_timestamps=True, vad_filter=True
    )
    print(f"Langue : {info.language} (p={info.language_probability:.2f}), durée {hms(info.duration)}", flush=True)

    data, srt_lines, txt_lines = [], [], []
    for i, seg in enumerate(segments, start=1):
        words = [{"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
                 for w in (seg.words or [])]
        text = seg.text.strip()
        data.append({"id": i, "start": round(seg.start, 3), "end": round(seg.end, 3),
                     "text": text, "words": words})
        srt_lines += [str(i), f"{srt_ts(seg.start)} --> {srt_ts(seg.end)}", text, ""]
        txt_lines.append(f"[{hms(seg.start)[:8]}] {text}")
        if i % 50 == 0:
            print(f"  {i} segments... ({hms(seg.end)[:8]})", flush=True)

    (out / "transcript.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "transcript.srt").write_text("\n".join(srt_lines), encoding="utf-8")
    (out / "transcript.txt").write_text("\n".join(txt_lines), encoding="utf-8")
    print(f"OK : {len(data)} segments -> {out}/transcript.(json|srt|txt)")


# ----------------------------------------------------------------- cut
def cmd_cut(a):
    need("ffmpeg")
    src = Path(a.video)
    if not src.is_file():
        sys.exit(f"Fichier introuvable : {src}")
    clips = json.loads(Path(a.clips).read_text(encoding="utf-8"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    for c in clips:
        cid = c["id"]
        start, end = to_seconds(c["start"]), to_seconds(c["end"])
        if end <= start:
            sys.exit(f"Clip {cid} : end ({end}) <= start ({start})")
        dest = out / f"{cid}.mp4"
        cmd = ["ffmpeg", "-y", "-ss", hms(start), "-i", src, "-t", f"{end - start:.3f}"]
        if a.copy:
            cmd += ["-c", "copy", "-avoid_negative_ts", "make_zero"]
        else:
            if a.vertical:
                cmd += ["-vf", "crop='min(iw,ih*9/16)':ih,scale=1080:1920"]
            cmd += ["-c:v", "libx264", "-crf", str(a.crf), "-preset", "veryfast",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"]
        cmd.append(dest)
        run(cmd)
        print(f"Clip {cid} : {hms(start)[:8]} -> {hms(end)[:8]} ({end - start:.1f}s) -> {dest}")


# ----------------------------------------------------------- normalize
def cmd_normalize(a):
    """Normalise le loudness (EBU R128, deux passes) et finalise pour mobile."""
    need("ffmpeg")
    src = Path(a.video)
    if not src.is_file():
        sys.exit(f"Fichier introuvable : {src}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / src.name

    # Passe 1 : mesure
    probe = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", str(src), "-af",
         f"loudnorm=I={a.lufs}:TP={a.tp}:LRA={a.lra}:print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True)
    try:
        blob = probe.stderr[probe.stderr.rindex("{"):probe.stderr.rindex("}") + 1]
        m = json.loads(blob)
    except (ValueError, json.JSONDecodeError):
        sys.exit("Mesure loudnorm illisible")

    af = (f"loudnorm=I={a.lufs}:TP={a.tp}:LRA={a.lra}"
          f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
          f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
          f":offset={m['target_offset']}:linear=true:print_format=summary")

    # Passe 2 : application (vidéo copiée, seul l'audio est réencodé)
    run(["ffmpeg", "-y", "-nostdin", "-i", src, "-af", af,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-movflags", "+faststart", dest])
    print(f"{src.name} : {m['input_i']} LUFS -> {a.lufs} LUFS  ->  {dest}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("prep", help="audio léger + proxy basse définition")
    s.add_argument("video")
    s.add_argument("--out", default="work")
    s.add_argument("--audio-only", action="store_true", help="ne pas créer le proxy vidéo")
    s.add_argument("--proxy-height", type=int, default=540)
    s.set_defaults(fn=cmd_prep)

    s = sub.add_parser("transcribe", help="transcription locale faster-whisper")
    s.add_argument("audio")
    s.add_argument("--out", default="work")
    s.add_argument("--model", default="small", help="tiny/base/small/medium/large-v3-turbo...")
    s.add_argument("--lang", default=None, help="ex: en, fr (auto-détection si absent)")
    s.add_argument("--device", default="auto", help="auto/cpu/cuda")
    s.add_argument("--compute", default="auto", help="auto/int8/float16...")
    s.set_defaults(fn=cmd_transcribe)

    s = sub.add_parser("cut", help="découper des clips depuis l'original")
    s.add_argument("video")
    s.add_argument("clips", help="clips.json")
    s.add_argument("--out", default="clips/raw")
    s.add_argument("--vertical", action="store_true", help="recadrage 9:16 centré (aperçu rapide)")
    s.add_argument("--copy", action="store_true", help="sans réencodage (instantané, mais démarre à l'image clé précédente : clip plus long que demandé)")
    s.add_argument("--crf", type=int, default=18)
    s.set_defaults(fn=cmd_cut)

    s = sub.add_parser("normalize", help="normalise le loudness a -14 LUFS")
    s.add_argument("video")
    s.add_argument("--out", default="out")
    s.add_argument("--lufs", type=float, default=-14.0)
    s.add_argument("--tp", type=float, default=-1.5)
    s.add_argument("--lra", type=float, default=11.0)
    s.set_defaults(fn=cmd_normalize)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
