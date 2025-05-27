from src.model.Adventurer import Adventurer
from src.view.Dungeon import Dungeon


class DungeonAdventure:
    def __init__(self):
        self.dungeon = Dungeon()
        self.adventurer = Adventurer("Player")
        self.gameActive = False
        self.debugMode = False

    def startGame(self) -> bool:
        self.gameActive = True
        return self.gameActive

    def endGame(self) -> bool:
        self.gameActive = False
        return self.gameActive

    def printCurrentRoom(self) -> None:
        pass

    def gameLoop(self) -> None:
        pass

    def __str__(self) -> str:
        return "DungeonAdventure Game"
