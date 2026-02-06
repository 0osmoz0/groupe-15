"""Gestion des entrées clavier et manette (joysticks, état joueur, attaques)."""
import pygame
from game.config import (
    JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_ATTACK, JOY_BTN_GRAB, JOY_BTN_COUNTER, JOY_BTN_SPECIAL,
    DEBUG_JOYSTICK, DEBUG_JOYSTICK_VERBOSE, DEBUG_JOYSTICK_VERBOSE_INTERVAL,
)

_last_joystick_count = -1
_joystick_ever_seen = False
_frames_n_zero = 0  # nombre de frames consécutives avec get_count() == 0
FULL_RESCAN_AFTER_FRAMES = 2   # attendre 2 frames à 0 puis rescan à chaque frame
# Nombre "effectif" de manettes : reste à 2 pendant STICKY_JOY_FRAMES après un passage à 1 (évite de perdre P2 quand get_count() flicker sur macOS/Bluetooth)
_effective_joy_count = 0
_frames_joy_below_effective = 0
STICKY_JOY_FRAMES = 90  # ~1.5 s à 60 FPS : on garde 2 manettes pendant ce temps après que get_count() soit repassé à 1
# État précédent pour le polling (fallback quand les events SDL ne marchent pas sur macOS)
_poll_axis_prev = {}  # (joy_id, axis) -> value
_poll_button_prev = {}  # (joy_id, button) -> pressed
# Compteur de frame global pour logs verbose (incrémenté par main.py à chaque boucle)
_debug_joy_global_frame = 0


def safe_event_get():
    """Récupère les events pygame. Après un rescan joystick (quit+init), SDL peut être en erreur : on évite le crash."""
    try:
        return list(pygame.event.get())
    except (KeyError, SystemError):
        return []


def get_effective_joy_count():
    """Nombre de manettes à utiliser (collant à 2 quand on a déjà vu 2, pour éviter les flickers Bluetooth)."""
    return _effective_joy_count


def _update_effective_joy_count():
    """Met à jour _effective_joy_count à partir de get_count() (à appeler une fois par frame)."""
    global _effective_joy_count, _frames_joy_below_effective
    raw = pygame.joystick.get_count()
    if raw >= 2:
        _effective_joy_count = 2
        _frames_joy_below_effective = 0
    elif raw == 1:
        if _effective_joy_count == 2:
            _frames_joy_below_effective += 1
            if _frames_joy_below_effective >= STICKY_JOY_FRAMES:
                _effective_joy_count = 1
                _frames_joy_below_effective = 0
        else:
            _effective_joy_count = 1
    else:
        _effective_joy_count = 0
        _frames_joy_below_effective = 0


def tick_debug_joy_frame():
    """À appeler une fois par frame dans la boucle principale (pour logs verbose)."""
    global _debug_joy_global_frame
    _debug_joy_global_frame += 1
    return _debug_joy_global_frame


def init_joysticks(player1, player2, force_log=False):
    """Initialise les manettes et assigne joy_id aux joueurs (d'après le nombre effectif, collant à 2)."""
    global _last_joystick_count
    n_raw = pygame.joystick.get_count()
    n_effective = get_effective_joy_count()
    for i in range(n_raw):
        try:
            pygame.joystick.Joystick(i).init()
        except Exception as e:
            if DEBUG_JOYSTICK:
                print(f"  [Manettes] Joystick({i}).init() erreur: {e}")
    player1.joy_id = 0 if n_effective >= 1 else None
    player2.joy_id = 1 if n_effective >= 2 else None
    # Synchroniser l'objet joystick avec joy_id (ne créer Joystick(i) que si i < get_count(), sinon segfault macOS)
    n_now = pygame.joystick.get_count()
    for pl in (player1, player2):
        if getattr(pl, "joy_id", None) is None:
            if hasattr(pl, "joystick"):
                pl.joystick = None
        elif pl.joy_id >= n_now:
            if hasattr(pl, "joystick"):
                pl.joystick = None
        else:
            try:
                pl.joystick = pygame.joystick.Joystick(pl.joy_id)
                pl.joystick.init()
            except Exception:
                if hasattr(pl, "joystick"):
                    pl.joystick = None
    if DEBUG_JOYSTICK and (force_log or n_raw != _last_joystick_count):
        _last_joystick_count = n_raw
        print(f"[Manettes] get_count() = {n_raw} effective = {n_effective} -> P1.joy_id={player1.joy_id} P2.joy_id={player2.joy_id}")
        for i in range(n_raw):
            try:
                j = pygame.joystick.Joystick(i)
                print(f"  Joystick {i}: {j.get_name()!r} (axes={j.get_numaxes()}, buttons={j.get_numbuttons()}, hats={j.get_numhats()})")
            except Exception as e:
                print(f"  Joystick {i}: erreur {e}")


def _do_full_joystick_rescan():
    """Force une réénumération des manettes (quit+init). Donne à SDL le temps de voir les périphériques via event.pump()."""
    try:
        pygame.joystick.quit()
        pygame.joystick.init()
        for _ in range(8):
            pygame.event.pump()
    except Exception:
        pass


