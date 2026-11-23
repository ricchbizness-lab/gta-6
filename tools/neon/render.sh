#!/bin/bash
# Rend un projet neon puis normalise a -14 LUFS : bash tools/neon/render.sh <id>
set -euo pipefail
cd /home/user/gta-6/remotion
mkdir -p out/neon /home/user/gta-6/out/neon
npx remotion render "neon-$1" "out/neon/$1.mp4" --browser-executable=/opt/pw-browsers/chromium_headless_shell --concurrency=2 --log=error
cd /home/user/gta-6 && python3 -I clip_pipeline.py normalize "remotion/out/neon/$1.mp4" --out out/neon | tail -1
