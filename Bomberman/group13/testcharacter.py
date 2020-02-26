# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back

class TestCharacter(CharacterEntity):

    def do(self, wrld):
        pass
        
    def __list_next_moves(self):
        '''
        Use self to determine position on board, return
        a list of coordinates representing legal next moves.
        Note: return tuples
        '''
        pass
        
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