import unittest
from unittest.mock import MagicMock, patch
from src.model.DungeonHero import Hero
from src.model.DungeonEntity import Direction, AnimationState


class TestDungeonHero(unittest.TestCase):
    """Tests for the DungeonHero base class"""

    def setUp(self):
        """Set up a Hero instance for testing"""
        self.x, self.y = 100, 200
        self.hero_type = "test_hero"
        # Use a concrete implementation of the hero
        self.hero = Hero(self.x, self.y, hero_type=self.hero_type)

    def test_initialization(self):
        """Test that a Hero is initialized with correct values"""
        self.assertEqual(self.hero.get_x(), self.x)
        self.assertEqual(self.hero.get_y(), self.y)
        self.assertEqual(self.hero.get_hero_type(), self.hero_type)
        self.assertTrue(self.hero.get_is_alive())
        
        # Default values
        self.assertGreater(self.hero.get_max_health(), 0)
        self.assertEqual(self.hero.get_health(), self.hero.get_max_health())
        self.assertGreater(self.hero.get_damage(), 0)
        self.assertGreater(self.hero.get_speed(), 0)
        self.assertFalse(self.hero.is_attacking())
        self.assertFalse(self.hero.is_invulnerable())

    def test_take_damage(self):
        """Test hero taking damage"""
        initial_health = self.hero.get_health()
        damage = 20
        
        # Hero takes damage
        self.hero.take_damage(damage)
        
        # Check health reduction
        self.assertEqual(self.hero.get_health(), initial_health - damage)
        self.assertTrue(self.hero.is_invulnerable())  # Should be temporarily invulnerable

    def test_fatal_damage(self):
        """Test hero taking fatal damage"""
        # Set hero to low health
        self.hero.set_health(10)
        
        # Take fatal damage
        self.hero.take_damage(20)
        
        # Check result and state
        self.assertEqual(self.hero.get_health(), 0)
        self.assertFalse(self.hero.get_is_alive())

    def test_damage_while_invulnerable(self):
        """Test that hero doesn't take damage while invulnerable"""
        # Make hero invulnerable
        self.hero._Hero__is_invulnerable = True
        initial_health = self.hero.get_health()
        
        # Try to damage hero
        self.hero.take_damage(20)
        
        # Check health didn't change
        self.assertEqual(self.hero.get_health(), initial_health)

    def test_heal(self):
        """Test healing functionality"""
        # Take some damage first
        self.hero.take_damage(30)
        damaged_health = self.hero.get_health()
        
        # Heal partial amount
        healing_amount = 20
        self.hero.heal(healing_amount)
        
        # Check healing
        self.assertEqual(self.hero.get_health(), damaged_health + healing_amount)
        
        # Heal beyond max health
        self.hero.heal(100)
        
        # Check health is capped at max
        self.assertEqual(self.hero.get_health(), self.hero.get_max_health())

    def test_attack_start_and_complete(self):
        """Test starting and completing an attack"""
        # Verify not attacking initially
        self.assertFalse(self.hero.is_attacking())
        
        # Start attack
        self.hero.start_attack()
        
        # Verify now attacking
        self.assertTrue(self.hero.is_attacking())
        self.assertEqual(self.hero.get_animation_state(), AnimationState.ATTACKING_1)
        
        # Complete attack
        self.hero.complete_attack()
        
        # Verify attack completed
        self.assertFalse(self.hero.is_attacking())

    def test_activate_special_ability(self):
        """Test activating special ability"""
        # Verify not using special initially
        self.assertFalse(self.hero.is_using_special())
        
        # Activate special
        self.hero.activate_special_ability()
        
        # Verify now using special
        self.assertTrue(self.hero.is_using_special())

    def test_movement(self):
        """Test hero movement"""
        initial_x = self.hero.get_x()
        initial_y = self.hero.get_y()
        
        # Move right
        self.hero.move(Direction.RIGHT, 1.0)
        self.assertGreater(self.hero.get_x(), initial_x)
        self.assertEqual(self.hero.get_direction(), Direction.RIGHT)
        
        # Move left
        new_x = self.hero.get_x()
        self.hero.move(Direction.LEFT, 1.0)
        self.assertLess(self.hero.get_x(), new_x)
        self.assertEqual(self.hero.get_direction(), Direction.LEFT)

    def test_jump(self):
        """Test hero jumping"""
        initial_y = self.hero.get_y()
        
        # Start jump
        self.hero.jump()
        
        # Check vertical velocity is negative (upward)
        self.assertLess(self.hero.get_velocity_y(), 0)
        
        # Update to simulate jump physics
        self.hero.update(0.1)
        
        # Should be moving upward
        self.assertLess(self.hero.get_y(), initial_y)

    def test_update_invulnerability(self):
        """Test invulnerability timer updates"""
        # Make hero invulnerable
        self.hero._Hero__is_invulnerable = True
        self.hero._Hero__invulnerable_timer = 0.5
        
        # Update with small dt
        self.hero.update(0.1)
        
        # Should still be invulnerable but timer decreased
        self.assertTrue(self.hero.is_invulnerable())
        self.assertLess(self.hero._Hero__invulnerable_timer, 0.5)
        
        # Update with large dt to end invulnerability
        self.hero.update(1.0)
        
        # Should no longer be invulnerable
        self.assertFalse(self.hero.is_invulnerable())

    def test_string_representation(self):
        """Test the string representation of the hero"""
        hero_str = str(self.hero)
        
        # Check that string contains important information
        self.assertIn(self.hero_type, hero_str)
        self.assertIn(f"HP: {self.hero.get_health()}/{self.hero.get_max_health()}", hero_str)
        self.assertIn(f"DMG: {self.hero.get_damage()}", hero_str)


if __name__ == '__main__':
    unittest.main()