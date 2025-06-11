import pygame
import os
import pickle
import hashlib
import time
from typing import Dict, Optional, List, Tuple, Any
from enum import Enum


class PauseMenuState(Enum):
    MAIN = 0
    SAVE = 1
    LOAD = 2


class SaveGameMenu:
    def __init__(self, screen, game_instance):
        """Initialize the save game menu

        Args:
            screen: Pygame screen surface
            game_instance: Reference to the Game object
        """
        self.screen = screen
        self.game = game_instance
        self.selected_index = 0
        self.buttons: List[Tuple[pygame.Rect, str]] = []
        self.state = PauseMenuState.MAIN

        # Input handling
        self.input_text = ""
        self.input_active = False

        # Colors
        self.bg_color = (0, 0, 0, 180)  # Semi-transparent background
        self.text_color = (200, 200, 200)
        self.selected_color = (255, 255, 0)
        self.button_color = (60, 60, 60)
        self.input_box_color = (40, 40, 40)

        # Fonts
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)

        # Save directory
        self.__save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'saves')
        os.makedirs(self.__save_dir, exist_ok=True)

        # Status message
        self.status_message = ""
        self.status_color = (255, 255, 255)
        self.status_timer = 0

        # Save files list
        self.save_files = []
        self.save_scroll_offset = 0


    def draw_pause_overlay(self):
        """Draw the pause menu overlay"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)  # 50% transparency
        overlay.fill((0, 0, 0))  # Black background
        self.screen.blit(overlay, (0, 0))

        # Clear buttons
        self.buttons = []

        # Render based on current state
        if self.state == PauseMenuState.MAIN:
            self._render_pause_menu()
        elif self.state == PauseMenuState.SAVE:
            self._render_save_menu()
        elif self.state == PauseMenuState.LOAD:
            self._render_load_menu()

        # Display status message if there is one
        if self.status_message and self.status_timer > 0:
            status_text = self.font.render(self.status_message, True, self.status_color)
            status_rect = status_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 100))
            self.screen.blit(status_text, status_rect)
            self.status_timer -= 1

    def handle_event(self, event) -> Optional[str]:
        """Handle pygame events for the menu

        Args:
            event: Pygame event

        Returns:
            Action string if an action should be taken, None otherwise
        """
        # Handle keyboard events
        if event.type == pygame.KEYDOWN:
            # Input handling for save menu
            if self.state == PauseMenuState.SAVE and self.input_active:
                if event.key == pygame.K_RETURN:
                    self.save_game_with_name(self.input_text)
                    self.input_text = ""
                    self.state = PauseMenuState.MAIN
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    return None
                elif event.key == pygame.K_ESCAPE:
                    self.input_text = ""
                    self.state = PauseMenuState.MAIN
                    return None
                else:
                    # Add character to input (limit to reasonable length)
                    if len(self.input_text) < 20:
                        self.input_text += event.unicode
                    return None

            # Navigation keys
            if event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
                return None
            elif event.key == pygame.K_DOWN:
                if self.state == PauseMenuState.MAIN:
                    self.selected_index = min(3, self.selected_index + 1)
                elif self.state == PauseMenuState.LOAD:
                    self.selected_index = min(len(self.save_files) - 1, self.selected_index + 1)
                return None
            elif event.key == pygame.K_RETURN:
                # Handle selection based on menu state
                if self.state == PauseMenuState.MAIN:
                    if self.selected_index == 0:
                        return "resume"
                    elif self.selected_index == 1:
                        self.state = PauseMenuState.SAVE
                        self.input_text = ""
                        self.input_active = True
                        self.selected_index = 0
                    elif self.selected_index == 2:
                        self.state = PauseMenuState.LOAD
                        self.refresh_save_files()
                        self.selected_index = 0
                    elif self.selected_index == 3:
                        return "main_menu"
                elif self.state == PauseMenuState.LOAD and self.save_files:
                    # Load selected save file
                    if 0 <= self.selected_index < len(self.save_files):
                        save_name = self.save_files[self.selected_index].split('.')[0]
                        self.load_game(save_name)
                        self.state = PauseMenuState.MAIN
                        return "resume"
            elif event.key == pygame.K_ESCAPE:
                if self.state == PauseMenuState.MAIN:
                    return "resume"
                else:
                    self.state = PauseMenuState.MAIN
                    self.selected_index = 0
            elif event.key == pygame.K_F5:
                self.quick_save()
                return None
            elif event.key == pygame.K_F9:
                self.quick_load()
                return None

        # Mouse handling
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check button clicks
            for button_rect, action in self.buttons:
                if button_rect.collidepoint(event.pos):
                    if action == "resume":
                        return "resume"
                    elif action == "save_menu":
                        self.state = PauseMenuState.SAVE
                        self.input_text = ""
                        self.input_active = True
                        self.selected_index = 0
                    elif action == "load_menu":
                        self.state = PauseMenuState.LOAD
                        self.refresh_save_files()
                        self.selected_index = 0
                    elif action == "main_menu":
                        return "main_menu"
                    elif action == "back":
                        self.state = PauseMenuState.MAIN
                        self.selected_index = 0
                    elif action == "confirm_save":
                        self.save_game_with_name(self.input_text)
                        self.input_text = ""
                        self.state = PauseMenuState.MAIN
                    elif action == "quick_save":
                        self.quick_save()
                    elif action == "quick_load":
                        self.quick_load()
                    elif action.startswith("load_"):
                        # Extract save name from action
                        save_index = int(action.split('_')[1])
                        if 0 <= save_index < len(self.save_files):
                            save_name = self.save_files[save_index].split('.')[0]
                            self.load_game(save_name)
                            self.state = PauseMenuState.MAIN
                            return "resume"
                    return None

            # Check for input box click in save menu
            if self.state == PauseMenuState.SAVE:
                input_box = pygame.Rect(self.screen.get_width() // 2 - 200, 200, 400, 50)
                if input_box.collidepoint(event.pos):
                    self.input_active = True
                else:
                    self.input_active = False

        return None

    def _render_pause_menu(self):
        """Render the pause menu options"""
        # Title
        title_text = self.font.render("GAME PAUSED", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_text, title_rect)

        # Define pause menu options
        options = [
            "Resume Game",
            "Save Game",
            "Load Game",
            "Return to Main Menu"
        ]

        # Draw each option
        for i, option in enumerate(options):
            color = self.selected_color if i == self.selected_index else self.text_color
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(self.screen.get_width() // 2, 150 + i * 60))
            self.screen.blit(text, rect)

            # Add button rect for mouse interaction
            button_rect = pygame.Rect(rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10)

            # Map index to action
            if i == 0:
                action = "resume"
            elif i == 1:
                action = "save_menu"
            elif i == 2:
                action = "load_menu"
            elif i == 3:
                action = "main_menu"

            self.buttons.append((button_rect, action))

            # Draw button highlight
            pygame.draw.rect(self.screen, color, button_rect, 2)

        # Add quick save/load buttons
        quick_save_btn = pygame.Rect(50, self.screen.get_height() - 120, 140, 40)
        pygame.draw.rect(self.screen, self.button_color, quick_save_btn)
        quick_save_text = self.small_font.render("Quick Save (F5)", True, self.text_color)
        quick_save_rect = quick_save_text.get_rect(center=quick_save_btn.center)
        self.screen.blit(quick_save_text, quick_save_rect)
        self.buttons.append((quick_save_btn, "quick_save"))

        quick_load_btn = pygame.Rect(50, self.screen.get_height() - 70, 140, 40)
        pygame.draw.rect(self.screen, self.button_color, quick_load_btn)
        quick_load_text = self.small_font.render("Quick Load (F9)", True, self.text_color)
        quick_load_rect = quick_load_text.get_rect(center=quick_load_btn.center)
        self.screen.blit(quick_load_text, quick_load_rect)
        self.buttons.append((quick_load_btn, "quick_load"))

    def _render_save_menu(self):
        """Render the save game interface"""
        # Title
        title_text = self.font.render("SAVE GAME", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_text, title_rect)

        # Draw prompt
        prompt = self.font.render("Enter save name:", True, self.text_color)
        prompt_rect = prompt.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(prompt, prompt_rect)

        # Draw input box
        input_box = pygame.Rect(self.screen.get_width() // 2 - 200, 200, 400, 50)
        pygame.draw.rect(self.screen, self.input_box_color, input_box)
        pygame.draw.rect(self.screen, self.text_color if not self.input_active else self.selected_color, input_box, 2)

        # Draw input text
        input_surf = self.font.render(self.input_text + ("|" if self.input_active and time.time() % 1 > 0.5 else ""),
                                      True, self.text_color)
        input_rect = input_surf.get_rect(midleft=(input_box.left + 10, input_box.centery))
        self.screen.blit(input_surf, input_rect)

        # Draw save button
        save_button = pygame.Rect(self.screen.get_width() // 2 - 100, 300, 200, 50)
        pygame.draw.rect(self.screen, self.button_color, save_button)
        save_text = self.font.render("Save", True, self.text_color)
        save_text_rect = save_text.get_rect(center=save_button.center)
        self.screen.blit(save_text, save_text_rect)
        self.buttons.append((save_button, "confirm_save"))

        # Draw back button
        back_button = pygame.Rect(self.screen.get_width() // 2 - 100, 370, 200, 50)
        pygame.draw.rect(self.screen, self.button_color, back_button)
        back_text = self.font.render("Back", True, self.text_color)
        back_text_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_text_rect)
        self.buttons.append((back_button, "back"))

    def _render_load_menu(self):
        """Render the load game interface"""
        # Title
        title_text = self.font.render("LOAD GAME", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_text, title_rect)

        # Draw save files list
        if not self.save_files:
            no_saves_text = self.font.render("No save files found", True, self.text_color)
            no_saves_rect = no_saves_text.get_rect(center=(self.screen.get_width() // 2, 250))
            self.screen.blit(no_saves_text, no_saves_rect)
        else:
            # Show list of save files
            list_y = 150
            for i, save_file in enumerate(self.save_files):
                # Skip files based on scroll offset
                if i < self.save_scroll_offset:
                    continue

                # Stop if we've displayed enough files
                if list_y > self.screen.get_height() - 100:
                    break

                # Get save name without extension
                save_name = save_file.split('.')[0]

                # Get timestamp if available
                timestamp = self._get_save_timestamp(save_name)
                if timestamp:
                    save_name = f"{save_name} ({timestamp})"

                # Draw save entry
                color = self.selected_color if i == self.selected_index else self.text_color
                text = self.font.render(save_name, True, color)
                rect = text.get_rect(center=(self.screen.get_width() // 2, list_y))
                self.screen.blit(text, rect)

                # Add button
                button_rect = pygame.Rect(rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10)
                pygame.draw.rect(self.screen, color, button_rect, 2)
                self.buttons.append((button_rect, f"load_{i}"))

                list_y += 50

        # Draw back button
        back_button = pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() - 70, 200, 50)
        pygame.draw.rect(self.screen, self.button_color, back_button)
        back_text = self.font.render("Back", True, self.text_color)
        back_text_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_text_rect)
        self.buttons.append((back_button, "back"))

    def refresh_save_files(self):
        """Refresh the list of save files"""
        try:
            # Get all .save files
            self.save_files = [f for f in os.listdir(self.__save_dir) if f.endswith('.save')]
            # Sort by modification time (newest first)
            self.save_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.__save_dir, x)), reverse=True)
        except Exception as e:
            print(f"Error refreshing save files: {e}")
            self.save_files = []

    def _get_save_timestamp(self, save_name):
        """Get a formatted timestamp for a save file"""
        try:
            save_path = os.path.join(self.__save_dir, f"{save_name}.save")
            if os.path.exists(save_path):
                mod_time = os.path.getmtime(save_path)
                return time.strftime("%Y-%m-%d %H:%M", time.localtime(mod_time))
        except Exception:
            pass
        return None

    def show_status(self, message, color=(255, 255, 255), duration=180):
        """Show a status message for a duration

        Args:
            message: Status message to show
            color: RGB color tuple
            duration: Duration in frames
        """
        self.status_message = message
        self.status_color = color
        self.status_timer = duration

    def __sanitize_filename(self, filename):
        """Sanitize a filename to be safe for file system

        Args:
            filename: Input filename

        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        import re
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)
        filename = filename.strip()

        # Use default if empty
        if not filename:
            filename = f"save_{int(time.time())}"

        return filename

    def save_game_with_name(self, save_name):
        """Save game with the given name"""
        # Get game state from game instance
        game_state = self.game.get_serializable_state()
        if not game_state:
            self.show_status("Error: Could not get game state", (255, 0, 0))
            return False

        return self.save_game(game_state, save_name)

    def save_game(self, game_state: Dict, save_name: str) -> bool:
        """
        Save game state to file

        Args:
            game_state: Game state dictionary
            save_name: Name for the save file

        Returns:
            True if save successful
        """
        try:
            # Sanitize filename
            safe_name = self.__sanitize_filename(save_name)
            if not safe_name:
                return False

            # Add metadata
            game_state['__meta'] = {
                'timestamp': time.time(),
                'version': '1.0'
            }

            # Generate checksum for integrity verification
            state_bytes = pickle.dumps(game_state)
            checksum = hashlib.sha256(state_bytes).hexdigest()

            # Save file with checksum
            with open(os.path.join(self.__save_dir, f"{safe_name}.save"), 'wb') as f:
                pickle.dump({'checksum': checksum, 'data': game_state}, f)

            # Show success status
            self.show_status("Game saved successfully!", (0, 255, 0))
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            self.show_status("Failed to save game!", (255, 0, 0))
            return False

    def load_game(self, save_name: str) -> bool:
        """
        Load game state from file

        Args:
            save_name: Name of save file to load

        Returns:
            True if load successful
        """
        try:
            # Sanitize filename
            safe_name = self.__sanitize_filename(save_name)
            if not safe_name:
                return False

            save_path = os.path.join(self.__save_dir, f"{safe_name}.save")
            if not os.path.exists(save_path):
                self.show_status(f"Save file not found!", (255, 0, 0))
                return False

            # Load save file
            with open(save_path, 'rb') as f:
                save_data = pickle.load(f)

            # Verify checksum
            checksum = save_data['checksum']
            game_state = save_data['data']

            calculated_checksum = hashlib.sha256(pickle.dumps(game_state)).hexdigest()
            if checksum != calculated_checksum:
                self.show_status("Warning: Save file may be corrupted", (255, 255, 0))

            # Load state into game
            if self.game.load_from_state(game_state):
                self.show_status("Game loaded successfully!", (0, 255, 0))
                return True
            else:
                self.show_status("Error loading game state", (255, 0, 0))
                return False
        except Exception as e:
            print(f"Error loading game: {e}")
            self.show_status("Failed to load game!", (255, 0, 0))
            return False

    def quick_save(self):
        """Perform a quick save"""
        game_state = self.game.get_serializable_state()
        if not game_state:
            self.show_status("Error: Could not get game state", (255, 0, 0))
            return False

        return self.save_game(game_state, "quicksave")

    def quick_load(self):
        """Load the quick save file"""
        return self.load_game("quicksave")