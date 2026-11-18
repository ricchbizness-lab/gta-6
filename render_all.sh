#!/bin/bash
# Rend chaque clip Remotion un par un, puis normalise le loudness vers out/.
set -uo pipefail
cd /home/user/gta-6/remotion
mkdir -p out/raw
IDS=$(python3 -I -c "import json;print(' '.join(c['id'] for c in json.load(open('public/clips-meta.json'))))")
for id in $IDS; do
  if [ -f "/home/user/gta-6/out/$id.mp4" ]; then echo "== $id déjà fait, saut"; continue; fi
  echo "===== RENDU $id  $(date +%H:%M:%S) ====="
  npx remotion render "$id" "out/raw/$id.mp4" \
    --browser-executable=/opt/pw-browsers/chromium_headless_shell \
    --concurrency=2 --log=error 2>&1 | tail -3
  if [ -f "out/raw/$id.mp4" ]; then
    echo "----- loudness $id -----"
    (cd /home/user/gta-6 && python3 -I clip_pipeline.py normalize \
       "remotion/out/raw/$id.mp4" --out out 2>&1 | tail -2)
  else
    echo "!! échec rendu $id"
  fi
done
echo "===== TERMINÉ $(date +%H:%M:%S) ====="
