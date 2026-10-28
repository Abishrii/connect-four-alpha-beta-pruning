# Connect Four AI — Minimax & Alpha-Beta Pruning

## 1. Project Overview

This project implements an AI-powered Connect Four game in Python. The AI uses **Minimax search, Alpha-Beta Pruning, and heuristic evaluation** to select strategic moves against a human player.

The project includes a playable graphical interface, a search-tree explorer to understand the AI's decision-making, benchmarking tools to compare search algorithms, and automated tests.

## 2. Technologies Used

- **Python** — Game logic, AI algorithms, evaluation, and benchmarking.
- **Tkinter** — Graphical user interface (GUI).
- **Minimax** — Explores possible future moves assuming both players make optimal decisions.
- **Alpha-Beta Pruning** — Reduces unnecessary search by skipping branches that cannot influence the final decision.
- **Heuristic Evaluation** — Estimates board strength when the search reaches its depth limit.
- **CSV** — Stores benchmark results.

## 3. Project Structure

| File | Purpose |
|---|---|
| `connect_four.py` | Core game logic, board management, win/draw detection, heuristic evaluation, Minimax, Alpha-Beta Pruning, AI move selection, and command-line gameplay. |
| `gui.py` | Provides the graphical interface for playing Connect Four, displaying the board, handling player interactions, and showing game results. |
| `search_explorer.py` | Explores the AI's search process, showing evaluated and pruned branches and the Alpha-Beta bounds used during decision-making. |
| `benchmark.py` | Runs experiments to compare Minimax and Alpha-Beta Pruning in terms of search nodes, execution time, and other performance measures. |
| `results.csv` | Stores benchmark results for analysis and comparison. |
| `test_connect_four.py` | Contains automated tests for winning conditions, invalid moves, and the correctness and efficiency of the search algorithms. |

## 4. Core Implementation — `connect_four.py`

### Game Logic
The game uses a **6 × 7 board**. The human player uses `X`, while the AI uses `O`. The implementation manages legal moves, piece placement, win detection in horizontal, vertical, and diagonal directions, and draw detection.

### AI Decision-Making Flow

1. Generate all legal moves.
2. Simulate each possible move.
3. Explore future game states using depth-limited Minimax.
4. Apply Alpha-Beta Pruning to eliminate branches that cannot change the decision.
5. Evaluate positions at the depth limit using the heuristic function.
6. Propagate scores through the search tree and select the best move for the AI.

### Heuristic Evaluation

The heuristic evaluates groups of four cells horizontally, vertically, and diagonally.

| Board pattern | Score |
|---|---:|
| Four AI pieces in a group | +100,000 |
| Three AI pieces and one empty cell | +120 |
| Two AI pieces and two empty cells | +12 |
| Three opponent pieces and one empty cell | -150 |
| Two opponent pieces and two empty cells | -10 |
| Other patterns | 0 |

The evaluation also rewards AI pieces in the centre column (`+6` per piece) and penalizes opponent pieces there (`-6` per piece).

Terminal positions receive much larger scores: **+1,000,000 for an AI win, -1,000,000 for an opponent win, and 0 for a draw**. Positive scores favour the AI, while negative scores favour the opponent.

The stronger penalty for an opponent's three-in-a-row encourages the AI to block immediate threats rather than focus only on its own opportunities.

### Algorithm Complexity

- **Minimax:** `O(b^d)` in the worst case.
- **Alpha-Beta Pruning:** `O(b^d)` in the worst case and approximately `O(b^(d/2))` in the ideal case with effective move ordering.

Here, `b` is the average branching factor and `d` is the search depth.

## 5. How to Run

Run the game from the project directory:

```bash
python connect_four.py
```

To launch the graphical interface:

```bash
python gui.py
```

Run the benchmark script to compare search performance:

```bash
python benchmark.py
```

## 6. Key Features

- Interactive Connect Four gameplay.
- Strategic AI using Minimax and Alpha-Beta Pruning.
- Heuristic evaluation of potential winning combinations.
- Search-tree exploration to inspect evaluated and pruned branches.
- Performance benchmarking and automated tests.
