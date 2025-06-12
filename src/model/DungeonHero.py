import os

from src.model.DungeonCharacter import DungeonCharacter
from src.model.DungeonEntity import AnimationState, Direction
from src.utils.SpriteSheet import SpriteSheet
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

        # Hero-specific properties
        self.hero_type = hero_type
        self.name = hero_type.capitalize()

        # Load hero stats from database
        stats = self._load_hero_stats()

        # Initialize DungeonCharacter with loaded stats
        super().__init__(
            x=x, y=y,
            width=128, height=128,
            name=self.name,
            max_health=stats["max_health"],
            health=stats["max_health"],
            speed=stats["speed"],
            damage=stats["damage"]
        )

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

        # Frame rates for attackTest-style timing
        self.frame_rates = {
            AnimationState.IDLE: 6,
            AnimationState.WALKING: 6,
            AnimationState.ATTACKING_1: 5,
            AnimationState.ATTACKING_2: 5,
            AnimationState.ATTACKING_3: 5,
            AnimationState.DEFENDING: 6,
            AnimationState.HURT: 4,
            AnimationState.DYING: 8,
            AnimationState.DEAD: 1,
            AnimationState.SPECIAL_SKILL: 6,
            AnimationState.FALLING: 6
        }

        # Special ability state
        self.special_cooldown_remaining = 0
        self.using_special = False
        self.special_duration = 1.0  # How long the special ability lasts (1 second)
        self.special_duration_remaining = 0  # Timer for special ability duration

        # Attack state - simplified like special ability
        self.is_attacking = False
        self.attack_cooldown = 0.3  # Time between attacks (0.3 seconds)
        self.attack_cooldown_remaining = 0
        self.attack_combo = 0
        self.hit_targets = set()

        # Load frame counts for this hero type
        self.frame_counts = self._load_frame_counts()

        # Load all animation frames
        self.frames = self._load_all_frames()
        self.frame_index = 0
        self.animation_counter = 0
        self.animation_speed = 0.15
        self.current_sprite = self.frames[self.animation_state][self.frame_index]
        self.image = self.current_sprite
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        # Ground position for jumping
        self.ground_y = y
        self.on_ground = True
        self.is_falling = False
        self.y_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -12

    def _load_all_frames(self):
        """Load all frames for each animation state from sprite sheets using SpriteSheet class"""
        conn = sqlite3.connect('game_data.db')
        c = conn.cursor()

        # Load all sprite paths and frame data
        c.execute('''
            SELECT animation_state, sprite_path, frame_count, frame_rate, frame_width, frame_height
            FROM hero_animations
            WHERE hero_type = ?
        ''', (self.hero_type,))
        animation_data = c.fetchall()
        conn.close()

        # Convert to dict: {AnimationState: data}
        animation_map = {}
        for row in animation_data:
            state = AnimationState[row[0]]
            animation_map[state] = {
                'path': row[1],
                'frame_count': row[2],
                'frame_rate': row[3],
                'frame_width': row[4],
                'frame_height': row[5]
            }

        frames = {}
        frame_counts = self.get_frame_counts()

        # Load frames for each animation state
        for state in AnimationState:
            data = animation_map.get(state)
            count = frame_counts.get(state, 1)
            
            if not data or not os.path.exists(data['path']):
                # Fallback: use idle frame or colored rectangle
                if AnimationState.IDLE in frames:
                    frames[state] = frames[AnimationState.IDLE]
                else:
                    # Create fallback surface with correct size for hero type
                    if self.hero_type == "archer":
                        surf = pygame.Surface((64, 128), pygame.SRCALPHA)  # Updated height to 128
                    else:  # knight and cleric
                        surf = pygame.Surface((128, 128), pygame.SRCALPHA)
                    
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

            # Load sprite sheet and extract frames using SpriteSheet class
            try:
                sheet_image = pygame.image.load(data['path']).convert_alpha()
                spritesheet = SpriteSheet(sheet_image)
                
                frame_count = data['frame_count']
                frame_width = data['frame_width']
                frame_height = data['frame_height']
                
                # Extract frames using the SpriteSheet class
                state_frames = []
                for i in range(frame_count):
                    # Scale based on hero type
                    if self.hero_type == "archer":
                        # Archer sprites are 64x128, no scaling needed
                        frame = spritesheet.get_frame(i, frame_width, frame_height, scale=1.0)
                    else:
                        # Knight and cleric sprites are 128x128, scale to 128x128
                        frame = spritesheet.get_frame(i, frame_width, frame_height, scale=1.0)
                    state_frames.append(frame)
                
                frames[state] = state_frames
                print(f"Loaded {len(state_frames)} frames for {state.name} from {data['path']}")
                
            except (pygame.error, FileNotFoundError) as e:
                print(f"Error loading animation {state.name}: {e}")
                # Fallback if sprite loading fails
                if AnimationState.IDLE in frames:
                    frames[state] = frames[AnimationState.IDLE]
                else:
                    # Create fallback surface with correct size for hero type
                    if self.hero_type == "archer":
                        surf = pygame.Surface((64, 128), pygame.SRCALPHA)  # Updated height to 128
                    else:  # knight and cleric
                        surf = pygame.Surface((128, 128), pygame.SRCALPHA)
                    
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
        """Load animation frame counts and rates from SQLite Database"""
        conn = sqlite3.connect('game_data.db')
        c = conn.cursor()

        c.execute('''
        SELECT animation_state, frame_count, frame_rate
        FROM hero_animations
        WHERE hero_type = ?''', (self.hero_type,))

        results = c.fetchall()
        conn.close()

        # Convert results to dictionaries
        frame_counts = {}
        frame_rates = {}
        for animation_state, frame_count, frame_rate in results:
            state = AnimationState[animation_state]
            frame_counts[state] = frame_count
            frame_rates[state] = frame_rate

        # Store frame rates for use in animation updates
        self.frame_rates = frame_rates

        # Default values if database doesn't have all states
        default_counts = {
            AnimationState.IDLE: 4,
            AnimationState.WALKING: 7,
            AnimationState.ATTACKING_1: 5,
            AnimationState.ATTACKING_2: 4,
            AnimationState.ATTACKING_3: 4,
            AnimationState.DEFENDING: 5,
            AnimationState.HURT: 3,
            AnimationState.DYING: 5,
            AnimationState.DEAD: 1,
            AnimationState.SPECIAL_SKILL: 6,
            AnimationState.RUNNING: 6,
            AnimationState.JUMPING: 6,
            AnimationState.FALLING: 4,
            AnimationState.RUNNING_ATTACK: 6
        }

        # Use defaults for any missing states
        for state, count in default_counts.items():
            if state not in frame_counts:
                frame_counts[state] = count
            if state not in frame_rates:
                frame_rates[state] = 0.15  # Default frame rate

        return frame_counts

    def get_frames_count(self, state):
        """get the number of frames for a given state"""
        return self.frame_counts.get(state, 4) #default to 4 is not found

    def handle_input(self, keys, space_pressed):
        """Handle player input - simplified like special ability"""
        if not self.is_alive:
            return

        # Process defending (E key)
        self.is_defending = keys[pygame.K_e] and not self.is_attacking

        # Only allow movement if not defending or attacking
        if not self.is_defending and not self.is_attacking:
            if keys[pygame.K_a]:
                self.x -= self.speed
                self.direction = Direction.LEFT
                self.is_moving = True
            elif keys[pygame.K_d]:
                self.x += self.speed
                self.direction = Direction.RIGHT
                self.is_moving = True
            else:
                self.is_moving = False
        else:
            self.is_moving = False

        # Attack input will be handled in Game.py like special ability

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

        # Update attack cooldown
        if self.attack_cooldown_remaining > 0:
            self.attack_cooldown_remaining -= dt
            if self.attack_cooldown_remaining < 0:
                self.attack_cooldown_remaining = 0

        # Update animation frames for all states
        self.animation_counter += dt
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            frame_count = self.get_frames_count(self.animation_state)
            self.frame_index = (self.frame_index + 1) % frame_count
            
            # Check if attack animation is complete (reached the last frame)
            if self.is_attacking and self.frame_index == 0 and frame_count > 1:
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

        # Update current sprite for rendering
        if self.animation_state in self.frames and len(self.frames[self.animation_state]) > 0:
            # Ensure frame_index is within bounds
            max_frame_index = len(self.frames[self.animation_state]) - 1
            if self.frame_index > max_frame_index:
                self.frame_index = max_frame_index
            elif self.frame_index < 0:
                self.frame_index = 0
                
            self.current_frame = self.frames[self.animation_state][self.frame_index]
            self.current_sprite = self.current_frame
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
            if not (self.is_attacking and 
                    self.last_animation_state in [AnimationState.ATTACKING_1, AnimationState.ATTACKING_2, AnimationState.ATTACKING_3] and
                    self.animation_state in [AnimationState.ATTACKING_1, AnimationState.ATTACKING_2, AnimationState.ATTACKING_3]):
                self.frame_index = 0
                self.animation_counter = 0

    def get_attack_hitbox(self):
        """Get the hitbox for the current attack"""
        if not self.is_attacking:
            return None

        # Create attack hitbox based on character direction
        width = self.attack_range
        height = 80

        if self.direction == Direction.RIGHT:
            x = self.x + self.width  # Start at the right edge of the character
            y = self.y + self.height - height  # Bottom of hitbox touches sprite feet
        else:  # Direction.LEFT
            x = self.x - width  # Start at the left edge of the character
            y = self.y + self.height - height  # Bottom of hitbox touches sprite feet

        return pygame.Rect(x, y, width, height)

    def attack(self, targets):
        """Attempt to attack a list of target entities"""
        if not self.is_attacking or not self.is_alive:
            return []

        hit_targets = []
        attack_hitbox = self.get_attack_hitbox()

        if attack_hitbox:
            for target in targets:
                # Skip targets already hit by this attack and those that aren't alive
                if target in self.hit_targets or not target.is_alive:
                    continue

                # Check collision with target's hitbox
                if attack_hitbox.colliderect(target.hitbox):
                    # Hit successful
                    hit = target.take_damage(self.damage)
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

    def activate_attack(self):
        """Activate basic attack - simple like special ability"""
        if not self.is_alive or self.is_attacking or self.attack_cooldown_remaining > 0:
            return False
        
        self.is_attacking = True
        self.attack_cooldown_remaining = self.attack_cooldown
        
        # Cycle through attack combos (1-2-3)
        self.attack_combo = (self.attack_combo % 3) + 1
        
        # Clear hit targets for new attack
        self.hit_targets.clear()
        
        return True

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
        return getattr(self, 'current_frame', None)

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