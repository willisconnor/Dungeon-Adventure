from game import Game


def main():
    """Entry point for the game"""
    # Create game with 1000x750 resolution
    game = Game(1000, 750)

    # Initialize game state
    game.init_game()

    # Run the game loop
    game.run()


if __name__ == "__main__":
    main()