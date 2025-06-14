import pygame
import math
from enum import Enum
from typing import Tuple, Optional

class PotionType(Enum):
    """
    Enumeration of potion types available in the game.

    Defines the different types of potions that can be collected and used.
    """
    HEALING = "healing"

class Potion:
    """
    Represents a collectible healing potion in the game world.

    A potion is a visual game object that can be collected by the player.
    It features animated effects including glowing, floating, and rotation.
    Once collected, the potion becomes invisible and cannot be collected again.
    """

    def __init__(self, potion_type: PotionType, x: int, y: int):
        """
        Initializes a new potion instance.

        @param potion_type The type of potion this represents
        @param x The X position in the room where the potion is placed
        @param y The Y position in the room where the potion is placed
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
        self.__rect = pygame.Rect(self.__x - self.__size // 2, self.__y - self.__size // 2,
                                  self.__size, self.__size)

        # Visual properties
        self.__base_color = self.__get_potion_color()
        self.__glow_color = self.__get_glow_color()

    def __get_potion_color(self) -> Tuple[int, int, int]:
        """
        Determines the base color for the potion based on its type.

        @return RGB color tuple representing the potion's base color
        """
        colors = {
            PotionType.HEALING: (255, 100, 100),  # Red
        }
        return colors.get(self.__potion_type, (150, 150, 150))

    def __get_glow_color(self) -> Tuple[int, int, int]:
        """
        Calculates the glow color for visual effects by brightening the base color.

        @return RGB color tuple representing the potion's glow color
        """
        base = self.__base_color
        return (min(255, base[0] + 50), min(255, base[1] + 50), min(255, base[2] + 50))

    @property
    def potion_type(self) -> PotionType:
        """
        Gets the type of this potion.

        @return The potion type enum value
        """
        return self.__potion_type

    @property
    def name(self) -> str:
        """
        Gets the human-readable name of the potion.

        @return String representation of the potion type
        """
        return self.__potion_type.value

    @property
    def is_collected(self) -> bool:
        """
        Checks whether this potion has been collected by the player.

        @return True if the potion has been collected, false otherwise
        """
        return self.__collected

    @property
    def rect(self) -> pygame.Rect:
        """
        Gets a copy of the collision rectangle for this potion.

        @return Copy of the pygame.Rect used for collision detection
        """
        return self.__rect.copy()

    @property
    def x(self) -> int:
        """
        Gets the X coordinate of the potion's position.

        @return X position in pixels
        """
        return self.__x

    @property
    def y(self) -> int:
        """
        Gets the Y coordinate of the potion's position.

        @return Y position in pixels
        """
        return self.__y

    def check_collision(self, entity_rect: pygame.Rect) -> bool:
        """
        Determines if an entity's rectangle collides with this potion.

        Only returns true if the potion hasn't been collected yet.

        @param entity_rect The collision rectangle of the entity to check against
        @return True if collision is detected and potion is not collected
        """
        if self.__collected:
            return False
        return self.__rect.colliderect(entity_rect)

    def collect(self) -> bool:
        """
        Attempts to collect this potion.

        Marks the potion as collected if it hasn't been collected already.

        @return True if the potion was successfully collected, false if already collected
        """
        if not self.__collected:
            self.__collected = True
            return True
        return False

    def update(self, dt: float):
        """
        Updates the potion's animation state.

        Handles glow effects, floating animation, and rotation based on elapsed time.

        @param dt Delta time in seconds since the last update
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
        Renders the potion as a triangle with visual effects.

        Draws glow effects, the main triangle shape, and a type indicator letter.
        Does nothing if the potion has been collected.

        @param surface The pygame surface to draw the potion on
        @param camera_offset Camera offset tuple for scrolling support
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
            (center_x, center_y - self.__size // 2),  # Top point
            (center_x - self.__size // 2, center_y + self.__size // 2),  # Bottom left
            (center_x + self.__size // 2, center_y + self.__size // 2)  # Bottom right
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
    """
    Manages the collection, tracking, and usage of potions throughout the game.

    This class handles potion placement in rooms, collision detection with the player,
    inventory management, and UI display. It maintains separate tracking for potions
    by room and overall collection statistics.
    """

    def __init__(self):
        """
        Initializes a new potion manager with empty collections and zero counters.
        """
        self.__potions_by_room = {}  # Dict[Tuple[int, int], List[Potion]]
        self.__collected_potions = {}  # Dict[Tuple[int, int], List[PotionType]] - by room
        self.__total_potions_spawned = 0
        self.__healing_potions_collected = 0
        self.__consumable_potions = 0  # Track potions available for use

    @property
    def collected_count(self) -> int:
        """
        Gets the total number of potions collected across all rooms.

        @return Total count of collected potions
        """
        total = 0
        for room_potions in self.__collected_potions.values():
            total += len(room_potions)
        return total

    @property
    def total_count(self) -> int:
        """
        Gets the total number of potions that have been spawned in the dungeon.

        @return Total count of potions in the game world
        """
        return self.__total_potions_spawned

    @property
    def healing_potions_collected(self) -> int:
        """
        Gets the number of healing potions that have been collected.

        @return Count of healing potions collected
        """
        return self.__healing_potions_collected

    @property
    def consumable_potions(self) -> int:
        """
        Gets the number of potions available for consumption by the player.

        @return Count of potions in the player's usable inventory
        """
        return self.__consumable_potions

    def has_collected_in_room(self, room_pos: Tuple[int, int], potion_type: PotionType) -> bool:
        """
        Checks if a specific type of potion has been collected in a given room.

        @param room_pos The room coordinates to check
        @param potion_type The type of potion to look for
        @return True if the specified potion type has been collected in that room
        """
        room_potions = self.__collected_potions.get(room_pos, [])
        return potion_type in room_potions

    def get_collected_potions_in_room(self, room_pos: Tuple[int, int]) -> list:
        """
        Retrieves a list of all potion types collected in a specific room.

        @param room_pos The room coordinates to query
        @return Copy of the list containing collected potion types for that room
        """
        return self.__collected_potions.get(room_pos, []).copy()

    def add_potion_to_room(self, room_pos: Tuple[int, int], potion: Potion):
        """
        Adds a potion to a specific room and increments the total spawn counter.

        @param room_pos The room coordinates where the potion should be placed
        @param potion The potion instance to add to the room
        """
        if room_pos not in self.__potions_by_room:
            self.__potions_by_room[room_pos] = []
        self.__potions_by_room[room_pos].append(potion)
        self.__total_potions_spawned += 1

    def get_potions_in_room(self, room_pos: Tuple[int, int]) -> list:
        """
        Retrieves all potions present in a specific room.

        @param room_pos The room coordinates to query
        @return List of potion instances in the specified room
        """
        return self.__potions_by_room.get(room_pos, [])

    def check_potion_collection(self, room_pos: Tuple[int, int], player_rect: pygame.Rect) -> Optional[Potion]:
        """
        Checks if the player collides with any potion in the current room and handles collection.

        Updates collection statistics and inventory when a potion is collected.

        @param room_pos The current room coordinates
        @param player_rect The player's collision rectangle
        @return The collected potion instance if any, None otherwise
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
        Consumes one healing potion from the player's inventory if available.

        @return True if a potion was successfully used, false if no potions available
        """
        if self.__consumable_potions > 0:
            self.__consumable_potions -= 1
            return True
        return False

    def update_potions_in_room(self, room_pos: Tuple[int, int], dt: float):
        """
        Updates the animation state of all potions in a specific room.

        @param room_pos The room coordinates containing potions to update
        @param dt Delta time in seconds since the last update
        """
        potions = self.get_potions_in_room(room_pos)
        for potion in potions:
            potion.update(dt)

    def draw_potions_in_room(self, room_pos: Tuple[int, int], surface: pygame.Surface,
                             camera_offset: Tuple[int, int] = (0, 0)):
        """
        Renders all potions in a specific room to the given surface.

        @param room_pos The room coordinates containing potions to draw
        @param surface The pygame surface to render potions on
        @param camera_offset Camera offset tuple for scrolling support
        """
        potions = self.get_potions_in_room(room_pos)
        for potion in potions:
            potion.draw(surface, camera_offset)

    def draw_collection_ui(self, surface: pygame.Surface, x: int, y: int):
        """
        Renders the potion collection user interface showing available potions.

        Displays a background panel with the current count of consumable healing potions.

        @param surface The pygame surface to draw the UI on
        @param x The X position for the UI panel
        @param y The Y position for the UI panel
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