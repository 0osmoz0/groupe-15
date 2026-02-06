"""Constantes globales du jeu (écran, manettes, timings)."""
import pygame

# Fenêtre
WIDTH, HEIGHT = 1920, 1080

# Manettes (zone morte : plus élevé = moins sensible ; 0.35 = sensibilité normale)
JOY_DEADZONE = 0.35
# Clavier (facteur vitesse déplacement : plus bas = moins sensible, 0.5 = à fond)
KEYBOARD_MOVE_MULT = 0.5
JOY_BTN_JUMP = 0      # X (PS4) / A (Xbox)
JOY_BTN_SPECIAL = 1   # Cercle / B
JOY_BTN_ATTACK = 2    # Carré / X
JOY_BTN_GRAB = 3      # Triangle / Y
JOY_BTN_COUNTER = 5   # L1 / LB — Parade (contre) — pas 4 (Share sur PS4)
JOY_BTN_COUNTER_ALT = 7   # L2 / LT — Parade alternative
JOY_BTN_START = 9     # Options (PS4) / Menu (Xbox)

# Caméra
CAMERA_LERP = 0.08

# Countdown
COUNTDOWN_DURATION_MS = 1000

# Timings GIF
WAIT_AFTER_GIF_MS = 2000
WAIT_AFTER_P1_CONFIRM_MS = 2000
WAIT_AFTER_ENTER_GIF_MS = 2000
WAIT_AFTER_ENTER_THEN_A_MS = 2000

# Debug manette (True = logs init, rescan, erreurs)
DEBUG_JOYSTICK = True
# Debug ultra-verbose : résumé toutes les 30 frames (get_count, cache, _get_joy_input) + chaque event manette
DEBUG_JOYSTICK_VERBOSE = True
# Intervalle des logs verbose (frames) — 30 = ~0.5 s à 60 FPS
DEBUG_JOYSTICK_VERBOSE_INTERVAL = 30
DEBUG_HUD_BLACK = False
