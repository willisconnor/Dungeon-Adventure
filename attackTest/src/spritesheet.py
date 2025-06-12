import pygame

class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, row, col, sprite_size, scale, colour):
        # sprite_size refers to one 128x128 sprite
        x = (frame * sprite_size) + (col * sprite_size)
        y = row * sprite_size

        # Create surface for the sub image using per pixel alpha
        image = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)

        # Blit the specific part of the spritesheet onto the new surface
        image.blit(self.sheet, (0, 0), (x, y, sprite_size, sprite_size))

        # Scale the image
        image = pygame.transform.scale(image, (sprite_size * scale, sprite_size * scale))

        return image