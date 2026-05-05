"""
AI system: BFS pathfinding and AI ball movement for Pacman mode.

The AI chases the player using breadth-first search on the maze matrix.
BFS guarantees the shortest path. The path is recalculated every
PACMAN_REPATH_INTERVAL frames (~6 times/second) to adapt to player movement
without being too CPU-intensive.

Key design decisions:
    - Parent-pointer BFS (O(n) memory) instead of path-copy BFS (O(n²))
    - Returns a deque so popleft() is O(1) as cells are consumed
    - AI speed scales per difficulty, up to 105% of player on Extreme
"""

import math
from collections import deque


def bfs_path(matrix, start, end, cols, rows):
    """Find the shortest path between two cells using BFS.

    Uses parent pointers to reconstruct the path at the end, avoiding
    the O(n²) memory cost of copying the full path at each BFS node.

    Args:
        matrix: 2D list where 0 = open, 1 = wall.
        start: (col, row) tuple — starting cell.
        end: (col, row) tuple — target cell.
        cols, rows: Grid dimensions for bounds checking.

    Returns:
        deque of (col, row) tuples from start to end (inclusive).
        Returns deque([start]) if no path exists or start == end.
    """
    if start == end:
        return deque([start])

    # BFS with parent tracking for O(n) path reconstruction
    parent = {start: None}
    queue = deque([start])

    while queue:
        cx, cy = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (cx + dx, cy + dy)
            if (nb not in parent
                    and 0 <= nb[0] < cols and 0 <= nb[1] < rows
                    and matrix[nb[1]][nb[0]] == 0):
                parent[nb] = (cx, cy)
                if nb == end:
                    # Reconstruct path by walking parent pointers backward
                    path = deque()
                    node = nb
                    while node is not None:
                        path.appendleft(node)
                        node = parent[node]
                    return path
                queue.append(nb)

    # No path found — return start position (AI stays put)
    return deque([start])


def move_ai_toward(ball, path, ai_speed, dt, walls):
    """Move an AI-controlled ball toward the next cell in its BFS path.

    The AI moves in a straight line toward the center of the next cell
    in the path. When it gets close enough (<0.05 grid units), it pops
    that cell and targets the next one.

    Movement uses the same physics system (move_ball) as the player,
    so the AI obeys the same wall collision rules — it can't cheat
    through walls.

    Args:
        ball: The AI-controlled Ball entity.
        path: deque of (col, row) cells. Modified in-place (popleft).
        ai_speed: AI movement speed in grid units/second.
        dt: Fixed timestep in seconds.
        walls: List of wall tuples for collision checking.
    """
    from systems.physics import move_ball

    if len(path) < 2:
        return  # At destination or no path

    # Target the center of the next cell in the path
    next_cell = path[1]
    tx = next_cell[0] + 0.5
    ty = next_cell[1] + 0.5

    dx = tx - ball.gx
    dy = ty - ball.gy
    dist = math.hypot(dx, dy)

    if dist < 0.05:
        # Close enough — pop this cell and move to the next target
        path.popleft()
        return

    # Move toward target at ai_speed, capped at the remaining distance
    # to prevent overshooting. ratio = min(1.0, step/dist) normalizes
    # the direction vector and scales it by the step size.
    step = min(ai_speed * dt / dist, 1.0)
    move_ball(ball, dx * step, dy * step, walls)
