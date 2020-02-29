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

# TODO This is your code!
sys.path.insert(1, '../group13')
from testcharacter import TestCharacter

weights = None
eps = 0.25

games = 0
won = 0
#for _ in range(t_games):
while True:
    # Create the game
    random.seed(time.time())
    g = Game.fromfile('map_blocked.txt')
    g.add_monster(SelfPreservingMonster("smart", 
                                "S",      
                                3, 13,
                                1      
    ))

    
    g.add_monster(SelfPreservingMonster("smart", 
                                "S",      
                                3, 2,
                                1      
    ))

    our_char = TestCharacter("me","C", 0, 0, weights, eps)
    g.add_character(our_char)

    # Run!
    g.go(1)

    final_score = g.world.scores["me"]
    r = None
    if final_score > 0:
        won += 1
        r = 1000
    games += 1

    # last q calculation
    our_char.calc_q(our_char.pair,our_char.weights,g.world,r=r)

    # save weights
    weights = our_char.weights
    print("final weights", weights, "score", final_score)
    print("WON:", won, "GAMES:", games, "%WON", (won/games)*100)