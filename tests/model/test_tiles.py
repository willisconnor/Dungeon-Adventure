import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import pygame
import csv
from src.model.tiles import Tile, TileMap  # Adjust import based on your actual class structure


class TestTile(unittest.TestCase):
    """Tests for the Tile class"""

    def setUp(self):
        """Set up test environment"""
        pygame.init()
        
        # Create a mock spritesheet
        self.mock_spritesheet = MagicMock()
        self.mock_spritesheet.get_image = MagicMock(return_value=pygame.Surface((32, 32)))
        
        # Create a tile
        self.x, self.y = 100, 200
        self.tile_name = "ground.png"
        self.tile = Tile(self.tile_name, self.x, self.y, self.mock_spritesheet)

    def tearDown(self):
        """Clean up pygame"""
        pygame.quit()

    def test_initialization(self):
        """Test tile initialization"""
        self.assertEqual(self.tile.x, self.x)
        self.assertEqual(self.tile.y, self.y)
        self.assertEqual(self.tile.name, self.tile_name)
        
        # Should have loaded image from spritesheet
        self.mock_spritesheet.get_image.assert_called_once()
        
        # Should have a rect
        self.assertIsInstance(self.tile.rect, pygame.Rect)
        self.assertEqual(self.tile.rect.x, self.x)
        self.assertEqual(self.tile.rect.y, self.y)

    def test_update(self):
        """Test tile update method"""
        # Store initial position
        initial_x = self.tile.rect.x
        initial_y = self.tile.rect.y
        
        # Update position
        new_x, new_y = 150, 250
        self.tile.update(new_x, new_y)
        
        # Position should change
        self.assertEqual(self.tile.rect.x, new_x)
        self.assertEqual(self.tile.rect.y, new_y)

    def test_draw(self):
        """Test tile draw method"""
        # Create mock screen
        mock_screen = MagicMock()
        mock_screen.blit = MagicMock()
        
        # Draw tile
        self.tile.draw(mock_screen)
        
        # Should call screen.blit once
        mock_screen.blit.assert_called_once()


class TestTileMap(unittest.TestCase):
    """Tests for the TileMap class"""

    def setUp(self):
        """Set up test environment"""
        pygame.init()
        
        # Create a mock spritesheet
        self.mock_spritesheet = MagicMock()
        self.mock_spritesheet.get_image = MagicMock(return_value=pygame.Surface((32, 32)))
        
        # Create a tilemap
        self.tile_size = 32
        self.tilemap = TileMap(self.tile_size, self.mock_spritesheet)

    def tearDown(self):
        """Clean up pygame"""
        pygame.quit()

    def test_initialization(self):
        """Test tilemap initialization"""
        self.assertEqual(self.tilemap.tile_size, self.tile_size)
        self.assertEqual(self.tilemap.spritesheet, self.mock_spritesheet)
        self.assertEqual(self.tilemap.start_x, 0)
        self.assertEqual(self.tilemap.start_y, 0)
        self.assertEqual(self.tilemap.map_w, 0)
        self.assertEqual(self.tilemap.map_h, 0)

    @patch("builtins.open", new_callable=mock_open, read_data="0,1,2\n1,0,1\n2,1,0")
    def test_read_csv(self, mock_file):
        """Test reading CSV file"""
        # Call read_csv method
        filename = "test_map.csv"
        result = self.tilemap.read_csv(filename)
        
        # Should open the file
        mock_file.assert_called_once_with(filename, newline='')
        
        # Should return a list of rows
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)  # 3 rows
        for row in result:
            self.assertIsInstance(row, list)
            self.assertEqual(len(row), 3)  # 3 columns

    @patch.object(TileMap, "read_csv")
    def test_load_tiles(self, mock_read_csv):
        """Test loading tiles from CSV"""
        # Set up mock CSV data
        mock_read_csv.return_value = [
            ['0', '1', '2'],
            ['1', '0', '1'],
            ['2', '1', '0']
        ]
        
        # Load tiles
        filename = "test_map.csv"
        tiles = self.tilemap.load_tiles(filename)
        
        # Should read the CSV
        mock_read_csv.assert_called_once_with(filename)
        
        # Should create tiles for each non-zero cell
        self.assertIsInstance(tiles, list)
        
        # Count expected tiles (excluding '0' which are player start positions)
        expected_tile_count = sum(row.count('1') + row.count('2') for row in mock_read_csv.return_value)
        self.assertEqual(len(tiles), expected_tile_count)
        
        # Should set start position from '0' cell
        self.assertEqual(self.tilemap.start_x, 0 * self.tile_size)  # First '0' is at (0,0)
        self.assertEqual(self.tilemap.start_y, 0 * self.tile_size)
        
        # Should set map dimensions
        self.assertEqual(self.tilemap.map_w, 3 * self.tile_size)
        self.assertEqual(self.tilemap.map_h, 3 * self.tile_size)

    def test_draw_map(self):
        """Test drawing the map"""
        # Create some test tiles
        tiles = [
            Tile("ground.png", 0, 0, self.mock_spritesheet),
            Tile("ground2.png", 32, 0, self.mock_spritesheet),
            Tile("ground.png", 0, 32, self.mock_spritesheet)
        ]
        
        # Create mock screen
        mock_screen = MagicMock()
        
        # Draw tiles
        self.tilemap.draw_map(mock_screen, tiles)
        
        # Each tile's draw method should be called once
        for tile in tiles:
            tile.draw = MagicMock()
        
        self.tilemap.draw_map(mock_screen, tiles)
        for tile in tiles:
            tile.draw.assert_called_once_with(mock_screen)


if __name__ == '__main__':
    unittest.main()