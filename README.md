# Two Balls - A Pygame Maze Puzzle

A puzzle game where you control two balls simultaneously with WASD. Both respond to the same input, but each is blocked independently by maze walls. Navigate them through procedurally generated mazes until they touch.

Features 5 game types (Classic, Challenger, Infinite, Pacman, Mirror), 2 play modes (Arcade, Story), 4 difficulty levels, 6 maze generation algorithms, AI pathfinding, and a fully resizable window.

---

## Gameplay

| Game Type | Description |
|-----------|-------------|
| **Classic** | No time pressure. Both balls move together — solve at your own pace. |
| **Challenger** | Countdown timer. Finish before time runs out or fail. |
| **Infinite** | Portal edges. Boundary openings are randomly paired — entering one might exit at a different row/col on the other side. More portals on harder difficulties. |
| **Pacman** | Blue ball chases you with AI. Only you control pink. Survive the timer to win. Mazes have loops for evasion. |
| **Mirror** | Pink moves normally, blue moves **inverted** (press right → blue goes left). Same maze, mirrored controls. |

| Play Mode | Description |
|-----------|-------------|
| **Arcade** | Endless random puzzles. Solve one, get another. |
| **Story** | 50 fixed seeded puzzles per difficulty. Level select grid. Same mazes every time. |

| Difficulty | Grid | Challenger | Pacman Survive | Pacman AI Speed |
|------------|------|------------|----------------|-----------------|
| Easy | 15x12 | 12s | 30s | 63% of player |
| Normal | 20x16 | 25s | 45s | 75% |
| Hard | 25x20 | 47s | 60s | 96% |
| Extreme | 40x50 | 75s | 90s | 105% (faster) |

---

## Installation

```bash
cd Scratch_again
python3 -m venv venv
source venv/bin/activate
pip install pygame
```

## How to Run

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| W / Up | Move up / Navigate up |
| S / Down | Move down / Navigate down |
| A / Left | Move left / Navigate left |
| D / Right | Move right / Navigate right |
| Enter | Confirm selection |
| ESC | Go back / Return to menu |
| R | Restart current puzzle |

---

## Project Structure

```
two_balls/
├── main.py                     # Entry point (3 lines)
│
├── core/                       # Application infrastructure
│   ├── app.py                  # Window, clock, state machine, run loop
│   ├── state_machine.py        # State ABC + StateMachine controller
│   └── clock.py                # Fixed-timestep accumulator
│
├── config/                     # All tuning values (no logic)
│   ├── settings.py             # Gameplay: speeds, grids, timers, difficulties
│   └── theme.py                # Visual: colors, UI layout, font sizes
│
├── entities/                   # Game objects (data + minimal behavior)
│   └── ball.py                 # Ball: position, collision state, reset
│
├── systems/                    # Stateless logic operating on entities
│   ├── input.py                # WASD keys → movement vector
│   ├── collision.py            # AABB overlap, ball touch, toroidal touch
│   ├── physics.py              # Move ball with collision, wrap for infinite
│   └── ai.py                   # BFS pathfinding, AI movement for pacman
│
├── states/                     # Application screens (State objects)
│   ├── title.py                # "TWO BALLS" opening screen
│   ├── menu.py                 # Reusable generic menu (game type, mode, difficulty)
│   └── playing.py              # All gameplay: classic/challenger/infinite/pacman × arcade/story
│
├── rendering/                  # All drawing (zero game logic)
│   ├── renderer.py             # clear, overlay, game background, scaling math
│   ├── maze_renderer.py        # Wall drawing with inset + rounded corners
│   ├── ball_renderer.py        # Ball circle, highlight, ghost copies
│   ├── hud.py                  # Timer bar with color gradient
│   ├── menu_renderer.py        # Animated title, option lists, title screen
│   └── overlay_renderer.py     # Win/fail/caught prompts, story complete, level select
│
├── components/                 # Reusable game building blocks
│   ├── maze_generator.py       # 6 procedural maze algorithms
│   ├── level_factory.py        # Unified level creation for all game types
│   └── particles.py            # ParticleSystem, FloatingBubbles, BallTrail
│
├── assets/                     # Asset loading + caching (initialized once)
│   ├── fonts.py                # FontManager singleton
│   └── sounds.py               # SoundManager with procedural audio generation
│
├── PLAYERS_GUIDE.md
└── README.md
```

