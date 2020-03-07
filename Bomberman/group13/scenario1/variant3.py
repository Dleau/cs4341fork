# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
import time
from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../groupNN')
from specialopscharacter import SpecialOpsCharacter

# Create the game
random.seed(time.time()) # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
g.add_monster(SelfPreservingMonster("selfpreserving", # name
                                    "S",              # avatar
                                    3, 9,             # position
                                    1                 # detection range
))

# TODO Add your character
# weights = {'__goal_dist_score': 53.012209846051945, '__distance_to_monster': 14.332240246509578, '__goal_to_monster_ratio': -16.678503789000597}
weights = {'__goal_dist_score': 101.4914450610426, '__distance_to_monster': 41.88293032952136, '__goal_to_monster_ratio': -95.55063381131076, '__goal_distance_as_crow': -43.95348572831751, '__bomb_threats': 84.99263820458155}
g.add_character(SpecialOpsCharacter("me", "C", 0, 0, weights=weights))

# Run!
g.go(1)
