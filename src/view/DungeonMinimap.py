"""
DungeonMinimap.py - Minimap system for dungeon exploration
Provides visual representation of explored rooms and player position
"""

import pygame
from typing import Dict, Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass



class RoomDisplayType(Enum):
    """Types of rooms with different visual representations"""
    NORMAL = "normal"
    START = "start"
    BOSS = "boss"
    TREASURE = "treasure"
    LOCKED = "locked"


@dataclass(frozen=True)
class RoomColors:
    """Immutable color configuration for different room types"""
    NORMAL: Tuple[int, int, int] = (120, 120, 120)
    START: Tuple[int, int, int] = (100, 200, 100)
    BOSS: Tuple[int, int, int] = (200, 100, 100)
    TREASURE: Tuple[int, int, int] = (200, 200, 100)
    LOCKED: Tuple[int, int, int] = (100, 100, 100)
    CURRENT: Tuple[int, int, int] = (255, 255, 100)
    BACKGROUND: Tuple[int, int, int] = (30, 30, 30)
    BORDER: Tuple[int, int, int] = (200, 200, 200)
    DOOR: Tuple[int, int, int] = (150, 150, 150)


@dataclass(frozen=True)
class MinimapDimensions:
    """Immutable dimensions configuration for the minimap"""
    room_size: int = 24
    padding: int = 2
    border_size: int = 10
    door_thickness: int = 2
    door_length: int = 8


class GridCoordinate:
    """Encapsulates grid coordinate operations with validation"""

    def __init__(self, row: int, col: int):
        self.__row = self.__validate_coordinate(row, "row")
        self.__col = self.__validate_coordinate(col, "col")

    @staticmethod
    def __validate_coordinate(value: int, name: str) -> int:
        """Validate coordinate value"""
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
        if value < 0:
            raise ValueError(f"{name} must be non-negative")
        return value

    @property
    def row(self) -> int:
        """Get row coordinate"""
        return self.__row

    @property
    def col(self) -> int:
        """Get column coordinate"""
        return self.__col

    def as_tuple(self) -> Tuple[int, int]:
        """Get coordinate as tuple"""
        return (self.__row, self.__col)

    def __eq__(self, other) -> bool:
        if not isinstance(other, GridCoordinate):
            return False
        return self.__row == other.row and self.__col == other.col

    def __hash__(self) -> int:
        return hash((self.__row, self.__col))

    def __repr__(self) -> str:
        return f"GridCoordinate({self.__row}, {self.__col})"


class RoomInfo:
    """Encapsulates information about a single room"""

    def __init__(self, grid_pos: GridCoordinate, room_type: RoomDisplayType = RoomDisplayType.NORMAL):
        self.__grid_pos = grid_pos
        self.__room_type = room_type
        self.__is_visited = False
        self.__connected_directions: Set[Tuple[int, int]] = set()

    @property
    def grid_position(self) -> GridCoordinate:
        """Get room grid position"""
        return self.__grid_pos

    @property
    def room_type(self) -> RoomDisplayType:
        """Get room type"""
        return self.__room_type

    @property
    def is_visited(self) -> bool:
        """Check if room has been visited"""
        return self.__is_visited

    @property
    def connected_directions(self) -> Set[Tuple[int, int]]:
        """Get copy of connected directions"""
        return self.__connected_directions.copy()

    def set_room_type(self, room_type: RoomDisplayType) -> None:
        """Set room type with validation"""
        if not isinstance(room_type, RoomDisplayType):
            raise TypeError("room_type must be a RoomDisplayType")
        self.__room_type = room_type

    def mark_visited(self) -> None:
        """Mark room as visited"""
        self.__is_visited = True

    def mark_unvisited(self) -> None:
        """Mark room as unvisited"""
        self.__is_visited = False

    def add_connection(self, direction: Tuple[int, int]) -> None:
        """Add a door connection direction"""
        if not isinstance(direction, tuple) or len(direction) != 2:
            raise ValueError("Direction must be a tuple of (row_offset, col_offset)")
        self.__connected_directions.add(direction)

    def remove_connection(self, direction: Tuple[int, int]) -> None:
        """Remove a door connection direction"""
        self.__connected_directions.discard(direction)

    def clear_connections(self) -> None:
        """Clear all door connections"""
        self.__connected_directions.clear()

    def get_display_color(self, colors: RoomColors) -> Tuple[int, int, int]:
        """Get appropriate display color for this room"""
        if self.__room_type == RoomDisplayType.START:
            return colors.START
        elif self.__room_type == RoomDisplayType.BOSS:
            return colors.BOSS
        elif self.__room_type == RoomDisplayType.TREASURE:
            return colors.TREASURE
        elif self.__room_type == RoomDisplayType.LOCKED:
            return colors.LOCKED
        else:
            return colors.NORMAL


