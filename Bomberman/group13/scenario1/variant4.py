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
g.add_monster(SelfPreservingMonster("aggressive", # name
                                    "A",          # avatar
                                    3, 13,        # position
                                    2             # detection range
))

# TODO Add your character
g.add_character(SpecialOpsCharacter("me", # name
                              "C",  # avatar
                              0, 0  # position
,weights =  {'__goal_dist_score': 19.63618900838964, '__distance_to_monster': 10.294196640723415, '__goal_to_monster_ratio': -14.866932303600555, '__goal_distance_as_crow': -6.017510630677442, '__bomb_threats': -1.8075836853346297}
))

# Run!
g.go(1)
