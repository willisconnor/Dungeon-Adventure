#class to handle room generation
from typing import List

import pygame, csv, os

from src.model.Item import Item
from src.model.Monster import Monster
from src.model.Platform import Platform


class Room:
    def __init__(self, room_id: int, width: int = screen_width * 2, height: int = SCREEN_HEIGHT):
        self.room_id = room_id
        self.width = width
        self.height = height
        self.platforms: List[Platform] = []
        self.items: List[Item] = []
        self.enemies = List[Monster] = [] #append Boss, Skeleton, etc
        self.background_color = pygame.Color('black')
        self.visited = False


    def _generate_room_content(self):
        #first, we need to generate floor platforms
        #or platform
        pass
