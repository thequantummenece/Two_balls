"""
Generic reusable menu state.

A single MenuState class handles ALL menu screens in the game: game type,
play mode, and difficulty. The only differences are the options list, colors,
subtitle text, and the on_select callback.

This eliminates the need for separate GameTypeMenu, PlayModeMenu, and
DifficultyMenu classes that would share 95% of their code.

Usage:
    MenuState(app, ["easy", "normal", "hard"], DIFFICULTY_COLORS,
              "Select Difficulty", on_difficulty_chosen, default_index=1,
              back_state=lambda: TitleState(app))
"""

import pygame
from core.state_machine import State
from assets.sounds import sound_manager
from rendering.menu_renderer import draw_menu_screen


class MenuState(State):
    """Reusable vertical option menu with keyboard navigation.

    The user navigates with W/S (or Up/Down arrows), confirms with Enter,
    and optionally goes back with ESC.

    Args:
        app: Application instance.
        options: List of option strings (e.g., ["classic", "challenger"]).
        colors: Dict mapping each option string to its RGB display color.
        subtitle: Text shown above the options (e.g., "Select Game Type").
        on_select: Callback function(choice_string) called on Enter.
        default_index: Which option is highlighted by default (0-indexed).
        back_state: Optional callable() → State for ESC. If None, ESC
            does nothing.
    """

    def __init__(self, app, options, colors, subtitle, on_select,
                 default_index=0, back_state=None):
        super().__init__(app)
        self.options = options
        self.colors = colors
        self.subtitle = subtitle
        self.on_select = on_select
        self.index = default_index
        # back_state is a factory (callable) not a state instance, because
        # states are mutable and we want a fresh one each time ESC is pressed.
        self.back_state = back_state

    def handle_event(self, event):
        """Handle menu navigation: W/S to move, Enter to confirm, ESC to go back."""
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_w, pygame.K_UP):
            sound_manager.play("nav")
            self.index = (self.index - 1) % len(self.options)
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            sound_manager.play("nav")
            self.index = (self.index + 1) % len(self.options)
        elif event.key == pygame.K_RETURN:
            sound_manager.play("select")
            # Call the callback with the selected option string.
            # The callback is responsible for transitioning to the next state.
            self.on_select(self.options[self.index])
        elif event.key == pygame.K_ESCAPE and self.back_state:
            sound_manager.play("nav")
            # back_state is a factory — call it to get a fresh State instance
            self.app.state_machine.change(self.back_state())

    def update(self, dt):
        """Update floating bubbles for the animated menu background."""
        self.app.bubbles.update(self.app.tick)

    def draw(self, surface, tick):
        """Render the complete menu screen: title + option list + bubbles."""
        draw_menu_screen(surface, self.options, self.colors,
                         self.index, self.subtitle, tick)
        self.app.bubbles.draw(surface)
