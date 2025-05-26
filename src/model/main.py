"""
main.py - Entry point for the dungeon game
"""
import pygame
import sys
from Game import Game


def main():
    """Main entry point for the game"""
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen_width = 1024
    screen_height = 768
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Dungeon Heroes")

    # Create clock for controlling frame rate
    clock = pygame.time.Clock()
    fps = 60

    # Create the game instance
    game = Game(screen, screen_width, screen_height)

    # Game loop
    running = True
    dt = 0

    while running:
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            # Pass events to game
            game.handle_event(event)

        # Update game state
        keys = pygame.key.get_pressed()
        game.update(dt, keys)

        # Draw everything
        game.draw()

        # Update display
        pygame.display.flip()

        # Control frame rate
        dt = clock.tick(fps) / 1000.0  # Convert to seconds

    # Quit
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

