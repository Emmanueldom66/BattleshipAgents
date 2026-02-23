
from GameSettings.bs_settings import Board, GRID_SIZE, SHIPS
import random

# ─────────────────────────────────────────────
#  SIMPLE REFLEX AGENT
# ─────────────────────────────────────────────
class SimpleReflexAgent:
    """
    Fires at a random cell that has not been shot yet.
    No memory of results — the only 'rule' is: avoid repeating shots.
    This is the simplest possible rational agent.
    """

    def __init__(self):
        self.name = "Simple Reflex Agent"
        # The only 'percept' used is the set of already-shot cells
        self.untried = [(r, c) for r in range(GRID_SIZE)
                                for c in range(GRID_SIZE)]
        random.shuffle(self.untried)

    def choose_shot(self, opponent_board: Board) -> tuple:
        """Return (row, col) to fire at — purely random from unvisited cells."""
        # Filter to cells not yet shot (defensive re-sync with real board state)
        available = [(r, c) for r, c in self.untried
                    if opponent_board.shots[r][c] is None]
        if not available:
            # Fallback: scan whole board
            available = [(r, c) for r in range(GRID_SIZE)
                                    for c in range(GRID_SIZE)
                                    if opponent_board.shots[r][c] is None]
        choice = random.choice(available)
        return choice

    def receive_result(self, r: int, c: int, result: str):
        """Simple reflex: ignore the result entirely — no learning."""
        pass  # intentionally empty — this agent has no state update


# ─────────────────────────────────────────────
#  GOAL-BASED AGENT
# ─────────────────────────────────────────────
class GoalBasedAgent:
    """
    Two-phase strategy:

    HUNT phase  — fires at high-probability cells derived from a density map.
                  The map counts how many valid ship placements cover each cell.
    TARGET phase — after a hit, fires at adjacent cells until the ship sinks,
                   then returns to HUNT.

    The agent maintains a goal (sink all ships) and uses internal state to plan.
    """

    def __init__(self):
        self.name = "Goal-Based Agent"
        self.mode        = "hunt"          # 'hunt' or 'target'
        self.hit_stack   = []              # cells hit but ship not yet sunk
        self.tried_dirs  = {}             # cell -> tried directions list

    # ── Public interface ──────────────────────
    def choose_shot(self, opponent_board: Board) -> tuple:
        if self.mode == "target" and self.hit_stack:
            return self._target_shot(opponent_board)
        return self._hunt_shot(opponent_board)

    def receive_result(self, r: int, c: int, result: str):
        """Update internal state based on the outcome of the last shot."""
        if result == "hit":
            self.mode = "target"
            self.hit_stack.append((r, c))
        elif result.startswith("sunk"):
            # Ship sunk — remove those cells from stack and return to hunt
            self.hit_stack.clear()
            self.mode = "hunt"
        # miss: if targeting, stay in target mode to try another direction

    # ── Hunt phase ────────────────────────────
    def _hunt_shot(self, board: Board) -> tuple:
        """
        Build a probability density map.
        For each ship still alive, slide it horizontally and vertically
        over the board.  Each valid placement increments those cells.
        The agent then picks the cell with the highest score.
        """
        density = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        remaining_ships = self._remaining_ships(board)

        for length in remaining_ships:
            # Horizontal placements
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE - length + 1):
                    cells = [(r, c + i) for i in range(length)]
                    if self._placement_valid(board, cells):
                        for cr, cc in cells:
                            density[cr][cc] += 1
            # Vertical placements
            for r in range(GRID_SIZE - length + 1):
                for c in range(GRID_SIZE):
                    cells = [(r + i, c) for i in range(length)]
                    if self._placement_valid(board, cells):
                        for cr, cc in cells:
                            density[cr][cc] += 1

        # Pick unshot cell with maximum density score
        best_score = -1
        best_cells = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board.shots[r][c] is None:
                    if density[r][c] > best_score:
                        best_score = density[r][c]
                        best_cells = [(r, c)]
                    elif density[r][c] == best_score:
                        best_cells.append((r, c))

        return random.choice(best_cells) if best_cells else self._fallback(board)

    # ── Target phase ──────────────────────────
    def _target_shot(self, board: Board) -> tuple:
        """
        Try cells adjacent to known hits.
        If multiple hits are in a line, extend that line first.
        """
        # If 2+ hits exist, try to continue the line
        if len(self.hit_stack) >= 2:
            shot = self._continue_line(board)
            if shot:
                return shot

        # Otherwise try any neighbor of any hit cell
        for hr, hc in reversed(self.hit_stack):
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = hr + dr, hc + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                    if board.shots[nr][nc] is None:
                        return nr, nc

        # No adjacent cell available — fallback to hunt
        self.mode = "hunt"
        self.hit_stack.clear()
        return self._hunt_shot(board)

    def _continue_line(self, board: Board) -> tuple | None:
        """Extend an existing line of hits in both directions."""
        rows = sorted(set(r for r, c in self.hit_stack))
        cols = sorted(set(c for r, c in self.hit_stack))

        if len(rows) == 1:
            # Horizontal line — extend left/right
            r = rows[0]
            for c in [min(cols) - 1, max(cols) + 1]:
                if 0 <= c < GRID_SIZE and board.shots[r][c] is None:
                    return r, c
        elif len(cols) == 1:
            # Vertical line — extend up/down
            c = cols[0]
            for r in [min(rows) - 1, max(rows) + 1]:
                if 0 <= r < GRID_SIZE and board.shots[r][c] is None:
                    return r, c
        return None

    # ── Helpers ───────────────────────────────
    def _remaining_ships(self, board: Board) -> list:
        """Return lengths of ships not yet fully sunk on the opponent board."""
        sunk = set()
        for name, cells in board.ship_cells.items():
            if all(board.shots[r][c] == "hit" for r, c in cells):
                sunk.add(name)
        return [l for n, l in SHIPS.items() if n not in sunk]

    def _placement_valid(self, board: Board, cells: list) -> bool:
        """A ship placement is valid if no cell in it has been shot 'miss'."""
        return all(board.shots[r][c] != "miss" for r, c in cells)

    def _fallback(self, board: Board) -> tuple:
        available = [(r, c) for r in range(GRID_SIZE)
                                for c in range(GRID_SIZE)
                                if board.shots[r][c] is None]
        return random.choice(available)
