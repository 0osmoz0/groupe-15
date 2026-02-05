"""Écran countdown 3-2-1-go."""
import pygame
from game.config import COUNTDOWN_DURATION_MS
from game.hud import draw_player_ping


class CountdownScreen:
    def run(self, ctx):
        dt_ms = ctx.clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ctx.running = False
                return
        if not ctx.running:
            return
        if ctx.countdown_step == 0 and ctx.countdown_timer_ms == 0 and 0 <= ctx.selected_map_index < len(ctx.assets.map_surfaces):
            ctx.assets.background = ctx.assets.map_surfaces[ctx.selected_map_index].copy()
        ctx.countdown_timer_ms += dt_ms
        if ctx.countdown_timer_ms >= COUNTDOWN_DURATION_MS:
            ctx.countdown_timer_ms = 0
            ctx.countdown_step += 1
            if ctx.countdown_step >= 4:
                ctx.game_state = "playing"
                pygame.display.flip()
                ctx.clock.tick(60)
                return
        ctx.world_surface.blit(ctx.assets.background, (0, 0))
        ctx.platforms.draw(ctx.world_surface)
        ctx.players.draw(ctx.world_surface)
        draw_player_ping(ctx.world_surface, ctx.player1, ctx.assets.ping_p1, ctx.assets.ping_offset_above)
        draw_player_ping(ctx.world_surface, ctx.player2, ctx.assets.ping_p2, ctx.assets.ping_offset_above)
        ctx.screen.blit(ctx.world_surface, (0, 0), (int(ctx.camera_x), int(ctx.camera_y), ctx.screen_w, ctx.screen_h))
        if ctx.countdown_step < 4 and ctx.assets.counter_surfaces and ctx.assets.counter_surfaces[ctx.countdown_step]:
            surf = ctx.assets.counter_surfaces[ctx.countdown_step]
            x = (ctx.screen_w - surf.get_width()) // 2
            y = (ctx.screen_h - surf.get_height()) // 2
            ctx.screen.blit(surf, (x, y))
        pygame.display.flip()
        ctx.clock.tick(60)
