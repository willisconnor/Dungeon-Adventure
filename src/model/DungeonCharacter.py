from DungeonEntity import DungeonEntity, AnimationState, Direction

class DungeonCharacter(DungeonEntity):
    """Base character class for both hero and enemy, inherits from DungeonEntity"""
    def __init__(self, x, y,width, height, name, max_health, health, speed, damage, animation_state):
        super().__init__(x, y, max_health)
        self.speed = speed
        self.damage = damage
        self.width = width
        self.height = height
        self.name = name
        self.health = health #Do I need to pass in current health?
        self.max_health = max_health
        self.animation_state = animation_state.IDLE
        self.last_animation_state = animation_state.IDLE
        self.last_direction = Direction.LEFT
        self.animation_counter = 0
        self.speed = 0


        #Animation properties
        #setting frame rates for each aniimation state, should
        #be determined in lower classes


        #Combat properties
        self.is_attacking = False
        self.attack_combo = 0
        self.attack_complete = True
        self.attack_window = 0
        self.hit_targets = set() #track whats been hit this attack

    def update(self, dt):
        """Update entity state """
        self._update_hitbox()
        self._update_invulnerability(dt)
        self.update_animation(dt)
        self.update_attack_state(dt)

    def take_damage(self, amount):
        """handles taking damage"""
        if not self.is_alive or self.is_invulnerable:
            return False

        self.health -= amount

        #set PLAYER invulnerability, might rethink placement
        #actually, might just pass this to the hero?


    def _update_animation(self, dt):
        """Update animation frame index"""
        #get current frame rate for this animation state
        current_frame_rate = self.frame_rates.get(self.animation_state, 6)

        #increment counter
        self.animation_counter += dt *60 #convert to roughly 60 fps

        #update frame when counter exceeds frame rate
        if self.animation_counter >= current_frame_rate:
            self.anmimation_counter = 0


