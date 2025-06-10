"""
Room Transition Manager - Handles smooth transitions between rooms
"""
import pygame
from typing import Tuple, Optional, Callable
from enum import Enum


class TransitionType(Enum):
    """Types of room transitions"""
    FADE = "fade"
    SLIDE = "slide"
    INSTANT = "instant"


class RoomTransitionManager:
    """Manages transitions between dungeon rooms with proper encapsulation"""

    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize transition manager

        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.__screen_width = screen_width
        self.__screen_height = screen_height
        self.__is_transitioning = False
        self.__transition_type = TransitionType.INSTANT
        self.__transition_progress = 0.0
        self.__transition_duration = 0.5  # seconds
        self.__transition_timer = 0.0
        self.__transition_callback: Optional[Callable] = None
        self.__fade_surface = None

    def start_transition(self,
                         transition_type: TransitionType = TransitionType.FADE,
                         duration: float = 0.5,
                         callback: Optional[Callable] = None):
        """
        Start a room transition

        Args:
            transition_type: Type of transition to perform
            duration: Duration of transition in seconds
            callback: Function to call when transition is halfway through
        """
        if self.__is_transitioning:
            return  # Already transitioning

        self.__is_transitioning = True
        self.__transition_type = transition_type
        self.__transition_duration = duration
        self.__transition_timer = 0.0
        self.__transition_progress = 0.0
        self.__transition_callback = callback

        # Prepare transition-specific resources
        if transition_type == TransitionType.FADE:
            self.__fade_surface = pygame.Surface((self.__screen_width, self.__screen_height))
            self.__fade_surface.set_alpha(0)
            self.__fade_surface.fill((0, 0, 0))

    def update(self, dt: float):
        """
        Update transition state

        Args:
            dt: Delta time in seconds
        """
        if not self.__is_transitioning:
            return

        self.__transition_timer += dt
        self.__transition_progress = min(1.0, self.__transition_timer / self.__transition_duration)

        # Call callback at midpoint of transition
        if (self.__transition_progress >= 0.5 and
                self.__transition_callback and
                hasattr(self, '_callback_called') == False):
            self._callback_called = True
            self.__transition_callback()

        # End transition when complete
        if self.__transition_progress >= 1.0:
            self.__end_transition()

    def __end_transition(self):
        """End the current transition"""
        self.__is_transitioning = False
        self.__transition_callback = None
        self.__fade_surface = None
        if hasattr(self, '_callback_called'):
            delattr(self, '_callback_called')

    def draw_transition(self, screen: pygame.Surface):
        """
        Draw transition effect on screen

        Args:
            screen: Surface to draw transition on
        """
        if not self.__is_transitioning:
            return

        if self.__transition_type == TransitionType.FADE:
            self.__draw_fade_transition(screen)
        elif self.__transition_type == TransitionType.SLIDE:
            # Could implement slide transition here
            pass

    def __draw_fade_transition(self, screen: pygame.Surface):
        """Draw fade transition effect"""
        if not self.__fade_surface:
            return

        # Calculate alpha based on progress
        # Fade out to black, then fade in from black
        if self.__transition_progress <= 0.5:
            # Fading out (0 -> 255)
            alpha = int(255 * (self.__transition_progress * 2))
        else:
            # Fading in (255 -> 0)
            alpha = int(255 * (2 - self.__transition_progress * 2))

        self.__fade_surface.set_alpha(alpha)
        screen.blit(self.__fade_surface, (0, 0))

    @property
    def is_transitioning(self) -> bool:
        """Check if currently transitioning"""
        return self.__is_transitioning

    @property
    def transition_progress(self) -> float:
        """Get current transition progress (0.0 to 1.0)"""
        return self.__transition_progress


class DoorInteractionManager:
    """Manages door interactions and requirements"""

    def __init__(self):
        """Initialize door interaction manager"""
        self.__door_requirements: dict = {}
        self.__player_inventory: set = set()

    def set_door_requirement(self, room_pos: Tuple[int, int], direction, requirement: str):
        """
        Set a requirement for a door

        Args:
            room_pos: Position of room containing the door
            direction: Direction of the door
            requirement: Requirement string (e.g., "key_red", "pillar_count_5")
        """
        door_key = (room_pos, direction)
        self.__door_requirements[door_key] = requirement

    def add_to_inventory(self, item: str):
        """Add an item to player inventory"""
        self.__player_inventory.add(item)

    def remove_from_inventory(self, item: str):
        """Remove an item from player inventory"""
        self.__player_inventory.discard(item)

    def can_use_door(self, room_pos: Tuple[int, int], direction) -> bool:
        """
        Check if player can use a specific door

        Args:
            room_pos: Position of room containing the door
            direction: Direction of the door

        Returns:
            True if door can be used
        """
        door_key = (room_pos, direction)
        requirement = self.__door_requirements.get(door_key)

        if not requirement:
            return True  # No requirement

        # Check different types of requirements
        if requirement.startswith("key_"):
            return requirement in self.__player_inventory
        elif requirement.startswith("pillar_count_"):
            required_count = int(requirement.split("_")[-1])
            pillar_count = len([item for item in self.__player_inventory if item.startswith("pillar")])
            return pillar_count >= required_count

        return False

    def get_door_requirement_message(self, room_pos: Tuple[int, int], direction) -> Optional[str]:
        """
        Get a message explaining why a door can't be used

        Args:
            room_pos: Position of room containing the door
            direction: Direction of the door

        Returns:
            Message string or None if door can be used
        """
        if self.can_use_door(room_pos, direction):
            return None

        door_key = (room_pos, direction)
        requirement = self.__door_requirements.get(door_key, "")

        if requirement.startswith("key_"):
            key_color = requirement.split("_")[1].title()
            return f"Requires {key_color} Key"
        elif requirement.startswith("pillar_count_"):
            required_count = int(requirement.split("_")[-1])
            return f"Collect {required_count} Pillars to proceed"

        return "Door is locked"


