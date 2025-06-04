import pygame
import sqlite3
from enum import Enum, auto
from src.model.DungeonCharacter import DungeonCharacter
from src.model.DungeonEntity import AnimationState, Direction


class Hero(DungeonCharacter, pygame.sprite.Sprite):
    """Base Hero class that all hero types will inherit from"""

    def __init__(self, x, y, hero_type="default"):
        # Store hero type first so _load_hero_stats can use it
        self.__hero_type = hero_type

        # Load hero stats from database
        stats = self._load_hero_stats()

        # Initialize parent classes
        super().__init__(
            x, y,
            max_health=stats["max_health"],
            speed=stats["speed"],
            damage=stats["damage"]
        )
        pygame.sprite.Sprite.__init__(self)

        # Load animation frame counts
        self.__frame_counts = self._load_frame_counts()

        # Hero specific properties - combat states
        self.__is_moving = False
        self.__is_defending = False
        self.__can_input = True  # to prevent multiple attacks from a single keypress

        # Special ability related properties
        self.__special_cooldown = stats["special_cooldown"]
        self.__special_cooldown_remaining = 0
        self.__using_special = False

        # Attack properties
        self.__attack_range = stats["attack_range"]

        # Attack combo properties
        self.__attack_combo = 0
        self.__attack_window = 0
        self.__attack_complete = True
        self.__hit_targets = set()

    # Methods needed for __str__ that are inherited from DungeonEntity and DungeonCharacter
    def get_health(self):
        """Get current health - delegated to parent class"""
        return super().get_health()

    def get_max_health(self):
        """Get maximum health - delegated to parent class"""
        return super().get_max_health()

    def get_damage(self):
        """Get damage value - delegated to parent class"""
        return super().get_damage()

    def get_x(self):
        """Get x position - delegated to parent class"""
        return super().get_x()

    def get_y(self):
        """Get y position - delegated to parent class"""
        return super().get_y()

    def get_direction(self):
        """Get facing direction - delegated to parent class"""
        return super().get_direction()

    def get_animation_state(self):
        """Get current animation state - delegated to parent class"""
        return super().get_animation_state()

    def is_attacking(self):
        """Check if entity is attacking - delegated to parent class"""
        return super().is_attacking()

    def set_attacking(self, attacking):
        """Set attacking state - delegated to parent class"""
        super().set_attacking(attacking)

    def get_hitbox(self):
        """Get entity hitbox - delegated to parent class"""
        return super().get_hitbox()

    def set_frame_index(self, index):
        """Set animation frame index - delegated to parent class"""
        super().set_frame_index(index)

    def set_animation_state(self, state):
        """Set animation state - delegated to parent class"""
        super().set_animation_state(state)

    def set_direction(self, direction):
        """Set facing direction - delegated to parent class"""
        super().set_direction(direction)

    def reset_animation_counter(self):
        """Reset animation counter - delegated to parent class"""
        super().reset_animation_counter()

    def _load_hero_stats(self):
        """Load hero stats from SQLite Database"""
        try:
            conn = sqlite3.connect('game_data.db')
            c = conn.cursor()

            c.execute('''
                      SELECT max_health, speed, damage, attack_range, special_cooldown
                      FROM hero_stats
                      WHERE hero_type = ?''', (self.__hero_type,))

            result = c.fetchone()
            conn.close()

            if result:
                return {
                    "max_health": result[0],
                    "speed": result[1],
                    "damage": result[2],
                    "attack_range": result[3],
                    "special_cooldown": result[4]
                }
        except Exception as e:
            print(f"Database error: {e}")

        # Default stats if not found in DB or error occurred
        return {
            "max_health": 100,
            "speed": 7,
            "damage": 5,
            "attack_range": 80,
            "special_cooldown": 10
        }

    def _load_frame_counts(self):
        """Load animation frame counts from SQLite Database"""
        frame_counts = {}

        try:
            conn = sqlite3.connect('game_data.db')
            c = conn.cursor()

            c.execute('''
                      SELECT animation_state, frame_count
                      FROM hero_animations
                      WHERE hero_type = ?''', (self.__hero_type,))

            results = c.fetchall()
            conn.close()

            # Convert results to dictionary
            for animation_state, frame_count in results:
                frame_counts[AnimationState(animation_state)] = frame_count
        except Exception as e:
            print(f"Database error loading animations: {e}")

        # Default values if database doesn't have all states
        default_counts = {
            AnimationState.IDLE: 4,
            AnimationState.WALKING: 7,
            AnimationState.ATTACKING_1: 5,
            AnimationState.ATTACKING_2: 4,
            AnimationState.ATTACKING_3: 4,
            AnimationState.HURT: 3,
            AnimationState.DYING: 5,
            AnimationState.DEAD: 1,
            AnimationState.SPECIAL_SKILL: 6  # For special abilities
        }

        # Use defaults for any missing states
        for state, count in default_counts.items():
            if state not in frame_counts:
                frame_counts[state] = count

        return frame_counts

    def get_frames_count(self, state):
        """Get the number of frames for a given state"""
        return self.__frame_counts.get(state, 4)  # default to 4 if not found

    def handle_input(self, keys, space_pressed):
        """Handle player input"""
        if not self.is_alive():
            return

        # Process defending (E key)
        self.__is_defending = keys[pygame.K_e] and not self.is_attacking() and not self.__using_special

        # Special Ability (Q Key)
        if keys[
            pygame.K_q] and self.__special_cooldown_remaining <= 0 and not self.is_attacking() and not self.__is_defending:
            self.activate_special_ability()

        # Only allow movement if not defending, attacking, or using special
        if not self.__is_defending and not self.is_attacking() and not self.__using_special:
            # Move left with A
            if keys[pygame.K_a]:
                self.set_x(self.get_x() - self.get_speed())
                self.set_direction(Direction.LEFT)
                self.__is_moving = True
            # Move right with D
            elif keys[pygame.K_d]:
                self.set_x(self.get_x() + self.get_speed())
                self.set_direction(Direction.RIGHT)
                self.__is_moving = True
            else:
                self.__is_moving = False
        else:
            # No movement while defending, attacking, or using special
            self.__is_moving = False

        # Handle attack input (spacebar for now, could change to mouse)
        if space_pressed and self.__can_input and not self.__using_special and (
                self.__attack_complete or self.__attack_window > 0):
            self.__can_input = False  # prevent multiple attacks from one press

            # Start or continue attack combo
            if self.__attack_complete or self.__attack_window > 0:
                if self.__attack_window > 0 and self.__attack_combo > 0:
                    # Continue combo
                    self.__attack_combo += 1
                    if self.__attack_combo > 3:
                        # Loop back to the first attack animation
                        self.__attack_combo = 1
                else:
                    # Start new combo
                    self.__attack_combo = 1

                self.set_attacking(True)
                self.__attack_complete = False
                self.__attack_window = 0  # Reset combo window on successful input
                # Clear hit targets for new attack
                self.__hit_targets.clear()

        # Reset input flag when spacebar is released
        if not space_pressed:
            self.__can_input = True

    def update(self, dt):
        """Update hero state"""
        super().update(dt)

        # Update special cooldown
        if self.__special_cooldown_remaining > 0:
            self.__special_cooldown_remaining -= dt
            if self.__special_cooldown_remaining < 0:
                self.__special_cooldown_remaining = 0

        # Update animation state based on current actions
        if self.is_alive() and self.get_animation_state() not in [AnimationState.HURT, AnimationState.DYING,
                                                                  AnimationState.DEAD]:
            self._update_animation_state()

    def _update_animation_state(self):
        """Update the current animation state based on hero actions"""
        # Store previous state before changing
        last_state = self.get_animation_state()

        # Determine new animation state with priority for special abilities, attacks, and defending
        if self.__using_special:
            new_state = AnimationState.SPECIAL_SKILL
        elif self.is_attacking():
            if self.__attack_combo == 1:
                new_state = AnimationState.ATTACKING_1
            elif self.__attack_combo == 2:
                new_state = AnimationState.ATTACKING_2
            elif self.__attack_combo == 3:
                new_state = AnimationState.ATTACKING_3
            else:
                new_state = AnimationState.IDLE
        elif self.__is_defending:
            new_state = AnimationState.HURT  # Using HURT as DEFENDING for now
        elif self.__is_moving:
            new_state = AnimationState.WALKING
        else:
            new_state = AnimationState.IDLE

        # Only change state if it's different from current
        if new_state != last_state:
            self.set_animation_state(new_state)

            # Only reset frame index if not chaining attacks
            if not (self.is_attacking() and
                    last_state in [AnimationState.ATTACKING_1, AnimationState.ATTACKING_2,
                                   AnimationState.ATTACKING_3] and
                    new_state in [AnimationState.ATTACKING_1, AnimationState.ATTACKING_2, AnimationState.ATTACKING_3]):
                self.set_frame_index(0)
                self.reset_animation_counter()

    def get_attack_hitbox(self):
        """Get hitbox for current attack"""
        if not self.is_attacking() and not self.__using_special:
            return None

        # Create attack hitbox based on character direction
        width = self.__attack_range
        height = 80

        if self.get_direction() == Direction.RIGHT:
            x = self.get_x() + 25
            y = self.get_y() - height // 2
        else:
            x = self.get_x() - 25 - width
            y = self.get_y() - height // 2

        return pygame.Rect(x, y, width, height)

    def attack(self, targets):
        """Attempt to attack a list of target entities"""
        if (not self.is_attacking() and not self.__using_special) or not self.is_alive():
            return []

        hit_targets = []
        attack_hitbox = self.get_attack_hitbox()

        if attack_hitbox:
            for target in targets:
                # Skip targets already hit by this attack or that aren't alive
                if target in self.__hit_targets or not target.is_alive():
                    continue

                # Check collision with target's hitbox
                if attack_hitbox.colliderect(target.get_hitbox()):
                    # Calculate damage, might be modified by ability or potion
                    damage = self.calculate_damage(target)
                    # Hit successful
                    hit = target.take_damage(damage)
                    if hit:
                        self.__hit_targets.add(target)
                        hit_targets.append(target)

        return hit_targets

    def calculate_damage(self, target):
        """Calculate damage to be dealt to target, can be overridden by subclasses"""
        return self.get_damage()

    def activate_special_ability(self):
        """Activate hero's special ability, to be implemented by child classes"""
        self.__using_special = True
        self.__special_cooldown_remaining = self.__special_cooldown
        # Specific implementation should be in subclasses

    def get_sprite_path(self, animation_state):
        """Get the sprite path for a specific animation state"""
        try:
            conn = sqlite3.connect('game_data.db')
            c = conn.cursor()

            c.execute('''
                      SELECT sprite_path
                      FROM hero_sprites
                      WHERE hero_type = ?
                        AND animation_state = ?''',
                      (self.__hero_type, animation_state.name))

            result = c.fetchone()
            conn.close()

            if result:
                return result[0]
        except Exception as e:
            print(f"Error loading sprite path: {e}")

        # Default path if not found in database
        return f"assets/sprites/{self.__hero_type}/{animation_state.name.lower()}.png"

    def __str__(self):
        """String representation of the hero"""
        state_names = {
            True: "Active",
            False: "Inactive"
        }

        cooldown_status = "Ready" if self.__special_cooldown_remaining <= 0 else f"{self.__special_cooldown_remaining:.1f}s"

        return (
                f"{self.__hero_type.title()} Hero (Level {1}) | " +  # Assuming level 1 as placeholder
                f"HP: {self.get_health()}/{self.get_max_health()} | " +
                f"DMG: {self.get_damage()} | " +
                f"POS: ({self.get_x()}, {self.get_y()}) | " +
                f"Direction: {self.get_direction().name} | " +
                f"State: {self.get_animation_state().name} | " +
                f"Moving: {state_names[self.__is_moving]} | " +
                f"Attacking: {state_names[self.is_attacking()]} | " +
                f"Defending: {state_names[self.__is_defending]} | " +
                f"Special: {state_names[self.__using_special]} | " +
                f"Special Cooldown: {cooldown_status}"
        )

    # Getter and setter methods for encapsulation

    def get_hero_type(self):
        """Get the hero type"""
        return self.__hero_type

    def is_moving(self):
        """Check if hero is moving"""
        return self.__is_moving

    def set_moving(self, is_moving):
        """Set hero moving state"""
        self.__is_moving = is_moving

    def is_defending(self):
        """Check if hero is defending"""
        return self.__is_defending

    def set_defending(self, is_defending):
        """Set hero defending state"""
        self.__is_defending = is_defending

    def can_input(self):
        """Check if hero can receive input"""
        return self.__can_input

    def set_can_input(self, can_input):
        """Set whether hero can receive input"""
        self.__can_input = can_input

    def get_special_cooldown(self):
        """Get maximum special ability cooldown"""
        return self.__special_cooldown

    def set_special_cooldown(self, cooldown):
        """Set maximum special ability cooldown"""
        self.__special_cooldown = cooldown

    def get_special_cooldown_remaining(self):
        """Get remaining special ability cooldown"""
        return self.__special_cooldown_remaining

    def set_special_cooldown_remaining(self, remaining):
        """Set remaining special ability cooldown"""
        self.__special_cooldown_remaining = max(0, remaining)

    def is_using_special(self):
        """Check if hero is using special ability"""
        return self.__using_special

    def set_using_special(self, using_special):
        """Set whether hero is using special ability"""
        self.__using_special = using_special

    def get_attack_range(self):
        """Get hero's attack range"""
        return self.__attack_range

    def set_attack_range(self, attack_range):
        """Set hero's attack range"""
        self.__attack_range = attack_range

    def get_frame_counts(self):
        """Get animation frame counts dictionary"""
        return self.__frame_counts.copy()

    # Attack combo methods
    def get_attack_combo(self):
        """Get current attack combo count"""
        return self.__attack_combo

    def increment_attack_combo(self):
        """Increment attack combo count"""
        self.__attack_combo += 1

    def reset_attack_combo(self):
        """Reset attack combo count to 0"""
        self.__attack_combo = 0

    def get_attack_window(self):
        """Get attack combo window time"""
        return self.__attack_window

    def set_attack_window(self, window):
        """Set attack combo window time"""
        self.__attack_window = window

    def is_attack_complete(self):
        """Check if current attack is complete"""
        return self.__attack_complete

    def set_attack_complete(self, complete):
        """Set whether current attack is complete"""
        self.__attack_complete = complete

    # Hit targets handling
    def get_hit_targets(self):
        """Get set of entities hit by current attack"""
        return self.__hit_targets

    def add_hit_target(self, target):
        """Add entity to hit targets set"""
        self.__hit_targets.add(target)

    def clear_hit_targets(self):
        """Clear hit targets set"""
        self.__hit_targets.clear()

    def is_alive(self):
        """Check if hero is alive - delegated to parent class"""
        return super().is_alive()

    def is_invulnerable(self):
        """Check if hero is invulnerable - delegated to parent class"""
        return super().is_invulnerable()