---

## Architecture

### Design Philosophy

The codebase follows a strict **layered architecture** inspired by ECS (Entity-Component-System) principles adapted for Pygame:

1. **Config** defines constants → imported by everything, owns nothing
2. **Entities** hold data → no rendering, no logic beyond self-reset
3. **Systems** operate on entities → stateless pure functions
4. **States** orchestrate gameplay → own entities, call systems, trigger rendering
5. **Rendering** draws what states tell it → zero game logic, reads data only
6. **Components** provide reusable building blocks → maze gen, particles, levels

### Data Flow Per Frame

```
App.run()
  │
  ├─ _process_events()
  │    └─ state_machine.handle_event(event)
  │         └─ current_state.handle_event(event)    ← event dispatch
  │
  ├─ _update()
  │    └─ for dt in timestep.steps():               ← fixed timestep
  │         └─ state_machine.update(dt)
  │              └─ current_state.update(dt)         ← game logic
  │                   ├─ systems.input.get_movement()
  │                   ├─ systems.physics.move_ball()
  │                   ├─ systems.ai.bfs_path()       (pacman only)
  │                   ├─ systems.collision.balls_touch()
  │                   └─ particles.update()
  │
  └─ _draw()
       └─ state_machine.draw(surface, tick)
            └─ current_state.draw(surface, tick)     ← pure rendering
                 ├─ rendering.renderer.clear()
                 ├─ rendering.maze_renderer.draw_walls()
                 ├─ rendering.ball_renderer.draw_ball()
                 ├─ rendering.hud.draw_timer()
                 ├─ rendering.overlay_renderer.draw_prompt()
                 └─ particles.draw()
```

### State Machine

All screens are `State` objects managed by a `StateMachine`. One state is active at a time. States transition by calling `app.state_machine.change(new_state)`.

```
TitleState ──Enter──→ MenuState (game type)
                         ──Enter──→ MenuState (play mode)
                                       ──Enter──→ MenuState (difficulty)
                                                     ──Enter──→ PlayingState
                                                                   │
                                                     ←──ESC/Back───┘
```

`MenuState` is **fully reusable** — the same class handles game type, play mode, and difficulty selection. It takes `options`, `colors`, `subtitle`, and an `on_select` callback. No duplication.

`PlayingState` handles **all 10 combinations** (5 game types × 2 play modes) via composition flags (`is_pacman`, `is_infinite`, `is_challenger`, `is_mirror`, `is_story`), not inheritance.

---

## Package Reference

### `core/` — Application Infrastructure

The engine layer. Manages the window, clock, and state lifecycle. Nothing game-specific lives here.

| Module | Class/Function | Purpose |
|--------|---------------|---------|
| `app.py` | `App` | Top-level application. Creates the pygame window, initializes assets, owns the `StateMachine` and `FixedTimestep`. The `run()` method contains the main loop: events → update → draw. Also holds shared selection state (`selected_game_type`, `selected_play_mode`, `selected_difficulty`) that menu states write and gameplay states read. |
| `state_machine.py` | `State` (ABC) | Abstract base for all application screens. Subclasses implement `handle_event(event)`, `update(dt)`, and `draw(surface, tick)`. Has `enter()` and `exit()` hooks for setup/teardown. Receives an `app` reference for accessing shared resources. |
| `state_machine.py` | `StateMachine` | Manages state transitions. Calls `exit()` on the old state and `enter()` on the new one. Forwards `handle_event`, `update`, and `draw` to the current state. |
| `clock.py` | `FixedTimestep` | Accumulates real elapsed time and yields fixed-size `dt` steps. Ensures physics runs at exactly 60Hz regardless of render framerate. Usage: `accumulate(real_dt)` then `for dt in steps(): update(dt)`. |

