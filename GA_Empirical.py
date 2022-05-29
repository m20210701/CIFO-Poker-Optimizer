# -*- coding: utf-8 -*-
"""
Created on Sat May 28 23:40:15 2022

@author: 'Kevin Goodman-Rendall'
"""

''' This file uses the GA to deteremine empirically which hole cards will
perform the best over several iterations by checking individual's fitness
its throwing errors sometimes, not sure why, but just rerun it, before running
this you must change the GA function to return mortal nuts (commented)'''

# Import libraries
from Project_Poker import *
from Project_Player import Situation, Player, Opponent
import matplotlib.pyplot as plt
import random

# Define methods for classes
situation = Situation(deck, board, current_pot, remaining_deck, current_stack, opp_current_stack, current_street)
situation.deal = deal
situation.deal_flop = deal_flop
situation.deal_turn = deal_turn
situation.deal_river = deal_river
situation.best_possible_hand = best_possible_hand

hand_stat_dict = dict() # store hands
num_gen = 10 # number of trials

for i in range(0, num_gen):
    
    situation = Situation(deck, board, current_pot, remaining_deck, current_stack, opp_current_stack, current_street)

    ## Deal

    situation.HC, situation.remaining_deck, situation.current_stack, situation.opp_current_stack, situation.current_pot, situation.current_street = deal(situation, situation.deck, situation.current_pot, situation.current_stack, situation.opp_current_stack)

    ## Flop
    situation.board, situation.remaining_deck, situation.current_street = deal_flop(situation, situation.remaining_deck, situation.current_street)

    ## Turn
    situation.board, situation.remaining_deck, situation.current_street = deal_turn(situation, situation.board, situation.remaining_deck, situation.current_street)

    ## River
    situation.board, situation.remaining_deck, situation.current_street = deal_river(situation, situation.board, situation.remaining_deck, situation.current_street)

    # GA - CHANGED BEST POSSIBLE HAND FUNCTION TO RETURN MORTAL NUTS NOT JUST PRINT ####

    mortal_nuts = best_possible_hand(situation, situation.board, situation.deck, 'River')
    
    for hand in mortal_nuts:
        
        # first map hands more generically so QsJc and JcQs are both QJo
        # this reduces the equivalent combinations to a more manageable size
        
        hand = sorted(hand)
        
        if hand[0] == hand[1]: # paired cards
            hand = hand[0] + hand[1]
        elif hand[0] != hand[1] and hand[2] == hand[3]: # suited 
            hand = hand[0] + hand[1] + 's'
        elif hand[0] != hand[1] and hand[2] != hand[3]: # offsuit
            hand = hand[0] + hand[1] + 'o'
        else:
            raise Exception('cant read the hand dude')
        
        if hand not in hand_stat_dict.keys():
            
            hand_stat_dict[hand] = 0
            hand_stat_dict[hand] += 1 # count the number of times that hand was the best
        
        else:
            
            hand_stat_dict[hand] += 1

# Plot bar graph 
plt.figure(dpi = 400, figsize = (20,10))
plt.xlabel('Hole Cards', fontsize = 30)
plt.ylabel('Counts', fontsize = 30)
plt.xticks(fontsize = 25, rotation = 90)
plt.yticks(fontsize = 25)
plt.title('Number of Generations: ' + str(num_gen), fontsize = 50)
plt.bar(sorted(hand_stat_dict, key = hand_stat_dict.get, reverse = True), sorted(hand_stat_dict.values(), reverse = True), color = [random.random(), random.random(), random.random()])

# Optionally save figure
plt.savefig('Generation' + str(num_gen))
    

