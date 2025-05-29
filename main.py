####Connor Willis ####
#entry point, single room testing for now
import pygame
import sys
import os

#add the src directory to python path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.model.Game import Game, GameState
from src.model.knight import Knight
from src.model.archer import Archer
from src.model.cleric import Cleric
from enum import Enum, auto



def main():
    """Main entry point for video game"""

    #iniitialiize pygame
    pygame.init()

    #initialize db if doesnt exist
    if not os.path.exists('game_data.db'):
        print("Initializing database...")
        from src.utils.SQLite_DB_Implementation import initialize_databse
        initialize_databse()
        print("Database initialized.")


    #set up display
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Dungeon Adventure - Single Room Test')

    #create the game
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)

    #init and start the game
    #loop already implemented in Game.gameLoop()
    game._initialize_game()
    game.state = GameState.MENU

    print("Starting game...")
    print("Controls: ")
    print("- A/D: Move left/right")
    print("- SPACE: Attack")
    print("- Q: Special ability")
    print("- E: Defend")
    print("- 1/2/3: Switch heroes")
    print("- ESC: Pause")

    #run the game loop
    game.gameLoop()
