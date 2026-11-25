#!/usr/bin/env python3
"""Fabrique un short au format neon a partir d'un dossier projet.

projects/<id>/
  brand.json    identite visuelle (couleurs, polices, nom, avatar, tags)
  script.json   texte de la voix off + scenes (titre, carte, ancre = mots qui declenchent la scene)
  voice_raw.*   voix off brute (enregistree ou TTS)

Etapes : voix accelere au debit cible -> transcription mot a mot -> calage des scenes sur
leurs ancres -> fonds floutes + images -> props Remotion. Rendu ensuite avec render.sh.
"""
import json, re, shutil, subprocess, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import build_montage_data as bmd  # noqa: E402

PUBLIC = ROOT / "remotion" / "public"


def run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"echec : {' '.join(map(str, cmd))[:300]}\n{r.stderr[-1500:]}")
    return r.stdout


def duration(p):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", p]))


def transcribe(audio, out, lang, model="small"):
    run([sys.executable, "-I", ROOT / "clip_pipeline.py", "transcribe", audio, "--out", out,
         "--model", model, "--lang", lang, "--device", "cpu", "--compute", "int8"])
    segs = json.loads((out / "transcript.json").read_text())
    return [w for s in segs for w in s["words"] if w["w"]]


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", w)


def apply_fixes(items, fixes):
    """Remplace des suites de mots mal entendues par le texte exact, sur le meme intervalle de temps."""
    for old, new in fixes:
        pat = [norm(x) for x in old.split()]
        i = 0
        while i <= len(items) - len(pat):
            if [norm(w["w"]) for w in items[i:i + len(pat)]] == pat:
                s, e = items[i]["s"], items[i + len(pat) - 1]["e"]
                toks = new.split(); step = (e - s) / len(toks)
                items[i:i + len(pat)] = [{"w": x, "s": s + k * step, "e": s + (k + 1) * step} for k, x in enumerate(toks)]
                i += len(toks)
            else:
                i += 1
    return items


