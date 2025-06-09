import pygame
import sys
import os
from typing import Optional, List, Tuple, Dict, Callable

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
            print(f"File exists: {os.path.exists(full_path)}")
            if os.path.exists(full_path):
                return pygame.image.load(full_path)
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
        action = self.display()
        
        if action == "play":
            # Start a new game
            print("Starting game...")
            print("Controls: ")
            print("- A/D: Move left/right")
            print("- SPACE: Attack")
            print("- Q: Special ability")
            print("- E: Defend")
            print("- 1/2/3: Switch heroes")
            print("- ESC: Pause")
            
            game = game_class(self.__screen, self.__width, self.__height)
            game.run()
            
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
                            # If loading fails, go back to menu
                            self.start_game(game_class)
                    else:
                        # If no load_game_state method, just run the game
                        print(f"Game loaded, but no load_game_state method found")
                        game.run()
                else:
                    print(f"Failed to load save file: {save_name}")
                    # If loading fails, go back to menu
                    self.start_game(game_class)