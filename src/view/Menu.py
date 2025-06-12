import pygame
import sys
import os
import time
from typing import Optional, List, Dict, Tuple
import sqlite3

class Button:
    """Encapsulated button class for menu interfaces"""
    
    def __init__(self, 
                 image: Optional[pygame.Surface], 
                 pos: Tuple[int, int], 
                 text_input: str, 
                 font: pygame.font.Font, 
                 base_color: Tuple[int, int, int], 
                 hovering_color: Tuple[int, int, int],
                 action: str):
        """
        Initialize a button with visual styling
        
        Args:
            image: Background image for button (can be None)
            pos: Center position (x, y) for the button
            text_input: Text displayed on button
            font: Font used for text
            base_color: Normal text color
            hovering_color: Text color when mouse hovers
            action: Action identifier string
        """
        self.__image = image
        self.__pos = pos
        self.__text_input = text_input
        self.__font = font
        self.__base_color = base_color
        self.__hovering_color = hovering_color
        self.__action = action
        
        # Render text with base color
        self.__text = self.__font.render(self.__text_input, True, self.__base_color)
        
        # Set up rectangles
        if self.__image is None:
            self.__image = self.__text
            
        self.__rect = self.__image.get_rect(center=self.__pos)
        self.__text_rect = self.__text.get_rect(center=self.__pos)
    
    def update(self, screen: pygame.Surface) -> None:
        """
        Draw the button on the screen
        
        Args:
            screen: Pygame surface to draw on
        """
        if self.__image is not None:
            screen.blit(self.__image, self.__rect)
        screen.blit(self.__text, self.__text_rect)
    
    def check_for_input(self, position: Tuple[int, int]) -> bool:
        """
        Check if position is within button boundaries
        
        Args:
            position: Mouse position (x, y)
            
        Returns:
            True if position is on the button, False otherwise
        """
        return (position[0] in range(self.__rect.left, self.__rect.right) and 
                position[1] in range(self.__rect.top, self.__rect.bottom))
    
    def change_color(self, position: Tuple[int, int]) -> None:
        """
        Change text color based on mouse position
        
        Args:
            position: Mouse position (x, y)
        """
        if self.check_for_input(position):
            self.__text = self.__font.render(self.__text_input, True, self.__hovering_color)
        else:
            self.__text = self.__font.render(self.__text_input, True, self.__base_color)
    
    @property
    def action(self) -> str:
        """Get the button's action identifier"""
        return self.__action


