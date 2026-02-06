"""État de jeu principal (combat, caméra, HUD)."""
import random
import pygame
from game.config import (
    CAMERA_LERP, JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_ATTACK, JOY_BTN_GRAB, JOY_BTN_COUNTER, JOY_BTN_COUNTER_ALT, JOY_BTN_SPECIAL,
    DEBUG_JOYSTICK, DEBUG_JOYSTICK_VERBOSE, DEBUG_JOYSTICK_VERBOSE_INTERVAL,
)
from game.hud import draw_player_ping, draw_portraits, draw_percent_hud
from game.input_handling import get_player_input_state, start_attack_from_input, get_joystick_poll_events, get_effective_joy_count, _debug_joy_global_frame, safe_event_get
from combat.projectile_sprite import ProjectileSprite
from player.player import (
    DISTANCE_ATTACK_COOLDOWN_FRAMES,
    DISTANCE_ATTACK_BURST_DELAY,
    DISTANCE_ATTACK_BURST_SIZE,
    DISTANCE_ATTACK_NUM_BURSTS,
)


class PlayingScreen:
    def run(self, ctx):
        # Musique de combat (Sonic Unleashed - Endless Possibility)
        if getattr(ctx.assets, "combat_music_loaded", False) and not getattr(ctx, "combat_music_playing", False):
            try:
                if getattr(ctx, "menu_music_playing", False):
                    pygame.mixer.music.stop()
                    ctx.menu_music_playing = False
                pygame.mixer.music.load(ctx.assets.combat_music_path)
                pygame.mixer.music.set_volume(0.10)
                pygame.mixer.music.play(-1)
                ctx.combat_music_playing = True
            except Exception:
                pass
        # Conditions de victoire : selon le gagnant (P1 ou P2) et son personnage
        def _start_win_music():
            try:
                pygame.mixer.music.stop()
                if getattr(ctx.assets, "win_music_loaded", False):
                    pygame.mixer.music.load(ctx.assets.win_music_path)
                    pygame.mixer.music.set_volume(0.15)
                    pygame.mixer.music.play(0)
            except Exception:
                pass

        if ctx.player1.lives <= 0 and ctx.player2.lives > 0:
            # P2 gagne → écran selon le perso de P2
            winner_nick = getattr(ctx.player2, "character", None) == "nick"
            ctx.game_state = "nick_wins" if winner_nick else "judy_wins"
            ctx.nick_win_frame_index = 0
            ctx.nick_win_frame_timer_ms = 0
            ctx.judy_win_frame_index = 0
            ctx.judy_win_frame_timer_ms = 0
            _start_win_music()
            if winner_nick:
                if getattr(ctx.assets, "nick_win_sound_loaded", False):
                    try:
                        snd = pygame.mixer.Sound(ctx.assets.nick_win_sound_path)
                        snd.set_volume(1.0)
                        snd.play()
                    except Exception:
                        pass
            else:
                paths = getattr(ctx.assets, "judy_win_sound_paths", [])
                loaded = getattr(ctx.assets, "judy_win_sounds_loaded", [])
                if paths and loaded:
                    idx = random.randrange(len(paths))
                    if loaded[idx]:
                        try:
                            snd = pygame.mixer.Sound(paths[idx])
                            snd.set_volume(1.0)
                            snd.play()
                        except Exception:
                            pass
            ctx.combat_music_playing = False
            return
        if ctx.player2.lives <= 0 and ctx.player1.lives > 0:
            # P1 gagne → écran selon le perso de P1
            winner_nick = getattr(ctx.player1, "character", None) == "nick"
            ctx.game_state = "nick_wins" if winner_nick else "judy_wins"
            ctx.nick_win_frame_index = 0
            ctx.nick_win_frame_timer_ms = 0
            ctx.judy_win_frame_index = 0
            ctx.judy_win_frame_timer_ms = 0
            _start_win_music()
            if winner_nick:
                if getattr(ctx.assets, "nick_win_sound_loaded", False):
                    try:
                        snd = pygame.mixer.Sound(ctx.assets.nick_win_sound_path)
                        snd.set_volume(1.0)
                        snd.play()
                    except Exception:
                        pass
            else:
                paths = getattr(ctx.assets, "judy_win_sound_paths", [])
                loaded = getattr(ctx.assets, "judy_win_sounds_loaded", [])
                if paths and loaded:
                    idx = random.randrange(len(paths))
                    if loaded[idx]:
                        try:
                            snd = pygame.mixer.Sound(paths[idx])
                            snd.set_volume(1.0)
                            snd.play()
                        except Exception:
                            pass
            ctx.combat_music_playing = False
            return

        events = safe_event_get()
        n_joy_raw = pygame.joystick.get_count()
        n_joy = get_effective_joy_count()  # collant à 2 pour ne pas perdre P2 quand get_count() flicker
        # Toujours réassigner P1/P2 aux manettes (manette 0 = P1, manette 1 = P2)
        ctx.player1.joy_id = 0 if n_joy >= 1 else None
        ctx.player2.joy_id = 1 if n_joy >= 2 else None
        # Synchroniser joystick : ne créer qu'une seule fois (évite segfault macOS si on recrée à chaque frame)
        for pl in (ctx.player1, ctx.player2):
            if getattr(pl, "joy_id", None) is None or pl.joy_id >= n_joy_raw:
                pl.joystick = None
            elif getattr(pl, "joystick", None) is None:
                try:
                    pl.joystick = pygame.joystick.Joystick(pl.joy_id)
                    pl.joystick.init()
                except Exception:
                    pl.joystick = None
        # Forcer l'init des manettes physiquement présentes (on peut avoir effective=2 alors que raw=1)
        for jid in range(min(2, n_joy_raw)):
            try:
                pygame.joystick.Joystick(jid).init()
            except Exception:
                pass
        if n_joy_raw > 0:
            events.extend(get_joystick_poll_events(
                JOY_DEADZONE,
                (JOY_BTN_JUMP, JOY_BTN_ATTACK, JOY_BTN_SPECIAL, JOY_BTN_COUNTER, JOY_BTN_COUNTER_ALT, JOY_BTN_GRAB),  # 5=L1, 7=L2 (parade)
            ))
        if DEBUG_JOYSTICK_VERBOSE and _debug_joy_global_frame > 0 and _debug_joy_global_frame % DEBUG_JOYSTICK_VERBOSE_INTERVAL == 0:
            print(f"[Manette VERBOSE] frame={_debug_joy_global_frame} Playing: get_count()={n_joy} P1.joy_id={ctx.player1.joy_id} P2.joy_id={ctx.player2.joy_id} nb_events_manette={sum(1 for e in events if e.type in (pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN))}")
        for event in events:
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
                        if getattr(ctx.player1, "_distance_attack_cooldown_remaining", 0) <= 0:
                            ProjectileSprite(ctx.player1, ctx.hitboxes)
                            ctx.player1.start_distance_attack_animation()
                            ctx.player1._distance_attack_cooldown_remaining = DISTANCE_ATTACK_COOLDOWN_FRAMES
                            ctx.player1._distance_burst_remaining = DISTANCE_ATTACK_BURST_SIZE * DISTANCE_ATTACK_NUM_BURSTS - 1
                            ctx.player1._distance_burst_timer = DISTANCE_ATTACK_BURST_DELAY
                if event.key == ctx.player2.controls.get("special") and ctx.player2.lives > 0:
                    pl, pr, pu, pd = get_player_input_state(ctx.player2)
                    if pl or pr: ctx.player2.start_attack("side_special", ctx.hitboxes)
                    elif pu: ctx.player2.start_attack("up_special", ctx.hitboxes)
                    elif pd: ctx.player2.start_attack("down_special", ctx.hitboxes)
                    else:
                        if getattr(ctx.player2, "_distance_attack_cooldown_remaining", 0) <= 0:
                            ProjectileSprite(ctx.player2, ctx.hitboxes)
                            ctx.player2.start_distance_attack_animation()
                            ctx.player2._distance_attack_cooldown_remaining = DISTANCE_ATTACK_COOLDOWN_FRAMES
                            ctx.player2._distance_burst_remaining = DISTANCE_ATTACK_BURST_SIZE * DISTANCE_ATTACK_NUM_BURSTS - 1
                            ctx.player2._distance_burst_timer = DISTANCE_ATTACK_BURST_DELAY
            if event.type == pygame.JOYAXISMOTION and DEBUG_JOYSTICK_VERBOSE and abs(event.value) > JOY_DEADZONE:
                print(f"[Manette EVENT] JOYAXISMOTION joy={event.joy} axis={event.axis} value={event.value:.2f}")
            if event.type == pygame.JOYBUTTONDOWN:
                if DEBUG_JOYSTICK or DEBUG_JOYSTICK_VERBOSE:
                    print(f"[Manette EVENT] JOYBUTTONDOWN joy_id={event.joy} button={event.button}")
                joy_id, btn = event.joy, event.button
                # Manette 0 = P1, Manette 1 = P2 (quand n_joy >= 2)
                if joy_id == 0:
                    if btn == JOY_BTN_JUMP: ctx.player1.jump()
                    elif btn == JOY_BTN_ATTACK and ctx.player1.lives > 0:
                        start_attack_from_input(ctx.player1, ctx.hitboxes, "jab", "ftilt", "utilt", "dtilt", "nair", "fair", "bair", "uair", "dair")
                    elif btn in (JOY_BTN_COUNTER, JOY_BTN_COUNTER_ALT) and ctx.player1.lives > 0: ctx.player1.start_counter()
                    elif btn == JOY_BTN_SPECIAL and ctx.player1.lives > 0:
                        pl, pr, pu, pd = get_player_input_state(ctx.player1)
                        if pl or pr: ctx.player1.start_attack("side_special", ctx.hitboxes)
                        elif pu: ctx.player1.start_attack("up_special", ctx.hitboxes)
                        elif pd: ctx.player1.start_attack("down_special", ctx.hitboxes)
                        else:
                            if getattr(ctx.player1, "_distance_attack_cooldown_remaining", 0) <= 0:
                                ProjectileSprite(ctx.player1, ctx.hitboxes)
                                ctx.player1.start_distance_attack_animation()
                                ctx.player1._distance_attack_cooldown_remaining = DISTANCE_ATTACK_COOLDOWN_FRAMES
                                ctx.player1._distance_burst_remaining = DISTANCE_ATTACK_BURST_SIZE * DISTANCE_ATTACK_NUM_BURSTS - 1
                                ctx.player1._distance_burst_timer = DISTANCE_ATTACK_BURST_DELAY
                elif joy_id == 1 and n_joy >= 2:
                    if btn == JOY_BTN_JUMP: ctx.player2.jump()
                    elif btn == JOY_BTN_ATTACK and ctx.player2.lives > 0:
                        start_attack_from_input(ctx.player2, ctx.hitboxes, "jab", "ftilt", "utilt", "dtilt", "nair", "fair", "bair", "uair", "dair")
                    elif btn in (JOY_BTN_COUNTER, JOY_BTN_COUNTER_ALT) and ctx.player2.lives > 0: ctx.player2.start_counter()
                    elif btn == JOY_BTN_SPECIAL and ctx.player2.lives > 0:
                        pl, pr, pu, pd = get_player_input_state(ctx.player2)
                        if pl or pr: ctx.player2.start_attack("side_special", ctx.hitboxes)
                        elif pu: ctx.player2.start_attack("up_special", ctx.hitboxes)
                        elif pd: ctx.player2.start_attack("down_special", ctx.hitboxes)
                        else:
                            if getattr(ctx.player2, "_distance_attack_cooldown_remaining", 0) <= 0:
                                ProjectileSprite(ctx.player2, ctx.hitboxes)
                                ctx.player2.start_distance_attack_animation()
                                ctx.player2._distance_attack_cooldown_remaining = DISTANCE_ATTACK_COOLDOWN_FRAMES
                                ctx.player2._distance_burst_remaining = DISTANCE_ATTACK_BURST_SIZE * DISTANCE_ATTACK_NUM_BURSTS - 1
                                ctx.player2._distance_burst_timer = DISTANCE_ATTACK_BURST_DELAY

        # Rafale : décrémenter le timer puis tirer les projectiles 2 à 3 après le délai ; cooldown entre rafales
        for player in (ctx.player1, ctx.player2):
            cooldown = getattr(player, "_distance_attack_cooldown_remaining", 0)
            if cooldown > 0:
                player._distance_attack_cooldown_remaining = cooldown - 1
            burst_remaining = getattr(player, "_distance_burst_remaining", 0)
            if burst_remaining > 0:
                timer = getattr(player, "_distance_burst_timer", 0)
                player._distance_burst_timer = max(0, timer - 1)
                if player._distance_burst_timer <= 0:
                    ProjectileSprite(player, ctx.hitboxes)
                    player._distance_burst_remaining -= 1
                    player._distance_burst_timer = DISTANCE_ATTACK_BURST_DELAY

        ctx.player1.handle_input()
        ctx.player2.handle_input()
        # Secours double saut manette : si en l'air + bouton saut tenu et pas encore utilisé ce vol
        for pl in (ctx.player1, ctx.player2):
            if getattr(pl, "joystick", None) and not pl.on_ground and pl.jump_count < pl.jump_max:
                joy_in = pl._get_joy_input()
                if joy_in and joy_in[4] and not getattr(pl, "_did_air_jump_this_flight", True):
                    pl.jump()
                    pl._did_air_jump_this_flight = True
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
        ctx.platforms.draw(ctx.world_surface)
        ctx.players.draw(ctx.world_surface)
        # Fumée d'impact aléatoire (smog) quand un joueur reçoit un coup — visible ~12 frames
        smog_list = getattr(ctx.assets, "smog_surfaces", [])
        valid_smog = [s for s in smog_list if s is not None] if smog_list else []
        for pl in (ctx.player1, ctx.player2):
            if getattr(pl, "_show_smoke", False) and valid_smog:
                pl._show_smoke = False
                pl._smoke_surface = random.choice(valid_smog)
                pl._smoke_x, pl._smoke_y = pl.rect.centerx, pl.rect.centery
                pl._smoke_frames_remaining = 12
            if getattr(pl, "_smoke_frames_remaining", 0) > 0 and pl._smoke_surface is not None:
                surf = pl._smoke_surface
                w, h = surf.get_size()
                x = pl._smoke_x - w // 2
                y = pl._smoke_y - h // 2
                ctx.world_surface.blit(surf, (x, y))
                pl._smoke_frames_remaining -= 1
        draw_player_ping(ctx.world_surface, ctx.player1, ctx.assets.ping_p1, ctx.assets.ping_offset_above)
        draw_player_ping(ctx.world_surface, ctx.player2, ctx.assets.ping_p2, ctx.assets.ping_offset_above)
        ctx.screen.blit(ctx.world_surface, (0, 0), (int(ctx.camera_x), int(ctx.camera_y), ctx.screen_w, ctx.screen_h))

        hud_y = ctx.screen_h - ctx.assets.hud_bottom_y_offset
        percent_y = hud_y - 28
        margin = ctx.assets.portrait_side_margin
        draw_percent_hud(ctx.screen, ctx.player1, margin, percent_y, ctx.assets, align_left=True)
        draw_percent_hud(ctx.screen, ctx.player2, ctx.screen_w - margin, percent_y, ctx.assets, align_left=False)
        draw_portraits(ctx.screen, ctx.assets, ctx.screen_w, hud_y, ctx.player1, ctx.player2)
        pygame.display.flip()
        ctx.clock.tick(60)
