"""
Input system: converts key state into a movement vector.

Stateless function. Called once per physics step with the current key
state and returns a (dx, dy) displacement in grid units. The displacement
is scaled by PLAYER_SPEED * dt for frame-rate independence.

Having input reading in its own module means:
    - The same function is used by all game types
    - Future input methods (gamepad, touch) can be added here
    - Easy to mock in tests
"""

import pygame
from config.settings import PLAYER_SPEED


def get_movement(keys, dt):
    """Read WASD key state and return (dx, dy) grid-unit displacement.

    Diagonal movement is allowed — pressing W+D returns both a negative
    dy and positive dx. Each axis is independent (no speed normalization
    for diagonals — intentional, matches the original game feel).

    Args:
        keys: Result of pygame.key.get_pressed() (bool array).
        dt: Fixed timestep in seconds (typically 1/60).

    Returns:
        Tuple (dx, dy) in grid units. Zero if no keys pressed.
    """
    displacement = PLAYER_SPEED * dt
    dx, dy = 0.0, 0.0
    if keys[pygame.K_w]:
        dy -= displacement
    if keys[pygame.K_s]:
        dy += displacement
    if keys[pygame.K_a]:
        dx -= displacement
    if keys[pygame.K_d]:
        dx += displacement
    return dx, dy
