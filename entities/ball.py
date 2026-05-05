"""
Ball entity: pure data with minimal self-management.

A Ball stores its grid position, start position, color, radii, and
collision state. It does NOT contain movement logic (see systems/physics.py)
or rendering logic (see rendering/ball_renderer.py).

This separation means the same Ball data structure works across all game
types (Classic, Infinite, Pacman) without modification. Different game
types use different systems to move the ball.

Uses __slots__ for memory efficiency — no per-instance __dict__.
"""

from config.settings import BALL_RADIUS, COLLISION_RADIUS


class Ball:
    """A single ball on the maze grid.

    Attributes:
        gx, gy: Current grid position (center of ball). Floats.
        start_gx, start_gy: Initial position, used by reset().
        color: RGB tuple for rendering.
        radius: Visual radius (0.5 = fills one corridor cell).
        collision_radius: Physics radius (0.4 = slightly smaller for
            corridor tolerance — see systems/physics.py for why).
        bumped: True if a wall blocked movement THIS frame.
        _was_bumped: True if bumped on the PREVIOUS frame.
    """

    __slots__ = (
        "gx", "gy", "start_gx", "start_gy",
        "color", "radius", "collision_radius",
        "bumped", "_was_bumped",
    )

    def __init__(self, gx, gy, color):
        self.gx = float(gx)
        self.gy = float(gy)
        self.start_gx = float(gx)
        self.start_gy = float(gy)
        self.color = color
        self.radius = BALL_RADIUS
        self.collision_radius = COLLISION_RADIUS
        self.bumped = False
        self._was_bumped = False

    @property
    def just_bumped(self):
        """True only on the FIRST frame of a wall collision.

        Used to trigger the bump sound once per collision, not every
        frame while held against a wall. Requires systems/physics.py
        to update _was_bumped before setting bumped each frame.
        """
        return self.bumped and not self._was_bumped

    def reset(self):
        """Snap back to starting position and clear collision state.

        Called when the player presses R to restart the current puzzle.
        """
        self.gx = self.start_gx
        self.gy = self.start_gy
        self.bumped = False
        self._was_bumped = False
