
import unittest
from unittest.mock import MagicMock, patch
import pygame
from src.model.Hero_Movement_Extension import HeroMovementExtension
from src.model.DungeonEntity import Direction, AnimationState


class HeroWithMovement(HeroMovementExtension):
    """Test class that inherits from HeroMovementExtension mixin"""
    
    def __init__(self):
        # Initialize properties that would normally be in a Hero class
        self.x = 100
        self.y = 200
        self.speed = 5
        self.animation_state = AnimationState.IDLE
        self.direction = Direction.RIGHT
        self.is_alive = True
        self.is_attacking = False
        self.attack_complete = True
        self.hit_targets = []
        self.attack_range = 50
        self.frame_index = 0
        self.animation_counter = 0
        self.frame_rates = {
            AnimationState.IDLE: 10,
            AnimationState.RUNNING: 8,
            AnimationState.ATTACKING: 6
        }
        
        # Initialize movement extension
        self.initialize_movement_capabilities()
    
    def calculate_damage(self, target):
        """Mock implementation of calculate_damage"""
        return 10


class TestHeroMovementExtension(unittest.TestCase):
    """Tests for the HeroMovementExtension mixin class"""

    def setUp(self):
        """Set up a hero with movement capabilities"""
        # Initialize pygame for key constants
        pygame.init()
        
        # Create hero with movement extension
        self.hero = HeroWithMovement()

    def tearDown(self):
        """Clean up pygame"""
        pygame.quit()

    def test_initialization(self):
        """Test that movement properties are initialized correctly"""
        # Check jumping properties
        self.assertFalse(self.hero.is_jumping)
        self.assertFalse(self.hero.is_falling)
        self.assertEqual(self.hero.jump_velocity, 15)
        self.assertEqual(self.hero.jump_height, 200)
        self.assertEqual(self.hero.y_velocity, 0)
        self.assertEqual(self.hero.gravity, 0.8)
        self.assertEqual(self.hero.ground_y, self.hero.y)
        
        # Check running properties
        self.assertFalse(self.hero.is_running)
        self.assertEqual(self.hero.run_speed, self.hero.speed * 1.5)
        self.assertEqual(self.hero.run_threshold, 10)
        self.assertEqual(self.hero.run_counter, 0)
        
        # Check running attack properties
        self.assertFalse(self.hero.is_running_attacking)
        self.assertEqual(self.hero.running_attack_damage_multiplier, 1.3)
        
        # Check frame rates were updated
        self.assertEqual(self.hero.frame_rates[AnimationState.RUNNING], 5)
        self.assertEqual(self.hero.frame_rates[AnimationState.JUMPING], 4)
        self.assertEqual(self.hero.frame_rates[AnimationState.FALLING], 4)
        self.assertEqual(self.hero.frame_rates[AnimationState.RUNNING_ATTACK], 5)

    def test_jump_mechanics(self):
        """Test jumping mechanics"""
        # Initial state
        self.assertFalse(self.hero.is_jumping)
        self.assertFalse(self.hero.is_falling)
        initial_y = self.hero.y
        
        # Start jump
        self.hero.start_jump()
        
        # Should now be jumping
        self.assertTrue(self.hero.is_jumping)
        self.assertFalse(self.hero.is_falling)
        self.assertEqual(self.hero.y_velocity, -15)  # Initial upward velocity
        
        # Update movement (should move upward)
        self.hero.update_movement(1.0)
        self.assertLess(self.hero.y, initial_y)  # Y should decrease (moving up)
        
        # Keep updating until reaching apex
        while self.hero.is_jumping:
            self.hero.update_movement(1.0)
        
        # Should now be falling
        self.assertFalse(self.hero.is_jumping)
        self.assertTrue(self.hero.is_falling)
        self.assertGreaterEqual(self.hero.y_velocity, 0)  # Velocity should be positive (downward)
        
        # Keep updating until reaching ground
        while self.hero.is_falling:
            self.hero.update_movement(1.0)
        
        # Should now be back on ground
        self.assertFalse(self.hero.is_jumping)
        self.assertFalse(self.hero.is_falling)
        self.assertEqual(self.hero.y, self.hero.ground_y)
        self.assertEqual(self.hero.y_velocity, 0)

    def test_running_mechanics(self):
        """Test running mechanics"""
        # Create mock keys dictionary
        keys = {
            pygame.K_a: False,
            pygame.K_d: True,
            pygame.K_LSHIFT: True,
            pygame.K_SPACE: False,
            pygame.K_x: False
        }
        
        # Initial state
        self.assertFalse(self.hero.is_running)
        self.assertEqual(self.hero.run_counter, 0)
        
        # Not enough frames for running yet
        self.hero.handle_extended_input(keys, 1.0)
        self.assertFalse(self.hero.is_running)
        self.assertEqual(self.hero.run_counter, 1)
        
        # Simulate multiple frames to reach run threshold
        for _ in range(self.hero.run_threshold - 1):
            self.hero.handle_extended_input(keys, 1.0)
        
        # Should now be running
        self.assertTrue(self.hero.is_running)
        self.assertEqual(self.hero.run_counter, self.hero.run_threshold)
        
        # Stop running when shift is released
        keys[pygame.K_LSHIFT] = False
        self.hero.handle_extended_input(keys, 1.0)
        self.assertFalse(self.hero.is_running)
        self.assertEqual(self.hero.run_counter, 0)

    def test_running_attack(self):
        """Test running attack mechanics"""
        # Set up for running attack
        self.hero.is_running = True
        self.hero.is_running_attacking = False
        self.hero.is_attacking = False
        
        # Create mock keys dictionary
        keys = {
            pygame.K_a: False,
            pygame.K_d: True,
            pygame.K_LSHIFT: True,
            pygame.K_SPACE: False,
            pygame.K_x: True  # X key for running attack
        }
        
        # Perform running attack
        self.hero.handle_extended_input(keys, 1.0)
        
        # Should now be running attacking
        self.assertTrue(self.hero.is_running_attacking)
        self.assertFalse(self.hero.attack_complete)
        self.assertEqual(len(self.hero.hit_targets), 0)  # Should be cleared
        
        # Check hitbox creation
        hitbox = self.hero.get_running_attack_hitbox()
        self.assertIsNotNone(hitbox)
        self.assertIsInstance(hitbox, pygame.Rect)
        
        # Hitbox should be in front of character for right direction
        self.assertGreater(hitbox.right, self.hero.x)
        
        # Check damage calculation
        mock_target = MagicMock()
        damage = self.hero.calculate_running_attack_damage(mock_target)
        expected_damage = int(10 * self.hero.running_attack_damage_multiplier)  # 10 is from mock calculate_damage
        self.assertEqual(damage, expected_damage)
        
        # Check animation state update
        self.hero._update_extended_animation_state()
        self.assertEqual(self.hero.animation_state, AnimationState.RUNNING_ATTACK)

    def test_animation_state_priorities(self):
        """Test animation state priorities"""
        # Set various states
        self.hero.is_running_attacking = True
        self.hero.is_jumping = True
        self.hero.is_falling = False
        self.hero.is_running = True
        
        # Running attack should have highest priority
        self.hero._update_extended_animation_state()
        self.assertEqual(self.hero.animation_state, AnimationState.RUNNING_ATTACK)
        
        # Turn off running attack, jumping should be next
        self.hero.is_running_attacking = False
        self.hero._update_extended_animation_state()
        self.assertEqual(self.hero.animation_state, AnimationState.JUMPING)
        
        # Turn off jumping, falling should be next
        self.hero.is_jumping = False
        self.hero.is_falling = True
        self.hero._update_extended_animation_state()
        self.assertEqual(self.hero.animation_state, AnimationState.FALLING)
        
        # Turn off falling, running should be next
        self.hero.is_falling = False
        self.hero._update_extended_animation_state()
        self.assertEqual(self.hero.animation_state, AnimationState.RUNNING)

    def test_handle_input_when_dead(self):
        """Test that input is ignored when character is dead"""
        # Set character as dead
        self.hero.is_alive = False
        
        # Create mock keys dictionary with all keys pressed
        keys = {
            pygame.K_a: True,
            pygame.K_d: True,
            pygame.K_LSHIFT: True,
            pygame.K_SPACE: True,
            pygame.K_x: True
        }
        
        # Handle input
        self.hero.handle_extended_input(keys, 1.0)
        
        # No state should change
        self.assertFalse(self.hero.is_jumping)
        self.assertFalse(self.hero.is_running)
        self.assertFalse(self.hero.is_running_attacking)


if __name__ == '__main__':
    unittest.main()