class CoordinateTransform:
    """Handles coordinate transformation between dungeon grid and minimap display"""

    def __init__(self, grid_height: int):
        self.__grid_height = self.__validate_dimension(grid_height, "grid_height")

    @staticmethod
    def __validate_dimension(value: int, name: str) -> int:
        """Validate dimension value"""
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
        if value <= 0:
            raise ValueError(f"{name} must be positive")
        return value

    def dungeon_to_minimap(self, dungeon_pos: Tuple[int, int]) -> GridCoordinate:
        """
        Convert dungeon coordinates to minimap coordinates

        Dungeon coordinate system: (row, col) where row=0 is north, col=0 is west
        Minimap display: row=0 is top, col=0 is left

        Args:
            dungeon_pos: (row, col) position in dungeon grid

        Returns:
            GridCoordinate for minimap display
        """
        dungeon_row, dungeon_col = dungeon_pos

        # Direct mapping: dungeon row/col maps to minimap row/col
        # This ensures: north->up, east->right, south->down, west->left
        minimap_row = dungeon_col
        minimap_col = self.__grid_height - dungeon_row - 1

        return GridCoordinate(minimap_row, minimap_col)

    def minimap_to_dungeon(self, minimap_coord: GridCoordinate) -> Tuple[int, int]:
        """
        Convert minimap coordinates back to dungeon coordinates

        Args:
            minimap_coord: GridCoordinate from minimap

        Returns:
            (row, col) position in dungeon grid
        """
        # Reverse of dungeon_to_minimap transformation
        dungeon_row = self.__grid_height - minimap_coord.col - 1
        dungeon_col = minimap_coord.row
        return (dungeon_row, dungeon_col)


