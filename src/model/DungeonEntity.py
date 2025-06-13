"""
Dungeon Character "abstract" class
@author Connor Willis
@version 0.1
"""
import pygame
from abc import ABC, abstractmethod
from enum import Enum, auto


#class for direction states left and right
class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()

#for animation setup later on
class AnimationState(Enum):
    IDLE = auto()
    WALKING = auto()
    ATTACKING_1 = auto()
    ATTACKING_2 = auto()
    ATTACKING_3 = auto()
    SPECIAL_SKILL = auto()
    HURT = auto()
    DYING = auto()
    DEAD = auto()
    #new animation states
    RUNNING = auto()
    JUMPING = auto()
    FALLING = auto()
    RUNNING_ATTACK = auto()
    #projectiles
    ARROW = auto()
    FIREBALL = auto()
    DEFENDING = auto()
    SPECIAL = auto()


"""Abstract class for Dungeon Entities, inherits from pygame.sprite.Sprite"""
#sprites all the same size for PLAYERs only
class DungeonEntity(ABC, pygame.sprite.Sprite):

    def __init__(self, x, y, width, height, name, max_health, health, speed, animation_state):

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

        #combat properties
        self.damage = 0
        self.critical_chance = 0
        self.critical_damage = 0
        self.attack_range = 0
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.is_invulnerable = False
        self.invulnerable_timer = 0

        #sprite specific shindigs
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


    @abstractmethod
    def update(self, dt):
        """Update entity state """
        self._update_hitbox()
        self._update_invulnerability(dt)

        #sync rect with position
        self.rect.x = self.x
        self.rect.y = self.y

    @abstractmethod
    def take_damage(self, damage):
        """handle taking damage"""
        pass


    def is_hit_by(self, attacker):
        """handle being hit by another entity"""
        if not self.is_alive or self.is_invulnerable:
            return False
        #check if attackers hitbox overlaps with entity's hitbox
        return self.hitbox.colliderect(self.hitbox)

    def _update_hitbox(self):
        """update hitbox based on entity position"""
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
        """update invuln timer"""
        if self.is_invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.is_invulnerable = False
                self.invulnerable_timer = 0
