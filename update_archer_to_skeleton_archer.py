import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print('Updating archer animations to use Skeleton_Archer pack...')

# Map archer animation states to Skeleton_Archer files
updates = [
    ("IDLE",      "assets/sprites/enemies/Skeleton_Archer/Idle.png",      10, 0.12, 64, 128),
    ("WALKING",   "assets/sprites/enemies/Skeleton_Archer/Walk.png",      16, 0.10, 64, 128),
    ("ATTACKING_1", "assets/sprites/enemies/Skeleton_Archer/Attack_1.png", 10, 0.08, 64, 128),
    ("ATTACKING_2", "assets/sprites/enemies/Skeleton_Archer/Attack_2.png", 8, 0.08, 64, 128),
    ("ATTACKING_3", "assets/sprites/enemies/Skeleton_Archer/Attack_3.png", 6, 0.08, 64, 128),
    ("SPECIAL_SKILL", "assets/sprites/enemies/Skeleton_Archer/Shot_1.png", 30, 0.05, 64, 128),
    ("DEFENDING",  "assets/sprites/enemies/Skeleton_Archer/Evasion.png",   8, 0.10, 64, 128),
    ("HURT",      "assets/sprites/enemies/Skeleton_Archer/Hurt.png",      4, 0.15, 64, 128),
    ("DEAD",      "assets/sprites/enemies/Skeleton_Archer/Dead.png",      6, 0.20, 64, 128),
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
print('Archer animations updated to Skeleton_Archer pack!') 