import pygame

class SpriteSheet:
    """Utility class for loading and extracting frames from sprite sheets"""
    
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, row, col, sprite_size, scale, colour):
        """
        Extract a specific frame from the sprite sheet
        
        Args:
            frame: Frame index (0-based)
            row: Row index (0-based)
            col: Column index (0-based)
            sprite_size: Size of each sprite (assumes square sprites)
            scale: Scale factor for the output image
            colour: Color key for transparency (usually (0, 0, 0) for black)
        
        Returns:
            pygame.Surface: The extracted and scaled frame
        """
        # Calculate position in sprite sheet
        x = (frame * sprite_size) + (col * sprite_size)
        y = row * sprite_size

        # Create surface for the sub image using per pixel alpha
        image = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)

        # Blit the specific part of the spritesheet onto the new surface
        image.blit(self.sheet, (0, 0), (x, y, sprite_size, sprite_size))

        # Scale the image
        scaled_size = int(sprite_size * scale)
        image = pygame.transform.scale(image, (scaled_size, scaled_size))

        return image

    def get_frame(self, frame_index, frame_width, frame_height, scale=1.0):
        """
        Extract a frame from a horizontal sprite sheet
        
        Args:
            frame_index: Index of the frame to extract (0-based)
            frame_width: Width of each frame
            frame_height: Height of each frame
            scale: Scale factor for the output image
        
        Returns:
            pygame.Surface: The extracted and scaled frame
        """
        # Calculate position in sprite sheet
        x = frame_index * frame_width
        y = 0

        # Create surface for the sub image
        image = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)

        # Blit the specific part of the spritesheet onto the new surface
        image.blit(self.sheet, (0, 0), (x, y, frame_width, frame_height))

        # Scale the image if needed
        if scale != 1.0:
            scaled_width = int(frame_width * scale)
            scaled_height = int(frame_height * scale)
            image = pygame.transform.scale(image, (scaled_width, scaled_height))

        return image 