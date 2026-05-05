"""
HUD (Heads-Up Display) elements: timer bars and countdown text.

Used by both Challenger mode (countdown to failure) and Pacman mode
(countdown to survival victory). The same draw_timer function serves
both — the label parameter distinguishes them visually.
"""

import pygame
from config.theme import TIMER_BAR_HEIGHT, TIMER_MARGIN, TIMER_BG
from assets.fonts import font_manager


def draw_timer(surface, time_left, time_total, label=None):
    """Draw a horizontal countdown bar at the top of the screen.

    The bar fills from left to right proportional to remaining time.
    Color transitions smoothly:
        - Green when > 50% time remains
        - Gradual shift through yellow
        - Red when < 50% time remains

    Below the bar, text shows the remaining seconds and optional label.

    Gracefully handles time_total=0 (no division by zero).

    Args:
        surface: Target surface.
        time_left: Remaining time in seconds.
        time_total: Total time for this level in seconds.
        label: Optional prefix text (e.g., "Survive" for Pacman mode).
    """
    w = surface.get_width()
    # Guard against division by zero (e.g., non-timed mode calling this)
    fill_ratio = max(0.0, time_left / time_total) if time_total > 0 else 0.0

    # Color gradient: green → yellow → red as time decreases
    if fill_ratio > 0.5:
        # More than half: green with increasing red component
        color = (int(255 * (1 - fill_ratio) * 2), 220, 50)
    else:
        # Less than half: red with decreasing green component
        color = (255, int(220 * fill_ratio * 2), 50)

    # Background bar (dark gray, full width)
    bar_w = w - TIMER_MARGIN * 2
    pygame.draw.rect(surface, TIMER_BG,
                     (TIMER_MARGIN, 8, bar_w, TIMER_BAR_HEIGHT), border_radius=3)

    # Fill bar (colored, proportional to remaining time)
    fill_w = max(0, int(bar_w * fill_ratio))
    if fill_w > 0:
        pygame.draw.rect(surface, color,
                         (TIMER_MARGIN, 8, fill_w, TIMER_BAR_HEIGHT), border_radius=3)

    # Text: "12s" or "Survive: 25s"
    secs = max(0, int(time_left) + 1)
    display = f"{label}: {secs}s" if label else f"{secs}s"
    text = font_manager.small.render(display, True, color)
    surface.blit(text, (w // 2 - text.get_width() // 2, 16))
