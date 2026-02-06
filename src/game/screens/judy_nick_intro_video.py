"""Écran de lecture des vidéos d'intro (1.mp4 Judy P1 / Nick P2, 1_2.mp4 Nick P1 / Judy P2).
Import de cv2 différé pour éviter le conflit SDL2 avec pygame (sinon les manettes ne marchent pas).
"""
import os
import pygame
from game.config import JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_START
from game.input_handling import get_joystick_poll_events, safe_event_get


def _import_cv2():
    """Import OpenCV uniquement au moment de lire la vidéo (évite conflit SDL2 / manettes)."""
    try:
        import cv2
        return cv2
    except (ImportError, OSError, Exception):
        return None


class JudyNickIntroVideoScreen:
    """Joue la vidéo d'intro selon P1/P2 (fichier dans ctx.intro_video_filename), puis enchaîne sur le jeu."""
    def __init__(self):
        self._cap = None
        self._video_path = None
        self._cv2 = None  # chargé à la première lecture

    def run(self, ctx):
        # Pas d'OpenCV ou première frame : ouvrir la vidéo ou passer à versus
        if self._cap is None:
            if not getattr(ctx, "intro_video_filename", None):
                self._go_versus(ctx)
                return
            if self._cv2 is None:
                self._cv2 = _import_cv2()
            if self._cv2 is None:
                self._go_versus(ctx)
                return
            self._video_path = os.path.join(
                ctx.assets.base_dir, "assets", "BG_perso", ctx.intro_video_filename
            )
            if not os.path.isfile(self._video_path):
                self._go_versus(ctx)
                return
            try:
                self._cap = self._cv2.VideoCapture(self._video_path)
                if not self._cap.isOpened():
                    self._go_versus(ctx)
                    return
            except Exception:
                self._go_versus(ctx)
                return

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

        # Vitesse x2 : on avance de 2 frames vidéo par frame affichée
        self._cap.read()  # frame ignorée
        ret, frame = self._cap.read()
        if not ret:
            self._release()
            self._go_versus(ctx)
            return

        # BGR (OpenCV) -> RGB, puis Surface
        cv2 = self._cv2
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame_rgb.shape[:2]
        surf = pygame.image.frombuffer(frame_rgb.tobytes(), (w, h), "RGB")
        surf = pygame.transform.smoothscale(surf, (ctx.screen_w, ctx.screen_h))
        ctx.screen.blit(surf, (0, 0))
        pygame.display.flip()
        ctx.clock.tick(60)

    def _release(self):
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

    def _go_versus(self, ctx):
        # Enchaînement direct vers P1 confirm (pas d’écran versus ni Entrée)
        ctx.game_state = "versus_gif_p1_confirm"
        ctx.p1_confirm_frame_index = 0
        ctx.p1_confirm_timer_ms = 0
        ctx.p1_confirm_phase = "playing"
        ctx.wait_after_p1_confirm_timer_ms = 0