class GameStateManager:
    """Secure game save/load manager"""
    
    def __init__(self, save_directory: str = "saves"):
        """
        Initialize the game manager
        
        Args:
            save_directory: Directory for save files
        """
        self.__save_dir = save_directory
        
        # Create save directory if it doesn't exist
        if not os.path.exists(self.__save_dir):
            os.makedirs(self.__save_dir)
    
    def get_save_files(self) -> List[str]:
        """
        Get list of available save files
        
        Returns:
            List of save file names (without extension)
        """
        try:
            # Security - only get .save files from the saves directory
            saves = [f[:-5] for f in os.listdir(self.__save_dir) 
                    if f.endswith('.save') and os.path.isfile(os.path.join(self.__save_dir, f))]
            return saves
        except Exception:
            return []
    
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
                
            import pickle
            import hashlib
            
            # Add metadata
            game_state['__meta'] = {
                'timestamp': pygame.time.get_ticks(),
                'version': '1.0'
            }
            
            # Generate checksum for integrity verification
            state_bytes = pickle.dumps(game_state)
            checksum = hashlib.sha256(state_bytes).hexdigest()
            
            # Save file with checksum
            with open(os.path.join(self.__save_dir, f"{safe_name}.save"), 'wb') as f:
                pickle.dump({'checksum': checksum, 'data': game_state}, f)
                
            return True
        except Exception:
            return False
    
    def load_game(self, save_name: str) -> Optional[Dict]:
        """
        Load game state from file
        
        Args:
            save_name: Name of save file
            
        Returns:
            Game state dictionary or None if loading failed
        """
        try:
            # Sanitize filename
            safe_name = self.__sanitize_filename(save_name)
            if not safe_name:
                return None
                
            import pickle
            import hashlib
            
            # Load save file
            save_path = os.path.join(self.__save_dir, f"{safe_name}.save")
            if not os.path.exists(save_path):
                return None
                
            with open(save_path, 'rb') as f:
                save_data = pickle.load(f)
                
            # Verify checksum for integrity
            stored_checksum = save_data.get('checksum')
            game_state = save_data.get('data')
            
            if not stored_checksum or not game_state:
                return None
                
            # Verify integrity
            calculated_checksum = hashlib.sha256(pickle.dumps(game_state)).hexdigest()
            if calculated_checksum != stored_checksum:
                return None  # Data integrity issue
                
            return game_state
        except Exception:
            return None
    
    def __sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent security issues
        
        Args:
            filename: Raw filename
            
        Returns:
            Sanitized filename
        """
        # Remove any path components and non-alphanumeric characters
        valid_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_- "
        sanitized = ''.join(c for c in os.path.basename(filename) if c in valid_chars)
        return sanitized[:50]  # Limit length


class LoadMenu:
    """Menu for loading saved games"""
    
    def __init__(self, screen: pygame.Surface, screen_width: int, screen_height: int, save_files: List[str]):
        """
        Initialize the load menu
        
        Args:
            screen: Pygame surface to draw on
            screen_width: Width of the screen
            screen_height: Height of the screen
            save_files: List of save file names
        """
        self.__screen = screen
        self.__width = screen_width
        self.__height = screen_height
        self.__save_files = save_files
        self.__bg_color = (30, 30, 50)
        self.__clock = pygame.time.Clock()
        self.__fps = 60
        
        # Initialize fonts
        self.__title_font = pygame.font.SysFont(None, 80)
        self.__button_font = pygame.font.SysFont(None, 40)
        self.__info_font = pygame.font.SysFont(None, 30)
        
        # Create buttons
        self.__buttons = self.__create_buttons()
    
    def __create_buttons(self) -> List[Button]:
        """Create buttons for load menu"""
        buttons = []
        
        # Back button
        back_button = Button(
            image=None,
            pos=(100, 550),
            text_input="BACK",
            font=self.__button_font,
            base_color="White",
            hovering_color="#b68f40",
            action="back"
        )
        buttons.append(back_button)
        
        # Save file buttons
        center_x = self.__width // 2
        start_y = 200
        spacing = 70
        
        if self.__save_files:
            for i, save_file in enumerate(self.__save_files):
                button = Button(
                    image=None,
                    pos=(center_x, start_y + i * spacing),
                    text_input=save_file,
                    font=self.__button_font,
                    base_color="White",
                    hovering_color="#b68f40",
                    action=f"load:{save_file}"
                )
                buttons.append(button)
        
        return buttons
    
    def display(self) -> Optional[str]:
        """
        Display load menu
        
        Returns:
            Save file to load or None if cancelled
        """
        while True:
            mouse_pos = pygame.mouse.get_pos()
            self.__screen.fill(self.__bg_color)
            
            # Draw title
            title_text = self.__title_font.render("LOAD GAME", True, "White")
            title_rect = title_text.get_rect(center=(self.__width // 2, 100))
            self.__screen.blit(title_text, title_rect)
            
            # Show message if no save files
            if not self.__save_files:
                info_text = self.__info_font.render("No save files found", True, "White")
                info_rect = info_text.get_rect(center=(self.__width // 2, self.__height // 2))
                self.__screen.blit(info_text, info_rect)
            
            # Update and draw buttons
            for button in self.__buttons:
                button.change_color(mouse_pos)
                button.update(self.__screen)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.__buttons:
                        if button.check_for_input(mouse_pos):
                            action = button.action
                            if action == "back":
                                return None
                            elif action.startswith("load:"):
                                return action[5:]  # Return save file name
            
            pygame.display.update()
            self.__clock.tick(self.__fps)


class Menu:
    """Main menu class with proper encapsulation"""
    
    def __init__(self, screen: pygame.Surface, screen_width: int, screen_height: int):
        """
        Initialize the menu
        
        Args:
            screen: Pygame surface to draw on
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        self.__screen = screen
        self.__width = screen_width
        self.__height = screen_height
        self.__clock = pygame.time.Clock()
        self.__fps = 60
        self.__game_state_manager = GameStateManager()
        
        # Get the path to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.__assets_path = os.path.join(project_root, "assets")
        
        # Load background image
        background_img = self.__load_image("environment/MenuBackground.png")
        if background_img:
            # Resize the background to fit the screen
            self.__background = pygame.transform.scale(background_img, (self.__width, self.__height))
        else:
            self.__background = None
        
        # Fallback background color if image fails to load
        self.__bg_color = (40, 40, 60)
        
        # Load font
        self.__font_path = os.path.join(self.__assets_path, "fonts")
        self.__title_font = self.__get_font(100)
        self.__button_font = self.__get_font(75)
        
        # Button images
        self.__play_btn_img = self.__load_image("Play Rect.png")
        self.__load_btn_img = self.__load_image("Options Rect.png")
        self.__exit_btn_img = self.__load_image("Quit Rect.png")
        
        # Create buttons
        self.__buttons = self.__create_buttons()
        
        # Prevent tampering with private attributes
        self.__initialized = True
    
    def __load_image(self, image_path: str) -> Optional[pygame.Surface]:
        """
        Safely load an image, returning None if it fails
        
        Args:
            image_path: Path to image file relative to assets directory
            
        Returns:
            Loaded image or None if loading failed
        """
        try:
            full_path = os.path.join(self.__assets_path, image_path)
            print(f"Attempting to load image from: {full_path}")
            if os.path.exists(full_path):
                return pygame.image.load(full_path).convert_alpha()
            return None
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading image: {e}")
            return None
    
    def __get_font(self, size: int) -> pygame.font.Font:
        """
        Get a font of specified size, falling back to system font if needed
        
        Args:
            size: Font size
            
        Returns:
            Font object
        """
        try:
            # Try to load custom font
            font_file = os.path.join(self.__font_path, "font.ttf")
            if os.path.exists(font_file):
                return pygame.font.Font(font_file, size)
            # Fall back to system font
            return pygame.font.SysFont(None, size)
        except (pygame.error, FileNotFoundError):
            # Fall back to system font
            return pygame.font.SysFont(None, size)
    
    def __create_buttons(self) -> List[Button]:
        """
        Create menu buttons
        
        Returns:
            List of Button objects
        """
        buttons = []
        
        # Visual styling
        base_color = "#d7fcd4"  # Light green
        hover_color = "White"
        
        # Button positions (centered)
        center_x = self.__width // 2
        
        # Create buttons with lower Y positions
        play_button = Button(
            image=self.__play_btn_img,
            pos=(center_x, 350),  # Changed from 250 to 350
            text_input="PLAY",
            font=self.__button_font,
            base_color=base_color,
            hovering_color=hover_color,
            action="play"
        )
        
        load_button = Button(
            image=self.__load_btn_img,
            pos=(center_x, 450),  # Changed from 400 to 450
            text_input="LOAD",
            font=self.__button_font,
            base_color=base_color,
            hovering_color=hover_color,
            action="load"
        )
        
        exit_button = Button(
            image=self.__exit_btn_img,
            pos=(center_x, 550),  # This was already at 550, so it can stay
            text_input="EXIT",
            font=self.__button_font,
            base_color=base_color,
            hovering_color=hover_color,
            action="exit"
        )
        
        buttons.extend([play_button, load_button, exit_button])
        return buttons
    
    def display(self) -> Optional[str]:
        """
        Display the menu and process events
        
        Returns:
            Action string ("play", "load") or None if exiting
        """
        # Security check
        if not hasattr(self, '_Menu__initialized') or not self.__initialized:
            raise RuntimeError("Menu object has been tampered with")
        
        while True:
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw background
            if self.__background:
                self.__screen.blit(self.__background, (0, 0))
            else:
                self.__screen.fill(self.__bg_color)
            
            # Update and draw buttons
            for button in self.__buttons:
                button.change_color(mouse_pos)
                button.update(self.__screen)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.__buttons:
                        if button.check_for_input(mouse_pos):
                            action = button.action
                            if action == "exit":
                                pygame.quit()
                                sys.exit()
                            return action
            
            # Update display
            pygame.display.update()
            self.__clock.tick(self.__fps)
    
    def start_game(self, game_class) -> None:
        """
        Main entry point for the menu system
        
        Args:
            game_class: The Game class to instantiate when starting a new game
        """
        from src.model.Game import GameState, HeroType
        
        while True:  # Loop to keep returning to the main menu
            action = self.display()
            
            if action == "play":
                # Show character selection menu
                char_selection = CharacterSelectionMenu(self.__screen, self.__width, self.__height, self.__assets_path)
                selected_character = char_selection.display()
                
                # If a character was selected (not back button)
                if selected_character:
                    print(f"Starting game with {selected_character}...")
                    print("Controls: ")
                    print("- A/D: Move left/right")
                    print("- SPACE: Attack")
                    print("- Q: Special ability")
                    print("- E: Defend")
                    print("- ESC: Pause")
                    
                    # Map the selected character string to the HeroType enum
                    hero_type_map = {
                        "knight": HeroType.KNIGHT,
                        "archer": HeroType.ARCHER,
                        "cleric": HeroType.CLERIC
                    }
                    
                    # Create game with selected character
                    if selected_character in hero_type_map:
                        game = game_class(self.__screen, self.__width, self.__height)
                        # Skip the hero selection screen and initialize game directly
                        game.state = GameState.PLAYING  # Set the state directly to PLAYING
                        game._selected_hero_type = hero_type_map[selected_character]  # Set the selected hero type
                        game._hero_selection_made = True  # Mark hero selection as made
                        game._initialize_game()  # Initialize the game with the selected hero
                        game.run()
            # If back button was clicked, continue loop to show main menu again
            
            elif action == "load":
                # Show load game menu
                save_files = self.__game_state_manager.get_save_files()
                load_menu = LoadMenu(self.__screen, self.__width, self.__height, save_files)
                save_name = load_menu.display()
                
                if save_name:
                    # Load the selected save file
                    game_state = self.__game_state_manager.load_game(save_name)
                    
                    if game_state:
                        # Create game and load state
                        game = game_class(self.__screen, self.__width, self.__height)
                    
                        # Check if the Game class has a load_game_state method
                        if hasattr(game, 'load_game_state'):
                            if game.load_game_state(game_state):
                                print(f"Loaded game: {save_name}")
                                game.run()
                            else:
                                print(f"Failed to load game: {save_name}")
                        else:
                            # If no load_game_state method, just run the game
                            print(f"Game loaded, but no load_game_state method found")
                            game.run()
                    else:
                        print(f"Failed to load save file: {save_name}")
            
            elif action == "exit":
                # Exit the game and break the loop
                pygame.quit()
                sys.exit()

