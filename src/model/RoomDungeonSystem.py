# class to handle room generation
'''Connor Willis
6/5/25
Updated with Pillar support and improved dungeon generation
'''
from typing import List, Dict, Tuple, Optional
import random
import xml.etree.ElementTree as ET
from enum import Enum
import pygame, csv, os

from src.model.Item import Item
from src.model.Monster import Monster
from src.model.Platform import Platform
# Add this import at the top of RoomDungeonSystem.py
from src.model.Pillar import Pillar, PillarType, PillarManager
from src.model.Potion import Potion, PotionType, PotionManager
from src.model.EnemySpawnManager import EnemySpawnManager


class DoorType(Enum):
    # Doors based through interaction method
    WALK_THROUGH = "walk_through"
    INTERACTIVE = "interactive"


class Direction(Enum):
    # for door directions
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class DungeonTemplate(Enum):
    """Predefined dungeon layouts for controlled generation"""
    CROSS = "cross"
    SQUARE = "square"
    DEMO = "demo"  # Easy layout for demonstrations
    FULL = "full"  # All rooms filled


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
        # check if we can use a cached surface
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
        # draw floor pattern at a specific position
        for row_idx, row in enumerate(self.__floor_pattern):
            for col_idx, tile_id in enumerate(row):
                if tile_id > 0:
                    tile_x = col_idx * self.__tile_size
                    tile_y = row_idx * self.__tile_size
                    # only draw if within surface bounds
                    if (tile_x < surface.get_width() and tile_y < surface.get_height()):
                        self.__draw_tile(surface, tileset, tile_id, tile_x, tile_y)

    def __draw_tile(self, surface: pygame.Surface, tileset: pygame.Surface, tile_id: int, x: int, y: int):
        if tile_id <= 0:
            return

        tileset_width_in_tiles = tileset.get_width() // self.__tile_size
        tile_x_in_tileset = ((tile_id - 1) % tileset_width_in_tiles) * self.__tile_size
        tile_y_in_tileset = ((tile_id - 1) // tileset_width_in_tiles) * self.__tile_size

        # extract tile from tileset
        tile_rect = pygame.Rect(tile_x_in_tileset, tile_y_in_tileset, self.__tile_size, self.__tile_size)

        # draw tile to surface
        try:
            surface.blit(tileset, (x, y), tile_rect)
        except:
            print(f"Error drawing tile {tile_id} at position {x}, {y}")


class DoorInteractionState:
    """Encapsulates door interaction state and UI management"""

    def __init__(self):
        self.__player_nearby = False
        self.__show_prompt = False
        self.__prompt_font = pygame.font.Font(None, 20)
        self.__prompt_text = ""
        self.__prompt_surface = None

    def set_player_nearby(self, nearby: bool, prompt_text: str = ""):
        """Update player proximity and prompt text"""
        self.__player_nearby = nearby
        self.__show_prompt = nearby
        if nearby and prompt_text:
            self.__prompt_text = prompt_text
            self.__prompt_surface = self.__prompt_font.render(
                prompt_text, True, (255, 255, 255), (0, 0, 0)
            )
        else:
            self.__prompt_surface = None

    def is_player_nearby(self) -> bool:
        """Check if player is nearby"""
        return self.__player_nearby

    def should_show_prompt(self) -> bool:
        """Check if interaction prompt should be shown"""
        return self.__show_prompt

    def get_prompt_surface(self) -> Optional[pygame.Surface]:
        """Get the rendered prompt surface"""
        return self.__prompt_surface


class Door:
    """Represents a door"""

    def __init__(self, direction: Direction, dest_room: Tuple[int, int], room_width: int, room_height: int,
                 floor_y: int):
        """
        Initialize a door with calculated position based on room dimensions

        Args:
            direction: Direction the door faces
            dest_room: Grid position of destination room
            room_width: Width of the room containing this door
            room_height: Height of the room containing this door
            floor_y: Y position of the floor
        """
        self.__direction = direction
        self.__dest_room = dest_room
        self.__width = 64
        self.__height = 96
        self.__is_locked = False
        self.__lock_message = ""

        # determine door type based on direction
        self.__door_type = (DoorType.INTERACTIVE
                            if direction in [Direction.UP, Direction.DOWN]
                            else DoorType.WALK_THROUGH)

        # Calculate door position based on direction and room dimensions
        self.__x, self.__y = self.__calculate_door_position(direction, room_width, room_height, floor_y)
        self.__rect = pygame.Rect(self.__x, self.__y, self.__width, self.__height)

        # Interaction state management
        self.__interaction_state = DoorInteractionState()

        # Create interaction prompt text
        self.__interaction_prompt = self.__create_interaction_prompt()

    def __calculate_door_position(self, direction: Direction, room_width: int, room_height: int, floor_y: int) -> Tuple[
        int, int]:
        """
        Calculate door position - UP/DOWN doors separated and all at floor level

        Args:
            direction: Direction the door faces
            room_width: Width of the room
            room_height: Height of the room
            floor_y: Y position where floor starts

        Returns:
            (x, y) position for the door
        """
        # All doors positioned at floor level (floor_y - height)
        door_y = floor_y - self.__height

        if direction == Direction.LEFT:
            return (0, door_y)
        elif direction == Direction.RIGHT:
            return (room_width - self.__width, door_y)
        elif direction == Direction.UP:
            # Position UP door to the left of center
            separation_offset = 80  # Distance from center
            return (room_width // 2 - separation_offset - self.__width // 2, door_y)
        elif direction == Direction.DOWN:
            # Position DOWN door to the right of center
            separation_offset = 80  # Distance from center
            return (room_width // 2 + separation_offset - self.__width // 2, door_y)
        else:
            # Default fallback
            return (room_width // 2 - self.__width // 2, door_y)

    def __create_interaction_prompt(self) -> str:
        """Create appropriate interaction prompt text"""
        if self.__door_type == DoorType.INTERACTIVE:
            direction_text = "UP" if self.__direction == Direction.UP else "DOWN"
            return f"Press E to go {direction_text}"
        return ""

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

    @property
    def door_type(self) -> DoorType:
        """Get door interaction type"""
        return self.__door_type

    def lock(self, message: str = ""):
        """Lock the door with optional message"""
        self.__is_locked = True
        self.__lock_message = message

    def unlock(self):
        """Unlock the door"""
        self.__is_locked = False
        self.__lock_message = ""

    def get_lock_message(self) -> str:
        """Get lock message"""
        return self.__lock_message

    def check_collision(self, entity_rect: pygame.Rect) -> bool:
        """
        Check if an entity collides with this door

        Args:
            entity_rect: Rectangle representing entity position

        Returns:
            True if collision detected
        """
        return self.__rect.colliderect(entity_rect)

    def update_player_proximity(self, player_x: int, player_y: int, player_width: int = 32, player_height: int = 32):
        """
        Update door's awareness of player proximity for interactive doors

        Args:
            player_x: Player X position
            player_y: Player Y position
            player_width: Player width
            player_height: Player height
        """
        if self.__door_type == DoorType.INTERACTIVE:
            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            is_nearby = self.check_collision(player_rect)

            if is_nearby and self.__is_locked and self.__lock_message:
                prompt_text = self.__lock_message
            elif is_nearby and not self.__is_locked:
                prompt_text = self.__interaction_prompt
            else:
                prompt_text = ""

            self.__interaction_state.set_player_nearby(is_nearby, prompt_text)
        else:
            # Walk-through doors don't need proximity tracking
            self.__interaction_state.set_player_nearby(False)

    def can_enter_automatically(self, player_rect: pygame.Rect) -> bool:
        """Check if player can enter this door automatically (walk-through doors)"""
        return (self.__door_type == DoorType.WALK_THROUGH and
                not self.__is_locked and
                self.check_collision(player_rect))

    def can_enter_with_interaction(self, player_rect: pygame.Rect, interaction_key_pressed: bool) -> bool:
        """Check if player can enter this door with key press (interactive doors)"""
        return (self.__door_type == DoorType.INTERACTIVE and
                not self.__is_locked and
                self.check_collision(player_rect) and
                interaction_key_pressed)

    def get_spawn_position_for_entering_entity(self, room_width: int, room_height: int, floor_y: int,
                                               entity_width: int = 32, entity_height: int = 32) -> Tuple[int, int]:
        """Get the position where an entity should spawn when entering through this door"""
        spawn_offset = 80  # Distance from the door to spawn the entity

        if self.__direction == Direction.LEFT:
            return (spawn_offset, floor_y - entity_height)
        elif self.__direction == Direction.RIGHT:
            return (room_width - spawn_offset - entity_width, floor_y - entity_height)
        elif self.__direction == Direction.UP:
            # Spawn below the UP door
            return (self.__x + self.__width // 2 - entity_width // 2, floor_y - entity_height)
        elif self.__direction == Direction.DOWN:
            # Spawn below the DOWN door
            return (self.__x + self.__width // 2 - entity_width // 2, floor_y - entity_height)
        else:
            return (room_width // 2 - entity_width // 2, floor_y - entity_height)

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Draw the door with visual indicators and interaction prompts

        Args:
            surface: Surface to draw on
            camera_offset: Camera offset for scrolling
        """
        draw_x = self.__x - camera_offset[0]
        draw_y = self.__y - camera_offset[1]

        # Choose color based on lock status and door type
        if self.__is_locked:
            color = (100, 100, 100)  # Gray if locked
        elif self.__door_type == DoorType.INTERACTIVE:
            color = (100, 150, 200)  # Blue for interactive doors
        else:
            color = (139, 69, 19)  # Brown for walk-through doors

        # Draw door
        pygame.draw.rect(surface, color, (draw_x, draw_y, self.__width, self.__height))

        # Draw door frame
        frame_color = (160, 82, 45) if not self.__is_locked else (120, 120, 120)
        pygame.draw.rect(surface, frame_color, (draw_x, draw_y, self.__width, self.__height), 3)

        # Draw direction indicator
        self.__draw_direction_indicator(surface, draw_x, draw_y)

        # Draw interaction prompt if player is nearby
        self.__draw_interaction_prompt(surface, draw_x, draw_y)

    def __draw_direction_indicator(self, surface: pygame.Surface, draw_x: int, draw_y: int):
        """Draw directional arrow on the door"""
        indicator_color = (255, 255, 0) if not self.__is_locked else (150, 150, 150)
        center_x = draw_x + self.__width // 2
        center_y = draw_y + self.__height // 2

        arrow_size = 8

        if self.__direction == Direction.LEFT:
            pygame.draw.polygon(surface, indicator_color, [
                (center_x - arrow_size, center_y),
                (center_x + arrow_size // 2, center_y - arrow_size),
                (center_x + arrow_size // 2, center_y + arrow_size)
            ])
        elif self.__direction == Direction.RIGHT:
            pygame.draw.polygon(surface, indicator_color, [
                (center_x + arrow_size, center_y),
                (center_x - arrow_size // 2, center_y - arrow_size),
                (center_x - arrow_size // 2, center_y + arrow_size)
            ])
        elif self.__direction == Direction.UP:
            pygame.draw.polygon(surface, indicator_color, [
                (center_x, center_y - arrow_size),
                (center_x - arrow_size, center_y + arrow_size // 2),
                (center_x + arrow_size, center_y + arrow_size // 2)
            ])
        elif self.__direction == Direction.DOWN:
            pygame.draw.polygon(surface, indicator_color, [
                (center_x, center_y + arrow_size),
                (center_x - arrow_size, center_y - arrow_size // 2),
                (center_x + arrow_size, center_y - arrow_size // 2)
            ])

    def __draw_interaction_prompt(self, surface: pygame.Surface, draw_x: int, draw_y: int):
        """Draw interaction prompt above the door if player is nearby"""
        if self.__interaction_state.should_show_prompt():
            prompt_surface = self.__interaction_state.get_prompt_surface()
            if prompt_surface:
                # Position prompt above the door, centered
                prompt_x = draw_x + self.__width // 2 - prompt_surface.get_width() // 2
                prompt_y = draw_y - prompt_surface.get_height() - 10

                # Draw background for better readability
                background_rect = pygame.Rect(
                    prompt_x - 4, prompt_y - 2,
                    prompt_surface.get_width() + 8,
                    prompt_surface.get_height() + 4
                )
                pygame.draw.rect(surface, (0, 0, 0, 180), background_rect)
                pygame.draw.rect(surface, (255, 255, 255), background_rect, 1)

                # Draw the prompt text
                surface.blit(prompt_surface, (prompt_x, prompt_y))


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

    def update_door_interactions(self, player_x: int, player_y: int, player_width: int = 32, player_height: int = 32):
        """Update interaction state for all doors in the room"""
        for door in self.__doors.values():
            door.update_player_proximity(player_x, player_y, player_width, player_height)

    def get_interactive_door_at_position(self, player_x: int, player_y: int,
                                         player_width: int = 32, player_height: int = 32) -> Optional[Door]:
        """Get interactive door that player is colliding with"""
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

        for door in self.__doors.values():
            if (door.door_type == DoorType.INTERACTIVE and
                    door.check_collision(player_rect)):
                return door
        return None

    def get_walkthrough_door_at_position(self, player_x: int, player_y: int,
                                         player_width: int = 32, player_height: int = 32) -> Optional[Door]:
        """Get walk-through door that player is colliding with"""
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

        for door in self.__doors.values():
            if (door.door_type == DoorType.WALK_THROUGH and
                    door.check_collision(player_rect)):
                return door
        return None

    def has_door_in_direction(self, direction: Direction) -> bool:
        """
        Check if room has a door in the specified direction

        Args:
            direction: Direction to check

        Returns:
            True if door exists in that direction
        """
        return direction in self.__doors

    def add_door(self, direction: Direction, dest_room: Tuple[int, int]):
        """
        Add a door to the room

        Args:
            direction: Direction the door faces
            dest_room: Destination room grid coordinates
        """
        door = Door(direction, dest_room, self.__width, self.__height, self.__floor_y)
        self.__doors[direction] = door

    def get_door_in_direction(self, direction: Direction) -> Optional[Door]:
        """
        Get door in specified direction

        Args:
            direction: Direction to look for door

        Returns:
            Door object if found, None otherwise
        """
        return self.__doors.get(direction)

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

    def get_spawn_position_from_direction(self, from_direction: Direction, entity_width: int = 32,
                                          entity_height: int = 32) -> Tuple[int, int]:
        """
        Get spawn position for entity entering from specified direction
        """
        print(f"DEBUG: from_direction = {from_direction}")

        # Spawn near the SAME direction door (not opposite)
        target_door = self.__doors.get(from_direction)
        print(f"DEBUG: target_door exists = {target_door is not None}")

        if target_door:
            spawn_offset = 100

            if from_direction == Direction.LEFT:
                print("DEBUG: Spawning near LEFT door")
                return (target_door.x + 64 + spawn_offset, self.__floor_y - entity_height)
            elif from_direction == Direction.RIGHT:
                print("DEBUG: Spawning near RIGHT door")
                return (target_door.x - spawn_offset - entity_width, self.__floor_y - entity_height)
            elif from_direction == Direction.UP:
                print("DEBUG: Spawning near UP door")
                door_center_x = target_door.x + 32
                # Always spawn on the floor, just positioned horizontally near the UP door
                return (door_center_x - entity_width // 2, self.__floor_y - entity_height)
            elif from_direction == Direction.DOWN:
                print("DEBUG: Spawning near DOWN door")
                door_center_x = target_door.x + 32
                # Always spawn on the floor, just positioned horizontally near the DOWN door
                return (door_center_x - entity_width // 2, self.__floor_y - entity_height)

        print("DEBUG: Using fallback position")
        return (self.__width // 2 - entity_width // 2, self.__floor_y - entity_height)

    def __get_opposite_direction(self, direction: Direction) -> Direction:
        """Get opposite direction"""
        opposites = {
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP
        }
        return opposites[direction]

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Draw the room including background, floor, and doors

        Args:
            surface: Surface to draw on
            camera_offset: Camera offset for scrolling
        """
        # Draw background
        #if self.__background_surface:
            #surface.blit(self.__background_surface, (-camera_offset[0], -camera_offset[1]))

         #Draw floor
        if self.__floor_surface:
            floor_draw_y = self.__floor_y - camera_offset[1]
            surface.blit(self.__floor_surface, (-camera_offset[0], floor_draw_y))

        # Draw doors
        for door in self.__doors.values():
            door.draw(surface, camera_offset)

    def mark_boss_defeated(self):
        '''Mark this room as having defeated boss'''
        if self.is_boss_room():
            self.boss_defeated = True


class DungeonManager:
    """manages the entire dungeon layout an dprogression"""

    def __init__(self, dungeon_size: Tuple[int, int], floor_csv_path: str, tileset_path: str,
                 template: DungeonTemplate = DungeonTemplate.SQUARE):
        self.__grid_width, self.__grid_height = dungeon_size
        self.__dungeon_grid: List[List[Optional[Room]]] = [[None for _ in range(self.__grid_width)] for _ in
                                                           range(self.__grid_height)]
        self.__current_room_pos: Tuple[int, int] = None
        self.__previous_room_pos: Optional[Tuple[int, int]] = None
        self.__template = template

        # initialize rendered and assets
        self.__floor_renderer = FloorRenderer(floor_csv_path)
        self.__tileset = self.__load_tileset(tileset_path)

        # Initialize pillar manager
        self.__pillar_manager = PillarManager()
        
        # Initialize potion manager
        self.__potion_manager = PotionManager()

        #initialize enemy spawn manager
        self.__enemy_spawn_manager = EnemySpawnManager()

        self.pillars_collected = 0
        self.boss_defeated = False

        # load base templaate from TMX
        # self.base_tile_data = self._load_tmx_data(tmx_file)

        # generate dungeon
        self.__generate_dungeon()

        self.rooms = {}  # keys are (x, y) tuples, values are Room instances
        self.current_room = None

    def add_room(self, room: Room):
            self.rooms[room.grid_pos] = room


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

    @property
    def pillar_manager(self) -> PillarManager:
        """Get the pillar manager"""
        return self.__pillar_manager

    @property
    def potion_manager(self) -> PotionManager:
        """Get the potion manager"""
        return self.__potion_manager

    @property
    def enemy_spawn_manager(self) -> EnemySpawnManager:
        """get the enemy spawn manager"""
        return self.__enemy_spawn_manager

    def check_pillar_collection(self, player_x: int, player_y: int, player_width: int = 32, player_height: int = 32) -> \
    Optional[Pillar]:
        """Check if player collects a pillar in current room"""
        if not self.__current_room_pos:
            return None

        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        collected_pillar = self.__pillar_manager.check_pillar_collection(self.__current_room_pos, player_rect)

        if collected_pillar:
            print(f"Collected {collected_pillar.name} pillar!")
            # Check if we can now unlock boss room
            if self.__pillar_manager.can_access_boss_room():
                self.__unlock_boss_room_doors()

        return collected_pillar

    def __unlock_boss_room_doors(self):
        """Unlock all doors leading to boss room"""
        for row in range(self.__grid_height):
            for col in range(self.__grid_width):
                room = self.__dungeon_grid[row][col]
                if room:
                    for door in room.doors.values():
                        dest_room = self.get_room_at_position(door.dest_room)
                        if dest_room and dest_room.is_boss_room():
                            door.unlock()
                            print("Boss room door unlocked!")

    def try_enter_walkthrough_door(self, player_x: int, player_y: int) -> bool:
        """Try to enter a walk-through door automatically"""
        current_room = self.get_current_room()
        if not current_room:
            return False

        # Use a reasonable hitbox size for door collision (not the tiny hitbox)
        door = current_room.get_walkthrough_door_at_position(player_x, player_y, 64, 64)
        if door and not door.is_locked:
            return self.__execute_room_transition(door)
        return False

    def try_enter_interactive_door(self, player_x: int, player_y: int, interaction_key_pressed: bool) -> bool:
        """Try to enter an interactive door with key press"""
        current_room = self.get_current_room()
        if not current_room:
            return False

        # Use a reasonable hitbox size for door collision (not the tiny hitbox)
        door = current_room.get_interactive_door_at_position(player_x, player_y, 64, 64)
        if door and not door.is_locked and interaction_key_pressed:
            return self.__execute_room_transition(door)
        return False

    def __execute_room_transition(self, door: Door) -> bool:
        """Execute the actual room transition"""
        self.__previous_room_pos = self.__current_room_pos
        self.__current_room_pos = door.dest_room

        # Verify destination room exists
        dest_room = self.get_current_room()
        if dest_room:
            return True
        else:
            # Revert if destination doesn't exist
            self.__current_room_pos = self.__previous_room_pos
            self.__previous_room_pos = None
            return False

    def update_current_room_interactions(self, player_x: int, player_y: int,
                                         player_width: int = 32, player_height: int = 32):
        """Update door interactions for current room"""
        current_room = self.get_current_room()
        if current_room:
            current_room.update_door_interactions(player_x, player_y, player_width, player_height)

    def __get_template_layout(self) -> List[Tuple[int, int]]:
        """Get room positions based on selected template"""
        center = (self.__grid_height // 2, self.__grid_width // 2)

        if self.__template == DungeonTemplate.CROSS:
            # Original cross pattern
            return [
                center,  # Center room
                (center[0], center[1] - 1),  # Left
                (center[0], center[1] + 1),  # Right
                (center[0] - 1, center[1]),  # Up
                (center[0] + 1, center[1]),  # Down
            ]

        elif self.__template == DungeonTemplate.DEMO:
            # Simple linear path for easy demonstration
            return [
                center,  # Start room
                (center[0], center[1] + 1),  # Right to boss
            ]

        elif self.__template == DungeonTemplate.SQUARE:
            # Square pattern with corners filled
            positions = []
            for row in range(self.__grid_height):
                for col in range(self.__grid_width):
                    positions.append((row, col))
            return positions

        elif self.__template == DungeonTemplate.FULL:
            # All rooms filled
            positions = []
            for row in range(self.__grid_height):
                for col in range(self.__grid_width):
                    positions.append((row, col))
            return positions

        else:
            # Default to square
            return self.__get_template_layout()

    def __generate_dungeon(self):
        """Generate the dungeon layout with proper connectivity"""
        # Get room positions from template
        room_positions = self.__get_template_layout()

        # Start in center
        start_pos = (self.__grid_height // 2, self.__grid_width // 2)
        self.__current_room_pos = start_pos

        # Create rooms based on template
        for pos in room_positions:
            if self.__is_valid_position(pos):
                room = Room(pos)

                # Set special rooms
                if pos == start_pos:
                    room.set_as_start_room()
                elif self.__template == DungeonTemplate.DEMO and pos == (start_pos[0], start_pos[1] + 1):
                    room.set_as_boss_room()
                elif pos == (0, self.__grid_width - 1):  # Top-right corner for non-demo
                    room.set_as_boss_room()

                self.__initialize_room(room)
                self.__dungeon_grid[pos[0]][pos[1]] = room

        # Create doors between connected rooms
        self.__create_doors()

        # Distribute pillars
        self.__distribute_pillars()

        # Distribute potions
        self.__distribute_potions()

        # Lock boss room doors initially
        self.__lock_boss_room_doors()

    def __distribute_pillars(self):
        """Distribute pillars throughout the dungeon"""
        available_pillar_types = list(PillarType)
        available_rooms = []
        boss_room_pos = None

        # Find available rooms (not start room)
        for row in range(self.__grid_height):
            for col in range(self.__grid_width):
                room = self.__dungeon_grid[row][col]
                if room:
                    if room.is_boss_room():
                        boss_room_pos = (row, col)
                    elif not room.is_start_room():
                        available_rooms.append((row, col))

        # Shuffle pillar types
        random.shuffle(available_pillar_types)

        # Place Composition pillar in boss room
        if boss_room_pos:
            composition_pillar = Pillar(
                PillarType.COMPOSITION,
                self.__dungeon_grid[boss_room_pos[0]][boss_room_pos[1]].width // 2,
                self.__dungeon_grid[boss_room_pos[0]][boss_room_pos[1]].floor_y - 64
            )
            self.__pillar_manager.add_pillar_to_room(boss_room_pos, composition_pillar)
            available_pillar_types.remove(PillarType.COMPOSITION)

        # Place other pillars in random rooms
        random.shuffle(available_rooms)
        for i, pillar_type in enumerate(available_pillar_types):
            if i < len(available_rooms):
                room_pos = available_rooms[i]
                room = self.__dungeon_grid[room_pos[0]][room_pos[1]]

                # Random position in room (avoiding edges)
                pillar_x = random.randint(200, room.width - 200)
                pillar_y = room.floor_y - 64

                pillar = Pillar(pillar_type, pillar_x, pillar_y)
                self.__pillar_manager.add_pillar_to_room(room_pos, pillar)

    def __distribute_potions(self):
        """Distribute healing potions throughout the dungeon"""
        available_rooms = []
        
        # Find available rooms (not start room, not boss room)
        for row in range(self.__grid_height):
            for col in range(self.__grid_width):
                room = self.__dungeon_grid[row][col]
                if room and not room.is_start_room() and not room.is_boss_room():
                    available_rooms.append((row, col))

        # Shuffle available rooms for random distribution
        random.shuffle(available_rooms)
        
        # Determine number of potions to spawn (1-3 per room, but not every room)
        num_rooms_with_potions = min(len(available_rooms), random.randint(2, 4))
        
        for i in range(num_rooms_with_potions):
            if i < len(available_rooms):
                room_pos = available_rooms[i]
                room = self.__dungeon_grid[room_pos[0]][room_pos[1]]
                
                # Determine number of potions in this room (1-2)
                num_potions_in_room = random.randint(1, 2)
                
                for _ in range(num_potions_in_room):
                    # Random position in room (avoiding edges and other objects)
                    potion_x = random.randint(150, room.width - 150)
                    potion_y = room.floor_y - 80  # Slightly above floor
                    
                    # Create healing potion
                    potion = Potion(PotionType.HEALING, potion_x, potion_y)
                    self.__potion_manager.add_potion_to_room(room_pos, potion)

    def __lock_boss_room_doors(self):
        """Lock all doors leading to boss room"""
        for row in range(self.__grid_height):
            for col in range(self.__grid_width):
                room = self.__dungeon_grid[row][col]
                if room:
                    for door in room.doors.values():
                        dest_room = self.get_room_at_position(door.dest_room)
                        if dest_room and dest_room.is_boss_room():
                            door.lock("Need 4 OOP Pillars to enter Boss Room")

    def __generate_connected_rooms(self):
        """Generate a connected set of rooms"""
        rooms_to_create = [
            (self.__grid_height // 2, self.__grid_width // 2 - 1),  # Left of start
            (self.__grid_height // 2, self.__grid_width // 2 + 1),  # Right of start
            (self.__grid_height // 2 - 1, self.__grid_width // 2),  # Above start
            (self.__grid_height // 2 + 1, self.__grid_width // 2),  # Below start
        ]

        # Create rooms at valid positions
        for pos in rooms_to_create:
            if self.__is_valid_position(pos):
                room = Room(pos)

                # Make one of the edge rooms a boss room
                if pos == (self.__grid_height // 2, self.__grid_width // 2 + 1):
                    room.set_as_boss_room()

                self.__initialize_room(room)
                self.__dungeon_grid[pos[0]][pos[1]] = room

    def __create_doors(self):
        """Create doors between connected rooms"""
        for row in range(self.__grid_height):
            for col in range(self.__grid_width):
                current_room = self.__dungeon_grid[row][col]
                if current_room is None:
                    continue

                # Check all four directions
                for direction in Direction:
                    neighbor_pos = self.__get_neighbor_position((row, col), direction)

                    if (self.__is_valid_position(neighbor_pos) and
                            self.__dungeon_grid[neighbor_pos[0]][neighbor_pos[1]] is not None):
                        # There's a room in this direction, add a door
                        current_room.add_door(direction, neighbor_pos)

    def __initialize_room(self, room: Room):
        """Initialize room with floor and background"""
        room.generate_background()
        room.generate_floor(self.__floor_renderer, self.__tileset)

        # Initialize enemy spawns for this room
        self.__enemy_spawn_manager.initialize_room_spawns(
            room.grid_pos,
            room.width,
            room.height,
            room.floor_y,
            room.is_boss_room(),
            room.is_start_room()
        )



    def _constrain_enemy_to_ground(self, enemy: Monster, ground_y: int):
        """Constrain enemy to move only on the ground along X axis"""
        # Set enemy Y position to ground level
        enemy_height = getattr(enemy, 'height', 32)  # Default height if not available
        enemy.y = ground_y - enemy_height

        # If your Monster class has movement constraints, set them here
        if hasattr(enemy, 'constrain_to_ground'):
            enemy.constrain_to_ground(True)

        # If your Monster class has gravity or Y velocity, disable it
        if hasattr(enemy, 'gravity_enabled'):
            enemy.gravity_enabled = False
        if hasattr(enemy, 'velocity_y'):
            enemy.velocity_y = 0

    def update_enemies_ground_constraint(self, enemies: List[Monster]):
        """Update enemies to maintain ground constraint"""
        current_room = self.get_current_room()
        if not current_room:
            return

        ground_y = current_room.floor_y

        for enemy in enemies:
            enemy_height = getattr(enemy, 'height', 32)
            target_y = ground_y - enemy_height

            # Force enemy to stay at ground level
            if hasattr(enemy, 'y'):
                enemy.y = target_y
            if hasattr(enemy, 'rect'):
                enemy.rect.y = target_y

            # Reset any Y velocity
            if hasattr(enemy, 'velocity_y'):
                enemy.velocity_y = 0

    def update_enemy_spawns(self, dt: float):
        """Update enemy spawn system"""
        if self.__current_room_pos:
            self.__enemy_spawn_manager.update(self.__current_room_pos, dt)

    def get_active_enemies_in_current_room(self) -> List[Monster]:
        """Get active enemies in current room"""
        if self.__current_room_pos:
            return self.__enemy_spawn_manager.get_active_enemies_for_room(self.__current_room_pos)
        return []


    def __get_neighbor_position(self, pos: Tuple[int, int], direction: Direction) -> Tuple[int, int]:
        """Get neighbor position in given direction"""
        dr, dc = direction.value
        return (pos[0] + dr, pos[1] + dc)

    def __is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """Check if position is within grid bounds"""
        return (0 <= pos[0] < self.__grid_height and 0 <= pos[1] < self.__grid_width)

    def __get_direction_between_rooms(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> Optional[Direction]:
        """Get the direction from one room to another"""
        dr = to_pos[0] - from_pos[0]
        dc = to_pos[1] - from_pos[1]

        print(f"DEBUG: from_pos = {from_pos}, to_pos = {to_pos}")
        print(f"DEBUG: dr = {dr}, dc = {dc}")

        if dr == 1 and dc == 0:
            print("DEBUG: Returning RIGHT")
            return Direction.RIGHT
        elif dr == -1 and dc == 0:
            print("DEBUG: Returning LEFT")
            return Direction.LEFT
        elif dr == 0 and dc == 1:
            print("DEBUG: Returning DOWN")
            return Direction.DOWN
        elif dr == 0 and dc == -1:
            print("DEBUG: Returning UP")
            return Direction.UP
        else:
            print("DEBUG: Returning None")
            return None
    def get_current_room(self) -> Optional[Room]:
        """Get the current room"""
        if self.__current_room_pos:
            return self.__dungeon_grid[self.__current_room_pos[0]][self.__current_room_pos[1]]
        return None

    def update_pillars(self, dt: float):
        """Update pillars in current room"""
        if self.__current_room_pos:
            self.__pillar_manager.update_pillars_in_room(self.__current_room_pos, dt)

    def update_potions(self, dt: float):
        """Update potions in current room"""
        if self.__current_room_pos:
            self.__potion_manager.update_potions_in_room(self.__current_room_pos, dt)

    def draw_pillars(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Draw pillars in current room"""
        if self.__current_room_pos:
            self.__pillar_manager.draw_pillars_in_room(self.__current_room_pos, surface, camera_offset)

    def draw_potions(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Draw potions in current room"""
        if self.__current_room_pos:
            self.__potion_manager.draw_potions_in_room(self.__current_room_pos, surface, camera_offset)

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
            self.__previous_room_pos = self.__current_room_pos
            self.__current_room_pos = door.dest_room
            return True

        return False

    def get_player_spawn_position_for_current_room(self, entity_width: int = 32, entity_height: int = 32) -> Tuple[
        int, int]:
        """
        Get the position where the player should spawn in the current room

        Args:
            entity_width: Width of the player entity
            entity_height: Height of the player entity

        Returns:
            (x, y) position where player should spawn
        """
        current_room = self.get_current_room()
        if not current_room:
            return (800, 480)  # Fallback position

        if self.__previous_room_pos is None:
            # First time entering (start room), spawn in center
            return (current_room.width // 2 - entity_width // 2, current_room.floor_y - entity_height)

        # Get direction we came from
        from_direction = self.__get_direction_between_rooms(self.__current_room_pos, self.__previous_room_pos)
        if from_direction:
            return current_room.get_spawn_position_from_direction(from_direction, entity_width, entity_height)
        else:
            # Fallback to center
            return (current_room.width // 2 - entity_width // 2, current_room.floor_y - entity_height)

    def get_current_room_position(self) -> Tuple[int, int]:
        """Get current room grid position"""
        return self.__current_room_pos

    def set_current_room_by_coordinates(self, x, y):
        key = (x, y)
        if key in self.rooms:
            self.current_room = self.rooms[key]
        else:
            raise ValueError(f"No room found at coordinates {x}, {y}")

    def get_previous_room_position(self) -> Optional[Tuple[int, int]]:
        """Get previous room grid position"""
        return self.__previous_room_pos

    def get_dungeon_width(self) -> int:
        """Get dungeon grid width"""
        return self.__grid_width

    def get_dungeon_height(self) -> int:
        """Get dungeon grid height"""
        return self.__grid_height

    def get_room_at_position(self, pos: Tuple[int, int]) -> Optional[Room]:
        """
        Get room at specified grid position

        Args:
            pos: Grid position to check

        Returns:
            Room at position or None if no room exists
        """
        if self.__is_valid_position(pos):
            return self.__dungeon_grid[pos[0]][pos[1]]
        return None

    def check_potion_collection(self, player_x: int, player_y: int, player_width: int = 32, player_height: int = 32) -> \
    Optional[Potion]:
        """Check if player collects a potion in current room"""
        if not self.__current_room_pos:
            return None

        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        collected_potion = self.__potion_manager.check_potion_collection(self.__current_room_pos, player_rect)

        if collected_potion:
            print(f"Collected {collected_potion.name} potion!")

        return collected_potion

    def get_boss_room_position(self) -> tuple:
        """Get the position of the boss room in the dungeon grid"""
        for row in range(self.dungeon_height):
            for col in range(self.dungeon_width):
                room = self.rooms.get((row, col))
                if room and room.is_boss_room():
                    return (row, col)
        return None

    def is_room_cleared(self, room_position: tuple) -> bool:
        """Check if a specific room has been cleared of all enemies"""
        if not room_position or room_position not in self.rooms:
            return False

        room = self.rooms[room_position]
        if not room:
            return False

        # For boss room, check if boss is defeated
        if room.is_boss_room():
            # This would need to track boss state across room transitions
            # You might want to add a boss_defeated flag to the room or dungeon manager
            return getattr(room, 'boss_defeated', False)

        # For regular rooms, check if spawn manager considers it cleared
        return self.enemy_spawn_manager.is_room_cleared(room_position)

    # REPLACE your existing spawn_enemies_for_current_room method in RoomDungeonSystem.py with this:

    def spawn_enemies_for_current_room(self):
        """Spawn 1-2 enemies per regular room, boss only in boss room"""
        print(f"=== SPAWNING ENEMIES ===")

        # Get current room
        room = getattr(self, 'current_room', None)
        if not room:
            print("No current room - returning empty list")
            return []

        print(f"Room found: {type(room).__name__}")
        print(f"Room position: {room.grid_pos}")

        # Check if this is a boss room using the existing is_boss_room method
        is_boss = room.is_boss_room()
        print(f"Is boss room: {is_boss}")

        enemies = []

        try:
            if is_boss:
                print("🏰 SPAWNING BOSS ROOM")
                # Only spawn demon boss in center
                from src.model.DemonBoss import DemonBoss
                boss = DemonBoss(400, room.floor_y - 120)  # Position boss on floor
                enemies.append(boss)
                print(f"✓ Spawned Demon Boss at (400, {room.floor_y - 120})")

            else:
                print("🏠 SPAWNING REGULAR ROOM")
                # Spawn 1-2 random enemies
                import random
                enemy_count = random.randint(1, 2)

                # Create positions spread across room
                if enemy_count == 1:
                    positions = [(400, room.floor_y - 64)]  # Center
                else:  # 2 enemies
                    positions = [(250, room.floor_y - 64), (550, room.floor_y - 64)]  # Left and right

                # Create enemies
                for i, (x, y) in enumerate(positions):
                    # Add some random variation
                    varied_x = x + random.randint(-50, 50)
                    varied_y = y + random.randint(-10, 10)

                    # Choose random enemy type
                    if i % 2 == 0:
                        from src.model.Skeleton import Skeleton
                        enemy = Skeleton(varied_x, varied_y)
                        enemy_name = "Skeleton"
                    else:
                        from src.model.Ogre import Ogre
                        enemy = Ogre(varied_x, varied_y)
                        enemy_name = "Ogre"

                    enemies.append(enemy)
                    print(f"✓ Spawned {enemy_name} at ({varied_x}, {varied_y})")

        except Exception as e:
            print(f" Error in spawning: {e}")
            import traceback
            traceback.print_exc()

            # Emergency fallback - create basic monsters
            print("Creating fallback enemies...")
            try:
                from src.model.Monster import Monster
                enemies = [
                    Monster("Fallback Enemy 1", 100, 20, False, 300, room.floor_y - 64),
                    Monster("Fallback Enemy 2", 100, 20, False, 500, room.floor_y - 64)
                ]
                print("Created fallback enemies")
            except Exception as fallback_error:
                print(f"Even fallback failed: {fallback_error}")
                return []

        print(f"Total enemies created: {len(enemies)}")
        print(f"=== END SPAWNING ===")
        return enemies


    def _create_enemy_by_type(self, enemy_type, x, y):
        """Create an enemy of the specified type at the given position"""
        try:
            if enemy_type == 'skeleton':
                from src.model.Skeleton import Skeleton
                return Skeleton(x, y)
            elif enemy_type == 'ogre':
                from src.model.Ogre import Ogre
                return Ogre(x, y)
            elif enemy_type == 'demon_boss':
                from src.model.DemonBoss import DemonBoss
                return DemonBoss(x, y)
            else:
                # Fallback: create a basic monster
                from src.model.Monster import Monster
                return Monster(f"{enemy_type.title()} Enemy", 100, 25, False, x, y)

        except Exception as e:
            print(f"Error creating {enemy_type}: {e}")
            # Return a basic monster as fallback
            try:
                from src.model.Monster import Monster
                return Monster("Unknown Enemy", 100, 25, False, x, y)
            except:
                return None

