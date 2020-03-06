# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from sensed_world import SensedWorld
from random import uniform, randrange
from math import inf, sqrt
from time import sleep
from events import Event
from queue import PriorityQueue



class SpecialOpsCharacter(CharacterEntity):

    # NOTE use approx_qlearning.png!!!, literally following that to the letter
    # action, a.k.a "a" in the formula, is (dx, dy) tuple
        
    # order of determination: max a, delta, weights, q

    def __init__(self, name, avatar, x, y, eps=0, weights=None):
        # @dillon
        super().__init__(name, avatar, x, y)
        self.alpha = 0.01 # alpha value for use in q-learning formula
        self.gamma = 0.9 # gamma value, likewise
        self.epsilon = eps # epsilon value, likewise
        self.q = 0
        if weights is None:
            self.weights = {f.__name__: 1 for f in self.__functions()} # function name -> weight
        else:
            self.weights = weights
        self.max_a = None
        self.max_q = 0
        self.clone = None
        self.events = []
        self.curiosity_scores = {}

    def do(self, world):
        # Commands
        ''' @dillon
        Does the next move
        '''
        #sleep(0.5) # helpful for debugging
        #input() # alternative, also helpful
        # gets the next best action using max a
        dx, dy = self.__next_action(world)
        # updates the function weights using max a and delta
        for function in self.__functions():
            self.__w_i(world, (dx, dy), function)
        # determines a q value for this state
        self.q = self.__q(world, (dx, dy)) 
        
        # updates curiosity scores
        '''
        x, y = self.__s(world)
        state_tuple = (dx, dy, x, y) 
        if state_tuple not in self.curiosity_scores:
            self.curiosity_scores[state_tuple] = 0
        self.curiosity_scores[state_tuple] += 1
        '''

        if (dx, dy) == (0, 0):
            self.place_bomb()
            # self.move(dx, dy) # for debugging only
        else:
            self.move(dx, dy)

        #print(self.weights)
        #print('q', self.q)
        #print('epsilon', self.epsilon)
            
    def __next_action(self, world):
        ''' @dillon
        Considers possible (dx, dy) actions from current position,
        either explores or exploits. Exploitation uses max a to find
        optimal (dx, dy) action.
        '''
        possible_actions = self.__possible_actions(world)
        z = uniform(0, 1)
        if z < self.epsilon: # exploration
            return possible_actions[randrange(0, len(possible_actions))] # pick random action
        else: # exploitation
            return self.__max_a(world)
      
    def __functions(self):
        ''' @dillon
        List f1 through fn
        Every function must take ONLY world and action as args
        '''
        '''
        return [self.__goal_dist_score, self.__bomb_threats, 
            self.__distance_to_monster, self.__wall_blow_up_score,
            self.__chaos_score]
        '''
        return [
            self.__goal_dist_score,
            self.__distance_to_monster,
            self.__goal_to_monster_ratio,
            self.__goal_distance_as_crow,
            self.__bomb_threats
        ]
        
    def __goal_distance_as_crow(self, world, action):
        ''' @dillon, @ray
        Distance to goal as the crow flies, crows can go over walls
        Uses ignore_walls=True in BFS method
        Helpful for bombs, identifying when paths could be more direct
        '''
        goal_loc = world.exitcell
        char_pos = (world.me(self).x+action[0],world.me(self).y+action[1])
        path = self.__bfs(world,char_pos,goal_loc, ignore_walls=True)
        if not path[1]: return 1
        else: return 1/(len(path[0])+1)
        
    def __goal_to_monster_ratio(self, world, action):
        ''' @dillon
        (distance to goal) : (distance to closest monster)
        Incentivize cooking the monster once closer to the goal than him
        '''
        goal = self.__goal_dist_score(world, action)
        monster = self.__distance_to_monster(world, action)
        ratio = goal / monster
        return 1 / (1 + ratio) # so that closer to 1 is better (I think)
    
    def __could_die(self, world, action):
        ''' @ray
        Returns 0 if this move could cause the agent to die
        returns 1 otherwise
        '''
        me = world.me(self)
        (x,y) = (me.x+action[0],me.y+action[1])
        if world.bomb_at(x,y) is not None:
            return 0
        return 1
        
    def __goal_dist_score(self, world, action):
        ''' @ray
        BFS distance to the goal, 0 if blocked
        '''
        goal_loc = world.exitcell
        char_pos = (world.me(self).x+action[0],world.me(self).y+action[1])
        #goal_dist = sqrt(pow((goal_loc[0] - action[0]),2) + pow((goal_loc[1] - action[1]),2))
        path = self.__bfs(world,char_pos,goal_loc)
        if not path[1]:
            return 1
        return 1/(len(path[0])+1)
    
    def __wall_blow_up_score(self, world, action):
        ''' @ray
        1 if there is a bomb by a wall, 0 otherwise
        '''
        for bomb in world.bombs.values():
            pos = (bomb.x, bomb.y)
            for n_x, n_y in self.__list_neighbors(world,pos):
                if world.wall_at(n_x,n_y):
                    return 1
        return 0
    
    def __chaos_score(self, world, action):
        ''' @ray
        returns 0 if theres no bomb on screen, 1 if there is
        '''
        if len(world.bombs.keys()) > 0:
            return 1
        return 0
    
    def __bfs(self, world, fr, to, ignore_walls=False):
        ''' @ray
        Returns the path from 'from' to 'to'
        if the path doesn't exist then it returns
        the incomplete path
        (path, True) if complete
        (path, False) if incomplete
        
        use BFS and go through walls w/ ignore_walls=True
        '''
        queue = [fr]
        came_from = {fr: None}
        while queue:
            s = queue.pop(0)
            if s == to:
                break
            neighbors = None
            if ignore_walls: neighbors = self.__surrounding_pairs(world) # get path w/ walls
            else: neighbors = self.__list_neighbors(world, s) # get path w/out walls
            for neighbor in neighbors:
                if neighbor not in came_from:
                    came_from[neighbor] = s
                    queue.append(neighbor)
        path = []
        complete = False
        while to is not None:
            path = [to] + path
            if to in came_from and fr == came_from[to]:
                complete = True
            if to not in came_from:
                break
            to = came_from[to]
        return (path, complete)

    def __a_star(self, world, fr, to):
        ''' @Joe
        Returns the path from 'from' to 'to'
        if the path doesn't exist then it returns
        the incomplete path
        (path, True) if complete
        (path, False) if incomplete
        '''
        start = fr
        goal = to
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0    
        while not frontier.empty():
            current = frontier._get()
            if current == goal:
                break
            for next in self.__list_neighbors(world,current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + sqrt(pow((goal[0] - next[0]),2) + pow((goal[1] - next[1]),2))
                    frontier.put(next, priority)
                    came_from[next] = current
        path = []
        complete = False
        while to is not None:
            path = [to] + path
            if to in came_from and fr == came_from[to]:
                complete = True
            if to not in came_from:
                break
            to = came_from[to]
        return (path, complete)
        
    def __bomb_threats(self, world, action):
        ''' @dillon
        Threatening bombs, 1 is 0 bombs, 0 is a bomb
        '''
        pos = self.__s(world)
        (x,y) = (pos[0]+action[0],pos[1]+action[1])
        bomb_threats = 0
        for dx in range(-3, 4):
            if not self.__within_bounds(world,x+dx,y):
                continue
            if world.bomb_at(x+dx, action[1]):
                bomb_threats += 1
        for dy in range(-3, 4):
            if dy == 0:
                continue
            if not self.__within_bounds(world,x,y+dy):
                continue
            if world.bomb_at(y+dy, dy):
                bomb_threats += 1
        return 1 if bomb_threats == 0 else 0
        
    def __distance_to_monster(self, world, action):
        ''' @ray
        Path distance to nearest monster
        '''
        distances = [] # distances to monsters
        monsters = [l[0] for l in list(world.monsters.values())] # list of monsters
        for monster in monsters:
            x, y = self.__s(world)
            x += action[0]
            y += action[1]
            path, unblocked = self.__bfs(world, (x,y), (monster.x,monster.y))
            if unblocked:
                distances.append(len(path))
        return 1 if len(distances) == 0 else 1-(1/(min(distances) + 1))
        #return 0 if not len(distances) else min(distances)
            
    def __q(self, world, action):
        ''' @dillon
        Approximate q-learning function
        Q(s, a) = w1 * f1(s, a) + ... + wn * fn(s, a)
        f1(s, a) -> takes state and action, state derived from __s
        '''
        sum = 0
        for function in self.__functions(): # f1 through fn
            weight = self.weights[function.__name__] # get weight val
            sum += weight * function(world, action) # w_i * f_i, part of summation
        # add the curiosity score
        '''
        x, y = self.__s(world)
        state_tuple = (action[0], action[1], x, y)
        times_visited = 0
        if state_tuple in self.curiosity_scores:
            times_visited = self.curiosity_scores[state_tuple]
        sum += 1/(times_visited+1)
        '''
        return sum
        
    def __delta(self, world, action):
        ''' @dillon
        Delta assignment, approximate q-learning
        '''
        r = self.__r(self.events)
        max_a = self.max_q
        return (r + self.gamma * max_a) - self.q
        
    def __w_i(self, world, action, function):
        ''' @dillon
        Weight assignmnet, approximate q-learning
        '''
        w_i = self.weights[function.__name__] # get current weight on function name key
        delta = self.__delta(world, action)
        f_i = function(world, action)
        self.weights[function.__name__] = w_i + self.alpha * delta * f_i # update weight val
        
    def __r(self, events):
        ''' @ray
        calculates the reward for a given action
        '''
        r = 0
        for event in events:
            if event.tpe == Event.CHARACTER_FOUND_EXIT:
                r += 100
            elif event.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
                r -= 100
            elif event.tpe == Event.BOMB_HIT_CHARACTER:
                r -= 100
            elif event.tpe == Event.BOMB_HIT_MONSTER:
                r += 10
            elif event.tpe == Event.BOMB_HIT_WALL:
                r += 0.5
        r -= 0.001
        return r
        
    def __max_a(self, world):
        ''' @dillon
        max a assignment, approximate q-learnings
        '''
        self.max_q = -inf
        possible_actions = self.__possible_actions(world) # list of dx, dy
        for action in possible_actions:
            clone = SensedWorld.from_world(world) # clone the current world
            dx, dy = action # unpack
            me = clone.me(self) # find me in cloned world
            if dx == 0 and dy == 0:
                me.place_bomb()
            else:
                me.move(dx, dy) # make the move in cloned world
            next_clone, ev = clone.next() # simulate the move and clone the next world
            if next_clone.me(self) is None:
                # terminal state, q = r
                q = self.__r(ev)
            else:
                q = self.__q(next_clone, (0, 0)) # derive q of new world, don't move though
            if q > self.max_q:
               self.max_q = q # record q
               self.max_a = action # record action
               self.events = ev # record actions
        return self.max_a # return action corresponding to best q
        
    def __s(self, world):
        ''' @dillon
        Get character position, i.e. current state
        '''
        return (world.me(self).x, world.me(self).y)
        
    def __within_bounds(self, world, x, y):
        ''' @joe or @ray idk
        Is a location within the bounds of the board?
        '''
        return x < world.width() and y < world.height() and x >= 0 and y >= 0
        
    def __possible_actions(self, world):
        ''' @someone
        Use self to determine position on board, return
        a list of coordinates representing legal next moves.
        Note: return tuples of move locations
        '''
        pairs = [] # keep legal pairs
        character_x, character_y = self.__s(world)
        for d_x in range(-1, 2):
            for d_y in range(-1, 2):
                x = character_x + d_x
                y = character_y + d_y
                """
                if d_x == 0 and d_y == 0:
                    continue"""
                if (self.__within_bounds(world, x, y) 
                        and not world.wall_at(x,y)):
                    pairs.append((d_x, d_y))
        return pairs
    
    def __list_neighbors(self, world, pos):
        ''' @ray
        Lists neighbors given a position
        '''
        pairs = [] # keep legal pairs
        for d_x in range(-1, 2):
            for d_y in range(-1, 2):
                x = pos[0] + d_x
                y = pos[1] + d_y
                if d_x == 0 and d_y == 0:
                    continue
                if (self.__within_bounds(world, x, y) 
                        and not world.wall_at(x,y)):
                    pairs.append((x, y))
        return pairs
        
    def __surrounding_pairs(self, world):
        ''' @Dillon
        List pairs surrounding the character, including those w/ walls
        '''
        pairs = [] # keep list (dx, dy)
        x, y = self.__s(world) # derive current position
        for dx in range(-1, 2): # -1 to 1
            for dy in range(-1, 2): # likewise
                if self.__within_bounds(world, x + dx, y + dy): # check boundries
                    pairs.append((dx, dy)) # append to list
        return pairs # return list of pairs (dx, dy)
        
