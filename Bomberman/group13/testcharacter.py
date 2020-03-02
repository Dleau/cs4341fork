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
import numpy as np
import pickle
import torch
import torch.nn as nn
import torch.nn.functional as F

class BombNet(nn.Module):
    def __init__(self,wrld):
        super(BombNet, self).__init__()
        self.conv1 = nn.Conv2d(1,6,3)
        # size
        size = wrld.width()*wrld.height()
        # hidden layer
        self.lin1 = nn.Linear(size,int(size/2))
        # world dimensions to q value
        self.lin2 = nn.Linear(int(size/2),1)
    
    def forward(self, x):
        x = F.max_pool2d(F.relu(self.conv1(x)),(2,2))
        x = F.relu(self.lin1(x))
        x = F.relu(self.lin2(x))
        return x

    def __get_wrld_v(self, wrld):
        wrld_v = np.ndarray((wrld.width(),wrld.height()))
        for idx in np.ndindex(wrld_v.shape):
            x = idx[0]
            y = idx[1]
            # what is at a cell
            wrld_v[x][y] = 1
            if wrld.wall_at(x,y):
                wrld_v[x][y] = 2
            elif wrld.exit_at(x,y):
                wrld_v[x][y] = 3
            elif wrld.bomb_at(x,y) is not None:
                wrld_v[x][y] = 4
            elif wrld.explosion_at(x,y) is not None:
                wrld_v[x][y] = 5
            elif wrld.monsters_at(x,y) is not None:
                wrld_v[x][y] = 6
            elif wrld.characters_at(x,y) is not None:
                wrld_v[x][y] = 7
        return wrld_v

class TestCharacter(CharacterEntity):

    def __init__(self, name, avatar, x, y, nn_file=None, eps=0):
        super().__init__(name, avatar, x, y)
        self.gamma = 0.9
        self.alpha = 0.1
        self.q = 0
        self.eps = eps
        self.pair = (x, y)
        self.approx_net = None
        self.nn_file = nn_file

    def __init_nn(self, wrld, filename=None):
        if self.nn_file is not None:
            with open(filename,"rb") as f:
                self.approx_net = torch.load(f)
            return
        self.approx_net = BombNet(wrld)
        
    def save_nn(self, filename):
        with open(filename, "wb") as f:
            torch.save(self.approx_net, f)

    def __approx_q(self, wrld):
        pass
    
    def __update_nn(self,wrld,v_out):
        pass

    def do(self, wrld):
        if self.approx_net is None:
            # create the neural network
            self.__init_nn(wrld, filename=self.nn_file)
        s_wrld = SensedWorld.from_world(wrld)
        (dx,dy) = self.__calc_next_move(s_wrld)
        if (dx,dy) == (0,0):
            self.place_bomb()
        else:
            self.move(dx,dy)
            self.pair = (self.pair[0]+dx,self.pair[1]+dy)
        
    def __list_next_moves(self, wrld):
        '''
        Use self to determine position on board, return
        a list of coordinates representing legal next moves.
        Note: return tuples of move locations
        '''
        pairs = [] # keep legal pairs
        character_x = wrld.me(self).x
        character_y = wrld.me(self).y
        for d_x in range(-1, 2):
            for d_y in range(-1, 2):
                x = character_x + d_x
                y = character_y + d_y
                if self.__is_move_legal(wrld, x, y):
                    pairs.append((d_x, d_y))
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
        return True

    def __find_max_a(self, wrld):
        max_q = -inf
        if wrld.me(self) is None:
            # died
            return self.__approx_q(wrld)
        for (dx,dy) in self.__list_next_moves(wrld):
            clone_wrld = SensedWorld.from_world(wrld)
            me = clone_wrld.me(self)
            if me is None:
                # died
                pass
            elif dx == 0 and dy == 0:
                me.place_bomb()
            else:
                me.move(dx,dy)
            (clone_wrld, _) = clone_wrld.next()
            """
            print("TEST --", dx, dy)
            clone_wrld.printit()
            print("----")
            """
            q = self.__approx_q(clone_wrld)
            if q > max_q:
                max_q = q
        return max_q

    def __dist_to_goal(self, wrld, pair):
        e = wrld.exitcell
        return np.linalg.norm(np.subtract(e,pair))

    def calc_q(self, wrld, r=None, final_state=False):
        '''
        @ray
        Calculates and returns the q value given a world
        '''
        if r is None:
            # cost of living
            r = -1
        # calculate the next q value step
        if final_state:
            diff = self.alpha * (r - self.q)
        else:
            # find the estimated max future q
            max_a = self.__find_max_a(wrld)
            print("MAX A", max_a)
            diff = self.alpha * (r + self.gamma * max_a - self.q)
        target = self.q + diff
        # update the neural network
        self.__update_nn(wrld,[target])
        return self.__approx_q(wrld)
        
    def __calc_next_move(self, wrld):
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
            c_wrld = SensedWorld.from_world(wrld)
            c_wrld.me(self).move(new_move[0],new_move[1])
            (c_wrld, _) = c_wrld.next()
            self.q = self.calc_q(c_wrld)
        else:
            # exploitation
            max_q = -inf
            for move in next_moves:
                c_wrld = SensedWorld.from_world(wrld)
                c_wrld.me(self).move(move[0],move[1])
                (c_wrld, _) = c_wrld.next()
                cur_q = self.calc_q(c_wrld)
                if cur_q > max_q:
                    max_q = cur_q
                    new_move = move
            self.q = max_q
        return new_move
