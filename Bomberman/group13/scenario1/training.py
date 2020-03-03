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

sys.path.insert(1, '../group13')
from testcharacter import TestCharacter

from sensed_world import SensedWorld

eps = 0
nn_filename = "model.pickle"
games = 0
won = 0
try:
    #while eps > 0:
    while True:
        # epochs
        sx = 0; sy = 0
        for _ in range(1):
            # Create the game
            random.seed(time.time())
            g = Game.fromfile('map_blocked.txt')
            g.world.time = 1200

            #sx = random.randrange(0,8)
            #sy = random.randrange(0,19)
            
            """
            g.add_monster(SelfPreservingMonster("smart", 
                                        "S",      
                                        3, 14,
                                        1      
            ))"""

            """
            g.add_monster(SelfPreservingMonster("smart", 
                                        "S",      
                                        3, 13,
                                        1      
            ))"""
                    
            
            our_char = TestCharacter("me","C", sx, sy, eps=eps, nn_file=nn_filename, training=True)
            g.add_character(our_char)

            # Run!
            g.go(1)

        games += 1
        
        # decrease epsilon
        if eps > 0:
            eps *= 0.95
        elif eps < 0:
            eps = 0
        print("EPS:", eps)
        
        final_score = g.world.scores["me"]
        print("score", final_score, "games", games)
        # save neural network
        if nn_filename is None:
            nn_filename = "model.pickle"
        our_char.save_nn(nn_filename)
except KeyboardInterrupt:
    print("Saving neural network...")
    our_char.save_nn(nn_filename)
    print("Saved!")