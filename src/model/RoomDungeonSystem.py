#class to handle room generation
'''Connor Willis
6/5/25
'''
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

class FloorRenderer:
    """handles floor tile rendering"""
    def __init__(self, csv_file_path: str, tile_size: int = 16):
        self.__tile_size = tile_size
        self.__floor_pattern = self.__load_floor_pattern(csv_file_path)
        self.__cached_floor_surface = None
        self.__cached_room_size = None

    def __load_floor_pattern(self, csv_file_path: str) -> List[List[int]]:
        try:
            pattern = []
            with open(csv_file_path, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if row:  # Skip empty rows
                        # Convert to integers, handle empty cells as 0
                        tile_row = []
                        for cell in row:
                            try:
                                tile_row.append(int(cell) if cell.strip() else 0)
                            except ValueError:
                                tile_row.append(0)
                        pattern.append(tile_row)

            if not pattern:
                # Fallback pattern if CSV is empty or invalid
                return [[1, 2], [3, 4]]

            return pattern
        except FileNotFoundError:
            print(f"Warning: Floor pattern file {csv_file_path} not found. Using default pattern.")
            # Return a simple 2x2 pattern as fallback
            return [[1, 2], [3, 4]]

    def generate_floor_surface(self, room_width: int, room_height: int, tileset: pygame.Surface) -> pygame.Surface:
        #check if we can use a cached surface
        if (self.__cached_floor_surface and
                self.__cached_room_size == (room_width, room_height)):
            return self.__cached_floor_surface

        # Create new floor surface
        floor_surface = pygame.Surface((room_width, room_height))

        # Calculate how many pattern repetitions we need
        pattern_width = len(self.__floor_pattern[0]) * self.__tile_size
        pattern_height = len(self.__floor_pattern) * self.__tile_size

        tiles_x = (room_width // pattern_width) + 2
        tiles_y = (room_height // pattern_height) + 2

        # Tile the pattern across the room
        for pattern_x in range(tiles_x):
            for pattern_y in range(tiles_y):
                self.__draw_pattern_at_position(
                    floor_surface,
                    tileset,
                    pattern_x * pattern_width,
                    pattern_y * pattern_height
                )

        # Cache the result
        self.__cached_floor_surface = floor_surface
        self.__cached_room_size = (room_width, room_height)

        return floor_surface

    def __draw_pattern_at_position(self, surface: pygame.Surface, tileset: pygame.Surface, x: int, y: int):
        #draw floor pattern at a specific position
        for row_idx, row in enumerate(self.__floor_pattern):
            for col_idx, tile_id in enumerate(row):
                if tile_id > 0:
                    tile_x = col_idx * self.__tile_size
                    tile_y = row_idx * self.__tile_size
                    #only draw if within surface bounds
                    if (tile_x < surface.get_width() and tile_y < surface.get_height()):
                        self.__draw_tile(surface, tileset, tile_id, tile_x, tile_y)

    def __draw_tile(self, surface: pygame.Surface, tileset: pygame.Surface, tile_id: int, x: int, y: int):
        if tile_id <- 0:
            return

        tileset_width_in_tiles = tileset.get_width() // self.__tile_size
        tile_x_in_tileset = ((tile_id - 1) % tileset_width_in_tiles) * self.__tile_size
        tile_y_in_tileset = ((tile_id - 1) // tileset_width_in_tiles) * self.__tile_size

        #extract tile from tileset
        tile_rect = pygame.Rect(tile_x_in_tileset, tile_y_in_tileset, self.__tile_size, self.__tile_size)

        #draw tile to surface
        try:
            surface.blit(tileset, (x, y), tile_rect)
        except:
            print(f"Error drawing tile {tile_id} at position {x}, {y}")

class Door:
    """Represents a door"""

    def __init__(self, x: int, y: int, direction: Direction, dest_room: Tuple[int, int], width: int = 64,
                 height: int = 32):
        """
        Initialize a door

        Args:
            x: X position of door
            y: Y position of door
            direction: Direction the door faces
            dest_room: Grid position of destination room
            width: Width of door
            height: Height of door
        """
        self.__x = x
        self.__y = y
        self.__direction = direction
        self.__dest_room = dest_room
        self.__width = width
        self.__height = height
        self.__rect = pygame.Rect(x, y, width, height)
        self.__is_locked = False

    @property
    def x(self) -> int:
        """Get door X position"""
        return self.__x

    @property
    def y(self) -> int:
        """Get door Y position"""
        return self.__y

    @property
    def direction(self) -> Direction:
        """Get door direction"""
        return self.__direction

    @property
    def dest_room(self) -> Tuple[int, int]:
        """Get destination room coordinates"""
        return self.__dest_room

    @property
    def rect(self) -> pygame.Rect:
        """Get door collision rectangle"""
        return self.__rect.copy()

    @property
    def is_locked(self) -> bool:
        """Check if door is locked"""
        return self.__is_locked

    def lock(self):
        """Lock the door"""
        self.__is_locked = True

    def unlock(self):
        """Unlock the door"""
        self.__is_locked = False

    def check_collision(self, entity_rect: pygame.Rect) -> bool:
        """
        Check if an entity collides with this door

        Args:
            entity_rect: Rectangle representing entity position

        Returns:
            True if collision detected
        """
        return self.__rect.colliderect(entity_rect)

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Draw the door

        Args:
            surface: Surface to draw on
            camera_offset: Camera offset for scrolling
        """
        draw_x = self.__x - camera_offset[0]
        draw_y = self.__y - camera_offset[1]

        # Choose color based on lock status
        color = (100, 100, 100) if self.__is_locked else (139, 69, 19)  # Gray if locked, brown if unlocked

        # Draw door
        pygame.draw.rect(surface, color, (draw_x, draw_y, self.__width, self.__height))

        # Draw door frame
        pygame.draw.rect(surface, (160, 82, 45), (draw_x, draw_y, self.__width, self.__height), 3)

class Room:
    """represents a single room"""
    def __init__(self, grid_pos: Tuple[int, int], width: int = 1600, height: int = 600, tile_size: int = 16):
        self.__grid_pos = grid_pos
        self.__width = width
        self.__height = height
        self.__tile_size = tile_size
        self.__doors: Dict[Direction, Door] = {}
        self.__floor_surface = None
        self.__background_surface = None

        # Room properties
        self.__has_pillar = False
        self.__pillar_collected = False
        self.__pillar_rect = None
        self.__is_boss_room = False
        self.__is_start_room = False

        # Calculate floor Y position (bottom 20% of room)
        self.__floor_y = int(height * 0.8)
        self.__floor_height = height - self.__floor_y

    @property
    def grid_pos(self) -> Tuple[int, int]:
        """Get room grid position"""
        return self.__grid_pos

    @property
    def width(self) -> int:
        """Get room width"""
        return self.__width

    @property
    def height(self) -> int:
        """Get room height"""
        return self.__height

    @property
    def floor_y(self) -> int:
        """Get Y position where floor starts"""
        return self.__floor_y

    @property
    def doors(self) -> Dict[Direction, Door]:
        """Get copy of doors dictionary"""
        return self.__doors.copy()

    def set_as_boss_room(self):
        """Mark this room as boss room"""
        self.__is_boss_room = True

    def set_as_start_room(self):
        """Mark this room as start room"""
        self.__is_start_room = True

    def is_boss_room(self) -> bool:
        """Check if this is a boss room"""
        return self.__is_boss_room

    def is_start_room(self) -> bool:
        """Check if this is the start room"""
        return self.__is_start_room

    def add_door(self, direction: Direction, dest_room: Tuple[int, int]):
        """
        Add a door to the room

        Args:
            direction: Direction the door faces
            dest_room: Destination room grid coordinates
        """
        door_x, door_y = self.__calculate_door_position(direction)
        door = Door(door_x, door_y, direction, dest_room)
        self.__doors[direction] = door

    def __calculate_door_position(self, direction: Direction) -> Tuple[int, int]:
        """
        Calculate door position based on direction

        Args:
            direction: Direction the door should face

        Returns:
            (x, y) position for the door
        """
        door_width = 64
        door_height = 32

        if direction == Direction.LEFT:
            return (0, self.__floor_y - door_height)
        elif direction == Direction.RIGHT:
            return (self.__width - door_width, self.__floor_y - door_height)
        else:
            # Fallback to center for unsupported directions
            return (self.__width // 2 - door_width // 2, self.__floor_y - door_height)

    def generate_floor(self, floor_renderer: FloorRenderer, tileset: pygame.Surface):
        """
        Generate floor surface for this room

        Args:
            floor_renderer: FloorRenderer instance
            tileset: Tileset image
        """
        self.__floor_surface = floor_renderer.generate_floor_surface(
            self.__width, self.__floor_height, tileset
        )

    def generate_background(self, background_color: Tuple[int, int, int] = (40, 40, 60)):
        """
        Generate background surface for this room

        Args:
            background_color: RGB color for background
        """
        self.__background_surface = pygame.Surface((self.__width, self.__height))
        self.__background_surface.fill(background_color)

        # Add some simple wall decoration
        wall_color = (60, 60, 80)

        # Left wall
        pygame.draw.rect(self.__background_surface, wall_color, (0, 0, 32, self.__floor_y))
        # Right wall
        pygame.draw.rect(self.__background_surface, wall_color, (self.__width - 32, 0, 32, self.__floor_y))
        # Top wall
        pygame.draw.rect(self.__background_surface, wall_color, (0, 0, self.__width, 32))

    def get_door_at_position(self, x: int, y: int, entity_width: int = 32, entity_height: int = 32) -> Optional[Door]:
        """
        Check if there's a door at the given position

        Args:
            x: X position to check
            y: Y position to check
            entity_width: Width of entity checking
            entity_height: Height of entity checking

        Returns:
            Door object if found, None otherwise
        """
        entity_rect = pygame.Rect(x, y, entity_width, entity_height)

        for door in self.__doors.values():
            if door.check_collision(entity_rect):
                return door

        return None

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Draw the room including background, floor, and doors

        Args:
            surface: Surface to draw on
            camera_offset: Camera offset for scrolling
        """
        # Draw background
        if self.__background_surface:
            surface.blit(self.__background_surface, (-camera_offset[0], -camera_offset[1]))

        # Draw floor
        if self.__floor_surface:
            floor_draw_y = self.__floor_y - camera_offset[1]
            surface.blit(self.__floor_surface, (-camera_offset[0], floor_draw_y))

        # Draw doors
        for door in self.__doors.values():
            door.draw(surface, camera_offset)

class DungeonManager:
    """manages the entire dungeon layout an dprogression"""

    def __init__(self, dungeon_size: Tuple[int, int], floor_csv_path: str, tileset_path: str):
        self.__grid_width, self.__grid_height = dungeon_size
        self.__dungeon_grid: List[List[Optional[Room]]] = [[None for _ in range(self.__grid_width)] for _ in range(self.__grid_height)]
        self.__current_room_pos: Tuple[int, int] = None

        #initialize rendered and assets
        self.__floor_renderer = FloorRenderer(floor_csv_path)
        self.__tileset = self.__load_tileset(tileset_path)

        self.pillars_collected = 0
        self.boss_defeated = False

        #load base templaate from TMX
        #self.base_tile_data = self._load_tmx_data(tmx_file)

        #generate dungeon
        self.__generate_dungeon()

    def __load_tileset(self, tileset_path: str) -> pygame.Surface:
        """
        Load tileset image

        Args:
            tileset_path: Path to tileset image

        Returns:
            Loaded tileset surface
        """
        try:
            return pygame.image.load(tileset_path).convert_alpha()
        except pygame.error:
            print(f"Warning: Could not load tileset from {tileset_path}")
            # Create a simple fallback tileset
            fallback = pygame.Surface((128, 128))
            fallback.fill((100, 100, 100))
            return fallback

    def __generate_dungeon(self):
        """Generate the dungeon layout"""
        # Start in center
        start_pos = (self.__grid_height // 2, self.__grid_width // 2)
        self.__current_room_pos = start_pos

        # Create start room
        start_room = Room(start_pos)
        start_room.set_as_start_room()
        self.__initialize_room(start_room)
        self.__dungeon_grid[start_pos[0]][start_pos[1]] = start_room

        # Generate additional rooms
        self.__generate_connected_rooms(start_pos)

    def __generate_connected_rooms(self, start_pos: Tuple[int, int]):
        """Generate connected rooms from start position"""
        rooms_to_process = [start_pos]
        created_rooms = {start_pos}
        room_count = 1
        max_rooms = min(8, self.__grid_width * self.__grid_height // 2)

        while rooms_to_process and room_count < max_rooms:
            current = rooms_to_process.pop(0)
            current_room = self.__dungeon_grid[current[0]][current[1]]

            # Try to add doors (left and right only)
            directions = [Direction.LEFT, Direction.RIGHT]
            random.shuffle(directions)

            for direction in directions:
                if random.random() < 0.7:  # 70% chance to add door
                    new_pos = self.__get_neighbor_position(current, direction)

                    if self.__is_valid_position(new_pos) and new_pos not in created_rooms:
                        # Create new room
                        new_room = Room(new_pos)
                        self.__initialize_room(new_room)
                        self.__dungeon_grid[new_pos[0]][new_pos[1]] = new_room

                        # Add doors
                        current_room.add_door(direction, new_pos)
                        opposite_dir = self.__get_opposite_direction(direction)
                        new_room.add_door(opposite_dir, current)

                        created_rooms.add(new_pos)
                        rooms_to_process.append(new_pos)
                        room_count += 1

        # Set boss room
        if len(created_rooms) > 1:
            room_list = list(created_rooms)
            room_list.remove(start_pos)
            boss_pos = random.choice(room_list)
            self.__dungeon_grid[boss_pos[0]][boss_pos[1]].set_as_boss_room()

    def __initialize_room(self, room: Room):
        """Initialize room with floor and background"""
        room.generate_background()
        room.generate_floor(self.__floor_renderer, self.__tileset)

    def __get_neighbor_position(self, pos: Tuple[int, int], direction: Direction) -> Tuple[int, int]:
        """Get neighbor position in given direction"""
        dr, dc = direction.value
        return (pos[0] + dr, pos[1] + dc)

    def __is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """Check if position is within grid bounds"""
        return (0 <= pos[0] < self.__grid_height and 0 <= pos[1] < self.__grid_width)

    def __get_opposite_direction(self, direction: Direction) -> Direction:
        """Get opposite direction"""
        opposites = {
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return opposites[direction]

    def get_current_room(self) -> Room:
        """Get the current room"""
        if self.__current_room_pos:
            return self.__dungeon_grid[self.__current_room_pos[0]][self.__current_room_pos[1]]
        return None

    def try_enter_door(self, player_x: int, player_y: int) -> bool:
        """
        Try to enter a door at player position

        Args:
            player_x: Player X position
            player_y: Player Y position

        Returns:
            True if successfully entered door
        """
        current_room = self.get_current_room()
        if not current_room:
            return False

        door = current_room.get_door_at_position(player_x, player_y)
        if door and not door.is_locked:
            self.__current_room_pos = door.dest_room
            return True

        return False

    def get_current_room_position(self) -> Tuple[int, int]:
        """Get current room grid position"""
        return self.__current_room_pos

    def get_dungeon_width(self):
        return self.__grid_width

    def get_dungeon_height(self):
        return self.__grid_height