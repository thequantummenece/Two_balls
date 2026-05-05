"""
Collision detection system: AABB overlap and ball distance checks.

All functions are stateless — they take data, return a boolean, and have
no side effects. This module is used by:
    - systems/physics.py (wall collision during movement)
    - states/playing.py (win condition checks)
"""


def aabb_collide(ax, ay, aw, ah, bx, by, bw, bh):
    """Return True if two axis-aligned bounding boxes overlap.

    Uses strict inequality (< and >) so boxes that merely touch edges
    do NOT count as colliding. This is critical for the corridor tolerance
    system: a ball with collision_radius 0.4 in a 1.0-wide corridor has
    its AABB edge exactly at the wall boundary — strict inequality means
    no collision, allowing it to fit.

    Args:
        ax, ay, aw, ah: First box (x, y, width, height).
        bx, by, bw, bh: Second box.
    """
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def balls_touch(a, b, use_collision_radius=False):
    """Return True if two balls overlap (distance ≤ sum of radii).

    By default uses visual radius (for win condition — balls connect when
    they visually overlap). Set use_collision_radius=True for Pacman mode's
    fairer catch detection (AI must physically reach you, not just look close).

    Uses squared distance to avoid expensive sqrt.
    """
    r_attr = "collision_radius" if use_collision_radius else "radius"
    r_sum = getattr(a, r_attr) + getattr(b, r_attr)
    dx = a.gx - b.gx
    dy = a.gy - b.gy
    return dx * dx + dy * dy <= r_sum * r_sum


def balls_touch_toroidal(a, b, cols, rows):
    """Return True if two balls overlap with toroidal (wrapping) distance.

    In Infinite mode, a ball at x=0.5 and another at x=cols-0.5 are
    actually only 1 unit apart through the wrap, not (cols-1) units.
    This function checks the minimum of direct distance and wrapped distance
    on each axis.

    Args:
        a, b: Ball entities.
        cols, rows: Grid dimensions for wrap calculation.
    """
    dx = abs(a.gx - b.gx)
    dy = abs(a.gy - b.gy)
    # Take the shorter path: direct or wrapped around
    dx = min(dx, cols - dx)
    dy = min(dy, rows - dy)
    r_sum = a.radius + b.radius
    return dx * dx + dy * dy <= r_sum * r_sum
