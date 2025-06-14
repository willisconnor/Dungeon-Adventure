"""
Dungeon Character "abstract" class
@author Connor Willis
@version 0.1
"""
import pygame
from abc import ABC, abstractmethod
from enum import Enum, auto


class Direction(Enum):
    """Enumeration for direction states left and right.

    Attributes:
        LEFT: Entity facing left direction
        RIGHT: Entity facing right direction
    """
    LEFT = auto()
    RIGHT = auto()


class AnimationState(Enum):
    """Enumeration for animation setup and state management.

    Attributes:
        IDLE: Entity is standing still
        WALKING: Entity is walking
        ATTACKING_1: First attack animation
        ATTACKING_2: Second attack animation
        ATTACKING_3: Third attack animation
        SPECIAL_SKILL: Special skill animation
        HURT: Entity taking damage animation
        DYING: Entity death animation
        DEAD: Entity is dead
        RUNNING: Entity running animation
        JUMPING: Entity jumping animation
        FALLING: Entity falling animation
        RUNNING_ATTACK: Attack while running animation
        ARROW: Arrow projectile animation
        FIREBALL: Fireball projectile animation
        DEFENDING: Entity defending animation
        SPECIAL: Special action animation
    """
    IDLE = auto()
    WALKING = auto()
    ATTACKING_1 = auto()
    ATTACKING_2 = auto()
    ATTACKING_3 = auto()
    SPECIAL_SKILL = auto()
    HURT = auto()
    DYING = auto()
    DEAD = auto()
    # new animation states
    RUNNING = auto()
    JUMPING = auto()
    FALLING = auto()
    RUNNING_ATTACK = auto()
    # projectiles
    ARROW = auto()
    FIREBALL = auto()
    DEFENDING = auto()
    SPECIAL = auto()

class DungeonEntity(ABC, pygame.sprite.Sprite):
    """Abstract class for Dungeon Entities, inherits from pygame.sprite.Sprite.

    This class serves as a base for all entities in the dungeon game, providing
    common properties and methods for position, health, animation, and combat.
    All sprites are the same size for PLAYER entities only.
    """

    def __init__(self, x, y, width, height, name, max_health, health, speed, animation_state):
        """Initialize a DungeonEntity.

        Args:
            x (int): Initial x position
            y (int): Initial y position
            width (int): Entity width in pixels
            height (int): Entity height in pixels
            name (str): Name of the entity
            max_health (int): Maximum health points
            health (int): Current health points
            speed (int): Movement speed
            animation_state (AnimationState): Initial animation state
        """
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.health = health
        self.max_health = max_health
        self.speed = speed
        self.direction = Direction.LEFT
        self.animation_state = animation_state.IDLE
        self.last_animation_state = animation_state.IDLE
        self.last_direction = Direction.LEFT
        self.animation_counter = 0
        self.speed = 0
        self.is_alive = True

        # combat properties
        self.damage = 0
        self.critical_chance = 0
        self.critical_damage = 0
        self.attack_range = 0
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.is_invulnerable = False
        self.invulnerable_timer = 0

        # sprite specific properties
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    @abstractmethod
    def update(self, dt):
        """Update entity state each frame.

        Args:
            dt (float): Delta time since last update

        Note:
            This method must be implemented by subclasses.
            Updates hitbox, invulnerability, and syncs rect with position.
        """
        self._update_hitbox()
        self._update_invulnerability(dt)

        # sync rect with position
        self.rect.x = self.x
        self.rect.y = self.y

    @abstractmethod
    def take_damage(self, damage):
        """Handle taking damage from an attack.

        Args:
            damage (int): Amount of damage to take

        Note:
            This method must be implemented by subclasses.
        """
        pass

    def is_hit_by(self, attacker):
        """Check if this entity is hit by another entity.

        Args:
            attacker (DungeonEntity): The attacking entity

        Returns:
            bool: True if hit detected, False otherwise

        Note:
            Returns False if entity is dead or invulnerable.
            Checks collision between attacker's hitbox and this entity's hitbox.
        """
        if not self.is_alive or self.is_invulnerable:
            return False
        # check if attackers hitbox overlaps with entity's hitbox
        return self.hitbox.colliderect(attacker.hitbox)

    def _update_hitbox(self):
        """Update hitbox based on entity position.

        Creates a smaller hitbox positioned at the entity's feet for more
        precise collision detection. Hitbox is 48px wide and 16px tall,
        centered horizontally and positioned at the bottom of the entity.
        """
        hitbox_width = 48  # Slightly smaller width
        hitbox_height = 16  # Much smaller height - just feet level
        # Position hitbox at the very bottom of the character (feet only)
        self.hitbox = pygame.Rect(
            self.x + (self.width - hitbox_width) // 2,  # Center horizontally
            self.y + self.height - hitbox_height,  # Very bottom (feet)
            hitbox_width,
            hitbox_height
        )

    def _update_invulnerability(self, dt):
        """Update invulnerability timer.

        Args:
            dt (float): Delta time since last update

        Decrements the invulnerability timer and disables invulnerability
        when the timer reaches zero or below.
        """
        if self.is_invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.is_invulnerable = False
                self.invulnerable_timer = 0