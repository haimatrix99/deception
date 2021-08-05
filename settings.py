from random import shuffle
import pandas as pd
import numpy as np

clue_data = pd.read_csv('data/clue.csv')
mean_data = pd.read_csv('data/mean.csv')
death_data = pd.read_csv('data/causeofdeath.csv')
location_data = pd.read_csv('data/location.csv')
hint_data = pd.read_csv('data/hint.csv')

death = death_data.to_dict()
location = location_data.to_dict()
hint = hint_data.to_dict()

keys_hint = list(hint.keys())

TOKEN = ''

NUM_CLUE = 200
NUM_MEAN = 90
NUM_HINT = 21

global NUMBERS
NUMBERS = []

global players
players = 0

global list_id
list_id = []

global list_player_id
list_player_id = []

global kick
kick = False

global isselect
isselect = False

global isfound
isfond = False
global ispick
ispick = False

global num_murder, num_accomplice, num_witness
num_murder = 0
num_accomplice = 0
num_witness = 0

name_murder = []

clue = np.reshape(clue_data.to_numpy(), (1, NUM_CLUE))
mean = np.reshape(mean_data.to_numpy(), (1, NUM_MEAN))

player_clue = []
player_mean = []
total_clue = []
total_mean = []


class Cards:
    global clues, means, hints
    clues = clue[0]
    means = mean[0]
    hints = keys_hint

    def __init__(self):
        pass


class Deck(Cards):
    def __init__(self):
        Cards.__init__(self)
        self.myclueset = []
        self.mymeanset = []
        self.myhintset = []
        for n in clues:
            self.myclueset.append(n)
        for n in means:
            self.mymeanset.append(n)
        for n in hints:
            self.myhintset.append(n)

    def popCard(self):
        if len(self.myclueset) == 0 or len(self.mymeanset) == 0:
            return "NO CARDS CAN BE POPPED FURTHER"
        else:
            cluepopped = self.myclueset.pop()
            meanpopped = self.mymeanset.pop()
            print("Clue removed is", cluepopped)
            print("Mean removed is", meanpopped)

class ShuffleCards(Deck):

    # Constructor
    def __init__(self):
        Deck.__init__(self)

    # Method to shuffle cards
    def shuffle_clue(self):
        if len(self.myclueset) < NUM_CLUE:
            print("cannot shuffle the cards")
        else:
            shuffle(self.myclueset)
            return self.myclueset

    def shuffle_mean(self):
        if len(self.mymeanset) < NUM_MEAN:
            print("cannot shuffle the cards")
        else:
            shuffle(self.mymeanset)
            return self.mymeanset

    def shuffle_hint(self):
        if len(self.mymeanset) < NUM_HINT:
            print("cannot shuffle the cards")
        else:
            shuffle(self.myhintset)
            return self.myhintset

    def popClue(self):
        if len(self.myclueset) == 0:
            return "NO CLUES CAN BE POPPED FURTHER"
        else:
            cluepopped = self.myclueset.pop()
            return cluepopped

    def popMean(self):
        if len(self.mymeanset) == 0:
            return "NO CLUES CAN BE POPPED FURTHER"
        else:
            meanpopped = self.mymeanset.pop()
            return meanpopped

    def popHint(self):
        if len(self.myhintset) == 0:
            return "NO CLUES CAN BE POPPED FURTHER"
        else:
            hintpopped = self.myhintset.pop()
            return hintpopped

    def resetDeck(self):
        self.myclueset = []
        self.mymeanset = []
        self.myhintset = []
        for n in clues:
            self.myclueset.append(n)
        for n in means:
            self.mymeanset.append(n)
        for n in hints:
            self.myhintset.append(n)


objCards = Cards()
objDeck = Deck()
objShuffleCards = ShuffleCards()
shuffle_clue_deck = objShuffleCards.shuffle_clue()
shuffle_mean_deck = objShuffleCards.shuffle_mean()
shuffle_hint_deck = objShuffleCards.shuffle_hint()


class Player:
    def __init__(self, role='', clue=[], mean=[], honor=1):
        self.role = role
        self.clue = clue
        self.mean = mean
        self.hint = hint
        self.honor = honor


def show_card(player, num_card):
    player_clue = []
    player_mean = []

    total_clue = []
    total_mean = []
    for _ in range(player):
        for _ in range(int(num_card)):
            player_clue.append(objShuffleCards.popClue())
            player_mean.append(objShuffleCards.popMean())
        total_clue.append(player_clue)
        total_mean.append(player_mean)
        player_clue = []
        player_mean = []
    return total_mean, total_clue


def show_hint():
    total_hint = []
    hint_show = []
    for i in range(4):
        total_hint.append(objShuffleCards.popHint())
    for i in total_hint:
        hints = pd.Series(hint[i]).values
        hint_show.append(hints)
    return hint_show


def show_death():
    cause_of_death = pd.DataFrame(death_data).values
    cause_of_death = np.reshape(cause_of_death, (1, 7))
    cause_of_death = cause_of_death[0]
    return cause_of_death


def show_location(choice):
    location_of_crime = []
    location_of_crime = pd.Series(location_data[choice]).values
    return location_of_crime


def shuffle_number(num_player):
    NUMBERS = list(range(1, num_player + 1))
    shuffle(NUMBERS)
    return NUMBERS


def locations():
    locations = []
    for i in range(1, 5):
        locate = []
        for j in range(1, 7):
            locate.append(location[str(i)][j])
        locations.append(locate)
    return locations
