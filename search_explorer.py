"""Explainable Alpha-Beta search tree viewer for the Connect Four project."""
import copy
import tkinter as tk
from tkinter import ttk

from connect_four import (
    ROWS, COLS, EMPTY, HUMAN, AI, legal_moves, drop_piece, winning_piece,
    is_draw, evaluate_board, ordered_moves,
)


def terminal_score(board, depth):
    winner = winning_piece(board)
    if winner == AI:
        return 1_000_000 + depth
    if winner == HUMAN:
        return -1_000_000 - depth
    if is_draw(board):
        return 0
    return evaluate_board(board)


def traced_alpha_beta(board, depth):
    """Return best root move, score, and a tree containing explored/pruned paths."""
    counter = [0]

    def visit(position, remaining, maximizing, alpha, beta, move=None, parent=None):
        counter[0] += 1
        node = {
            "id": counter[0], "move": move, "player": "MAX / AI" if maximizing else "MIN / Human",
            "depth": depth - remaining, "alpha_in": alpha, "beta_in": beta,
            "score": None, "score_kind": "unknown", "status": "explored",
            "children": [], "parent": parent, "board": copy.deepcopy(position),
            "cutoff": False, "alpha_out": alpha, "beta_out": beta,
        }
        winner = winning_piece(position)
        if remaining == 0 or winner is not None or is_draw(position):
            node["score"] = terminal_score(position, remaining)
            node["score_kind"] = "exact"
            node["status"] = "leaf / evaluated"
            node["alpha_out"] = alpha
            node["beta_out"] = beta
            return node["score"], node

        best = float("-inf") if maximizing else float("inf")
        moves = ordered_moves(position)
        for i, col in enumerate(moves):
            child_board = copy.deepcopy(position)
            drop_piece(child_board, col, AI if maximizing else HUMAN)
            score, child = visit(child_board, remaining - 1, not maximizing,
                                 alpha, beta, move=col, parent=node["id"])
            child["score"] = score
            node["children"].append(child)
            if maximizing:
                best = max(best, score)
                alpha = max(alpha, best)
            else:
                best = min(best, score)
                beta = min(beta, best)
            if alpha >= beta:
                node["cutoff"] = True
                node["cutoff_reason"] = f"α ({alpha:g}) ≥ β ({beta:g})"
                # Remaining sibling moves are not searched. Record them as pruned placeholders.
                for skipped_col in moves[i + 1:]:
                    counter[0] += 1
                    node["children"].append({
                        "id": counter[0], "move": skipped_col,
                        "player": "MAX / AI" if not maximizing else "MIN / Human",
                        "depth": depth - remaining + 1, "alpha_in": alpha, "beta_in": beta,
                        "score": None, "status": "PRUNED — not explored", "children": [],
                        "parent": node["id"], "board": None, "cutoff": False,
                    })
                break
        node["score"] = int(best)
        node["alpha_out"] = alpha
        node["beta_out"] = beta
        if node["cutoff"]:
            # A cutoff value is a bound, not necessarily an exact minimax value.
            node["score_kind"] = "lower bound" if maximizing else "upper bound"
            node["status"] = "cutoff occurred here"
        else:
            node["score_kind"] = "exact"
        return int(best), node

    # Root is MAX; search each legal AI move and preserve root values for comparison.
    root = {"id": 0, "move": None, "player": "ROOT / AI (MAX)", "depth": 0,
            "alpha_in": float("-inf"), "beta_in": float("inf"), "score": None,
            "status": "root: choose highest score", "children": [], "parent": None,
            "board": copy.deepcopy(board), "cutoff": False, "score_kind": "exact"}
    alpha, beta = float("-inf"), float("inf")
    best_move, best_score = None, float("-inf")
    for col in ordered_moves(board):
        child_board = copy.deepcopy(board)
        drop_piece(child_board, col, AI)
        score, child = visit(child_board, depth - 1, False, alpha, beta,
                             move=col, parent=0)
        child["score"] = score
        if child.get("cutoff"):
            child["score_kind"] = "upper bound"
            child["status"] = f"ROOT MOVE {col + 1} → score ≤ {score} (upper bound)"
        else:
            child["score_kind"] = "exact"
            child["status"] = f"ROOT MOVE {col + 1} → exact score {score}"
        root["children"].append(child)
        if score > best_score:
            best_score, best_move = score, col
        alpha = max(alpha, best_score)
    root["score"] = int(best_score)
    root["chosen_move"] = best_move
    return best_move, int(best_score), root, counter[0]


