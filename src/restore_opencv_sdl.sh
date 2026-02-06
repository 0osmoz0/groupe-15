#!/bin/bash
# Restaure la SDL2 d'OpenCV si elle a ete renommee par main.py (pour que l'intro video refonctionne).
# Usage: depuis src/  ->  chmod +x restore_opencv_sdl.sh && ./restore_opencv_sdl.sh

cd "$(dirname "$0")"
D=""
[ -d "venv" ] && D="venv/lib"
[ -z "$D" ] && [ -d "../venv" ] && D="../venv/lib"
if [ -z "$D" ]; then
  echo "Venv non trouve (venv ou ../venv)."
  exit 1
fi
for py in python3.9 python3.10 python3.11 python3.12; do
  dir="$D/$py/site-packages/cv2/.dylibs"
  bak="$dir/libSDL2-2.0.0.dylib.disabled_for_joystick"
  orig="$dir/libSDL2-2.0.0.dylib"
  if [ -f "$bak" ]; then
    mv "$bak" "$orig" && echo "SDL OpenCV restauree: $orig" || echo "Erreur mv"
    exit 0
  fi
done
echo "Aucun fichier .disabled_for_joystick trouve (rien a restaurer)."
