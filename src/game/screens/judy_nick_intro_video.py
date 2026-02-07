"""Écran de lecture des vidéos d'intro (1.mp4 Judy P1 / Nick P2, 1_2.mp4 Nick P1 / Judy P2).
Utilise OpenCV (cv2) pour lire les MP4. Import différé pour éviter conflit SDL2 avec pygame.
"""
import os
import pygame
from game.config import JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_START
from game.input_handling import get_joystick_poll_events, safe_event_get


def _import_cv2():
    """Import OpenCV au moment de lire la vidéo (évite conflit SDL2 / manettes)."""
    try:
        import cv2
        return cv2
    except (ImportError, OSError, Exception):
        return None


def _video_path_for(ctx, filename):
    """Chemin absolu vers la vidéo dans assets/BG_perso."""
    base = getattr(ctx.assets, "base_dir", None)
    if not base:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "assets", "BG_perso", filename)
    return os.path.abspath(path)


class JudyNickIntroVideoScreen:
    """Joue la vidéo d'intro avec OpenCV (1.mp4 si Judy P1, 1_2.mp4 si Nick P1), puis enchaîne sur le jeu."""
    VIDEO_SPEED = 2.5

    def __init__(self):
        self._cap = None
        self._video_path = None
        self._cv2 = None
        self._speed_phase = 0
        self._video_start_ticks = None
        self._sfx_played = False
        self._sfx_sound = None

    def run(self, ctx):
        filename = getattr(ctx, "intro_video_filename", None)
        if not filename:
            self._go_versus(ctx)
            return

        if self._cv2 is None:
            self._cv2 = _import_cv2()
        if self._cv2 is None:
            self._go_versus(ctx)
            return

        if self._cap is None:
            self._video_path = _video_path_for(ctx, filename)
            if not os.path.isfile(self._video_path):
                self._go_versus(ctx)
                return
            try:
                cap_ffmpeg = getattr(self._cv2, "CAP_FFMPEG", 1900)
                self._cap = self._cv2.VideoCapture(self._video_path, cap_ffmpeg)
                if not self._cap.isOpened():
                    try:
                        self._cap.release()
                    except Exception:
                        pass
                    self._cap = self._cv2.VideoCapture(self._video_path)
                if not self._cap.isOpened():
                    try:
                        self._cap.release()
                    except Exception:
                        pass
                    self._cap = None
                    self._go_versus(ctx)
                    return
            except Exception:
                self._cap = None
                self._go_versus(ctx)
                return
            self._video_start_ticks = pygame.time.get_ticks()

        if not self._sfx_played and self._video_start_ticks is not None:
            elapsed_ms = pygame.time.get_ticks() - self._video_start_ticks
            if elapsed_ms >= 1500:
                self._sfx_played = True
                base = getattr(ctx.assets, "base_dir", None) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                sfx_path = os.path.join(base, "assets", "song", "menu", "sfx versus", "special-attack_1.wav")
                if os.path.isfile(sfx_path):
                    try:
                        self._sfx_sound = pygame.mixer.Sound(sfx_path)
                        self._sfx_sound.set_volume(0.4)
                        self._sfx_sound.play()
                    except Exception:
                        pass

        events = safe_event_get()
        n_joy = pygame.joystick.get_count()
        if n_joy > 0:
            events.extend(get_joystick_poll_events(JOY_DEADZONE, (JOY_BTN_JUMP, JOY_BTN_START)))
        for event in events:
            if event.type == pygame.QUIT:
                ctx.running = False
                self._release()
                return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                self._release()
                self._go_versus(ctx)
                return
            if event.type == pygame.JOYBUTTONDOWN and event.joy in (0, 1) and event.button in (JOY_BTN_JUMP, JOY_BTN_START):
                self._release()
                self._go_versus(ctx)
                return

        skip = 2 if self._speed_phase == 0 else 3
        self._speed_phase = 1 - self._speed_phase
        for _ in range(skip):
            ret, _ = self._cap.read()
            if not ret:
                self._release()
                self._go_versus(ctx)
                return
        ret, frame = self._cap.read()
        if not ret or frame is None:
            self._release()
            self._go_versus(ctx)
            return

        cv2 = self._cv2
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame_rgb.shape[:2]
        surf = pygame.image.frombuffer(frame_rgb.tobytes(), (w, h), "RGB")
        surf = surf.copy()
        surf = pygame.transform.smoothscale(surf, (ctx.screen_w, ctx.screen_h))
        ctx.screen.blit(surf, (0, 0))
        pygame.display.flip()
        ctx.clock.tick(30)

    def _release(self):
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

    def _go_versus(self, ctx):
        if getattr(ctx, "menu_music_playing", False):
            try:
                pygame.mixer.music.stop()
                ctx.menu_music_playing = False
            except Exception:
                pass
        ctx.game_state = "versus_gif_p1_confirm"
        ctx.p1_confirm_frame_index = 0
        ctx.p1_confirm_timer_ms = 0
        ctx.p1_confirm_phase = "playing"
        ctx.wait_after_p1_confirm_timer_ms = 0
