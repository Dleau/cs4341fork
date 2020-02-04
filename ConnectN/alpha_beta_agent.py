import math
import agent
#import board

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
        # think up to 6 moves ahead
        d = min(8, brd.n + 1)
        (v, move) = self.alpha_beta((brd, 0), d, -math.inf, math.inf, True)
        print("VALUE", v, "MOVES", move)
        return move

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
                (n_v, _) = self.alpha_beta(child, depth - 1, alpha, beta, False)
                if n_v > v or math.isnan(col):
                    col = child[1]
                v = max(v, n_v)
                alpha = max(alpha, v)
                if alpha >= beta:
                    break
        else:
            v = math.inf
            for child in self.get_successors(brd):
                (n_v, _) = self.alpha_beta(child, depth - 1, alpha, beta, True)
                if n_v < v or math.isnan(col):
                    col = child[1]
                v = min(v, n_v)
                beta = min(beta, v)
                if alpha >= beta:
                    break
        return (v, col)

    def playable_chain_single(self, brd, row, col, drow, dcol, target):
        '''
        @author Dillon (just working through this)
        brd as game board
        row as root row coordinate
        col as root column coordinate
        drow as delta row
        dcol as delta col
        target as 1 or 2 denoting player
        returns the length of the chain
        '''
        # set r and c pre-traversal
        r, c = row + drow, col + dcol
        # store length of playable chain
        length = 0 #FIXME should this start at 0?
        # verify that row,col cursor is still on the board
        while r in range(0, brd.h) and c in range(0, brd.w):
            # print(r, c, brd.board[r][c])
            # verify that r,c cursor is on target
            if brd.board[r][c] != target:
                #print('no') # NOTE
                return length
            # increment chain length
            length += 1
            # return n if length is equal to n
            if length == brd.n:
                return length
            # apply row and column deltas
            r += drow
            c += dcol
        # we went off the board, give what we have
        return length
        ''' @author Ray
        # iterate in the dx, dy direction and find a chain (if any)
        cur_row = row
        cur_col = col
        blank_traverse = False
        bt_pc = 0
        pc = 0
        i = 0
        while cur_row < brd.h and cur_col < brd.w and i < brd.n:
            val = brd.board[cur_row][cur_col]
            if val == target:
                if blank_traverse:
                    # add blank traversal to total
                    # don't reset the variable because double blanks aren't allowed
                    pc += bt_pc
                    bt_pc = 0
                pc += 1
            elif val == 0:
                if blank_traverse:
                    # double blank, done
                    break
                # blank spot in the chain
                # first check if there is a supporting piece below
                if cur_row - 1 > 0 and brd.board[cur_row - 1][cur_col] == 0:
                    # there isn't, stop counting pieces
                    break
                # trigger the blank_traverse
                # before we start traversing blanks
                # save to temporary variable that will only
                # get copied over if this is connected past a blank
                blank_traverse = True
                bt_pc += 0.5
                # we have to get back to a target in order to
                # keep the blank traverse spots
            else:
                # if we encounter another player's piece
                # then this is not a viable chain
                return 0
            cur_row += drow
            cur_col += dcol
            i += 1
        return pc
        '''

    def playable_chain(self, brd, target):
        '''@author Dillon
        brd as game board
        target as 1 or 2 for player
        returns the longest! playable chain for a target
        '''
        # keep maximum chain length
        max_length = 0
        # iterate across columns
        for c in range(0, brd.w):
            # assume playable cell at 0,c
            r = 0
            # find the playable, empty cell in this column
            while r in range(0, brd.h) and brd.board[r][c] != 0:
                r += 1
            # continue through column if height was reached
            if r == brd.h:
                continue
            # define directions NOTE look into necessary directions
            directions = [
                    (0, 1), # north
                    (1, 1), # northeast
                    (1, 0), # east
                    (1, -1), # southeast
                    (0, -1), # south
                    (-1, -1), # southwest
                    (-1, 0), # west
                    (-1, 1),] # northwest
            # iterate through directions
            for drow, dcol in directions:
                # find chain length in this direction
                length = self.playable_chain_single(brd, r, c, drow, dcol, target)
                # print('(%d,%d) (%d,%d), target %d -> %d' % (c, r, dcol, drow, target, length))
                # adjust maximum if warranted
                if length > max_length:
                    max_length = length
        # the longest chain found from any playable cell in any direction
        return max_length
        '''@author Ray
        go_up = [1,0]; go_right = [0,1]; go_left = [0,-1]
        go_diag_top = [1,1]; go_diag_bottom = [-1,1]
        check_cols = [i for i in range(0, brd.w)]
        max_pc = 0
        for row in range(brd.h):
            if len(check_cols) == 0:
                break
            new_check_cols = []
            for col in check_cols:
                val = brd.board[row][col]
                # check on next iteration if it isn't a blank spot
                if val != 0:
                    new_check_cols.append(col)
                if val != target:
                    continue
                # check for max playable chain
                check_types = []
                # measurements away from the wall
                close_top = row > brd.h - brd.n
                close_right = col > brd.w - brd.n
                close_left = col < brd.n
                if not close_top:
                    # if close top is false, up is possible
                    check_types.append(go_up)
                if not close_left:
                    check_types.append(go_left)
                if not close_right:
                    check_types.append(go_right)
                    # must be close right for diagonals
                    # to work
                    if close_top:
                        check_types.append(go_diag_bottom)
                    else:
                        check_types.append(go_diag_top)
                for drow, dcol in check_types:
                    max_pc = max(max_pc,
                        self.playable_chain_single(brd, row,
                                                   col, drow, dcol, target))
            check_cols = new_check_cols
        return max_pc
        '''

    def pc_weighted(self, brd, target):
        chain = self.playable_chain(brd, target)
        """if chain >= brd.n and target == 1:
            return math.inf"""
        # take the exponent of the chain value
        # in order to make longer chains more desirable/undesirable
        # to the AI then they otherwise would be
        chain = math.exp(chain)
        return chain


    def heuristic(self, brd_tuple):
        # brd_tuple is (board state, column where last token was added)
        # return either an approximation of the value of moving to this board state
        # -inf if this will cause the minimizing player to win and
        # inf if the maximizing player will win
        olpc = self.pc_weighted(brd_tuple[0], 2)
        xlpc = self.pc_weighted(brd_tuple[0], 1)
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



'''
@author Dillon
testing with boards
    def playable_chain_single(self, brd, row, col, drow, dcol, target):
'''
# board = board.Board([[1,1,1,1],[0,2,2,2],[0,0,1,1],[0,0,1,0]], 4, 4, 4)
'''
board = board.Board([   [2,1,0,0,1,0,1],
                        [2,0,0,0,0,0,2],
                        [1,0,0,0,0,0,2],
                        [1,0,0,0,0,0,2],
                        [0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0] ], 7, 6, 4)
board.print_it()

#r = AlphaBetaAgent(None, None).playable_chain_single(board, 0, 1, 0, 1, 1)
r = AlphaBetaAgent(None, None).playable_chain(board, 2)
print(r)
'''
