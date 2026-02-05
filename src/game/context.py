"""Contexte de jeu : écran, clock, assets, monde, joueurs, et tout l'état mutable (états, timers, curseurs)."""
import pygame
from game.assets import GameAssets


class GameContext:
    """Contient tout ce dont les écrans et la boucle de jeu ont besoin."""
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, base_dir: str,
                 screen_size: tuple, world_size: tuple):
        self.screen = screen
        self.clock = clock
        self.screen_w, self.screen_h = screen_size
        self.world_w, self.world_h = world_size
        self.assets = GameAssets(base_dir, screen_size, world_size)
        self.world_surface = pygame.Surface(world_size)
        self.running = True
        self.fullscreen_mode = True
        self.window_size = screen_size  # (WIDTH, HEIGHT) pour set_mode

        # Références remplies par main (joueurs, plateformes, hitboxes)
        self.player1 = None
        self.player2 = None
        self.players = None
        self.platforms = None
        self.hitboxes = None

        # Caméra
        self.camera_x = world_size[0] // 2 - screen_size[0] // 2
        self.camera_y = world_size[1] // 2 - screen_size[1] // 2

        # État global
        self.game_state = "main_menu"
        self.menu_music_playing = False

        # Map select
        self.selected_map_index = 0
        self.map_select_cursor = 0

        # Character select
        self.char_select_phase = "p1"
        self.char_select_cursor = 0
        self.p1_character_choice = None
        self.p2_character_choice = None
        self.characters = ("judy", "nick")
        self.character_labels = ("Judy Hopps", "Nick Wilde")

        # Countdown
        self.countdown_step = 0
        self.countdown_timer_ms = 0

        # Intro vidéo (Judy+Nick ou Nick+Judy)
        self.intro_video_filename = None

        # Versus GIF
        self.versus_gif_frame_index = 0
        self.versus_gif_timer_ms = 0
        self.versus_gif_phase = "playing"
        self.wait_after_gif_timer_ms = 0

        # Versus P1 confirm
        self.p1_confirm_frame_index = 0
        self.p1_confirm_timer_ms = 0
        self.p1_confirm_phase = "playing"
        self.wait_after_p1_confirm_timer_ms = 0

        # Enter GIF
        self.enter_gif_frame_index = 0
        self.enter_gif_timer_ms = 0
        self.enter_gif_phase = "playing"
        self.wait_after_enter_gif_timer_ms = 0

        # Enter then A GIF
        self.enter_then_a_frame_index = 0
        self.enter_then_a_timer_ms = 0
        self.enter_then_a_phase = "playing"
        self.wait_after_enter_then_a_timer_ms = 0

        # Win screens
        self.nick_win_frame_index = 0
        self.nick_win_frame_timer_ms = 0
        self.judy_win_frame_index = 0
        self.judy_win_frame_timer_ms = 0

    @property
    def background(self):
        return self.assets.background

    @background.setter
    def background(self, value):
        self.assets.background = value
