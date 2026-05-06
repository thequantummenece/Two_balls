"""
Playing state: the core gameplay loop for ALL game type × play mode combinations.

Instead of separate ArcadeMode, StoryMode, InfiniteMode, and PacmanMode classes
(which shared 90% of their code), this single state handles all 10 combinations:
    classic × arcade, classic × story,
    challenger × arcade, challenger × story,
    infinite × arcade, infinite × story,
    pacman × arcade, pacman × story,
    mirror × arcade, mirror × story

The differences between game types (wrapping, AI, timers, mirrored input) are
handled by boolean flags checked at the relevant points. This avoids massive
code duplication while keeping the logic readable.

Sub-states:
    "level_select" — Story mode level grid (entry point for story)
    "playing"      — Active gameplay (entry point for arcade)
    "win_prompt"   — Post-win overlay with Keep Going / Next Level options
    "timeout_prompt" — Challenger timer expired
    "caught_prompt" — Pacman AI caught the player
    "complete"     — All 50 story levels finished

The update() method follows strict event → update → draw separation:
    - Input reading via systems/input.py
    - Ball movement via systems/physics.py
    - AI pathfinding via systems/ai.py
    - Collision checks via systems/collision.py
    - One-shot event firing (win, caught, timeout) via boolean flags
    - Trail and particle updates

The draw() method is pure rendering — reads state, draws pixels, returns nothing.
"""

import pygame
from collections import deque
from core.state_machine import State
from config.settings import (
    DIFFICULTY_GRIDS, CHALLENGER_TIMES, STORY_LEVELS,
    PACMAN_AI_SPEEDS, PACMAN_REPATH_INTERVAL, PACMAN_SURVIVE_TIMES,
    LEVEL_GRID_COLS,
)
from config.theme import PINK, BLUE
from entities.ball import Ball
from systems.input import get_movement
from systems.physics import move_ball, teleport_ball
from systems.collision import balls_touch
from systems.ai import bfs_path, move_ai_toward
from components.level_factory import create_level
from components.particles import ParticleSystem, BallTrail
from rendering.renderer import clear, get_scaling, draw_game_bg
from rendering.maze_renderer import draw_walls
from rendering.ball_renderer import draw_ball, ball_to_pixel, draw_ghost_portal
from rendering.hud import draw_timer
from rendering.overlay_renderer import (
    draw_win_prompt, draw_timeout_prompt, draw_caught_prompt,
    draw_story_complete, draw_level_select,
)
from assets.sounds import sound_manager


