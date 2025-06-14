import unittest
from unittest.mock import MagicMock, patch
from src.model.Skeleton import Skeleton

class TestSkeleton(unittest.TestCase):
    """Tests for the Skeleton class"""

    def setUp(self):
        """Set up a Skeleton instance for testing"""
        self.skeleton = Skeleton()

    def test_initialization(self):
        """Test that a skeleton is initialized with correct values"""
        self.assertEqual(self.skeleton.get_name(), "Skeleton")
        self.assertGreater(self.skeleton.get_health(), 0)
        self.assertFalse(self.skeleton.is_boss_monster())
        
        # Skeleton specific values
        self.assertGreater(self.skeleton.get_chance_to_hit(), 0)
        min_damage, max_damage = self.skeleton.get_damage_range()
        self.assertLessEqual(min_damage, max_damage)  # Damage range should be valid
        
        # Check if skeleton has undead type
        if hasattr(self.skeleton, "get_enemy_type"):
            self.assertEqual(self.skeleton.get_enemy_type(), "undead")

    def test_attack(self):
        """Test skeleton's attack method"""
        # Create a mock player
        mock_player = MagicMock()
        mock_player.take_damage = MagicMock()
        
        # Mock random.random to guarantee a hit
        with patch('random.random', return_value=0.1):
            # Mock random.randint to get consistent damage
            with patch('random.randint', return_value=15):
                # Skeleton attacks player
                damage_dealt = self.skeleton.attack(mock_player)
                
                # Verify damage
                self.assertEqual(damage_dealt, 15)
                mock_player.take_damage.assert_called_once_with(15)

    def test_attack_miss(self):
        """Test skeleton's attack when it misses"""
        # Create a mock player
        mock_player = MagicMock()
        mock_player.take_damage = MagicMock()
        
        # Mock random.random to guarantee a miss
        with patch('random.random', return_value=0.99):
            # Skeleton attacks player
            damage_dealt = self.skeleton.attack(mock_player)
            
            # Verify attack missed
            self.assertEqual(damage_dealt, 0)
            mock_player.take_damage.assert_not_called()

    def test_take_damage_from_normal_attack(self):
        """Test skeleton taking damage from normal attack"""
        initial_health = self.skeleton.get_health()
        damage = 20
        
        # Simulate normal attack
        self.skeleton.take_damage(damage)
        
        # Check health reduction
        self.assertEqual(self.skeleton.get_health(), initial_health - damage)

    def test_special_vulnerability(self):
        """Test skeleton's special vulnerability to certain attacks"""
        # Only test if the skeleton has vulnerability to certain damage types
        if hasattr(self.skeleton, "take_damage_with_type"):
            initial_health = self.skeleton.get_health()
            damage = 20
            
            # Test regular damage
            self.skeleton.take_damage_with_type(damage, "physical")
            expected_health = initial_health - damage
            self.assertEqual(self.skeleton.get_health(), expected_health)
            
            # Reset health
            self.skeleton.set_health(initial_health)
            
            # Test damage type skeleton is vulnerable to (like holy/fire)
            vulnerable_type = "holy"  # Assuming skeletons are weak to holy damage
            self.skeleton.take_damage_with_type(damage, vulnerable_type)
            # Should take more damage from vulnerable type
            self.assertLess(self.skeleton.get_health(), initial_health - damage)

    def test_special_ability(self):
        """Test skeleton's special ability if available"""
        if hasattr(self.skeleton, "resurrect") and callable(getattr(self.skeleton, "resurrect")):
            # Kill the skeleton
            self.skeleton.take_damage(self.skeleton.get_health() + 10)
            self.assertFalse(self.skeleton.is_alive())
            
            # Try to resurrect
            resurrected = self.skeleton.resurrect()
            
            # If resurrection succeeded, skeleton should be alive again
            if resurrected:
                self.assertTrue(self.skeleton.is_alive())
                self.assertGreater(self.skeleton.get_health(), 0)

    def test_string_representation(self):
        """Test the string representation of the skeleton"""
        skeleton_str = str(self.skeleton)
        
        # Check that string contains important information
        self.assertIn("Skeleton", skeleton_str)
        
        # Check for health in string
        health_str = f"{self.skeleton.get_health()}"
        self.assertIn(health_str, skeleton_str)


if __name__ == '__main__':
    unittest.main()