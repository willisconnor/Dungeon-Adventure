from src.model.DungeonEntity import Direction, AnimationState
import pygame


# Additional animation states to add to AnimationState enum:
# RUNNING = auto()
# JUMPING = auto()
# FALLING = auto()
# RUNNING_ATTACK = auto()

# Add these to your AnimationState class in DungeonEntity.py

class HeroMovementExtension:
    """Mixin class to add jumping and running attack capabilities to Hero classes"""

    def initialize_movement_capabilities(self):
        """Initialize jumping and running attack properties"""
        # Jumping properties
        self.is_jumping = False
        self.is_falling = False
        self.jump_velocity = 15  # Initial upward velocity
        self.jump_height = 200  # Maximum jump height
        self.y_velocity = 0  # Current vertical velocity
        self.gravity = 0.8  # Gravity constant
        self.ground_y = self.y  # Store original ground position
        self.max_fall_speed = 20  # Maximum falling speed
        self.can_double_jump = True  # Enable double jumping
        self.has_double_jumped = False

        # Running properties
        self.is_running = False
        self.run_speed = self.speed * 1.5  # 50% faster than walking
        self.run_threshold = 10  # Frames before walking becomes running
        self.run_counter = 0

        # Running attack properties
        self.is_running_attacking = False
        self.running_attack_damage_multiplier = 1.3  # 30% more damage

        # Update frame rates dictionary if it exists
        if hasattr(self, 'frame_rates'):
            self.frame_rates.update({
                AnimationState.RUNNING: 5,
                AnimationState.JUMPING: 4,
                AnimationState.FALLING: 4,
                AnimationState.RUNNING_ATTACK: 5
            })

    def handle_extended_input(self, keys, dt):
        """Extended input handling for jumps and running"""
        if not self.is_alive:
            return

        # Process jumping (W key)
        if keys[pygame.K_w]:
            if not self.is_jumping and not self.is_falling:
                # Regular jump from ground
                self.start_jump()
            elif self.is_jumping or self.is_falling:
                # Double jump in mid-air if available
                if self.can_double_jump and not self.has_double_jumped:
                    self.double_jump()

        # Process running (hold Shift while moving)
        if (keys[pygame.K_a] or keys[pygame.K_d]) and keys[pygame.K_LSHIFT]:
            self.run_counter += 1
            if self.run_counter >= self.run_threshold:
                self.is_running = True
        else:
            self.is_running = False
            self.run_counter = 0

        # Running attack (X key while running)
        if keys[pygame.K_x] and self.is_running and not self.is_running_attacking and not self.is_attacking:
            self.start_running_attack()

    def update_movement(self, dt):
        """Update jumping and running states"""
        # Update jumping physics
        if self.is_jumping or self.is_falling:
            # Apply gravity
            self.y_velocity += self.gravity * dt * 60

            # Limit fall speed
            if self.y_velocity > self.max_fall_speed:
                self.y_velocity = self.max_fall_speed

            # Update position
            self.y += self.y_velocity * dt * 60

            # Check if reached apex of jump (velocity becomes positive/downward)
            if self.is_jumping and self.y_velocity >= 0:
                self.is_jumping = False
                self.is_falling = True

            # Check if reached ground
            if self.is_falling and self.y >= self.ground_y:
                self.land()

        # Update animation state based on movement
        self._update_extended_animation_state()

    def start_jump(self):
        """Start a jump"""
        if not self.is_jumping and not self.is_falling:
            self.is_jumping = True
            self.is_falling = False
            self.y_velocity = -self.jump_velocity
            self.ground_y = self.y  # Store ground position
            self.has_double_jumped = False

    def double_jump(self):
        """Perform a double jump in mid-air"""
        self.is_jumping = True
        self.is_falling = False
        self.y_velocity = -self.jump_velocity * 0.8  # Slightly weaker than first jump
        self.has_double_jumped = True

    def land(self):
        """Land on the ground"""
        self.y = self.ground_y
        self.is_jumping = False
        self.is_falling = False
        self.y_velocity = 0
        self.has_double_jumped = False

    def start_running_attack(self):
        """Start a running attack"""
        self.is_running_attacking = True
        self.attack_complete = False

        # Clear any targets hit in previous attack
        self.hit_targets.clear()

    def _update_extended_animation_state(self):
        """Update animation state based on jumping and running"""
        # Priority: running attack > jumping/falling > running > other states

        if self.is_running_attacking:
            new_state = AnimationState.RUNNING_ATTACK
        elif self.is_jumping:
            new_state = AnimationState.JUMPING
        elif self.is_falling:
            new_state = AnimationState.FALLING
        elif self.is_running:
            new_state = AnimationState.RUNNING
        else:
            # Let the base class handle other states
            return

        # Only change state if it's different
        if new_state != self.animation_state:
            self.animation_state = new_state
            self.frame_index = 0
            self.animation_counter = 0

    def get_running_attack_hitbox(self):
        """Get hitbox for running attack"""
        if not self.is_running_attacking:
            return None

        # Running attack has a wider, forward-focused hitbox
        width = self.attack_range * 1.5
        height = 60

        if self.direction == Direction.RIGHT:
            x = self.x + 25  # Offset from character center
            y = self.y - height // 2
        else:  # Direction.LEFT
            x = self.x - 25 - width  # Offset from character center
            y = self.y - height // 2

        return pygame.Rect(x, y, width, height)

    def calculate_running_attack_damage(self, target):
        """Calculate damage for running attack"""
        # Base damage increased by multiplier
        base_damage = self.calculate_damage(target)
        return int(base_damage * self.running_attack_damage_multiplier)

    def jump_attack(self, targets):
        """Perform an attack while in the air"""
        # Air attacks might have different properties
        # For example, a downward strike that can bounce off enemies
        if not self.is_alive or (not self.is_jumping and not self.is_falling):
            return []

        # Similar to normal attack but with air-specific hitbox/damage
        hit_targets = []

        # Create a downward-focused hitbox
        attack_hitbox = self.get_jump_attack_hitbox()

        if attack_hitbox:
            for target in targets:
                # Skip targets already hit or dead
                if target in self.hit_targets or not target.is_alive:
                    continue

                # Check collision
                if attack_hitbox.colliderect(target.hitbox):
                    # Bounce off enemy
                    self.y_velocity = -self.jump_velocity * 0.6

                    # Deal damage
                    damage = int(self.damage * 1.2)  # 20% more damage for jump attacks
                    hit = target.take_damage(damage)

                    if hit:
                        self.hit_targets.add(target)
                        hit_targets.append(target)

        return hit_targets

    def get_jump_attack_hitbox(self):
        """Get hitbox for jump attack"""
        if not (self.is_jumping or self.is_falling) or not self.is_attacking:
            return None

        # Different hitbox for air attacks - more focused below the player
        width = self.width * 0.8
        height = self.height * 1.5

        x = self.x - width / 2
        y = self.y  # Extend below the player

        return pygame.Rect(x, y, width, height)