def main(pid):
    P = ROOT / "projects" / pid
    script = json.loads((P / "script.json").read_text(encoding="utf-8"))
    brand = json.loads((P / "brand.json").read_text(encoding="utf-8"))
    lang = script.get("lang", "fr")
    pub = PUBLIC / "neon" / pid
    if pub.exists():
        shutil.rmtree(pub)
    (pub / "img").mkdir(parents=True)
    work = ROOT / "work" / "neon" / pid
    work.mkdir(parents=True, exist_ok=True)

    # 1) debit de parole : la reference tourne a ~320 mots/min ; on vise script["target_wpm"]
    raw = next(P.glob("voice_raw.*"))
    words = transcribe(raw, work / "raw", lang)
    span = words[-1]["end"] - words[0]["start"]
    wpm = len(words) / span * 60
    target = script.get("target_wpm", 290)
    tempo = max(1.0, min(1.45, target / wpm))
    voice = pub / "voice.wav"
    run(["ffmpeg", "-y", "-nostdin", "-i", raw, "-af", f"atempo={tempo:.4f}", "-ar", "48000", "-ac", "2", voice])
    print(f"voix : {wpm:.0f} mots/min -> x{tempo:.3f} -> ~{wpm*tempo:.0f} mots/min")

    # 2) mots horodates de la voix finale
    raw_words = transcribe(voice, work / "final", lang, script.get("whisper_model", "small"))
    items = [{"w": w["w"], "s": w["start"] * 1000, "e": max(w["end"], w["start"] + 0.07) * 1000} for w in raw_words]
    items = apply_fixes(bmd.merge_elisions(items), script.get("caption_fixes", []))
    words = [{"w": it["w"], "start": it["s"] / 1000, "end": it["e"] / 1000} for it in items]
    vdur = duration(voice)
    total = round(vdur + script.get("tail", 0.8), 3)

    # 3) calage des scenes : chaque ancre est cherchee apres la precedente
    toks = [norm(w["w"]) for w in words]
    pos, scenes = 0, []
    for i, sc in enumerate(script["scenes"]):
        if i == 0:
            start = 0.0
        else:
            pat = [norm(x) for x in sc["anchor"].split()]
            # correspondance par prefixe : 'abonne' trouve 'abonne-toi', 'jet' trouve 'jetski'
            hit = next((k for k in range(pos, len(toks) - len(pat) + 1)
                        if all(toks[k + j] == p or (len(p) >= 5 and toks[k + j].startswith(p))
                               for j, p in enumerate(pat))), None)
            if hit is None:
                sys.exit(f"ancre introuvable apres le mot {pos} : '{sc['anchor']}'\n"
                         f"texte entendu : {' '.join(w['w'] for w in words[pos:pos+40])}")
            pos = hit + len(pat)
            start = max(0.0, words[hit]["start"] - sc.get("lead", 0.08))
        ch = sc["chapter"] if "chapter" in sc else (scenes[-1]["chapter"] if scenes else 0)  # herite du chapitre precedent
        scenes.append({**{k: v for k, v in sc.items() if k not in ("anchor", "lead", "bg")}, "chapter": ch, "start": round(start, 3), "_bg": sc.get("bg")})
    for i, sc in enumerate(scenes):
        sc["end"] = scenes[i + 1]["start"] if i + 1 < len(scenes) else total

    # 4) images de cartes extraites des sources (frame nette sur fond flou)
    for i, sc in enumerate(scenes):
        card = sc.get("card") or {}
        if card.get("type") == "image" and "frame" in card:
            fr = card.pop("frame")
            dst = pub / "img" / f"s{i}.jpg"
            run(["ffmpeg", "-y", "-nostdin", "-ss", fr["t"], "-i", ROOT / fr["source"], "-frames:v", "1",
                 "-vf", "crop=ih*4/3:ih,scale=800:-2", "-q:v", "3", dst])
            card["src"] = f"neon/{pid}/img/{dst.name}"

    # 5) fonds : un plan flou par groupe de scenes consecutives sur la meme source
    bgs, cur = [], None
    for sc in scenes:
        b = sc.pop("_bg")
        if b is None:
            b = cur["idx"] if cur else 0
        if cur and cur["idx"] == b:
            cur["to"] = sc["end"]
        else:
            cur = {"idx": b, "from": sc["start"], "to": sc["end"]}
            bgs.append(cur)
    backgrounds = []
    for k, g in enumerate(bgs):
        src = script["backgrounds"][g["idx"]]
        dst = pub / f"bg{k}.mp4"
        d = g["to"] - g["from"] + 0.2
        # source video (+ t) ou image fixe (fond flou d'une capture d'article)
        inp = (["-loop", "1", "-framerate", "30", "-i", ROOT / src["image"]] if "image" in src
               else ["-ss", src["t"], "-i", ROOT / src["source"]])
        run(["ffmpeg", "-y", "-nostdin", *inp, "-t", f"{d:.3f}", "-an",
             "-vf", "scale=-2:1920,crop=1080:1920,gblur=sigma=26,eq=brightness=-0.10:saturation=1.15,fps=30",
             "-c:v", "libx264", "-crf", "22", "-preset", "veryfast", "-pix_fmt", "yuv420p", dst])
        backgrounds.append({"src": f"neon/{pid}/{dst.name}", "from": round(g["from"], 3), "to": round(g["to"], 3)})

    # 6) sous-titres : pages de 3 mots max
    bmd.MAX_WORDS_PER_PAGE = 3
    caps = bmd.paginate(items)
    (pub / "captions.json").write_text(json.dumps(caps, ensure_ascii=False))

    # 7) props + registre des compositions
    props = {"brand": brand, "scenes": scenes, "backgrounds": backgrounds, "voice": f"neon/{pid}/voice.wav",
             "captions": f"neon/{pid}/captions.json", "sfx": script.get("sfx", True), "durationInSeconds": total}
    if script.get("thumb"):
        props["thumb"] = script["thumb"]
    if script.get("music"):
        mdst = pub / "music" / Path(script["music"]).name
        mdst.parent.mkdir(exist_ok=True)
        shutil.copy2(ROOT / script["music"], mdst)
        props["music"] = f"neon/{pid}/music/{mdst.name}"
        props["musicVolume"] = script.get("music_volume", 0.18)
    reg = PUBLIC / "neon" / "projects.json"
    projects = [p for p in json.loads(reg.read_text()) if p["id"] != f"neon-{pid}"]
    projects.append({"id": f"neon-{pid}", "props": props})
    reg.write_text(json.dumps(projects, ensure_ascii=False, indent=1))
    print(f"{len(scenes)} scenes, {len(backgrounds)} fonds, {total:.1f}s -> composition neon-{pid}")
    for s in scenes:
        print(f"  {s['start']:6.2f}-{s['end']:6.2f}  ch{s.get('chapter', 0)}  {s.get('title', '')!s:28.28}  {(s.get('card') or {}).get('type', '')}")


if __name__ == "__main__":
    main(sys.argv[1])
