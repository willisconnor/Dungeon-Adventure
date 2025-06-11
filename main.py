####Connor Willis ####
#entry point, single room testing for now
import pygame
import sys
import os

#add the src directory to python path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#print(dir(src.model))
from src.model.Game import Game, GameState
from src.view.Menu import Menu #-- Jayda -- for Menu class
from src.model.tiles import *



def main():
    """Main entry point for video game"""

    #iniitialiize pygame
    pygame.init()

    #initialize db if doesnt exist
    if not os.path.exists('game_data.db'):
        print("Initializing database...")
        try:
            from src.utils.SQLite_DB_Implementation import initialize_database
            initialize_database()
            print("Database initialized!")
        except ImportError:
            print("Warning: Could not import database initialization")
            print("Game will use default values")


    #set up display
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Dungeon Adventure')

    #Jayda -- Show menu and start the game (only line needed)
    menu = Menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    menu.start_game(Game)

    print("Starting game...")
    print("Controls: ")
    print("- A/D: Move left/right")
    print("- SPACE: Attack")
    print("- Q: Special ability")
    print("- E: Defend")
    print("- 1/2/3: Switch heroes")
    print("- ESC: Pause")
    print("- F11: Toggle fullscreen (or use maximize button)")

    #create and run the game
    #game = Game(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    #game.run()

    #cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()