class CharacterSelectionMenu:
    """Menu for selecting a character to play with"""
    
    def __init__(self, screen: pygame.Surface, screen_width: int, screen_height: int, assets_path: str):
        """
        Initialize the character selection menu
        
        Args:
            screen: Pygame surface to draw on
            screen_width: Width of the screen
            screen_height: Height of the screen
            assets_path: Path to assets directory
        """
        self.__screen = screen
        self.__width = screen_width
        self.__height = screen_height
        self.__assets_path = assets_path
        self.__clock = pygame.time.Clock()
        self.__fps = 60
        
        # Load background image
        background_img = self.__load_image("environment/SelectionScreenBackground.png")
        if background_img:
            # Resize the background to fit the screen
            self.__background = pygame.transform.scale(background_img, (self.__width, self.__height))
        else:
            self.__background = None
            print("Failed to load selection screen background")
        
        # Fallback background color if image fails to load
        self.__bg_color = (30, 30, 50)
        
        # Initialize fonts
        self.__title_font = pygame.font.SysFont(None, 60)
        self.__char_name_font = pygame.font.SysFont(None, 40)
        self.__stats_font = pygame.font.SysFont(None, 25)
        self.__button_font = pygame.font.SysFont(None, 40)
        
        # Load character data from database
        self.__characters = self.__load_character_data_from_db()
        
        # Load character images or create placeholders
        self.__character_images = {}
        for char_id, char_data in self.__characters.items():
            image = self.__load_image(char_data["image_path"])
            if image:
                # Get original dimensions for aspect ratio
                orig_width, orig_height = image.get_size()
                
                # Determine size for a square image (use the larger dimension)
                square_size = 150
                
                # Scale image to fit in the square while maintaining aspect ratio
                if orig_width > orig_height:
                    new_width = square_size
                    new_height = int(orig_height * (square_size / orig_width))
                else:
                    new_height = square_size
                    new_width = int(orig_width * (square_size / orig_height))
                
                # Scale the image
                scaled_image = pygame.transform.scale(image, (new_width, new_height))
                
                # Create a square surface (with transparent background if possible)
                try:
                    square_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
                except:
                    # Fallback to non-alpha surface if SRCALPHA not supported
                    square_surface = pygame.Surface((square_size, square_size))
                    square_surface.fill((0, 0, 0))  # Black background
                
                # Center the scaled image on the square surface
                square_surface.blit(scaled_image, 
                                   ((square_size - new_width) // 2, 
                                    (square_size - new_height) // 2))
                
                self.__character_images[char_id] = square_surface
            else:
                print(f"Failed to load image for {char_id}, creating placeholder")
                # Create a colored square placeholder with character name
                square_size = 150
                placeholder = pygame.Surface((square_size, square_size))
                
                # Use different colors for different characters
                if char_id == "knight":
                    placeholder.fill((100, 100, 200))  # Blue-ish for knight
                elif char_id == "archer":
                    placeholder.fill((100, 200, 100))  # Green-ish for archer
                elif char_id == "cleric":
                    placeholder.fill((200, 100, 100))  # Red-ish for cleric
                
                # Add character initial to the placeholder
                placeholder_font = pygame.font.SysFont(None, 70)
                initial_text = placeholder_font.render(char_data["name"][0], True, (255, 255, 255))
                initial_rect = initial_text.get_rect(center=(square_size//2, square_size//2))
                placeholder.blit(initial_text, initial_rect)
                
                self.__character_images[char_id] = placeholder
        
        # Create back button
        self.__back_button = Button(
            image=None,
            pos=(100, 550),
            text_input="BACK",
            font=self.__button_font,
            base_color="White",
            hovering_color="#b68f40",
            action="back"
        )
        
        # Character selection buttons
        self.__selection_buttons = self.__create_selection_buttons()
    
    def __load_image(self, image_path: str) -> Optional[pygame.Surface]:
        """
        Safely load an image, returning None if it fails
        
        Args:
            image_path: Path to image file relative to assets directory
            
        Returns:
            Loaded image or None if loading failed
        """
        try:
            full_path = os.path.join(self.__assets_path, image_path)
            print(f"Attempting to load image from: {full_path}")
            if os.path.exists(full_path):
                return pygame.image.load(full_path).convert_alpha()
            return None
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading image: {e}")
            return None
    
    def __load_character_data_from_db(self) -> Dict[str, Dict]:
        """
        Load character stats and data from the database
        
        Returns:
            Dictionary containing character data with actual stats from database
        """
        try:
            conn = sqlite3.connect('game_data.db')
            c = conn.cursor()
            
            # Get hero stats from database
            c.execute('''
                SELECT hero_type, max_health, speed, damage, attack_range, 
                       attack_speed, special_cooldown, defense, critical_chance, critical_damage
                FROM hero_stats
                WHERE hero_type IN ('knight', 'archer', 'cleric')
            ''')
            
            hero_stats = c.fetchall()
            conn.close()
            
            # Create character data dictionary
            characters = {}
            
            for hero_type, max_health, speed, damage, attack_range, attack_speed, special_cooldown, defense, critical_chance, critical_damage in hero_stats:
                # Format stats for display
                stats = [
                    f"HP: {max_health}",
                    f"Attack: {damage}",
                    f"Speed: {speed}",
                    f"Range: {attack_range}"
                ]
                
                # Define character-specific abilities and descriptions
                abilities = {
                    "knight": {
                        "name": "Knight",
                        "ability": "Special: Shield Bash - Stuns enemies",
                        "description": "Tank with high defense and health",
                        "image_path": "sprites/heroes/knight/Knight_1/Knight_Stance.png"
                    },
                    "archer": {
                        "name": "Archer", 
                        "ability": "Special: Rain of Arrows - Multiple projectiles",
                        "description": "Ranged attacker with high critical chance",
                        "image_path": "sprites/heroes/archer/Samurai_Archer/Archer_Stance.png"
                    },
                    "cleric": {
                        "name": "Cleric",
                        "ability": "Special: Heal + Fireball - Support magic",
                        "description": "Support with healing and magic damage",
                        "image_path": "sprites/heroes/cleric/Fire_Cleric/Cleric_Stance.png"
                    }
                }
                
                # Combine database stats with character-specific info
                characters[hero_type] = {
                    "name": abilities[hero_type]["name"],
                    "stats": stats,
                    "ability": abilities[hero_type]["ability"],
                    "description": abilities[hero_type]["description"],
                    "image_path": abilities[hero_type]["image_path"],
                    # Store raw stats for potential use
                    "raw_stats": {
                        "max_health": max_health,
                        "speed": speed,
                        "damage": damage,
                        "attack_range": attack_range,
                        "attack_speed": attack_speed,
                        "special_cooldown": special_cooldown,
                        "defense": defense,
                        "critical_chance": critical_chance,
                        "critical_damage": critical_damage
                    }
                }
            
            return characters
            
        except Exception as e:
            print(f"Error loading character data from database: {e}")
            # Fallback to hardcoded stats if database fails
            return {
                "knight": {
                    "name": "Knight",
                    "stats": ["HP: 375", "Attack: 55", "Speed: 12", "Range: 80"],
                    "ability": "Special: Shield Bash - Stuns enemies",
                    "description": "Tank with high defense and health",
                    "image_path": "sprites/heroes/knight/Knight_1/Knight_Stance.png"
                },
                "archer": {
                    "name": "Archer",
                    "stats": ["HP: 150", "Attack: 40", "Speed: 10", "Range: 120"],
                    "ability": "Special: Rain of Arrows - Multiple projectiles",
                    "description": "Ranged attacker with high critical chance",
                    "image_path": "sprites/heroes/archer/Samurai_Archer/Archer_Stance.png"
                },
                "cleric": {
                    "name": "Cleric",
                    "stats": ["HP: 250", "Attack: 85", "Speed: 8", "Range: 60"],
                    "ability": "Special: Heal + Fireball - Support magic",
                    "description": "Support with healing and magic damage",
                    "image_path": "sprites/heroes/cleric/Fire_Cleric/Cleric_Stance.png"
                }
            }
    
    def __create_selection_buttons(self) -> List[Button]:
        """
        Create clickable buttons for character selection
        
        Returns:
            List of Button objects for character selection
        """
        buttons = []
        
        # Position characters horizontally centered and evenly spaced
        character_ids = list(self.__characters.keys())
        num_characters = len(character_ids)
        total_width = self.__width * 0.8  # Use 80% of screen width
        spacing = total_width / num_characters
        
        start_x = (self.__width - total_width) / 2 + spacing / 2
        y_position = 180  # Vertical position for character images (moved up a bit)
        
        for i, char_id in enumerate(character_ids):
            char_data = self.__characters[char_id]
            x_position = start_x + i * spacing
            
            # Create a select button below each character
            select_button = Button(
                image=None,
                pos=(x_position, y_position + 260),  # Position below character stats
                text_input="SELECT",
                font=self.__button_font,
                base_color="White",
                hovering_color="#b68f40",
                action=f"select:{char_id}"
            )
            buttons.append(select_button)
        
        return buttons
    
    def display(self) -> Optional[str]:
        """
        Display character selection menu
        
        Returns:
            Selected character ID or None if cancelled
        """
        while True:
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw background
            if self.__background:
                self.__screen.blit(self.__background, (0, 0))
            else:
                self.__screen.fill(self.__bg_color)
            
            # Draw title
            title_text = self.__title_font.render("SELECT YOUR CHARACTER", True, "White")
            title_rect = title_text.get_rect(center=(self.__width // 2, 70))
            self.__screen.blit(title_text, title_rect)
            
            # Draw character images and info
            self.__draw_characters()
            
            # Update and draw back button
            self.__back_button.change_color(mouse_pos)
            self.__back_button.update(self.__screen)
            
            # Update and draw character selection buttons
            for button in self.__selection_buttons:
                button.change_color(mouse_pos)
                button.update(self.__screen)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if back button is clicked
                    if self.__back_button.check_for_input(mouse_pos):
                        return None
                    
                    # Check if any character select button is clicked
                    for button in self.__selection_buttons:
                        if button.check_for_input(mouse_pos):
                            action = button.action
                            if action.startswith("select:"):
                                return action[7:]  # Return character ID
            
            pygame.display.update()
            self.__clock.tick(self.__fps)
    
    def __draw_characters(self) -> None:
        """
        Draw character images, names, stats, and abilities
        """
        character_ids = list(self.__characters.keys())
        num_characters = len(character_ids)
        total_width = self.__width * 0.8
        spacing = total_width / num_characters
        
        start_x = (self.__width - total_width) / 2 + spacing / 2
        y_position = 180  # Vertical position for character images (moved up a bit)
        
        for i, char_id in enumerate(character_ids):
            char_data = self.__characters[char_id]
            x_position = start_x + i * spacing
            
            # Draw character image
            image_rect = self.__character_images[char_id].get_rect(center=(x_position, y_position))
            self.__screen.blit(self.__character_images[char_id], image_rect)
            
            # Draw character name
            name_text = self.__char_name_font.render(char_data["name"], True, "White")
            name_rect = name_text.get_rect(center=(x_position, y_position + 110))
            self.__screen.blit(name_text, name_rect)
            
            # Draw character stats
            for j, stat in enumerate(char_data["stats"]):
                stat_text = self.__stats_font.render(stat, True, "White")
                stat_rect = stat_text.get_rect(center=(x_position, y_position + 150 + j * 25))
                self.__screen.blit(stat_text, stat_rect)
            
            # Draw character ability
            ability_text = self.__stats_font.render(char_data["ability"], True, (255, 215, 0))  # Gold color
            ability_rect = ability_text.get_rect(center=(x_position, y_position + 200))


class GameResultMenu:
    """Menu for displaying game results (victory or defeat)"""

    def __init__(self, screen: pygame.Surface, screen_width: int, screen_height: int, assets_path: str,
                 is_victory: bool):
        """
        Initialize the game result menu

        Args:
            screen: Pygame surface to draw on
            screen_width: Width of the screen
            screen_height: Height of the screen
            assets_path: Path to assets directory
            is_victory: True for victory screen, False for game over screen
        """
        self.__screen = screen
        self.__width = screen_width
        self.__height = screen_height
        self.__assets_path = assets_path
        self.__is_victory = is_victory
        self.__clock = pygame.time.Clock()
        self.__fps = 60

        # Load background image based on result
        if is_victory:
            self.__bg_image = self.__load_image("environment/victory_pic.png")
            self.__result_text = "YOU WON!"
            self.__text_color = (0, 255, 0)  # Green for victory
            self.__bg_color = (20, 50, 20)  # Dark green fallback
        else:
            self.__bg_image = self.__load_image("environment/gameover_pic.jpg")
            self.__result_text = "YOU LOST"
            self.__text_color = (255, 0, 0)  # Red for defeat
            self.__bg_color = (50, 20, 20)  # Dark red fallback

        # Scale background to fit screen if loaded
        if self.__bg_image:
            self.__bg_image = pygame.transform.scale(self.__bg_image, (self.__width, self.__height))

        # Initialize fonts
        self.__title_font = pygame.font.SysFont(None, 100)
        self.__button_font = pygame.font.SysFont(None, 50)

        # Create buttons
        self.__buttons = self.__create_buttons()

    def __load_image(self, image_path: str) -> Optional[pygame.Surface]:
        """
        Safely load an image, returning None if it fails

        Args:
            image_path: Path to image file relative to assets directory

        Returns:
            Loaded image or None if loading failed
        """
        try:
            full_path = os.path.join(self.__assets_path, image_path)
            print(f"Attempting to load image from: {full_path}")
            if os.path.exists(full_path):
                return pygame.image.load(full_path).convert_alpha()
            return None
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading image: {e}")
            return None

    def __create_buttons(self) -> List[Button]:
        """
        Create buttons for the result screen

        Returns:
            List of Button objects
        """
        buttons = []

        # Main menu button
        main_menu_button = Button(
            image=None,
            pos=(self.__width // 2, self.__height - 150),
            text_input="MAIN MENU",
            font=self.__button_font,
            base_color="White",
            hovering_color="#b68f40",
            action="main_menu"
        )
        buttons.append(main_menu_button)

        return buttons

    def display(self) -> str:
        """
        Display the result screen

        Returns:
            Action string (currently only "main_menu")
        """
        while True:
            mouse_pos = pygame.mouse.get_pos()

            # Draw background
            if self.__bg_image:
                self.__screen.blit(self.__bg_image, (0, 0))
            else:
                self.__screen.fill(self.__bg_color)

            # Draw semi-transparent overlay to make text more visible
            overlay = pygame.Surface((self.__width, self.__height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
            self.__screen.blit(overlay, (0, 0))

            # Draw title text
            title_text = self.__title_font.render(self.__result_text, True, self.__text_color)
            title_rect = title_text.get_rect(center=(self.__width // 2, self.__height // 3))
            self.__screen.blit(title_text, title_rect)

            # Update and draw buttons
            for button in self.__buttons:
                button.change_color(mouse_pos)
                button.update(self.__screen)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "main_menu"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.__buttons:
                        if button.check_for_input(mouse_pos):
                            return button.action

            pygame.display.update()
            self.__clock.tick(self.__fps)
