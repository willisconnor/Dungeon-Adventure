#class to handle room generation
from typing import List, Dict, Tuple, Optional
import random
import xml.etree.ElementTree as ET
from enum import Enum
import pygame, csv, os

from src.model.Item import Item
from src.model.Monster import Monster
from src.model.Platform import Platform

class Direction(Enum):
    #for door directions
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class DoorPosition:
    """Represents a doors position and destination in a room"""
    def  __init__(self, x: int, y: int, direction: Direction, dest_room: Tuple[int, int] = None):
        self.x = x
        self.y = y
        self.direction = direction
        self.dest_room = dest_room #(row, col) in grid
        self.rect = pygame.Rect(x, y, 32, 32)

class Room:
    """represents a single room"""
    def __init__(self, grid_pos: Tuple[int, int], tile_data: List[List[int]] = None, tile_width: int = 16, tile_height: int = 16):
        self.grid_pos = grid_pos #row col
        self.tile_data = tile_data
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.width = 1600
        self.height = 600 #2x screen

        if tile_data is None:
            self._generate_room_layout()
        else:
            self.tile_data = tile_data
            self.width = len(tile_data[0]) * tile_width
            self.height = len(tile_data[1]) * tile_height

        self.doors: Dict[Direction, DoorPosition] = {}
        self.has_pillar = False
        self.pillar_collected = False
        self.pillar_rect = None
        self.is_boss_room = False
        self.is_start_room = False

        #Door positions, adjust if  change tilemap. updated for larger size rooms
        self.door_positions = {
            Direction.UP: (self.width // 2- 16, 16),
            Direction.DOWN: (self.width // 2-16, self.height -48),
            Direction.LEFT: (16, self.height // 2-16),
            Direction.RIGHT: (self.width -48, self.height //2 -16)
        }


    def _generate_room_layout(self):
        """generate tile data for a larger room"""
        tiles_wide = self.width //self.tile_width # 50 tiles wide
        tiles_high = self.height //self.tile_height
        #create empty room
        self.tile_data = [[0 for _ in range(tiles_wide)]for _ in range (tiles_high)]

        #calculat the correc ttile ID's for the ones i want
        #tileset is 52 tiles wide 832/16
        tiles_per_row = 52

        #floor tile ids (i want 31-32, 10-13
        floor_tiles = []
        for row in range(10, 14):
            for col in range(31, 33):
                tile_id = (row * tiles_per_row) + col+1
                floor_tiles.append(tile_id)
        #this gives me 604, 656, 657, 708, 709


        #add floor tiles assuming tile id 1 is floor
        floor_y = tiles_high -4 #floor 5 tiles from bot
        for x in range(tiles_wide):
            for y in range(floor_y, tiles_high):
                self.tile_data[y][x] = random.choice([553, 554, 605, 606]) #use appropriate floor tile id


        #add walls on sides from diff part of tileset
        wall_tile = 55
        for y in range(tiles_high):
            self.tile_data[y][0] = wall_tile
            self.tile_data[y][tiles_wide-1] = wall_tile

        #add ceiling
        for x in range(tiles_wide):
            self.tile_data[0][x] = wall_tile #celing

    def add_door(self, direction: Direction, dest_room: Tuple[int, int]):
        """add a door in the specified direction"""
        pos = self.door_positions[direction]
        self.doors[direction] = DoorPosition(pos[0], pos[1], direction, dest_room)

    def add_pillar(self):
        """add a pillar in the room"""
        self.has_pillar = True
        #place pillar in center
        pillar_x = self.width//2 -16
        pillar_y = self.height//2 -16
        self.pillar_rect = pygame.Rect(pillar_x, pillar_y, 32, 32)

    def collect_pillar(self):
        """collect pillar in the room"""
        if self.has_pillar and not self.pillar_collected:
            self.pillar_collected = True
            return True
        return False

    def get_door_at_pos(self, x: int, y:int) -> Optional[DoorPosition]:
        """check if position overlaps with any door"""
        player_rect = pygame.Rect(x, y, 32, 32) #assuming 32x32 player CHANGEEE
        for door in self.doors.values():
            if player_rect.colliderect(door.rect):
                return door
            return None

    def draw(self, screen: pygame.Surface, tileset: pygame.Surface, camera_offset: Tuple[int, int] = (0,0)):
        """draw room tiles"""

        #draw only visible tiles
        start_x = max(0, int(camera_offset[0] // self.tile_width))
        start_y = max(0, int(camera_offset[1] // self.tile_height))
        end_x = min(len(self.tile_data[0]), start_x + (screen.get_width()// self.tile_width) + 2)
        end_y = min(len(self.tile_data), start_y + (screen.get_height() // self.tile_height) + 2)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = self.tile_data[y][x]
                if tile_id >0: #0 is empty tile
                    #calc tile position in set
                    tileset_width = tileset.get_width() // self.tile_width
                    tile_x = ((tile_id -1) % tileset_width) * self.tile_width
                    tile_y = ((tile_id - 1) // tileset_width) * self.tile_height

                    #draw tile
                    screen.blit(tileset, (x * self.tile_width - camera_offset[0],
                                          y * self.tile_height - camera_offset[1]),
                                (tile_x, tile_y, self.tile_width, self.tile_height))

        #draw doors
        for door in self.doors.values():
            pygame.draw.rect(screen, (0, 255,0),
                             (door.x - camera_offset[0], door.y -  camera_offset[1], 32, 32), 2)

        #draw pillar if present and not collecetd
        if self.has_pillar and not self.pillar_collected:
            pygame.draw.circle(screen, (255, 255, 0),
                               self.pillar_rect.centerx - camera_offset[0],
                               self.pillar_rect.centery - camera_offset[1], 16)

class DungeonManager:
    """manages the entire dungeon layout an dprogression"""

    def __init__(self, dungeon_size: Tuple[int, int], tmx_file: str):
        self.grid_width, self.grid_height = dungeon_size
        self.dungeon_grid: List[List[Optional[Room]]] = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_room_pos: Tuple[int, int] = None
        self.tmx_file = tmx_file
        self.pillars_collected = 0
        self.boss_defeated = False

        #load base templaate from TMX
        #self.base_tile_data = self._load_tmx_data(tmx_file)

        #generate dungeon
        self._generate_dungeon()

    def _load_tmx_data(self, tmx_file:str) -> List[List[int]]:
        """load tile data from TMX file"""
        tree = ET.parse(tmx_file)
        root = tree.getroot()

        #get map dimensions
        width = int(root.get('width'))
        height = int(root.get('height'))

        #find the layer data
        layer = root.find('./layer')
        data = layer.find('data')

        #parse CSV data
        csv_data = data.text.strip()
        tiles = [int(x) for x in csv_data.replace('\n', '').split(',') if x]

        #convert to 2d array
        tile_data = []
        for y in range(height):
            row = tiles[y * width:(y+1) * width]
            tile_data.append(row)

        return tile_data

    def _generate_dungeon(self):
        """generate a connected, completable dungeon with rooms"""
        #start in center cuz why not
        start_pos = (self.grid_height // 2, self.grid_width //2)
        self.current_room_pos = start_pos

        #generate starting room WITHOUT tmx data?
        start_room = Room(start_pos, None)
        start_room.is_start_room = True
        self.dungeon_grid[start_pos[0]][start_pos[1]] = start_room

        #generate connected rooms
        rooms_to_process = [start_pos]
        created_rooms = {start_pos}
        room_count = 1
        max_rooms = self.grid_width * self.grid_height //2

        while rooms_to_process and room_count < max_rooms:
            current = rooms_to_process.pop(0)
            current_room = self.dungeon_grid[current[0]][current[1]]

            #try to add 2-4 doors
            num_doors = random.randint(2,4)
            directions = list(Direction)
            random.shuffle(directions)

            doors_added = 0
            for direction in directions:
                if doors_added >= num_doors:
                    break

                #calc neighbor pos
                dr, dc = direction.value
                new_pos = (current[0] + dr, current[1] + dc)

                #check bounds
                if (0 <= new_pos[0] < self.grid_height and 0 <= new_pos[1] < self.grid_width):
                    #create new room or connect to existing rewm
                    new_room = Room(new_pos, None)
                    self.dungeon_grid[new_pos[0]][new_pos[1]] = new_room
                    created_rooms.add(new_pos)
                    rooms_to_process.append(new_pos)
                    room_count += 1

                    #add doorsies
                    current_room.add_door(direction, new_pos)
                    opposite_dir = self._get_opposite_direction(direction)
                    new_room.add_door(opposite_dir, current)
                    doors_added += 1

                elif new_pos in created_rooms and new_pos not in [d.dest_room for d in current_room.doors.values()]:
                    #connect to existing room if not already conencted
                    neighbor_room = self.dungeon_grid[new_pos[0]][new_pos[1]]
                    current_room.add_door(direction, new_pos)
                    opposite_dir = self._get_opposite_direction(direction)
                    neighbor_room.add_door(opposite_dir, current)
                    doors_added += 1

        room_list = list(created_rooms)
        room_list.remove(start_pos) #dont put pillar in start room

        pillar_rooms = random.sample(room_list, min(5, len(room_list)))
        for room_pos in pillar_rooms:
            room = self.dungeon_grid[room_pos[0]][room_pos[1]]
            room.add_pillar()

        #place boss room at furthest point from the start
        furthest_room = self._find_furthest_room(start_pos, created_rooms)
        boss_room = self.dungeon_grid[furthest_room[0]][furthest_room[1]]
        boss_room.is_boss_room = True

    def _get_opposite_direction(self, direction: Direction) -> Direction:
        """get the opposite direction"""
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opposites[direction]

    def _find_furthest_room(self, start: Tuple[int, int], rooms: set) -> Tuple[int, int]:
        """find the furthest room using BFS"""
        visited = {start}
        queue = [(start, 0)]
        furthest = start
        max_dist = 0

        while queue:
            pos, dist = queue.pop(0)
            if dist > max_dist:
                max_dist = dist
                furthest = pos

            room = self.dungeon_grid[pos[0]][pos[1]]
            for door in room.doors.values():
                if door.dest_room not in visited:
                    visited.add(door.dest_room)
                    queue.append((door.dest_room, dist +1))
        return furthest

    def get_current_room(self) -> Room:
        """get the current room"""
        return self.dungeon_grid[self.current_room_pos[0]][self.current_room_pos[1]]

    def try_enter_door(self, player_x: int, player_y: int) -> bool:
        """try to enter a door at player pos"""
        current_room = self.get_current_room()
        door = current_room.get_door_at_pos(player_x, player_y)

        if door:
            #check if boss door is locked
            if door.dest_room:
                dest_room = self.dungeon_grid[door.dest_room[0]][door.dest_room[1]]
                if dest_room.is_boss_room and self.pillars_collected <5:
                    return False #boss door locked

            #move to new room
            self.current_room_pos = door.dest_room
            return True
        return False

    def try_collect_pillar(self, player_x: int, player_y: int) -> bool:
        """try to collect a pillar at player pos"""
        current_room = self.get_current_room()
        if current_room.has_pillar and not current_room.pillar_collected:
            player_rect = pygame.Rect(player_x, player_y, 32, 32) #change this for sprites
            if player_rect.colliderect(current_room.pillar_rect):
                if current_room.collect_pillar():
                    self.pillars_collected += 1
                    return True

        return False

    def is_game_won(self) -> bool:
        """check if game is won"""
        current_room = self.get_current_room()
        return current_room.is_boss_room and self.boss_defeated

    def defeat_boss(self):
        """defeat the boss!!!!!"""
        current_room = self.get_current_room()
        if current_room.is_boss_room:
            self.boss_defeated = True
