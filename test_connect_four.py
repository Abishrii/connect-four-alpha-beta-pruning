"""Basic correctness tests for the Connect Four search project.
Run: python -m unittest -v
"""
import unittest

from connect_four import (
    AI, HUMAN, EMPTY, ROWS, COLS, SearchStats,
    new_board, drop_piece, winning_piece, legal_moves,
    minimax, alpha_beta, choose_ai_move,
)


class GameEngineTests(unittest.TestCase):
    def test_horizontal_win(self):
        board = new_board()
        for col in range(4):
            self.assertTrue(drop_piece(board, col, HUMAN))
        self.assertEqual(winning_piece(board), HUMAN)

    def test_vertical_win(self):
        board = new_board()
        for _ in range(4):
            self.assertTrue(drop_piece(board, 3, AI))
        self.assertEqual(winning_piece(board), AI)

    def test_diagonal_win(self):
        # Construct a valid-enough board shape to test the win detector directly.
        board = new_board()
        board[5][0] = AI
        board[4][1] = AI
        board[3][2] = AI
        board[2][3] = AI
        self.assertEqual(winning_piece(board), AI)

    def test_full_column_is_not_legal(self):
        board = new_board()
        for r in range(ROWS):
            board[r][0] = HUMAN
        self.assertNotIn(0, legal_moves(board))
        self.assertFalse(drop_piece(board, 0, AI))

    def test_invalid_column_rejected(self):
        board = new_board()
        self.assertFalse(drop_piece(board, -1, HUMAN))
        self.assertFalse(drop_piece(board, COLS, HUMAN))


class SearchAlgorithmTests(unittest.TestCase):
    def test_minimax_and_alpha_beta_scores_match(self):
        board = new_board()
        # Use a small depth to keep this test fast and deterministic.
        mm_stats = SearchStats()
        ab_stats = SearchStats()
        mm_score = minimax(board, 4, True, mm_stats)
        ab_score = alpha_beta(board, 4, float('-inf'), float('inf'), True, ab_stats)
        self.assertEqual(mm_score, ab_score)

    def test_best_move_scores_match(self):
        board = new_board()
        _, mm_score, _, _ = choose_ai_move(board, depth=3, use_alpha_beta=False)
        _, ab_score, _, _ = choose_ai_move(board, depth=3, use_alpha_beta=True)
        self.assertEqual(mm_score, ab_score)

    def test_alpha_beta_prunes_on_opening_position(self):
        board = new_board()
        mm_stats = SearchStats()
        ab_stats = SearchStats()
        minimax(board, 4, True, mm_stats)
        alpha_beta(board, 4, float('-inf'), float('inf'), True, ab_stats)
        self.assertGreater(ab_stats.cutoffs, 0)
        self.assertLess(ab_stats.nodes, mm_stats.nodes)


if __name__ == '__main__':
    unittest.main(verbosity=2)
