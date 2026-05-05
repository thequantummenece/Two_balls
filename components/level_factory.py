"""
Unified level creation for all game types.

This is the SINGLE entry point for generating playable levels. Instead of
separate make_level(), make_infinite_level(), make_pacman_level() functions,
there's one create_level(difficulty, game_type, seed) that handles all types.

The function:
    1. Generates a perfect maze via MazeGenerator
    2. Applies game-type-specific modifications (portals, loops)
    3. Places balls at maximum distance via double-BFS
    4. Returns a level dict ready for the PlayingState

Seeding: When seed is not None, the global random state is saved, replaced
with the seed, and restored after generation via try/finally. This ensures
story mode levels are deterministic while arcade levels remain random.
"""

import random
from config.settings import (
    DIFFICULTY_GRIDS, PORTALS_PER_AXIS, PACMAN_LOOP_REMOVAL_RATIO,
)
from components.maze_generator import MazeGenerator


def _seeded(seed, func):
    """Run func() with a deterministic random seed, then restore state.

    If seed is None, func() runs with whatever random state exists (random).
    If seed is provided, the current random state is saved, replaced with
    the seed, func() runs, and the original state is restored — even if
    func() raises an exception (guaranteed by try/finally).

    This is critical for story mode: the same seed always produces the
    same maze, but arcade mode's randomness isn't contaminated.

    Args:
        seed: Hashable seed value, or None for random.
        func: Zero-argument callable that uses the random module.

    Returns:
        Whatever func() returns.
    """
    if seed is None:
        return func()
    old_state = random.getstate()
    random.seed(seed)
    try:
        return func()
    finally:
        random.setstate(old_state)


def _build_walls(matrix):
    """Convert a 2D matrix (1=wall, 0=open) into a flat list of wall tuples.

    Each wall cell becomes a (col, row, 1, 1) tuple in grid coordinates.
    These tuples are used for both collision detection and rendering.

    Args:
        matrix: 2D list where matrix[row][col] is 0 (open) or 1 (wall).

    Returns:
        List of (gx, gy, gw, gh) tuples, one per wall cell.
    """
    return [(c, r, 1, 1) for r, row in enumerate(matrix)
            for c, cell in enumerate(row) if cell == 1]


def _base_generate(cols, rows):
    """Generate a base perfect maze.

    Returns both the generator (for find_distant_pair) and the matrix
    (for further modification by game-type-specific code).
    """
    gen = MazeGenerator(cols, rows)
    matrix = gen.generate()
    return gen, matrix


def create_level(difficulty, game_type="classic", seed=None):
    """Create a complete level for any game type.

    This is the unified level factory. It generates a maze, applies
    game-type-specific modifications, places balls, and returns a dict.

    The returned dict always has:
        pink_start: (float, float) — ball center in grid coordinates
        blue_start: (float, float) — ball center in grid coordinates
        walls: list of (gx, gy, gw, gh) tuples

    Game-type-specific extras:
        "infinite" adds: portals (list of portal dicts)
        "pacman" adds:  matrix (2D list for AI pathfinding)

    Args:
        difficulty: "easy", "normal", "hard", or "extreme"
        game_type: "classic", "challenger", "infinite", or "pacman"
        seed: Deterministic seed for story mode, or None for random.

    Returns:
        Level dict ready to be consumed by PlayingState.
    """
    cols, rows = DIFFICULTY_GRIDS[difficulty]

    def _generate():
        gen, matrix = _base_generate(cols, rows)

        # Apply game-type-specific maze modifications BEFORE placing balls,
        # because modifications change the maze topology and affect which
        # cells are the most distant pair.
        portals = None
        if game_type == "infinite":
            portals = _open_portals(matrix, cols, rows)
        elif game_type == "pacman":
            _add_loops(matrix, cols, rows)

        # Place balls at the two most distant open cells (graph diameter).
        # This maximizes the puzzle difficulty by starting balls far apart.
        pink, blue = gen.find_distant_pair(matrix)

        level = {
            "pink_start": (pink[0] + 0.5, pink[1] + 0.5),  # Cell center
            "blue_start": (blue[0] + 0.5, blue[1] + 0.5),
            "walls": _build_walls(matrix),
        }

        # Only include extra data when the game type needs it.
        # Pacman needs the matrix for BFS pathfinding.
        # Infinite needs portal positions for ghost rendering (currently
        # portals are just visual gaps, but the data is available).
        if game_type == "pacman":
            level["matrix"] = matrix
        if game_type == "infinite":
            level["portals"] = portals

        return level

    return _seeded(seed, _generate)


