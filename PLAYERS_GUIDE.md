# Two Balls - Player's Guide

## Welcome

Two Balls is a maze puzzle where you control two balls at the same time. Both respond to the same keys, but walls block each ball independently. Your goal: bring them together.

---

## Getting Started

Launch the game and you'll see the **title screen**. Press **Enter** to begin.

You'll navigate through three selection screens:

1. **Game Type** — How the rules work
2. **Play Mode** — How progression works
3. **Difficulty** — How big and hard the maze is

Use **W/S** or **arrow keys** to navigate, **Enter** to confirm, **ESC** to go back.

---

## Game Types

### Classic

Standard gameplay. You control both balls with WASD. They move simultaneously. One hits a wall? It stops — the other keeps going. Guide them through the maze until they touch.

No timer. No pressure. Pure puzzle solving.

### Challenger

Same rules as Classic, but with a **countdown timer**. A color-coded bar at the top of the screen ticks down from green to red. If time runs out, you see "Time's Up!" and can retry or quit.

| Difficulty | Time Limit |
|------------|------------|
| Easy | 12 seconds |
| Normal | 25 seconds |
| Hard | 47 seconds |
| Extreme | 75 seconds |

### Infinite

Both balls still move together, but some maze edges are **open**. Move through one side of the screen and you appear on the opposite side — pac-man style.

The openings look like normal background — just gaps in the boundary wall. When a ball is near a portal edge, a faded **ghost copy** appears on the other side so you can see where it'll emerge.

Both balls wrap independently. One going through a portal doesn't affect the other.

### Pacman

Role reversal. You control **only the pink ball**. The blue ball is controlled by **AI** that chases you using shortest-path finding.

Your goal: **survive** until the countdown reaches zero. The AI recalculates its path several times per second.

Mazes in Pacman mode have **circular loops** — walls are removed to create shortcuts and escape routes. Use them. The AI takes the shortest path, so longer routes around loops buy you time.

| Difficulty | Survive Time | AI Speed (vs you) |
|------------|-------------|-------------------|
| Easy | 30 seconds | 63% |
| Normal | 45 seconds | 75% |
| Hard | 60 seconds | 96% (nearly equal) |
| Extreme | 90 seconds | 105% (faster than you) |

On Extreme, the AI is actually faster. You **must** use the maze geometry to survive — straight running won't work.

---

## Play Modes

### Arcade

Every puzzle is randomly generated. You'll never see the same maze twice.

When you complete a puzzle (or survive in Pacman):
- **Keep Going** — new random puzzle
- **Back to Menu** — return to title screen

No end, no score, no limit. Just puzzles.

### Story

Each game type × difficulty combination has **50 fixed puzzles**. The mazes are generated from deterministic seeds, so they're the same every time you play. Classic Story and Challenger Story have different puzzle sets — solving one doesn't spoil the other.

After choosing a difficulty, you see a **level select grid** (10 columns × 5 rows, levels 1–50). Navigate with **WASD** or **arrow keys**, press **Enter** to play any level.

When you complete a puzzle:
- **Next Level** — advance to the next puzzle (shows progress X/50)
- **Back to Levels** — return to the grid

Complete all 50 to see the congratulations screen.

---

## Difficulty Levels

| Level | Grid Size | What to Expect |
|-------|-----------|----------------|
| **Easy** | 15 × 12 | Open paths, fewer walls. Learn the mechanics. |
| **Normal** | 20 × 16 | Moderate density. Plan a few moves ahead. |
| **Hard** | 25 × 20 | Tight corridors. Careful navigation required. |
| **Extreme** | 40 × 50 | Massive maze. Demands patience and strategy. |

---

## Maze Generation

Every maze is procedurally generated using one of 6 algorithms, picked randomly:

| Algorithm | Style |
|-----------|-------|
| Recursive Backtracker | Long winding corridors, river-like |
| Prim's | Many short dead ends, bushy |
| Kruskal's | Spiky, short dead ends |
| Recursive Division | Long straight walls, open feel |
| Eller's | Balanced, row-by-row |
| Binary Tree | Strong diagonal bias |

