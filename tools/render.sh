#!/usr/bin/env bash
# Rebuild output/word-choice-final.mp4 from the source video.
# Usage: tools/render.sh source.mp4 output.mp4
set -euo pipefail
SRC="$1"; OUT="$2"; DIR="$(cd "$(dirname "$0")" && pwd)"
AF="highpass=f=75,afftdn=nr=8:nf=-50:tn=1,equalizer=f=250:t=q:w=1.2:g=-1.5,equalizer=f=4000:t=q:w=1.5:g=1.5,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=160:makeup=2,alimiter=limit=-3dB:attack=3:release=60:level=disabled,loudnorm=I=-15:TP=-1.5:LRA=7:measured_I=-16.42:measured_TP=-3.00:measured_LRA=4.60:measured_thresh=-28.99:offset=-0.26:linear=true,aresample=48000"
python3 "$DIR/overlay.py" | ffmpeg -y -i "$SRC" -f rawvideo -pix_fmt rgba -s 1080x280 -r 30 -i - \
  -filter_complex "[0:v]eq=contrast=1.04:brightness=0.005:saturation=1.04:gamma=1.01,unsharp=5:5:0.35:5:5:0,format=yuv420p[base];[base][1:v]overlay=0:960:format=auto:eof_action=pass,format=yuv420p[v]" \
  -map "[v]" -map 0:a -af "$AF" -c:v libx264 -preset slow -crf 16 -profile:v high -level 4.2 -pix_fmt yuv420p -r 30 \
  -movflags +faststart -c:a aac -b:a 192k -ar 48000 -t 24.2 "$OUT"
