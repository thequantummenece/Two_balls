"""
Overlay prompts and special screens drawn on top of gameplay.

All overlays use a dark semi-transparent background to dim the game,
then render text and options on top. The draw_prompt() function is the
generic base — win, timeout, and caught prompts are thin wrappers with
different header text and colors.

Also includes the story completion screen and the level select grid.
"""

import math
import pygame
from config.settings import STORY_LEVELS, LEVEL_GRID_COLS
from config.theme import GREEN, DIM_GRAY, LEVEL_CELL_MAX_W, LEVEL_CELL_MAX_H
from rendering.renderer import draw_overlay, clear
from rendering.menu_renderer import wave_color, draw_animated_title
from assets.fonts import font_manager

# Computed once from constants — 50 levels / 10 columns = 5 rows
LEVEL_GRID_ROWS = (STORY_LEVELS + LEVEL_GRID_COLS - 1) // LEVEL_GRID_COLS


def draw_prompt(surface, header, header_color, options, selected, tick):
    """Generic overlay prompt with a colored header and selectable options.

    Draws a dark overlay, the header text with wave coloring, and a
    vertical list of options where the selected one bounces.

    Used as the base for win/timeout/caught prompts — each just passes
    different header text and color.

    Args:
        surface: Target surface (game is already drawn underneath).
        header: Text shown at the top of the prompt (e.g., "Puzzle Complete!").
        header_color: RGB base color for the header wave animation.
        options: List of option strings (e.g., ["Keep Going", "Back to Menu"]).
        selected: Index of the currently highlighted option.
        tick: Frame counter for animation.
    """
    w, h = surface.get_size()
    draw_overlay(surface)

    # Animated header
    color = wave_color(header_color, tick, intensity=40)
    text = font_manager.font.render(header, True, color)
    surface.blit(text, (w // 2 - text.get_width() // 2, h // 2 - 80))

    # Selectable options
    for i, opt in enumerate(options):
        y = h // 2 + i * 50
        if i == selected:
            bounce = int(math.sin(tick * 0.1) * 2)
            label = "> " + opt + " <"
            text = font_manager.font.render(label, True, (255, 255, 255))
            surface.blit(text, (w // 2 - text.get_width() // 2, y + bounce))
        else:
            text = font_manager.small.render(opt, True, (160, 160, 160))
            surface.blit(text, (w // 2 - text.get_width() // 2, y))


def draw_win_prompt(surface, options, selected, header, tick):
    """Win overlay: green header, called after puzzle completion."""
    draw_prompt(surface, header, GREEN, options, selected, tick)


def draw_timeout_prompt(surface, options, selected, tick):
    """Timeout overlay: red header, shown when challenger timer expires."""
    draw_prompt(surface, "Time's Up!", (255, 80, 80), options, selected, tick)


def draw_caught_prompt(surface, options, selected, tick):
    """Caught overlay: red header, shown when AI catches player in Pacman."""
    draw_prompt(surface, "Caught!", (255, 50, 50), options, selected, tick)


def draw_story_complete(surface, tick):
    """Story completion celebration screen.

    Shown when the player finishes all 50 story levels. Features a
    gold-colored "Congratulations!" title, green subtitle, and a
    pulsing "Press ENTER" hint.

    Args:
        surface: Target surface.
        tick: Frame counter.
    """
    w, h = surface.get_size()
    draw_overlay(surface, alpha=180)

    # Gold title with wave animation
    color = wave_color((255, 220, 50), tick, intensity=50)
    text = font_manager.title.render("Congratulations!", True, color)
    surface.blit(text, (w // 2 - text.get_width() // 2, h // 2 - 60))

    # Green subtitle
    sub = font_manager.font.render("All 50 puzzles complete!", True, GREEN)
    surface.blit(sub, (w // 2 - sub.get_width() // 2, h // 2 + 10))

    # Pulsing hint
    alpha = int(160 + 80 * math.sin(tick * 0.06))
    hint = font_manager.small.render("Press ENTER to return to levels",
                                     True, (alpha, alpha, alpha))
    surface.blit(hint, (w // 2 - hint.get_width() // 2, h // 2 + 70))


def draw_level_select(surface, selected, tick):
    """Story mode level selection grid (10 columns × 5 rows).

    Displays level numbers 1-50 in a grid. The selected level gets:
        - Larger font
        - Wave-colored text
        - A bouncing selection box
        - Vertical bounce animation

    Cell sizes are capped at LEVEL_CELL_MAX_W/H and the grid is
    centered horizontally.

    Args:
        surface: Target surface.
        selected: 0-indexed level number that's currently highlighted.
        tick: Frame counter for animation.
    """
    w, h = surface.get_size()
    clear(surface)

    # Animated game title at the top
    title_bottom = draw_animated_title(surface, tick)

    # "Select Level" subtitle
    sub = font_manager.small.render("Select Level", True, (160, 160, 160))
    surface.blit(sub, (w // 2 - sub.get_width() // 2, title_bottom + 20))

    # Compute grid layout — cells are capped in size and the grid is centered
    grid_top = title_bottom + 60
    cell_w = min(LEVEL_CELL_MAX_W, (w - 80) // LEVEL_GRID_COLS)
    cell_h = min(LEVEL_CELL_MAX_H, (h - grid_top - 80) // LEVEL_GRID_ROWS)
    grid_w = LEVEL_GRID_COLS * cell_w
    grid_x = w // 2 - grid_w // 2

    # Draw each level number
    for i in range(STORY_LEVELS):
        col = i % LEVEL_GRID_COLS
        row = i // LEVEL_GRID_COLS
        cx = grid_x + col * cell_w + cell_w // 2  # Cell center X
        cy = grid_top + row * cell_h + cell_h // 2  # Cell center Y

        if i == selected:
            # Selected: larger text, wave color, bounce, selection box
            bounce = int(math.sin(tick * 0.1) * 2)
            color = wave_color((100, 220, 255), tick, intensity=50)
            text = font_manager.font.render(str(i + 1), True, color)
            surface.blit(text, (cx - text.get_width() // 2,
                                cy - text.get_height() // 2 + bounce))
            # Selection box around the cell
            box = pygame.Rect(cx - cell_w // 2 + 4, cy - cell_h // 2 + 4 + bounce,
                              cell_w - 8, cell_h - 8)
            pygame.draw.rect(surface, color, box, 2, border_radius=4)
        else:
            # Unselected: small font, dim gray
            text = font_manager.small.render(str(i + 1), True, DIM_GRAY)
            surface.blit(text, (cx - text.get_width() // 2,
                                cy - text.get_height() // 2))

    # Pulsing navigation hint at the bottom
    alpha = int(140 + 80 * math.sin(tick * 0.04))
    hint = font_manager.small.render("WASD to navigate  |  ENTER to play  |  ESC back",
                                     True, (alpha, alpha, alpha))
    surface.blit(hint, (w // 2 - hint.get_width() // 2, h - 60))
