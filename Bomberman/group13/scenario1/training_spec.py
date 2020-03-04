# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

import time

# Import necessary stuff
import random
from game_nodisp import Game
#from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster
from monsters.stupid_monster import StupidMonster

sys.path.insert(1, '../group13')
from specialopscharacter import SpecialOpsCharacter

from sensed_world import SensedWorld

training = True
interactive = False
eps = 0.8
games = 0
sx = 0; sy = 0

#weights = {'__goal_dist_score': 0.8084695703881198, '__bomb_threats': 1.0, '__distance_to_monster': 0.8494102513595749, '__goal_blocked_score': 0.8259362740838581}

weights = None

while eps > 0.1 or not training:
    # Create the game
    random.seed(time.time())
    g = Game.fromfile('map_blocked.txt')
    #g = Game.fromfile('map.txt')
    g.world.time = 1200

    #sx = random.randrange(0,8)
    #sy = random.randrange(0,19)
    
    """
    g.add_monster(SelfPreservingMonster("1", 
                                "S",      
                                3, 14,
                                1      
    ))"""

    
    g.add_monster(StupidMonster("2", 
                                "S",      
                                3, 13
                                
    ))
            
    
    our_char = SpecialOpsCharacter("me","C", sx, sy, eps=0 if not training else eps, weights=weights)
    g.add_character(our_char)

    # Run!
    g.go(0 if interactive else 1)

    games += 1
    
    # decrease epsilon
    if eps > 0:
        eps *= 0.99
    elif eps < 0:
        eps = 0

    print("EPS:", eps)
    final_score = g.world.scores["me"]
    print("score", final_score, "games", games)
    print(our_char.weights)