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

---

# Casting voix — révision du 2026-11-20

Arthur jugé trop âgé. Les voix n'ayant aucune métadonnée d'âge dans l'API,
j'ai classé les 36 voix masculines par hauteur fondamentale médiane mesurée
sur leurs aperçus (`analyse_voix.py`, résultats dans `work/voices/f0.json`).
Repères : <115 Hz grave/mature, 115-135 Hz moyenne, >135 Hz claire/jeune.

Têtes de classement : Cody 250,0 · Bram 205,1 · Evan 188,2 · Miles 188,2 ·
John 173,9 · Reid 170,2 · Dylan 150,2 · Callan 143,5 · Arthur 141,6 Hz.

## A_bram.mp4 — VOIX RETENUE
- voix    : `qwen_audio_tts`, voice_id `549ff70a-3ee7-4f04-a4d9-89a24fab7709`
            (Bram), voice_type `preset`, language `fr`,
            instruction "Voix off gaming, jeune homme, energique, complice,
            debit rapide", format wav, sample_rate 48000
- durée voix generee : 8,96 s pour 10 s -> tient sans accélération
- F0 mesurée sur le rendu : 164,9 Hz, contre 136,8 Hz pour Arthur
  (+28 Hz, environ 3 demi-tons plus haut)
- lit, remix et normalisation : identiques à A_qwen
- mesuré  : -14,6 LUFS, crête -1,0 dBFS
- Whisper : fr p=1.00, texte restitué conforme au script

## Crédits de la révision
| Étape | Coût |
|---|---|
| Echantillons Evan + Dylan (`text2speech_v2`) | 1,20 cr |
| Tentatives Qwen sur 5 voix hors liste blanche | 0,00 cr (rejet 400) |
| Voix Bram (`qwen_audio_tts`) | 0,07 cr |
| **Sous-total révision** | **1,27 cr** |

Solde : 35,21 -> 33,94 crédits. Cumul depuis le début du test : 2,94 cr.

## Limite constatée
`qwen_audio_tts` n'accepte qu'une liste blanche de voix non documentée :
Arthur et Bram passent, Cody / Evan / Miles / Reid / Dylan sont refusés en 400.
Le rejet ne coûte rien, donc tester Qwen avant ElevenLabs est toujours gagnant
(0,07 cr contre 0,60 cr quand ça passe).

---

# B_bram.mp4 — version retenue (2026-11-20)

L'utilisateur a entendu un décalage sur `A_bram.mp4`. Mesure à l'appui : la
méthode A désynchronise, la méthode B non.

## Mesure du synchronisme
Comparaison des instants d'attaque de mots-ancres, version contre audio d'origine :

| version | écart moyen | écart max | verdict |
|---|---|---|---|
| A_bram (remix) | -1,85 s | 2,66 s | désynchronisé |
| **B_bram (voice_change)** | **-0,01 s** | **0,04 s** | **synchrone** |

Cause du décalage de A : la voix générée démarre à 0 s et parle d'une traite,
alors que les sous-titres incrustés placent "sur GTA 6" à 2,2 s et
"légendaire" à 6,4 s. Aucun réglage de remix ne corrige ça sans découper la
voix segment par segment.

## Paramètres de B_bram.mp4
- `voice_change` (`voice_change_merge`), video_id `feca1b65-...` (extrait 10 s)
- voice_id `549ff70a-3ee7-4f04-a4d9-89a24fab7709` (Bram), voice_type `preset`
- sortie brute -23,98 LUFS -> normalisée -14,0 LUFS (`clip_pipeline.py normalize`)
- mesuré : -14,1 LUFS, crête -1,4 dBFS, 720x1280, 10,00 s
- texte et minutage d'origine conservés -> les sous-titres incrustés restent calés

## Coût
`voice_change` 10 s : 1,00 cr. Extrapolation 64 s : environ 6,4 cr.