class PlayingState(State):
    """Unified gameplay state for all game type × play mode combinations.

    Reads app.selected_game_type, selected_play_mode, and selected_difficulty
    from the App to configure itself. All game-type differences are handled
    by boolean flags (is_infinite, is_pacman, is_challenger, is_story).
    """

    def __init__(self, app):
        super().__init__(app)

        # -- Configuration from user selections --
        self.game_type = app.selected_game_type
        self.play_mode = app.selected_play_mode
        self.difficulty = app.selected_difficulty

        # Grid dimensions for this difficulty
        cols, rows = DIFFICULTY_GRIDS[self.difficulty]
        self.cols, self.rows = cols, rows

        # Boolean flags for game-type differences. Checked in update/draw
        # to avoid string comparisons every frame.
        self.is_infinite = self.game_type == "infinite"
        self.is_pacman = self.game_type == "pacman"
        self.is_challenger = self.game_type == "challenger"
        self.is_mirror = self.game_type == "mirror"
        self.is_story = self.play_mode == "story"

        # -- Entity state --
        self.pink = None           # Player-controlled pink ball
        self.blue = None           # Second ball (player or AI controlled)
        self.walls = []            # List of (gx, gy, gw, gh) wall tuples
        self._matrix = None        # 2D grid for AI pathfinding (pacman only)
        self._cached_level = None  # Cached for reset (same maze on R press)
        self.portal_map = {}       # Portal pair map (infinite only)

        # -- Visual effects --
        self.pink_trail = BallTrail(PINK)
        self.blue_trail = BallTrail(BLUE)
        self.particles = ParticleSystem()

        # -- Progress tracking --
        self.level_num = 0         # Current level (0-indexed)
        self.level_index = 0       # Cursor position in story level grid

        # -- Win/fail state --
        # Using boolean flags instead of consume_event pattern. _win_fired
        # ensures one-shot effects (sound, particles) only trigger once.
        self.won = False
        self.caught = False
        self._win_fired = False
        self._caught_fired = False

        # -- Challenger timer --
        self.challenger_limit = (
            CHALLENGER_TIMES.get(self.difficulty, 0) if self.is_challenger else 0
        )
        self.challenger_left = self.challenger_limit
        self.timed_out = False

        # -- Pacman timer and AI --
        self.survive_time = (
            PACMAN_SURVIVE_TIMES.get(self.difficulty, 45) if self.is_pacman else 0
        )
        self.survive_left = self.survive_time
        self.ai_speed = (
            PACMAN_AI_SPEEDS.get(self.difficulty, 3.6) if self.is_pacman else 0
        )
        self._ai_path = deque()    # BFS path for AI (deque for O(1) popleft)
        self._ai_frame = 0         # Frame counter for repath interval

        # -- Sub-state --
        # Story mode starts at level select; arcade starts playing immediately.
        self.sub = "level_select" if self.is_story else "playing"
        self.prompt_index = 0      # Selected option in win/fail prompts

    # -----------------------------------------------------------------------
    # Level management
    # -----------------------------------------------------------------------

    def enter(self):
        """Called when this state becomes active. Generate the first level
        for arcade mode. Story mode waits for user to pick from the grid."""
        if not self.is_story:
            self._new_level()

    def _seed(self):
        """Generate a deterministic seed for story mode levels.

        Includes game_type so classic-story and pacman-story have different
        mazes for the same level number. Returns None for arcade (random).
        """
        if self.is_story:
            return f"{self.game_type}_{self.difficulty}_{self.level_num}"
        return None

    def _new_level(self):
        """Generate a fresh maze using the level factory.

        The level is cached so that reset() (R key) restores the exact
        same maze layout and ball positions without regenerating.
        """
        level = create_level(self.difficulty, self.game_type, seed=self._seed())
        self._cached_level = level
        self._apply(level)

    def _apply(self, level):
        """Apply a level dict: set walls, create balls, clear effects.

        Called by both _new_level() (fresh maze) and _restart() (same maze).
        Resets all per-level state: win/fail flags, timers, AI path, trails.
        """
        self.walls = level["walls"]
        self._matrix = level.get("matrix")    # Only present for pacman
        self.portal_map = level.get("portal_map", {})  # Only present for infinite

        # Create ball entities at the positions specified by the level
        px, py = level["pink_start"]
        bx, by = level["blue_start"]
        self.pink = Ball(px, py, PINK)
        self.blue = Ball(bx, by, BLUE)

        # Clear all per-level visual and game state
        self.pink_trail.clear()
        self.blue_trail.clear()
        self.particles.clear()
        self.won = self.caught = False
        self._win_fired = self._caught_fired = False
        self.timed_out = False
        self.challenger_left = self.challenger_limit
        self.survive_left = self.survive_time
        self._ai_path = deque()
        self._ai_frame = 0

    def _restart(self):
        """Reset the current level (same maze, same start positions).

        Uses the cached level dict so no maze regeneration occurs.
        Called when the player presses R or selects Retry from a prompt.
        """
        sound_manager.play("restart")
        self._apply(self._cached_level)

    def _next_level(self):
        """Advance to the next level (story mode). Generates a new maze."""
        self.level_num += 1
        self._new_level()
        self.sub = "playing"

    # -----------------------------------------------------------------------
    # Event handling
    # -----------------------------------------------------------------------

    def handle_event(self, event):
        """Dispatch events to the appropriate sub-state handler.

        Only KEYDOWN events are processed. Each sub-state has its own
        handler method to keep the logic clean.
        """
        if event.type != pygame.KEYDOWN:
            return
        handler = {
            "level_select": self._ev_level_select,
            "playing": self._ev_playing,
            "win_prompt": self._ev_prompt,
            "timeout_prompt": self._ev_prompt,
            "caught_prompt": self._ev_prompt,
            "complete": self._ev_complete,
        }.get(self.sub)
        if handler:
            handler(event)

    def _ev_level_select(self, event):
        """Handle navigation in the story level select grid.

        WASD/arrows move the cursor in 2D. Enter starts the selected level.
        ESC goes back to the title screen.
        """
        cols = LEVEL_GRID_COLS
        moved = True
        if event.key in (pygame.K_a, pygame.K_LEFT):
            self.level_index = max(0, self.level_index - 1)
        elif event.key in (pygame.K_d, pygame.K_RIGHT):
            self.level_index = min(STORY_LEVELS - 1, self.level_index + 1)
        elif event.key in (pygame.K_w, pygame.K_UP):
            self.level_index = max(0, self.level_index - cols)
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self.level_index = min(STORY_LEVELS - 1, self.level_index + cols)
        else:
            moved = False
        if moved:
            sound_manager.play("nav")
        elif event.key == pygame.K_RETURN:
            sound_manager.play("select")
            self.level_num = self.level_index
            self._new_level()
            self.sub = "playing"
        elif event.key == pygame.K_ESCAPE:
            sound_manager.play("nav")
            self._go_back()

    def _ev_playing(self, event):
        """Handle events during active gameplay.

        R restarts the current level. ESC returns to level select (story)
        or title screen (arcade).
        """
        if event.key == pygame.K_r:
            self._restart()
        elif event.key == pygame.K_ESCAPE:
            sound_manager.play("nav")
            if self.is_story:
                self.sub = "level_select"
            else:
                self._go_back()

    def _ev_prompt(self, event):
        """Handle navigation in win/fail/caught prompt overlays.

        W/S navigates between two options. Enter confirms:
            Option 0 = Continue (Keep Going / Next Level / Retry)
            Option 1 = Back (Back to Menu / Back to Levels)
        """
        if event.key in (pygame.K_w, pygame.K_UP):
            sound_manager.play("nav")
            self.prompt_index = (self.prompt_index - 1) % 2
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            sound_manager.play("nav")
            self.prompt_index = (self.prompt_index + 1) % 2
        elif event.key == pygame.K_RETURN:
            sound_manager.play("select")
            self.particles.clear()
            if self.prompt_index == 0:
                # Continue: advance or retry depending on which prompt
                if self.sub == "win_prompt":
                    if self.is_story:
                        self._next_level()
                    else:
                        # Arcade: new random level
                        self.level_num += 1
                        self._new_level()
                        self.sub = "playing"
                else:
                    # Timeout or caught: retry same level
                    self._restart()
                    self.sub = "playing"
            else:
                # Back: return to level select or title
                if self.is_story:
                    self.sub = "level_select"
                else:
                    self._go_back()

    def _ev_complete(self, event):
        """Handle the story completion screen. Enter returns to level select."""
        if event.key == pygame.K_RETURN:
            sound_manager.play("select")
            self.particles.clear()
            self.sub = "level_select"

    def _go_back(self):
        """Return to the title screen."""
        from states.title import TitleState
        self.app.state_machine.change(TitleState(self.app))

    # -----------------------------------------------------------------------
    # Update (fixed timestep — all game logic here, no rendering)
    # -----------------------------------------------------------------------

    def update(self, dt):
        """Per-fixed-timestep update. Handles movement, AI, collisions, timers.

        Only runs game logic when sub-state is "playing". Other sub-states
        (prompts, level select) only update particles for visual continuity.
        """
        if self.sub != "playing":
            # Keep particles animating during prompts for visual polish
            self.particles.update()
            return

        keys = pygame.key.get_pressed()

        # -- Player movement --
        dx, dy = get_movement(keys, dt)
        if self.is_pacman:
            # Pacman: player only controls pink
            move_ball(self.pink, dx, dy, self.walls)
        elif self.is_mirror:
            # Mirror: pink moves normally, blue moves inverted
            move_ball(self.pink, dx, dy, self.walls)
            move_ball(self.blue, -dx, -dy, self.walls)
        else:
            # All other types: both balls move together
            move_ball(self.pink, dx, dy, self.walls)
            move_ball(self.blue, dx, dy, self.walls)

        # -- Infinite portal teleportation --
        if self.is_infinite:
            teleport_ball(self.pink, self.portal_map, self.cols, self.rows)
            teleport_ball(self.blue, self.portal_map, self.cols, self.rows)

        # -- Pacman AI --
        if self.is_pacman and not self.won and not self.caught:
            self._ai_frame += 1
            # Recalculate path periodically (not every frame — CPU savings)
            if self._ai_frame >= PACMAN_REPATH_INTERVAL or len(self._ai_path) < 2:
                self._ai_frame = 0
                start = (int(self.blue.gx), int(self.blue.gy))
                end = (int(self.pink.gx), int(self.pink.gy))
                self._ai_path = bfs_path(self._matrix, start, end,
                                         self.cols, self.rows)
            move_ai_toward(self.blue, self._ai_path, self.ai_speed,
                           dt, self.walls)

        # -- Bump sound (first frame of wall collision only) --
        if self.pink.just_bumped or self.blue.just_bumped:
            sound_manager.play("bump")

        # -- Win/fail condition checks --
        if not self.won and not self.caught:
            if self.is_pacman:
                # Pacman survive timer: counts down, win when it hits 0
                self.survive_left -= dt
                if self.survive_left <= 0:
                    self.survive_left = 0
                    self.won = True
                # Caught check: uses collision_radius for fairness
                cr = self.pink.collision_radius + self.blue.collision_radius
                dx_c = self.pink.gx - self.blue.gx
                dy_c = self.pink.gy - self.blue.gy
                if dx_c * dx_c + dy_c * dy_c <= cr * cr:
                    self.caught = True
            elif self.is_infinite:
                # Infinite: standard touch (portals teleport, not wrap)
                if balls_touch(self.pink, self.blue):
                    self.won = True
            else:
                # Classic/Challenger: standard distance check
                if balls_touch(self.pink, self.blue):
                    self.won = True

            # Challenger timer: independent of win (can time out even if close)
            if self.is_challenger and not self.won:
                self.challenger_left -= dt
                if self.challenger_left <= 0:
                    self.challenger_left = 0
                    self.timed_out = True

        # -- One-shot event firing --
        # These blocks run ONCE on the frame the condition first becomes true.
        # The _fired flags prevent re-triggering on subsequent frames.
        if self.won and not self._win_fired:
            self._win_fired = True
            sound_manager.play("win")
            self._emit_win_particles()
            self.prompt_index = 0
            # Story: check if this was the last level
            if self.is_story and self.level_num >= STORY_LEVELS - 1:
                self.sub = "complete"
            else:
                self.sub = "win_prompt"

        if self.caught and not self._caught_fired:
            self._caught_fired = True
            self.prompt_index = 0
            self.sub = "caught_prompt"

        if self.timed_out and self.sub == "playing":
            self.prompt_index = 0
            self.sub = "timeout_prompt"

        # -- Trail and particle updates --
        self._update_trails()
        self.particles.update()

    def _emit_win_particles(self):
        """Emit celebratory particle bursts from both ball positions.

        Called once on the frame the win condition triggers. Creates
        colored bursts from each ball and confetti from the top.
        """
        sw, sh = self.app.screen.get_size()
        cs, ox, oy = get_scaling(self.cols, self.rows, sw, sh)
        ppx, ppy, _ = ball_to_pixel(self.pink, cs, ox, oy)
        bpx, bpy, _ = ball_to_pixel(self.blue, cs, ox, oy)
        self.particles.emit_burst(ppx, ppy, self.pink.color, count=30, speed=4)
        self.particles.emit_burst(bpx, bpy, self.blue.color, count=30, speed=4)
        self.particles.emit_confetti(sw, sh, count=80)

    def _update_trails(self):
        """Add current ball positions to their trails if they've moved.

        Only adds a new trail point when the pixel position has changed
        from the last recorded point. This prevents the trail from
        "pooling up" at rest when the ball isn't moving.
        """
        sw, sh = self.app.screen.get_size()
        cs, ox, oy = get_scaling(self.cols, self.rows, sw, sh)
        ppx, ppy, ppr = ball_to_pixel(self.pink, cs, ox, oy)
        bpx, bpy, bpr = ball_to_pixel(self.blue, cs, ox, oy)
        if not self.pink_trail.positions or (ppx, ppy) != self.pink_trail.positions[-1][:2]:
            self.pink_trail.add(ppx, ppy, ppr)
        if not self.blue_trail.positions or (bpx, bpy) != self.blue_trail.positions[-1][:2]:
            self.blue_trail.add(bpx, bpy, bpr)

    # -----------------------------------------------------------------------
    # Draw (pure rendering — no state mutation)
    # -----------------------------------------------------------------------

    def draw(self, surface, tick):
        """Render the current frame based on the active sub-state.

        Level select renders its own screen. All other sub-states render
        the game board with appropriate overlay prompts on top.
        """
        if self.sub == "level_select":
            draw_level_select(surface, self.level_index, tick)
            # Bubbles continue animating on the level select screen
            self.app.bubbles.update(tick)
            self.app.bubbles.draw(surface)
            return

        # -- Game board rendering --
        sw, sh = surface.get_size()
        cs, ox, oy = get_scaling(self.cols, self.rows, sw, sh)

        # Layer 1: Black background + white game area + walls
        clear(surface)
        draw_game_bg(surface, self.cols, self.rows, cs, ox, oy)
        draw_walls(surface, self.walls, cs, ox, oy)

        # Layer 2: Ball trails (drawn before balls so they appear behind)
        self.pink_trail.draw(surface)
        self.blue_trail.draw(surface)

        # Layer 3: Balls
        draw_ball(surface, self.pink, cs, ox, oy)
        draw_ball(surface, self.blue, cs, ox, oy)

        # Layer 4: Ghost copies near portal edges (Infinite only)
        if self.is_infinite:
            draw_ghost_portal(surface, self.pink, self.portal_map,
                              self.cols, self.rows, cs, ox, oy)
            draw_ghost_portal(surface, self.blue, self.portal_map,
                              self.cols, self.rows, cs, ox, oy)

        # Layer 5: HUD (timer bars)
        if self.is_pacman and self.sub == "playing":
            draw_timer(surface, self.survive_left, self.survive_time, label="Survive")
        if self.is_challenger and self.sub == "playing":
            draw_timer(surface, self.challenger_left, self.challenger_limit)

        # Layer 6: Particles (on top of game, below overlays)
        self.particles.draw(surface)

        # Layer 7: Overlay prompts (drawn last, on top of everything)
        if self.sub == "win_prompt":
            header = self._win_header()
            opts = self._continue_options()
            draw_win_prompt(surface, opts, self.prompt_index, header, tick)
        elif self.sub == "timeout_prompt":
            draw_timeout_prompt(surface, self._back_options(),
                                self.prompt_index, tick)
        elif self.sub == "caught_prompt":
            draw_caught_prompt(surface, self._back_options(),
                               self.prompt_index, tick)
        elif self.sub == "complete":
            draw_story_complete(surface, tick)

    def _win_header(self):
        """Generate the win prompt header text based on game type and mode."""
        if self.is_pacman:
            return "You Survived!"
        if self.is_story:
            return f"Level {self.level_num + 1}/{STORY_LEVELS} Complete!"
        return "Puzzle Complete!"

    def _continue_options(self):
        """Options for the win prompt: continue or go back."""
        if self.is_story:
            return ["Next Level", "Back to Levels"]
        return ["Keep Going", "Back to Menu"]

    def _back_options(self):
        """Options for fail prompts (timeout/caught): retry or go back."""
        back = "Back to Levels" if self.is_story else "Back to Menu"
        return ["Retry", back]
