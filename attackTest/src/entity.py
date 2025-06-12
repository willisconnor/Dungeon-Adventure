from abc import ABC, abstractmethod
import pygame
from enum import Enum, auto


class Direction(Enum):
    RIGHT = auto()
    LEFT = auto()


class AnimationState(Enum):
    IDLE = auto()
    WALKING = auto()
    ATTACKING_1 = auto()
    ATTACKING_2 = auto()
    ATTACKING_3 = auto()
    DEFENDING = auto()
    HURT = auto()
    DYING = auto()
    DEAD = auto()


class Entity(ABC):
    """Abstract base class for all game entities"""

    def __init__(self, x, y, max_health):
        self.x = x
        self.y = y
        self.max_health = max_health
        self.health = max_health
        self.direction = Direction.RIGHT
        self.animation_state = AnimationState.IDLE
        self.last_animation_state = AnimationState.IDLE
        self.frame_index = 0
        self.animation_counter = 0
        self.speed = 0
        self.is_alive = True

        # Combat properties
        self.damage = 0
        self.attack_range = 0
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.is_invulnerable = False
        self.invulnerable_timer = 0

    @abstractmethod
    def update(self, dt):
        """Update entity state"""
        pass

    @abstractmethod
    def take_damage(self, amount):
        """Handle taking damage"""
        pass

    def is_hit_by(self, attacker):
        """Check if this entity is hit by the attacker"""
        if not self.is_alive or self.is_invulnerable:
            return False

        # Check if attacker's hitbox overlaps with this entity's hitbox
        return attacker.hitbox.colliderect(self.hitbox)

    def _update_hitbox(self):
        """Update the hitbox position based on entity position"""
        hitbox_width = 50  # Adjust these values based on your sprites
        hitbox_height = 80
        self.hitbox = pygame.Rect(
            self.x - hitbox_width // 2,
            self.y - hitbox_height // 2,
            hitbox_width,
            hitbox_height
        )

    def _update_invulnerability(self, dt):
        """Update invulnerability timer"""
        if self.is_invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.is_invulnerable = False
                self.invulnerable_timer = 0