class MinimapRenderer:
    """Handles all rendering operations for the minimap"""

    def __init__(self, dimensions: MinimapDimensions, colors: RoomColors):
        self.__dimensions = dimensions
        self.__colors = colors

    def render_background(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Render minimap background"""
        pygame.draw.rect(surface, self.__colors.BACKGROUND, rect)
        pygame.draw.rect(surface, self.__colors.BORDER, rect, 2)

    def render_room(self, surface: pygame.Surface, room_info: RoomInfo,
                   screen_pos: Tuple[int, int], is_current: bool = False) -> None:
        """
        Render a single room

        Args:
            surface: Surface to draw on
            room_info: Room information
            screen_pos: Screen position to draw at
            is_current: Whether this is the current room
        """
        if not room_info.is_visited:
            return

        x, y = screen_pos
        room_rect = pygame.Rect(x, y, self.__dimensions.room_size, self.__dimensions.room_size)

        # Fill room with appropriate color
        color = room_info.get_display_color(self.__colors)
        pygame.draw.rect(surface, color, room_rect)

        # Draw current room indicator
        if is_current:
            pygame.draw.rect(surface, self.__colors.CURRENT, room_rect, 3)
        else:
            pygame.draw.rect(surface, self.__colors.BORDER, room_rect, 1)

    def render_door_connection(self, surface: pygame.Surface,
                             from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        """
        Render door connection between two rooms

        Args:
            surface: Surface to draw on
            from_pos: Screen position of source room
            to_pos: Screen position of destination room
        """
        from_center = (
            from_pos[0] + self.__dimensions.room_size // 2,
            from_pos[1] + self.__dimensions.room_size // 2
        )
        to_center = (
            to_pos[0] + self.__dimensions.room_size // 2,
            to_pos[1] + self.__dimensions.room_size // 2
        )

        pygame.draw.line(surface, self.__colors.DOOR, from_center, to_center,
                        self.__dimensions.door_thickness)


class MinimapGeometry:
    """Handles geometric calculations and transformations for the minimap"""

    def __init__(self, grid_width: int, grid_height: int, dimensions: MinimapDimensions):
        self.__grid_width = self.__validate_dimension(grid_width, "grid_width")
        self.__grid_height = self.__validate_dimension(grid_height, "grid_height")
        self.__dimensions = dimensions
        self.__position = (0, 0)
        self.__coordinate_transform = CoordinateTransform(grid_height)

        # Calculate dimensions (standard orientation: north=up, east=right)
        self.__width = self.__grid_width * (dimensions.room_size + dimensions.padding) - dimensions.padding + 2 * dimensions.border_size
        self.__height = self.__grid_height * (dimensions.room_size + dimensions.padding) - dimensions.padding + 2 * dimensions.border_size

    @staticmethod
    def __validate_dimension(value: int, name: str) -> int:
        """Validate dimension value"""
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
        if value <= 0:
            raise ValueError(f"{name} must be positive")
        return value

    @property
    def width(self) -> int:
        """Get minimap width"""
        return self.__width

    @property
    def height(self) -> int:
        """Get minimap height"""
        return self.__height

    @property
    def position(self) -> Tuple[int, int]:
        """Get minimap position"""
        return self.__position

    def set_position(self, position: Tuple[int, int]) -> None:
        """Set minimap position with validation"""
        if not isinstance(position, tuple) or len(position) != 2:
            raise ValueError("Position must be a tuple of (x, y)")
        if not all(isinstance(coord, (int, float)) for coord in position):
            raise TypeError("Position coordinates must be numeric")
        self.__position = (int(position[0]), int(position[1]))

    def get_bounding_rect(self) -> pygame.Rect:
        """Get bounding rectangle for the minimap"""
        return pygame.Rect(self.__position[0], self.__position[1], self.__width, self.__height)

    def get_room_screen_position(self, dungeon_pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Get screen position for a room from dungeon coordinates

        Args:
            dungeon_pos: (row, col) position in dungeon grid

        Returns:
            Screen position for the room
        """
        # Transform dungeon coordinates to minimap coordinates
        minimap_coord = self.__coordinate_transform.dungeon_to_minimap(dungeon_pos)

        x = (self.__position[0] + self.__dimensions.border_size +
             minimap_coord.col * (self.__dimensions.room_size + self.__dimensions.padding))
        y = (self.__position[1] + self.__dimensions.border_size +
             minimap_coord.row * (self.__dimensions.room_size + self.__dimensions.padding))

        return (x, y)

    def is_valid_dungeon_position(self, dungeon_pos: Tuple[int, int]) -> bool:
        """Check if dungeon coordinate is valid"""
        row, col = dungeon_pos
        return (0 <= row < self.__grid_height and 0 <= col < self.__grid_width)


class MinimapUIManager:
    """Manages UI elements and text display for the minimap"""

    def __init__(self, font: pygame.font.Font):
        self.__font = font
        self.__text_color = (255, 255, 255)
        self.__text_spacing = 20

    def render_room_info(self, surface: pygame.Surface, current_pos: Tuple[int, int],
                        minimap_rect: pygame.Rect) -> None:
        """Render room position information"""
        room_text = f"Room: ({current_pos[0]}, {current_pos[1]})"
        text_surface = self.__font.render(room_text, True, self.__text_color)

        # Position to the right of minimap
        text_x = minimap_rect.right + 10
        text_y = minimap_rect.y

        surface.blit(text_surface, (text_x, text_y))

    def render_exploration_stats(self, surface: pygame.Surface, visited_count: int,
                               total_count: int, minimap_rect: pygame.Rect) -> None:
        """Render exploration statistics"""
        stats_text = f"Explored: {visited_count}/{total_count}"
        text_surface = self.__font.render(stats_text, True, self.__text_color)

        # Position below room info
        text_x = minimap_rect.right + 10
        text_y = minimap_rect.y + self.__text_spacing

        surface.blit(text_surface, (text_x, text_y))

    def render_toggle_instruction(self, surface: pygame.Surface, minimap_rect: pygame.Rect) -> None:
        """Render toggle instruction"""
        instruction_text = "Press M to toggle map"
        text_surface = self.__font.render(instruction_text, True, (150, 150, 150))

        # Position below exploration stats
        text_x = minimap_rect.right + 10
        text_y = minimap_rect.y + self.__text_spacing * 2

        surface.blit(text_surface, (text_x, text_y))


class DungeonMinimap:
    """
    Main minimap class that provides visual representation of dungeon exploration
    Encapsulates all minimap functionality with proper OOP principles
    """

    def __init__(self, dungeon_size: Tuple[int, int], position: Tuple[int, int] = (10, 10)):
        """
        Initialize the minimap

        Args:
            dungeon_size: (width, height) of the dungeon grid
            position: (x, y) position on screen where minimap should be drawn
        """
        if not isinstance(dungeon_size, tuple) or len(dungeon_size) != 2:
            raise ValueError("dungeon_size must be a tuple of (width, height)")

        grid_width, grid_height = dungeon_size

        # Initialize components
        self.__dimensions = MinimapDimensions()
        self.__colors = RoomColors()
        self.__geometry = MinimapGeometry(grid_width, grid_height, self.__dimensions)
        self.__renderer = MinimapRenderer(self.__dimensions, self.__colors)
        self.__coordinate_transform = CoordinateTransform(grid_height)

        # Set initial position
        self.__geometry.set_position(position)

        # Room data storage (using dungeon coordinates as keys)
        self.__rooms: Dict[Tuple[int, int], RoomInfo] = {}
        self.__current_room: Optional[Tuple[int, int]] = None
        self.__visible = True

    @property
    def is_visible(self) -> bool:
        """Check if minimap is visible"""
        return self.__visible

    @property
    def position(self) -> Tuple[int, int]:
        """Get minimap position"""
        return self.__geometry.position

    @property
    def width(self) -> int:
        """Get minimap width"""
        return self.__geometry.width

    @property
    def height(self) -> int:
        """Get minimap height"""
        return self.__geometry.height

    def set_position(self, position: Tuple[int, int]) -> None:
        """Set minimap position"""
        self.__geometry.set_position(position)

    def toggle_visibility(self) -> None:
        """Toggle minimap visibility"""
        self.__visible = not self.__visible

    def set_visibility(self, visible: bool) -> None:
        """Set minimap visibility"""
        if not isinstance(visible, bool):
            raise TypeError("visible must be a boolean")
        self.__visible = visible

    def add_room(self, dungeon_pos: Tuple[int, int], room_type: RoomDisplayType = RoomDisplayType.NORMAL) -> None:
        """
        Add a room to the minimap

        Args:
            dungeon_pos: (row, col) position in dungeon grid
            room_type: Type of room for visual representation
        """
        if not isinstance(dungeon_pos, tuple) or len(dungeon_pos) != 2:
            raise ValueError("dungeon_pos must be a tuple of (row, col)")

        if not self.__geometry.is_valid_dungeon_position(dungeon_pos):
            raise ValueError(f"Dungeon position {dungeon_pos} is outside valid range")

        if dungeon_pos not in self.__rooms:
            # Convert to minimap coordinates for the RoomInfo
            minimap_coord = self.__coordinate_transform.dungeon_to_minimap(dungeon_pos)
            self.__rooms[dungeon_pos] = RoomInfo(minimap_coord, room_type)

    def set_room_type(self, dungeon_pos: Tuple[int, int], room_type: RoomDisplayType) -> None:
        """Set the type of a room"""
        if dungeon_pos in self.__rooms:
            self.__rooms[dungeon_pos].set_room_type(room_type)
        else:
            raise KeyError(f"Room at {dungeon_pos} does not exist")

    def mark_room_visited(self, dungeon_pos: Tuple[int, int]) -> None:
        """
        Mark a room as visited

        Args:
            dungeon_pos: (row, col) position in dungeon grid
        """
        if dungeon_pos in self.__rooms:
            self.__rooms[dungeon_pos].mark_visited()
        else:
            # Auto-create room if it doesn't exist
            self.add_room(dungeon_pos)
            self.__rooms[dungeon_pos].mark_visited()

    def set_current_room(self, dungeon_pos: Optional[Tuple[int, int]]) -> None:
        """
        Set the current room position

        Args:
            dungeon_pos: (row, col) position of current room, or None
        """
        if dungeon_pos is None:
            self.__current_room = None
        else:
            if not isinstance(dungeon_pos, tuple) or len(dungeon_pos) != 2:
                raise ValueError("dungeon_pos must be a tuple of (row, col) or None")

            if not self.__geometry.is_valid_dungeon_position(dungeon_pos):
                raise ValueError(f"Dungeon position {dungeon_pos} is outside valid range")

            self.__current_room = dungeon_pos
            # Automatically mark current room as visited
            self.mark_room_visited(dungeon_pos)

    def add_door_connection(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        """
        Add a door connection between two rooms

        Args:
            from_pos: (row, col) position of source room
            to_pos: (row, col) position of destination room
        """
        # Ensure both rooms exist
        if from_pos not in self.__rooms:
            self.add_room(from_pos)
        if to_pos not in self.__rooms:
            self.add_room(to_pos)

        # Calculate direction vector in dungeon coordinates
        direction = (to_pos[0] - from_pos[0], to_pos[1] - from_pos[1])
        rotated_direction = self.__rotate_direction_90_clockwise(direction)
        self.__rooms[from_pos].add_connection(rotated_direction)

    def get_visited_room_count(self) -> int:
        """Get number of visited rooms"""
        return sum(1 for room in self.__rooms.values() if room.is_visited)

    def get_total_room_count(self) -> int:
        """Get total number of rooms"""
        return len(self.__rooms)

    def clear_all_rooms(self) -> None:
        """Clear all room data"""
        self.__rooms.clear()
        self.__current_room = None

    def draw(self, surface: pygame.Surface) -> Optional[pygame.Rect]:
        """
        Draw the minimap

        Args:
            surface: Surface to draw on

        Returns:
            Rectangle representing the drawn minimap area, or None if not visible
        """
        if not self.__visible:
            return None

        minimap_rect = self.__geometry.get_bounding_rect()

        # Draw background
        self.__renderer.render_background(surface, minimap_rect)

        # Draw door connections first (so they appear behind rooms)
        self.__draw_door_connections(surface)

        # Draw rooms
        self.__draw_rooms(surface)

        return minimap_rect

    def __draw_rooms(self, surface: pygame.Surface) -> None:
        """Draw all rooms"""
        for dungeon_pos, room_info in self.__rooms.items():
            if room_info.is_visited:
                screen_pos = self.__geometry.get_room_screen_position(dungeon_pos)
                is_current = (self.__current_room is not None and dungeon_pos == self.__current_room)

                self.__renderer.render_room(surface, room_info, screen_pos, is_current)

    def __draw_door_connections(self, surface: pygame.Surface) -> None:
        """Draw door connections between visited rooms"""
        for dungeon_pos, room_info in self.__rooms.items():
            if not room_info.is_visited:
                continue

            from_pos = self.__geometry.get_room_screen_position(dungeon_pos)

            for direction in room_info.connected_directions:
                # Calculate destination coordinate in dungeon space
                dest_dungeon_pos = (dungeon_pos[0] + direction[0], dungeon_pos[1] + direction[1])

                # Only draw if destination room exists and is visited
                if (dest_dungeon_pos in self.__rooms and
                    self.__rooms[dest_dungeon_pos].is_visited):

                    to_pos = self.__geometry.get_room_screen_position(dest_dungeon_pos)
                    self.__renderer.render_door_connection(surface, from_pos, to_pos)
    @staticmethod
    def __rotate_direction_90_clockwise(direction: Tuple[int, int]) -> Tuple[int, int]:
        """
        Rotate a direction vector (row_offset, col_offset) 90 degrees clockwise.
        (dr, dc) → (dc, -dr)
        """
        dr, dc = direction
        return (dc, -dr)


class MinimapIntegration:
    """
    Integration helper for connecting minimap with dungeon management systems
    Provides high-level interface for common operations
    """

    def __init__(self, minimap: DungeonMinimap, ui_font: pygame.font.Font = None):
        if not isinstance(minimap, DungeonMinimap):
            raise TypeError("minimap must be a DungeonMinimap instance")
        self.__minimap = minimap

        # Create UI manager if font provided
        if ui_font:
            self.__ui_manager = MinimapUIManager(ui_font)
        else:
            # Create default font
            pygame.font.init()
            default_font = pygame.font.Font(None, 24)
            self.__ui_manager = MinimapUIManager(default_font)

    def sync_with_dungeon_manager(self, dungeon_manager) -> None:
        """
        Synchronize minimap with a dungeon manager

        Args:
            dungeon_manager: Dungeon manager instance with grid access
        """
        # Clear existing data
        self.__minimap.clear_all_rooms()

        # Get dungeon dimensions
        grid_width = dungeon_manager.get_dungeon_width()
        grid_height = dungeon_manager.get_dungeon_height()

        # Scan all possible positions for rooms
        for row in range(grid_height):
            for col in range(grid_width):
                room = dungeon_manager.get_room_at_position((row, col))

                if room is not None:
                    # Determine room type
                    if room.is_start_room():
                        room_type = RoomDisplayType.START
                    elif room.is_boss_room():
                        room_type = RoomDisplayType.BOSS
                    else:
                        room_type = RoomDisplayType.NORMAL

                    # Add room to minimap using dungeon coordinates
                    self.__minimap.add_room((row, col), room_type)

                    # Add door connections
                    self.__add_room_doors(room, (row, col))

        # Set current room
        current_pos = dungeon_manager.get_current_room_position()
        if current_pos:
            self.__minimap.set_current_room(current_pos)

    def __add_room_doors(self, room, room_pos: Tuple[int, int]) -> None:
        """Add door connections for a room"""
        # Direction mappings for your Direction enum
        # Your enum values are (row_offset, col_offset)
        for direction, door in room.doors.items():
            direction_offset = direction.value  # This gets the (row_offset, col_offset) tuple
            dest_pos = door.dest_room
            self.__minimap.add_door_connection(room_pos, dest_pos)

    def update_player_position(self, dungeon_manager) -> None:
        """
        Update player position in minimap

        Args:
            dungeon_manager: Dungeon manager instance
        """
        current_pos = dungeon_manager.get_current_room_position()
        if current_pos:
            self.__minimap.set_current_room(current_pos)

    def draw_with_ui(self, surface: pygame.Surface) -> Optional[pygame.Rect]:
        """
        Draw minimap with UI elements

        Args:
            surface: Surface to draw on

        Returns:
            Rectangle representing the drawn minimap area, or None if not visible
        """
        minimap_rect = self.__minimap.draw(surface)

        if minimap_rect and self.__minimap.is_visible:
            # Get current room position for UI display
            current_pos = self.__get_current_room_position()
            if current_pos:
                # Draw room info to the right of minimap
                self.__ui_manager.render_room_info(surface, current_pos, minimap_rect)

                # Draw exploration stats
                visited_count = self.__minimap.get_visited_room_count()
                total_count = self.__minimap.get_total_room_count()
                self.__ui_manager.render_exploration_stats(surface, visited_count, total_count, minimap_rect)

                # Draw toggle instruction
                self.__ui_manager.render_toggle_instruction(surface, minimap_rect)

        return minimap_rect

    def __get_current_room_position(self) -> Optional[Tuple[int, int]]:
        """Get current room position from minimap"""
        # Access the private variable through the minimap's public interface
        # Since we don't have a getter, we'll track it through the integration
        # This is a design limitation we could improve
        return getattr(self.__minimap, '_DungeonMinimap__current_room', None)

    def toggle_visibility(self) -> None:
        """Toggle minimap visibility"""
        self.__minimap.toggle_visibility()

    def mark_room_discovered(self, grid_pos: Tuple[int, int]) -> None:
        """Mark a room as discovered/visited"""
        self.__minimap.mark_room_visited(grid_pos)

    def set_room_special_type(self, grid_pos: Tuple[int, int], room_type: RoomDisplayType) -> None:
        """Set special type for a room (treasure, locked, etc.)"""
        self.__minimap.set_room_type(grid_pos, room_type)


