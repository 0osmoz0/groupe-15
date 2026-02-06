"""
Point d'entrée du jeu. Initialise pygame, crée le contexte et les écrans, puis lance la boucle principale.
La logique des états (map select, character select, countdown, GIF, win, playing) est déléguée au package game.
"""
import os
import sys
import time

# Permettre les events manette même si la fenêtre n’a pas le focus (macOS / SDL)
os.environ.setdefault("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1")

# macOS : desactiver la SDL2 d'opencv pour n'avoir que celle de pygame (sinon 2 manettes ne marchent pas)
if sys.platform == "darwin":
    _venv = getattr(sys, "prefix", None) or os.path.dirname(os.path.dirname(sys.executable))
    for _py in ("python3.9", "python3.10", "python3.11", "python3.12"):
        _sdl = os.path.join(_venv, "lib", _py, "site-packages", "cv2", ".dylibs", "libSDL2-2.0.0.dylib")
        if os.path.isfile(_sdl):
            try:
                _bak = _sdl + ".disabled_for_joystick"
                if not os.path.isfile(_bak):
                    os.rename(_sdl, _bak)
            except Exception:
                pass
            break
    # Chercher aussi dans sys.path au cas ou le venv a un autre layout
    for _sp in sys.path:
        _sdl2 = os.path.join(_sp, "cv2", ".dylibs", "libSDL2-2.0.0.dylib")
        if os.path.isfile(_sdl2):
            try:
                _bak2 = _sdl2 + ".disabled_for_joystick"
                if not os.path.isfile(_bak2):
                    os.rename(_sdl2, _bak2)
            except Exception:
                pass
            break

import pygame

# --- Init Pygame : fenêtre AVANT joystick (obligatoire sur macOS pour que la manette soit détectée) ---
pygame.init()
pygame.font.init()
# Créer la fenêtre en premier (sinon get_count() reste à 0 sur macOS)
screen = pygame.display.set_mode((1920, 1080), 0)
pygame.joystick.init()
# Laisser le temps au système d’enregistrer la manette et pomper les événements
for _ in range(35):
    pygame.event.pump()
    time.sleep(0.05)
pygame.joystick.quit()
pygame.joystick.init()
for _ in range(10):
    pygame.event.pump()
    time.sleep(0.03)
try:
    pygame.mixer.init()
except Exception:
    pass
time.sleep(0.2)

from game.config import (
    WIDTH, HEIGHT, JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_START, DEBUG_JOYSTICK,
)
from player.player import Player
from smash_platform.game_platform import Platform
from menu import MainMenu, SettingsMenu, ControlsMenu
from game.context import GameContext
from game.input_handling import init_joysticks, tick_joystick_rescan, get_joystick_poll_events, tick_debug_joy_frame, safe_event_get
from game.input_handling import _update_effective_joy_count as _update_joy_count_once
from game.screens import (
    MapSelectScreen,
    CharacterSelectScreen,
    JudyNickIntroVideoScreen,
    CountdownScreen,
    VersusGifScreen,
    WaitP1EnterScreen,
    VersusGifP1ConfirmScreen,
    EnterGifScreen,
    EnterThenAGifScreen,
    NickWinScreen,
    JudyWinScreen,
    PlayingScreen,
)

# Repasser en 1920x1080 (plein écran si activé)
fullscreen_mode = True
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if fullscreen_mode else 0)
# Ré-init manette après création de la fenêtre finale (macOS)
pygame.joystick.quit()
pygame.joystick.init()
for _ in range(10):
    pygame.event.pump()
    time.sleep(0.02)
# Attendre jusqu'à 2 s qu'au moins une manette soit détectée (Bluetooth peut être lent)
for _ in range(10):
    if pygame.joystick.get_count() >= 1:
        break
    pygame.joystick.quit()
    pygame.joystick.init()
    for __ in range(5):
        pygame.event.pump()
        time.sleep(0.02)
    time.sleep(0.2)
n_joy_start = pygame.joystick.get_count()
if DEBUG_JOYSTICK:
    print(f"[Manette DBG] Démarrage: get_count()={n_joy_start} (après attente 2s max)")
