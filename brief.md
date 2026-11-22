# Brief — Clip Studio

Règles par défaut, mises à jour le 2026-11-20 sur instruction de l'humain.

## Campagne en cours : Kai Cenat GTA 6 Marathon (regles recues le 2026-11-22)
Paiement : seuil de 1 000 vues par video ; seules les videos approuvees comptent.
**Obligatoire**
- Source : stream/video/clip du marathon GTA de Kai Cenat a partir du 18/11/2026, chaines
  officielles (Twitch kaicenat, YouTube @KaiCenatLive / @KaiCenatGaming).
- Kai Cenat = sujet principal de la video (facecam en haut, jamais seulement en intro).
- Plateformes : TikTok, Instagram Reels, YouTube Shorts, X. Rien d'autre.
- Le **texte a l'ecran ou la legende doit citer "Kai Cenat"** (on fait les deux).
- Hashtag **#KAICENAT** obligatoire dans la legende.
- Audience du compte : au moins 50 % de pays anglophones natifs (US, CA, AU, UK, NZ),
  et un compte dont la niche est coherente (gaming / streamers).
**Interdit**
- Montrer Kai sous un jour negatif, creer une fausse narration negative ("hate farm").
- Manipuler vues ou engagement (bots, reposts, collabs).
- **Aucun logo** (pas de watermark, pas de logo de chaine ; on recadre aussi les
  compteurs Twitch/YouTube du stream).
- Miniatures repetitives ou sans rapport, legendes en japonais.
- Reposter un Short deja publie par les chaines de Kai : chaque clip est notre propre coupe.
**Choix de production**
- Langue : anglais (hooks, sous-titres, legendes). Aucune IA generative.
- Image : VOD Twitch officielle v2932305259 en 1080p ; son de la VOD (passages non muets).
- Format : facecam en haut, jeu en bas, 1080x1920, -14 LUFS, sans chat ni compteur.

## Provenance des sources
- `input/source.mp4` — gameplay GTA 6 FR fourni par l'humain (Dropbox, 18/11).
- `input/amintech_0.mp4`, `_1.mp4`, `_2.mp4` — shorts GTA 6 (argent, reglages,
  premier million), fournis par l'humain le 20/11. Le nom de fichier d'origine
  portait le pseudo "amintechfr" et la voix off dit "moi c'est Amin".
  Revoicing effectue sur instruction explicite de l'humain.
  Formats 720x1280, 58,6 s / 55,7 s / 75,2 s, sous-titres incrustes.
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
