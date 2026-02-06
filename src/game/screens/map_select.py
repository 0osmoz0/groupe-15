"""Écran de sélection de carte."""
import pygame
from game.config import JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_START
from game.input_handling import get_joystick_poll_events, safe_event_get


class MapSelectScreen:
    def __init__(self):
        self._prev_axis0 = {}  # joy_id -> dernière valeur axe horizontal (debounce)

    def run(self, ctx):
        events = safe_event_get()
        n_joy = pygame.joystick.get_count()
        for jid in range(min(2, n_joy)):
            try:
                pygame.joystick.Joystick(jid).init()
            except Exception:
                pass
        if n_joy > 0:
            events.extend(get_joystick_poll_events(JOY_DEADZONE, (JOY_BTN_JUMP, JOY_BTN_START)))
        n_maps = max(1, len(getattr(ctx.assets, "map_surfaces", [])))
        ctx.map_select_cursor = min(max(0, ctx.map_select_cursor), n_maps - 1)
        for event in events:
            if event.type == pygame.QUIT:
                ctx.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    ctx.map_select_cursor = (ctx.map_select_cursor - 1) % n_maps
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    ctx.map_select_cursor = (ctx.map_select_cursor + 1) % n_maps
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    ctx.selected_map_index = min(ctx.map_select_cursor, n_maps - 1)
                    ctx.game_state = "character_select"
                    return
            if event.type == pygame.JOYAXISMOTION and n_joy > 0 and event.joy in (0, 1) and event.axis == 0:
                ax = event.value
                prev = self._prev_axis0.get(event.joy, 0.0)
                if prev >= -JOY_DEADZONE and ax < -JOY_DEADZONE:
                    ctx.map_select_cursor = (ctx.map_select_cursor - 1) % n_maps
                elif prev <= JOY_DEADZONE and ax > JOY_DEADZONE:
                    ctx.map_select_cursor = (ctx.map_select_cursor + 1) % n_maps
                self._prev_axis0[event.joy] = ax
            if event.type == pygame.JOYBUTTONDOWN and n_joy > 0 and event.joy in (0, 1) and event.button in (JOY_BTN_JUMP, JOY_BTN_START):
                if getattr(ctx, "map_select_ignore_confirm_frame", False):
                    continue
                ctx.selected_map_index = min(ctx.map_select_cursor, n_maps - 1)
                ctx.game_state = "character_select"
                return
        if not ctx.running:
            return
        ctx.map_select_ignore_confirm_frame = False
        self._draw(ctx)
        pygame.display.flip()
        ctx.clock.tick(60)

    def _draw(self, ctx):
        if getattr(ctx.assets, "map_select_background", None):
            ctx.screen.blit(ctx.assets.map_select_background, (0, 0))
        elif getattr(ctx.assets, "menu_background", None):
            ctx.screen.blit(ctx.assets.menu_background, (0, 0))
        else:
            ctx.screen.fill((30, 30, 50))
        try:
            font_map = pygame.font.SysFont("arial", 48, bold=True)
            font_small = pygame.font.SysFont("arial", 28, bold=True)
        except Exception:
            font_map = getattr(ctx.assets, "font_percent", None) or pygame.font.Font(None, 48)
            font_small = font_map
        title = font_map.render("Choisis la carte", True, (255, 255, 255))
        ctx.screen.blit(title, title.get_rect(center=(ctx.screen_w // 2, ctx.screen_h // 6)))
        n_maps = max(1, len(getattr(ctx.assets, "map_surfaces", [])))
        thumb_w = min(220, max(80, (ctx.screen_w - 80) // n_maps - 20))
        thumb_h = int(thumb_w * ctx.world_h / ctx.world_w)
        map_surfaces = getattr(ctx.assets, "map_surfaces", [])
        map_labels = getattr(ctx.assets, "map_labels", ())
        for i in range(n_maps):
            surf = map_surfaces[i] if i < len(map_surfaces) else None
            if surf is not None:
                thumb = pygame.transform.smoothscale(surf, (thumb_w, thumb_h))
            else:
                thumb = pygame.Surface((thumb_w, thumb_h))
                thumb.fill((60, 60, 80))
            x = ctx.screen_w * (i + 1) // (n_maps + 1) - thumb_w // 2
            y = ctx.screen_h // 2 - thumb_h // 2
            if i == ctx.map_select_cursor:
                pygame.draw.rect(ctx.screen, (255, 220, 80), (x - 4, y - 4, thumb_w + 8, thumb_h + 8), 4)
            ctx.screen.blit(thumb, (x, y))
            label = map_labels[i] if i < len(map_labels) else f"Carte {i + 1}"
            lbl = font_small.render(label, True, (255, 220, 100) if i == ctx.map_select_cursor else (200, 200, 200))
            ctx.screen.blit(lbl, (x + thumb_w // 2 - lbl.get_width() // 2, y + thumb_h + 8))
        hint = font_small.render("Gauche/Droite : carte   Entree / A : valider", True, (160, 160, 160))
        ctx.screen.blit(hint, hint.get_rect(center=(ctx.screen_w // 2, ctx.screen_h - 50)))
