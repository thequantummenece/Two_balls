"""
Core rendering utilities: screen clearing, overlays, and coordinate scaling.

These are the low-level primitives used by all other renderers. No
game-specific knowledge — just surfaces, colors, and math.
"""

import pygame
from config.theme import BLACK, GAME_BG

# Cached overlay surface. Recreated only when screen size changes,
# avoiding a full-screen RGBA surface allocation every frame (~1.9MB
# at 800×600). The cache key is the surface dimensions.
_overlay_cache = {"size": (0, 0), "surface": None}


def clear(surface):
    """Fill the entire surface with black. Used as the first step of every frame."""
    surface.fill(BLACK)


def draw_overlay(surface, alpha=160):
    """Draw a semi-transparent dark overlay over the entire surface.

    Used for dimming the game behind win/fail prompts. The overlay surface
    is cached and only reallocated when the screen size changes.

    Args:
        surface: The target pygame surface to darken.
        alpha: Transparency (0=invisible, 255=solid black). Default 160.
    """
    size = surface.get_size()
    if _overlay_cache["size"] != size or _overlay_cache["surface"] is None:
        _overlay_cache["surface"] = pygame.Surface(size, pygame.SRCALPHA)
        _overlay_cache["size"] = size
    _overlay_cache["surface"].fill((0, 0, 0, alpha))
    surface.blit(_overlay_cache["surface"], (0, 0))


def draw_game_bg(surface, cols, rows, cell_size, ox, oy):
    """Fill the game area rectangle with GAME_BG color (white).

    Only fills the grid area, not the full screen. The black letterbox
    bars (from clear()) remain visible on the sides if the window aspect
    ratio doesn't match the grid.

    Args:
        surface: Target surface.
        cols, rows: Grid dimensions.
        cell_size: Pixel size of one grid cell.
        ox, oy: Pixel offsets for centering the grid.
    """
    rect = pygame.Rect(int(ox), int(oy), int(cols * cell_size), int(rows * cell_size))
    pygame.draw.rect(surface, GAME_BG, rect)


def get_scaling(cols, rows, screen_w, screen_h):
    """Compute cell size and centering offsets for the current screen.

    Uses min(width_ratio, height_ratio) to ensure cells are always
    square. The grid is centered in the window with equal offsets.

    Args:
        cols, rows: Grid dimensions.
        screen_w, screen_h: Current window size in pixels.

    Returns:
        (cell_size, offset_x, offset_y) — all in pixels.
    """
    cell_size = min(screen_w / cols, screen_h / rows)
    offset_x = (screen_w - cols * cell_size) / 2
    offset_y = (screen_h - rows * cell_size) / 2
    return cell_size, offset_x, offset_y
