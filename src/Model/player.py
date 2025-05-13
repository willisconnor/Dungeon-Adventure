import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill((0, 255, 0))  # Green rectangle as placeholder
        self.rect = self.image.get_rect(topleft=(x, y))

        # Movement attributes
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 5
        self.jump_power = -12
        self.gravity = 0.5
        self.on_ground = False

    def update(self, room):
        """Handle movement and collisions"""
        keys = pygame.key.get_pressed()

        # Horizontal movement
        self.velocity.x = 0
        if keys[pygame.K_a]:
            self.velocity.x = -self.speed
        if keys[pygame.K_d]:
            self.velocity.x = self.speed

        # Apply gravity
        self.velocity.y += self.gravity

        # Check horizontal collisions
        self.rect.x += self.velocity.x
        if room.check_collision(self.rect):
            self.rect.x -= self.velocity.x

        # Check vertical collisions
        self.rect.y += self.velocity.y
        platform_top = room.check_platform(self.rect, self.velocity.y)

        if platform_top is not None:
            self.rect.bottom = platform_top
            self.velocity.y = 0
            self.on_ground = True
        elif room.check_collision(self.rect):
            self.rect.y -= self.velocity.y
            self.velocity.y = 0
            self.on_ground = self.velocity.y > 0
        else:
            self.on_ground = False

    def jump(self):
        if self.on_ground:
            self.velocity.y = self.jump_power
            self.on_ground = False

    def draw(self, surface, offset):
        """Draw player relative to camera"""
        surface.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))