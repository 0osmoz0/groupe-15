#!/bin/bash
# Convertit les MP3 de victoire Judy en WAV pour pygame.mixer.Sound (qui ne gère pas le MP3).
# À lancer depuis la racine du projet : ./scripts/convert_judy_win_to_wav.sh
# Recommandé : installer ffmpeg (brew install ffmpeg) pour un meilleur support des formats.

DIR="$(cd "$(dirname "$0")/.." && pwd)"
JUDY_DIR="$DIR/src/assets/song/JudyWin"
cd "$JUDY_DIR" || exit 1

convert_one() {
  local src="$1"
  local wav="${src%.mp3}.wav"
  [ ! -f "$src" ] && echo "Fichier absent: $src" && return 1
  if command -v ffmpeg &>/dev/null; then
    ffmpeg -y -i "$src" -acodec pcm_s16le -ar 44100 "$wav" &>/dev/null && echo "OK: $src -> $wav" && return 0
  fi
  if command -v afconvert &>/dev/null; then
    afconvert -f WAVE -d LEI16 "$src" "$wav" 2>/dev/null && echo "OK: $src -> $wav" && return 0
  fi
  echo "Échec: $src (installez ffmpeg: brew install ffmpeg)"
  return 1
}

ok=0
for mp3 in winJudy.mp3 WinJudy3.mp3; do
  convert_one "$mp3" && ok=1
done
[ "$ok" -eq 0 ] && echo "Aucune conversion. Installez ffmpeg: brew install ffmpeg" && exit 1
exit 0
