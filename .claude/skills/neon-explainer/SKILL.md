---
name: neon-explainer
description: Fabrique un short vertical 9:16 (TikTok/Reels/Shorts) au format "neon explainer" (voix off rapide, titres neon manuscrits, cartes animees, parties numerotees, grille synthwave, question binaire + carte createur). Seul le branding change d'une video a l'autre (brand.json). Utiliser quand on demande "une video dans le style amintech", "un short explicatif neon", "3 trucs a savoir sur X", ou un short pedagogique rapide avec cartes.
---

# Neon explainer : short explicatif rapide, branding interchangeable

Format reproduit d'apres l'analyse de `amintech_2.mp4` (mesures dans `reference/style_bible.md`).
On reproduit les **codes** (rythme, structure, mise en page), jamais les assets d'un autre createur
(pas son nom, son logo, sa musique, ses captures).

## Fichiers
- `remotion/src/neon/` : gabarit (types.ts, NeonShort.tsx, Cards.tsx, anim.ts, fonts.ts). Composition `neon-<id>`.
- `tools/neon/build.py <id>` : voix -> transcription -> calage des scenes -> fonds -> props + `remotion/public/neon/projects.json`.
- `tools/neon/render.sh <id>` : rendu Remotion + normalisation -14 LUFS -> `out/neon/<id>.mp4`.
- `tools/neon/make_sfx.py` : regenere pop/impact/whoosh (deja dans `remotion/public/neon/sfx/`).
- Exemple complet : `projects/vicebeach/` (brand.json + script.json + voice_raw.wav).

## Procedure
1. **Branding** : copier `projects/vicebeach/brand.json` vers `projects/<id>/brand.json`, changer
   `name`, `tagline`, `tags`, `chapterLabel` (PARTIE / ETAPE / PART), couleurs, police titre
   (`kaushan` = brush, `pacifico` = neon script, `bebas` = condense). `avatar` optionnel (chemin dans `remotion/public/`), sinon initiales.
   Contraste : `primary` clair et sature (glow), `panel` sombre opaque >= 0.9.
2. **Script** (`script.json`), structure qui marche (voir style bible) :
   hook chiffre ou avant/apres (< 2 s) -> promesse ("3 trucs que personne ne te dit") ->
   3 a 5 parties numerotees, 1 idee chacune -> question binaire "A ou B ? Dis-le en commentaire" -> abonne-toi.
   90 a 130 mots = 22 a 30 s a 290 mots/min. Phrases courtes, un mot fort par phrase.
3. **Voix** : `projects/<id>/voice_raw.wav` (voix de l'humain, ou TTS Higgsfield si autorise par brief.md :
   `qwen_audio_tts`, voix Bram id `549ff70a-3ee7-4f04-a4d9-89a24fab7709`, ~0,07 credit / 160 caracteres ;
   estimer le cout avant). build.py accelere vers `target_wpm` (atempo plafonne a 1,45).
4. **Scenes** : une scene par idee visuelle, 0,7 a 3 s. Champs :
   - `anchor` : 1-3 mots de la voix qui declenchent la scene (premiere occurrence apres la scene precedente ;
     prefixe accepte seulement pour un mot >= 5 lettres). Premiere scene sans ancre (t=0).
   - `chapter` : numero de partie (herite ensuite ; 0 = pas de pastille). `flash: true` au debut de chaque partie.
   - `title` : 1 a 4 mots, ecrit au neon (typewriter).
   - `bg` : index dans `backgrounds` (fonds floutes extraits des sources a `t` secondes).
   - `card` : `stat` (icon, label, sub, value | countTo+prefix, lock), `compare`, `badge` (n), `checklist`
     (title, items[{label, state: done|locked|cross}]), `levels`, `gauge` (left, right, value 0-1, verdict),
     `image` (`frame: {source, t}` extrait auto, ou `src`), `choice` (a, b), `icon`, `creator` (outro).
   - `caption_fixes` : corrections de transcription `[["mal entendu","correct"]]` (noms propres surtout).
   - Optionnel : `music` (chemin d'une piste libre de droits, bouclee) + `music_volume` (0.18), `sfx` (true), `tail` (0.8 s).
5. `python3 -I tools/neon/build.py <id>` puis verifier le calage : lire la table start/titre affichee,
   rendre 6-8 stills (`npx remotion still neon-<id> f.jpg --frame=N --browser-executable=/opt/pw-browsers/chromium_headless_shell`)
   et regarder chevauchements carte/sous-titre, titres coupes, cartes vides.
6. `bash tools/neon/render.sh <id>` (en arriere-plan si > 40 s de video).
7. QC : ffprobe 1080x1920 30 fps ; `clip_pipeline.py` normalize donne -14 LUFS / crete <= -1 dBTP ;
   4 frames verifiees ; sous-titres = texte de la voix ; question + abonne-toi presents.
8. Livrer `out/neon/<id>.mp4` + `out/neon/<id>.txt` (titre, description, hashtags).

## Images des sources (regle validee par l'humain)
- Des qu'un article source contient de vraies captures du jeu, on les met dans la video (carte `image` avec
  `src` + `caption: "Image : <auteur reel>"`). Lire les legendes : creditter l'auteur de la capture
  (ex. la chaine YouTube citee), pas seulement le site.
- Ecarter : images generees par IA (illustrations "trop belles", texte incruste), captures d'articles, logos.
- Domaines bloques : proposer l'ajout exact du domaine a l'environnement (update_environment), jamais de contournement.
- Fichiers dans `remotion/public/neon/ext_<id>/` (ignore par git : on ne committe pas les images de tiers).
- Avec credit, l'image fait 450 px de haut (sinon 520) pour ne pas toucher les sous-titres.

## Miniature + intro (facon Kai)
- `script.json` -> `thumb` : `{image, focus, kicker, lines:[{text, color: white|primary|badge|negative, size, font}], arrow}`.
  3 lignes max, une idee : l'interdit / la consequence. Verifier que la phrase dit bien la meme chose que l'astuce.
- `bash tools/neon/intro.sh <id>` : rend `out/neon/<id>_miniature.png` (couverture a uploader) et
  `out/neon/<id>_intro.mp4` (miniature 0,9 s -> flash blanc -> video). A lancer apres render.sh.

## Zones (1080x1920, ne pas deplacer sans raison)
Pastille partie y190-310 · titre neon y470-760 · carte y820 (badge y760), hauteur max ~550 ·
sous-titres bas a y1490 (1-3 mots, mot a venir en transparence) · grille synthwave y1540-1920.
Les images de carte sont plafonnees a 520 px de haut pour ne pas toucher les sous-titres.

## Pieges connus
- Une ancre trop courte ("pas", "un") accroche le mauvais mot : prendre 2 mots ou un mot rare.
- Whisper ecrit mal les marques ("Buckmy") : `caption_fixes`.
- Pas de musique fournie par defaut : sans piste, le rendu reste propre (voix + SFX) mais moins "energique".
- Rendre un projet a la fois (concurrency 2), verifier `df -h` avant un lot.
