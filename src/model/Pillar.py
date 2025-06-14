import pygame
import math
from enum import Enum
from typing import Tuple, Optional

class PillarType(Enum):
    """
    Represents the different types of Object-Oriented Programming concepts
    that can be collected as pillars in the game.

    Each pillar type corresponds to a fundamental OOP principle that players
    can collect to progress through the dungeon.
    """
    ENCAPSULATION = "Encapsulation"
    INHERITANCE = "Inheritance"
    POLYMORPHISM = "Polymorphism"
    ABSTRACTION = "Abstraction"
    COMPOSITION = "Composition"


class Pillar:
    """
    A collectible pillar that represents an Object-Oriented Programming concept.

    Each pillar is a glowing, animated object that players can collect by walking
    into it. Once collected, the pillar disappears and contributes to the player's
    progress toward accessing the boss room.

    The pillar features visual effects like glowing, floating animation, and
    color-coding based on the OOP concept it represents.
    """

    def __init__(self, pillar_type: PillarType, x: int, y: int):
        """
        Creates a new pillar at the specified location.

        The pillar will be initialized with appropriate colors and visual effects
        based on its type. It starts in an uncollected state and begins its
        floating animation immediately.

        Args:
            pillar_type: The OOP concept this pillar represents (affects color and display)
            x: Horizontal position in the room where the pillar should appear
            y: Vertical position in the room where the pillar should appear
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
        """
        Determines the base color for this pillar based on its type.

        Each OOP concept has its own distinctive color to help players
        visually identify what they're collecting:
        - Encapsulation: Blue (represents containment)
        - Inheritance: Pink (represents relationships)
        - Polymorphism: Green (represents flexibility)
        - Abstraction: Orange (represents simplification)
        - Composition: Purple (represents building blocks)

        Returns:
            RGB color tuple for the pillar's base appearance
        """
        colors = {
            PillarType.ENCAPSULATION: (100, 150, 200),  # Blue
            PillarType.INHERITANCE: (200, 100, 150),  # Pink
            PillarType.POLYMORPHISM: (150, 200, 100),  # Green
            PillarType.ABSTRACTION: (200, 150, 100),  # Orange
            PillarType.COMPOSITION: (150, 100, 200)  # Purple
        }
        return colors.get(self.__pillar_type, (150, 150, 150))

    def __get_glow_color(self) -> Tuple[int, int, int]:
        """
        Creates a brighter version of the base color for the glow effect.

        The glow color is used for the pillar's animated light effect and
        highlight areas. It's calculated by brightening each RGB component
        of the base color while ensuring we don't exceed the maximum value.

        Returns:
            RGB color tuple for the pillar's glow effects
        """
        base = self.__base_color
        return (min(255, base[0] + 50), min(255, base[1] + 50), min(255, base[2] + 50))

    @property
    def pillar_type(self) -> PillarType:
        """
        The OOP concept this pillar represents.

        This property is read-only to prevent external code from changing
        the pillar's fundamental identity after creation.

        Returns:
            The PillarType enum value for this pillar
        """
        return self.__pillar_type

    @property
    def name(self) -> str:
        """
        The human-readable name of the OOP concept this pillar represents.

        This is useful for displaying information to the player or in debug output.

        Returns:
            String name of the pillar type (e.g., "Encapsulation")
        """
        return self.__pillar_type.value

    @property
    def is_collected(self) -> bool:
        """
        Whether this pillar has been collected by the player.

        Once a pillar is collected, it won't be drawn and can't be collected again.
        This property is read-only to prevent external tampering with collection state.

        Returns:
            True if the pillar has been collected, False otherwise
        """
        return self.__collected

    @property
    def rect(self) -> pygame.Rect:
        """
        The collision rectangle for this pillar.

        This is used to detect when the player walks into the pillar.
        A copy is returned to prevent external code from modifying the
        pillar's collision bounds.

        Returns:
            Copy of the pillar's collision rectangle
        """
        return self.__rect.copy()

    @property
    def x(self) -> int:
        """
        The horizontal position of the pillar in the room.

        Returns:
            X coordinate in pixels
        """
        return self.__x

    @property
    def y(self) -> int:
        """
        The vertical position of the pillar in the room.

        Returns:
            Y coordinate in pixels
        """
        return self.__y

    def check_collision(self, entity_rect: pygame.Rect) -> bool:
        """
        Checks if another entity (like the player) is touching this pillar.

        This method is used to detect when the player walks into a pillar
        and should collect it. Already collected pillars won't register
        collisions since they're no longer interactive.

        Args:
            entity_rect: The collision rectangle of the entity to check against

        Returns:
            True if the entity is touching this pillar and it hasn't been collected yet
        """
        if self.__collected:
            return False
        return self.__rect.colliderect(entity_rect)

    def collect(self) -> bool:
        """
        Attempts to collect this pillar.

        When called, this marks the pillar as collected so it will no longer
        be drawn or interactive. This should typically be called when the
        player walks into the pillar.

        Returns:
            True if the pillar was successfully collected (wasn't already collected),
            False if it was already collected
        """
        if not self.__collected:
            self.__collected = True
            return True
        return False

    def update(self, dt: float):
        """
        Updates the pillar's visual animations each frame.

        This handles the glowing effect and floating animation that makes
        the pillar more visually appealing and easier to spot. The animations
        only run while the pillar hasn't been collected.

        Args:
            dt: Time elapsed since the last update, in seconds
        """
        if not self.__collected:
            # Update glow effect
            self.__glow_timer += dt * 2

            # Update floating animation
            self.__float_offset = math.sin(self.__glow_timer) * 5

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Renders the pillar on the screen with all its visual effects.

        This creates a layered visual effect with an outer glow, the main pillar
        body, highlights, and a text initial. The pillar gently floats up and
        down and pulses with a glow effect to attract the player's attention.

        Collected pillars won't be drawn at all.

        Args:
            surface: The pygame surface to draw the pillar on
            camera_offset: How much to offset the drawing position for camera scrolling.
                         Tuple of (x_offset, y_offset) in pixels.
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
    """
    Manages all the pillars in the dungeon and tracks the player's collection progress.

    This class handles spawning pillars in different rooms, checking for collections,
    updating animations, and determining when the player has collected enough pillars
    to access the boss room. It also provides a UI display for the player's progress.

    The manager organizes pillars by room location and maintains a global collection
    state that persists as the player moves between rooms.
    """

    def __init__(self):
        """
        Creates a new pillar manager with empty collections.

        The manager starts with no pillars spawned and no pillars collected.
        Pillars must be added to rooms using add_pillar_to_room() before they
        can be interacted with.
        """
        self.__pillars_by_room = {}  # Dict[Tuple[int, int], List[Pillar]]
        self.__collected_pillars = set()  # Set of PillarType
        self.__total_pillars_spawned = 0

    @property
    def collected_count(self) -> int:
        """
        The number of different pillar types the player has collected.

        This counts unique pillar types, not individual pillar instances.
        So if there are multiple Encapsulation pillars but the player has
        collected at least one, this only counts as 1 toward the total.

        Returns:
            Number of unique pillar types collected (0-5)
        """
        return len(self.__collected_pillars)

    @property
    def total_count(self) -> int:
        """
        The total number of pillar instances that have been placed in the dungeon.

        This counts every individual pillar that was spawned, regardless of type
        or whether it's been collected. Useful for debugging and statistics.

        Returns:
            Total number of pillar instances in the dungeon
        """
        return self.__total_pillars_spawned

    def has_collected(self, pillar_type: PillarType) -> bool:
        """
        Checks if the player has collected at least one pillar of the specified type.

        This is useful for checking specific prerequisites or displaying
        which OOP concepts the player has learned.

        Args:
            pillar_type: The type of pillar to check for

        Returns:
            True if the player has collected this type of pillar
        """
        return pillar_type in self.__collected_pillars

    def get_collected_pillars(self) -> list:
        """
        Gets a list of all the pillar types the player has collected.

        This returns the actual PillarType enum values, which can be used
        to display information about what the player has learned or to
        check for specific combinations of collected pillars.

        Returns:
            List of PillarType enums representing collected pillars
        """
        return list(self.__collected_pillars)

    def can_access_boss_room(self) -> bool:
        """
        Determines if the player has collected enough pillars to face the boss.

        The player needs to collect at least 4 out of 5 different pillar types
        to demonstrate sufficient understanding of OOP concepts before taking
        on the final challenge.

        Returns:
            True if the player has collected 4 or more different pillar types
        """
        return self.collected_count >= 4

    def add_pillar_to_room(self, room_pos: Tuple[int, int], pillar: Pillar):
        """
        Places a pillar in a specific room of the dungeon.

        This is typically called during dungeon generation to populate rooms
        with collectible pillars. Each room can contain multiple pillars,
        and the same pillar type can appear in multiple rooms.

        Args:
            room_pos: The room coordinates as (x, y) where the pillar should be placed
            pillar: The pillar instance to add to that room
        """
        if room_pos not in self.__pillars_by_room:
            self.__pillars_by_room[room_pos] = []
        self.__pillars_by_room[room_pos].append(pillar)
        self.__total_pillars_spawned += 1

    def get_pillars_in_room(self, room_pos: Tuple[int, int]) -> list:
        """
        Gets all the pillars that exist in a specific room.

        This is used to update and draw only the pillars that are relevant
        to the player's current location, improving performance by not
        processing pillars in distant rooms.

        Args:
            room_pos: The room coordinates to get pillars for

        Returns:
            List of Pillar objects in that room (empty list if room has no pillars)
        """
        return self.__pillars_by_room.get(room_pos, [])

    def check_pillar_collection(self, room_pos: Tuple[int, int], player_rect: pygame.Rect) -> Optional[Pillar]:
        """
        Checks if the player is touching any collectible pillars in their current room.

        This should be called each frame with the player's current position.
        If the player is touching a pillar, it will be automatically collected
        and added to their progress.

        Args:
            room_pos: The room the player is currently in
            player_rect: The player's collision rectangle

        Returns:
            The pillar that was collected if any, or None if no collection occurred
        """
        pillars = self.get_pillars_in_room(room_pos)

        for pillar in pillars:
            if pillar.check_collision(player_rect):
                if pillar.collect():
                    self.__collected_pillars.add(pillar.pillar_type)
                    return pillar

        return None

    def update_pillars_in_room(self, room_pos: Tuple[int, int], dt: float):
        """
        Updates the animations for all pillars in the specified room.

        This handles the glowing and floating effects that make pillars
        visually appealing. Only pillars in the current room need to be
        updated for performance reasons.

        Args:
            room_pos: The room whose pillars should be updated
            dt: Time elapsed since last update, in seconds
        """
        pillars = self.get_pillars_in_room(room_pos)
        for pillar in pillars:
            pillar.update(dt)

    def draw_pillars_in_room(self, room_pos: Tuple[int, int], surface: pygame.Surface,
                             camera_offset: Tuple[int, int] = (0, 0)):
        """
        Renders all the pillars in the specified room.

        This draws all the visual effects for pillars in the current room,
        including glow effects, floating animation, and the pillar bodies themselves.
        Collected pillars won't be drawn.

        Args:
            room_pos: The room whose pillars should be drawn
            surface: The pygame surface to draw on
            camera_offset: Camera scrolling offset as (x_offset, y_offset)
        """
        pillars = self.get_pillars_in_room(room_pos)
        for pillar in pillars:
            pillar.draw(surface, camera_offset)

    def draw_collection_ui(self, surface: pygame.Surface, x: int, y: int):
        """
        Draws a user interface showing the player's pillar collection progress.

        This creates a HUD element that shows how many pillars have been collected
        and provides visual indicators for each pillar type. The display changes
        color when the player has enough pillars to access the boss room.

        Args:
            surface: The pygame surface to draw the UI on
            x: Horizontal position for the UI panel
            y: Vertical position for the UI panel
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