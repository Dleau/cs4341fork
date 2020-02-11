import math
import agent
import hashlib
import board

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
        self.trans_table = {}

    # Pick a column.
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: the column where the token must be added
    #
    # NOTE: make sure the column is legal, or you'll lose the game.
    def go(self, brd):
        self.max_player = brd.player
        if self.max_player == 1:
            self.min_player = 2
        else:
            self.min_player = 1
        if brd.n > 4:
            self.max_depth = 7
        else:
            self.max_depth = 9
        (v, move) = self.alpha_beta((brd, 0), self.max_depth, -math.inf, math.inf, True)
        print("DEPTH", self.max_depth, "VALUE", v, "MOVE", move)
        return move
    
    def alpha_beta_helper(self, child, depth, alpha, beta, is_max_player):
        n_v = math.nan
        tbl_hash = self.hash_board(child[0])
        if tbl_hash not in self.trans_table:
            (n_v, _) = self.alpha_beta(child, depth - 1, alpha, beta, is_max_player)
            if depth - 1 > 0:
                self.trans_table[tbl_hash] = n_v
        else:
            n_v = self.trans_table[tbl_hash]
        return n_v

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
            for child in self.get_sorted_successors(brd):
                n_v = self.alpha_beta_helper(child, depth, alpha, beta, False)
                if n_v > v or math.isnan(col):
                    col = child[1]
                v = max(v, n_v)
                alpha = max(alpha, v)
                if alpha >= beta:
                    break
        else:
            v = math.inf
            for child in self.get_sorted_successors(brd):
                n_v = self.alpha_beta_helper(child, depth, alpha, beta, True)
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
        #r, c = row + drow, col + dcol
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

    def playable_chain(self, brd, target):
        '''@author Dillon
        brd as game board
        target as 1 or 2 for player
        returns the longest! playable chain for a target
        '''
        
        # keep all chains
        chains = []
        # columns to look through (not found to be empty)
        cols = list(range(0, brd.w))
        new_cols = cols
        # iterate row first
        for r in range(0, brd.h):
            if len(new_cols) == 0:
                break
            new_cols = []
            for c in cols:
                if brd.board[r][c] != 0:
                    new_cols.append(c)
                    continue
                # define directions
                directions = [
                        (1, 0), # north
                        (1, 1), # northeast
                        (0, 1), # east
                        (-1, 1), # southeast
                        (-1, 0), # south
                        (-1, -1), # southwest
                        (0, -1), # west
                        (1, -1)] # northwest
                # iterate through directions
                for drow, dcol in directions:
                    # find chain length in this direction
                    length = self.playable_chain_single(brd, r, c, drow, dcol, target)
                    # print('(%d,%d) (%d,%d), target %d -> %d' % (c, r, dcol, drow, target, length))
                    # if there is a chain, put it into the array
                    if length > 0:
                        chains.append(length)
        # all the chains found
        return chains
        """
        # keep all chains
        chains = []
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
                    (-1, 1)] # northwest
            # iterate through directions
            for drow, dcol in directions:
                # find chain length in this direction
                length = self.playable_chain_single(brd, r, c, drow, dcol, target)
                # print('(%d,%d) (%d,%d), target %d -> %d' % (c, r, dcol, drow, target, length))
                # if there is a chain, put it into the array
                if length > 0:
                    chains.append(length)
        # all the chains found
        return chains
        """
    
    def check_path(self, brd, dr, dc, r, c, target):
        board = brd.board
        blanks = 0
        length = 0
        #print("---", (dr, dc), "---")
        # A line consists of target pieces followed by a blank spot
        # keep going in the direction until we hit
        # the end of the board or the length runs out
        while c in range(0, brd.w) and r in range(0, brd.h) and length < brd.n:
            cur_val = board[r][c]
            if cur_val != target:
                if cur_val == 0:
                    if blanks > 0:
                        # we have already seen a blank and 
                        # there's another, traversal over
                        length -= blanks # blank space no longer counts
                        break
                    elif ((r+dr) not in range(0, brd.h) or 
                        (c+dc) not in range(0, brd.w)):
                        # there's a blank but there's also a wall after
                        # so break now
                        break
                    else:
                        # innocuous blank space, increment blank counter
                        blanks += 1
                        length += 1
                else:
                    # something is in the way, not viable
                    return False
            else:
                # found a piece
                length += 1
            if r > 0 and board[r-1][c] == 0:
                # not resting on anything
                return False
            #print(cur_val)
            # increment in the correct direction
            r += dr
            c += dc
        #print("---", length, "---")
        return length == brd.n

    def winning_moves(self, brd, target):
        directions = [
            (1, 0), # north
            (1, 1), # northeast
            (0, 1), # east
            (-1, 1)] # southeast
        winning_moves = 0
        cols = list(range(0, brd.w))
        # iterate columns then rows
        # stop after a column is white
        for r in range(0, brd.h):
            for c in cols:
                new_cols = []
                for dr, dc in directions:
                    if self.check_path(brd, dr, dc, r, c, target):
                        winning_moves += 1
                        cols.append(c)
                cols = new_cols
        return winning_moves

    def pc_weighted(self, brd, target):
        """
        chains = sorted(self.playable_chain(brd, target), reverse=True)
        score = 0
        # if there are two directly winning positions, then the game is over
        if len(chains) >= 2 and chains[0] == chains[1] and chains[0] == brd.n - 1:
            return math.inf
        # othwerwise return the number of chains that are about to win
        for chain in chains:
            if chain < brd.n - 1:
                break
            score += chain
        return score
        """
        score = self.winning_moves(brd, target)
        # if there are two directly winning positions, then the game is over
        if score >= 2:
            return math.inf
        return score
    
    def free_pos(self, brd):
        """ Returns the count of all free board positions """
        cnt = 0
        for r in brd.board:
            for elem in r:
                if elem == 0:
                    cnt += 1
        return cnt


    def heuristic(self, brd_tuple):
        # brd_tuple is (board state, column where last token was added)
        # return either an approximation of the value of moving to this board state
        # -inf if this will cause the minimizing player to win and
        # inf if the maximizing player will win
        olpc = self.pc_weighted(brd_tuple[0], self.max_player)
        xlpc = self.pc_weighted(brd_tuple[0], self.min_player)
        free = self.free_pos(brd_tuple[0])
        h = olpc - xlpc + (free / (10**len(str(free))))
        """
        print("CHAIN FOR 1:", self.playable_chain(brd_tuple[0], 1),
        "CHAIN FOR 2:" , self.playable_chain(brd_tuple[0], 2))
        brd_tuple[0].print_it()
        print(h, brd_tuple[1])
        print("----")
        """
        return (h, brd_tuple[1])
    
    def get_sorted_successors(self, brd):
        succ = self.get_successors(brd)
        succ_sorted = []
        # check inner rows first because they are more likely to
        # be the best moves
        half = int(len(succ)/2)
        j = 1
        for i in range(half, len(succ)):
            succ_sorted.append(succ[i])
            if half-j >= 0:
                succ_sorted.append(succ[half-j])
                j += 1
        return succ_sorted

    def hash_board(self, brd):
        hash_str = bytearray()
        for r in brd.board:
            for elem in r:
                hash_str.append(elem)
        hash_str = bytes(hash_str)
        return hash_str

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
#board = board.Board([[1,1,1,1],[0,2,2,2],[0,0,1,1],[0,0,1,0]], 4, 4, 4)
'''
board = board.Board([   [2,1,1,0,1,0,1],
                        [2,2,2,0,0,0,2],
                        [1,0,0,0,0,0,2],
                        [1,0,0,0,0,0,2],
                        [0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0] ], 7, 6, 4)
'''

'''
board = board.Board([   [2,1,1,1,0,0,0],
                        [1,2,1,1,0,0,0],
                        [1,1,2,1,0,0,0],
                        [0,2,2,0,0,0,0],
                        [0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0] ], 7, 6, 4)
board.print_it()

#r = AlphaBetaAgent(None, None).playable_chain_single(board, 0, 1, 0, 1, 1)
r = AlphaBetaAgent(None, None).winning_moves(board, 1)
print(r)
'''