# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from sensed_world import SensedWorld
from random import uniform, randrange
from math import inf, sqrt

class SpecialOpsCharacter(CharacterEntity):

    # NOTE use approx_qlearning.png!!!, literally following that to the letter
    # action, a.k.a "a" in the formula, is (dx, dy) tuple
        
    # order of determination: max a, delta, weights, q

    def __init__(self, name, avatar, x, y):
        # @dillon
        super().__init__(name, avatar, x, y)
        self.alpha = 0.25 # alpha value for use in q-learning formula
        self.gamma = 0.01 # gamma value, likewise
        self.epsilon = 0 # epsilon value, likewise
        self.q = 0
        self.weights = {f.__name__: 1 for f in self.__functions()} # function name -> weight
        self.max_a = 0

    def do(self, world):
        # Commands
        ''' @dillon
        Does the next move
        '''
        # gets the next best action using max a
        dx, dy = self.__next_action(world)
        # updates the function weights using max a and delta
        for function in self.__functions():
            self.__w_i(world, (dx, dy), function)
        # determines a q value for this state
        self.q = self.__q(world, (dx, dy)) 
        if (dx, dy) == (0, 0):
            self.place_bomb()
        else:
            self.move(dx, dy)
        print(self.weights)
        print('q', self.q)
            
    def __next_action(self, world):
        ''' @dillon
        Considers possible (dx, dy) actions from current position,
        either explores or exploits. Exploitation uses max a to find
        optimal (dx, dy) action.
        '''
        possible_actions = self.__list_next_moves(world)
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
        return [self.__distance_to_goal, self.__bomb_threats, self.__distance_to_monster]
        
    def __distance_to_goal(self, world, action):
        ''' @dillon
        Euclidian distance to the goal
        '''
        goal_loc = world.exitcell
        return sqrt(pow((goal_loc[0] - action[0]),2) + pow((goal_loc[1] - action[1]),2))
        
    def __bomb_threats(self, world, action):
        ''' @dillon
        Number of threatening bombs
        '''
        bomb_threats = 0
        for dx in range(0, world.width()):
            if world.bomb_at(dx, action[1]):
                bomb_threats += 1
        for dy in range(0, world.height()):
            if world.bomb_at(action[0], dy):
                bomb_threats += 1
        return bomb_threats
        
    def __distance_to_monster(self, world, action):
        ''' @dillon
        Euclidian distance to the closest monster
        '''
        distances = [] # distances to monsters
        monsters = [l[0] for l in list(world.monsters.values())] # list of monsters
        for monster in monsters:
            x, y = self.__s(world)
            d_x, d_y = x - monster.x, y - monster.y
            distance = sqrt(pow(d_x, 2) + pow(d_y, 2))
            distances.append(distance)
        # return 0 if len(distances) == 0 else 1 / (min(distances) + 1)
        return 0 if not len(distances) else min(distances)
            
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
        return sum
        
    def __delta(self, world, action):
        ''' @dillon
        Delta assignment, approximate q-learning
        '''
        r = self.__r(world, action)
        max_a = self.max_a
        q = self.__q(world, action)
        return (r + self.gamma * max_a) - q
        
    def __w_i(self, world, action, function):
        ''' @dillon
        Weight assignmnet, approximate q-learning
        '''
        w_i = self.weights[function.__name__] # get current weight on function name key
        delta = self.__delta(world, action)
        f_i = function(world, action)
        self.weights[function.__name__] = w_i + self.alpha * delta * f_i # update weight val
        
    def __r(self, world, action):
        ''' @dillon
        Reward assignment, approximate q-learning
        This would likely need to be adjusted
        '''
        return -self.__distance_to_goal(world, action)
        
    def __max_a(self, world):
        ''' @dillon
        max a assignment, approximate q-learnings
        '''
        possible_actions = self.__list_next_moves(world) # list of dx, dy
        clone = SensedWorld.from_world(world)
        max_q = -inf
        max_action = None
        for action in possible_actions:
            q = self.__q(clone, action)
            if q > max_q:
                max_q = q
                max_action = action
        self.max_a = max_q
        return max_action
        
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
        
    def __list_next_moves(self, world):
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
                if self.__within_bounds(world, x, y): # adjust w/ walls probably
                    pairs.append((d_x, d_y))
        return pairs
