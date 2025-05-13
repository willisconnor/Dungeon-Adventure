import pygame
import os
from typing import Dict, List, Tuple

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 16  # Changed to 16x16
SCALE_FACTOR = 2  # This will make 16x16 tiles render at 32x32 for better visibility

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)


class TileSheet:
    def __init__(self, filename: str):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.tile_size = TILE_SIZE
        self.tiles = {}  # Cache for tiles

    def get_tile(self, x: int, y: int) -> pygame.Surface:
        """Extract a tile from the sheet at grid position (x, y)"""
        key = (x, y)
        if key not in self.tiles:
            tile = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            tile.blit(self.sheet, (0, 0),
                      (x * self.tile_size, y * self.tile_size,
                       self.tile_size, self.tile_size))
            # Scale the tile
            self.tiles[key] = pygame.transform.scale(tile,
                                                     (self.tile_size * SCALE_FACTOR,
                                                      self.tile_size * SCALE_FACTOR))
        return self.tiles[key]


class Room:
    def __init__(self, width: int, height: int):
        self.width_tiles = width
        self.height_tiles = height
        self.width_pixels = width * TILE_SIZE * SCALE_FACTOR
        self.height_pixels = height * TILE_SIZE * SCALE_FACTOR
        self._layout = self._generate_room_layout(width, height)

    def _generate_room_layout(self, width: int, height: int) -> List[List[int]]:
        """Generate a simple room layout with walls and platforms"""
        layout = [[0 for _ in range(width)] for _ in range(height)]

        # Add floor
        for x in range(width):
            layout[-1][x] = 1

        # Add walls
        for y in range(height):
            layout[y][0] = 1
            layout[y][-1] = 1

        # Add some platforms
        layout[height - 4][5:8] = [2, 2, 2]
        layout[height - 7][10:13] = [2, 2, 2]

        return layout


class Player:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, TILE_SIZE * SCALE_FACTOR, TILE_SIZE * SCALE_FACTOR * 1.5)
        self.velocity_y = 0
        self.jumping = False
        self.speed = 4
        self.gravity = 0.5
        self.jump_power = -12

    def update(self, room: Room):
        # Gravity
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Basic collision with floor
        if self.rect.bottom > room.height_pixels - (TILE_SIZE * SCALE_FACTOR):
            self.rect.bottom = room.height_pixels - (TILE_SIZE * SCALE_FACTOR)
            self.velocity_y = 0
            self.jumping = False

        # Basic collision with walls
        if self.rect.left < TILE_SIZE * SCALE_FACTOR:
            self.rect.left = TILE_SIZE * SCALE_FACTOR
        if self.rect.right > room.width_pixels - (TILE_SIZE * SCALE_FACTOR):
            self.rect.right = room.width_pixels - (TILE_SIZE * SCALE_FACTOR)


def load_assets() -> Dict[str, Dict[str, pygame.Surface]]:
    assets = {
        'assets': {},
        'background': {},
        'trees': {}
    }

    # Define files to load
    asset_files = [
        'Buildings.png',
        'Hive.png',
        'Interior-01.png',
        'Props-Rocks.png',
        'Tiles.png',
        'Tree-Assets.png'
    ]

    tree_files = [
        'Dark-Tree.png',
        'Golden-Tree.png',
        'Green-Tree.png',
        'Red-Tree.png',
        'Yellow-Tree.png'
    ]

    # Load background
    try:
        bg_path = os.path.join('background', 'Background.png')
        assets['background']['main'] = pygame.image.load(bg_path).convert_alpha()
    except Exception as e:
        print(f"Error loading background: {e}")

    # Load trees
    for tree_file in tree_files:
        try:
            tree_path = os.path.join('trees', tree_file)
            key = tree_file.replace('.png', '')
            assets['trees'][key] = pygame.image.load(tree_path).convert_alpha()
        except Exception as e:
            print(f"Error loading tree {tree_file}: {e}")

    # Load game assets
    for asset_file in asset_files:
        try:
            asset_path = os.path.join('assets', asset_file)
            key = asset_file.replace('.png', '')
            if asset_file == 'Tiles.png':
                assets['assets'][key] = TileSheet(asset_path)
            else:
                assets['assets'][key] = pygame.image.load(asset_path).convert_alpha()
        except Exception as e:
            print(f"Error loading asset {asset_file}: {e}")

    return assets


def main():
    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2D Platformer Test")
    clock = pygame.time.Clock()

    # Load assets
    GAME_ASSETS = load_assets()

    # Create room and player (40x30 tiles)
    room = Room(40, 30)
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Camera offset
    camera_offset = [0, 0]

    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not player.jumping:
                    player.velocity_y = player.jump_power
                    player.jumping = True

        # Handle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.rect.x -= player.speed
        if keys[pygame.K_RIGHT]:
            player.rect.x += player.speed

        # Update player
        player.update(room)

        # Update camera with smooth following
        target_x = player.rect.centerx - SCREEN_WIDTH // 2
        target_y = player.rect.centery - SCREEN_HEIGHT // 2

        camera_offset[0] += (target_x - camera_offset[0]) * 0.1
        camera_offset[1] += (target_y - camera_offset[1]) * 0.1

        # Clamp camera to room bounds
        camera_offset[0] = max(0, min(camera_offset[0], room.width_pixels - SCREEN_WIDTH))
        camera_offset[1] = max(0, min(camera_offset[1], room.height_pixels - SCREEN_HEIGHT))

        # Draw everything
        screen.fill(BLACK)

        # Draw background
        if 'main' in GAME_ASSETS['background']:
            bg = GAME_ASSETS['background']['main']
            scaled_bg = pygame.transform.scale(bg, (room.width_pixels, room.height_pixels))
            screen.blit(scaled_bg, (-camera_offset[0], -camera_offset[1]))

        # Draw tiles
        if 'Tiles' in GAME_ASSETS['assets']:
            tileset = GAME_ASSETS['assets']['Tiles']
            for y, row in enumerate(room._layout):
                for x, tile in enumerate(row):
                    if tile > 0:  # If it's not empty
                        pos_x = x * (TILE_SIZE * SCALE_FACTOR) - camera_offset[0]
                        pos_y = y * (TILE_SIZE * SCALE_FACTOR) - camera_offset[1]

                        # For now, using the first tile for walls and second for platforms
                        # We'll adjust these positions based on your tileset layout
                        if tile == 1:  # Wall
                            tile_img = tileset.get_tile(0, 0)  # First tile
                        elif tile == 2:  # Platform
                            tile_img = tileset.get_tile(1, 0)  # Second tile

                        screen.blit(tile_img, (pos_x, pos_y))

        # Draw trees
        tree_spacing = 300
        tree_types = list(GAME_ASSETS['trees'].values())
        if tree_types:
            for x in range(0, room.width_pixels, tree_spacing):
                tree_img = tree_types[int(x / tree_spacing) % len(tree_types)]
                tree_height = TILE_SIZE * SCALE_FACTOR * 4
                tree_width = int(tree_height * 0.8)
                scaled_tree = pygame.transform.scale(tree_img, (tree_width, tree_height))
                tree_y = room.height_pixels - tree_height - (TILE_SIZE * SCALE_FACTOR)
                screen.blit(scaled_tree,
                            (x - camera_offset[0],
                             tree_y - camera_offset[1]))

        # Draw player
        pygame.draw.rect(screen, GREEN,
                         (player.rect.x - camera_offset[0],
                          player.rect.y - camera_offset[1],
                          player.rect.width, player.rect.height))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()