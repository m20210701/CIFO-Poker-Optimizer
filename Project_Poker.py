# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 16:56:09 2022

@author: 'Kevin Goodman-Rendall'
"""
### Project for CIFO Course Spring 2022
### a poker optimizer that makes decisions
### as bet, call, fold, raise, check
### don't forget to comment this before handing it in!
### Please read glossary of poker terms if you aren't sure
### what something means!

'''
.------..------..------..------.        
|C.--. ||I.--. ||F.--. ||O.--. |        
| :/\: || (\/) || :(): || :/\: |        
| :\/: || :\/: || ()() || :\/: |        
| '--'C|| '--'I|| '--'F|| '--'O|        
`------'`------'`------'`------'        
.------..------..------..------..------.
|P.--. ||O.--. ||K.--. ||E.--. ||R.--. |
| :/\: || :/\: || :/\: || (\/) || :(): |
| (__) || :\/: || :\/: || :\/: || ()() |
| '--'P|| '--'O|| '--'K|| '--'E|| '--'R|
`------'`------'`------'`------'`------
'''

# Import libraries
import random
import itertools
import numpy as np
from scipy import stats

# Import class objects


# Define the game's basic parameters

cards = ('2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A') # card names
suits = ('d','h','c','s') # clubs, hearts, spades, diamonds
deck = tuple(itertools.product(cards,suits)) # 52 cards possible from cards + suits
num_players = 2 # only plays heads-up for now
board = [] # community cards 
hand_ids = ('no pair', 'pair', 'two-pair', 'trips', 'straight', 'flush', 'boat', 'quads', 'straight-flush') 
current_stack = 100 # ongoing updated stack after betting
opp_current_stack = 100 # ongoing updated stack for opponent
current_pot = 0 # ongoing updated pot size after betting
blind = 1 # both players will pay the blind
remaining_deck = list(itertools.product(cards,suits)) # cards remaining in deck after cards are drawn
positions = ('OOP', 'IP') # 2 player max for now
my_position = random.choice(positions) # computers position
all_actions = ('Check', 'Bet', 'Raise', 'Fold', 'Call')
streets = ('Pre', 'Flop', 'Turn', 'River')
current_street = None

card_strength_dict = {'A':13,
                      'K':12,
                      'Q':11,
                      'J':10,
                      'T':9,
                      '9':8,
                      '8':7,
                      '7':6,
                      '6':5,
                      '5':4,
                      '4':3,
                      '3':2,
                      '2':1}

# Define basic functions for game use

def deal(self, deck, current_pot, current_stack, opp_current_stack): # deal two hole cards to the player
    # problem with this is its considering Ad-6d different than 6d-Ad, permutations should not matter ### build in HC for opponent here
    HC = random.sample(deck,2)
    # update remaining cards in deck
    remaining_deck = list(set(deck)-set(HC))
    # both players pay ante of 2$
    current_stack -= blind
    opp_current_stack -= blind
    current_pot += num_players*blind # two players blinds
    current_street = streets[0]
    return HC, remaining_deck, current_stack, opp_current_stack, current_pot, current_street

def deal_flop(self, given_remaining_deck, given_current_street):
    if given_current_street == 'Pre':
        given_board = random.sample(given_remaining_deck,3)
        #update remaining cards in deck
        given_remaining_deck = list(set(given_remaining_deck)-set(given_board))
        given_current_street = streets[1] # street is now 'Flop'
    else:
        raise ValueError('Its not pre')
        
    return given_board, given_remaining_deck, given_current_street

def deal_turn(self, given_board, given_remaining_deck, given_current_street):
    if given_current_street == 'Flop' and len(given_board) == 3:
        given_board.append(random.sample(given_remaining_deck,1)[0])
        #update remaining cards in deck
        given_remaining_deck = list(set(given_remaining_deck)-set(given_board))
        given_current_street = streets[2]
    else:
        raise ValueError('Its not flop')
        
    return given_board, given_remaining_deck, given_current_street

def deal_river(self, given_board, given_remaining_deck, given_current_street):
    if given_current_street == 'Turn' and len(given_board) == 4:
        given_board.append(random.sample(given_remaining_deck,1)[0])
        #update remaining cards in deck
        given_remaining_deck = list(set(given_remaining_deck)-set(given_board))
        given_current_street = streets[3]
    else:
        raise ValueError('Its not turn')
        
    return given_board, given_remaining_deck, given_current_street
    
def get_hole_card_strength(self, HC):
    # input your hole cards, output is their strength
    
    HC_strength = 0
    
    for card in HC:
        HC_strength += card_strength_dict[card[0]]
    
    # suited cards
    if HC[0][1] == HC[1][1]:
        HC_strength += 10
        
    # if paired += 20
    if HC[0][0] == HC[1][0]:
        HC_strength += 20
        
    # if connected
    if abs(cards.index(HC[0][0]) - cards.index(HC[1][0])) == 1:
        HC_strength += 8
    
    return HC_strength

def get_hand_id(self, HC, board, current_street):
    # input your hole cards and the board and output your hand's id, ### need to make these more separated like you did for straights
	
    if current_street == 'Pre' and HC[0][0] != HC[1][0]:
        hand_id = hand_ids[0] # no pair
    elif current_street == 'Pre' and HC[0][0] == HC[1][0]:
        hand_id = hand_ids[1] # pair
    else:
        # first define board pairs, suitedness
        board_pair_count = dict({card:0 for card in cards}) # num times each card paired
        board_suit_count = dict({'h':0,'s':0,'c':0,'d':0}) # suit counter
        board_face_count = dict({card:0 for card in cards}) # num times each card on board
    
        for commface, commsuit in board:
            board_suit_count[commsuit] += 1
            board_face_count[commface] += 1
        
        board_pair_count = {key: value - 1 for key, value in board_face_count.items() if value > 0} # pairs on board
        
        for key, value in board_face_count.items(): # add in the zero values
            if value == 0:
                board_pair_count[key] = value
                
        if HC[0][0] != HC[1][0]: # unpaired hole cards
			
            pair_count = 0
            num_times_paired = dict() # two element list for number of times HC card is paired
            num_times_suited = dict({'h':0,'s':0,'c':0,'d':0}) # two element list for number of times HC card is suited to another
            card_indexes = list()
			
            if board_face_count['A'] >= 1:
                card_indexes.append(-1) # Aces play high and low for a wheel
			
			# iterate over hole cards and board
			
            for face, suit in HC: # hole cards
                num_times_paired[face+suit] = 0
                num_times_suited[suit] += 1
                card_indexes.append(cards.index(face))
				
                for commface, commsuit in board: # community cards
                    card_indexes.append(cards.index(commface))
					
                    if face == commface:
                        pair_count += 1
                        num_times_paired[face+suit] += 1
			
            for commface, commsuit in board: num_times_suited[commsuit] += 1
			
            card_indexes = np.unique(np.sort(card_indexes)) # detecting a straight
            max_straight_card = str() # store top card of straight
            straight_counter = 1 # starts on 1 as second card makes two to a straight
            straight_flush_counter = 0 # counting cards to a straight flush
            all_cards_out_index = list()
			
            for idx, value in enumerate(card_indexes[1:]): # determine if there's a straight
                if straight_counter == 5: # you've made a straight, exit the loop
                    break
                elif value == card_indexes[idx]+1:
                    straight_counter += 1
                    max_straight_card = cards[value] # store top card's face 
                else: 
                    straight_counter = 1 # reset counter
			
            if straight_counter >= 5 and max(num_times_suited.values()) >= 5: # determine if straight is a straight flush
                all_cards_out = HC + board # all cards available
				
                for face, suit in all_cards_out: # index for all cards
                    all_cards_out_index.append(cards.index(face))
				
                all_cards_out_index = np.sort(all_cards_out_index) # sort all cards by index
                all_cards_out = [all_cards_out for _, all_cards_out in sorted(zip(all_cards_out_index, all_cards_out))]
				
                for face, suit in all_cards_out: # iterate over all cards and match with suit of flush
                    if suit == max(num_times_suited, key=num_times_suited.get): 
                        straight_flush_counter += 1
                    elif suit != max(num_times_suited, key=num_times_suited.get):
                        straight_flush_counter = 0
                    else:
                        raise ValueError('Error in straight flush determination')
			
            # assign hand id in order of decreasing strength, decreasingly probable
			
            if straight_flush_counter >= 5: # straight-flush or royal flush
                hand_id = hand_ids[8]
            elif list(board_pair_count.values()).count(3) == 1: # quads
                hand_id = hand_ids[7]
            elif pair_count == 3 and list(num_times_paired.values())==[0,3]: # quads
                hand_id = hand_ids[7]
            elif pair_count == 3 and list(num_times_paired.values())==[3,0]: # quads
                hand_id = hand_ids[7]
            elif pair_count == 4 and list(num_times_paired.values())==[3,1]: # quads
                hand_id = hand_ids[7]
            elif pair_count == 4 and list(num_times_paired.values())==[1,3]: # quads
                hand_id = hand_ids[7]
            elif pair_count >= 5: # quads
                hand_id = hand_ids[7]
            elif pair_count == 2 and list(num_times_paired.values())==[2,0] and list(board_pair_count.values()).count(1) == 2: # boat
                hand_id = hand_ids[6]
            elif pair_count == 2 and list(num_times_paired.values())==[0,2] and list(board_pair_count.values()).count(1) == 2: # boat
                hand_id = hand_ids[6]
            elif pair_count == 0 and np.max(list(board_pair_count.values())) == 2 and 1 in board_pair_count.values(): # boat
                hand_id = hand_ids[6]
            elif pair_count == 3 and list(num_times_paired.values())==[2,1]: # boat
                hand_id = hand_ids[6]
            elif pair_count == 3 and list(num_times_paired.values())==[1,2]: # boat
                hand_id = hand_ids[6]
            elif pair_count == 4 and list(num_times_paired.values())==[2,2]: # boat
                hand_id = hand_ids[6]
            elif np.max(list(num_times_suited.values())) >= 5: # flush
                hand_id = hand_ids[5]
            elif straight_counter >= 5: # straight
                hand_id = hand_ids[4] 
            elif pair_count == 2 and list(num_times_paired.values())==[0,2]: # trips
                hand_id = hand_ids[3]
            elif pair_count == 2 and list(num_times_paired.values())==[2,0]: # trips
                hand_id = hand_ids[3]
            elif pair_count == 2 and list(num_times_paired.values())==[1,1]: # 2-pair
                hand_id = hand_ids[2]
            elif pair_count == 1: # 1-pair
                hand_id = hand_ids[1]
            elif pair_count == 0: # no-pair
                hand_id = hand_ids[0]        
            else:
                raise ValueError('Cant determine unpaired hand, board = ' + str(board) + 'HC = ' + str(HC))
				
        elif HC[0][0] == HC[1][0]: # pocket pairs
		
            pair_count = 1
            num_times_paired = dict() # two element list for number of times HC card is paired
            num_times_suited = dict({'h':0,'s':0,'c':0,'d':0}) # two element list for number of times HC card is suited to another
            card_indexes = list()
			
            if board_face_count['A'] >= 1:
                card_indexes.append(-1) # Aces play high and low for a wheel
			
			# iterate over hole cards and board
			
            for face, suit in HC: # hole cards
                num_times_paired[face+suit] = 0
                num_times_suited[suit] += 1
                card_indexes.append(cards.index(face))
				
                for commface, commsuit in board: # community cards
                    card_indexes.append(cards.index(commface))
					
                    if face == commface:
                        pair_count += 1
                        num_times_paired[face+suit] += 1
			
            for commface, commsuit in board: num_times_suited[commsuit] += 1
			
            card_indexes = np.unique(np.sort(card_indexes)) # detecting a straight
            max_straight_card = str() # store top card of straight
            straight_counter = 1 # starts on 1 as second card makes two to a straight
            straight_flush_counter = 0 # counting cards to a straight flush
            all_cards_out_index = list()
			
            for idx, value in enumerate(card_indexes[1:]): # determine if there's a straight
                if straight_counter == 5: # you've made a straight, exit the loop
                    break
                elif value == card_indexes[idx]+1:
                    straight_counter += 1
                    max_straight_card = cards[value] # store top card's deck index of straight
                else: 
                    straight_counter = 1 # reset counter
			
            if straight_counter >= 5 and max(num_times_suited.values()) >= 5: # determine if straight is a straight flush
                all_cards_out = HC + board # all cards available
				
                for face, suit in all_cards_out: # index for all cards
                    all_cards_out_index.append(cards.index(face))
				
                all_cards_out_index = np.sort(all_cards_out_index) # sort all cards by index
                all_cards_out = [all_cards_out for _, all_cards_out in sorted(zip(all_cards_out_index, all_cards_out))]
				
                for face, suit in all_cards_out: # iterate over all cards and match with suit of flush
                    if suit == max(num_times_suited, key=num_times_suited.get): 
                        straight_flush_counter += 1
                    elif suit != max(num_times_suited, key=num_times_suited.get):
                        straight_flush_counter = 0
                    else:
                        raise ValueError('Error in straight flush determination')
			
			# assign hand id in order of decreasing strength, decreasingly probable
			
            if straight_flush_counter >= 5: # straight-flush or royal flush
                hand_id = hand_ids[8]
            elif pair_count == 1 and list(board_pair_count.values()).count(3) == 1: # quads
                hand_id = hand_ids[7]
            elif pair_count == 5 and list(num_times_paired.values())==[2,2]: # quads
                hand_id = hand_ids[7]
            elif pair_count > 5: # quads debugging hand isnt possible
                hand_id = hand_ids[7]
            elif pair_count == 1 and list(board_pair_count.values()).count(2) == 1: # boat
                hand_id = hand_ids[6]
            elif pair_count == 3 and list(num_times_paired.values())==[1,1] and list(board_pair_count.values()).count(2) == 1: # boat
                hand_id = hand_ids[6]
            elif pair_count == 3 and list(num_times_paired.values())==[1,1] and list(board_pair_count.values()).count(1) >= 1: # boat
                hand_id = hand_ids[6]
            elif np.max(list(num_times_suited.values())) >= 5: # flush
                hand_id = hand_ids[5]
            elif straight_counter >= 5: # straight
                hand_id = hand_ids[4]
            elif pair_count == 3 and list(board_pair_count.values()).count(0) == len(board_pair_count): # set
                hand_id = hand_ids[3]
            elif pair_count == 1 and list(board_pair_count.values()).count(1) == 2: # 2-pair
                hand_id = hand_ids[2]
            elif pair_count == 1 and list(board_pair_count.values()).count(1) == 1: # 2-pair
                hand_id = hand_ids[2]
            elif pair_count == 1 and list(board_pair_count.values()).count(0) == len(board_pair_count): # 1-pair
                hand_id = hand_ids[1]
            else:
                raise ValueError('Cant determine paired hand, board = ' + str(board) + 'HC = ' + str(HC))
                
    if hand_id == 4: # increment straights by top card value
        hand_id = hand_id + (card_strength_dict[max_straight_card] / 100)
    else: # increment hand strength by hole cards face value, example: so a pair of Aces is worth more than a pair of Jacks
        hand_id = hand_ids.index(hand_id) + (card_strength_dict[HC[0][0]]/100) + (card_strength_dict[HC[1][0]]/100) # convert to numeric, take high card into consideration
		
    return hand_id # returns hand id (ie. flush, full house, pair, as a rank order float)

def get_hand_strength(self, HC, board, remaining_deck, HC_strength, hand_id, current_street): 
    # returns the strength of your hand as hole cards as a five card hand using percentiles
    
    hand_strength = dict()
    num_iter = 1000 # compare your hand to 1000 other possible hands
    HC_samples = list()
    HC_sample_strengths = list()
    hand_ids_samples = list()
    rel_HC_strength = 0 # your hole cards' strength relative to the sample
    rel_hand_id_strength = 0 # your hand_id's strength relative to sample
    
    if current_street == 'Pre':
        # Monte Carlo simulation on just hole cards, without flop hand strength = hole card strength
        for i in range(num_iter):
            HC_samples.append(random.sample(remaining_deck,2))
            HC_sample_strengths.append(get_hole_card_strength(self, HC_samples[i]))
         
        rel_HC_strength = stats.percentileofscore(np.array(HC_sample_strengths), HC_strength, kind='mean')
        hand_strength = {'HC':rel_HC_strength, 'hand_id':0} # no hand has been made yet so hand id strength is zero
    
    else:
        # Monte Carlo simulation on hole cards and hands
        for i in range(num_iter):
            HC_samples.append(random.sample(remaining_deck,2))
            HC_sample_strengths.append(get_hole_card_strength(self, HC_samples[i]))
            hand_ids_samples.append(get_hand_id(self, HC_samples[i], board, current_street))
            
        # this part of the function solves the problem of equally ranked hands
        # of different strengths (ex. AJ vs KJ on J-8-2 board)
        # both will have same hand_id strength but AJ will have higher HC_strength
        rel_HC_strength = stats.percentileofscore(np.array(HC_sample_strengths), HC_strength, kind='mean')
        rel_hand_id_strength = stats.percentileofscore(np.array(hand_ids_samples), hand_id, kind='mean')
        
        hand_strength = {'HC':rel_HC_strength, 'hand_id':rel_hand_id_strength}
        
    return hand_strength

def get_hand_sensitivity(self, HC, board, hand_strength, remaining_deck, current_street):
    # potential for your hand to change strength on subsequent street
    # will take hypothetical future board cards and calculate hand strength
    # and compare to current hand strength
    
    hand_sensitivity = 0 # -ve number indicates hand can weaken, +ve strengthen
    num_iter = 100
    sensitivity_list = list() # list of hypothetical hand strengths
    
    if current_street == 'Pre':
        HC_strength = get_hole_card_strength(self,HC)
        
        for _ in range(num_iter):
            # draw a hypothetical flop from the deck and calculate your hand's fitness
            board_iter = list(board)
            board_iter, remaining_deck_iter, current_street_iter = deal_flop(self, remaining_deck, current_street)
            hand_id_iter = get_hand_id(self, HC, board_iter, current_street_iter)
            hand_strength_iter = get_hand_strength(self, HC, board_iter, remaining_deck_iter, HC_strength, hand_id_iter, current_street_iter)
            sensitivity_list.append(hand_strength_iter['hand_id'])
            
        hand_sensitivity = np.mean(sensitivity_list) - hand_strength['HC'] # if prelop the sensitivity is defined by the potential flop percentile minus the HC percentile from pre
        
    elif current_street == 'Flop':
        HC_strength = get_hole_card_strength(self, HC)
        
        for _ in range(num_iter):
            # draw a hypothetical turn from the deck and calculate your hand's fitness
            board_iter = list(board)
            board_iter, remaining_deck_iter, current_street_iter = deal_turn(self, board_iter, remaining_deck, current_street)
            hand_id_iter = get_hand_id(self, HC, board_iter, current_street_iter)
            hand_strength_iter = get_hand_strength(self, HC, board_iter, remaining_deck_iter, HC_strength, hand_id_iter, current_street_iter)
            sensitivity_list.append(hand_strength_iter['hand_id'])
            
        hand_sensitivity = np.mean(sensitivity_list) - hand_strength['hand_id'] # potential hand percentile minus current percentile
        
    elif current_street == 'Turn':
        HC_strength = get_hole_card_strength(self, HC)
        
        for _ in range(num_iter):
            # draw a hypothetical river from the deck and calculate your hand's fitness
            board_iter = list(board)
            board_iter, remaining_deck_iter, current_street_iter = deal_river(self, board_iter, remaining_deck, current_street)
            hand_id_iter = get_hand_id(self, HC, board_iter, current_street_iter)
            hand_strength_iter = get_hand_strength(self, HC, board_iter, remaining_deck_iter, HC_strength, hand_id_iter, current_street_iter)
            sensitivity_list.append(hand_strength_iter['hand_id'])
            
        hand_sensitivity = np.mean(sensitivity_list) - hand_strength['hand_id'] # if it goes up in strength then sens is positive
        
    elif current_street == 'River':
        hand_sensitivity = 0 # hand cannot change
        
    else:
        raise ValueError('street problem')
        
    return hand_sensitivity

def card_name_converter(twocards): #converts names of two card holdings
    output = None
    
    if type(twocards) == list:
        output = ''.join([twocards[0][0], twocards[0][1], twocards[1][0], twocards[1][1]])
        
    elif type(twocards) == str:
        output = [(twocards[0],twocards[1]), (twocards[2],twocards[3])]
    else:
        raise Exception('two card format?')
        
    return output

def get_stack_to_pot_ratio(current_stack, current_pot):
    # a higher SPR indicates more risk, a lower SPR indicates more reward
    SPR = current_stack/current_pot
    return SPR
	
def get_margin(THS, bet_size, current_pot):
	# return margin odds
    if bet_size < 0:
        raise ValueError('bet is negative')
        
    THS = THS/100 # needs to be expressed as a percentage

    fold_range = bet_size/(bet_size + current_pot) # minimum defense frequency, expressed as bottom percent of range that folds to bet
    PO = bet_size/((2*bet_size) + current_pot) # odds you need to break even on given bet size
    cont_equity = (THS-fold_range)/(1-fold_range) # continuing equity 
    margin = cont_equity - PO # margin difference
    
    return margin
	
def winner(self, HC, board, current_street, opp_HC = None): # determines winner of the hand
	
    if opp_HC == None:
        opp_HC = random.sample(remaining_deck, 2) # pick two random cards for your opponent unless you give them
    
    if type(opp_HC) == str:
        opp_HC = card_name_converter(opp_HC) # so you can input as strings
    
    if type(HC) == str:
        HC = card_name_converter(HC)
        
    my_hand = get_hand_id(self, HC, board, current_street)
    opp_hand = get_hand_id(self, opp_HC, board, current_street)
	
    if my_hand > opp_hand: # player wins
        outcome = 1
    elif my_hand < opp_hand: # opponent wins
        outcome = 0
    elif my_hand == opp_hand: # tie
        outcome = 0.5
        
		
    return outcome
	
def tourny(self, current_street, tournament_size = 10, cpop = None): # run a tournament selection, optionally provide child population
    
    if cpop == None: # not a child tournament
        tpop = list(set(deck)-set(board)) # initial population comprises all non-community cards, but is not calculated for pairs of cards, same card can be sampled twice or more
        tournament = []
        tournament_fitness = dict()
		
        for indiv_num in range(0, tournament_size): # create tournament sample
            tournament.append(random.sample(tpop, 2)) 
		
        for indiv in tournament: # calculate everyone's fitness in sample (computationally expensive)
            indiv_name = ''.join([indiv[0][0], indiv[0][1], indiv[1][0], indiv[1][1]])
            
            if indiv_name[:2] == indiv_name[2:]: # cards mutated to the same card
                continue
            
            if indiv_name not in tournament_fitness:
                tournament_fitness[indiv_name] = []
                tournament_fitness[indiv_name].append(get_hand_id(self, indiv, self.board, self.current_street))
        
        if len(tournament_fitness) > 0: # in rare cases the tournament is zero sized, its a bug
            tournament_winner_name = max(tournament_fitness, key = tournament_fitness.get)
            tournament_winner_name = card_name_converter(tournament_winner_name)
            tournament_winner_fitness = max(tournament_fitness.values())
        else:
            tournament_winner_name = card_name_converter('XyXy')
            tournament_winner_fitness = 0.0 # not sure how to fix, somehow it finds no winner
		
    else: # tournament among children
        tournament = []
        tournament_fitness = dict()
		
        for indiv_num in range(0, tournament_size): # create tournament sample
            tournament.append(random.sample(cpop, 1)[0]) # same child can be chosen multiple times
		
        for indiv in tournament: # calculate everyone's fitness in sample (computationally expensive)
            indiv_name = ''.join([indiv[0][0], indiv[0][1], indiv[1][0], indiv[1][1]])
            
            if indiv_name[:2] == indiv_name[2:]: # cards mutated to the same card
                continue
            
            if indiv_name not in tournament_fitness:
                tournament_fitness[indiv_name] = []
                tournament_fitness[indiv_name].append(get_hand_id(self, indiv, self.board, self.current_street))
                
        if len(tournament_fitness) > 0: # in rare cases the tournament is zero sized, its a bug	
            tournament_winner_name = max(tournament_fitness, key = tournament_fitness.get)
            tournament_winner_name = card_name_converter(tournament_winner_name)
            tournament_winner_fitness = max(tournament_fitness.values())
        else:
            tournament_winner_name = card_name_converter('XyXy')
            tournament_winner_fitness = 0.0 # not sure how to fix, somehow it finds no winner
        
    return tournament_winner_name, tournament_winner_fitness # format back as a list of strings

def best_possible_hand(self, board, deck, current_street): # Genetic Algorithm implementation to determine the best possible two-card holding for opponent
	
    population = list()
    child_pop = list()
    elite_dict = dict()
    num_generations = 5
    curr_generation = 1
	
    while curr_generation < num_generations:
        
	
        while len(population) < 50: # arbitrarily defined population size
		
            if curr_generation == 1: # first generation is drawn from deck
                parent1 = tourny(self, self.current_street, 10) # arbitrary tournament size
                parent2 = tourny(self, self.current_street, 10)
            elif curr_generation != 1 and curr_generation <= num_generations: # subsequent generations come from child population
                parent1 = tourny(self, self.current_street, 10, child_pop)
                parent2 = tourny(self, self.current_street, 10, child_pop)
            elif curr_generation > num_generations: # shouldn't happen but whatever
                break
            else:
                raise ValueError('num_generations error')
			
            if type(parent1[1] == list) and type(parent2[1] == list): # bug fixing
                elite_dict[card_name_converter(parent1[0])] = parent1[1][0] # keep parents in format {name:fitness}
                elite_dict[card_name_converter(parent2[0])] = parent2[1][0]
            elif type(parent1[1] == float) and type(parent2[1] == float): # more bug fixing
                elite_dict[card_name_converter(parent1[0])] = parent1[1] # keep parents in format {name:fitness}
                elite_dict[card_name_converter(parent2[0])] = parent2[1]
            elif type(parent1[1] == list) and type(parent2[1] == float):
                elite_dict[card_name_converter(parent1[0])] = parent1[1][0] # keep parents in format {name:fitness}
                elite_dict[card_name_converter(parent2[0])] = parent2[1]
            elif type(parent1[1] == float) and type(parent2[1] == list):
                elite_dict[card_name_converter(parent1[0])] = parent1[1] # keep parents in format {name:fitness}
                elite_dict[card_name_converter(parent2[0])] = parent2[1][0]
            else:
                
                continue
            
            parent1 = parent1[0] # dump their fitnesses
            parent2 = parent2[0]
            
            child1 = [parent1[0], parent2[1]] # crossover
            child2 = [parent1[1], parent2[0]] # crossover
			
            if child1[0] == child1[1]: # card has been repeated, child is not allowed, mutate child
                mutation = random.choice(random.choice(child1))
				
                if mutation in cards and mutation != 'A': # point of mutation is the face of the card
                    child1[0] = tuple([cards[cards.index(mutation)+random.choice([-1,1])], child1[0][1]]) # mutate up or down one index value
                elif mutation in cards and mutation == 'A':
                    child1[0] = tuple([random.choice(['K','2']), child1[0][1]]) # because of indexing bug
                elif mutation in suits: # point of mutation is the suit of the card
                    child1[0] = tuple([child1[0][0], random.choice(suits)]) # mutate up or down one index value
                else:
                    raise ValueError('Mutation point not in suits or cards')
            elif child2[0] == child2[1]: # card has been repeated, child is not allowed, mutate child
                mutation = random.choice(random.choice(child2))
				
                if mutation in cards and mutation != 'A': # point of mutation is the face of the card
                    child2[0] = tuple([cards[cards.index(mutation)+random.choice([-1,1])], child2[0][1]]) # mutate up or down one index value
                elif mutation in cards and mutation == 'A':
                    child2[0] = tuple([random.choice(['K','2']), child2[0][1]]) # because of indexing bug
                elif mutation in suits: # point of mutation is the suit of the card
                    child2[0] = tuple([child2[0][0], random.choice(suits)]) # mutate up or down one index value
                else:
                    raise ValueError('Mutation point not in suits or cards')
			
            else:
                continue
			
            population.extend([child1, child2])
			
        child_pop = population # copy population to next generation
        population = list() # empty the population
        curr_generation += 1  # iterate generation
		
    mortal_fitness = max(elite_dict.values())
    mortal_nuts = [key for key, value in elite_dict.items() if value == mortal_fitness]
	
    #return mortal_nuts # Comment this line to run Project_Action.py, uncomment the print line below
    print('The best possible hand is: ' + ' or '.join(mortal_nuts) + ' with fitness ' + str(mortal_fitness)) # Comment this line for GA_Empirical.py

def desired_pot_size(self, current_pot, hand_strength, hand_sensitivity, hand_id, current_street, current_stack, opp_current_stack):
    # optimize for the pot size you would like based on hand odds and pot odds, hand odds will decrease with increasing bet size 
 	# to reflect opponents tighter continuing range
    desired_pot = 0
    bluff_factor = random.random() # probability of bluffing
    bluff_size = random.randint(5,20) # wide bluff sizing
    betting_weights = [3,1,0.5] # factor weights for different hand strength quantifiers, current made hand is most important, this could be changed 
    #domain = range(1, current_stack) # betting domain, not used right now
    
    if current_street == 'Pre':
        THS = betting_weights[1]*hand_strength['HC'] + betting_weights[2]*hand_sensitivity # THS - Total Hand Strength, a weighted average of all percentiles of strength
        THS = THS/sum(betting_weights[1:]) # average percentile by weights, hand id does not contribute
 			
        if bluff_factor > 0.95: # 5% bluff frequency
            desired_pot = bluff_size * blind
 			
        else: # hill climb - descend margin as close to zero without being negative
            bet_size = blind # start at one end of the domain
 			
            while True:
 			
                margin = get_margin(THS, bet_size, current_pot) # fitness for this bet size
                neighbours = list([bet_size + blind, bet_size - blind]) # neighbours for this bet size
                margin_n1 = get_margin(THS, neighbours[0], current_pot) # neighbours fitness
                margin_n2 = get_margin(THS, neighbours[1], current_pot) # neighbours fitness
                bet_margins = dict({bet_size:margin, neighbours[0]:margin_n1, neighbours[1]:margin_n2})
                bet_margins = {key: value for (key, value) in bet_margins.items() if value >= 0} # filter out negative values
                bet_size = min(bet_margins, key = bet_margins.get) # new bet size equal smallest non-zero, non-negative margin
				
                if len(bet_margins) < 3: # some margin has become negative
                    break
 			
            desired_pot = (2*bet_size) + current_pot
 			
 			
    elif current_street == 'Flop':
        THS = betting_weights[0]*hand_strength['hand_id'] + betting_weights[1]*hand_strength['HC'] + betting_weights[2]*hand_sensitivity # THS - Total Hand Strength, a weighted average of all percentiles of strength
        THS = THS/sum(betting_weights) # average percentile by weights
 			
        if bluff_factor > 0.95: # 5% bluff frequency
            desired_pot = bluff_size * (current_pot/10) # standard sizing
 			
        else: # hill climb - descend margin as close to zero without being negative
            bet_size = blind # start at one end of the domain
 			
            while True:
 			
                margin = get_margin(THS, bet_size, current_pot) # fitness for this bet size
                neighbours = list([bet_size + blind, bet_size - blind]) # neighbours for this bet size
                margin_n1 = get_margin(THS, neighbours[0], current_pot) # neighbours fitness
                margin_n2 = get_margin(THS, neighbours[1], current_pot) # neighbours fitness
                bet_margins = dict({bet_size:margin, neighbours[0]:margin_n1, neighbours[1]:margin_n2})
                bet_margins = {key: value for (key, value) in bet_margins.items() if value >= 0} # filter out negative values
                bet_size = min(bet_margins, key = bet_margins.get) # new bet size equal smallest non-zero, non-negative margin
				
                if len(bet_margins) < 3: # some margin has become negative
                    break
 			
            desired_pot = (2*bet_size) + current_pot
 			
    elif current_street == 'Turn':
        THS = betting_weights[0]*hand_strength['hand_id'] + betting_weights[1]*hand_strength['HC'] + betting_weights[2]*hand_sensitivity # THS - Total Hand Strength, a weighted average of all percentiles of strength
        THS = THS/sum(betting_weights) # average percentile by weights
 			
        if bluff_factor > 0.95: # 5% bluff frequency
            desired_pot = bluff_size * (current_pot/10) # standard sizing
 			
        else: # hill climb - descend margin as close to zero without being negative
            bet_size = blind # start at one end of the domain
 			
            while True:
 			
                margin = get_margin(THS, bet_size, current_pot) # fitness for this bet size
                neighbours = list([bet_size + blind, bet_size - blind]) # neighbours for this bet size
                margin_n1 = get_margin(THS, neighbours[0], current_pot) # neighbours fitness
                margin_n2 = get_margin(THS, neighbours[1], current_pot) # neighbours fitness
                bet_margins = dict({bet_size:margin, neighbours[0]:margin_n1, neighbours[1]:margin_n2})
                bet_margins = {key: value for (key, value) in bet_margins.items() if value >= 0} # filter out negative values
                bet_size = min(bet_margins, key = bet_margins.get) # new bet size equal smallest non-zero, non-negative margin
				
                if len(bet_margins) < 3: # some margin has become negative
                    break
 			
            desired_pot = (2*bet_size) + current_pot
 			
 			
 			
    elif current_street == 'River':
        THS = betting_weights[0]*hand_strength['hand_id'] + betting_weights[1]*hand_strength['HC'] # THS - Total Hand Strength, a weighted average of all percentiles of strength
        THS = THS/sum(betting_weights[:2]) # average percentile by weights, sens does not contribute
 			
        if bluff_factor > 0.95: # 5% bluff frequency
            desired_pot = bluff_size * (current_pot/10) # standard sizing
 			
        else: # hill climb - descend margin as close to zero without being negative
            bet_size = blind # start at one end of the domain
 			
            while True:
 			
                margin = get_margin(THS, bet_size, current_pot) # fitness for this bet size
                neighbours = list([bet_size + blind, bet_size - blind]) # neighbours for this bet size
                margin_n1 = get_margin(THS, neighbours[0], current_pot) # neighbours fitness
                margin_n2 = get_margin(THS, neighbours[1], current_pot) # neighbours fitness
                bet_margins = dict({bet_size:margin, neighbours[0]:margin_n1, neighbours[1]:margin_n2})
                bet_margins = {key: value for (key, value) in bet_margins.items() if value >= 0} # filter out negative values
                bet_size = min(bet_margins, key = bet_margins.get) # new bet size equal smallest non-zero, non-negative margin
				
                if len(bet_margins) < 3: # some margin has become negative
                    break
 			
            desired_pot = (2*bet_size) + current_pot
    else:
        raise Exception('Cannot determine street for pot size optimization')

    return desired_pot 

def best_action(self, desired_pot, current_pot, my_position, opp_action = None, opp_bet = 0):
    action = None # optimize for discrete action based on desired pot
    amount = 0 # amount associated with action
 	
    # First decide what to do if you're out of position
		
    if my_position == 'OOP' and opp_action == None: 
		
        if desired_pot <= 1.3*current_pot:
            action = 'Check'
            amount = 0
        else:
            action = 'Bet'
            amount = (desired_pot - current_pot)/2 
 			
    elif my_position == 'OOP' and opp_action == 'Bet': # opponent bets after computer checked
        None
    elif my_position == 'OOP' and opp_action == 'Raise': # opponent raises after computer bet
        None
        
    # If opponent closes action then position doesn't matter
    
    elif opp_action == 'Call' or opp_action == 'Fold': # nothing to think about
        action = None
        amount = 0
        
    # Decide what to do if you're in position
    
    elif my_position == 'IP' and opp_action == None:
        
        raise Exception('Opponent must have an action OOP')
        
    elif my_position == 'IP' and opp_action == 'Check': # opponent checks to computer
		
        if desired_pot <= 1.3*current_pot:
            action = 'Check'
            amount = 0
        else:
            action = 'Bet'
            amount = (desired_pot - current_pot)/2
 			
    elif my_position == 'IP' and opp_action == 'Bet': # opponent bets into computer
		
        if desired_pot < (current_pot + (2*opp_bet)):
            action = 'Fold'
            amount = 0
        elif desired_pot >= (current_pot + (2*opp_bet)) and desired_pot <= 1.3*(current_pot + (2*opp_bet)):
            action = 'Call'
            amount = opp_bet
        elif desired_pot >= 1.3*(current_pot + (2*opp_bet)):
            action = 'Raise'
            amount = (desired_pot - current_pot)/2 # this is a raise total amount, not in addition to opponents bet
 			
    elif my_position == 'IP' and opp_action == 'Raise': # opponent raises into computer
		
        if desired_pot < (current_pot + (2*opp_bet)):
            action = 'Fold'
            amount = 0
        elif desired_pot >= (current_pot + (2*opp_bet)) and desired_pot <= 1.3*(current_pot + (2*opp_bet)):
            action = 'Call'
            amount = opp_bet
        elif desired_pot >= 1.3*(current_pot + (2*opp_bet)):
            action = 'Raise'
            amount = (desired_pot - current_pot)/2 # this is a raise total amount, not in addition to opponents bet
        else:
            raise Exception('IP problem')
		
    else:
        raise Exception('action problem')
 	
    return action, amount

def stack_adjust(self, current_stack, opp_current_stack, current_pot, current_street, action, amount, outcome, opp_action = None):
 	# perform best action and update stack sizes and pot size, opp_action will be input by the user
 	
 	if action == 'Fold': # computer folds at any point it loses
         opp_current_stack += current_pot
         current_pot = 0
		
 	elif opp_action == 'Fold': # user folds at any point computer wins
         current_stack += current_pot
         current_pot = 0
		
 	else:
         if current_street == 'River': # River is final street so calling ends the hand, checking IP also ends the hand
             
				
             if action == 'Call' and outcome == 0: # computer loses hand is over
                 opp_current_stack = opp_current_stack + current_pot + amount
                 current_pot = 0
				
             elif action == 'Call' and outcome == 1: # computer wins hand is over
                 current_stack = current_stack + current_pot # current pot has already been updated with opponents bet
                 current_pot = 0
 			
             elif opp_action == 'Call' and outcome == 0: # computer loses hand is over
                 opp_current_stack = opp_current_stack + current_pot + amount
                 current_pot = 0
             elif opp_action == 'Call' and outcome == 1: # computer wins hand is over
                 current_stack = current_stack + current_pot # current pot has already been updated with opponents bet
                 current_pot = 0
				
             elif my_position == 'OOP' and action == 'Check':
                 None
				
             elif my_position == 'IP' and action == 'Check' & outcome == 0: # check back and computer loses
                 opp_current_stack += current_pot
                 current_pot = 0
				
             elif my_position == 'IP' and action == 'Check' & outcome == 1: # check back and computer wins
                 current_stack += current_pot
                 current_pot = 0
 			
             elif my_position == 'OOP' and action == 'Bet':
                 current_stack -= amount
                 current_pot += amount
				
             elif my_position == 'IP' and action == 'Bet':
                 current_stack -= amount
                 current_pot += amount
				
             elif my_position == 'IP' and action == 'Raise':
                 current_stack -= amount
                 current_pot += amount
				
             else:
                 raise ValueError('river problems')
				
         elif current_street != 'River': # calling does not end the hand
             None
 			
		
         else:
             raise ValueError('stack adjust with street')
 	
 	return current_stack, opp_current_stack, current_pot

