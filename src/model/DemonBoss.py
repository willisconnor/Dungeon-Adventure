from src.model.DungeonEntity import Direction, AnimationState
import pygame


class DemonBoss:
    """Demon boss enemy class with specialized abilities"""

    def __init__(self, x, y):
        self.__x = x
        self.__y = y
        self.__width = 128  # Assuming 128x128 sprite size
        self.__height = 128
        self.__name = "Demon Boss"
        self.__enemy_type = "demon_boss"

        # Stats
        self.__max_health = 500
        self.__health = self.__max_health
        self.__damage = 25
        self.__speed = 3  # Slower but powerful
        self.__attack_range = 120
        self.__is_alive = True

        # Animation properties
        self.__direction = Direction.LEFT
        self.__animation_state = AnimationState.IDLE
        self.__last_animation_state = AnimationState.IDLE
        self.__frame_index = 0
        self.__animation_counter = 0

        # Animation frame rates
        self.__frame_rates = {
            AnimationState.IDLE: 10,
            AnimationState.WALKING: 8,
            AnimationState.ATTACKING_1: 6,
            AnimationState.HURT: 4,
            AnimationState.DYING: 5,
            AnimationState.DEAD: 999  # Static frame
        }

        # Combat properties
        self.__is_attacking = False
        self.__attack_cooldown = 0
        self.__is_invulnerable = False
        self.__invulnerable_timer = 0
        self.__hitbox = pygame.Rect(x, y, width=80, height=100)  # Smaller than sprite for better gameplay
        self.__hit_targets = set()

        # Boss specific properties
        self.__enraged = False
        self.__enrage_threshold = 0.3  # Enrages at 30% health
        self.__attack_pattern = 0  # Tracks attack pattern phase
        self.__cleave_damage_multiplier = 1.5  # Special cleave attack deals more damage

    def update(self, dt):
        """Update boss state"""
        self._update_hitbox()
        self._update_invulnerability(dt)
        self._update_animation(dt)
        self._update_attack_cooldown(dt)
        self._check_enrage_state()

    def _update_hitbox(self):
        """Update hitbox position based on entity position"""
        # Center the hitbox to the entity with slight adjustments
        self.__hitbox.x = self.__x + self.__width // 4
        self.__hitbox.y = self.__y + self.__height // 4

    def _update_invulnerability(self, dt):
        """Update invulnerability timer"""
        if self.__is_invulnerable:
            self.__invulnerable_timer -= dt
            if self.__invulnerable_timer <= 0:
                self.__is_invulnerable = False
                self.__invulnerable_timer = 0

    def _update_animation(self, dt):
        """Update animation frame index"""
        # Get current frame rate for this animation state
        current_frame_rate = self.__frame_rates.get(self.__animation_state, 6)

        # Increment counter
        self.__animation_counter += dt * 60  # convert to roughly 60 fps

        # Update frame when counter exceeds frame rate
        if self.__animation_counter >= current_frame_rate:
            self.__animation_counter = 0

            # Special handling for dying animation
            if self.__animation_state == AnimationState.DYING:
                if self.__frame_index >= self.get_frames_count(AnimationState.DYING) - 1:
                    self.__animation_state = AnimationState.DEAD
                    self.__frame_index = 0
                else:
                    self.__frame_index += 1

            # Normal animation cycling
            else:
                frame_count = self.get_frames_count(self.__animation_state)
                self.__frame_index = (self.__frame_index + 1) % frame_count

                # For attack animations, check if complete
                if self.__is_attacking and self.__frame_index == 0:
                    self.__is_attacking = False
                    self.__animation_state = AnimationState.IDLE

    def _update_attack_cooldown(self, dt):
        """Update attack cooldown timer"""
        if self.__attack_cooldown > 0:
            self.__attack_cooldown -= dt
            if self.__attack_cooldown <= 0:
                self.__attack_cooldown = 0

    def _check_enrage_state(self):
        """Check if boss should enter enraged state"""
        if not self.__enraged and self.__health / self.__max_health < self.__enrage_threshold:
            self.__enraged = True
            self.__damage *= 1.5  # Increase damage when enraged
            self.__speed *= 1.2  # Slightly faster when enraged

    def take_damage(self, amount):
        """Handle taking damage"""
        if not self.__is_alive or self.__is_invulnerable:
            return False

        self.__health -= amount

        # Set invulnerability period
        self.__is_invulnerable = True
        self.__invulnerable_timer = 0.5  # Half second invulnerability

        # Handle death
        if self.__health <= 0:
            self.__health = 0
            self.__is_alive = False
            self.__animation_state = AnimationState.DYING
            self.__frame_index = 0
            return True

        # Play hurt animation
        self.__animation_state = AnimationState.HURT
        self.__frame_index = 0

        return True

    def attack(self, target):
        """Attempt to attack a target"""
        if not self.__is_alive or self.__is_attacking or self.__attack_cooldown > 0:
            return False

        # Start attack animation
        self.__is_attacking = True
        self.__animation_state = AnimationState.ATTACKING_1
        self.__frame_index = 0
        self.__attack_cooldown = 1.5  # 1.5 seconds between attacks

        # Calculate attack hitbox
        attack_hitbox = self.get_attack_hitbox()

        # Check if target is within attack range
        if attack_hitbox and hasattr(target, 'hitbox') and target.hitbox.colliderect(attack_hitbox):
            # Different damage based on attack type (cleave or normal)
            actual_damage = self.__damage
            if self.__attack_pattern == 1:  # Cleave attack
                actual_damage = int(self.__damage * self.__cleave_damage_multiplier)

            target.take_damage(actual_damage)

            # Cycle to next attack pattern
            self.__attack_pattern = (self.__attack_pattern + 1) % 2
            return True

        return False

    def get_attack_hitbox(self):
        """Get hitbox for current attack"""
        if not self.__is_attacking:
            return None

        # Create attack hitbox based on direction
        width = self.__attack_range
        height = 100

        if self.__direction == Direction.RIGHT:
            x = self.__x + self.__width // 2
            y = self.__y - height // 4
        else:  # Direction.LEFT
            x = self.__x - width
            y = self.__y - height // 4

        return pygame.Rect(x, y, width, height)

    def get_frames_count(self, state):
        """Get the number of frames for a given animation state"""
        # Default frame counts, should be replaced with database values in production
        frame_counts = {
            AnimationState.IDLE: 6,
            AnimationState.WALKING: 6,
            AnimationState.ATTACKING_1: 8,  # Cleave attack
            AnimationState.HURT: 3,
            AnimationState.DYING: 8,
            AnimationState.DEAD: 1
        }
        return frame_counts.get(state, 4)  # Default to 4 if not found

    def move_towards_target(self, target_x, target_y, dt):
        """Move boss towards a target position"""
        if not self.__is_alive or self.__is_attacking:
            return

        # Calculate direction to target
        dx = target_x - self.__x
        dy = target_y - self.__y

        # Update facing direction
        if dx > 0:
            self.__direction = Direction.RIGHT
        elif dx < 0:
            self.__direction = Direction.LEFT

        # Calculate distance to target
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Only move if target is far enough
        if distance > self.__attack_range:
            # Normalize direction vector
            if distance > 0:
                dx /= distance
                dy /= distance

            # Move towards target
            self.__x += dx * self.__speed * dt * 60
            self.__y += dy * self.__speed * dt * 60

            # Update animation state
            self.__animation_state = AnimationState.WALKING
        else:
            # In range to attack, stop moving
            self.__animation_state = AnimationState.IDLE

    def __str__(self):
        """String representation of the Demon Boss"""
        enrage_status = "ENRAGED" if self.__enraged else "Normal"
        attack_pattern = "Cleave" if self.__attack_pattern == 1 else "Normal"

        return (
                f"{self.__name} | " +
                f"HP: {self.__health}/{self.__max_health} | " +
                f"DMG: {self.__damage} | " +
                f"POS: ({self.__x}, {self.__y}) | " +
                f"Direction: {self.__direction.name} | " +
                f"State: {self.__animation_state.name} | " +
                f"Status: {enrage_status} | " +
                f"Attack Pattern: {attack_pattern} | " +
                f"Invulnerable: {self.__is_invulnerable}"
        )

    # Getters for properties
    def get_x(self):
        """Get x position"""
        return self.__x

    def get_y(self):
        """Get y position"""
        return self.__y

    def get_width(self):
        """Get width"""
        return self.__width

    def get_height(self):
        """Get height"""
        return self.__height

    def get_name(self):
        """Get name"""
        return self.__name

    def get_enemy_type(self):
        """Get enemy type"""
        return self.__enemy_type

    def get_max_health(self):
        """Get max health"""
        return self.__max_health

    def get_health(self):
        """Get current health"""
        return self.__health

    def get_damage(self):
        """Get damage"""
        return self.__damage

    def get_speed(self):
        """Get speed"""
        return self.__speed

    def get_attack_range(self):
        """Get attack range"""
        return self.__attack_range

    def get_direction(self):
        """Get direction"""
        return self.__direction

    def get_animation_state(self):
        """Get animation state"""
        return self.__animation_state

    def get_frame_index(self):
        """Get frame index"""
        return self.__frame_index

    def get_frame_rates(self):
        """Get frame rates"""
        return self.__frame_rates.copy()

    def is_attacking(self):
        """Check if attacking"""
        return self.__is_attacking

    def get_attack_cooldown(self):
        """Get attack cooldown"""
        return self.__attack_cooldown

    def is_invulnerable(self):
        """Check if invulnerable"""
        return self.__is_invulnerable

    def get_invulnerable_timer(self):
        """Get invulnerable timer"""
        return self.__invulnerable_timer

    def get_hitbox(self):
        """Get hitbox"""
        return self.__hitbox

    def is_enraged(self):
        """Check if enraged"""
        return self.__enraged

    def get_enrage_threshold(self):
        """Get enrage threshold"""
        return self.__enrage_threshold

    def get_attack_pattern(self):
        """Get attack pattern"""
        return self.__attack_pattern

    def get_cleave_damage_multiplier(self):
        """Get cleave damage multiplier"""
        return self.__cleave_damage_multiplier

    # Properties for backward compatibility
    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def name(self):
        return self.__name

    @property
    def enemy_type(self):
        return self.__enemy_type

    @property
    def max_health(self):
        return self.__max_health

    @property
    def health(self):
        return self.__health

    @property
    def damage(self):
        return self.__damage

    @property
    def speed(self):
        return self.__speed

    @property
    def attack_range(self):
        return self.__attack_range

    @property
    def is_alive(self):
        return self.__is_alive

    @property
    def direction(self):
        return self.__direction

    @property
    def animation_state(self):
        return self.__animation_state

    @property
    def frame_index(self):
        return self.__frame_index

    @property
    def is_attacking(self):
        return self.__is_attacking

    @property
    def attack_cooldown(self):
        return self.__attack_cooldown

    @property
    def is_invulnerable(self):
        return self.__is_invulnerable

    @property
    def invulnerable_timer(self):
        return self.__invulnerable_timer

    @property
    def hitbox(self):
        return self.__hitbox

    @property
    def enraged(self):
        return self.__enraged

    # Setters for backward compatibility where needed
    @x.setter
    def x(self, value):
        self.__x = value

    @y.setter
    def y(self, value):
        self.__y = value

    @health.setter
    def health(self, value):
        self.__health = value

    @direction.setter
    def direction(self, value):
        self.__direction = value

    @animation_state.setter
    def animation_state(self, value):
        self.__animation_state = value

    @frame_index.setter
    def frame_index(self, value):
        self.__frame_index = value