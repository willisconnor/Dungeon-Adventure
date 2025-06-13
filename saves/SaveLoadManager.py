"""
Enhanced SaveLoadSystem with proper game state serialization
"""
import hashlib
import pickle
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, Optional
import pygame


@dataclass
class GameSaveData:
    """Data class to hold all saveable game state"""
    # Hero data
    selected_hero_type: str
    hero_data: Dict[str, Any]

    # Dungeon state
    dungeon_template: str
    current_room_position: tuple
    visited_rooms: set

    # Game progress
    collected_pillars: Dict[str, bool]
    enemies_defeated: Dict[str, int]

    # Camera and positioning
    camera_x: float
    camera_y: float

    # Metadata
    save_timestamp: str
    play_time: float
    game_version: str = "1.0"

import os
import pickle
import hashlib

class SaveLoadSystem:
    def __init__(self, save_dir="saves", save_filename="autosave"):
        self.save_dir = save_dir
        self.save_filename = save_filename
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def save_game(self, game_state: dict, filename: str = None) -> bool:
        try:
            if filename is None:
                filename = self.save_filename
            filepath = os.path.join(self.save_dir, f"{filename}.save")

            game_state['__meta'] = {
                'version': '1.0'
            }

            data_bytes = pickle.dumps(game_state)
            checksum = hashlib.sha256(data_bytes).hexdigest()

            with open(filepath, 'wb') as f:
                pickle.dump({'checksum': checksum, 'data': game_state}, f)

            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, filename: str = None) -> dict or None:
        try:
            if filename is None:
                filename = self.save_filename
            filepath = os.path.join(self.save_dir, f"{filename}.save")

            if not os.path.exists(filepath):
                print("Save file does not exist.")
                return None

            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)

            stored_checksum = save_data.get('checksum')
            game_state = save_data.get('data')

            if stored_checksum != hashlib.sha256(pickle.dumps(game_state)).hexdigest():
                print("Checksum mismatch — corrupted save file.")
                return None

            return game_state
        except Exception as e:
            print(f"Error loading game: {e}")
            return None