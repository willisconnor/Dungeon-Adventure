class Monster:
    def __init__(self, name: str, health: int, attack_damage: int, is_boss: bool):
        self.name = name
        self.health = health
        self.attackDamage = attack_damage
        self.isBoss = is_boss

    def monsterType(self) -> str:
        return self.name

    def attack(self, player) -> int:
        return self.attackDamage

    def isAlive(self) -> bool:
        return self.health > 0

    def takeDamage(self, damage: int):
        self.health -= damage