import unittest
from unittest.mock import MagicMock, patch
from src.model.knight import Knight


class TestKnight(unittest.TestCase):
    """Tests for the Knight hero class"""

    def setUp(self):
        """Set up a knight instance for testing"""
        self.x, self.y = 100, 200
        self.knight = Knight(self.x, self.y)

    def test_initialization(self):
        """Test that a knight is initialized with correct values"""
        self.assertEqual(self.knight.get_x(), self.x)
        self.assertEqual(self.knight.get_y(), self.y)
        self.assertEqual(self.knight.get_hero_type(), "knight")
        self.assertTrue(self.knight.get_is_alive())

    def test_calculate_damage_normal(self):
        """Test knight damage calculation at normal health"""
        # Set up knight with full health
        self.knight.set_health(self.knight.get_max_health())
        base_damage = self.knight.get_damage()
        
        # Calculate damage
        damage = self.knight.calculate_damage(None)  # Target doesn't matter for knights
        
        # Should be normal damage
        self.assertEqual(damage, base_damage)

    def test_calculate_damage_low_health(self):
        """Test knight damage calculation at low health"""
        # Set knight to 20% health to trigger bonus damage
        max_health = self.knight.get_max_health()
        self.knight.set_health(int(max_health * 0.2))
        base_damage = self.knight.get_damage()
        
        # Calculate damage
        damage = self.knight.calculate_damage(None)  # Target doesn't matter for knights
        
        # Should be 50% bonus damage
        self.assertEqual(damage, int(base_damage * 1.5))

    def test_special_ability(self):
        """Test knight's special ability activation"""
        # Create a mock for the parent class method
        with patch('src.model.DungeonHero.Hero.activate_special_ability') as mock_parent:
            # Activate special ability
            self.knight.activate_special_ability()
            
            # Verify parent method was called
            mock_parent.assert_called_once()
            
            # In a real test, you might also check that the stun effect was applied
            # But this would require integration with the game system


if __name__ == '__main__':
    unittest.main()