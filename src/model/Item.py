#Connor willis
from enum import Enum

import pygame

from src.model.DungeonHero import Hero
#Connor Willis

#enum for items
class ItemType(Enum):
    HEALING_POTION = "healing"
    VISION_POTION = "vision"
    PIT = "pit"
    PILLAR_ABSTRACTION = "abstraction"
    PILLAR_ENCAPSULATION = "encapsulation"
    PILLAR_INHERITANCE = "inheritance"
    PILLAR_POLYMORPHISM = "polymorphism"
    ENTRANCE = "entrance"
    EXIT = "exit"
    GOLD = "gold"
    WEAPON = "weapon"


class Item:
    "Collectiblke items"

    def __init__(self, x, y, item_type: ItemType, value: int -0):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.value = value
        self.width = 128
        self.height = 128
        self.collected = False
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def collect(self, hero: Hero):
        "handle item collection"
        if self.item_type == ItemType.HEALING_POTION:
            hero.health = min(hero.max_health, hero.health + self.value)
        elif self.item_type == ItemType.GOLD:
            pass
        elif self.item_type == ItemType.PIT:
            hero.take_damage(self.value)

        self.collected = True