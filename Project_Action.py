# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 16:50:39 2022

@author: 'Kevin Goodman-Rendall'
"""
### Game input/output interactive platform

''' This is the file to run, I tried to implement it but it doesnt work so well
occaisionally there's bugs but most can be solved by just rerunning because there
are some very improbable events that I haven't taken into consideration when dealing
the cards but because of the number of iterations/generations they do occur from time 
to time. '''

# Import datasets

from Project_Poker import *
from Project_Player import Situation, Player, Opponent

## Define Class Objects and functions
# Situation

situation = Situation(deck, board, current_pot, remaining_deck, current_stack, opp_current_stack, current_street)
situation.deal = deal
situation.deal_flop = deal_flop
situation.deal_turn = deal_turn
situation.deal_river = deal_river
situation.winner = winner
situation.best_possible_hand = best_possible_hand
situation.stack_adjust = stack_adjust

# Define initial situation - pay blinds and deal two hole cards

situation.HC, situation.remaining_deck, situation.current_stack, situation.opp_current_stack, situation.current_pot, situation.current_street = situation.deal(situation, situation.deck, situation.current_pot, situation.current_stack, situation.opp_current_stack)

# Player

player = Player(my_position, situation.HC, current_stack)
player.get_hole_card_strength = get_hole_card_strength
player.get_hand_id = get_hand_id
player.get_hand_strength = get_hand_strength
player.get_hand_sensitivity = get_hand_sensitivity
player.desired_pot_size = desired_pot_size
player.best_action = best_action

# Opponent

opponent = Opponent(situation.opp_current_stack, player.my_position, positions)
situation.remaining_deck, opponent.opp_HC = opponent.deal_opp_HC(situation.remaining_deck)

# Make Preflop Calculations

player.HC_strength = player.get_hole_card_strength(player, player.HC)
player.hand_id = player.get_hand_id(player, player.HC, situation.board, situation.current_street)
player.hand_strength = player.get_hand_strength(player, player.HC, situation.board, situation.remaining_deck, player.HC_strength, player.hand_id, situation.current_street)
player.hand_sensitivity = player.get_hand_sensitivity(player, player.HC, situation.board, player.hand_strength, situation.remaining_deck, situation.current_street)
player.desired_pot = player.desired_pot_size(player, situation.current_pot, player.hand_strength, player.hand_sensitivity, player.hand_id, situation.current_street, situation.current_stack, opponent.opp_current_stack)

## Input/Output Preflop

print('Your current stack is ', opponent.opp_current_stack)
print('Your current position is ', opponent.opp_position)
print('The current pot is ', situation.current_pot)
print('Your hole cards are ', opponent.opp_HC)
print('The community cards are ', situation.board)
situation.best_possible_hand(situation, situation.board, situation.deck, situation.current_street)

### UNCOMMENT BLOCK BELOW TO SEE MY ATTEMPT AT IMPLEMENTATION WHICH SUCKED

# if opponent.opp_position == 'OOP':
#     opponent.opp_action, opponent.opp_bet = input('Please enter your action and amount: (ex. Bet 23 or Check 0)  ').split()
#     opponent.opp_bet = int(opponent.opp_bet)
# elif opponent.opp_position == 'IP':
#     player.action, player.amount = player.best_action(player, player.desired_pot, situation.current_pot, player.my_position)
#     print('Player chooses to ', player.action, ' for ', player.amount)
    
#     opponent.opp_action, opponent.opp_bet = input('Please enter your action and amount: (ex. Bet 23 or Check 0)  ').split()
#     opponent.opp_bet = int(opponent.opp_bet)

### END OF AREA TO UNCOMMENT
    
## Input/Output Flop
situation.board, situation.remaining_deck, situation.current_street = situation.deal_flop(situation.board, situation.remaining_deck, situation.current_street)
board = situation.board
current_street = situation.current_street

print('Your current stack is ', opponent.opp_current_stack)
print('Your current position is ', opponent.opp_position)
print('The current pot is ', situation.current_pot)
print('Your hole cards are ', opponent.opp_HC)
print('The community cards are ', situation.board)
situation.best_possible_hand(situation, situation.board, situation.deck, situation.current_street)

## Input/Output Turn
situation.board, situation.remaining_deck, situation.current_street = situation.deal_turn(situation, situation.board, situation.remaining_deck, situation.current_street)
board = situation.board

print('Your current stack is ', opponent.opp_current_stack)
print('Your current position is ', opponent.opp_position)
print('The current pot is ', situation.current_pot)
print('Your hole cards are ', opponent.opp_HC)
print('The community cards are ', situation.board)
situation.best_possible_hand(situation, situation.board, situation.deck, situation.current_street)

## Input/Output River
situation.board, situation.remaining_deck, situation.current_street = situation.deal_river(situation, situation.board, situation.remaining_deck, situation.current_street)
board = situation.board

print('Your current stack is ', opponent.opp_current_stack)
print('Your current position is ', opponent.opp_position)
print('The current pot is ', situation.current_pot)
print('Your hole cards are ', opponent.opp_HC)
print('The community cards are ', situation.board)
situation.best_possible_hand(situation, situation.board, situation.deck, situation.current_street)

    
    