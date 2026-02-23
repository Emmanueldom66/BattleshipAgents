from GameSettings.bs_settings import Board, GRID_SIZE, SHIPS
from GameModes.bs_gameModes import SimpleReflexAgent, GoalBasedAgent


# ─────────────────────────────────────────────
#  GAME CONTROLLER
# ─────────────────────────────────────────────
class GameController:
    """Manages game state and turn logic for all modes."""

    def __init__(self, mode: str, ai_type: str = "goal"):
        """
        mode    : 'human_vs_ai' | 'ai_vs_ai'
        ai_type : 'reflex' | 'goal'  (ignored in ai_vs_ai mode)
        """
        self.mode     = mode
        self.board_p1 = Board()   # Human or Reflex Agent
        self.board_p2 = Board()   # Goal-Based or specified AI

        self.board_p1.place_ships_randomly()
        self.board_p2.place_ships_randomly()

        # Assign agents
        if mode == "human_vs_ai":
            self.agent_p2 = GoalBasedAgent() if ai_type == "goal" \
                            else SimpleReflexAgent()
            self.agent_p1 = None  # Human
        else:  # ai_vs_ai
            self.agent_p1 = SimpleReflexAgent()
            self.agent_p2 = GoalBasedAgent()

        self.turn        = "p1"   # whose turn
        self.game_over   = False
        self.winner      = None
        self.shot_count  = {"p1": 0, "p2": 0}

    def human_shoot(self, r: int, c: int) -> str:
        """Process a human shot at opponent board (board_p2)."""
        if self.game_over or self.turn != "p1":
            return "not_your_turn"
        result = self.board_p2.receive_shot(r, c)
        if result != "already":
            self.shot_count["p1"] += 1
            if self.board_p2.all_sunk():
                self.game_over = True
                self.winner    = "p1"
            else:
                self.turn = "p2"
        return result

    def ai_shoot(self) -> tuple:
        """Let the current AI agent fire. Returns (r, c, result)."""
        if self.game_over:
            return None

        if self.turn == "p1":
            agent = self.agent_p1
            target_board = self.board_p2
        else:
            agent = self.agent_p2
            target_board = self.board_p1

        r, c   = agent.choose_shot(target_board)
        result = target_board.receive_shot(r, c)
        agent.receive_result(r, c, result)
        self.shot_count[self.turn] += 1

        if target_board.all_sunk():
            self.game_over = True
            self.winner    = self.turn
        else:
            self.turn = "p2" if self.turn == "p1" else "p1"

        return r, c, result
