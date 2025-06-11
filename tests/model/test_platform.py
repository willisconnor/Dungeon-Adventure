import unittest
import pygame
from src.model.Platform import Platform


class TestPlatform(unittest.TestCase):
    """Tests for the Platform class"""

    def setUp(self):
        """Set up test environment"""
        pygame.init()
        
        # Create platforms of different types
        self.normal_platform = Platform(100, 200, 200, 20, "normal")
        self.moving_platform = Platform(300, 400, 100, 20, "moving")
        self.breakable_platform = Platform(500, 300, 150, 20, "breakable")
        self.one_way_platform = Platform(700, 500, 200, 10, "one-way")

    def tearDown(self):
        """Clean up pygame"""
        pygame.quit()

    def test_initialization(self):
        """Test platform initialization"""
        # Test normal platform
        self.assertEqual(self.normal_platform.x, 100)
        self.assertEqual(self.normal_platform.y, 200)
        self.assertEqual(self.normal_platform.width, 200)
        self.assertEqual(self.normal_platform.height, 20)
        self.assertEqual(self.normal_platform.platform_type, "normal")
        self.assertIsInstance(self.normal_platform.rect, pygame.Rect)
        self.assertFalse(self.normal_platform.is_moving)
        self.assertFalse(self.normal_platform.is_breakable)
        self.assertFalse(self.normal_platform.is_one_way)
        
        # Test moving platform
        self.assertEqual(self.moving_platform.platform_type, "moving")
        self.assertTrue(self.moving_platform.is_moving)
        self.assertEqual(self.moving_platform.move_speed, 2)
        self.assertEqual(self.moving_platform.move_distance, 100)
        self.assertEqual(self.moving_platform.move_direction, 1)
        self.assertEqual(self.moving_platform.start_x, 300)
        self.assertEqual(self.moving_platform.start_y, 400)
        self.assertEqual(self.moving_platform.move_axis, "x")
        
        # Test breakable platform
        self.assertEqual(self.breakable_platform.platform_type, "breakable")
        self.assertTrue(self.breakable_platform.is_breakable)
        self.assertEqual(self.breakable_platform.health, 3)
        self.assertFalse(self.breakable_platform.broken)
        
        # Test one-way platform
        self.assertEqual(self.one_way_platform.platform_type, "one-way")
        self.assertTrue(self.one_way_platform.is_one_way)

    def test_moving_platform_horizontal(self):
        """Test horizontal moving platform mechanics"""
        # Initial position
        initial_x = self.moving_platform.x
        
        # Update for one frame with default direction (right)
        self.moving_platform.update(1/60)  # dt = 1/60 for 60 FPS
        
        # Should move right
        self.assertGreater(self.moving_platform.x, initial_x)
        self.assertEqual(self.moving_platform.y, self.moving_platform.start_y)  # Y shouldn't change
        
        # Update until it reaches its maximum distance
        while abs(self.moving_platform.x - self.moving_platform.start_x) < self.moving_platform.move_distance:
            self.moving_platform.update(1/60)
        
        # Direction should reverse
        self.assertEqual(self.moving_platform.move_direction, -1)
        
        # Update one more frame, should move left
        x_before_left = self.moving_platform.x
        self.moving_platform.update(1/60)
        self.assertLess(self.moving_platform.x, x_before_left)
        
        # Rect should update with position
        self.assertEqual(self.moving_platform.rect.x, self.moving_platform.x)
        self.assertEqual(self.moving_platform.rect.y, self.moving_platform.y)

    def test_moving_platform_vertical(self):
        """Test vertical moving platform mechanics"""
        # Change to vertical movement
        self.moving_platform.move_axis = "y"
        
        # Initial position
        initial_y = self.moving_platform.y
        
        # Update for one frame with default direction (down)
        self.moving_platform.update(1/60)  # dt = 1/60 for 60 FPS
        
        # Should move down
        self.assertGreater(self.moving_platform.y, initial_y)
        self.assertEqual(self.moving_platform.x, self.moving_platform.start_x)  # X shouldn't change
        
        # Update until it reaches its maximum distance
        while abs(self.moving_platform.y - self.moving_platform.start_y) < self.moving_platform.move_distance:
            self.moving_platform.update(1/60)
        
        # Direction should reverse
        self.assertEqual(self.moving_platform.move_direction, -1)
        
        # Update one more frame, should move up
        y_before_up = self.moving_platform.y
        self.moving_platform.update(1/60)
        self.assertLess(self.moving_platform.y, y_before_up)
        
        # Rect should update with position
        self.assertEqual(self.moving_platform.rect.x, self.moving_platform.x)
        self.assertEqual(self.moving_platform.rect.y, self.moving_platform.y)

    def test_breakable_platform(self):
        """Test breakable platform mechanics"""
        # Initially not broken
        self.assertFalse(self.breakable_platform.broken)
        self.assertEqual(self.breakable_platform.health, 3)
        original_width = self.breakable_platform.rect.width
        original_height = self.breakable_platform.rect.height
        
        # Take damage once
        result = self.breakable_platform.take_damage()
        self.assertTrue(result)  # Should return True for successful damage
        self.assertEqual(self.breakable_platform.health, 2)
        self.assertFalse(self.breakable_platform.broken)
        
        # Take damage again
        self.breakable_platform.take_damage()
        self.assertEqual(self.breakable_platform.health, 1)
        self.assertFalse(self.breakable_platform.broken)
        
        # Take final damage to break
        self.breakable_platform.take_damage()
        self.assertEqual(self.breakable_platform.health, 0)
        self.assertTrue(self.breakable_platform.broken)
        
        # Rect should now have zero dimensions
        self.assertEqual(self.breakable_platform.rect.width, 0)
        self.assertEqual(self.breakable_platform.rect.height, 0)
        
        # Taking damage on broken platform should do nothing
        result = self.breakable_platform.take_damage()
        self.assertFalse(result)  # Should return False
        self.assertEqual(self.breakable_platform.health, 0)

    def test_normal_platform_damage(self):
        """Test that normal platforms can't take damage"""
        # Try to damage normal platform
        result = self.normal_platform.take_damage()
        self.assertFalse(result)  # Should return False

    def test_platform_update_when_broken(self):
        """Test that broken platforms don't move"""
        # Set up moving & broken platform
        self.moving_platform.is_breakable = True
        self.moving_platform.broken = True
        
        # Store initial position
        initial_x = self.moving_platform.x
        initial_y = self.moving_platform.y
        
        # Update platform
        self.moving_platform.update(1/60)
        
        # Position shouldn't change
        self.assertEqual(self.moving_platform.x, initial_x)
        self.assertEqual(self.moving_platform.y, initial_y)


if __name__ == '__main__':
    unittest.main()