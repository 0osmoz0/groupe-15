"""
Point d'entrée du jeu. Initialise pygame, crée le contexte et les écrans, puis lance la boucle principale.
La logique des états (map select, character select, countdown, GIF, win, playing) est déléguée au package game.
"""
import os
import time
import pygame
from player.player import Player
from smash_platform.game_platform import Platform
from menu import MainMenu, SettingsMenu, ControlsMenu

from game.config import (
    WIDTH, HEIGHT, JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_START,
)
from game.context import GameContext
from game.input_handling import init_joysticks, tick_joystick_rescan
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

# --- Init Pygame ---
pygame.init()
pygame.font.init()
pygame.joystick.init()
try:
    pygame.mixer.init()
except Exception:
    pass

# Ne pas créer d'objet Joystick ici : évite segfault macOS (double init). init_joysticks() s'en charge.
time.sleep(0.3)
print(f"🎮 Manettes détectées : {pygame.joystick.get_count()}")

fullscreen_mode = True
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if fullscreen_mode else 0)
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
    controls={
        "left": pygame.K_q, 
        "right": pygame.K_d, 
        "jump": pygame.K_SPACE, 
        "down": pygame.K_s, 
        "attacking": pygame.K_f, 
        "special": pygame.K_e, 
        "grab": pygame.K_g, 
        "counter": pygame.K_h
    },
    screen_size=(world_w, world_h),
    joystick_id=0  # ✅ MANETTE 1
)
player2 = Player(
    start_pos=(world_w // 2 + 200, world_h // 2),
    color=(0, 0, 255),
    controls={
        "left": pygame.K_LEFT, 
        "right": pygame.K_RIGHT, 
        "jump": pygame.K_UP, 
        "down": pygame.K_DOWN, 
        "attacking": pygame.K_m, 
        "special": pygame.K_i, 
        "grab": pygame.K_o, 
        "counter": pygame.K_j
    },
    screen_size=(world_w, world_h),
    character="nick",
    joystick_id=1  # ✅ MANETTE 2
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
    Platform(
        a.main_platform_size, 
        (wc_x - a.main_platform_size[0] // 2, wc_y + 200), 
        image=a.main_platform_image, 
        surface_offset=int(a.main_platform_size[1] * 0.42) if a.main_platform_image else 0
    ),
    Platform(
        a.small_platform_size, 
        (wc_x - 350 - a.small_platform_size[0] // 2, wc_y - 150), 
        one_way=True, 
        image=a.small_platform_image, 
        surface_offset=int(a.small_platform_size[1] * 0.38)
    ),
    Platform(
        a.small_platform_size, 
        (wc_x + 350 - a.small_platform_size[0] // 2, wc_y - 150), 
        one_way=True, 
        image=a.small_platform_image, 
        surface_offset=int(a.small_platform_size[1] * 0.38)
    ),
)
ctx.platforms = platforms

# ✅ ASSOCIER LES MANETTES AUX JOUEURS
init_joysticks(player1, player2)

# --- Menus ---
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
settings_menu = SettingsMenu(
    screen_w, screen_h, 
    get_fullscreen=lambda: ctx.fullscreen_mode, 
    joy_deadzone=JOY_DEADZONE, 
    joy_confirm_buttons=(JOY_BTN_JUMP, JOY_BTN_START)
)
controls_menu = ControlsMenu(
    screen_w, screen_h, 
    player1.controls, 
    player2.controls, 
    joy_deadzone=JOY_DEADZONE, 
    joy_confirm_buttons=(JOY_BTN_JUMP, JOY_BTN_START)
)

# --- Écrans de jeu ---
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
while ctx.running:
    # ✅ RESCANNER LES MANETTES (pour hotplug)
    tick_joystick_rescan(player1, player2)
    
    if ctx.game_state == "main_menu":
        if a.menu_music_loaded and not ctx.menu_music_playing:
            try:
                pygame.mixer.music.set_volume(0.15)
                pygame.mixer.music.play(-1)
                ctx.menu_music_playing = True
            except Exception:
                pass
        
        try:
            events = pygame.event.get()
        except (KeyError, SystemError):
            events = []
        
        n_joy = pygame.joystick.get_count()
        
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
                ctx.selected_map_index = 0
                ctx.map_select_ignore_confirm_frame = True  # évite validation manette résiduelle (menu s'affiche)
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
        try:
            events = pygame.event.get()
        except (KeyError, SystemError):
            events = []
        
        n_joy = pygame.joystick.get_count()
        
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
                ctx.screen = pygame.display.set_mode(
                    (WIDTH, HEIGHT), 
                    pygame.FULLSCREEN if ctx.fullscreen_mode else 0
                )
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
        try:
            events = pygame.event.get()
        except (KeyError, SystemError):
            events = []
        
        n_joy = pygame.joystick.get_count()
        
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
        try:
            events = pygame.event.get()
        except (KeyError, SystemError):
            events = []
        
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
            
            # ✅ GÉRER LES MANETTES SUR L'ÉCRAN TITRE
            if event.type == pygame.JOYBUTTONDOWN:
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

    # ✅ DÉLÉGATION AUX ÉCRANS
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