### `config/` — Constants and Tuning

Pure data. No logic, no imports from game code. Everything else imports from here.

| Module | Purpose |
|--------|---------|
| `settings.py` | **Gameplay constants**: window defaults (`DEFAULT_WIDTH`, `DEFAULT_HEIGHT`, `FPS`), ball physics (`PLAYER_SPEED`, `BALL_RADIUS`, `COLLISION_RADIUS`), difficulty grids (`DIFFICULTY_GRIDS`), timers (`CHALLENGER_TIMES`, `PACMAN_SURVIVE_TIMES`), AI speeds (`PACMAN_AI_SPEEDS`), story levels (`STORY_LEVELS`), particle physics (`PARTICLE_GRAVITY`, `PARTICLE_DRAG`), and menu option lists (`GAME_TYPES`, `PLAY_MODES`, `DIFFICULTIES`). |
| `theme.py` | **Visual constants**: color palette (`PINK`, `BLUE`, `BLACK`, `WHITE`, `GREEN`), game area colors (`GAME_BG`, `WALL_COLOR`, `WALL_INSET`), per-option colors (`GAME_TYPE_COLORS`, `PLAY_MODE_COLORS`, `DIFFICULTY_COLORS`), UI layout values (`MENU_ITEM_SPACING`, `UNDERLINE_PADDING`, `LEVEL_CELL_MAX_W`), and timer HUD styling (`TIMER_BAR_HEIGHT`, `TIMER_MARGIN`). |

**Why two files?** Changing ball speed shouldn't touch color definitions. Designers tune `theme.py`; gameplay programmers tune `settings.py`.

### `entities/` — Game Objects

Data holders with minimal self-management. No rendering, no game logic beyond self-reset.

| Module | Class | Purpose |
|--------|-------|---------|
| `ball.py` | `Ball` | Represents a single ball on the grid. Stores position (`gx`, `gy`), start position (for reset), color, visual `radius` (0.5 — fills a corridor), physics `collision_radius` (0.4 — slightly smaller for turning tolerance), and bump state (`bumped`, `_was_bumped`). The `just_bumped` property detects the first frame of a wall collision for sound triggering. Uses `__slots__` for memory efficiency. |

**Design decision**: Ball has no `try_move()` or `draw()` — those are in `systems/physics.py` and `rendering/ball_renderer.py`. This keeps entities as pure data, making them easy to serialize, test, and swap between game types.

### `systems/` — Stateless Game Logic

Pure functions that operate on entities and return results. No side effects beyond modifying the entities passed to them. No rendering.

| Module | Functions | Purpose |
|--------|-----------|---------|
| `input.py` | `get_movement(keys, dt)` | Reads WASD key state, returns `(dx, dy)` displacement vector scaled by `PLAYER_SPEED * dt`. Single source of truth for input → movement conversion. |
| `collision.py` | `aabb_collide(...)`, `balls_touch(a, b)`, `balls_touch_toroidal(a, b, cols, rows)` | AABB overlap test for wall collision. `balls_touch` checks if two balls overlap using visual radius (for win condition — used by all modes including Infinite). `balls_touch_toroidal` handles wrapping distance (available for simple toroidal grids). A `use_collision_radius` flag on `balls_touch` allows Pacman's fairer catch detection. |
| `physics.py` | `move_ball(ball, dx, dy, walls)`, `wrap_ball(ball, cols, rows)`, `teleport_ball(ball, portal_map, cols, rows)` | Moves a ball with axis-separated collision detection. Tests X first, then Y (allows wall-sliding). Sets `ball.bumped` on collision. `teleport_ball` handles Infinite mode's randomly-paired portals — when a ball crosses a boundary at a portal opening, it's teleported to the paired portal's position. `wrap_ball` is the simpler toroidal wrap (kept for utility). |
| `ai.py` | `bfs_path(matrix, start, end, cols, rows)`, `move_ai_toward(ball, path, speed, dt, walls)` | BFS pathfinding using parent pointers (O(n) memory, returns `deque`). `move_ai_toward` moves the AI ball toward the next cell in the path at `ai_speed`, popping cells as they're reached. Used only in Pacman mode. |

