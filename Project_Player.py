# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 16:48:03 2022

@author: 'Kevin Goodman-Rendall'
"""
### The poker player, opponent and situation class object file

''' this script defines the classes for the player and their situation '''

# Import libraries
import random
from Project_Poker import *

# Define classes

class Situation: # this can come later, the action to the player
    def __init__(self, deck, board, current_pot, remaining_deck, current_stack, opp_current_stack, current_street):
        self.deck = deck
        self.board = board
        self.current_pot = current_pot
        self.remaining_deck = remaining_deck
        self.HC = []
        self.current_stack = current_stack
        self.current_street = current_street
        self.opp_current_stack = opp_current_stack
        
    def deal(self, deck, current_pot, current_stack, opp_current_stack):
        return self.HC, self.remaining_deck, self.current_stack, self.opp_current_stack, self.current_pot, self.current_street
    
    def deal_flop(self, board, remaining_deck, current_street):
        return self.board, self.remaining_deck, self.current_street
    
    def deal_turn(self, board, remaining_deck, current_street):
        return self.board, self.remaining_deck, self.current_street
    
    def deal_river(self, board, remaining_deck, current_street):
        return self.board, self.remaining_deck, self.current_street

    def winner(self, HC, board, current_street, opp_HC = None):
        return self.outcome
    
    def best_possible_hand(self, board, deck, current_street):
        return self.best_possible_hand
    
    def stack_adjust(self, current_stack, opp_current_stack, current_pot, current_street, action, amount, outcome, opp_action = None):
        return self.current_stack, self.opp_current_stack, self.current_pot
    
    
    
# Define your player's parameters

class Player:
    def __init__(self, my_position, HC, current_stack):
        self.my_position = my_position
        self.HC = HC
        self.current_stack = current_stack
              
    def get_hole_card_strength(self, HC):
        return self.HC_strength
    
    def get_hand_id(self, HC, board, current_street):
        return self.hand_id
    
    def get_hand_strength(self, HC, board, remaining_deck, HC_strength, hand_id, current_street):
        return self.hand_strength
    
    def get_hand_sensitivity(self, HC, board, hand_strength, remaining_deck, current_street):
        return self.hand_sensitivity
        
    def desired_pot_size(self, current_pot, hand_strength, hand_sensitivity, hand_id, current_street, current_stack, opp_current_stack):
        return self.desired_pot
        
    def best_action(self, desired_pot, current_pot, my_position, opp_action = None, opp_bet = 0):
        return self.action, self.amount
 
# Define your opponents's parameters

class Opponent:
    def __init__(self, opp_current_stack, my_position, positions):
        self.opp_current_stack = opp_current_stack
        self.opp_position = list(filter(lambda x: x != my_position, positions))[0]
        self.opp_action = None
        self.opp_bet = 0
    
    def deal_opp_HC(self, remaining_deck):
        self.opp_HC = random.sample(remaining_deck, 2)
        remaining_deck = list(set(remaining_deck)-set(self.opp_HC))
        
        return remaining_deck, self.opp_HC
    
  