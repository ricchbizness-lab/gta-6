#!/bin/bash
# Télécharge la vidéo source dans input/ depuis une URL présignée (S3 / R2 / GCS).
# Usage : VIDEO_URL="https://..." bash fetch_input.sh [nom.mp4]
set -euo pipefail

name="${1:-source.mp4}"
[ -n "${VIDEO_URL:-}" ] || { echo "Définis VIDEO_URL (URL présignée de la vidéo)."; exit 1; }

# Lien de partage Dropbox : force le téléchargement direct (dl=0 -> dl=1, ou ajoute dl=1)
case "${VIDEO_URL}" in
  *dropbox.com*)
    if [[ "${VIDEO_URL}" == *"dl=0"* ]]; then
      VIDEO_URL="${VIDEO_URL//dl=0/dl=1}"
    elif [[ "${VIDEO_URL}" != *"dl=1"* ]]; then
      sep="?"; [[ "${VIDEO_URL}" == *"?"* ]] && sep="&"
      VIDEO_URL="${VIDEO_URL}${sep}dl=1"
    fi
    ;;
esac

mkdir -p input
# -C - : reprise si le téléchargement est interrompu ; --retry : réessaie sur erreur réseau
curl -L --fail --retry 5 --retry-delay 3 -C - -o "input/${name}" "${VIDEO_URL}"

ls -lh "input/${name}"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "input/${name}"
