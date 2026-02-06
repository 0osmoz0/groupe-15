#!/bin/bash
# Lance le jeu sur macOS en forçant la SDL de pygame (manettes 1 et 2).
# Usage : depuis le dossier groupe-15 : ./src/run_mac.sh
#         ou : cd src && ./run_mac.sh

cd "$(dirname "$0")"

if [ -d "venv" ]; then
    VENV="venv"
elif [ -d "../venv" ]; then
    VENV="../venv"
else
    VENV=""
fi

if [ -n "$VENV" ]; then
    PYTHON="$VENV/bin/python"
    for _py in python3.9 python3.10 python3.11 python3.12; do
        PYGAME_LIBS="$VENV/lib/$_py/site-packages/pygame/.dylibs"
        if [ -d "$PYGAME_LIBS" ]; then
            export DYLD_LIBRARY_PATH="${PYGAME_LIBS}${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
            break
        fi
    done
else
    PYTHON="python3"
fi

exec "$PYTHON" main.py
