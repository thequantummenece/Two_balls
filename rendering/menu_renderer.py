"""
Menu screen rendering: animated title, option lists, title screen.

All menu screens share the same visual language:
    - Wave-colored animated title at the top
    - Vertical option list with bounce/underline on the selected item
    - Pulsing hint text at the bottom

The draw_menu_screen() function composes these into a complete menu screen,
eliminating the need for per-menu draw functions. The title screen has its
own layout with a larger "TWO BALLS" title and different color scheme.
"""

import math
import pygame
from config.theme import (
    PINK, BLUE, SUBTITLE_GRAY,
    MENU_ITEM_OFFSET, MENU_ITEM_SPACING, UNDERLINE_PADDING,
)
from assets.fonts import font_manager
from rendering.renderer import clear

# Cache for font metric widths. Computing sum(font.size(ch) for ch in text)
# is expensive (~18 lookups per frame for the title). We cache results
# keyed by (text, font_attr_name) and compute them only once.
_width_cache = {}


def _cached_width(text, font_attr="title"):
    """Get the total pixel width of `text` using the named font. Cached.

    Args:
        text: The string to measure.
        font_attr: Attribute name on font_manager ("title", "font", "small").

    Returns:
        Total width in pixels, or 0 if fonts aren't initialized yet.
    """
    key = (text, font_attr)
    if key not in _width_cache:
        f = getattr(font_manager, font_attr)
        if f is None:
            return 0
        _width_cache[key] = sum(f.size(ch)[0] for ch in text)
    return _width_cache[key]


def wave_color(base, tick, offset=0, intensity=40):
    """Shift an RGB color's brightness with a sine wave.

    Creates a pulsing/shimmering effect. Each color channel is shifted
    by the same amount, clamped to [0, 255].

    Args:
        base: Base RGB tuple (e.g., (255, 255, 255)).
        tick: Frame counter for animation timing.
        offset: Phase offset — use different values per character for
            a "wave" effect across text.
        intensity: Maximum brightness shift in either direction.

    Returns:
        New RGB tuple with shifted brightness.
    """
    shift = int(math.sin(tick * 0.05 + offset) * intensity)
    return tuple(max(0, min(255, c + shift)) for c in base)


def draw_animated_title(surface, tick, text="Two Balls"):
    """Draw the game title with per-character wave coloring.

    Each character gets a slight phase offset, creating a ripple effect.
    The title bobs vertically with a slow sine wave.

    Args:
        surface: Target surface.
        tick: Frame counter.
        text: Title string to render.

    Returns:
        The Y coordinate of the title's bottom edge (for positioning
        content below it).
    """
    w, h = surface.get_size()
    total_w = _cached_width(text)
    x = w // 2 - total_w // 2
    # Slow vertical bob (±4 pixels)
    y = h // 6 + int(math.sin(tick * 0.03) * 4)
    for i, ch in enumerate(text):
        color = wave_color((255, 255, 255), tick, offset=i * 0.5)
        surf = font_manager.title.render(ch, True, color)
        surface.blit(surf, (x, y))
        x += surf.get_width()
    return y + font_manager.title.get_height()


