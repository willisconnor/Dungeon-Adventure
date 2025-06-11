import unittest
from unittest.mock import MagicMock, patch
from src.model.DungeonCharacter import DungeonCharacter


class TestDungeonCharacter(unittest.TestCase):
    """Tests for the DungeonCharacter class"""

    def setUp(self):
        """Set up a DungeonCharacter instance for testing"""
        self.x, self.y = 100, 200
        self.width, self.height = 64, 64
        self.name = "TestCharacter"
        self.max_health = 100
        self.health = 100
        self.speed = 5
        self.damage = 10
        
        # Create a DungeonCharacter instance
        self.character = DungeonCharacter(
            self.x, self.y, self.width, self.height, self.name,
            self.max_health, self.health, self.speed, self.damage
        )

    def test_initialization(self):
        """Test that character is initialized with correct values"""
        self.assertEqual(self.character.get_x(), self.x)
        self.assertEqual(self.character.get_y(), self.y)
        self.assertEqual(self.character.get_width(), self.width)
        self.assertEqual(self.character.get_height(), self.height)
        self.assertEqual(self.character.get_name(), self.name)
        self.assertEqual(self.character.get_max_health(), self.max_health)
        self.assertEqual(self.character.get_health(), self.health)
        self.assertEqual(self.character.get_speed(), self.speed)
        self.assertEqual(self.character.get_damage(), self.damage)
        self.assertTrue(self.character.is_alive())

    def test_take_damage(self):
        """Test character taking damage"""
        initial_health = self.character.get_health()
        damage = 30
        
        # Take damage
        self.character.take_damage(damage)
        
        # Verify health reduction
        self.assertEqual(self.character.get_health(), initial_health - damage)
        self.assertTrue(self.character.is_alive())

    def test_take_fatal_damage(self):
        """Test character taking fatal damage"""
        fatal_damage = self.character.get_health() + 10
        
        # Take fatal damage
        self.character.take_damage(fatal_damage)
        
        # Verify character is dead
        self.assertEqual(self.character.get_health(), 0)  # Health should be clamped to 0
        self.assertFalse(self.character.is_alive())

    def test_heal(self):
        """Test healing the character"""
        # First take some damage
        self.character.take_damage(50)
        damaged_health = self.character.get_health()
        
        # Heal partial amount
        heal_amount = 20
        self.character.heal(heal_amount)
        
        # Verify healing
        self.assertEqual(self.character.get_health(), damaged_health + heal_amount)
        
        # Heal beyond max health
        large_heal = 100
        self.character.heal(large_heal)
        
        # Verify health is capped at max_health
        self.assertEqual(self.character.get_health(), self.character.get_max_health())

    def test_attack(self):
        """Test character attack method"""
        # Create a mock target
        mock_target = MagicMock()
        mock_target.take_damage = MagicMock()
        
        # Attack target
        if hasattr(self.character, "attack"):
            damage = self.character.attack(mock_target)
            
            # Verify damage calculation and target.take_damage called
            self.assertEqual(damage, self.damage)
            mock_target.take_damage.assert_called_once_with(self.damage)

    def test_movement(self):
        """Test character movement"""
        initial_x = self.character.get_x()
        initial_y = self.character.get_y()
        
        # Move right
        self.character.move_right(1.0)
        self.assertGreater(self.character.get_x(), initial_x)
        
        # Move left
        new_x = self.character.get_x()
        self.character.move_left(1.0)
        self.assertLess(self.character.get_x(), new_x)
        
        # Jump (if implemented)
        if hasattr(self.character, "jump"):
            initial_y = self.character.get_y()
            self.character.jump()
            # In most implementations, jump sets a negative y velocity
            self.assertLess(self.character.get_velocity_y(), 0)

    def test_is_alive(self):
        """Test alive status methods"""
        # Initially alive
        self.assertTrue(self.character.is_alive())
        
        # Take fatal damage
        self.character.take_damage(self.character.get_health() + 10)
        
        # Should be dead
        self.assertFalse(self.character.is_alive())
        
        # Resurrect
        self.character.set_health(10)
        self.assertTrue(self.character.is_alive())

    def test_set_stats(self):
        """Test setting character stats"""
        # Set new values
        new_health = 75
        new_max_health = 150
        new_speed = 7
        new_damage = 15
        
        # Update stats
        self.character.set_health(new_health)
        self.character.set_max_health(new_max_health)
        self.character.set_speed(new_speed)
        self.character.set_damage(new_damage)
        
        # Verify changes
        self.assertEqual(self.character.get_health(), new_health)
        self.assertEqual(self.character.get_max_health(), new_max_health)
        self.assertEqual(self.character.get_speed(), new_speed)
        self.assertEqual(self.character.get_damage(), new_damage)
        
        # Test setting health above max health
        self.character.set_health(new_max_health + 20)
        self.assertEqual(self.character.get_health(), new_max_health)  # Should be capped

    def test_string_representation(self):
        """Test string representation of character"""
        character_str = str(self.character)
        
        # Check that string contains important information
        self.assertIn(self.name, character_str)
        self.assertIn(f"{self.health}/{self.max_health}", character_str)
        self.assertIn(str(self.damage), character_str)


if __name__ == '__main__':
    unittest.main()