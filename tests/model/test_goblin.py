import unittest
from unittest.mock import MagicMock, patch
from src.model.Goblin import Goblin


class TestGoblin(unittest.TestCase):
    """Tests for the Goblin class"""

    def setUp(self):
        """Set up a Goblin instance for testing"""
        self.goblin = Goblin()

    def test_initialization(self):
        """Test that a goblin is initialized with correct values"""
        self.assertEqual(self.goblin.get_name(), "Goblin")
        self.assertEqual(self.goblin.get_health(), 80)
        self.assertFalse(self.goblin.is_boss_monster())
        
        # Goblin specific values
        self.assertEqual(self.goblin.get_chance_to_hit(), 0.7)
        self.assertEqual(self.goblin.get_damage_range(), (10, 25))
        self.assertEqual(self.goblin.get_heal_chance(), 0.2)
        self.assertEqual(self.goblin.get_heal_range(), (10, 25))
        self.assertEqual(self.goblin.get_special_skill(), "Speed X2")
        self.assertEqual(self.goblin.get_attack_speed(), 4)
        self.assertEqual(self.goblin.get_movement_speed(), 40.0)

    def test_attack(self):
        """Test goblin's attack method"""
        # Create a mock player
        mock_player = MagicMock()
        mock_player.take_damage = MagicMock()
        
        # Mock random.random to guarantee a hit
        with patch('random.random', return_value=0.5):
            # Mock random.randint to get consistent damage
            with patch('random.randint', return_value=15):
                # Goblin attacks player
                damage_dealt = self.goblin.attack(mock_player)
                
                # Verify damage
                self.assertEqual(damage_dealt, 15)
                mock_player.take_damage.assert_called_once_with(15)

    def test_attack_miss(self):
        """Test goblin's attack when it misses"""
        # Create a mock player
        mock_player = MagicMock()
        mock_player.take_damage = MagicMock()
        
        # Mock random.random to guarantee a miss
        with patch('random.random', return_value=0.8):
            # Goblin attacks player
            damage_dealt = self.goblin.attack(mock_player)
            
            # Verify attack missed
            self.assertEqual(damage_dealt, 0)
            mock_player.take_damage.assert_not_called()

    def test_take_damage_and_heal(self):
        """Test goblin taking damage and potentially healing"""
        initial_health = self.goblin.get_health()
        
        # Mock random.random to guarantee healing
        with patch('random.random', return_value=0.1):  # 0.1 < 0.2 heal chance
            # Mock random.randint for consistent healing
            with patch('random.randint', return_value=15):
                # Take damage
                self.goblin.take_damage(30)
                
                # Health should be: initial - damage + healing
                expected_health = initial_health - 30 + 15
                self.assertEqual(self.goblin.get_health(), expected_health)

    def test_setters_and_getters(self):
        """Test setter and getter methods"""
        # Test special skill
        new_skill = "Ultra Speed"
        self.goblin.set_special_skill(new_skill)
        self.assertEqual(self.goblin.get_special_skill(), new_skill)
        
        # Test movement speed
        new_speed = 50.0
        self.goblin.set_movement_speed(new_speed)
        self.assertEqual(self.goblin.get_movement_speed(), new_speed)
        
        # Test attack speed
        new_attack_speed = 5
        self.goblin.set_attack_speed(new_attack_speed)
        self.assertEqual(self.goblin.get_attack_speed(), new_attack_speed)
        
        # Test hit points
        new_hp = 60
        self.goblin.setHitPoints(new_hp)  # Using legacy method
        self.assertEqual(self.goblin.getHitPoints(), new_hp)  # Using legacy method
        self.assertEqual(self.goblin.get_health(), new_hp)  # Using new method

    def test_string_representation(self):
        """Test the string representation of the goblin"""
        goblin_str = str(self.goblin)
        
        # Check that string contains important information
        self.assertIn("Goblin", goblin_str)
        self.assertIn(self.goblin.get_special_skill(), goblin_str)
        self.assertIn(f"Attack Speed: {self.goblin.get_attack_speed()}", goblin_str)
        self.assertIn(f"Movement Speed: {self.goblin.get_movement_speed()}", goblin_str)


if __name__ == '__main__':
    unittest.main()