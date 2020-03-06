# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../groupNN')
from specialopscharacter import SpecialOpsCharacter

# Create the game
random.seed(123) # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
g.add_monster(SelfPreservingMonster("selfpreserving", # name
                                    "S",              # avatar
                                    3, 9,             # position
                                    1                 # detection range
))

# TODO Add your character
# weights = {'__goal_dist_score': 53.012209846051945, '__distance_to_monster': 14.332240246509578, '__goal_to_monster_ratio': -16.678503789000597}
weights = {'__goal_dist_score': 19.63618900838964, '__distance_to_monster': 10.294196640723415, '__goal_to_monster_ratio': -14.866932303600555, '__goal_distance_as_crow': -6.017510630677442, '__bomb_threats': -1.8075836853346297}
g.add_character(SpecialOpsCharacter("me", "C", 0, 0, weights=weights))

# Run!
g.go(1)
