#!/usr/bin/env python3
"""Génère out/<id>.txt : titre, description et hashtags par clip."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
BASE_TAGS = ["#gta6", "#gta6gameplay", "#vicecity", "#gta6fr", "#gaming",
             "#rockstargames", "#gtavi"]

COPY = {
    "c10": {
        "titre": "La police m'a eu sur la plage de GTA 6",
        "desc": ("Trop tard pour me rendre. Fuite dans l'eau, bateau de police "
                 "derrière moi... et le plan final sur Vice Beach est magnifique. "
                 "Vous auriez fait quoi à ma place ?"),
        "tags": ["#gta6police", "#viceBeach", "#gameplayfr"],
    },
    "c02": {
        "titre": "J'ai tué un PNJ avec un couteau sans faire exprès",
        "desc": ("Je voulais juste tester les réactions des PNJ sur la plage de "
                 "Vice City. Ça a mal tourné. La suite, je la laisse à votre "
                 "imagination."),
        "tags": ["#gta6pnj", "#gtafail", "#gameplayfr"],
    },
    "c07": {
        "titre": "Est-ce que la bouée flotte vraiment dans GTA 6 ?",
        "desc": ("Rockstar a poussé le détail jusque dans les bouées gonflables. "
                 "Je l'ai mise à l'eau pour voir. Réponse à la fin."),
        "tags": ["#gta6details", "#rockstar", "#gta6physique"],
    },
    "c01": {
        "titre": "La plage de GTA 6 pour la première fois",
        "desc": ("Vice Beach en plein midi : l'eau, le sable, les PNJ, les "
                 "transats. Je m'attendais pas à ça. C'est quoi votre endroit "
                 "préféré du jeu pour l'instant ?"),
        "tags": ["#vicebeach", "#gta6plage", "#gta6map"],
    },
    "c09": {
        "titre": "Les voitures de Vice City sont irréelles",
        "desc": ("Une Lamborghini, une Corvette et un bar avec des danseuses en "
                 "30 secondes sur Ocean Drive. GTA 6 est une carte postale."),
        "tags": ["#gta6voiture", "#oceandrive", "#gta6cars"],
    },
    "c03": {
        "titre": "J'ai pas assez d'argent pour louer un jet ski",
        "desc": ("J'avais choisi le mien, celui aux couleurs de la France. "
                 "Sauf qu'il faut payer. Quelqu'un sait ce que c'est, BugMi ?"),
        "tags": ["#gta6jetski", "#gta6argent", "#gameplayfr"],
    },
    "c08": {
        "titre": "Ce PNJ random est trop détaillé pour être random",
        "desc": ("Regardez les détails de son visage. Soit Rockstar a poussé le "
                 "niveau de détail très loin sur tous les PNJ, soit c'est un "
                 "personnage de l'histoire. On sait jamais avec eux."),
        "tags": ["#gta6pnj", "#gta6details", "#rockstargames"],
    },
    "c05": {
        "titre": "J'ai écrasé un mec avec ma remorque de jet ski",
        "desc": ("Je voulais juste amener mon jet ski jusqu'à l'eau. Ça passait "
                 "pas. Il y avait quelqu'un."),
        "tags": ["#gtafail", "#gta6jetski", "#gameplayfr"],
    },
}


def main():
    clips = json.loads((ROOT / "clips.json").read_text(encoding="utf-8"))
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    for c in clips:
        cid = c["id"]
        copy = COPY[cid]
        tags = copy["tags"] + BASE_TAGS
        dur = float(c["end"]) - float(c["start"])
        body = (
            f"TITRE\n{copy['titre']}\n\n"
            f"DESCRIPTION\n{copy['desc']}\n\n"
            f"HASHTAGS\n{' '.join(tags)}\n\n"
            f"CTA DE FIN (incrusté)\n{c['cta']}\n\n"
            f"--- technique ---\n"
            f"source      : input/source.mp4  {c['start']}s -> {c['end']}s\n"
            f"durée       : {dur:.1f}s\n"
            f"format      : 1080x1920, 30 fps, H.264 + AAC, -14 LUFS\n"
            f"hook        : {c['hook']}\n"
            f"plateformes : TikTok / YouTube Shorts / Instagram Reels\n"
        )
        (out / f"{cid}.txt").write_text(body, encoding="utf-8")
        print(f"out/{cid}.txt")


if __name__ == "__main__":
    main()
