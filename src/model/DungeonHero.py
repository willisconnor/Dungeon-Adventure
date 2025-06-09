import os

from src.model.DungeonCharacter import DungeonCharacter
from src.model.DungeonEntity import AnimationState, Direction
import pygame
import sqlite3
'''Connor Willis
'''
class Hero(DungeonCharacter, pygame.sprite.Sprite):
    """Base Hero class that all hero types will inherit from"""

    def __init__(self, x, y, hero_type = "default"):
        #initialize pygame.sprite.Sprite first
        pygame.sprite.Sprite.__init__(self)

        # Set basic hero info
        self.hero_type = hero_type

        # Set animation state early — required for frame loading
        self.animation_state = AnimationState.IDLE
        self.last_animation_state = AnimationState.IDLE

        # Load stats from database
        stats = self._load_hero_stats()

        width = 64
        height = 64
        name = hero_type.capitalize()

        # DEBUG: Print what we're about to pass
        print("About to call DungeonCharacter.__init__ with:")
        print(f"x={x}, y={y}, width={width}, height={height}, name={name}")
        print(f"max_health={stats['max_health']}, health={stats['max_health']}")
        print(f"speed={stats['speed']}, damage={stats['damage']}")

        # Initialize parent class (sets self.x, self.y, etc.)
        DungeonCharacter.__init__(self,
            x, y,
            width, height,
            name,
            stats["max_health"],
            stats["max_health"],  # current health
            stats["speed"],
            stats["damage"],
        )
        self.hero_type = hero_type

        # Load animations after base init (self.x, self.y now exist)
        self.frame_counts = self._load_frame_counts()
        self.frames = self._load_all_frames()
        self.frame_index = 0
        self.animation_counter = 0
        self.animation_speed = 0.15
        self.current_frame = self.frames[self.animation_state][self.frame_index]
        self.image = self.current_frame
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        # Hero-specific stats
        self.damage = stats["damage"]
        self.attack_range = stats["attack_range"]
        self.special_cooldown = stats["special_cooldown"]

        # Hero state flags
        self.is_moving = False
        self.is_defending = False
        self.can_input = True

        # Special ability state
        self.special_cooldown_remaining = 0
        self.using_special = False

        # Attack state
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_combo = 0
        self.attack_complete = True
        self.attack_window = 0
        self.hit_targets = set()

        # Movement/physics state
        self.is_jumping = False
        self.is_falling = False
        self.jump_velocity = 15
        self.y_velocity = 0
        self.gravity = 0.8
        self.ground_y = self.y
        self.on_ground = True

    def _load_all_frames(self):
        """Load all frames for each animation state from sprite sheets"""
        conn = sqlite3.connect('game_data.db')
        c = conn.cursor()

        # Load all sprite paths
        c.execute('''
            SELECT animation_state, sprite_path
            FROM hero_sprites
            WHERE hero_type = ?
        ''', (self.hero_type,))
        sprite_path_rows = c.fetchall()
        conn.close()

        # Convert to dict: {AnimationState: path}
        path_map = {
            AnimationState(int(row[0])): row[1] for row in sprite_path_rows
        }

        frames = {}
        for state in self.frame_counts:
            path = path_map.get(state)
            if not path or not os.path.exists(path):
                # fallback placeholder
                surf = pygame.Surface((64, 64))
                surf.fill((255, 0, 255))
                frames[state] = [surf]
                continue

            # Load and slice sprite sheet
            sheet = pygame.image.load(path).convert_alpha()
            frame_width = sheet.get_width() // self.frame_counts[state]
            frame_height = sheet.get_height()

            state_frames = [
                sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                for i in range(self.frame_counts[state])
            ]
            frames[state] = state_frames

        return frames

    def _load_hero_stats(self):
        """Load hero stats from SQLite Database"""
        conn = sqlite3.connect('game_data.db')
        c = conn.cursor()

        c.execute('''
            SELECT max_health, speed, damage, attack_range, special_cooldown
            FROM hero_stats
            WHERE hero_type = ?''', (self.hero_type,))

        #need to make the db for this to work lol
        #also, can change this based on what stats we want
        result = c.fetchone()
        conn.close()

        if result:
            return{
                "max_health": result[0],
                "speed": result[1],
                "damage": result[2],
                "attack_range": result[3],
                "special_cooldown": result[4]
            }
        else: #default stats if not found in DB (should not be used
            return{
                "max_health": 100,
                "speed": 7,
                "damage": 5,
                "attack_range": 80,
                "special_cooldown": 10
            }

    def _load_frame_counts(self):
        """load animiaton frame coutns from SQLite Database"""
        conn = sqlite3.connect('game_data.db')
        c = conn.cursor()

        c.execute('''
        SELECT animation_state, frame_count
        FROM hero_animations
        WHERE hero_type = ?''', (self.hero_type,))

        results = c.fetchall()
        conn.close()

        #convert results to dictionary
        frame_counts = {}
        for animation_state, frame_count in results:
            frame_counts[AnimationState(animation_state)] = frame_count

        #default values if databse doesnt have all states
        #arbitrarily decided, might cause skipping in anim states
        default_counts = {
            AnimationState.IDLE: 4,
            AnimationState.WALKING : 7,
            AnimationState.ATTACKING_1: 5,
            AnimationState.ATTACKING_2: 4,
            AnimationState.ATTACKING_3: 4,
            AnimationState.DEFENDING: 5,
            AnimationState.HURT: 3,
            AnimationState.DYING: 5,
            AnimationState.DEAD: 1,
            AnimationState.SPECIAL: 6  # Added for special abilities

        }
        #use defaults for any missing states
        for state, count in default_counts.items():
            if state not in frame_counts:
                frame_counts[state] = count

        return frame_counts

    def get_frames_count(self, state):
        """get the number of frames for a given state"""
        return self.frame_counts.get(state, 4) #default to 4 is not found

    def handle_input(self, keys, space_pressed):
        """handle player input""" #should this go inthe view? no,
        #the view is for checking if something has been pressed
        # this is the logic behind each keystroke
        if not self.is_alive:
            return

        #process defending (E key)
        self.is_defending = keys[pygame.K_e] and not self.is_attacking and not self.using_special

        #Special Ability (Q Key)
        if keys[pygame.K_q] and self.special_cooldown_remaining <= 0 and not self.is_attacking and not self.is_defending:
            self.activate_special_ability()

        #only allow movement if not defending, attacking, or using special
        if not self.is_defending and not self.is_attacking and not self.using_special:
            #move left with A
            if keys[pygame.K_a]:
                self.x -= self.speed
                self.direction = Direction.LEFT
                self.is_moving = True
            #move right with D
            elif keys[pygame.K_d]:
                self.x += self.speed
                self.direction = Direction.RIGHT
                self.is_moving = True
            else:
                self.is_moving = False
        else:
            #no movement while defending, attacking, or using special
            self.is_moving = False

        #handle attack input (spacebar for now, could change to mouse)
        if space_pressed and self.can_input and not self.using_special and(self.attack_complete or self.attack_window >0):
            self.can_input = False #prevent multiple attacks from one press

            #start or continue attack combo
            if self.attack_complete or self.attack_window >0:
                if self.attack_window >0 and self.attack_combo >0:
                    #continue combo
                    self.attack_combo +=1
                    if self.attack_combo >3:
                        #loop back to the first attack animation
                        self.attack_combo = 1 #this is hardcoded, change for animaition shits

                else:
                    #start new combo
                    self.attack_combo = 1

                self.is_attacking = True
                self.attack_complete = False
                self.attack_window = 0 #reset combo window on successful input
                #clear hit targets for new attack
                self.hit_targets.clear()
        #reset input flag when spacebar is released
        if not space_pressed:
            self.can_input = True

    #jump stuff? or possibly the entering/exiting rooms that Zach talked about

    def update(self, dt):
        """update hero state"""
        super().update(dt)

        #update special cooldown
        if self.special_cooldown_remaining >0:
            self.special_cooldown_remaining -= dt
            if self.special_cooldown_remaining < 0:
                self.special_cooldown_remaining = 0

        #update attack timer
        if self.attack_timer > 0:
            self.special_cooldown_remaining -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False

        #ground check
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self. on_ground = True
            self.is_falling = False
            self.y_velocity = 0

        #update animaiton state based on current actions
        if self.is_alive and not self.animation_state in [AnimationState.HURT, AnimationState.DYING, AnimationState.DEAD]:
            self._update_animation_state()

        # Animation frame update
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames[self.animation_state])

        self.current_frame = self.frames[self.animation_state][self.frame_index]
        self.image = self.current_frame
        self.rect.topleft = (self.x, self.y)

    def _update_animation_state(self):
        """update the current animation state based on hero actions"""
        #store previous state before changing
        self.last_animation_state = self.animation_state

        if not self.is_alive:
            return

        #determine new animation state with priority for special abilities, attacks, and defending
        if self.using_special:
            new_state = AnimationState.SPECIAL_SKILL
        elif self.is_attacking:
            if self.attack_combo == 1:
                new_state = AnimationState.ATTACKING_1
            elif self.attack_combo == 2:
                new_state = AnimationState.ATTACKING_2
            elif self.attack_combo == 3:
                new_state = AnimationState.ATTACKING_3
            else:
                new_state = AnimationState.IDLE
        elif self.is_defending:
            new_state = AnimationState.DEFENDING
        elif self.is_falling:
            new_state = AnimationState.FALLING
        elif self.is_moving:
            new_state = AnimationState.WALKING
        else:
            new_state = AnimationState.IDLE

        #only change state if its different from current
        if new_state != self.animation_state:
            self.animation_state = new_state

            #only reset frame index if not chaining attacks
            if not (self.is_attacking and self.last_animation_state in [AnimationState.ATTACKING_1, AnimationState.ATTACKING_2, AnimationState.ATTACKING_3] and
                    self.animation_state in [AnimationState.ATTACKING_1, AnimationState.ATTACKING_2, AnimationState.ATTACKING_3]):
                self.frame_index = 0
                self.animation_counter = 0

    def get_attack_hitbox(self):
        #possibly update this based off of hitbox parameters passed in abstract class
        #get hitbox for current attack
        if not self.is_attacking and not self.using_special:
            return None

        #create attack hitbox based on character direction
        width = self.attack_range
        height = 80

        if self.direction == Direction.RIGHT:
            x = self.x + 25
            y = self.y -height //2
        else:
            x = self.x - 25 -width
            y = self.y - height //2

        return pygame.Rect(x, y, width, height)

    def attack(self, targets):
        """Attempt to attack a list of target entities"""
        if(not self.is_attacking and not self.using_special) or not self.is_alive:
            return []

        hit_targets = []
        attack_hitbox = self.get_attack_hitbox()

        if attack_hitbox:
            for target in targets:
                #skip targets already hit by this attack or by those that arent alive
                if target in self.hit_targets or not target.is_alive:
                    continue

                #check collision with target's hitbox
                if attack_hitbox.colliderect(target.hitbox):
                    #calculate damage, might be modified by ability or potion
                    damage = self.calculate_damage(target)
                    #hit successful
                    hit = target.take_damage(damage)
                    if hit:
                        self.hit_targets.add(target)
                        hit_targets.append(target)

        return hit_targets

    def calculate_damage(self, target):
        """Calculate damage to  be dealt to target, can be override by subclasses"""
        return self.damage

    def activate_special_ability(self):
        """Activate heros special ability, to be implemented by child classes"""
        self.using_special = True
        self.special_cooldown_remaining = self.special_cooldown

    def take_damage(self, damage):
        """Take damage, return True if hit, False if not"""
        if damage <= 0:
            return False
        if not self.is_alive or self.is_invulnerable or self.is_defending:
            return False

        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.animation_state = AnimationState.DEAD
            return True

        self.is_invulnerable = True
        self.invulnerable_timer = 1.0
        self.animation_state = AnimationState.HURT
        return True


    def get_sprite_path(self, animation_state):
        """Get the sprite path for a specific animaiton state"""
        conn = sqlite3.connect('game_data.db')
        c = conn.cursor()

        c.execute('''
            SELECT sprite_path
            FROM hero_sprites
            WHERE hero_type = ? AND animation_state = ?''', (self.hero_type, animation_state))

        result = c.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return f"assets/sprites/{self.hero_type}/{animation_state.name.lower()}.png"