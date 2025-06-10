import unittest
from unittest.mock import MagicMock
from src.model.Monster import Monster


class TestMonster(unittest.TestCase):
    """Tests for the Monster class"""

    def setUp(self):
        """Set up a monster instance for testing"""
        self.monster_name = "Test Monster"
        self.monster_health = 100
        self.attack_damage = 20
        self.is_boss = False
        self.monster = Monster(self.monster_name, self.monster_health, self.attack_damage, self.is_boss)

    def test_initialization(self):
        """Test that a monster is initialized with correct values"""
        self.assertEqual(self.monster.get_name(), self.monster_name)
        self.assertEqual(self.monster.get_health(), self.monster_health)
        self.assertEqual(self.monster.get_attack_damage(), self.attack_damage)
        self.assertEqual(self.monster.is_boss_monster(), self.is_boss)
        
        # Default values
        self.assertEqual(self.monster.get_chance_to_hit(), 1.0)
        damage_range = self.monster.get_damage_range()
        self.assertEqual(damage_range, (self.attack_damage, self.attack_damage))
        self.assertEqual(self.monster.get_heal_chance(), 0.0)
        self.assertEqual(self.monster.get_heal_range(), (0, 0))

    def test_take_damage(self):
        """Test that monster takes correct damage"""
        initial_health = self.monster.get_health()
        damage = 30
        self.monster.take_damage(damage)
        
        expected_health = initial_health - damage
        self.assertEqual(self.monster.get_health(), expected_health)
        self.assertTrue(self.monster.is_alive())

    def test_fatal_damage(self):
        """Test that monster dies when health reaches 0"""
        # Set up a monster with low health
        low_health_monster = Monster("Weak Monster", 10, 5, False)
        
        # Deal fatal damage
        low_health_monster.take_damage(15)
        
        # Check monster is dead
        self.assertEqual(low_health_monster.get_health(), -5)
        self.assertFalse(low_health_monster.is_alive())

    def test_attack(self):
        """Test monster's attack method"""
        # Create a mock player
        mock_player = MagicMock()
        mock_player.take_damage = MagicMock()
        
        # Set 100% chance to hit
        self.monster.set_chance_to_hit(1.0)
        
        # Set a fixed damage range
        self.monster.set_damage_range(10, 10)
        
        # Monster attacks player
        damage_dealt = self.monster.attack(mock_player)
        
        # Verify player's take_damage was called with correct amount
        self.assertEqual(damage_dealt, 10)
        mock_player.take_damage.assert_called_once_with(10)

    def test_attack_miss(self):
        """Test monster's attack when it misses"""
        # Create a mock player
        mock_player = MagicMock()
        
        # Set 0% chance to hit
        self.monster.set_chance_to_hit(0.0)
        
        # Monster attacks player
        damage_dealt = self.monster.attack(mock_player)
        
        # Verify attack missed
        self.assertEqual(damage_dealt, 0)
        mock_player.take_damage.assert_not_called()

    def test_healing(self):
        """Test monster's healing capability"""
        # Set up monster with healing ability
        healing_monster = Monster("Healing Monster", 100, 10, False)
        healing_monster.set_heal_chance(1.0)  # 100% chance to heal
        healing_monster.set_heal_range(5, 5)  # Fixed healing amount
        
        # Take some damage
        healing_monster.take_damage(20)
        # Should be at 80 health
        
        # Take more damage to trigger healing
        # The monster will heal 5 health after taking damage
        healing_monster.take_damage(10)
        
        # Health should be: 100 - 20 - 10 + 5 = 75
        self.assertEqual(healing_monster.get_health(), 75)

    def test_setting_attributes(self):
        """Test setter methods for monster attributes"""
        # Test setting health
        self.monster.set_health(50)
        self.assertEqual(self.monster.get_health(), 50)
        
        # Test setting chance to hit (with value clamping)
        self.monster.set_chance_to_hit(1.5)  # Should clamp to 1.0
        self.assertEqual(self.monster.get_chance_to_hit(), 1.0)
        
        self.monster.set_chance_to_hit(-0.5)  # Should clamp to 0.0
        self.assertEqual(self.monster.get_chance_to_hit(), 0.0)
        
        # Test setting damage range
        self.monster.set_damage_range(15, 25)
        self.assertEqual(self.monster.get_damage_range(), (15, 25))
        
        # Test that max damage can't be less than min damage
        self.monster.set_damage_range(30, 20)  # Should set both to 30
        self.assertEqual(self.monster.get_damage_range(), (30, 30))
        
        # Test setting heal chance
        self.monster.set_heal_chance(0.5)
        self.assertEqual(self.monster.get_heal_chance(), 0.5)
        
        # Test setting heal range
        self.monster.set_heal_range(10, 20)
        self.assertEqual(self.monster.get_heal_range(), (10, 20))


if __name__ == '__main__':
    unittest.main()