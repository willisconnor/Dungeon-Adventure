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

class DoorType(Enum):
    #Doors based through interaction method
    WALK_THROUGH = "walk_through"
    INTERACTIVE = "interactive"

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
        if tile_id <= 0:
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

        #determine door type based on direction
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

            self.__interaction_state.set_player_nearby(
                is_nearby,
                self.__interaction_prompt if is_nearby and not self.__is_locked else ""
            )
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

        Args:
            from_direction: Direction entity is coming from
            entity_width: Width of entity
            entity_height: Height of entity

        Returns:
            (x, y) position where entity should spawn
        """
        # Get the opposite direction door (where we're entering through)
        opposite_direction = self.__get_opposite_direction(from_direction)
        door = self.__doors.get(opposite_direction)

        if door:
            return door.get_spawn_position_for_entering_entity(
                self.__width, self.__height, self.__floor_y, entity_width, entity_height
            )
        else:
            # Fallback to center if no door found
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
        self.__previous_room_pos: Optional[Tuple[int, int]] = None

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

    def try_enter_walkthrough_door(self, player_x: int, player_y: int) -> bool:
        """Try to enter a walk-through door automatically"""
        current_room = self.get_current_room()
        if not current_room:
            return False

        door = current_room.get_walkthrough_door_at_position(player_x, player_y)
        if door and not door.is_locked:
            return self.__execute_room_transition(door)
        return False

    def try_enter_interactive_door(self, player_x: int, player_y: int, interaction_key_pressed: bool) -> bool:
        """Try to enter an interactive door with key press"""
        current_room = self.get_current_room()
        if not current_room:
            return False

        door = current_room.get_interactive_door_at_position(player_x, player_y)
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


    def __generate_dungeon(self):
        """Generate the dungeon layout with proper connectivity"""
        # Start in center
        start_pos = (self.__grid_height // 2, self.__grid_width // 2)
        self.__current_room_pos = start_pos

        # Create start room
        start_room = Room(start_pos)
        start_room.set_as_start_room()
        self.__initialize_room(start_room)
        self.__dungeon_grid[start_pos[0]][start_pos[1]] = start_room

        # Generate connected rooms
        self.__generate_connected_rooms()

        # Add doors only where connections exist
        self.__create_doors()

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

    def __get_neighbor_position(self, pos: Tuple[int, int], direction: Direction) -> Tuple[int, int]:
        """Get neighbor position in given direction"""
        dr, dc = direction.value
        return (pos[0] + dr, pos[1] + dc)

    def __is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """Check if position is within grid bounds"""
        return (0 <= pos[0] < self.__grid_height and 0 <= pos[1] < self.__grid_width)

    def __get_direction_between_rooms(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> Optional[Direction]:
        """
        Get the direction from one room to another

        Args:
            from_pos: Starting room position
            to_pos: Destination room position

        Returns:
            Direction from from_pos to to_pos, or None if not adjacent
        """
        dr = to_pos[0] - from_pos[0]
        dc = to_pos[1] - from_pos[1]

        if dr == 0 and dc == 1:
            return Direction.RIGHT
        elif dr == 0 and dc == -1:
            return Direction.LEFT
        elif dr == 1 and dc == 0:
            return Direction.DOWN
        elif dr == -1 and dc == 0:
            return Direction.UP
        else:
            return None

    def get_current_room(self) -> Optional[Room]:
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
