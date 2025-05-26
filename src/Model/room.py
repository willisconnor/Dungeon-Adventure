import random
import pytmx


class Room:
    def __init__(self, tmx_file, background_file):
        # Define screen dimensions
        self.width = 800  # Default screen width
        self.height = 600  # Default screen height
        self.tmx_file = tmx_file

        # Construct proper path to assets
        assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        self.background_path = os.path.join(assets_path, background_file)
        self.platforms_path = os.path.join(assets_path, tmx_file)

        try:
            # Load and scale background
            self.background = pygame.image.load(self.background_path).convert()
            self.background = pygame.transform.scale(self.background, (self.width, self.height))

            # Load TMX file for platforms
            self.tmx_data = pytmx.load_pygame(self.platforms_path)
            self.platforms = self.load_platforms()
        except Exception as e:
            print(f"Error loading assets: {e}")
            self.background = pygame.Surface((self.width, self.height))
            self.background.fill((50, 50, 60))  # Fallback color
            # Create default platforms
            self.platforms = [
                pygame.Rect(0, self.height - 40, self.width, 40),  # Ground
                pygame.Rect(300, 400, 200, 20),  # Platform 1
                pygame.Rect(100, 300, 200, 20),  # Platform 2
                pygame.Rect(500, 200, 200, 20)   # Platform 3
            ]

    def load_platforms(self):
        platforms = []
        try:
            layer = self.tmx_data.get_layer_by_name('platforms')
            for x, y, gid in layer:
                if gid:
                    px = x * self.tmx_data.tilewidth
                    py = y * self.tmx_data.tileheight
                    platforms.append(pygame.Rect(
                        px, py,
                        self.tmx_data.tilewidth,
                        self.tmx_data.tileheight
                    ))
        except Exception as e:
            print(f"Error loading platforms: {e}")
            return self.create_default_platforms()
        return platforms

    def create_default_platforms(self):
        return [
            pygame.Rect(0, self.height - 40, self.width, 40),  # Ground
            pygame.Rect(300, 400, 200, 20),  # Platform 1
            pygame.Rect(100, 300, 200, 20),  # Platform 2
            pygame.Rect(500, 200, 200, 20)   # Platform 3
        ]
