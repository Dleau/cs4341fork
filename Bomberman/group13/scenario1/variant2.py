# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
import time
from game import Game
from monsters.stupid_monster import StupidMonster

# TODO This is your code!
sys.path.insert(1, '../group13')
from specialopscharacter import SpecialOpsCharacter

# Create the game
random.seed(time.time()) # TODO Change this if you want different random choices
 # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
g.add_monster(StupidMonster("stupid", # name
                            "S",      # avatar
                            3, 9      # position
))

# TODO Add your character
# weights = {'__goal_dist_score': 53.012209846051945, '__distance_to_monster': 14.332240246509578, '__goal_to_monster_ratio': -16.678503789000597}
#weights = {'__goal_dist_score': 19.63618900838964, '__distance_to_monster': 10.294196640723415, '__goal_to_monster_ratio': -14.866932303600555, '__goal_distance_as_crow': -6.017510630677442, '__bomb_threats': -1.8075836853346297}
#weights =   {'__goal_dist_score': 7.99835006713818, '__distance_to_monster': 1.3746297279276296, '__goal_to_monster_ratio': -8.961974001273859, '__goal_distance_as_crow': -6.69759158412074, '__bomb_threats': -10.809530207008228}
weights = {'__goal_dist_score': 101.4914450610426, '__distance_to_monster': 41.88293032952136, '__goal_to_monster_ratio': -95.55063381131076, '__goal_distance_as_crow': -43.95348572831751, '__bomb_threats': 80.99263820458155}

g.add_character(SpecialOpsCharacter("me", "C", 0, 0, weights=weights))

# Run!
g.go(1)
