"""Connect Four: Minimax vs Alpha-Beta Pruning.

Run: python connect_four.py
No third-party packages required.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Optional

ROWS = 6
COLS = 7
EMPTY = "."
HUMAN = "X"
AI = "O"
WINDOW = 4


@dataclass
class SearchStats:
    nodes: int = 0
    leaves: int = 0
    cutoffs: int = 0


def new_board() -> list[list[str]]:
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def print_board(board: list[list[str]]) -> None:
    print("\n  " + " ".join(str(c + 1) for c in range(COLS)))
    for row in board:
        print("  " + " ".join(row))
    print()


def legal_moves(board: list[list[str]]) -> list[int]:
    return [c for c in range(COLS) if board[0][c] == EMPTY]


def drop_piece(board: list[list[str]], col: int, piece: str) -> bool:
    """Drop a piece into a column. Return False if the column is full/invalid."""
    if col < 0 or col >= COLS or board[0][col] != EMPTY:
        return False
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            board[r][col] = piece
            return True
    return False


def winning_piece(board: list[list[str]]) -> Optional[str]:
    """Return the winning piece, if any."""
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece == EMPTY:
                continue
            for dr, dc in directions:
                end_r, end_c = r + (WINDOW - 1) * dr, c + (WINDOW - 1) * dc
                if not (0 <= end_r < ROWS and 0 <= end_c < COLS):
                    continue
                if all(board[r + i * dr][c + i * dc] == piece for i in range(WINDOW)):
                    return piece
    return None


def is_draw(board: list[list[str]]) -> bool:
    return winning_piece(board) is None and not legal_moves(board)


def score_window(window: list[str], piece: str) -> int:
    opponent = HUMAN if piece == AI else AI
    own = window.count(piece)
    other = window.count(opponent)
    empty = window.count(EMPTY)
    if own == 4:
        return 100_000
    if own == 3 and empty == 1:
        return 120
    if own == 2 and empty == 2:
        return 12
    if other == 3 and empty == 1:
        return -150
    if other == 2 and empty == 2:
        return -10
    return 0


def evaluate_board(board: list[list[str]]) -> int:
    """Heuristic score from the AI (O) perspective; positive favors AI."""
    winner = winning_piece(board)
    if winner == AI:
        return 1_000_000
    if winner == HUMAN:
        return -1_000_000
    if is_draw(board):
        return 0

    score = 0
    # Center columns are strategically useful in Connect Four.
    center_col = [board[r][COLS // 2] for r in range(ROWS)]
    score += center_col.count(AI) * 6
    score -= center_col.count(HUMAN) * 6

    # Horizontal windows.
    for r in range(ROWS):
        for c in range(COLS - 3):
            score += score_window(board[r][c:c + 4], AI)
    # Vertical windows.
    for c in range(COLS):
        for r in range(ROWS - 3):
            score += score_window([board[r + i][c] for i in range(4)], AI)
    # Diagonal down-right windows.
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            score += score_window([board[r + i][c + i] for i in range(4)], AI)
    # Diagonal up-right windows.
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            score += score_window([board[r - i][c + i] for i in range(4)], AI)
    return score


def ordered_moves(board: list[list[str]]) -> list[int]:
    """Try central columns first to improve pruning; deterministic for fair tests."""
    center = COLS // 2
    return sorted(legal_moves(board), key=lambda c: (abs(c - center), c))


def minimax(board: list[list[str]], depth: int, maximizing: bool,
            stats: SearchStats) -> int:
    stats.nodes += 1
    winner = winning_piece(board)
    if depth == 0 or winner is not None or is_draw(board):
        stats.leaves += 1
        value = evaluate_board(board)
        # Prefer quicker wins and slower losses when searching terminal positions.
        if winner == AI:
            return value + depth
        if winner == HUMAN:
            return value - depth
        return value

    if maximizing:
        best = -math.inf
        for col in ordered_moves(board):
            child = [row[:] for row in board]
            drop_piece(child, col, AI)
            best = max(best, minimax(child, depth - 1, False, stats))
        return int(best)
    best = math.inf
    for col in ordered_moves(board):
        child = [row[:] for row in board]
        drop_piece(child, col, HUMAN)
        best = min(best, minimax(child, depth - 1, True, stats))
    return int(best)


def alpha_beta(board: list[list[str]], depth: int, alpha: float, beta: float,
               maximizing: bool, stats: SearchStats) -> int:
    stats.nodes += 1
    winner = winning_piece(board)
    if depth == 0 or winner is not None or is_draw(board):
        stats.leaves += 1
        value = evaluate_board(board)
        if winner == AI:
            return value + depth
        if winner == HUMAN:
            return value - depth
        return value

    if maximizing:
        best = -math.inf
        for col in ordered_moves(board):
            child = [row[:] for row in board]
            drop_piece(child, col, AI)
            best = max(best, alpha_beta(child, depth - 1, alpha, beta, False, stats))
            alpha = max(alpha, best)
            if alpha >= beta:
                stats.cutoffs += 1
                break
        return int(best)

    best = math.inf
    for col in ordered_moves(board):
        child = [row[:] for row in board]
        drop_piece(child, col, HUMAN)
        best = min(best, alpha_beta(child, depth - 1, alpha, beta, True, stats))
        beta = min(beta, best)
        if alpha >= beta:
            stats.cutoffs += 1
            break
    return int(best)


def choose_ai_move(board: list[list[str]], depth: int = 4,
                   use_alpha_beta: bool = True) -> tuple[int, int, SearchStats, float]:
    """Return (column, score, stats, elapsed_seconds) for the AI's move."""
    moves = ordered_moves(board)
    if not moves:
        raise ValueError("No legal moves remain.")
    stats = SearchStats()
    start = time.perf_counter()
    best_col = moves[0]
    best_score = -math.inf
    alpha, beta = -math.inf, math.inf

    for col in moves:
        child = [row[:] for row in board]
        drop_piece(child, col, AI)
        if use_alpha_beta:
            score = alpha_beta(child, depth - 1, alpha, beta, False, stats)
            alpha = max(alpha, score)
        else:
            score = minimax(child, depth - 1, False, stats)
        if score > best_score:
            best_score, best_col = score, col

    elapsed = time.perf_counter() - start
    return best_col, int(best_score), stats, elapsed


