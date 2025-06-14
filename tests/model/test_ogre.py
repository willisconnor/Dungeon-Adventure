import unittest
from unittest.mock import MagicMock, patch
from src.model.Ogre import Ogre


class TestOgre(unittest.TestCase):
    """Tests for the Ogre class"""

    def setUp(self):
        """Set up an Ogre instance for testing"""
        self.ogre = Ogre()

    def test_initialization(self):
        """Test that an ogre is initialized with correct values"""
        self.assertEqual(self.ogre.get_name(), "Ogre")
        self.assertGreater(self.ogre.get_health(), 0)
        self.assertFalse(self.ogre.is_boss_monster())
        
        # Ogre specific values
        self.assertGreater(self.ogre.get_chance_to_hit(), 0)
        min_damage, max_damage = self.ogre.get_damage_range()
        self.assertGreater(max_damage, min_damage)  # Damage range should be valid
        
        # Ogre should have some specific attributes
        if hasattr(self.ogre, "get_strength"):
            self.assertGreater(self.ogre.get_strength(), 0)

    def test_attack(self):
        """Test ogre's attack method"""
        # Create a mock player
        mock_player = MagicMock()
        mock_player.take_damage = MagicMock()
        
        # Mock random.random to guarantee a hit
        with patch('random.random', return_value=0.1):
            # Mock random.randint to get consistent damage
            with patch('random.randint', return_value=30):
                # Ogre attacks player
                damage_dealt = self.ogre.attack(mock_player)
                
                # Verify damage
                self.assertEqual(damage_dealt, 30)
                mock_player.take_damage.assert_called_once_with(30)

    def test_attack_miss(self):
        """Test ogre's attack when it misses"""
        # Create a mock player
        mock_player = MagicMock()
        mock_player.take_damage = MagicMock()
        
        # Mock random.random to guarantee a miss (hit chance should be < 1.0)
        with patch('random.random', return_value=0.99):
            # Ogre attacks player
            damage_dealt = self.ogre.attack(mock_player)
            
            # Verify attack missed
            self.assertEqual(damage_dealt, 0)
            mock_player.take_damage.assert_not_called()

    def test_take_damage_and_rage(self):
        """Test ogre taking damage and potentially entering rage state"""
        initial_health = self.ogre.get_health()
        
        # Take damage
        self.ogre.take_damage(initial_health // 2)
        
        # Check rage state if applicable
        if hasattr(self.ogre, "is_enraged"):
            # Ogre might be enraged after taking significant damage
            enraged = self.ogre.is_enraged()
            
            # If enraged, damage should be boosted
            if enraged and hasattr(self.ogre, "get_damage_range"):
                min_damage, max_damage = self.ogre.get_damage_range()
                self.assertGreater(min_damage, 0)  # Damage should be positive
        
        # Test that ogre is still alive
        self.assertTrue(self.ogre.is_alive())

    def test_special_attack(self):
        """Test ogre's special attack if available"""
        if hasattr(self.ogre, "special_attack"):
            # Create a mock player
            mock_player = MagicMock()
            mock_player.take_damage = MagicMock()
            
            # Use special attack
            damage = self.ogre.special_attack(mock_player)
            
            # Verify damage is positive
            self.assertGreaterEqual(damage, 0)
            
            # Verify player took damage if attack hit
            if damage > 0:
                mock_player.take_damage.assert_called_once_with(damage)

    def test_string_representation(self):
        """Test the string representation of the ogre"""
        ogre_str = str(self.ogre)
        
        # Check that string contains important information
        self.assertIn("Ogre", ogre_str)
        
        # Check for specific ogre attributes in string
        if hasattr(self.ogre, "get_strength"):
            self.assertIn(str(self.ogre.get_strength()), ogre_str)

#Testing
if __name__ == '__main__':
    unittest.main()