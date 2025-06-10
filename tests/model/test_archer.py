import unittest
from unittest.mock import MagicMock, patch
from src.model.archer import Archer
from src.model.DungeonEntity import Direction


class TestArcher(unittest.TestCase):
    """Tests for the Archer hero class"""

    def setUp(self):
        """Set up an Archer instance for testing"""
        self.x, self.y = 100, 200
        self.archer = Archer(self.x, self.y)

    def test_initialization(self):
        """Test that an Archer is initialized with correct values"""
        self.assertEqual(self.archer.get_x(), self.x)
        self.assertEqual(self.archer.get_y(), self.y)
        self.assertEqual(self.archer.get_hero_type(), "archer")
        self.assertTrue(self.archer.get_is_alive())
        
        # Archer specific attributes
        self.assertGreater(self.archer.get_attack_range(), 0)  # Should have positive attack range
        if hasattr(self.archer, "get_arrow_damage"):
            self.assertGreater(self.archer.get_arrow_damage(), 0)
        if hasattr(self.archer, "get_arrow_speed"):
            self.assertGreater(self.archer.get_arrow_speed(), 0)

    def test_calculate_damage(self):
        """Test archer damage calculation"""
        # Create a mock target
        target = MagicMock()
        
        # Test normal damage
        base_damage = self.archer.get_damage()
        damage = self.archer.calculate_damage(target)
        self.assertEqual(damage, base_damage)  # Default damage without any modifiers
        
        # Test different distances if archer has distance bonus
        if hasattr(self.archer, "get_distance_damage_bonus"):
            # Set archer position
            self.archer.set_x(100)
            self.archer.set_y(100)
            
            # Test with a distant target
            target.get_x.return_value = 300
            target.get_y.return_value = 100
            far_damage = self.archer.calculate_damage(target)
            
            # Test with a close target
            target.get_x.return_value = 120
            target.get_y.return_value = 100
            close_damage = self.archer.calculate_damage(target)
            
            # Damage should be higher at optimal range
            self.assertGreaterEqual(far_damage, close_damage)

    def test_special_ability(self):
        """Test archer's special ability activation"""
        # Create a mock for the parent class method
        with patch('src.model.DungeonHero.Hero.activate_special_ability') as mock_parent:
            # Create a mock projectile manager if needed
            if hasattr(self.archer, "get_projectile_manager") or hasattr(self.archer, "projectile_manager"):
                projectile_manager = MagicMock()
                if hasattr(self.archer, "set_projectile_manager"):
                    self.archer.set_projectile_manager(projectile_manager)
                else:
                    self.archer.projectile_manager = projectile_manager
                
                # Activate special ability
                self.archer.activate_special_ability()
                
                # Verify parent method was called
                mock_parent.assert_called_once()
                
                # Verify projectile was created
                projectile_manager.add_projectile.assert_called()
            else:
                # Just test that the method runs without error
                self.archer.activate_special_ability()
                mock_parent.assert_called_once()

    def test_attack(self):
        """Test archer's attack method if it has one"""
        if hasattr(self.archer, "attack") and callable(getattr(self.archer, "attack")):
            # Set up targets
            target1 = MagicMock()
            target1.is_alive = True
            target1.hitbox = MagicMock()
            target1.hitbox.colliderect.return_value = True
            target1.take_damage.return_value = True
            
            target2 = MagicMock()
            target2.is_alive = True
            target2.hitbox = MagicMock()
            target2.hitbox.colliderect.return_value = False
            
            targets = [target1, target2]
            
            # Set archer to attacking state
            if hasattr(self.archer, "set_is_attacking"):
                self.archer.set_is_attacking(True)
            elif hasattr(self.archer, "is_attacking"):
                self.archer.is_attacking = True
            
            # Mock get_attack_hitbox if needed
            if hasattr(self.archer, "get_attack_hitbox"):
                original_get_attack_hitbox = self.archer.get_attack_hitbox
                self.archer.get_attack_hitbox = MagicMock(return_value=MagicMock())
            
            # Call attack method
            hit_targets = self.archer.attack(targets)
            
            # Verify results
            self.assertEqual(len(hit_targets), 1)
            self.assertIn(target1, hit_targets)
            self.assertNotIn(target2, hit_targets)
            target1.take_damage.assert_called_once()
            
            # Restore original method if mocked
            if hasattr(self.archer, "get_attack_hitbox") and self.archer.get_attack_hitbox != original_get_attack_hitbox:
                self.archer.get_attack_hitbox = original_get_attack_hitbox

    def test_string_representation(self):
        """Test the string representation of the archer"""
        archer_str = str(self.archer)
        
        # Check that string contains important information
        self.assertIn("archer", archer_str.lower())
        
        # Check if health is included
        health_str = f"{self.archer.get_health()}/{self.archer.get_max_health()}"
        self.assertIn(health_str, archer_str)


if __name__ == '__main__':
    unittest.main()