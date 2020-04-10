from functools import total_ordering

from poker import log
from poker.utils import cmp

def ranksym(rank):
    return Card.facerank[rank]

@total_ordering
class Card:
    '''
    A standard playing card
    '''
    ranks = ('deuce', 'trey', 'four', 'five', 'six', 'seven', 'eight',
             'nine', 'ten', 'jack', 'queen', 'king', 'ace')
    suits = ('clubs', 'diamonds', 'hearts', 'spades')
    facerank = ('2', '3', '4', '5', '6', '7', '8',
                '9', 'T', 'J', 'Q', 'K', 'A')
    facesuit = ('♣', '♦', '♥', '♠')

    def __init__(self, cardnum=0):
        self.cardnum = cardnum

    def __str__(self):
        return '[Card:%d:%s:%s]' % (self.cardnum, self.face(), self.cardname())

    def __cmp__(self, other):
        return cmp(self.rank(), other.rank())

    def __lt__(self, other):
        return self.__cmp__(other) == -1

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def rank(self):
        return self.cardnum % 13

    def rankname(self):
        return self.ranks[self.rank()]

    def suit(self):
        return self.cardnum // 13

    def suitname(self):
        return self.suits[self.suit()]

    def cardname(self):
        return self.rankname() + ' of ' + self.suitname()

    def face(self, color = True):
        r = Card.facerank[self.rank()]
        s = Card.facesuit[self.suit()]
        f = r + s

        if color:
            if s in '♣♠':
                f = '%c%c' % (r, s)
            else:
                f = '%c\x034%c\x03' % (r, s)
        return f
