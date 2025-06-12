import pygame
from hero import Hero
from enemy import Skeleton
from input_handler import InputHandler
from collision_handler import CollisionHandler
from animation import Animation
from renderer import Renderer
from spritesheet import SpriteSheet


class Game:
    """Main game class"""

    def __init__(self, screen_width, screen_height):
        # Initialize pygame
        pygame.init()

        # Create the game window
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Dungeon Fighter MVC')

        # Create background
        self.bg_color = (50, 50, 50)

        # Initialize game systems
        self.animation_manager = Animation()
        self.renderer = Renderer(self.screen, self.animation_manager)
        self.input_handler = InputHandler()
        self.collision_handler = CollisionHandler()

        # Game entities
        self.entities = []

        # Game state
        self.running = True
        self.clock = pygame.time.Clock()
        self.delta_time = 0

    def init_game(self):
        """Initialize the game state"""
        # Load animations
        self.animation_manager.load_hero_animations()
        self.animation_manager.load_skeleton_animations()

        # Create player character at center of screen
        self.hero = Hero(self.screen_width // 2, self.screen_height // 2)
        self.entities.append(self.hero)

        # Create skeleton enemy
        self.skeleton = Skeleton(self.screen_width // 2 + 150, self.screen_height // 2)
        self.skeleton.set_target(self.hero)
        self.entities.append(self.skeleton)

        # Register entities with collision handler
        self.collision_handler.register_entities(self.entities)

    def run(self):
        """Main game loop"""
        while self.running:
            # Calculate delta time (time since last frame)
            self.delta_time = self.clock.tick(60) / 1000.0  # Convert to seconds

            # Process input
            self.running = self.input_handler.process_input()

            # Toggle debug mode if F1 is pressed
            if self.input_handler.debug_key_pressed:
                self.renderer.toggle_debug_mode()
                self.input_handler.debug_key_pressed = False

            # Update game state
            self.update()

            # Render frame
            self.render()

            # Update display
            pygame.display.update()

        # Clean up
        pygame.quit()

    def update(self):
        """Update game state"""
        # Update hero based on input
        self.input_handler.update_hero(self.hero)

        # Update all entities
        for entity in self.entities:
            entity.update(self.delta_time)

        # Update collision detection
        self.collision_handler.update()

    def render(self):
        """Render game frame"""
        # Clear screen
        self.screen.fill(self.bg_color)

        # Render entities
        self.renderer.render(self.entities)