**Why stateless?** The same `move_ball()` function is used for player balls in Classic, wrapping balls in Infinite, and AI balls in Pacman. No duplication.

### `states/` — Application Screens

Each screen the player sees is a `State` subclass. States own their entities and call systems.

| Module | Class | Purpose |
|--------|-------|---------|
| `title.py` | `TitleState` | The "TWO BALLS" opening screen. Renders the animated title with pink/blue wave coloring and a pulsing "Press ENTER to Start" prompt. On Enter, transitions to a `MenuState` for game type selection. Chains menu callbacks: game type → play mode → difficulty → `PlayingState`. |
| `menu.py` | `MenuState` | **Fully reusable** menu screen. Constructor takes `options` (list of strings), `colors` (dict), `subtitle`, `on_select` (callback), and optional `back_state` (factory for ESC). Used three times in the flow: game type selection, play mode selection, difficulty selection — zero code duplication. W/S navigates, Enter confirms, ESC goes back. |
| `playing.py` | `PlayingState` | **The core gameplay state**. Handles all 10 game type × play mode combinations via composition flags. Owns two `Ball` entities, wall data, trails, particles. Sub-states: `"level_select"` (story), `"playing"`, `"win_prompt"`, `"timeout_prompt"`, `"caught_prompt"`, `"complete"`. On each `update(dt)`: reads input → moves balls (via systems) → checks win/caught/timeout → fires one-shot events. On each `draw()`: renders game area, walls, balls, trails, ghosts, HUD, and overlays. Level creation delegates to `level_factory.create_level()`. |

**Why one PlayingState?** Classic, Challenger, Infinite, Pacman, and Mirror share 90% of their logic (ball creation, wall rendering, trail updates, prompt handling). The differences (wrapping, AI, timers, inverted input) are just flag-checked branches. One class with flags is cleaner than 5+ classes with duplicated state machines.

### `rendering/` — All Drawing Logic

Pure rendering. Every function takes data and a surface, draws pixels, returns nothing. Zero game state mutation.

| Module | Functions | Purpose |
|--------|-----------|---------|
| `renderer.py` | `clear(surface)`, `draw_overlay(surface, alpha)`, `draw_game_bg(...)`, `get_scaling(cols, rows, w, h)` | Foundation drawing: fills screen with black, draws semi-transparent dark overlay (cached surface to avoid allocation per frame), fills the game area rectangle with white, computes cell size and centering offsets for any screen dimension. |
| `maze_renderer.py` | `draw_walls(surface, walls, cell_size, ox, oy)` | Draws wall tuples as dark rounded rectangles with a 2px inset on each side for a thinner visual appearance. Each wall is a `(gx, gy, gw, gh)` tuple in grid units, converted to pixels at draw time. |
| `ball_renderer.py` | `ball_to_pixel(ball, cs, ox, oy)`, `draw_ball(surface, ball, cs, ox, oy)`, `draw_ghost_portal(surface, ball, portal_map, cols, rows, cs, ox, oy)` | Converts ball grid position to pixel coordinates. Draws the ball as a filled circle with a small highlight dot for depth. `draw_ghost_portal` renders faded copies at destination portal positions when a ball is near a portal opening (Infinite mode). |
| `hud.py` | `draw_timer(surface, time_left, time_total, label)` | Draws a horizontal timer bar at the top of the screen with a color gradient (green → yellow → red as time decreases). Shows remaining seconds as text. Used by both Challenger (countdown) and Pacman (survive) modes. The `label` parameter distinguishes them ("Survive: 25s" vs "12s"). |
| `menu_renderer.py` | `draw_title_screen(surface, tick)`, `draw_menu_screen(surface, options, colors, selected, subtitle, tick)`, `draw_animated_title(surface, tick)`, `draw_option_list(...)`, `wave_color(base, tick, offset, intensity)` | All menu-screen rendering. `wave_color` shifts RGB brightness with a sine wave for animations. `draw_animated_title` renders "Two Balls" with per-character wave coloring. `draw_option_list` renders a vertical list with bounce animation and underline on the selected item. `draw_menu_screen` combines title + option list (used for all 3 menu screens). `draw_title_screen` renders the "TWO BALLS" opening with pink/blue coloring. Font metric widths are cached to avoid recalculation every frame. |
| `overlay_renderer.py` | `draw_prompt(...)`, `draw_win_prompt(...)`, `draw_timeout_prompt(...)`, `draw_caught_prompt(...)`, `draw_story_complete(surface, tick)`, `draw_level_select(surface, selected, tick)` | Post-game overlays. `draw_prompt` is the generic base: dark overlay + header + selectable options. `draw_win_prompt`, `draw_timeout_prompt`, and `draw_caught_prompt` call it with different header text and colors. `draw_story_complete` shows the congratulations screen. `draw_level_select` renders the 10×5 grid of level numbers for Story mode. |

