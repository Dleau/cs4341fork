# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from random import uniform, randrange

class TestCharacter(CharacterEntity):

    def __init__(self, name, avatar, x, y):
        super().__init__(name, avatar, x, y)
        self.weights = None
        self.gamma = 0.9
        self.alpha = 1
        self.q = 0
        self.r = -0.01
        self.eps = 1

    def do(self, wrld):
        x = self.__list_next_moves(wrld)
        print(x)
        
    def __list_next_moves(self, wrld):
        '''
        Use self to determine position on board, return
        a list of coordinates representing legal next moves.
        Note: return tuples as legal (dx, dy)
        '''
        pairs = [] # keep legal pairs
        character_x = wrld.me(self).x
        character_y = wrld.me(self).y
        for d_x in range(-1, 2):
            for d_y in range(-1, 2):
                x = character_x + d_x
                y = character_y + d_y
                if self.__is_move_legal(wrld, x, y):
                    pairs.append((x, y))
        return pairs

    def __is_move_legal(self, wrld, x, y):
        '''
        Determines if a move is legal
        '''
        return x < wrld.width() and y < wrld.height() and x >= 0 and y >= 0
    
    def __get_values(self, pair):
        '''
        Call helper functions and return list
        '''
        pass
        
    def __bomb_score(self, wrld, pair):
        '''
        Bombs within strike range
        '''
        pass
        
    def __monster_score(self, wrld, pair):
        '''
        Distance to closest monster
        '''
        pass
        
    def __goal_distance_score(self, wrld, pair):
        '''
        Manhattan or euclidian distance to goal
        '''
        pass
        
    def __wall_score(self, wlrd, pair):
        '''
        Return 0 if move is into a wall, 1 if not
        '''
        pass

    def __calc_q(self, pair, weights):
        '''
        Calculates and returns the q value and weights
        given a tuple pair for move and the current weights
        '''
        # retrieve state values and calculate new weights
        state_vals = self.__get_value(pair)
        if weights is None:
            weights = [1 for _ in state_vals]
        max_a = 0 # TODO: how do we calculate this?
        delta = (self.r + self.gamma * max_a) - self.q
        weights = [weights[i] + self.alpha * delta * f 
            for i, f in enumerate(state_vals)]
        # calculate the next q value step using approximate q learning
        return (
            sum([weights[i] * f for i, f in enumerate(state_vals)]),
            weights
        )
        
    def __calc_next_move(self, pair):
        '''
        Calculates the next move based on approximate q learning
        '''
        (self.q, self.weights) = self.__calc_q(pair, self.weights)
        # take a new move using epsilon greedy exploration
        new_move = None
        next_moves = self.__list_next_moves()
        x = uniform(0, 1)
        if x < self.eps:
            # exploration
            new_move = next_moves[randrange(0,len(next_moves))]
        else:
            # exploitation
            max_q = 0
            for move in next_moves:
                (cur_q, _) = self.__calc_q(move, self.weights)
                if cur_q > max_q:
                    max_q = cur_q
                    new_move = move
        # decrease epsilon
        if self.eps > 0:
            self.eps -= 0.01
        if self.eps < 0:
            self.eps = 0
        return new_move
