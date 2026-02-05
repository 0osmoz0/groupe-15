"""Écran de sélection de carte."""
import pygame
from game.config import JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_START


class MapSelectScreen:
    def run(self, ctx):
        try:
            events = pygame.event.get()
        except (KeyError, SystemError):
            events = []
        n_joy = pygame.joystick.get_count()
        for event in events:
            if event.type == pygame.QUIT:
                ctx.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    ctx.map_select_cursor = (ctx.map_select_cursor - 1) % len(ctx.assets.map_surfaces)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    ctx.map_select_cursor = (ctx.map_select_cursor + 1) % len(ctx.assets.map_surfaces)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    ctx.selected_map_index = ctx.map_select_cursor
                    ctx.game_state = "character_select"
                    return
            if event.type == pygame.JOYAXISMOTION and n_joy > 0 and event.joy == 0 and event.axis == 0:
                ax = event.value
                if ax < -JOY_DEADZONE:
                    ctx.map_select_cursor = (ctx.map_select_cursor - 1) % len(ctx.assets.map_surfaces)
                elif ax > JOY_DEADZONE:
                    ctx.map_select_cursor = (ctx.map_select_cursor + 1) % len(ctx.assets.map_surfaces)
            if event.type == pygame.JOYBUTTONDOWN and n_joy > 0 and event.joy == 0 and event.button in (JOY_BTN_JUMP, JOY_BTN_START):
                ctx.selected_map_index = ctx.map_select_cursor
                ctx.game_state = "character_select"
                return
        if not ctx.running:
            return
        self._draw(ctx)
        pygame.display.flip()
        ctx.clock.tick(60)

    def _draw(self, ctx):
        if ctx.assets.menu_background:
            ctx.screen.blit(ctx.assets.menu_background, (0, 0))
        else:
            ctx.screen.fill((30, 30, 50))
        try:
            font_map = pygame.font.SysFont("arial", 48, bold=True)
            font_small = pygame.font.SysFont("arial", 28, bold=True)
        except Exception:
            font_map = ctx.assets.font_percent
            font_small = ctx.assets.font_percent
        title = font_map.render("Choisis la carte", True, (255, 255, 255))
        ctx.screen.blit(title, title.get_rect(center=(ctx.screen_w // 2, ctx.screen_h // 6)))
        n_maps = len(ctx.assets.map_surfaces)
        thumb_w = min(220, (ctx.screen_w - 80) // n_maps - 20)
        thumb_h = int(thumb_w * ctx.world_h / ctx.world_w)
        for i in range(n_maps):
            thumb = pygame.transform.smoothscale(ctx.assets.map_surfaces[i], (thumb_w, thumb_h))
            x = ctx.screen_w * (i + 1) // (n_maps + 1) - thumb_w // 2
            y = ctx.screen_h // 2 - thumb_h // 2
            if i == ctx.map_select_cursor:
                pygame.draw.rect(ctx.screen, (255, 220, 80), (x - 4, y - 4, thumb_w + 8, thumb_h + 8), 4)
            ctx.screen.blit(thumb, (x, y))
            label = ctx.assets.map_labels[i] if i < len(ctx.assets.map_labels) else f"Carte {i + 1}"
            lbl = font_small.render(label, True, (255, 220, 100) if i == ctx.map_select_cursor else (200, 200, 200))
            ctx.screen.blit(lbl, (x + thumb_w // 2 - lbl.get_width() // 2, y + thumb_h + 8))
        hint = font_small.render("Gauche/Droite : carte   Entree / A : valider", True, (160, 160, 160))
        ctx.screen.blit(hint, hint.get_rect(center=(ctx.screen_w // 2, ctx.screen_h - 50)))
