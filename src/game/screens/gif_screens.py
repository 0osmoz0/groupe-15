"""Écrans GIF (versus, enter, P1 confirm, etc.)."""
import pygame
from game.config import JOY_BTN_JUMP, JOY_BTN_START
from game.config import WAIT_AFTER_GIF_MS, WAIT_AFTER_P1_CONFIRM_MS, WAIT_AFTER_ENTER_GIF_MS, WAIT_AFTER_ENTER_THEN_A_MS


def _run_gif_playing(ctx, frames_attr, frame_index_attr, timer_attr, phase_attr, wait_timer_attr, wait_max_ms, next_state, dt_ms):
    """Avance le GIF et gère playing/waiting. Retourne True si on a dessiné et il faut flip."""
    frames = getattr(ctx.assets, frames_attr)
    frame_index = getattr(ctx, frame_index_attr)
    timer = getattr(ctx, timer_attr)
    phase = getattr(ctx, phase_attr)
    wait_timer = getattr(ctx, wait_timer_attr)
    if phase == "playing" and frames:
        timer += dt_ms
        setattr(ctx, timer_attr, timer)
        surf, duration_ms = frames[frame_index]
        while timer >= duration_ms:
            timer -= duration_ms
            frame_index += 1
            if frame_index >= len(frames):
                setattr(ctx, phase_attr, "waiting")
                frame_index = len(frames) - 1
                setattr(ctx, frame_index_attr, frame_index)
                setattr(ctx, timer_attr, timer)
                if frames:
                    ctx.screen.blit(frames[-1][0], (0, 0))
                return True
            surf, duration_ms = frames[frame_index]
        setattr(ctx, frame_index_attr, frame_index)
        if frames:
            ctx.screen.blit(frames[frame_index][0], (0, 0))
        return True
    elif phase == "waiting":
        wait_timer += dt_ms
        setattr(ctx, wait_timer_attr, wait_timer)
        if frames:
            ctx.screen.blit(frames[-1][0], (0, 0))
        if wait_timer >= wait_max_ms:
            ctx.game_state = next_state
            if next_state == "countdown":
                ctx.countdown_step = 0
                ctx.countdown_timer_ms = 0
            elif next_state == "versus_gif_enter_then_a":
                ctx.enter_then_a_frame_index = 0
                ctx.enter_then_a_timer_ms = 0
                ctx.enter_then_a_phase = "playing"
                ctx.wait_after_enter_then_a_timer_ms = 0
            elif next_state == "versus_gif_p1_confirm":
                ctx.p1_confirm_frame_index = 0
                ctx.p1_confirm_timer_ms = 0
                ctx.p1_confirm_phase = "playing"
                ctx.wait_after_p1_confirm_timer_ms = 0
        return True
    return False


class VersusGifScreen:
    def run(self, ctx):
        dt_ms = ctx.clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ctx.running = False
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                ctx.game_state = "versus_gif_p1_confirm"
                ctx.p1_confirm_frame_index = 0
                ctx.p1_confirm_timer_ms = 0
                ctx.p1_confirm_phase = "playing"
                ctx.wait_after_p1_confirm_timer_ms = 0
                return
            if event.type == pygame.JOYBUTTONDOWN and event.joy == 0 and event.button in (JOY_BTN_JUMP, JOY_BTN_START):
                ctx.game_state = "versus_gif_p1_confirm"
                ctx.p1_confirm_frame_index = 0
                ctx.p1_confirm_timer_ms = 0
                ctx.p1_confirm_phase = "playing"
                ctx.wait_after_p1_confirm_timer_ms = 0
                return
        if not ctx.running:
            return
        if ctx.versus_gif_phase == "playing" and ctx.assets.versus_gif_frames:
            ctx.versus_gif_timer_ms += dt_ms
            frames = ctx.assets.versus_gif_frames
            while ctx.versus_gif_timer_ms >= frames[ctx.versus_gif_frame_index][1]:
                ctx.versus_gif_timer_ms -= frames[ctx.versus_gif_frame_index][1]
                ctx.versus_gif_frame_index += 1
                if ctx.versus_gif_frame_index >= len(frames):
                    ctx.versus_gif_phase = "waiting"
                    ctx.versus_gif_frame_index = len(frames) - 1
                    break
            ctx.screen.blit(frames[ctx.versus_gif_frame_index][0], (0, 0))
        elif ctx.versus_gif_phase == "waiting":
            ctx.wait_after_gif_timer_ms += dt_ms
            if ctx.assets.versus_gif_frames:
                ctx.screen.blit(ctx.assets.versus_gif_frames[-1][0], (0, 0))
            if ctx.wait_after_gif_timer_ms >= WAIT_AFTER_GIF_MS:
                ctx.game_state = "wait_p1_enter"
        else:
            ctx.game_state = "wait_p1_enter"
        pygame.display.flip()
        ctx.clock.tick(60)


