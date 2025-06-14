import unittest
from unittest.mock import MagicMock, patch
from src.model.Gorgon import Gorgon


class TestGorgon(unittest.TestCase):
    """Tests for the Gorgon class"""

    def setUp(self):
        """Set up a Gorgon instance for testing"""
        self.gorgon = Gorgon()

    def test_initialization(self):
        """Test that a gorgon is initialized with correct values"""
        self.assertEqual(self.gorgon.get_name(), "Gorgon")
        self.assertEqual(self.gorgon.get_health(), 80)
        self.assertFalse(self.gorgon.is_boss_monster())
        
        # Goblin specific values
        self.assertEqual(self.gorgon.get_chance_to_hit(), 0.7)
        self.assertEqual(self.gorgon.get_damage_range(), (10, 25))
        self.assertEqual(self.gorgon.get_heal_chance(), 0.2)
        self.assertEqual(self.gorgon.get_heal_range(), (10, 25))
        self.assertEqual(self.gorgon.get_special_skill(), "Speed X2")
        self.assertEqual(self.gorgon.get_attack_speed(), 4)
        self.assertEqual(self.gorgon.get_movement_speed(), 40.0)

    def test_attack(self):
        """Test gorgon's attack method"""
        # Create a mock player
        mock_player = MagicMock()
        mock_player.take_damage = MagicMock()
        
        # Mock random.random to guarantee a hit
        with patch('random.random', return_value=0.5):
            # Mock random.randint to get consistent damage
            with patch('random.randint', return_value=15):
                # Goblin attacks player
                damage_dealt = self.gorgon.attack(mock_player)
                
                # Verify damage
                self.assertEqual(damage_dealt, 15)
                mock_player.take_damage.assert_called_once_with(15)

    def test_attack_miss(self):
        """Test gorgon's attack when it misses"""
        # Create a mock player
        mock_player = MagicMock()
        mock_player.take_damage = MagicMock()
        
        # Mock random.random to guarantee a miss
        with patch('random.random', return_value=0.8):
            # Goblin attacks player
            damage_dealt = self.gorgon.attack(mock_player)
            
            # Verify attack missed
            self.assertEqual(damage_dealt, 0)
            mock_player.take_damage.assert_not_called()

    def test_take_damage_and_heal(self):
        """Test gorgon taking damage and potentially healing"""
        initial_health = self.gorgon.get_health()
        
        # Mock random.random to guarantee healing
        with patch('random.random', return_value=0.1):  # 0.1 < 0.2 heal chance
            # Mock random.randint for consistent healing
            with patch('random.randint', return_value=15):
                # Take damage
                self.gorgon.take_damage(30)
                
                # Health should be: initial - damage + healing
                expected_health = initial_health - 30 + 15
                self.assertEqual(self.gorgon.get_health(), expected_health)

    def test_setters_and_getters(self):
        """Test setter and getter methods"""
        # Test special skill
        new_skill = "Ultra Speed"
        self.gorgon.set_special_skill(new_skill)
        self.assertEqual(self.gorgon.get_special_skill(), new_skill)
        
        # Test movement speed
        new_speed = 50.0
        self.gorgon.set_movement_speed(new_speed)
        self.assertEqual(self.gorgon.get_movement_speed(), new_speed)
        
        # Test attack speed
        new_attack_speed = 5
        self.gorgon.set_attack_speed(new_attack_speed)
        self.assertEqual(self.gorgon.get_attack_speed(), new_attack_speed)
        
        # Test hit points
        new_hp = 60
        self.gorgon.setHitPoints(new_hp)  # Using legacy method
        self.assertEqual(self.gorgon.getHitPoints(), new_hp)  # Using legacy method
        self.assertEqual(self.gorgon.get_health(), new_hp)  # Using new method

    def test_string_representation(self):
        """Test the string representation of the gorgon"""
        goblin_str = str(self.gorgon)
        
        # Check that string contains important information
        self.assertIn("Gorgon", gorgon_str)
        self.assertIn(self.gorgon.get_special_skill(), gorgon_str)
        self.assertIn(f"Attack Speed: {self.gorgon.get_attack_speed()}", gorgon_str)
        self.assertIn(f"Movement Speed: {self.gorgon.get_movement_speed()}", gorgon_str)


if __name__ == '__main__':
    unittest.main()