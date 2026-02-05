"""Gestion des entrées clavier et manette (joysticks, état joueur, attaques)."""
import pygame
from game.config import JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_ATTACK, JOY_BTN_GRAB, JOY_BTN_COUNTER, JOY_BTN_SPECIAL
from game.config import DEBUG_JOYSTICK

_last_joystick_count = -1
_joystick_ever_seen = False
_joystick_rescan_frames = 0


def init_joysticks(player1, player2, force_log=False):
    """Initialise les manettes et assigne joy_id aux joueurs."""
    global _last_joystick_count
    n = pygame.joystick.get_count()
    for i in range(n):
        try:
            pygame.joystick.Joystick(i).init()
        except Exception:
            pass
    player1.joy_id = 0 if n >= 1 else None
    player2.joy_id = 1 if n >= 2 else None
    if DEBUG_JOYSTICK and (force_log or n != _last_joystick_count):
        _last_joystick_count = n
        print(f"[Manettes] Détectées: {n}")
        for i in range(n):
            try:
                j = pygame.joystick.Joystick(i)
                print(f"  Joystick {i}: {j.get_name()!r}")
            except Exception as e:
                print(f"  Joystick {i}: erreur {e}")


def tick_joystick_rescan(player1, player2):
    """Re-scan périodique si aucune manette n'a jamais été vue."""
    global _joystick_ever_seen, _joystick_rescan_frames
    n = pygame.joystick.get_count()
    if n > 0:
        _joystick_ever_seen = True
        _joystick_rescan_frames = 0
    elif not _joystick_ever_seen:
        _joystick_rescan_frames += 1
        if _joystick_rescan_frames >= 60:
            _joystick_rescan_frames = 0
            pygame.joystick.quit()
            pygame.joystick.init()
            try:
                pygame.event.clear()
            except Exception:
                pass
            init_joysticks(player1, player2, force_log=True)
    init_joysticks(player1, player2)


def get_player_input_state(player):
    """Retourne (left, right, up, down) depuis clavier ou manette."""
    joy_id = getattr(player, "joy_id", None)
    if joy_id is not None and joy_id < pygame.joystick.get_count():
        try:
            joy = pygame.joystick.Joystick(joy_id)
            ax0 = joy.get_axis(0) if joy.get_numaxes() > 0 else 0.0
            ax1 = joy.get_axis(1) if joy.get_numaxes() > 1 else 0.0
            left = ax0 < -JOY_DEADZONE
            right = ax0 > JOY_DEADZONE
            up = ax1 < -JOY_DEADZONE
            down = ax1 > JOY_DEADZONE
            if joy.get_numhats() > 0:
                hx, hy = joy.get_hat(0)
                if hx < 0: left = True
                if hx > 0: right = True
                if hy > 0: up = True
                if hy < 0: down = True
            return (left, right, up, down)
        except Exception:
            pass
    keys = pygame.key.get_pressed()
    return (
        keys[player.controls["left"]],
        keys[player.controls["right"]],
        keys[player.controls["jump"]],
        keys[player.controls.get("down", pygame.K_s)],
    )


def start_attack_from_input(player, hitboxes, jab, ftilt, utilt, dtilt, nair, fair, bair, uair, dair):
    """Lance l'attaque appropriée selon l'entrée (sol / air)."""
    left, right, up, down = get_player_input_state(player)
    on_ground = getattr(player, "on_ground", True)
    facing_right = getattr(player, "facing_right", True)
    if on_ground:
        if up: player.start_attack(utilt, hitboxes)
        elif down: player.start_attack(dtilt, hitboxes)
        elif left or right: player.start_attack(ftilt, hitboxes)
        else: player.start_attack(jab, hitboxes)
    else:
        if up: player.start_attack(uair, hitboxes)
        elif down: player.start_attack(dair, hitboxes)
        elif (right and facing_right) or (left and not facing_right): player.start_attack(fair, hitboxes)
        elif (left and facing_right) or (right and not facing_right): player.start_attack(bair, hitboxes)
        else: player.start_attack(nair, hitboxes)
