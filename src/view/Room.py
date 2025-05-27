class Room:
    def __init__(self, row: int, col: int):
        self.rows = row
        self.cols = col
        self.visited = False
        self.northDoor = False
        self.eastDoor = False
        self.southDoor = False
        self.westDoor = False
        self.hasLoot = False
        self.possibleLoot = []

    def getRoom(self, row: int, col: int) -> int:
        pass

    def __str__(self) -> str:
        return "Room info"

    def dropLoot(self, hasLoot: bool, possibleLoot: list):
        pass