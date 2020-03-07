# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')
import time


# Import necessary stuff
import random
from game import Game
from monsters.stupid_monster import StupidMonster
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../groupNN')
from specialopscharacter import SpecialOpsCharacter

# Create the game
random.seed(time.time()) # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
g.add_monster(StupidMonster("stupid", # name
                            "S",      # avatar
                            3, 5,     # position
))
g.add_monster(SelfPreservingMonster("aggressive", # name
                                    "A",          # avatar
                                    3, 13,        # position
                                    2             # detection range
))

g.add_character(SpecialOpsCharacter("me", # name
                              "C",  # avatar
                              0, 0  # position

,weights =   {'__goal_dist_score': 100.0157139736459162, '__distance_to_monster': 90.356608344043547, '__goal_to_monster_ratio': -1.899725942090054, '__goal_distance_as_crow': 1.7205125700525967, '__bomb_threats': 95.26731497713193, '__goal_dist_obstructed_score': 1.0157139736459162}
))

# Run!
g.go(1)
