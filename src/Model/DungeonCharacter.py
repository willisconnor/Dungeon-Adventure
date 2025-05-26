class DungeonCharacter:
    def __init__(self, name: str, hit_points: int, damage_min: int, damage_max: int, attack_speed: float):
        self.character_name = name
        self.hit_points = hit_points
        self.damage_min = damage_min
        self.damage_max = damage_max
        self.attack_speed = attack_speed

    def getHitPoints(self):
        return self.hit_points

    def setHitPoints(self, hp: int):
        self.hit_points = hp

    def getDamage(self):
        return (self.damage_min, self.damage_max)

    def attackBehavior(self):
        pass

    def setAttackSpeed(self, speed: float):
        self.attack_speed = speed
