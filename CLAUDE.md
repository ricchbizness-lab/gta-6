# Clip Studio — instructions pour Claude Code

Objectif : transformer une longue vidéo (live/VOD de 30 min et plus) en shorts verticaux 9:16
de qualité "monteur", prêts à publier sur TikTok / Reels / YouTube Shorts.
Tu fais TOUT le travail de production. L'humain valide les moments choisis (étape 4) et le résultat final.

## Règles non négociables
- Source : uniquement la vidéo fournie dans `input/`. Ne télécharge jamais de contenu tiers de ta propre initiative.
  Si l'humain donne une URL, vérifie d'abord dans `brief.md` que la campagne ou le créateur autorise ce clipping.
- Lis `brief.md` (règles de la campagne) AVANT toute chose et résume-moi les contraintes en 5 lignes
  (CTA obligatoire, hashtags, langue, durée, plateformes, interdits comme "pas d'IA", etc.).
- Si le brief interdit le contenu généré par IA : tu n'utilises l'IA que pour CHOISIR les moments.
  Aucun visuel ni voix généré. Montage, sous-titres et effets calculés restent OK.
- Tu ne publies rien. Tu produis des fichiers dans `out/`.
- Ne jamais écraser `input/` (originaux en lecture seule). Tout le reste va dans `work/`, `clips/`, `out/`.
- Demande avant d'installer un paquet global.

## Dossiers
- `input/`  vidéos sources (jamais modifiées)
- `work/`   audio.ogg, proxy.mp4, transcript.(json|srt|txt)
- `clips/raw/` découpes brutes depuis l'original
- `out/`    montages finaux (.mp4 1080x1920) + `captions.txt` par clip (titre, description, hashtags)
- `brief.md` règles de la campagne (fournies par l'humain)

## Outils
- `python clip_pipeline.py prep|transcribe|cut` (voir le docstring du fichier)
- `bash fetch_input.sh` : télécharge la vidéo source depuis `VIDEO_URL` (URL présignée) vers `input/`.
- Montage : Remotion (npm, installé dans le projet `remotion/`), ffmpeg pour tout le reste.
- Pour "voir" une vidéo : extrais des frames avec ffmpeg depuis `work/proxy.mp4`
  (ex. `ffmpeg -ss 00:12:34 -i work/proxy.mp4 -frames:v 1 f.jpg`) puis ouvre-les avec l'outil de lecture d'images.

## Contexte d'exécution : session cloud Claude Code (pas ton PC)
- VM Linux : 4 vCPU, 16 Go RAM, ~30 Go de disque, **pas de GPU**. Transcription : `--model small --device cpu`.
- Les plugins de marketplace NE sont PAS chargés en session cloud : n'essaie pas `/plugin`. Utilise ffmpeg et Remotion directement.
- Réseau : niveau Trusted + domaines ajoutés par l'humain. Pas d'accès à YouTube/Twitch. Si un téléchargement est refusé,
  dis-le et demande à l'humain de fournir l'URL présignée, ne contourne pas.
- Limites de temps : une commande de premier plan dure au plus 10 min ; lance les tâches longues
  (transcription, rendu) en arrière-plan (`nohup ... > work/log.txt 2>&1 &`) et vérifie le log. Une session inactive se met en pause.
- Rends les clips un par un (concurrency Remotion basse) ; vérifie l'espace disque (`df -h`) avant un gros lot.
- Les fichiers de la VM ne sont pas sur le PC de l'humain : committe les livrables légers (`out/*.mp4`, `out/*.txt`, `clips.json`)
  sur une branche dédiée du dépôt, jamais la vidéo source (ajoute `input/` et `work/` au .gitignore).

## Workflow (dans cet ordre, avec points d'arrêt)
1. **Brief** : lis `brief.md`, résume les contraintes.
2. **Prep** : `python clip_pipeline.py prep input/<video> --out work`
   (audio léger + proxy 540p : on analyse sur ces copies légères, jamais sur l'original).
3. **Transcription** : `python clip_pipeline.py transcribe work/audio.ogg --out work --model small --lang <langue>`
   (GPU présent : `--model large-v3-turbo --device cuda`). Vérifie la qualité sur 3 passages.
4. **Sélection des moments** : lis `work/transcript.txt`, repère 8 à 12 candidats de 15 à 45 s
   (rire, réaction forte, chaos, retournement, punchline, premières réactions). Pour chaque candidat plausible,
   regarde 3 à 5 frames du proxy autour du moment (skill `watch` ou ffmpeg) pour vérifier qu'il y a de l'action visible.
   Écris `clips.json` : `[{"id","start","end","hook","cta","why","score"}]`.
   Règles : une idée par clip, aucun contexte nécessaire au-delà de 3 s, début sur l'action, fin nette.
   **STOP : présente la liste à l'humain et attends sa validation.**
5. **Découpe** : `python clip_pipeline.py cut input/<video> clips.json --out clips/raw`
   (réencodage par défaut = précis à l'image près).
6. **Montage Remotion** (1080x1920, 30 fps), pour chaque clip :
   - Recadrage 9:16 : suivi du sujet / facecam si présent, sinon plan gameplay + blur en fond.
   - Hook texte dans les 2 premières secondes (court, lisible sans le son).
   - Sous-titres mot par mot depuis `work/transcript.json` (mots horodatés), style gras contrasté, zone sûre (hors UI plateformes : ~150 px en haut, ~320 px en bas).
   - 2 à 4 punch-ins sur les temps forts, léger shake sur l'impact, étalonnage léger, transitions nettes.
   - Sons d'impact discrets seulement si ça sert le gag. Loudness normalisée (-14 LUFS).
   - CTA parlé ou écrit en fin de clip, conforme au brief (nom du créateur, où regarder la suite).
   Rends dans `out/<id>.mp4`.
7. **Contrôle qualité** (par clip, avant de me le présenter) : extrais 4 frames et vérifie visuellement ;
   ffprobe : 1080x1920, durée 15–60 s ; hook visible < 2 s ; CTA présent ; sous-titres lisibles et corrects ;
   pas de coupure au milieu d'un mot ; son non saturé. Corrige puis seulement après, présente.
8. **Livrables** : pour chaque clip, `out/<id>.mp4` + `out/<id>.txt` (titre, description, hashtags du brief).
   Termine par un tableau : id, durée, hook, raison du choix, points à vérifier.

## Style de travail
- Commence chaque étape par une phrase, puis exécute. Pas de roman.
- Si une étape échoue deux fois, arrête et explique plutôt que de contourner.
- Qualité > quantité : 6 excellents clips valent mieux que 12 moyens.
