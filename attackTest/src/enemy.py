import pygame
from character import Character
from entity import AnimationState, Direction


class Enemy(Character):
    """Base enemy class"""

    def __init__(self, x, y, max_health, speed, damage):
        super().__init__(x, y, max_health, speed, damage)

        # Enemy-specific properties
        self.target = None  # Target to attack or follow
        self.aggro_range = 300  # Distance at which enemy becomes aggressive
        self.frame_counts = {}  # Will be set by subclasses

    def get_frames_count(self, state):
        """Get the number of frames for a given animation state"""
        return self.frame_counts.get(state, 4)  # Default to 4 if not found

    def set_target(self, target):
        """Set the enemy's target"""
        self.target = target

    def update(self, dt):
        """Update enemy state"""
        super().update(dt)

        # If dead, don't update behavior
        if not self.is_alive:
            return

        # If hurt, don't update behavior until animation completes
        if self.animation_state == AnimationState.HURT:
            return

        # Update behavior based on target
        if self.target and self.target.is_alive:
            self._update_behavior(dt)

    def _update_behavior(self, dt):
        """Update enemy behavior based on target"""
        # This would be implemented by specific enemy types
        pass


class Skeleton(Enemy):
    """Skeleton enemy class"""

    def __init__(self, x, y):
        # Initialize with health=40, speed=0, damage=3
        super().__init__(x, y, max_health=40, speed=0, damage=3)

        # Skeleton's animation frame counts
        self.frame_counts = {
            AnimationState.
            IDLE: 4,
            AnimationState.WALKING: 0,  # Skeleton doesn't move in this implementation
            AnimationState.ATTACKING_1: 0,  # Skeleton doesn't attack in this implementation
            AnimationState.HURT: 4,
            AnimationState.DYING: 4,
            AnimationState.DEAD: 1
        }

        # Set initial animation state
        self.animation_state = AnimationState.IDLE

    def _update_behavior(self, dt):
        """Skeletons don't move or attack in this implementation"""
        # We're just keeping this skeleton stationary
        self.animation_state = AnimationState.IDLE