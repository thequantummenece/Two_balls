"""
Procedurally generated sound effects.

All sounds are synthesized from sine waves at runtime — no external audio
files needed. Each sound is a short pygame.mixer.Sound created from a
computed sample buffer.

Uses the singleton-instance pattern for the same reason as fonts.py.
Must call sound_manager.init() after pygame.mixer.init().
"""

import array
import math
import pygame


def _wave(freq_func, duration, volume=0.3, sample_rate=22050):
    """Generate a pygame Sound from a frequency function.

    The frequency can vary over time (for sweeps). An envelope with a
    short fade-in/fade-out (0.008s) prevents click artifacts at the
    start and end of each sound.

    Args:
        freq_func: Callable(t) -> Hz, where t ranges from 0.0 to 1.0.
            Constant for tones (lambda t: 440), linear for sweeps
            (lambda t: 400 + 400*t).
        duration: Sound length in seconds.
        volume: Amplitude multiplier (0.0 to 1.0).
        sample_rate: Samples per second. 22050 is fine for simple tones.

    Returns:
        A pygame.mixer.Sound ready to .play().
    """
    n = int(sample_rate * duration)
    buf = array.array("h", [0] * n)  # 16-bit signed integer buffer
    fade = int(sample_rate * 0.008)   # 8ms fade to prevent clicks
    for i in range(n):
        t = i / max(n, 1)  # 0.0 to 1.0 progress
        # Envelope: ramps up over `fade` samples, ramps down at the end
        env = min(1.0, i / max(fade, 1), (n - i) / max(fade, 1))
        # Sine wave at the frequency for this point in time
        buf[i] = int(volume * 32767 * env * math.sin(
            2 * math.pi * freq_func(t) * i / sample_rate
        ))
    return pygame.mixer.Sound(buffer=buf)


class SoundManager:
    """Holds all game sound effects. Call init() after pygame.mixer.init().

    Sounds are accessed by name via play("nav"), play("win"), etc.
    Unknown names are silently ignored (no crash if a sound is missing).
    """

    def __init__(self):
        self._sounds = {}

    def init(self):
        """Generate all game sounds. Call once at startup.

        Sound design rationale:
            nav:     Short high beep (440Hz, 60ms) — menu cursor movement
            select:  Rising sweep (400→800Hz, 150ms) — menu confirm
            bump:    Low thud (120Hz, 50ms) — ball hits wall
            win:     Long rising sweep (400→1200Hz, 400ms) — puzzle solved
            restart: Falling sweep (600→300Hz, 120ms) — level reset
        """
        self._sounds = {
            "nav": _wave(lambda t: 440, 0.06, volume=0.15),
            "select": _wave(lambda t: 400 + 400 * t, 0.15, volume=0.25),
            "bump": _wave(lambda t: 120, 0.05, volume=0.2),
            "win": _wave(lambda t: 400 + 800 * t, 0.4, volume=0.3),
            "restart": _wave(lambda t: 600 - 300 * t, 0.12, volume=0.2),
        }

    def play(self, name):
        """Play a sound by name. Silently does nothing if name is unknown."""
        s = self._sounds.get(name)
        if s:
            s.play()


# Module-level singleton. Import this, not the class.
sound_manager = SoundManager()
