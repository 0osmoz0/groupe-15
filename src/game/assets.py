"""Chargement des assets (cartes, GIFs, HUD, plateformes, polices)."""
import os
import pygame

try:
    from PIL import Image, ImageSequence
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False


def load_gif_frames(path, scale_size=None):
    """Charge les frames d'un GIF animé. Retourne liste de (Surface, duration_ms)."""
    if not _HAS_PIL:
        try:
            surf = pygame.image.load(path).convert_alpha()
            if scale_size:
                surf = pygame.transform.smoothscale(surf, scale_size)
            return [(surf, 50)]
        except Exception:
            return []
    frames = []
    try:
        with Image.open(path) as gif:
            for frame in ImageSequence.Iterator(gif):
                f = frame.convert("RGBA")
                size = f.size
                data = f.tobytes()
                surf = pygame.image.frombytes(data, size, "RGBA")
                surf = surf.convert_alpha()
                if scale_size:
                    surf = pygame.transform.smoothscale(surf, scale_size)
                duration = 50
                if hasattr(frame, "info") and "duration" in frame.info:
                    duration = max(20, frame.info["duration"])
                frames.append((surf, duration))
    except Exception:
        try:
            surf = pygame.image.load(path).convert_alpha()
            if scale_size:
                surf = pygame.transform.smoothscale(surf, scale_size)
            return [(surf, 50)]
        except Exception:
            return []
    return frames if frames else []


