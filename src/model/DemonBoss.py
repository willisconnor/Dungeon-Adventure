from src.model.DungeonEntity import Direction, AnimationState, DungeonEntity
import pygame


class DemonBoss(DungeonEntity):
    """Demon boss enemy class with specialized abilities"""

    def __init__(self, x, y):
        super().__init__(x, y, 128, 128, "Demon Boss", 500, 500, 3)
        self.x = x
        self.y = y
        self.width = 128  # Assuming 128x128 sprite size
        self.height = 128
        self.name = "Demon Boss"
        self.enemy_type = "demon_boss"

        # Stats
        self.max_health = 500
        self.health = self.max_health
        self.damage = 25
        self.speed = 3  # Slower but powerful
        self.attack_range = 120
        self.is_alive = True

        # Animation properties
        self.direction = Direction.LEFT
        self.animation_state = AnimationState.IDLE
        self.last_animation_state = AnimationState.IDLE
        self.frame_index = 0
        self.animation_counter = 0

        # Animation frame rates
        self.frame_rates = {
            AnimationState.IDLE: 10,
            AnimationState.WALKING: 8,
            AnimationState.ATTACKING_1: 6,
            AnimationState.HURT: 4,
            AnimationState.DYING: 5,
            AnimationState.DEAD: 999  # Static frame
        }

        # Combat properties
        self.is_attacking = False
        self.attack_cooldown = 0
        self.is_invulnerable = False
        self.invulnerable_timer = 0
        self.hitbox = pygame.Rect(x, y, width=80, height=100)  # Smaller than sprite for better gameplay
        self.hit_targets = set()

        # Boss specific properties
        self.enraged = False
        self.enrage_threshold = 0.3  # Enrages at 30% health
        self.attack_pattern = 0  # Tracks attack pattern phase
        self.cleave_damage_multiplier = 1.5  # Special cleave attack deals more damage

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
        self.hitbox.x = self.x + self.width // 4
        self.hitbox.y = self.y + self.height // 4

    def _update_invulnerability(self, dt):
        """Update invulnerability timer"""
        if self.is_invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.is_invulnerable = False
                self.invulnerable_timer = 0

    def _update_animation(self, dt):
        """Update animation frame index"""
        # Get current frame rate for this animation state
        current_frame_rate = self.frame_rates.get(self.animation_state, 6)

        # Increment counter
        self.animation_counter += dt * 60  # convert to roughly 60 fps

        # Update frame when counter exceeds frame rate
        if self.animation_counter >= current_frame_rate:
            self.animation_counter = 0

            # Special handling for dying animation
            if self.animation_state == AnimationState.DYING:
                if self.frame_index >= self.get_frames_count(AnimationState.DYING) - 1:
                    self.animation_state = AnimationState.DEAD
                    self.frame_index = 0
                else:
                    self.frame_index += 1

            # Normal animation cycling
            else:
                frame_count = self.get_frames_count(self.animation_state)
                self.frame_index = (self.frame_index + 1) % frame_count

                # For attack animations, check if complete
                if self.is_attacking and self.frame_index == 0:
                    self.is_attacking = False
                    self.animation_state = AnimationState.IDLE

    def _update_attack_cooldown(self, dt):
        """Update attack cooldown timer"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 0

    def _check_enrage_state(self):
        """Check if boss should enter enraged state"""
        if not self.enraged and self.health / self.max_health < self.enrage_threshold:
            self.enraged = True
            self.damage *= 1.5  # Increase damage when enraged
            self.speed *= 1.2  # Slightly faster when enraged

    def take_damage(self, amount):
        """Handle taking damage"""
        if not self.is_alive or self.is_invulnerable:
            return False

        self.health -= amount

        # Set invulnerability period
        self.is_invulnerable = True
        self.invulnerable_timer = 0.5  # Half second invulnerability

        # Handle death
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.animation_state = AnimationState.DYING
            self.frame_index = 0
            return True

        # Play hurt animation
        self.animation_state = AnimationState.HURT
        self.frame_index = 0

        return True

    def attack(self, target):
        """Attempt to attack a target"""
        if not self.is_alive or self.is_attacking or self.attack_cooldown > 0:
            return False

        # Start attack animation
        self.is_attacking = True
        self.animation_state = AnimationState.ATTACKING_1
        self.frame_index = 0
        self.attack_cooldown = 1.5  # 1.5 seconds between attacks

        # Calculate attack hitbox
        attack_hitbox = self.get_attack_hitbox()

        # Check if target is within attack range
        if attack_hitbox and target.hitbox.colliderect(attack_hitbox):
            # Different damage based on attack type (cleave or normal)
            actual_damage = self.damage
            if self.attack_pattern == 1:  # Cleave attack
                actual_damage = int(self.damage * self.cleave_damage_multiplier)

            target.take_damage(actual_damage)

            # Cycle to next attack pattern
            self.attack_pattern = (self.attack_pattern + 1) % 2
            return True

        return False

    def get_attack_hitbox(self):
        """Get hitbox for current attack"""
        if not self.is_attacking:
            return None

        # Create attack hitbox based on direction
        width = self.attack_range
        height = 100

        if self.direction == Direction.RIGHT:
            x = self.x + self.width // 2
            y = self.y - height // 4
        else:  # Direction.LEFT
            x = self.x - width
            y = self.y - height // 4

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
        if not self.is_alive or self.is_attacking:
            return

        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y

        # Update facing direction
        if dx > 0:
            self.direction = Direction.RIGHT
        elif dx < 0:
            self.direction = Direction.LEFT

        # Calculate distance to target
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Only move if target is far enough
        if distance > self.attack_range:
            # Normalize direction vector
            if distance > 0:
                dx /= distance
                dy /= distance

            # Move towards target
            self.x += dx * self.speed * dt * 60
            self.y += dy * self.speed * dt * 60

            # Update animation state
            self.animation_state = AnimationState.WALKING
        else:
            # In range to attack, stop moving
            self.animation_state = AnimationState.IDLE