### `components/` — Reusable Building Blocks

Game-specific components that don't fit neatly into entities/systems/rendering.

| Module | Classes/Functions | Purpose |
|--------|-------------------|---------|
| `maze_generator.py` | `MazeGenerator` | Generates perfect mazes using 6 algorithms: Recursive Backtracker (long corridors), Prim's (bushy, short dead ends), Kruskal's (spiky), Recursive Division (long straight walls), Eller's (balanced, row-by-row), Binary Tree (NW diagonal bias). Uses a wall-passage grid representation where passage cells are at odd positions. Generated maze is padded to target dimensions. `find_distant_pair(matrix)` uses double-BFS to find the two most distant open cells for ball placement. |
| `level_factory.py` | `create_level(difficulty, game_type, seed)` | **Single entry point** for all level creation. Generates a maze via `MazeGenerator`, then applies game-type-specific modifications: Infinite mode opens randomly-paired portals on boundary edges (count scales with difficulty: 2/3/5/8 per axis). Pacman mode removes ~25% of internal bridge walls to create circular loops for evasion. Places balls at maximum distance via double-BFS. Returns a level dict with `pink_start`, `blue_start`, `walls`, and optional `matrix` (pacman) or `portal_map` (infinite). Deterministic seeding via `_seeded()` wrapper for Story mode reproducibility. |
| `particles.py` | `ParticleSystem`, `FloatingBubbles`, `BallTrail`, `Particle`, `Bubble` | Visual effects. `ParticleSystem`: general-purpose emitter with gravity and drag — `emit_burst()` for radial explosions on win, `emit_confetti()` for falling celebration particles. `FloatingBubbles`: ambient circles that drift upward on menu screens, respawning at the bottom. `BallTrail`: deque-based fading trail that blends from white toward the ball's color. `Particle` and `Bubble` use `__slots__` for memory efficiency. |

### `assets/` — Asset Management

Initialized once at startup, accessed globally via singleton instances.

| Module | Class | Purpose |
|--------|-------|---------|
| `fonts.py` | `FontManager` | Holds three pygame font objects: `font` (48pt, general text), `small` (32pt, hints and labels), `title` (72pt, headings). Initialized after `pygame.init()`. Accessed as `font_manager.font`, `font_manager.small`, etc. Singleton pattern avoids the "import captures None" gotcha of module-level variables. |
| `sounds.py` | `SoundManager` | Generates 5 sound effects procedurally using sine waves and frequency sweeps — no external audio files. `nav` (440Hz beep), `select` (rising sweep 400→800Hz), `bump` (120Hz thud), `win` (rising sweep 400→1200Hz), `restart` (falling sweep 600→300Hz). Each sound is a `pygame.mixer.Sound` created from a computed `array.array` buffer. Accessed via `sound_manager.play("name")`. |

