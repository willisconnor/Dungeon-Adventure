import random

class Monster:
    def __init__(self, name: str, health: int, attack_damage: int, is_boss: bool):
        self.name = name
        self.health = health
        self.attackDamage = attack_damage
        self.isBoss = is_boss

        # Optional attributes you can set in subclasses
        self.chance_to_hit = 1.0
        self.min_damage = attack_damage
        self.max_damage = attack_damage
        self.chance_to_heal = 0.0
        self.min_heal = 0
        self.max_heal = 0

    def attack(self, player):
        if random.random() <= self.chance_to_hit:
            damage = random.randint(self.min_damage, self.max_damage)
            player.take_damage(damage)
            return damage
        return 0

    def isAlive(self):
        return self.health > 0

    def takeDamage(self, damage):
        self.health -= damage
        if self.health > 0:
            self.try_heal()

    def try_heal(self):
        if random.random() <= self.chance_to_heal:
            heal_amount = random.randint(self.min_heal, self.max_heal)
            self.health += heal_amount
            print(f"{self.name} heals for {heal_amount} HP!")

    def getHitPoints(self):
        return self.health

    def setHitPoints(self, hp):
        self.health = hp
