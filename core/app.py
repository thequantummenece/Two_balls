"""
Application lifecycle: initialization, main loop, and shutdown.

App is the top-level object that owns:
    - The pygame window (screen)
    - The game clock and fixed-timestep accumulator
    - The state machine that controls which screen is active
    - Shared resources (bubbles for menu backgrounds)
    - User selections (game type, play mode, difficulty) that menu states
      write and the PlayingState reads

The main loop follows the strict event → update → draw separation:
    1. _process_events: pump pygame events, forward to current state
    2. _update: run fixed-timestep physics steps
    3. _draw: render current state to screen, flip display
"""

import pygame
import sys
from config.settings import DEFAULT_WIDTH, DEFAULT_HEIGHT, FPS
from core.state_machine import StateMachine
from core.clock import FixedTimestep
from assets.fonts import font_manager
from assets.sounds import sound_manager
from components.particles import FloatingBubbles


class App:
    """Top-level application. Creates the window, initializes assets,
    and runs the main game loop.

    Attributes:
        screen: The pygame display surface (resizable).
        clock: pygame.time.Clock for framerate management.
        timestep: FixedTimestep accumulator for deterministic physics.
        state_machine: Controls which State is active.
        tick: Monotonic frame counter for animations.
        bubbles: FloatingBubbles instance shared by all menu states.
        selected_game_type: Set by menu states ("classic", "challenger", etc.)
        selected_play_mode: Set by menu states ("arcade", "story")
        selected_difficulty: Set by menu states ("easy", "normal", etc.)
    """

    def __init__(self):
        # Initialize pygame subsystems. Order matters:
        # 1. pygame.init() must come first (initializes video, events, etc.)
        # 2. mixer.init() with explicit params before generating sounds
        # 3. Font and sound managers after their respective subsystems
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        self.screen = pygame.display.set_mode(
            (DEFAULT_WIDTH, DEFAULT_HEIGHT), pygame.RESIZABLE
        )
        pygame.display.set_caption("Two Balls")
        font_manager.init()
        sound_manager.init()

        self.clock = pygame.time.Clock()
        self.timestep = FixedTimestep()
        self.state_machine = StateMachine()
        self.tick = 0

        # Floating bubbles are shared across all menu states so they
        # persist smoothly when transitioning between menus.
        self.bubbles = FloatingBubbles(DEFAULT_WIDTH, DEFAULT_HEIGHT)

        # User selections — written by MenuState callbacks, read by PlayingState.
        # This avoids passing selections through constructor chains.
        self.selected_game_type = None
        self.selected_play_mode = None
        self.selected_difficulty = None

    def run(self):
        """Start the game. Enters TitleState and runs until quit.

        The import is deferred to avoid circular imports (TitleState
        imports MenuState which imports PlayingState which imports systems
        which import config — all fine at call time, not at import time).
        """
        from states.title import TitleState
        self.state_machine.change(TitleState(self))

        while True:
            self._process_events()
            self._update()
            self._draw()
            pygame.display.flip()
            self.tick += 1

    def _process_events(self):
        """Pump all pygame events and forward them to the current state.

        QUIT is handled here (not in states) because it's universal.
        VIDEORESIZE updates the bubbles so they respawn at the right size.
        All other events go to the state machine.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                self.bubbles.resize(event.w, event.h)
            self.state_machine.handle_event(event)

    def _update(self):
        """Run fixed-timestep physics updates.

        real_dt is the actual elapsed time since last frame. The timestep
        accumulator converts this into N fixed-size steps, ensuring physics
        runs at exactly 60Hz regardless of render framerate.
        """
        real_dt = self.clock.tick(FPS) / 1000.0
        # Re-fetch surface in case window was resized this frame
        self.screen = pygame.display.get_surface()
        self.timestep.accumulate(real_dt)
        for dt in self.timestep.steps():
            self.state_machine.update(dt)

    def _draw(self):
        """Render the current state. Pure output — no game logic here."""
        self.state_machine.draw(self.screen, self.tick)
