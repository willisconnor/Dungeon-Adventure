import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print('Updating archer animations to use Samurai_Archer pack...')

updates = [
    ("IDLE",      "assets/sprites/heroes/archer/Samurai_Archer/Archer_Stance.png", 1, 0.15, 64, 128),
    ("WALKING",   "assets/sprites/heroes/archer/Samurai_Archer/Walk.png",         16, 0.10, 64, 128),
    ("ATTACKING_1", "assets/sprites/heroes/archer/Samurai_Archer/Attack_1.png",   10, 0.08, 64, 128),
    ("ATTACKING_2", "assets/sprites/heroes/archer/Samurai_Archer/Attack_2.png",   10, 0.08, 64, 128),
    ("SPECIAL_SKILL", "assets/sprites/heroes/archer/Samurai_Archer/Shot.png",     28, 0.05, 64, 128),
    ("DEFENDING",  "assets/sprites/heroes/archer/Samurai_Archer/Archer_Stance.png", 1, 0.15, 64, 128),
    ("HURT",      "assets/sprites/heroes/archer/Samurai_Archer/Archer_Stance.png", 1, 0.15, 64, 128),
    ("DEAD",      "assets/sprites/heroes/archer/Samurai_Archer/Archer_Stance.png", 1, 0.15, 64, 128),
]

for state, path, frames, rate, w, h in updates:
    c.execute('''
        UPDATE hero_animations
        SET sprite_path=?, frame_count=?, frame_rate=?, frame_width=?, frame_height=?
        WHERE hero_type="archer" AND animation_state=?
    ''', (path, frames, rate, w, h, state))
    print(f"✓ {state}: {path} ({frames} frames, {w}x{h})")

conn.commit()
conn.close()
print('Archer animations updated to Samurai_Archer pack!') 