# ---------------------------------------------------------------------------
# Infinite mode: portal generation
# ---------------------------------------------------------------------------

def _open_portals(matrix, cols, rows):
    """Create portal pairs by removing boundary walls on opposite edges.

    For each axis (horizontal = left↔right, vertical = top↔bottom),
    finds cells where BOTH the near-boundary and far-boundary cells are
    open corridors, then removes the boundary walls to create openings.

    For grids with padding rows/columns (where the generated maze is
    smaller than the target grid), ALL padding cells along the portal
    path are cleared to ensure the ball can actually pass through.

    Args:
        matrix: Maze matrix (modified in-place).
        cols, rows: Grid dimensions.

    Returns:
        List of portal dicts with axis, position, and endpoint coordinates.
    """
    portals = []

    # Find the actual maze boundaries (padding rows are all walls)
    last_open_row = max(
        (r for r in range(rows - 1, 0, -1)
         if any(matrix[r][c] == 0 for c in range(cols))),
        default=rows - 2,
    )
    last_open_col = max(
        (c for c in range(cols - 1, 0, -1)
         if any(matrix[r][c] == 0 for r in range(rows))),
        default=cols - 2,
    )

    # Horizontal portals: left edge ↔ right edge
    # A row is a candidate if both its leftmost and rightmost corridor
    # cells are open (col 1 and last_open_col).
    h_candidates = [r for r in range(1, last_open_row + 1)
                    if matrix[r][1] == 0 and matrix[r][last_open_col] == 0]
    random.shuffle(h_candidates)
    for r in h_candidates[:PORTALS_PER_AXIS]:
        # Clear left boundary wall
        matrix[r][0] = 0
        # Clear all padding columns on the right side
        for c in range(last_open_col + 1, cols):
            matrix[r][c] = 0
        portals.append({"axis": "horizontal", "row": r,
                        "left": (0, r), "right": (cols - 1, r)})

    # Vertical portals: top edge ↔ bottom edge
    v_candidates = [c for c in range(1, last_open_col + 1)
                    if matrix[1][c] == 0 and matrix[last_open_row][c] == 0]
    random.shuffle(v_candidates)
    for c in v_candidates[:PORTALS_PER_AXIS]:
        # Clear top boundary wall
        matrix[0][c] = 0
        # Clear all padding rows on the bottom side
        for r in range(last_open_row + 1, rows):
            matrix[r][c] = 0
        portals.append({"axis": "vertical", "col": c,
                        "top": (c, 0), "bottom": (c, rows - 1)})

    return portals


# ---------------------------------------------------------------------------
# Pacman mode: loop generation
# ---------------------------------------------------------------------------

def _add_loops(matrix, cols, rows):
    """Remove internal walls to create circular loops for evasion.

    A perfect maze has no cycles — every path between two cells is unique.
    For Pacman mode, the player needs alternate routes to evade the AI.
    This function creates loops by removing "bridge" walls that separate
    two already-connected corridor cells.

    Only walls that have open cells on BOTH sides (horizontally or
    vertically) are eligible. Removing such a wall creates a shortcut
    between two parts of the maze that were previously connected only
    via a longer path — i.e., a loop.

    The PACMAN_LOOP_REMOVAL_RATIO controls what fraction of eligible
    walls are removed. Higher = more loops = easier evasion.

    Args:
        matrix: Maze matrix (modified in-place).
        cols, rows: Grid dimensions.
    """
    removable = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if matrix[r][c] != 1:
                continue
            # Check if this wall is a horizontal bridge (open left AND right)
            if matrix[r][c - 1] == 0 and matrix[r][c + 1] == 0:
                removable.append((c, r))
            # Check if this wall is a vertical bridge (open above AND below)
            elif matrix[r - 1][c] == 0 and matrix[r + 1][c] == 0:
                removable.append((c, r))

    random.shuffle(removable)
    num_to_remove = max(1, int(len(removable) * PACMAN_LOOP_REMOVAL_RATIO))
    for c, r in removable[:num_to_remove]:
        matrix[r][c] = 0
