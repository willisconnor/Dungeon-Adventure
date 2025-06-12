import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print('Updating demon boss animations to use Demon sprites pack...')

updates = [
    ("IDLE",      "assets/sprites/enemies/boss_demon_slime_FREE_v1.0/Demon sprites/Demon_Idle.png",   6, 0.12, 294, 160),
    ("WALKING",   "assets/sprites/enemies/boss_demon_slime_FREE_v1.0/Demon sprites/Demon_Walk.png",  12, 0.10, 294, 160),
    ("ATTACKING_1", "assets/sprites/enemies/boss_demon_slime_FREE_v1.0/Demon sprites/Demon_Attack.png", 15, 0.08, 294, 160),
    ("ATTACKING_2", "assets/sprites/enemies/boss_demon_slime_FREE_v1.0/Demon sprites/Demon_Attack.png", 15, 0.08, 294, 160),
    ("ATTACKING_3", "assets/sprites/enemies/boss_demon_slime_FREE_v1.0/Demon sprites/Demon_Attack.png", 15, 0.08, 294, 160),
    ("HURT",      "assets/sprites/enemies/boss_demon_slime_FREE_v1.0/Demon sprites/Demon_Idle.png",   1, 0.15, 294, 160),
    ("DEAD",      "assets/sprites/enemies/boss_demon_slime_FREE_v1.0/Demon sprites/Demon_Idle.png",   1, 0.20, 294, 160),
]

for state, path, frames, rate, w, h in updates:
    c.execute('''
        INSERT OR REPLACE INTO monster_animations
        (monster_type, animation_state, sprite_path, frame_count, frame_rate, frame_width, frame_height)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ("demon_boss", state, path, frames, rate, w, h))
    print(f"✓ {state}: {path} ({frames} frames, {w}x{h})")

conn.commit()
conn.close()
print('Demon boss animations updated to Demon sprites pack!') 