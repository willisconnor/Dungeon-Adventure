import sqlite3
import pygame
import os

def check_sprite_frames(sprite_path):
    """Check how many frames are actually in a sprite sheet"""
    if not os.path.exists(sprite_path):
        return 0
    
    try:
        sheet = pygame.image.load(sprite_path).convert_alpha()
        width = sheet.get_width()
        height = sheet.get_height()
        
        # For horizontal sprite sheets, divide width by frame width
        # Let's try different frame widths to find the correct one
        possible_frame_widths = [64, 128, 256, 512]
        
        for frame_width in possible_frame_widths:
            if width % frame_width == 0:
                frame_count = width // frame_width
                print(f"  {sprite_path}: {width}x{height} -> {frame_count} frames of {frame_width}x{height}")
                return frame_count
        
        print(f"  {sprite_path}: Could not determine frame count for {width}x{height}")
        return 0
        
    except Exception as e:
        print(f"  Error loading {sprite_path}: {e}")
        return 0

# Initialize pygame with a display for image loading
pygame.init()
screen = pygame.display.set_mode((1, 1))  # Minimal display
pygame.display.set_caption("Frame Checker")

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print("Checking archer sprite sheets for actual frame counts:")

# Get all archer animations
c.execute('SELECT animation_state, sprite_path, frame_count FROM hero_animations WHERE hero_type = "archer"')
archer_animations = c.fetchall()

print("\nArcher animations with actual frame counts:")
for animation_state, sprite_path, current_frame_count in archer_animations:
    actual_frames = check_sprite_frames(sprite_path)
    print(f"  {animation_state}: Database says {current_frame_count}, Actual: {actual_frames}")
    
    # Update database if frame count is wrong
    if actual_frames > 0 and actual_frames != current_frame_count:
        c.execute('''
            UPDATE hero_animations 
            SET frame_count = ? 
            WHERE hero_type = "archer" AND animation_state = ?
        ''', (actual_frames, animation_state))
        print(f"    -> Updated to {actual_frames} frames")

conn.commit()
conn.close()

pygame.quit()
print("\nArcher frame counts updated!") 