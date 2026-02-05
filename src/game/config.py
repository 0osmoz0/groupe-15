"""Constantes globales du jeu (écran, manettes, timings)."""
import pygame

# Fenêtre
WIDTH, HEIGHT = 1920, 1080

# Manettes
JOY_DEADZONE = 0.35
JOY_BTN_JUMP = 0      # X (PS4) / A (Xbox)
JOY_BTN_SPECIAL = 1   # Cercle / B
JOY_BTN_ATTACK = 2    # Carré / X
JOY_BTN_GRAB = 3      # Triangle / Y
JOY_BTN_COUNTER = 4   # L1 / LB
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

# Debug
DEBUG_JOYSTICK = True
DEBUG_HUD_BLACK = False
