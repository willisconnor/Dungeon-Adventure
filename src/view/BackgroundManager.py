import pygame

class BackgroundManager:
    """Handles room background image rendering with scaling and camera offset"""

    def __init__(self, image_path: str):
        """Initialize and load background image"""
        self._original_image = pygame.image.load(image_path).convert_alpha()
        self._scaled_cache = {}  # {(width, height): scaled_surface}

    def draw(self, surface: pygame.Surface, camera_offset: tuple, room_size: tuple):
        """
        Draw the background for a room with camera scrolling.

        Args:
            surface: The screen surface to draw on.
            camera_offset: (x, y) tuple representing camera scroll offset.
            room_size: (width, height) of the current room.
        """
        if room_size not in self._scaled_cache:
            self._scaled_cache[room_size] = pygame.transform.scale(self._original_image, room_size)

        bg_image = self._scaled_cache[room_size]
        surface.blit(bg_image, (-camera_offset[0], -camera_offset[1]))
