"""
Two Balls - Entry Point

This is the sole entry point for the application. All initialization,
game loop management, and state control is delegated to core.app.App.
Keeping main.py minimal ensures the project can be imported as a library
without triggering side effects.
"""

from core.app import App

if __name__ == "__main__":
    App().run()
