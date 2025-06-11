import pygame
import math
from enum import Enum
from typing import Tuple, Optional

class PillarType(Enum):
    """Enumeration of OOP pillar types"""
    ENCAPSULATION = "Encapsulation"
    INHERITANCE = "Inheritance"
    POLYMORPHISM = "Polymorphism"
    ABSTRACTION = "Abstraction"
    COMPOSITION = "Composition"

class Pillar:
    """Represents a collectible OOP concept pillar"""

    def __init__(self, pillar_type: PillarType, x: int, y: int):
        """
        Initialize a pillar

        Args:
            pillar_type: Type of OOP concept this pillar represents
            x: X position in the room
            y: Y position in the room
        """
        # Private attributes with proper encapsulation
        self.__pillar_type = pillar_type
        self.__x = x
        self.__y = y
        self.__width = 32
        self.__height = 64
        self.__collected = False
        self.__glow_timer = 0.0
        self.__float_offset = 0.0

        # Create collision rectangle
        self.__rect = pygame.Rect(self.__x, self.__y, self.__width, self.__height)

        # Visual properties
        self.__base_color = self.__get_pillar_color()
        self.__glow_color = self.__get_glow_color()

    def __get_pillar_color(self) -> Tuple[int, int, int]:
        """Get base color based on pillar type"""
        colors = {
            PillarType.ENCAPSULATION: (100, 150, 200),  # Blue
            PillarType.INHERITANCE: (200, 100, 150),     # Pink
            PillarType.POLYMORPHISM: (150, 200, 100),   # Green
            PillarType.ABSTRACTION: (200, 150, 100),    # Orange
            PillarType.COMPOSITION: (150, 100, 200)     # Purple
        }
        return colors.get(self.__pillar_type, (150, 150, 150))

    def __get_glow_color(self) -> Tuple[int, int, int]:
        """Get glow color for visual effect"""
        base = self.__base_color
        return (min(255, base[0] + 50), min(255, base[1] + 50), min(255, base[2] + 50))

    @property
    def pillar_type(self) -> PillarType:
        """Get the pillar type (read-only)"""
        return self.__pillar_type

    @property
    def name(self) -> str:
        """Get the pillar name (read-only)"""
        return self.__pillar_type.value

    @property
    def is_collected(self) -> bool:
        """Check if pillar has been collected (read-only)"""
        return self.__collected

    @property
    def rect(self) -> pygame.Rect:
        """Get collision rectangle (copy to prevent modification)"""
        return self.__rect.copy()

    @property
    def x(self) -> int:
        """Get X position"""
        return self.__x

    @property
    def y(self) -> int:
        """Get Y position"""
        return self.__y

    def check_collision(self, entity_rect: pygame.Rect) -> bool:
        """
        Check if entity collides with this pillar

        Args:
            entity_rect: Rectangle of the entity to check

        Returns:
            True if collision detected and pillar not yet collected
        """
        if self.__collected:
            return False
        return self.__rect.colliderect(entity_rect)

    def collect(self) -> bool:
        """
        Collect the pillar

        Returns:
            True if successfully collected, False if already collected
        """
        if not self.__collected:
            self.__collected = True
            return True
        return False

    def update(self, dt: float):
        """
        Update pillar animation

        Args:
            dt: Delta time in seconds
        """
        if not self.__collected:
            # Update glow effect
            self.__glow_timer += dt * 2

            # Update floating animation
            self.__float_offset = math.sin(self.__glow_timer) * 5

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Draw the pillar

        Args:
            surface: Surface to draw on
            camera_offset: Camera offset for scrolling
        """
        if self.__collected:
            return

        draw_x = self.__x - camera_offset[0]
        draw_y = self.__y - camera_offset[1] + self.__float_offset

        # Draw glow effect
        glow_intensity = (math.sin(self.__glow_timer) + 1) / 2
        glow_radius = int(self.__width * 0.8 + glow_intensity * 10)

        # Draw outer glow
        for i in range(3):
            alpha = 50 - i * 15
            radius = glow_radius + i * 5
            glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface,
                (*self.__glow_color, alpha),
                (radius, radius),
                radius
            )
            surface.blit(
                glow_surface,
                (draw_x + self.__width // 2 - radius, draw_y + self.__height // 2 - radius)
            )

        # Draw pillar base
        pillar_rect = pygame.Rect(draw_x, draw_y, self.__width, self.__height)
        pygame.draw.rect(surface, self.__base_color, pillar_rect)

        # Draw pillar highlight
        highlight_rect = pygame.Rect(draw_x + 2, draw_y + 2, self.__width - 4, 10)
        pygame.draw.rect(surface, self.__glow_color, highlight_rect)

        # Draw pillar outline
        pygame.draw.rect(surface, (255, 255, 255), pillar_rect, 2)

        # Draw pillar type initial
        font = pygame.font.Font(None, 24)
        initial = self.__pillar_type.value[0]
        text = font.render(initial, True, (255, 255, 255))
        text_rect = text.get_rect(center=(draw_x + self.__width // 2, draw_y + self.__height // 2))
        surface.blit(text, text_rect)


class PillarManager:
    """Manages pillar collection and tracking"""

    def __init__(self):
        """Initialize the pillar manager"""
        self.__pillars_by_room = {}  # Dict[Tuple[int, int], List[Pillar]]
        self.__collected_pillars = set()  # Set of PillarType
        self.__total_pillars_spawned = 0

    @property
    def collected_count(self) -> int:
        """Get number of pillars collected"""
        return len(self.__collected_pillars)

    @property
    def total_count(self) -> int:
        """Get total number of pillars in dungeon"""
        return self.__total_pillars_spawned

    def has_collected(self, pillar_type: PillarType) -> bool:
        """Check if specific pillar type has been collected"""
        return pillar_type in self.__collected_pillars

    def get_collected_pillars(self) -> list:
        """Get list of collected pillar types"""
        return list(self.__collected_pillars)

    def can_access_boss_room(self) -> bool:
        """Check if player has enough pillars to access boss room"""
        return self.collected_count >= 4

    def add_pillar_to_room(self, room_pos: Tuple[int, int], pillar: Pillar):
        """Add a pillar to a specific room"""
        if room_pos not in self.__pillars_by_room:
            self.__pillars_by_room[room_pos] = []
        self.__pillars_by_room[room_pos].append(pillar)
        self.__total_pillars_spawned += 1

    def get_pillars_in_room(self, room_pos: Tuple[int, int]) -> list:
        """Get all pillars in a specific room"""
        return self.__pillars_by_room.get(room_pos, [])

    def check_pillar_collection(self, room_pos: Tuple[int, int], player_rect: pygame.Rect) -> Optional[Pillar]:
        """
        Check if player collects any pillar in the room

        Args:
            room_pos: Current room position
            player_rect: Player's collision rectangle

        Returns:
            Collected pillar if any, None otherwise
        """
        pillars = self.get_pillars_in_room(room_pos)

        for pillar in pillars:
            if pillar.check_collision(player_rect):
                if pillar.collect():
                    self.__collected_pillars.add(pillar.pillar_type)
                    return pillar

        return None

    def update_pillars_in_room(self, room_pos: Tuple[int, int], dt: float):
        """Update all pillars in a room"""
        pillars = self.get_pillars_in_room(room_pos)
        for pillar in pillars:
            pillar.update(dt)

    def draw_pillars_in_room(self, room_pos: Tuple[int, int], surface: pygame.Surface,
                            camera_offset: Tuple[int, int] = (0, 0)):
        """Draw all pillars in a room"""
        pillars = self.get_pillars_in_room(room_pos)
        for pillar in pillars:
            pillar.draw(surface, camera_offset)

    def draw_collection_ui(self, surface: pygame.Surface, x: int, y: int):
        """
        Draw pillar collection UI

        Args:
            surface: Surface to draw on
            x: X position for UI
            y: Y position for UI
        """
        font = pygame.font.Font(None, 24)

        # Draw background
        ui_width = 250
        ui_height = 30
        bg_rect = pygame.Rect(x, y, ui_width, ui_height)
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 2)

        # Draw pillar count
        text = f"OOP Pillars: {self.collected_count}/5"
        color = (0, 255, 0) if self.can_access_boss_room() else (255, 255, 255)
        pillar_text = font.render(text, True, color)
        surface.blit(pillar_text, (x + 10, y + 5))

        # Draw individual pillar indicators
        indicator_x = x + 150
        for i, pillar_type in enumerate(PillarType):
            color = (0, 255, 0) if self.has_collected(pillar_type) else (100, 100, 100)
            indicator_rect = pygame.Rect(indicator_x + i * 20, y + 10, 10, 10)
            pygame.draw.rect(surface, color, indicator_rect)
            pygame.draw.rect(surface, (255, 255, 255), indicator_rect, 1)