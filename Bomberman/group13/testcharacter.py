# This is necessary to find the main code
import sys
from math import inf, sqrt
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from random import uniform, randrange
from math import sqrt

class TestCharacter(CharacterEntity):

    def __init__(self, name, avatar, x, y):
        super().__init__(name, avatar, x, y)
        self.weights = None
        self.gamma = 0.9
        self.alpha = 0.001
        self.q = 0
        self.r = -1
        self.eps = 5
        self.pair = (x, y)
        self.tried_pairs = {}
        # curiosity constant
        self.k = 10

    def do(self, wrld):
        #x = self.__get_values(wrld, (0, 0))
        #print(x)
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
        # don't allow bombs yet
        if self.pair == (x, y):
            return False
        # move isn't allowed if theres a wall there
        if wrld.wall_at(x,y):
            return False
        # move isn't allowed if it will go into a monster
        if wrld.monsters_at(x,y) is not None:
            return False
        return True
    
    def __get_values(self, world, pair):
        ''' @dillon
        Call helper functions and return list
        '''
        a = self.__bomb_score(world, pair)
        b = self.__monster_score(world, pair)
        c = self.__goal_distance_score(world, pair)
        d = self.__block_score(world, pair)
        e = self.__barriers_score(world, pair)
        return [a, b, c, d]
        
    
    def __barriers_score(self, wrld, pair):
        ''' @ray
        number of barriers between the agent and the goal
        1/(barriers+1)
        '''
        goal_pos = wrld.exitcell
        cur_pos = self.pair
        barriers = 0
        
        return 1/(barriers+1)
        
    
    def __block_score(self, wrld, pair):
        ''' @ray
        1/((number of blocks around us) + 1)
        '''
        blocks = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                x_n = pair[0]+dx
                y_n = pair[1]+dy
                if not self.__within_bounds(wrld,x_n,y_n):
                    blocks += 1
                elif wrld.wall_at(x_n,y_n):
                    blocks += 1
        return 1/(blocks+1)

        
    def __bomb_score(self, wrld, pair):
        ''' @joe
        Bombs within strike range
        '''
        bomb_threats = 0
        for dx in range(0, wrld.width()):
            if(wrld.bomb_at(dx, pair[1])):
                bomb_threats += 1
        for dy in range(0, wrld.height()):
            if(wrld.bomb_at(pair[0], dy)):
                bomb_threats += 1
        return bomb_threats 
        
    def __monster_score(self, world, pair):
        ''' @dillon
        Distance to closest monster
        Score gets lower as the monster gets closer
        '''
        distances = [] # distances to monsters
        monsters = [l[0] for l in list(world.monsters.values())] # list of monsters
        for monster in monsters:
            x, y = monster.x, monster.y
            d_x, d_y = pair[0] - x, pair[1] - y
            distance = sqrt(pow(d_x, 2) + pow(d_y, 2))
            distances.append(distance)
        return 0 if len(distances) == 0 else 1/(min(distances)+1)
        
    def __goal_distance(self, wrld, pair):
        goal_loc = wrld.exitcell
        return sqrt(pow((goal_loc[0] - pair[0]),2) + pow((goal_loc[1] - pair[1]),2))

    def __goal_distance_score(self, wrld, pair):
        ''' @ray
        (1/(Euclidean distance + 1)) increases to 1 as
        the agent gets closer to the goal and decreases
        as the agent gets farther way
        '''
        return 1/(self.__goal_distance(wrld, pair)+1)

    def __find_max_a(self, pair, weights, wrld):
        max_a = self.k/(self.tried_pairs[pair] + 1)
        dx = pair[0] - self.pair[0]
        dy = pair[1] - self.pair[1]
        cur_move = [pair[0], pair[1]]
        print("DX", dx, "DY", dy)
        while True:
            cur_move[0] += dx
            cur_move[1] += dy
            if not self.__is_move_legal(wrld, cur_move[0], cur_move[1]):
                break
            vals = self.__get_values(wrld, cur_move)
            q = sum([weights[i] * f for i, f in enumerate(vals)])
            # favor curiosity by decaying by the number of times
            # this particular pair has been tried
            m_tuple = (cur_move[0], cur_move[1])
            if m_tuple not in self.tried_pairs:
                self.tried_pairs[m_tuple] = 0
            q = q + self.k/(self.tried_pairs[m_tuple] + 1)
            print("Q", q)
            if q > max_a:
                max_a = q
        print("A", max_a)
        return max_a

    def __calc_q(self, pair, weights, wrld):
        '''
        Calculates and returns the q value and weights
        given a tuple pair for move and the current weights
        '''
        if pair not in self.tried_pairs:
            self.tried_pairs[pair] = 0
        else:
            self.tried_pairs[pair] += 1
        # retrieve state values and calculate new weights
        state_vals = self.__get_values(wrld, pair)
        if weights is None:
            weights = [1 for _ in state_vals]
        # find the estimated max future q
        # decay this by the amount of times we've tried this pair
        # to favor curiosity
        max_a = self.__find_max_a(pair, weights, wrld)
        delta = (self.r + self.gamma * max_a) - self.q
        weights = [weights[i] + self.alpha * delta * f 
            for i, f in enumerate(state_vals)]
        # calculate the next q value step using approximate q learning
        return (
            sum([weights[i] * f for i, f in enumerate(state_vals)]),
            weights
        )
        
    def __calc_next_move(self, pair, wrld):
        '''
        Calculates the next move based on approximate q learning
        '''
        # take a new move using epsilon greedy exploration
        new_move = None
        next_moves = self.__list_next_moves(wrld)
        x = uniform(0, 1)
        if x < self.eps:
            # exploration
            new_move = next_moves[randrange(0,len(next_moves))]
            (self.q, self.weights) = self.__calc_q(new_move, self.weights, wrld)
        else:
            # exploitation
            max_q = -inf
            max_weights = None
            for move in next_moves:
                (cur_q, w) = self.__calc_q(move, self.weights, wrld)
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
        print("Q", self.q, "W", self.weights)
        print(self.pair, new_move)
        return new_move
