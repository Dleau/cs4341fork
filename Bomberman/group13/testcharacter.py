# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from random import uniform, randrange

class TestCharacter(CharacterEntity):

    def __init__(self):
        self.weights = None
        self.gamma = 0.9
        self.alpha = 1
        self.q = 0
        self.r = -0.01
        self.eps = 1

    def do(self, wrld):
        pass
        
    def __list_next_moves(self):
        '''
        Use self to determine position on board, return
        a list of coordinates representing legal next moves.
        Note: return tuples
        '''
        legal_coordinate_list = [];
        character_x =  wrld.me(self).x
        character_y =  wrld.me(self).y
        for i in range(-1, 1):
        	for j in range(-1, 1):
        		x = character_x + i
        		y = character_y + j
        		if(!wrld.wall_at(x,y) &&
        		 x < wrld.width() &&
        		 y < wrld.height() &&
        		  x >= 0 && y >= 0)
        			legal_coordinate_list.append([x,y])

       	return legal_coordinate_list;

        
    def __get_value(self, pair):
        '''
        Use coordinate pair on board as given, get a value
        for the position using a hueristic or whatever.
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
