import pygame


class InputHandler:
    """Handles user input"""

    def __init__(self):
        self.keys = None
        self.space_pressed = False
        self.space_released = True  # Track if space was released to prevent multiple inputs
        self.debug_key_pressed = False
        self.debug_key_released = True

    def process_input(self):
        """Process all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Signal to quit the game

            # Track spacebar press and release
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.space_released:  # Only register if space was released before
                        self.space_pressed = True
                        self.space_released = False
                elif event.key == pygame.K_F1:  # Debug mode toggle
                    if self.debug_key_released:
                        self.debug_key_pressed = True
                        self.debug_key_released = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.space_pressed = False
                    self.space_released = True
                elif event.key == pygame.K_F1:
                    self.debug_key_pressed = False
                    self.debug_key_released = True

        # Get keyboard state
        self.keys = pygame.key.get_pressed()

        return True  # Continue the game

    def update_hero(self, hero):
        """Update hero based on current input state"""
        hero.handle_input(self.keys, self.space_pressed)

        # Reset space_pressed after it's been processed
        if self.space_pressed:
            self.space_pressed = False