from entity import Entity, AnimationState, Direction


class Character(Entity):
    """Base character class for both hero and enemies"""

    def __init__(self, x, y, max_health, speed, damage):
        super().__init__(x, y, max_health)
        self.speed = speed
        self.damage = damage

        # Animation properties
        self.frame_rates = {
            AnimationState.IDLE: 6,
            AnimationState.WALKING: 6,
            AnimationState.ATTACKING_1: 5,
            AnimationState.ATTACKING_2: 5,
            AnimationState.ATTACKING_3: 5,
            AnimationState.DEFENDING: 6,
            AnimationState.HURT: 4,
            AnimationState.DYING: 8,
            AnimationState.DEAD: 1  # Single frame for dead state
        }

        # Combat properties
        self.is_attacking = False
        self.attack_combo = 0
        self.attack_complete = True
        self.attack_window = 0
        self.hit_targets = set()  # Track what's been hit this attack

    def update(self, dt):
        """Update character state"""
        self._update_hitbox()
        self._update_invulnerability(dt)
        self._update_animation(dt)
        self._update_attack_state(dt)

    def take_damage(self, amount):
        """Handle taking damage"""
        if not self.is_alive or self.is_invulnerable:
            return False

        self.health -= amount

        # Set invulnerability
        self.is_invulnerable = True
        self.invulnerable_timer = 0.5  # 500ms invulnerability

        # Check if dead
        if self.health <= 0:
            self.health = 0
            self.animation_state = AnimationState.DYING
            return True
        else:
            self.animation_state = AnimationState.HURT
            return True

    def _update_animation(self, dt):
        """Update animation frame index"""
        # Get current frame rate for this animation state
        current_frame_rate = self.frame_rates.get(self.animation_state, 6)

        # Increment counter
        self.animation_counter += dt * 60  # Convert to roughly 60fps counting

        # Update frame when counter exceeds frame rate
        if self.animation_counter >= current_frame_rate:
            self.animation_counter = 0

            # Special handling for dying animation
            if self.animation_state == AnimationState.DYING:
                if self.frame_index >= self.get_frames_count(AnimationState.DYING) - 1:
                    self.animation_state = AnimationState.DEAD
                    self.frame_index = 0
                    self.is_alive = False
                else:
                    self.frame_index += 1
            # Special handling for hurt animation
            elif self.animation_state == AnimationState.HURT:
                if self.frame_index >= self.get_frames_count(AnimationState.HURT) - 1:
                    self.animation_state = AnimationState.IDLE
                    self.frame_index = 0
                else:
                    self.frame_index += 1
            # Normal animation cycling
            else:
                frame_count = self.get_frames_count(self.animation_state)
                self.frame_index = (self.frame_index + 1) % frame_count

                # For attack animations, check if complete
                if self.is_attacking and self.frame_index == 0:
                    self._handle_attack_complete()

    def _update_attack_state(self, dt):
        """Update attack combo window"""
        if self.attack_window > 0:
            self.attack_window -= dt * 60
            if self.attack_window <= 0:
                self.attack_window = 0
                if self.attack_complete:
                    self.attack_combo = 0

    def _handle_attack_complete(self):
        """Handle completion of an attack animation"""
        self.attack_complete = True
        self.attack_window = 20  # ~333ms at 60fps to chain attacks
        # Clear hit targets when an attack is complete
        self.hit_targets.clear()

        # If not chaining attacks, end attacking state
        if self.attack_combo == 0:
            self.is_attacking = False
            self.animation_state = AnimationState.IDLE

    def get_frames_count(self, state):
        """Get the number of frames for a given animation state"""
        # This will be implemented by subclasses
        return 4  # Default value, should be overridden
