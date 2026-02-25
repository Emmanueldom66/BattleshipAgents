import tkinter as tk
from tkinter import messagebox, font as tkfont
from GameSettings.bs_settings import *
from GameController.bs_controller import GameController

# ─────────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────────
class BattleshipGUI:
    """Full tkinter GUI for Battleship."""

    def __init__(self, root=None):
        self.root = root if root else tk.Tk()
        self.root.title("Battleship — AI Agents")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        self.controller   = None
        self.ai_delay_ms  = 600   # ms between AI shots in ai_vs_ai
        self._after_id    = None

        self._show_menu()
        self.root.mainloop()

    # ── Menu Screen ───────────────────────────
    def _show_menu(self):
        self._clear_window()
        frame = tk.Frame(self.root, bg=BG_DARK, padx=40, pady=40)
        frame.pack()

        title_font = tkfont.Font(family="Courier New", size=24, weight="bold")
        sub_font   = tkfont.Font(family="Courier New", size=13)
        btn_font   = tkfont.Font(family="Courier New", size=12, weight="bold")

        tk.Label(frame, text="⚓ BATTLESHIP Strait of Hormuz", font=title_font,
                fg=ACCENT, bg=BG_DARK).pack(pady=(0, 6))
        tk.Label(frame, text="AI Agents Edition", font=sub_font,
                fg=TEXT_COLOR, bg=BG_DARK).pack(pady=(0, 30))

        # Mode buttons
        modes = [
            ("Human  vs  Simple Reflex AI", "human_vs_ai", "reflex"),
            ("Human  vs  Goal-Based AI",    "human_vs_ai", "goal"),
            ("Simple Reflex  vs  Goal-Based  (AI v AI)", "ai_vs_ai", "both"),
        ]
        for label, mode, ai in modes:
            b = tk.Button(frame, text=label, font=btn_font,
                        bg=BTN_COLOR, fg=TEXT_COLOR,
                        activebackground=BTN_HOVER, activeforeground=TEXT_COLOR,
                        relief="flat", padx=20, pady=10, cursor="hand2",
                        command=lambda m=mode, a=ai: self._start_game(m, a))
            b.pack(fill="x", pady=6)
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg=BTN_HOVER))
            b.bind("<Leave>", lambda e, btn=b: btn.config(bg=BTN_COLOR))

        # Speed slider for ai_vs_ai
        tk.Label(frame, text="AI-vs-AI shot delay (ms):", font=sub_font,
                fg=TEXT_COLOR, bg=BG_DARK).pack(pady=(20, 4))
        self.delay_var = tk.IntVar(value=600)
        tk.Scale(frame, from_=100, to=2000, orient="horizontal",
                variable=self.delay_var,
                bg=BG_MID, fg=TEXT_COLOR, troughcolor=SEA_EMPTY,
                highlightbackground=BG_DARK, length=300).pack()
    def _start_game(self, mode: str, ai_type: str):
        self.ai_delay_ms = self.delay_var.get()
        if ai_type == "both":
            self.controller = GameController("ai_vs_ai")
        else:
            self.controller = GameController(mode, ai_type)
        self._build_game_screen()
        if mode == "ai_vs_ai":
            self._schedule_ai_turn()

    # ── Game Screen ───────────────────────────
    def _build_game_screen(self):
        self._clear_window()
        ctrl = self.controller

        header_font = tkfont.Font(family="Courier New", size=12, weight="bold")
        label_font  = tkfont.Font(family="Courier New", size=10)

        top = tk.Frame(self.root, bg=BG_DARK)
        top.pack(pady=10)

        # ── determine board labels ──
        if ctrl.mode == "human_vs_ai":
            p1_label = "YOUR FLEET"
            p2_label = f"ENEMY FLEET  [{ctrl.agent_p2.name}]"
        else:
            p1_label = f"[ {ctrl.agent_p2.name} ]"
            p2_label = f"[ {ctrl.agent_p1.name} ]"

        # Status bar
        self.status_var = tk.StringVar(value="Your turn — click the enemy grid!")
        tk.Label(top, textvariable=self.status_var, font=header_font,
                fg=ACCENT, bg=BG_DARK).pack()

        boards_frame = tk.Frame(self.root, bg=BG_DARK)
        boards_frame.pack(padx=20, pady=6)

        # ── Left board (P1) ──
        left = tk.Frame(boards_frame, bg=BG_DARK)
        left.grid(row=0, column=0, padx=20)
        tk.Label(left, text=p1_label, font=header_font,
                fg=TEXT_COLOR, bg=BG_DARK).pack(pady=(0, 4))
        self.canvas_p1 = self._make_canvas(left)
        self.canvas_p1.pack()
        self.shots_label_p1 = tk.Label(left, text="Shots: 0",
                                    font=label_font, fg=TEXT_COLOR, bg=BG_DARK)
        self.shots_label_p1.pack(pady=4)

        # ── Right board (P2 / enemy) ──
        right = tk.Frame(boards_frame, bg=BG_DARK)
        right.grid(row=0, column=1, padx=20)
        tk.Label(right, text=p2_label, font=header_font,
                fg=TEXT_COLOR, bg=BG_DARK).pack(pady=(0, 4))
        self.canvas_p2 = self._make_canvas(right)
        self.canvas_p2.pack()
        self.shots_label_p2 = tk.Label(right, text="Shots: 0",
                                    font=label_font, fg=TEXT_COLOR, bg=BG_DARK)
        self.shots_label_p2.pack(pady=4)

        # ── Legend ──
        leg = tk.Frame(self.root, bg=BG_DARK)
        leg.pack(pady=6)
        for color, text in [(HIT_COLOR, "Hit"), (MISS_COLOR, "Miss"),
                            (SHIP_COLOR, "Your Ship"), (SUNK_COLOR, "Sunk")]:
            box = tk.Frame(leg, bg=color, width=16, height=16)
            box.pack(side="left", padx=4)
            tk.Label(leg, text=text, font=label_font,
                    fg=TEXT_COLOR, bg=BG_DARK).pack(side="left", padx=(0, 10))

        # ── Menu button ──
        tk.Button(self.root, text="⟵ Menu",
                font=tkfont.Font(family="Courier New", size=10, weight="bold"),
                bg=BTN_COLOR, fg=TEXT_COLOR, relief="flat",
                padx=12, pady=6, cursor="hand2",
                command=self._back_to_menu).pack(pady=10)

        # Bind human clicks only on enemy (p2) canvas
        if ctrl.mode == "human_vs_ai":
            self.canvas_p2.bind("<Button-1>", self._on_human_click)
            self.canvas_p2.bind("<Motion>",   self._on_hover)
            self.canvas_p2.bind("<Leave>",    self._on_leave)

        self._draw_board(self.canvas_p1, ctrl.board_p1, show_ships=True)
        self._draw_board(self.canvas_p2, ctrl.board_p2, show_ships=False)

        if ctrl.mode == "ai_vs_ai":
            self.status_var.set(
                f"{ctrl.agent_p1.name}  vs  {ctrl.agent_p2.name} — Watch the battle!")

    def _make_canvas(self, parent) -> tk.Canvas:
        size = CELL_SIZE * GRID_SIZE + 1
        c = tk.Canvas(parent, width=size + CELL_SIZE, height=size + CELL_SIZE,
                    bg=BG_MID, highlightthickness=0)
        # Draw column labels (A–J)
        for i in range(GRID_SIZE):
            c.create_text(CELL_SIZE + i*CELL_SIZE + CELL_SIZE//2, CELL_SIZE//2,
                        text=chr(65+i), fill=TEXT_COLOR,
                        font=("Courier New", 9, "bold"))
        # Draw row labels (1–10)
        for i in range(GRID_SIZE):
            c.create_text(CELL_SIZE//2, CELL_SIZE + i*CELL_SIZE + CELL_SIZE//2,
                        text=str(i+1), fill=TEXT_COLOR,
                        font=("Courier New", 9, "bold"))
        return c

    def _draw_board(self, canvas: tk.Canvas, board: Board, show_ships: bool,
                    highlight: tuple = None):
        """Redraw a board canvas from scratch."""
        canvas.delete("cell")
        ox, oy = CELL_SIZE, CELL_SIZE  # offset for labels

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x1 = ox + c*CELL_SIZE
                y1 = oy + r*CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                shot = board.shots[r][c]
                ship = board.ships[r][c]

                # Determine fill colour
                if shot == "hit":
                    # Check if ship sunk
                    if ship and all(board.shots[sr][sc] == "hit"
                                    for sr, sc in board.ship_cells[ship]):
                        fill = SUNK_COLOR
                    else:
                        fill = HIT_COLOR
                elif shot == "miss":
                    fill = MISS_COLOR
                elif show_ships and ship:
                    fill = SHIP_COLOR
                else:
                    fill = SEA_EMPTY

                if highlight == (r, c):
                    fill = SEA_HOVER

                canvas.create_rectangle(x1+1, y1+1, x2-1, y2-1,
                                        fill=fill, outline=BG_MID,
                                        width=1, tags="cell")

                # Dot marker for hit/miss
                if shot == "hit":
                    cx, cy = (x1+x2)//2, (y1+y2)//2
                    canvas.create_oval(cx-7, cy-7, cx+7, cy+7,
                                    fill="white", outline="", tags="cell")
                elif shot == "miss":
                    cx, cy = (x1+x2)//2, (y1+y2)//2
                    canvas.create_oval(cx-4, cy-4, cx+4, cy+4,
                                    fill=BG_MID, outline="", tags="cell")

    def _pixel_to_cell(self, x: int, y: int) -> tuple | None:
        ox, oy = CELL_SIZE, CELL_SIZE
        c = (x - ox) // CELL_SIZE
        r = (y - oy) // CELL_SIZE
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            return r, c
        return None

    # ── Human interaction ─────────────────────
    def _on_human_click(self, event):
        cell = self._pixel_to_cell(event.x, event.y)
        if not cell:
            return
        r, c = cell
        ctrl = self.controller
        if ctrl.game_over:
            return

        result = ctrl.human_shoot(r, c)

        if result == "already":
            self.status_var.set("Already tried that cell!")
            return

        self._draw_board(self.canvas_p2, ctrl.board_p2, show_ships=False)
        self._update_shot_counts()

        if ctrl.game_over:
            self._show_winner()
            return

        # AI's turn
        self.status_var.set("AI is thinking…")
        self.root.update()
        self.root.after(400, self._run_ai_turn)

    def _on_hover(self, event):
        cell = self._pixel_to_cell(event.x, event.y)
        ctrl = self.controller
        if cell and ctrl and not ctrl.game_over:
            r, c = cell
            if ctrl.board_p2.shots[r][c] is None:
                self._draw_board(self.canvas_p2, ctrl.board_p2,
                                show_ships=False, highlight=cell)

    def _on_leave(self, event):
        if self.controller:
            self._draw_board(self.canvas_p2, self.controller.board_p2,
                            show_ships=False)

    def _run_ai_turn(self):
        ctrl = self.controller
        if ctrl.game_over:
            return
        r, c, result = ctrl.ai_shoot()
        self._draw_board(self.canvas_p1, ctrl.board_p1, show_ships=True)
        self._update_shot_counts()

        if ctrl.game_over:
            self._show_winner()
            return

        self.status_var.set(f"AI fired at {chr(65+c)}{r+1} → {result}. Your turn!")

    # ── AI vs AI loop ─────────────────────────
    def _schedule_ai_turn(self):
        self._after_id = self.root.after(self.ai_delay_ms, self._ai_vs_ai_step)

    def _ai_vs_ai_step(self):
        ctrl = self.controller
        if ctrl.game_over:
            return

        r, c, result = ctrl.ai_shoot()
        canvas = self.canvas_p1 if ctrl.turn == "p1" else self.canvas_p2
        # Refresh both boards
        self._draw_board(self.canvas_p1, ctrl.board_p1, show_ships=True)
        self._draw_board(self.canvas_p2, ctrl.board_p2, show_ships=True)
        self._update_shot_counts()

        who = ctrl.agent_p1.name if ctrl.turn == "p2" else ctrl.agent_p2.name
        self.status_var.set(
            f"{who} fired {chr(65+c)}{r+1} → {result}")

        if ctrl.game_over:
            self._show_winner()
        else:
            self._schedule_ai_turn()

    # ── Utilities ─────────────────────────────
    def _update_shot_counts(self):
        ctrl = self.controller
        self.shots_label_p1.config(text=f"Shots: {ctrl.shot_count['p1']}")
        self.shots_label_p2.config(text=f"Shots: {ctrl.shot_count['p2']}")

    def _show_winner(self):
        ctrl = self.controller
        w = ctrl.winner
        if ctrl.mode == "human_vs_ai":
            msg = "🎉 You win!" if w == "p1" else f"💀 {ctrl.agent_p2.name} wins!"
        else:
            msg = (f"🏆 {ctrl.agent_p1.name} wins!"
                if w == "p1" else f"🏆 {ctrl.agent_p2.name} wins!")

        shots_p1 = ctrl.shot_count["p1"]
        shots_p2 = ctrl.shot_count["p2"]
        detail = f"\nShots fired — P1: {shots_p1}  |  P2: {shots_p2}"
        self.status_var.set(msg + detail)
        messagebox.showinfo("Game Over", msg + detail)

    def _back_to_menu(self):
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self._show_menu()

    def _clear_window(self):
        for w in self.root.winfo_children():
            w.destroy()