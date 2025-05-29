import pygame, csv, os
#import this into main game loop
#cw

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.parse_sprite(image)
        #manual laod in: self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

class Tilemap():
    def __init__(self, filename, spritesheet):
        self.tile_size = 16
        self.start_x, self.start_y = 0, 0
        self.spritesheet = spritesheet
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey((0, 0, 0))
        self.load_tiles()

    def draw_map(self, surface):
        surface.blit(self.map_surface, (0, 0))

    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surface)

    def read_csv(self, filename):
        map = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                map.append(list(row))
        return map

    def load_tiles(self, filename):
        tiles = []
        map = self.read_csv(filename)
        x, y = 0, 0
        for row in map:
            x = 0
            for tile in row:
                if tile == '0':
                    self.start_x, self.start_y = x * self.tile_size, y *self.tile_size
                elif tile == '1':
                    tiles.append(Tile('ground.png', x * self.tile_size, y * self.tile_size, self.spritesheet))
                elif tile == '2':
                    tiles.append(Tile('ground2.png', x * self.tile_size, y * self.tile_size, self.spritesheet))
                    #move to next tile in current row
                x+= 1
                #move
            y +=1
            #store the size of the tile map
        self.map_w, self.map_h = x*self.tile_size, y*self.tile_size
        return tiles

