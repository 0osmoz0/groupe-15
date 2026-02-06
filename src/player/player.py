import math
import os
import pygame
from game.config import JOY_DEADZONE
from player.stats import Stats
from combat.hitbox_sprite import HitboxSprite
from combat.knockback import decay_launch_speed

WALK_ANIM_FRAMES = 8
SPRITE_HEIGHT = 130
SPRITE_WIDTH_SCALE = 0.85
ATTACK_ANIM_DURATION = 24
ATTACK_ANIM_FRAME_DURATION = 8


def _load_walk_frames(character: str):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if character == "nick":
        folder = os.path.join(base, "assets", "Nick", "nick_walk")
        paths = [os.path.join(folder, "1.png"), os.path.join(folder, "2.png")]
    else:
        folder = os.path.join(base, "assets", "JUDY_HOPPS", "judy_hopps_walk")
        paths = [os.path.join(folder, "1.png"), os.path.join(folder, "2.png"), os.path.join(folder, "3.png")]
    frames_raw = [pygame.image.load(p).convert_alpha() for p in paths]
    h = SPRITE_HEIGHT
    w = max(max(1, int(f.get_width() * h / f.get_height() * SPRITE_WIDTH_SCALE)) for f in frames_raw)
    return [pygame.transform.smoothscale(f, (w, h)) for f in frames_raw]


