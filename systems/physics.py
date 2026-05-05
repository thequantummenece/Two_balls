"""
Physics system: ball movement with collision detection and wrapping.

Stateless functions that operate on Ball entities and wall data.
The same move_ball() is used for:
    - Player-controlled balls in Classic/Challenger
    - Both balls in Infinite mode (followed by wrap_ball)
    - AI-controlled blue ball in Pacman mode
"""

from systems.collision import aabb_collide


def move_ball(ball, dx, dy, walls):
    """Move a ball by (dx, dy) with axis-separated wall collision.

    Tests X movement first (with current Y), then Y movement (with
    potentially updated X). This axis separation allows wall-sliding:
    a ball blocked on one axis can still move on the other.

    Side effects:
        - Updates ball.gx and/or ball.gy if movement is valid
        - Sets ball.bumped = True if either axis was blocked
        - Saves previous bumped state to ball._was_bumped (for just_bumped)

    The collision check uses ball.collision_radius (0.4), which is smaller
    than the visual radius (0.5). This 0.1-unit tolerance per side allows
    the ball to turn into perpendicular corridors without needing to be
    perfectly centered. The max single-frame displacement (0.08 at 60fps)
    is less than the tolerance, so the ball can always enter corridors.

    Args:
        ball: Ball entity to move.
        dx, dy: Desired displacement in grid units.
        walls: List of (gx, gy, gw, gh) wall tuples.
    """
    # Save previous bump state for just_bumped edge detection
    ball._was_bumped = ball.bumped
    ball.bumped = False
    r = ball.collision_radius

    # Test X axis: compute new AABB at proposed X, check against all walls
    if dx != 0:
        nx = ball.gx + dx
        bx, by, bw, bh = nx - r, ball.gy - r, r * 2, r * 2
        if not any(aabb_collide(bx, by, bw, bh, *w) for w in walls):
            ball.gx = nx
        else:
            ball.bumped = True

    # Test Y axis: uses updated X (allows sliding along walls)
    if dy != 0:
        ny = ball.gy + dy
        bx, by, bw, bh = ball.gx - r, ny - r, r * 2, r * 2
        if not any(aabb_collide(bx, by, bw, bh, *w) for w in walls):
            ball.gy = ny
        else:
            ball.bumped = True


def wrap_ball(ball, cols, rows):
    """Wrap ball position for pac-man style toroidal movement.

    Called after move_ball() in Infinite mode. If the ball has moved past
    a grid edge (through a removed boundary wall), wraps it to the
    opposite side. Only triggers at actual portal openings because intact
    boundary walls prevent the ball from reaching the edge elsewhere.

    Args:
        ball: Ball entity to wrap.
        cols, rows: Grid dimensions for wrap bounds.
    """
    if ball.gx < 0:
        ball.gx += cols
    elif ball.gx >= cols:
        ball.gx -= cols
    if ball.gy < 0:
        ball.gy += rows
    elif ball.gy >= rows:
        ball.gy -= rows