The two balls are always placed as far apart as possible within the maze (calculated using a graph diameter algorithm).

---

## Resizable Window

Drag the window edges to any size. The maze scales to fit while keeping cells perfectly square. If the aspect ratio doesn't match the grid, black bars appear on the sides.

---

## How the Puzzle Works

The core mechanic:

1. Both balls receive the **same movement input**
2. Walls block each ball **independently**
3. Identical inputs produce **different results** depending on each ball's position

The puzzle is finding a sequence of moves where the combined effect on both balls brings them to the same spot.

The key technique: **parking**. Move one ball against a wall so it can't go further in that direction. Now when you press that direction, only the *other* ball moves. This lets you reposition them relative to each other.

---

## Controls Reference

| Key | In Menus | In Game |
|-----|----------|---------|
| W / Up | Navigate up | Move balls up |
| S / Down | Navigate down | Move balls down |
| A / Left | Navigate left (level grid) | Move balls left |
| D / Right | Navigate right (level grid) | Move balls right |
| Enter | Confirm selection | — |
| ESC | Go back | Return to menu / level grid |
| R | — | Restart current puzzle |

---

## Visual Feedback

- **Ball trails** — Light-colored fading trails show each ball's recent path. Helps track both balls at once.
- **Ball highlight** — Small bright dot on each ball gives a 3D depth effect.
- **Ghost copies** — (Infinite mode) Faded ball copies appear near wrap edges to preview where the ball will emerge.
- **Timer bar** — (Challenger / Pacman) Color gradient bar at the top: green → yellow → red as time decreases. Shows remaining seconds.
- **Wall bump sound** — Low thud when a ball hits a wall. Tells you a ball is blocked even if you're watching the other one.
- **Win particles** — Colored bursts from both balls + confetti rain when you complete a puzzle.
- **Menu bubbles** — Floating colored circles drift upward on menu screens.

---

## Tips and Strategies

### General

- **Watch both balls.** It's easy to focus on one and forget the other is stuck.
- **Listen for bumps.** The wall-hit sound tells you when a ball is blocked.
- **Use walls to your advantage.** If one ball is against a wall, pressing that direction only moves the *other* ball.
- **Diagonal movement works.** W+D moves both balls up-right. Each axis is independent.

### Easy / Normal

- Move both balls toward the center in broad sweeps.
- Look for long corridors where both balls can move freely.

### Hard / Extreme

- Plan sequences: "park pink against this wall, then move blue three cells right."
- Dead ends are dangerous — avoid getting both balls stuck.
- On Extreme, the maze is huge. Be methodical, not random.

### Challenger Mode

- Don't wander. Scan the maze structure first, then execute.
- Short, deliberate move sequences beat long exploratory ones.

### Infinite Mode

- Think in terms of which portal exits are closer. Sometimes going "backward" through a portal is the shortest path.
- Both balls wrap independently — you can use a portal to separate them or bring them together.

### Pacman Mode

- **Use the loops.** Circle around walls to gain distance. The AI always takes the shortest path, so a detour around a loop buys you time.
- **Don't get cornered.** Dead ends are fatal — the AI will trap you.
- **On Extreme, the AI is faster than you.** Pure running is impossible. You must exploit corners, loops, and direction changes where the AI's pathfinding takes a longer route.
- **Watch the countdown.** Sometimes the best strategy is to survive in a small area with good loop options rather than running across the whole maze.

---

## Menu Flow

```
Title Screen ("TWO BALLS")
  └─ Enter
     Game Type (Classic / Challenger / Infinite / Pacman)
       └─ Enter
          Play Mode (Arcade / Story)
            └─ Enter
               Difficulty (Easy / Normal / Hard / Extreme)
                 └─ Enter
                    ├─ Arcade → Gameplay → Win Prompt → Keep Going / Menu
                    └─ Story → Level Select → Gameplay → Win Prompt → Next / Levels
```

ESC goes back one step at any point. During gameplay, ESC returns to the level grid (Story) or the title screen (Arcade).
