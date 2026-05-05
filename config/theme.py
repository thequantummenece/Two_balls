"""
Visual constants: colors, UI layout, and animation tuning.

Everything here affects appearance only — no gameplay impact. A designer
can freely modify this file without breaking game logic.
"""

# -- Core palette --
PINK = (255, 105, 180)       # Pink ball color
BLUE = (0, 100, 255)         # Blue ball color
BLACK = (0, 0, 0)            # Screen clear / menu background
WHITE = (255, 255, 255)      # General white
GREEN = (0, 255, 100)        # Win message accent
SUBTITLE_GRAY = (160, 160, 160)  # Menu subtitle text
DIM_GRAY = (120, 120, 120)      # Unselected level numbers

# -- Game area --
GAME_BG = WHITE              # Background behind the maze (white)
WALL_COLOR = (30, 30, 30)    # Near-black for maze walls
WALL_INSET = 2               # Pixels inset per side for thinner wall look
WALL_BORDER_RADIUS = 3       # Corner rounding on wall blocks

# -- Per-option colors for menu screens --
# Each dict maps an option string to its display color.
GAME_TYPE_COLORS = {
    "classic": (100, 200, 255),
    "challenger": (255, 80, 80),
    "infinite": (0, 220, 200),
    "pacman": (255, 255, 50),
}

PLAY_MODE_COLORS = {
    "arcade": (255, 180, 50),
    "story": (180, 100, 255),
}

DIFFICULTY_COLORS = {
    "easy": (100, 220, 100),
    "normal": (100, 180, 255),
    "hard": (255, 100, 100),
    "extreme": (255, 50, 200),
}

# -- UI layout (pixels) --
MENU_ITEM_OFFSET = 60        # Gap between subtitle and first option
MENU_ITEM_SPACING = 80       # Vertical spacing between menu options
UNDERLINE_PADDING = 20       # Extra width on the selection underline bar
LEVEL_CELL_MAX_W = 60        # Max pixel width of a level grid cell
LEVEL_CELL_MAX_H = 50        # Max pixel height of a level grid cell

# -- Timer HUD --
TIMER_BAR_HEIGHT = 6         # Height of the countdown bar in pixels
TIMER_MARGIN = 20            # Horizontal margin from screen edge
TIMER_BG = (60, 60, 60)      # Bar background (dark gray)
