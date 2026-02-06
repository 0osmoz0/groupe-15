"""
Écran Paramètres (POO).
Options : Plein écran (toggle), Retour.
"""
from typing import Optional, Tuple, Callable
import pygame
from game.input_handling import get_poll_axis


class SettingsMenu:
    """Menu des paramètres avec options modifiables."""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        get_fullscreen: Callable[[], bool],
        joy_deadzone: float = 0.35,
        joy_confirm_buttons: Tuple[int, ...] = (0, 9),
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.get_fullscreen = get_fullscreen
        self.joy_deadzone = joy_deadzone
        self.joy_confirm_buttons = joy_confirm_buttons

        self._cursor = 0
        self._axis1_prev = {0: 0.0, 1: 0.0}  # par joy_id pour les deux manettes
        self._option_count = 3  # Plein écran, Contrôles, Retour

        self._font_title = self._create_font(80, bold=True)
        self._font_option = self._create_font(56, bold=True)
        self._font_hint = self._create_font(28, bold=False)

        self._color_selected = (255, 220, 100)
        self._color_normal = (200, 200, 200)
        self._color_hint = (150, 150, 150)
        self._color_bg = (20, 20, 40)

    @staticmethod
    def _create_font(size: int, bold: bool = False) -> pygame.font.Font:
        try:
            return pygame.font.SysFont("arial", size, bold=bold)
        except Exception:
            return pygame.font.Font(None, max(40, size + 20))

    def _get_option_labels(self) -> Tuple[str, ...]:
        return (
            "Plein ecran : Oui" if self.get_fullscreen() else "Plein ecran : Non",
            "Controles (touches)",
            "Retour",
        )

    def _move_cursor(self, delta: int) -> None:
        self._cursor = (self._cursor + delta) % self._option_count

    def handle_event(self, event: pygame.event.Event, joystick_count: int) -> Optional[str]:
        """
        Traite un événement.
        Retourne "toggle_fullscreen", "back", ou None.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move_cursor(-1)
                return None
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self._move_cursor(1)
                return None
            if event.key in (pygame.K_RETURN, pygame.K_a):
                if self._cursor == 0:
                    return "toggle_fullscreen"
                if self._cursor == 1:
                    return "controls"
                return "back"
            if event.key == pygame.K_ESCAPE:
                return "back"

        if event.type == pygame.JOYAXISMOTION and joystick_count > 0 and event.joy in (0, 1) and event.axis == 1:
            ax1 = event.value
            prev = self._axis1_prev.get(event.joy, 0.0)
            if ax1 < -self.joy_deadzone and prev >= -self.joy_deadzone:
                self._move_cursor(-1)
            elif ax1 > self.joy_deadzone and prev <= self.joy_deadzone:
                self._move_cursor(1)
            self._axis1_prev[event.joy] = ax1
            return None

        if (
            event.type == pygame.JOYBUTTONDOWN
            and joystick_count > 0
            and event.joy in (0, 1)
            and event.button in self.joy_confirm_buttons
        ):
            if self._cursor == 0:
                return "toggle_fullscreen"
            if self._cursor == 1:
                return "controls"
            return "back"

        return None

    def update(self, joystick_count: int) -> None:
        if joystick_count >= 2:
            for joy_id in (0, 1):
                self._axis1_prev[joy_id] = get_poll_axis(joy_id, 1)
        elif joystick_count > 0:
            try:
                j = pygame.joystick.Joystick(0)
                if j.get_numaxes() > 1:
                    self._axis1_prev[0] = j.get_axis(1)
            except Exception:
                pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(self._color_bg)

        title_surf = self._font_title.render("PARAMETRES", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 5))
        screen.blit(title_surf, title_rect)

        options = self._get_option_labels()
        option_y = self.screen_height // 2 - 60
        for i, label in enumerate(options):
            color = self._color_selected if i == self._cursor else self._color_normal
            opt_surf = self._font_option.render(label, True, color)
            opt_rect = opt_surf.get_rect(center=(self.screen_width // 2, option_y + i * 70))
            if i == self._cursor:
                cursor_surf = self._font_option.render(">", True, self._color_selected)
                screen.blit(
                    cursor_surf,
                    (
                        opt_rect.left - cursor_surf.get_width() - 20,
                        opt_rect.centery - cursor_surf.get_height() // 2,
                    ),
                )
            screen.blit(opt_surf, opt_rect)

        hint = self._font_hint.render(
            "Haut/Bas : choisir   A / Entree : valider   Echap : retour",
            True,
            self._color_hint,
        )
        hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height - 60))
        screen.blit(hint, hint_rect)
