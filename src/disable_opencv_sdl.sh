#!/bin/bash
# À lancer UNE FOIS avant le jeu sur Mac pour que les manettes marchent.
# Désactive la SDL2 d'OpenCV (conflit avec pygame = une seule manette ou aucune).
# Usage: cd src && chmod +x disable_opencv_sdl.sh && ./disable_opencv_sdl.sh

cd "$(dirname "$0")"
D=""
[ -d "venv" ] && D="venv/lib"
[ -z "$D" ] && [ -d "../venv" ] && D="../venv/lib"
if [ -z "$D" ]; then
  echo "Venv non trouve. Lance depuis le dossier src."
  exit 1
fi
for py in python3.9 python3.10 python3.11 python3.12; do
  orig="$D/$py/site-packages/cv2/.dylibs/libSDL2-2.0.0.dylib"
  bak="$orig.disabled_for_joystick"
  if [ -f "$orig" ]; then
    mv "$orig" "$bak" && echo "OK: SDL OpenCV desactivee. Les manettes devraient marcher." || echo "Erreur mv"
    exit 0
  fi
  if [ -f "$bak" ]; then
    echo "Deja fait (fichier desactive present). Lance le jeu."
    exit 0
  fi
done
echo "Fichier libSDL2 non trouve dans cv2. Lance le jeu quand meme."
