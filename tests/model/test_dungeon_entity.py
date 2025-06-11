import unittest
from unittest.mock import MagicMock
from src.model.DungeonEntity import DungeonEntity, Direction, AnimationState


class TestDungeonEntity(unittest.TestCase):
    """Tests for the base DungeonEntity class"""

    def setUp(self):
        """Set up a DungeonEntity instance for testing"""
        self.x, self.y = 100, 200
        self.width, self.height = 50, 60
        self.name = "TestEntity"
        self.entity = DungeonEntity(self.x, self.y, self.width, self.height, self.name)

    def test_initialization(self):
        """Test that entity is initialized with correct values"""
        self.assertEqual(self.entity.get_x(), self.x)
        self.assertEqual(self.entity.get_y(), self.y)
        self.assertEqual(self.entity.get_width(), self.width)
        self.assertEqual(self.entity.get_height(), self.height)
        self.assertEqual(self.entity.get_name(), self.name)
        self.assertEqual(self.entity.get_direction(), Direction.RIGHT)  # Default direction
        self.assertEqual(self.entity.get_animation_state(), AnimationState.IDLE)  # Default state

    def test_movement(self):
        """Test entity movement"""
        initial_x = self.entity.get_x()
        initial_y = self.entity.get_y()
        
        # Move entity
        self.entity.set_x(initial_x + 10)
        self.entity.set_y(initial_y - 5)
        
        # Check new position
        self.assertEqual(self.entity.get_x(), initial_x + 10)
        self.assertEqual(self.entity.get_y(), initial_y - 5)
        
        # Test set_position method
        new_x, new_y = 300, 400
        self.entity.set_position(new_x, new_y)
        self.assertEqual(self.entity.get_x(), new_x)
        self.assertEqual(self.entity.get_y(), new_y)

    def test_direction(self):
        """Test changing entity direction"""
        # Test default direction
        self.assertEqual(self.entity.get_direction(), Direction.RIGHT)
        
        # Change direction
        self.entity.set_direction(Direction.LEFT)
        self.assertEqual(self.entity.get_direction(), Direction.LEFT)
        
        # Test invalid direction
        with self.assertRaises(ValueError):
            self.entity.set_direction("invalid_direction")

    def test_animation_state(self):
        """Test changing animation state"""
        # Test default state
        self.assertEqual(self.entity.get_animation_state(), AnimationState.IDLE)
        
        # Change state
        self.entity.set_animation_state(AnimationState.RUNNING)
        self.assertEqual(self.entity.get_animation_state(), AnimationState.RUNNING)
        
        # Change to jumping state
        self.entity.set_animation_state(AnimationState.JUMPING)
        self.assertEqual(self.entity.get_animation_state(), AnimationState.JUMPING)
        
        # Test invalid state
        with self.assertRaises(ValueError):
            self.entity.set_animation_state("invalid_state")

    def test_collision_detection(self):
        """Test collision detection between entities"""
        # Create another entity that overlaps
        overlapping_entity = DungeonEntity(
            self.x + 10,  # Overlap on x-axis
            self.y + 10,  # Overlap on y-axis
            self.width,
            self.height,
            "OverlappingEntity"
        )
        
        # Create another entity that doesn't overlap
        non_overlapping_entity = DungeonEntity(
            self.x + self.width + 10,  # No overlap on x-axis
            self.y,
            self.width,
            self.height,
            "NonOverlappingEntity"
        )
        
        # Test collision detection
        self.assertTrue(self.entity.collides_with(overlapping_entity))
        self.assertFalse(self.entity.collides_with(non_overlapping_entity))

    def test_update(self):
        """Test entity update method"""
        # Set velocity
        self.entity.set_velocity(5, -10)
        
        # Get initial position
        initial_x = self.entity.get_x()
        initial_y = self.entity.get_y()
        
        # Update with dt of 1.0 (one second)
        self.entity.update(1.0)
        
        # Check that position has changed according to velocity
        self.assertEqual(self.entity.get_x(), initial_x + 5)
        self.assertEqual(self.entity.get_y(), initial_y - 10)

    def test_render(self):
        """Test entity render method"""
        # Mock the screen
        mock_screen = MagicMock()
        
        # Call render method
        if hasattr(self.entity, "render"):
            self.entity.render(mock_screen)
            
            # If render method draws to the screen, mock_screen methods would be called
            # This is a simple check that the method doesn't crash
            # For a real test, you'd need to check that the correct drawing methods were called

    def test_string_representation(self):
        """Test string representation of entity"""
        entity_str = str(self.entity)
        
        # Check that string contains important information
        self.assertIn(self.name, entity_str)
        self.assertIn(str(self.x), entity_str)
        self.assertIn(str(self.y), entity_str)


if __name__ == '__main__':
    unittest.main()