def benchmark(depth: int = 4) -> None:
    """Compare both algorithms on the same opening position."""
    board = new_board()
    print(f"Benchmarking the same empty board at search depth {depth}...")
    results = []
    for name, use_ab in (("Minimax", False), ("Alpha-Beta", True)):
        col, score, stats, elapsed = choose_ai_move(board, depth, use_ab)
        results.append((name, col + 1, score, stats, elapsed))
    print("\nAlgorithm      Move  Score       Nodes       Leaves      Cutoffs   Time (s)")
    for name, move, score, stats, elapsed in results:
        print(f"{name:<14} {move:<5} {score:<11} {stats.nodes:<11} {stats.leaves:<11} {stats.cutoffs:<9} {elapsed:.4f}")
    mini_nodes = results[0][3].nodes
    ab_nodes = results[1][3].nodes
    if mini_nodes:
        reduction = (mini_nodes - ab_nodes) / mini_nodes * 100
        print(f"\nNode reduction with Alpha-Beta: {reduction:.2f}%")
    if results[0][2] != results[1][2]:
        print("WARNING: scores differ; investigate before using these results in a report.")
    else:
        print("Check: both algorithms returned the same best score on this position.")


def play() -> None:
    print("=" * 44)
    print(" CONNECT FOUR — MINIMAX + ALPHA-BETA PRUNING")
    print("You are X. The AI is O. Connect four to win.")
    print("=" * 44)
    while True:
        raw_depth = input("AI search depth (recommended 4; try 2–6) [4]: ").strip()
        if not raw_depth:
            depth = 4
            break
        try:
            depth = int(raw_depth)
            if 1 <= depth <= 8:
                break
        except ValueError:
            pass
        print("Enter a whole number from 1 to 8.")

    board = new_board()
    print_board(board)
    while True:
        # Human turn.
        moves = legal_moves(board)
        if not moves:
            print("It's a draw!")
            break
        raw = input("Your move — choose a column (1–7), or type q to quit: ").strip().lower()
        if raw == "q":
            print("Game ended.")
            break
        try:
            col = int(raw) - 1
        except ValueError:
            print("Please enter a column number from 1 to 7.")
            continue
        if not drop_piece(board, col, HUMAN):
            print("That move is invalid or the column is full. Try again.")
            continue
        print_board(board)
        if winning_piece(board) == HUMAN:
            print("You win! 🎉")
            break
        if is_draw(board):
            print("It's a draw!")
            break

        print("AI is thinking...")
        col, score, stats, elapsed = choose_ai_move(board, depth, use_alpha_beta=True)
        drop_piece(board, col, AI)
        print(f"AI chose column {col + 1} | score={score} | nodes={stats.nodes} | "
              f"cutoffs={stats.cutoffs} | time={elapsed:.3f}s")
        print_board(board)
        if winning_piece(board) == AI:
            print("AI wins. Try again and look for a way to block it!")
            break
        if is_draw(board):
            print("It's a draw!")
            break

    again = input("Run the benchmark too? (y/n): ").strip().lower()
    if again == "y":
        benchmark(depth=min(depth, 6))


if __name__ == "__main__":
    play()
