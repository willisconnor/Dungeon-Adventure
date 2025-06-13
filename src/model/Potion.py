import pygame
import math
from enum import Enum
from typing import Tuple, Optional

class PotionType(Enum):
    """Enumeration of potion types"""
    HEALING = "healing"

class Potion:
    """Represents a collectible healing potion"""

    def __init__(self, potion_type: PotionType, x: int, y: int):
        """
        Initialize a potion

        Args:
            potion_type: Type of potion this represents
            x: X position in the room
            y: Y position in the room
        """
        # Private attributes with proper encapsulation
        self.__potion_type = potion_type
        self.__x = x
        self.__y = y
        self.__size = 24  # Size of the triangle
        self.__collected = False
        self.__glow_timer = 0.0
        self.__float_offset = 0.0
        self.__rotation = 0.0

        # Create collision rectangle (slightly larger than triangle for easier collection)
        self.__rect = pygame.Rect(self.__x - self.__size//2, self.__y - self.__size//2, 
                                 self.__size, self.__size)

        # Visual properties
        self.__base_color = self.__get_potion_color()
        self.__glow_color = self.__get_glow_color()

    def __get_potion_color(self) -> Tuple[int, int, int]:
        """Get base color based on potion type"""
        colors = {
            PotionType.HEALING: (255, 100, 100),    # Red
        }
        return colors.get(self.__potion_type, (150, 150, 150))

    def __get_glow_color(self) -> Tuple[int, int, int]:
        """Get glow color for visual effect"""
        base = self.__base_color
        return (min(255, base[0] + 50), min(255, base[1] + 50), min(255, base[2] + 50))

    @property
    def potion_type(self) -> PotionType:
        """Get the potion type (read-only)"""
        return self.__potion_type

    @property
    def name(self) -> str:
        """Get the potion name (read-only)"""
        return self.__potion_type.value

    @property
    def is_collected(self) -> bool:
        """Check if potion has been collected (read-only)"""
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
        Check if entity collides with this potion

        Args:
            entity_rect: Rectangle of the entity to check

        Returns:
            True if collision detected and potion not yet collected
        """
        if self.__collected:
            return False
        return self.__rect.colliderect(entity_rect)

    def collect(self) -> bool:
        """
        Collect the potion

        Returns:
            True if successfully collected, False if already collected
        """
        if not self.__collected:
            self.__collected = True
            return True
        return False

    def update(self, dt: float):
        """
        Update potion animation

        Args:
            dt: Delta time in seconds
        """
        if not self.__collected:
            # Update glow effect
            self.__glow_timer += dt * 3

            # Update floating animation
            self.__float_offset = math.sin(self.__glow_timer) * 3

            # Update rotation
            self.__rotation += dt * 2

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Draw the potion as a triangle

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
        glow_radius = int(self.__size * 0.8 + glow_intensity * 8)

        # Draw outer glow
        for i in range(3):
            alpha = 40 - i * 12
            radius = glow_radius + i * 4
            glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface,
                (*self.__glow_color, alpha),
                (radius, radius),
                radius
            )
            surface.blit(
                glow_surface,
                (draw_x - radius, draw_y - radius)
            )

        # Create a surface for the triangle to enable rotation
        triangle_surface = pygame.Surface((self.__size * 2, self.__size * 2), pygame.SRCALPHA)
        
        # Calculate triangle points (pointing up)
        center_x, center_y = self.__size, self.__size
        points = [
            (center_x, center_y - self.__size//2),  # Top point
            (center_x - self.__size//2, center_y + self.__size//2),  # Bottom left
            (center_x + self.__size//2, center_y + self.__size//2)   # Bottom right
        ]

        # Draw triangle
        pygame.draw.polygon(triangle_surface, self.__base_color, points)
        
        # Draw triangle outline
        pygame.draw.polygon(triangle_surface, (255, 255, 255), points, 2)

        # Rotate the triangle surface
        rotated_surface = pygame.transform.rotate(triangle_surface, self.__rotation)
        
        # Get the rect of the rotated surface and center it
        rotated_rect = rotated_surface.get_rect(center=(draw_x, draw_y))
        
        # Draw the rotated triangle
        surface.blit(rotated_surface, rotated_rect)

        # Draw potion type initial
        font = pygame.font.Font(None, 20)
        initial = self.__potion_type.value[0].upper()
        text = font.render(initial, True, (255, 255, 255))
        text_rect = text.get_rect(center=(draw_x, draw_y))
        surface.blit(text, text_rect)


class PotionManager:
    """Manages potion collection and tracking"""

    def __init__(self):
        """Initialize the potion manager"""
        self.__potions_by_room = {}  # Dict[Tuple[int, int], List[Potion]]
        self.__collected_potions = {}  # Dict[Tuple[int, int], List[PotionType]] - by room
        self.__total_potions_spawned = 0
        self.__healing_potions_collected = 0
        self.__consumable_potions = 0  # Track potions available for use

    @property
    def collected_count(self) -> int:
        """Get number of potions collected"""
        total = 0
        for room_potions in self.__collected_potions.values():
            total += len(room_potions)
        return total

    @property
    def total_count(self) -> int:
        """Get total number of potions in dungeon"""
        return self.__total_potions_spawned

    @property
    def healing_potions_collected(self) -> int:
        """Get number of healing potions collected"""
        return self.__healing_potions_collected

    @property
    def consumable_potions(self) -> int:
        """Get number of potions available for use"""
        return self.__consumable_potions

    def has_collected_in_room(self, room_pos: Tuple[int, int], potion_type: PotionType) -> bool:
        """Check if specific potion type has been collected in a room"""
        room_potions = self.__collected_potions.get(room_pos, [])
        return potion_type in room_potions

    def get_collected_potions_in_room(self, room_pos: Tuple[int, int]) -> list:
        """Get list of collected potion types in a room"""
        return self.__collected_potions.get(room_pos, []).copy()

    def add_potion_to_room(self, room_pos: Tuple[int, int], potion: Potion):
        """Add a potion to a specific room"""
        if room_pos not in self.__potions_by_room:
            self.__potions_by_room[room_pos] = []
        self.__potions_by_room[room_pos].append(potion)
        self.__total_potions_spawned += 1

    def get_potions_in_room(self, room_pos: Tuple[int, int]) -> list:
        """Get all potions in a specific room"""
        return self.__potions_by_room.get(room_pos, [])

    def check_potion_collection(self, room_pos: Tuple[int, int], player_rect: pygame.Rect) -> Optional[Potion]:
        """
        Check if player collects any potion in the room

        Args:
            room_pos: Current room position
            player_rect: Player's collision rectangle

        Returns:
            Collected potion if any, None otherwise
        """
        potions = self.get_potions_in_room(room_pos)

        for potion in potions:
            if potion.check_collision(player_rect):
                if potion.collect():
                    # Track collection by room
                    if room_pos not in self.__collected_potions:
                        self.__collected_potions[room_pos] = []
                    self.__collected_potions[room_pos].append(potion.potion_type)
                    
                    # Track healing potions specifically
                    if potion.potion_type == PotionType.HEALING:
                        self.__healing_potions_collected += 1
                        self.__consumable_potions += 1  # Add to consumable inventory
                    
                    return potion

        return None

    def use_healing_potion(self) -> bool:
        """
        Use a healing potion if available
        
        Returns:
            True if potion was used, False if no potions available
        """
        if self.__consumable_potions > 0:
            self.__consumable_potions -= 1
            return True
        return False

    def update_potions_in_room(self, room_pos: Tuple[int, int], dt: float):
        """Update all potions in a room"""
        potions = self.get_potions_in_room(room_pos)
        for potion in potions:
            potion.update(dt)

    def draw_potions_in_room(self, room_pos: Tuple[int, int], surface: pygame.Surface,
                            camera_offset: Tuple[int, int] = (0, 0)):
        """Draw all potions in a room"""
        potions = self.get_potions_in_room(room_pos)
        for potion in potions:
            potion.draw(surface, camera_offset)

    def draw_collection_ui(self, surface: pygame.Surface, x: int, y: int):
        """
        Draw potion collection UI

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

        # Draw potion count
        text = f"Healing Potions: {self.consumable_potions}"
        potion_text = font.render(text, True, (255, 255, 255))
        surface.blit(potion_text, (x + 10, y + 5)) 