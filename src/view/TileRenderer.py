import pygame
import csv

class TileRenderer:
    def __init__(self, csv_path, tileset_path, tile_width, tile_height):
        self._csv_path = csv_path
        self._tileset_path = tileset_path
        self._tile_width = tile_width
        self._tile_height = tile_height
        self._tiles = []
        self._tilemap = []
        self._load_tileset()
        self._load_csv()

    def _load_tileset(self):
        tileset_img = pygame.image.load(self._tileset_path).convert_alpha()
        tileset_width, tileset_height = tileset_img.get_size()

        for y in range(0, tileset_height, self._tile_height):
            for x in range(0, tileset_width, self._tile_width):
                rect = pygame.Rect(x, y, self._tile_width, self._tile_height)
                tile = tileset_img.subsurface(rect)
                self._tiles.append(tile)

    def _load_csv(self):
        with open(self._csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            self._tilemap = [[int(tile) for tile in row] for row in reader]

    def draw(self, surface, camera_offset=(0, 0)):
        for row_idx, row in enumerate(self._tilemap):
            for col_idx, tile_idx in enumerate(row):
                if tile_idx >= 0 and tile_idx < len(self._tiles):
                    tile = self._tiles[tile_idx]
                    surface.blit(tile, (
                        col_idx * self._tile_width - camera_offset[0],
                        row_idx * self._tile_height - camera_offset[1]
                    ))
