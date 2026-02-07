"""
Constantes globales : résolution, mapping des boutons manette (type Xbox/PS),
timings caméra / countdown / GIFs, et flags de debug manette.
"""
import pygame

# Résolution cible (le mode plein écran peut redimensionner)
WIDTH, HEIGHT = 1920, 1080

# Manettes : zone morte et facteur clavier
JOY_DEADZONE = 0.35
KEYBOARD_MOVE_MULT = 0.5
# Boutons (0=A/X, 1=B/Cercle, 2=X/Carré, 3=Y/Triangle, 5=L1, 7=L2, 9=Start)
JOY_BTN_JUMP = 0
JOY_BTN_SPECIAL = 1
JOY_BTN_ATTACK = 2
JOY_BTN_GRAB = 3
JOY_BTN_COUNTER = 5
JOY_BTN_COUNTER_ALT = 7
JOY_BTN_START = 9

# Caméra : plus la valeur est basse, plus le suivi est fluide
CAMERA_LERP = 0.08

# Countdown 3-2-1-GO (ms)
COUNTDOWN_DURATION_MS = 1000

# Durées d’attente après les différentes GIF (versus, enter, etc.)
WAIT_AFTER_GIF_MS = 2000
WAIT_AFTER_P1_CONFIRM_MS = 2000
WAIT_AFTER_ENTER_GIF_MS = 2000
WAIT_AFTER_ENTER_THEN_A_MS = 2000

# Debug : logs manette (init, rescan, events)
DEBUG_JOYSTICK = True
DEBUG_JOYSTICK_VERBOSE = True
DEBUG_JOYSTICK_VERBOSE_INTERVAL = 30
DEBUG_HUD_BLACK = False