def _load_attack_frames(character: str):
    """Charge toutes les frames d'attaque (Nick: nick_atack 1-3, Judy: judy_attack_normal 1-6)."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if character == "nick":
        folder = os.path.join(base, "assets", "Nick", "nick_atack")
        n_frames = 3
    else:
        folder = os.path.join(base, "assets", "JUDY_HOPPS", "judy_attack_normal")
        n_frames = 6
    result = []
    for i in range(n_frames):
        path = os.path.join(folder, f"{i + 1}.png")
        try:
            img = pygame.image.load(path).convert_alpha()
            h = SPRITE_HEIGHT
            w = max(1, int(img.get_width() * h / img.get_height() * SPRITE_WIDTH_SCALE))
            result.append(pygame.transform.smoothscale(img, (w, h)))
        except Exception:
            result.append(None)
    return result


def _load_distance_attack_frame(character: str):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if character == "nick":
        path = os.path.join(base, "assets", "Nick", "nick_distance_attack", "1.png")
    elif character == "judy":
        path = os.path.join(base, "assets", "JUDY_HOPPS", "judy_distance", "1.png")
    else:
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        h = SPRITE_HEIGHT
        w = max(1, int(img.get_width() * h / img.get_height() * SPRITE_WIDTH_SCALE))
        return pygame.transform.smoothscale(img, (w, h))
    except Exception:
        return None


def _load_counter_frame(character: str):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if character == "nick":
        path = os.path.join(base, "assets", "Nick", "nick_hold", "1.png")
    elif character == "judy":
        path = os.path.join(base, "assets", "JUDY_HOPPS", "judy_hold", "1-removebg-preview-2.png")
    else:
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        h = SPRITE_HEIGHT
        w = max(1, int(img.get_width() * h / img.get_height() * SPRITE_WIDTH_SCALE))
        return pygame.transform.smoothscale(img, (w, h))
    except Exception:
        return None


DISTANCE_ATTACK_DURATION = 28
DISTANCE_ATTACK_COOLDOWN_FRAMES = 0   # munition infinie
DISTANCE_ATTACK_BURST_SIZE = 3        # 3 projectiles par rafale (délai entre chaque tir)
DISTANCE_ATTACK_NUM_BURSTS = 1        # 1 rafale de 3 = 3 tirs au total
DISTANCE_ATTACK_BURST_DELAY = 8       # frames entre chaque tir
COUNTER_DURATION = 40


class Player(pygame.sprite.Sprite):
    STALE_QUEUE_MAX = 9
    STALE_DECAY_PER_USE = 0.09
    CROUCH_CANCEL_MULT = 0.67
    BLAST_MARGIN = 250
    RESPAWN_INVULN_FRAMES = 120
    COYOTE_FRAMES = 10
    JUMP_BUFFER_FRAMES = 8
    KNOCKBACK_SCALE = 5.0

    _walk_frames_cache = {}
    _attack_frames_cache = {}
    _distance_attack_frame_cache = {}
    _counter_frame_cache = {}

    def __init__(self, start_pos, color, controls, screen_size, character: str = "judy", joystick_id=None):
        super().__init__()
        self.screen_width, self.screen_height = screen_size
        self.color = color
        self.character = character

        # Manette : id stocké, objet Joystick assigné plus tard par init_joysticks() (évite segfault macOS)
        self.joystick_id = joystick_id
        self.joystick = None

        # Charger sprites
        if self.character not in Player._walk_frames_cache:
            Player._walk_frames_cache[self.character] = _load_walk_frames(self.character)
        if self.character not in Player._attack_frames_cache:
            Player._attack_frames_cache[self.character] = _load_attack_frames(self.character)
        if self.character not in Player._distance_attack_frame_cache:
            Player._distance_attack_frame_cache[self.character] = _load_distance_attack_frame(self.character)
        if self.character not in Player._counter_frame_cache:
            Player._counter_frame_cache[self.character] = _load_counter_frame(self.character)

        self._walk_frames = Player._walk_frames_cache[self.character]
        self._attack_frames = Player._attack_frames_cache[self.character]
        self._distance_attack_frame = Player._distance_attack_frame_cache[self.character]
        self._counter_frame = Player._counter_frame_cache[self.character]

        self._walk_index = 0
        self._anim_timer = 0
        self._attack_animation_remaining = 0
        self._attack_animation_variant = 0
        self._attack_variant_toggle = 0
        self._attack_frame_index = 0
        self._attack_frame_timer = 0
        self._distance_attack_remaining = 0
        self._counter_remaining = 0

        self.image = self._walk_frames[0].copy()
        self.rect = self.image.get_rect(topleft=start_pos)
        self.spawn_pos = start_pos
        self.prev_y = self.rect.y
        self.drop_through = False

        self.controls = controls
        self.joy_id = joystick_id  # Compatibilité ancien code
        
        self.speed_x = 0
        self.speed_y = 0
        self.gravity = 0.42
        self.move_speed = 5
        self.air_move_mult = 0.95
        self.jump_count = 0
        self.jump_max = 2
        self.jump_force = -15.5
        self.double_jump_mult = 1.1
        self.jump_cut_speed = -6.0
        self.coyote_frames = 0
        self.jump_buffer_frames = 0
        self._jump_held = False
        self._did_air_jump_this_flight = False  # double saut manette (1 saut en l'air par vol)
        self._jump_btn_prev = False  # état précédent du bouton saut (détection "just pressed")

        self.stats = Stats(weight=1.0)
        self.lives = 3
        self.state = "idle"
        self.hitstun = 0
        self.facing_right = True
        self.tumbling = False
        self.crouching = False
        self.di_angle_rad = None
        self.stale_queue = []
        self.gravity_for_kb = 0.05
        self.respawn_invuln = 0
        self.on_ground = False

    def respawn(self):
        self.rect.topleft = self.spawn_pos
        self.speed_x = 0
        self.speed_y = 0
        self.hitstun = 0
        self.tumbling = False
        self.crouching = False
        self.on_ground = False
        self.jump_count = 0
        self.stats.percent = 0
        self.state = "idle"
        self.respawn_invuln = self.RESPAWN_INVULN_FRAMES

    def set_character(self, new_character: str):
        """Change le personnage (judy / nick) et met à jour sprites et image."""
        if new_character not in ("judy", "nick"):
            return
        self.character = new_character
        if self.character not in Player._walk_frames_cache:
            Player._walk_frames_cache[self.character] = _load_walk_frames(self.character)
        if self.character not in Player._attack_frames_cache:
            Player._attack_frames_cache[self.character] = _load_attack_frames(self.character)
        if self.character not in Player._distance_attack_frame_cache:
            Player._distance_attack_frame_cache[self.character] = _load_distance_attack_frame(self.character)
        if self.character not in Player._counter_frame_cache:
            Player._counter_frame_cache[self.character] = _load_counter_frame(self.character)
        self._walk_frames = Player._walk_frames_cache[self.character]
        self._attack_frames = Player._attack_frames_cache[self.character]
        self._distance_attack_frame = Player._distance_attack_frame_cache[self.character]
        self._counter_frame = Player._counter_frame_cache[self.character]
        self.image = self._walk_frames[0].copy()
        cx, cy = self.rect.center
        self.rect = self.image.get_rect(center=(cx, cy))

    def _get_joy_input(self):
        """✅ CORRIGÉ : Retourne (left, right, up, down, jump_held) depuis la manette si connectée."""
        # ✅ Vérifier si la manette existe
        if self.joystick is None:
            # Tenter de la réinitialiser si elle a été déconnectée
            if self.joystick_id is not None and self.joystick_id < pygame.joystick.get_count():
                try:
                    self.joystick = pygame.joystick.Joystick(self.joystick_id)
                    self.joystick.init()
                except:
                    return None
            else:
                return None
        
        try:
            dead = JOY_DEADZONE

            # Axes analogiques
            ax0 = self.joystick.get_axis(0) if self.joystick.get_numaxes() > 0 else 0.0
            ax1 = self.joystick.get_axis(1) if self.joystick.get_numaxes() > 1 else 0.0

            left = ax0 < -dead
            right = ax0 > dead
            up = ax1 < -dead
            down = ax1 > dead
            
            # D-Pad (croix directionnelle)
            if self.joystick.get_numhats() > 0:
                hx, hy = self.joystick.get_hat(0)
                if hx < 0:
                    left = True
                if hx > 0:
                    right = True
                if hy > 0:
                    up = True
                if hy < 0:
                    down = True
            
            # Bouton saut (A sur Xbox, Croix sur PS)
            jump_held = self.joystick.get_button(0) if self.joystick.get_numbuttons() > 0 else False
            
            return (left, right, up, down, jump_held)
        
        except Exception as e:
            print(f"⚠️ Erreur lecture manette {self.joystick_id}: {e}")
            return None

    def update_di(self):
        """Directional Influence pour le knockback"""
        joy_in = self._get_joy_input()
        if joy_in is not None:
            left, right, up, down, _ = joy_in
            dx = 1 if right else (-1 if left else 0)
            dy = 1 if up else (-1 if down else 0)
        else:
            keys = pygame.key.get_pressed()
            dx = 1 if keys[self.controls["right"]] else (-1 if keys[self.controls["left"]] else 0)
            dy = 1 if keys[self.controls["jump"]] else (-1 if keys[self.controls.get("down", pygame.K_s)] else 0)
        
        if dx != 0 or dy != 0:
            self.di_angle_rad = math.atan2(dy, dx)
        else:
            self.di_angle_rad = None

    def get_di_angle_rad(self):
        return self.di_angle_rad

    def get_stale_damage_mult(self, attack_id: str) -> float:
        n = self.stale_queue.count(attack_id)
        mult = 1.0 - self.STALE_DECAY_PER_USE * min(self.STALE_QUEUE_MAX, n)
        return max(0.1, mult)

    def push_stale(self, attack_id: str):
        self.stale_queue.append(attack_id)
        if len(self.stale_queue) > self.STALE_QUEUE_MAX:
            self.stale_queue.pop(0)

    def handle_input(self):
        """✅ CORRIGÉ : Gère manette OU clavier"""
        if self.lives <= 0:
            return
        if self.hitstun > 0:
            return
        
        self.speed_x = 0
        move = self.move_speed if self.on_ground else self.move_speed * self.air_move_mult

        # ✅ PRIORITÉ MANETTE
        joy_in = self._get_joy_input()
        if joy_in is not None:
            left, right, up, down, jump_held = joy_in
            
            if left:
                self.speed_x = -move
                self.facing_right = False
            if right:
                self.speed_x = move
                self.facing_right = True
            
            self.drop_through = down and jump_held
            # Double saut manette : même logique que clavier = 2 appuis distincts (pas en restant appuyé)
            jump_just_pressed = jump_held and not getattr(self, "_jump_btn_prev", False)
            if not self.on_ground and self.jump_count < self.jump_max and not self._did_air_jump_this_flight and jump_just_pressed:
                self.jump()
                self._did_air_jump_this_flight = True
            self._jump_held = jump_held
            self._jump_btn_prev = jump_held
        
        # ✅ FALLBACK CLAVIER
        else:
            keys = pygame.key.get_pressed()
            
            if keys[self.controls["left"]]:
                self.speed_x = -move
                self.facing_right = False
            if keys[self.controls["right"]]:
                self.speed_x = move
                self.facing_right = True
            
            self.drop_through = keys[self.controls.get("down", pygame.K_s)] and keys[self.controls["jump"]]
            self._jump_held = keys[self.controls["jump"]]
            self._jump_btn_prev = keys[self.controls["jump"]]

    def start_attack(self, attack_id: str, hitboxes_group, charge_mult: float = 1.0):
        hb = HitboxSprite(owner=self, attack_id=attack_id, charge_mult=charge_mult)
        hitboxes_group.add(hb)
        self._attack_animation_remaining = ATTACK_ANIM_DURATION
        self._attack_animation_variant = self._attack_variant_toggle
        self._attack_variant_toggle = (self._attack_variant_toggle + 1) % 2
        self._attack_frame_index = 0
        self._attack_frame_timer = 0

    def start_distance_attack_animation(self):
        if self._distance_attack_frame is not None:
            self._distance_attack_remaining = DISTANCE_ATTACK_DURATION

    def start_counter(self):
        self._counter_remaining = COUNTER_DURATION

    def _update_walk_animation(self):
        """Met à jour l'animation de marche"""
        if self._counter_remaining > 0:
            self._counter_remaining -= 1
            if self._counter_frame is not None:
                frame = self._counter_frame
                flip_x = self.facing_right if self.character == "nick" else not self.facing_right
                self.image = pygame.transform.flip(frame, flip_x, False)
            return
        
        if self._distance_attack_remaining > 0:
            self._distance_attack_remaining -= 1
            if self._distance_attack_frame is not None:
                frame = self._distance_attack_frame
                flip_x = self.facing_right if self.character == "nick" else not self.facing_right
                self.image = pygame.transform.flip(frame, flip_x, False)
            return
        
        if self._attack_animation_remaining > 0:
            self._attack_animation_remaining -= 1
            self._attack_frame_timer += 1
            if self._attack_frame_timer >= ATTACK_ANIM_FRAME_DURATION:
                self._attack_frame_timer = 0
                self._attack_frame_index += 1
            idx = min(self._attack_frame_index, len(self._attack_frames) - 1)
            if idx >= 0 and self._attack_frames[idx] is not None:
                frame = self._attack_frames[idx]
            else:
                frame = self._walk_frames[0]
            flip_x = self.facing_right if self.character == "nick" else not self.facing_right
            self.image = pygame.transform.flip(frame, flip_x, False)
            return
        
        if self.speed_x != 0:
            self._anim_timer += 1
            if self._anim_timer >= WALK_ANIM_FRAMES:
                self._anim_timer = 0
                n = len(self._walk_frames)
                step = 1 if self.facing_right else -1
                self._walk_index = (self._walk_index + step) % n
        else:
            self._walk_index = 0
            self._anim_timer = 0
        
        frame = self._walk_frames[self._walk_index]
        flip_x = self.facing_right if self.character == "nick" else not self.facing_right
        self.image = pygame.transform.flip(frame, flip_x, False)

    def jump(self):
        if self.coyote_frames > 0:
            self.speed_y = self.jump_force
            self.jump_count = 1
            self.drop_through = False
            self.coyote_frames = 0
            self.jump_buffer_frames = 0
            self._jump_held = True
        elif self.jump_count < self.jump_max:
            mult = self.double_jump_mult if self.jump_count > 0 else 1.0
            self.speed_y = self.jump_force * mult
            self.jump_count += 1
            self._did_air_jump_this_flight = True
            self.drop_through = False
            self.coyote_frames = 0
            self.jump_buffer_frames = 0
            self._jump_held = True
        else:
            self.jump_buffer_frames = self.JUMP_BUFFER_FRAMES

    def receive_hit(self, hit_result):
        if self.respawn_invuln > 0:
            return
        self.stats.take_damage(hit_result.damage_dealt)
        self.speed_x = hit_result.velocity_x * self.KNOCKBACK_SCALE
        self.speed_y = hit_result.velocity_y * self.KNOCKBACK_SCALE
        self.hitstun = hit_result.hitstun_frames
        self.tumbling = hit_result.tumble
        self.state = "hitstun"

    def update(self, platforms):
        """✅ Mise à jour complète du joueur"""
        if self.respawn_invuln > 0:
            self.respawn_invuln -= 1
        
        if self.lives <= 0:
            return
        
        self.prev_y = self.rect.y
        prev_on_ground = self.on_ground
        self.on_ground = False
        self.crouching = False

        if self.hitstun > 0:
            self.hitstun -= 1
            if self.hitstun == 0:
                self.tumbling = False
                self.state = "idle"
            if self.tumbling:
                self.speed_x, self.speed_y = decay_launch_speed(self.speed_x, self.speed_y)
            else:
                self.speed_y += self.gravity_for_kb
        else:
            self.handle_input()
            self.speed_y += self.gravity
            
            # ✅ Jump cut (relâcher saut = moins haut)
            if not self._jump_held and self.speed_y < self.jump_cut_speed:
                self.speed_y = self.jump_cut_speed

        self.rect.x += int(self.speed_x)
        self.rect.y += int(self.speed_y)

        # Collisions avec plateformes et autres joueurs
        others = list(platforms)
        for player in pygame.sprite.Group():
            if hasattr(player, 'lives') and player != self:
                others.append(player)

        for other in others:
            if not hasattr(other, "rect"):
                continue

            other_collide_rect = other.rect
            surface_offset = getattr(other, "surface_offset", 0)
            if surface_offset > 0:
                so = surface_offset
                other_collide_rect = pygame.Rect(
                    other.rect.left, other.rect.top + so,
                    other.rect.width, other.rect.height - so
                )
            
            if not self.rect.colliderect(other_collide_rect):
                continue

            is_other_player = getattr(other, "lives", None) is not None
            if is_other_player:
                overlap_left = max(0, self.rect.right - other.rect.left)
                overlap_right = max(0, other.rect.right - self.rect.left)
                overlap_top = max(0, self.rect.bottom - other.rect.top)
                overlap_bottom = max(0, other.rect.bottom - self.rect.top)
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                
                if min_overlap > 0:
                    if min_overlap == overlap_left:
                        self.rect.x -= overlap_left
                    elif min_overlap == overlap_right:
                        self.rect.x += overlap_right
                    elif min_overlap == overlap_top:
                        self.rect.y -= overlap_top
                    else:
                        self.rect.y += overlap_bottom
                continue

            surface_top = other.rect.top + getattr(other, "surface_offset", 0)
            one_way = getattr(other, "one_way", False)
            
            if one_way:
                if (
                    self.speed_y > 0 and
                    self.prev_y + self.rect.height <= surface_top and
                    not self.drop_through
                ):
                    self.rect.bottom = surface_top
                    self.speed_y = 0
                    self.jump_count = 0
                    self.on_ground = True
            else:
                if self.speed_y > 0:
                    self.rect.bottom = surface_top
                    self.speed_y = 0
                    self.jump_count = 0
                    self.on_ground = True
                elif self.speed_y < 0:
                    self.rect.top = other.rect.bottom
                    self.speed_y = 0
        
        # Crouch
        if self.on_ground:
            joy_in = self._get_joy_input()
            down_pressed = (joy_in[3] if joy_in is not None else False) or (
                pygame.key.get_pressed()[self.controls.get("down", pygame.K_s)]
            )
            if down_pressed:
                self.crouching = True

        # Coyote time + jump buffer
        if not self.on_ground:
            if prev_on_ground:
                self.coyote_frames = self.COYOTE_FRAMES
            else:
                self.coyote_frames = max(0, self.coyote_frames - 1)
            self.jump_buffer_frames = max(0, self.jump_buffer_frames - 1)
        else:
            self._did_air_jump_this_flight = False
            self.coyote_frames = 0
            if self.jump_buffer_frames > 0 and self.jump_count < self.jump_max:
                mult = self.double_jump_mult if self.jump_count > 0 else 1.0
                self.speed_y = self.jump_force * mult
                self.jump_count += 1
                self.jump_buffer_frames = 0
                self.drop_through = False

        self._update_walk_animation()

        # Blast zones (sortie d'écran = perte de vie)
        if (
            self.rect.right < -self.BLAST_MARGIN
            or self.rect.left > self.screen_width + self.BLAST_MARGIN
            or self.rect.bottom < -self.BLAST_MARGIN
            or self.rect.top > self.screen_height + self.BLAST_MARGIN
        ):
            self.lives -= 1
            if self.lives > 0:
                self.respawn()
            else:
                self.rect.center = (-999, -999)