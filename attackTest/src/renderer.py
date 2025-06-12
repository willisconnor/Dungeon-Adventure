import pygame
from entity import Entity, AnimationState, Direction


class Renderer:
    """Handles rendering game entities to the screen"""

    def __init__(self, screen, animation_manager):
        self.screen = screen
        self.animation_manager = animation_manager
        self.debug_mode = False

    def render(self, entities):
        """Render all game entities"""
        # Sort entities by y position for pseudo-depth
        sorted_entities = sorted(entities, key=lambda e: e.y)

        for entity in sorted_entities:
            self._render_entity(entity)

            # Draw hitboxes in debug mode
            if self.debug_mode:
                self._draw_hitbox(entity)

                # Draw attack hitbox for hero
                if hasattr(entity, 'get_attack_hitbox') and entity.is_attacking:
                    attack_hitbox = entity.get_attack_hitbox()
                    if attack_hitbox:
                        pygame.draw.rect(self.screen, (255, 0, 0), attack_hitbox, 1)

    def _render_entity(self, entity):
        """Render a single entity"""
        # Determine entity type
        entity_type = self._get_entity_type(entity)

        # Get the current animation frame
        current_frame = self.animation_manager.get_frame(
            entity_type,
            entity.animation_state,
            entity.direction,
            entity.frame_index
        )

        if current_frame:
            # Calculate position to center the sprite
            offset_x = current_frame.get_width() // 2
            offset_y = current_frame.get_height() // 2

            # Flash the entity if invulnerable
            alpha = 128 if entity.is_invulnerable and pygame.time.get_ticks() % 200 < 100 else 255

            # Create a copy of the frame for alpha changes if needed
            if alpha < 255:
                frame_copy = current_frame.copy()
                frame_copy.set_alpha(alpha)
                self.screen.blit(frame_copy, (entity.x - offset_x, entity.y - offset_y))
            else:
                self.screen.blit(current_frame, (entity.x - offset_x, entity.y - offset_y))

            # Draw health bar
            self._draw_health_bar(entity)

    def _get_entity_type(self, entity):
        """Determine the entity type for animation lookup"""
        entity_class = entity.__class__.__name__
        if entity_class == "Hero":
            return 'hero'
        elif entity_class == "Skeleton":
            return 'skeleton'
        # Add more entity types as needed
        return 'hero'  # Default fallback

    def _draw_health_bar(self, entity):
        """Draw health bar above the entity"""
        # Only draw health bar if not at full health
        if entity.health < entity.max_health:
            bar_width = 50
            bar_height = 6

            # Position above entity
            x = entity.x - bar_width // 2
            y = entity.y - 60  # Adjust based on sprite size

            # Calculate fill width
            fill_width = int((entity.health / entity.max_health) * bar_width)

            # Draw background
            pygame.draw.rect(self.screen, (64, 64, 64), (x, y, bar_width, bar_height))

            # Draw health fill
            if entity.health > 0:
                # Color based on health percentage
                if entity.health / entity.max_health > 0.6:
                    color = (0, 255, 0)  # Green
                elif entity.health / entity.max_health > 0.3:
                    color = (255, 255, 0)  # Yellow
                else:
                    color = (255, 0, 0)  # Red

                pygame.draw.rect(self.screen, color, (x, y, fill_width, bar_height))

            # Draw outline
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, bar_width, bar_height), 1)

    def _draw_hitbox(self, entity):
        """Draw entity hitbox for debugging"""
        if hasattr(entity, 'hitbox'):
            pygame.draw.rect(self.screen, (0, 255, 0), entity.hitbox, 1)

    def toggle_debug_mode(self):
        """Toggle debug rendering mode"""
        self.debug_mode = not self.debug_mode