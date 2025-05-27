from src.model.DungeonCharacter import DungeonCharacter


class Hero(DungeonCharacter):
    def __init__(self, name: str):
        super().__init__(name, 100, 10, 20, 1.0)
        self.blockChance = 0.2
        self.specialSkill = None
        self.cooldownForSkill = 0.0
        self.movementSpeed = 1.0

    def specialSkill(self):
        pass

    def attack(self):
        pass