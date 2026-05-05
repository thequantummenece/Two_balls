"""
Generic state machine for managing application screens.

The game uses a state machine pattern where each screen (title, menu,
gameplay) is a State object. Only one state is active at a time. The
StateMachine forwards events, updates, and draw calls to the current state
and handles transitions with proper enter/exit lifecycle hooks.

This module is game-agnostic — it could be reused in any pygame project.
"""

from abc import ABC, abstractmethod


class State(ABC):
    """Abstract base class for all application states (screens).

    Each state receives an `app` reference to access shared resources
    (screen, clock, bubbles, selected options). States implement:
        - handle_event: process a single pygame event
        - update: per-fixed-timestep game logic
        - draw: render the current frame (pure rendering, no state changes)

    Optional hooks:
        - enter: called when this state becomes active (setup)
        - exit: called when leaving this state (cleanup)
    """

    def __init__(self, app):
        self.app = app

    def enter(self):
        """Called once when this state becomes the active state.
        Override to perform setup like generating a level."""

    def exit(self):
        """Called once when leaving this state.
        Override to perform cleanup like stopping sounds."""

    @abstractmethod
    def handle_event(self, event):
        """Process a single pygame event (keydown, resize, etc.)."""
        ...

    @abstractmethod
    def update(self, dt):
        """Run one fixed-timestep update. dt is always FIXED_DT seconds."""
        ...

    @abstractmethod
    def draw(self, surface, tick):
        """Render the current frame. tick is a monotonic frame counter
        used for animations. Must not mutate game state."""
        ...


class StateMachine:
    """Manages state transitions and forwards the game loop calls.

    Usage:
        sm = StateMachine()
        sm.change(TitleState(app))   # enter TitleState
        sm.handle_event(event)       # forwarded to TitleState
        sm.update(dt)                # forwarded to TitleState
        sm.draw(surface, tick)       # forwarded to TitleState
        sm.change(MenuState(app))    # exit TitleState, enter MenuState
    """

    def __init__(self):
        self._current = None

    @property
    def current(self):
        """The currently active state, or None."""
        return self._current

    def change(self, new_state):
        """Transition to a new state. Calls exit() on old, enter() on new."""
        if self._current is not None:
            self._current.exit()
        self._current = new_state
        if self._current is not None:
            self._current.enter()

    def handle_event(self, event):
        """Forward a pygame event to the current state."""
        if self._current:
            self._current.handle_event(event)

    def update(self, dt):
        """Forward a fixed-timestep update to the current state."""
        if self._current:
            self._current.update(dt)

    def draw(self, surface, tick):
        """Forward the draw call to the current state."""
        if self._current:
            self._current.draw(surface, tick)
