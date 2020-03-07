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
w={'__goal_dist_score': 3.739147693967935, '__distance_to_monster': -12.598523194413946, '__goal_to_monster_ratio': -8.404915725169761, '__goal_distance_as_crow': 0.233200676159416, '__bomb_threats': 25.314886437899077, '__goal_dist_obstructed_score':38}
#weights = {'__goal_dist_score': 0, '__distance_to_monster': 0, '__goal_to_monster_ratio': 0, '__euiclidean_distance': 0, '__bomb_threats': -100, '__could_die': -100000, '__tunnel': 1}
g.add_character(SpecialOpsCharacter("specops", "C", 0, 0, weights=w))

# Run!
g.go(1)