---

## Game Mechanics

### Grid Coordinate System

All game logic operates in **grid units** (floats). The grid origin `(0, 0)` is the top-left. Balls sit at cell centers like `(col + 0.5, row + 0.5)`. Conversion to pixels: `pixel = offset + grid_pos * cell_size`, where `cell_size = min(screen_w / cols, screen_h / rows)` ensures square cells. Offsets center the grid in the window.

### Movement and Collision

Player speed is 4.8 grid units/second. With the fixed timestep at 60Hz, each frame displaces 0.08 grid units. Collision uses axis-separated AABB: X movement is tested first, then Y. This allows wall-sliding (a ball blocked on one axis can still move on the other). The visual `BALL_RADIUS` (0.5) fills the corridor exactly; the physics `COLLISION_RADIUS` (0.4) is 20% smaller, giving 0.1 grid units of tolerance per side so balls can turn into perpendicular corridors without pixel-perfect alignment.

### Win Conditions

- **Classic/Challenger/Infinite**: Balls touch when `distance² ≤ (visual_radius × 2)²`
- **Infinite**: Uses toroidal distance (wrapping — a ball at x=0.5 and another at x=cols-0.5 are 1 unit apart)
- **Pacman**: Player survives the countdown. Caught uses collision radius (fairer — AI must physically overlap, not just be visually close)

### AI Pathfinding (Pacman)

BFS from blue's cell to pink's cell on the maze matrix. Uses parent pointers (O(n) memory) not path copies. Recalculates every 10 frames (~6 times/second). AI speed scales per difficulty: 63% of player (Easy) to 105% (Extreme). Loopy mazes (25% of bridge walls removed) give the player escape routes.

---

## Extending the Game

### Adding a New Game Type

1. Add the name to `GAME_TYPES` in `config/settings.py`
2. Add its color to `GAME_TYPE_COLORS` in `config/theme.py`
3. In `states/playing.py`, add a flag (e.g., `self.is_gravity = game_type == "gravity"`)
4. Add type-specific logic in `update()` and `draw()` gated by the flag
5. If the game type needs different level generation, add a branch in `components/level_factory.py:create_level()`

### Adding a New Maze Algorithm

1. Add a `_my_algorithm(self)` method to `MazeGenerator` in `components/maze_generator.py`
2. Add `"my_algorithm"` to the `ALGORITHMS` list
3. Add the entry to the `methods` dict in `generate()`

### Adding a New Difficulty

1. Add grid size to `DIFFICULTY_GRIDS` in `config/settings.py`
2. Add timers to `CHALLENGER_TIMES`, `PACMAN_SURVIVE_TIMES`, `PACMAN_AI_SPEEDS`
3. Add the name to `DIFFICULTIES` and color to `DIFFICULTY_COLORS`

### Adding a New Screen

1. Create `states/my_screen.py` extending `State`
2. Implement `handle_event`, `update`, `draw`
3. Transition to it via `app.state_machine.change(MyScreen(app))`

---

## Future Scope

Planned game types that fit the "same input, different results" core mechanic:

| Game Type | Description | Complexity |
|-----------|-------------|------------|
| **Ice** | Balls slide until they hit a wall (no fine movement). Same direction, different stopping points. Classic puzzle mechanic. | Modify `move_ball` to slide until blocked instead of fixed displacement. |
| **Gravity** | Balls constantly fall downward. You can move left/right freely but moving up is a single-cell "jump". Turns the maze into a platformer puzzle. | Add per-frame gravity in `update()`, modify up-input to be a one-shot jump. |
| **Shadow** | One ball responds immediately, the other replays your inputs with a ~0.5s delay. Plan sequences that work for both present and past input. | Queue input history, replay delayed inputs on the second ball. |
| **Shrink** | Maze walls close inward over time. Outer rings of cells become walls periodically. Bring the balls together before the playable area disappears. | Timer-driven wall addition in `update()`, rebuild wall list periodically. |
