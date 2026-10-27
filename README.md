# Explainable Game-Tree Search: Minimax with Alpha-Beta Pruning

A Python Connect Four game that lets a human play against an AI using Minimax with Alpha-Beta Pruning. A benchmark compares both search methods on the same board position and search depth.

## Requirements

- Python 3.10 or newer recommended
- No third-party packages required

## Run the game

```bash
python connect_four.py
```

You play as `X`; the AI plays as `O`. Choose a search depth when prompted. Higher depths explore more future moves and may take longer.

## Run the benchmark

```bash
python benchmark.py
python benchmark.py 4
python benchmark.py 5
```

The benchmark reports the selected move, score, visited nodes, leaf evaluations, alpha-beta cutoffs, and elapsed time. Both algorithms use the same evaluation function and deterministic move ordering.

## Run tests

```bash
python -m unittest -v
```

The tests cover horizontal, vertical, and diagonal win detection; invalid/full-column moves; equality of Minimax and Alpha-Beta scores; and evidence that Alpha-Beta prunes nodes on the tested opening position.

## Algorithms

- **Minimax:** recursively evaluates possible future states, maximizing the AI's score on AI turns and minimizing it on opponent turns.
- **Alpha-Beta Pruning:** computes the same Minimax decision value while skipping branches that cannot affect the result. `alpha` is the best value currently guaranteed to the maximizing player; `beta` is the best value currently guaranteed to the minimizing player. A branch can be cut off when `alpha >= beta`.
- **Heuristic evaluation:** scores center control and groups of two or three aligned pieces with open spaces. Terminal wins/losses receive much larger scores than non-terminal patterns.

## Important benchmarking note

Compare both methods at the same depth, from the same position, with the same move ordering and evaluation function. Node counts are more reproducible than execution time, which depends on the machine and background activity. Alpha-Beta's amount of pruning depends on move ordering and the position being searched.
