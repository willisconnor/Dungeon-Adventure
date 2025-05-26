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


"""Abstract class for Dungeon Entities"""
#sprites all the same size for PLAYERs only
class DungeonEntity(ABC):

    def __init__(self, x, y, width, height, name, max_health, health, speed, animation_state):
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

    @abstractmethod
    def update(self, dt):
        """Update entity state """
        pass

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
        """ Divided by 2 calculations put it near the center of sprite?"""
        hitbox_width = self.width //2 #can change this whenever
        hitbox_height = self.height //2

        self.hitbox = pygame.Rect(self.x//2, self.y//2, hitbox_width, hitbox_height) #maybe tweak this later

    def _update_invulnerability(self, dt):
        """update invuln timer"""
        if self.is_invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.is_invulnerable = False
                self.invulnerable_timer = 0
