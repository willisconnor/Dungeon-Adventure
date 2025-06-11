# Custom sprite group for handling camera offsets
class CameraGroup(pygame.sprite.Group):
    """Custom sprite group that handles camera offset when drawing"""

    def __init__(self, camera_x=0, camera_y=0):
        super().__init__()
        self.camera_x = camera_x
        self.camera_y = camera_y
        self.screen_width = 0
        self.screen_height = 0

    def set_camera(self, x, y):
        """Update camera position"""
        self.camera_x = x
        self.camera_y = y

    def draw(self, surface):
        """Draw all sprites with camera offset"""
        for sprite in self.sprites():
            # Calculate screen position
            screen_x = sprite.rect.x - self.camera_x
            screen_y = sprite.rect.y - self.camera_y

            # Only draw if visible on screen
            if (-sprite.rect.width < screen_x < surface.get_width() and
                    -sprite.rect.height < screen_y < surface.get_height()):
                surface.blit(sprite.image, (screen_x, screen_y))