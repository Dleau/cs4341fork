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
        legal_coordinate_list = [];
        character_x =  wrld.me(self).x
        character_y =  wrld.me(self).y
        for i in range(-1, 1):
        	for j in range(-1, 1):
        		x = character_x + i
        		y = character_y + j
        		if(!wrld.wall_at(x,y) &&
        		 x < wrld.width() &&
        		 y < wrld.height() &&
        		  x >= 0 && y >= 0)
        			legal_coordinate_list.append([x,y])

       	return legal_coordinate_list;

        
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