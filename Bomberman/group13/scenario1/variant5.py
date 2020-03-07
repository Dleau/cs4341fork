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

w={'__goal_dist_score': 127.04623127634393, '__distance_to_monster': 38.18276993334052, '__goal_to_monster_ratio': -105.7111068106168, '__goal_distance_as_crow': 124.86501794502585, '__bomb_threats': 23.055638750419487}

# TODO Add your character
g.add_character(SpecialOpsCharacter("me", # name
                              "C",  # avatar
                              0, 0,  # position
weights=w))

# Run!
g.go(1)
