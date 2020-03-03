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
from events import Event
import numpy as np
import pickle
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class BombNet(nn.Module):
    def __init__(self,wrld):
        super(BombNet, self).__init__()
        self.conv1 = nn.Conv2d(6,12,2,padding=1)
        self.conv2 = nn.Conv2d(12,20,2)
        # size
        size = wrld.width()*wrld.height()
        # hidden layer
        self.lin1 = nn.Linear(80,50)
        # world dimensions to q value
        self.lin2 = nn.Linear(50,1)
        self.size = size
        
    def forward(self, x):
        x = F.max_pool2d(F.relu(self.conv1(x)),(2,2))
        x = F.max_pool2d(F.relu(self.conv2(x)),(2,2))
        x = x.view(-1, 80)
        x = F.relu(self.lin1(x))
        x = self.lin2(x)
        return x

class TestCharacter(CharacterEntity):

    def __init__(self, name, avatar, x, y, nn_file=None, eps=0, training=False):
        super().__init__(name, avatar, x, y)
        self.gamma = 0.9
        self.alpha = 0.1
        self.q = 0
        self.eps = eps
        self.approx_net = None
        self.nn_file = nn_file
        self.training = training

    def __init_nn(self, wrld, filename=None):
        if self.nn_file is not None:
            with open(filename,"rb") as f:
                self.approx_net = torch.load(f)
        else:
            self.approx_net = BombNet(wrld)
        self.optimizer = optim.SGD(self.approx_net.parameters(),lr=self.alpha)
        self.criterion = nn.MSELoss()
        
    def save_nn(self, filename):
        with open(filename, "wb") as f:
            torch.save(self.approx_net, f)

    def __approx_q(self, wrld):
        x = torch.as_tensor(self.__get_wrld_v(wrld), dtype=torch.float32)
        x = x.unsqueeze(0)
        out = self.approx_net(x)
        return out
    
    def __update_nn(self,wrld,target):
        target = torch.tensor(np.asanyarray([[target]]),dtype=torch.float32)
        self.optimizer.zero_grad()
        self.approx_net.zero_grad()
        output = self.__approx_q(wrld)
        loss = self.criterion(output,target)
        loss.backward()
        self.optimizer.step()

    def __get_wrld_v(self, wrld):
        wrld_v = np.ndarray((wrld.width(),wrld.height(),6))
        for idx in np.ndindex((wrld.width(),wrld.height())):
            x = idx[0]
            y = idx[1]
            # what is at a cell
            wrld_v[x][y][:] = 0.5
            if wrld.wall_at(x,y):
                wrld_v[x][y][0] = 1
            if wrld.exit_at(x,y):
                wrld_v[x][y][1] = 1
            if wrld.bomb_at(x,y) is not None:
                wrld_v[x][y][2] = 1
            if wrld.explosion_at(x,y) is not None:
                wrld_v[x][y][3] = 1
            if wrld.monsters_at(x,y) is not None:
                wrld_v[x][y][4] = 1
            if wrld.characters_at(x,y) is not None:
                wrld_v[x][y][5] = 1
        return np.transpose(wrld_v)

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
        # cannot drop a bomb if one is already there
        me = wrld.me(self)
        if me is not None:
            if (me.x,me.y) == (x,y):
                return False
            if (x,y) == (me.x,me.y) and len(wrld.bombs) > 0:
                return False
        return True

    def __find_max_a(self, wrld):
        max_q = -inf
        for (dx,dy) in self.__list_next_moves(wrld):
            clone_wrld = SensedWorld.from_world(wrld)
            me = clone_wrld.me(self)
            if dx == 0 and dy == 0:
                me.place_bomb()
            else:
                me.move(dx,dy)
            (clone_wrld, _) = clone_wrld.next()
            """
            print("TEST --", dx, dy)
            clone_wrld.printit()
            print("----")
            """
            q = self.__approx_q(clone_wrld).item()
            if q > max_q:
                max_q = q
        #print("MAX Q", max_q)
        return max_q

    def __calc_r(self, wrld, ev, final_state):
        r = 0
        for event in ev:
            if event.tpe == Event.CHARACTER_FOUND_EXIT:
                r += 10
                final_state = True
            elif event.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
                r -= 100
                final_state = True
            elif event.tpe == Event.BOMB_HIT_CHARACTER:
                r -= 100
                final_state = True
            elif event.tpe == Event.BOMB_HIT_MONSTER:
                r += 0.01
            elif event.tpe == Event.BOMB_HIT_WALL:
                r += 0.005
        # cost of living (positive?)
        """
        me = wrld.me(self)
        if me is not None:
            dist = np.linalg.norm(np.subtract((me.x,me.y),wrld.exitcell))
            r -= (1-(1/(dist+1)))/100
        """
        r -= 0.00001
        return (r, final_state)

    def calc_q(self, wrld, ev, r=None, final_state=False):
        '''
        @ray
        Calculates and returns the q value given a world
        '''
        if r is None:
            (r, final_state) = self.__calc_r(wrld, ev, final_state)
        # calculate the next q value step
        if final_state:
            diff = self.alpha * (r + self.q)
        else:
            # find the estimated max future q
            max_a = self.__find_max_a(wrld)
            #print("MAX A", max_a)
            diff = self.alpha * (r + self.gamma * max_a - self.q)
        target = self.q + diff
        # update the neural network
        if self.training is True:
            self.__update_nn(wrld,target)
        q = self.__approx_q(wrld).item()
        #print("ESTIM Q:", q, "TARGET: ", target, "R: ", r)
        return q
        
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
            (c_wrld, ev) = c_wrld.next()
            self.q = self.calc_q(c_wrld, ev)
        else:
            # exploitation
            max_q = -inf
            for move in next_moves:
                c_wrld = SensedWorld.from_world(wrld)
                c_wrld.me(self).move(move[0],move[1])
                (c_wrld, ev) = c_wrld.next()
                cur_q = self.calc_q(c_wrld, ev)
                if cur_q > max_q:
                    max_q = cur_q
                    new_move = move
            self.q = max_q
        return new_move
