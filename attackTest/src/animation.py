import pygame
from entity import AnimationState, Direction
from spritesheet import SpriteSheet


class Animation:
    """Handles loading and managing animation frames"""

    def __init__(self):
        # Animation frames for each entity type, state, and direction
        self.frames = {
            'hero': {
                Direction.RIGHT: {},
                Direction.LEFT: {}
            },
            'skeleton': {
                Direction.RIGHT: {},
                Direction.LEFT: {}
            }
        }

    def load_hero_animations(self):
        """Load all hero animation frames"""
        # Load spritesheet images
        walk_sheet = pygame.image.load('walk.png').convert_alpha()
        warrior_idle_sheet = pygame.image.load('idle.png').convert_alpha()
        defend_sheet = pygame.image.load('defend.png').convert_alpha()
        attack1_sheet = pygame.image.load('attack 1.png').convert_alpha()
        attack2_sheet = pygame.image.load('attack 2.png').convert_alpha()
        attack3_sheet = pygame.image.load('attack 3.png').convert_alpha()

        # Create spritesheet objects
        walk_spritesheet = SpriteSheet(walk_sheet)
        warrior_idle_spritesheet = SpriteSheet(warrior_idle_sheet)
        defend_spritesheet = SpriteSheet(defend_sheet)
        attack1_spritesheet = SpriteSheet(attack1_sheet)
        attack2_spritesheet = SpriteSheet(attack2_sheet)
        attack3_spritesheet = SpriteSheet(attack3_sheet)

        # Load right-facing frames
        BLACK = (0, 0, 0)  # Transparency color key

        # Idle animation
        idle_frames = [
            warrior_idle_spritesheet.get_image(0, 0, i, 128, 1, BLACK)
            for i in range(4)
        ]
        self.frames['hero'][Direction.RIGHT][AnimationState.IDLE] = idle_frames

        # Walking animation
        walk_frames = [
            walk_spritesheet.get_image(0, 0, i, 128, 1, BLACK)
            for i in range(7)
        ]
        self.frames['hero'][Direction.RIGHT][AnimationState.WALKING] = walk_frames

        # Defending animation
        defend_frames = [
            defend_spritesheet.get_image(0, 0, i, 128, 1, BLACK)
            for i in range(5)
        ]
        self.frames['hero'][Direction.RIGHT][AnimationState.DEFENDING] = defend_frames

        # Attack animations
        attack1_frames = [
            attack1_spritesheet.get_image(0, 0, i, 128, 1, BLACK)
            for i in range(5)
        ]
        self.frames['hero'][Direction.RIGHT][AnimationState.ATTACKING_1] = attack1_frames

        attack2_frames = [
            attack2_spritesheet.get_image(0, 0, i, 128, 1, BLACK)
            for i in range(4)
        ]
        self.frames['hero'][Direction.RIGHT][AnimationState.ATTACKING_2] = attack2_frames

        attack3_frames = [
            attack3_spritesheet.get_image(0, 0, i, 128, 1, BLACK)
            for i in range(4)
        ]
        self.frames['hero'][Direction.RIGHT][AnimationState.ATTACKING_3] = attack3_frames

        # Generate left-facing frames by flipping right-facing frames
        for state in self.frames['hero'][Direction.RIGHT]:
            self.frames['hero'][Direction.LEFT][state] = [
                pygame.transform.flip(frame, True, False)
                for frame in self.frames['hero'][Direction.RIGHT][state]
            ]

    def load_skeleton_animations(self):
        """Load all skeleton animation frames"""
        # Load spritesheet images - assuming you have sprite sheets for the skeleton
        # You would need to provide the appropriate sprite sheet files
        skeleton_idle_sheet = pygame.image.load('./Skeleton_Warrior/Idle.png').convert_alpha()
        skeleton_hurt_sheet = pygame.image.load('./Skeleton_Warrior/Hurt.png').convert_alpha()
        skeleton_death_sheet = pygame.image.load('./Skeleton_Warrior/Dead.png').convert_alpha()

        # Create spritesheet objects
        skeleton_idle_spritesheet = SpriteSheet(skeleton_idle_sheet)
        hurt_spritesheet = SpriteSheet(skeleton_hurt_sheet)
        death_spritesheet = SpriteSheet(skeleton_death_sheet)

        # Load frames
        BLACK = (0, 0, 0)  # Transparency color key

        # Idle animation
        idle_frames = [
            skeleton_idle_spritesheet.get_image(0, 0, i, 128, 1, BLACK)
            for i in range(4)
        ]
        self.frames['skeleton'][Direction.RIGHT][AnimationState.IDLE] = idle_frames

        # Hurt animation
        hurt_frames = [
            hurt_spritesheet.get_image(0, 0, i, 128, 1, BLACK)
            for i in range(4)
        ]
        self.frames['skeleton'][Direction.RIGHT][AnimationState.HURT] = hurt_frames

        # Dying animation
        dying_frames = [
            death_spritesheet.get_image(0, 0, i, 128, 1, BLACK)
            for i in range(4)
        ]
        self.frames['skeleton'][Direction.RIGHT][AnimationState.DYING] = dying_frames

        # Dead animation (last frame of death animation)
        dead_frame = [death_spritesheet.get_image(0, 0, 3, 128, 1, BLACK)]
        self.frames['skeleton'][Direction.RIGHT][AnimationState.DEAD] = dead_frame

        # Generate left-facing frames by flipping right-facing frames
        for state in self.frames['skeleton'][Direction.RIGHT]:
            self.frames['skeleton'][Direction.LEFT][state] = [
                pygame.transform.flip(frame, True, False)
                for frame in self.frames['skeleton'][Direction.RIGHT][state]
            ]

    def get_frame(self, entity_type, state, direction, frame_index):
        """Get a specific animation frame"""
        if entity_type not in self.frames:
            return None

        if direction not in self.frames[entity_type]:
            return None

        if state not in self.frames[entity_type][direction]:
            return None

        frames = self.frames[entity_type][direction][state]
        if not frames or frame_index >= len(frames):
            return None

        return frames[frame_index]