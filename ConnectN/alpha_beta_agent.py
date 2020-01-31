import math
import agent


import sys


###########################
# Alpha-Beta Search Agent #
###########################

class AlphaBetaAgent(agent.Agent):
    """Agent that uses alpha-beta search"""

    # Class constructor.
    #
    # PARAM [string] name:      the name of this player
    # PARAM [int]    max_depth: the maximum search depth
    def __init__(self, name, max_depth):
        super().__init__(name)
        # Max search depth
        self.max_depth = max_depth

    # Pick a column.
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: the column where the token must be added
    #
    # NOTE: make sure the column is legal, or you'll lose the game.
    def go(self, brd):
        (v, drop) = self.alpha_beta((brd, 0), 3, -math.inf, math.inf, True)
        print("VALUE", v, "MOVE", drop)
        return drop

    def alpha_beta(self, brd_tuple, depth, alpha, beta, is_max_player):
        brd = brd_tuple[0]
        outcome = brd.get_outcome()
        v = math.nan
        col = math.nan
        if depth == 0 or outcome != 0:
            if outcome == 1:
                return (-math.inf, brd_tuple[1])
            elif outcome == 2:
                return (math.inf, brd_tuple[1])
            return self.heuristic(brd_tuple)
        if is_max_player:
            v = -math.inf
            for child in self.get_successors(brd):
                (n_v, col) = self.alpha_beta(child, depth - 1, alpha, beta, False)
                v = max(v, n_v)
                alpha = max(alpha, v)
                if alpha >= beta:
                    break
        else:
            v = math.inf
            for child in self.get_successors(brd):
                (n_v, col) = self.alpha_beta(child, depth - 1, alpha, beta, True)
                v = min(v, n_v)
                beta = min(beta, v)
                if alpha >= beta:
                    break 
        return (v, col)

    def playable_chain(self, brd, target):
        y = -1
        longest_chain = 0
        longest_playable_chain = 0
        zero_counter = 0
        for row in brd.board:
            y = y + 1
            if (y >= brd.h):
                break
            zero_counter = 0
            for x in range(len(row)):
                #Increment blank row counter and check for max blank row
                if (x >= brd.w):
                    break
                if brd.board[y][x] == 0:
                    zero_counter = zero_counter + 1
                    if zero_counter >= brd.w:
                        break
                if target == brd.board[y][x]:
                    start_x = x
                    start_y = y
                    # Check up
                    longest_chain = 0
                    while brd.board[y][x] == target:
                        longest_chain = longest_chain + 1
                        y = y + 1
                        if (y >= brd.h or y < 0 or x >= brd.w or x < 0):
                            break
                        if (y - 1 < 0):
                            if brd.board[y][x] == 0:
                                if longest_chain > longest_playable_chain:
                                    longest_playable_chain = longest_chain
                                    break
                        else:
                            if brd.board[y][x] == 0 and brd.board[y-1][x] != 0:
                                if longest_chain > longest_playable_chain:
                                    longest_playable_chain = longest_chain
                                    break
                    # Reset to curr token
                    x = start_x
                    y = start_y
                    longest_chain = 0
                    # Check right
                    while brd.board[y][x] == target:
                        longest_chain = longest_chain + 1
                        x = x + 1
                        if (y >= brd.h or y < 0 or x >= brd.w or x < 0):
                            break
                        if (y - 1 < 0):
                            if brd.board[y][x] == 0:
                                if longest_chain > longest_playable_chain:
                                    longest_playable_chain = longest_chain
                                    break
                        else:
                            if brd.board[y][x] == 0 and brd.board[y-1][x] != 0:
                                if longest_chain > longest_playable_chain:
                                    longest_playable_chain = longest_chain
                                    break
                    # Reset to curr token
                    x = start_x
                    y = start_y
                    longest_chain = 0
                    # Check diag right
                    while brd.board[y][x] == target:
                        longest_chain = longest_chain + 1
                        x = x + 1
                        y = y + 1
                        if (y >= brd.h or y < 0 or x >= brd.w or x < 0):
                            break
                        if (y - 1 < 0):
                            if brd.board[y][x] == 0:
                                if longest_chain > longest_playable_chain:
                                    longest_playable_chain = longest_chain
                                    break
                        else:
                            if brd.board[y][x] == 0 and brd.board[y-1][x] != 0:
                                if longest_chain > longest_playable_chain:
                                    longest_playable_chain = longest_chain
                                    break
                    # Reset to curr token
                    x = start_x
                    y = start_y
                    longest_chain = 0
                    # Check diag left
                    while brd.board[y][x] == target:
                        longest_chain = longest_chain + 1
                        x = x - 1
                        y = y + 1
                        if (y >= brd.h or y < 0 or x >= brd.w or x < 0):
                            break
                        if (y - 1 < 0):
                            if brd.board[y][x] == 0:
                                if longest_chain > longest_playable_chain:
                                    longest_playable_chain = longest_chain
                                    break
                        else:
                            if brd.board[y][x] == 0 and brd.board[y-1][x] != 0:
                                if longest_chain > longest_playable_chain:
                                    longest_playable_chain = longest_chain
                                    break
                    x = start_x
                    y = start_y
                    longest_chain = 0
                    # Check left
                    while brd.board[y][x] == target:
                        x = x - 1
                        longest_chain = longest_chain + 1
                        if (y >= brd.h or y < 0 or x >= brd.w or x < 0):
                            break
                        if (y - 1 < 0):
                            if brd.board[y][x] == 0:
                                if longest_chain > longest_playable_chain:
                                    longest_playable_chain = longest_chain
                                    break
                        else:
                            if brd.board[y][x] == 0 and brd.board[y-1][x] != 0:
                                if longest_chain > longest_playable_chain:
                                    longest_playable_chain = longest_chain
                                    break

        return longest_playable_chain

    def heuristic(self, brd_tuple):
        # brd_tuple is (board state, column where last token was added)
        # return either an approximation of the value of moving to this board state
        # -inf if this will cause the minimizing player to win and
        # inf if the maximizing player will win
        olpc = self.playable_chain(brd_tuple[0], 2)
        xlpc = self.playable_chain(brd_tuple[0], 1)
        h = olpc - (3*xlpc)
        print("CHAIN FOR 1:", self.playable_chain(brd_tuple[0], 1),
        "CHAIN FOR 2:" , self.playable_chain(brd_tuple[0], 2))
        brd_tuple[0].print_it()
        print(h, brd_tuple[1])
        print("----")
        return (h, brd_tuple[1])

    # Get the successors of the given board.
    #
    # PARAM [board.Board] brd: the board state
    # RETURN [list of (board.Board, int)]: a list of the successor boards,
    #                                      along with the column where the last
    #                                      token was added in it
    def get_successors(self, brd):
        """Returns the reachable boards from the given board brd. The return value is a tuple (new board state, column number where last token was added)."""
        # Get possible actions
        freecols = brd.free_cols()
        # Are there legal actions left?
        if not freecols:
            return []
        # Make a list of the new boards along with the corresponding actions
        succ = []
        for col in freecols:
            # Clone the original board
            nb = brd.copy()
            # Add a token to the new board
            # (This internally changes nb.player, check the method definition!)
            nb.add_token(col)
            # Add board to list of successors
            succ.append((nb,col))
        return succ
