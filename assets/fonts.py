"""
Font asset management.

Provides a singleton FontManager that holds pre-initialized pygame font
objects. Must call font_manager.init() after pygame.init().

Uses the singleton-instance pattern (not module-level variables) to avoid
the "import captures None" gotcha: `from assets.fonts import font_manager`
imports the FontManager object reference, and `font_manager.font` always
reads the current attribute — even if init() hasn't been called yet at
import time.
"""

import pygame


class FontManager:
    """Holds initialized pygame font objects.

    Three fonts at different sizes for different UI purposes:
        font:  48pt — menu option text, prompt headers
        small: 32pt — hints, subtitles, level numbers
        title: 72pt — game title, congratulations text

    Attributes are None until init() is called.
    """

    def __init__(self):
        self.font = None
        self.small = None
        self.title = None

    def init(self):
        """Initialize all fonts. Must be called after pygame.init().

        Uses SysFont(None, size) which loads the default system font.
        This avoids bundling font files while still rendering cleanly.
        """
        self.font = pygame.font.SysFont(None, 48)
        self.small = pygame.font.SysFont(None, 32)
        self.title = pygame.font.SysFont(None, 72)


# Module-level singleton. Import this, not the class.
font_manager = FontManager()
