#!/usr/bin/env python3
"""Donnees Remotion des clips Kai Cenat : video, sous-titres corriges, meta (hook, CTA, mise en page)."""
import json, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from build_montage_data import merge_elisions, paginate  # noqa: E402

PUB = Path("remotion/public/kai")
(PUB / "captions").mkdir(parents=True, exist_ok=True)

# Corrections d'ecoute, verifiees contre le transcript du stream et le contexte.
FIX = {
    "k01": [("who are in heaven hallowed be that name", "who art in heaven, hallowed be thy name"),
            ("that kingdom come that will be done on us it isn't him", "thy kingdom come, thy will be done, on earth as it is in heaven"),
            ("and gives us day our daily bearer for gives us trespasses", "give us this day our daily bread, forgive us our trespasses"),
            ("i so you forgive those", "as we forgive those"),
            ("and lead us out to temptation but it was evil", "and lead us not into temptation, but deliver us from evil")],
    "k07": [("you don't look these boys", "we gonna loot these boys"), ("loop them", "loot them"),
            ("now we don't look my boy", "now we gonna loot my boy")],
    "k09": [("this is chat right now", "chat, right now"), ("like if this how florida is", "like, is this how Florida is")],
    "k10": [("it's a house bro", "this messes up your house, bro")],
    "k12": [("i know what seeing this is", "I know what scene this is"), ("safe this time huh", "sink this time, huh"),
            ("i know we're seeing this", "I know what scene this is")],
    "k03": [("you heart", "you heard"), ("fill me", "feel me")],
}
CENSOR = [(r"(?i)\bfuck", "f*ck"), (r"(?i)\bshit", "sh*t"), (r"(?i)\bbitch", "b*tch"),
          (r"(?i)\bnigg", "n*gg"), (r"(?i)\bmotherf\*?u?ck", "motherf*ck")]
HOOKS = {
    "k01": "KAI CENAT PRAYED BEFORE PLAYING GTA 6",
    "k07": "KAI CENAT DUMPED THEM IN THE OCEAN",
    "k08": "KAI CENAT: \u201cIS ANYBODY NICE IN THIS NEIGHBORHOOD?!\u201d",
    "k09": "KAI CENAT ON GTA 6 FLORIDA",
    "k05": "KAI CENAT DOESN'T WANT TO FIGHT",
    "k10": "KAI CENAT TRIED VAPING IN GTA 6",
    "k12": "KAI CENAT KNEW EXACTLY WHAT SCENE THIS WAS",
    "k03": "KAI CENAT PAINTED THE HOUSE FOR LUCIA",
}
CTA = "FOLLOW FOR MORE KAI CENAT GTA 6"


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def apply_fixes(words, fixes):
    for old, new in fixes:
        pat = [norm(x) for x in old.split()]
        i = 0
        while i <= len(words) - len(pat):
            if [norm(w["w"]) for w in words[i:i + len(pat)]] == pat:
                s, e = words[i]["s"], words[i + len(pat) - 1]["e"]
                toks = new.split()
                step = (e - s) / len(toks)
                repl = [{"w": t, "s": s + k * step, "e": s + (k + 1) * step} for k, t in enumerate(toks)]
                words[i:i + len(pat)] = repl
                i += len(repl)
            else:
                i += 1
    return words


def clean(w):
    w = re.sub(r"\bChad\b", "chat", w)
    for pat, rep in CENSOR:
        w = re.sub(pat, rep, w)
    return w


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "default=nw=1:nk=1", str(p)], capture_output=True, text=True).stdout)


meta = []
for cid in HOOKS:
    src = Path(f"clips/kai_v/{cid}.mp4")
    d = dur(src)
    shutil.copy2(src, PUB / f"{cid}.mp4")
    segs = json.loads(Path(f"work/kai/tr/{cid}/transcript.json").read_text())
    words = [{"w": w["w"], "s": w["start"] * 1000, "e": w["end"] * 1000}
             for s in segs for w in s["words"] if w["w"]]
    for w in words:
        if w["e"] <= w["s"]:
            w["e"] = w["s"] + 70
    words = apply_fixes(words, FIX.get(cid, []))
    words = merge_elisions(words)
    for w in words:
        w["w"] = clean(w["w"])
    caps = paginate(words)
    (PUB / "captions" / f"{cid}.json").write_text(json.dumps(caps, ensure_ascii=False))
    meta.append({"id": f"kai-{cid}", "src": f"kai/{cid}.mp4", "captions": f"kai/captions/{cid}.json",
                 "durationInSeconds": round(d, 3), "hook": HOOKS[cid], "cta": CTA, "punches": [],
                 "ctaStart": round(max(0.0, d - 3.0), 3), "layout": "stacked"})
    txt = " ".join(c["text"].strip() for c in caps)
    print(f"{cid}: {d:5.1f}s, {len(caps)} mots | {txt[:150]}")
Path("remotion/public/kai-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
print("-> remotion/public/kai-meta.json")
