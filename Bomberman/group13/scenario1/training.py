# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

import time

# Import necessary stuff
import random
#from game_nodisp import Game
from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster

sys.path.insert(1, '../group13')
from testcharacter import TestCharacter

eps = 0
nn_filename = "model.pickle"

games = 0
won = 0
#for _ in range(t_games):
while True:
    # Create the game
    random.seed(time.time())
    g = Game.fromfile('map_blocked.txt')
    g.world.time = 1200

    g.add_monster(SelfPreservingMonster("smart", 
                                "S",      
                                3, 11,
                                1      
    ))


    g.add_monster(SelfPreservingMonster("smart", 
                                "S",      
                                3, 7,
                                1      
    ))

    our_char = TestCharacter("me","C", 0, 0, eps=eps, nn_file=nn_filename)
    g.add_character(our_char)

    # Run!
    g.go(1)

    final_score = g.world.scores["me"]
    r = None
    if our_char.pair == g.world.exitcell:
        won += 1
        r = 1000
        print("WON")
    else:
        print("LOST")
        r = -1000
    games += 1

    # last q calculation
    our_char.calc_q(our_char.pair,our_char.weights,g.world,r=r)

    print("final weights", our_char.weights, "score", final_score)
    print("WON:", won, "GAMES:", games, "%WON", (won/games)*100)
    # save neural network
    if nn_filename is None:
        nn_filename = "model.pickle"
    our_char.save_nn(nn_filename)