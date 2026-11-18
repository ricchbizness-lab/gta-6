#!/bin/bash
# Setup script de l'environnement cloud Claude Code (champ "Setup script" de l'environnement).
# Doit finir en moins de ~5 min et sortir en code 0 pour que l'environnement soit mis en cache.
apt-get update -y >/dev/null 2>&1 && apt-get install -y ffmpeg >/dev/null 2>&1 || true

pip install faster-whisper >/dev/null 2>&1 \
  || pip install --break-system-packages faster-whisper >/dev/null 2>&1 || true

# Pré-télécharge le modèle Whisper "small" dans le cache.
# Nécessite huggingface.co (et *.hf.co) dans les domaines autorisés de l'environnement.
python3 - <<'EOF' || true
from faster_whisper import WhisperModel
WhisperModel("small", device="cpu", compute_type="int8")
print("modele whisper small OK")
EOF

exit 0
