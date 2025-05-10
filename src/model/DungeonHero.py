from DungeonCharacter import DungeonCharacter
from DungeonEntity import AnimationState, Direction
import pygame
import sqlite3

class Hero(DungeonCharacter):
    """Base Hero class that all hero types will inherit from"""

    def __init__(self, x, y, hero_type = "default"):
        #We'll load specific stats from database
        self.hero_type = hero_type

        #Load hero stats from database
