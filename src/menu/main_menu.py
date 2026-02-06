"""
Menu principal type Smash Bros (POO).
Gère affichage, curseur et entrées clavier/manette.
"""
from typing import Optional, Tuple, Sequence
import pygame
from game.input_handling import get_poll_axis


class MainMenu:
    """Menu principal avec liste d'options et curseur."""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        options: Sequence[str],
        title: str = "SMASH",
        title_image: Optional[pygame.Surface] = None,
        background: Optional[pygame.Surface] = None,
        big_rect_background: Optional[pygame.Surface] = None,
        big_rect_background_param: Optional[pygame.Surface] = None,
        big_rect_background_quit: Optional[pygame.Surface] = None,
        joy_deadzone: float = 0.35,
        joy_confirm_buttons: Tuple[int, ...] = (0, 9),
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.options = tuple(options)
        self.title = title
        self.title_image = title_image
        self.background = background
        self.big_rect_background = big_rect_background
        self.big_rect_background_param = big_rect_background_param
        self.big_rect_background_quit = big_rect_background_quit
        self.joy_deadzone = joy_deadzone
        self.joy_confirm_buttons = joy_confirm_buttons

        self._cursor = 0
        self._axis_prev: dict = {}

        self._font_title = self._create_font(72, bold=True)
        self._font_option = self._create_font(48, bold=True)
        self._font_hint = self._create_font(22, bold=False)

        self._color_rect_selected = (218, 165, 32)
        self._color_rect_normal = (52, 58, 72)
        self._color_border_glow = (255, 215, 100)
        self._color_border_glow_outer = (255, 235, 160)
        self._color_text = (255, 252, 245)
        self._color_text_shadow = (30, 28, 35)
        self._color_hint = (160, 165, 175)
        self._color_bg_fallback = (28, 32, 42)
        self._color_card_shadow = (15, 18, 25)
        self._color_overlay = (0, 0, 0, 140)

        self._menu_margin_left = int(self.screen_width * 0.07)
        self._menu_margin_top = int(self.screen_height * 0.22)
        self._gap = 20
        self._rect_border = 4
        self._radius_big = 16
        self._radius_small = 12
        self._shadow_offset = 6
        self._big_width = int(self.screen_width * 0.42)
        self._big_height = int(self.screen_height * 0.12)
        self._small_width = (self._big_width - self._gap) // 2
        self._small_height = int(self._big_height * 0.72)
        self._grid_cols = 2
        self._grid_rows = 2

    @staticmethod
    def _create_font(size: int, bold: bool = False) -> pygame.font.Font:
        try:
            return pygame.font.SysFont("arial", size, bold=bold)
        except Exception:
            return pygame.font.Font(None, max(40, size + 20))

    def _move_cursor(self, delta: int) -> None:
        """Déplacement vertical (liste linéaire)."""
        self._cursor = (self._cursor + delta) % len(self.options)

    def _cursor_to_grid(self) -> Tuple[int, int]:
        """Indice -> (ligne, colonne) dans la grille 2x2."""
        i = self._cursor
        return (i // self._grid_cols, i % self._grid_cols)

    def _grid_to_cursor(self, row: int, col: int) -> int:
        """(ligne, colonne) -> indice. Si case vide (ex: 2x2 avec 3 options), retourne le plus proche valide."""
        if row < 0 or row >= self._grid_rows or col < 0 or col >= self._grid_cols:
            return self._cursor
        idx = row * self._grid_cols + col
        if idx < len(self.options):
            return idx
        return min(len(self.options) - 1, (row + 1) * self._grid_cols - 1)

    def _move_cursor_grid(self, drow: int, dcol: int) -> None:
        """Déplacement dans la grille 2x2 (haut/bas/gauche/droite)."""
        r, c = self._cursor_to_grid()
        r2, c2 = r + drow, c + dcol
        idx = self._grid_to_cursor(r2, c2)
        if idx < len(self.options):
            self._cursor = idx

    def handle_event(self, event: pygame.event.Event, joystick_count: int) -> Optional[str]:
        """
        Traite un événement. Retourne l'option sélectionnée ("VERSUS", "QUITTER", ...)
        ou None si aucune action.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move_cursor_grid(-1, 0)
                return None
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self._move_cursor_grid(1, 0)
                return None
            if event.key == pygame.K_LEFT:
                self._move_cursor_grid(0, -1)
                return None
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self._move_cursor_grid(0, 1)
                return None
            if event.key in (pygame.K_RETURN, pygame.K_a):
                return self.options[self._cursor]

        if event.type == pygame.JOYAXISMOTION and joystick_count > 0 and event.joy in (0, 1):
            key = (event.joy, event.axis)
            prev = self._axis_prev.get(key, 0.0)
            val = event.value
            if event.axis == 0:
                if val < -self.joy_deadzone and prev >= -self.joy_deadzone:
                    self._move_cursor_grid(0, -1)
                elif val > self.joy_deadzone and prev <= self.joy_deadzone:
                    self._move_cursor_grid(0, 1)
            elif event.axis == 1:
                if val < -self.joy_deadzone and prev >= -self.joy_deadzone:
                    self._move_cursor_grid(-1, 0)
                elif val > self.joy_deadzone and prev <= self.joy_deadzone:
                    self._move_cursor_grid(1, 0)
            self._axis_prev[key] = val
            return None

        if (
            event.type == pygame.JOYBUTTONDOWN
            and joystick_count > 0
            and event.joy in (0, 1)
            and event.button in self.joy_confirm_buttons
        ):
            return self.options[self._cursor]

        return None

    def update(self, joystick_count: int) -> None:
        """Met à jour l'état du stick par manette ; si 2 manettes, utilise le cache de polling (macOS)."""
        if joystick_count <= 0:
            self._axis_prev.clear()
            return
        for joy_id in (0, 1):
            if joy_id >= joystick_count:
                continue
            if joystick_count >= 2:
                ax0 = get_poll_axis(joy_id, 0)
                ax1 = get_poll_axis(joy_id, 1)
                key0, key1 = (joy_id, 0), (joy_id, 1)
                prev0 = self._axis_prev.get(key0, 0.0)
                prev1 = self._axis_prev.get(key1, 0.0)
                if ax0 < -self.joy_deadzone and prev0 >= -self.joy_deadzone:
                    self._move_cursor_grid(0, -1)
                elif ax0 > self.joy_deadzone and prev0 <= self.joy_deadzone:
                    self._move_cursor_grid(0, 1)
                if ax1 < -self.joy_deadzone and prev1 >= -self.joy_deadzone:
                    self._move_cursor_grid(-1, 0)
                elif ax1 > self.joy_deadzone and prev1 <= self.joy_deadzone:
                    self._move_cursor_grid(1, 0)
                self._axis_prev[key0] = ax0
                self._axis_prev[key1] = ax1
            else:
                try:
                    j = pygame.joystick.Joystick(joy_id)
                    j.init()
                    if j.get_numaxes() > 0:
                        self._axis_prev[(joy_id, 0)] = j.get_axis(0)
                    if j.get_numaxes() > 1:
                        self._axis_prev[(joy_id, 1)] = j.get_axis(1)
                except Exception:
                    pass

    def _draw_rounded_card(self, screen: pygame.Surface, rect: pygame.Rect, fill_color: tuple, radius: int, shadow: bool = True) -> None:
        """Dessine une carte avec ombre portée et coins arrondis."""
        if shadow:
            shadow_rect = rect.move(self._shadow_offset, self._shadow_offset)
            pygame.draw.rect(screen, self._color_card_shadow, shadow_rect, border_radius=radius + 2)
        pygame.draw.rect(screen, fill_color, rect, border_radius=radius)

    def _draw_text_with_shadow(self, screen: pygame.Surface, text: str, font: pygame.font.Font, center: Tuple[int, int], color: tuple = None) -> None:
        """Affiche un texte avec ombre légère pour la lisibilité."""
        color = color or self._color_text
        shadow_surf = font.render(text, True, self._color_text_shadow)
        text_surf = font.render(text, True, color)
        sw, sh = shadow_surf.get_size()
        tx, ty = center[0] - sw // 2, center[1] - sh // 2
        screen.blit(shadow_surf, (tx + 2, ty + 2))
        screen.blit(text_surf, (tx, ty))

    def draw(self, screen: pygame.Surface) -> None:
        """Dessine le menu : fond, titre, cartes avec ombres et barre d’aide."""
        if self.background is not None:
            screen.blit(self.background, (0, 0))
            overlay = pygame.Surface((self._big_width + self._menu_margin_left + 100, self.screen_height))
            overlay.set_alpha(70)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill(self._color_bg_fallback)

        title_y = self._menu_margin_top - 56
        if self.title_image is not None:
            title_rect = self.title_image.get_rect(midleft=(self._menu_margin_left, title_y))
            shadow_rect = title_rect.move(3, 3)
            shadow = pygame.Surface((title_rect.width + 6, title_rect.height + 6))
            shadow.set_alpha(80)
            shadow.fill((0, 0, 0))
            screen.blit(shadow, shadow_rect.topleft)
            screen.blit(self.title_image, title_rect)
        else:
            title_surf = self._font_title.render(self.title, True, self._color_text)
            title_shadow = self._font_title.render(self.title, True, self._color_text_shadow)
            tr = title_surf.get_rect(midleft=(self._menu_margin_left, title_y))
            screen.blit(title_shadow, tr.move(2, 2))
            screen.blit(title_surf, tr)

        big_rect = pygame.Rect(
            self._menu_margin_left,
            self._menu_margin_top,
            self._big_width,
            self._big_height,
        )
        selected_label = self.options[self._cursor]
        bg_surface = None
        if self._cursor == 0 and self.big_rect_background is not None:
            bg_surface = self.big_rect_background
        elif self._cursor == 1 and self.big_rect_background_param is not None:
            bg_surface = self.big_rect_background_param
        elif self._cursor == 2 and self.big_rect_background_quit is not None:
            bg_surface = self.big_rect_background_quit

        fill_big = self._color_rect_selected
        self._draw_rounded_card(screen, big_rect, fill_big, self._radius_big)
        if bg_surface is not None:
            bg_scaled = pygame.transform.smoothscale(bg_surface, (self._big_width, self._big_height))
            screen.blit(bg_scaled, big_rect.topleft)
            overlay_card = pygame.Surface((self._big_width, self._big_height))
            overlay_card.set_alpha(75)
            overlay_card.fill((0, 0, 0))
            screen.blit(overlay_card, big_rect.topleft)
        for border_w, color in [(self._rect_border + 2, self._color_border_glow_outer), (self._rect_border, self._color_border_glow)]:
            outer = big_rect.inflate(border_w * 2, border_w * 2)
            pygame.draw.rect(screen, color, outer, width=border_w, border_radius=self._radius_big + 2)
        self._draw_text_with_shadow(screen, selected_label, self._font_option, big_rect.center)

        grid_start_y = self._menu_margin_top + self._big_height + self._gap
        font_small = self._create_font(36, bold=True)
        for i in range(len(self.options)):
            row, col = i // self._grid_cols, i % self._grid_cols
            small_rect = pygame.Rect(
                self._menu_margin_left + col * (self._small_width + self._gap),
                grid_start_y + row * (self._small_height + self._gap),
                self._small_width,
                self._small_height,
            )
            is_selected = i == self._cursor
            fill_color = self._color_rect_selected if is_selected else self._color_rect_normal
            self._draw_rounded_card(screen, small_rect, fill_color, self._radius_small)
            if is_selected:
                for border_w, color in [(self._rect_border + 1, self._color_border_glow_outer), (self._rect_border, self._color_border_glow)]:
                    outer = small_rect.inflate(border_w * 2, border_w * 2)
                    pygame.draw.rect(screen, color, outer, width=max(1, border_w), border_radius=self._radius_small + 2)
            opt_surf = font_small.render(self.options[i], True, self._color_text)
            opt_rect = opt_surf.get_rect(center=small_rect.center)
            screen.blit(opt_surf, opt_rect)

        bar_height = 36
        bar_rect = pygame.Rect(0, self.screen_height - bar_height, self.screen_width, bar_height)
        pygame.draw.rect(screen, (38, 42, 52), bar_rect)
        pygame.draw.line(screen, (60, 65, 80), (0, self.screen_height - bar_height), (self.screen_width, self.screen_height - bar_height), 1)
        hint = self._font_hint.render(
            "Déplacer : flèches ou stick   ·   Valider : Entrée ou A",
            True,
            self._color_hint,
        )
        hint_rect = hint.get_rect(center=(self.screen_width // 2, self.screen_height - bar_height // 2))
        screen.blit(hint, hint_rect)
