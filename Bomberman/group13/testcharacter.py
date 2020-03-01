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

class TestCharacter(CharacterEntity):

    def __init__(self, name, avatar, x, y, weights=None, eps=1):
        super().__init__(name, avatar, x, y)
        self.weights = None
        self.gamma = 0.9
        self.alpha = 0.001
        self.q = 0
        self.eps = eps
        self.pair = (x, y)
        self.tried_pairs = {}
        if weights is not None:
            self.weights = weights
        # curiosity constant
        self.k = 10

    def do(self, wrld):
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
        return True
    
    def __get_values(self, world, pair):
        ''' @dillon
        Call helper functions and return list
        '''
        a = self.__bomb_score(world, pair)
        b = self.__monster_score(world, pair)
        c = self.__goal_path_score(world, pair)
        d = self.__will_die_score(world, pair)
        #e = self.__enemy_bomb_score(world, pair)
        e = self.__no_path_score(world, pair)
        f = self.__chaos_score(world)
        g = self.__goal_distance_score(world,pair)
        return [a, b, c, d, e, f, g]

    def __chaos_score(self, wrld):
        return len(wrld.bombs)

    def __no_path_score(self, wrld, pair):
        ''' @ray
        returns 0 if there is no path to the end, 1 otherwise
        '''
        path_tuple = self.__path_to_point(wrld,pair,wrld.exitcell,incomplete=True)
        # if the path is complete, return 1
        if path_tuple[0]:
            return 1
        # otherwise return a value that increases to 1 as the path gets longer
        return 1-(1/(path_tuple[1]+1))

    def __will_die_score(self, wrld, pair):
        ''' @ray
        returns 0 if we will die if we move to that location, 1 otherwise
        '''
        for move in self.__list_next_moves(wrld, move=pair):
            if wrld.monsters_at(move[0], move[1]) is not None:
                return 0
            if wrld.explosion_at(move[0],move[1]) is not None:
                return 0
            if wrld.monsters_at(move[0],move[1]) is not None:
                return 0
            if wrld.bomb_at(move[0],move[1]) is not None:
                return 0
        return 1
    
    def __barriers_score(self, wrld, pair):
        ''' @ray and @dillon
        number of barriers between the agent and the goal
        
        create rectangle with source as (0, 0) and destination
        as (r, c); travel down left and right edges of rectangle,
        count walls (this avoids the need for path finding, could
        be tweaked with a min() or max() call or something similar)
        
        1/(barriers+1)
        '''
        barriers = 0
        src_col, src_row = self.pair
        dst_col, dst_row = wrld.exitcell
        for row in range(src_row, dst_row):
            if wrld.wall_at(src_col, row):
                barriers += 1
            if wrld.wall_at(dst_col, row):
                barriers += 1
        #print('barrier', barriers)
        return 1 / (barriers + 1)

    def __bomb_score(self, wrld, pair):
        ''' @joe and @ray
        Bombs within strike range of the character
        normalized between 0 and 1
        '''
        bomb_threats = 0
        # count all the bombs in a cross around the character
        for dx in range(-3,4):
            x = pair[0]+dx
            y = pair[1]
            if self.__is_move_legal(wrld,x,y) and wrld.bomb_at(x,y) is not None:
                 bomb_threats += 1
        for dy in range(-3,4):
            x = pair[0]
            y = pair[1]+dy
            if self.__is_move_legal(wrld,x,y) and wrld.bomb_at(x,y) is not None:
                bomb_threats += 1
        return 1/(bomb_threats+1)

    def __enemy_bomb_score(self, wrld, pair):
        ''' @ray
        Bombs within strike range of the enemy, but not of the player
        normalized between 0 and 1
        '''
        enemies_in_danger = 0
        bombs = [l for l in list(wrld.bombs.values())] # list of bombs
        for bomb in bombs:
            for i in range(2):
                for d in range(-2,3):
                    x = bomb.x; y = bomb.y
                    if i == 0:
                        x += d
                    else:
                        y += d
                    monsters = wrld.monsters_at(x,y)
                    if monsters is not None:
                        enemies_in_danger += len(monsters)
                    if pair == (x,y):
                        # in range of the player
                        return 0
        return 1 if enemies_in_danger > 0 else 0
        #return 1-(1/(enemies_in_danger+1))
                            
        
    def __monster_score(self, world, pair):
        ''' @dillon
        Distance to closest monster
        Score gets lower as the monster gets closer
        '''
        distances = [] # distances to monsters
        monsters = [l[0] for l in list(world.monsters.values())] # list of monsters
        for monster in monsters:
            """
            x, y = monster.x, monster.y
            d_x, d_y = pair[0] - x, pair[1] - y
            distance = sqrt(pow(d_x, 2) + pow(d_y, 2))
            distances.append(distance)
            """
            distances.append(self.__path_to_point(world,pair,(monster.x,monster.y)))
        #print(distances)
        return 1 if len(distances) == 0 or min(distances) > 4 else 1-(1/(min(distances)+1))
    
    def __path_to_point(self, wrld, pair, to, incomplete=False):
        pair = (pair[0], pair[1])
        visited = {pair: None}
        queue = [pair]
        end = None
        while queue:
            s = queue.pop(0)
            end = s
            if s == to:
                break
            for move in self.__list_next_moves(wrld, move=s):
                if move not in visited:
                    queue.append(move)
                    visited[move] = s
        path_length = 0
        while end is not None:
            """if to == wrld.exitcell:
                self.set_cell_color(end[0],end[1], Fore.RED + Back.GREEN)"""
            end = visited[end]
            path_length += 1
        # in incomplete mode, return (True, path length) if the
        # path is complete, return (False, length found) if
        # its incomplete
        if incomplete and to not in visited:
            return (False, path_length)
        elif incomplete:
            return (True, path_length)
        # end path was not found
        if to not in visited:
            path_length = inf
        return path_length

    def __goal_path_score(self, wrld, pair):
        path_tuple = self.__path_to_point(wrld,pair,wrld.exitcell,incomplete=True)
        if path_tuple[0]:
            return 1/(path_tuple[1]+1)
        return 0

    def __goal_distance(self, wrld, pair):
        goal_loc = wrld.exitcell
        #return sqrt(pow((goal_loc[0] - pair[0]),2) + pow((goal_loc[1] - pair[1]),2))
        return abs(goal_loc[0] - pair[0]) + abs(goal_loc[1] - pair[1])

    def __goal_distance_score(self, wrld, pair):
        ''' @ray
        (1/(distance + 1)) increases to 1 as
        the agent gets closer to the goal and decreases
        as the agent gets farther way
        '''
        return 1/(self.__goal_distance(wrld, pair)+1)

    def __find_max_a(self, pair, weights, wrld):
        '''
        @ray
        predicts the maximum quality value for the given move
        '''
        max_a = self.k/(self.tried_pairs[pair] + 1)
        dx = pair[0] - self.pair[0]
        dy = pair[1] - self.pair[1]
        cur_move = [pair[0], pair[1]]
        #print("DX", dx, "DY", dy)
        clone_wrld = SensedWorld.from_world(wrld)
        while True:
            cur_move[0] += dx
            cur_move[1] += dy
            me = clone_wrld.me(self)
            if me is None:
                # died
                break
            if dx == 0 and dy == 0:
                if len(clone_wrld.bombs) > 0:
                    # already a bomb, no value to this state
                    break
                # calculate the quality value if monsters/blocks
                # adjacent were blown up
                for i in range(2):
                    for d in range(-5,5):
                        x = pair[0]; y = pair[1]
                        if i == 0:
                            x += d
                        else:
                            y += d
                        if self.__within_bounds(wrld,x,y):
                            monsters = clone_wrld.monsters_at(x,y)
                            if monsters is not None:
                                for monster in monsters:
                                    clone_wrld.remove_character(monster)
                            if clone_wrld.wall_at(x,y):
                                clone_wrld.grid[x][y] = None
                # add bomb so it's factored into bomb threats
                clone_wrld.add_bomb(cur_move[0],cur_move[1],me)
                """
                clone_wrld.add_bomb(cur_move[0],cur_move[1],me)
                # TODO: can there be more than one bomb?
                clone_wrld.add_blast(clone_wrld.bombs[0])
                """
            else:
                me.move(dx,dy)
            (clone_wrld, _) = clone_wrld.next()
            """
            print("AFTER:", dx, dy)
            clone_wrld.printit()
            print("----")
            """
            if not self.__is_move_legal(wrld, cur_move[0], cur_move[1]):
                break
            vals = self.__get_values(clone_wrld, cur_move)
            q = sum([weights[i] * f for i, f in enumerate(vals)])
            # favor curiosity by decaying by the number of times
            # this particular pair has been tried
            m_tuple = (cur_move[0], cur_move[1])
            if m_tuple not in self.tried_pairs:
                self.tried_pairs[m_tuple] = 0
            q = q + self.k/(self.tried_pairs[m_tuple] + 1)
            #print("Q", q)
            if q > max_a:
                max_a = q
            # only iterate once for bomb placements
            if dx == 0 and dy == 0:
                break
        #print("A", max_a, "DX", dx, "DY", dy)
        return max_a

    def calc_q(self, pair, weights, wrld, r=None):
        '''
        @ray
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
        if r is None:
            r = self.__calc_reward(pair, wrld)
        #print("R",r)
        delta = (r + self.gamma * max_a) - self.q
        weights = [weights[i] + self.alpha * delta * f 
            for i, f in enumerate(state_vals)]
        # calculate the next q value step using approximate q learning
        return (
            sum([weights[i] * f for i, f in enumerate(state_vals)]),
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
        # cost of living should be negative
        if score == 1:
            score = -1
        return score
        
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
