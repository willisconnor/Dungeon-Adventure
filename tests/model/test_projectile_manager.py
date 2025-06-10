import unittest
from unittest.mock import MagicMock, patch
import pygame
from src.model.ProjectileManager import ProjectileManager, Projectile, ProjectileType
from src.model.DungeonEntity import Direction


class TestProjectileManager(unittest.TestCase):
    """Tests for the ProjectileManager class"""

    def setUp(self):
        """Set up ProjectileManager for testing"""
        # Initialize pygame for Surface operations
        pygame.init()
        
        # Create a mock screen
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.Surface((self.screen_width, self.screen_height))
        
        # Create a ProjectileManager
        self.manager = ProjectileManager()
        
        # Create a mock owner
        self.owner = MagicMock()
        self.owner.get_x.return_value = 100
        self.owner.get_y.return_value = 100
        
        # Create a test projectile
        self.projectile = Projectile(
            x=100,
            y=100,
            direction=Direction.RIGHT,
            projectile_type=ProjectileType.ARROW,
            owner=self.owner,
            damage=20,
            speed=10,
            range=300
        )

    def tearDown(self):
        """Clean up pygame"""
        pygame.quit()

    def test_add_projectile(self):
        """Test adding a projectile to the manager"""
        # Initial count should be 0
        self.assertEqual(len(self.manager.get_projectiles()), 0)
        
        # Add a projectile
        self.manager.add_projectile(self.projectile)
        
        # Count should now be 1
        self.assertEqual(len(self.manager.get_projectiles()), 1)
        
        # Added projectile should be in the list
        self.assertIn(self.projectile, self.manager.get_projectiles())

    def test_update_projectiles(self):
        """Test updating projectiles"""
        # Add a projectile
        self.manager.add_projectile(self.projectile)
        
        # Get initial position
        initial_x = self.projectile.x
        
        # Update projectiles (dt = 1.0 second)
        self.manager.update(1.0)
        
        # Position should change based on direction and speed
        self.assertGreater(self.projectile.x, initial_x)
        
        # Update until projectile exceeds its range
        for _ in range(50):
            self.manager.update(1.0)
        
        # Projectile should be removed after exceeding range
        self.assertEqual(len(self.manager.get_projectiles()), 0)

    def test_check_collisions(self):
        """Test collision detection with entities"""
        # Add a projectile
        self.manager.add_projectile(self.projectile)
        
        # Create a mock target that will collide
        target1 = MagicMock()
        target1.is_alive = True
        target1.hitbox = pygame.Rect(150, 100, 50, 50)  # Will collide
        target1.take_damage = MagicMock(return_value=True)
        
        # Create a mock target that won't collide
        target2 = MagicMock()
        target2.is_alive = True
        target2.hitbox = pygame.Rect(500, 500, 50, 50)  # Won't collide
        target2.take_damage = MagicMock()
        
        # Check collisions
        targets = [target1, target2]
        hit_targets = self.manager.check_collisions(targets)
        
        # First target should be hit, second should not
        self.assertEqual(len(hit_targets), 1)
        self.assertIn(target1, hit_targets)
        self.assertNotIn(target2, hit_targets)
        
        # First target should take damage, second should not
        target1.take_damage.assert_called_once_with(self.projectile.damage)
        target2.take_damage.assert_not_called()
        
        # Projectile should be destroyed after hitting
        self.assertEqual(len(self.manager.get_projectiles()), 0)

    def test_render(self):
        """Test rendering projectiles"""
        # Add a projectile
        self.manager.add_projectile(self.projectile)
        
        # Call render method (just checking it doesn't crash)
        self.manager.render(self.screen)

    def test_projectile_initialization(self):
        """Test projectile initialization"""
        # Check initial values
        self.assertEqual(self.projectile.x, 100)
        self.assertEqual(self.projectile.y, 100)
        self.assertEqual(self.projectile.direction, Direction.RIGHT)
        self.assertEqual(self.projectile.projectile_type, ProjectileType.ARROW)
        self.assertEqual(self.projectile.owner, self.owner)
        self.assertEqual(self.projectile.damage, 20)
        self.assertEqual(self.projectile.speed, 10)
        self.assertEqual(self.projectile.range, 300)
        
        # Distance traveled should start at 0
        self.assertEqual(self.projectile.distance_traveled, 0)
        
        # Hitbox should be created
        self.assertIsInstance(self.projectile.hitbox, pygame.Rect)

    def test_projectile_update(self):
        """Test projectile update method"""
        # Initial position
        initial_x = self.projectile.x
        initial_y = self.projectile.y
        
        # Update with dt = 0.5
        self.projectile.update(0.5)
        
        # Position should change based on direction and speed
        expected_x = initial_x + (self.projectile.speed * 0.5)
        self.assertEqual(self.projectile.x, expected_x)
        self.assertEqual(self.projectile.y, initial_y)  # y shouldn't change
        
        # Distance traveled should increase
        self.assertGreater(self.projectile.distance_traveled, 0)
        
        # Test with LEFT direction
        left_projectile = Projectile(
            x=100,
            y=100,
            direction=Direction.LEFT,
            projectile_type=ProjectileType.ARROW,
            owner=self.owner,
            damage=20,
            speed=10,
            range=300
        )
        
        initial_x = left_projectile.x
        left_projectile.update(0.5)
        
        # X should decrease when moving left
        expected_x = initial_x - (left_projectile.speed * 0.5)
        self.assertEqual(left_projectile.x, expected_x)

    def test_projectile_range_exceeded(self):
        """Test detecting when projectile exceeds its range"""
        # Initially not exceeded
        self.assertFalse(self.projectile.has_exceeded_range())
        
        # Update until range is exceeded
        while not self.projectile.has_exceeded_range():
            self.projectile.update(1.0)
        
        # Should now exceed range
        self.assertTrue(self.projectile.has_exceeded_range())
        self.assertGreaterEqual(self.projectile.distance_traveled, self.projectile.range)


if __name__ == '__main__':
    unittest.main()