class WaitP1EnterScreen:
    def run(self, ctx):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ctx.running = False
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                ctx.game_state = "versus_gif_p1_confirm"
                ctx.p1_confirm_frame_index = 0
                ctx.p1_confirm_timer_ms = 0
                ctx.p1_confirm_phase = "playing"
                ctx.wait_after_p1_confirm_timer_ms = 0
                return
            if event.type == pygame.JOYBUTTONDOWN and event.joy == 0 and event.button in (JOY_BTN_JUMP, JOY_BTN_START):
                ctx.game_state = "versus_gif_p1_confirm"
                ctx.p1_confirm_frame_index = 0
                ctx.p1_confirm_timer_ms = 0
                ctx.p1_confirm_phase = "playing"
                ctx.wait_after_p1_confirm_timer_ms = 0
                return
        if not ctx.running:
            return
        if ctx.assets.versus_gif_frames:
            ctx.screen.blit(ctx.assets.versus_gif_frames[-1][0], (0, 0))
        pygame.display.flip()
        ctx.clock.tick(60)


class VersusGifP1ConfirmScreen:
    def run(self, ctx):
        dt_ms = ctx.clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ctx.running = False
                return
        if not ctx.running:
            return
        frames = ctx.assets.p1_confirm_gif_frames
        if ctx.p1_confirm_phase == "playing" and frames:
            ctx.p1_confirm_timer_ms += dt_ms
            while ctx.p1_confirm_timer_ms >= frames[ctx.p1_confirm_frame_index][1]:
                ctx.p1_confirm_timer_ms -= frames[ctx.p1_confirm_frame_index][1]
                ctx.p1_confirm_frame_index += 1
                if ctx.p1_confirm_frame_index >= len(frames):
                    ctx.p1_confirm_phase = "waiting"
                    ctx.p1_confirm_frame_index = len(frames) - 1
                    break
            ctx.screen.blit(frames[ctx.p1_confirm_frame_index][0], (0, 0))
        elif ctx.p1_confirm_phase == "waiting":
            ctx.wait_after_p1_confirm_timer_ms += dt_ms
            if frames:
                ctx.screen.blit(frames[-1][0], (0, 0))
            if ctx.wait_after_p1_confirm_timer_ms >= WAIT_AFTER_P1_CONFIRM_MS:
                ctx.game_state = "countdown"
                ctx.countdown_step = 0
                ctx.countdown_timer_ms = 0
        else:
            ctx.game_state = "countdown"
            ctx.countdown_step = 0
            ctx.countdown_timer_ms = 0
        pygame.display.flip()
        ctx.clock.tick(60)


