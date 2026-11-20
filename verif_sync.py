#!/usr/bin/env python3
"""Compare les instants d'attaque de mots entre un original et sa version revoicee."""
import json, sys, unicodedata, re
from pathlib import Path
from collections import Counter


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", w)


def words(p):
    segs = json.loads(Path(p).read_text(encoding="utf-8"))
    return [(w["start"], norm(w["w"])) for s in segs for w in s["words"] if w["w"]]


def compare(ref_path, cand_path, label, espacement=5.0):
    ref, cand = words(ref_path), words(cand_path)
    freq = Counter(w for _, w in ref)
    ancres, last = [], -99
    for t, w in ref:
        if freq[w] == 1 and len(w) >= 5 and t - last >= espacement:
            ancres.append((t, w))
            last = t
    ecarts = []
    manquants = 0
    for t, w in ancres:
        c = next((ct for ct, cw in cand if cw == w), None)
        if c is None:
            manquants += 1
            continue
        ecarts.append(c - t)
    if not ecarts:
        print(f"{label}: aucune ancre exploitable")
        return
    moy = sum(ecarts) / len(ecarts)
    amp = max(abs(e) for e in ecarts)
    verdict = "SYNCHRONE" if amp < 0.5 else "A VERIFIER"
    print(f"{label:<14} {len(ecarts):>2}/{len(ancres):<2} ancres | "
          f"moyen {moy:+.2f}s | max {amp:.2f}s | {verdict}")


for i in range(3):
    compare(f"work/amintech/a{i}/transcript.json",
            f"work/amintech/sync_{i}/transcript.json",
            f"amintech_{i}")
