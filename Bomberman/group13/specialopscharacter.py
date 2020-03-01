# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from sensed_world.SensedWorld import from_world

class SpecialOpsCharacter(CharacterEntity):

    # NOTE use approx_qlearning.png!!!, literally following that to the letter
    # action, a.k.a "a" in the formula, is a destination (x, y) tuple

    def __init__(self, name, avatar, x, y):
        # @dillon
        super().__init__(name, avatar, x, y)
        self.alpha = 0 # alpha value for use in q-learning formula
        self.gamma = 0 # gamma value, likewise
        self.weights = {f.__name__: 0 for f in self.__functions()} # function name -> weight

    def do(self, wrld):
        # Commands
        ''' @dillon
        Character won't go anywhere, function isn't done
        '''
        dx, dy = 0, 1
        bomb = False
        print(self.weights)
        self.move(dx, dy)
        if bomb:
            self.place_bomb()
      
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
        clone = from_world(world) # clone world for manipulation
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
        pass # TODO implement
        
    def __s(self, world):
        ''' @dillon
        Get character position, i.e. current state
        '''
        return (world.me(self).x, world.me(self).y)
        
    
    
