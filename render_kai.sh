#!/bin/bash
# Rend les clips Kai Cenat un par un, puis normalise le loudness vers out/kai/.
set -uo pipefail
cd /home/user/gta-6/remotion
mkdir -p out/raw_kai /home/user/gta-6/out/kai
IDS=$(python3 -I -c "import json;print(' '.join(c['id'] for c in json.load(open('public/kai-meta.json'))))")
for id in $IDS; do
  short=${id#kai-}
  [ -f "/home/user/gta-6/out/kai/$short.mp4" ] && { echo "== $short deja fait"; continue; }
  echo "===== RENDU $short $(date +%H:%M:%S) ====="
  npx remotion render "$id" "out/raw_kai/$short.mp4" --browser-executable=/opt/pw-browsers/chromium_headless_shell --concurrency=2 --log=error 2>&1 | tail -3
  if [ -f "out/raw_kai/$short.mp4" ]; then
    (cd /home/user/gta-6 && python3 -I clip_pipeline.py normalize "remotion/out/raw_kai/$short.mp4" --out out/kai 2>&1 | tail -1)
  else
    echo "!! echec $short"
  fi
done
echo "===== TERMINE $(date +%H:%M:%S) ====="