class EnterGifScreen:
    """Écran titre 'Enter' GIF (chemin alternatif depuis title_screen)."""
    def run(self, ctx):
        dt_ms = ctx.clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ctx.running = False
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                ctx.game_state = "versus_gif_enter_then_a"
                ctx.enter_then_a_frame_index = 0
                ctx.enter_then_a_timer_ms = 0
                ctx.enter_then_a_phase = "playing"
                ctx.wait_after_enter_then_a_timer_ms = 0
                return
            if event.type == pygame.JOYBUTTONDOWN and event.joy == 0 and event.button in (JOY_BTN_JUMP, JOY_BTN_START):
                ctx.game_state = "versus_gif_enter_then_a"
                ctx.enter_then_a_frame_index = 0
                ctx.enter_then_a_timer_ms = 0
                ctx.enter_then_a_phase = "playing"
                ctx.wait_after_enter_then_a_timer_ms = 0
                return
        if not ctx.running:
            return
        frames = ctx.assets.enter_gif_frames
        if ctx.enter_gif_phase == "playing" and frames:
            ctx.enter_gif_timer_ms += dt_ms
            while ctx.enter_gif_timer_ms >= frames[ctx.enter_gif_frame_index][1]:
                ctx.enter_gif_timer_ms -= frames[ctx.enter_gif_frame_index][1]
                ctx.enter_gif_frame_index += 1
                if ctx.enter_gif_frame_index >= len(frames):
                    ctx.enter_gif_phase = "waiting"
                    ctx.enter_gif_frame_index = len(frames) - 1
                    break
            ctx.screen.blit(frames[ctx.enter_gif_frame_index][0], (0, 0))
        elif ctx.enter_gif_phase == "waiting":
            ctx.wait_after_enter_gif_timer_ms += dt_ms
            if frames:
                ctx.screen.blit(frames[-1][0], (0, 0))
            if ctx.wait_after_enter_gif_timer_ms >= WAIT_AFTER_ENTER_GIF_MS:
                ctx.game_state = "versus_gif_enter_then_a"
                ctx.enter_then_a_frame_index = 0
                ctx.enter_then_a_timer_ms = 0
                ctx.enter_then_a_phase = "playing"
                ctx.wait_after_enter_then_a_timer_ms = 0
        else:
            ctx.game_state = "versus_gif_enter_then_a"
            ctx.enter_then_a_frame_index = 0
            ctx.enter_then_a_timer_ms = 0
            ctx.enter_then_a_phase = "playing"
            ctx.wait_after_enter_then_a_timer_ms = 0
        pygame.display.flip()
        ctx.clock.tick(60)


class EnterThenAGifScreen:
    def run(self, ctx):
        dt_ms = ctx.clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ctx.running = False
                return
        if not ctx.running:
            return
        frames = ctx.assets.enter_then_a_gif_frames
        if ctx.enter_then_a_phase == "playing" and frames:
            ctx.enter_then_a_timer_ms += dt_ms
            while ctx.enter_then_a_timer_ms >= frames[ctx.enter_then_a_frame_index][1]:
                ctx.enter_then_a_timer_ms -= frames[ctx.enter_then_a_frame_index][1]
                ctx.enter_then_a_frame_index += 1
                if ctx.enter_then_a_frame_index >= len(frames):
                    ctx.enter_then_a_phase = "waiting"
                    ctx.enter_then_a_frame_index = len(frames) - 1
                    break
            ctx.screen.blit(frames[ctx.enter_then_a_frame_index][0], (0, 0))
        elif ctx.enter_then_a_phase == "waiting":
            ctx.wait_after_enter_then_a_timer_ms += dt_ms
            if frames:
                ctx.screen.blit(frames[-1][0], (0, 0))
            if ctx.wait_after_enter_then_a_timer_ms >= WAIT_AFTER_ENTER_THEN_A_MS:
                ctx.game_state = "countdown"
                ctx.countdown_step = 0
                ctx.countdown_timer_ms = 0
        else:
            ctx.game_state = "countdown"
            ctx.countdown_step = 0
            ctx.countdown_timer_ms = 0
        pygame.display.flip()
        ctx.clock.tick(60)
