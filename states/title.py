"""
Title screen state: the "TWO BALLS" opening screen.

This is the first state the player sees. It displays the animated game
title and waits for Enter to begin. On Enter, it transitions through a
chain of MenuStates (game type → play mode → difficulty) via callbacks,
then launches PlayingState.

The callback chain pattern avoids storing intermediate selection state
in this class — each callback creates the next MenuState with the
appropriate on_select callback already bound. The final callback creates
PlayingState with all selections already stored in app.
"""

import pygame
from core.state_machine import State
from assets.sounds import sound_manager
from rendering.menu_renderer import draw_title_screen


class TitleState(State):
    """Displays 'TWO BALLS' title and 'Press ENTER to Start'.

    Transitions:
        Enter → MenuState (game type selection)
    """

    def handle_event(self, event):
        """Only responds to Enter key — starts the selection flow."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            sound_manager.play("select")
            # Begin the menu chain: game type → play mode → difficulty
            from states.menu import MenuState
            from config.settings import GAME_TYPES
            from config.theme import GAME_TYPE_COLORS
            self.app.state_machine.change(
                MenuState(self.app, GAME_TYPES, GAME_TYPE_COLORS,
                          "Select Game Type", self._on_game_type)
            )

    def _on_game_type(self, choice):
        """Callback when user selects a game type (classic/challenger/etc.).

        Stores the selection on app and creates the play mode menu.
        The back_state lambda recreates TitleState for ESC navigation.
        """
        self.app.selected_game_type = choice
        from states.menu import MenuState
        from config.settings import PLAY_MODES
        from config.theme import PLAY_MODE_COLORS
        self.app.state_machine.change(
            MenuState(self.app, PLAY_MODES, PLAY_MODE_COLORS,
                      "Select Game Mode", self._on_play_mode,
                      back_state=lambda: TitleState(self.app))
        )

    def _on_play_mode(self, choice):
        """Callback when user selects a play mode (arcade/story).

        Stores the selection and creates the difficulty menu.
        Default index is 1 (Normal) since it's the most common choice.
        """
        self.app.selected_play_mode = choice
        from states.menu import MenuState
        from config.settings import DIFFICULTIES
        from config.theme import DIFFICULTY_COLORS
        self.app.state_machine.change(
            MenuState(self.app, DIFFICULTIES, DIFFICULTY_COLORS,
                      "Select Difficulty", self._on_difficulty,
                      default_index=1,
                      back_state=lambda: self._restore_play_mode_menu())
        )

    def _restore_play_mode_menu(self):
        """Create a fresh play mode MenuState for ESC from difficulty.

        This is a factory (returns a state) rather than a stored reference
        because MenuState is mutable (tracks cursor position) and we want
        a fresh one each time the player goes back.
        """
        from states.menu import MenuState
        from config.settings import PLAY_MODES
        from config.theme import PLAY_MODE_COLORS
        return MenuState(self.app, PLAY_MODES, PLAY_MODE_COLORS,
                         "Select Game Mode", self._on_play_mode,
                         back_state=lambda: TitleState(self.app))

    def _on_difficulty(self, choice):
        """Callback when user selects difficulty. Launches gameplay."""
        self.app.selected_difficulty = choice
        from states.playing import PlayingState
        self.app.state_machine.change(PlayingState(self.app))

    def update(self, dt):
        """Update floating bubbles for the menu background animation."""
        self.app.bubbles.update(self.app.tick)

    def draw(self, surface, tick):
        """Render the title screen with bubbles on top."""
        draw_title_screen(surface, tick)
        self.app.bubbles.draw(surface)
