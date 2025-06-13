import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print('Updating knight attack animations to use attackTest sprites...')

updates = [
    ("ATTACKING_1", "assets/sprites/heroes/knight/Knight_1/Attack1.png", 5, 0.08, 128, 128),
    ("ATTACKING_2", "assets/sprites/heroes/knight/Knight_1/Attack2.png", 4, 0.08, 128, 128),
    ("ATTACKING_3", "assets/sprites/heroes/knight/Knight_1/Attack3.png", 4, 0.08, 128, 128),
]

for state, path, frames, rate, w, h in updates:
    c.execute('''
        UPDATE hero_animations
        SET sprite_path=?, frame_count=?, frame_rate=?, frame_width=?, frame_height=?
        WHERE hero_type="knight" AND animation_state=?
    ''', (path, frames, rate, w, h, state))
    print(f"✓ {state}: {path} ({frames} frames, {w}x{h})")

conn.commit()
conn.close()
print('Knight attack animations updated!') 