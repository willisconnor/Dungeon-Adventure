import os

from src.model.DungeonCharacter import DungeonCharacter
from src.model.DungeonEntity import AnimationState, Direction
import pygame
import sqlite3
import random
'''Connor Willis corndog
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
        self.current_sprite = self.frames[self.animation_state][self.frame_index]
        self.image = self.current_sprite
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        # Hero-specific stats
        self.damage = stats["damage"]
        self.attack_range = stats["attack_range"]
        self.attack_speed = stats["attack_speed"]
        self.special_cooldown = stats["special_cooldown"]
        self.defense = stats["defense"]
        self.critical_chance = stats["critical_chance"]
        self.critical_damage = stats["critical_damage"]

        # Hero state flags
        self.is_moving = False
        self.is_defending = False
        self.can_input = True

        # Special ability state
        self.special_cooldown_remaining = 0
        self.using_special = False
        self.special_duration = 1.0  # How long the special ability lasts (1 second)
        self.special_duration_remaining = 0  # Timer for special ability duration

        # Attack state
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_combo = 0
        self.attack_complete = True
        self.attack_window = 0
        self.hit_targets = set()
        self.attack_duration = 1.0 / stats["attack_speed"]  # Duration based on attack speed (hits per second)

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
            FROM hero_animations
            WHERE hero_type = ?
        ''', (self.hero_type,))
        sprite_path_rows = c.fetchall()
        conn.close()

        # Convert to dict: {AnimationState: path}
        path_map = {
            AnimationState[row[0]]: row[1] for row in sprite_path_rows
        }

        frames = {}
        frame_counts = self.get_frame_counts()

        # Ensure all AnimationStates have at least one frame
        for state in AnimationState:
            path = path_map.get(state)
            count = frame_counts.get(state, 1)
            if not path or not os.path.exists(path):
                # Fallback: use idle frame or colored rectangle
                if AnimationState.IDLE in frames:
                    frames[state] = frames[AnimationState.IDLE]
                else:
                    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
                    if self.hero_type == "knight":
                        surf.fill((100, 100, 200))
                    elif self.hero_type == "archer":
                        surf.fill((100, 200, 100))
                    elif self.hero_type == "cleric":
                        surf.fill((200, 100, 100))
                    else:
                        surf.fill((150, 150, 150))
                    frames[state] = [surf for _ in range(count)]
                continue
            # Try to load and slice sprite sheet
            try:
                sheet = pygame.image.load(path).convert_alpha()
                frame_count = frame_counts[state]
                frame_width = sheet.get_width() // frame_count
                frame_height = sheet.get_height()

                state_frames = [
                    sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                    for i in range(frame_count)
                ]

                frames[state] = state_frames
            except (pygame.error, FileNotFoundError):
                # Fallback if sprite loading fails
                if AnimationState.IDLE in frames:
                    frames[state] = frames[AnimationState.IDLE]
                else:
                    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
                    if self.hero_type == "knight":
                        surf.fill((100, 100, 200))
                    elif self.hero_type == "archer":
                        surf.fill((100, 200, 100))
                    elif self.hero_type == "cleric":
                        surf.fill((200, 100, 100))
                    else:
                        surf.fill((150, 150, 150))
                    frames[state] = [surf for _ in range(count)]
        return frames

    def _load_hero_stats(self):
        """Load hero stats from SQLite Database"""
        conn = sqlite3.connect('game_data.db')
        c = conn.cursor()

        c.execute('''
            SELECT max_health, speed, damage, attack_range, attack_speed, 
                   special_cooldown, defense, critical_chance, critical_damage
            FROM hero_stats
            WHERE hero_type = ?''', (self.hero_type,))

        result = c.fetchone()
        conn.close()

        if result:
            return{
                "max_health": result[0],
                "speed": result[1],
                "damage": result[2],
                "attack_range": result[3],
                "attack_speed": result[4],
                "special_cooldown": result[5],
                "defense": result[6],
                "critical_chance": result[7],
                "critical_damage": result[8]
            }
        else: #default stats if not found in DB (should not be used)
            return{
                "max_health": 100,
                "speed": 7,
                "damage": 5,
                "attack_range": 80,
                "attack_speed": 1.0,
                "special_cooldown": 10,
                "defense": 5,
                "critical_chance": 0.05,
                "critical_damage": 1.5
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
            frame_counts[AnimationState[animation_state]] = frame_count

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
                self.attack_timer = self.attack_duration  # Start the attack duration timer
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

        #update special ability duration
        if self.special_duration_remaining > 0:
            self.special_duration_remaining -= dt
            if self.special_duration_remaining <= 0:
                self.using_special = False
                self.special_duration_remaining = 0

        #update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False
                self.attack_timer = 0
                self.attack_complete = True

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
        """Calculate damage to be dealt to target, including critical hits and defense"""
        # Base damage
        base_damage = self.damage
        
        # Check for critical hit
        if random.random() < self.critical_chance:
            # Critical hit! Apply critical damage multiplier
            base_damage *= self.critical_damage
            print(f"{self.name} landed a critical hit! Damage: {base_damage}")
        
        # Apply target's defense (reduce damage)
        if hasattr(target, 'defense'):
            final_damage = max(1, base_damage - target.defense)  # Minimum 1 damage
        else:
            final_damage = base_damage
            
        return int(final_damage)

    def activate_special_ability(self):
        """Activate heros special ability, to be implemented by child classes"""
        self.using_special = True
        self.special_cooldown_remaining = self.special_cooldown
        self.special_duration_remaining = self.special_duration  # Start the duration timer

    def take_damage(self, damage):
        """Take damage, return True if hit, False if not"""
        if damage <= 0:
            return False
        if not self.is_alive or self.is_invulnerable or self.is_defending:
            return False

        # Apply defense to reduce incoming damage
        actual_damage = max(1, damage - self.defense)  # Minimum 1 damage
        self.health -= actual_damage

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
            FROM hero_animations
            WHERE hero_type = ? AND animation_state = ?''', (self.hero_type, animation_state))

        result = c.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return f"assets/sprites/{self.hero_type}/{animation_state.name.lower()}.png"

    """
    setters/getters
    """

    def get_hero_type(self):
        """Get hero type"""
        return self.hero_type

    def get_attack_range(self):
        """Get attack range"""
        return self.attack_range

    def get_current_sprite(self):
        """Get current sprite surface"""
        return getattr(self, 'current_sprite', None)

    def set_current_sprite(self, sprite):
        """Set current sprite surface"""
        self.current_sprite = sprite

    def get_frames(self):
        """Get frames dictionary"""
        return self.frames

    def get_frame_counts(self):
        """Get frame counts dictionary"""
        return self.frame_counts

    # Getter methods for state checking
    def get_is_attacking(self):
        """Check if character is currently attacking"""
        return self.is_attacking

    def get_is_using_special(self):
        """Check if character is using special ability"""
        return self.using_special

    def get_is_alive(self):
        """Check if character is alive"""
        return self.is_alive