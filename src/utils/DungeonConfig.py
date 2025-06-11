from src.model.RoomDungeonSystem import DungeonTemplate


class DungeonConfig:
    """Configuration for dungeon generation"""

    # Set this to True for easy demonstration mode
    DEMO_MODE = False

    @staticmethod
    def get_template() -> DungeonTemplate:
        """
        Get the dungeon template to use

        Returns:
            DungeonTemplate to use for generation
        """
        if DungeonConfig.DEMO_MODE:
            return DungeonTemplate.DEMO
        else:
            # You can change this to test different layouts:
            # - DungeonTemplate.CROSS: Original cross pattern
            # - DungeonTemplate.SQUARE: 3x3 grid with all rooms
            # - DungeonTemplate.DEMO: Simple 2-room path for demos
            # - DungeonTemplate.FULL: All possible rooms filled
            return DungeonTemplate.SQUARE

    @staticmethod
    def get_template_description(template: DungeonTemplate) -> str:
        """Get description of a template"""
        descriptions = {
            DungeonTemplate.CROSS: "Classic cross-shaped dungeon (5 rooms)",
            DungeonTemplate.SQUARE: "Full 3x3 grid dungeon (9 rooms)",
            DungeonTemplate.DEMO: "Simple linear path (2 rooms) - Easy for demonstrations",
            DungeonTemplate.FULL: "Maximum complexity - All rooms connected"
        }
        return descriptions.get(template, "Unknown template")


# Quick toggle for demonstration
def enable_demo_mode():
    """Enable demo mode for easy gameplay"""
    DungeonConfig.DEMO_MODE = True
    print("Demo mode enabled - Simple 2-room dungeon")


def disable_demo_mode():
    """Disable demo mode for normal gameplay"""
    DungeonConfig.DEMO_MODE = False
    print("Demo mode disabled - Full dungeon layout")