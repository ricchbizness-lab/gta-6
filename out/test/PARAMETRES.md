# Test voix off — crabe_geant.mp4, 10 premières secondes

Source : `input/crabe_geant.mp4` (720x1280, 63,8 s) — extrait 0-10 s.
Script dit par les voix A : `script_new.txt`, bloc 1.
Date : 2026-11-20.

## Crédits Higgsfield réellement dépensés

| Étape | Modèle | Coût |
|---|---|---|
| Voix A1 | `qwen_audio_tts` | 0,07 cr |
| Voix A2 | `text2speech_v2` (variant `elevenlabs`) | 0,60 cr |
| Séparation de pistes | `separate_stems` (htdemucs) | 0,00 cr |
| Méthode B | `voice_change` (`voice_change_merge`) | 1,00 cr |
| **Total** | | **1,67 cr** |

Solde : 36,88 -> 35,21 crédits. Devis annoncé avant dépense : 1,67 cr. Écart : aucun.

## A_qwen.mp4 — méthode A, moteur Qwen  [RECOMMANDÉ]
- voix    : `qwen_audio_tts`, voice_id `30fc8796-...` (Arthur), voice_type `preset`
            language `fr`, instruction "Voix off YouTube gaming, dynamique, complice,
            debit rapide", format wav, sample_rate 48000
- durée voix generee : 9,04 s pour une fenêtre de 10 s -> tient sans retouche
- lit     : `no_vocals.flac` (htdemucs, mode two) a gain 0,3
- remix   : `clip_pipeline.py remix` — voix loudnorm 2 passes vers -14 LUFS,
            image copiee sans reencodage, duree calee sur l'image
- mesuré  : -13,9 LUFS, crête -2,1 dBFS

## A_elevenlabs.mp4 — méthode A, moteur ElevenLabs
- voix    : `text2speech_v2`, variant `elevenlabs`, même voice_id
- durée voix generee : 12,28 s pour 10 s -> **accélérée x1,228** par `--fit`
- reste identique a A_qwen
- mesuré  : -14,1 LUFS, crête -1,3 dBFS

## B_voicechange.mp4 — méthode B
- `voice_change`, video_id de l'extrait uploadé, même voice_id, voice_type `preset`
- sortie brute a -21,96 LUFS -> normalisée a -14,0 LUFS par `clip_pipeline.py normalize`
- mesuré apres normalisation : -14,1 LUFS, crête -2,1 dBFS
- **conserve le texte d'origine** : voice_change ne remplace que le timbre,
  pas les mots. Le script de `script_new.txt` n'est pas utilisé ici.

## Vérifications automatiques
Chaque sortie a été repassée dans faster-whisper pour contrôler la prononciation :
- A_qwen       : fr p=1.00, texte restitué conforme au nouveau script
- A_elevenlabs : fr p=1.00, texte restitué conforme au nouveau script
- B            : fr p=0.99, texte restitué = ancien script, avec des déformations
                 ("crâne géant" au lieu de "crabe géant", "mitraide exclusif")

## Contenu généré par IA
Les trois versions contiennent une voix de synthèse. À déclarer comme média
synthétique à la publication sur TikTok, YouTube et Instagram.