class GameAssets:
    """Contient tous les assets chargés (cartes, GIFs, HUD, counter, etc.)."""
    def __init__(self, base_dir: str, screen_size: tuple, world_size: tuple):
        self.base_dir = base_dir
        self.screen_w, self.screen_h = screen_size
        self.world_w, self.world_h = world_size
        self._load_maps()
        self._load_gifs()
        self._load_menu()
        self._load_counter()
        self._load_ping()
        self._load_portraits()
        self._load_life_icons()
        self._load_font()
        self._load_platforms()
        self._load_smog()

    def _load_smog(self):
        """Fumée d'impact (smog/1.png à 9.png) affichée aléatoirement quand un joueur reçoit un coup."""
        self.smog_surfaces = []
        smog_dir = os.path.join(self.base_dir, "assets", "smog")
        self.smog_display_size = (160, 160)
        for i in range(1, 10):
            path = os.path.join(smog_dir, f"{i}.png")
            try:
                img = pygame.image.load(path).convert()
                img.set_colorkey((0, 0, 0))
                self.smog_surfaces.append(
                    pygame.transform.smoothscale(img, self.smog_display_size)
                )
            except Exception:
                pass
        if not self.smog_surfaces:
            self.smog_surfaces = [None]

    def _load_maps(self):
        bg_dir = os.path.join(self.base_dir, "assets", "background map")
        bp_dir = os.path.join(self.base_dir, "assets", "BG_perso")
        map_files = ("BG.png", "2.png", "3.png", "4.png")
        self.map_labels = ("Sahara Square", "Rainforest District", "Zootopie", "Tundra")
        self.map_surfaces = []
        for name in map_files:
            path = os.path.join(bg_dir, name)
            try:
                img = pygame.image.load(path).convert()
                self.map_surfaces.append(
                    pygame.transform.smoothscale(img, (self.world_w, self.world_h))
                )
            except Exception:
                if self.map_surfaces:
                    self.map_surfaces.append(self.map_surfaces[0].copy())
                else:
                    fallback = pygame.Surface((self.world_w, self.world_h))
                    fallback.fill((40, 40, 60))
                    self.map_surfaces.append(fallback)
        if not self.map_surfaces:
            self.map_surfaces = [pygame.Surface((self.world_w, self.world_h))]
            self.map_surfaces[0].fill((40, 40, 60))
        self.background = self.map_surfaces[0].copy()
        try:
            bg_map = pygame.image.load(os.path.join(bg_dir, "BG_map.png")).convert()
            self.map_select_background = pygame.transform.smoothscale(bg_map, (self.screen_w, self.screen_h))
        except Exception:
            try:
                bg_map = pygame.image.load(os.path.join(bp_dir, "1_7.png")).convert()
                self.map_select_background = pygame.transform.smoothscale(bg_map, (self.screen_w, self.screen_h))
            except Exception:
                self.map_select_background = None

    def _load_gifs(self):
        bp = os.path.join(self.base_dir, "assets", "BG_perso")
        scale = (self.screen_w, self.screen_h)
        self.nick_win_frames = load_gif_frames(os.path.join(self.base_dir, "assets", "Nick", "win_nick", "1.gif"), scale_size=scale)
        self.judy_win_frames = load_gif_frames(os.path.join(self.base_dir, "assets", "JUDY_HOPPS", "judy_win", "1 (1).gif"), scale_size=scale)
        self.versus_gif_frames = load_gif_frames(os.path.join(bp, "1 (4).gif"), scale_size=scale)
        self.p1_confirm_gif_frames = load_gif_frames(os.path.join(bp, "1 (5).gif"), scale_size=scale)
        self.enter_gif_frames = load_gif_frames(os.path.join(bp, "1 (2).gif"), scale_size=scale)
        self.enter_then_a_gif_frames = load_gif_frames(os.path.join(bp, "1 (3).gif"), scale_size=scale)
        try:
            title_img = pygame.image.load(os.path.join(bp, "1.png")).convert()
            self.title_screen = pygame.transform.smoothscale(title_img, (self.screen_w, self.screen_h))
        except Exception:
            try:
                title_img = pygame.image.load(os.path.join(bp, "1_7.png")).convert()
                self.title_screen = pygame.transform.smoothscale(title_img, (self.screen_w, self.screen_h))
            except Exception:
                self.title_screen = None
        try:
            char_bg = pygame.image.load(os.path.join(bp, "1_7.png")).convert()
            self.character_select_background = pygame.transform.smoothscale(char_bg, (self.screen_w, self.screen_h))
        except Exception:
            self.character_select_background = None

    def _load_menu(self):
        menu_dir = os.path.join(self.base_dir, "assets", "menu")
        try:
            bg = pygame.image.load(os.path.join(menu_dir, "background menu", "menu.jpg")).convert()
            self.menu_background = pygame.transform.smoothscale(bg, (self.screen_w, self.screen_h))
        except Exception:
            self.menu_background = None
        try:
            tit = pygame.image.load(os.path.join(menu_dir, "background menu", "title.png")).convert_alpha()
            tw = int(self.screen_w * 0.36)
            th = max(1, int(tit.get_height() * tw / tit.get_width()))
            self.menu_title_image = pygame.transform.smoothscale(tit, (tw, th))
        except Exception:
            self.menu_title_image = None
        btn_dir = os.path.join(menu_dir, "button")
        for attr, fname in (("menu_button_play_bg", "fond_play.png"), ("menu_button_param_bg", "PARAM.png"), ("menu_button_exit_bg", "exit.png")):
            try:
                img = pygame.image.load(os.path.join(btn_dir, fname)).convert_alpha()
                setattr(self, attr, img)
            except Exception:
                setattr(self, attr, None)
        try:
            pygame.mixer.music.load(os.path.join(self.base_dir, "assets", "song", "menu", "Recording 2026-02-04 215949.mp3"))
            self.menu_music_loaded = True
        except Exception:
            self.menu_music_loaded = False
        self.combat_music_path = os.path.join(
            self.base_dir, "assets", "song", "combat",
            "Sonic Unleashed Final Boss - Dark Gaia Phase 2 - Endless Possibility.mp3"
        )
        self.combat_music_loaded = os.path.isfile(self.combat_music_path)
        self.win_music_path = os.path.join(
            self.base_dir, "assets", "song", "win",
            "Fanfare du Héros.mp3"
        )
        self.win_music_loaded = os.path.isfile(self.win_music_path)
        # Sons de victoire Judy en WAV (pygame.mixer.Sound ne gère pas le MP3)
        # Utiliser scripts/convert_judy_win_to_wav.sh pour générer les .wav depuis les .mp3
        self.judy_win_sound_paths = [
            os.path.join(self.base_dir, "assets", "song", "JudyWin", "winJudy.wav"),
            os.path.join(self.base_dir, "assets", "song", "JudyWin", "WinJudy3.wav"),
        ]
        self.judy_win_sounds_loaded = [
            os.path.isfile(p) for p in self.judy_win_sound_paths
        ]
        # Son de victoire Nick (en plus de la fanfare) — WAV recommandé (Sinon MP3 peut ne pas marcher avec Sound())
        self.nick_win_sound_path_wav = os.path.join(self.base_dir, "assets", "song", "nick win", "nick_win.wav")
        self.nick_win_sound_path_mp3 = os.path.join(
            self.base_dir, "assets", "song", "nick win",
            "[Fandub] Zootopie - La Rencontre de Judy et Nick (mp3cut (mp3cut.net).mp3"
        )
        self.nick_win_sound_loaded = (
            os.path.isfile(self.nick_win_sound_path_wav) or os.path.isfile(self.nick_win_sound_path_mp3)
        )
        self.nick_win_sound_path = (
            self.nick_win_sound_path_wav if os.path.isfile(self.nick_win_sound_path_wav) else self.nick_win_sound_path_mp3
        )

    def _load_counter(self):
        """Countdown 3-2-1-GO : charge les assets counter/3.png, 2.png, 1.png, go.png."""
        self.counter_height = 180
        counter_dir = os.path.join(self.base_dir, "assets", "counter")
        order = ("3.png", "2.png", "1.png", "go.png")
        self.counter_surfaces = []
        for fname in order:
            try:
                img = pygame.image.load(os.path.join(counter_dir, fname)).convert_alpha()
                h = self.counter_height
                w = max(1, int(img.get_width() * h / img.get_height()))
                self.counter_surfaces.append(pygame.transform.smoothscale(img, (w, h)))
            except Exception:
                self.counter_surfaces.append(None)

    def _load_ping(self):
        ping_dir = os.path.join(self.base_dir, "assets", "Ping")
        self.ping_height = 60
        try:
            p1 = pygame.image.load(os.path.join(ping_dir, "P1.png")).convert_alpha()
            self.ping_p1 = pygame.transform.smoothscale(p1, (int(p1.get_width() * self.ping_height / p1.get_height()), self.ping_height))
        except Exception:
            self.ping_p1 = None
        try:
            p2 = pygame.image.load(os.path.join(ping_dir, "P2.png")).convert_alpha()
            self.ping_p2 = pygame.transform.smoothscale(p2, (int(p2.get_width() * self.ping_height / p2.get_height()), self.ping_height))
        except Exception:
            self.ping_p2 = None
        self.ping_offset_above = 15

    def _load_portrait_no_black(self, path):
        """Charge un portrait et rend le fond noir transparent (colorkey)."""
        surf = pygame.image.load(path).convert()
        surf.set_colorkey((0, 0, 0))
        w = int(surf.get_width() * self.portrait_height / surf.get_height())
        return pygame.transform.smoothscale(surf, (w, self.portrait_height))

    def _load_portraits(self):
        self.portrait_height = 200
        self.portrait_side_margin = 20
        self.hud_bottom_y_offset = 35
        try:
            path = os.path.join(self.base_dir, "assets", "JUDY_HOPPS", "PP_judy.png", "PP.png")
            self.judy_portrait = self._load_portrait_no_black(path)
        except Exception:
            self.judy_portrait = None
        try:
            path = os.path.join(self.base_dir, "assets", "Nick", "nick_PP", "PP.png")
            self.nick_portrait = self._load_portrait_no_black(path)
        except Exception:
            self.nick_portrait = None

    def _load_life_icons(self):
        """Charge les icônes PV (vies) pour Judy et Nick."""
        self.life_icon_size = 44
        size = (self.life_icon_size, self.life_icon_size)
        try:
            j = pygame.image.load(os.path.join(self.base_dir, "assets", "JUDY_HOPPS", "vie", "Pv_juddy.png")).convert()
            j.set_colorkey((0, 0, 0))
            self.life_icon_judy = pygame.transform.smoothscale(j, size)
        except Exception:
            self.life_icon_judy = None
        try:
            n = pygame.image.load(os.path.join(self.base_dir, "assets", "Nick", "pv", "pv_nick.png")).convert()
            n.set_colorkey((0, 0, 0))
            self.life_icon_nick = pygame.transform.smoothscale(n, size)
        except Exception:
            self.life_icon_nick = None

    def _load_font(self):
        for name in ("arial", "Arial", "Liberation Sans", "DejaVu Sans", "sans-serif"):
            try:
                self.font_percent = pygame.font.SysFont(name, 48, bold=True)
                break
            except Exception:
                continue
        else:
            self.font_percent = pygame.font.Font(None, 64)

    def _load_platforms(self):
        plat_dir = os.path.join(self.base_dir, "assets", "plaform")
        main_w, main_h = 1000, 25
        small_w, small_h = 220, 18
        try:
            g = pygame.image.load(os.path.join(plat_dir, "Grande.png")).convert_alpha()
            gh = max(25, int(g.get_height() * main_w / g.get_width()))
            self.main_platform_size = (main_w, gh)
            self.main_platform_image = pygame.transform.smoothscale(g, self.main_platform_size)
        except Exception:
            self.main_platform_size = (main_w, 25)
            self.main_platform_image = None
        stretch = 1.12
        try:
            p = pygame.image.load(os.path.join(plat_dir, "PETITE.png")).convert_alpha()
            ph = max(18, int(p.get_height() * small_w / p.get_width()))
            self.small_platform_size = (int(small_w * stretch), int(ph * stretch))
            self.small_platform_image = pygame.transform.smoothscale(p, self.small_platform_size)
        except Exception:
            self.small_platform_size = (small_w, 18)
            self.small_platform_image = None