def open_search_explorer(parent, board, depth):
    """Open a tree explorer for the supplied pre-AI-move board position."""
    move, score, tree, total_nodes = traced_alpha_beta(board, depth)
    win = tk.Toplevel(parent)
    win.title("Explain Alpha-Beta Pruning — Search Tree")
    win.geometry("1040x700")
    win.configure(bg="#101827")

    tk.Label(win, text="HOW THE AI DECIDED", font=("Segoe UI", 18, "bold"),
             fg="#f4f7fb", bg="#101827").pack(pady=(12, 2))
    tk.Label(win,
             text=f"Depth {depth}  •  chosen column {move + 1}  •  root score {score}  •  tree entries {total_nodes}",
             font=("Consolas", 10), fg="#7dd3fc", bg="#101827").pack(pady=(0, 8))

    explain = ("Expand a row to inspect the search path. Exact scores mean all needed children were searched. "
               "A cutoff can return a bound (MAX: lower bound; MIN: upper bound), not an exact score. "
               "PRUNED rows were never searched; their descendants were not generated.")
    tk.Label(win, text=explain, wraplength=990, justify="left", fg="#dbeafe", bg="#18243a",
             padx=10, pady=8).pack(fill="x", padx=12, pady=(0, 8))

    frame = tk.Frame(win, bg="#101827")
    frame.pack(fill="both", expand=True, padx=12, pady=4)
    cols = ("role", "score", "bounds", "status")
    treeview = ttk.Treeview(frame, columns=cols, show="tree headings")
    treeview.heading("#0", text="Search path / move")
    treeview.heading("role", text="Player")
    treeview.heading("score", text="Returned score")
    treeview.heading("bounds", text="α / β")
    treeview.heading("status", text="What happened")
    treeview.column("#0", width=270, minwidth=220)
    treeview.column("role", width=115, anchor="center")
    treeview.column("score", width=100, anchor="center")
    treeview.column("bounds", width=150, anchor="center")
    treeview.column("status", width=330)
    yscroll = ttk.Scrollbar(frame, orient="vertical", command=treeview.yview)
    xscroll = ttk.Scrollbar(frame, orient="horizontal", command=treeview.xview)
    treeview.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    treeview.grid(row=0, column=0, sticky="nsew")
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    style = ttk.Style(win)
    style.configure("Treeview", rowheight=24, font=("Consolas", 9))
    style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
    treeview.tag_configure("chosen", foreground="#087f23")
    treeview.tag_configure("pruned", foreground="#c24141")
    treeview.tag_configure("cutoff", foreground="#b45309")
    treeview.tag_configure("leaf", foreground="#1d4ed8")

    item_to_node = {}
    def add_node(node, parent_id=""):
        col = node.get("move")
        if node["id"] == 0:
            label = "Root: AI (MAX) considers every legal column"
        elif node["status"].startswith("PRUNED"):
            label = f"Column {col + 1} — NOT SEARCHED"
        elif node.get("depth") == 1 and node.get("parent") == 0:
            label = f"AI move: column {col + 1}"
        else:
            label = f"Column {col + 1}"
        if node.get("score") is None:
            score_text = "—"
        elif node.get("score_kind") == "upper bound":
            score_text = f"≤ {node['score']}"
        elif node.get("score_kind") == "lower bound":
            score_text = f"≥ {node['score']}"
        else:
            score_text = str(node["score"])
        a = node.get("alpha_out", node.get("alpha_in", float("-inf")))
        b = node.get("beta_out", node.get("beta_in", float("inf")))
        bounds = f"{a:g} / {b:g}"
        status = node.get("status", "explored")
        if node.get("cutoff"):
            status += f" ({node.get('cutoff_reason', 'α ≥ β')})"
        if node.get("score_kind") in ("upper bound", "lower bound") and not status.startswith("PRUNED"):
            status += f" — {node['score_kind']}"
        tags = ()
        if status.startswith("PRUNED"):
            tags = ("pruned",)
        elif node.get("cutoff"):
            tags = ("cutoff",)
        elif "leaf" in status:
            tags = ("leaf",)
        elif node.get("move") == tree.get("chosen_move") and node.get("parent") == 0:
            tags = ("chosen",)
            status += " — SELECTED BEST MOVE"
        item = treeview.insert(parent_id, "end", text=label,
                               values=(node.get("player", ""), score_text, bounds, status), tags=tags)
        item_to_node[item] = node
        for child in node.get("children", []):
            add_node(child, item)
        return item

    root_item = add_node(tree)
    treeview.item(root_item, open=True)
    # Expand root moves, but keep deeper branches collapsed for readability.
    for item in treeview.get_children(root_item):
        treeview.item(item, open=False)

    detail = tk.Label(win, text="Select a node to see its board position and explanation.",
                      anchor="w", justify="left", wraplength=990,
                      fg="#f4f7fb", bg="#18243a", padx=10, pady=8)
    detail.pack(fill="x", padx=12, pady=(6, 12))

    def selected(_event=None):
        selected_items = treeview.selection()
        if not selected_items:
            return
        node = item_to_node[selected_items[0]]
        if node.get("status", "").startswith("PRUNED"):
            message = (f"PRUNED BRANCH: column {node['move'] + 1} was not searched. "
                       "At its parent, α ≥ β, so this remaining sibling could not change the final choice.")
        elif node.get("cutoff"):
            bound = node.get("score_kind", "bound")
            message = (f"CUTOFF at this node: {node.get('cutoff_reason')}. Remaining sibling moves were skipped. "
                       f"Returned value {node.get('score')} is a {bound}, not necessarily an exact minimax score.")
        elif node.get("depth") == depth - 1 and node.get("parent") == 0:
            kind = node.get("score_kind", "unknown")
            shown_score = node.get("score")
            qualifier = "exact score" if kind == "exact" else kind
            message = (f"Candidate AI move: column {node['move'] + 1}; returned {qualifier} {shown_score}. "
                       f"The selected best move is column {move + 1} with root score {score}. "
                       "A bound is enough to reject a move, but should not be compared as if it were exact.")
        elif "leaf" in node.get("status", ""):
            message = f"Leaf reached: evaluate this position. Returned heuristic/terminal score = {node.get('score')}."
        else:
            kind = node.get("score_kind", "unknown")
            message = (f"{node.get('player')} node. Returned value = {node.get('score')} ({kind}). "
                       f"Bounds on entry: α={node.get('alpha_in')}, β={node.get('beta_in')}. "
                       f"Bounds on exit: α={node.get('alpha_out', node.get('alpha_in'))}, "
                       f"β={node.get('beta_out', node.get('beta_in'))}.")
        detail.config(text=message)
    treeview.bind("<<TreeviewSelect>>", selected)
    return win
