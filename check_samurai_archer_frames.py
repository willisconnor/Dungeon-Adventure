import pygame
import os

pygame.init()

folder = 'assets/sprites/heroes/archer/Samurai_Archer'
files = [f for f in os.listdir(folder) if f.endswith('.png')]

for file in files:
    path = os.path.join(folder, file)
    img = pygame.image.load(path)
    width, height = img.get_size()
    # Guess frame width (commonly 64 or 128)
    for fw in [64, 128]:
        if width % fw == 0:
            frames = width // fw
            print(f'{file}: {frames} frames, each {fw}x{height}')
            break
    else:
        print(f'{file}: Could not determine frame size (image size: {width}x{height})')

pygame.quit() 