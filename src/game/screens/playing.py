"""État de jeu principal (combat, caméra, HUD)."""
import pygame
from game.config import CAMERA_LERP, JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_ATTACK, JOY_BTN_GRAB, JOY_BTN_COUNTER, JOY_BTN_SPECIAL, DEBUG_JOYSTICK
from game.hud import draw_player_ping, draw_portraits, draw_percent_hud
from game.input_handling import get_player_input_state, start_attack_from_input
from combat.projectile_sprite import ProjectileSprite


class PlayingScreen:
    def run(self, ctx):
        # Conditions de victoire
        if ctx.player1.lives <= 0 and ctx.player2.lives > 0 and getattr(ctx.player2, "character", None) == "nick":
            ctx.game_state = "nick_wins"
            ctx.nick_win_frame_index = 0
            ctx.nick_win_frame_timer_ms = 0
            return
        if ctx.player2.lives <= 0 and ctx.player1.lives > 0 and getattr(ctx.player1, "character", "judy") == "judy":
            ctx.game_state = "judy_wins"
            ctx.judy_win_frame_index = 0
            ctx.judy_win_frame_timer_ms = 0
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ctx.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == ctx.player1.controls["jump"]:
                    ctx.player1.jump()
                if event.key == ctx.player2.controls["jump"]:
                    ctx.player2.jump()
                if event.key == ctx.player1.controls["attacking"] and ctx.player1.lives > 0:
                    start_attack_from_input(ctx.player1, ctx.hitboxes, "jab", "ftilt", "utilt", "dtilt", "nair", "fair", "bair", "uair", "dair")
                if event.key == ctx.player2.controls["attacking"] and ctx.player2.lives > 0:
                    start_attack_from_input(ctx.player2, ctx.hitboxes, "jab", "ftilt", "utilt", "dtilt", "nair", "fair", "bair", "uair", "dair")
                if event.key == ctx.player1.controls.get("grab") and ctx.player1.lives > 0:
                    ctx.player1.start_attack("grab", ctx.hitboxes)
                if event.key == ctx.player2.controls.get("grab") and ctx.player2.lives > 0:
                    ctx.player2.start_attack("grab", ctx.hitboxes)
                if event.key == ctx.player1.controls.get("counter") and ctx.player1.lives > 0:
                    ctx.player1.start_counter()
                if event.key == ctx.player2.controls.get("counter") and ctx.player2.lives > 0:
                    ctx.player2.start_counter()
                if event.key == ctx.player1.controls.get("special") and ctx.player1.lives > 0:
                    pl, pr, pu, pd = get_player_input_state(ctx.player1)
                    if pl or pr: ctx.player1.start_attack("side_special", ctx.hitboxes)
                    elif pu: ctx.player1.start_attack("up_special", ctx.hitboxes)
                    elif pd: ctx.player1.start_attack("down_special", ctx.hitboxes)
                    else:
                        ProjectileSprite(ctx.player1, ctx.hitboxes)
                        ctx.player1.start_distance_attack_animation()
                if event.key == ctx.player2.controls.get("special") and ctx.player2.lives > 0:
                    pl, pr, pu, pd = get_player_input_state(ctx.player2)
                    if pl or pr: ctx.player2.start_attack("side_special", ctx.hitboxes)
                    elif pu: ctx.player2.start_attack("up_special", ctx.hitboxes)
                    elif pd: ctx.player2.start_attack("down_special", ctx.hitboxes)
                    else:
                        ProjectileSprite(ctx.player2, ctx.hitboxes)
                        ctx.player2.start_distance_attack_animation()
            if event.type == pygame.JOYAXISMOTION and DEBUG_JOYSTICK and abs(event.value) > JOY_DEADZONE:
                print(f"[Manette] axe joy={event.joy} axis={event.axis} value={event.value:.2f}")
            if event.type == pygame.JOYBUTTONDOWN:
                if DEBUG_JOYSTICK:
                    print(f"[Manette] bouton joy_id={event.joy} button={event.button}")
                joy_id, btn = event.joy, event.button
                if joy_id == 0 and getattr(ctx.player1, "joy_id", None) == 0:
                    if btn == JOY_BTN_JUMP: ctx.player1.jump()
                    elif btn == JOY_BTN_ATTACK and ctx.player1.lives > 0:
                        start_attack_from_input(ctx.player1, ctx.hitboxes, "jab", "ftilt", "utilt", "dtilt", "nair", "fair", "bair", "uair", "dair")
                    elif btn == JOY_BTN_GRAB and ctx.player1.lives > 0: ctx.player1.start_attack("grab", ctx.hitboxes)
                    elif btn == JOY_BTN_COUNTER and ctx.player1.lives > 0: ctx.player1.start_counter()
                    elif btn == JOY_BTN_SPECIAL and ctx.player1.lives > 0:
                        pl, pr, pu, pd = get_player_input_state(ctx.player1)
                        if pl or pr: ctx.player1.start_attack("side_special", ctx.hitboxes)
                        elif pu: ctx.player1.start_attack("up_special", ctx.hitboxes)
                        elif pd: ctx.player1.start_attack("down_special", ctx.hitboxes)
                        else:
                            ProjectileSprite(ctx.player1, ctx.hitboxes)
                            ctx.player1.start_distance_attack_animation()
                if joy_id == 1 and getattr(ctx.player2, "joy_id", None) == 1:
                    if btn == JOY_BTN_JUMP: ctx.player2.jump()
                    elif btn == JOY_BTN_ATTACK and ctx.player2.lives > 0:
                        start_attack_from_input(ctx.player2, ctx.hitboxes, "jab", "ftilt", "utilt", "dtilt", "nair", "fair", "bair", "uair", "dair")
                    elif btn == JOY_BTN_GRAB and ctx.player2.lives > 0: ctx.player2.start_attack("grab", ctx.hitboxes)
                    elif btn == JOY_BTN_COUNTER and ctx.player2.lives > 0: ctx.player2.start_counter()
                    elif btn == JOY_BTN_SPECIAL and ctx.player2.lives > 0:
                        pl, pr, pu, pd = get_player_input_state(ctx.player2)
                        if pl or pr: ctx.player2.start_attack("side_special", ctx.hitboxes)
                        elif pu: ctx.player2.start_attack("up_special", ctx.hitboxes)
                        elif pd: ctx.player2.start_attack("down_special", ctx.hitboxes)
                        else:
                            ProjectileSprite(ctx.player2, ctx.hitboxes)
                            ctx.player2.start_distance_attack_animation()

        ctx.player1.handle_input()
        ctx.player2.handle_input()
        ctx.player1.update([ctx.player2] + list(ctx.platforms))
        ctx.player2.update([ctx.player1] + list(ctx.platforms))
        ctx.hitboxes.update(list(ctx.players))

        living = [p for p in (ctx.player1, ctx.player2) if getattr(p, "lives", 1) > 0]
        if living:
            cx = sum(p.rect.centerx for p in living) / len(living)
            cy = sum(p.rect.centery for p in living) / len(living)
            target_x = max(0, min(ctx.world_w - ctx.screen_w, cx - ctx.screen_w / 2))
            target_y = max(0, min(ctx.world_h - ctx.screen_h, cy - ctx.screen_h / 2))
            ctx.camera_x += (target_x - ctx.camera_x) * CAMERA_LERP
            ctx.camera_y += (target_y - ctx.camera_y) * CAMERA_LERP
            ctx.camera_x = max(0, min(ctx.world_w - ctx.screen_w, ctx.camera_x))
            ctx.camera_y = max(0, min(ctx.world_h - ctx.screen_h, ctx.camera_y))

        ctx.world_surface.blit(ctx.assets.background, (0, 0))
        ctx.hitboxes.draw(ctx.world_surface)
        for hb in ctx.hitboxes:
            hb.draw_hitboxes_debug(ctx.world_surface)
        ctx.platforms.draw(ctx.world_surface)
        ctx.players.draw(ctx.world_surface)
        draw_player_ping(ctx.world_surface, ctx.player1, ctx.assets.ping_p1, ctx.assets.ping_offset_above)
        draw_player_ping(ctx.world_surface, ctx.player2, ctx.assets.ping_p2, ctx.assets.ping_offset_above)
        ctx.screen.blit(ctx.world_surface, (0, 0), (int(ctx.camera_x), int(ctx.camera_y), ctx.screen_w, ctx.screen_h))

        hud_y = ctx.screen_h - ctx.assets.hud_bottom_y_offset
        percent_y = hud_y - 28
        margin = ctx.assets.portrait_side_margin
        draw_percent_hud(ctx.screen, ctx.player1, margin, percent_y, ctx.assets, align_left=True)
        draw_percent_hud(ctx.screen, ctx.player2, ctx.screen_w - margin, percent_y, ctx.assets, align_left=False)
        draw_portraits(ctx.screen, ctx.assets, ctx.screen_w, hud_y)
        pygame.display.flip()
        ctx.clock.tick(60)
