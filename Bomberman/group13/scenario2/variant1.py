# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game
from specialopscharacter import SpecialOpsCharacter


# TODO This is your code!
sys.path.insert(1, '../groupNN')
from testcharacter import TestCharacter


# Create the game
g = Game.fromfile('map.txt')

# TODO Add your character
w={'__goal_dist_score': 7.929575160465548, '__distance_to_monster': -8.142314868959463, '__goal_to_monster_ratio': -4.489245362797673, '__goal_distance_as_crow': 7.580431056185682, '__bomb_threats': 13.116525286722649}
#weights = {'__goal_dist_score': 0, '__distance_to_monster': 0, '__goal_to_monster_ratio': 0, '__euiclidean_distance': 0, '__bomb_threats': -100, '__could_die': -100000, '__tunnel': 1}
g.add_character(SpecialOpsCharacter("specops", "C", 0, 0, weights=w))

# Run!
g.go(1)
