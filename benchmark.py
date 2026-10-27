"""Run a reproducible Minimax vs Alpha-Beta benchmark.
Usage: python benchmark.py [depth]
"""
import sys
from connect_four import new_board, choose_ai_move


def main():
    try:
        depth = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    except ValueError:
        raise SystemExit('Depth must be an integer from 1 to 8.')
    if not 1 <= depth <= 8:
        raise SystemExit('Choose a depth from 1 to 8. Start with 4.')

    board = new_board()
    results = []
    for name, use_ab in [('Minimax', False), ('Alpha-Beta', True)]:
        col, score, stats, elapsed = choose_ai_move(board, depth, use_ab)
        results.append((name, col + 1, score, stats, elapsed))

    print(f'Connect Four benchmark | same empty board | depth={depth}')
    print('-' * 76)
    print(f'{"Algorithm":<14}{"Move":>7}{"Score":>10}{"Nodes":>12}{"Leaves":>12}{"Cutoffs":>10}{"Time(s)":>11}')
    for name, move, score, stats, elapsed in results:
        print(f'{name:<14}{move:>7}{score:>10}{stats.nodes:>12}{stats.leaves:>12}{stats.cutoffs:>10}{elapsed:>11.4f}')

    mm, ab = results
    reduction = ((mm[3].nodes - ab[3].nodes) / mm[3].nodes * 100) if mm[3].nodes else 0
    print('-' * 76)
    print(f'Node reduction: {reduction:.2f}%')
    print(f'Scores match: {mm[2] == ab[2]}')
    print('Note: runtime varies by machine; node counts are more reproducible.')

if __name__ == '__main__':
    main()
