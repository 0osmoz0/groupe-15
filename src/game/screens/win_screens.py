"""
Écrans de victoire Nick / Judy : animation d’images, puis touche ou bouton manette → menu principal.
"""
import pygame
from game.config import JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_START
from game.input_handling import get_joystick_poll_events, safe_event_get


class NickWinScreen:
    def run(self, ctx):
        dt_ms = ctx.clock.get_time()
        events = safe_event_get()
        n_joy = pygame.joystick.get_count()
        if n_joy > 0:
            events.extend(get_joystick_poll_events(JOY_DEADZONE, (JOY_BTN_JUMP, JOY_BTN_START)))
        for event in events:
            if event.type == pygame.QUIT:
                ctx.running = False
                return
            if event.type == pygame.KEYDOWN:
                ctx.game_state = "main_menu"
                return
            if event.type == pygame.JOYBUTTONDOWN and event.joy in (0, 1):
                ctx.game_state = "main_menu"
                return
        if not ctx.running:
            return
        # Animation frame par frame selon durées dans assets
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
        events = safe_event_get()
        n_joy = pygame.joystick.get_count()
        if n_joy > 0:
            events.extend(get_joystick_poll_events(JOY_DEADZONE, (JOY_BTN_JUMP, JOY_BTN_START)))
        for event in events:
            if event.type == pygame.QUIT:
                ctx.running = False
                return
            if event.type == pygame.KEYDOWN:
                ctx.game_state = "main_menu"
                return
            if event.type == pygame.JOYBUTTONDOWN and event.joy in (0, 1):
                ctx.game_state = "main_menu"
                return
        if not ctx.running:
            return
        # Même logique que Nick : animation puis retour menu
        frames = ctx.assets.judy_win_frames
        if frames:
            ctx.judy_win_frame_timer_ms += dt_ms
            while ctx.judy_win_frame_timer_ms >= frames[ctx.judy_win_frame_index][1] and len(frames) > 1:
                ctx.judy_win_frame_timer_ms -= frames[ctx.judy_win_frame_index][1]
                ctx.judy_win_frame_index = (ctx.judy_win_frame_index + 1) % len(frames)
            ctx.screen.blit(frames[ctx.judy_win_frame_index][0], (0, 0))
        pygame.display.flip()
        ctx.clock.tick(60)
