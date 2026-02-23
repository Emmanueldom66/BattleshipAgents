import random

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
GRID_SIZE    = 10
CELL_SIZE    = 40
SHIPS        = {"Carrier": 5, "Battleship": 4, "Cruiser": 3,
                "Submarine": 3, "Destroyer": 2}

# Colours
BG_DARK      = "#0d1b2a"
BG_MID       = "#1b2a3b"
SEA_EMPTY    = "#1e3a5f"
SEA_HOVER    = "#2a5f8f"
HIT_COLOR    = "#e63946"
MISS_COLOR   = "#457b9d"
SHIP_COLOR   = "#a8dadc"
SUNK_COLOR   = "#6d0000"
TEXT_COLOR   = "#f1faee"
ACCENT       = "#e9c46a"
BTN_COLOR    = "#264653"
BTN_HOVER    = "#2a9d8f"


# ─────────────────────────────────────────────
#  BOARD  (shared game logic)
# ─────────────────────────────────────────────
class Board:
    """Represents a single player's board: ship placement + shot tracking."""

    def __init__(self):
        # 'ship' grid: None or ship-name per cell
        self.ships   = [[None]*GRID_SIZE for _ in range(GRID_SIZE)]
        # 'shot' grid: None | 'hit' | 'miss'
        self.shots   = [[None]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.ship_cells: dict[str, list] = {}   # ship_name -> [(r,c), ...]

    def place_ships_randomly(self):
        """Place all ships at random valid positions."""
        for name, length in SHIPS.items():
            placed = False
            while not placed:
                horizontal = random.choice([True, False])
                if horizontal:
                    r = random.randint(0, GRID_SIZE - 1)
                    c = random.randint(0, GRID_SIZE - length)
                    cells = [(r, c + i) for i in range(length)]
                else:
                    r = random.randint(0, GRID_SIZE - length)
                    c = random.randint(0, GRID_SIZE - 1)
                    cells = [(r + i, c) for i in range(length)]

                if all(self.ships[r][c] is None for r, c in cells):
                    for r, c in cells:
                        self.ships[r][c] = name
                    self.ship_cells[name] = cells
                    placed = True

    def receive_shot(self, r: int, c: int) -> str:
        """Process an incoming shot.  Returns 'hit', 'miss', or 'sunk:<name>'."""
        if self.shots[r][c] is not None:
            return "already"
        ship = self.ships[r][c]
        if ship:
            self.shots[r][c] = "hit"
            # Check if entire ship is sunk
            if all(self.shots[sr][sc] == "hit"
                    for sr, sc in self.ship_cells[ship]):
                return f"sunk:{ship}"
            return "hit"
        else:
            self.shots[r][c] = "miss"
            return "miss"

    def all_sunk(self) -> bool:
        return all(self.shots[r][c] == "hit"
                    for name in self.ship_cells
                    for r, c in self.ship_cells[name])