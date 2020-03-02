# This is necessary to find the main code
import sys
from math import inf, sqrt
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from random import uniform, randrange
from math import sqrt
from sensed_world import SensedWorld
from neuralnet import NeuralNet, linear, linear_deriv, sigmoid, sigmoid_deriv, relu, relu_deriv
import numpy as np
import pickle

class TestCharacter(CharacterEntity):

    def __init__(self, name, avatar, x, y, nn_file=None, eps=1,explore=True):
        super().__init__(name, avatar, x, y)
        self.weights = None
        self.gamma = 0.9
        self.alpha = 0.01
        self.q = 0
        self.eps = eps
        self.pair = (x, y)
        self.tried_pairs = {}
        self.explore = explore
        self.approx_net = None
        # curiosity constant
        self.k = 10
        self.nn_file = nn_file

    def __init_nn(self, wrld, filename=None):
        if self.nn_file is not None:
            with open(filename,"rb") as f:
                self.approx_net = pickle.load(f)
            return
        # input layer is the size of the board
        # intermediate layers are empirically defined
        brd_size = wrld.width() * wrld.height()
        self.approx_net = NeuralNet(
            #[brd_size, 20, 15, 10, 10],
            [brd_size,30,1],
            [sigmoid, sigmoid, sigmoid],
            [sigmoid_deriv, sigmoid_deriv, sigmoid_deriv],
            0.01)
        self.approx_net.randomize_weights()
    
    def save_nn(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self.approx_net, f)
    
    def __get_wrld_v(self, wrld, pair):
        wrld_v = np.ndarray((wrld.width(),wrld.height()))
        for idx in np.ndindex(wrld_v.shape):
            x = idx[0]; y = idx[1]
            wrld_v[x][y] = 1
            # prime numbers determine whats at a cell
            if wrld.wall_at(x,y):
                wrld_v[x][y] *= 2
            if wrld.exit_at(x,y):
                wrld_v[x][y] *= 3
            if wrld.bomb_at(x,y) is not None:
                wrld_v[x][y] *= 5
            if wrld.explosion_at(x,y) is not None:
                wrld_v[x][y] *= 7
            if wrld.monsters_at(x,y) is not None:
                wrld_v[x][y] *= 11
            # TODO: clone the world always!!!! reeee
            """
            me = wrld.me(self)
            if me is not None:
                if (me.x,me.y) == pair:
                    wrld_v[x][y] *= 13
            """
            if wrld.characters_at(x,y) is not None:
                wrld_v[x][y] *= 17
        return np.ndarray.flatten(wrld_v)

    def __approx_vals(self, wrld, pair):
        wrld_v = self.__get_wrld_v(wrld, pair)
        return self.approx_net.feed_forward(wrld_v)
    
    def __update_nn(self,wrld,v_out,weights,pair):
        wrld_v = self.__get_wrld_v(wrld,pair)
        for i in range(len(v_out)):
            v_out[i] *= weights[i]
        self.approx_net.backpropogate(wrld_v,v_out)

    def do(self, wrld):
        if self.approx_net is None:
            # create the neural network
            self.__init_nn(wrld, filename=self.nn_file)
        (dx,dy) = self.__calc_next_move(self.pair, wrld)
        if (dx,dy) == (0,0):
            self.place_bomb()
        else:
            self.move(dx,dy)
            self.pair = (self.pair[0]+dx,self.pair[1]+dy)
        
    def __list_next_moves(self, wrld, move=None):
        '''
        Use self to determine position on board, return
        a list of coordinates representing legal next moves.
        Note: return tuples of move locations
        '''
        pairs = [] # keep legal pairs
        if move is None:
            character_x = wrld.me(self).x
            character_y = wrld.me(self).y
        else:
            character_x = move[0]
            character_y = move[1]
        for d_x in range(-1, 2):
            for d_y in range(-1, 2):
                x = character_x + d_x
                y = character_y + d_y
                if self.__is_move_legal(wrld, x, y):
                    pairs.append((x, y))
        return pairs

    def __within_bounds(self, wrld, x, y):
        return x < wrld.width() and y < wrld.height() and x >= 0 and y >= 0

    def __is_move_legal(self, wrld, x, y):
        '''
        Determines if a move is legal
        '''
        if not self.__within_bounds(wrld,x,y):
            return False
        # move isn't allowed if theres a wall there
        if wrld.wall_at(x,y):
            return False
        # can't place a bomb if one already exists
        if (wrld.characters_at(x,y) is not None 
            and len(wrld.bombs) > 0):
                return False
        return True

    def __find_max_a(self, pair, weights, wrld):
        '''
        @ray
        predicts the maximum quality value for the given move
        '''
        # initialize max_a with a curiosity score
        max_a = self.k/(self.tried_pairs[pair] + 1)
        # find the dx, dy for the given move
        # so we can add it every simulation step
        dx = pair[0] - self.pair[0]
        dy = pair[1] - self.pair[1]
        cur_move = [pair[0], pair[1]]
        #print("DX", dx, "DY", dy)
        # clone the world so we can simulate it
        clone_wrld = SensedWorld.from_world(wrld)
        # keep simulating into the future if this path is taken
        # until we hit a move that is illegal (like hitting into a wall)
        first = True
        bomb_pos = None
        while True:
            # add the dx,dy for this simulation step
            cur_move[0] += dx
            cur_move[1] += dy
            me = clone_wrld.me(self)
            # we died, so this estimate has ended
            if me is None:
                # died
                break
            # we are dropping a bomb
            # this works differently than moves
            # since when you drop a bomb you don't keep going
            # this simulates what will eventually happen if it explodes
            # and it assumes the agent moves out of the way
            if dx == 0 and dy == 0 and first:
                # place the bomb
                me.place_bomb()
                bomb_pos = cur_move
            else:
                # otherwise, simply move in the dx,dy direction
                me.move(dx,dy)
            # simulate the world
            (clone_wrld, _) = clone_wrld.next()
            # if the move is illegal, the estimation is over
            if not self.__is_move_legal(wrld, cur_move[0], cur_move[1]):
                break
            # get the approximate q value, get the values for this
            # simulated world and calulate q
            vals = self.__approx_vals(clone_wrld,cur_move)
            q = sum([weights[i] * f for i, f in enumerate(vals)])
            # increase the number of times this has been tried
            m_tuple = (cur_move[0], cur_move[1])
            if m_tuple not in self.tried_pairs:
                self.tried_pairs[m_tuple] = 0
            # add the calculated q value to the curiosity score
            q = q + self.k/(self.tried_pairs[m_tuple] + 1)
            #print("Q", q)
            # if this q value is better, then make it the new max_a
            if q > max_a:
                max_a = q
            first = False
            if dx == 0 and dy == 0 and not first:
                if clone_wrld.me(self) is None:
                    # died
                    break
                # break if the bomb has blown up
                if clone_wrld.bomb_at(bomb_pos[0],bomb_pos[1]) is None:
                    break
                # move once if we are on top of the bomb
                if cur_move == bomb_pos:
                    moves = self.__list_next_moves(clone_wrld)
                    move = moves[randrange(0,len(moves))]
                    me.move(move[0]-pair[0],move[1]-pair[1])
            first = False
        #print("A", max_a, "DX", dx, "DY", dy)
        return max_a

    def __dist_to_goal(self, wrld, pair):
        e = wrld.exitcell
        return np.linalg.norm(np.subtract(e,pair))

    def calc_q(self, pair, weights, wrld, r=None):
        '''
        @ray
        Calculates and returns the q value and weights
        given a tuple pair for move and the current weights
        '''
        if pair not in self.tried_pairs:
            self.tried_pairs[pair] = 0
        else:
            if self.explore:
                self.tried_pairs[pair] += 1
        # find the estimate of q using the neural network
        state_vals = self.__approx_vals(wrld,pair)
        if weights is None:
            weights = [1] * len(state_vals)
        # find the estimated max future q
        max_a = self.__find_max_a(pair, weights, wrld)
        """
        max_a = -1000
        for move in self.__list_next_moves(wrld,move=pair):
            new_wrld = SensedWorld.from_world(wrld)
            dx = move[0] - pair[0]
            dy = move[1] - pair[1]
            me = new_wrld.me(self)
            if me is None:
                continue
            if dx == 0 and dy == 0:
                me.place_bomb()
            else:
                me.move(dx,dy)
            (new_wrld,_) = new_wrld.next()
            vals = self.__approx_vals(new_wrld,move)
            q_approx = sum([weights[i] * f for i, f in enumerate(vals)])
            if q_approx > max_a:
                max_a = q_approx
        """
        if r is None:
            r = self.__calc_reward(pair, wrld)
        #print("R",r)
        delta = (r + self.gamma * max_a) - self.q
        weights = [weights[i] + self.alpha * delta * f 
            for i, f in enumerate(state_vals)]
        # update the neural network
        self.__update_nn(wrld,state_vals,weights,pair)
        # calculate the next q value step
        q = sum([weights[i] * f for i, f in enumerate(state_vals)])
        return (
            q,
            weights
        )
    
    def __calc_reward(self, pair, wrld):
        # calculates the difference in score between one turn to the next
        clone_wrld = SensedWorld.from_world(wrld)
        dx = pair[0] - self.pair[0]
        dy = pair[1] - self.pair[1]
        me = clone_wrld.me(self)
        if me is None:
            # died
            return -1000
        me.move(dx,dy)
        (clone_wrld, _) = clone_wrld.next()
        score = clone_wrld.scores["me"] - wrld.scores["me"]
        # cost of living
        #score -= self.__dist_to_goal(wrld,pair)
        score -= 5
        return score
        #return -self.__dist_to_goal(wrld,pair)
        
    def __calc_next_move(self, pair, wrld):
        '''
        @ray
        Calculates the next move based on approximate q learning
        '''
        # take a new move using epsilon greedy exploration
        new_move = None
        next_moves = self.__list_next_moves(wrld)
        x = uniform(0, 1)
        if x < self.eps:
            # exploration
            new_move = next_moves[randrange(0,len(next_moves))]
            (self.q, self.weights) = self.calc_q(new_move, self.weights, wrld)
        else:
            # exploitation
            max_q = -inf
            max_weights = None
            for move in next_moves:
                (cur_q, w) = self.calc_q(move, self.weights, wrld)
                if cur_q > max_q:
                    max_q = cur_q
                    new_move = move
                    max_weights = w
            self.q = max_q
            self.weights = max_weights
        # decrease epsilon
        if self.eps > 0:
            self.eps -= 0.01
        if self.eps < 0:
            self.eps = 0
        new_move = (new_move[0]-self.pair[0],new_move[1]-self.pair[1])
        #print("Q", self.q, "W", self.weights)
        #print(self.pair, new_move)
        return new_move
