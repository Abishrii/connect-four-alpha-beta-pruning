# Connect Four AI — Minimax & Alpha-Beta Pruning

A Python implementation of Connect Four using **Minimax and Alpha-Beta Pruning** to demonstrate adversarial search, game-tree evaluation, and search optimization.

## Overview

The game uses a **6 × 7 board**. The human plays as `X`, while the AI plays as `O`. The AI evaluates possible moves and selects one based on a heuristic scoring function.

## Algorithms Implemented

- **Minimax:** Explores possible moves using MAX (AI) and MIN (opponent) levels. MAX chooses the highest score, while MIN chooses the lowest.
- **Alpha-Beta Pruning:** Optimizes Minimax by skipping branches that cannot affect the final decision.
- **Move Ordering:** Examines centre columns first to improve pruning efficiency.
- **Depth-Limited Search:** Evaluates positions up to a configurable search depth.

### Algorithm Flow

1. Generate all legal moves.
2. Simulate each possible move.
3. Recursively explore future moves using Minimax or Alpha-Beta Pruning.
4. Evaluate positions using the heuristic function when the depth limit or a terminal state is reached.
5. Propagate scores upward through the search tree.
6. Select the move with the highest score for the AI.

## Heuristic Evaluation Function

The evaluation function scores potential four-cell winning combinations horizontally, vertically, and diagonally.

| Board Pattern | Score |
|---|---:|
| Four AI pieces | +100,000 |
| Three AI pieces + one empty | +120 |
| Two AI pieces + two empty | +12 |
| Three human pieces + one empty | -150 |
| Two human pieces + two empty | -10 |
| Other patterns | 0 |

Additional scoring:

- **AI win:** +1,000,000
- **Human win:** -1,000,000
- **Draw:** 0
- **Centre column:** +6 per AI piece and -6 per human piece

Positive scores favour the AI; negative scores favour the opponent. Terminal scores take precedence over ordinary heuristic evaluations.

## Complexity

Let `b` be the branching factor and `d` the search depth.

- **Minimax:** `O(b^d)`
- **Alpha-Beta Pruning:** Worst case `O(b^d)`; approximately `O(b^(d/2))` under ideal move ordering.

Alpha-Beta Pruning reduces unnecessary node exploration without changing the Minimax value for the same search depth and evaluation rules.

## Main File

**`connect_four.py`** contains the core game logic:

- Board creation and legal move generation
- Piece placement and win/draw detection
- Heuristic evaluation
- Minimax and Alpha-Beta Pruning
- AI move selection
- Benchmarking and command-line gameplay

## Run

```bash
python connect_four.py
```

To launch the graphical interface, if included in the repository:

```bash
python gui.py
```

## Technologies

**Python · Minimax · Alpha-Beta Pruning · Heuristic Search**
