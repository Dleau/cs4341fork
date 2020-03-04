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
,weights={'__goal_dist_score': 19.09047063849142, '__bomb_threats': 5.480078816026969, '__distance_to_monster': 8.698416583053438, '__goal_blocked_score': -14.584547361089848}))

# Run!
g.go(1)
