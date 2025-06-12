class CollisionHandler:
    """Handles collision detection between entities"""

    def __init__(self):
        self.entities = []

    def register_entities(self, entities):
        """Register entities for collision detection"""
        self.entities = entities

    def update(self):
        """Update collision detection for all entities"""
        # Find the hero (player character)
        hero = None
        enemies = []

        for entity in self.entities:
            if entity.__class__.__name__ == "Hero":
                hero = entity
            elif hasattr(entity, "take_damage") and entity != hero:
                enemies.append(entity)

        if hero and hero.is_attacking:
            # Check for attack collisions
            hero.attack(enemies)