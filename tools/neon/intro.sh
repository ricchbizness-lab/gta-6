#!/bin/bash
# Intro facon Kai : miniature plein ecran 0,9 s -> flash blanc -> video.
# bash tools/neon/intro.sh <id>   (necessite out/neon/<id>.mp4 ; rend la miniature depuis neon-<id>-thumb)
set -euo pipefail
id=$1; R=/home/user/gta-6
cd $R/remotion
npx remotion still "neon-$id-thumb" "$R/out/neon/${id}_miniature.png" --browser-executable=/opt/pw-browsers/chromium_headless_shell --log=error
cd $R
T=$(python3 -c "import subprocess;d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','out/neon/$id.mp4']));print(round(d+0.75,3))")
ffmpeg -nostdin -y -loglevel error \
  -loop 1 -t 0.9 -framerate 30 -i "out/neon/${id}_miniature.png" -i "out/neon/$id.mp4" \
  -filter_complex "[0:v]fps=30,format=yuv420p,setsar=1,settb=1/30[a];[1:v]fps=30,format=yuv420p,setsar=1,settb=1/30[b];[a][b]xfade=transition=fadewhite:duration=0.15:offset=0.75[v];[1:a]adelay=750|750[aa]" \
  -map "[v]" -map "[aa]" -t "$T" -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k -movflags +faststart "out/neon/${id}_intro.mp4"
ffprobe -v error -show_entries format=duration -of csv=p=0 "out/neon/${id}_intro.mp4"
