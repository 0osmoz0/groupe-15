"""
Sélection de personnage : P1 choisit en premier (clavier ou joy 0), puis P2 (joy 1).
P2 ne peut pas prendre le même perso que P1.
"""
import pygame
from game.config import JOY_DEADZONE, JOY_BTN_JUMP, JOY_BTN_START
from game.input_handling import get_joystick_poll_events, safe_event_get


class CharacterSelectScreen:
    def run(self, ctx):
        # Récupère les events + ceux des manettes (poll) pour que les gamepads répondent bien
        events = safe_event_get()
        n_joy = pygame.joystick.get_count()
        for jid in range(min(2, n_joy)):
            try:
                pygame.joystick.Joystick(jid).init()
            except Exception:
                pass
        if n_joy > 0:
            events.extend(get_joystick_poll_events(JOY_DEADZONE, (JOY_BTN_JUMP, JOY_BTN_START)))

        for event in events:
            if event.type == pygame.QUIT:
                ctx.running = False
                return

            # On filtre les events manette : P1 = joy 0, P2 = joy 1 (sinon on ignore)
            joy_ok_p1 = n_joy > 0 and getattr(event, "joy", -1) == 0
            joy_ok_p2 = n_joy > 1 and getattr(event, "joy", -1) == 1

            # Liste de touches acceptées : config du joueur + flèches + Entrée/Espace en secours (AZERTY, etc.)
            p1_left = (ctx.player1.controls.get("left", pygame.K_a), pygame.K_LEFT, pygame.K_q)
            p1_right = (ctx.player1.controls.get("right", pygame.K_d), pygame.K_RIGHT)
            p2_left = (ctx.player2.controls.get("left", pygame.K_LEFT), pygame.K_LEFT)
            p2_right = (ctx.player2.controls.get("right", pygame.K_RIGHT), pygame.K_RIGHT)
            confirm_keys = (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER)
            p2_confirm = (ctx.player2.controls.get("jump", pygame.K_UP), pygame.K_UP) + confirm_keys

            # ——— Phase Joueur 1 : il bouge le curseur et valide
            if ctx.char_select_phase == "p1":
                if event.type == pygame.KEYDOWN:
                    if event.key in p1_left:
                        ctx.char_select_cursor = (ctx.char_select_cursor - 1) % len(ctx.characters)
                    elif event.key in p1_right:
                        ctx.char_select_cursor = (ctx.char_select_cursor + 1) % len(ctx.characters)
                    elif event.key in confirm_keys:
                        self._confirm(ctx)
                        return
                # Manette : stick horizontal ou bouton A/Start pour confirmer
                if event.type == pygame.JOYAXISMOTION and joy_ok_p1 and event.axis == 0:
                    ax = event.value
                    if ax < -JOY_DEADZONE:
                        ctx.char_select_cursor = (ctx.char_select_cursor - 1) % len(ctx.characters)
                    elif ax > JOY_DEADZONE:
                        ctx.char_select_cursor = (ctx.char_select_cursor + 1) % len(ctx.characters)
                if event.type == pygame.JOYBUTTONDOWN and joy_ok_p1 and event.button in (JOY_BTN_JUMP, JOY_BTN_START):
                    self._confirm(ctx)
                    return

            # ——— Phase Joueur 2 : pareil, mais on saute le perso déjà pris par P1
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key in p2_left:
                        ctx.char_select_cursor = (ctx.char_select_cursor - 1) % len(ctx.characters)
                        # Si on tombe sur le perso de P1, on recule encore d’un cran
                        if ctx.characters[ctx.char_select_cursor] == ctx.p1_character_choice:
                            ctx.char_select_cursor = (ctx.char_select_cursor - 1) % len(ctx.characters)
                    elif event.key in p2_right:
                        ctx.char_select_cursor = (ctx.char_select_cursor + 1) % len(ctx.characters)
                        if ctx.characters[ctx.char_select_cursor] == ctx.p1_character_choice:
                            ctx.char_select_cursor = (ctx.char_select_cursor + 1) % len(ctx.characters)
                    elif event.key in p2_confirm:
                        self._confirm(ctx)
                        return
                if event.type == pygame.JOYAXISMOTION and joy_ok_p2 and event.axis == 0:
                    ax = event.value
                    if ax < -JOY_DEADZONE:
                        ctx.char_select_cursor = (ctx.char_select_cursor - 1) % len(ctx.characters)
                        if ctx.characters[ctx.char_select_cursor] == ctx.p1_character_choice:
                            ctx.char_select_cursor = (ctx.char_select_cursor - 1) % len(ctx.characters)
                    elif ax > JOY_DEADZONE:
                        ctx.char_select_cursor = (ctx.char_select_cursor + 1) % len(ctx.characters)
                        if ctx.characters[ctx.char_select_cursor] == ctx.p1_character_choice:
                            ctx.char_select_cursor = (ctx.char_select_cursor + 1) % len(ctx.characters)
                if event.type == pygame.JOYBUTTONDOWN and joy_ok_p2 and event.button in (JOY_BTN_JUMP, JOY_BTN_START):
                    self._confirm(ctx)
                    return

        if not ctx.running:
            return
        self._draw(ctx)
        pygame.display.flip()
        ctx.clock.tick(60)

    def _confirm(self, ctx):
        """Quand un joueur valide : soit on passe à P2, soit on lance la partie (vidéo ou versus)."""
        if ctx.char_select_phase == "p1":
            # P1 a choisi → on enregistre et on passe au tour de P2
            ctx.p1_character_choice = ctx.characters[ctx.char_select_cursor]
            ctx.char_select_phase = "p2"
            # Curseur P2 : on met sur l’autre perso par défaut pour éviter de rester sur celui de P1
            ctx.char_select_cursor = 1 if ctx.p1_character_choice == "judy" else 0
        else:
            # P2 a choisi → on assigne les persos aux joueurs et on enchaîne
            ctx.p2_character_choice = ctx.characters[ctx.char_select_cursor]
            ctx.assets.background = ctx.assets.map_surfaces[ctx.selected_map_index].copy()
            ctx.player1.set_character(ctx.p1_character_choice)
            ctx.player2.set_character(ctx.p2_character_choice)
            # Selon les combos Judy/Nick on part sur la bonne intro vidéo ou direct versus
            if ctx.p1_character_choice == "judy" and ctx.p2_character_choice == "nick":
                ctx.intro_video_filename = "1.mp4"
                ctx.game_state = "intro_video"
            elif ctx.p1_character_choice == "nick" and ctx.p2_character_choice == "judy":
                ctx.intro_video_filename = "1_2.mp4"
                ctx.game_state = "intro_video"
            else:
                ctx.game_state = "versus_gif"
                ctx.versus_gif_frame_index = 0
                ctx.versus_gif_timer_ms = 0
                ctx.versus_gif_phase = "playing"
                ctx.wait_after_gif_timer_ms = 0

    def _draw(self, ctx):
        """Dessine l’écran : fond, titre (J1 ou J2), slots des persos, curseur, hint en bas."""
        # Fond : image dédiée, sinon menu, sinon couleur unie
        if getattr(ctx.assets, "character_select_background", None):
            ctx.screen.blit(ctx.assets.character_select_background, (0, 0))
        elif ctx.assets.menu_background:
            ctx.screen.blit(ctx.assets.menu_background, (0, 0))
        else:
            ctx.screen.fill((30, 30, 50))

        title_text = "Joueur 1 - Choisis ton personnage" if ctx.char_select_phase == "p1" else "Joueur 2 - Choisis ton personnage"
        try:
            font_cs = pygame.font.SysFont("arial", 52, bold=True)
            font_opt = pygame.font.SysFont("arial", 42, bold=True)
        except Exception:
            font_cs = ctx.assets.font_percent
            font_opt = ctx.assets.font_percent

        title_surf = font_cs.render(title_text, True, (255, 255, 255))
        ctx.screen.blit(title_surf, title_surf.get_rect(center=(ctx.screen_w // 2, ctx.screen_h // 4)))

        # Une case par personnage (Judy, Nick), centrées à gauche/droite
        opt_y = ctx.screen_h // 2
        slot_w, slot_h = 280, 80
        for i, label in enumerate(ctx.character_labels):
            taken = ctx.char_select_phase == "p2" and ctx.p1_character_choice is not None and ctx.characters[i] == ctx.p1_character_choice
            x_center = ctx.screen_w // 2 + (i * 2 - 1) * 320
            slot_rect = pygame.Rect(x_center - slot_w // 2, opt_y - slot_h // 2, slot_w, slot_h)

            if taken:
                # En phase P2, le perso pris par P1 est grisé + texte "CHOISI PAR J1"
                pygame.draw.rect(ctx.screen, (180, 80, 80), slot_rect, 3)
                pris = font_cs.render("CHOISI PAR J1", True, (255, 200, 200))
                ctx.screen.blit(pris, pris.get_rect(center=slot_rect.center))
                lbl = font_opt.render(ctx.character_labels[i], True, (120, 120, 120))
                ctx.screen.blit(lbl, lbl.get_rect(center=(x_center, slot_rect.bottom - 18)))
            else:
                # Case sélectionnable : surlignée en jaune si c’est le curseur
                color = (255, 220, 100) if i == ctx.char_select_cursor else (200, 200, 200)
                opt = font_opt.render(label, True, color)
                opt_rect = opt.get_rect(center=(x_center, opt_y))
                if i == ctx.char_select_cursor:
                    pygame.draw.rect(ctx.screen, (255, 220, 100), slot_rect, 2)
                    cur = font_opt.render(">", True, (255, 220, 100))
                    ctx.screen.blit(cur, (opt_rect.left - 40, opt_rect.centery - cur.get_height() // 2))
                ctx.screen.blit(opt, opt_rect)

        hint = font_opt.render("Fleches ou A/D : deplacer   Entree ou Espace : valider", True, (160, 160, 160))
        ctx.screen.blit(hint, hint.get_rect(center=(ctx.screen_w // 2, ctx.screen_h - 80)))
