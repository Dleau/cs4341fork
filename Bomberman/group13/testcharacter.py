# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back

class TestCharacter(CharacterEntity):

    def do(self, wrld):
        x = self.__list_next_moves(wrld)
        print(x)
        
    def __list_next_moves(self, wrld):
        '''
        Use self to determine position on board, return
        a list of coordinates representing legal next moves.
        Note: return tuples
        '''
        pairs = [] # keep legal pairs
        character_x = wrld.me(self).x
        character_y = wrld.me(self).y
        for d_x in range(-1, 2):
            for d_y in range(-1, 2):
                x = character_x + d_x
                y = character_y + d_y
                if self.__is_move_legal(wrld, x, y):
                    pairs.append((x, y))
        return pairs

    def __is_move_legal(self, wrld, x, y):
        return (not wrld.wall_at(x,y)) and x < wrld.width() and y < wrld.height() and x >= 0 and y >= 0
    
    def __get_value(self, pair):
        '''
        Use coordinate pair on board as given, get a value
        for the position using a hueristic or whatever.
        '''
        pass
        
    def __q_function(self, pair):
        '''
        Q function as defined by wikipedia (probably), use self
        to determine current position, take tuple pair for move.
        Note: if pair == current position, a bomb is to be dropped
        '''
        pass