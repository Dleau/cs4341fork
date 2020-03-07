# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game

# TODO This is your code!
sys.path.insert(1, '../group13')

# Uncomment this if you want the empty test character
from testcharacter import TestCharacter
from specialopscharacter import SpecialOpsCharacter

# Uncomment this if you want the interactive character
from interactivecharacter import InteractiveCharacter

# Create the game
g = Game.fromfile('map.txt')

# TODO Add your character

# Uncomment this if you want the test character
# g.add_character(InteractiveCharacter("me", # name
#                               "C",  # avatar
#                               0, 0  # position
# ))

# Uncomment this if you want the interactive character
# g.add_character(TestCharacter("me", "C", 0, 0,
#     nn_file="model.pickle",eps=0,explore=False))

from specialopscharacter import SpecialOpsCharacter
# weights = {'__goal_dist_score': 53.012209846051945, '__distance_to_monster': 14.332240246509578, '__goal_to_monster_ratio': -16.678503789000597}
weights = {'__goal_dist_score': 10.0157139736459162, '__distance_to_monster': 19.356608344043547, '__goal_to_monster_ratio': -10.899725942090054, '__goal_distance_as_crow': 1.7205125700525967, '__bomb_threats': 95.26731497713193, '__goal_dist_obstructed_score': 1.0157139736459162}
g.add_character(SpecialOpsCharacter("specops", "C", 0, 0 , weights=weights))

# Run!

# Use this if you want to press ENTER to continue at each step
#g.go(0)

# Use this if you want to proceed automatically
g.go(1)