# Example usage in Hero subclass:
"""
class Knight(Hero, HeroMovementExtension):
    def __init__(self, x, y):
        super().__init__(x, y, hero_type="knight")
        self.initialize_movement_capabilities()

    def update(self, dt):
        super().update(dt)
        self.update_movement(dt)

    def handle_input(self, keys, space_pressed):
        super().handle_input(keys, space_pressed)
        self.handle_extended_input(keys, dt)
"""
from src.model.DungeonEntity import Direction, AnimationState
import pygame


# Additional animation states to add to AnimationState enum:
# RUNNING = auto()
# JUMPING = auto()
# FALLING = auto()
# RUNNING_ATTACK = auto()

# Add these to your AnimationState class in DungeonEntity.py

class HeroMovementExtension:
    """Mixin class to add jumping and running attack capabilities to Hero classes"""

    def initialize_movement_capabilities(self):
        """Initialize jumping and running attack properties"""
        # Jumping properties
        self.is_jumping = False
        self.is_falling = False
        self.jump_velocity = 15  # Initial upward velocity
        self.jump_height = 200  # Maximum jump height
        self.y_velocity = 0  # Current vertical velocity
        self.gravity = 0.8  # Gravity constant
        self.ground_y = self.y  # Store original ground position

        # Running properties
        self.is_running = False
        self.run_speed = self.speed * 1.5  # 50% faster than walking
        self.run_threshold = 10  # Frames before walking becomes running
        self.run_counter = 0

        # Running attack properties
        self.is_running_attacking = False
        self.running_attack_damage_multiplier = 1.3  # 30% more damage

        # Update frame rates dictionary if it exists
        if hasattr(self, 'frame_rates'):
            self.frame_rates.update({
                AnimationState.RUNNING: 5,
                AnimationState.JUMPING: 4,
                AnimationState.FALLING: 4,
                AnimationState.RUNNING_ATTACK: 5
            })

    def handle_extended_input(self, keys, dt):
        """Extended input handling for jumps and running"""
        if not self.is_alive:
            return

        # Process jumping (Space key)
        if keys[pygame.K_SPACE] and not self.is_jumping and not self.is_falling:
            self.start_jump()

        # Process running (hold Shift while moving)
        if (keys[pygame.K_a] or keys[pygame.K_d]) and keys[pygame.K_LSHIFT]:
            self.run_counter += 1
            if self.run_counter >= self.run_threshold:
                self.is_running = True
        else:
            self.is_running = False
            self.run_counter = 0

        # Running attack (X key while running)
        if keys[pygame.K_x] and self.is_running and not self.is_running_attacking and not self.is_attacking:
            self.start_running_attack()

    def update_movement(self, dt):
        """Update jumping and running states"""
        # Update jumping physics
        if self.is_jumping or self.is_falling:
            # Apply gravity
            self.y_velocity += self.gravity

            # Update position
            self.y += self.y_velocity

            # Check if reached apex of jump
            if self.is_jumping and self.y_velocity >= 0:
                self.is_jumping = False
                self.is_falling = True

            # Check if reached ground
            if self.is_falling and self.y >= self.ground_y:
                self.is_falling = False
                self.y = self.ground_y
                self.y_velocity = 0

        # Update animation state based on movement
        self._update_extended_animation_state()

    def start_jump(self):
        """Start a jump"""
        if not self.is_jumping and not self.is_falling:
            self.is_jumping = True
            self.y_velocity = -self.jump_velocity
            self.ground_y = self.y  # Store ground position

    def start_running_attack(self):
        """Start a running attack"""
        self.is_running_attacking = True
        self.attack_complete = False

        # Clear any targets hit in previous attack
        self.hit_targets.clear()

    def _update_extended_animation_state(self):
        """Update animation state based on jumping and running"""
        # Priority: running attack > jumping/falling > running > other states

        if self.is_running_attacking:
            new_state = AnimationState.RUNNING_ATTACK
        elif self.is_jumping:
            new_state = AnimationState.JUMPING
        elif self.is_falling:
            new_state = AnimationState.FALLING
        elif self.is_running:
            new_state = AnimationState.RUNNING
        else:
            # Let the base class handle other states
            return

        # Only change state if it's different
        if new_state != self.animation_state:
            self.animation_state = new_state
            self.frame_index = 0
            self.animation_counter = 0

    def get_running_attack_hitbox(self):
        """Get hitbox for running attack"""
        if not self.is_running_attacking:
            return None

        # Running attack has a wider, forward-focused hitbox
        width = self.attack_range * 1.5
        height = 60

        if self.direction == Direction.RIGHT:
            x = self.x + 25  # Offset from character center
            y = self.y - height // 2
        else:  # Direction.LEFT
            x = self.x - 25 - width  # Offset from character center
            y = self.y - height // 2

        return pygame.Rect(x, y, width, height)

    def calculate_running_attack_damage(self, target):
        """Calculate damage for running attack"""
        # Base damage increased by multiplier
        base_damage = self.calculate_damage(target)
        return int(base_damage * self.running_attack_damage_multiplier)


# Example usage in Hero subclass:
"""
class Knight(Hero, HeroMovementExtension):
    def __init__(self, x, y):
        super().__init__(x, y, hero_type="knight")
        self.initialize_movement_capabilities()

    def update(self, dt):
        super().update(dt)
        self.update_movement(dt)

    def handle_input(self, keys, space_pressed):
        super().handle_input(keys, space_pressed)
        self.handle_extended_input(keys, dt)
"""