"""
Écran de configuration des touches (POO).
Permet de remapper les touches pour P1 et P2.
"""
from typing import Optional, Tuple, Dict, Any
import pygame
from game.input_handling import get_poll_axis


# Ordre et libellés des actions
CONTROL_KEYS_ORDER = (
    "left",
    "right",
    "jump",
    "down",
    "attacking",
    "special",
    "grab",
    "counter",
)
CONTROL_LABELS = {
    "left": "Gauche",
    "right": "Droite",
    "jump": "Saut",
    "down": "Bas",
    "attacking": "Attaque",
    "special": "Special",
    "grab": "Grab",
    "counter": "Contre",
}


def _key_name(key: int) -> str:
    try:
        return pygame.key.name(key).upper()
    except Exception:
        return "?"


class ControlsMenu:
    """Menu de configuration des touches pour Joueur 1 et Joueur 2."""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        controls_p1: Dict[str, int],
        controls_p2: Dict[str, int],
        joy_deadzone: float = 0.35,
        joy_confirm_buttons: Tuple[int, ...] = (0, 9),
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.controls_p1 = controls_p1
        self.controls_p2 = controls_p2
        self.joy_deadzone = joy_deadzone
        self.joy_confirm_buttons = joy_confirm_buttons

        self._step = "player"  # "player" | "action" | "listening"
        self._cursor = 0
        self._player_index = 0  # 0 = P1, 1 = P2
        self._axis1_prev = {0: 0.0, 1: 0.0}  # par joy_id pour les deux manettes
        self._listening_control: Optional[str] = None

        self._font_title = self._create_font(64, bold=True)
        self._font_option = self._create_font(42, bold=True)
        self._font_hint = self._create_font(24, bold=False)
        self._color_selected = (255, 220, 100)
        self._color_normal = (200, 200, 200)
        self._color_bg = (20, 20, 40)

    @staticmethod
    def _create_font(size: int, bold: bool = False) -> pygame.font.Font:
        try:
            return pygame.font.SysFont("arial", size, bold=bold)
        except Exception:
            return pygame.font.Font(None, max(40, size + 20))

    def _current_controls(self) -> Dict[str, int]:
        return self.controls_p1 if self._player_index == 0 else self.controls_p2

    def _player_options(self) -> Tuple[str, ...]:
        return ("Joueur 1 (P1)", "Joueur 2 (P2)", "Retour")

    def _action_entries(self) -> list:
        """Liste de (cle_control ou None, label). None = Retour."""
        ctrl = self._current_controls()
        entries = []
        for k in CONTROL_KEYS_ORDER:
            if k in ctrl:
                entries.append((k, f"{CONTROL_LABELS[k]}: {_key_name(ctrl.get(k, 0))}"))
        entries.append((None, "Retour"))
        return entries

    def handle_event(self, event: pygame.event.Event, joystick_count: int) -> Optional[str]:
        """
        Retourne "back" pour revenir aux paramètres, ou None.
        En mode "listening", consomme KEYDOWN pour assigner la touche.
        """
        if self._step == "listening":
            if event.type == pygame.QUIT:
                self._listening_control = None
                self._step = "action"
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._listening_control = None
                    self._step = "action"
                    return None
                if self._listening_control is not None:
                    ctrl = self._current_controls()
                    ctrl[self._listening_control] = event.key
                    self._listening_control = None
                    self._step = "action"
                return None
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self._step == "action":
                    self._step = "player"
                    self._cursor = 0
                else:
                    return "back"
                return None
            if event.key in (pygame.K_UP, pygame.K_w):
                self._cursor = (self._cursor - 1) % self._option_count()
                return None
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self._cursor = (self._cursor + 1) % self._option_count()
                return None
            if event.key in (pygame.K_RETURN, pygame.K_a):
                return self._on_confirm()
        if event.type == pygame.JOYAXISMOTION and joystick_count > 0 and event.joy in (0, 1) and event.axis == 1:
            ax1 = event.value
            prev = self._axis1_prev.get(event.joy, 0.0)
            if ax1 < -self.joy_deadzone and prev >= -self.joy_deadzone:
                self._cursor = (self._cursor - 1) % self._option_count()
            elif ax1 > self.joy_deadzone and prev <= self.joy_deadzone:
                self._cursor = (self._cursor + 1) % self._option_count()
            self._axis1_prev[event.joy] = ax1
            return None
        if (
            event.type == pygame.JOYBUTTONDOWN
            and joystick_count > 0
            and event.joy in (0, 1)
            and event.button in self.joy_confirm_buttons
        ):
            return self._on_confirm()
        return None

    def _option_count(self) -> int:
        if self._step == "player":
            return 3
        return len(self._action_entries())

    def _on_confirm(self) -> Optional[str]:
        if self._step == "player":
            if self._cursor == 0:
                self._player_index = 0
                self._step = "action"
                self._cursor = 0
            elif self._cursor == 1:
                self._player_index = 1
                self._step = "action"
                self._cursor = 0
            else:
                return "back"
            return None
        # step == "action"
        entries = self._action_entries()
        key_or_none, _ = entries[self._cursor]
        if key_or_none is None:
            return "back"
        self._listening_control = key_or_none
        self._step = "listening"
        return None

    def update(self, joystick_count: int) -> None:
        if joystick_count >= 2 and self._step != "listening":
            for joy_id in (0, 1):
                self._axis1_prev[joy_id] = get_poll_axis(joy_id, 1)
        elif joystick_count > 0 and self._step != "listening":
            try:
                j = pygame.joystick.Joystick(0)
                if j.get_numaxes() > 1:
                    self._axis1_prev[0] = j.get_axis(1)
            except Exception:
                pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(self._color_bg)
        if self._step == "listening" and self._listening_control:
            label = CONTROL_LABELS.get(self._listening_control, self._listening_control)
            title = self._font_title.render(
                f"Appuyez sur une touche pour: {label}",
                True,
                (255, 255, 255),
            )
            r = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(title, r)
            hint = self._font_hint.render("Echap pour annuler", True, (150, 150, 150))
            screen.blit(hint, hint.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50)))
            return

        title_text = "CONTROLES - Choisir joueur" if self._step == "player" else f"TOUCHES - Joueur {self._player_index + 1}"
        title = self._font_title.render(title_text, True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 60))
        screen.blit(title, title_rect)

        if self._step == "player":
            options = [(None, lb) for lb in self._player_options()]
        else:
            options = self._action_entries()
        start_y = self.screen_height // 4
        for i, (_, label) in enumerate(options):
            color = self._color_selected if i == self._cursor else self._color_normal
            surf = self._font_option.render(label, True, color)
            rect = surf.get_rect(center=(self.screen_width // 2, start_y + i * 48))
            if i == self._cursor:
                cur = self._font_option.render(">", True, self._color_selected)
                screen.blit(cur, (rect.left - cur.get_width() - 16, rect.centery - cur.get_height() // 2))
            screen.blit(surf, rect)
        hint = self._font_hint.render(
            "Haut/Bas : choisir   A : valider   Echap : retour",
            True,
            (150, 150, 150),
        )
        screen.blit(hint, hint.get_rect(center=(self.screen_width // 2, self.screen_height - 40)))
