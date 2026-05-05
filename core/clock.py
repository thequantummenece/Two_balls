"""
Fixed-timestep accumulator for deterministic physics.

Instead of using variable dt (which makes physics framerate-dependent),
this accumulator collects real elapsed time and yields fixed-size steps.
If the game drops to 30fps, it runs 2 physics steps per render frame.
If it's at 60fps, it runs 1 step. Physics is always deterministic.

Usage:
    ts = FixedTimestep()
    real_dt = clock.tick(60) / 1000.0
    ts.accumulate(real_dt)
    for dt in ts.steps():
        game.update(dt)  # dt is always exactly FIXED_DT
"""

from config.settings import FIXED_DT


class FixedTimestep:
    """Accumulates real time and yields fixed-size dt steps.

    Args:
        dt: The fixed timestep size in seconds. Defaults to FIXED_DT (1/60).
    """

    def __init__(self, dt=FIXED_DT):
        self.dt = dt
        self._accumulator = 0.0

    def reset(self):
        """Clear accumulated time. Call when re-entering gameplay."""
        self._accumulator = 0.0

    def accumulate(self, real_dt):
        """Add real elapsed time (seconds) from pygame.clock.tick().

        Call this once per render frame before iterating steps().
        """
        self._accumulator += real_dt

    def steps(self):
        """Yield one fixed dt per physics step that should run this frame.

        If real time elapsed is 0.033s and dt is 0.0167s, yields twice.
        If real time is 0.010s, yields nothing (accumulates for next frame).
        """
        while self._accumulator >= self.dt:
            yield self.dt
            self._accumulator -= self.dt