def draw_option_list(surface, options, colors, selected, subtitle, tick, y_start):
    """Draw a carousel-style rotary list of selectable options.

    The selected option is centered in the available space and rendered large
    with wave color, bounce, and underline. Neighboring options appear above
    and below with decreasing opacity. At most MAX_VISIBLE items are shown,
    giving a rotating wheel feel that works for any number of options.

    Args:
        surface: Target surface.
        options: List of option strings (e.g., ["classic", "challenger"]).
        colors: Dict mapping option → RGB color.
        selected: Index of the currently highlighted option.
        subtitle: Text shown above the options (e.g., "Select Game Type").
        tick: Frame counter for animation.
        y_start: Pixel Y where the subtitle begins.
    """
    w, h = surface.get_size()
    n = len(options)

    # Subtitle
    sub = font_manager.small.render(subtitle, True, SUBTITLE_GRAY)
    surface.blit(sub, (w // 2 - sub.get_width() // 2, y_start))

    # Carousel layout: selected item is centered vertically in available space
    avail_top = y_start + MENU_ITEM_OFFSET
    avail_bottom = h - 80  # room for hint text
    center_y = (avail_top + avail_bottom) // 2

    # How many neighbors to show on each side
    max_visible = 5
    half = max_visible // 2  # 2 above, 2 below

    # Track which original indices we've drawn to avoid duplicates in small lists
    drawn = set()

    for offset in range(-half, half + 1):
        idx = (selected + offset) % n
        if idx in drawn:
            continue
        drawn.add(idx)

        opt = options[idx]
        base_color = colors[opt]
        label = opt.upper()
        abs_off = abs(offset)
        y = center_y + offset * MENU_ITEM_SPACING

        if offset == 0:
            # Selected: larger font, wave color, bounce, underline
            bounce = int(math.sin(tick * 0.1) * 3)
            color = wave_color(base_color, tick, intensity=50)
            label = "> " + label + " <"
            text = font_manager.font.render(label, True, color)
            surface.blit(text, (w // 2 - text.get_width() // 2, y + bounce))
            # Pulsing underline bar
            bar_w = text.get_width() + UNDERLINE_PADDING
            bar_a = int(180 + 60 * math.sin(tick * 0.08))
            bar_c = tuple(max(0, min(255, c * bar_a // 255)) for c in color)
            pygame.draw.rect(surface, bar_c,
                             (w // 2 - bar_w // 2, y + text.get_height() + 2 + bounce, bar_w, 3))
        else:
            # Neighbors: fade out with distance from center
            fade = max(0.15, 1.0 - abs_off * 0.35)
            dim = tuple(max(0, min(255, int(c * fade))) for c in base_color)
            text = font_manager.small.render(label, True, dim)
            surface.blit(text, (w // 2 - text.get_width() // 2, y))

    # Pulsing hint text at the bottom
    alpha = int(140 + 80 * math.sin(tick * 0.04))
    hint = font_manager.small.render(
        "W/S to select  |  ENTER to confirm  |  ESC back",
        True, (alpha, alpha, alpha),
    )
    surface.blit(hint, (w // 2 - hint.get_width() // 2, h - 60))


def draw_title_screen(surface, tick):
    """Draw the opening "TWO BALLS" title screen.

    Different from draw_animated_title — uses pink/blue coloring per word
    ("TWO" in pink, "BALLS" in blue), larger bob, and a pulsing
    "Press ENTER to Start" prompt below.

    Args:
        surface: Target surface.
        tick: Frame counter.
    """
    w, h = surface.get_size()
    clear(surface)

    title_text = "TWO BALLS"
    total_w = _cached_width(title_text)
    x = w // 2 - total_w // 2
    y = h // 3 + int(math.sin(tick * 0.03) * 6)
    for i, ch in enumerate(title_text):
        # Characters 0-3 ("TWO ") are pink, 4-8 ("BALLS") are blue
        base = PINK if i < 4 else BLUE
        color = wave_color(base, tick, offset=i * 0.6, intensity=40)
        surf = font_manager.title.render(ch, True, color)
        surface.blit(surf, (x, y))
        x += surf.get_width()

    # Pulsing "Press ENTER to Start" prompt
    alpha = int(140 + 100 * math.sin(tick * 0.06))
    prompt = font_manager.font.render("Press ENTER to Start", True, (alpha, alpha, alpha))
    surface.blit(prompt, (w // 2 - prompt.get_width() // 2, h * 2 // 3))


def draw_menu_screen(surface, options, colors, selected, subtitle, tick):
    """Draw a complete menu screen: clear + title + option list.

    This is the single function called by MenuState for all three menu
    screens (game type, play mode, difficulty). The only differences are
    the options, colors, and subtitle passed in.

    Args:
        surface: Target surface.
        options: List of option strings.
        colors: Dict mapping option → RGB.
        selected: Currently highlighted index.
        subtitle: Heading text above options.
        tick: Frame counter.
    """
    clear(surface)
    bottom = draw_animated_title(surface, tick)
    draw_option_list(surface, options, colors, selected, subtitle, tick, bottom + 30)
