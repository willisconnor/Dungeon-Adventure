import pygame
import json


class Room:
    def __init__(self, room_file):
        """
        Initialize a game room from JSON data
        Args:
            room_file: Path to JSON file containing room layout
        """
        with open(room_file) as f:
            self.data = json.load(f)

        # Room dimensions
        self.width = self.data['width'] * self.data['tile_size']
        self.height = self.data['height'] * self.data['tile_size']

        # Tile setup
        self.tile_size = self.data['tile_size']
        self.tiles = self.data['layout']

        # Collision objects
        self.walls = []
        self.platforms = []
        self._process_tiles()

        # Visual elements
        self.background = self._create_background()

    def _process_tiles(self):
        """Convert tile numbers to collision objects"""
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile == 1:  # Solid wall
                    self.walls.append(pygame.Rect(
                        x * self.tile_size,
                        y * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    ))
                elif tile == 2:  # Platform
                    self.platforms.append(pygame.Rect(
                        x * self.tile_size,
                        y * self.tile_size,
                        self.tile_size,
                        self.tile_size // 4  # Thin platform
                    ))

    def _create_background(self):
        """Generate a simple background surface"""
        bg = pygame.Surface((self.width, self.height))
        bg.fill((40, 40, 60))  # Dark dungeon color

        # Draw grid lines for debugging
        for x in range(0, self.width, self.tile_size):
            pygame.draw.line(bg, (60, 60, 80), (x, 0), (x, self.height))
        for y in range(0, self.height, self.tile_size):
            pygame.draw.line(bg, (60, 60, 80), (0, y), (self.width, y))

        return bg

    def check_collision(self, rect):
        """Check collision with walls and platforms"""
        for wall in self.walls:
            if rect.colliderect(wall):
                return True
        return False

    def check_platform(self, rect, velocity_y):
        """Special platform collision (only from top)"""
        if velocity_y <= 0:  # Only check when falling
            return False

        for platform in self.platforms:
            if (rect.colliderect(platform) and
                    rect.bottom > platform.top and
                    (rect.bottom - velocity_y) <= platform.top):
                return platform.top
        return None

    def draw(self, surface, camera_offset):
        """Draw room elements"""
        # Draw background
        surface.blit(self.background, (-camera_offset[0], -camera_offset[1]))

        # Draw walls (for debugging)
        for wall in self.walls:
            adjusted = wall.move(-camera_offset[0], -camera_offset[1])
            pygame.draw.rect(surface, (100, 80, 60), adjusted)

        # Draw platforms
        for platform in self.platforms:
            adjusted = platform.move(-camera_offset[0], -camera_offset[1])
            pygame.draw.rect(surface, (80, 60, 40), adjusted)