def tick_joystick_rescan(player1, player2):
    """Met à jour l'état manettes. Rescan (quit+init) uniquement quand get_count()=0 pour redétecter. Pas de refresh quand connecté : sur macOS ça fait figer."""
    global _joystick_ever_seen, _frames_n_zero, _poll_axis_prev, _poll_button_prev
    _update_effective_joy_count()
    n = pygame.joystick.get_count()
    if n > 0:
        _joystick_ever_seen = True
        _frames_n_zero = 0
    else:
        _frames_n_zero += 1
        if _frames_n_zero >= 2:
            _poll_axis_prev.clear()
            _poll_button_prev.clear()
        # Rescan à chaque frame quand 0 manette : quit+init + pump pour que SDL réénumère (macOS/Bluetooth)
        if _frames_n_zero >= FULL_RESCAN_AFTER_FRAMES:
            _do_full_joystick_rescan()
            n = pygame.joystick.get_count()
            if DEBUG_JOYSTICK and _frames_n_zero % 30 == FULL_RESCAN_AFTER_FRAMES:
                print(f"[Manette DBG] Rescan (get_count()=0 depuis {_frames_n_zero} frames) -> get_count()={n}")
            _update_effective_joy_count()
    init_joysticks(player1, player2)


def get_poll_axis(joy_id: int, axis: int) -> float:
    """Valeur d'axe depuis le cache du polling (fallback quand get_axis() ne marche pas pour la 2e manette)."""
    return _poll_axis_prev.get((joy_id, axis), 0.0)


def get_poll_button(joy_id: int, button: int) -> bool:
    """État bouton depuis le cache du polling."""
    return _poll_button_prev.get((joy_id, button), False)


def get_joystick_poll_events(deadzone: float, confirm_buttons: tuple = (0, 9)):
    """
    Fallback macOS : lit les manettes au polling et renvoie des events synthétiques
    (JOYAXISMOTION, JOYBUTTONDOWN) quand les events SDL ne sont pas livrés.
    """
    global _poll_axis_prev, _poll_button_prev
    out = []
    n = pygame.joystick.get_count()
    if DEBUG_JOYSTICK and n == 0:
        print("[Manette DBG] ATTENTION: get_joystick_poll_events() appelé alors que get_count()=0 -> cache vide, pas d'events.")
    for joy_id in range(n):
        try:
            j = pygame.joystick.Joystick(joy_id)
            j.init()
        except Exception:
            continue
        naxes = j.get_numaxes()
        nbuttons = j.get_numbuttons()
        for axis in range(min(2, naxes)):
            key = (joy_id, axis)
            val = j.get_axis(axis)
            # D-pad (hat) en secours si stick neutre
            if abs(val) < 0.5 and j.get_numhats() > 0:
                hx, hy = j.get_hat(0)
                if axis == 0 and hx != 0:
                    val = float(hx)
                elif axis == 1 and hy != 0:
                    val = -float(hy)  # pygame hat: up=1
            prev = _poll_axis_prev.get(key, 0.0)
            _poll_axis_prev[key] = val
            if abs(val) > deadzone and abs(prev) <= deadzone:
                out.append(pygame.event.Event(pygame.JOYAXISMOTION, joy=joy_id, axis=axis, value=val))
        for btn in confirm_buttons:
            if btn >= nbuttons:
                continue
            key = (joy_id, btn)
            pressed = j.get_button(btn)
            prev = _poll_button_prev.get(key, False)
            _poll_button_prev[key] = pressed
            if pressed and not prev:
                out.append(pygame.event.Event(pygame.JOYBUTTONDOWN, joy=joy_id, button=btn))
    if DEBUG_JOYSTICK_VERBOSE and _debug_joy_global_frame > 0 and _debug_joy_global_frame % DEBUG_JOYSTICK_VERBOSE_INTERVAL == 0:
        cache_axes = " ".join(f"J{j}a{a}={_poll_axis_prev.get((j, a), 0):.2f}" for j in range(2) for a in range(2))
        cache_btn0 = " ".join(f"J{j}B0={_poll_button_prev.get((j, 0), False)}" for j in range(2))
        print(f"[Manette VERBOSE] frame={_debug_joy_global_frame} poll: get_count()={n} | cache {cache_axes} | {cache_btn0} | events_générés={len(out)}")
    return out


def get_player_input_state(player):
    """Retourne (left, right, up, down) depuis clavier ou manette. Si le Player a _get_joy_input (manette directe), l'utiliser."""
    if callable(getattr(player, "_get_joy_input", None)):
        joy_in = player._get_joy_input()
        if joy_in is not None:
            return (joy_in[0], joy_in[1], joy_in[2], joy_in[3])
    n_joy = get_effective_joy_count()
    joy_id = getattr(player, "joy_id", None)
    if joy_id is not None and joy_id < n_joy and n_joy >= 1:
        ax0 = _poll_axis_prev.get((joy_id, 0), 0.0)
        ax1 = _poll_axis_prev.get((joy_id, 1), 0.0)
        left = ax0 < -JOY_DEADZONE
        right = ax0 > JOY_DEADZONE
        up = ax1 < -JOY_DEADZONE
        down = ax1 > JOY_DEADZONE
        if DEBUG_JOYSTICK_VERBOSE and _debug_joy_global_frame > 0 and _debug_joy_global_frame % DEBUG_JOYSTICK_VERBOSE_INTERVAL == 0:
            who = "P1" if joy_id == 0 else "P2"
            print(f"[Manette VERBOSE] frame={_debug_joy_global_frame} get_player_input_state({who}): joy_id={joy_id} ax0={ax0:.2f} ax1={ax1:.2f} -> L={left} R={right} U={up} D={down}")
        return (left, right, up, down)
    if DEBUG_JOYSTICK_VERBOSE and _debug_joy_global_frame > 0 and _debug_joy_global_frame % DEBUG_JOYSTICK_VERBOSE_INTERVAL == 0:
        who = "P1" if joy_id == 0 else "P2"
        reason = f"joy_id={joy_id} n_joy={n_joy}" if joy_id is not None else f"joy_id=None n_joy={n_joy}"
        print(f"[Manette VERBOSE] frame={_debug_joy_global_frame} get_player_input_state({who}): MANETTE IGNORÉE ({reason}) -> clavier")
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
