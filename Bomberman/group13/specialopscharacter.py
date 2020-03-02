# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from sensed_world import SensedWorld
from random import uniform, randrange
from math import inf

class SpecialOpsCharacter(CharacterEntity):

    # NOTE use approx_qlearning.png!!!, literally following that to the letter
    # action, a.k.a "a" in the formula, is a destination (x, y) tuple

    def __init__(self, name, avatar, x, y):
        # @dillon
        super().__init__(name, avatar, x, y)
        self.alpha = 0 # alpha value for use in q-learning formula
        self.gamma = 0 # gamma value, likewise
        self.epsilon = 0.01 # epsilon value, likewise
        self.q = 0
        self.weights = {f.__name__: 0 for f in self.__functions()} # function name -> weight

    def do(self, world):
        # Commands
        ''' @dillon
        Character won't go anywhere, function isn't done
        '''
        dx, dy = self.__next_action(world)
        if (dx, dy) == (0, 0):
            self.place_bomb()
        else:
            self.move(dx, dy)
            
    def __next_action(self, world):
        possible_actions = self.__list_next_moves(world)
        z = uniform(0, 1)
        a = None # next action
        if z < self.epsilon: # exploration
            a = possible_actions[randrange(0, len(next_moves))] # pick random action
        else: # exploitation
            max_q = -inf
            for possible_action in possible_actions:
                q = self.__q(world, possible_action)
                if q > max_q:
                    max_q = q
                    a = possible_action
        x, y = self.__s(world)
        ax, ay = a
        return (ax - x, ay - y)
      
    def __functions(self):
        ''' @dillon
        List f1 through fn
        Every function must take ONLY world and action as args
        '''
        # these are just examples
        return [self.__distance_to_goal, self.__distance_to_bomb, self.__distance_to_monster]
        
    def __distance_to_goal(self, world, action):
        return 0.5 # TODO possibly implement
        
    def __distance_to_bomb(self, world, action):
        return 0.5 # TODO possibly implement
        
    def __distance_to_monster(self, world, action):
        return 0.5 # TODO possibly implement
            
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
        max_a = self.__max_a(world, action)
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
        ''' @dillon, basically @ray's original code
        Reward assignment, approximate q-learning
        '''
        s_x, s_y = self.__s(world) # current position or state, (x, y)
        a_x, a_y = action # split action into x and y
        dx, dy = a_x - s_x, a_y - s_y # get directional deltas
        clone = SensedWorld.from_world(world) # clone world for manipulation
        me = clone.me(self) # get cloned character
        if me is None: return -1000 # death occured, reward is a terrible -1000
        me.move(dx, dy) # character is alive, make move
        clone, _ = clone.next() # get next iteration of cloned world, re-assign
        d_score = clone.scores['me'] - world.scores['me'] # score delta between worlds
        return d_score +- self.__distance_to_goal(world, action) # incentivize distance to goal
        
    def __max_a(self, world, action):
        '''
        max a assignment, approximate q-learnings
        '''
        x, y = self.__s(world) # current position or state, (x, y)
        a_x, a_y = action # split action into x and y
        dx, dy = a_x - x, a_y - y # get directional deltas
        clone = SensedWorld.from_world(world) # clone world for manipulation
        max_a = 0 # TODO
        while self.__within_bounds(world, x, y): # location is within bounds of board
            me = clone.me(self) # find character on the cloned board
            if me is None: # the character has died
                return max_a
            me.move(dx, dy) # move the character
            clone, _ = clone.next() # simulate the next iteration of the world
            q = self.__q(self, clone, action) # calculate q
            if q > max_a: # re-assign if necessary
                max_a = q
        return max_a
        
    def __s(self, world):
        ''' @dillon
        Get character position, i.e. current state
        '''
        return (world.me(self).x, world.me(self).y)
        
    def __within_bounds(self, world, x, y):
        '''
        Is a location within the bounds of the board?
        '''
        return x < world.width() and y < world.height() and x >= 0 and y >= 0
        
    def __list_next_moves(self, world):
        '''
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
                    pairs.append((x, y))
        return pairs
