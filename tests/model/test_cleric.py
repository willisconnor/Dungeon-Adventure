import unittest
from unittest.mock import MagicMock, patch
from src.model.cleric import Cleric
from src.model.DungeonEntity import Direction


class TestCleric(unittest.TestCase):
    """Tests for the Cleric hero class"""

    def setUp(self):
        """Set up a Cleric instance for testing"""
        self.x, self.y = 100, 200
        self.cleric = Cleric(self.x, self.y)

    def test_initialization(self):
        """Test that a Cleric is initialized with correct values"""
        self.assertEqual(self.cleric.get_x(), self.x)
        self.assertEqual(self.cleric.get_y(), self.y)
        self.assertEqual(self.cleric.get_hero_type(), "cleric")
        self.assertTrue(self.cleric.get_is_alive())
        
        # Cleric specific attributes
        self.assertGreater(self.cleric.get_healing_power(), 0)
        self.assertGreater(self.cleric.get_fireball_damage(), 0)
        self.assertGreater(self.cleric.get_fireball_speed(), 0)
        self.assertGreater(self.cleric.get_fireball_range(), 0)

    def test_calculate_damage_normal(self):
        """Test cleric damage calculation for normal enemies"""
        # Create a mock normal enemy
        normal_enemy = MagicMock()
        normal_enemy.enemy_type = "goblin"
        
        base_damage = self.cleric.get_damage()
        damage = self.cleric.calculate_damage(normal_enemy)
        
        # Should be normal damage
        self.assertEqual(damage, base_damage)

    def test_calculate_damage_undead(self):
        """Test cleric damage calculation for undead enemies"""
        # Create a mock undead enemy
        undead_enemy = MagicMock()
        undead_enemy.enemy_type = "undead"
        
        base_damage = self.cleric.get_damage()
        damage = self.cleric.calculate_damage(undead_enemy)
        
        # Should be double damage against undead
        self.assertEqual(damage, base_damage * 2)

    def test_special_ability(self):
        """Test cleric's special ability activation"""
        # Set cleric to less than full health
        self.cleric.set_health(self.cleric.get_max_health() - 30)
        initial_health = self.cleric.get_health()
        
        # Create a mock for the parent class method
        with patch('src.model.DungeonHero.Hero.activate_special_ability') as mock_parent:
            # Create a mock projectile manager
            projectile_manager = MagicMock()
            self.cleric.set_projectile_manager(projectile_manager)
            
            # Activate special ability
            self.cleric.activate_special_ability()
            
            # Verify parent method was called
            mock_parent.assert_called_once()
            
            # Verify healing occurred
            self.assertGreater(self.cleric.get_health(), initial_health)
            
            # Verify fireball was created
            projectile_manager.add_projectile.assert_called_once()

    def test_heal_ally(self):
        """Test cleric's heal ally method"""
        # Create a mock ally
        ally = MagicMock()
        ally.is_alive.return_value = True
        ally.get_max_health.return_value = 100
        ally.get_health.return_value = 60
        
        # Heal ally
        healing_amount = self.cleric.heal_ally(ally)
        
        # Verify healing amount and that ally's health was updated
        self.assertEqual(healing_amount, self.cleric.get_healing_power())
        ally.set_health.assert_called_once_with(60 + self.cleric.get_healing_power())

    def test_heal_ally_at_max_health(self):
        """Test healing an ally that's already at max health"""
        # Create a mock ally at full health
        ally = MagicMock()
        ally.is_alive.return_value = True
        ally.get_max_health.return_value = 100
        ally.get_health.return_value = 100
        
        # Heal ally
        healing_amount = self.cleric.heal_ally(ally)
        
        # Verify no healing occurred
        self.assertEqual(healing_amount, 0)
        ally.set_health.assert_called_once_with(100)

    def test_heal_dead_ally(self):
        """Test attempting to heal a dead ally"""
        # Create a mock dead ally
        dead_ally = MagicMock()
        dead_ally.is_alive.return_value = False
        
        # Attempt to heal
        healing_amount = self.cleric.heal_ally(dead_ally)
        
        # Verify no healing occurred
        self.assertEqual(healing_amount, 0)
        dead_ally.set_health.assert_not_called()

    def test_attack(self):
        """Test cleric's attack method"""
        # Only test if the attack method is available
        if hasattr(self.cleric, "attack") and callable(getattr(self.cleric, "attack")):
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
            
            # Set cleric to attacking state
            if hasattr(self.cleric, "set_is_attacking"):
                self.cleric.set_is_attacking(True)
            elif hasattr(self.cleric, "is_attacking"):
                self.cleric.is_attacking = True
            
            # Mock get_attack_hitbox and get_hit_targets
            with patch.object(self.cleric, 'get_attack_hitbox', return_value=MagicMock()):
                with patch.object(self.cleric, 'get_hit_targets', return_value=set()):
                    with patch.object(self.cleric, 'add_hit_target'):
                        # Call attack method
                        hit_targets = self.cleric.attack(targets)
                        
                        # Verify results
                        self.assertEqual(len(hit_targets), 1)
                        self.assertIn(target1, hit_targets)
                        self.assertNotIn(target2, hit_targets)
                        target1.take_damage.assert_called_once()
                        self.cleric.add_hit_target.assert_called_once_with(target1)

    def test_string_representation(self):
        """Test the string representation of the cleric"""
        cleric_str = str(self.cleric)
        
        # Check that string contains important information
        self.assertIn("cleric", cleric_str.lower())
        self.assertIn(f"Healing Power: {self.cleric.get_healing_power()}", cleric_str)
        self.assertIn(f"Fireball Damage: {self.cleric.get_fireball_damage()}", cleric_str)
        self.assertIn(f"Fireball Range: {self.cleric.get_fireball_range()}", cleric_str)


if __name__ == '__main__':
    unittest.main()