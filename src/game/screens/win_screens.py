"""Écrans de victoire (Nick wins / Judy wins)."""
import pygame
from game.config import JOY_BTN_START


class NickWinScreen:
    def run(self, ctx):
        dt_ms = ctx.clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ctx.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ctx.running = False
                    return
                else:
                    ctx.game_state = "playing"
                    ctx.player1.respawn()
                    ctx.player2.respawn()
                    ctx.player1.lives = 3
                    ctx.player2.lives = 3
                    return
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == JOY_BTN_START:
                    ctx.running = False
                    return
                else:
                    ctx.game_state = "playing"
                    ctx.player1.respawn()
                    ctx.player2.respawn()
                    ctx.player1.lives = 3
                    ctx.player2.lives = 3
                    return
        if not ctx.running:
            return
        frames = ctx.assets.nick_win_frames
        if frames:
            ctx.nick_win_frame_timer_ms += dt_ms
            while ctx.nick_win_frame_timer_ms >= frames[ctx.nick_win_frame_index][1] and len(frames) > 1:
                ctx.nick_win_frame_timer_ms -= frames[ctx.nick_win_frame_index][1]
                ctx.nick_win_frame_index = (ctx.nick_win_frame_index + 1) % len(frames)
            ctx.screen.blit(frames[ctx.nick_win_frame_index][0], (0, 0))
        pygame.display.flip()
        ctx.clock.tick(60)


class JudyWinScreen:
    def run(self, ctx):
        dt_ms = ctx.clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ctx.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ctx.running = False
                    return
                else:
                    ctx.game_state = "playing"
                    ctx.player1.respawn()
                    ctx.player2.respawn()
                    ctx.player1.lives = 3
                    ctx.player2.lives = 3
                    return
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == JOY_BTN_START:
                    ctx.running = False
                    return
                else:
                    ctx.game_state = "playing"
                    ctx.player1.respawn()
                    ctx.player2.respawn()
                    ctx.player1.lives = 3
                    ctx.player2.lives = 3
                    return
        if not ctx.running:
            return
        frames = ctx.assets.judy_win_frames
        if frames:
            ctx.judy_win_frame_timer_ms += dt_ms
            while ctx.judy_win_frame_timer_ms >= frames[ctx.judy_win_frame_index][1] and len(frames) > 1:
                ctx.judy_win_frame_timer_ms -= frames[ctx.judy_win_frame_index][1]
                ctx.judy_win_frame_index = (ctx.judy_win_frame_index + 1) % len(frames)
            ctx.screen.blit(frames[ctx.judy_win_frame_index][0], (0, 0))
        pygame.display.flip()
        ctx.clock.tick(60)
