#!/usr/bin/env python3
"""Prépare les données du montage Remotion à partir de clips.json + transcript.json.

Produit dans remotion/public/ :
  clips/<id>.mp4        copie de la découpe brute
  captions/<id>.json    sous-titres mot par mot (format @remotion/captions)
  clips-meta.json       hook, cta, punch-ins, durée pour chaque clip
"""
import json, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
PUB = ROOT / "remotion" / "public"

# punch-ins : secondes relatives au début du clip
PUNCHES = {
    "c10": [4.3, 12.4, 19.1, 31.5],
    "c02": [0.5, 9.0, 23.5, 41.5],
    "c07": [0.5, 18.0, 26.8],
    "c01": [0.5, 13.4, 22.2],
    "c09": [2.5, 6.2, 9.5, 16.2],
    "c03": [0.5, 4.2, 7.0, 38.2],
    "c08": [0.5, 3.5, 13.0],
    "c05": [4.5, 8.6],
}
CTA_SECONDS = 3.2  # durée du CTA en fin de clip


# Whisper coupe les élisions ("c'est" -> "c" + "'est") et les traits d'union
# ("est-ce" -> "est" + "-ce") : on recolle. Il laisse aussi des points de
# suspension sur les hésitations ("croix...") : on les enlève.
def clean_word(w):
    w = w.strip()
    while w.endswith("...") or w.endswith("\u2026"):
        w = w[:-3] if w.endswith("...") else w[:-1]
    return w.strip()


def merge_elisions(items):
    out = []
    for it in items:
        w = it["w"]
        glue = w.startswith("'") or w.startswith("-")
        if out and (glue or out[-1]["w"].endswith("'") or out[-1]["w"].endswith("-")):
            out[-1]["w"] += w
            out[-1]["e"] = it["e"]
            continue
        out.append(dict(it))
    for it in out:
        it["w"] = clean_word(it["w"])
    return [it for it in out if it["w"]]


MAX_WORDS_PER_PAGE = 4
PAGE_GAP_MS = 350


def split_balanced(n):
    """Découpe n mots en paquets de taille la plus égale possible (<= MAX)."""
    pages = max(1, -(-n // MAX_WORDS_PER_PAGE))
    base, extra = divmod(n, pages)
    return [base + (1 if i < extra else 0) for i in range(pages)]


def paginate(items):
    """Coupe d'abord aux respirations, puis équilibre les longues phrases.
    Évite les ruptures qui cassent un groupe de mots ou laissent un orphelin."""
    # phrases = suites de mots sans silence notable
    phrases, cur = [], []
    for i, it in enumerate(items):
        cur.append(it)
        nxt = items[i + 1] if i + 1 < len(items) else None
        if nxt is None or (nxt["s"] - it["e"]) > PAGE_GAP_MS:
            phrases.append(cur)
            cur = []

    caps = []
    for phrase in phrases:
        idx = 0
        for size in split_balanced(len(phrase)):
            chunk = phrase[idx:idx + size]
            idx += size
            for j, it in enumerate(chunk):
                cap = {
                    "text": " " + it["w"],
                    "startMs": round(it["s"]),
                    "endMs": round(it["e"]),
                    "timestampMs": round((it["s"] + it["e"]) / 2),
                    "confidence": None,
                }
                if j == len(chunk) - 1:
                    cap["pageBreakAfter"] = True
                caps.append(cap)
    return caps


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main():
    clips = json.loads((ROOT / "clips.json").read_text(encoding="utf-8"))
    segs = json.loads((ROOT / "work" / "transcript.json").read_text(encoding="utf-8"))

    words = []
    for s in segs:
        for w in s["words"]:
            if w["w"]:
                words.append(w)

    (PUB / "clips").mkdir(parents=True, exist_ok=True)
    (PUB / "captions").mkdir(parents=True, exist_ok=True)

    meta = []
    for c in clips:
        cid, start, end = c["id"], float(c["start"]), float(c["end"])
        src = ROOT / "clips" / "raw" / f"{cid}.mp4"
        if not src.is_file():
            raise SystemExit(f"Découpe manquante : {src}")
        dst = PUB / "clips" / f"{cid}.mp4"
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)

        duration = probe_duration(dst)

        raw = []
        for w in words:
            if w["end"] <= start or w["start"] >= end:
                continue
            s_ms = max(0.0, (w["start"] - start)) * 1000
            e_ms = min(duration, (w["end"] - start)) * 1000
            if e_ms <= s_ms:
                # Whisper donne parfois une durée nulle (ex. 'a') : on la plancherise
                # au lieu de perdre le mot.
                e_ms = min(duration * 1000, s_ms + 70)
            if e_ms <= s_ms:
                continue
            raw.append({"w": w["w"], "s": s_ms, "e": e_ms})

        raw = merge_elisions(raw)
        caps = paginate(raw)
        (PUB / "captions" / f"{cid}.json").write_text(
            json.dumps(caps, ensure_ascii=False), encoding="utf-8")

        meta.append({
            "id": cid,
            "src": f"clips/{cid}.mp4",
            "captions": f"captions/{cid}.json",
            "durationInSeconds": round(duration, 3),
            "hook": c["hook"],
            "cta": c["cta"],
            "punches": PUNCHES.get(cid, []),
            "ctaStart": round(max(0.0, duration - CTA_SECONDS), 3),
        })
        print(f"{cid}: {duration:6.2f}s, {len(caps):4d} mots, "
              f"{len(PUNCHES.get(cid, []))} punch-ins")

    (PUB / "clips-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {PUB/'clips-meta.json'} ({len(meta)} clips)")


if __name__ == "__main__":
    main()
