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
    def __init__(self, wrld):
        super(BombNet, self).__init__()
        # input convolutional layers
        #self.conv1 = nn.Conv2d(6,12,(8,4),padding=(3,2))
        self.conv1 = nn.Conv2d(6,12,4,padding=2)
        #self.conv2 = nn.Conv2d(12,12,4,padding=2)
        # size
        size = wrld.width()*wrld.height()
        # hidden layer
        self.lin1 = nn.Linear(2160,1024)
        self.lin2 = nn.Linear(1024,512)
        # output layer
        self.lin3 = nn.Linear(512,1)
        self.size = size
        
    def forward(self, x):
        #x = F.max_pool2d(F.relu(self.conv1(x)),(2,2))
        #x = F.max_pool2d(F.relu(self.conv2(x)),(2,2))
        x = F.relu(self.conv1(x))
        x = x.view(-1, 2160)
        x = F.relu(self.lin1(x))
        x = F.relu(self.lin2(x))
        x = self.lin3(x)
        return x

class TestCharacter(CharacterEntity):

    def __init__(self, name, avatar, x, y, nn_file=None, eps=0, training=False):
        super().__init__(name, avatar, x, y)
        self.gamma = 0.9
        self.alpha = 0.001
        self.q = 0
        self.eps = eps
        self.approx_net = None
        self.nn_file = nn_file
        self.training = training
        self.me_pos = (x,y)

        self.training_data = []

    def __init_nn(self, wrld, filename=None):
        if self.nn_file is not None:
            with open(filename,"rb") as f:
                self.approx_net = torch.load(f)
        else:
            self.approx_net = BombNet(wrld)
        self.optimizer = optim.Adam(self.approx_net.parameters(),lr=self.alpha)
        self.criterion = nn.MSELoss()
        
    def save_nn(self, filename):
        with open(filename, "wb") as f:
            torch.save(self.approx_net, f)

    def __approx_q(self, wrld, ev):
        x = torch.as_tensor(self.__get_wrld_v(wrld,ev), dtype=torch.float32)
        x = x.unsqueeze(0)
        out = self.approx_net(x)
        return out
    """
    def __update_nn(self,wrld,target):
        target = torch.tensor(np.asanyarray([[target]]),dtype=torch.float32)
        self.optimizer.zero_grad()
        output = self.__approx_q(wrld)
        loss = self.criterion(output,target)
        loss.backward()
        self.optimizer.step()
    """

    def __update_nn(self,training_data):
        for wrld, ev, target in training_data:
            #print(target)
            #(wrld,ev,target) = training_data[-1]
            target = torch.tensor(np.asanyarray([[target]]),dtype=torch.float32)
            self.optimizer.zero_grad()
            output = self.__approx_q(wrld,ev)
            loss = self.criterion(output,target)
            loss.backward()
            self.optimizer.step()
    """
    def __get_wrld_v(self, wrld):
        wrld_v = np.ndarray((6,6,6))
        me = wrld.me(self)
        if me is None:
            me = self.me_pos
        else:
            me = (me.x,me.y)
        # 'me' position
        for idx in np.ndindex((6,6)):
            # vision indices
            x_v = idx[0]
            y_v = idx[1]
            # board indices
            x = idx[0] + me[0] - 2
            y = idx[1] + me[1] - 2
            if not self.__within_bounds(wrld,x,y):
                wrld_v[x_v][y_v][:] = 0
                continue
            # what is at a cell
            wrld_v[x_v][y_v][:] = 0.5
            if wrld.wall_at(x,y):
                wrld_v[x_v][y_v][0] = 1
            if wrld.exit_at(x,y):
                wrld_v[x_v][y_v][1] = 1
            if wrld.bomb_at(x,y) is not None:
                wrld_v[x_v][y_v][2] = 1
            if wrld.explosion_at(x,y) is not None:
                wrld_v[x_v][y_v][3] = 1
            if wrld.monsters_at(x,y) is not None:
                wrld_v[x_v][y_v][4] = 1
            x_v = 2
            y_v = 2
            wrld_v[x_v][y_v][5] = 1
        return wrld_v
    """

    def __get_wrld_v(self,wrld,ev):
        wrld_v = np.ndarray((wrld.width(),wrld.height(),6))
        me = wrld.me(self)
        if me is None:
            for e in ev:
                # search the events to put the player
                # back on the map
                if (e.tpe == Event.BOMB_HIT_CHARACTER or 
                    e.tpe == Event.CHARACTER_FOUND_EXIT or
                    e.tpe == Event.CHARACTER_KILLED_BY_MONSTER):
                    me = (e.character.x,e.character.y)
        else:
            me = (me.x,me.y)
        # 'me' position
        for idx in np.ndindex((wrld.width(),wrld.height())):
            x = idx[0]
            y = idx[1]
            # what is at a cell
            wrld_v[x][y][:] = 0
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
            wrld_v[me[0]][me[1]][5] = 1
        return np.transpose(wrld_v)
    
    def do(self, wrld):
        if self.approx_net is None:
            # create the neural network
            self.__init_nn(wrld, filename=self.nn_file)
        s_wrld = SensedWorld.from_world(wrld)
        (dx,dy) = self.__calc_next_move(s_wrld)
        #(dx,dy) = self.__calc_next_interactive(s_wrld)
        #(dx,dy) = self.__calc_next_path(s_wrld)
        self.me_pos = (self.me_pos[0]+dx,self.me_pos[1]+dy)
        if (dx,dy) == (0,0):
            self.place_bomb()
        else:
            self.move(dx,dy)
        
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

    def __find_max_a(self, wrld, action):
        '''
        max_q = -100
        dx, dy = action
        clone = SensedWorld.from_world(wrld) # clone the world
        bomb = False
        #print("ACTION --", action)
        while True:
            me = clone.me(self)
            if  not self.__within_bounds(clone,dx+me.x,dy+me.y) or clone.wall_at(dx+me.x,dy+me.y):
                break
            if dx == 0 and dy == 0:
                me.place_bomb() # drop a bomb if we are not moving
                bomb = True
            else:
                me.move(dx, dy)
            clone, ev = clone.next()
            #clone.printit()
            q = self.__approx_q(clone, ev).item()
            print("A", q)
            if q > max_q:
                max_q = q
            if clone.me(self) is None or bomb:
                break
        #print("---")
        return max_q
        '''

        
        max_q = -inf
        for (dx,dy) in self.__list_next_moves(wrld):
            clone_wrld = SensedWorld.from_world(wrld)
            me = clone_wrld.me(self)
            if dx == 0 and dy == 0:
                me.place_bomb()
            else:
                me.move(dx,dy)
            (clone_wrld, ev) = clone_wrld.next()
            """
            print("TEST --", dx, dy)
            clone_wrld.printit()
            print(ev)
            print("----")
            """
            """
            (r, final) = self.__calc_r(clone_wrld,ev)
            if final:
                q = r
            else:
                a = self.__approx_q(clone_wrld,ev).item()
                q = r + self.gamma * a
            """
            q = self.__approx_q(clone_wrld,ev).item()
            #print("CUR A", q)
            if q > max_q:
                max_q = q
        #print("MAX Q", max_q)
        return max_q
        

    def __calc_r(self, wrld, ev):
        final_state = False
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
                r += 0.1
            elif event.tpe == Event.BOMB_HIT_WALL:
                r += 0.05
        # cost of living (positive?)
        """
        me = wrld.me(self)
        if me is not None:
            dist = np.linalg.norm(np.subtract((me.x,me.y),wrld.exitcell))
            r -= (1-(1/(dist+1)))/100
        """
        r -= 0.001
        return (r, final_state)

    def calc_q(self, wrld, ev, action):
        '''
        @ray
        Calculates and returns the q value given a world
        '''
        (r, final_state) = self.__calc_r(wrld, ev)
        # calculate the next q value step
        if final_state:
            target = r
        else:
            # find the estimated max future q
            max_a = self.__find_max_a(wrld, action)
            #print("MAX A", max_a)
            target = r + self.gamma * max_a
        q = self.q + self.alpha * (target - self.q)
        """
        if final_state is True:
            # update the neural network
            if self.training is True:
                self.__update_nn(wrld,target)
        """
        #q = self.__approx_q(wrld).item()
        #print("Q:", q, "TARGET: ", target, "R: ", r)
        return (q, target, final_state)
    ''
    def __calc_next_move(self, wrld):
        '''
        @ray
        Calculates the next move based on approximate q learning
        '''
        # take a new move using epsilon greedy exploration
        new_move = None
        chosen_world = None
        chosen_ev = None
        chosen_target = None
        final_state = False
        next_moves = self.__list_next_moves(wrld)
        x = uniform(0, 1)
        if x < self.eps:
            # exploration
            new_move = next_moves[randrange(0,len(next_moves))]
            chosen_world = SensedWorld.from_world(wrld)
            chosen_world.me(self).move(new_move[0],new_move[1])
            (chosen_world, chosen_ev) = chosen_world.next()
            (self.q, chosen_target, final_state) = self.calc_q(chosen_world, chosen_ev, new_move)
        else:
            # exploitation
            max_q = -inf
            for move in next_moves:
                c_wrld = SensedWorld.from_world(wrld)
                c_wrld.me(self).move(move[0],move[1])
                (c_wrld, ev) = c_wrld.next()
                (cur_q, cur_target, cur_fs) = self.calc_q(c_wrld, ev, move)
                if cur_q > max_q:
                    max_q = cur_q
                    new_move = move
                    chosen_world = c_wrld
                    chosen_target = cur_target
                    chosen_ev = ev
                    final_state = cur_fs
            self.q = max_q
        if self.training is True:
            self.training_data.append([chosen_world,chosen_ev,chosen_target])
            if final_state is True:
                print("Training...")
                self.__update_nn(self.training_data)
        return new_move
    
    def __calc_next_interactive(self, wrld):
        # Commands
        dx, dy = 0, 0
        # Handle input
        for c in input("How would you like to move (w=up,a=left,s=down,d=right)? "):
            if 'w' == c:
                dy -= 1
            if 'a' == c:
                dx -= 1
            if 's' == c:
                dy += 1
            if 'd' == c:
                dx += 1
        chosen_world = SensedWorld.from_world(wrld)
        chosen_world.me(self).move(dx,dy)
        (chosen_world, chosen_ev) = chosen_world.next()
        (self.q, chosen_target, final_state) = self.calc_q(chosen_world, chosen_ev,(dx,dy))
        if self.training is True:
            self.training_data.append([chosen_world,chosen_ev,chosen_target])
            if final_state is True:
                print("Training...")
                self.__update_nn(self.training_data)
        return (dx,dy)


    def __calc_next_path(self, wrld):
        chosen_world = SensedWorld.from_world(wrld)
        me = chosen_world.me(self)

        queue = [(me.x,me.y)]
        visited = {(me.x,me.y): None}
        while queue:
            s = queue.pop(0)
            if s == wrld.exitcell:
                break
            for (dx,dy) in self.__list_next_moves(chosen_world,move=s):
                move = (s[0]+dx,s[1]+dy)
                if move not in visited:
                    visited[move] = s
                    queue.append(move)

        end = wrld.exitcell
        dx = None; dy = None
        while True:
            if visited[end] is None or visited[visited[end]] is None:
                dx = end[0] - me.x
                dy = end[1] - me.y
                break
            end = visited[end]
        
        me.move(dx,dy)

        (chosen_world, chosen_ev) = chosen_world.next()
        (self.q, chosen_target, final_state) = self.calc_q(chosen_world, chosen_ev,(dx,dy))
        if self.training is True:
            self.training_data.append([chosen_world,chosen_ev,chosen_target])
            if final_state is True:
                print("Training...")
                self.__update_nn(self.training_data)
        return (dx,dy)