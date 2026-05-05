"""
Maze wall rendering.

Draws wall tuples as dark rounded rectangles. Each wall is stored as
(gx, gy, gw, gh) in grid units and converted to pixels at draw time
using cell_size and offsets. The WALL_INSET creates a thin visual gap
between adjacent wall blocks, making corridors appear cleaner.
"""

import pygame
from config.theme import WALL_COLOR, WALL_INSET, WALL_BORDER_RADIUS


def draw_walls(surface, walls, cell_size, offset_x, offset_y):
    """Draw all maze walls scaled to pixel coordinates.

    Each wall block is inset by WALL_INSET pixels on each side, making
    it slightly smaller than the full cell. This creates visible gaps
    between adjacent walls and gives the maze a thinner, cleaner look.
    border_radius rounds the corners.

    The max(1, ...) on width/height prevents zero-size rects on very
    small windows where cell_size * gw < 2 * inset.

    Args:
        surface: Target pygame surface.
        walls: List of (gx, gy, gw, gh) tuples in grid units.
        cell_size: Pixels per grid unit.
        offset_x, offset_y: Pixel offsets for grid centering.
    """
    inset = WALL_INSET
    for gx, gy, gw, gh in walls:
        px = int(offset_x + gx * cell_size) + inset
        py = int(offset_y + gy * cell_size) + inset
        pw = max(int(gw * cell_size) - inset * 2, 1)
        ph = max(int(gh * cell_size) - inset * 2, 1)
        pygame.draw.rect(surface, WALL_COLOR, (px, py, pw, ph),
                         border_radius=WALL_BORDER_RADIUS)
