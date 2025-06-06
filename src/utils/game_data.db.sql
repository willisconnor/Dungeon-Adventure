BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "enemy_animations" (
	"id"	INTEGER,
	"enemy_type"	TEXT,
	"animation_state"	INTEGER,
	"frame_count"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("enemy_type") REFERENCES "enemy_stats"
);
CREATE TABLE IF NOT EXISTS "enemy_sprites" (
	"id"	INTEGER,
	"enemy_type"	TEXT,
	"animation_state"	INTEGER,
	"sprite_path"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("enemy_type") REFERENCES "enemy_stats"
);
CREATE TABLE IF NOT EXISTS "enemy_stats" (
	"enemy_type"	TEXT,
	"max_health"	INTEGER,
	"speed"	REAL,
	"damage"	INTEGER,
	"attack_range"	INTEGER,
	PRIMARY KEY("enemy_type")
);
CREATE TABLE IF NOT EXISTS "hero_animations" (
	"id"	INTEGER,
	"hero_type"	TEXT,
	"animation_state"	INTEGER,
	"frame_count"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("hero_type") REFERENCES "hero_stats"
);
CREATE TABLE IF NOT EXISTS "hero_sprites" (
	"id"	INTEGER,
	"hero_type"	TEXT,
	"animation_state"	INTEGER,
	"sprite_path"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("hero_type") REFERENCES "hero_stats"
);
CREATE TABLE IF NOT EXISTS "hero_stats" (
	"hero_type"	TEXT,
	"max_health"	INTEGER,
	"speed"	REAL,
	"damage"	INTEGER,
	"attack_range"	INTEGER,
	"special_cooldown"	INTEGER
);
COMMIT;