if n_joy_start == 0 and sys.platform == "darwin":
    print("[Manette] Aucune manette détectée. Sur macOS, lancez une fois: ./disable_opencv_sdl.sh")
clock = pygame.time.Clock()
screen_w, screen_h = screen.get_size()
world_w, world_h = screen_w * 2, screen_h * 2
base_dir = os.path.dirname(os.path.abspath(__file__))

# --- Contexte (assets + état) ---
ctx = GameContext(screen, clock, base_dir, (screen_w, screen_h), (world_w, world_h))
ctx.fullscreen_mode = fullscreen_mode
ctx.window_size = (WIDTH, HEIGHT)

# --- Joueurs ---
player1 = Player(
    start_pos=(world_w // 2 - 200, world_h // 2),
    color=(255, 0, 0),
    controls={"left": pygame.K_q, "right": pygame.K_d, "jump": pygame.K_SPACE, "down": pygame.K_s, "attacking": pygame.K_f, "special": pygame.K_e, "grab": pygame.K_g, "counter": pygame.K_h},
    screen_size=(world_w, world_h),
)
player2 = Player(
    start_pos=(world_w // 2 + 200, world_h // 2),
    color=(0, 0, 255),
    controls={"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP, "down": pygame.K_DOWN, "attacking": pygame.K_m, "special": pygame.K_i, "grab": pygame.K_o, "counter": pygame.K_j},
    screen_size=(world_w, world_h),
    character="nick",
)
ctx.player1 = player1
ctx.player2 = player2
ctx.players = pygame.sprite.Group(player1, player2)
ctx.hitboxes = pygame.sprite.Group()

# --- Plateformes ---
a = ctx.assets
wc_x, wc_y = world_w // 2, world_h // 2
platforms = pygame.sprite.Group()
platforms.add(
    Platform(a.main_platform_size, (wc_x - a.main_platform_size[0] // 2, wc_y + 200), image=a.main_platform_image, surface_offset=int(a.main_platform_size[1] * 0.42) if a.main_platform_image else 0),
    Platform(a.small_platform_size, (wc_x - 350 - a.small_platform_size[0] // 2, wc_y - 150), one_way=True, image=a.small_platform_image, surface_offset=int(a.small_platform_size[1] * 0.38)),
    Platform(a.small_platform_size, (wc_x + 350 - a.small_platform_size[0] // 2, wc_y - 150), one_way=True, image=a.small_platform_image, surface_offset=int(a.small_platform_size[1] * 0.38)),
)
ctx.platforms = platforms

_update_joy_count_once()  # nombre effectif (collant à 2) avant premier init_joysticks
init_joysticks(player1, player2)
if DEBUG_JOYSTICK:
    print(f"[Manette] Après init_joysticks: get_count()={pygame.joystick.get_count()}, P1.joy_id={player1.joy_id}, P2.joy_id={player2.joy_id}")

# --- Menus (existant) ---
main_menu = MainMenu(
    screen_w, screen_h,
    ("VERSUS", "PARAMETRES", "QUITTER"),
    title="SMASH",
    title_image=a.menu_title_image,
    background=a.menu_background,
    big_rect_background=a.menu_button_play_bg,
    big_rect_background_param=a.menu_button_param_bg,
    big_rect_background_quit=a.menu_button_exit_bg,
    joy_deadzone=JOY_DEADZONE,
    joy_confirm_buttons=(JOY_BTN_JUMP, JOY_BTN_START),
)
settings_menu = SettingsMenu(screen_w, screen_h, get_fullscreen=lambda: ctx.fullscreen_mode, joy_deadzone=JOY_DEADZONE, joy_confirm_buttons=(JOY_BTN_JUMP, JOY_BTN_START))
controls_menu = ControlsMenu(screen_w, screen_h, player1.controls, player2.controls, joy_deadzone=JOY_DEADZONE, joy_confirm_buttons=(JOY_BTN_JUMP, JOY_BTN_START))

# --- Écrans de jeu (POO) ---
map_select_screen = MapSelectScreen()
character_select_screen = CharacterSelectScreen()
judy_nick_intro_video_screen = JudyNickIntroVideoScreen()
countdown_screen = CountdownScreen()
versus_gif_screen = VersusGifScreen()
wait_p1_enter_screen = WaitP1EnterScreen()
versus_gif_p1_confirm_screen = VersusGifP1ConfirmScreen()
enter_gif_screen = EnterGifScreen()
enter_then_a_screen = EnterThenAGifScreen()
nick_win_screen = NickWinScreen()
judy_win_screen = JudyWinScreen()
playing_screen = PlayingScreen()

# --- Boucle principale ---
_debug_joy_frames = 0
while ctx.running:
    tick_debug_joy_frame()
    tick_joystick_rescan(player1, player2)

    if ctx.game_state == "main_menu":
        _debug_joy_frames += 1
        if a.menu_music_loaded and not ctx.menu_music_playing:
            try:
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)
                ctx.menu_music_playing = True
            except Exception:
                pass
        events = safe_event_get()
        n_joy = pygame.joystick.get_count()
        # Fallback macOS : toujours ajouter les events du polling (get_axis/get_button)
        if n_joy > 0:
            events.extend(get_joystick_poll_events(0.2, (JOY_BTN_JUMP, JOY_BTN_START)))
        if DEBUG_JOYSTICK and _debug_joy_frames % 120 == 1:
            n_axis = sum(1 for e in events if e.type == pygame.JOYAXISMOTION)
            n_btn = sum(1 for e in events if e.type == pygame.JOYBUTTONDOWN)
            # Valeurs brutes du stick (pour vérifier si get_axis/get_button marchent sur macOS)
            raw = ""
            if n_joy > 0:
                try:
                    parts = []
                    for jid in range(min(2, n_joy)):
                        j = pygame.joystick.Joystick(jid)
                        ax0 = j.get_axis(0) if j.get_numaxes() > 0 else 0
                        ax1 = j.get_axis(1) if j.get_numaxes() > 1 else 0
                        b0 = j.get_button(0) if j.get_numbuttons() > 0 else 0
                        b9 = j.get_button(9) if j.get_numbuttons() > 9 else 0
                        parts.append(f"J{jid}: ax0={ax0:.2f} ax1={ax1:.2f} B0={b0} B9={b9}")
                    raw = " | " + " | ".join(parts)
                except Exception as e:
                    raw = f" | erreur: {e}"
            print(f"[Manette debug] get_count()={n_joy} | events: JOYAXIS={n_axis} JOYBUTTON={n_btn}{raw}")
        for event in events:
            if event.type == pygame.QUIT:
                if ctx.menu_music_playing:
                    try:
                        pygame.mixer.music.stop()
                        ctx.menu_music_playing = False
                    except Exception:
                        pass
                ctx.running = False
                break
            selected = main_menu.handle_event(event, n_joy)
            if selected == "QUITTER":
                if ctx.menu_music_playing:
                    try:
                        pygame.mixer.music.stop()
                        ctx.menu_music_playing = False
                    except Exception:
                        pass
                ctx.running = False
                break
            if selected == "VERSUS":
                ctx.game_state = "map_select"
                ctx.map_select_cursor = 0
                ctx.char_select_phase = "p1"
                ctx.char_select_cursor = 0
                ctx.p1_character_choice = None
                ctx.p2_character_choice = None
                break
            if selected == "PARAMETRES":
                ctx.game_state = "settings"
                break
        if not ctx.running:
            break
        main_menu.update(n_joy)
        if ctx.game_state == "main_menu":
            main_menu.draw(screen)
            pygame.display.flip()
            clock.tick(60)
            continue

    if ctx.game_state == "settings":
        events = safe_event_get()
        n_joy = pygame.joystick.get_count()
        if n_joy > 0:
            events.extend(get_joystick_poll_events(0.2, (JOY_BTN_JUMP, JOY_BTN_START)))
        for event in events:
            if event.type == pygame.QUIT:
                ctx.running = False
                break
            action = settings_menu.handle_event(event, n_joy)
            if action == "back":
                ctx.game_state = "main_menu"
                break
            if action == "controls":
                ctx.game_state = "controls"
                break
            if action == "toggle_fullscreen":
                ctx.fullscreen_mode = not ctx.fullscreen_mode
                ctx.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if ctx.fullscreen_mode else 0)
                break
        if not ctx.running:
            break
        settings_menu.update(n_joy)
        if ctx.game_state == "settings":
            settings_menu.draw(screen)
            pygame.display.flip()
            clock.tick(60)
            continue

    if ctx.game_state == "controls":
        events = safe_event_get()
        n_joy = pygame.joystick.get_count()
        if n_joy > 0:
            events.extend(get_joystick_poll_events(0.2, (JOY_BTN_JUMP, JOY_BTN_START)))
        for event in events:
            if event.type == pygame.QUIT:
                ctx.running = False
                break
            action = controls_menu.handle_event(event, n_joy)
            if action == "back":
                ctx.game_state = "settings"
                break
        if not ctx.running:
            break
        controls_menu.update(n_joy)
        if ctx.game_state == "controls":
            controls_menu.draw(screen)
            pygame.display.flip()
            clock.tick(60)
            continue

    if ctx.game_state == "title_screen":
        events = safe_event_get()
        n_joy_ts = pygame.joystick.get_count()
        if n_joy_ts > 0:
            events.extend(get_joystick_poll_events(0.2, (JOY_BTN_JUMP, JOY_BTN_START)))
        for event in events:
            if event.type == pygame.QUIT:
                ctx.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                ctx.game_state = "versus_gif"
                ctx.versus_gif_frame_index = 0
                ctx.versus_gif_timer_ms = 0
                ctx.versus_gif_phase = "playing"
                ctx.wait_after_gif_timer_ms = 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                ctx.game_state = "versus_gif_enter"
                ctx.enter_gif_frame_index = 0
                ctx.enter_gif_timer_ms = 0
                ctx.enter_gif_phase = "playing"
                ctx.wait_after_enter_gif_timer_ms = 0
            if event.type == pygame.JOYBUTTONDOWN and n_joy_ts > 0 and event.joy in (0, 1):
                if event.button == JOY_BTN_JUMP:
                    ctx.game_state = "versus_gif"
                    ctx.versus_gif_frame_index = 0
                    ctx.versus_gif_timer_ms = 0
                    ctx.versus_gif_phase = "playing"
                    ctx.wait_after_gif_timer_ms = 0
                elif event.button == JOY_BTN_START:
                    ctx.game_state = "versus_gif_enter"
                    ctx.enter_gif_frame_index = 0
                    ctx.enter_gif_timer_ms = 0
                    ctx.enter_gif_phase = "playing"
                    ctx.wait_after_enter_gif_timer_ms = 0
        if not ctx.running:
            break
        if ctx.game_state == "title_screen":
            if a.title_screen:
                screen.blit(a.title_screen, (0, 0))
            pygame.display.flip()
            clock.tick(60)
            continue

    if ctx.game_state == "map_select":
        map_select_screen.run(ctx)
        continue
    if ctx.game_state == "character_select":
        character_select_screen.run(ctx)
        continue
    if ctx.game_state == "intro_video":
        judy_nick_intro_video_screen.run(ctx)
        continue
    if ctx.game_state == "versus_gif":
        versus_gif_screen.run(ctx)
        continue
    if ctx.game_state == "wait_p1_enter":
        wait_p1_enter_screen.run(ctx)
        continue
    if ctx.game_state == "versus_gif_p1_confirm":
        versus_gif_p1_confirm_screen.run(ctx)
        continue
    if ctx.game_state == "versus_gif_enter":
        enter_gif_screen.run(ctx)
        continue
    if ctx.game_state == "versus_gif_enter_then_a":
        enter_then_a_screen.run(ctx)
        continue
    if ctx.game_state == "countdown":
        countdown_screen.run(ctx)
        continue
    if ctx.game_state == "nick_wins":
        nick_win_screen.run(ctx)
        continue
    if ctx.game_state == "judy_wins":
        judy_win_screen.run(ctx)
        continue
    if ctx.game_state == "playing":
        playing_screen.run(ctx)
        continue

pygame.quit()
