from src.model.Monster import Monster
import random
import pygame


# Define animation states to match Skeleton
class AnimationState:
    IDLE = "idle"
    WALKING = "walking"
    ATTACKING = "attacking"
    HURT = "hurt"
    DYING = "dying"
    DEAD = "dead"


class Direction:
    LEFT = "left"
    RIGHT = "right"


class Ogre(Monster):
    """Ogre monster - a powerful boss enemy"""

    def __init__(self, x=0, y=0):
        super().__init__("Grar the Ogre", 200, 0, is_boss=True)

        # Basic stats
        self.__max_health = 200
        self.__health = 200
        self.__is_alive = True
        self.__is_invulnerable = False
        self.__invulnerable_timer = 0
        self.__attack_cooldown = 0
        self.__attack_cooldown_max = 2.0  # 2 seconds between attacks (slower than skeleton)
        self.__damage = 45
        self.__attack_speed = 2
        self.__movement_speed = 15.0  # Slower than skeleton
        self.__special_skill = "Stun"
        self.__attack_range = 100  # Longer range than skeleton
        self.__target = None
        self.__animation_state = AnimationState.IDLE
        self.__direction = Direction.RIGHT

        # Set movement speed using parent class method
        self.set_movement_speed(self.__movement_speed)
        self.set_attack_range(self.__attack_range)
        self.set_attack_cooldown(self.__attack_cooldown_max)

        # Set combat stats using parent class setters
        self.set_chance_to_hit(0.6)
        self.set_damage_range(30, 60)

        # Set healing stats using parent class setters
        self.set_heal_chance(0.1)
        self.set_heal_range(30, 60)

        # Set up sprite image and rect
        self.image = pygame.Surface((64, 80))  # Larger than skeleton
        self.image.fill((139, 69, 19))  # Brown color for ogre
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Set up hitbox for collision detection
        self.hitbox = pygame.Rect(x + 8, y + 16, 48, 64)  # Larger hitbox than skeleton

    @property
    def is_alive(self):
        """Check if ogre is alive"""
        return self.__is_alive

    def get_enemy_type(self):
        """Get the enemy type"""
        return "ogre"

    def get_animation_state(self):
        """Get current animation state"""
        return self.__animation_state

    def get_direction(self):
        """Get current facing direction"""
        return self.__direction

    def get_max_health(self):
        """Get maximum health"""
        return self.__max_health

    def get_health(self):
        """Get current health"""
        return self.__health

    def get_damage(self):
        """Get attack damage"""
        return self.__damage

    def get_attack_range(self):
        """Get attack range"""
        return self.__attack_range

    def get_x(self):
        """Get x position"""
        return self.rect.x

    def get_y(self):
        """Get y position"""
        return self.rect.y

    def is_invulnerable(self):
        """Check if ogre is currently invulnerable"""
        return self.__is_invulnerable

    def is_attacking(self):
        """Check if ogre is attacking"""
        return self.__animation_state == AnimationState.ATTACKING

    def take_damage(self, damage):
        """Take damage, return True if enemy died, False otherwise"""
        # Don't take damage if already dead or invulnerable
        if not self.__is_alive or self.__is_invulnerable:
            return False

        if damage <= 0:
            return False

        # Apply damage
        self.__health -= damage
        print(f"{self.get_name()} takes {damage} damage! HP: {self.__health}/{self.__max_health}")

        # Check if dead
        if self.__health <= 0:
            self.__health = 0
            self.__is_alive = False
            self.__animation_state = AnimationState.DYING
            print(f"{self.get_name()} has been defeated!")
            return True  # Enemy died
        else:
            # Set invulnerability briefly
            self.__is_invulnerable = True
            self.__invulnerable_timer = 0.8  # Longer invulnerability for boss
            self.__animation_state = AnimationState.HURT
            return False  # Enemy took damage but didn't die

    def get_name(self):
        """Get the monster's name"""
        return self._name if hasattr(self, '_name') else "Grar the Ogre"

    def attack(self, target):
        """Attack the target"""
        # Don't attack if on cooldown or dead
        if self.__attack_cooldown > 0 or not self.__is_alive:
            return False

        # Set attacking state
        self.__animation_state = AnimationState.ATTACKING
        print(f"{self.get_name()} uses {self.__special_skill}!")

        # Calculate if hit connects
        if random.random() <= self.get_chance_to_hit():
            min_damage, max_damage = self.get_damage_range()
            damage = random.randint(min_damage, max_damage)

            # Apply damage to target if it has take_damage method
            if hasattr(target, 'take_damage'):
                target.take_damage(damage)
                print(f"{self.get_name()} hits for {damage} damage!")
            else:
                print(f"{self.get_name()} attacks but target cannot take damage!")

            # Set attack cooldown
            self.__attack_cooldown = self.__attack_cooldown_max
            return True
        else:
            print(f"{self.get_name()} missed!")
            # Attack missed
            self.__attack_cooldown = self.__attack_cooldown_max / 2  # Shorter cooldown on miss
            return False

    def set_target(self, target):
        """Set the target for this enemy to follow/attack"""
        self.__target = target

    def get_target(self):
        """Get the current target"""
        return self.__target

    def move_towards_target(self, target_x, target_y, dt):
        """Move the ogre towards a target position"""
        # Don't move if dead, attacking or hurt
        if not self.__is_alive or self.__animation_state in [AnimationState.ATTACKING, AnimationState.HURT,
                                                             AnimationState.DYING]:
            return

        # Calculate distance to target
        dx = target_x - self.rect.centerx
        distance = abs(dx)

        # Set direction based on target position
        if dx > 0:
            self.__direction = Direction.RIGHT
        else:
            self.__direction = Direction.LEFT

        # Don't move if already in attack range
        if distance <= self.__attack_range:
            self.__animation_state = AnimationState.IDLE
            return

        # Set walking animation
        self.__animation_state = AnimationState.WALKING

        # Move towards target (horizontal only)
        move_distance = self.get_movement_speed() * dt
        move_x = min(move_distance, distance) * (1 if dx > 0 else -1)

        # Update position
        self.rect.x += move_x
        # Update hitbox position
        self._update_hitbox()

    def _update_hitbox(self):
        """Update the hitbox position to match the sprite"""
        self.hitbox.x = self.rect.x + 8  # Adjust as needed for ogre
        self.hitbox.y = self.rect.y + 16  # Adjust as needed for ogre

    def _update_attack_cooldown(self, dt):
        """Update attack cooldown timer"""
        if self.__attack_cooldown > 0:
            self.__attack_cooldown -= dt

    def _update_invulnerability(self, dt):
        """Update invulnerability timer"""
        if self.__is_invulnerable:
            self.__invulnerable_timer -= dt
            if self.__invulnerable_timer <= 0:
                self.__is_invulnerable = False
                # Return to idle if was hurt
                if self.__animation_state == AnimationState.HURT:
                    self.__animation_state = AnimationState.IDLE

    def update(self, dt=0):
        """Update method called by pygame sprite groups"""
        # Don't update if dead
        if not self.__is_alive and self.__animation_state == AnimationState.DEAD:
            return

        # Update timers
        self._update_attack_cooldown(dt)
        self._update_invulnerability(dt)

        # Handle death animation transition
        if self.__animation_state == AnimationState.DYING:
            # In a real implementation, you'd wait for death animation to finish
            # For now, just transition to DEAD state immediately
            self.__animation_state = AnimationState.DEAD
            return

        # If we have a target, move towards it and try to attack
        if self.__target and self.__is_alive:
            if hasattr(self.__target, 'rect'):
                target_x = self.__target.rect.centerx
                target_y = self.__target.rect.centery
            else:
                # Fallback if target doesn't have a rect
                target_x = getattr(self.__target, 'x', 0)
                target_y = getattr(self.__target, 'y', 0)

            # Check if in attack range
            distance = ((target_x - self.rect.centerx) ** 2 + (target_y - self.rect.centery) ** 2) ** 0.5

            if distance <= self.__attack_range and self.__attack_cooldown <= 0:
                # In range and cooldown ready - attack!
                self.attack(self.__target)
            else:
                # Not in range or on cooldown - move towards target
                self.move_towards_target(target_x, target_y, dt)

        # Call parent class update
        super().update(dt)

    def __str__(self):
        """String representation of the ogre"""
        status = "DEAD" if not self.__is_alive else f"HP: {self.__health}/{self.__max_health}"
        ogre_specific = (
                f" | Special Skill: {self.__special_skill}" +
                f" | Attack Speed: {self.__attack_speed}" +
                f" | Movement Speed: {self.__movement_speed}"
        )
        return f"{self.get_name()} ({status}, DMG: {self.__damage})" + ogre_specific

    # Keep your existing getter/setter methods for backward compatibility
    def get_attack_speed(self):
        """Get the ogre's attack speed"""
        return self.__attack_speed

    def set_attack_speed(self, speed):
        """Set the ogre's attack speed"""
        self.__attack_speed = speed

    def get_movement_speed(self):
        """Get the ogre's movement speed"""
        return self.__movement_speed

    def set_movement_speed(self, speed):
        """Set the ogre's movement speed"""
        self.__movement_speed = speed

    def get_special_skill(self):
        """Get the ogre's special skill name"""
        return self.__special_skill

    def set_special_skill(self, skill):
        """Set the ogre's special skill name"""
        self.__special_skill = skill

    # Legacy method support for backward compatibility
    def setSpecialSkill(self, skill):
        """Legacy method for setting special skill"""
        self.set_special_skill(skill)

    def setMovementSpeed(self, speed):
        """Legacy method for setting movement speed"""
        self.set_movement_speed(speed)

    # Properties for easier access while maintaining encapsulation
    @property
    def attack_speed(self):
        return self.__attack_speed

    @attack_speed.setter
    def attack_speed(self, value):
        self.__attack_speed = value

    @property
    def movement_speed(self):
        return self.__movement_speed

    @movement_speed.setter
    def movement_speed(self, value):
        self.__movement_speed = value

    @property
    def specialSkill(self):
        return self.__special_skill

    @specialSkill.setter
    def specialSkill(self, value):
        self.__special_skill = value

    def is_visible_on_screen(self, camera_x, camera_y, screen_width, screen_height):
        """Check if the ogre is visible on screen with current camera position"""
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        return (screen_x + self.rect.width > 0 and screen_x < screen_width and
                screen_y + self.rect.height > 0 and screen_y < screen_height)
