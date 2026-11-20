# Brief — Clip Studio

Règles par défaut, mises à jour le 2026-11-20 sur instruction de l'humain.

## Provenance des sources
- `input/source.mp4` — gameplay GTA 6 FR fourni par l'humain (Dropbox, 18/11).
- `input/crabe_geant.mp4` — short « easter egg crabe géant », fourni par l'humain
  le 20/11. Clipping et revoicing autorisés par lui : il a explicitement levé la
  condition préalable de vérification le 20/11 après que je l'aie signalée.
  Format d'origine 720x1280, 63,8 s, voix off scriptée.

## Contraintes
- **Langue** : français. Sous-titres FR mot par mot obligatoires (lecture sans son).
- **Plateformes** : TikTok, YouTube Shorts, Instagram Reels. Même master pour les trois.
- **Format** : H.264 + AAC 192k, faststart, audio -14 LUFS.
  Sortie 1080x1920 si la source le permet ; sinon on garde la définition native
  plutôt que d'agrandir (voir `input/crabe_geant.mp4` : 720x1280).
- **Durée** : 15-60 s.
- **Recadrage** : full-bleed, pas de barres floutées.
- **Zones sûres** : rien d'important dans les 150 px du haut ni les 320 px du bas.
- **Hook** : texte lisible dans les 2 premières secondes, sans le son.
- **CTA** : générique, sans nom de créateur (non fourni).

## Voix off générée par IA : AUTORISÉE
Levée explicite de l'interdiction par l'humain le 2026-11-20.
- Voix de synthèse et remplacement de voix autorisés sur les sources listées
  ci-dessus en « Provenance ».
- Reste interdit : générer des **images** ou de la **vidéo** par IA. Le visuel
  provient uniquement de la source.
- Toute voix générée doit être signalée dans le `.txt` du livrable, pour que
  l'humain puisse cocher la case « contenu généré par IA » à la publication
  (obligatoire sur TikTok, YouTube et Instagram pour les médias synthétiques).

## Interdits
- Aucune publication : les livrables restent dans `out/`.
- Ne jamais écraser `input/` (fichiers en lecture seule).
- Pas de musique ajoutée (droits non vérifiés) : son de la source uniquement.

## Hashtags (base, à ajuster par clip)
#gta6 #gta6gameplay #gta6fr #gaming #rockstargames #gtavi
