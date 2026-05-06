"""
Gameplay constants and tuning values.

This module contains ONLY gameplay-affecting numbers: speeds, grid sizes,
timers, difficulty definitions, and structural constants. No colors or
visual layout values — those live in config/theme.py.

Separating gameplay from visuals means a designer can tweak colors without
risk of breaking physics, and a gameplay programmer can tune speeds without
touching the UI.
"""

# -- Window defaults --
# The window is resizable; these are just the initial dimensions.
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
FPS = 60
# Fixed physics timestep. The game loop accumulates real time and steps
# physics in exactly FIXED_DT increments, ensuring deterministic behavior
# regardless of render framerate.
FIXED_DT = 1.0 / FPS

# -- Ball physics (all values in grid units) --
# Visual radius: 0.5 means the ball fills exactly one corridor cell.
BALL_RADIUS = 0.5
# Collision radius: smaller than visual (0.4 vs 0.5) to give 0.1 units
# of tolerance per side when entering perpendicular corridors. Without
# this tolerance, the ball needs pixel-perfect alignment to turn corners.
COLLISION_RADIUS = 0.4
# Player speed in grid units per second. At 60fps with FIXED_DT, each
# frame displaces 4.8 * (1/60) = 0.08 grid units.
PLAYER_SPEED = 4.8

# -- Difficulty definitions --
# Grid sizes as (cols, rows). The maze generator produces a wall-passage
# grid where passage cells are at odd positions. The effective number of
# corridor cells is roughly (cols-1)/2 × (rows-1)/2.
DIFFICULTY_GRIDS = {
    "easy": (15, 12),
    "normal": (20, 16),
    "hard": (25, 20),
    "extreme": (40, 50),
}

# -- Menu option lists --
# These define the choices shown in each menu screen. The order here
# determines the display order. Adding a new entry here + its color in
# theme.py is all that's needed to add a new option to the menu.
GAME_TYPES = ["classic", "challenger", "infinite", "pacman", "mirror"]
PLAY_MODES = ["arcade", "story"]
DIFFICULTIES = ["easy", "normal", "hard", "extreme"]

# -- Story mode --
# Number of seeded puzzles per game_type × difficulty combination.
STORY_LEVELS = 50
# Columns in the level select grid. Rows are computed from this.
LEVEL_GRID_COLS = 10

# -- Challenger mode timers (seconds) --
# The player must solve the puzzle within this time or fail.
CHALLENGER_TIMES = {
    "easy": 12, "normal": 25, "hard": 47, "extreme": 75,
}

# -- Pacman mode --
# AI chase speed per difficulty (grid units/second). Player speed is 4.8.
# At "extreme", the AI is 5% faster than the player, forcing the player
# to exploit maze loops rather than outrun the AI.
PACMAN_AI_SPEEDS = {
    "easy": 3.0,      # 63% of player
    "normal": 3.6,    # 75%
    "hard": 4.6,      # 96% — nearly equal
    "extreme": 5.04,  # 105% — faster than the player
}
# How often (in physics frames) the AI recalculates its BFS path.
# Lower = smarter but more CPU. 10 frames ≈ 6 recalcs/second.
PACMAN_REPATH_INTERVAL = 10
# Fraction of removable internal walls to delete when creating loops.
# Higher = more loops = easier to evade. 0.25 is a good balance.
PACMAN_LOOP_REMOVAL_RATIO = 0.25
# How long the player must survive to win (seconds).
PACMAN_SURVIVE_TIMES = {
    "easy": 30, "normal": 45, "hard": 60, "extreme": 65,
}

# -- Infinite mode --
# Number of portal pairs per axis (left↔right, top↔bottom), scaled by difficulty.
# Bigger mazes get more portals. Each pair connects a random left opening to a
# random right opening (or top↔bottom), so portals don't always lead straight across.
PORTALS_PER_AXIS = {
    "easy": 2,
    "normal": 3,
    "hard": 5,
    "extreme": 8,
}

# -- Particle physics --
# Applied per frame to particle velocity. Gravity pulls down, drag slows.
PARTICLE_GRAVITY = 0.05
PARTICLE_DRAG = 0.98
