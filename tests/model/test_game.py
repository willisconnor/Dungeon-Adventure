import unittest
from unittest.mock import MagicMock, patch
import pygame
from enum import Enum
from src.model.Game import Game, GameState, HeroType


class TestGame(unittest.TestCase):
    """Tests for the Game class"""

    def setUp(self):
        """Set up test environment"""
        pygame.init()
        
        # Create mock screen
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.Surface((self.screen_width, self.screen_height))
        
        # Create game instance
        self.game = Game(self.screen, self.screen_width, self.screen_height)

    def tearDown(self):
        """Clean up pygame"""
        pygame.quit()

    def test_initialization(self):
        """Test game initialization"""
        # Check initial state
        self.assertEqual(self.game.state, GameState.MENU)
        self.assertFalse(self.game._hero_selection_made)
        self.assertIsNone(self.game._selected_hero_type)
        
        # Screen parameters should be set
        self.assertEqual(self.game.screen, self.screen)
        self.assertEqual(self.game.screen_width, self.screen_width)
        self.assertEqual(self.game.screen_height, self.screen_height)
        
        # Clock should be initialized
        self.assertIsInstance(self.game.clock, pygame.time.Clock)

    @patch('src.model.Game.HeroFactory')
    def test_initialize_game(self, mock_hero_factory):
        """Test game initialization process"""
        # Set up for initialization
        self.game._hero_selection_made = True
        self.game._selected_hero_type = HeroType.KNIGHT
        
        # Create mock hero and factory
        mock_hero = MagicMock()
        mock_hero_factory.create_hero.return_value = mock_hero
        
        # Initialize game
        self.game._initialize_game()
        
        # Hero factory should be called to create hero
        mock_hero_factory.create_hero.assert_called_once_with(
            HeroType.KNIGHT, 
            self.game.screen_width // 2, 
            self.game.screen_height // 2
        )
        
        # Hero should be set
        self.assertEqual(self.game.hero, mock_hero)
        
        # Game state should change to PLAYING
        self.assertEqual(self.game.state, GameState.PLAYING)

    def test_handle_events_quit(self):
        """Test handling quit event"""
        # Create a quit event
        quit_event = pygame.event.Event(pygame.QUIT)
        
        # Set running flag
        self.game._running = True
        
        # Handle event with mocked pygame.event.get
        with patch('pygame.event.get', return_value=[quit_event]):
            self.game._handle_events()
        
        # Game should stop running
        self.assertFalse(self.game._running)

    def test_handle_events_hero_selection(self):
        """Test handling hero selection events"""
        # Set game to HERO_SELECTION state
        self.game.state = GameState.HERO_SELECTION
        
        # Create keydown events for number keys
        key1_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1)
        key2_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2)
        key3_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3)
        
        # Test knight selection (key 1)
        with patch('pygame.event.get', return_value=[key1_event]):
            self.game._handle_events()
        
        self.assertEqual(self.game._selected_hero_type, HeroType.KNIGHT)
        self.assertTrue(self.game._hero_selection_made)
        
        # Reset and test archer selection (key 2)
        self.game._hero_selection_made = False
        self.game._selected_hero_type = None
        
        with patch('pygame.event.get', return_value=[key2_event]):
            self.game._handle_events()
        
        self.assertEqual(self.game._selected_hero_type, HeroType.ARCHER)
        self.assertTrue(self.game._hero_selection_made)
        
        # Reset and test cleric selection (key 3)
        self.game._hero_selection_made = False
        self.game._selected_hero_type = None
        
        with patch('pygame.event.get', return_value=[key3_event]):
            self.game._handle_events()
        
        self.assertEqual(self.game._selected_hero_type, HeroType.CLERIC)
        self.assertTrue(self.game._hero_selection_made)

    def test_handle_events_playing(self):
        """Test handling events in PLAYING state"""
        # Set up game in PLAYING state with mock hero
        self.game.state = GameState.PLAYING
        self.game.hero = MagicMock()
        self.game.hero.is_alive = True
        
        # Create keydown event for ESC key (pause)
        esc_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        
        # Handle event
        with patch('pygame.event.get', return_value=[esc_event]):
            self.game._handle_events()
        
        # Game should be paused
        self.assertEqual(self.game.state, GameState.PAUSED)
        
        # Create another ESC event to unpause
        with patch('pygame.event.get', return_value=[esc_event]):
            self.game._handle_events()
        
        # Game should resume
        self.assertEqual(self.game.state, GameState.PLAYING)

    def test_handle_events_game_over(self):
        """Test handling events in GAME_OVER state"""
        # Set game to GAME_OVER state
        self.game.state = GameState.GAME_OVER
        
        # Create keydown event for RETURN key (restart)
        return_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        
        # Handle event
        with patch('pygame.event.get', return_value=[return_event]):
            self.game._handle_events()
        
        # Game should return to menu
        self.assertEqual(self.game.state, GameState.MENU)

    @patch('src.model.Game.pygame.key.get_pressed')
    def test_handle_player_input(self, mock_get_pressed):
        """Test handling player input"""
        # Set up game in PLAYING state with mock hero
        self.game.state = GameState.PLAYING
        self.game.hero = MagicMock()
        self.game.hero.is_alive = True
        
        # Mock key presses
        mock_keys = {pygame.K_a: True, pygame.K_d: False}
        mock_get_pressed.return_value = mock_keys
        
        # Handle input
        self.game._handle_player_input(1/60)  # dt = 1/60
        
        # Hero's handle_input should be called
        self.game.hero.handle_input.assert_called_once_with(mock_keys, 1/60)

    def test_update_playing(self):
        """Test updating game in PLAYING state"""
        # Set up game in PLAYING state with mock hero
        self.game.state = GameState.PLAYING
        self.game.hero = MagicMock()
        self.game.hero.is_alive = True
        self.game.dungeon = MagicMock()
        self.game.projectile_manager = MagicMock()
        self.game.monsters = []
        
        # Update game
        self.game._update(1/60)  # dt = 1/60
        
        # Hero should be updated
        self.game.hero.update.assert_called_once_with(1/60)
        
        # Dungeon should be updated
        self.game.dungeon.update_current_room_interactions.assert_called_once()
        
        # Projectile manager should be updated
        self.game.projectile_manager.update.assert_called_once_with(1/60)

    def test_update_hero_death(self):
        """Test hero death state transition"""
        # Set up game in PLAYING state with dead hero
        self.game.state = GameState.PLAYING
        self.game.hero = MagicMock()
        self.game.hero.is_alive = False
        self.game.dungeon = MagicMock()
        self.game.projectile_manager = MagicMock()
        self.game.monsters = []
        
        # Update game
        self.game._update(1/60)  # dt = 1/60
        
        # Game state should change to GAME_OVER
        self.assertEqual(self.game.state, GameState.GAME_OVER)

    def test_save_game_state(self):
        """Test saving game state"""
        # Set up game with mock components
        self.game.hero = MagicMock()
        self.game.hero.get_serializable_state.return_value = {"health": 100, "position": [100, 200]}
        
        # Save game state
        state = self.game.save_game_state()
        
        # Should include hero state
        self.assertIn("hero", state)
        self.assertEqual(state["hero"], {"health": 100, "position": [100, 200]})

    def test_load_game_state(self):
        """Test loading game state"""
        # Create a mock hero
        mock_hero = MagicMock()
        
        # Set up hero factory to return mock hero
        with patch('src.model.Game.HeroFactory') as mock_factory:
            mock_factory.create_hero.return_value = mock_hero
            
            # Create game state to load
            state = {
                "hero": {
                    "type": "KNIGHT",
                    "health": 80,
                    "position": [150, 250]
                }
            }
            
            # Load state
            result = self.game.load_game_state(state)
            
            # Should return True for successful load
            self.assertTrue(result)
            
            # Hero should be created and state loaded
            mock_factory.create_hero.assert_called_once()
            mock_hero.load_state.assert_called_once_with(state["hero"])
            
            # Game should be in PLAYING state
            self.assertEqual(self.game.state, GameState.PLAYING)

    def test_render(self):
        """Test game rendering"""
        # Set up game with mock components
        self.game.hero = MagicMock()
        self.game.dungeon = MagicMock()
        self.game.current_room = MagicMock()
        self.game.projectile_manager = MagicMock()
        self.game.monsters = [MagicMock()]
        
        # Set game to PLAYING state
        self.game.state = GameState.PLAYING
        
        # Render game
        self.game._render()
        
        # Components should be rendered
        self.game.dungeon.get_current_room().draw.assert_called_once()
        self.game.hero.render.assert_called_once()
        self.game.monsters[0].render.assert_called_once()
        self.game.projectile_manager.render.assert_called_once()


if __name__ == '__main__':
    unittest.main()