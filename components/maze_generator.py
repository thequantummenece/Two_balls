import random
from collections import deque


ALGORITHMS = [
    "recursive_backtracker",
    "prims",
    "kruskals",
    "recursive_division",
    "ellers",
    "binary_tree",
]


class MazeGenerator:
    """Generates perfect mazes on a grid using various algorithms.

    The grid uses the standard wall-passage representation:
      - Odd,odd positions are passage cells
      - Even positions are walls or connections
      - Outer ring is always walls

    Logical maze has maze_cols x maze_rows cells, mapped onto a
    (2*maze_cols+1) x (2*maze_rows+1) grid, padded to target size.
    """

    def __init__(self, cols, rows):
        self.target_cols = cols
        self.target_rows = rows
        self.maze_cols = (cols - 1) // 2
        self.maze_rows = (rows - 1) // 2

    # -- Grid helpers --

    def _new_grid(self):
        gen_cols = 2 * self.maze_cols + 1
        gen_rows = 2 * self.maze_rows + 1
        return [[1] * gen_cols for _ in range(gen_rows)]

    def _pad(self, grid):
        """Pad grid with wall rows/columns to reach target dimensions."""
        for row in grid:
            row.extend([1] * (self.target_cols - len(row)))
        while len(grid) < self.target_rows:
            grid.append([1] * self.target_cols)
        return grid

    def _cell_pos(self, mc, mr):
        return 2 * mc + 1, 2 * mr + 1

    def _wall_pos(self, mc1, mr1, mc2, mr2):
        gc1, gr1 = self._cell_pos(mc1, mr1)
        gc2, gr2 = self._cell_pos(mc2, mr2)
        return (gc1 + gc2) // 2, (gr1 + gr2) // 2

    def _in_bounds(self, mc, mr):
        return 0 <= mc < self.maze_cols and 0 <= mr < self.maze_rows

    def _neighbors(self, mc, mr):
        for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nc, nr = mc + dc, mr + dr
            if self._in_bounds(nc, nr):
                yield nc, nr

    def _open_cell(self, grid, mc, mr):
        gc, gr = self._cell_pos(mc, mr)
        grid[gr][gc] = 0

    def _connect(self, grid, mc1, mr1, mc2, mr2):
        """Open the wall between two adjacent maze cells."""
        wx, wy = self._wall_pos(mc1, mr1, mc2, mr2)
        grid[wy][wx] = 0

    def _open_all_cells(self, grid):
        for mc in range(self.maze_cols):
            for mr in range(self.maze_rows):
                self._open_cell(grid, mc, mr)

    def _open_all_connections(self, grid):
        for mc in range(self.maze_cols):
            for mr in range(self.maze_rows):
                if mc + 1 < self.maze_cols:
                    self._connect(grid, mc, mr, mc + 1, mr)
                if mr + 1 < self.maze_rows:
                    self._connect(grid, mc, mr, mc, mr + 1)

    def _close_wall(self, grid, mc1, mr1, mc2, mr2):
        wx, wy = self._wall_pos(mc1, mr1, mc2, mr2)
        grid[wy][wx] = 1

    # -- Public API --

    def generate(self, algorithm=None):
        """Generate a maze. If algorithm is None, pick randomly."""
        if algorithm is None:
            algorithm = random.choice(ALGORITHMS)
        methods = {
            "recursive_backtracker": self._recursive_backtracker,
            "prims": self._prims,
            "kruskals": self._kruskals,
            "recursive_division": self._recursive_division,
            "ellers": self._ellers,
            "binary_tree": self._binary_tree,
        }
        grid = methods[algorithm]()
        return self._pad(grid)

    @staticmethod
    def find_distant_pair(matrix):
        """Find two open cells far apart using double-BFS (approximate diameter)."""
        rows = len(matrix)
        cols = len(matrix[0])
        open_cells = [
            (c, r) for r in range(rows) for c in range(cols)
            if matrix[r][c] == 0
        ]
        if len(open_cells) < 2:
            return open_cells[0], open_cells[-1]

        def bfs_farthest(start):
            visited = {start}
            queue = deque([(start, 0)])
            farthest, max_dist = start, 0
            while queue:
                (cx, cy), dist = queue.popleft()
                if dist > max_dist:
                    max_dist = dist
                    farthest = (cx, cy)
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nb = (cx + dx, cy + dy)
                    if (0 <= nb[0] < cols and 0 <= nb[1] < rows
                            and matrix[nb[1]][nb[0]] == 0
                            and nb not in visited):
                        visited.add(nb)
                        queue.append((nb, dist + 1))
            return farthest

        start = random.choice(open_cells)
        far1 = bfs_farthest(start)
        far2 = bfs_farthest(far1)
        return far1, far2

    # -- Algorithms --

    def _recursive_backtracker(self):
        """DFS: long winding corridors, river-like paths."""
        grid = self._new_grid()
        visited = set()
        start = (random.randrange(self.maze_cols), random.randrange(self.maze_rows))
        stack = [start]
        visited.add(start)
        self._open_cell(grid, *start)

        while stack:
            mc, mr = stack[-1]
            unvisited = [
                (nc, nr) for nc, nr in self._neighbors(mc, mr)
                if (nc, nr) not in visited
            ]
            if unvisited:
                nc, nr = random.choice(unvisited)
                self._open_cell(grid, nc, nr)
                self._connect(grid, mc, mr, nc, nr)
                visited.add((nc, nr))
                stack.append((nc, nr))
            else:
                stack.pop()
        return grid

    def _prims(self):
        """Randomized Prim's: many short dead ends, bushy layout."""
        grid = self._new_grid()
        in_maze = set()

        start = (random.randrange(self.maze_cols), random.randrange(self.maze_rows))
        in_maze.add(start)
        self._open_cell(grid, *start)

        frontier = [(nc, nr, start[0], start[1])
                     for nc, nr in self._neighbors(*start)]

        while frontier:
            idx = random.randrange(len(frontier))
            nc, nr, fc, fr = frontier[idx]
            frontier[idx] = frontier[-1]
            frontier.pop()

            if (nc, nr) in in_maze:
                continue

            in_maze.add((nc, nr))
            self._open_cell(grid, nc, nr)
            self._connect(grid, fc, fr, nc, nr)

            for nnc, nnr in self._neighbors(nc, nr):
                if (nnc, nnr) not in in_maze:
                    frontier.append((nnc, nnr, nc, nr))

        return grid

    def _kruskals(self):
        """Randomized Kruskal's: spiky, many short dead ends."""
        grid = self._new_grid()
        self._open_all_cells(grid)

        parent = {}
        for mc in range(self.maze_cols):
            for mr in range(self.maze_rows):
                parent[(mc, mr)] = (mc, mr)

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
                return True
            return False

        edges = []
        for mc in range(self.maze_cols):
            for mr in range(self.maze_rows):
                if mc + 1 < self.maze_cols:
                    edges.append(((mc, mr), (mc + 1, mr)))
                if mr + 1 < self.maze_rows:
                    edges.append(((mc, mr), (mc, mr + 1)))
        random.shuffle(edges)

        for (mc1, mr1), (mc2, mr2) in edges:
            if union((mc1, mr1), (mc2, mr2)):
                self._connect(grid, mc1, mr1, mc2, mr2)

        return grid

    def _recursive_division(self):
        """Recursive division: long straight walls, open feel."""
        grid = self._new_grid()
        self._open_all_cells(grid)
        self._open_all_connections(grid)

        def divide(x1, y1, x2, y2):
            w, h = x2 - x1, y2 - y1
            if w < 2 and h < 2:
                return

            if w > h:
                horizontal = False
            elif h > w:
                horizontal = True
            else:
                horizontal = random.choice([True, False])

            if horizontal and h >= 2:
                wy = random.randint(y1, y2 - 2)
                for mc in range(x1, x2):
                    self._close_wall(grid, mc, wy, mc, wy + 1)
                passage = random.randint(x1, x2 - 1)
                self._connect(grid, passage, wy, passage, wy + 1)
                divide(x1, y1, x2, wy + 1)
                divide(x1, wy + 1, x2, y2)

            elif not horizontal and w >= 2:
                wx = random.randint(x1, x2 - 2)
                for mr in range(y1, y2):
                    self._close_wall(grid, wx, mr, wx + 1, mr)
                passage = random.randint(y1, y2 - 1)
                self._connect(grid, wx, passage, wx + 1, passage)
                divide(x1, y1, wx + 1, y2)
                divide(wx + 1, y1, x2, y2)

        divide(0, 0, self.maze_cols, self.maze_rows)
        return grid

    def _ellers(self):
        """Eller's: balanced maze, memory-efficient row-by-row generation."""
        grid = self._new_grid()
        self._open_all_cells(grid)

        set_of = list(range(self.maze_cols))
        next_set = self.maze_cols

        for mr in range(self.maze_rows):
            # Randomly merge adjacent cells in different sets
            for mc in range(self.maze_cols - 1):
                if set_of[mc] != set_of[mc + 1]:
                    if mr == self.maze_rows - 1 or random.random() < 0.5:
                        old_id = set_of[mc + 1]
                        new_id = set_of[mc]
                        for i in range(self.maze_cols):
                            if set_of[i] == old_id:
                                set_of[i] = new_id
                        self._connect(grid, mc, mr, mc + 1, mr)

            # Downward connections (skip last row)
            if mr < self.maze_rows - 1:
                groups = {}
                for mc in range(self.maze_cols):
                    groups.setdefault(set_of[mc], []).append(mc)

                new_set_of = [0] * self.maze_cols
                for sid, members in groups.items():
                    random.shuffle(members)
                    down_count = random.randint(1, len(members))
                    for mc in members[:down_count]:
                        self._connect(grid, mc, mr, mc, mr + 1)
                        new_set_of[mc] = sid
                    for mc in members[down_count:]:
                        new_set_of[mc] = next_set
                        next_set += 1

                set_of = new_set_of

        return grid

    def _binary_tree(self):
        """Binary tree: strong NW diagonal bias, trivially simple."""
        grid = self._new_grid()
        self._open_all_cells(grid)

        for mc in range(self.maze_cols):
            for mr in range(self.maze_rows):
                choices = []
                if mc > 0:
                    choices.append((mc - 1, mr))
                if mr > 0:
                    choices.append((mc, mr - 1))
                if choices:
                    nc, nr = random.choice(choices)
                    self._connect(grid, mc, mr, nc, nr)

        return grid
