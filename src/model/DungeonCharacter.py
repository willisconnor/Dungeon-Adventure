from src.model.DungeonEntity import DungeonEntity, AnimationState, Direction


class DungeonCharacter(DungeonEntity):
    """Base character class for both hero and enemy, inherits from DungeonEntity"""

    def __init__(self, x, y, width, height, name, max_health, health, speed, damage, animation_state):
        super().__init__(x, y, width, height, name, max_health, health, speed, animation_state)

        # Combat attributes
        self.__damage = damage
        self.__is_attacking = False
        self.__attack_combo = 0
        self.__attack_complete = True
        self.__attack_window = 0
        self.__hit_targets = set()  # track what's been hit this attack

        # Animation frame properties
        self.__frame_index = 0
        self.__frame_rates = {}  # To be set by subclasses

    def update(self, dt):
        """Update character state"""
        self._update_hitbox()
        self._update_invulnerability(dt)
        self._update_animation(dt)
        self._update_attack_state(dt)

    def take_damage(self, amount):
        """Handle taking damage"""
        if not self.is_alive() or self.is_invulnerable():
            return False

        self.set_health(self.get_health() - amount)
        return True

    def _update_animation(self, dt):
        """Update animation frame index"""
        # Get current frame rate for this animation state
        current_frame_rate = self.__frame_rates.get(self.get_animation_state(), 6)

        # Increment counter
        self.increment_animation_counter(dt * 60)  # Convert to roughly 60 fps

        # Update frame when counter exceeds frame rate
        if self.get_animation_counter() >= current_frame_rate:
            self.reset_animation_counter()

            # Special handling for dying animation
            if self.get_animation_state() == AnimationState.DYING:
                if self.__frame_index >= self.get_frames_count(AnimationState.HURT) - 1:
                    self.set_animation_state(AnimationState.DEAD)
                    self.__frame_index = 0
                else:
                    self.__frame_index += 1
            # Normal animation cycling
            else:
                frame_count = self.get_frames_count(self.get_animation_state())
                self.__frame_index = (self.__frame_index + 1) % frame_count

                # For attack animations, check if complete
                if self.__is_attacking and self.__frame_index == 0:
                    self._handle_attack_complete()

    def _update_attack_state(self, dt):
        """Update attack combo window for combat"""
        if self.__attack_window > 0:
            self.__attack_window -= dt * 60
            if self.__attack_window <= 0:
                self.__attack_window = 0
                if self.__attack_complete:
                    self.__attack_combo = 0

    def _handle_attack_complete(self):
        """Handle completion of an attack animation"""
        self.__attack_complete = True
        self.__attack_window = 20  # ~333 ms at 60 fps to chain attacks
        # Clear hit targets when an attack is complete
        self.__hit_targets.clear()

        # If not chaining attacks, end attacking state
        if self.__attack_combo == 0:
            self.__is_attacking = False
            self.set_animation_state(AnimationState.IDLE)

    def get_frames_count(self, state):
        """Get the number of frames for a given animation state
        Should be overridden in child classes"""
        return 4  # Default value, should be overridden

    # Getters and setters
    def get_damage(self):
        """Get character's damage"""
        return self.__damage

    def set_damage(self, damage):
        """Set character's damage"""
        self.__damage = damage

    def is_attacking(self):
        """Check if character is attacking"""
        return self.__is_attacking

    def set_attacking(self, attacking):
        """Set attacking state"""
        self.__is_attacking = attacking
        if attacking:
            self.set_animation_state(AnimationState.ATTACKING)

    def get_attack_combo(self):
        """Get current attack combo count"""
        return self.__attack_combo

    def increment_attack_combo(self):
        """Increment attack combo counter"""
        self.__attack_combo += 1
        return self.__attack_combo

    def reset_attack_combo(self):
        """Reset attack combo counter"""
        self.__attack_combo = 0

    def is_attack_complete(self):
        """Check if attack animation is complete"""
        return self.__attack_complete

    def set_attack_complete(self, complete):
        """Set attack complete state"""
        self.__attack_complete = complete

    def get_attack_window(self):
        """Get remaining time in attack window"""
        return self.__attack_window

    def set_attack_window(self, window):
        """Set attack window time"""
        self.__attack_window = window

    def get_hit_targets(self):
        """Get set of targets hit by this attack"""
        return self.__hit_targets.copy()

    def add_hit_target(self, target):
        """Add a target to the hit targets set"""
        self.__hit_targets.add(target)

    def clear_hit_targets(self):
        """Clear all hit targets"""
        self.__hit_targets.clear()

    def get_frame_index(self):
        """Get current animation frame index"""
        return self.__frame_index

    def set_frame_index(self, index):
        """Set animation frame index"""
        self.__frame_index = index

    def increment_frame_index(self):
        """Increment frame index by one"""
        self.__frame_index += 1

    def get_frame_rates(self):
        """Get frame rates dictionary"""
        return self.__frame_rates.copy()

    def set_frame_rate(self, animation_state, rate):
        """Set frame rate for a specific animation state"""
        self.__frame_rates[animation_state] = rate

    def set_frame_rates(self, frame_rates):
        """Set all frame rates at once"""
        self.__frame_rates = frame_rates.copy()

    def __str__(self):
        """String representation of character"""
        return f"{self.get_name()} (HP: {self.get_health()}/{self.get_max_health()}, DMG: {self.__damage})"

# Added __str__ method ^^^
# __repr__ method?