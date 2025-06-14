"""
DungeonCharacter.py - Base character class for heroes and enemies
@author Connor Willis
"""
import pygame
from src.model.DungeonEntity import Direction, AnimationState


class DungeonCharacter:
    """
    Base class for all characters in the dungeon (heroes and enemies).

    This class handles character positioning, movement, combat mechanics, animation states,
    and basic character attributes like health, damage, and special abilities.

    Attributes (there's a lot):
        x (float): X position of the character
        y (float): Y position of the character
        width (int): Width of the character sprite
        height (int): Height of the character sprite
        rect (pygame.Rect): Main collision rectangle
        hitbox (pygame.Rect): Smaller hitbox for more precise collision detection
        name (str): Character's name
        max_health (int): Maximum health points
        health (int): Current health points
        speed (float): Movement speed in pixels per second
        damage (int): Base damage dealt by attacks
        is_alive (bool): Whether the character is alive
        direction (Direction): Current facing direction
        is_moving (bool): Whether character is currently moving
        is_jumping (bool): Whether character is jumping
        is_falling (bool): Whether character is falling
        y_velocity (float): Vertical velocity for physics
        gravity (float): Gravity strength
        jump_strength (float): Initial jump velocity (negative value)
        is_attacking (bool): Whether character is currently attacking
        attack_combo (int): Current attack combo number (1-3)
        hit_targets (set): Set of targets hit by current attack
        is_defending (bool): Whether character is defending
        using_special (bool): Whether character is using special ability
        attack_timer (float): Timer for attack duration
        attack_duration (float): Duration of each attack in seconds
        critical_chance (float): Probability of critical hit (0.0-1.0)
        critical_damage (float): Damage multiplier for critical hits
        is_invulnerable (bool): Whether character is temporarily invulnerable
        invulnerable_timer (float): Timer for invulnerability duration
        special_cooldown (float): Cooldown time for special ability in seconds
        special_cooldown_remaining (float): Remaining cooldown time
        animation_state (AnimationState): Current animation state
        last_animation_state (AnimationState): Previous animation state
        current_frame_index (int): Current frame in animation sequence
        animation_timer (float): Timer for animation frame progression
        animation_speed (float): Time per animation frame in seconds
    """

    def __init__(self, x, y, width, height, name, max_health, health, speed, damage):
        """
        Initialize a new DungeonCharacter.

        Args:
            x (float): Initial X position
            y (float): Initial Y position
            width (int): Character sprite width
            height (int): Character sprite height
            name (str): Character's name
            max_health (int): Maximum health points
            health (int): Starting health points
            speed (float): Movement speed in pixels per second
            damage (int): Base damage for attacks
        """
        # Position and size
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.hitbox = pygame.Rect(x + width * 0.2, y + height * 0.2, width * 0.6, height * 0.8)

        # Basic attributes
        self.name = name
        self.max_health = max_health
        self.health = health
        self.speed = speed
        self.damage = damage
        self.is_alive = True

        # Movement attributes
        self.direction = Direction.RIGHT
        self.is_moving = False
        self.is_jumping = False
        self.is_falling = True
        self.y_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -12

        # Combat attributes
        self.is_attacking = False
        self.attack_combo = 0
        self.hit_targets = set()
        self.is_defending = False
        self.using_special = False
        self.attack_timer = 0
        self.attack_duration = 0.5  # Half a second per attack
        self.critical_chance = 0.1  # 10% critical hit chance
        self.critical_damage = 1.5  # 50% bonus damage on critical hits

        # Status effects
        self.is_invulnerable = False
        self.invulnerable_timer = 0

        # Special ability
        self.special_cooldown = 5.0  # Default cooldown in seconds
        self.special_cooldown_remaining = 0

        # Animation
        self.animation_state = AnimationState.IDLE
        self.last_animation_state = AnimationState.IDLE
        self.current_frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # Seconds per frame

    def update(self, dt):
        """
        Update character state including physics, combat, and animation.

        This method should be called every frame to update the character's
        position, animation, attack states, and status effects.

        Args:
            dt (float): Delta time in seconds since last update
        """
        # Update position based on physics
        self._apply_gravity(dt)

        # Update hitbox position
        self._update_hitbox()

        # Update attack state
        if self.is_attacking:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_duration:
                self.is_attacking = False
                self.attack_timer = 0
                self.hit_targets.clear()

        # Update invulnerability
        if self.is_invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.is_invulnerable = False

        # Update special cooldown
        if self.special_cooldown_remaining > 0:
            self.special_cooldown_remaining -= dt
            if self.special_cooldown_remaining < 0:
                self.special_cooldown_remaining = 0

        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame_index += 1
            # Reset frame if we've reached the end (assuming 4 frames per animation)
            if self.current_frame_index >= 4:
                self.current_frame_index = 0

                # If this was a one-time animation (like attacking), go back to idle
                if self.animation_state in [AnimationState.ATTACKING_1, AnimationState.ATTACKING_2,
                                            AnimationState.ATTACKING_3, AnimationState.HURT,
                                            AnimationState.SPECIAL_SKILL] and not self.is_attacking:
                    self.animation_state = AnimationState.IDLE

    def _apply_gravity(self, dt):
        """
        Apply gravity physics to the character.

        Updates the character's vertical velocity and position based on gravity.
        Only applies when the character is jumping or falling.

        Args:
            dt (float): Delta time in seconds
        """
        if self.is_falling or self.is_jumping:
            # Apply gravity to y velocity
            self.y_velocity += self.gravity * dt * 60

            # Apply y velocity to position
            self.y += self.y_velocity * dt * 60

            # Check if we're falling
            if self.y_velocity > 0:
                self.is_falling = True
                self.is_jumping = False

    def _update_hitbox(self):
        """
        Update hitbox position based on character position.

        Synchronizes the collision rectangle and hitbox with the character's
        current position. The hitbox is smaller than the full sprite for
        more precise collision detection.
        """
        self.rect.x = self.x
        self.rect.y = self.y
        self.hitbox.x = self.x + self.width * 0.2
        self.hitbox.y = self.y + self.height * 0.2

    def take_damage(self, damage):
        """
        Handle taking damage from an attack.

        Applies damage to the character, handles defense reduction,
        death condition, and invulnerability frames.

        Args:
            damage (int): Amount of damage to take

        Returns:
            bool: True if damage was successfully applied, False if character
                  is invulnerable or already dead
        """
        if not self.is_alive or self.is_invulnerable:
            return False

        # Reduce damage if defending
        if self.is_defending:
            damage = max(1, int(damage * 0.5))  # At least 1 damage

        # Apply damage
        self.health -= damage

        # Check if dead
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.animation_state = AnimationState.DYING
            return True

        # Apply hit reaction
        self.is_invulnerable = True
        self.invulnerable_timer = 0.5  # Half second of invulnerability
        self.animation_state = AnimationState.HURT

        return True

    def heal(self, amount):
        """
        Heal the character by the specified amount.

        Args:
            amount (int): Amount of health to restore

        Returns:
            bool: True if healing was successful, False if character is dead
        """
        if not self.is_alive:
            return False

        self.health = min(self.max_health, self.health + amount)
        return True

    def start_attack(self):
        """
        Initiate an attack sequence.

        Starts the attack animation and sets up the attack combo system.
        The attack combo cycles through three different attack animations (1-2-3).

        Returns:
            bool: True if attack was successfully started, False if character
                  cannot attack (dead, already attacking, or using special)
        """
        if not self.is_alive or self.is_attacking or self.using_special:
            return False

        self.is_attacking = True
        self.attack_timer = 0
        self.hit_targets.clear()

        # Cycle through attack combos (1-2-3)
        self.attack_combo = (self.attack_combo % 3) + 1

        # Set animation state based on combo
        if self.attack_combo == 1:
            self.animation_state = AnimationState.ATTACKING_1
        elif self.attack_combo == 2:
            self.animation_state = AnimationState.ATTACKING_2
        else:  # attack_combo == 3
            self.animation_state = AnimationState.ATTACKING_3

        self.current_frame_index = 0
        return True

    def use_special_ability(self):
        """
        Activate the character's special ability.

        Triggers the special ability if it's not on cooldown and the character
        is not currently attacking or already using a special ability.

        Returns:
            bool: True if special ability was successfully activated, False if
                  character cannot use special (dead, attacking, already using
                  special, or on cooldown)
        """
        if not self.is_alive or self.is_attacking or self.using_special or self.special_cooldown_remaining > 0:
            return False

        self.using_special = True
        self.special_cooldown_remaining = self.special_cooldown
        self.animation_state = AnimationState.SPECIAL_SKILL
        self.current_frame_index = 0
        return True

    def get_attack_hitbox(self):
        """
        Get the collision rectangle for the current attack.

        Creates a hitbox extending from the character in their facing direction
        for detecting attack collisions with other characters.

        Returns:
            pygame.Rect or None: Attack hitbox rectangle if attacking or using
                                special, None otherwise
        """
        if not self.is_attacking and not self.using_special:
            return None

        # Calculate attack hitbox based on direction
        if self.direction == Direction.RIGHT:
            attack_x = self.x + self.width * 0.8
            attack_width = self.width * 0.8
        else:  # LEFT
            attack_x = self.x - self.width * 0.8
            attack_width = self.width * 0.8

        attack_y = self.y + self.height * 0.2
        attack_height = self.height * 0.6

        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)

    def calculate_damage(self, target):
        """
        Calculate the damage to be dealt to a target.

        Computes damage including critical hit chance and multipliers.

        Args:
            target (DungeonCharacter): The target character (unused in base implementation)

        Returns:
            int: Final damage amount including critical hit modifiers
        """
        base_damage = self.damage

        # Critical hit chance
        import random
        if random.random() < self.critical_chance:
            base_damage = int(base_damage * self.critical_damage)

        return base_damage

    def move_towards_target(self, target_x, target_y, dt):
        """
        Move the character towards a target position.

        Handles AI movement towards a specified coordinate, updating position,
        direction, and animation state appropriately.

        Args:
            target_x (float): Target X coordinate
            target_y (float): Target Y coordinate (currently unused)
            dt (float): Delta time in seconds
        """
        if not self.is_alive or self.is_attacking:
            return

        dx = target_x - self.x

        # Determine movement direction
        direction = 1 if dx > 0 else -1

        # Don't move if very close
        if abs(dx) < 10:
            self.is_moving = False
            return

        # Move character
        self.x += direction * self.speed * dt * 60

        # Update direction
        self.direction = Direction.RIGHT if direction > 0 else Direction.LEFT

        # Set moving state
        self.is_moving = True

        # Update animation
        if self.is_moving and self.animation_state not in [AnimationState.ATTACKING_1,
                                                           AnimationState.ATTACKING_2,
                                                           AnimationState.ATTACKING_3,
                                                           AnimationState.HURT,
                                                           AnimationState.DYING,
                                                           AnimationState.SPECIAL_SKILL]:
            self.animation_state = AnimationState.WALKING

    def land(self):
        """
        Handle the character landing after falling or jumping.

        Resets jumping and falling states, clears vertical velocity,
        and updates animation state if necessary.
        """
        self.is_falling = False
        self.is_jumping = False
        self.y_velocity = 0

        if self.animation_state == AnimationState.FALLING:
            self.animation_state = AnimationState.IDLE

    def jump(self):
        """
        Make the character jump.

        Initiates a jump by setting vertical velocity and updating states.
        Only works if the character is not already jumping or falling.

        Returns:
            bool: True if jump was successful, False if character cannot jump
        """
        if not self.is_alive or self.is_jumping or self.is_falling:
            return False

        self.is_jumping = True
        self.is_falling = False
        self.y_velocity = self.jump_strength
        self.animation_state = AnimationState.JUMPING
        return True

    def start_defend(self):
        """
        Start defending to reduce incoming damage.

        Activates defense mode which reduces damage taken by 50%.
        Cannot defend while attacking or using special abilities.

        Returns:
            bool: True if defense was successfully started, False if character
                  cannot defend
        """
        if not self.is_alive or self.is_attacking or self.using_special:
            return False

        self.is_defending = True
        self.animation_state = AnimationState.DEFENDING
        return True

    def stop_defend(self):
        """
        Stop defending and return to normal damage reception.

        Returns:
            bool: True if defense was successfully stopped, False if not defending
        """
        if self.is_defending:
            self.is_defending = False
            if self.animation_state == AnimationState.DEFENDING:
                self.animation_state = AnimationState.IDLE
            return True
        return False

    def handle_input(self, keys, space_pressed):
        """
        Handle input for character control.

        Abstract method to be implemented by subclasses for specific
        character control schemes.

        Args:
            keys: Current key states
            space_pressed (bool): Whether space key was pressed this frame
        """
        pass

    # Getter and setter methods

    def get_is_attacking(self):
        """
        Check if character is currently attacking.

        Returns:
            bool: True if character is in attack state
        """
        return self.is_attacking

    def get_is_using_special(self):
        """
        Check if character is using special ability.

        Returns:
            bool: True if character is using special ability
        """
        return self.using_special

    def get_is_alive(self):
        """
        Check if character is alive.

        Returns:
            bool: True if character is alive
        """
        return self.is_alive

    def get_direction(self):
        """
        Get character's facing direction.

        Returns:
            Direction: Current facing direction (LEFT or RIGHT)
        """
        return self.direction

    def get_x(self):
        """
        Get character's X position.

        Returns:
            float: Current X coordinate
        """
        return self.x

    def get_y(self):
        """
        Get character's Y position.

        Returns:
            float: Current Y coordinate
        """
        return self.y

    def get_damage(self):
        """
        Get character's base damage value.

        Returns:
            int: Base damage dealt by attacks
        """
        return self.damage

    def get_frame_index(self):
        """
        Get current animation frame index.

        Returns:
            int: Index of current animation frame (0-3)
        """
        return self.current_frame_index

    def get_hit_targets(self):
        """
        Get set of targets hit by current attack.

        Returns:
            set: Set of characters hit by the current attack
        """
        return self.hit_targets

    def add_hit_target(self, target):
        """
        Add target to hit targets set.

        Prevents the same target from being hit multiple times
        by the same attack.

        Args:
            target (DungeonCharacter): Character to add to hit targets
        """
        self.hit_targets.add(target)

    def is_attack_complete(self):
        """
        Check if current attack is complete.

        Returns:
            bool: True if not currently attacking
        """
        return not self.is_attacking

    def get_attack_range(self):
        """
        Get attack range distance.

        Default implementation returns character width.
        Subclasses can override for custom attack ranges.

        Returns:
            int: Attack range in pixels
        """
        return self.width  # Default attack range

    def get_max_health(self):
        """
        Get maximum health points.

        Returns:
            int: Maximum health value
        """
        return self.max_health

    def get_health(self):
        """
        Get current health points.

        Returns:
            int: Current health value
        """
        return self.health

    def set_health(self, health):
        """
        Set current health points.

        Clamps the value between 0 and maximum health.

        Args:
            health (int): New health value
        """
        self.health = max(0, min(self.max_health, health))