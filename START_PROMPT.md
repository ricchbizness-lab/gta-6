# Clip Studio — session cloud Claude Code

## Préparation (une seule fois)

1. **Dépôt GitHub privé** : pousse ce dossier (CLAUDE.md, clip_pipeline.py, fetch_input.sh, setup.sh, brief.md)
   et attache le dépôt à ta session cloud sur claude.ai/code.
   Ajoute un `.gitignore` avec `input/`, `work/`, `clips/`, `node_modules/`.
2. **Environnement cloud** (claude.ai/code, sélecteur d'environnement, "modifier") :
   - **Setup script** : colle le contenu de `setup.sh`.
   - **Network access** : *Custom*, coche "Also include default list of common package managers",
     et ajoute : `huggingface.co`, `*.hf.co` (modèle Whisper) et, si tu utilises Dropbox,
     `dropbox.com`, `*.dropbox.com`, `*.dropboxusercontent.com`.
     (S3, GCS et R2 sont déjà dans la liste par défaut : l'URL présignée de ta vidéo passe sans rien ajouter.)
3. **Envoi de la vidéo** — au choix :
   - **Dropbox** : mets la vidéo dans Dropbox, crée un lien de partage ("toute personne disposant du lien")
     et garde-le pour le prompt. Supprime le lien une fois la vidéo récupérée.
   - **Bucket** (R2 / S3 / GCS) : génère une **URL présignée à durée courte** (24 h).
   Ne mets jamais ce lien dans le dépôt.
4. `brief.md` : colle les règles de la campagne et commit.

## Prompt de démarrage (à coller dans la session)

```
Lis CLAUDE.md et brief.md. Je veux des shorts à partir d'une vidéo dont l'URL présignée est :
<URL_PRESIGNEE>
(créateur : <NOM>, langue : <en|fr>, plateformes : TikTok / Reels / Shorts)

Pour ce premier test, travaille uniquement sur les 5 premières minutes de la vidéo.

Avant de commencer :
1. Vérifie l'environnement (ffmpeg, faster-whisper, node) et l'accès réseau à huggingface.co et au bucket.
   Dis-moi ce qui manque, sans contourner.
2. Résume les contraintes du brief en 5 lignes.

Ensuite enchaîne seul : fetch_input.sh, prep, transcribe (en arrière-plan si besoin), puis propose 8 à 12 moments
dans clips.json (hook, CTA, raison, score) et ARRÊTE-TOI pour ma validation.
Après validation : découpe, montage Remotion, contrôle qualité sur chaque clip, livrables dans out/ commités sur une branche.
Une phrase par étape, pas de roman.
```

## Récupérer les clips finis
Les clips (`out/*.mp4`, quelques dizaines de Mo) sont committés sur une branche du dépôt :
télécharge-les depuis GitHub ou demande à la session de te les renvoyer.
