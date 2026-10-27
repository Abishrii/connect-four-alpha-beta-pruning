"""Graphical Connect Four UI using Tkinter (standard library).
Run with: python gui.py
The search algorithms remain in connect_four.py.
"""
import tkinter as tk
from tkinter import messagebox

from connect_four import (
    ROWS, COLS, EMPTY, HUMAN, AI,
    new_board, legal_moves, drop_piece, winning_piece, is_draw,
    choose_ai_move,
)

# Display palette
BG = "#101827"
PANEL = "#18243a"
BOARD_BLUE = "#2458a6"
EMPTY_HOLE = "#0b1424"
HUMAN_COLOR = "#ff5c68"
AI_COLOR = "#ffd166"
TEXT = "#f4f7fb"
MUTED = "#a9b8ce"

CELL = 76
PAD = 14
BOARD_W = COLS * CELL + PAD * 2
BOARD_H = ROWS * CELL + PAD * 2


def winning_cells(board):
    """Return coordinates of four consecutive winning cells, or an empty set."""
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == EMPTY:
                continue
            for dr, dc in directions:
                cells = [(r + i * dr, c + i * dc) for i in range(4)]
                if all(0 <= rr < ROWS and 0 <= cc < COLS for rr, cc in cells):
                    if all(board[rr][cc] == piece for rr, cc in cells):
                        return set(cells)
    return set()


class ConnectFourGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect Four | Minimax + Alpha-Beta Pruning")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.board = new_board()
        self.depth = tk.IntVar(value=4)
        self.busy = False
        self.finished = False
        self.last_stats = None

        title = tk.Label(root, text="CONNECT FOUR", font=("Segoe UI", 22, "bold"),
                         fg=TEXT, bg=BG)
        title.pack(pady=(14, 0))
        subtitle = tk.Label(root, text="MINIMAX  •  ALPHA-BETA PRUNING",
                            font=("Segoe UI", 10, "bold"), fg="#7dd3fc", bg=BG)
        subtitle.pack(pady=(2, 10))

        top = tk.Frame(root, bg=PANEL, padx=12, pady=9)
        top.pack(fill="x", padx=16)
        tk.Label(top, text="Search depth", fg=TEXT, bg=PANEL,
                 font=("Segoe UI", 10)).pack(side="left")
        self.depth_box = tk.Spinbox(top, from_=1, to=6, width=4, textvariable=self.depth,
                                    font=("Segoe UI", 10), justify="center")
        self.depth_box.pack(side="left", padx=(8, 16))
        tk.Label(top, text="You: red", fg=HUMAN_COLOR, bg=PANEL,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=4)
        tk.Label(top, text="AI: yellow", fg=AI_COLOR, bg=PANEL,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=4)

        self.status = tk.Label(root, text="Your turn — click a column to drop a red disc.",
                               fg=TEXT, bg=BG, font=("Segoe UI", 11, "bold"),
                               wraplength=BOARD_W, pady=10)
        self.status.pack()

        self.canvas = tk.Canvas(root, width=BOARD_W, height=BOARD_H,
                                bg=BOARD_BLUE, highlightthickness=0, cursor="hand2")
        self.canvas.pack(padx=16)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)

        self.stats = tk.Label(root,
            text="AI search stats will appear here after its move.",
            fg=MUTED, bg=BG, font=("Consolas", 10), justify="left", pady=9)
        self.stats.pack()

        self.comparison = tk.Label(
            root,
            text="Algorithm comparison will appear after the AI move.",
            fg=TEXT, bg=PANEL, font=("Consolas", 10), justify="left",
            padx=12, pady=8
        )
        self.comparison.pack(fill="x", padx=18, pady=(0, 8))

        buttons = tk.Frame(root, bg=BG)
        buttons.pack(pady=(0, 14))
        tk.Button(buttons, text="New Game", command=self.new_game,
                  font=("Segoe UI", 10, "bold"), bg="#7dd3fc", fg=BG,
                  activebackground="#bae6fd", relief="flat", padx=16, pady=7).pack(side="left", padx=5)
        tk.Button(buttons, text="Quit", command=root.destroy,
                  font=("Segoe UI", 10), bg=PANEL, fg=TEXT,
                  activebackground="#263650", relief="flat", padx=16, pady=7).pack(side="left", padx=5)

        self.draw_board()

    def draw_board(self, hover_col=None):
        self.canvas.delete("all")
        winners = winning_cells(self.board)
        # Column numbers make the clickable target clear.
        for c in range(COLS):
            x = PAD + c * CELL + CELL / 2
            self.canvas.create_text(x, 7, text=str(c + 1), fill="#e8f1ff",
                                    font=("Segoe UI", 9, "bold"), anchor="n")
        for r in range(ROWS):
            for c in range(COLS):
                x0 = PAD + c * CELL + 8
                y0 = PAD + r * CELL + 8
                x1, y1 = x0 + CELL - 16, y0 + CELL - 16
                piece = self.board[r][c]
                fill = HUMAN_COLOR if piece == HUMAN else AI_COLOR if piece == AI else EMPTY_HOLE
                is_winner = (r, c) in winners
                is_hover = hover_col == c and r == 0 and piece == EMPTY
                outline = "#ffffff" if is_winner or is_hover else fill
                width = 4 if is_winner else 2 if is_hover else 0
                self.canvas.create_oval(x0, y0, x1, y1, fill=fill,
                                        outline=outline, width=width)

    def on_motion(self, event):
        col = (event.x - PAD) // CELL
        if 0 <= col < COLS and not self.busy and not self.finished:
            self.draw_board(hover_col=int(col))

    def on_click(self, event):
        if self.busy or self.finished:
            return

        # Validate the search depth before changing the board. Otherwise, an
        # invalid value could consume the human's move without letting the AI reply.
        try:
            depth = int(self.depth.get())
            if not 1 <= depth <= 6:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Invalid depth", "Choose a search depth from 1 to 6.")
            self.depth.set(4)
            return

        col = int((event.x - PAD) // CELL)
        if col < 0 or col >= COLS:
            return
        if not drop_piece(self.board, col, HUMAN):
            self.status.config(text="That column is full. Choose another column.")
            return
        self.draw_board()
        if winning_piece(self.board) == HUMAN:
            self.finish("You win! Four red discs in a row.")
            return
        if is_draw(self.board):
            self.finish("It's a draw — the board is full.")
            return

        self.busy = True
        self.status.config(text="AI is thinking…")
        self.root.update_idletasks()
        # The human move has already been accepted and checked for a win/draw.
        # Therefore, the AI should only search a non-terminal board.
        try:
            # Compare both algorithms on exactly the same board and depth.
            mini_col, mini_score, mini_stats, mini_time = choose_ai_move(
                self.board, depth, use_alpha_beta=False
            )
            ai_col, score, stats, elapsed = choose_ai_move(
                self.board, depth, use_alpha_beta=True
            )
        except (ValueError, RuntimeError) as exc:
            self.busy = False
            self.status.config(text="AI could not find a move. Start a new game.")
            messagebox.showerror("AI move error", str(exc))
            return

        if mini_score != score:
            messagebox.showwarning(
                "Algorithm comparison", 
                "Minimax and Alpha-Beta returned different scores on this position. "
                "Please save this position for debugging."
            )

        reduction = ((mini_stats.nodes - stats.nodes) / mini_stats.nodes * 100) if mini_stats.nodes else 0.0
        self.comparison.config(text=(
            f"Algorithm comparison (same board, depth {depth})\n"
            f"Minimax:    {mini_stats.nodes:,} nodes | {mini_stats.leaves:,} leaves | {mini_time:.4f}s\n"
            f"Alpha-Beta: {stats.nodes:,} nodes | {stats.leaves:,} leaves | {stats.cutoffs:,} cutoffs | {elapsed:.4f}s\n"
            f"Node reduction: {reduction:.2f}% | Scores match: {'YES' if mini_score == score else 'NO'}"
        ))

        if not drop_piece(self.board, ai_col, AI):
            self.busy = False
            self.status.config(text="AI selected an invalid move. Start a new game.")
            messagebox.showerror("AI move error", "The AI selected a full or invalid column.")
            return
        self.last_stats = stats
        self.draw_board()
        self.stats.config(text=(
            f"AI move: column {ai_col + 1}    score: {score}\n"
            f"Nodes visited: {stats.nodes:,}    Leaves: {stats.leaves:,}    "
            f"Cutoffs: {stats.cutoffs:,}    Time: {elapsed:.4f}s"
        ))
        self.busy = False
        if winning_piece(self.board) == AI:
            self.finish("AI wins! Try again and look for a block.")
        elif is_draw(self.board):
            self.finish("It's a draw — the board is full.")
        else:
            self.status.config(text="Your turn — click a column to drop a red disc.")

    def finish(self, message):
        self.finished = True
        self.status.config(text=message)
        self.draw_board()

    def new_game(self):
        self.board = new_board()
        self.busy = False
        self.finished = False
        self.last_stats = None
        self.status.config(text="Your turn — click a column to drop a red disc.")
        self.stats.config(text="AI search stats will appear here after its move.")
        self.comparison.config(text="Algorithm comparison will appear after the AI move.")
        self.draw_board()


def main():
    root = tk.Tk()
    ConnectFourGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
