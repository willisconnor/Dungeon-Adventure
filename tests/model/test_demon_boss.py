import unittest
from unittest.mock import MagicMock, patch
import pygame
from src.model.DemonBoss import DemonBoss
from src.model.DungeonEntity import Direction, AnimationState

# Mock pygame.Rect to avoid actual pygame initialization
class MockRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def colliderect(self, other):
        # Simple collision check
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

# Mock pygame.Surface
class MockSurface:
    def __init__(self, size):
        self.size = size
        
    def fill(self, color):
        pass


class TestDemonBoss(unittest.TestCase):
    """Tests for the DemonBoss class"""

    def setUp(self):
        """Set up a DemonBoss instance for testing"""
        # Mock pygame dependencies
        pygame.Surface = MagicMock(return_value=MockSurface((128, 128)))
        pygame.Rect = MagicMock(side_effect=MockRect)
        
        self.x, self.y = 300, 400
        self.boss = DemonBoss(self.x, self.y)

    def test_initialization(self):
        """Test that a DemonBoss is initialized with correct values"""
        self.assertEqual(self.boss.get_x(), self.x)
        self.assertEqual(self.boss.get_y(), self.y)
        self.assertEqual(self.boss.get_name(), "Demon Boss")
        self.assertEqual(self.boss.get_enemy_type(), "demon_boss")
        self.assertEqual(self.boss.get_max_health(), 500)
        self.assertEqual(self.boss.get_health(), 500)
        self.assertEqual(self.boss.get_damage(), 25)
        self.assertEqual(self.boss.get_attack_range(), 120)
        self.assertTrue(self.boss.is_alive)
        self.assertFalse(self.boss.is_enraged())

    def test_take_damage(self):
        """Test boss taking damage"""
        initial_health = self.boss.get_health()
        damage = 50
        
        # Boss takes damage
        result = self.boss.take_damage(damage)
        
        # Check result and health
        self.assertTrue(result)
        self.assertEqual(self.boss.get_health(), initial_health - damage)
        self.assertEqual(self.boss.get_animation_state(), AnimationState.HURT)
        self.assertTrue(self.boss.is_invulnerable())

    def test_fatal_damage(self):
        """Test boss taking fatal damage"""
        # Set boss to low health
        self.boss.health = 20
        
        # Take fatal damage
        result = self.boss.take_damage(50)
        
        # Check result and state
        self.assertTrue(result)
        self.assertEqual(self.boss.get_health(), 0)
        self.assertFalse(self.boss.is_alive)
        self.assertEqual(self.boss.get_animation_state(), AnimationState.DYING)

    def test_damage_while_invulnerable(self):
        """Test that boss doesn't take damage while invulnerable"""
        # Make boss invulnerable
        self.boss._DemonBoss__is_invulnerable = True
        initial_health = self.boss.get_health()
        
        # Try to damage boss
        result = self.boss.take_damage(50)
        
        # Check result and health
        self.assertFalse(result)
        self.assertEqual(self.boss.get_health(), initial_health)

    def test_enrage_threshold(self):
        """Test that boss enrages at low health"""
        # Boss starts not enraged
        self.assertFalse(self.boss.is_enraged())
        
        # Set health just above threshold
        threshold = self.boss.get_enrage_threshold()
        self.boss.health = int(self.boss.get_max_health() * threshold) + 1
        
        # Update boss to check enrage state
        self.boss.update(0.1)
        self.assertFalse(self.boss.is_enraged())
        
        # Drop health below threshold
        self.boss.health = int(self.boss.get_max_health() * threshold) - 1
        
        # Update boss to check enrage state
        self.boss.update(0.1)
        self.assertTrue(self.boss.is_enraged())
        
        # Check that damage and speed were increased
        self.assertGreater(self.boss.get_damage(), 25)  # Original damage
        self.assertGreater(self.boss.get_speed(), 3)   # Original speed

    def test_attack_cooldown(self):
        """Test attack cooldown mechanics"""
        # Create a mock target
        target = MagicMock()
        target.hitbox = MockRect(self.x + 50, self.y, 50, 50)  # Within attack range
        
        # Initial attack should succeed
        initial_attack = self.boss.attack(target)
        self.assertTrue(initial_attack)
        self.assertTrue(self.boss.is_attacking())
        self.assertGreater(self.boss.get_attack_cooldown(), 0)
        
        # Second attack should fail due to cooldown
        second_attack = self.boss.attack(target)
        self.assertFalse(second_attack)
        
        # Reduce cooldown
        self.boss._update_attack_cooldown(1.0)
        
        # Attack should still fail as cooldown may not be fully reset
        third_attack = self.boss.attack(target)
        self.assertFalse(third_attack)
        
        # Fully reset cooldown
        self.boss._DemonBoss__attack_cooldown = 0
        self.boss._DemonBoss__is_attacking = False
        
        # Attack should succeed now
        fourth_attack = self.boss.attack(target)
        self.assertTrue(fourth_attack)

    def test_move_towards_target(self):
        """Test boss movement towards target"""
        initial_x = self.boss.get_x()
        initial_y = self.boss.get_y()
        
        # Target is far to the right
        target_x = initial_x + 500
        target_y = initial_y
        
        # Move towards target
        self.boss.move_towards_target(target_x, target_y, 0.1)
        
        # Boss should have moved right
        self.assertGreater(self.boss.get_x(), initial_x)
        self.assertEqual(self.boss.get_direction(), Direction.RIGHT)
        self.assertEqual(self.boss.get_animation_state(), AnimationState.WALKING)
        
        # Reset position
        self.boss.x = initial_x
        self.boss.y = initial_y
        
        # Target is within attack range
        target_x = initial_x + 50  # Within attack_range (120)
        target_y = initial_y
        
        # Move towards target
        self.boss.move_towards_target(target_x, target_y, 0.1)
        
        # Boss should not have moved (in attack range)
        self.assertEqual(self.boss.get_x(), initial_x)
        self.assertEqual(self.boss.get_animation_state(), AnimationState.IDLE)
        
        # Test not moving when attacking
        self.boss._DemonBoss__is_attacking = True
        
        # Target is far
        target_x = initial_x + 500
        target_y = initial_y
        
        # Try to move
        self.boss.move_towards_target(target_x, target_y, 0.1)
        
        # Boss should not have moved (is attacking)
        self.assertEqual(self.boss.get_x(), initial_x)

    def test_string_representation(self):
        """Test the string representation of the boss"""
        boss_str = str(self.boss)
        
        # Check that string contains important information
        self.assertIn("Demon Boss", boss_str)
        self.assertIn("HP: 500/500", boss_str)
        self.assertIn("DMG: 25", boss_str)
        self.assertIn("Normal", boss_str)  # Not enraged
        
        # Enrage boss and check updated string
        self.boss._DemonBoss__enraged = True
        boss_str = str(self.boss)
        self.assertIn("ENRAGED", boss_str)


if __name__ == '__main__':
    unittest.main()