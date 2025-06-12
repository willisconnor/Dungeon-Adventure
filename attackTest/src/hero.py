from character import Character
from entity import AnimationState, Direction
import pygame


class Hero(Character):
    """Player character class"""

    def __init__(self, x, y):
        # Initialize with health=100, speed=7, damage=5
        super().__init__(x, y, max_health=100, speed=7, damage=5)

        # Hero-specific properties
        self.is_moving = False
        self.is_defending = False
        self.can_input = True  # To prevent multiple attacks from a single keypress

        # Frame counts for each animation state
        self.frame_counts = {
            AnimationState.IDLE: 4,
            AnimationState.WALKING: 7,
            AnimationState.ATTACKING_1: 5,
            AnimationState.ATTACKING_2: 4,
            AnimationState.ATTACKING_3: 4,
            AnimationState.DEFENDING: 5,
            AnimationState.HURT: 3,  # Placeholder, adjust based on actual sprites
            AnimationState.DYING: 5,  # Placeholder
            AnimationState.DEAD: 1  # Single frame for dead state
        }

        # Combat properties
        self.attack_range = 80  # Range in pixels

    def get_frames_count(self, state):
        """Get the number of frames for a given animation state"""
        return self.frame_counts.get(state, 4)  # Default to 4 if not found

    def handle_input(self, keys, space_pressed):
        """Handle player input"""
        if not self.is_alive:
            return

        # Process defending (E key)
        self.is_defending = keys[pygame.K_e] and not self.is_attacking

        # Only allow movement if not defending or attacking
        if not self.is_defending and not self.is_attacking:
            # Move left with A
            if keys[pygame.K_a]:
                self.x -= self.speed
                self.direction = Direction.LEFT
                self.is_moving = True
            # Move right with D
            elif keys[pygame.K_d]:
                self.x += self.speed
                self.direction = Direction.RIGHT
                self.is_moving = True
            else:
                self.is_moving = False
        else:
            # No movement while defending or attacking
            self.is_moving = False

        # Handle attack input (spacebar)
        if space_pressed and self.can_input and (self.attack_complete or self.attack_window > 0):
            self.can_input = False  # Prevent multiple attacks from one press

            # Start or continue attack combo
            if self.attack_complete or self.attack_window > 0:
                if self.attack_window > 0 and self.attack_combo > 0:
                    # Continue combo
                    self.attack_combo += 1
                    if self.attack_combo > 3:
                        # Loop back to first attack animation
                        self.attack_combo = 1
                else:
                    # Start new combo
                    self.attack_combo = 1

                self.is_attacking = True
                self.attack_complete = False
                self.attack_window = 0  # Reset combo window on successful input
                # Clear hit targets for new attack
                self.hit_targets.clear()

        # Reset input flag when spacebar is released
        if not space_pressed:
            self.can_input = True

    def update(self, dt):
        """Update hero state"""
        super().update(dt)

        # Update animation state based on current actions
        if self.is_alive and not self.animation_state in [AnimationState.HURT, AnimationState.DYING,
                                                          AnimationState.DEAD]:
            self._update_animation_state()

    def _update_animation_state(self):
        """Update the current animation state based on hero actions"""
        # Store previous state before changing
        self.last_animation_state = self.animation_state

        # Determine new animation state with priority for attacks/defending
        if self.is_attacking:
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
        elif self.is_moving:
            new_state = AnimationState.WALKING
        else:
            new_state = AnimationState.IDLE

        # Only change state if it's different from current
        if new_state != self.animation_state:
            self.animation_state = new_state

            # Only reset frame index if not chaining attacks
            if not (self.is_attacking and
                    self.last_animation_state in [AnimationState.ATTACKING_1, AnimationState.ATTACKING_2,
                                                  AnimationState.ATTACKING_3] and
                    self.animation_state in [AnimationState.ATTACKING_1, AnimationState.ATTACKING_2,
                                             AnimationState.ATTACKING_3]):
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
            x = self.x + 25  # Offset from character center
            y = self.y - height // 2
        else:  # Direction.LEFT
            x = self.x - 25 - width  # Offset from character center
            y = self.y - height // 2

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